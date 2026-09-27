#!/usr/bin/env bash
# Install only the goodcodex command on PATH. Native Codex files require `goodcodex apply`.
TOOLS_DIR="${GOODTOOLS_TOOL_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)}"
SOURCED=0
if [ -n "${ZSH_EVAL_CONTEXT:-}" ]; then
  case "$ZSH_EVAL_CONTEXT" in *:file*) SOURCED=1 ;; esac
elif [ -n "${BASH_SOURCE:-}" ] && [ "${BASH_SOURCE[0]}" != "$0" ]; then
  SOURCED=1
fi
if [ "$SOURCED" -eq 1 ]; then
  case ":$PATH:" in *":$TOOLS_DIR:"*) ;; *) export PATH="$TOOLS_DIR:$PATH" ;; esac
  _gh_dir="$(cd "$TOOLS_DIR/../goodhelp" 2>/dev/null && pwd)"
  if [ -n "$_gh_dir" ] && [ -x "$_gh_dir/goodhelp" ]; then
    case ":$PATH:" in *":$_gh_dir:"*) ;; *) export PATH="$_gh_dir:$PATH" ;; esac
  fi
  unset _gh_dir TOOLS_DIR SOURCED
else
  ROOT="$(cd "$TOOLS_DIR/.." && pwd)"
  # shellcheck source=../lib/rcblock.sh
  . "$ROOT/lib/rcblock.sh"
  RC="$(gt_rc)"
  if gt_has "$RC" "goodcodex"; then
    echo "goodcodex: already installed in $RC"
  else
    gt_add "$ROOT" "goodcodex"
    echo "goodcodex: command installed in $RC"
  fi
  echo "goodcodex: Codex profiles remain inactive; run 'goodcodex plan' then 'goodcodex apply' to install them."
  echo "goodcodex: open a new terminal or run: source ${RC/#$HOME/~}"
fi
