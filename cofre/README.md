# cofre — gerenciador de senhas em um único arquivo

Versão "programinha" do cofre de senhas: **um executável só, zero dependências**, roda em Windows, macOS e Linux. Criptografia [age](https://age-encryption.org) (X25519 — moderna, auditada), sincronização com pendrive e backup da chave por **QR code** embutidos.

É a evolução do setup [pendrive/](../pendrive) (`pass` + GPG): mesma ideia, mas sem precisar instalar `pass`, `gpg` nem `git` — tudo dentro do binário.

## Instalar

Baixe (ou compile) o binário do seu sistema e coloque no PATH:

| Sistema | Binário |
|---------|---------|
| Windows | `cofre-windows.exe` |
| macOS (M1/M2/M3) | `cofre-mac-m1` |
| macOS (Intel) | `cofre-mac-intel` |
| Linux | `cofre-linux` |

Compilar do código (requer Go):

```bash
cd cofre
go build -o cofre .                      # pro seu sistema
GOOS=windows GOARCH=amd64 go build .     # cross-compile
```

## Usar

```bash
cofre            # menu interativo no terminal
cofre web        # abre a interface no navegador (mesmo cofre)
```

Primeira vez → o menu te guia: criar cofre novo (gera a chave e já oferece o backup em QR) ou restaurar de um backup existente.

### Comandos diretos

```bash
cofre init             # cria um cofre novo
cofre restore          # restaura da chave (QR/arquivo/papel)

cofre ls               # lista
cofre add banco/nu     # salva senha digitada (não pede passphrase!)
cofre gen banco/nu 24  # gera aleatória de 24 chars e copia
cofre get banco/nu     # mostra (pede passphrase)
cofre cp banco/nu      # copia pro clipboard, limpa em 45s
cofre rm banco/nu      # apaga

cofre push             # backup → pendrive (lembra o caminho)
cofre pull             # pendrive → máquina
cofre qr               # backup da chave: QR no terminal, PNG ou texto
cofre frase            # sugere passphrases fortes (diceware PT-BR, crypto/rand)
```

Detalhe legal: **salvar senha não pede passphrase** (criptografa com a chave pública). Só **ler** exige destrancar.

## Como funciona por dentro

```
~/.cofre/
├── key.pub      chave pública (tranca) — viaja pro pendrive, sem perigo
├── key.age      chave secreta (destranca) — criptografada com sua passphrase
├── config.json  caminho do pendrive lembrado
└── store/
    └── banco/nubank.age   cada senha = um arquivo criptografado
```

- **Criptografia**: age X25519. Cada entrada é um arquivo `.age` trancado pela chave pública; ler exige a chave secreta, que só destranca com a passphrase (scrypt).
- **Pendrive**: `cofre push` espelha `store/` + `key.pub` em `<pendrive>/cofre/`. A chave secreta NUNCA vai pro pendrive. Sincronização é "união, mais novo vence" — nada é apagado automaticamente.
- **QR da chave**: a chave age tem ~74 caracteres — cabe num QR pequeno. Escaneia com o celular e guarda numa nota segura do Bitwarden/1Password, ou imprime. (Era impossível com GPG/RSA: ~7KB não cabem em QR.)
- **Interface web**: `cofre web` sobe um servidor **só em 127.0.0.1** com token aleatório na URL e abre o navegador. Nada sai da máquina; fechou o terminal, morreu o servidor.

## Modelo de segurança

| Cenário | Resultado |
|---------|-----------|
| Perdeu o pendrive | Ok — só arquivos criptografados + chave pública. Ninguém lê nada |
| Perdeu o PC | Ok SE tem backup da chave — `cofre restore` + `cofre pull` recupera tudo |
| Roubaram o PC ligado | Passphrase protege — a chave secreta em disco está criptografada |
| Perdeu a chave E o backup | Perdeu as senhas. Sem recuperação — faça o backup no primeiro dia |
| Esqueceu a passphrase | Restaure com o backup da chave (`cofre restore` pede passphrase nova) |

> Diferente do GPG: se você esquecer a passphrase mas TIVER o backup da chave (QR/papel/Bitwarden), não perdeu nada — a chave do backup é a chave "crua", e o `restore` deixa você escolher uma passphrase nova.

## cofre vs pendrive/ (pass + GPG)

| | `cofre` | `pass` + GPG |
|---|---|---|
| Dependências | zero | pass, gpg, git |
| Windows | binário nativo | WSL/Git Bash |
| Backup de chave por QR | ✅ (~74 chars) | ❌ (RSA não cabe) |
| Interface web local | ✅ | ❌ |
| Histórico git completo | ❌ (espelho simples) | ✅ |
| Ecossistema (apps celular, extensões) | ❌ | ✅ |

Os dois cofres são independentes — use o que preferir.
