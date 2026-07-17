# tools/ — utilitários de terminal

Coleção de scripts e cheatsheets portáteis pra macOS, Linux e Windows (Git Bash).

## Estrutura

```
tools/
  cheat       — visualizador de cheatsheets
  setup.sh    — adiciona tools/ ao PATH
  cheats/     — coleção de cheatsheets
    tar
    git
    docker
    network
    compose-recipes
```

## Uso rápido

### 1. Adicionar ao PATH (uma vez)

No **~/.zshrc**, **~/.bashrc** ou **~/.bash_profile**:

```bash
source ~/Desktop/tools/setup.sh
```

Depois recarregue: `source ~/.zshrc`

### 2. Usar

```bash
cheat tar          # ver cheatsheet de tar
cheat git          # ver cheatsheet de git
cheat -l           # listar todas
cheat -e docker    # editar ou criar uma nova
```

## Adicionar novas cheatsheets

```bash
cheat -e meu-comando
```

Ou crie manualmente um arquivo em `tools/cheats/`.

## Windows

Funciona no **Git Bash** (incluso no Git for Windows). No PowerShell, use `wsl` ou o Git Bash.
