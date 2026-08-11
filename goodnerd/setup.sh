#!/usr/bin/env bash
# setup.sh — put goodnerd/ on PATH (macOS / Linux / Windows via Git Bash)
#
# Two ways to use it:
#   bash setup.sh     ← one-time install: writes the source line into your shell rc
#   source setup.sh   ← what the rc line runs on every new terminal (adds to PATH)

# quando o load.sh chama, o diretório vem pronto: dentro de uma função o zsh
# troca $0 pelo nome da função e a auto-localização daria o diretório errado
TOOLS_DIR="${GOODTOOLS_TOOL_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)}"

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
  # instalação: um bloco único no rc, ancorado no symlink ~/.goodtools, em vez
  # de uma linha com caminho absoluto por ferramenta (ver lib/rcblock.sh)
  ROOT="$(cd "$TOOLS_DIR/.." && pwd)"
  # shellcheck source=../lib/rcblock.sh
  . "$ROOT/lib/rcblock.sh"
  RC="$(gt_rc)"

  if gt_has "$RC" "goodnerd"; then
    echo "goodnerd: already installed in $RC"
  else
    gt_add "$ROOT" "goodnerd"
    echo "goodnerd: installed in $RC"
  fi
  echo "goodnerd: open a new terminal or run:  source ${RC/#$HOME/~}"
fi
