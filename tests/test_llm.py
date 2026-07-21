"""Tests for lib/llm.py — the shared OpenRouter client.

Run from the repo root:  python3 -m unittest discover -s tests
Only the standard library is used (no pytest), matching the tools themselves.
"""

import io
import json
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
from llm import LLM, LLMError, extrair_json  # noqa: E402


class TestExtrairJson(unittest.TestCase):
    def test_array_puro(self):
        self.assertEqual(extrair_json('[{"a": 1}]', "array"), [{"a": 1}])

    def test_objeto_puro(self):
        self.assertEqual(extrair_json('{"a": 1}', "objeto"), {"a": 1})

    def test_array_dentro_de_cerca_markdown(self):
        self.assertEqual(extrair_json('```json\n[{"a": 1}]\n```', "array"), [{"a": 1}])

    def test_ignora_bloco_think(self):
        self.assertEqual(
            extrair_json('<think>talvez [1, 2]</think>[{"a": 1}]', "array"), [{"a": 1}]
        )

    def test_texto_em_volta(self):
        self.assertEqual(extrair_json('aqui vai: [{"x": 9}] pronto', "array"), [{"x": 9}])

    def test_array_de_nao_objetos_rejeitado(self):
        # a lista existe mas não é array de objetos -> não serve
        self.assertIsNone(extrair_json("[1, 2, 3]", "array"))

    def test_colchete_solto_nao_confunde(self):
        # "lista[0]" é ruído; o parser precisa achar o array de objetos real
        self.assertEqual(
            extrair_json('lista[0] e depois [{"ok": true}]', "array"), [{"ok": True}]
        )

    def test_sem_json_retorna_none(self):
        self.assertIsNone(extrair_json("nada de json aqui", "array"))


class TestModelos(unittest.TestCase):
    def test_usa_defaults_sem_env(self):
        llm = LLM("t", ["a:free", "b:free"])
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("OPENROUTER_MODEL", None)
            self.assertEqual(llm.modelos(), ["a:free", "b:free"])

    def test_env_sobrescreve_e_limpa_espacos(self):
        llm = LLM("t", ["a:free"])
        with mock.patch.dict(os.environ, {"OPENROUTER_MODEL": " x:free , y:free ,"}):
            self.assertEqual(llm.modelos(), ["x:free", "y:free"])


class TestChat(unittest.TestCase):
    def test_sem_chave_levanta_no_key(self):
        llm = LLM("t", ["a:free"])
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("OPENROUTER_API_KEY", None)
            with self.assertRaises(LLMError) as ctx:
                llm.chat([{"role": "user", "content": "oi"}])
            self.assertEqual(ctx.exception.kind, "no_key")

    def test_sucesso_retorna_conteudo_e_modelo(self):
        payload = json.dumps(
            {"choices": [{"message": {"content": "  olá  "}}]}
        ).encode("utf-8")
        llm = LLM("t", ["primeiro:free"])
        with mock.patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-x"}), \
                mock.patch("urllib.request.urlopen", return_value=io.BytesIO(payload)):
            content, model = llm.chat([{"role": "user", "content": "oi"}])
        self.assertEqual(content, "olá")
        self.assertEqual(model, "primeiro:free")

    def test_todos_falham_agrega_erros(self):
        llm = LLM("t", ["m1:free", "m2:free"])
        vazio = json.dumps({"choices": [{"message": {"content": ""}}]}).encode("utf-8")

        def resp(*a, **k):
            return io.BytesIO(vazio)

        with mock.patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-x"}), \
                mock.patch("urllib.request.urlopen", side_effect=resp):
            with self.assertRaises(LLMError) as ctx:
                llm.chat([{"role": "user", "content": "oi"}])
        self.assertEqual(ctx.exception.kind, "all_failed")
        self.assertEqual(len(ctx.exception.errors), 2)  # um erro por modelo

    def test_json_tipo_valida_e_cai_pro_proximo(self):
        # 1º modelo devolve JSON quebrado -> falha; 2º devolve válido -> aceito
        ruim = json.dumps({"choices": [{"message": {"content": "sem json"}}]}).encode("utf-8")
        bom = json.dumps(
            {"choices": [{"message": {"content": '[{"a": 1}]'}}]}
        ).encode("utf-8")
        respostas = [io.BytesIO(ruim), io.BytesIO(bom)]
        llm = LLM("t", ["ruim:free", "bom:free"])
        with mock.patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-or-x"}), \
                mock.patch("urllib.request.urlopen", side_effect=lambda *a, **k: respostas.pop(0)):
            parsed, model = llm.chat([{"role": "user", "content": "oi"}], json_tipo="array")
        self.assertEqual(parsed, [{"a": 1}])
        self.assertEqual(model, "bom:free")


class TestFreeModels(unittest.TestCase):
    def test_filtra_e_ordena_free(self):
        payload = json.dumps(
            {"data": [{"id": "z:free"}, {"id": "meio"}, {"id": "a:free"}]}
        ).encode("utf-8")
        llm = LLM("t", ["x:free"])
        with mock.patch("urllib.request.urlopen", return_value=io.BytesIO(payload)):
            self.assertEqual(llm.free_models(), ["a:free", "z:free"])

    def test_falha_de_rede_levanta_fetch(self):
        llm = LLM("t", ["x:free"])
        with mock.patch("urllib.request.urlopen", side_effect=OSError("boom")):
            with self.assertRaises(LLMError) as ctx:
                llm.free_models()
        self.assertEqual(ctx.exception.kind, "fetch")


if __name__ == "__main__":
    unittest.main()
