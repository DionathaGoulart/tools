#!/usr/bin/env bash
# setup.sh — put goodbio/ on PATH (macOS / Linux / Windows via Git Bash)
#
# Two ways to use it:
#   bash setup.sh     ← one-time install: writes the source line into your shell rc
#   source setup.sh   ← what the rc line runs on every new terminal (adds to PATH)
#
# Optional: set GOODBIO_LEMBRETE=1 before sourcing to print the day's question
# once per day when you open a terminal (a gentle nudge, not a nag).

TOOLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"

SOURCED=0
if [ -n "${ZSH_EVAL_CONTEXT:-}" ]; then
  case "$ZSH_EVAL_CONTEXT" in *:file*) SOURCED=1 ;; esac
elif [ -n "${BASH_SOURCE:-}" ] && [ "${BASH_SOURCE[0]}" != "$0" ]; then
  SOURCED=1
fi

if [ "$SOURCED" -eq 1 ]; then
  case ":$PATH:" in
    *":$TOOLS_DIR:"*) ;;
    *) export PATH="$TOOLS_DIR:$PATH" ;;
  esac

  # goodhelp vem junto por padrão: mapa da família (goodhelp / <ferramenta> help)
  _gh_dir="$(cd "$TOOLS_DIR/../goodhelp" 2>/dev/null && pwd)"
  if [ -n "$_gh_dir" ] && [ -x "$_gh_dir/goodhelp" ]; then
    case ":$PATH:" in
      *":$_gh_dir:"*) ;;
      *) export PATH="$_gh_dir:$PATH" ;;
    esac
  fi
  unset _gh_dir

  # once-a-day reminder (opt-in)
  if [ "${GOODBIO_LEMBRETE:-0}" = "1" ]; then
    _bio_stamp="${GOODBIO_DIR:-$HOME/.biografo}/.ultimo_lembrete"
    _bio_hoje="$(date +%Y-%m-%d)"
    if [ ! -f "$_bio_stamp" ] || [ "$(cat "$_bio_stamp" 2>/dev/null)" != "$_bio_hoje" ]; then
      mkdir -p "$(dirname "$_bio_stamp")" && echo "$_bio_hoje" > "$_bio_stamp"
      if [ ! -f "${GOODBIO_DIR:-$HOME/.biografo}/respostas/$_bio_hoje.md" ]; then
        echo "📖 goodbio: você ainda não respondeu hoje. Rode  goodbio"
      fi
    fi
    unset _bio_stamp _bio_hoje
  fi

  # Windows (Git Bash): não existe python3.exe — cai no shim do repo (py/python)
  if ! command -v python3 >/dev/null 2>&1 && [ -f "$TOOLS_DIR/../lib/shims/python3" ]; then
    case ":$PATH:" in
      *":$TOOLS_DIR/../lib/shims:"*) ;;
      *) export PATH="$TOOLS_DIR/../lib/shims:$PATH" ;;
    esac
  fi

  unset TOOLS_DIR SOURCED
else
  LINE="[ -f \"$TOOLS_DIR/setup.sh\" ] && source \"$TOOLS_DIR/setup.sh\""
  case "$(basename "${SHELL:-bash}")" in
    zsh) RC="$HOME/.zshrc" ;;
    *)   RC="$HOME/.bashrc"; [ -f "$RC" ] || RC="$HOME/.bash_profile" ;;
  esac

  if grep -qsF "goodbio/setup.sh" "$RC"; then
    echo "goodbio: already installed in $RC"
  else
    printf '\n# tools/goodbio — comando goodbio (autobiografia diária)\n# export GOODBIO_LEMBRETE=1  # descomente pra lembrete diário\n%s\n' "$LINE" >> "$RC"
    echo "goodbio: installed in $RC"
  fi
  echo "goodbio: open a new terminal or run:  source ${RC/#$HOME/~}"
fi
