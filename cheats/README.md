# cheats — colinhas de terminal

Cheatsheets organizadas por tópico. Bater o olho e lembrar.

## Uso

```bash
cheat tar          # ver colinha
cheat -l           # listar todas (com descrição)
cheat -e docker    # editar/criar
cheat -h           # ajuda
```

Se `bat` estiver instalado, usa ele pra exibir; senão, `cat`.

## Instalação

```bash
bash ~/Desktop/tools/cheats/setup.sh
```

Isso adiciona a linha de `source` no seu `~/.zshrc` (ou `~/.bashrc`). Depois abra um terminal novo ou rode `source ~/.zshrc`. O `setup.sh` detecta o próprio caminho — funciona de qualquer lugar que o repo esteja clonado.

## Estrutura

```
cheats/
  cheat        ← o CLI
  setup.sh     ← adiciona esta pasta ao PATH
  sheets/      ← as colinhas (uma por arquivo, sem extensão)
  compose/     ← docker compose files usados pela sheet compose-recipes
```

## Adicionar nova colinha

```bash
cheat -e meu-comando
```

Ou crie um arquivo em `sheets/`. Dica: comece o arquivo com `# descrição` — a primeira linha aparece no `cheat -l`.

## Sheets disponíveis

```bash
cheat -l
```

(a lista vem dos arquivos em `sheets/` — sempre atualizada)
