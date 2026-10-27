"""Tests for lib/retro.py — the shared retro-terminal theme.

Run from the repo root:  python3 -m unittest discover -s tests
"""

import os
import sys
import unittest
from io import StringIO
from unittest.mock import patch

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib")
)
from retro import Retro, TerminalParser, TEMAS, TEMA_PADRAO, TEMAS_GOOD, cortar, quebrar, largura, mix  # noqa: E402


class TestLargura(unittest.TestCase):
    def test_ignora_sequencias_ansi(self):
        self.assertEqual(largura("\033[31mabc\033[0m"), 3)

    def test_caracteres_largos_contam_dois(self):
        self.assertEqual(largura("日本"), 4)

    def test_combinantes_contam_zero(self):
        # "a" + acento combinante = 1 coluna visível
        self.assertEqual(largura("á"), 1)

    def test_string_vazia(self):
        self.assertEqual(largura(""), 0)

    def test_corta_ansi_sem_separar_cjk_ou_acento(self):
        texto = "\033[31m日本ábc\033[0m"
        resultado = cortar(texto, 5)
        self.assertLessEqual(largura(resultado), 5)
        self.assertIn("\033[0m", resultado)
        self.assertNotIn("a\u0301", cortar(texto, 4))

    def test_quebra_preserva_todo_texto(self):
        texto = "abc 日本 ábc"
        self.assertEqual("".join(quebrar(texto, 3)), texto)
        self.assertTrue(
            all(largura(linha) <= 3 or linha == "日" for linha in quebrar(texto, 3))
        )

    def test_quebra_reaplica_cor_e_fecha_estilo_em_cada_linha(self):
        self.assertEqual(
            quebrar("\033[31mabcdef\033[0m", 3),
            ["\033[31mabc\033[0m", "\033[31mdef\033[0m"],
        )


class TestMix(unittest.TestCase):
    def test_100_por_cento_e_a_cor_a(self):
        self.assertEqual(mix("ffffff", "000000", 100), "ffffff")

    def test_0_por_cento_e_a_cor_b(self):
        self.assertEqual(mix("ffffff", "000000", 0), "000000")

    def test_meio_a_meio(self):
        self.assertEqual(mix("ffffff", "000000", 50), "7f7f7f")


class TestTema(unittest.TestCase):
    def test_nome_invalido_cai_no_padrao(self):
        ui = Retro(tema="nao-existe-mesmo")
        self.assertEqual(ui.tema, TEMA_PADRAO)

    def test_nome_valido_e_respeitado(self):
        alvo = "cyber-teal"
        self.assertIn(alvo, TEMAS)  # sanity: o tema existe no catálogo
        ui = Retro(tema=alvo)
        self.assertEqual(ui.tema, alvo)

    def test_barra_mostra_porcentagem(self):
        ui = Retro(tema="vault-gold")
        self.assertIn("50%", ui.barra(1, 2))

    def test_barra_nunca_estoura_com_total_zero(self):
        ui = Retro(tema="vault-gold")
        # total 0 não pode dividir por zero
        self.assertIn("%", ui.barra(3, 0))


class _Tty(StringIO):
    def isatty(self):
        return True


class TestResponsivo(unittest.TestCase):
    def tamanho(self, colunas, linhas=24):
        return patch(
            "retro.shutil.get_terminal_size",
            return_value=os.terminal_size((colunas, linhas)),
        )

    def test_mesma_instancia_acompanha_resize(self):
        with self.tamanho(80):
            ui = Retro(largura_caixa=52)
        self.assertEqual(ui.cols, 80)
        with self.tamanho(8, 5):
            self.assertEqual(ui.atualizar_tamanho(), (8, 5))
        self.assertEqual(ui.bw, 7)
        self.assertEqual(ui.cf, 3)
        self.assertFalse(ui.caixa)

    def test_override_plano_persiste_ao_renderizar(self):
        saida = _Tty()
        with self.tamanho(80), patch("retro.sys.stdout", saida):
            ui = Retro()
            ui.permitir_caixa = False
            ui.janela("teste", ["conteúdo"])
        self.assertFalse(ui.caixa)
        self.assertNotIn("┏", saida.getvalue())

    def test_terminal_baixo_remove_moldura(self):
        saida = _Tty()
        with self.tamanho(80, 4), patch("retro.sys.stdout", saida):
            Retro().janela("teste", ["conteúdo"], rodape="sair")
        self.assertNotIn("┏", saida.getvalue())

    def test_ajuda_argparse_cabe_em_terminal_estreito(self):
        saida = _Tty()
        with self.tamanho(8), patch("retro.sys.stdout", saida):
            parser = TerminalParser(prog="teste")
            parser.add_argument("arquivo")
            parser.print_help()
        self.assertTrue(all(largura(line) <= 8 for line in saida.getvalue().splitlines()))

    def test_tamanho_real_tem_prioridade_e_funciona_em_captura(self):
        saida = _Tty()
        saida.fileno = lambda: 42
        with self.tamanho(200, 90), patch("retro.sys.stdout", saida), patch(
            "retro.os.get_terminal_size", return_value=os.terminal_size((28, 8))
        ):
            ui = Retro()
            with patch("retro.sys.stdout", StringIO()):
                self.assertEqual(ui.atualizar_tamanho(), (28, 8))

    def test_term_dumb_e_no_color_vazio_desativam_ansi(self):
        for env in ({"TERM": "dumb"}, {"NO_COLOR": ""}):
            with patch.dict(os.environ, env, clear=True), patch("retro.sys.stdout", _Tty()):
                self.assertFalse(Retro().cor)

    def test_pipe_nao_substitui_cjk_mesmo_em_uma_coluna(self):
        with self.tamanho(1), patch("retro.sys.stdout", StringIO()):
            self.assertEqual(Retro().quebrar("日本\ntexto completo", 1), ["日本", "texto completo"])

    def test_helpers_nao_estouram_em_larguras_extremas(self):
        for colunas in (1, 8, 20, 40, 80, 160):
            saida = _Tty()
            with self.subTest(colunas=colunas), self.tamanho(colunas), patch(
                "retro.sys.stdout", saida
            ):
                ui = Retro(largura_caixa=52)
                ui.modulo("monitor_muito_longo", "metadado muito longo")
                ui.kv("CHAVE_LONGA", "valor 日本 á muito longo")
                ui.item("►", "texto de lista bastante longo", "metadado")
                ui.janela(
                    "titulo longo",
                    ["conteúdo 日本 á bastante longo"],
                    "meta longa",
                    "rodapé longo",
                )
            for linha in saida.getvalue().splitlines():
                self.assertLessEqual(largura(linha), colunas)

    def test_caixa_e_skin_good_respeitam_largura(self):
        saida = _Tty()
        with self.tamanho(46), patch("retro.sys.stdout", saida):
            ui = Retro(skin="good", largura_caixa=110)
            ui.janela("titulo " * 20, ["linha " * 30], "meta " * 20, "rodape " * 20)
        self.assertTrue(saida.getvalue())
        self.assertTrue(
            all(largura(linha) <= 46 for linha in saida.getvalue().splitlines())
        )

    def test_pipe_preserva_texto_sem_ansi(self):
        saida = StringIO()
        with self.tamanho(1), patch("retro.sys.stdout", saida):
            ui = Retro()
            ui.texto("texto 日本 completo")
            ui.janela("x", ["linha inteira 日本"], "", "")
        self.assertIn("texto 日本 completo", saida.getvalue())
        self.assertIn("linha inteira 日本", saida.getvalue())
        self.assertNotIn("\033", saida.getvalue())


class TestSkinGood(unittest.TestCase):
    def test_padrao_e_black(self):
        ui = Retro(skin="good")
        self.assertEqual(ui.tema, "black")
        self.assertEqual((ui.bg, ui.acc), ("000000", "fbee23"))

    def test_yellow_inverte_o_par(self):
        ui = Retro(skin="good", tema="yellow")
        self.assertEqual((ui.bg, ui.fg_hex, ui.acc), ("fbee23", "000000", "000000"))

    def test_paleta_legada_cai_no_black(self):
        self.assertEqual(Retro(skin="good", tema="vault-gold").tema, "black")

    def test_catalogo_so_tem_o_par_da_marca(self):
        self.assertEqual(set(Retro(skin="good").temas), set(TEMAS_GOOD))

    def test_barra_sem_pontilhado(self):
        self.assertNotIn("▒", Retro(skin="good").barra(1, 4))

    def test_sem_skin_nada_muda(self):
        ui = Retro(tema="vault-gold")
        self.assertFalse(ui.good)
        self.assertIn("▒", ui.barra(1, 4))


if __name__ == "__main__":
    unittest.main()
