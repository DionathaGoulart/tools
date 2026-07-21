#!/usr/bin/env bash
# setup.sh — put goodbiografo/ on PATH (macOS / Linux / Windows via Git Bash)
#
# Two ways to use it:
#   bash setup.sh     ← one-time install: writes the source line into your shell rc
#   source setup.sh   ← what the rc line runs on every new terminal (adds to PATH)
#
# Optional: set GOODBIOGRAFO_LEMBRETE=1 before sourcing to print the day's question
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

  # once-a-day reminder (opt-in)
  if [ "${GOODBIOGRAFO_LEMBRETE:-0}" = "1" ]; then
    _bio_stamp="${GOODBIOGRAFO_DIR:-$HOME/.biografo}/.ultimo_lembrete"
    _bio_hoje="$(date +%Y-%m-%d)"
    if [ ! -f "$_bio_stamp" ] || [ "$(cat "$_bio_stamp" 2>/dev/null)" != "$_bio_hoje" ]; then
      mkdir -p "$(dirname "$_bio_stamp")" && echo "$_bio_hoje" > "$_bio_stamp"
      if [ ! -f "${GOODBIOGRAFO_DIR:-$HOME/.biografo}/respostas/$_bio_hoje.md" ]; then
        echo "📖 goodbiografo: você ainda não respondeu hoje. Rode  goodbiografo"
      fi
    fi
    unset _bio_stamp _bio_hoje
  fi

  unset TOOLS_DIR SOURCED
else
  LINE="[ -f \"$TOOLS_DIR/setup.sh\" ] && source \"$TOOLS_DIR/setup.sh\""
  case "$(basename "${SHELL:-bash}")" in
    zsh) RC="$HOME/.zshrc" ;;
    *)   RC="$HOME/.bashrc"; [ -f "$RC" ] || RC="$HOME/.bash_profile" ;;
  esac

  if grep -qsF "goodbiografo/setup.sh" "$RC"; then
    echo "goodbiografo: already installed in $RC"
  else
    printf '\n# tools/goodbiografo — comando goodbiografo (autobiografia diária)\n# export GOODBIOGRAFO_LEMBRETE=1  # descomente pra lembrete diário\n%s\n' "$LINE" >> "$RC"
    echo "goodbiografo: installed in $RC"
  fi
  echo "goodbiografo: open a new terminal or run:  source ${RC/#$HOME/~}"
fi
