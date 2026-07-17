# pendrive — gerenciador de senhas com `pass` + USB

Guia completo pra transformar um pendrive num cofre de senhas criptografado usando [`pass`](https://www.passwordstore.org/) (o gerenciador de senhas oficial do Unix).

## Como funciona

```
pendrive (git bare repo)  ←→  ~/.password-store (local)
         ↕
      GPG (RSA 4096)
```

- As senhas ficam **criptografadas** com sua chave GPG
- O pendrive é o **remote git** — você sincroniza quando conectar
- Dá pra usar o mesmo pendrive em **vários PCs**
- Pode ter **backup no GitHub** também

## Setup rápido

```bash
bash ~/Desktop/tools/goodpen/pendrive/setup.sh
```

O script faz tudo:
1. Verifica dependências (`pass`, `gpg`, `git`)
2. Cria chave GPG se não existir (pergunta se você quer passphrase)
3. Inicializa `pass` **e** o repositório git do store (`pass git init`)
4. Cria repositório git bare no pendrive
5. Conecta e faz primeiro push (detecta o nome da branch automaticamente)

Funciona em macOS, Linux e Windows (WSL recomendado; Git Bash funciona se o `pass` estiver instalado).

## Manual passo a passo

### 1. Instalar dependências

```bash
# macOS
brew install pass gnupg

# Linux (Ubuntu/Debian)
sudo apt install pass gnupg

# Windows — use WSL:
sudo apt install pass gnupg
```

### 2. Criar chave GPG

```bash
gpg --full-generate-key
# Tipo: RSA (4096)
# Expiração: 0 (nunca)
```

> **Passphrase: use uma.** Sem passphrase, qualquer pessoa com acesso à sua
> máquina (ou a um backup dela) lê todas as senhas. Pra não digitar toda hora,
> aumente o cache do gpg-agent em `~/.gnupg/gpg-agent.conf`:
>
> ```
> default-cache-ttl 28800   # 8h
> max-cache-ttl 86400       # 24h
> ```
>
> Digita uma vez por dia só.

### 3. Inicializar `pass`

```bash
gpg --list-secret-keys --keyid-format LONG
# Copia o ID da chave (ex: 3AA5C34371567BD2)
pass init "3AA5C34371567BD2"
pass git init     # ← IMPORTANTE: pass init sozinho NÃO cria o repo git
```

### 4. Configurar pendrive

```bash
# Monta o pendrive e descobre o caminho
# macOS:    /Volumes/MEU_PENDRIVE
# Linux:    /media/usuario/MEU_PENDRIVE
# Git Bash: /e        (letra do drive)
# WSL:      /mnt/e

git init --bare /Volumes/MEU_PENDRIVE/pass-store.git

cd ~/.password-store
git remote add origin /Volumes/MEU_PENDRIVE/pass-store.git
git push --set-upstream origin "$(git branch --show-current)"
# (a branch pode ser master ou main dependendo do seu git config)
```

### 5. Usar

```bash
# Salvar senha
pass insert github.com/DionathaGoulart

# Ver
pass github.com/DionathaGoulart

# Copiar pro clipboard
pass -c github.com/DionathaGoulart

# Gerar senha aleatória
pass generate email/contato 20
```

### 6. Sincronizar

```bash
# Antes de desmontar o pendrive
pass git push

# Em outro PC (com pendrive montado)
pass git pull
```

## Usar em outro PC

```bash
# 1. Importa sua chave GPG (do backup)
gpg --import backup-chave-gpg.asc

# 2. Marca a chave como confiável
gpg --edit-key dionatha.work@gmail.com
# > trust > 5 > y > quit

# 3. Clona do pendrive
git clone /Volumes/MEU_PENDRIVE/pass-store.git ~/.password-store

# Pronto — pass funciona normal
pass
```

## Organização sugerida

```
pass insert github.com/DionathaGoulart
pass insert github.com/pessoal
pass insert email/gmail
pass insert email/trabalho
pass insert server/vps-root
pass insert wifi/casa
pass insert banco/nubank
```

## Segurança

- A chave GPG é a **única porta de entrada** pra suas senhas
- O pendrive sem a chave GPG não adianta nada (tudo criptografado)
- **Perdeu a chave GPG?** Perdeu as senhas. **Faça backup da chave:**

```bash
gpg --export-secret-keys --armor "dionatha.work@gmail.com" > backup-chave-gpg.asc
# Guarda esse arquivo em outro lugar seguro (NÃO no mesmo pendrive)
```

## Backup no GitHub (opcional)

```bash
# GitHub como remote extra
pass git remote add backup https://github.com/DionathaGoulart/pass-backup
pass git push backup "$(git -C ~/.password-store branch --show-current)"
```

> ⚠️ Só faça isso se confiar que o repositório GitHub fica privado. As senhas são criptografadas, mas metadados (nomes dos arquivos) ficam visíveis.

## Estrutura do pendrive

```
MEU_PENDRIVE/
  pass-store.git/   ← repositório git (criado pelo setup)
  (outros arquivos seus)
```

O repositório git é **bare** — não mexe nos seus outros arquivos. Funciona até em pendrive FAT32.

## Comandos úteis

| Comando | Ação |
|---------|------|
| `pass` | listar todas senhas |
| `pass otp github/rafael` | código 2FA — requer a extensão [`pass-otp`](https://github.com/tadfisher/pass-otp) (`brew install pass-otp` / `apt install pass-extension-otp`) |
| `pass grep "banco"` | buscar senha |
| `pass git log --oneline` | histórico de alterações |
| `PASSWORD_STORE_DIR=/Volumes/OUTRO/.password-store pass` | usar outro store |
