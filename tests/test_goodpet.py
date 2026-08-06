# -*- coding: utf-8 -*-
"""Tests for games/goodpet/goodpet — pure engine, actions and persistence.

Run from the repo root: python3 -m unittest discover -s tests
"""

import copy
import importlib.machinery
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CAMINHO = os.path.join(ROOT, "games", "goodpet", "goodpet")

_loader = importlib.machinery.SourceFileLoader("goodpet", CAMINHO)
_spec = importlib.util.spec_from_loader("goodpet", _loader)
GP = importlib.util.module_from_spec(_spec)
_loader.exec_module(GP)

T0 = 1700000000.0
HORA = 3600.0


def bebe(nome="Test"):
    """Pet recém-chocado: fase bebê, stats cheios, nascido em T0."""
    estado = GP.novo_pet(nome, T0)
    estado["fase"] = "bebe"
    return estado


class TestMotor(unittest.TestCase):
    def test_decay_cai_na_taxa_esperada(self):
        estado = bebe()
        GP.simular(estado, T0 + 10 * HORA)
        s = estado["stats"]
        self.assertAlmostEqual(s["fome"], 75.0, delta=0.01)
        self.assertAlmostEqual(s["energia"], 50.0, delta=0.01)
        self.assertAlmostEqual(s["higiene"], 85.0, delta=0.01)
        self.assertAlmostEqual(s["felicidade"], 85.0, delta=0.01)

    def test_clamp_stats_ficam_entre_0_e_100(self):
        estado = bebe()
        GP.simular(estado, T0 + 200 * HORA)
        for v in estado["stats"].values():
            self.assertGreaterEqual(v, 0.0)
            self.assertLessEqual(v, 100.0)

    def test_simular_e_deterministico_e_idempotente(self):
        a = bebe()
        b = copy.deepcopy(a)
        GP.simular(a, T0 + 30 * HORA)
        GP.simular(b, T0 + 30 * HORA)
        self.assertEqual(a, b)
        de_novo = copy.deepcopy(a)
        GP.simular(de_novo, T0 + 30 * HORA)
        self.assertEqual(a, de_novo)

    def test_dormir_recupera_energia_e_acorda_sozinho_em_8h(self):
        estado = bebe()
        estado["dormindo"] = True
        estado["stats"]["energia"] = 0.0
        _, eventos = GP.simular(estado, T0 + 8 * HORA + 60)
        self.assertIn("acordou", eventos)
        self.assertFalse(estado["dormindo"])
        self.assertGreaterEqual(estado["stats"]["energia"], 99.0)

    def test_energia_zero_desmaia_e_dorme(self):
        estado = bebe()
        estado["stats"]["energia"] = 1.0
        _, eventos = GP.simular(estado, T0 + 1 * HORA)
        self.assertIn("desmaiou", eventos)
        self.assertTrue(estado["dormindo"])

    def test_higiene_baixa_6h_adoece(self):
        estado = bebe()
        estado["stats"]["higiene"] = 19.0
        _, eventos = GP.simular(estado, T0 + 6 * HORA + 120)
        self.assertIn("adoeceu", eventos)
        self.assertTrue(estado["doente"])

    def test_higiene_recuperada_zera_o_timer(self):
        estado = bebe()
        estado["stats"]["higiene"] = 19.0
        GP.simular(estado, T0 + 3 * HORA)
        estado["stats"]["higiene"] = 100.0
        GP.simular(estado, T0 + 8 * HORA)
        self.assertFalse(estado["doente"])
        self.assertIsNone(estado["higiene_baixa_desde"])

    def test_fome_zero_24h_mata(self):
        estado = bebe()
        estado["stats"]["fome"] = 0.0
        _, eventos = GP.simular(estado, T0 + 25 * HORA)
        self.assertTrue(estado["morto"])
        self.assertEqual(estado["morte"]["causa"], "fome")
        self.assertIn("morreu:fome", eventos)

    def test_doenca_48h_sem_cura_mata(self):
        estado = bebe()
        estado["doente"] = True
        estado["doente_desde"] = T0
        GP.simular(estado, T0 + 48 * HORA + 60)
        self.assertTrue(estado["morto"])
        self.assertEqual(estado["morte"]["causa"], "doenca")

    def test_ovo_choca_em_1h_e_nao_morre(self):
        estado = GP.novo_pet("Ovo", T0)
        _, eventos = GP.simular(estado, T0 + 30 * 60)
        self.assertEqual(estado["fase"], "ovo")
        _, eventos = GP.simular(estado, T0 + 1 * HORA + 60)
        self.assertEqual(estado["fase"], "bebe")
        self.assertIn("chocou", eventos)
        self.assertFalse(estado["morto"])
        # ovo é inerte: stats intactos até chocar
        for v in GP.novo_pet("X", T0)["stats"].values():
            self.assertEqual(v, 100.0)

    def test_evolucao_1h_24h_72h_com_cuidado(self):
        estado = GP.novo_pet("Evo", T0)
        fases = {}
        t = T0
        while t < T0 + 73 * HORA:
            t += 6 * HORA
            GP.simular(estado, t)
            estado["stats"].update(
                {"fome": 100.0, "felicidade": 100.0, "energia": 100.0, "higiene": 100.0}
            )
            estado["fome_zero_desde"] = None
            estado["higiene_baixa_desde"] = None
            fases[(t - T0) / HORA] = estado["fase"]
        self.assertEqual(fases[6.0], "bebe")
        self.assertEqual(fases[24.0], "crianca")
        self.assertEqual(fases[72.0], "adulto")
        self.assertFalse(estado["morto"])

    def test_evolucao_espera_cura(self):
        estado = bebe()
        estado["fase"] = "crianca"
        estado["nascido_em"] = T0 - 80 * HORA
        estado["doente"] = True
        estado["doente_desde"] = T0
        GP.passo(estado, 60, T0 + 60)
        self.assertEqual(estado["fase"], "crianca")
        GP.acao_heal(estado, T0 + 120)
        GP.passo(estado, 60, T0 + 180)
        self.assertEqual(estado["fase"], "adulto")

    def test_morto_ignora_passos(self):
        estado = bebe()
        estado["morto"] = True
        antes = copy.deepcopy(estado["stats"])
        eventos = GP.passo(estado, 10 * HORA, T0 + 10 * HORA)
        self.assertEqual(eventos, [])
        self.assertEqual(estado["stats"], antes)


class TestAcoes(unittest.TestCase):
    def test_feed_alimenta_e_recusa_de_barriga_cheia(self):
        estado = bebe()
        estado["stats"]["fome"] = 50.0
        estado, recusa = GP.acao_feed(estado, T0)
        self.assertIsNone(recusa)
        self.assertEqual(estado["stats"]["fome"], 80.0)
        estado["stats"]["fome"] = 96.0
        _, recusa = GP.acao_feed(estado, T0)
        self.assertIsNotNone(recusa)

    def test_feed_recusa_dormindo_e_ovo(self):
        estado = bebe()
        estado["dormindo"] = True
        _, recusa = GP.acao_feed(estado, T0)
        self.assertIsNotNone(recusa)
        ovo = GP.novo_pet("O", T0)
        _, recusa = GP.acao_feed(ovo, T0)
        self.assertIsNotNone(recusa)

    def test_play_recusa_exausto_e_doente(self):
        estado = bebe()
        estado["stats"]["energia"] = 10.0
        _, recusa = GP.acao_play(estado, T0)
        self.assertIsNotNone(recusa)
        estado["stats"]["energia"] = 100.0
        estado["doente"] = True
        _, recusa = GP.acao_play(estado, T0)
        self.assertIsNotNone(recusa)

    def test_clean_zera_timer_de_higiene(self):
        estado = bebe()
        estado["stats"]["higiene"] = 5.0
        estado["higiene_baixa_desde"] = T0 - HORA
        estado, recusa = GP.acao_clean(estado, T0)
        self.assertIsNone(recusa)
        self.assertEqual(estado["stats"]["higiene"], 100.0)
        self.assertIsNone(estado["higiene_baixa_desde"])

    def test_sleep_wake_e_recusas(self):
        estado = bebe()
        estado, recusa = GP.acao_sleep(estado, T0)
        self.assertIsNone(recusa)
        self.assertTrue(estado["dormindo"])
        _, recusa = GP.acao_sleep(estado, T0)
        self.assertIsNotNone(recusa)
        estado, recusa = GP.acao_wake(estado, T0)
        self.assertIsNone(recusa)
        self.assertFalse(estado["dormindo"])
        _, recusa = GP.acao_wake(estado, T0)
        self.assertIsNotNone(recusa)

    def test_heal_cura_e_recusa_saudavel(self):
        estado = bebe()
        estado["doente"] = True
        estado["doente_desde"] = T0
        estado, recusa = GP.acao_heal(estado, T0)
        self.assertIsNone(recusa)
        self.assertFalse(estado["doente"])
        self.assertIsNone(estado["doente_desde"])
        _, recusa = GP.acao_heal(estado, T0)
        self.assertIsNotNone(recusa)

    def test_morto_recusa_toda_acao(self):
        estado = bebe()
        estado["morto"] = True
        for fn in (GP.acao_feed, GP.acao_play, GP.acao_clean, GP.acao_sleep, GP.acao_wake, GP.acao_heal):
            _, recusa = fn(estado, T0)
            self.assertIsNotNone(recusa)

    def test_executar_acao_alterna_sono_no_watch(self):
        estado = bebe()
        estado["dormindo"] = True
        estado, _, sucesso = GP.executar_acao(estado, "sleep", T0, alternar_sono=True)
        self.assertTrue(sucesso)
        self.assertFalse(estado["dormindo"])


class TestRenderPuro(unittest.TestCase):
    def test_pose_do_prioridades(self):
        estado = bebe()
        self.assertEqual(GP.pose_do(estado), "feliz")
        estado["stats"]["fome"] = 50.0
        self.assertEqual(GP.pose_do(estado), "normal")
        estado["stats"]["fome"] = 20.0
        self.assertEqual(GP.pose_do(estado), "triste")
        estado["doente"] = True
        self.assertEqual(GP.pose_do(estado), "doente")
        estado["dormindo"] = True
        self.assertEqual(GP.pose_do(estado), "dormindo")
        estado["morto"] = True
        self.assertEqual(GP.pose_do(estado), "morto")
        ovo = GP.novo_pet("O", T0)
        self.assertEqual(GP.pose_do(ovo), "normal")

    def test_toda_arte_tem_5_linhas_e_cabe_na_janela(self):
        for fase, poses in GP.ARTE.items():
            for pose, frames in poses.items():
                for fr in frames:
                    self.assertEqual(len(fr), 5, f"{fase}/{pose}")
                    for ln in fr:
                        self.assertLessEqual(GP.largura(ln), 20, f"{fase}/{pose}: {ln!r}")
        self.assertEqual(len(GP.ARTE_MORTO), 5)

    def test_rotulo_ev_cobre_prefixos(self):
        self.assertIn("CRIANÇA", GP.rotulo_ev("evoluiu:crianca"))
        self.assertIn("fome", GP.rotulo_ev("morreu:fome"))
        self.assertEqual(GP.rotulo_ev("chocou"), "o ovo chocou!")


class TestPersistencia(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self._base, self._pet = GP.BASE_DIR, GP.PET_FILE
        GP.BASE_DIR = Path(self.tmp.name)
        GP.PET_FILE = GP.BASE_DIR / "pet.json"

    def tearDown(self):
        GP.BASE_DIR, GP.PET_FILE = self._base, self._pet
        self.tmp.cleanup()

    def test_roundtrip(self):
        estado = bebe("Rond")
        GP.salvar_json(GP.PET_FILE, estado)
        lido = GP.carregar_json(GP.PET_FILE, None)
        self.assertEqual(estado, lido)

    def test_corrompido_cai_no_padrao(self):
        GP.PET_FILE.parent.mkdir(parents=True, exist_ok=True)
        GP.PET_FILE.write_text("{nao é json", encoding="utf-8")
        self.assertIsNone(GP.carregar_json(GP.PET_FILE, None))

    def test_migrar_completa_chaves_ausentes(self):
        velho = {"nome": "Antigo", "nascido_em": T0, "stats": {"fome": 40.0}}
        estado = GP.migrar(velho)
        self.assertEqual(estado["nome"], "Antigo")
        self.assertEqual(estado["stats"]["fome"], 40.0)
        self.assertEqual(estado["stats"]["energia"], 100.0)
        for chave in GP.novo_pet("X", T0):
            self.assertIn(chave, estado)
        self.assertEqual(estado["schema"], 1)

    def test_historico_capado_em_50(self):
        estado = bebe()
        for i in range(80):
            GP.registrar(estado, "dormiu", T0 + i)
        self.assertEqual(len(estado["historico"]), 50)


if __name__ == "__main__":
    unittest.main()
