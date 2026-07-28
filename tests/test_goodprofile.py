"""Tests for images/goodprofile/goodprofile — pure-python ops, no decoder.

Test images are built by hand as RGBA buffers with solid colours, so the
assertions are immune to which resampling path (Pillow or pure python) runs.
"""

import importlib.machinery
import importlib.util
import os
import subprocess
import sys
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CAMINHO = os.path.join(ROOT, "images", "goodprofile", "goodprofile")

_loader = importlib.machinery.SourceFileLoader("goodprofile", CAMINHO)
_spec = importlib.util.spec_from_loader("goodprofile", _loader)
GP = importlib.util.module_from_spec(_spec)
_loader.exec_module(GP)

VERM = (255, 0, 0, 255)
AZUL = (0, 0, 255, 255)
BRANCO = (255, 255, 255, 255)


def imagem(linhas):
    """list of rows of RGBA tuples -> (w, h, bytearray)."""
    h = len(linhas)
    w = len(linhas[0])
    buf = bytearray()
    for linha in linhas:
        for px in linha:
            buf += bytes(px)
    return w, h, buf


def pixel(w, buf, x, y):
    i = (y * w + x) * 4
    return tuple(buf[i:i + 4])


class TestPresets(unittest.TestCase):
    def test_dimensoes_validas(self):
        for nome, (grupo, w, h, _nota) in GP.PRESETS.items():
            with self.subTest(preset=nome):
                self.assertGreater(w, 0)
                self.assertGreater(h, 0)
                self.assertTrue(grupo)
                self.assertEqual(nome, nome.lower())

    def test_kits_apontam_pra_presets(self):
        for kit, lista in GP.KITS.items():
            with self.subTest(kit=kit):
                self.assertTrue(lista)
                for p in lista:
                    self.assertIn(p, GP.PRESETS)

    def test_resolver_custom(self):
        alvos = GP.resolver_alvos(["800x600"])
        self.assertEqual(alvos, [("800x600", 800, 600, "", None)])

    def test_resolver_kit_expande(self):
        alvos = GP.resolver_alvos(["kit-favicon"])
        self.assertEqual(len(alvos), len(GP.KITS["kit-favicon"]))
        self.assertTrue(all(a[4] == "kit-favicon" for a in alvos))


class TestParseCor(unittest.TestCase):
    def test_formatos(self):
        self.assertEqual(GP.parse_cor("fff"), (255, 255, 255, 255))
        self.assertEqual(GP.parse_cor("#112233"), (17, 34, 51, 255))
        self.assertEqual(GP.parse_cor("11223344"), (17, 34, 51, 68))
        self.assertEqual(GP.parse_cor("transparente"), (0, 0, 0, 0))
        self.assertEqual(GP.parse_cor("PRETO"), (0, 0, 0, 255))

    def test_invalida(self):
        with self.assertRaises(ValueError):
            GP.parse_cor("verde-limao")


class TestFitCover(unittest.TestCase):
    def setUp(self):
        # 4x2: left half red, right half blue
        self.w, self.h, self.buf = imagem([
            [VERM, VERM, AZUL, AZUL],
            [VERM, VERM, AZUL, AZUL],
        ])

    def test_gravidade_oeste(self):
        out = GP.fit_cover(self.w, self.h, self.buf, 2, 2, "oeste")
        self.assertEqual(pixel(2, out, 0, 0), VERM)
        self.assertEqual(pixel(2, out, 1, 1), VERM)

    def test_gravidade_leste(self):
        out = GP.fit_cover(self.w, self.h, self.buf, 2, 2, "leste")
        self.assertEqual(pixel(2, out, 0, 0), AZUL)
        self.assertEqual(pixel(2, out, 1, 1), AZUL)

    def test_foco_clampa_na_borda(self):
        out = GP.fit_cover(self.w, self.h, self.buf, 2, 2, foco=(100.0, 50.0))
        self.assertEqual(pixel(2, out, 0, 0), AZUL)


class TestFitContain(unittest.TestCase):
    def test_padding_e_centro(self):
        w, h, buf = imagem([[VERM, VERM]])  # 2x1 red
        out = GP.fit_contain(w, h, buf, 4, 4, fundo=(0, 0, 0, 255))
        # scaled to 4x2, centred: rows 0/3 background, rows 1/2 content
        self.assertEqual(pixel(4, out, 0, 0), (0, 0, 0, 255))
        self.assertEqual(pixel(4, out, 0, 3), (0, 0, 0, 255))
        self.assertEqual(pixel(4, out, 1, 1), VERM)
        self.assertEqual(pixel(4, out, 2, 2), VERM)


class TestTrim(unittest.TestCase):
    def test_apara_borda_uniforme(self):
        linhas = [[BRANCO] * 6 for _ in range(6)]
        for y in (2, 3):
            for x in (2, 3):
                linhas[y][x] = VERM
        w, h, buf = imagem(linhas)
        nw, nh, out = GP.trim(w, h, buf)
        self.assertEqual((nw, nh), (2, 2))
        self.assertEqual(pixel(nw, out, 0, 0), VERM)

    def test_sem_borda_nao_mexe(self):
        w, h, buf = imagem([[VERM, AZUL], [AZUL, VERM]])
        nw, nh, _ = GP.trim(w, h, buf)
        self.assertEqual((nw, nh), (2, 2))


class TestCores(unittest.TestCase):
    def test_trocar_cor(self):
        w, h, buf = imagem([[VERM, AZUL]])
        GP.trocar_cor(buf, VERM, (0, 255, 0, 255), tol=10)
        self.assertEqual(pixel(w, buf, 0, 0), (0, 255, 0, 255))
        self.assertEqual(pixel(w, buf, 1, 0), AZUL)

    def test_trocar_pra_transparente(self):
        w, h, buf = imagem([[BRANCO, VERM]])
        GP.trocar_cor(buf, BRANCO, (0, 0, 0, 0), tol=10)
        self.assertEqual(buf[3], 0)       # white -> alpha 0
        self.assertEqual(buf[7], 255)     # red untouched

    def test_tingir_preserva_extremos(self):
        w, h, buf = imagem([[(0, 0, 0, 255), (255, 255, 255, 255)]])
        GP.tingir(buf, (200, 100, 50, 255))
        self.assertEqual(pixel(w, buf, 0, 0), (0, 0, 0, 255))
        self.assertEqual(pixel(w, buf, 1, 0), (255, 255, 255, 255))

    def test_tingir_meio_vira_o_tom(self):
        w, h, buf = imagem([[(127, 127, 127, 255)]])
        GP.tingir(buf, (200, 100, 50, 255))
        r, g, b, a = pixel(w, buf, 0, 0)
        self.assertGreater(r, g)
        self.assertGreater(g, b)
        self.assertEqual(a, 255)

    def test_pb(self):
        w, h, buf = imagem([[VERM]])
        GP.pb(buf)
        r, g, b, _ = pixel(w, buf, 0, 0)
        self.assertEqual(r, g)
        self.assertEqual(g, b)


class TestMascaras(unittest.TestCase):
    def test_circulo(self):
        w, h, buf = imagem([[VERM] * 8 for _ in range(8)])
        GP.mascara_circulo(w, h, buf)
        self.assertEqual(buf[3], 0)                       # corner clipped
        self.assertEqual(pixel(w, buf, 4, 4)[3], 255)     # centre solid

    def test_cantos(self):
        w, h, buf = imagem([[VERM] * 8 for _ in range(8)])
        GP.mascara_cantos(w, h, buf, 3)
        self.assertEqual(buf[3], 0)                       # corner clipped
        self.assertEqual(pixel(w, buf, 4, 0)[3], 255)     # edge midpoint solid


class TestCli(unittest.TestCase):
    def test_help_responde(self):
        amb = dict(os.environ, NO_COLOR="1")
        out = subprocess.run(
            [sys.executable, CAMINHO, "help"],
            capture_output=True, env=amb,
        )
        self.assertEqual(out.returncode, 0)
        self.assertIn(b"GOODPROFILE", out.stdout)

    def test_posicional_desconhecido(self):
        amb = dict(os.environ, NO_COLOR="1")
        out = subprocess.run(
            [sys.executable, CAMINHO, "nao-existe.png"],
            capture_output=True, env=amb,
        )
        self.assertEqual(out.returncode, 2)


if __name__ == "__main__":
    unittest.main()
