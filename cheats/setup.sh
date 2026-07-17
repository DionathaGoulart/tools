#!/usr/bin/env bash
# setup.sh — add tools/ to PATH (macOS / Linux / Windows via Git Bash)
#
# Usage: source setup.sh
#   or:  . setup.sh
#
# Add this line to ~/.zshrc, ~/.bashrc, or ~/.bash_profile:
#   [ -f "$HOME/Desktop/tools/cheats/setup.sh" ] && source "$HOME/Desktop/tools/cheats/setup.sh"

TOOLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"

case ":$PATH:" in
  *":$TOOLS_DIR:"*) ;;
  *) export PATH="$TOOLS_DIR:$PATH" ;;
esac

unset TOOLS_DIR
