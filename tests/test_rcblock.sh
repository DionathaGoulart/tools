#!/usr/bin/env bash
# Smoke tests for lib/rcblock.sh + load.sh — the managed rc block.
# Pure bash + a temp sandbox, no framework. Run from anywhere:
#   bash tests/test_rcblock.sh
# Exits non-zero if any assertion fails.
#
# O sandbox usa GOODTOOLS_RC (rc alvo) e GOODTOOLS_LINK (symlink âncora), então
# nada aqui toca no ~/.zshrc nem no ~/.goodtools de verdade.

set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SB="$(mktemp -d)"
trap 'rm -rf "$SB"' EXIT

export GOODTOOLS_RC="$SB/rc"
export GOODTOOLS_LINK="$SB/link"
export NO_COLOR=1

ok=0
ko=0
check() { # <desc> <cmd...>  — saída 0 = passou
  local desc="$1"; shift
  if "$@"; then ok=$((ok + 1)); else echo "  FAIL: $desc"; ko=$((ko + 1)); fi
}
check_nao() { # <desc> <cmd...>  — saída NÃO-zero = passou
  local desc="$1"; shift
  if "$@" >/dev/null 2>&1; then echo "  FAIL: $desc (esperava falhar)"; ko=$((ko + 1)); else ok=$((ok + 1)); fi
}
rc_tem()   { grep -qF "$1" "$GOODTOOLS_RC"; }
rc_nao_tem() { ! grep -qF "$1" "$GOODTOOLS_RC"; }
blocos()   { grep -c '^# >>> good tools >>>$' "$GOODTOOLS_RC"; }
lista_eh() { [ "$(gt_list "$GOODTOOLS_RC")" = "$1" ]; }

# shellcheck source=../lib/rcblock.sh
. "$ROOT/lib/rcblock.sh"

# ---------- instalação do zero ----------
: > "$GOODTOOLS_RC"
gt_add "$ROOT" goodcheats
check "escreve o bloco"                 rc_tem '# >>> good tools >>>'
check "fecha o bloco"                   rc_tem '# <<< good tools <<<'
check "chama o loader"                  rc_tem 'goodtools_load goodcheats'
check "ancora em GOODTOOLS_ROOT"        rc_tem 'export GOODTOOLS_ROOT='
check "sem caminho absoluto do repo"    rc_nao_tem "$ROOT/goodcheats/setup.sh"
check "cria o symlink âncora"           test -L "$GOODTOOLS_LINK"
check "symlink aponta pro repo"         test "$(readlink "$GOODTOOLS_LINK")" = "$ROOT"

# ---------- segunda ferramenta: mesma lista, um bloco só ----------
gt_add "$ROOT" goodivers
gt_add "$ROOT" images/goodpixel
check "acumula na mesma lista"          lista_eh "goodcheats goodivers images/goodpixel"
check "continua com um bloco só"        test "$(blocos)" = 1
check "gt_has acha o que instalou"      gt_has "$GOODTOOLS_RC" goodivers
check_nao "gt_has nega o que não instalou" gt_has "$GOODTOOLS_RC" goodzap

# ---------- reinstalar não duplica ----------
gt_add "$ROOT" goodivers
check "reinstalar não duplica nome"     lista_eh "goodcheats goodivers images/goodpixel"
check "reinstalar não duplica bloco"    test "$(blocos)" = 1

# ---------- desinstalar ----------
gt_remove "$ROOT" goodivers
check "tira só a ferramenta pedida"     lista_eh "goodcheats images/goodpixel"
gt_remove "$ROOT" goodcheats
gt_remove "$ROOT" images/goodpixel
check "última leva o bloco junto"       rc_nao_tem '# >>> good tools >>>'
check "última leva a âncora junto"      test ! -L "$GOODTOOLS_LINK"

# ---------- migração do formato antigo ----------
# rc de quem instalou antes: caminho absoluto por ferramenta, nomes que já não
# existem mais (good, pomo, zapstats) e goodpixel sem o prefixo images/
VELHO="/qualquer/lugar/tools"
cat > "$GOODTOOLS_RC" <<EOF
export EDITOR=vim

# tools/good — comando good (fetch de sistema)
[ -f "$VELHO/good/setup.sh" ] && source "$VELHO/good/setup.sh"

# tools/goodcheats — comandos good, goodcheat…
[ -f "$VELHO/goodcheats/setup.sh" ] && source "$VELHO/goodcheats/setup.sh"

# tools/pomo — comando pomo (pomodoro no terminal)
[ -f "$VELHO/pomo/setup.sh" ] && source "$VELHO/pomo/setup.sh"

# tools/goodivers — copiloto do canal (Helldivers 2)
# export GOODIVERS_LEMBRETE=1  # descomente pra lembrete diário
[ -f "$VELHO/goodivers/setup.sh" ] && source "$VELHO/goodivers/setup.sh"

# tools/images/goodpixel — comando goodpixel (imagem -> pixel art)
[ -f "$VELHO/images/goodpixel/setup.sh" ] && source "$VELHO/images/goodpixel/setup.sh"

alias ll='ls -la'
EOF

gt_add "$ROOT" goodzap
check "migra o que ainda existe"         gt_has "$GOODTOOLS_RC" goodcheats
check "migra e mantém goodivers"         gt_has "$GOODTOOLS_RC" goodivers
check "reprefixa images/goodpixel"       gt_has "$GOODTOOLS_RC" images/goodpixel
check "adiciona a nova"                  gt_has "$GOODTOOLS_RC" goodzap
check_nao "descarta nome morto (good)"   gt_has "$GOODTOOLS_RC" good
check_nao "descarta nome morto (pomo)"   gt_has "$GOODTOOLS_RC" pomo
check "apaga as linhas antigas"          rc_nao_tem "$VELHO"
check "apaga o comentário antigo"        rc_nao_tem '# tools/goodcheats'
check "preserva o resto do rc (EDITOR)"  rc_tem 'export EDITOR=vim'
check "preserva o resto do rc (alias)"   rc_tem "alias ll='ls -la'"
check "migração deixa um bloco só"       test "$(blocos)" = 1

# ---------- load.sh ----------
# num shell limpo: bloco do rc -> PATH com as ferramentas
saida="$(env -u GOODTOOLS_ROOT PATH="/usr/bin:/bin" bash -c '
  . "$1/load.sh"
  export GOODTOOLS_ROOT="$1"
  goodtools_load goodcheats images/goodpixel
  printf %s "$PATH"
' _ "$ROOT" 2>/dev/null)"
case "$saida" in
  *"$ROOT/goodcheats"*)    ok=$((ok + 1)) ;;
  *) echo "  FAIL: load.sh põe goodcheats no PATH"; ko=$((ko + 1)) ;;
esac
case "$saida" in
  *"$ROOT/images/goodpixel"*) ok=$((ok + 1)) ;;
  *) echo "  FAIL: load.sh põe images/goodpixel no PATH"; ko=$((ko + 1)) ;;
esac
case "$saida" in
  *"$ROOT/goodhelp"*)      ok=$((ok + 1)) ;;
  *) echo "  FAIL: load.sh põe goodhelp no PATH"; ko=$((ko + 1)) ;;
esac

# ferramenta que sumiu: avisa alto, nunca falha calado
erro="$(bash -c '
  . "$1/load.sh"
  export GOODTOOLS_ROOT="$1"
  goodtools_load nao-existe
' _ "$ROOT" 2>&1 >/dev/null)"
case "$erro" in
  *"nao-existe"*) ok=$((ok + 1)) ;;
  *) echo "  FAIL: load.sh avisa sobre ferramenta ausente"; ko=$((ko + 1)) ;;
esac

# raiz que não resolve: avisa e devolve erro
erro="$(bash -c '
  . "$1/load.sh"
  export GOODTOOLS_ROOT="/nao/existe/mesmo"
  goodtools_load goodcheats
' _ "$ROOT" 2>&1 >/dev/null)"
case "$erro" in
  *"não resolve"*) ok=$((ok + 1)) ;;
  *) echo "  FAIL: load.sh avisa quando a raiz some"; ko=$((ko + 1)) ;;
esac

# ---------- resultado ----------
echo
echo "rcblock: $ok passaram, $ko falharam"
[ "$ko" -eq 0 ]
