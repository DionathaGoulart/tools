#!/usr/bin/env bash
# setup.sh — put good/ on PATH (macOS / Linux / Windows via Git Bash)
#
# Two ways to use it:
#   bash setup.sh     ← one-time install: writes the source line into your shell rc
#   source setup.sh   ← what the rc line runs on every new terminal (adds to PATH)

GOOD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"

# detect whether this file is being sourced or executed
SOURCED=0
if [ -n "${ZSH_EVAL_CONTEXT:-}" ]; then
  case "$ZSH_EVAL_CONTEXT" in *:file*) SOURCED=1 ;; esac
elif [ -n "${BASH_SOURCE:-}" ] && [ "${BASH_SOURCE[0]}" != "$0" ]; then
  SOURCED=1
fi

if [ "$SOURCED" -eq 1 ]; then
  # sourced: just prepend to PATH
  case ":$PATH:" in
    *":$GOOD_DIR:"*) ;;
    *) export PATH="$GOOD_DIR:$PATH" ;;
  esac
  unset GOOD_DIR SOURCED
else
  # executed (bash setup.sh): a subshell can't change your shell's PATH,
  # so install the source line into the shell rc instead
  LINE="[ -f \"$GOOD_DIR/setup.sh\" ] && source \"$GOOD_DIR/setup.sh\""
  case "$(basename "${SHELL:-bash}")" in
    zsh) RC="$HOME/.zshrc" ;;
    *)   RC="$HOME/.bashrc"; [ -f "$RC" ] || RC="$HOME/.bash_profile" ;;
  esac

  if grep -qsF "good/setup.sh" "$RC"; then
    echo "good: already installed in $RC"
  else
    printf '\n# tools/good — comando good (fetch de sistema)\n%s\n' "$LINE" >> "$RC"
    echo "good: installed in $RC"
  fi
  echo "good: open a new terminal or run:  source ${RC/#$HOME/~}"
fi
