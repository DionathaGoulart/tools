# goodhelp

Mapa da família `good*` no terminal: lista as ferramentas do repo que estão
instaladas no `PATH` e abre a ajuda de qualquer uma.

```bash
goodhelp                # lista o que você tem instalado
goodhelp goodivers      # abre a ajuda do goodivers (= goodivers help)
goodhelp temas          # paletas do terminal
```

Cada ferramenta da família também responde a `<ferramenta> help` direto
(ex: `goodpomo help`, `goodjob help`).

## Instalação

Nenhuma — o `goodhelp` vem junto por padrão. O `setup.sh` de cada ferramenta
coloca este diretório no `PATH` automaticamente: instalou qualquer uma
(`goodpomo`, `goodivers`, …), ganhou o `goodhelp` de brinde.

## Tema

`GOODHELP_TEMA` / `RETRO_TEMA` escolhem a paleta (veja `goodhelp temas`).
`NO_COLOR` desliga as cores.
