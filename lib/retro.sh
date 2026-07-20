#!/usr/bin/env bash
# retro.sh — shared retro-terminal theme for the bash tools in this repo.
#
#   source "$(dirname "${BASH_SOURCE[0]}")/../lib/retro.sh"
#   retro_init [largura]        # defaults to 52 columns
#
# Implements .harness/styleguide-terminal.md: accent-only palette, square
# corners, 2px-ish heavy borders, flat offset shadow, uppercase labels.
#
# Theme comes from <TOOL>_TEMA (set by the caller before sourcing) or
# RETRO_TEMA; falls back to vault-gold. NO_COLOR and non-tty are respected.

# ---------- palette ----------
# each theme: <background> <foreground> <accent>   (hex, no #)
retro_tema_hex() {
  case "$1" in
    vault-gold)     echo "111111 e0e0e0 c8a96e" ;;
    noir-rose)      echo "121212 f2efe7 e8729a" ;;
    midnight-ember) echo "0d1117 e0ffe0 ff6b45" ;;
    cyber-teal)     echo "0a0f14 e0f4ff 00e5ff" ;;
    velvet-purple)  echo "0e0a14 ede0ff b47aff" ;;
    abyss-frost)    echo "e4f0f6 0f172a 0a0f1e" ;;
    crimson-chalk)  echo "f2efe7 1a0a0a dc143c" ;;
    forest-mist)    echo "eef4ee 1a2e1a 2d6a2d" ;;
    sand-dusk)      echo "f5f0e8 2a1a0a b56a30" ;;
    *)              return 1 ;;
  esac
}
RETRO_TEMAS="vault-gold noir-rose midnight-ember cyber-teal velvet-purple abyss-frost crimson-chalk forest-mist sand-dusk"

# mix hexA over hexB at alpha% — simulates the style guide's opacity steps
retro_mix() { # $1 hexA  $2 hexB  $3 alpha(0-100)
  local ar ag ab br bg bb a=$3
  ar=$((16#${1:0:2})); ag=$((16#${1:2:2})); ab=$((16#${1:4:2}))
  br=$((16#${2:0:2})); bg=$((16#${2:2:2})); bb=$((16#${2:4:2}))
  printf '%02x%02x%02x' \
    $(( (ar * a + br * (100 - a)) / 100 )) \
    $(( (ag * a + bg * (100 - a)) / 100 )) \
    $(( (ab * a + bb * (100 - a)) / 100 ))
}
retro_fg24() { printf '\033[38;2;%d;%d;%dm' "$((16#${1:0:2}))" "$((16#${1:2:2}))" "$((16#${1:4:2}))"; }
retro_bg24() { printf '\033[48;2;%d;%d;%dm' "$((16#${1:0:2}))" "$((16#${1:2:2}))" "$((16#${1:4:2}))"; }

retro_eh_numero() { case "$1" in ''|*[!0-9]*) return 1 ;; *) return 0 ;; esac; }
retro_repetir() { # $1 = char, $2 = n
  local n=$2 s=""
  while [ "$n" -gt 0 ]; do s="$s$1"; n=$((n - 1)); done
  printf '%s' "$s"
}
retro_espacos() { printf '%*s' "$1" ''; }
retro_upper() { printf '%s' "$1" | tr '[:lower:]' '[:upper:]'; }

# ---------- init ----------
retro_init() { # $1 = box width (default 52)
  TEMA="${TEMA:-${RETRO_TEMA:-vault-gold}}"
  retro_tema_hex "$TEMA" >/dev/null 2>&1 || TEMA=vault-gold
  read -r HEX_BG HEX_FG HEX_ACC <<EOF
$(retro_tema_hex "$TEMA")
EOF

  USE_COLOR=1
  [ -n "${NO_COLOR:-}" ] && USE_COLOR=0
  [ -t 1 ] || USE_COLOR=0

  TRUECOLOR=0
  case "${COLORTERM:-}" in truecolor|24bit|*truecolor*|*24bit*) TRUECOLOR=1 ;; esac
  [ "$USE_COLOR" -eq 1 ] || TRUECOLOR=0

  DESENHA=0
  [ -t 1 ] && DESENHA=1

  COLS=$( { tput cols; } 2>/dev/null || echo 80 )
  retro_eh_numero "$COLS" || COLS=80
  BW="${1:-52}"
  [ "$COLS" -lt $((BW + 3)) ] && BW=$((COLS - 3))
  CAIXA=1
  { [ "$DESENHA" -eq 1 ] && [ "$BW" -ge 46 ]; } || CAIXA=0
  CLR=""
  [ "$DESENHA" -eq 1 ] && CLR=$'\033[K'
  CF=$((BW - 4))   # usable content width inside the box

  RESET="" BOLD="" DIM=""
  ACC="" ACC70="" ACC50="" ACC30="" ACC15="" FG="" FG70="" FG40=""
  INV="" OK="" ALERTA=""
  if [ "$USE_COLOR" -eq 1 ]; then
    RESET=$'\033[0m'; BOLD=$'\033[1m'; DIM=$'\033[2m'
    if [ "$TRUECOLOR" -eq 1 ]; then
      ACC=$(retro_fg24 "$HEX_ACC")
      ACC70=$(retro_fg24 "$(retro_mix "$HEX_ACC" "$HEX_BG" 70)")
      ACC50=$(retro_fg24 "$(retro_mix "$HEX_ACC" "$HEX_BG" 50)")
      ACC30=$(retro_fg24 "$(retro_mix "$HEX_ACC" "$HEX_BG" 30)")
      ACC15=$(retro_fg24 "$(retro_mix "$HEX_ACC" "$HEX_BG" 18)")
      FG=$(retro_fg24 "$HEX_FG")
      FG70=$(retro_fg24 "$(retro_mix "$HEX_FG" "$HEX_BG" 70)")
      FG40=$(retro_fg24 "$(retro_mix "$HEX_FG" "$HEX_BG" 40)")
      INV="$(retro_bg24 "$HEX_ACC")$(retro_fg24 "$HEX_BG")"
      OK=$(retro_fg24 "3fb950")
      ALERTA=$(retro_fg24 "e5534b")
    else
      ACC=$'\033[1;33m'; ACC70=$'\033[33m'; ACC50=$'\033[33m'
      ACC30=$'\033[2;33m'; ACC15=$'\033[2;33m'
      FG=$'\033[0m'; FG70=$'\033[0m'; FG40=$'\033[2m'
      INV=$'\033[7;33m'; OK=$'\033[1;32m'; ALERTA=$'\033[1;31m'
    fi
  fi
}

# ---------- box (terminal window recipe) ----------
retro_topo()   { printf '%s┏%s┓%s%s\n' "$ACC" "$(retro_repetir '━' $((BW - 2)))" "$RESET" "$CLR"; }
retro_sep()    { printf '%s┠%s┨%s%s▒%s%s\n' "$ACC" "$(retro_repetir '─' $((BW - 2)))" "$RESET" "$ACC15" "$RESET" "$CLR"; }
retro_base()   { printf '%s┗%s┛%s%s▒%s%s\n' "$ACC" "$(retro_repetir '━' $((BW - 2)))" "$RESET" "$ACC15" "$RESET" "$CLR"; }
retro_sombra() { printf ' %s%s%s%s\n' "$ACC15" "$(retro_repetir '▒' "$BW")" "$RESET" "$CLR"; }

retro_linha() { # $1 = already-colored content, $2 = visible width of that content
  local pad=$((CF - $2))
  [ "$pad" -lt 0 ] && pad=0
  printf '%s┃%s %s%s %s┃%s%s▒%s%s\n' \
    "$ACC" "$RESET" "$1" "$(retro_espacos "$pad")" "$ACC" "$RESET" "$ACC15" "$RESET" "$CLR"
}
retro_vazia() { retro_linha "" 0; }

retro_chrome() { # $1 = title (path), $2 = right-hand meta
  local t=$1 m=${2:-}
  local pad=$((CF - 7 - ${#t} - ${#m}))
  while [ "$pad" -lt 1 ] && [ -n "$t" ]; do   # title gives way before the meta
    t="${t%?}"; pad=$((CF - 7 - ${#t} - ${#m}))
  done
  [ "$pad" -lt 1 ] && pad=1
  printf '%s┃%s %s●%s %s●%s %s●%s  %s%s%s%s%s%s%s %s┃%s%s▒%s%s\n' \
    "$ACC" "$RESET" "$ACC" "$RESET" "$ACC50" "$RESET" "$ACC30" "$RESET" \
    "$ACC50" "$t" "$RESET" "$(retro_espacos "$pad")" "$ACC30" "$m" "$RESET" \
    "$ACC" "$RESET" "$ACC15" "$RESET" "$CLR"
}

retro_status() { # $1 = left (plain), $2 = right (plain)
  local e=$1 d=${2:-}
  local pad=$((CF - ${#e} - ${#d}))
  while [ "$pad" -lt 1 ] && [ -n "$e" ]; do   # left side gives way before the status
    e="${e%?}"; pad=$((CF - ${#e} - ${#d}))
  done
  [ "$pad" -lt 1 ] && pad=1
  printf '%s┃%s%s %s%s%s %s%s┃%s%s▒%s%s\n' \
    "$ACC" "$INV" "$BOLD" "$e" "$(retro_espacos "$pad")" "$d" "$RESET" \
    "$ACC" "$RESET" "$ACC15" "$RESET" "$CLR"
}

# ---------- flat blocks (outside the box) ----------
retro_modulo() { # $1 = label, $2 = optional right meta   → [ MODULE: X ]      META
  local m; m=$(retro_upper "$1")
  printf '\n  %s%s[ MODULE: %s ]%s' "$ACC" "$BOLD" "$m" "$RESET"
  [ -n "${2:-}" ] && printf '  %s%s%s' "$ACC30" "$(retro_upper "$2")" "$RESET"
  printf '\n\n'
}

retro_secao() { # $1 = label   → # HEADING
  printf '  %s# %s%s\n' "$ACC" "$(retro_upper "$1")" "$RESET"
}

retro_kv() { # $1 key  $2 value   (dot leader, key dim, value accent-bold)
  local k=$1 v=$2 pontos=$(( COLS > 60 ? 44 : COLS - 12 ))
  [ "$pontos" -lt 20 ] && pontos=20
  local n=$((pontos - ${#k} - ${#v}))
  [ "$n" -lt 2 ] && n=2
  printf '  %s%s%s %s%s%s %s%s%s\n' \
    "$FG40" "$k" "$RESET" "$ACC15" "$(retro_repetir '·' "$n")" "$RESET" "$ACC$BOLD" "$v" "$RESET"
}

retro_regra() { # thin separator
  printf '  %s%s%s\n' "$ACC15" "$(retro_repetir '─' $(( COLS > 60 ? 44 : COLS - 12 )))" "$RESET"
}

retro_ok()     { printf '  %s[ OK ]%s %s%s%s%s\n' "$OK" "$RESET" "$ACC" "$BOLD" "$(retro_upper "$1")" "$RESET"; }
retro_erro()   { printf '  %s[ ERRO ]%s %s\n' "$ALERTA" "$RESET" "$1"; }
retro_aviso()  { printf '  %s[ %s ]%s %s\n' "$FG40" "$(retro_upper "$1")" "$RESET" "${2:-}"; }
retro_proximo(){ printf '  %s>%s %s  %s%s%s%s\n' "$ACC30" "$RESET" "${2:-proximo passo:}" "$ACC" "$BOLD" "$1" "$RESET"; }

retro_barra() { # $1 = done, $2 = total, $3 = width   → ████▒▒▒▒  62%
  local n=$1 total=$2 lar=${3:-24} i feito pct s=""
  [ "$total" -le 0 ] && total=1
  feito=$(( n * lar / total )); pct=$(( n * 100 / total ))
  [ "$feito" -gt "$lar" ] && feito=$lar
  i=0
  while [ "$i" -lt "$lar" ]; do
    if [ "$i" -lt "$feito" ]; then s="${s}█"; else s="${s}▒"; fi
    i=$((i + 1))
  done
  printf '%s%s%s%s%s  %s%3d%%%s' \
    "$ACC" "${s:0:$feito}" "$ACC15" "${s:$feito}" "$RESET" "$ACC$BOLD" "$pct" "$RESET"
}

retro_catalogo_temas() { # theme picker screen, shared by every tool
  local envvar=${1:-RETRO_TEMA}
  retro_modulo "theme_catalog"
  local t hb hf ha swatch marca
  for t in $RETRO_TEMAS; do
    read -r hb hf ha <<EOF
$(retro_tema_hex "$t")
EOF
    marca="  "
    [ "$t" = "$TEMA" ] && marca="► "
    if [ "$TRUECOLOR" -eq 1 ]; then
      swatch="$(retro_bg24 "$ha")    $RESET$(retro_bg24 "$hf")  $RESET$(retro_bg24 "$hb")  $RESET"
    else
      swatch="[#$ha]"
    fi
    printf '  %s%s%s%-16s%s %s  %s#%s%s\n' \
      "$ACC" "$marca" "$RESET" "$t" "$RESET" "$swatch" "$ACC15" "$ha" "$RESET"
  done
  printf '\n  %sexport %s=<nome>%s\n\n' "$FG40" "$envvar" "$RESET"
}
