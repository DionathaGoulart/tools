# Style Guide — Terminal (retro terminal, CLI edition)

How `.harness/styleguide.md` (the web `portfolio-dev` neo-brutalist retro terminal)
maps onto the CLI tools in this repo. Every tool in `tools/` must look like the same
product: same palette, same box, same labels, same voice.

Reference implementation: `pomo/pomo` (bash) · shared code: `lib/retro.sh`, `lib/retro.py`.

## 1. Tokens

Three hex values per theme — `background`, `foreground`, `accent` — exactly the
palettes from the web guide. Everything else is derived by alpha-blending the accent
over the background, which is how the web guide's `accent/5 /10 /20 /30 /50` steps
survive in a terminal.

| token | web equivalent | use |
|---|---|---|
| `ACC` | `text-accent` | borders, titles, values, markers |
| `ACC70` / `ACC50` | `accent/70` `/50` | chrome text, secondary dots |
| `ACC30` | `accent/30` | prompts `>`, meta, hairlines |
| `ACC15` | `accent/10..20` | shadow, dot leaders, empty bar track |
| `FG` / `FG70` / `FG40` | `foreground/100 /70 /40` | body copy, dim labels |
| `INV` | `bg-accent text-white` | status bar, active row |
| `OK` / `ALERTA` | `green-500` / `red-500` | `[ OK ]`, `[ ERRO ]` — only these two |

Themes (env `<TOOL>_TEMA`, fallback `RETRO_TEMA`, default `vault-gold`):
`vault-gold` `noir-rose` `midnight-ember` `cyber-teal` `velvet-purple`
`abyss-frost` `crimson-chalk` `forest-mist` `sand-dusk`.

Degradation is mandatory: 24-bit when `COLORTERM` says so, 8-color ANSI otherwise,
zero escapes under `NO_COLOR` or when stdout is not a tty. Layout must stay readable
with every escape stripped.

## 2. Typography → casing

No fonts in a terminal, so the "all JetBrains Mono, uppercase, wide tracking" identity
becomes **casing and structure**:

- Labels, headers, keys, statuses, chips: `UPPERCASE`.
- Identifiers: `snake_case` / `dot.case` (`focus_timer`, `root@pomo: ~/focus`).
- Body copy: normal case, pt-BR content, en-US system labels.
- Emphasis = `ACC` + bold, never a different color.
- Emoji: at most one per screen, and only where it carries meaning (`🍅` for a focus
  session). Never as decoration or bullets — brackets and markers do that job.

## 3. Components

Use the shared helpers; do not hand-roll these.

### Terminal window — `janela` / `topo`+`chrome`+`sep`+`linha`+`status`+`base`+`sombra`
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ● ● ●  root@pomo: ~/focus                PID: 12 ┃▒
┠──────────────────────────────────────────────────┨▒
┃ [ MODULE: FOCUS_TIMER ]              SEM ROTULO  ┃▒
┃                                                  ┃▒
┃ ████████████████▒▒▒▒▒▒▒▒                    62%  ┃▒
┠──────────────────────────────────────────────────┨▒
┃ [P] PAUSAR · [Q] SAIR              ● EM EXECUCAO ┃▒
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛▒
 ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
```
Heavy box-drawing = the 2px border. The `▒` column on the right and row underneath =
the `6px 6px 0` flat offset shadow (accent at ~18%). Corners are square, always.
Default width 52; below 46 columns or without a tty, fall back to flat lines.

### Module header — `modulo("focus_stats", "src: log.csv")`
`[ MODULE: FOCUS_STATS ]` in accent-bold, optional dim meta on the right. This is the
CLI form of the bento module card header. Every command output opens with one.

### Section label — `secao("ultimos 14 dias")` → `# ULTIMOS 14 DIAS` in accent.

### Key-value row — `kv("SEQUENCIA", "7 DIA(S)")`
```
  SEQUENCIA ···························· 7 DIA(S)
```
Dim key, `ACC15` dot leader, accent-bold value. This replaces every `label: value`
line in the repo.

### Status / result lines
`[ OK ] TEXTO` (green bracket, accent-bold text) · `[ ERRO ] texto` · `[ VAZIO ]`,
`[ ABORTADO ]` and friends in `FG40`. Next-step hint: `> proximo passo:  comando`
with a dim `>` and the command in accent-bold.

### Progress / histogram bars — `barra(feito, total)`
`█` filled in accent, `▒` track in `ACC15`, percentage in accent-bold. Same glyphs for
day histograms; mark today's row with `►`.

### List rows — `item("►", texto, meta)`
Inactive rows in `FG70`, active row uses `INV` (accent background). Fake-precise meta
(`-rwxr-xr-x`, `4.2K`, `PID: 001`) in `FG40`/`ACC30` — flavor, not data.

### Chips / tags — `chip("SPOILER")` → `[SPOILER]`, brackets dim, text accent.

## 4. Motion

- Entrances are fade/slide only: reveal line by line with ~12ms between lines. No
  bounce, no spring, no overshoot, no spinner that jumps.
- Ambient motion allowed: blinking cursor block, pulsing status dot (`●`/`◍`),
  progress-bar head alternating `█`/`▓`.
- Redraw by moving the cursor up N lines and repainting with `\033[K`; never clear the
  whole screen mid-session.
- Any animation is skipped when not a tty, under `NO_COLOR`, or with `<TOOL>_SEM_ANIM`.

## 5. Voice

Terminal narrative: prompts `>` and `$`, paths `root@<tool>: ~/<area>`, `# HEADINGS`,
`[ OK ]`, `[ MODULE: X ]`, `PID`, `SRC:`. Labels in SCREAMING_SNAKE; explanations in
pt-BR; system chrome in en-US.

## 6. Do / Don't

- DO route every color through the tokens — no raw `\033[1;35m` anywhere.
- DO uppercase anything label-like; DO keep corners square.
- DO check `-t 1` / `isatty` before drawing boxes or animating.
- DON'T introduce new colors (purple/cyan/magenta headers are gone), gradients, or
  rounded corners.
- DON'T use emoji as bullets or decoration.
- DON'T print raw `label: value`; use `kv`.
