# goodpomo

Pomodoro no terminal com visual de terminal retrô (neo-brutalista): janela em
box-drawing, relógio em dígitos gigantes, barra de progresso viva, sombra
offset e paletas trocáveis. Notificação nativa quando o tempo acaba (com som
no macOS) e estatísticas dos últimos dias. Zero dependências — bash puro.

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ● ● ●  root@goodpomo: ~/focus              PID: 4821 ┃▒
┠──────────────────────────────────────────────────┨▒
┃ [ MODULE: FOCUS_TIMER ]              ESTUDAR GO  ┃▒
┃                                                  ┃▒
┃         ██████ ██████    ██████ ██████           ┃▒
┃         ██  ██ ██  ██ ██     ██     ██           ┃▒
┃         ██  ██ ██████    ██████ ██████           ┃▒
┃         ██  ██ ██  ██ ██     ██ ██               ┃▒
┃         ██████ ██████    ██████ ██████           ┃▒
┃                                                  ┃▒
┃ ███████████████████████████▓▒▒▒▒▒▒▒▒▒▒▒▒▒   65%  ┃▒
┠──────────────────────────────────────────────────┨▒
┃ [P] PAUSAR · [Q] SAIR              ◍ EM EXECUCAO ┃▒
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛▒
 ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
```

```bash
goodpomo                   # foco de 25 min
goodpomo 50                # foco de 50 min
goodpomo 25 estudar go     # foco com rótulo (vai pro log)
goodpomo pausa             # pausa de 5 min
goodpomo pausa 15          # pausa longa
goodpomo -l                # estatísticas: hoje + últimos 14 dias
goodpomo temas             # paletas disponíveis
```

Em terminal estreito (< 49 colunas) ou fora de TTY ele cai automaticamente no
modo compacto de uma linha.

Durante a contagem:

| Tecla | Faz |
|---|---|
| `p` | pausa / retoma o cronômetro |
| `q` | aborta a sessão (não conta na estatística) |

A cada 4 focos concluídos no dia, ele sugere a pausa longa (15 min).

## Estatísticas

Cada sessão vira uma linha num CSV simples (`~/.pomo/log.csv` — fácil de
processar com qualquer coisa). `goodpomo -l` mostra:

```
  [ MODULE: FOCUS_STATS ]        SRC: log.csv

  HOJE ··························· 4 POMODORO(S)
  FOCO HOJE ···························· 125 MIN
  SEQUENCIA ··························· 3 DIA(S)
  TOTAL ACUMULADO ········ 16 POMODORO(S) · 7H5M

  # ULTIMOS 14 DIAS
  ────────────────────────────────────────────
    2026-07-18  ███▒▒▒▒▒▒▒▒▒▒▒▒▒   3 (75 min)
    2026-07-19  ███▒▒▒▒▒▒▒▒▒▒▒▒▒   3 (75 min)
  ► 2026-07-20  ████▒▒▒▒▒▒▒▒▒▒▒▒   4 (125 min)
```

`SEQUENCIA` é o streak de dias consecutivos com pelo menos um foco concluído.

Só focos **concluídos** contam — abortar com `q` ou Ctrl-C registra a sessão
como `abortado` e ela fica de fora.

## Notificação

- **macOS**: notificação do sistema via `osascript` + som (`Glass.aiff`).
- **Linux**: `notify-send` (presente na maioria dos desktops).
- Sempre: bell do terminal (`\a`) como fallback.

## Instalação

```bash
bash ~/Desktop/tools/goodpomo/setup.sh
```

Abra um terminal novo (ou `source ~/.zshrc`) e rode `goodpomo`.

## Configuração

| Variável | Pra quê | Padrão |
|---|---|---|
| `GOODPOMO_FOCO` | minutos do foco padrão | `25` |
| `GOODPOMO_PAUSA` | minutos da pausa padrão | `5` |
| `GOODPOMO_PAUSA_LONGA` | minutos da pausa longa (sugerida a cada 4 focos) | `15` |
| `GOODPOMO_DIR` | onde fica o log | `~/.pomo` |
| `GOODPOMO_TEMA` | paleta (veja `goodpomo temas`) | `vault-gold` |
| `GOODPOMO_SEM_ANIM` | qualquer valor desliga a animação de entrada | — |
| `NO_COLOR` | qualquer valor desliga as cores | — |

## Temas

Nove paletas vindas do style guide (`goodpomo temas` lista com swatch):

| Escuras | Claras |
|---|---|
| `vault-gold` (padrão), `noir-rose`, `midnight-ember`, `cyber-teal`, `velvet-purple` | `abyss-frost`, `crimson-chalk`, `forest-mist`, `sand-dusk` |

```bash
export GOODPOMO_TEMA=cyber-teal
```

Cores true-color (24-bit) quando `COLORTERM=truecolor`; senão cai pro ANSI
básico de 8 cores.

---

↩ [Voltar pro índice de ferramentas](../README.md)
