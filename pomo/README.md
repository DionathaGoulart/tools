# pomo

Pomodoro no terminal. Barra de progresso ASCII, notificação nativa quando o
tempo acaba (com som no macOS), estatísticas dos últimos dias. Zero
dependências — bash puro.

```bash
pomo                   # foco de 25 min
pomo 50                # foco de 50 min
pomo 25 estudar go     # foco com rótulo (vai pro log)
pomo pausa             # pausa de 5 min
pomo pausa 15          # pausa longa
pomo -l                # estatísticas: hoje + últimos 14 dias
```

Durante a contagem:

| Tecla | Faz |
|---|---|
| `p` | pausa / retoma o cronômetro |
| `q` | aborta a sessão (não conta na estatística) |

A cada 4 focos concluídos no dia, ele sugere a pausa longa (15 min).

## Estatísticas

Cada sessão vira uma linha num CSV simples (`~/.pomo/log.csv` — fácil de
processar com qualquer coisa). `pomo -l` mostra:

```
  🍅 hoje: 3 pomodoro(s) · 75 min de foco

  2026-07-18  ████ 4 (100 min)
  2026-07-19  ██ 2 (50 min)
  2026-07-20  ███ 3 (75 min)
```

Só focos **concluídos** contam — abortar com `q` ou Ctrl-C registra a sessão
como `abortado` e ela fica de fora.

## Notificação

- **macOS**: notificação do sistema via `osascript` + som (`Glass.aiff`).
- **Linux**: `notify-send` (presente na maioria dos desktops).
- Sempre: bell do terminal (`\a`) como fallback.

## Instalação

```bash
bash ~/Desktop/tools/pomo/setup.sh
```

Abra um terminal novo (ou `source ~/.zshrc`) e rode `pomo`.

## Configuração

| Variável | Pra quê | Padrão |
|---|---|---|
| `POMO_FOCO` | minutos do foco padrão | `25` |
| `POMO_PAUSA` | minutos da pausa padrão | `5` |
| `POMO_PAUSA_LONGA` | minutos da pausa longa (sugerida a cada 4 focos) | `15` |
| `POMO_DIR` | onde fica o log | `~/.pomo` |
| `NO_COLOR` | qualquer valor desliga as cores | — |

---

↩ [Voltar pro índice de ferramentas](../README.md)
