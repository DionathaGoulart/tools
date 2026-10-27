#!/usr/bin/env bash
# setup.sh — put goodmon/ on PATH (macOS / Linux / Windows via Git Bash)
TOOLS_DIR="${GOODTOOLS_TOOL_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)}"
SOURCED=0
if [ -n "${ZSH_EVAL_CONTEXT:-}" ]; then case "$ZSH_EVAL_CONTEXT" in *:file*) SOURCED=1;; esac
elif [ -n "${BASH_SOURCE:-}" ] && [ "${BASH_SOURCE[0]}" != "$0" ]; then SOURCED=1; fi
if [ "$SOURCED" -eq 1 ]; then
  case ":$PATH:" in *":$TOOLS_DIR:"*) ;; *) export PATH="$TOOLS_DIR:$PATH";; esac
  _gm_help="$(cd "$TOOLS_DIR/../goodhelp" 2>/dev/null && pwd)"
  if [ -n "$_gm_help" ] && [ -x "$_gm_help/goodhelp" ]; then case ":$PATH:" in *":$_gm_help:"*) ;; *) export PATH="$_gm_help:$PATH";; esac; fi
  if ! command -v python3 >/dev/null 2>&1 && [ -f "$TOOLS_DIR/../lib/shims/python3" ]; then export PATH="$TOOLS_DIR/../lib/shims:$PATH"; fi
  unset _gm_help TOOLS_DIR SOURCED
else
  ROOT="$(cd "$TOOLS_DIR/.." && pwd)"
  . "$ROOT/lib/rcblock.sh"
  RC="$(gt_rc)"
  if gt_has "$RC" goodmon; then echo "goodmon: already installed in $RC"; else gt_add "$ROOT" goodmon; echo "goodmon: installed in $RC"; fi
  echo "goodmon: open a new terminal or run:  source ${RC/#$HOME/~}"
fi
