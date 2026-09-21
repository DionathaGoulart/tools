# Style guide: terminal (edição CLI)

Como a base ([styleguide.md](styleguide.md), neobrutalismo de terminal retrô) vira saída de linha
de comando. Toda ferramenta tem que parecer o mesmo produto: mesma paleta, mesma caixa, mesmos
rótulos, mesma voz.

Implementação de referência: a lib compartilhada do repositório de ferramentas, `lib/retro.sh`
(bash) e `lib/retro.py` (python). Ferramenta nova usa a lib; não redesenha os componentes à mão.

## 1. Tokens

Três hex por paleta, `fundo`, `texto` e `accent`, exatamente os do catálogo da base (§3:
`base-100`, `base-content`, `accent`). Todo o resto é derivado misturando o accent sobre o fundo,
e é assim que os degraus `accent/5 /10 /20 /30 /50` do web sobrevivem num terminal.

| Token | Equivalente web | Uso |
|---|---|---|
| `ACC` | `text-accent` | bordas, títulos, valores, marcadores |
| `ACC70` / `ACC50` | `accent/70` `/50` | texto de chrome, pontos secundários |
| `ACC30` | `accent/30` | prompt `>`, meta, hairlines |
| `ACC15` | `accent/10` a `/20` | sombra, pontilhado do kv, trilho vazio da barra (mistura a 18%) |
| `FG` / `FG70` / `FG40` | `base-content` 100 / 70 / 40% | corpo, rótulo apagado |
| `INV` | `bg-accent` | barra de status, linha ativa (texto na cor do fundo) |
| `OK` / `ALERTA` | `success` / `error` | `[ OK ]`, `[ ERRO ]`: só esses dois |

`OK` (`#3fb950`) e `ALERTA` (`#e5534b`) são as duas únicas cores fora da paleta, e moram só na
lib (a regra "uma cor existe uma única vez" vale para o CLI com a lib no papel do `palettes.css`).

> Divergência resolvida: o guia de origem citava `green-500` / `red-500` do Tailwind; vale o hex
> que a lib implementa. Unificar com os `-soft` do catálogo web exige mudar a lib primeiro.

Paletas: env `<PREFIXO>_TEMA` (definido pela ferramenta), depois `RETRO_TEMA`, e por fim o default
`vault-gold`. Ids iguais aos da base: `vault-gold` `noir-rose` `midnight-ember` `cyber-teal`
`velvet-purple` `abyss-frost` `crimson-chalk` `forest-mist` `sand-dusk`. Nome desconhecido cai no
default. A lib implementa 9 das 10 paletas do catálogo; `neon-matrix` entra com os mesmos hex da
base quando alguma ferramenta pedir.

> Divergência resolvida: o web usa o par `crimson-chalk`/`noir-rose`; o CLI mantém `vault-gold`,
> porque o terminal não informa se o fundo é claro ou escuro, o escuro é o caso comum e é o que a
> lib implementa.

Degradação obrigatória: 24 bits quando `COLORTERM` diz `truecolor`/`24bit`; 8 cores ANSI no resto
(accent vira amarelo, `INV` vira vídeo reverso, `OK`/`ALERTA` viram verde e vermelho); zero
escapes com `NO_COLOR` ou quando stdout não é tty. O layout continua legível com todo escape
removido. No Windows a saída é forçada a UTF-8 e o processamento VT é ligado.

Contraste: `FG40`, `ACC30` e `ACC15` são apagados de propósito e ficam abaixo de 4.5:1. Servem a
chrome, chave de kv e meta; o dado em si vai em `FG`, `ACC` ou negrito. Em paleta clara, `OK` e
`ALERTA` também ficam abaixo de 4.5:1, e a palavra entre colchetes é que carrega o sentido.

## 2. Tipografia vira caixa

Terminal não tem fonte, então a identidade "tudo JetBrains Mono, caixa alta, tracking largo" vira
**caixa e estrutura**:

- Rótulos, cabeçalhos, chaves, status, chips: `CAIXA ALTA`.
- Identificadores: `snake_case` / `dot.case` (`focus_timer`, `root@<ferramenta>: ~/foco`).
- Texto corrido: caixa normal, conteúdo em pt-BR; jargão de terminal fica como é.
- Ênfase = `ACC` + negrito, nunca outra cor.
- Emoji: no máximo um por tela, e só onde carrega sentido (um tomate numa sessão de foco). Nunca
  como decoração ou bullet: colchetes e marcadores fazem esse trabalho.

## 3. Componentes

Use os helpers da lib; não reimplemente. Nomes entre parênteses: bash (`retro_*`) / python
(`ui.*`).

### Janela (`retro_topo` + `chrome` + `sep` + `linha` + `status` + `base` + `sombra` / `ui.janela`)

Exemplo (um timer de foco):

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ● ● ●  root@pomo: ~/foco                 PID: 12 ┃▒
┠──────────────────────────────────────────────────┨▒
┃ [ MODULE: FOCUS_TIMER ]              SEM ROTULO  ┃▒
┃                                                  ┃▒
┃ ████████████████▒▒▒▒▒▒▒▒                    62%  ┃▒
┠──────────────────────────────────────────────────┨▒
┃ [P] PAUSAR · [Q] SAIR              ● EM EXECUCAO ┃▒
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛▒
 ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
```

Box-drawing pesado = a borda de 2px. A coluna de `▒` à direita e a linha embaixo = a sombra dura
`6px 6px 0` (accent a cerca de 18%). Cantos retos, sempre. Os três pontos do chrome são o
WindowDots da skin terminal (`ACC`, `ACC50`, `ACC30`). A barra de status usa `INV`. Largura
padrão 52; abaixo de 46 colunas, ou sem tty, cai para linhas planas. Quando falta espaço, o
título cede antes da meta, e o lado esquerdo do status cede antes do direito.

### Cabeçalho de módulo (`retro_modulo` / `ui.modulo("focus_stats", "src: log.csv")`)

`[ MODULE: FOCUS_STATS ]` em accent negrito, com meta apagada opcional à direita. É a forma CLI do
cabeçalho de card de módulo. Toda saída de comando abre com um.

### Label de seção (`retro_secao` / `ui.secao("ultimos 14 dias")`)

Vira `# ULTIMOS 14 DIAS` em accent.

### Chave-valor (`retro_kv` / `ui.kv("SEQUENCIA", "7 DIA(S)")`)

```
  SEQUENCIA ···························· 7 DIA(S)
```

Chave apagada (`FG40`), pontilhado em `ACC15`, valor em accent negrito. Substitui toda linha
`rótulo: valor` do repositório.

### Linhas de status e resultado (`ok`, `erro`, `aviso`, `proximo`)

`[ OK ] TEXTO` (colchete verde, texto em accent negrito) · `[ ERRO ] texto` · `[ VAZIO ]`,
`[ ABORTADO ]` e afins em `FG40`. Dica de próximo passo: `> proximo passo:  comando`, com `>`
apagado e o comando em accent negrito.

### Barras de progresso e histograma (`retro_barra` / `ui.barra(feito, total)`)

`█` preenchido em accent, `▒` de trilho em `ACC15`, porcentagem em accent negrito. Os mesmos
glifos servem ao histograma por dia; a linha de hoje leva `►`.

### Linhas de lista (`ui.item("►", texto, meta)`)

Linha inativa em `FG70`, linha ativa em `INV` (fundo accent). Meta falso-precisa (`-rwxr-xr-x`,
`4.2K`, `PID: 001`) em `FG40`/`ACC30`: sabor, não dado.

### Chips e tags (`ui.chip("SPOILER")`)

Vira `[SPOILER]`: colchetes apagados, texto em accent.

### Catálogo de temas (`retro_catalogo_temas` / `ui.catalogo_temas()`)

Tela compartilhada de escolha de paleta: cabeçalho `[ MODULE: THEME_CATALOG ]`, uma linha por
paleta com amostra (accent, texto, fundo), `►` na ativa e a dica `export <PREFIXO>_TEMA=<nome>`.

## 4. Motion

- Entrada é só fade e deslize: revelar linha a linha com cerca de 12ms entre linhas. Sem bounce,
  sem spring, sem overshoot, sem spinner que pula.
- Movimento ambiente permitido: bloco de cursor piscando, ponto de status pulsando (`●`/`◍`),
  cabeça da barra de progresso alternando `█`/`▓`.
- Redesenho movendo o cursor N linhas para cima e repintando com `\033[K`; nunca limpar a tela
  inteira no meio da sessão.
- Toda animação é pulada sem tty, com `NO_COLOR` ou com `<PREFIXO>_SEM_ANIM`.

> Divergência resolvida: o web proíbe pulso (base §8), o CLI permite o ponto de status pulsando.
> Mantido no CLI: num terminal é o único sinal de "vivo" que não depende de redesenhar a tela.

## 5. Voz

Narrativa de terminal: prompts `>` e `$`, caminhos `root@<ferramenta>: ~/<area>`, `# TITULOS`,
`[ OK ]`, `[ MODULE: X ]`, `PID`, `SRC:`. Rótulos em SCREAMING_SNAKE; explicações em pt-BR; o
jargão de sistema (`MODULE`, `PID`, `SRC`) fica em inglês, como na base.

## 6. Faça / não faça

- FAÇA passar toda cor pelos tokens: nenhum `\033[1;35m` cru em lugar nenhum.
- FAÇA caixa alta em tudo que é rótulo; FAÇA cantos retos.
- FAÇA checar `-t 1` / `isatty` antes de desenhar caixa ou animar.
- NÃO introduza cores novas (cabeçalho roxo, ciano ou magenta acabou), gradientes ou cantos
  arredondados.
- NÃO use emoji como bullet ou decoração.
- NÃO imprima `rótulo: valor` cru; use `kv`.
