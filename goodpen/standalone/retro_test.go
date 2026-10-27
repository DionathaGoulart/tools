package main

import (
	"io"
	"os"
	"strings"
	"testing"
)

func retroTeste(largura, altura *int, tty bool) *Retro {
	r := NewRetro(52)
	r.TTY = tty
	r.Plano = !tty
	r.Cor = false
	r.tamanho = func() (int, int) { return *largura, *altura }
	r.AtualizarTamanho()
	return r
}

func capturar(t *testing.T, fn func()) string {
	t.Helper()
	antigo := os.Stdout
	leitura, escrita, err := os.Pipe()
	if err != nil {
		t.Fatal(err)
	}
	os.Stdout = escrita
	fn()
	_ = escrita.Close()
	os.Stdout = antigo
	saida, err := io.ReadAll(leitura)
	if err != nil {
		t.Fatal(err)
	}
	_ = leitura.Close()
	return string(saida)
}

func TestRetroAtualizaMesmoObjeto(t *testing.T) {
	largura, altura := 80, 24
	r := retroTeste(&largura, &altura, true)
	if r.Caixa == false || r.bw != 52 {
		t.Fatalf("geometria inicial: caixa=%v largura=%d", r.Caixa, r.bw)
	}
	largura, altura = 8, 6
	r.AtualizarTamanho()
	if r.Caixa || r.bw != 7 || r.cf != 3 {
		t.Fatalf("geometria apos resize: caixa=%v largura=%d conteudo=%d", r.Caixa, r.bw, r.cf)
	}
}

func TestCortarEQuebrarANSIUnicode(t *testing.T) {
	texto := "\033[31m日本a\u0301bc\033[0m"
	cortado := Cortar(texto, 4)
	if Largura(cortado) > 4 || !strings.Contains(cortado, "\033[0m") {
		t.Fatalf("corte ANSI invalido: %q (%d)", cortado, Largura(cortado))
	}
	for _, linha := range Quebrar(texto, 3) {
		if Largura(linha) > 3 {
			t.Fatalf("linha transbordou: %q (%d)", linha, Largura(linha))
		}
	}
	linhas := Quebrar("\033[31mABCD\033[0m", 2)
	if len(linhas) != 2 || !strings.HasPrefix(linhas[1], "\033[31m") || !strings.HasSuffix(linhas[0], "\033[0m") {
		t.Fatalf("estado ANSI perdido entre linhas: %#v", linhas)
	}
}

func TestNoColorVazioDesativaCor(t *testing.T) {
	t.Setenv("NO_COLOR", "")
	if !modoPlano(true) {
		t.Fatal("NO_COLOR presente e vazio deve desativar cores")
	}
}

func TestMenuIgnoraControles(t *testing.T) {
	for _, b := range []byte{27, '[', 0} {
		if comandoMenuByte(b) {
			t.Fatalf("controle entrou no menu: %q", b)
		}
	}
	if !comandoMenuByte('9') || !comandoMenuByte('w') {
		t.Fatal("comando valido foi descartado")
	}
}

func TestRenderizadoresRespeitamLargura(t *testing.T) {
	for _, largura := range []int{1, 8, 20, 40, 46, 80, 160} {
		t.Run("largura", func(t *testing.T) {
			w, h := largura, 40
			r := retroTeste(&w, &h, true)
			saida := capturar(t, func() {
				r.Modulo("teste_日本", "metadado muito longo")
				r.Secao("secao longa")
				r.KV("CHAVE_LONGA", "valor 日本 completo")
				r.Regra()
				r.Item("►", "item com texto longo 日本", "meta longa")
				r.Ok("resultado longo")
				r.Erro("erro muito longo 日本")
				r.Aviso("aviso", "texto longo")
				r.Proximo("comando muito longo 日本", "proximo passo:")
				r.Janela("titulo longo 日本", []string{"corpo muito longo 日本 a\u0301bc"}, "META LONGA", "rodape longo")
				r.CatalogoTemas()
			})
			for _, linha := range strings.Split(strings.TrimSuffix(saida, "\n"), "\n") {
				if Largura(linha) > largura {
					t.Fatalf("largura %d transbordou: %q (%d)", largura, linha, Largura(linha))
				}
			}
		})
	}
}

func TestPipePreservaTexto(t *testing.T) {
	w, h := 8, 4
	r := retroTeste(&w, &h, false)
	const texto = "texto 日本 completo a\u0301bc"
	saida := capturar(t, func() {
		r.Texto(texto)
		r.Janela("titulo", []string{texto}, "meta", texto)
	})
	if strings.Count(saida, texto) < 2 {
		t.Fatalf("pipe perdeu dados: %q", saida)
	}
	if strings.Contains(saida, "\033[") {
		t.Fatalf("pipe contem ANSI: %q", saida)
	}
}

func TestMenuCompactoPaginado(t *testing.T) {
	antigo := ui
	defer func() { ui = antigo }()
	w, h := 20, 11
	ui = retroTeste(&w, &h, true)
	var saida strings.Builder
	for pagina := 0; pagina < 2; pagina++ {
		saida.WriteString(capturar(t, func() { drawMenu(0, pagina) }))
	}
	for _, acao := range []string{"[1]", "[2]", "[3]", "[4]", "[5]", "[6]", "[7]", "[8]", "[9]", "[W]"} {
		if !strings.Contains(saida.String(), acao) {
			t.Fatalf("acao ausente no menu compacto: %s", acao)
		}
	}
	for _, linha := range strings.Split(strings.TrimSuffix(saida.String(), "\n"), "\n") {
		if Largura(linha) > w {
			t.Fatalf("menu transbordou: %q (%d)", linha, Largura(linha))
		}
	}
}

func TestMenuCabeNaAlturaReal(t *testing.T) {
	antigo := ui
	defer func() { ui = antigo }()
	for _, caso := range []struct{ largura, altura int }{{1, 4}, {8, 8}, {80, 11}} {
		w, h := caso.largura, caso.altura
		ui = retroTeste(&w, &h, true)
		quadro, paginas := menuFrame(0, 0)
		if len(quadro)+1 > h { // a linha do prompt tambem ocupa tela
			t.Fatalf("%dx%d: %d linhas mais prompt", w, h, len(quadro))
		}
		if paginas < 1 {
			t.Fatalf("%dx%d: pagina invalida", w, h)
		}
		for _, linha := range quadro {
			if Largura(linha) > w {
				t.Fatalf("%dx%d transbordou: %q", w, h, linha)
			}
		}
		if Largura(menuPrompt("q")) > w {
			t.Fatalf("%dx%d: prompt transbordou", w, h)
		}
	}
}

// Exercitado por script(1) na verificacao manual; nao bloqueia a suite comum.
func TestMenuPTYRedesenhaSemEnter(t *testing.T) {
	if os.Getenv("COFRE_PTY_MENU_TEST") != "1" {
		t.Skip("requer PTY")
	}
	antigo := ui
	defer func() { ui = antigo }()
	ui = NewRetro(52) // o harness PTY altera o tamanho real com TIOCSWINSZ.
	if !ui.TTY {
		t.Skip("requer stdout PTY")
	}
	if os.Getenv("COFRE_PTY_MENU_PLANO") == "1" {
		ui.Plano = true
	}
	resposta, _ := leMenu(0, 0)
	if resposta != "q" {
		t.Fatalf("entrada do menu perdida apos resize: %q", resposta)
	}
}
