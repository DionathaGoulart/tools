#!/usr/bin/env bash
# setup.sh — configura pass (password-store) com pendrive criptografado
# Funciona em: macOS, Linux, Windows (WSL ou Git Bash com pass instalado)
# Uso: bash setup.sh
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[0;33m'; NC='\033[0m'
info()  { echo -e "${CYAN}::${NC} $1"; }
ok()    { echo -e "${GREEN}✓${NC} $1"; }
warn()  { echo -e "${YELLOW}!${NC} $1"; }
err()   { echo -e "${RED}✗${NC} $1"; }

STORE="$HOME/.password-store"

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
  echo "  macOS:   brew install pass gnupg"
  echo "  Linux:   sudo apt install pass gnupg"
  echo "  Windows: use WSL (sudo apt install pass gnupg) — recomendado."
  echo "           Git Bash já traz gpg e git, mas o pass precisa ser"
  echo "           instalado manualmente: https://git.zx2c4.com/password-store"
  exit 1
fi
ok "Todas as dependências instaladas"

# ── 2. Chave GPG ───────────────────────────────────────────────────────
KEY_COUNT=$(gpg --list-secret-keys --keyid-format LONG 2>/dev/null | grep -c '^sec' || true)

if [ "$KEY_COUNT" -eq 0 ]; then
  echo ""
  info "Nenhuma chave GPG encontrada. Vamos criar uma."
  DEFAULT_NAME="$(git config user.name 2>/dev/null || echo "$USER")"
  DEFAULT_EMAIL="$(git config user.email 2>/dev/null || echo "")"
  read -r -p "  Nome [$DEFAULT_NAME]: " GPG_NAME
  GPG_NAME="${GPG_NAME:-$DEFAULT_NAME}"
  read -r -p "  Email [$DEFAULT_EMAIL]: " GPG_EMAIL
  GPG_EMAIL="${GPG_EMAIL:-$DEFAULT_EMAIL}"
  if [ -z "$GPG_EMAIL" ]; then
    err "Email é obrigatório"
    exit 1
  fi

  echo ""
  warn "Passphrase protege a chave: sem ela, qualquer pessoa com acesso"
  warn "a esta máquina (ou a um backup dela) lê todas as suas senhas."
  read -r -p "  Proteger a chave com passphrase? [S/n]: " USE_PASS
  USE_PASS="${USE_PASS:-S}"

  BATCH_FILE="$(mktemp)"
  trap 'rm -f "$BATCH_FILE"' EXIT
  {
    echo "Key-Type: RSA"
    echo "Key-Length: 4096"
    echo "Subkey-Type: RSA"
    echo "Subkey-Length: 4096"
    echo "Name-Real: $GPG_NAME"
    echo "Name-Email: $GPG_EMAIL"
    echo "Expire-Date: 0"
    case "$USE_PASS" in
      [nN]*) echo "%no-protection" ;;
    esac
    echo "%commit"
  } > "$BATCH_FILE"

  case "$USE_PASS" in
    [nN]*) gpg --batch --gen-key "$BATCH_FILE" ;;
    *)     info "O GPG vai pedir a passphrase agora (janela ou terminal)."
           gpg --batch --pinentry-mode ask --gen-key "$BATCH_FILE" ;;
  esac
  rm -f "$BATCH_FILE"
  trap - EXIT

  KEY_ID=$(gpg --list-secret-keys --keyid-format LONG 2>/dev/null | grep '^sec' | head -1 | awk '{print $2}' | cut -d'/' -f2)
  ok "Chave GPG criada: $KEY_ID"

elif [ "$KEY_COUNT" -eq 1 ]; then
  KEY_ID=$(gpg --list-secret-keys --keyid-format LONG 2>/dev/null | grep '^sec' | head -1 | awk '{print $2}' | cut -d'/' -f2)
  ok "Chave GPG encontrada: $KEY_ID"

else
  echo ""
  info "Você tem $KEY_COUNT chaves GPG. Escolha qual usar:"
  gpg --list-secret-keys --keyid-format LONG | grep -E '^(sec|uid)' | sed 's/^/  /'
  DEFAULT_KEY=$(gpg --list-secret-keys --keyid-format LONG 2>/dev/null | grep '^sec' | head -1 | awk '{print $2}' | cut -d'/' -f2)
  read -r -p "  ID da chave [$DEFAULT_KEY]: " KEY_ID
  KEY_ID="${KEY_ID:-$DEFAULT_KEY}"
  if ! gpg --list-secret-keys "$KEY_ID" >/dev/null 2>&1; then
    err "Chave '$KEY_ID' não encontrada"
    exit 1
  fi
  ok "Usando chave: $KEY_ID"
fi

# ── 3. Inicializar pass + git ──────────────────────────────────────────
if [ ! -d "$STORE" ]; then
  pass init "$KEY_ID"
  ok "pass init"
else
  ok "pass já inicializado"
fi

# pass init NÃO cria repo git — precisa do pass git init
if [ ! -d "$STORE/.git" ]; then
  pass git init >/dev/null
  ok "Repositório git do store criado"
else
  ok "Store já é um repositório git"
fi

# Garante pelo menos 1 commit (necessário pro push)
if ! git -C "$STORE" rev-parse HEAD >/dev/null 2>&1; then
  git -C "$STORE" add -A
  git -C "$STORE" commit -m "Init password store" >/dev/null
fi

BRANCH="$(git -C "$STORE" branch --show-current)"

# ── 4. Pendrive ────────────────────────────────────────────────────────
echo ""
info "Conecte o pendrive agora e digite o caminho dele."
info "  macOS:    /Volumes/MEU_PENDRIVE"
info "  Linux:    /media/$USER/MEU_PENDRIVE"
info "  Git Bash: /e  (letra do drive no Windows)"
info "  WSL:      /mnt/e"
read -r -p "  Caminho do pendrive: " PENDRIVE

if [ ! -d "$PENDRIVE" ]; then
  err "Caminho inválido: $PENDRIVE"
  exit 1
fi
ok "Pendrive montado em $PENDRIVE"

STORE_PATH="$PENDRIVE/pass-store.git"
if [ -d "$STORE_PATH" ]; then
  info "Repositório já existe no pendrive. Conectando..."
else
  git init --bare "$STORE_PATH" >/dev/null
  ok "Repositório criado em $STORE_PATH"
fi

if git -C "$STORE" remote get-url origin >/dev/null 2>&1; then
  git -C "$STORE" remote set-url origin "$STORE_PATH"
  ok "Remote atualizado para $STORE_PATH"
else
  git -C "$STORE" remote add origin "$STORE_PATH"
  ok "Remote configurado"
fi

git -C "$STORE" push --set-upstream origin "$BRANCH"
ok "Push feito (branch: $BRANCH)"

# ── 5. Concluído ───────────────────────────────────────────────────────
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
