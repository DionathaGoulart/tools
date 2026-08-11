#!/usr/bin/env bash
# load.sh — every-shell loader for the good* family.
#
# Sourced by the managed block that setup.sh writes into your shell rc. It only
# defines goodtools_load; it does not touch PATH by itself.
#
#   goodtools_load <tool>...   sources each tool's own setup.sh (which is what
#                              puts it on PATH). Names are relative to
#                              $GOODTOOLS_ROOT — e.g. goodivers, images/goodpixel.
#
# Nada aqui guarda caminho absoluto: $GOODTOOLS_ROOT é a âncora única e aponta
# pro symlink ~/.goodtools. Mover o repo = um `ln -sfn`, sem editar rc nenhum.
#
# Ferramenta que não resolve mais vira AVISO na abertura do shell, nunca um
# no-op silencioso — foi exatamente o silêncio do antigo `[ -f … ] && source …`
# que deixou a família inteira quebrada sem ninguém perceber.

goodtools_load() {
  # zsh não faz word splitting como o bash, então a lista vem por argumento
  # (nunca por variável) e este laço funciona igual nos dois shells.
  local root="${GOODTOOLS_ROOT:-}" tool setup

  if [ -z "$root" ] || [ ! -d "$root" ]; then
    printf 'good tools: GOODTOOLS_ROOT (%s) não resolve — repo moveu ou sumiu?\n' \
      "${root:-unset}" >&2
    printf '            conserto: ln -sfn /caminho/para/tools ~/.goodtools\n' >&2
    return 1
  fi

  # goodhelp vem junto por padrão: mapa da família (goodhelp / <ferramenta> help)
  if [ -x "$root/goodhelp/goodhelp" ]; then
    case ":$PATH:" in
      *":$root/goodhelp:"*) ;;
      *) PATH="$root/goodhelp:$PATH"; export PATH ;;
    esac
  fi

  for tool in "$@"; do
    setup="$root/$tool/setup.sh"
    if [ -r "$setup" ]; then
      # o setup.sh de cada ferramenta se auto-localiza, mas dentro de uma função
      # o zsh troca $0 pelo nome da função — então entregamos o diretório pronto
      GOODTOOLS_TOOL_DIR="$root/$tool"
      # shellcheck source=/dev/null
      . "$setup"
      unset GOODTOOLS_TOOL_DIR
    else
      printf "good tools: '%s' não existe em %s — renomeada ou removida?\n" \
        "$tool" "$root" >&2
      printf '            veja o que está saudável com:  goodhelp doctor\n' >&2
    fi
  done
}
