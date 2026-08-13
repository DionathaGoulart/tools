# goodpixel

Transforma qualquer imagem em **pixel art** limpa e honesta, no terminal. Aceita
`png`, `jpg`/`jpeg`, `gif`, `bmp`, `webp`, `tiff` — e vetores (`svg`, `pdf`, `eps`)
quando o ImageMagick está por perto.

Faz cada etapa do pixel art por conta própria — o resultado é o mesmo
independente do decoder:

```
decodifica → downscale por média de área (em luz linear) → quantização de
paleta (median cut, ou um preset tipo gameboy/pico8) → dithering opcional →
upscale nearest-neighbour → PNG sem perdas.
```

A parte de imagem (transform + escrita do PNG) é **Python puro, sem dependência**.
A única coisa que pode faltar é o *decoder* — e aí ele usa Pillow ou ImageMagick.

## Uso

```bash
goodpixel foto.jpg                     # 128px de grade, 16 cores, tamanho ~original
goodpixel logo.svg -w 64 -c 8          # grade menor, paleta menor
goodpixel *.png --palette gameboy      # lote, paleta clássica de 4 verdes
goodpixel arte.png -w 48 -d            # cores chapadas → com dithering
goodpixel icon.svg -w 32 --true        # salva no tamanho real da grade (1x1)
```

Saída: `<nome>.pixel.png` na mesma pasta (ou `-o arquivo.png` com uma imagem só).
Sempre PNG, sempre com blocos nítidos (nearest-neighbour).

## Opções

| Flag | O que faz | Padrão |
|---|---|---|
| `-w, --width N` | largura da grade em pixels | `128` |
| `--height N` | altura da grade | proporção |
| `-c, --colors N` | tamanho da paleta (`0` = não quantiza) | `16` |
| `--palette P` | paleta clássica: `mono` `gameboy` `cga` `pico8` | — |
| `-d, --dither` | dithering Floyd-Steinberg | chapado |
| `-s, --scale N` | tamanho do bloco de cada pixel | `~original` |
| `--true` | salva no tamanho real da grade (bloco 1×1) | — |
| `-o, --out FILE` | arquivo de saída (só com 1 imagem) | `<nome>.pixel.png` |
| `--no-preview` | não desenha a prévia no terminal | — |
| `--temas` | catálogo de temas retrô | — |

**Grade × escala.** `--width` controla quantos pixels a arte tem (menor = mais
chunky). `--scale` controla o tamanho de cada pixel no arquivo. Por padrão a escala
é escolhida pra saída ficar perto do tamanho original — a imagem parece a mesma, só
pixelada. Use `--true` pro sprite cru no tamanho da grade.

## Decoder

- **Pillow** (`pip install Pillow`), se disponível — cobre todos os formatos raster.
- **ImageMagick** (`brew install imagemagick`) como fallback, e obrigatório pra
  vetores (`svg`/`pdf`/`eps`), que ele rasteriza em alta densidade antes de reduzir.

Se nenhum dos dois existir, o comando avisa qual instalar.

## Instalação

```bash
# do diretório do repo (git clone … && cd tools)
bash images/goodpixel/setup.sh
```

Depois abra um terminal novo (ou `source ~/.zshrc`). O `setup.sh` detecta o próprio
caminho — clonar o repo em outro lugar funciona igual. Desinstalar: `bash
bash setup.sh -u`.

## Tema

Segue o [styleguide de terminal](../../.harness/styleguide-terminal.md) do repo
(paleta accent-only, cantos retos, borda pesada). Escolha o tema com
`GOODPIXEL_TEMA` ou `RETRO_TEMA`; veja `goodpixel --temas`. No terminal com truecolor
ele ainda desenha uma **prévia** da arte em half-blocks e a paleta em swatches.
