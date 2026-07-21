# Style Guide — portfolio-dev (Retro Terminal)

Extracted from `Portfolio` (Next.js 15 + Tailwind v4), page `/dev`.
Aesthetic: **neo-brutalist retro terminal** — hard edges, 2px solid borders, offset flat shadows, monospace everything, terminal metaphors (prompts, modules, PIDs, scanlines). All type is JetBrains Mono; almost everything is UPPERCASE with wide tracking.

## 1. Design Tokens (CSS variables)

The whole theme runs on 6 CSS vars, consumed by Tailwind v4 `@theme inline`:

```css
@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-accent: var(--accent);
  --color-card: var(--card-bg);
  --color-border-custom: var(--border);
  --color-shadow-custom: var(--shadow);
  --font-sans: var(--font-jetbrains-mono);
  --font-mono: var(--font-jetbrains-mono);
}
```

Utility classes available: `bg-background`, `text-foreground`, `text-accent`, `bg-card`, `border-border-custom`, plus opacity modifiers (`text-accent/30`, `bg-accent/10`, `border-accent/20`...).

### Default /dev palettes

**Light — P2 "Abyss Frost"**
| token | value |
|---|---|
| `--background` | `#e4f0f6` |
| `--foreground` | `#0f172a` |
| `--accent` | `#0a0f1e` |
| `--card-bg` | `#e4f0f6` |
| `--border` | `#0f172a` |
| `--shadow` | `#0a0f1e` |

**Dark — D2 "Vault Gold"** (applied under `.dark`)
| token | value |
|---|---|
| `--background` | `#111111` |
| `--foreground` | `#e0e0e0` |
| `--accent` | `#c8a96e` |
| `--card-bg` | `#111111` |
| `--border` | `#c8a96e` |
| `--shadow` | `#c8a96e` |

### Full palette catalog (user-switchable at runtime)

Light: P1 Crimson Chalk (`#f2efe7`/`#1a0a0a`/acc `#dc143c`/card `#ffffff`), P2 Abyss Frost (above), P3 Forest Mist (`#eef4ee`/`#1a2e1a`/acc `#2d6a2d`/card `#f5faf5`), P4 Sand Dusk (`#f5f0e8`/`#2a1a0a`/acc `#b56a30`/card `#fffcf5`).
Dark: D1 Noir Rose (`#121212`/`#f2efe7`/acc `#e8729a`/card `#1a1a1a`), D2 Vault Gold (above), D3 Midnight Ember (`#0d1117`/`#e0ffe0`/acc `#ff6b45`/card `#121a12`), D4 Cyber Teal (`#0a0f14`/`#e0f4ff`/acc `#00e5ff`/card `#0f1820`), D5 Velvet Purple (`#0e0a14`/`#ede0ff`/acc `#b47aff`/card `#160f20`).

Pattern: `border` and `shadow` equal `foreground` (light) or `accent` (dark). Semantic extras used sparingly: `text-green-500/90` for `[ OK ]` status, `red-500` tones for locked/private states, plain `white` for text on accent surfaces.

## 2. Typography

- **Single family:** JetBrains Mono (local files), weights 400, 500, 700, 800 + italics. Exposed as both `--font-sans` and `--font-mono`; body uses it by default with `antialiased`.
- **Casing:** headings, labels, buttons, nav = `uppercase`. Identifiers in snake_case or dot.case (`projects_repo`, `USER_MANIFEST`, `dionatha.goulart`).

Scale in use:
| role | classes |
|---|---|
| Giant display (contact title) | `text-3xl md:text-6xl font-black uppercase` + `terminal-glow` |
| Section title (terminal variant) | `text-xl md:text-2xl font-black text-accent uppercase tracking-wider` with dim number prefix `text-xs opacity-40` |
| Big section header (About) | `text-2xl md:text-4xl font-black text-accent tracking-tighter uppercase` |
| Card/project title | `text-2xl md:text-3xl font-black text-accent uppercase tracking-tight` |
| Item title (company) | `text-base md:text-lg font-black text-accent uppercase tracking-tight` |
| Hero statement | `text-base md:text-xl uppercase font-bold tracking-tight italic text-foreground/80 leading-snug` |
| Body | `text-sm` or `text-xs md:text-sm`, `leading-relaxed`, `text-foreground/70..85` |
| Sub-heading label (`# RESUMO`) | `text-xs font-bold text-accent uppercase tracking-wider` |
| Micro-label / chrome | `text-[9px]`–`text-[10px] font-mono uppercase tracking-widest` (up to `tracking-[0.4em]`/`[0.5em]`), often `opacity-30..50` |

Weights: `font-black` dominates titles/labels; `font-bold` for emphasis; `font-medium`/normal for terminal output.

## 3. Spacing & Layout

- Page container: `max-w-7xl mx-auto px-4 sm:px-6 md:px-10 pb-20 pt-20 md:pt-24`.
- Sections stack: `flex flex-col gap-16 md:gap-28`.
- Section title margin: `mb-6 md:mb-8`.
- Card innards: `p-5 md:p-8` (dense: `p-4`, spacious: `md:p-12`).
- Module chrome bar: `px-4 py-2`.
- Grids: 12-col (`grid-cols-1 md:grid-cols-12` with `col-span-7/5/8/4` splits), gaps `gap-5 md:gap-6`.
- Breakpoints: stock Tailwind `sm` / `md` / `lg`; mobile-first, most splits flip at `md` or `lg`.
- Header: `fixed top-0 left-0 w-full z-[100] py-3 md:py-6`, no background (pointer-events trick: `pointer-events-none` on header, `pointer-events-auto` on nav).

## 4. Borders, Radius & Shadows

```css
.retro-border    { border: 2px solid var(--border); }
.retro-shadow    { box-shadow: 6px 6px 0 0 var(--shadow); }  /* hero/major windows */
.retro-shadow-sm { box-shadow: 3px 3px 0 0 var(--shadow); }  /* modules/cards */
```

- **Radius: 0 everywhere.** Sharp corners are the identity. Exceptions: `rounded-full` for dots/rings/avatar, `rounded-sm` only on tiny status chips.
- No blur shadows, no gradients (except decorative radial dot-grid). Flat offset shadows only.
- Hairline separators: `border-accent/10..20`, dashed variant `border-t border-dashed border-accent/20`.

## 5. Signature Effects

```css
.terminal-glow     { text-shadow: 0 0 10px var(--accent); }
.terminal-scanline { /* fixed overlay, repeating 4px horizontal lines, opacity .3 (dark: rgba(0,0,0,.2)) */ }
.terminal-cursor   { /* 0.6em × 1.1em block in accent, blink 1s step-end infinite */ }
```

- Watermark logo inside cards: absolutely centered, `opacity-[0.03]`, oversized (`w-[150%] -rotate-12`), `pointer-events-none select-none`.
- Decorative dot grid: `radial-gradient(var(--color-accent) 1px, transparent 1px)`, `backgroundSize: 20px 20px`, `opacity-[0.05]`.
- ASCII progress bars: `"█".repeat(active) + "▒".repeat(rest)` (20 blocks), `text-accent/90 tracking-widest`.
- Glow bar fill: `bg-accent shadow-[0_0_15px_var(--accent)]`.

## 6. Component Recipes (exact classes)

### Terminal window (hero, projects, experience)
Wrapper: `retro-border bg-card retro-shadow overflow-hidden w-full flex flex-col relative`.
Chrome bar: `bg-accent/5 border-b border-accent/10 px-4 py-2 flex justify-between items-center text-[10px] font-mono tracking-wider text-accent/50 font-black` — traffic lights are accent circles `w-2.5 h-2.5 rounded-full bg-accent` / `bg-accent/40` / `bg-accent/20`; center title like `root@dg-os: ~/workspace/projects-repository`. Hero uses stronger chrome: `bg-accent/10 border-b-2 border-accent px-6 py-3` and lights `w-3.5 h-3.5`.
Status bar (bottom): `bg-accent text-white px-4 py-1.5 flex justify-between font-mono text-[9px] uppercase tracking-[0.3em]` with inverted chip `bg-white text-accent px-2 py-0.5 font-black`.

### Module card (About bento)
`retro-border bg-card retro-shadow-sm flex flex-col relative` + module header `bg-accent/10 border-b border-accent/20 px-4 py-2 flex items-center justify-between text-[10px] font-mono tracking-wider text-accent font-bold` with bracketed label `[ MODULE: PRIMARY_BIO ]` + right-side meta (`PID: 001`).

### Section title
`SectionTitle` terminal variant: `text-xl md:text-2xl font-black mb-6 md:mb-8 text-accent uppercase tracking-wider flex items-center gap-2`, optional number `text-xs opacity-40` (e.g. `03.` + `projects_repo`). Alternative header block: title + subtitle `text-xs md:text-sm text-foreground/60 tracking-widest uppercase`, wrapped by `border-b-2 border-accent/20 pb-4`.

### Buttons / action links
Base: `retro-border border-accent/30 bg-accent/5 hover:bg-accent hover:text-white px-4 py-2.5 font-mono text-xs font-bold tracking-wider flex items-center justify-center gap-2 transition-all cursor-pointer`.
Small ghost (header toggle): `border border-accent/30 px-2 py-1 text-[9px] md:text-[10px] font-black tracking-wider hover:bg-accent hover:text-white transition-all`.
Disabled: same box, `opacity-40`, no hover. Danger/locked: `border-red-500/15 bg-red-500/5 text-red-500/60`.
**Hover rule everywhere: invert to solid accent + white text.**

### Nav link
`text-foreground hover:text-accent transition-colors relative group font-mono text-sm uppercase` with prompt prefix `>` at `opacity-40 group-hover:opacity-100`. Logo/home: `font-mono font-bold text-accent hover:bg-accent hover:text-white px-2 py-1` + blinking `terminal-cursor`.

### List item (file manager, active state)
Inactive: `font-mono text-xs py-3 px-3 border-b border-accent/5 hover:bg-accent/10 text-foreground/85 cursor-pointer`.
Active: `bg-accent text-white font-black border-l-4 border-white` + `►` marker. Fake metadata (`-rwxr-xr-x`, sizes) at `opacity-30..40`.

### Tags / chips
Tech tag: `text-[9px] font-bold border border-accent/20 px-2 py-0.5 text-accent bg-accent/5`.
Status chip: `px-1.5 py-0.5 font-bold uppercase rounded-sm border border-accent/20 text-accent bg-accent/5` (active: `border-white/50 text-white bg-white/10`).

### Key-value rows (user manifest, env vars)
`flex justify-between items-center text-xs border-b border-accent/10 pb-1.5 font-mono` — key `opacity-40..50 uppercase`, value `text-accent font-black`. Link value: `text-accent hover:text-card hover:bg-accent px-1 transition-colors font-black` + `↗` at `text-[8px] opacity-50`.

### Skill bar (terminal variant)
Label row `flex justify-between mb-2 text-xs md:text-sm font-bold tracking-widest uppercase` (value in accent); track `h-2 border border-accent/20 p-0.5`; fill `h-full bg-accent shadow-[0_0_15px_var(--accent)]` animated width 0 → level%.

### Social links (terminal variant)
`flex items-center gap-2 border border-accent/20 bg-accent/5 px-4 py-2 hover:bg-accent hover:text-white transition-all font-mono text-xs uppercase` + 16px icon.

### Contact banner
Outer `border border-accent/30 bg-accent/5 p-1`; title strip `bg-accent text-white p-2 font-black uppercase text-xs tracking-widest`; body `p-6 md:p-12 space-y-10`; footer microcopy `text-[8px] md:text-[10px] opacity-30 uppercase tracking-[0.4em]`.

### Footer
`mt-20 py-8 border-t-2 border-accent/20 font-mono text-[10px] md:text-xs text-accent/60 uppercase tracking-widest` with pulsing dot `w-2 h-2 bg-accent/40 rounded-full animate-pulse`.

### Avatar / photo panel
Circular photo `w-32 h-32 md:w-40 md:h-40 rounded-full border-2 border-accent/60` (desktop starts `/20` + `grayscale`, hover → colored/`/60` over `duration-500..700`); two spinning ring borders `animate-[spin_15s_linear_infinite]` and `animate-[spin_20s_linear_infinite_reverse]`; side panel `border-l-2 border-accent bg-accent/5`.

## 7. Interaction & Motion

- Library: framer-motion (+ gsap fade for mode switch). **Entrances are fade/slide only — no springs, no bounce, no overshoot.**
  - Standard entrance: `initial={{ opacity: 0, y: 10..20 }}` → `animate/whileInView={{ opacity: 1, y: 0 }}`, `transition={{ duration: 0.3–0.5 }}`, `viewport={{ once: true }}`; stagger with `delay: i * 0.1–0.2`.
  - Content swap: `AnimatePresence mode="wait"`, fade + y±10, `duration: 0.15–0.3`.
- Hover feedback: color inversion + `transition-colors`/`transition-all`; retro cards may `hover:-translate-y-1 active:translate-y-0`.
- Ambient motion allowed: `animate-pulse` on status dots/cursors, slow ring spins, scanline overlay, typing effect (~40ms/char) with blinking block cursor.
- Selection: `selection:bg-accent selection:text-white`.
- Keyboard support on interactive lists (↑/↓ navigate, Enter open, G github) + auto-cycle 8s paused on hover.

## 8. Dark Mode & Theming

- `next-themes` with `attribute="class"`, `defaultTheme="system"` — `.dark` on `<html>`.
- Route themes: wrapper class per section (`theme-dev`) sets the 6 vars; `.dark .theme-dev` overrides with dark palette. Palette switcher writes inline vars on the themed element (persisted in `localStorage`).
- Components never hardcode colors — always the token classes, so palette swaps are free.

## 9. Copy & Voice

- Terminal narrative everywhere: prompts `>`, `$`, paths `root@dg-os: ~/...`, commands (`whoami`, `git branch`), `// comments`, `# HEADINGS`, `[ OK ]`, `[+]` bullets, `PID`, `MODULE:`, `SYS_BUILD`.
- Labels in SCREAMING_SNAKE or snake_case; pt-BR content, en-US system labels.
- Numbers/decorations are fake-precise (`CPU: 2%`, `-rwxr-xr-x`, `4.2K`) — flavor, not data.

## 10. Do / Don't

- DO keep corners square, borders 2px, shadows offset-flat in `--shadow`.
- DO use accent-opacity steps (`/5 /10 /20 /30 /40 /50`) for hierarchy instead of gray scales.
- DO uppercase + wide tracking for anything label-like.
- DON'T introduce new colors, gradients, blur shadows, or rounded corners.
- DON'T use bouncy/spring entrance animations — fade/slide with ease-out only.
- DON'T break the monospace: JetBrains Mono is the only font.
