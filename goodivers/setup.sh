#!/usr/bin/env bash
# setup.sh — put goodivers/ on PATH (macOS / Linux / Windows via Git Bash)
#
# Ways to use it:
#   bash setup.sh          ← one-time install of the CLI: writes the source line into your rc
#   bash setup.sh --skill  ← install only the /goodivers Claude Code skill (symlink)
#   source setup.sh        ← what the rc line runs on every new terminal (adds to PATH)
#
# CLI and skill are independent: install one, the other, or both.
# Optional: set GOODIVERS_LEMBRETE=1 before sourcing to print a reminder once
# per day when you open a terminal, if you haven't checked the radar yet.

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
  if [ "${GOODIVERS_LEMBRETE:-0}" = "1" ]; then
    _gdv_stamp="${GOODIVERS_DIR:-$HOME/.goodivers}/.ultimo_radar"
    _gdv_hoje="$(date +%Y-%m-%d)"
    if [ "$(cat "$_gdv_stamp" 2>/dev/null)" != "$_gdv_hoje" ]; then
      echo "🎬 goodivers: radar de hoje ainda não visto (Ordem Maior? patch novo?). Rode  goodivers"
    fi
    unset _gdv_stamp _gdv_hoje
  fi

  unset TOOLS_DIR SOURCED
elif [ "${1:-}" = "--skill" ]; then
  # skill /goodivers do Claude Code (geração com o Claude da sessão, sem OpenRouter)
  [ -d "$HOME/.claude" ] || echo "goodivers: aviso — ~/.claude não existe (Claude Code não instalado?); criando mesmo assim."
  mkdir -p "$HOME/.claude/skills"
  ln -sfn "$TOOLS_DIR/skill" "$HOME/.claude/skills/goodivers"
  echo "goodivers: skill /goodivers instalada em ~/.claude/skills/goodivers"
  echo "goodivers: o skill usa o CLI pra coletar — instale-o também se ainda não tiver (bash setup.sh)"
else
  LINE="[ -f \"$TOOLS_DIR/setup.sh\" ] && source \"$TOOLS_DIR/setup.sh\""
  case "$(basename "${SHELL:-bash}")" in
    zsh) RC="$HOME/.zshrc" ;;
    *)   RC="$HOME/.bashrc"; [ -f "$RC" ] || RC="$HOME/.bash_profile" ;;
  esac

  if grep -qsF "goodivers/setup.sh" "$RC"; then
    echo "goodivers: already installed in $RC"
  else
    printf '\n# tools/goodivers — copiloto do canal (Helldivers 2)\n# export GOODIVERS_LEMBRETE=1  # descomente pra lembrete diário\n%s\n' "$LINE" >> "$RC"
    echo "goodivers: installed in $RC"
  fi
  echo "goodivers: open a new terminal or run:  source ${RC/#$HOME/~}"
fi
