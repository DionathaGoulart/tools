"""Tests for goodwash/goodwash — parsing routing + offline checar heuristic.

The argparse ``comando`` positional used to carry ``choices=[...]``, so every
documented free-text invocation (``goodwash "texto"``, ``goodwash profunda "x"``,
``goodwash arquivo.txt``) exited 2 before the text was ever read. These tests lock
the fix: bare text/intensity/file must route to ``lavar``, and the real subcommands
must still route correctly. ``lavar`` itself needs a network key, so the CLI tests
force an empty ``OPENROUTER_API_KEY`` (which also neutralises any local ``.env``)
and assert the tool reaches the no-key path (exit 1), never an argparse error
(exit 2). Run from the repo root:

    python3 -m unittest discover -s tests
"""

import importlib.machinery
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CAMINHO = os.path.join(ROOT, "goodwash", "goodwash")

_loader = importlib.machinery.SourceFileLoader("goodwash", CAMINHO)
_spec = importlib.util.spec_from_loader("goodwash", _loader)
GW = importlib.util.module_from_spec(_spec)
_loader.exec_module(GW)


def _amb_sem_chave():
    amb = {k: v for k, v in os.environ.items() if k != "OPENROUTER_API_KEY"}
    amb["OPENROUTER_API_KEY"] = ""   # força no_key e bloqueia o .env (setdefault)
    amb["NO_COLOR"] = "1"
    return amb


def _rodar(*argv, entrada=None):
    return subprocess.run(
        [sys.executable, CAMINHO, *argv],
        capture_output=True, env=_amb_sem_chave(), input=entrada,
    )


class _Args:
    """Stand-in pro Namespace do argparse que ler_entrada espera."""
    arquivo = ""


class TestLerEntrada(unittest.TestCase):
    """ler_entrada é a função pura por trás do roteamento de texto/intensidade."""

    def test_intensidade_default_media(self):
        inten, texto = GW.ler_entrada(_Args(), ["meu", "texto"])
        self.assertEqual(inten, "media")
        self.assertEqual(texto, "meu texto")

    def test_intensidade_explicita(self):
        inten, texto = GW.ler_entrada(_Args(), ["profunda", "meu texto"])
        self.assertEqual(inten, "profunda")
        self.assertEqual(texto, "meu texto")

    def test_le_arquivo_quando_caminho_existe(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
            fh.write("conteudo do arquivo")
            caminho = fh.name
        try:
            _inten, texto = GW.ler_entrada(_Args(), [caminho])
            self.assertEqual(texto, "conteudo do arquivo")
        finally:
            os.unlink(caminho)

    def test_texto_solto_nao_vira_arquivo(self):
        _inten, texto = GW.ler_entrada(_Args(), ["arquivo-que-nao-existe.txt"])
        self.assertEqual(texto, "arquivo-que-nao-existe.txt")


class TestChecarTells(unittest.TestCase):
    def test_pega_formula_apos_pontuacao(self):
        # "além disso" colado numa vírgula não era detectado antes do fix
        formulas, _buzz, _var, _n = GW.checar_tells(
            "É importante notar que, além disso, a solução é robusta.")
        achadas = {f for f, _ in formulas}
        self.assertIn("além disso", achadas)
        self.assertIn("é importante notar", achadas)

    def test_buzzwords(self):
        _formulas, buzz, _var, _n = GW.checar_tells(
            "o ecossistema é fundamental e crucial para a sinergia.")
        for termo in ("ecossistema", "fundamental", "crucial", "sinergia"):
            self.assertIn(termo, buzz)

    def test_var_none_com_uma_frase(self):
        _formulas, _buzz, var, n = GW.checar_tells("uma frase só aqui.")
        self.assertIsNone(var)
        self.assertEqual(n, 1)

    def test_var_calculado_com_varias_frases(self):
        _formulas, _buzz, var, n = GW.checar_tells(
            "Curto. Uma frase bem mais longa do que a anterior tem aqui.")
        self.assertIsNotNone(var)
        self.assertGreater(var, 0)
        self.assertEqual(n, 2)


class TestRoteamentoCli(unittest.TestCase):
    def test_help_exit0(self):
        out = _rodar("help")
        self.assertEqual(out.returncode, 0)
        self.assertIn(b"GOODWASH", out.stdout)

    def test_checar_offline_exit0(self):
        out = _rodar("checar", "além disso, a solução é crucial.")
        self.assertEqual(out.returncode, 0)
        self.assertIn(b"FORMULAS", out.stdout)

    def test_temas_exit0(self):
        self.assertEqual(_rodar("temas").returncode, 0)

    def test_texto_posicional_roteia_pra_lavar(self):
        # regressão do bug crítico: NÃO pode ser exit 2 (argparse); tem que chegar
        # no caminho de lavar, que sem chave morre com no_key (exit 1).
        out = _rodar("seu texto de teste aqui")
        self.assertNotEqual(out.returncode, 2)
        self.assertEqual(out.returncode, 1)
        self.assertIn(b"OPENROUTER_API_KEY", out.stderr)

    def test_intensidade_posicional_roteia_pra_lavar(self):
        out = _rodar("profunda", "meu texto")
        self.assertNotEqual(out.returncode, 2)
        self.assertIn(b"OPENROUTER_API_KEY", out.stderr)

    def test_stdin_roteia_pra_lavar(self):
        out = _rodar(entrada=b"texto vindo do stdin")
        self.assertNotEqual(out.returncode, 2)
        self.assertIn(b"OPENROUTER_API_KEY", out.stderr)


if __name__ == "__main__":
    unittest.main()
