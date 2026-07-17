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

### [pendrive](./pendrive)
Guia completo pra usar `pass` (password-store) com um pendrive como cofre de senhas criptografado.

```bash
bash ~/Desktop/tools/pendrive/setup.sh
```

### [cofre](./cofre)
O mesmo cofre de senhas em versão **programinha**: um executável único (Windows/macOS/Linux), zero dependências, menu no terminal + interface no navegador, backup da chave por QR code (escaneia e guarda no Bitwarden).

```bash
cofre          # menu no terminal
cofre web      # interface no navegador
```

## Estrutura

```
tools/
  cheats/
    cheat            ← o CLI
    setup.sh         ← adiciona ao PATH
    sheets/          ← as colinhas (uma por arquivo)
    compose/         ← docker compose files prontos
  pendrive/
    setup.sh         ← setup interativo do pass + pendrive
    README.md        ← guia completo
    cheatsheet       ← colinha do pass
  cofre/
    *.go             ← o programinha (Go, binário único)
    README.md        ← uso, build e modelo de segurança
```
