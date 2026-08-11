#!/usr/bin/env bash
# setup.sh — put goodvocab/ on PATH (macOS / Linux / Windows via Git Bash)
#
# Two ways to use it:
#   bash setup.sh     ← one-time install: writes the source line into your shell rc
#   source setup.sh   ← what the rc line runs on every new terminal (adds to PATH)
#
# Optional: set GOODVOCAB_LEMBRETE=1 before sourcing to print a reminder once per
# day when you open a terminal, if you haven't practiced yet.

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

  # once-a-day reminder (opt-in)
  if [ "${GOODVOCAB_LEMBRETE:-0}" = "1" ]; then
    _voc_stamp="${GOODVOCAB_DIR:-$HOME/.vocab}/.ultima_sessao"
    _voc_hoje="$(date +%Y-%m-%d)"
    if [ "$(cat "$_voc_stamp" 2>/dev/null)" != "$_voc_hoje" ]; then
      echo "📚 goodvocab: você ainda não praticou hoje. Rode  goodvocab"
    fi
    unset _voc_stamp _voc_hoje
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
  # instalação: um bloco único no rc, ancorado no symlink ~/.goodtools, em vez
  # de uma linha com caminho absoluto por ferramenta (ver lib/rcblock.sh)
  ROOT="$(cd "$TOOLS_DIR/.." && pwd)"
  # shellcheck source=../lib/rcblock.sh
  . "$ROOT/lib/rcblock.sh"
  RC="$(gt_rc)"

  if gt_has "$RC" "goodvocab"; then
    echo "goodvocab: already installed in $RC"
  else
    gt_add "$ROOT" "goodvocab"
    echo "goodvocab: installed in $RC"
  fi
  echo "goodvocab: open a new terminal or run:  source ${RC/#$HOME/~}"
fi
