# {{PROJETO}}: Style Guide (base)

Base visual da família Good*: **neobrutalismo de terminal retrô**. Vale para o produto inteiro,
sob qualquer skin e em qualquer stack. O que cada tela *parece* sob cada skin está no style guide
da skin:

| Skin | `data-skin` | Style guide | Quando entra |
|---|---|---|---|
| neobrutal | `retro` (default) | [styleguides/retro.md](styleguides/retro.md) | sempre |
| terminal | `terminal` | [styleguides/terminal.md](styleguides/terminal.md) | só se o produto trocar de skin |

Saída de linha de comando segue o `styleguide-cli.md` (`goodrepo add cli`). Seções numeradas: o
código referencia por número (`styleguide §9.2`). Decisão específica de {{PROJETO}} não entra nas §1 a §13; vai na §14.

## 1. Princípios

1. **Uma fonte: JetBrains Mono.** Título, corpo, número, botão. Não existe sans.
2. **Raio zero, sem exceção.** Botão, campo, avatar, presença, switch, radio, toast. Nada é círculo.
3. **Moldura grossa e neutra.** 2px em `base-300`. A cor de ênfase nunca é a borda.
4. **Sombra dura sem blur**, deslocada (`6px 6px 0`, `3px 3px 0`). Blur e gradiente não existem.
5. **O retro preenche.** A cor vive no *fill* (CTA, item ativo, linha selecionada, avatar).
6. **Uma cor existe uma única vez.** Todo hex mora num arquivo só, como `--palette-*`.
7. **Caixa alta com tracking largo** em tudo que é interface. Conteúdo mantém a caixa original.
8. **Sem bounce.** Entrada é fade + deslize curto, ease-out, zero overshoot.
9. **Scanline é textura**, não tela: fixa, fraca, sem capturar clique. Produto centrado em mídia
   (capa, foto, vídeo) a põe atrás do conteúdo.
10. **Apagar é cor, nunca opacidade.** `opacity` só em `:disabled` (0.4) e na scanline.
11. **Nenhum componente ramifica por tema ou skin.** Ele escreve a hook class e os `data-*`; o
    CSS (ou o tema nativo) decide o resto.
12. **Voz de máquina.** Prompt `>`, colchetes `[ OK ]`, nome de "arquivo" na barra de janela
    (`CONTAS.CFG`), caret `_` no lugar de spinner.

## 2. Arquitetura de tokens

| Camada | Arquivo (web) | Seletor | Exemplo | Quem escolhe |
|---|---|---|---|---|
| Cor bruta | `palettes.css` | `:root` | `--palette-cream` | ninguém: catálogo fixo |
| Paleta (tema) | `themes.css` | `[data-theme]` | `--color-accent`, `--shadow` | usuário |
| Skin (moldura) | `skins.css` | `[data-skin]` | `--frame-shadow` | usuário ou produto |

A paleta diz *com que cor*; a skin diz *com que forma*. Toda paleta funciona sob toda skin: 10
paletas × 2 skins = 20 aparências, não 20 temas para manter. Tokens de moldura na §7.

Tokens semânticos, com os nomes do daisyUI usados como vocabulário também fora dele:

| Papel | Token |
|---|---|
| Fundo de página | `base-100` |
| Superfície elevada (painel, card, campo, popover, dialog, toast) | `base-200` |
| Toda moldura | `base-300` |
| Texto | `base-content` |
| Texto apagado (meta, micro-texto, placeholder, cabeçalho de tabela) | `muted-text` |
| Ênfase como fill (CTA, item ativo, linha selecionada, avatar) | `accent` + `accent-content` |
| Ênfase como glifo (texto ou ícone na cor de ênfase) | `accent-text` |
| Status como fill / como glifo | `info`, `success`, `warning`, `error` + `-content` / `-text` |
| Sombra dura | `--shadow` |
| Scanline / vinheta do CRT (skin terminal) | `--scanline-color` / `--crt-edge` |

`primary` = `accent` (bibliotecas pedem). `secondary` e `neutral` = texto, `-content` = fundo.

## 3. Catálogo de paletas

**Nomenclatura:** a paleta tem um id kebab de duas palavras (`crimson-chalk`), e o mesmo id é o
`data-theme`, o valor salvo na conta, o `<PREFIXO>_TEMA` do CLI e o enum do app nativo. Rótulo na
tela: o id com espaço (`crimson chalk`). Cor bruta é outra coisa (`--palette-crimson`) e o usuário
nunca a escolhe.

> Divergência resolvida: havia `goodchat-crimson` (web), `crimson`/`rose` (painel e app), "P1
> Crimson Chalk" (portfólio) e `crimson-chalk` (CLI). Vale o id do CLI, sem prefixo de produto.

**Par default (par hub): `crimson-chalk` (claro) e `noir-rose` (escuro).** O modo inicial segue o
sistema (`prefers-color-scheme`); o usuário pode fixar claro ou escuro e escolher uma paleta de
cada modo. Id desconhecido cai no default do modo. O CLI usa `vault-gold` (styleguide-cli.md).

| Id | Modo | `base-100` | `base-200` | `base-content` | `accent` | `accent-content` |
|---|---|---|---|---|---|---|
| `crimson-chalk` | claro | cream | white | ink | crimson | white |
| `abyss-frost` | claro | frost-bg | frost-bg | frost-ink | abyss | white |
| `forest-mist` | claro | forest-bg | forest-bg-raised | forest-ink | forest-green | white |
| `sand-dusk` | claro | sand-bg | sand-bg-raised | sand-ink | copper | near-black |
| `noir-rose` | escuro | noir | noir-raised | cream | rose | near-black |
| `vault-gold` | escuro | graphite | graphite | silver | gold | near-black |
| `midnight-ember` | escuro | midnight | midnight-raised | mint | ember | near-black |
| `cyber-teal` | escuro | cyan-bg | cyan-bg-raised | cyan-mist | cyan | near-black |
| `velvet-purple` | escuro | violet-bg | violet-bg-raised | violet-mist | violet | near-black |
| `neon-matrix` | escuro | black | matrix-bg-raised | matrix-mist | matrix-green | matrix-ink |

- `base-300`: nas claras, a cor do texto; nas escuras, o `accent`, exceto `noir-rose` (cream).
  Sempre borda forte e visível, nunca cinza sutil.
- `--shadow`: o `accent`, exceto `crimson-chalk` (ink).
- Status nas claras: cheios, `-content` white, exceto `success` e `warning` com texto escuro (`ink`
  no crimson-chalk, `near-black` nas outras). Nas escuras: `-soft` com `-content` near-black.
- `--scanline-color` e `--crt-edge`: variante `-light` nas claras, `-dark` nas escuras.

Conteúdo inicial de `palettes.css` (criado o arquivo, ele é a fonte; esta lista não é mantida em
paralelo):

```css
:root {
  --palette-cream: #f2efe7; --palette-white: #ffffff; --palette-black: #000000;
  --palette-ink: #1a0a0a; --palette-noir: #121212; --palette-noir-raised: #1a1a1a;
  --palette-near-black: #0d0d0d; --palette-graphite: #111111; --palette-silver: #e0e0e0;
  --palette-crimson: #dc143c; --palette-crimson-deep: #c8102e; --palette-rose: #e8729a;
  --palette-gold: #c8a96e; --palette-ember: #ff6b45; --palette-copper: #b56a30;
  --palette-frost-bg: #e4f0f6; --palette-frost-ink: #0f172a; --palette-abyss: #0a0f1e;
  --palette-forest-bg: #eef4ee; --palette-forest-bg-raised: #f5faf5;
  --palette-forest-ink: #1a2e1a; --palette-forest-green: #2d6a2d;
  --palette-sand-bg: #f5f0e8; --palette-sand-bg-raised: #fffcf5; --palette-sand-ink: #2a1a0a;
  --palette-midnight: #0d1117; --palette-midnight-raised: #121a12; --palette-mint: #e0ffe0;
  --palette-cyan-bg: #0a0f14; --palette-cyan-bg-raised: #0f1820; --palette-cyan: #00e5ff;
  --palette-cyan-mist: #e0f4ff; --palette-violet-bg: #0e0a14; --palette-violet: #b47aff;
  --palette-violet-bg-raised: #160f20; --palette-violet-mist: #ede0ff;
  --palette-matrix-bg-raised: #0a140a; --palette-matrix-green: #00ff66;
  --palette-matrix-mist: #d7ffd7; --palette-matrix-ink: #001a08;
  /* status: cheio (claras), -deep (glifo nas claras), -soft (escuras) */
  --palette-info: #2563eb; --palette-success: #16a34a; --palette-warning: #d97706;
  --palette-error: #dc2626; --palette-success-deep: #15803d; --palette-warning-deep: #b45309;
  --palette-info-soft: #60a5fa; --palette-success-soft: #4ade80;
  --palette-warning-soft: #fbbf24; --palette-error-soft: #f87171;
  /* overlays; crt-edge é sempre preto, nunca derivado de base-300 */
  --palette-scanline-light: rgba(0, 0, 0, 0.05); --palette-scanline-dark: rgba(0, 0, 0, 0.2);
  --palette-crt-edge-light: rgba(0, 0, 0, 0.16); --palette-crt-edge-dark: rgba(0, 0, 0, 0.55);
}
```

## 4. Contraste

Alvo WCAG AA: **4.5:1** para texto (inclusive o micro-texto de 10px) e **3:1** para elemento de
interface que carrega significado (moldura, trilho, ícone). Razões calculadas em 2026-09-21 sobre
`base-100` e `base-200` de cada paleta.

**Fill não é glifo.** Cor que serve de fundo nem sempre serve de texto; daí os tokens `-text`:

| Token | Valor | Exceção |
|---|---|---|
| `accent-text` | `accent` | crimson-chalk: crimson-deep (5.12:1); sand-dusk: `base-content` |
| `muted-text` | 60% de `base-content` em `base-100` | 65% em abyss-frost, forest-mist, sand-dusk |
| status `-text`, escuras | o `-soft` | nenhuma (todos acima de 6.2:1) |
| status `-text`, claras | `info`, `error`, `success-deep`, `warning-deep` | só sobre `base-200` |

- `bg-accent` usa `accent`; texto e ícone usam `accent-text`. Idem para status. Moldura na cor de
  status fica no token base (3:1 basta).
- **Página clara não recebe status como texto solto:** sobre `base-100` claro, verde, âmbar e
  vermelho ficam abaixo de 4.5:1. Lá o status vai como fill (tag, banner, quadrado de cor) com
  rótulo em `-content` ou `base-content`. Em abyss-frost (`base-200` = `base-100`) vale sempre.
- Sand-dusk: copper como texto dá 3.65:1. Até existir um `--palette-copper-deep` conferido, a
  ênfase em texto nessa paleta usa `base-content`; o accent fica no fill.

> Divergência resolvida: GoodChat e GoodEconomy têm `accent-content: white` no noir-rose (2.87:1);
> Goodbot e GoodMusic corrigiram para near-black. O kit estende a correção às outras escuras e ao
> sand-dusk (white dava 1.54 a 4.14:1) e troca `success`/`warning-content` das claras por texto
> escuro (3.30 e 3.19:1 viram 5.84 e 6.04:1).

**Apagar é cor.** `opacity` apaga a subárvore inteira e nenhum filho escapa: um botão dentro de
uma barra apagada vira um falso `:disabled`. **Trilho não é cor fraca:** `base-content` a 20% dá
cerca de 1.6:1; todo trilho (progresso, seek, uso) tem moldura.

> Divergência resolvida: portfólio, GoodChat e GoodEconomy apagavam com `opacity-40` a `70`;
> vale o `muted-text` do Goodbot e do GoodMusic.

## 5. Tipografia

- **Família:** JetBrains Mono, pesos 400, 500, 700 e 800 com itálicos. Web:
  `@fontsource/jetbrains-mono` (sem CDN). Nativo: asset empacotado com a licença OFL, nunca
  baixado em runtime.
- **Peso 900:** `font-black` pede 900 e o render resolve para a face 800. Herdado e aprovado.
- **Números:** mono já é tabular; coluna numérica alinha à direita.

| Papel | Hook class | Regra comum (o tratamento está na §3 da skin) |
|---|---|---|
| Título de tela | `screen-title` | um por tela, caixa alta |
| Kicker | `screen-kicker` + `sigil` | acima do título, prefixo `>` literal |
| Meta da tela | `screen-meta` | micro-texto (`12 REGRAS · 3 ATIVAS`) |
| Label de seção | `section-label` | micro-texto com `>` |
| Corpo | (nenhuma) | `text-sm`/`text-base`, `leading-relaxed`, caixa normal |
| Micro-texto | (utility) | 10px, bold, caixa alta, tracking 0.2em, `muted-text` |
| Valor de stat | `stat-value` | grande, tabular, tracking apertado |

**Caixa.** Interface (botão, aba, label, kicker, estado) em caixa alta aplicada por CSS ou pelo
componente; a string no código e no i18n fica em caixa normal, para o leitor de tela não
soletrar. Conteúdo (nome de pessoa, título de item, texto digitado, metadado) nunca muda de
caixa: pode ganhar peso ou itálico, a caixa é a original. Identificador técnico em `snake_case`.

**Voz.** Interface em pt-BR, inclusive estados (`SALVANDO_`, `NADA AQUI`); jargão de terminal fica
como é (`MODULE`, `PID`, `SRC`, `root@`). Valor ausente em colchetes (`[SEM NOME]`). Metadado
falso-preciso (`-rwxr-xr-x`, `PID: 001`) só como sabor no chrome, nunca parecendo dado real.
Emoji: no máximo um por tela, só com significado, nunca como bullet.

> Divergência resolvida: portfólio e CLI usam chrome em en-US e conteúdo em pt-BR; os apps usam
> pt-BR em tudo. Vale pt-BR, com o jargão de terminal preservado.

## 6. Espaço, layout e responsividade

- **Escala:** a padrão do Tailwind (passo de 4px); no nativo, 4 · 8 · 12 · 16 · 24 · 32.
- **Borda da tela** (`screen-pad`): 1rem, 2rem a partir de 40rem, sempre `max()` com o
  `safe-area-inset`; em paisagem baixa (`height < 30rem`) o vertical cai para 0.5rem.
- **Breakpoints**, mobile-first: `xs` 23rem (360px é o piso), `sm` 40rem, `md` 48rem, `lg` 64rem.
  Botões crescem em `md`; sidebar fixa a partir de `lg`, `sheet` abaixo.
- **Sombra ocupa espaço:** quem tem `--frame-shadow` reserva 6px à direita e embaixo; pai com
  `overflow: hidden` não pode cortá-la.
- **Toque:** com `pointer: coarse`, alvo mínimo de 2.75rem (44px) em `icon-btn`, `tool-btn` e
  campo; Android nativo, 48dp de área (o visual pode ser 40dp).
- **Campo abaixo de 40rem** com `font-size: 1rem`: o Safari dá zoom em campo menor que 16px.
- **Tabela estreita** rola dentro da própria moldura. Texto nunca abaixo de 10px; texto longo
  trunca com reticências e tooltip, nunca marquee. Densidade única, sem "modo compacto".

## 7. Moldura: borda, raio, sombra

Tokens de skin, lidos pelas utilities `retro-border`, `retro-shadow`, `retro-shadow-sm` e pela
regra de foco (o prefixo `retro-` é histórico: toda skin repinta esses ganchos). Projeto de skin
única os declara em `:root` e não usa `data-skin`.

| Token | `retro` (default) | `terminal` |
|---|---|---|
| `--radius-selector` / `-field` / `-box` (tema) | `0rem` | `0rem` |
| `--border` (tema, controles daisyUI) | `2px` | `2px` |
| `--frame-border` | `2px` | `1px` |
| `--frame-shadow` | `6px 6px 0 0 var(--shadow)` | anel 1px + halo (terminal §5) |
| `--frame-shadow-sm` | `3px 3px 0 0 var(--shadow)` | anel 1px + halo menor |
| `--focus-ring-style` / `-offset` | `solid` / `2px` | `dashed` / `1px` |

- `retro-border` = `var(--frame-border) solid var(--color-base-300)`; moldura de status (campo
  com erro, banner) troca só a cor. Separador: 1px de `base-300` a 30% por `color-mix`.
- Painel de topo leva a sombra padrão; clicável descansa com a `sm`; caixa aninhada em painel é
  moldura sobre `base-100`, sem sombra.

> Divergência resolvida: o portfólio permitia `rounded-full` em pontos e avatar e `rounded-sm` em
> chips, e GoodChat/GoodEconomy desenham WindowDots redondos; vale raio zero sem exceção (Goodbot,
> GoodMusic), com WindowDots quadrados.

## 8. Motion

| Movimento | Regra |
|---|---|
| Entrada | fade + `translateY(8px)` para 0, 200ms, `cubic-bezier(0.33, 1, 0.68, 1)` |
| Saída / troca de conteúdo | fade 150ms / cross-fade 150ms, sem deslize |
| Tela (nativo) | fade + 8px em 200ms; modal de tela cheia sobe em 240ms; teto 260ms |
| Interação | da skin: retro levanta ou afunda, terminal só inverte cor |
| Troca de tema | `background-color` e `color` em 0.3s ease no `body` |
| Ambiente | caret `_` (1s, `step-end`), scanline estática; roll do CRT na skin terminal |
| Gráfico | sem animação de entrada, ou 200ms ease-out crescendo de baixo |

Proibido: spring, bounce, elastic, overshoot, shimmer, spinner circular, três bolinhas, pulsar,
girar, marquee, parallax, rolagem com quique e brilho de overscroll (nativo).

**Movimento reduzido** (`prefers-reduced-motion` ou a opção do sistema): durações a 0.01ms,
scanline escondida, caret parado e visível. Efeito que fica feio congelado (o roll do CRT) é
desligado, não congelado.

> Divergência resolvida: o portfólio usava entradas de 300 a 500ms e permitia pulso, anéis
> girando e digitação animada; vale 200ms e só caret + scanline (GoodChat em diante).

## 9. Componentes recorrentes

Anatomia, estados e regras; metragem e pintura estão na §6 de cada skin. Toda classe citada é
**hook class**: o componente a escreve sob qualquer skin.

**9.1 Painel / janela** (`panel`, `panel-body`, `window-bar`, `window-bar-title`, `window-dots`).
Moldura + superfície + sombra. Barra de título opcional: nome de "arquivo" em micro-texto à
esquerda (`CONTAS.CFG`, `CASOS.LOG`) e três WindowDots quadrados de 8px à direita; o primeiro é
accent, ou `error` em diálogo destrutivo, ou a cor do status num toast. A barra pode hospedar
ações: o apagado vale só para o título.

**9.2 Botões.** `btn-brutal` (CTA, fill accent), `btn-brutal-outline` (secundário),
`btn-brutal-danger` (fill `error`, sempre atrás de confirmação), `icon-btn` (ação compacta de
barra e tabela), `tool-btn` (só glifo). Rótulo em caixa alta, verbo no infinitivo (`SALVAR`).
Estados obrigatórios: hover, active, focus-visible, disabled (`opacity` 0.4, sem hover) e
carregando (rótulo vira `SALVANDO_` com caret e o botão desabilita; nunca spinner). Todo
controle tem `cursor: pointer`.

> Divergência resolvida: GoodChat e Goodbot usam `btn-goodchat*`, GoodEconomy `btn-brutal*`; vale
> `btn-brutal*`, que não carrega nome de produto.

**9.3 Campos.** `input`, `textarea` e gatilho de `select`: moldura, `base-200`, 2.75rem de
altura. Label acima no estilo de `section-label`; obrigatório com `*` em `accent-text`; ajuda em
`muted-text` entre label e campo. Erro: moldura `error` + micro-texto `error-text` com prefixo
`!`. `select` mostra `▼` literal. Switch é trilho retangular com polegar quadrado (nunca pílula);
checkbox quadrado com `✓`; escolha única é `segmented` (itens colados, ativo com fill) ou radio
quadrado. Rodapé de formulário: primária à direita, descartar à esquerda.

**9.4 Tags** (`tag` + `tag-accent|info|success|warning|error|muted`). Micro-texto bold caixa alta,
`px-2 py-0.5`. Tag clicável (filtro, legenda) ganha cursor, hover e foco.

**9.5 Tabela** (`data-table`). Moldura com `overflow-x-auto`. Cabeçalho sobre `base-100` com linha
inferior de 2px, `th` em micro-texto `muted-text`; coluna ordenável é `<button>` com `▲`/`▼`.
Linhas com hairline, sem zebra; hover faz fill de `base-content` a 8% (não levanta); selecionada
faz fill accent. Número à direita; ID em micro-texto `select-all`, nunca truncado; data em
`<time>` com o ISO no tooltip. Acima, busca, filtros e `icon-btn`s (com seleção, a barra de ação
em massa ocupa o lugar); abaixo, `< ANTERIOR` / `PRÓXIMA >` e `PÁGINA 3/12 · 240 REGISTROS`.
Recarregar mantém os dados e marca `aria-busy`.

**9.6 Chave-valor** (`kv-row`). Chave em micro-texto `muted-text`, valor em bold `accent-text`,
hairline embaixo. É a forma de todo "rótulo: valor".

**9.7 Stat** (`stat-tile`, `stat-label`, `stat-value`, `stat-delta`). Painel com `> MINUTOS`,
valor grande e delta em micro-texto: `▲ 12%` em `success-text`, `▼` em `error-text`, `= IGUAL`
em `muted-text`.

**9.8 Uso e progresso** (`usage-track`, `usage-fill`). Trilho sempre emoldurado, fill sólido
accent; em cota, `warning` acima de 80% e `error` em 100%. Sem total conhecido: micro-texto com
caret (`PROCURANDO 12/340_`).

**9.9 Skeleton** (`skeleton`). Blocos emoldurados em `base-200` com listras diagonais estáticas
(45°, `base-300` a 10%), na altura real do conteúdo (tabela: 5 linhas). Só aparece se o
carregamento passar de 150ms; o cabeçalho mostra `CARREGANDO_`.

> Divergência resolvida: GoodEconomy usa skeleton com shimmer; vale o estático do Goodbot e do
> GoodMusic.

**9.10 Estados** (`empty-state`). **Vazio:** centralizado, kicker `> NADA AQUI` (ou específico),
uma linha em `muted-text` e CTA outline quando houver ação óbvia; sem ilustração. **Erro de
carregamento:** banner `error` no lugar do conteúdo, a mensagem, o id da requisição em
micro-texto `select-all` e `TENTAR DE NOVO`. **Serviço fora:** banner `warning` fixo abaixo da
topbar, ações dependentes desabilitadas com tooltip. **Sem permissão:** `ACESSO NEGADO`,
explicação e uma saída. **Sessão expirada:** volta ao login com banner `info`.

**9.11 Toast e banner** (`toast`, `alert`). Toast: painel compacto no canto inferior direito
(mobile: acima da navegação inferior), WindowDots com o primeiro na cor do status, título em
micro-texto (`SALVO`, `ERRO`), corpo `text-sm`, ação como `icon-btn` (`DESFAZER`), some em 3s;
sem ícone redondo. Banner: moldura na cor do status sobre `base-200`, título com prefixo `!` em
`-text`. Ação pequena destrutiva confirma inline: o botão vira `CONFIRMAR?` em `error` por 3s.

**9.12 Modais e overlays** (`dialog-box`). Diálogo: painel com barra (`APAGAR.CMD`), ações à
direita (outline + CTA), fundo `base-100` a 80% sem blur, foco preso, `Esc` fecha, foco volta ao
gatilho; destrutivo tem o primeiro WindowDot em `error` e confirma com `btn-brutal-danger`.
Popover, menu, combobox: moldura, `base-200`, sombra `sm`, item ativo com fill accent. Tooltip
invertido (`base-300` de fundo, `base-100` de texto), sem seta. Bottom sheet: cantos retos,
moldura superior, alça retangular 32×4. Entrada `animate-enter`, saída fade 150ms.

**9.13 Avatar e presença** (`avatar-sq`, `presence-dot`). Avatar quadrado emoldurado: foto, ou
fill accent com a inicial em `accent-content`. Presença: quadrado de 12px; pessoa fica `success`
online e apagada offline; serviço (bot, API) fica `success`, `warning` reconectando e `error`
fora. O estado também existe em texto.

**9.14 Navegação.** Sidebar: `base-100`, borda direita 2px, item em caixa alta bold, ativo com
fill accent. Topbar: borda inferior 2px, breadcrumb em micro-texto, toggle de tema (`icon-btn`,
atalho `Shift+T`). Cabeçalho de página: kicker + título + meta, ações à direita. Aba ativa inunda
(retângulo inteiro accent). Navegação inferior (mobile): indicador quadrado, rótulos sempre
visíveis.

**9.15 Gráficos.** Séries só de tokens, no máximo 5, ordem fixa: accent, info, success, warning,
error; período anterior em `base-content` a 30%. Grade só horizontal em hairline; eixos em
micro-texto, sem linha de eixo. Linha reta entre pontos (nunca curva suave), 2px, sem marcador;
barra sólida sem raio, vão de 20%; área a 15% sem gradiente. Legenda como tags clicáveis;
heatmap em 5 degraus (0, 25, 50, 75, 100%).

**Vocabulário de hook classes:** `crt` · `panel`/`panel-body` · `window-bar`/`window-bar-title`/
`window-dots` · `screen-kicker`/`screen-title`/`screen-meta`/`sigil` · `section-label` ·
`prompt-line` · `tile`/`tile-name`/`tile-meta` · `avatar-sq` · `presence-dot` · `icon-btn`/
`tool-btn` · `stat-tile`/`stat-label`/`stat-value`/`stat-delta` · `kv-row` · `tag` · `data-table`
· `usage-track`/`usage-fill` · `dialog-box` · `toast` · `alert` · `skeleton` · `empty-state` ·
`segmented` · `skin-swatch`. Estado vai em `data-*` (`data-selected`, `data-online`,
`data-status`), não em classe. Hook nova nasce disponível para todas as skins.

## 10. Acessibilidade

1. Contraste pela §4. Fill e glifo usam tokens diferentes.
2. **Foco:** `:focus-visible` sempre visível, 2px accent, estilo e offset da skin. A regra global
   fica fora de `@layer`, para vencer o `outline-hidden` de bibliotecas. Em campo com prefixo
   (`.input` como wrapper) o anel vai no wrapper; em overlay com rolagem, offset negativo.
3. Cor nunca é a única pista: item atual também tem forma (`▶`, `[ATIVO]`); status tem palavra.
4. Colchetes, prompts e prefixos decorativos por pseudo-elemento ou `aria-hidden`.
5. Ação é `<button>`, navegação é `<a>`. Nada clicável sem hover, foco e cursor.
6. Região recarregando: `aria-busy`. Toast: `role="status"` (erro: `role="alert"`).
7. Web aguenta zoom de 200%; nativo aguenta `textScaler` 1.3 sem cortar controle.
8. `::selection` em accent/accent-content; `lang="pt-BR"` no documento.

## 11. Receita web (Tailwind v4 + daisyUI 5)

CSS-first, sem `tailwind.config.js`. A skin vem depois do tema porque `[data-skin]` e
`[data-theme]` têm a mesma especificidade e a ordem do arquivo decide.

```css
@import "tailwindcss";
@import "./styles/palettes.css";  /* hex só aqui */
@import "./styles/themes.css";    /* um @plugin "daisyui/theme" por paleta */
@import "./styles/skins.css";     /* moldura; skin grande ganha skin-<id>.css logo depois */
@import "@fontsource/jetbrains-mono/400.css"; /* + 400-italic, 500, 700, 800 e itálicos */
@plugin "daisyui" { themes: false; logs: false; }

@theme {
  --breakpoint-xs: 23rem;
  --font-sans: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  --font-mono: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
}
@theme inline { --color-muted-text: var(--muted-text); --color-accent-text: var(--accent-text);
  /* idem info-text, success-text, warning-text, error-text */ }

@utility retro-border { border: var(--frame-border) solid var(--color-base-300); }
@utility retro-shadow { box-shadow: var(--frame-shadow); }
@utility retro-shadow-sm { box-shadow: var(--frame-shadow-sm); }
@utility terminal-cursor { animation: blink 1s step-end infinite; }
@utility terminal-scanline {
  position: fixed; inset: 0; pointer-events: none; opacity: 0.3;
  background:
    repeating-linear-gradient(to bottom, var(--scanline-color) 0 1px, transparent 1px 4px);
}
@utility animate-enter { animation: brutal-enter 0.2s cubic-bezier(0.33, 1, 0.68, 1) both; }
@keyframes brutal-enter { from { opacity: 0; transform: translateY(8px); } }
@keyframes blink { 50% { opacity: 0; } }

/* Botão estende o btn do daisyUI PELOS TOKENS dele; nunca redefinir .btn. */
@utility btn-brutal {
  --btn-color: var(--color-accent); --btn-fg: var(--color-accent-content);
  --btn-border: var(--color-base-300); --btn-p: 1rem; --size: 3.25rem; --fontsize: 0.875rem;
  font-weight: 900; text-transform: uppercase; letter-spacing: 0.05em;
  @media (width >= 48rem) { --btn-p: 2rem; --size: 3.75rem; --fontsize: 1rem; }
}
/* -outline: --btn-color transparent, --btn-fg base-content.
   -danger: --btn-color error, --btn-fg error-content. O resto igual. */

:focus-visible {
  outline: 2px var(--focus-ring-style) var(--color-accent);
  outline-offset: var(--focus-ring-offset);
}
::selection { background: var(--color-accent); color: var(--color-accent-content); }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important; transition-duration: 0.01ms !important; }
  .terminal-scanline { display: none; }
}
/* + as regras de toque e de campo da §6 (pointer: coarse, width < 40rem) */
```

Molde de tema; as outras paletas seguem a §3. A primeira declarada leva `default: true` e cai em
`:root`; a escura default leva `prefersdark: true`:

```css
@plugin "daisyui/theme" {
  name: "crimson-chalk"; default: true; color-scheme: light;
  --color-base-100: var(--palette-cream);  --color-base-200: var(--palette-white);
  --color-base-300: var(--palette-ink);    --color-base-content: var(--palette-ink);
  --color-primary: var(--palette-crimson); --color-primary-content: var(--palette-white);
  --color-accent: var(--palette-crimson);  --color-accent-content: var(--palette-white);
  --color-secondary: var(--palette-ink);   --color-secondary-content: var(--palette-white);
  --color-neutral: var(--palette-ink);     --color-neutral-content: var(--palette-white);
  --color-info: var(--palette-info);       --color-info-content: var(--palette-white);
  --color-success: var(--palette-success); --color-success-content: var(--palette-ink);
  --color-warning: var(--palette-warning); --color-warning-content: var(--palette-ink);
  --color-error: var(--palette-error);     --color-error-content: var(--palette-white);
  --radius-selector: 0rem; --radius-field: 0rem; --radius-box: 0rem;
  --size-selector: 0.25rem; --size-field: 0.25rem; --border: 2px; --depth: 0; --noise: 0;
  --shadow: var(--palette-ink); --scanline-color: var(--palette-scanline-light);
  --crt-edge: var(--palette-crt-edge-light); --accent-text: var(--palette-crimson-deep);
  --success-text: var(--palette-success-deep); --warning-text: var(--palette-warning-deep);
  --info-text: var(--palette-info); --error-text: var(--palette-error);
  --muted-text: color-mix(in srgb, var(--color-base-content) 60%, var(--color-base-100));
}
```

Regras: (1) variante de botão mexe só nos tokens do `btn` (`--btn-color`, `--btn-fg`,
`--btn-border`, `--btn-p`, `--size`, `--fontsize`), e foco, active e disabled continuam vindo do
daisyUI; (2) regra de skin é unlayered e mira a hook class, nunca uma utility que o componente
combina com variante (`bg-base-200` + `hover:bg-accent` pararia de fazer hover); (3) `data-theme`
e `data-skin` vão no `<html>` por script inline no `<head>`, antes do primeiro paint, lendo o
cache em `localStorage` (`{{PROJETO}}-theme`); a preferência de verdade mora na conta.

**Stack shadcn em vez de daisyUI:** os tokens semânticos ficam em blocos `[data-theme='<id>']` e
as variáveis do shadcn viram aliases, nunca cores novas: `--background`/`--foreground` =
`base-100`/`base-content`; `--card`, `--popover` = `base-200`; `--primary`, `--accent` = `accent`;
`--muted-foreground` = `muted-text`; `--destructive` = `error`; `--border`, `--input` =
`base-300`; `--ring` = `accent`; `--chart-1..5` = accent, info, success, warning, error;
`--radius: 0rem`. Componentes gerados pelo CLI do shadcn são editados para casar com a §9.

## 12. Ports nativos (Flutter, React Native, Rust)

**Idêntico ao web:** os hex, num arquivo só (`palette.dart`, `palette.ts`, módulo `raw` do
`theme.rs`); os nomes semânticos (camelCase permitido: `base100`, `accentText`); a geometria
(raio 0, moldura 2, sombra dura 6,6 e 3,3 sem blur); durações e curva da §8; escala e pesos da
tipografia com a fonte empacotada; regras de caixa; tokens de contraste da §4; anel de foco.

**Adaptado ao meio:**

- Sem hover: o clicável **afunda** ao ser pressionado (skin retro §4.9).
- Onde a plataforma só tem sombra difusa (Android, React Native), a sombra dura é uma caixa
  `--shadow` deslocada atrás do conteúdo. `elevation` é 0 em tudo.
- Material 3: `ColorScheme` é alias dos tokens (`primary` = accent, `surface` = base-100, todo
  `surfaceContainer*` = base-200, `outline` = base-300, `onSurfaceVariant` = muted-text,
  `surfaceTint` transparente); sem ripple; `Radio` e `Switch` redondos trocados por primitivas
  quadradas; ícones na variante de cantos retos.
- Scanline opcional; quando existe, fica atrás do conteúdo. Overlay sobre outro app não a tem.
- Movimento reduzido é a opção do sistema operacional.

> Divergência resolvida: GoodEconomy omite a scanline no mobile e GoodMusic a mantém atrás do
> conteúdo; vale opcional e, quando presente, atrás.

## 13. Como adaptar a um projeto novo

1. Instalar com `goodrepo add styleguide` (traz `styleguide.md` e `styleguides/retro.md` e
   `styleguides/terminal.md`); apagar `styleguides/terminal.md` se o produto não oferecer troca
   de skin. Saída de terminal: `goodrepo add cli` (`styleguide-cli.md`).
2. Trocar `{{PROJETO}}` pelo nome de exibição (em minúsculas quando for id ou chave).
3. Decidir o catálogo (as dez paletas com seletor, ou só o par hub) e as skins (só `retro`, ou
   `retro` + `terminal`). Mudar o par default exige registro na §14 com o motivo.
4. Criar `palettes.css` pela §3 e os temas pela §11; depois utilities, hook classes e os
   componentes da §9, antes das telas.
5. Documentar os componentes do produto na §14 (anatomia, estados) e na §8 de cada skin
   (pintura).
6. Não editar as §1 a §13 para caber o produto: regra que não serve vira "Divergência:" na §14.

## 14. Adaptações de {{PROJETO}}

Única seção que o projeto escreve. Esqueleto:

- **Escopo:** superfícies cobertas (web, app, embeds, notificações, imagem gerada).
- **Catálogo e skins adotados:** quais paletas, qual default, quais skins.
- **Semântica de estado do domínio:** estado do produto para token (`pendente` → `warning`).
- **Componentes do produto:** hook class, anatomia, estados.
- **Motifs do produto:** numerados `A1`, `A2`… para não colidir com a base.
- **Divergências:** regra da base que não vale aqui, com o motivo, uma linha cada.
