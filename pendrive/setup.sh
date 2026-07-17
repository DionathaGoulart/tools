#!/usr/bin/env bash
# setup.sh — configura pass (password-store) com pendrive criptografado
# Uso: bash setup.sh
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'
info()  { echo -e "${CYAN}::${NC} $1"; }
ok()    { echo -e "${GREEN}✓${NC} $1"; }
err()   { echo -e "${RED}✗${NC} $1"; }

# ── 1. Verificar dependências ──────────────────────────────────────────
info "Verificando dependências..."
MISSING=0
for cmd in pass gpg git; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    err "$cmd não encontrado"
    MISSING=1
  fi
done

if [ "$MISSING" = 1 ]; then
  echo ""
  info "Instale os que faltam:"
  echo "  macOS: brew install pass gnupg"
  echo "  Linux: sudo apt install pass gnupg"
  exit 1
fi
ok "Todas as dependências instaladas"

# ── 2. Verificar chave GPG ─────────────────────────────────────────────
KEY_ID=$(gpg --list-secret-keys --keyid-format LONG 2>/dev/null | grep ^sec | head -1 | awk '{print $2}' | cut -d'/' -f2)

if [ -z "$KEY_ID" ]; then
  echo ""
  info "Nenhuma chave GPG encontrada. Vamos criar uma."
  read -p "  Nome [DionathaGoulart]: " GPG_NAME
  GPG_NAME="${GPG_NAME:-DionathaGoulart}"
  read -p "  Email [dionatha.work@gmail.com]: " GPG_EMAIL
  GPG_EMAIL="${GPG_EMAIL:-dionatha.work@gmail.com}"

  cat > /tmp/gpg-batch <<EOF
Key-Type: RSA
Key-Length: 4096
Subkey-Type: RSA
Subkey-Length: 4096
Name-Real: $GPG_NAME
Name-Email: $GPG_EMAIL
Expire-Date: 0
%no-protection
%commit
EOF
  gpg --batch --gen-key /tmp/gpg-batch
  rm /tmp/gpg-batch
  KEY_ID=$(gpg --list-secret-keys --keyid-format LONG 2>/dev/null | grep ^sec | head -1 | awk '{print $2}' | cut -d'/' -f2)
  ok "Chave GPG criada: $KEY_ID"
else
  ok "Chave GPG encontrada: $KEY_ID"
fi

# ── 3. Inicializar pass ─────────────────────────────────────────────────
if [ ! -d "$HOME/.password-store" ]; then
  pass init "$KEY_ID"
  ok "pass init"
else
  ok "pass já inicializado"
fi

# ── 4. Pendrive ─────────────────────────────────────────────────────────
echo ""
info "Conecte o pendrive agora e digite o caminho dele."
info "Exemplos: /Volumes/SEGURANCA  /media/usb  /mnt/usb"
read -p "  Caminho do pendrive: " PENDRIVE

if [ ! -d "$PENDRIVE" ]; then
  err "Caminho inválido: $PENDRIVE"
  exit 1
fi
ok "Pendrive montado em $PENDRIVE"

STORE_PATH="$PENDRIVE/pass-store.git"
if [ -d "$STORE_PATH" ]; then
  info "Repositório já existe. Conectando..."
else
  git init --bare "$STORE_PATH"
  ok "Repositório criado em $STORE_PATH"
fi

cd "$HOME/.password-store"
if ! git remote get-url origin 2>/dev/null; then
  git remote add origin "$STORE_PATH"
  git push --set-upstream origin master
  ok "Remote configurado e primeiro push feito"
else
  git remote set-url origin "$STORE_PATH"
  ok "Remote atualizado para $STORE_PATH"
fi

# ── 5. Concluído ────────────────────────────────────────────────────────
echo ""
info "Setup concluído!"
echo ""
echo "  Salvar senha:    pass insert github/rafael"
echo "  Ver senha:       pass github/rafael"
echo "  Copiar (45s):    pass -c github/rafael"
echo "  Sincronizar:     pass git push"
echo "  Puxar em outro:  pass git pull"
echo ""
info "Antes de remover o pendrive:  pass git push"
