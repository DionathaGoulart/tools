# goodcheats

Vários comandos de utilidade num lugar só, todos da família **good**. Um
`setup.sh` instala a pasta inteira no PATH; cada utilitário é um comando com
prefixo `good`.

| Comando | O que faz |
|---|---|
| [`good`](#good) | fetch de sistema estilo neofetch com o logo good |
| [`goodcheat`](#goodcheat) | cheatsheets de comandos que eu sempre esqueço |
| [`goodharness`](#goodharness) | gerenciador de harness: presets do `.harness/` (bundle), scaffold e config |

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

Gerenciador de harness: presets do `.harness/` pra instalar em projetos. Extraia
o harness de um projeto uma vez, salve como preset versionado aqui no repo, e
scaffolde/instale em qualquer projeto novo — os arquivos vão pro `.harness/`,
onde os skills (Claude Code) leem.

Um preset pode ser **um arquivo** (`<nome>.md`, legado → `styleguide.md`) ou um
**bundle** (diretório `<nome>/` com `styleguide*.md`, `rules/`, …). O bundle
captura o harness inteiro, não só um arquivo.

### Uso

```bash
good harness init .                                  # scaffold de um .harness/ padrão (config, memory, plans)
good harness init . --from portfolio-dev             # scaffold já semeando de um preset
good harness list                                    # lista presets (bundle/file)
good harness copy portfolio-dev ~/Desktop/Portfolio  # salva o .harness/ do projeto como bundle
good harness install portfolio-dev ~/dev/site-novo   # instala no projeto (cria .harness/ se precisar)
good harness show portfolio-dev                      # arquivos + metadata do preset
good harness rm portfolio-dev                        # remove (pede confirmação)
good harness config show .                           # imprime o .harness/config.json
good harness config set tracker_team PROD .          # edita um campo (via jq)
good harness install portfolio-dev . --link          # symlink em vez de cópia (update do preset propaga)
good harness diff portfolio-dev .                    # compara preset x instalado (exit 1 se difere)
good harness update portfolio-dev .                  # atualiza o projeto a partir do preset
good harness sync portfolio-dev                      # reaplica o preset em todos os projetos que o usam
good harness status                                  # árvore preset -> projetos (mode, data)
```

- `init [dest] [--from <preset>]` — cria `<dest>/.harness/` com `config.json`
  (template), `styleguide.md` placeholder, `memory/` e `plans/`. Não sobrescreve
  o que já existe.
- `copy <nome> [origem] [--files a,b]` — origem = arquivo `.md` (preset legado)
  ou diretório de projeto (vira **bundle**, capturando `styleguide*.md` + `rules/`;
  `config.json` **não** é capturado, pra não vazar valores do projeto). `--files`
  escolhe explicitamente o que entra no bundle.
- `install <nome> [destino]` — derrama os arquivos do preset em
  `<destino>/.harness/`. O `config.json` do projeto é **preservado** (merge via
  `jq`, valores existentes vencem; só entram chaves novas). Grava um recibo
  `.goodharness.json`.
- `config <show|get KEY|set KEY VAL> [dest]` — lê/edita `.harness/config.json`
  (campos: `tracker_team`, `tracker_project`, `prd`, `client`, `stack`, …).
  `get`/`set` precisam do `jq`; `show` funciona sem.
- `install ... --link` — symlinka os arquivos do preset em vez de copiar. Editar
  o preset propaga na hora pros projetos linkados (o `config.json` continua real e
  com merge — nunca é symlink). Trade-off: não mova o diretório de presets.
- `diff <nome> [dest]` — compara os arquivos do preset com o instalado no
  `.harness/` (exit `1` se houver drift; útil em script/CI).
- `update <nome> [dest]` — reinstala do preset (força), respeitando o modo do
  install anterior (cópia ou link). O `config.json` do projeto é preservado.
- `sync [preset]` / `status` — o goodharness registra cada install num
  `registry.json` (em `~/.goodharness`, ou `GOODHARNESS_STATE`). `sync` reaplica
  um preset (ou todos) em cada projeto registrado, pulando os que sumiram;
  `status` mostra a árvore preset → projetos com modo e data.
- `--force` sobrescreve (faz backup `.bak` antes). Vale pra `copy`/`install`.

> **Dependência opcional:** `jq`. Sem ele, `config.json` sai do template cru (sem
> merge), `config get/set` avisam que precisam do `jq`, e `sync`/`status` (que
> dependem do registry JSON) ficam indisponíveis. Bundle, `init`, `copy`,
> `install`, `diff` e `update` funcionam sem `jq`.

### Presets

Ficam em [`styleguides/`](./styleguides) — cada entrada é um `.md` (legado) ou um
diretório de bundle, versionado junto com o repo tools.

| Preset | Origem | Estética |
|---|---|---|
| [portfolio-dev](./styleguides/portfolio-dev.md) | Portfolio, página `/dev` | Retro terminal neo-brutalista: JetBrains Mono, bordas 2px, sombras offset, paletas Abyss Frost / Vault Gold |

### Fluxo típico

1. Projeto novo? `good harness init .` — nasce com `.harness/` completo.
2. Tem um visual/harness pra reaproveitar? `good harness copy meu-tema ~/caminho/do/site`
3. Instala em outro: `good harness install meu-tema .` (config do projeto é preservado).
4. Ajusta o tracker: `good harness config set tracker_team TEAM .`
5. O Claude Code (skills `prod:*`) lê `.harness/` e implementa seguindo os tokens.

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
