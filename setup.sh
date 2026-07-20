#!/usr/bin/env bash
# setup.sh — instalador interativo das ferramentas (macOS / Linux / Git Bash)
#
#   bash setup.sh        ← lista tudo, você marca o que quer e confirma no botão
#   bash setup.sh -u     ← desinstalar (lista só o que está instalado)
#
# Teclas: ↑↓ navega · espaço/Enter marca · 1-9 marca direto · a todos · n nenhum
#         Enter (ou espaço) no botão [Instalar] confirma · q sai
# "Instalada" = a linha `source .../setup.sh` existe em algum rc do shell
# (exceção: goodivers-skill = symlink em ~/.claude/skills/goodivers).
# Desinstalar remove do rc as linhas da ferramenta (backup: <rc>.tools-backup).

ROOT="$(cd "$(dirname "$0")" && pwd)"

NOMES=(goodcheats pomo professor biografo vocab zapstats goodivers goodivers-skill dark dark-skill)
DESCS=(
  "kit good: fetch de sistema + cheatsheets + styleguides"
  "pomodoro no terminal com notificação e stats"
  "estudo Feynman invertido, te sabatina até dominar (IA)"
  "sua autobiografia, uma pergunta por dia (IA)"
  "uma palavra de inglês por dia, revisão espaçada (IA)"
  "retrô de conversa exportada do WhatsApp (IA)"
  "copiloto do canal de Helldivers 2 no terminal (OpenRouter)"
  "skill /goodivers no Claude Code: gera com o Claude, sem chave"
  "copiloto do Instagram @darkning.art, horror art (OpenRouter)"
  "skill /dark no Claude Code: gera com o Claude, sem chave"
)

RCS=("$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.bash_profile")
SKILL_GOODIVERS="$HOME/.claude/skills/goodivers"
SKILL_DARK="$HOME/.claude/skills/dark"

instalada() {
  case "$1" in
    goodivers-skill) [ -L "$SKILL_GOODIVERS" ] ;;
    dark-skill) [ -L "$SKILL_DARK" ] ;;
    *) grep -qsF "$1/setup.sh" "${RCS[@]}" 2>/dev/null ;;
  esac
}

MODO=install
case "${1:-}" in
  -u|--uninstall|uninstall|desinstalar) MODO=uninstall ;;
  -h|--help) sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
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
CUR=0                 # linha do cursor (itens + botão no fim)
BTN="${#ITENS[@]}"    # índice do botão

ROTULO="Instalar"
[ "$MODO" = uninstall ] && ROTULO="Desinstalar"

draw() {
  printf '\033[H\033[2J'
  if [ "$MODO" = uninstall ]; then
    printf '\033[1m🗑  tools — desinstalar\033[0m  \033[2m(mostrando só as instaladas)\033[0m\n\n'
  else
    printf '\033[1m🧰 tools — instalar\033[0m\n\n'
  fi
  local n=1 i caixa tag seta
  for k in "${!ITENS[@]}"; do
    i="${ITENS[$k]}"
    caixa="[ ]"
    [ "${SEL[$k]}" = 1 ] && caixa="\033[1;32m[x]\033[0m"
    seta="  "
    [ "$CUR" = "$k" ] && seta="\033[1;36m❯\033[0m "
    tag=""
    [ "$MODO" = install ] && instalada "${NOMES[$i]}" && tag="  \033[2m(já instalada)\033[0m"
    printf " $seta$caixa %d. \033[1m%-15s\033[0m %s$tag\n" "$n" "${NOMES[$i]}" "${DESCS[$i]}"
    n=$((n + 1))
  done
  if [ "$CUR" = "$BTN" ]; then
    printf '\n   \033[1;7m  %s  \033[0m\n' "$ROTULO"
  else
    printf '\n   \033[2m[  %s  ]\033[0m\n' "$ROTULO"
  fi
  printf '\n  \033[2m↑↓ navega · espaço/Enter marca · 1-9 marca direto · a todos · n nenhum · q sai\033[0m\n'
  printf '  \033[2mEnter no botão [%s] confirma\033[0m\n' "$ROTULO"
  if [ "$MODO" = install ]; then
    printf '  \033[2mdesinstalar: bash setup.sh -u · goodpen tem setup próprio (goodpen/README.md)\033[0m\n'
  fi
  [ -n "$AVISO" ] && printf '\n  \033[33m%s\033[0m\n' "$AVISO"
}

alternar() {
  if [ "${SEL[$1]}" = 1 ]; then SEL[$1]=0; else SEL[$1]=1; fi
}

confirmar() {
  MARCADAS=()
  for k in "${!ITENS[@]}"; do
    [ "${SEL[$k]}" = 1 ] && MARCADAS+=("${NOMES[${ITENS[$k]}]}")
  done
  if [ "${#MARCADAS[@]}" -eq 0 ]; then
    AVISO="marque pelo menos uma (espaço, 1-9, ou 'a' pra todas)"
    return 1
  fi
  return 0
}

while :; do
  draw
  IFS= read -rsn1 t || t=q
  AVISO=""
  if [ "$t" = $'\x1b' ]; then
    seq=""
    IFS= read -rsn2 -t 1 seq 2>/dev/null
    case "$seq" in
      '[A') CUR=$((CUR - 1)); [ "$CUR" -lt 0 ] && CUR=$BTN ;;          # ↑
      '[B') CUR=$((CUR + 1)); [ "$CUR" -gt "$BTN" ] && CUR=0 ;;        # ↓
      '[H') CUR=0 ;;                                                    # Home
      '[F') CUR=$BTN ;;                                                 # End
    esac
    continue
  fi
  case "$t" in
    k|K) CUR=$((CUR - 1)); [ "$CUR" -lt 0 ] && CUR=$BTN ;;
    j|J) CUR=$((CUR + 1)); [ "$CUR" -gt "$BTN" ] && CUR=0 ;;
    [1-9])
      k=$((t - 1))
      if [ "$k" -lt "${#ITENS[@]}" ]; then
        alternar "$k"
        CUR=$k
      fi ;;
    a|A) for k in "${!SEL[@]}"; do SEL[$k]=1; done ;;
    n|N) for k in "${!SEL[@]}"; do SEL[$k]=0; done ;;
    " "|"")
      if [ "$CUR" = "$BTN" ]; then
        confirmar && break
      else
        alternar "$CUR"
      fi ;;
    q|Q) printf '\ncancelado.\n'; exit 0 ;;
  esac
done

printf '\033[H\033[2J'
if [ "$MODO" = install ]; then
  for t in "${MARCADAS[@]}"; do
    printf '\n\033[1m→ %s\033[0m\n' "$t"
    case "$t" in
      goodivers-skill) bash "$ROOT/goodivers/setup.sh" --skill ;;
      dark-skill)      bash "$ROOT/dark/setup.sh" --skill ;;
      *)               bash "$ROOT/$t/setup.sh" ;;
    esac
  done
  printf '\n✅ %d instalada(s). Abra um terminal novo (ou:  source ~/.zshrc).\n' "${#MARCADAS[@]}"
else
  # backup de cada rc existente, uma vez por execução
  for rc in "${RCS[@]}"; do
    [ -f "$rc" ] && cp "$rc" "$rc.tools-backup"
  done
  for t in "${MARCADAS[@]}"; do
    if [ "$t" = goodivers-skill ] || [ "$t" = dark-skill ]; then
      # remove só se for symlink apontando pra este repo
      if [ "$t" = goodivers-skill ]; then LINKS="$SKILL_GOODIVERS"; ORIGEM="$ROOT/goodivers"; NOME_SKILL=goodivers
      else LINKS="$SKILL_DARK"; ORIGEM="$ROOT/dark"; NOME_SKILL=dark; fi
      if [ -L "$LINKS" ]; then
        case "$(readlink "$LINKS")" in
          "$ORIGEM"*) rm -f "$LINKS"
                      printf '  − skill /%s removida de ~/.claude/skills\n' "$NOME_SKILL" ;;
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
