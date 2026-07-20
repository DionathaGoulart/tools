package main

// retro.go — retro-terminal theme for the cofre CLI.
//
// Self-contained port of lib/retro.py (this repo has no shared Go module), so
// the API shape mirrors it 1:1: accent-only palette derived by alpha-blending
// the accent over the background, square corners, heavy borders, flat offset
// shadow, uppercase labels. NO_COLOR and non-tty output degrade to plain text.
//
// Theme comes from COFRE_TEMA, then RETRO_TEMA, falling back to vault-gold.
// See .harness/styleguide-terminal.md.

import (
	"fmt"
	"os"
	"regexp"
	"strings"
	"unicode"

	"golang.org/x/term"
)

const envPrefix = "COFRE"

// tema is a palette triple — background, foreground, accent (hex, no '#').
type tema struct{ bg, fg, acc string }

var temas = map[string]tema{
	"vault-gold":     {"111111", "e0e0e0", "c8a96e"},
	"noir-rose":      {"121212", "f2efe7", "e8729a"},
	"midnight-ember": {"0d1117", "e0ffe0", "ff6b45"},
	"cyber-teal":     {"0a0f14", "e0f4ff", "00e5ff"},
	"velvet-purple":  {"0e0a14", "ede0ff", "b47aff"},
	"abyss-frost":    {"e4f0f6", "0f172a", "0a0f1e"},
	"crimson-chalk":  {"f2efe7", "1a0a0a", "dc143c"},
	"forest-mist":    {"eef4ee", "1a2e1a", "2d6a2d"},
	"sand-dusk":      {"f5f0e8", "2a1a0a", "b56a30"},
}

// temasOrdem keeps the catalog deterministic (Go maps are unordered).
var temasOrdem = []string{
	"vault-gold", "noir-rose", "midnight-ember", "cyber-teal", "velvet-purple",
	"abyss-frost", "crimson-chalk", "forest-mist", "sand-dusk",
}

const temaPadrao = "vault-gold"

var reANSI = regexp.MustCompile("\033\\[[0-9;]*m")

// wideRanges lists the East Asian Wide / Fullwidth blocks that occupy two cells.
var wideRanges = [][2]rune{
	{0x1100, 0x115F}, {0x2E80, 0x303E}, {0x3041, 0x33FF}, {0x3400, 0x4DBF},
	{0x4E00, 0x9FFF}, {0xA000, 0xA4CF}, {0xAC00, 0xD7A3}, {0xF900, 0xFAFF},
	{0xFE10, 0xFE19}, {0xFE30, 0xFE6F}, {0xFF00, 0xFF60}, {0xFFE0, 0xFFE6},
	{0x1F300, 0x1F64F}, {0x1F900, 0x1F9FF}, {0x20000, 0x2FFFD}, {0x30000, 0x3FFFD},
}

func runeLargo(r rune) bool {
	for _, faixa := range wideRanges {
		if r >= faixa[0] && r <= faixa[1] {
			return true
		}
	}
	return false
}

// Largura is the visible width of a string: ANSI-free, wide chars count as 2.
func Largura(texto string) int {
	total := 0
	for _, r := range reANSI.ReplaceAllString(texto, "") {
		if unicode.Is(unicode.Mn, r) || unicode.Is(unicode.Me, r) {
			continue
		}
		if runeLargo(r) {
			total += 2
		} else {
			total++
		}
	}
	return total
}

func hexRGB(h string) (int, int, int) {
	var r, g, b int
	fmt.Sscanf(h, "%02x%02x%02x", &r, &g, &b)
	return r, g, b
}

// Mix blends hex a over hex b at alfa% — the style guide's opacity steps.
func Mix(a, b string, alfa int) string {
	ar, ag, ab := hexRGB(a)
	br, bg, bb := hexRGB(b)
	return fmt.Sprintf("%02x%02x%02x",
		(ar*alfa+br*(100-alfa))/100,
		(ag*alfa+bg*(100-alfa))/100,
		(ab*alfa+bb*(100-alfa))/100)
}

// Retro holds the resolved tokens plus the component recipes.
type Retro struct {
	Tema   string
	EnvVar string

	bg, fgHex, acc string

	TTY       bool
	Cor       bool
	Truecolor bool

	cols  int
	bw    int  // box width
	cf    int  // usable content width inside the box
	Caixa bool // draw boxes at all

	RESET, BOLD, DIM                 string
	ACC, ACC70, ACC50, ACC30, ACC15  string
	FG, FG70, FG40, INV, OK_, ALERTA string
}

// ui is the process-wide theme instance.
var ui = NewRetro(52)

func NewRetro(larguraCaixa int) *Retro {
	nome := os.Getenv(envPrefix + "_TEMA")
	if nome == "" {
		nome = os.Getenv("RETRO_TEMA")
	}
	if _, existe := temas[nome]; !existe {
		nome = temaPadrao
	}
	t := temas[nome]

	r := &Retro{
		Tema:   nome,
		EnvVar: envPrefix + "_TEMA",
		bg:     t.bg,
		fgHex:  t.fg,
		acc:    t.acc,
	}

	r.TTY = term.IsTerminal(int(os.Stdout.Fd()))
	r.Cor = r.TTY && os.Getenv("NO_COLOR") == ""
	ct := os.Getenv("COLORTERM")
	r.Truecolor = r.Cor && (strings.Contains(ct, "truecolor") || strings.Contains(ct, "24bit"))

	r.cols = 80
	if w, _, err := term.GetSize(int(os.Stdout.Fd())); err == nil && w > 0 {
		r.cols = w
	}
	r.bw = larguraCaixa
	if lim := r.cols - 3; lim < r.bw {
		r.bw = lim
	}
	if r.bw < 20 {
		r.bw = 20
	}
	r.Caixa = r.TTY && r.bw >= 46
	r.cf = r.bw - 4

	r.tokens()
	return r
}

func (r *Retro) fgSeq(h string) string {
	red, g, b := hexRGB(h)
	return fmt.Sprintf("\033[38;2;%d;%d;%dm", red, g, b)
}

func (r *Retro) bgSeq(h string) string {
	red, g, b := hexRGB(h)
	return fmt.Sprintf("\033[48;2;%d;%d;%dm", red, g, b)
}

func (r *Retro) tokens() {
	if !r.Cor {
		return // every token stays "" — layout must survive escape-free
	}
	r.RESET, r.BOLD, r.DIM = "\033[0m", "\033[1m", "\033[2m"
	if r.Truecolor {
		r.ACC = r.fgSeq(r.acc)
		r.ACC70 = r.fgSeq(Mix(r.acc, r.bg, 70))
		r.ACC50 = r.fgSeq(Mix(r.acc, r.bg, 50))
		r.ACC30 = r.fgSeq(Mix(r.acc, r.bg, 30))
		r.ACC15 = r.fgSeq(Mix(r.acc, r.bg, 18))
		r.FG = r.fgSeq(r.fgHex)
		r.FG70 = r.fgSeq(Mix(r.fgHex, r.bg, 70))
		r.FG40 = r.fgSeq(Mix(r.fgHex, r.bg, 40))
		r.INV = r.bgSeq(r.acc) + r.fgSeq(r.bg)
		r.OK_ = r.fgSeq("3fb950")
		r.ALERTA = r.fgSeq("e5534b")
		return
	}
	r.ACC = "\033[1;33m"
	r.ACC70, r.ACC50 = "\033[33m", "\033[33m"
	r.ACC30, r.ACC15 = "\033[2;33m", "\033[2;33m"
	r.FG, r.FG70 = "\033[0m", "\033[0m"
	r.FG40 = "\033[2m"
	r.INV = "\033[7;33m"
	r.OK_ = "\033[1;32m"
	r.ALERTA = "\033[1;31m"
}

// ── inline helpers ─────────────────────────────────────────────────────

func (r *Retro) Acento(texto string) string  { return r.ACC + texto + r.RESET }
func (r *Retro) Forte(texto string) string   { return r.ACC + r.BOLD + texto + r.RESET }
func (r *Retro) Apagado(texto string) string { return r.FG40 + texto + r.RESET }

// Chip is a bracketed uppercase tag: [SPOILER].
func (r *Retro) Chip(texto string) string {
	return r.ACC30 + "[" + r.RESET + r.ACC + strings.ToUpper(texto) + r.RESET + r.ACC30 + "]" + r.RESET
}

func (r *Retro) Invertido(texto string) string {
	return r.INV + r.BOLD + " " + strings.ToUpper(texto) + " " + r.RESET
}

// Preenche pads a styled string to n visible columns.
func (r *Retro) Preenche(texto string, n int) string {
	if pad := n - Largura(texto); pad > 0 {
		return texto + strings.Repeat(" ", pad)
	}
	return texto
}

// ── flat blocks ────────────────────────────────────────────────────────

// Modulo prints the [ MODULE: X ] header every command output opens with.
func (r *Retro) Modulo(rotulo, meta string) {
	linha := "\n  " + r.ACC + r.BOLD + "[ MODULE: " + strings.ToUpper(rotulo) + " ]" + r.RESET
	if meta != "" {
		linha += "  " + r.ACC30 + strings.ToUpper(meta) + r.RESET
	}
	fmt.Println(linha + "\n")
}

// Secao prints a "# HEADING" sub-section label.
func (r *Retro) Secao(rotulo string) {
	fmt.Println("  " + r.ACC + "# " + strings.ToUpper(rotulo) + r.RESET)
}

func (r *Retro) pontos() int {
	if r.cols > 60 {
		return 44
	}
	if n := r.cols - 12; n > 20 {
		return n
	}
	return 20
}

// SKV renders a key-value row (dim key, dot leader, accent-bold value).
func (r *Retro) SKV(chave, valor string) string {
	n := r.pontos() - Largura(chave) - Largura(valor)
	if n < 2 {
		n = 2
	}
	return r.FG40 + chave + r.RESET + " " +
		r.ACC15 + strings.Repeat("·", n) + r.RESET + " " +
		r.ACC + r.BOLD + valor + r.RESET
}

// KV prints a key-value row. Replaces every "label: value" line.
func (r *Retro) KV(chave, valor string) { fmt.Println("  " + r.SKV(chave, valor)) }

func (r *Retro) Regra() {
	fmt.Println("  " + r.ACC15 + strings.Repeat("─", r.pontos()) + r.RESET)
}

// SItem renders a list row: accent marker, foreground text, dim trailing meta.
func (r *Retro) SItem(marca, texto, meta string) string {
	linha := r.ACC + marca + r.RESET + " " + r.FG70 + texto + r.RESET
	if meta != "" {
		linha += "  " + r.FG40 + meta + r.RESET
	}
	return linha
}

func (r *Retro) Item(marca, texto, meta string) {
	fmt.Println("  " + r.SItem(marca, texto, meta))
}

func (r *Retro) Ok(texto string) {
	fmt.Println("  " + r.OK_ + "[ OK ]" + r.RESET + " " + r.ACC + r.BOLD + strings.ToUpper(texto) + r.RESET)
}

func (r *Retro) Erro(texto string) {
	fmt.Println("  " + r.ALERTA + "[ ERRO ]" + r.RESET + " " + texto)
}

// Aviso prints a neutral bracketed status: [ VAZIO ], [ ABORTADO ], …
func (r *Retro) Aviso(etiqueta, texto string) {
	linha := "  " + r.FG40 + "[ " + strings.ToUpper(etiqueta) + " ]" + r.RESET
	if texto != "" {
		linha += " " + texto
	}
	fmt.Println(linha)
}

// Proximo prints the "> proximo passo:  comando" hint.
func (r *Retro) Proximo(comando, prefixo string) {
	if prefixo == "" {
		prefixo = "proximo passo:"
	}
	fmt.Println("  " + r.ACC30 + ">" + r.RESET + " " + prefixo + "  " + r.ACC + r.BOLD + comando + r.RESET)
}

// Barra renders an ASCII progress bar: filled accent, track accent/18, percent.
func (r *Retro) Barra(feito, total, larg int) string {
	if total < 1 {
		total = 1
	}
	if larg < 1 {
		larg = 24
	}
	n := feito * larg / total
	if n > larg {
		n = larg
	}
	if n < 0 {
		n = 0
	}
	pct := feito * 100 / total
	return fmt.Sprintf("%s%s%s%s%s  %s%s%3d%%%s",
		r.ACC, strings.Repeat("█", n),
		r.ACC15, strings.Repeat("▒", larg-n), r.RESET,
		r.ACC, r.BOLD, pct, r.RESET)
}

// ── box (terminal window recipe) ───────────────────────────────────────

func (r *Retro) Topo() {
	fmt.Println(r.ACC + "┏" + strings.Repeat("━", r.bw-2) + "┓" + r.RESET)
}

func (r *Retro) Sep() {
	fmt.Println(r.ACC + "┠" + strings.Repeat("─", r.bw-2) + "┨" + r.RESET + r.ACC15 + "▒" + r.RESET)
}

func (r *Retro) Base() {
	fmt.Println(r.ACC + "┗" + strings.Repeat("━", r.bw-2) + "┛" + r.RESET + r.ACC15 + "▒" + r.RESET)
}

func (r *Retro) Sombra() {
	fmt.Println(" " + r.ACC15 + strings.Repeat("▒", r.bw) + r.RESET)
}

func (r *Retro) Linha(conteudo string) {
	pad := r.cf - Largura(conteudo)
	if pad < 0 {
		pad = 0
	}
	fmt.Println(r.ACC + "┃" + r.RESET + " " + conteudo + strings.Repeat(" ", pad) + " " +
		r.ACC + "┃" + r.RESET + r.ACC15 + "▒" + r.RESET)
}

// Chrome is the window title bar: three accent dots, path title, right meta.
func (r *Retro) Chrome(titulo, meta string) {
	pad := r.cf - 7 - Largura(titulo) - Largura(meta)
	if pad < 1 {
		pad = 1
	}
	fmt.Println(r.ACC + "┃" + r.RESET + " " +
		r.ACC + "●" + r.RESET + " " + r.ACC50 + "●" + r.RESET + " " + r.ACC30 + "●" + r.RESET + "  " +
		r.ACC50 + titulo + r.RESET + strings.Repeat(" ", pad) +
		r.ACC30 + meta + r.RESET + " " + r.ACC + "┃" + r.RESET + r.ACC15 + "▒" + r.RESET)
}

// Status is the inverted status bar at the bottom of a window.
func (r *Retro) Status(esquerda, direita string) {
	pad := r.cf - Largura(esquerda) - Largura(direita)
	if pad < 1 {
		pad = 1
	}
	fmt.Println(r.ACC + "┃" + r.INV + r.BOLD + " " + esquerda + strings.Repeat(" ", pad) + direita + " " +
		r.RESET + r.ACC + "┃" + r.RESET + r.ACC15 + "▒" + r.RESET)
}

// Janela draws a full terminal window: chrome + body + status bar + shadow.
func (r *Retro) Janela(titulo string, linhas []string, meta, rodape string) {
	if !r.Caixa {
		for _, l := range linhas {
			fmt.Println("  " + l)
		}
		if rodape != "" {
			fmt.Println("  " + rodape)
		}
		return
	}
	r.Topo()
	r.Chrome(titulo, meta)
	r.Sep()
	for _, l := range linhas {
		r.Linha(l)
	}
	if rodape != "" {
		r.Sep()
		r.Status(rodape, "")
	}
	r.Base()
	r.Sombra()
}

// ── theme catalog ──────────────────────────────────────────────────────

func (r *Retro) CatalogoTemas() {
	r.Modulo("theme_catalog", "")
	for _, nome := range temasOrdem {
		t := temas[nome]
		marca := "  "
		if nome == r.Tema {
			marca = "► "
		}
		swatch := "[#" + t.acc + "]"
		if r.Truecolor {
			swatch = r.bgSeq(t.acc) + "    " + r.RESET +
				r.bgSeq(t.fg) + "  " + r.RESET +
				r.bgSeq(t.bg) + "  " + r.RESET
		}
		fmt.Printf("  %s%s%s%-16s %s  %s#%s%s\n",
			r.ACC, marca, r.RESET, nome, swatch, r.ACC15, t.acc, r.RESET)
	}
	fmt.Printf("\n  %sexport %s=<nome>%s\n\n", r.FG40, r.EnvVar, r.RESET)
}
