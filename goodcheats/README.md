# goodcheats

Vários comandos de utilidade num lugar só, todos da família **good**. Um
`setup.sh` instala a pasta inteira no PATH; cada utilitário é um comando com
prefixo `good`.

| Comando | O que faz |
|---|---|
| [`good`](#good) | fetch de sistema estilo neofetch com o logo good |
| [`goodcheat`](#goodcheat) | cheatsheets de comandos que eu sempre esqueço |
| [`goodharness`](#goodharness) | biblioteca de styleguides pra instalar em projetos |

Todo comando da família também roda como subcomando do `good`:
`good cheat tar` = `goodcheat tar` · `good harness list` = `goodharness list`.

Os três seguem o [style guide de terminal](../.harness/styleguide-terminal.md) —
mesma paleta, mesmos rótulos, mesmas linhas key-value — via a lib compartilhada
[`lib/retro.sh`](../lib/retro.sh). O tema vem de `GOOD_TEMA` (ou `RETRO_TEMA`),
padrão `vault-gold`; veja as paletas com `good temas`. `NO_COLOR` e saída sem
tty caem pra texto puro.

## Instalação (uma vez)

```bash
bash ~/Desktop/tools/goodcheats/setup.sh
```

Isso adiciona a linha de `source` no seu `~/.zshrc` (ou `~/.bashrc`). Depois
abra um terminal novo ou rode `source ~/.zshrc`.

> Rodar `bash setup.sh` sozinho não muda o PATH do terminal atual — subshell
> não altera o shell pai. Por isso ele instala a linha no rc e avisa. O caminho
> é detectado automaticamente, funciona com o repo clonado em qualquer lugar.

> Migrando das pastas antigas `good/` e `cheats/`? As linhas velhas no rc são
> inofensivas (têm guarda `[ -f … ]` e param de fazer efeito), mas pode
> removê-las. O comando `cheat` agora chama `goodcheat`.

---

## good

Fetch de sistema estilo neofetch, com o logo good em ASCII art. Digite `good` e veja o logo colorido ao lado das infos da máquina (OS, kernel, uptime, CPU, GPU, memória, disco, pacotes, bateria).

```
  [ MODULE: SYSTEM_INFO ]  RAFAEL@MACBOOKAIR

      ▄████████      ████████▄         OS ······················ macOS 26.2 arm64
      █████████      █████████         HOST ······ MacBook Air (MacBookAir10,1)
      █████████      █████████         KERNEL ······················ Darwin 25.2.0
▄▄▄▄▄▄████████████████████████▄▄▄▄▄▄   UPTIME ······························ 7h 49m
████████▀  ▀████████████▀  ▀████████   SHELL ······························ zsh 5.9
████████    ████████████    ████████   DISPLAY ················ 2560 x 1600 Retina
████████    ████████████    ████████   TERM ·························· WarpTerminal
▀██████████████████████████████████▀   CPU ································ Apple M1
      ████████████████████████         GPU ································ Apple M1
      █████████▀▀▀▀▀▀█████████         MEMORY ·········· 5.3 GiB / 8.0 GiB (66%)
  ▄▄▄▄█████████▄▄▄▄▄▄█████████▄▄▄▄     DISK ···················· 190G / 245G (93%)
█████████▀▀▀▀██████████▀▀▀▀█████████   PKGS ················· 174 (brew), 1 (cask)
████████      ████████      ████████   BATTERY ················ 67% (discharging)
████████      ████████      ████████
████████      ▀███████      ████████   ████████████████████
```

### Uso

```bash
good              # logo + infos
good temas        # paletas disponíveis (marca a atual)
good -c fbee23    # logo em cor sólida (6 dígitos hex, com ou sem #)
good -c fbee23,ff5500  # gradiente entre duas cores
good --refresh    # refaz o cache de hardware (modelo, GPU, resolução)
good -h           # ajuda
```

### Como funciona

- Script bash puro, sem dependências. Funciona em macOS e Linux.
- No macOS, as infos lentas (`system_profiler`: modelo, GPU, resolução) são coletadas **uma vez** e cacheadas em `~/.cache/good/hardware` — as execuções seguintes levam ~0.1s. Trocou de monitor? Roda `good --refresh`.
- Logo sai no accent do tema atual por padrão (`vault-gold` → `#c8a96e`); `-c`/`GOOD_COLOR` sobrescreve com qualquer hex (ex: o amarelo good `#fbee23`). Em terminais com truecolor (`COLORTERM=truecolor`) a cor é exata; sem truecolor, aproxima pro palette 256 (gradiente incluso). Respeita `NO_COLOR`.
- As infos saem como linhas key-value do style guide: chave em UPPERCASE dim, dot leader, valor em accent-bold.
- **Responsivo**: se o terminal for estreito demais pro layout lado a lado, o logo vai centralizado em cima e as infos embaixo. Estreito demais até pro logo (< 36 colunas)? Só as infos.

### Personalização

```bash
good -c fbee23           # cor sólida via flag
GOOD_COLOR=fbee23        # ou via env (ex: no ~/.zshrc, pra virar padrão)
GOOD_COLOR=fbee23,ff5500 # duas cores = gradiente
GOOD_TEMA=cyber-teal     # paleta retro dos três comandos (good, goodcheat, goodharness)
```

Sem `-c`/`GOOD_COLOR`, o logo acompanha o accent de `GOOD_TEMA`. Rode
`good temas` pra ver as nove paletas.

O logo em ASCII foi gerado a partir de `logo.svg` (rasterizado e amostrado em half-blocks `▀▄█`). O SVG original fica em [`logo.svg`](./logo.svg).

---

## goodcheat

Cheatsheets organizadas por tópico. Bater o olho e lembrar.

### Uso

```bash
goodcheat tar          # ver colinha
goodcheat -l           # listar todas (com descrição)
goodcheat -s porta     # buscar um termo dentro de todas as colinhas
goodcheat -e docker    # editar/criar
goodcheat -h           # ajuda
```

Se `bat` estiver instalado, usa ele pra exibir; senão, `cat`. Errou o nome?
Ele sugere os parecidos (`goodcheat dock` → `# VOCE QUIS DIZER · ► DOCKER`).
O `-s` mostra os hits agrupados por colinha, com o termo realçado em accent.

### Adicionar nova colinha

```bash
goodcheat -e meu-comando
```

Ou crie um arquivo em `sheets/`. Dica: comece o arquivo com `# descrição` — a
primeira linha aparece no `goodcheat -l`.

---

## goodharness

Biblioteca de styleguides pré-definidos. Extraia o styleguide de um projeto uma
vez, salve como predefinição versionada aqui no repo, e instale em qualquer
projeto novo com um comando — o arquivo vai pra `.harness/styleguide.md`, onde
os skills do harness (Claude Code) leem.

### Uso

```bash
good harness list                                    # lista predefinições
good harness copy portfolio-dev ~/Desktop/Portfolio  # salva styleguide do projeto como predefinição
good harness install portfolio-dev ~/dev/site-novo   # instala no projeto (cria .harness/ se precisar)
good harness show portfolio-dev                      # imprime a predefinição
good harness rm portfolio-dev                        # remove (pede confirmação)
```

- `copy <nome> [origem]` — origem pode ser um arquivo `.md` direto ou um
  diretório de projeto (procura `.harness/styleguide.md`, depois
  `styleguide.md`). Padrão: diretório atual.
- `install <nome> [destino]` — destino é o diretório do projeto; escreve em
  `<destino>/.harness/styleguide.md`. Padrão: diretório atual.
- `--force` sobrescreve arquivo existente (vale pra `copy` e `install`).

### Predefinições

Ficam em [`styleguides/`](./styleguides) — um `.md` por tema, versionado junto
com o repo tools.

| Predefinição | Origem | Estética |
|---|---|---|
| [portfolio-dev](./styleguides/portfolio-dev.md) | Portfolio, página `/dev` | Retro terminal neo-brutalista: JetBrains Mono, bordas 2px, sombras offset, paletas Abyss Frost / Vault Gold |

### Fluxo típico

1. Fez um site com um visual que quer reaproveitar? `good harness copy meu-tema ~/caminho/do/site`
2. Começou um projeto novo? `good harness install meu-tema .`
3. O Claude Code (skills `prod:*`) lê `.harness/styleguide.md` e implementa seguindo os tokens.

---

## Estrutura

```
goodcheats/
  setup.sh     ← adiciona esta pasta ao PATH (instala todos os comandos)
  good         ← fetch de sistema com logo (+ dispatcher: good <sub> → good<sub>)
  logo.svg     ← o logo original
  goodcheat    ← cheatsheets
  sheets/      ← as colinhas (uma por arquivo, sem extensão)
  compose/     ← docker compose files usados pela sheet compose-recipes
  goodharness  ← biblioteca de styleguides
  styleguides/ ← as predefinições de styleguide (uma por .md)
```

Novo utilitário? Cria o script com prefixo `good` na raiz da pasta — o
`setup.sh` já cobre (a pasta inteira está no PATH).

---

↩ [Voltar pro índice de ferramentas](../README.md)
