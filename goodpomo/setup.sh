#!/usr/bin/env bash
# setup.sh — put goodpomo/ on PATH (macOS / Linux / Windows via Git Bash)
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

  # goodhelp vem junto por padrão: mapa da família (goodhelp / <ferramenta> help)
  _gh_dir="$(cd "$TOOLS_DIR/../goodhelp" 2>/dev/null && pwd)"
  if [ -n "$_gh_dir" ] && [ -x "$_gh_dir/goodhelp" ]; then
    case ":$PATH:" in
      *":$_gh_dir:"*) ;;
      *) export PATH="$_gh_dir:$PATH" ;;
    esac
  fi
  unset _gh_dir
  unset TOOLS_DIR SOURCED
else
  LINE="[ -f \"$TOOLS_DIR/setup.sh\" ] && source \"$TOOLS_DIR/setup.sh\""
  case "$(basename "${SHELL:-bash}")" in
    zsh) RC="$HOME/.zshrc" ;;
    *)   RC="$HOME/.bashrc"; [ -f "$RC" ] || RC="$HOME/.bash_profile" ;;
  esac

  if grep -qsF "goodpomo/setup.sh" "$RC"; then
    echo "goodpomo: already installed in $RC"
  else
    printf '\n# tools/goodpomo — comando goodpomo (pomodoro no terminal)\n%s\n' "$LINE" >> "$RC"
    echo "goodpomo: installed in $RC"
  fi
  echo "goodpomo: open a new terminal or run:  source ${RC/#$HOME/~}"
fi
