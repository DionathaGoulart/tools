# goodprofile

Encaixa qualquer imagem nos tamanhos prontos de perfil e rede social: avatar,
capa, banner, thumbnail, favicon. Corta com gravidade ou ponto focal, centraliza
logo com respiro, troca cor, aplica tint duotone e máscara redonda — tudo em
Python puro sobre o buffer RGBA, então o resultado é idêntico seja qual for o
decoder que leu o arquivo.

## Uso

```bash
goodprofile foto.jpg ig-avatar              # avatar do Instagram (320x320)
goodprofile foto.jpg ig-avatar --circulo    # já com máscara redonda
goodprofile logo.png kit-perfil             # TODOS os avatares de uma vez (pasta)
goodprofile logo.svg kit-favicon            # 16/32/48 + apple-touch + PWA
goodprofile arte.png x-header --foco 30,40  # o rosto em 30%,40% sobrevive ao corte
goodprofile logo.png yt-banner --centralizar --fundo 111111
goodprofile print.png --cor-de ffffff --cor-para transparente
goodprofile presets                         # catálogo completo
```

Vários arquivos de uma vez funcionam (`goodprofile *.png ig-post`). A saída
padrão é `nome-<preset>.png` ao lado do original; kits criam a pasta
`nome-<kit>/`.

## Opções

| Opção | O que faz |
|---|---|
| `--modo cobrir\|conter\|esticar` | cobrir corta (padrão) · conter põe padding · esticar deforma |
| `--gravidade centro\|norte\|sul\|leste\|oeste\|…` | âncora do corte no modo cobrir |
| `--foco X,Y` | ponto focal em % que deve sobreviver ao corte |
| `--fundo COR` | cor do padding (`RRGGBB`, `branco`, `transparente`) |
| `--centralizar` | apara a borda uniforme e centra o conteúdo (logos) |
| `--margem N` | respiro do conteúdo em % (padrão 8 com `--centralizar`) |
| `--cor-de C --cor-para C` | troca uma cor (borda suavizada; `--tolerancia 0-100`) |
| `--tint COR` | recolore a imagem toda pelo tom (duotone preto→cor→branco) |
| `--pb` | preto e branco |
| `--circulo` | máscara circular com borda anti-aliased |
| `--raio N` | cantos arredondados em px |
| `-o, --out ARQ` | arquivo de saída (pasta, no caso de kits) |
| `--formato png\|jpg\|webp` | formato de saída (padrão png; jpg achata sobre `--fundo`) |
| `--qualidade N` | qualidade jpg/webp (padrão 90) |
| `--temas` | catálogo de temas retrô |

## Presets

`goodprofile presets` lista tudo. Resumo (tamanhos revisados em 2026-07):

- **instagram** — `ig-avatar` 320² · `ig-post` 1080² · `ig-retrato` 1080x1350 · `ig-story` 1080x1920
- **youtube** — `yt-avatar` 800² · `yt-banner` 2560x1440 (área segura 1546x423) · `yt-thumb` 1280x720
- **x-twitter** — `x-avatar` 400² · `x-header` 1500x500 · `x-post` 1600x900
- **linkedin** — `li-avatar` 400² · `li-capa` 1584x396 · `li-capa-empresa` 1128x191
- **github** — `gh-avatar` 460² · `gh-social` 1280x640
- **discord / twitch / facebook / whatsapp / tiktok** — avatares e banners
- **web** — `og` 1200x630 · `favicon-16/32/48` · `apple-touch` 180² · `pwa-192/512`
- **custom** — qualquer `LARGURAxALTURA`, ex. `800x600`

Kits: `kit-perfil` (10 avatares), `kit-favicon`, `kit-ig`, `kit-canal`.

## Decoder

Pillow se houver, senão o CLI do ImageMagick (`magick`/`convert`) — SVG/PDF
sempre via magick. Só a *decodificação* depende de backend; toda edição é
Python puro. Com Pillow instalado o redimensionamento usa Lanczos e fica bem
mais rápido em imagens grandes (`pip install Pillow`, opcional). Saída `jpg`
e `webp` precisam de Pillow ou magick; `png` é escrito em Python puro, sempre
funciona.

## Instalação

```bash
# do diretório do repo (git clone … && cd tools)
bash images/goodprofile/setup.sh
```

## Tema

`GOODPROFILE_TEMA` ou `RETRO_TEMA` (`goodprofile --temas` lista as paletas;
`NO_COLOR=1` desliga as cores).
