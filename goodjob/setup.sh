#!/usr/bin/env bash
# setup.sh — put goodjob/ on PATH (macOS / Linux / Windows via Git Bash)
#
# Ways to use it:
#   bash setup.sh          ← one-time install of the CLI: writes the source line into your rc
#   bash setup.sh --skill  ← install only the /goodjob Claude Code skill (symlink)
#   source setup.sh        ← what the rc line runs on every new terminal (adds to PATH)
#
# CLI and skill are independent: install one, the other, or both.
# Optional: set GOODJOB_LEMBRETE=1 before sourcing to print a reminder once
# per day when you open a terminal, if you haven't checked the radar yet.

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
  if [ "${GOODJOB_LEMBRETE:-0}" = "1" ]; then
    _gjb_stamp="${GOODJOB_DIR:-$HOME/.goodjob}/.ultimo_radar"
    _gjb_hoje="$(date +%Y-%m-%d)"
    if [ "$(cat "$_gjb_stamp" 2>/dev/null)" != "$_gjb_hoje" ]; then
      echo "💼 goodjob: radar de vagas de hoje ainda não visto. Rode  goodjob"
    fi
    unset _gjb_stamp _gjb_hoje
  fi

  # Windows (Git Bash): não existe python3.exe — cai no shim do repo (py/python)
  if ! command -v python3 >/dev/null 2>&1 && [ -f "$TOOLS_DIR/../lib/shims/python3" ]; then
    case ":$PATH:" in
      *":$TOOLS_DIR/../lib/shims:"*) ;;
      *) export PATH="$TOOLS_DIR/../lib/shims:$PATH" ;;
    esac
  fi

  unset TOOLS_DIR SOURCED
elif [ "${1:-}" = "--skill" ]; then
  # skill /goodjob do Claude Code (geração com o Claude da sessão, sem OpenRouter)
  [ -d "$HOME/.claude" ] || echo "goodjob: aviso — ~/.claude não existe (Claude Code não instalado?); criando mesmo assim."
  mkdir -p "$HOME/.claude/skills"
  # Windows (Git Bash): sem symlink nativo, ln viraria cópia silenciosa — força
  # symlink real e, se não der (sem Developer Mode), copia a pasta de verdade
  if ! MSYS=winsymlinks:nativestrict ln -sfn "$TOOLS_DIR/skill" "$HOME/.claude/skills/goodjob" 2>/dev/null; then
    rm -rf "$HOME/.claude/skills/goodjob"
    cp -R "$TOOLS_DIR/skill" "$HOME/.claude/skills/goodjob"
  fi
  echo "goodjob: skill /goodjob instalada em ~/.claude/skills/goodjob"
  echo "goodjob: o skill usa o CLI pra coletar — instale-o também se ainda não tiver (bash setup.sh)"
else
  # instalação: um bloco único no rc, ancorado no symlink ~/.goodtools, em vez
  # de uma linha com caminho absoluto por ferramenta (ver lib/rcblock.sh)
  ROOT="$(cd "$TOOLS_DIR/.." && pwd)"
  # shellcheck source=../lib/rcblock.sh
  . "$ROOT/lib/rcblock.sh"
  RC="$(gt_rc)"

  if gt_has "$RC" "goodjob"; then
    echo "goodjob: already installed in $RC"
  else
    gt_add "$ROOT" "goodjob"
    echo "goodjob: installed in $RC"
  fi
  echo "goodjob: open a new terminal or run:  source ${RC/#$HOME/~}"
fi
