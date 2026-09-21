# Skin `terminal`: style guide

**Escopo:** só a skin `terminal`. Paletas, tokens, fonte, motion, acessibilidade e receita estão
em [../styleguide.md](../styleguide.md); a anatomia e os estados dos componentes, na base §9.
**Opcional:** só existe em produto que oferece troca de skin. Quando ativa, vale para o produto
inteiro.

- `data-skin='terminal'` · rótulo na tela de aparência: **terminal**.
- Arquivos: bloco de tokens em `skins.css` (ao lado da retro) e o resto em `skin-terminal.css`,
  importado logo depois. A divisão é só por tamanho; a cascata é a mesma.
- Nenhum componente sabe que ela existe: tudo é CSS sobre as hook classes e os `data-*`.

## 1. Identidade

**Um CRT com um log rodando nele.** Não é a retro mais fina: é outra máquina. A página é vidro
escuro atrás de um bezel; as superfícies não sobem, são separadas por **linhas de fósforo**.
Título vira prompt de shell, lista vira listagem de diretório, feed vira log, campo de envio vira
linha de comando, botão vira `[ comando ]`.

A frase que resolve dúvida: *o retro preenche, o terminal risca.* Quase nada tem fill: o que
existe é hairline em accent, wash de accent a 3 a 6% e glow. Fill sólido accent fica para **um**
estado: a inversão de seleção (linha ou botão em hover), o idioma de qualquer TUI.

**O que a skin retira, de propósito:** o levante no hover (`transform: none`), porque nada flutua
numa tela de fósforo; a sombra dura; o fill `base-200`; o display itálico gordo.

## 2. Cores (uso)

As cores são as da paleta ativa (todas funcionam; as de accent forte, como `neon-matrix` e
`cyber-teal`, mostram melhor o glow). O que é da skin é a **diluição**: accent misturado com
transparente, em degraus fixos.

| Degrau | Onde |
|---|---|
| accent 3 a 6% | corpo de painel (3%), vidro do diálogo e do campo (4%), botão e barra (5%) |
| accent 8 a 10% | avatar, skeleton, linha inferior da barra de janela |
| accent 14 a 16% | hairline de lista e de tabela (14%), bezel do CRT (16%) |
| accent 22 a 30% | moldura de painel, campo e botão (30%), mídia (25%), trilho (22%) |
| accent 100% | texto de destaque, caret, fill da inversão em hover |

- **Diluição é para fundo, linha e glifo decorativo** (colchetes, `>` de gutter, prompt, pontos).
  Texto que o usuário precisa ler (título de janela, meta, label, placeholder) usa `muted-text`
  ou `accent-text`: accent a 45 ou 55% sobre o fundo dá 2.2 a 3.5:1 na maioria das paletas.
- Texto "em accent" é sempre `accent-text` (em crimson-chalk e sand-dusk ele difere do accent).
- Vinheta: `--crt-edge` (do tema), sempre preta. Derivada de `base-300`, acenderia os cantos das
  paletas escuras em vez de escurecê-los.
- Status continua com as cores do tema; tags viram `[texto]` na cor `-text`, sem bloco.

> Divergência resolvida: o GoodChat apaga título de janela, meta, kicker e placeholder com
> `opacity` de .35 a .55 (2.2 a 3.5:1 calculado); o kit limita a diluição à decoração e usa
> `muted-text` no texto, pela regra "apagar é cor" (base §4).

## 3. Tipografia (tratamento)

O oposto da retro: **nada de display gordo e itálico**; tudo é micro-tipografia larga.

- **`screen-title`:** 1.375rem (≥40rem: 1.75rem), peso 700, sem itálico, `letter-spacing:
  0.3em`, sem sublinhado, `accent-text`, `text-shadow: 0 0 12px currentColor`, seguido de caret
  em bloco.
- **`screen-kicker`:** minúsculas (um prompt não grita); o `>` do markup vira o prompt
  `{{PROJETO}}@tty1:~$` em 0.75rem, decorativo. **`screen-meta`:** `muted-text`.
- **`section-label`:** `[ LABEL ]`. O `>` some, os colchetes ficam diluídos, `letter-spacing:
  0.2em`, hairline embaixo (accent 15%, `padding-bottom: 0.375rem`).
- **`prompt-line`:** o `>` vira `$`. **Log e feed:** 0.8125rem, `line-height: 1.55`.
- **Nome ou valor em destaque:** `accent-text` + `text-shadow: 0 0 10px currentColor`.

O glow chega por `[data-skin='terminal'] .text-accent, .text-accent-text { text-shadow: 0 0 10px
currentColor }`: por `currentColor`, e não pelo token, para sobreviver ao hover que inverte o
texto.

## 4. Motifs

Numerados: o código referencia por número (`terminal §4.6`).

1. **Bezel + vidro** (`.crt`, montado uma vez na raiz do app, invisível nas outras skins):
   `position: fixed; inset: 0.25rem`, borda 1px accent 16%, acima do conteúdo,
   `pointer-events: none`.
2. **Vinheta + dot grid** (`.crt::before`, esticado a `-0.25rem`): elipse escurecendo a partir de
   45% com `--crt-edge`, sobre pontos de 1px a cada 26px em accent 9%.
3. **Roll** (`.crt::after`): banda de 30% da altura em accent 5% descendo em
   `crt-roll 7s linear infinite`. Desligado por completo em movimento reduzido (congelado, vira
   uma faixa parada).
4. **Scanline forte:** `terminal-scanline` reescrita como banda de 4px
   (`linear-gradient(to bottom, transparent 50%, var(--scanline-color) 51%, transparent 51%)`,
   `background-size: 100% 4px`), `opacity: 0.22`. Lê como tela, não como textura.
5. **Glow de fósforo:** `0 0 10px currentColor` no texto em accent, 12px no título de tela.
6. **Caret em bloco:** `terminal-cursor` vira bloco de 0.6em × 1.05em em accent, com o caractere
   transparente por baixo; `blink 1s step-end`.
7. **WindowDots:** um accent que apaga: accent, accent 40%, accent 20% (quadrados, via
   `.window-dots > :nth-child(n)`).
8. **Barra de janela** (`window-bar`): wash accent 5% sob hairline de `var(--frame-border)` em
   accent 10%, `padding: 0.5rem 1rem`; título em `muted-text`, peso 400, `letter-spacing:
   0.05em`, minúsculo e prefixado de `~/` (`~/contas.cfg`).
9. **Colchetes como chrome:** `[ salvar ]` em botão de barra, `[3]` em contador, `[ativo]` em
   tag. Sempre por pseudo-elemento: o texto no DOM continua a palavra limpa, para o leitor de tela
   e para a outra skin.
10. **Cursor de gutter:** `>` em `::before` de cada linha de lista, diluído, acendendo no hover.
11. **Sem levante:** `transform: none` no hover das utilities de moldura. A inversão de cor é o
    feedback.
12. **Foco tracejado:** `--focus-ring-style: dashed`, `--focus-ring-offset: 1px` (espessura e cor
    vêm da regra global); `caret-color` de campo em accent.
13. **Movimento reduzido:** herda o congelamento global e desliga o roll.

**Não existem nesta skin** (não inventar): sombra dura deslocada, fill `base-200`, título itálico,
raio, levante no hover.

**Motion:** entrada pela `animate-enter` da base; ambiente com roll do CRT (7s), caret (1s) e
scanline estática; interação só troca de cor (inversão accent/accent-content), nenhum transform.

## 5. Geometria e tokens

```css
[data-skin='terminal'] {
  --frame-border: 1px;
  --focus-ring-style: dashed;
  --focus-ring-offset: 1px;
  --frame-shadow:
    0 0 0 1px color-mix(in srgb, var(--color-accent) 30%, transparent),
    0 0 18px -4px color-mix(in srgb, var(--color-accent) 45%, transparent);
  --frame-shadow-sm:
    0 0 0 1px color-mix(in srgb, var(--color-accent) 22%, transparent),
    0 0 10px -4px color-mix(in srgb, var(--color-accent) 35%, transparent);
}
/* A moldura é fósforo, não base-300. Unlayered, para vencer a utility retro-border. */
[data-skin='terminal'] .retro-border {
  border-color: color-mix(in srgb, var(--color-accent) 30%, transparent);
}
```

O anel hairline mantém a moldura legível em paleta cujo accent quase não brilha; o halo
desfocado carrega as que brilham. Os dois juntos são a "sombra" da skin. Numa superfície com fill
accent (hover invertido, avatar) a linha some no fill de propósito; a borda fica por conta do
anel.

Densidade: a skin **aperta** tudo. Painel com `padding: 1rem`; linha de lista `0.625rem 0.5rem`;
barra de contexto `0.5rem 0.75rem`; log com `gap: 0.125rem`; botão de 2.5rem de altura contra os
3.25/3.75rem da retro.

## 6. Componentes

Anatomia e estados na base §9; aqui só a pintura.

- **Botões** (`btn-brutal`, `-outline`): fantasma. Fill accent 5%, texto accent, borda accent 30%
  via `--btn-border`, `--btn-p: 1rem`, `--size: 2.5rem`, `--fontsize: 0.75rem`, peso 700, sem
  crescer no breakpoint. Hover inunda de accent (5% é fraco demais para ler um hover). `-danger`:
  a mesma receita com `error` no lugar do accent.
- **`icon-btn`:** fill 5%, texto accent, `letter-spacing: 0.1em`, envolto em `[ ]`; hover inunda.
  **`tool-btn`:** o mesmo fantasma **sem** colchetes: são glifos (`+`, `▦`), não comandos.
- **Painel:** sem superfície elevada. Borda accent 30% sobre `base-100` com 3% de accent
  misturado; `panel-body` com `padding: 1rem`. `dialog-box`: o mesmo vidro, a 4%.
- **Campo:** fundo accent 4%, borda accent 30%, placeholder em `muted-text`. Campo de envio
  (composer, busca principal) vira linha de comando: hairline no topo (accent 25%), fundo
  transparente, prefixo `>` em accent com glow antes do caret.
- **Skeleton:** fósforo apagado (accent 10%), não bloco cinza; sem shimmer.
- **Lista** (`tile`): listagem de diretório. Sem moldura, fill ou sombra; só hairline embaixo
  (accent 14%) e o `>` no gutter. O hover **mantém** a inundação de accent do markup (é a barra
  de seleção de TUI). `tile-name` em accent com glow; contador sem chip, escrito `[3]`.
- **Tabela:** o mesmo idioma da lista. Moldura accent 30%, `th` em micro-texto `muted-text` sobre
  hairline, linhas com hairline accent 14%; hover e seleção invertem.
- **Stat e chave-valor** (readout): transparente, sem sombra; `stat-label` e chave prefixados de
  `# `; `stat-value` e valor em `accent-text` com glow.
- **Tag:** `[palavra]` na cor `-text` do estado, sem fill.
- **Uso e progresso:** caixa de 1px accent 22%; `usage-fill` vira blocos (`▮▮▮▮░░`) por gradiente
  repetido de 4px cheios e 2px vazios. A proporção continua exata.
- **Avatar:** quadrado de fósforo, fundo accent 8% e inicial em accent; sob hover da linha,
  inverte para `accent-content` a 12%.
- **Presença:** perde o anel (não há superfície para recortar) e ganha halo `0 0 8px` de
  `success` só online (`[data-online='true']`): ponto apagado brilhando diria o contrário.
- **Log e feed** (mensagens, eventos, auditoria): cada item vira uma linha de log. O prefixo é um
  `::before` montado de `attr(data-time)` e `attr(data-sender)`, atributos que o componente
  sempre escreve e a retro ignora:

  ```
  [14:22] <alice> deploy concluído
  [14:23] <bob> ok ✓✓
  ```

  O corpo vira `display: inline` (como bloco, dobraria a altura do log). A meta some: a hora está
  no prefixo e o estado vira glifo no fim (`…` enviando, `✓` enviado, `✓✓` entregue). Item
  próprio se distingue por cor (accent), não por lado. Mídia ganha moldura de 1px accent 25% e
  `max-height: 14rem`.
- **Barra de contexto** (cabeçalho de detalhe ou conversa): wash accent 6%, sem sombra, nome em
  accent com glow e `letter-spacing: 0.08em`.
- **Toast e banner:** vidro com moldura na cor do status a 30%; título entre colchetes na cor
  `-text` do status (`[ ERRO ]`, `[ SALVO ]`).
- **Prévia de skin** (`skin-swatch`): a prévia terminal desenha as próprias scanlines, e a prévia
  retro reivindica a face limpa (`[data-skin='retro'] .skin-swatch`); senão as duas mentiriam.

## 7. Origem e decisões

Adaptada da skin terminal do portfólio, via GoodChat. Nasceu **sem style guide**, como um bloco
de três tokens de moldura, e ganhou este arquivo quando virou uma tomada de conta do produto
inteiro. A régua para qualquer skin nova: se ela inventa regra que um implementador precisaria
adivinhar, ganha style guide (mesmo esqueleto: identidade, cores, tipografia, motifs, geometria,
componentes, origem); se só troca os tokens de moldura, basta o bloco comentado em `skins.css`.

Decisões consolidadas neste kit: texto legível nunca é accent diluído (§2); `-danger`, tabela,
toast e banner foram derivados das regras da skin (fantasma, hairline, colchetes), porque a origem
era um chat sem esses componentes; o log de IRC vale para qualquer lista cronológica.

## 8. Componentes de {{PROJETO}}

Pintura, sob esta skin, dos componentes que o produto declarou na base §14. Uma entrada por
componente: hook class, regra CSS, estados. A pergunta de cada entrada: *como isso vira texto num
terminal?* (linha de log, listagem, readout, comando entre colchetes).
