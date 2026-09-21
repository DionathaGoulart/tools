# Skin `retro`: style guide

**Escopo:** só a skin `retro`. Paletas, tokens, fonte, motion, acessibilidade e receita estão em
[../styleguide.md](../styleguide.md); a anatomia e os estados dos componentes, na base §9. Aqui
fica a pintura. Quando ativa, a skin vale para o produto inteiro.

- `data-skin='retro'` · rótulo na tela de aparência: **neobrutal**.
- **É a skin default.** Documento ainda sem `data-skin`, conta que nunca escolheu e projeto de
  skin única já estão nela: os tokens ficam em `:root, [data-skin='retro']`.
- É pequena em CSS porque é a linha de base: as utilities da receita (base §11) já falam retro.

## 1. Identidade

**Neobrutalismo.** Cantos retos, molduras grossas, sombra dura deslocada sem blur, display gordo
e itálico. O clicável se comporta como cartão físico: **levanta** sob o mouse e **afunda** sob o
dedo.

A frase que resolve dúvida de implementação: *o retro preenche, o terminal risca.* Aqui a cor
vive no **fill** (CTA, avatar, linha selecionada, tag, aba ativa) e a moldura é `base-300`.

## 2. Cores (uso)

| Papel | Token |
|---|---|
| Fundo de página | `base-100` |
| Superfície elevada (painel, tile, campo, popover, dialog, toast) | `base-200` |
| Toda moldura | `base-300`: neutra, nunca accent |
| Sombra dura | `--shadow` |
| Ênfase, estado ativo, CTA, avatar, linha selecionada | `accent` + `accent-content` |
| Texto e ícone em ênfase | `accent-text` |
| Texto apagado | `muted-text` |
| Hover de linha (tabela, lista, menu) | `base-content` a 8% (`color-mix`) |
| Fundo de modal | `base-100` a 80%, sem blur |
| Tooltip | invertido: `base-300` de fundo, `base-100` de texto |

Nos temas escuros a moldura é clara (a cor do texto ou o accent): borda forte nos dois modos.

## 3. Tipografia (tratamento)

| Uso | Tratamento (Tailwind) |
|---|---|
| `screen-title` | `text-3xl md:text-4xl font-black uppercase italic tracking-tighter` |
| `screen-title` na tela de entrada | `text-5xl md:text-6xl` + sublinhado accent (abaixo) |
| `screen-kicker` | `text-xs font-bold uppercase tracking-widest text-accent-text` + `>` |
| `section-label` | igual ao kicker; compacto: `text-[10px] tracking-[0.2em]` |
| `screen-meta`, micro-texto | `text-[10px] font-bold uppercase tracking-[0.2em] text-muted-text` |
| `th` | `text-[10px] font-black uppercase tracking-[0.2em] text-muted-text` |
| Label de campo | `text-xs font-bold uppercase tracking-widest` |
| Corpo, célula | `text-sm`/`text-base leading-relaxed` |
| `stat-value` | `text-3xl md:text-4xl font-black tracking-tighter tabular-nums` |
| Conteúdo em destaque | `font-black italic`, caixa preservada |

O `>` do kicker é o `.sigil`. Sublinhado da tela de entrada: `underline decoration-accent
decoration-4 underline-offset-4`. Nativo (sp): título 28 (entrada 36), kicker 12, corpo 14,
botão 14, micro-texto 10, stat 40 a 48; `w800` onde o web pede `font-black`; `letterSpacing` -1
no título, 2 no micro-texto, 2.4 no kicker, 0.7 no botão.

Padrão: caixa alta em tudo que não é corpo nem conteúdo, `tracking-tighter` nos títulos grandes,
`tracking-widest`/`0.2em` nos micro-labels, itálico como recurso de display,
`font-black`/`font-bold` dominantes.

## 4. Motifs

Numerados: o código referencia por número (`retro §4.3`).

1. **Sombra dura deslocada.** `--frame-shadow: 6px 6px 0 0 var(--shadow)` e `--frame-shadow-sm:
   3px 3px 0 0 var(--shadow)`, via `retro-shadow`/`retro-shadow-sm`. Sem blur, sem spread. É a
   assinatura nº 1.
2. **Moldura grossa reta.** `--frame-border: 2px` em `base-300`, via `retro-border`.
3. **Zero raio.** Inclusive presença, avatar, switch, radio e WindowDots.
4. **Scanline discreta.** `terminal-scanline`: 1px a cada 4px, `opacity: 0.3`, fixa,
   `pointer-events: none`. Textura, não tela (o CRT é da skin terminal).
5. **Caret `_` piscando.** `terminal-cursor`, `blink 1s step-end infinite`. Em `SALVANDO_`,
   `CARREGANDO_` e digitação, no lugar de spinner ou três bolinhas.
6. **Micro-texto de máquina.** `>` em kicker e label, valor ausente em colchetes, estado em caixa
   alta.
7. **WindowDots.** Três quadrados de 8px: `accent`, `base-300`, `base-300`.
8. **Barra de título** (`window-bar`). Linha inferior de 2px `base-300` sobre `base-100`,
   `px-4 py-3`, título em micro-texto bold `muted-text` caixa alta (`CONTAS.CFG`), WindowDots à
   direita.
9. **Levantar no hover, afundar no toque.** Mouse: `hover:-translate-y-1` + sombra `sm` para a
   padrão, `active:translate-y-0`, `transition-all duration-300` (no Tailwind v4, `hover:` já só
   vale com `@media (hover: hover)`). Toque (nativo): o elemento desloca pelo offset da própria
   sombra e a sombra vai a zero em 90ms; soltar volta em 120ms. Só em clicável com moldura e
   sombra (botão, tile, card-link); linha de tabela ou lista faz fill. Arrastar levanta: o item
   arrastado ganha a sombra grande.
10. **Seleção temática.** `::selection` em accent/accent-content.
11. **CTA grande.** 3.25rem (md: 3.75rem), peso 900, caixa alta (§6).
12. **Foco sólido.** `outline: 2px solid` accent, `outline-offset: 2px`.
13. **Movimento reduzido.** Animações congeladas, scanline escondida.
14. **Nada clicável parece desligado.** Cursor, hover e foco em todo controle; opacidade menor
    que a de um controle ativo significa `:disabled`, e só isso.

> Divergência resolvida: no toque, GoodEconomy afunda 3px com sombra `sm`; GoodMusic desloca pelo
> offset inteiro e zera a sombra. Vale o GoodMusic: o cartão encosta na própria sombra.

**Não existem nesta skin** (não inventar): glow de fósforo, vinheta ou curvatura de CRT, dot grid,
dithering, glitch, fonte pixel, borda pixel-stepped, prompt de shell, gradiente, sombra suave,
raio, spinner circular, skeleton com shimmer, ripple de toque.

### Motion

- Entrada: `animate-enter` (base §8).
- Interação: levanta em 300ms (mouse) ou afunda em 90ms e volta em 120ms (toque).
- Ambiente: caret e scanline estática. Nada mais se mexe sozinho.

## 5. Geometria e tokens

```css
:root,
[data-skin='retro'] {
  --frame-border: 2px;
  --frame-shadow: 6px 6px 0 0 var(--shadow);
  --frame-shadow-sm: 3px 3px 0 0 var(--shadow);
  --focus-ring-style: solid;
  --focus-ring-offset: 2px;
}
/* Só com skin terminal no produto, e DEPOIS da regra `.retro-border` da terminal (mesma
   especificidade: a ordem decide). A prévia retro dentro de página terminal reivindica a
   própria moldura; as duas formas porque a prévia carimba o atributo no próprio elemento. */
[data-skin='retro'] .retro-border,
.retro-border[data-skin='retro'] { border-color: var(--color-base-300); }
```

O seletor de atributo junto do `:root` não é redundante: é o que deixa uma subárvore (a prévia na
tela de aparência) voltar para a retro dentro de uma página em outra skin.

Medidas (escala padrão do Tailwind): painel `p-4 md:p-6 gap-4`; tile `p-4 gap-3`; barra de título
`px-4 py-3`; `icon-btn` `px-3 py-2`; célula `px-4 py-3`; campo `h-11 px-3`; formulário `gap-6`
entre campos e `gap-2` de label para campo; tag `px-2 py-0.5`.

## 6. Componentes

Anatomia e estados na base §9; aqui só a pintura.

- **Botões.** `btn-brutal`: fill accent, texto `accent-content`, moldura `base-300`, `--btn-p`
  1rem (md: 2rem), altura 3.25rem (md: 3.75rem), fonte 0.875rem (md: 1rem), peso 900, caixa
  alta, `letter-spacing: 0.05em`, sombra `sm` e levante no hover. `-outline`: transparente, texto
  `base-content`. `-danger`: fill `error`, texto `error-content`.
- **`icon-btn`.** `retro-border bg-base-200 px-3 py-2`, `text-[10px] font-black uppercase
  tracking-widest`; hover inunda de accent e levanta; `disabled:opacity-40`. `tool-btn`: o mesmo,
  só com glifo.
- **Painel.** `retro-border bg-base-200 retro-shadow` + `window-bar` (§4.8) + `panel-body`.
- **Tile** (item interativo de lista, card-link). `retro-border bg-base-200 p-4
  retro-shadow-sm` + `hover:bg-accent hover:text-accent-content hover:-translate-y-1
  hover:retro-shadow active:translate-y-0`. Nome em bold, meta em micro-texto.
- **Campos.** `retro-border bg-base-200 h-11 px-3 text-sm`; foco pelo anel global; erro com
  `border-error`. Switch: trilho 2.5×1.25rem emoldurado, polegar quadrado `base-300` que vira
  `accent-content` sobre trilho `accent` quando ligado. Checkbox de 1.25rem, marcado com fill
  accent e `✓`. `segmented`: itens `retro-border` colados (`-ml-[2px]`), ativo com fill accent.
- **Tag.** Moldura 2px e fill sólido: `tag-accent` (accent), `tag-info|success|warning|error`
  (status com `-content`), `tag-muted` (`base-200` com `muted-text`).
- **Tabela.** Wrapper `retro-border bg-base-200 retro-shadow overflow-x-auto`; `thead`
  `bg-base-100 border-b-2 border-base-300`; linha com hairline, hover com fill a 8%, selecionada
  com fill accent.
- **Chave-valor.** Chave `muted-text`, valor `font-bold text-accent-text`, hairline embaixo.
- **Stat.** Painel com `stat-label` (`> NOME`), `stat-value` e `stat-delta`. Sparkline opcional:
  uma linha accent, sem eixo, 40px de altura.
- **Uso e progresso.** Trilho `retro-border bg-base-100 h-3`, fill sólido accent.
- **Skeleton.** Blocos `retro-border bg-base-200` com `repeating-linear-gradient(45deg, ...)` de
  `base-300` a 10%.
- **Toast.** `retro-border bg-base-200 retro-shadow`, WindowDots com o primeiro na cor do status.
  **Banner** (`alert`): `border-2` na cor do status, fill `base-200`, título com `!` em `-text`.
- **Overlays.** `dialog-box`: `retro-border bg-base-200 retro-shadow` + `window-bar`, fundo
  `bg-base-100/80`. Popover e menu: `retro-border bg-base-200 retro-shadow-sm`, item ativo com
  fill accent. Tooltip: `retro-border bg-base-300 text-base-100 retro-shadow-sm`, micro-texto.
- **Avatar.** `retro-border`; foto, ou fill accent com a inicial `accent-content font-black
  uppercase`.
- **Presença.** Quadrado de 12px com anel de 2px `base-200` recortando a superfície.
- **Navegação.** Sidebar `bg-base-100 border-r-2 border-base-300`, item `px-3 py-2 text-sm
  font-bold uppercase tracking-wide`, ativo com fill accent + `retro-shadow-sm`, hover com fill a
  8%. Topbar `bg-base-100 border-b-2 border-base-300`. Aba ativa: fill accent no retângulo
  inteiro. Navegação inferior: moldura superior de 2px, indicador quadrado accent.
- **Gráficos.** Barra sólida sem raio; o destaque (período atual, item nº 1) ganha sombra `sm`.
  Tooltip no estilo de popover.
- **Vazio.** Kicker `> NADA AQUI`, uma linha em `muted-text`, `btn-brutal-outline` se houver ação.

## 7. Origem e decisões

Linhagem: portfólio (web) → GoodChat (skin `retro`) → Goodbot (painel, conferência WCAG) →
GoodMusic (Flutter, toque). Mantido de ponta a ponta: o par hub; `font-black` resolvendo para 800;
scanline na força base; foco sólido de 2px.

Decisões consolidadas neste kit:

1. Raio zero sem exceção, WindowDots quadrados (base §7).
2. Apagado por `muted-text`, nunca por `opacity` (base §4).
3. Linha de tabela ou lista faz fill; só o que é cartão levanta (Goodbot).
4. No toque, afundar pelo offset inteiro da sombra (GoodMusic, ver §4.9).
5. Skeleton estático, sem shimmer (base §9.9).
6. Gráfico com linha reta, sem gradiente, sem animação de entrada (base §9.15).

## 8. Componentes de {{PROJETO}}

Pintura, sob esta skin, dos componentes que o produto declarou na base §14. Uma entrada por
componente: hook class, classes ou tokens, estados. Exemplo de forma:

- **`<hook-class>`.** `retro-border bg-base-200 ...`; hover ...; selecionado ...; vazio ...
