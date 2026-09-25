"""Tests for lib/retro.py — the shared retro-terminal theme.

Run from the repo root:  python3 -m unittest discover -s tests
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from retro import Retro, TEMAS, TEMA_PADRAO, TEMAS_GOOD, largura, mix  # noqa: E402


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
