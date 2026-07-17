# good

Fetch de sistema estilo neofetch, com o logo good em ASCII art. Digite `good` e veja o logo colorido ao lado das infos da máquina (OS, kernel, uptime, CPU, GPU, memória, disco, pacotes, bateria).

```
      ▄████████      ████████▄         rafael@MacBookAir
      █████████      █████████         -----------------
      █████████      █████████         OS:      macOS 26.2 arm64
▄▄▄▄▄▄████████████████████████▄▄▄▄▄▄   Host:    MacBook Air (MacBookAir10,1)
████████▀  ▀████████████▀  ▀████████   Kernel:  Darwin 25.2.0
████████    ████████████    ████████   Uptime:  7h 49m
████████    ████████████    ████████   Shell:   zsh 5.9
▀██████████████████████████████████▀   Display: 2560 x 1600 Retina
      ████████████████████████         Term:    WarpTerminal
      █████████▀▀▀▀▀▀█████████         CPU:     Apple M1
  ▄▄▄▄█████████▄▄▄▄▄▄█████████▄▄▄▄     GPU:     Apple M1
█████████▀▀▀▀██████████▀▀▀▀█████████   Memory:  5.3 GiB / 8.0 GiB (66%)
████████      ████████      ████████   Disk:    190G / 245G (93%)
████████      ████████      ████████   Pkgs:    174 (brew), 1 (cask)
████████      ▀███████      ████████   Battery: 67% (discharging)
```

## Uso

```bash
good            # logo + infos
good --refresh  # refaz o cache de hardware (modelo, GPU, resolução)
good -h         # ajuda
```

## Instalação (uma vez)

```bash
bash ~/Desktop/tools/good/setup.sh
```

Isso adiciona a linha de `source` no seu `~/.zshrc` (ou `~/.bashrc`). Depois abra um terminal novo ou rode `source ~/.zshrc`.

> Rodar `bash setup.sh` sozinho não muda o PATH do terminal atual — subshell não altera o shell pai. Por isso ele instala a linha no rc e avisa. O caminho é detectado automaticamente, funciona com o repo clonado em qualquer lugar.

## Como funciona

- Script bash puro, sem dependências. Funciona em macOS e Linux.
- No macOS, as infos lentas (`system_profiler`: modelo, GPU, resolução) são coletadas **uma vez** e cacheadas em `~/.cache/good/hardware` — as execuções seguintes levam ~0.1s. Trocou de monitor? Roda `good --refresh`.
- Em terminais com truecolor (`COLORTERM=truecolor`), o logo sai com gradiente violeta → ciano. Sem truecolor, cai pra uma cor sólida do palette 256. Respeita `NO_COLOR`.

## Personalização

```bash
GOOD_COLOR=ff5500 good   # logo em cor sólida (6 dígitos hex, com ou sem #)
```

O logo em ASCII foi gerado a partir de `logo.svg` (rasterizado e amostrado em half-blocks `▀▄█`). O SVG original fica em [`logo.svg`](./logo.svg).

---

↩ [Voltar pro índice de ferramentas](../README.md)
