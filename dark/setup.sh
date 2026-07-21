#!/usr/bin/env bash
# setup.sh — put dark/ on PATH (macOS / Linux / Windows via Git Bash)
#
# Ways to use it:
#   bash setup.sh          ← one-time install of the CLI: writes the source line into your rc
#   bash setup.sh --skill  ← install only the /dark Claude Code skill (symlink)
#   source setup.sh        ← what the rc line runs on every new terminal (adds to PATH)
#
# CLI and skill are independent: install one, the other, or both.
# Optional: set DARK_LEMBRETE=1 before sourcing to print a reminder once
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
  if [ "${DARK_LEMBRETE:-0}" = "1" ]; then
    _drk_stamp="${DARK_DIR:-$HOME/.dark}/.ultimo_radar"
    _drk_hoje="$(date +%Y-%m-%d)"
    if [ "$(cat "$_drk_stamp" 2>/dev/null)" != "$_drk_hoje" ]; then
      echo "🕯 dark: radar de hoje ainda não visto (janela sazonal chegando?). Rode  dark"
    fi
    unset _drk_stamp _drk_hoje
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
  # skill /dark do Claude Code (geração com o Claude da sessão, sem OpenRouter)
  [ -d "$HOME/.claude" ] || echo "dark: aviso — ~/.claude não existe (Claude Code não instalado?); criando mesmo assim."
  mkdir -p "$HOME/.claude/skills"
  # Windows (Git Bash): sem symlink nativo, ln viraria cópia silenciosa — força
  # symlink real e, se não der (sem Developer Mode), copia a pasta de verdade
  if ! MSYS=winsymlinks:nativestrict ln -sfn "$TOOLS_DIR/skill" "$HOME/.claude/skills/dark" 2>/dev/null; then
    rm -rf "$HOME/.claude/skills/dark"
    cp -R "$TOOLS_DIR/skill" "$HOME/.claude/skills/dark"
  fi
  echo "dark: skill /dark instalada em ~/.claude/skills/dark"
  echo "dark: o skill usa o CLI pra coletar — instale-o também se ainda não tiver (bash setup.sh)"
else
  LINE="[ -f \"$TOOLS_DIR/setup.sh\" ] && source \"$TOOLS_DIR/setup.sh\""
  case "$(basename "${SHELL:-bash}")" in
    zsh) RC="$HOME/.zshrc" ;;
    *)   RC="$HOME/.bashrc"; [ -f "$RC" ] || RC="$HOME/.bash_profile" ;;
  esac

  if grep -qsF "dark/setup.sh" "$RC"; then
    echo "dark: already installed in $RC"
  else
    printf '\n# tools/dark — copiloto do Instagram @darkning.art (horror art)\n# export DARK_LEMBRETE=1  # descomente pra lembrete diário\n%s\n' "$LINE" >> "$RC"
    echo "dark: installed in $RC"
  fi
  echo "dark: open a new terminal or run:  source ${RC/#$HOME/~}"
fi
