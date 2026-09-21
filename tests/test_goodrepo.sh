#!/usr/bin/env bash
# Smoke tests for goodrepo: add (with dependencies), the generated index, status, update, rm,
# conflicts with files that are not goodrepo's. Pure bash + a temp sandbox, no framework:
#   bash tests/test_goodrepo.sh
# Exits non-zero if any assertion fails.

set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GR="$ROOT/goodrepo/goodrepo"
SB="$(mktemp -d)"
trap 'rm -rf "$SB"' EXIT
export NO_COLOR=1

ok=0
ko=0
check() { # <desc> <cmd...>  cmd exit 0 = pass
  local desc="$1"; shift
  if "$@"; then ok=$((ok + 1)); else echo "  FAIL: $desc"; ko=$((ko + 1)); fi
}
check_fail() { # <desc> <cmd...>  cmd NON-zero exit = pass
  local desc="$1"; shift
  if "$@" >/dev/null 2>&1; then echo "  FAIL: $desc (esperava erro)"; ko=$((ko + 1)); else ok=$((ok + 1)); fi
}
file_has() { grep -q -- "$2" "$1" 2>/dev/null; }
gr() { bash "$GR" -C "$P" "$@" 2>&1; }

# ---------- fonte: todo arquivo do catálogo existe ----------
# (lê ARQS direto do script, então um guia renomeado sem atualizar o catálogo falha aqui)
while IFS= read -r rel; do
  check "fonte tem $rel" test -f "$ROOT/goodrepo/guias/$rel"
done < <(sed -n '/^ARQS=(/,/^)/p' "$GR" | grep -o '[a-z][A-Za-z0-9./_-]*\.[a-z]*' | sort -u)

# ---------- add com dependências ----------
P="$SB/proj"; mkdir -p "$P"
out="$(gr add readme)"
check "add readme instala o guia"            test -f "$P/.harness/repo/padrao-readme.md"
check "add readme traz os modelos"           test -f "$P/.harness/repo/modelos/README.pt-BR.md"
check "readme puxa escrita (dependência)"    test -f "$P/.harness/repo/escrita.md"
check "readme puxa licenca (dependência)"    test -f "$P/.harness/repo/licencas/MIT.txt"
check "avisa as dependências"                file_has <(echo "$out") "escrita"
check "manifesto criado"                     test -f "$P/.harness/repo/.goodrepo"
check "manifesto lista o guia"               file_has "$P/.harness/repo/.goodrepo" "^guia readme"
check "índice gerado"                        test -f "$P/.harness/repo/README.md"
check "índice cita padrao-readme.md"         file_has "$P/.harness/repo/README.md" "(padrao-readme.md)"
# macOS é case-insensitive: o índice README.md não pode colidir com nenhum guia
check "guia intacto depois do índice"        cmp -s "$P/.harness/repo/padrao-readme.md" "$ROOT/goodrepo/guias/repo/padrao-readme.md"
check "styleguide não veio junto"            test ! -f "$P/.harness/styleguide.md"

# ---------- styleguide na raiz do .harness ----------
gr add cli >/dev/null
check "cli instala styleguide-cli.md"        test -f "$P/.harness/styleguide-cli.md"
check "cli puxa styleguide.md"               test -f "$P/.harness/styleguide.md"
check "styleguide traz as skins"             test -f "$P/.harness/styleguides/retro.md"
check "índice aponta ../styleguide.md"       file_has "$P/.harness/repo/README.md" "(../styleguide.md)"

# ---------- links relativos dos guias instalados resolvem ----------
broken=0
while IFS= read -r f; do
  d="$(dirname "$f")"
  for l in $(grep -oE '\]\([^)#]+' "$f" | sed 's/^](//' | grep -v '^https\?:'); do
    case "$l" in *'{{'*|LICENSE|SECURITY.md|CHANGELOG.md|CONTRIBUTING.md|docs/*|arquivo) continue ;; esac
    [ -e "$d/$l" ] || { echo "    link quebrado: $f -> $l"; broken=1; }
  done
done < <(find "$P/.harness" -name '*.md' -not -path '*/modelos/*')
check "links entre guias instalados resolvem" test "$broken" -eq 0

# ---------- status ----------
check "status tudo ok"                       file_has <(gr status) "TUDO IGUAL"
echo "mudança local" >> "$P/.harness/repo/escrita.md"
st="$(gr status)"
check "status vê arquivo editado"            file_has <(echo "$st") "EDITADO"

# ---------- update respeita edição local ----------
# simula guia novo na fonte: cópia da fonte com um arquivo alterado
SRC="$SB/guias"; cp -R "$ROOT/goodrepo/guias" "$SRC"
echo "linha nova na fonte" >> "$SRC/repo/git.md"
GOODREPO_GUIAS="$SRC" bash "$GR" -C "$P" add git >/dev/null 2>&1
echo "outra linha" >> "$SRC/repo/git.md"
check "status vê desatualizado"              file_has <(GOODREPO_GUIAS="$SRC" bash "$GR" -C "$P" status 2>&1) "DESATUALIZADO"
GOODREPO_GUIAS="$SRC" bash "$GR" -C "$P" update >/dev/null 2>&1
check "update traz a versão nova"            file_has "$P/.harness/repo/git.md" "outra linha"
check "update não passa por cima de edição"  file_has "$P/.harness/repo/escrita.md" "mudança local"
GOODREPO_GUIAS="$SRC" bash "$GR" -C "$P" update -f >/dev/null 2>&1
check "update -f sobrescreve"                test ! "$(grep -c 'mudança local' "$P/.harness/repo/escrita.md")" -gt 0
check "update -f deixa backup .bak"          file_has "$P/.harness/repo/escrita.md.bak" "mudança local"

# ---------- arquivo que não é do goodrepo ----------
P="$SB/proj2"; mkdir -p "$P/.harness"
echo "# meu styleguide" > "$P/.harness/styleguide.md"
gr add styleguide >/dev/null
check "não sobrescreve styleguide alheio"    file_has "$P/.harness/styleguide.md" "meu styleguide"
check "mas instala o resto do guia"          test -f "$P/.harness/styleguides/retro.md"
gr add styleguide -f >/dev/null
check "-f sobrescreve alheio"                test ! "$(grep -c 'meu styleguide' "$P/.harness/styleguide.md")" -gt 0
check "-f guarda o alheio em .bak"           file_has "$P/.harness/styleguide.md.bak" "meu styleguide"

# ---------- rm ----------
P="$SB/proj3"; mkdir -p "$P"
gr add seguranca >/dev/null
gr rm seguranca >/dev/null
check "rm apaga o guia"                      test ! -f "$P/.harness/repo/seguranca.md"
check "rm apaga os modelos do guia"          test ! -f "$P/.harness/repo/modelos/SECURITY.en.md"
check "rm mantém a dependência"              test -f "$P/.harness/repo/escrita.md"
check "manifesto esquece o guia"             test ! "$(grep -c '^guia seguranca' "$P/.harness/repo/.goodrepo")" -gt 0
gr rm escrita >/dev/null
check "último guia sai: some o manifesto"    test ! -f "$P/.harness/repo/.goodrepo"
check "e some a pasta repo/"                 test ! -d "$P/.harness/repo"

# ---------- erros ----------
check_fail "guia desconhecido"               bash "$GR" -C "$SB/proj3" add nada
check_fail "update sem nada instalado"       bash "$GR" -C "$SB/proj3" update
check_fail "-C inexistente"                  bash "$GR" -C "$SB/nao-existe" list
check_fail "comando desconhecido"            bash "$GR" -C "$SB/proj3" voar

echo "goodrepo: $ok ok, $ko falha(s)"
[ "$ko" -eq 0 ]
