#!/usr/bin/env bash
# setup.sh — instalador interativo das ferramentas (macOS / Linux / Git Bash)
#
#   bash setup.sh        ← lista tudo, você marca o que quer, Enter instala
#   bash setup.sh -u     ← desinstalar (lista só o que está instalado)
#
# Teclas: 1-9 marca/desmarca · a todos · n nenhum · Enter confirma · q sai
# "Instalada" = a linha `source .../setup.sh` existe em algum rc do shell
# (exceção: goodivers-skill = symlink em ~/.claude/skills/goodivers).
# Desinstalar remove do rc as linhas da ferramenta (backup: <rc>.tools-backup).

ROOT="$(cd "$(dirname "$0")" && pwd)"

NOMES=(goodcheats pomo professor biografo vocab zapstats goodivers goodivers-skill)
DESCS=(
  "kit good: fetch de sistema + cheatsheets + styleguides"
  "pomodoro no terminal com notificação e stats"
  "estudo Feynman invertido, te sabatina até dominar (IA)"
  "sua autobiografia, uma pergunta por dia (IA)"
  "uma palavra de inglês por dia, revisão espaçada (IA)"
  "retrô de conversa exportada do WhatsApp (IA)"
  "copiloto do canal de Helldivers 2 no terminal (OpenRouter)"
  "skill /goodivers no Claude Code: gera com o Claude, sem chave"
)

RCS=("$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.bash_profile")
SKILL_GOODIVERS="$HOME/.claude/skills/goodivers"

instalada() {
  case "$1" in
    goodivers-skill) [ -L "$SKILL_GOODIVERS" ] ;;
    *) grep -qsF "$1/setup.sh" "${RCS[@]}" 2>/dev/null ;;
  esac
}

MODO=install
case "${1:-}" in
  -u|--uninstall|uninstall|desinstalar) MODO=uninstall ;;
  -h|--help) sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
esac

# monta a lista visível (uninstall: só as instaladas)
ITENS=()
for i in "${!NOMES[@]}"; do
  if [ "$MODO" = uninstall ]; then
    instalada "${NOMES[$i]}" && ITENS+=("$i")
  else
    ITENS+=("$i")
  fi
done
if [ "${#ITENS[@]}" -eq 0 ]; then
  echo "nenhuma ferramenta instalada — nada pra desinstalar."
  exit 0
fi

SEL=()
for _ in "${ITENS[@]}"; do SEL+=(0); done
AVISO=""

draw() {
  printf '\033[H\033[2J'
  if [ "$MODO" = uninstall ]; then
    printf '\033[1m🗑  tools — desinstalar\033[0m  \033[2m(mostrando só as instaladas)\033[0m\n\n'
  else
    printf '\033[1m🧰 tools — instalar\033[0m\n\n'
  fi
  local n=1 i caixa tag
  for k in "${!ITENS[@]}"; do
    i="${ITENS[$k]}"
    caixa="[ ]"
    [ "${SEL[$k]}" = 1 ] && caixa="\033[1;32m[x]\033[0m"
    tag=""
    [ "$MODO" = install ] && instalada "${NOMES[$i]}" && tag="  \033[2m(já instalada)\033[0m"
    printf "  $caixa %d. \033[1m%-15s\033[0m %s$tag\n" "$n" "${NOMES[$i]}" "${DESCS[$i]}"
    n=$((n + 1))
  done
  printf '\n  \033[2m1-9 marca/desmarca · a todos · n nenhum · Enter confirma · q sai\033[0m\n'
  if [ "$MODO" = install ]; then
    printf '  \033[2mdesinstalar: bash setup.sh -u · goodpen tem setup próprio (goodpen/README.md)\033[0m\n'
  fi
  [ -n "$AVISO" ] && printf '\n  \033[33m%s\033[0m\n' "$AVISO"
}

while :; do
  draw
  IFS= read -rsn1 t || t=q
  AVISO=""
  case "$t" in
    [1-9])
      k=$((t - 1))
      if [ "$k" -lt "${#ITENS[@]}" ]; then
        if [ "${SEL[$k]}" = 1 ]; then SEL[$k]=0; else SEL[$k]=1; fi
      fi ;;
    a|A) for k in "${!SEL[@]}"; do SEL[$k]=1; done ;;
    n|N) for k in "${!SEL[@]}"; do SEL[$k]=0; done ;;
    "")
      MARCADAS=()
      for k in "${!ITENS[@]}"; do
        [ "${SEL[$k]}" = 1 ] && MARCADAS+=("${NOMES[${ITENS[$k]}]}")
      done
      if [ "${#MARCADAS[@]}" -eq 0 ]; then
        AVISO="marque pelo menos uma (tecla 1-9, ou 'a' pra todas)"
        continue
      fi
      break ;;
    q|Q) printf '\ncancelado.\n'; exit 0 ;;
  esac
done

printf '\033[H\033[2J'
if [ "$MODO" = install ]; then
  for t in "${MARCADAS[@]}"; do
    printf '\n\033[1m→ %s\033[0m\n' "$t"
    if [ "$t" = goodivers-skill ]; then
      bash "$ROOT/goodivers/setup.sh" --skill
    else
      bash "$ROOT/$t/setup.sh"
    fi
  done
  printf '\n✅ %d instalada(s). Abra um terminal novo (ou:  source ~/.zshrc).\n' "${#MARCADAS[@]}"
else
  # backup de cada rc existente, uma vez por execução
  for rc in "${RCS[@]}"; do
    [ -f "$rc" ] && cp "$rc" "$rc.tools-backup"
  done
  for t in "${MARCADAS[@]}"; do
    if [ "$t" = goodivers-skill ]; then
      # remove só se for symlink apontando pra este repo
      if [ -L "$SKILL_GOODIVERS" ]; then
        case "$(readlink "$SKILL_GOODIVERS")" in
          "$ROOT/goodivers"*) rm -f "$SKILL_GOODIVERS"
                              printf '  − skill /goodivers removida de ~/.claude/skills\n' ;;
        esac
      fi
      continue
    fi
    T_UP="$(printf %s "$t" | tr '[:lower:]' '[:upper:]')"
    for rc in "${RCS[@]}"; do
      [ -f "$rc" ] || continue
      grep -qsF "$t/setup.sh" "$rc" || continue
      awk -v t="$t" -v T="$T_UP" '
        index($0, t "/setup.sh")      { next }
        index($0, "# tools/" t)       { next }
        index($0, T "_LEMBRETE=")     { next }
        { print }
      ' "$rc" > "$rc.tmp$$" && mv "$rc.tmp$$" "$rc"
      printf '  − %s removida de %s\n' "$t" "${rc/#$HOME/~}"
    done
  done
  printf '\n✅ pronto. Vale pros próximos terminais (backup em <rc>.tools-backup).\n'
fi
