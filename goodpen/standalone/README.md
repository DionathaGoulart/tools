# cofre — gerenciador de senhas em um único arquivo

Versão "programinha" do cofre de senhas: **um executável só, zero dependências**, roda em Windows, macOS e Linux. Criptografia [age](https://age-encryption.org) (X25519 — moderna, auditada), sincronização com pendrive e backup da chave por **QR code** embutidos.

É a evolução do setup [pass-store/](../pass-store) (`pass` + GPG): mesma ideia, mas sem precisar instalar `pass`, `gpg` nem `git` — tudo dentro do binário.

## Instalar

Compile (requer [Go](https://go.dev/dl/)) e coloque o binário no PATH:

```bash
cd goodpen/standalone
go build -o cofre .        # só pro seu sistema
bash build.sh              # ou todas as plataformas de uma vez → dist/
```

O `build.sh` gera em `dist/` (a pasta não é versionada — os binários são
buildados localmente):

| Sistema | Binário |
|---------|---------|
| Windows | `cofre-windows.exe` |
| macOS (Apple Silicon) | `cofre-mac-m1` |
| macOS (Intel) | `cofre-mac-intel` |
| Linux | `cofre-linux` |

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
cofre temas            # lista as paletas disponíveis
```

### Aparência

A interface do terminal segue o [style guide retro](../../.harness/styleguide-terminal.md):
caixa de borda pesada, cantos retos, rótulos em maiúsculas e uma cor de destaque só.

```bash
cofre temas                    # catálogo das 9 paletas (► marca a ativa)
export COFRE_TEMA=cyber-teal   # tema só do cofre
export RETRO_TEMA=noir-rose    # tema de todas as ferramentas (fallback)
```

Temas: `vault-gold` (padrão) · `noir-rose` · `midnight-ember` · `cyber-teal` ·
`velvet-purple` · `abyss-frost` · `crimson-chalk` · `forest-mist` · `sand-dusk`.

`COFRE_TEMA` tem prioridade sobre `RETRO_TEMA`. As cores somem sozinhas com
`NO_COLOR` ou quando a saída não é um terminal (pipe, arquivo, script).

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

## cofre vs pass-store (pass + GPG)

Comparação completa das duas versões no [README do goodpen](../README.md).
Resumo: o `cofre` ganha em simplicidade (zero dependências, Windows nativo,
QR, interface web); o `pass` ganha em ecossistema (apps de celular, extensões
de browser, histórico git). São independentes — use o que preferir.

---

↩ [goodpen](../README.md) · [índice de ferramentas](../../README.md)
