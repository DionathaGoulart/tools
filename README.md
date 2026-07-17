# tools

Coleção de ferramentas de terminal pro meu dia a dia como desenvolvedor. Scripts leves, portáteis e sem dependências — funcionam em macOS, Linux e Windows (Git Bash / WSL).

## Ferramentas

### [cheats](./cheats)
Cheatsheets de comandos que eu sempre esqueço. Mais rápido que abrir o Google.

```bash
cheat tar          # ver colinha
cheat -l           # listar todas
cheat -e docker    # editar ou criar nova
```

Instalação (uma vez):
```bash
# adiciona ao ~/.zshrc, ~/.bashrc ou ~/.bash_profile (Git Bash):
[ -f "$HOME/Desktop/tools/cheats/setup.sh" ] && source "$HOME/Desktop/tools/cheats/setup.sh"
```

> O caminho é detectado automaticamente — se clonar o repo em outro lugar, só ajuste a linha acima.

## [goodpen](./goodpen) — cofre de senhas em duas versões

Dentro de [`goodpen/`](./goodpen) tem **duas** ferramentas pra guardar senhas criptografadas com backup em pendrive. Fazem **a mesma coisa** — mudam só o "como". Escolha uma:

| | [**cofre**](./goodpen/cofre) | [**pendrive**](./goodpen/pendrive) |
|---|---|---|
| O que é | Um programa próprio (binário único) | Guia + script que configuram ferramentas prontas |
| Motor | age (embutido no binário) | `pass` + `gpg` + `git` (instala no sistema) |
| Dependências | **Zero** — só baixar o executável | Precisa instalar 3 programas |
| Windows | Roda nativo (`.exe`) | Só via WSL / Git Bash |
| Interface | Menu no terminal **+ web no navegador** | Linha de comando pura |
| Criptografia | X25519 (age) | RSA 4096 (GPG) — as duas são fortes |
| Backup da chave | **QR code** (cabe no Bitwarden) | Arquivo de ~7KB (sem QR) |
| Esqueceu a passphrase | Recupera com o QR da chave | Perdeu tudo |
| Gera passphrase forte | Sim (`cofre frase`) | Não |
| Apps de celular / browser | Não (formato próprio) | Sim (ecossistema `pass`) |

**Regra rápida:** quer simplicidade, QR e rodar em qualquer sistema sem instalar nada → **cofre**. Quer o padrão consagrado e usar apps de celular/extensão de browser → **pendrive**. São independentes; teste os dois e fique com o que gostar.

### [cofre](./goodpen/cofre) — a versão programinha

```bash
cofre          # menu no terminal
cofre web      # interface no navegador
```

Um executável único (Windows/macOS/Linux), zero dependências, backup da chave por QR code (escaneia e guarda no Bitwarden). Detalhes em [goodpen/cofre/README.md](./goodpen/cofre/README.md).

### [pendrive](./goodpen/pendrive) — a versão "ferramentas Unix"

```bash
bash ~/Desktop/tools/goodpen/pendrive/setup.sh
```

Configura `pass` (password-store) + GPG + git com um pendrive como cofre. Padrão da indústria, integra com apps de celular e browser. Guia completo em [goodpen/pendrive/README.md](./goodpen/pendrive/README.md).

## Estrutura

```
tools/
  cheats/
    cheat            ← o CLI
    setup.sh         ← adiciona ao PATH
    sheets/          ← as colinhas (uma por arquivo)
    compose/         ← docker compose files prontos
  goodpen/           ← cofre de senhas (duas versões)
    cofre/           ← versão programinha (binário único, Go)
      *.go           ← o código
      README.md      ← uso, build e modelo de segurança
    pendrive/        ← versão pass + gpg + git
      setup.sh       ← setup interativo
      README.md      ← guia completo
      cheatsheet     ← colinha do pass
```
