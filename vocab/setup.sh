#!/usr/bin/env bash
# setup.sh — put vocab/ on PATH (macOS / Linux / Windows via Git Bash)
#
# Two ways to use it:
#   bash setup.sh     ← one-time install: writes the source line into your shell rc
#   source setup.sh   ← what the rc line runs on every new terminal (adds to PATH)
#
# Optional: set VOCAB_LEMBRETE=1 before sourcing to print a reminder once per
# day when you open a terminal, if you haven't practiced yet.

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
  if [ "${VOCAB_LEMBRETE:-0}" = "1" ]; then
    _voc_stamp="${VOCAB_DIR:-$HOME/.vocab}/.ultima_sessao"
    _voc_hoje="$(date +%Y-%m-%d)"
    if [ "$(cat "$_voc_stamp" 2>/dev/null)" != "$_voc_hoje" ]; then
      echo "📚 vocab: você ainda não praticou hoje. Rode  vocab"
    fi
    unset _voc_stamp _voc_hoje
  fi

  unset TOOLS_DIR SOURCED
else
  LINE="[ -f \"$TOOLS_DIR/setup.sh\" ] && source \"$TOOLS_DIR/setup.sh\""
  case "$(basename "${SHELL:-bash}")" in
    zsh) RC="$HOME/.zshrc" ;;
    *)   RC="$HOME/.bashrc"; [ -f "$RC" ] || RC="$HOME/.bash_profile" ;;
  esac

  if grep -qsF "vocab/setup.sh" "$RC"; then
    echo "vocab: already installed in $RC"
  else
    printf '\n# tools/vocab — comando vocab (inglês diário)\n# export VOCAB_LEMBRETE=1  # descomente pra lembrete diário\n%s\n' "$LINE" >> "$RC"
    echo "vocab: installed in $RC"
  fi
  echo "vocab: open a new terminal or run:  source ${RC/#$HOME/~}"
fi
