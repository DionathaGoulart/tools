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
bash ~/Desktop/tools/pendrive/setup.sh
```

O script faz tudo:
1. Verifica dependências (`pass`, `gpg`, `git`)
2. Cria chave GPG se não existir
3. Inicializa `pass`
4. Cria repositório git no pendrive
5. Conecta e faz primeiro push

## Manual passo a passo

### 1. Instalar dependências

```bash
# macOS
brew install pass gnupg

# Linux (Ubuntu/Debian)
sudo apt install pass gnupg
```

### 2. Criar chave GPG

```bash
gpg --full-generate-key
# Tipo: RSA (4096)
# Nome: DionathaGoulart
# Email: dionatha.work@gmail.com
# Expiração: 0 (nunca)
# Sem passphrase (pra não ter que digitar toda hora)
```

### 3. Inicializar `pass`

```bash
gpg --list-secret-keys --keyid-format LONG
# Copia o ID da chave (ex: 3AA5C34371567BD2)
pass init "3AA5C34371567BD2"
```

### 4. Configurar pendrive

```bash
# Monta o pendrive e descobre o caminho
# macOS: /Volumes/MEU_PENDRIVE
# Linux: /media/usuario/MEU_PENDRIVE

git init --bare /Volumes/MEU_PENDRIVE/pass-store.git

cd ~/.password-store
git remote add origin /Volumes/MEU_PENDRIVE/pass-store.git
git push --set-upstream origin master
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
# Guarda esse arquivo em outro lugar seguro
```

## Backup no GitHub (opcional)

```bash
# GitHub como remote extra
pass git remote add backup https://github.com/DionathaGoulart/pass-backup
pass git push backup master
```

> ⚠️ Só faça isso se confiar que o repositório GitHub fica privado. As senhas são criptografadas, mas metadados (nomes dos arquivos) ficam visíveis.

## Estrutura do pendrive

```
MEU_PENDRIVE/
  pass-store.git/   ← repositório git (criado pelo setup)
  (outros arquivos seus)
```

O repositório git é **bare** — não mexe nos seus outros arquivos.

## Comandos úteis

| Comando | Ação |
|---------|------|
| `pass` | listar todas senhas |
| `pass otp github/rafael` | código 2FA (se configurado) |
| `pass grep "banco"` | buscar senha |
| `pass git log --oneline` | histórico de alterações |
| `PASSWORD_STORE_DIR=/Volumes/OUTRO/.password-store pass` | usar outro store |
