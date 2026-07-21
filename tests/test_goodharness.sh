#!/usr/bin/env bash
# Smoke tests for goodharness (Fase 1: bundle presets, init scaffold, config.json).
# Pure bash + a temp sandbox — no framework. Run from anywhere:
#   bash tests/test_goodharness.sh
# Exits non-zero if any assertion fails. Config assertions are skipped without jq.

set -u

GH="$(cd "$(dirname "$0")/.." && pwd)/goodcheats/goodharness"
SB="$(mktemp -d)"
trap 'rm -rf "$SB"' EXIT
export GOODHARNESS_DIR="$SB/presets"
export GOODHARNESS_STATE="$SB/state"   # isola o registry (não toca ~/.goodharness)
export NO_COLOR=1

HAS_JQ=0
command -v jq >/dev/null 2>&1 && HAS_JQ=1

ok=0
ko=0
check() { # <desc> <cmd...>  — cmd's exit 0 = pass
  local desc="$1"; shift
  if "$@"; then ok=$((ok + 1)); else echo "  FAIL: $desc"; ko=$((ko + 1)); fi
}
check_fail() { # <desc> <cmd...>  — cmd's NON-zero exit = pass
  local desc="$1"; shift
  if "$@" >/dev/null 2>&1; then echo "  FAIL: $desc (esperava erro)"; ko=$((ko + 1)); else ok=$((ok + 1)); fi
}
file_has() { grep -q "$2" "$1" 2>/dev/null; }

# ---------- init ----------
mkdir -p "$SB/proj1"
bash "$GH" init "$SB/proj1" >/dev/null 2>&1
check "init cria config.json"          test -f "$SB/proj1/.harness/config.json"
check "init cria styleguide.md"        test -f "$SB/proj1/.harness/styleguide.md"
check "init cria memory/features.md"   test -f "$SB/proj1/.harness/memory/features.md"
check "init cria plans/.gitkeep"       test -f "$SB/proj1/.harness/plans/.gitkeep"

# ---------- config (jq) ----------
if [ "$HAS_JQ" -eq 1 ]; then
  bash "$GH" config set tracker_team PROD "$SB/proj1" >/dev/null 2>&1
  check "config set/get roundtrip"     test "$(bash "$GH" config get tracker_team "$SB/proj1")" = "PROD"
else
  echo "  (jq ausente — pulando testes de config)"
fi

# ---------- copy bundle ----------
mkdir -p "$SB/src/.harness/rules"
printf '# SG web\n'      > "$SB/src/.harness/styleguide.md"
printf '# SG terminal\n' > "$SB/src/.harness/styleguide-terminal.md"
printf '# dry\n'         > "$SB/src/.harness/rules/dry.md"
printf 'x=segredo\n'     > "$SB/src/.harness/config.json"   # não deve ser capturado
bash "$GH" copy meu-tema "$SB/src" >/dev/null 2>&1
check "bundle captura styleguide.md"           test -f "$SB/presets/meu-tema/styleguide.md"
check "bundle captura styleguide-terminal.md"  test -f "$SB/presets/meu-tema/styleguide-terminal.md"
check "bundle captura rules/"                  test -f "$SB/presets/meu-tema/rules/dry.md"
check "bundle NAO captura config.json (leak)"  test ! -f "$SB/presets/meu-tema/config.json"
check "bundle gera manifest.json"              test -f "$SB/presets/meu-tema/manifest.json"

# ---------- install bundle (merge preserva valores) ----------
bash "$GH" install meu-tema "$SB/proj1" --force >/dev/null 2>&1
check "install copia styleguide-terminal.md"   test -f "$SB/proj1/.harness/styleguide-terminal.md"
check "install copia rules/dry.md"             test -f "$SB/proj1/.harness/rules/dry.md"
check "install escreve recibo"                 test -f "$SB/proj1/.harness/.goodharness.json"
check "install faz backup .bak"                test -f "$SB/proj1/.harness/styleguide.md.bak"
if [ "$HAS_JQ" -eq 1 ]; then
  check "merge preserva tracker_team"          test "$(bash "$GH" config get tracker_team "$SB/proj1")" = "PROD"
fi

# ---------- retrocompat: preset .md legado ----------
printf '# legacy\nl2\n' > "$SB/one.md"
bash "$GH" copy legado "$SB/one.md" >/dev/null 2>&1
check "preset legado salvo como .md"   test -f "$SB/presets/legado.md"
mkdir -p "$SB/proj2"
bash "$GH" install legado "$SB/proj2" >/dev/null 2>&1
check "install legado -> styleguide.md" file_has "$SB/proj2/.harness/styleguide.md" "legacy"

# ---------- list / erros ----------
check      "list roda"                    bash "$GH" list
check_fail "copy nome invalido falha"     bash "$GH" copy 'x/y' "$SB/one.md"
check_fail "copy duplicado sem --force falha" bash "$GH" copy meu-tema "$SB/src"
check_fail "install inexistente falha"    bash "$GH" install fantasma "$SB/proj1"

# ---------- Fase 2: link / diff / update / sync ----------
mkdir -p "$SB/projL"
bash "$GH" install meu-tema "$SB/projL" --link >/dev/null 2>&1
check "install --link cria symlink"       test -L "$SB/projL/.harness/styleguide.md"
check "link NAO symlinka config.json"     test ! -L "$SB/projL/.harness/config.json"
check "diff apos install = identico"      bash "$GH" diff meu-tema "$SB/projL"

# altera o preset -> cópia (proj1) fica em drift; o link segue idêntico
printf '# mudou v2\n' >> "$SB/presets/meu-tema/styleguide.md"
check_fail "diff acusa drift na copia"    bash "$GH" diff meu-tema "$SB/proj1"
check      "diff do link segue identico"  bash "$GH" diff meu-tema "$SB/projL"
bash "$GH" update meu-tema "$SB/proj1" >/dev/null 2>&1
check "update remove o drift"             bash "$GH" diff meu-tema "$SB/proj1"

if [ "$HAS_JQ" -eq 1 ]; then
  check "update preserva config (merge)"  test "$(bash "$GH" config get tracker_team "$SB/proj1")" = "PROD"
  check "status roda"                     bash "$GH" status
  check "sync roda"                       bash "$GH" sync meu-tema
  check "sync sem jq-less: rows ok"       test -f "$SB/state/registry.json"
fi

# ---------- resultado ----------
echo "goodharness: $ok ok, $ko fail"
[ "$ko" -eq 0 ]
