#!/usr/bin/env bash
# setup.sh — instalador interativo das ferramentas (macOS / Linux / Git Bash)
#
#   bash setup.sh        ← lista tudo, você marca o que quer e confirma no botão
#   bash setup.sh -u     ← desinstalar (lista só o que está instalado)
#
# Teclas: ↑↓ move · ←→ troca de página · espaço/Enter marca · 1-9 marca visível · a todos · n nenhum
#         Enter (ou espaço) no botão [INSTALAR] confirma · q sai
# Tema:   TOOLS_TEMA / RETRO_TEMA (ver .harness/styleguide-terminal.md)
# "Instalada" = a linha `source .../setup.sh` existe em algum rc do shell
# (exceção: goodivers-skill = symlink em ~/.claude/skills/goodivers).
# Desinstalar remove do rc as linhas da ferramenta (backup: <rc>.tools-backup).

ROOT="$(cd "$(dirname "$0")" && pwd)"

NOMES=(goodcheats goodpomo goodprof goodbio goodvocab goodzap goodivers goodivers-skill goodjob goodjob-skill dark dark-skill images/goodpixel goodnerd)
DESCS=(
  "kit good: fetch de sistema + cheatsheets + styleguides"
  "pomodoro no terminal com notificação e stats"
  "estudo Feynman invertido, te sabatina até dominar (IA)"
  "sua autobiografia, uma pergunta por dia (IA)"
  "uma palavra de inglês por dia, revisão espaçada (IA)"
  "retrô de conversa exportada do WhatsApp (IA)"
  "copiloto do canal de Helldivers 2 no terminal (OpenRouter)"
  "skill /goodivers no Claude Code: gera com o Claude, sem chave"
  "radar de vagas + aderência, carta, CV e prep (OpenRouter)"
  "skill /goodjob no Claude Code: gera com o Claude, sem chave"
  "copiloto do Instagram @darkning.art, horror art (OpenRouter)"
  "skill /dark no Claude Code: gera com o Claude, sem chave"
  "imagem (png/jpg/svg/…) -> pixel art, paletas clássicas"
  "teatro de hacker fake no terminal, pra impressionar leigos"
)

RCS=("$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.bash_profile")
SKILL_GOODIVERS="$HOME/.claude/skills/goodivers"
SKILL_GOODJOB="$HOME/.claude/skills/goodjob"
SKILL_DARK="$HOME/.claude/skills/dark"

instalada() {
  # skills: symlink no macOS/Linux; no Windows (Git Bash) pode ser cópia da pasta
  case "$1" in
    goodivers-skill) [ -L "$SKILL_GOODIVERS" ] || [ -d "$SKILL_GOODIVERS" ] ;;
    goodjob-skill) [ -L "$SKILL_GOODJOB" ] || [ -d "$SKILL_GOODJOB" ] ;;
    dark-skill) [ -L "$SKILL_DARK" ] || [ -d "$SKILL_DARK" ] ;;
    *) grep -qsF "$1/setup.sh" "${RCS[@]}" 2>/dev/null ;;
  esac
}

MODO=install
case "${1:-}" in
  -u|--uninstall|uninstall|desinstalar) MODO=uninstall ;;
  -h|--help) sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
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
PAGE=0                # página atual (0-based)
PAGE_SIZE=5           # itens por página (reduz se o terminal for baixo)
NPAGES=1              # total de páginas (recalculado em paginate)

ROTULO="INSTALAR"
[ "$MODO" = uninstall ] && ROTULO="DESINSTALAR"

# tema retrô compartilhado (.harness/styleguide-terminal.md)
TEMA="${TOOLS_TEMA:-${RETRO_TEMA:-vault-gold}}"
. "$ROOT/lib/retro.sh"
retro_init 92

# corta uma string em N colunas visíveis
cortar() { # $1 texto  $2 limite
  local s=$1 lim=$2
  [ "${#s}" -le "$lim" ] && { printf '%s' "$s"; return; }
  printf '%s…' "${s:0:$((lim - 1))}"
}

LARG_NOME=16

draw() {
  local titulo="root@tools: ~/install"
  [ "$MODO" = uninstall ] && titulo="root@tools: ~/uninstall"

  local total=${#ITENS[@]}
  local pstart=$((PAGE * PAGE_SIZE))
  local pend=$((pstart + PAGE_SIZE)); [ "$pend" -gt "$total" ] && pend=$total

  local meta="$total ITENS"
  [ "$NPAGES" -gt 1 ] && meta="PÁG $((PAGE + 1))/$NPAGES · $total ITENS"

  retro_topo
  retro_chrome "$titulo" "$meta"
  retro_sep

  local n i caixa nome desc tag marca conteudo larg k shown=0
  for (( k = pstart; k < pend; k++ )); do
    n=$((k + 1))
    i="${ITENS[$k]}"
    nome="${NOMES[$i]}"
    inst=0
    [ "$MODO" = install ] && instalada "$nome" && inst=1
    desc="$(cortar "${DESCS[$i]}" $((CF - LARG_NOME - 10)))"
    marca="  "
    [ "$CUR" = "$k" ] && marca="► "
    # checkbox: [x] selecionada (accent) · [✓] já instalada (verde) · [ ] livre
    caixa="[ ]"
    if [ "${SEL[$k]}" = 1 ]; then caixa="[x]"
    elif [ "$inst" = 1 ]; then caixa="[✓]"; fi

    larg=$(( 2 + 3 + 1 + 4 + LARG_NOME + 1 + ${#desc} ))
    [ "$larg" -gt "$CF" ] && larg=$CF
    if [ "$CUR" = "$k" ]; then
      # linha ativa: inversão em accent ocupando toda a largura do campo
      conteudo="$(printf '%s%s%s%s %2d. %-*s %s%s' \
        "$INV" "$BOLD" "$marca" "$caixa" "$n" "$LARG_NOME" "$nome" \
        "$desc$(retro_espacos $((CF - larg)))" "$RESET")"
      larg=$CF
    else
      local cor_caixa="$ACC30"
      if [ "${SEL[$k]}" = 1 ]; then cor_caixa="$ACC"
      elif [ "$inst" = 1 ]; then cor_caixa="$OK"; fi
      conteudo="$(printf '%s%s%s%s%s%s %2d. %s%-*s%s %s%s%s' \
        "$ACC" "$marca" "$RESET" "$cor_caixa" "$caixa" "$RESET" "$n" \
        "$ACC" "$LARG_NOME" "$nome" "$RESET" "$FG40" "$desc" "$RESET")"
    fi
    retro_linha "$conteudo" "$larg"
    shown=$((shown + 1))
  done
  # completa a página com linhas vazias -> altura estável entre páginas
  while [ "$shown" -lt "$PAGE_SIZE" ]; do retro_vazia; shown=$((shown + 1)); done

  retro_vazia
  if [ "$CUR" = "$BTN" ]; then
    retro_linha "$(printf '%s►%s %s%s  %s  %s' \
      "$ACC" "$RESET" "$INV" "$BOLD" "$ROTULO" "$RESET")" \
      $((2 + ${#ROTULO} + 4))
  else
    retro_linha "$(printf '  %s[  %s  ]%s' "$ACC30" "$ROTULO" "$RESET")" \
      $((2 + ${#ROTULO} + 6))
  fi
  retro_sep
  retro_status "[↑↓] MOVE · [←→] PÁGINA · [SPC] MARCA · [A/N] TUDO/NADA" "[Q] SAI · ENTER = $ROTULO"
  retro_base
  retro_sombra

  if [ "$MODO" = install ]; then
    printf '  %s[%s✓%s]%s %sjá instalada · desinstalar: bash setup.sh -u · goodpen tem setup próprio%s%s\n' \
      "$FG40" "$OK" "$FG40" "$RESET" "$FG40" "$RESET" "$CLR"
  fi
  [ -n "$AVISO" ] && printf '\n  %s[ AVISO ]%s %s%s' "$ALERTA" "$RESET" "$AVISO" "$CLR"
}

# recalcula a paginação (itens por página + página atual).
# roda no shell-pai, NÃO dentro de $(draw), pra que PAGE/PAGE_SIZE persistam.
paginate() {
  local rows total fits
  rows=$( { tput lines; } 2>/dev/null || echo 24 )
  case "$rows" in ''|*[!0-9]*) rows=24 ;; esac
  total=${#ITENS[@]}
  # linhas fixas: topo+chrome+sep(3) + vazia+botao+sep+status+base+sombra(6) [+dica]
  local overhead=9; [ "$MODO" = install ] && overhead=$((overhead + 1))
  fits=$((rows - overhead - 2))          # -2 reserva pro AVISO
  # page size acompanha a altura do terminal: enche o espaço disponível,
  # nunca passa do total de itens (terminal alto = tudo numa página só)
  PAGE_SIZE=$fits
  [ "$PAGE_SIZE" -gt "$total" ] && PAGE_SIZE=$total
  [ "$PAGE_SIZE" -lt 1 ] && PAGE_SIZE=1
  NPAGES=$(( (total + PAGE_SIZE - 1) / PAGE_SIZE ))
  [ "$NPAGES" -lt 1 ] && NPAGES=1
  # quando o cursor está num item, a página segue o cursor
  [ "$CUR" -lt "$total" ] && PAGE=$(( CUR / PAGE_SIZE ))
  [ "$PAGE" -ge "$NPAGES" ] && PAGE=$((NPAGES - 1))
  [ "$PAGE" -lt 0 ] && PAGE=0
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

# esconde o cursor e limpa a tela uma vez; o loop redesenha por cima (sem piscar)
if [ "$DESENHA" -eq 1 ]; then
  printf '\033[?25l\033[2J'
  trap 'printf "\033[?25h"' EXIT INT TERM
fi

while :; do
  paginate
  if [ "$DESENHA" -eq 1 ]; then
    # bufferiza o frame; $(...) corta o \n final -> nada é escrito na última
    # linha do terminal, então a tela nunca rola ao redesenhar. \033[J limpa
    # o que sobrou de um frame anterior mais alto.
    printf '\033[H%s\033[J' "$(draw)"
  else
    draw
  fi
  IFS= read -rsn1 t || t=q
  AVISO=""
  # limites da página atual (ps..pe-1 = itens; BTN = botão logo abaixo)
  ps=$((PAGE * PAGE_SIZE)); pe=$((ps + PAGE_SIZE)); [ "$pe" -gt "$BTN" ] && pe=$BTN
  if [ "$t" = $'\x1b' ]; then
    seq=""
    IFS= read -rsn2 -t 1 seq 2>/dev/null
    case "$seq" in
      '[A')  # ↑ move dentro da página; sobe do topo pro botão
        if [ "$CUR" = "$BTN" ]; then CUR=$((pe - 1))
        elif [ "$CUR" -le "$ps" ]; then CUR=$BTN
        else CUR=$((CUR - 1)); fi ;;
      '[B')  # ↓ move dentro da página; desce do fim pro botão
        if [ "$CUR" = "$BTN" ]; then CUR=$ps
        elif [ "$CUR" -ge $((pe - 1)) ]; then CUR=$BTN
        else CUR=$((CUR + 1)); fi ;;
      '[C')  # → próxima página
        [ "$NPAGES" -gt 1 ] && { PAGE=$(((PAGE + 1) % NPAGES)); CUR=$((PAGE * PAGE_SIZE)); } ;;
      '[D')  # ← página anterior
        [ "$NPAGES" -gt 1 ] && { PAGE=$(((PAGE - 1 + NPAGES) % NPAGES)); CUR=$((PAGE * PAGE_SIZE)); } ;;
      '[H') CUR=0 ;;                                                    # Home
      '[F') CUR=$BTN ;;                                                 # End
    esac
    continue
  fi
  case "$t" in
    k|K)
      if [ "$CUR" = "$BTN" ]; then CUR=$((pe - 1))
      elif [ "$CUR" -le "$ps" ]; then CUR=$BTN
      else CUR=$((CUR - 1)); fi ;;
    j|J)
      if [ "$CUR" = "$BTN" ]; then CUR=$ps
      elif [ "$CUR" -ge $((pe - 1)) ]; then CUR=$BTN
      else CUR=$((CUR + 1)); fi ;;
    h)  [ "$NPAGES" -gt 1 ] && { PAGE=$(((PAGE - 1 + NPAGES) % NPAGES)); CUR=$((PAGE * PAGE_SIZE)); } ;;
    l)  [ "$NPAGES" -gt 1 ] && { PAGE=$(((PAGE + 1) % NPAGES)); CUR=$((PAGE * PAGE_SIZE)); } ;;
    [1-9])
      k=$((t - 1))                      # número = número absoluto do item mostrado
      if [ "$k" -ge "$ps" ] && [ "$k" -lt "$pe" ]; then
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
    q|Q) printf '\n'; retro_aviso "cancelado" "nada foi alterado."; exit 0 ;;
  esac
done

[ "$DESENHA" -eq 1 ] && printf '\033[?25h'   # cursor de volta antes da saída
printf '\033[H\033[2J'
if [ "$MODO" = install ]; then
  retro_modulo "install_runner" "${#MARCADAS[@]} item(s)"
  for t in "${MARCADAS[@]}"; do
    printf '  %s>%s %s%s%s\n' "$ACC30" "$RESET" "$ACC$BOLD" "$(retro_upper "$t")" "$RESET"
    case "$t" in
      goodivers-skill) bash "$ROOT/goodivers/setup.sh" --skill ;;
      goodjob-skill)   bash "$ROOT/goodjob/setup.sh" --skill ;;
      dark-skill)      bash "$ROOT/dark/setup.sh" --skill ;;
      *)               bash "$ROOT/$t/setup.sh" ;;
    esac
  done
  echo
  retro_ok "${#MARCADAS[@]} instalada(s)"
  retro_proximo "source ~/.zshrc" "abra um terminal novo, ou rode:"
  echo
else
  retro_modulo "uninstall_runner" "${#MARCADAS[@]} item(s)"
  # backup de cada rc existente, uma vez por execução
  for rc in "${RCS[@]}"; do
    [ -f "$rc" ] && cp "$rc" "$rc.tools-backup"
  done
  for t in "${MARCADAS[@]}"; do
    if [ "$t" = goodivers-skill ] || [ "$t" = goodjob-skill ] || [ "$t" = dark-skill ]; then
      # remove só se for symlink apontando pra este repo
      if [ "$t" = goodivers-skill ]; then LINKS="$SKILL_GOODIVERS"; ORIGEM="$ROOT/goodivers"; NOME_SKILL=goodivers
      elif [ "$t" = goodjob-skill ]; then LINKS="$SKILL_GOODJOB"; ORIGEM="$ROOT/goodjob"; NOME_SKILL=goodjob
      else LINKS="$SKILL_DARK"; ORIGEM="$ROOT/dark"; NOME_SKILL=dark; fi
      if [ -L "$LINKS" ]; then
        case "$(readlink "$LINKS")" in
          "$ORIGEM"*) rm -f "$LINKS"
                      printf '  %s−%s skill /%s removida de ~/.claude/skills\n' "$ALERTA" "$RESET" "$NOME_SKILL" ;;
        esac
      elif [ -d "$LINKS" ] && [ -f "$LINKS/SKILL.md" ]; then
        # Windows (Git Bash): a skill foi instalada como cópia, não symlink
        rm -rf "$LINKS"
        printf '  %s−%s skill /%s removida de ~/.claude/skills\n' "$ALERTA" "$RESET" "$NOME_SKILL"
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
      printf '  %s−%s %s%s%s removida de %s%s%s\n' "$ALERTA" "$RESET" "$ACC" "$t" "$RESET" "$FG40" "${rc/#$HOME/~}" "$RESET"
    done
  done
  echo
  retro_ok "pronto"
  printf '  %svale pros próximos terminais · backup em <rc>.tools-backup%s\n\n' "$FG40" "$RESET"
fi
