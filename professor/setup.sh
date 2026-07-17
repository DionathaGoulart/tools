#!/usr/bin/env bash
# setup.sh — put professor/ on PATH (macOS / Linux / Windows via Git Bash)
#
# Two ways to use it:
#   bash setup.sh     ← one-time install: writes the source line into your shell rc
#   source setup.sh   ← what the rc line runs on every new terminal (adds to PATH)

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
  unset TOOLS_DIR SOURCED
else
  LINE="[ -f \"$TOOLS_DIR/setup.sh\" ] && source \"$TOOLS_DIR/setup.sh\""
  case "$(basename "${SHELL:-bash}")" in
    zsh) RC="$HOME/.zshrc" ;;
    *)   RC="$HOME/.bashrc"; [ -f "$RC" ] || RC="$HOME/.bash_profile" ;;
  esac

  if grep -qsF "professor/setup.sh" "$RC"; then
    echo "professor: already installed in $RC"
  else
    printf '\n# tools/professor — comando professor (estudo Feynman)\n%s\n' "$LINE" >> "$RC"
    echo "professor: installed in $RC"
  fi
  echo "professor: open a new terminal or run:  source ${RC/#$HOME/~}"
fi
