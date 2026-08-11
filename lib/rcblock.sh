#!/usr/bin/env bash
# rcblock.sh — shared install/uninstall helpers for the shell rc.
#
# Sourced by setup.sh at the repo root and by every <tool>/setup.sh. Never
# sourced by an interactive shell.
#
# O problema que isto resolve: cada <tool>/setup.sh já se auto-localiza, então o
# repo é relocável — o único lugar preso a caminho absoluto era o rc do shell,
# uma linha por ferramenta. Mover o repo quebrava todas de uma vez, em silêncio,
# porque o guard `[ -f … ] && source …` engolia o erro.
#
# O formato novo é UM bloco só, ancorado num symlink estável:
#
#   # >>> good tools >>>
#   export GOODTOOLS_ROOT="$HOME/.goodtools"
#   if [ -r "$GOODTOOLS_ROOT/load.sh" ]; then
#     . "$GOODTOOLS_ROOT/load.sh"
#     goodtools_load goodcheats goodivers images/goodpixel
#   else
#     echo "…" >&2
#   fi
#   # <<< good tools <<<
#
# Mover o repo = `ln -sfn /caminho/novo/tools ~/.goodtools`, e nada no rc muda.
#
# Env de teste: GOODTOOLS_RC (rc alvo) e GOODTOOLS_LINK (symlink âncora).

GT_BEGIN="# >>> good tools >>>"
GT_END="# <<< good tools <<<"

# Âncora: caminho real usado por nós e literal escrito no rc. `$HOME` fica
# literal no rc pra que o bloco seja o mesmo em qualquer máquina/usuário.
if [ -n "${GOODTOOLS_LINK:-}" ]; then
  GT_LINK="$GOODTOOLS_LINK"
  GT_LINK_RC="$GOODTOOLS_LINK"
else
  GT_LINK="$HOME/.goodtools"
  GT_LINK_RC='$HOME/.goodtools'
fi
GT_ROOT_RC="$GT_LINK_RC"

# ---------- rc alvo ----------
gt_rc() {
  if [ -n "${GOODTOOLS_RC:-}" ]; then
    printf '%s\n' "$GOODTOOLS_RC"
    return 0
  fi
  case "$(basename "${SHELL:-bash}")" in
    zsh) printf '%s\n' "$HOME/.zshrc" ;;
    *)   if [ -f "$HOME/.bashrc" ]; then
           printf '%s\n' "$HOME/.bashrc"
         else
           printf '%s\n' "$HOME/.bash_profile"
         fi ;;
  esac
}

gt_backup() { # <rc> — uma vez por execução do instalador da raiz
  [ "${GT_NO_BACKUP:-0}" = 1 ] && return 0
  [ -f "$1" ] && cp "$1" "$1.tools-backup"
  return 0
}

# ---------- âncora ----------
# Aponta ~/.goodtools pro repo e define GT_ROOT_RC.
# 0 = symlink ok · 1 = fallback pro caminho absoluto (Windows sem Developer Mode,
# ou algo que não é symlink ocupando o lugar).
gt_anchor() { # <root>
  local root=$1 cur=""
  [ -L "$GT_LINK" ] && cur="$(readlink "$GT_LINK")"
  if [ "$cur" = "$root" ]; then
    GT_ROOT_RC="$GT_LINK_RC"
    return 0
  fi
  if [ -e "$GT_LINK" ] && [ ! -L "$GT_LINK" ]; then
    GT_ROOT_RC="$root"          # não é nosso, não mexe
    return 1
  fi
  if MSYS=winsymlinks:nativestrict ln -sfn "$root" "$GT_LINK" 2>/dev/null; then
    GT_ROOT_RC="$GT_LINK_RC"
    return 0
  fi
  GT_ROOT_RC="$root"
  return 1
}

gt_anchor_aviso() { # <root> — explica o fallback sem fingir que deu certo
  printf '%s\n' \
    "good tools: não deu pra criar o symlink $GT_LINK." \
    "            o rc vai apontar direto pra $1 — funciona, mas se você mover" \
    "            o repo vai precisar rodar o instalador de novo." >&2
}

# ---------- leitura do bloco ----------
gt_list() { # <rc> → "a b c" (vazio se não houver bloco)
  local rc=$1
  [ -f "$rc" ] || return 0
  awk -v b="$GT_BEGIN" -v e="$GT_END" '
    $0 == b { dentro = 1; next }
    $0 == e { dentro = 0; next }
    dentro && $1 == "goodtools_load" {
      $1 = ""; sub(/^[ \t]+/, ""); print; exit
    }
  ' "$rc"
}

gt_has() { # <rc> <tool>
  local t
  for t in $(gt_list "$1"); do
    [ "$t" = "$2" ] && return 0
  done
  return 1
}

# Nomes do formato antigo (uma linha absoluta por ferramenta), resolvidos contra
# o repo: o que não existe mais (good, cheats, pomo, zapstats…) é descartado, e
# goodpixel/goodprofile voltam com o prefixo images/.
gt_legacy() { # <rc> <root> → nomes, um por linha
  local rc=$1 root=$2 n
  [ -f "$rc" ] || return 0
  sed -n 's|^\[ -f "[^"]*/\([A-Za-z0-9_.-]*\)/setup\.sh" \].*|\1|p' "$rc" |
    while IFS= read -r n; do
      [ -n "$n" ] || continue
      if [ -d "$root/$n" ]; then
        printf '%s\n' "$n"
      elif [ -d "$root/images/$n" ]; then
        printf '%s\n' "images/$n"
      fi
    done
}

gt_merge() { # <nomes...> → "a b c" sem repetição, ordem de chegada
  printf '%s\n' "$@" | tr ' ' '\n' | awk 'NF && !visto[$0]++' | tr '\n' ' ' |
    sed 's/[[:space:]]*$//'
}

# ---------- escrita do bloco ----------
gt_bloco() { # <root_literal> <lista>
  cat <<EOF
$GT_BEGIN
# Gerado por tools/setup.sh — pode editar a lista do goodtools_load na mão.
# Moveu o repo? Só repontar o symlink, nada aqui muda:
#   ln -sfn /caminho/novo/tools ~/.goodtools
# Lembrete diário (opcional): descomente o que quiser
#   export GOODIVERS_LEMBRETE=1 GOODJOB_LEMBRETE=1 GOODBIO_LEMBRETE=1
#   export GOODVOCAB_LEMBRETE=1 DARK_LEMBRETE=1
export GOODTOOLS_ROOT="$1"
if [ -r "\$GOODTOOLS_ROOT/load.sh" ]; then
  . "\$GOODTOOLS_ROOT/load.sh"
  goodtools_load $2
else
  echo "good tools: \$GOODTOOLS_ROOT não resolve — repo moveu ou sumiu?" >&2
  echo "            conserto: ln -sfn /caminho/para/tools ~/.goodtools" >&2
fi
$GT_END
EOF
}

# Reescreve o rc: tira o bloco antigo, tira as linhas do formato legado, e
# devolve o bloco novo no fim. Lista vazia = rc fica sem bloco nenhum.
gt_apply() { # <rc> <root_literal> <lista>
  local rc=$1 root=$2 lista=$3 tmp
  tmp="$rc.gt$$"

  if [ -f "$rc" ]; then
    awk -v b="$GT_BEGIN" -v e="$GT_END" '
      $0 == b { dentro = 1; next }
      $0 == e { dentro = 0; next }
      dentro { next }
      # formato legado: uma linha absoluta por ferramenta, mais os comentários
      # que o instalador antigo escrevia junto
      /^\[ -f "[^"]*\/setup\.sh" \][[:space:]]*&&[[:space:]]*source / { next }
      /^# tools\// { next }
      /^# export [A-Z_]*_LEMBRETE=/ { next }
      { print }
    ' "$rc" > "$tmp" || { rm -f "$tmp"; return 1; }
  else
    : > "$tmp"
  fi

  # tira as linhas em branco do fim pra não acumular espaço a cada reinstalação
  awk '{ linhas[NR] = $0 }
       END {
         ultima = NR
         while (ultima > 0 && linhas[ultima] ~ /^[[:space:]]*$/) ultima--
         for (i = 1; i <= ultima; i++) print linhas[i]
       }' "$tmp" > "$tmp.trim" && mv "$tmp.trim" "$tmp"

  if [ -n "$lista" ]; then
    [ -s "$tmp" ] && printf '\n' >> "$tmp"
    gt_bloco "$root" "$lista" >> "$tmp"
  fi

  mv "$tmp" "$rc"
}

# ---------- API usada pelos setup.sh ----------
gt_add() { # <root> <tool>
  local root=$1 tool=$2 rc lista
  rc="$(gt_rc)"
  gt_anchor "$root" || gt_anchor_aviso "$root"
  # o legado entra junto: quem já tinha a família instalada no formato antigo
  # migra sozinho na primeira reinstalação, sem perder nada do que tinha
  lista="$(gt_merge "$(gt_list "$rc")" "$(gt_legacy "$rc" "$root")" "$tool")"
  gt_backup "$rc"
  gt_apply "$rc" "$GT_ROOT_RC" "$lista"
}

gt_remove() { # <root> <tool>
  local root=$1 tool=$2 rc lista
  rc="$(gt_rc)"
  [ -f "$rc" ] || return 0
  # o legado entra na conta antes de tirar o alvo: gt_apply apaga TODAS as linhas
  # do formato antigo, então quem ficou precisa reaparecer dentro do bloco
  lista="$(gt_merge "$(gt_list "$rc")" "$(gt_legacy "$rc" "$root")")"
  lista="$(printf '%s\n' "$lista" | tr ' ' '\n' | awk -v t="$tool" 'NF && $0 != t' |
    tr '\n' ' ' | sed 's/[[:space:]]*$//')"
  gt_apply "$rc" "$GT_ROOT_RC" "$lista"
  # sem ferramenta nenhuma sobrando, a âncora também vai embora
  if [ -z "$lista" ] && [ -L "$GT_LINK" ] && [ "$(readlink "$GT_LINK")" = "$root" ]; then
    rm -f "$GT_LINK"
  fi
}
