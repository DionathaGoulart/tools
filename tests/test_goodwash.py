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

import contextlib
import importlib.machinery
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import textwrap
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


def _rodar(*argv, entrada=None, amb_extra=None):
    amb = _amb_sem_chave()
    amb.update(amb_extra or {})
    return subprocess.run(
        [sys.executable, CAMINHO, *argv],
        capture_output=True, env=amb, input=entrada,
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


def _formulas(texto):
    return {f for f, _ in GW.checar_tells(texto)["formulas"]}


class TestChecarTells(unittest.TestCase):
    def test_pega_formula_apos_pontuacao(self):
        # "além disso" colado numa vírgula não era detectado antes do fix
        achadas = _formulas("É importante notar que, além disso, a solução é robusta.")
        self.assertIn("além disso", achadas)
        self.assertIn("é importante notar", achadas)

    def test_buzzwords(self):
        buzz = GW.checar_tells("o ecossistema é fundamental e crucial para a sinergia.")["buzz"]
        for termo in ("ecossistema", "fundamental", "crucial", "sinergia"):
            self.assertIn(termo, buzz)

    def test_cv_none_sem_frases_suficientes(self):
        r = GW.checar_tells("uma frase só aqui.")
        self.assertIsNone(r["cv"])
        self.assertEqual(r["frases"], 1)

    def test_cv_calculado_com_frases_suficientes(self):
        r = GW.checar_tells(
            "Curto. Bem mais longo do que a frase anterior era, de longe. "
            "Médio aqui nesse ponto. Fim.")
        self.assertEqual(r["frases"], 4)
        self.assertIsNotNone(r["cv"])
        self.assertGreater(r["cv"], 0)


class TestChecarRegressoes(unittest.TestCase):
    """Cada teste aqui trava um falso negativo que a heurística tinha.

    A raiz comum dos três primeiros era ``re.sub(r"[^\\w\\s]", " ", ...)``: ele
    apagava a pontuação só do TEXTO, nunca das entradas das listas, e não mexia
    no espaçamento. Hoje texto e termo passam pelo mesmo ``normalizar``.
    """

    def test_entrada_com_apostrofo_ou_hifen_nao_e_morta(self):
        # "it's important to note" e "game-changer" NUNCA casavam: a pontuação
        # sumia do texto e continuava na entrada da lista.
        r = GW.checar_tells("It's important to note that this is a game-changer.")
        self.assertIn("it's important to note", {f for f, _ in r["formulas"]})
        self.assertIn("game-changer", r["buzz"])

    def test_formula_quebrada_entre_linhas(self):
        # arquivo com wrap de coluna partia a fórmula em duas linhas e ela sumia
        self.assertIn("além disso", _formulas("Texto qualquer, além\ndisso segue."))

    def test_formula_com_espaco_duplo(self):
        self.assertIn("além disso", _formulas("Texto qualquer, além  disso segue."))

    def test_texto_sem_acento_ainda_e_detectado(self):
        r = GW.checar_tells("Alem disso, o ponto e crucial.")
        self.assertIn("além disso", {f for f, _ in r["formulas"]})
        self.assertIn("crucial", r["buzz"])

    def test_buzz_no_plural(self):
        # "fundamentais"/"cruciais"/"ecossistemas" passavam batido (sem flexão)
        buzz = GW.checar_tells(
            "Os pontos fundamentais e as questões cruciais dos ecossistemas.")["buzz"]
        for termo in ("fundamental", "crucial", "ecossistema"):
            self.assertIn(termo, buzz)

    def test_texto_sem_pontuacao_final_conta_como_frase(self):
        # antes: frases=0 e o eixo de ritmo inteiro zerava em silêncio
        r = GW.checar_tells("esse texto não termina com ponto")
        self.assertEqual(r["frases"], 1)
        self.assertEqual(r["palavras"], 6)

    def test_abreviacao_nao_quebra_frase(self):
        self.assertEqual(GW.checar_tells("O Dr. Silva chegou tarde na reunião.")["frases"], 1)

    def test_inicial_de_nome_nao_quebra_frase(self):
        self.assertEqual(GW.checar_tells("Li o J. R. R. Tolkien inteiro ontem.")["frases"], 1)

    def test_decimal_nao_quebra_frase(self):
        self.assertEqual(GW.checar_tells("O valor subiu 3.5 por cento no ano.")["frases"], 1)

    def test_formula_ambigua_so_conta_abrindo_oracao(self):
        # "com isso"/"por outro lado" também são predicado normal em PT e davam
        # falso positivo em cima de texto humano
        self.assertNotIn("com isso", _formulas("Trabalho com isso há uns oito anos."))
        self.assertIn("com isso", _formulas("O time cresceu. Com isso, tudo mudou."))
        self.assertNotIn("por outro lado", _formulas("A padaria fica por outro lado da rua."))
        self.assertIn("por outro lado", _formulas("É caro. Por outro lado, dura mais."))

    def test_contexto_aponta_pro_trecho_certo(self):
        texto = "Uma abertura qualquer aqui. Além disso, o resto do texto segue."
        (_f, ctx), = [x for x in GW.checar_tells(texto)["formulas"] if x[0] == "além disso"]
        self.assertIn("Além disso", ctx)


class TestFormulasFamilia(unittest.TestCase):
    """Lista literal perdia variantes triviais ("é importante LEMBRAR", "é
    FUNDAMENTAL destacar"). As famílias por padrão cobrem a combinação."""

    def test_pega_variantes_fora_da_lista(self):
        achadas = _formulas("É importante lembrar que o prazo mudou. "
                            "É fundamental destacar o custo disso.")
        self.assertTrue(any(f.startswith("e importante lembrar") for f in achadas))
        self.assertTrue(any(f.startswith("e fundamental destacar") for f in achadas))

    def test_nao_duplica_literal_da_lista(self):
        # o span coberto pelo literal não pode contar de novo pra família
        r = GW.checar_tells("É importante notar que o prazo mudou.")
        self.assertEqual(len(r["formulas"]), 1)
        self.assertIn("é importante notar", {f for f, _ in r["formulas"]})

    def test_conectivos_datados(self):
        achadas = _formulas("Ademais, o prazo encurtou. Dito isso, seguimos. "
                            "Nesse sentido, a medida funciona. Em síntese, deu certo.")
        self.assertEqual(len(achadas), 4)

    def test_em_primeiro_lugar_so_abrindo_oracao(self):
        self.assertEqual(_formulas("Ele chegou em primeiro lugar na corrida."), set())
        self.assertTrue(_formulas("Em primeiro lugar, o custo caiu."))


class TestScore(unittest.TestCase):
    """O score existe porque contagem crua não dizia nada: 5 fórmulas em 80
    palavras e 5 em 2000 são coisas opostas."""

    IA = ("A inteligência artificial tem transformado o mercado de trabalho. "
          "É importante notar que essa mudança afeta diversos setores. "
          "Além disso, novas oportunidades surgem para profissionais. "
          "Por outro lado, funções tradicionais tendem a desaparecer. "
          "Portanto, a requalificação se torna fundamental nesse cenário. "
          "Em suma, adaptar-se é a alternativa viável para permanecer relevante.")
    HUMANO = ("Trabalho com isso há uns oito anos. No começo achei que fosse hype. "
              "Não era. Meu chefe me chamou numa terça e disse que metade do time "
              "de suporte ia embora até dezembro. Montei o pipeline. Deu errado "
              "duas vezes. A parte difícil não é o modelo — é o jurídico.")

    def test_separa_ia_de_humano(self):
        ia, humano = GW.checar_tells(self.IA), GW.checar_tells(self.HUMANO)
        self.assertEqual(ia["veredito"], "ALTO")
        self.assertEqual(humano["veredito"], "BAIXO")
        self.assertGreater(ia["score"] - humano["score"], 40)

    def test_densidade_normaliza_pelo_tamanho(self):
        curto = GW.checar_tells("Além disso, portanto, em suma.")
        longo = GW.checar_tells("Além disso, portanto, em suma. " + "palavra " * 500)
        self.assertEqual(len(curto["formulas"]), len(longo["formulas"]))
        self.assertGreater(curto["dens_formulas"], longo["dens_formulas"])

    def test_score_estavel_sob_quebra_de_coluna(self):
        # 68% das larguras de wrap perdiam detecção antes do fix
        quebrado = textwrap.fill(" ".join(self.IA.split()), 54)
        self.assertEqual(GW.checar_tells(quebrado)["score"],
                         GW.checar_tells(self.IA)["score"])


class TestAvaliar(unittest.TestCase):
    """``avaliar`` responde 'IA ou humano?'. O risco real é o falso positivo em
    prosa formal humana — ela usa as mesmas transições e a mesma voz passiva."""

    IA = ("A transformação digital tem se consolidado como um pilar fundamental "
          "para as organizações contemporâneas. É importante notar que essa "
          "mudança envolve processos, cultura e modelos de negócio.\n\n"
          "Além disso, as empresas que investem em capacitação, infraestrutura "
          "e governança tendem a obter resultados superiores. Por outro lado, "
          "aquelas que negligenciam esses aspectos enfrentam dificuldades no "
          "cenário atual.\n\n"
          "Vale ressaltar que a jornada é contínua. Portanto, é essencial "
          "estabelecer métricas claras. Em suma, a transformação digital é "
          "crucial para a sustentabilidade das organizações no longo prazo.")
    HUMANO = ("Trabalho com isso há uns oito anos e no começo achei que fosse "
              "hype. Não era. Meu chefe me chamou numa terça, disse que metade "
              "do time de suporte ia embora até dezembro, e que eu tinha três "
              "meses pra montar o pipeline novo.\n\n"
              "Montei. Deu errado duas vezes. Na terceira funcionou, mais ou "
              "menos — o que ninguém te conta é que a parte difícil não é o "
              "modelo, é convencer o jurídico. Ainda estou nessa. Sei lá, acho "
              "que vou continuar nessa por um bom tempo ainda, sinceramente.")
    FORMAL_HUMANO = ("A Lei nº 14.133, de 2021, substituiu o regime anterior de "
                     "licitações. O texto foi construído ao longo de quase uma "
                     "década de tramitação, e carrega marcas dessa demora.\n\n"
                     "Na prática, os municípios menores enfrentaram o maior "
                     "custo de adaptação. Faltou pessoal treinado, faltou "
                     "sistema, e faltou jurisprudência consolidada para "
                     "orientar o gestor diante das dúvidas mais banais.\n\n"
                     "O resultado é conhecido de quem acompanha o setor. "
                     "Contratações travadas, editais republicados, e um volume "
                     "expressivo de impugnações que poderiam ter sido evitadas.")

    def test_separa_ia_de_humano(self):
        self.assertEqual(GW.avaliar_texto(self.IA)["veredito_autoria"], "PROVAVELMENTE IA")
        self.assertEqual(GW.avaliar_texto(self.HUMANO)["veredito_autoria"],
                         "PROVAVELMENTE HUMANO")

    def test_prosa_formal_humana_nao_e_acusada(self):
        # o falso positivo que mais machuca: texto humano formal NÃO pode sair
        # como "provavelmente IA"
        self.assertNotEqual(GW.avaliar_texto(self.FORMAL_HUMANO)["veredito_autoria"],
                            "PROVAVELMENTE IA")

    def test_texto_curto_e_sempre_incerto(self):
        r = GW.avaliar_texto("Além disso, portanto, é importante notar. Em suma, crucial.")
        self.assertLess(r["palavras"], 60)
        self.assertEqual(r["veredito_autoria"], "INCERTO")

    def test_confianca_cresce_com_o_tamanho(self):
        curto = GW.avaliar_texto(self.IA[:200])
        longo = GW.avaliar_texto(self.IA * 3)
        self.assertGreater(longo["confianca"], curto["confianca"])

    def test_peso_de_eixo_indisponivel_e_redistribuido(self):
        # um eixo sem dados não pode contar como zero e diluir o score
        r = GW.avaliar_texto("Além disso, é importante notar que isso é crucial.")
        indisponiveis = [n for n, v, _p in r["eixos"] if v is None]
        self.assertIn("uniformidade dos parágrafos", indisponiveis)
        self.assertGreater(r["score_autoria"], 50)


class TestSinaisEstruturais(unittest.TestCase):
    """Rodam em ``normalizar_leve`` porque dependem da vírgula — o
    ``normalizar`` do checar apaga toda a pontuação."""

    def test_triade(self):
        r = GW.avaliar_texto("Ficou rápido, simples e barato de manter.")
        self.assertEqual(r["paralelismos"], 1)

    def test_correlativo(self):
        r = GW.avaliar_texto("Não apenas rápido, mas também barato.")
        self.assertEqual(r["paralelismos"], 1)

    def test_voz_passiva(self):
        r = GW.avaliar_texto("O relatório foi considerado válido e é utilizado hoje.")
        self.assertEqual(r["passivas"], 2)

    def test_marcas_humanas(self):
        r = GW.avaliar_texto("Tipo assim, eu acho que dá pra fazer, né.")
        self.assertGreaterEqual(r["marcas_humanas"], 4)


class TestMarkdown(unittest.TestCase):
    """Resposta de chat com bullets/cabeçalhos era o formato de IA mais comum e
    saía como 'PROVAVELMENTE HUMANO': bullet sem ponto final colava tudo numa
    frase gigante (CV inflado pra 'variado') e a estrutura não era sinal."""

    LISTICLE = ("## Como melhorar sua gestão de tempo\n\n"
                "A gestão eficaz do tempo envolve três pilares fundamentais:\n\n"
                "- **Priorização**: identifique as tarefas mais importantes do dia\n"
                "- **Foco**: elimine distrações durante os blocos de trabalho\n"
                "- **Descanso**: pausas regulares mantêm a produtividade\n\n"
                "### Dicas práticas\n\n"
                "1. Use a técnica Pomodoro para manter o foco\n"
                "2. Desative notificações desnecessárias\n"
                "3. Revise suas prioridades semanalmente\n\n"
                "É importante lembrar que a consistência é mais valiosa que a "
                "perfeição. Comece com pequenas mudanças e ajuste conforme "
                "necessário.")

    @staticmethod
    def _eixo(r, nome):
        return {n: v for n, v, _p in r["eixos"]}[nome]

    def test_bullet_e_frase_propria(self):
        fr = GW.sentencas("Intro.\n- item um\n- item dois\n- item três\nFim.")
        self.assertEqual(len(fr), 5)

    def test_marcador_nao_vira_falsa_frase(self):
        # o "1." de item numerado abria uma falsa frase de uma palavra
        fr = GW.sentencas("1. Use a técnica\n2. Desative tudo")
        self.assertEqual(fr, ["Use a técnica", "Desative tudo"])

    def test_listicle_nao_sai_como_humano(self):
        r = GW.avaliar_texto(self.LISTICLE)
        self.assertNotEqual(r["veredito_autoria"], "PROVAVELMENTE HUMANO")
        self.assertEqual(self._eixo(r, "estrutura markdown"), 1.0)

    def test_prosa_corrida_nao_tem_eixo_md(self):
        # ausência de markdown não é evidência: o eixo sai da conta (None),
        # não conta como zero
        r = GW.avaliar_texto(TestAvaliar.HUMANO)
        self.assertIsNone(self._eixo(r, "estrutura markdown"))

    def test_bullet_sozinho_pesa_pouco(self):
        # humano também anota em bullet — lista de mercado não é listicle de IA
        r = GW.avaliar_texto("- comprar pão\n- pagar conta\n- ligar pro dentista")
        self.assertLessEqual(self._eixo(r, "estrutura markdown"), 0.2)


class TestRegexCorrigidos(unittest.TestCase):
    """Falsos positivos dos sinais estruturais do ``avaliar``."""

    @staticmethod
    def _eixo(r, nome):
        return {n: v for n, v, _p in r["eixos"]}[nome]

    def test_conjuncao_mais_participio_nao_e_passiva(self):
        # o fold de acento virava "é"->"e" e a CONJUNÇÃO casava com o particípio:
        # "limpo e organizado" contava como voz passiva
        r = GW.avaliar_texto("O quarto estava limpo e organizado. Deixei tudo "
                             "revisado e assinado antes de viajar.")
        self.assertEqual(r["passivas"], 0)

    def test_passiva_real_segue_detectada(self):
        r = GW.avaliar_texto("O relatório foi considerado válido e é utilizado hoje.")
        self.assertEqual(r["passivas"], 2)

    def test_participio_acentuado(self):
        # "construído"/"demolido": o sufixo com í não casava com "ido"
        r = GW.avaliar_texto("O prédio foi construído em 1980 e será demolido em breve.")
        self.assertEqual(r["passivas"], 2)

    def test_coordenacao_de_verbos_nao_e_triade(self):
        # "fui na feira, comprei tomate e voltei" é oração coordenada, não
        # tríade retórica — o padrão antigo pegava o rabo de qualquer oração
        r = GW.avaliar_texto("Fui na feira, comprei tomate e voltei pra casa.")
        self.assertEqual(r["paralelismos"], 0)

    def test_enumeracao_isolada_nao_pontua_no_eixo(self):
        r = GW.avaliar_texto("Levei pão, leite e ovos pra casa da minha mãe.")
        self.assertEqual(r["paralelismos"], 1)     # aparece na contagem…
        self.assertEqual(self._eixo(r, "paralelismo/tríade"), 0.0)  # …mas não pesa sozinha

    def test_triade_retorica_segue_detectada(self):
        r = GW.avaliar_texto("Ficou rápido, simples e barato. O plano é claro, "
                             "direto e objetivo.")
        self.assertEqual(r["paralelismos"], 2)
        self.assertGreater(self._eixo(r, "paralelismo/tríade"), 0.0)

    def test_to_ingles_nao_e_coloquial(self):
        # "to" (tô sem acento) casava com o "to" inglês — crédito aleatório
        achados = GW.RE_COLOQUIAL.findall(GW.normalizar_leve("I was scared to open it."))
        self.assertEqual(achados, [])

    def test_ingles_casual_tem_marcas_humanas(self):
        r = GW.avaliar_texto("Honestly, I think my notebook works better. "
                             "Whatever people say, I doubt an app was the "
                             "answer for me.")
        self.assertGreaterEqual(r["marcas_humanas"], 5)


class TestAncoragem(unittest.TestCase):
    """Humano ancora em específico (número, nome, sigla); IA genérica evita."""

    def test_conta_numero_nome_sigla(self):
        # Gartner (meio de frase), 58, 2024, ONU
        self.assertEqual(
            GW._ancoras_concretas("A Gartner mediu 58 bilhões em 2024, diz a ONU."), 4)

    def test_inicio_de_frase_ou_linha_nao_e_nome(self):
        # maiúscula de início de frase/linha não diz nada
        self.assertEqual(
            GW._ancoras_concretas("Comece agora. Depois revise tudo.\nUse a técnica."), 0)

    def test_marcador_de_lista_nao_e_numero(self):
        r = GW.avaliar_texto("1. Use a técnica\n2. Desative tudo\n3. Revise depois")
        self.assertEqual(r["ancoras"], 0)

    def test_rttr_none_em_texto_curto(self):
        self.assertIsNone(GW.avaliar_texto("Texto curto demais pra régua.")["rttr"])


class TestVereditoComEvidencia(unittest.TestCase):
    """O selo 'humano' exige evidência POSITIVA — IA moderna instruída a soar
    casual zera os eixos lexicais e ganhava 'PROVAVELMENTE HUMANO' de graça."""

    IA_CASUAL = ("Olha, gestão de tempo não é sobre acordar às 5 da manhã. "
                 "Sério. É sobre saber o que importa.\n\n"
                 "Passei anos tentando apps de produtividade. Todos. Nenhum "
                 "resolveu. O que resolveu foi bem mais simples: escolher três "
                 "coisas por dia. Só três.\n\n"
                 "Parece pouco? É. Mas é o que cabe num dia real, com reunião "
                 "surpresa, e-mail urgente e aquele colega que \"só precisa de "
                 "cinco minutinhos\".\n\n"
                 "E o descanso conta como tarefa. Não é frescura. Cérebro "
                 "cansado decide mal, e decisão ruim custa caro. Então anota "
                 "aí: três coisas, pausas de verdade, e o resto espera. "
                 "Funciona porque é simples. E o simples a gente mantém.")

    def test_ausencia_de_tells_nao_vira_humano(self):
        r = GW.avaliar_texto(self.IA_CASUAL)
        self.assertLessEqual(r["score_autoria"], 35)
        self.assertEqual(r["veredito_autoria"], "SEM TELLS DE IA")

    def test_marcas_humanas_dao_o_selo(self):
        self.assertEqual(GW.avaliar_texto(TestAvaliar.HUMANO)["veredito_autoria"],
                         "PROVAVELMENTE HUMANO")

    def test_ancoragem_da_o_selo_sem_coloquialidade(self):
        # prosa formal ancorada em fato (número, nome próprio) é humana sem
        # precisar de gíria — jornalismo não fala "né"
        ancorado = ("O mercado de aplicativos de produtividade movimentou 58 "
                    "bilhões de dólares no ano passado, segundo a consultoria "
                    "Gartner. O número esconde um paradoxo que pesquisadores da "
                    "Universidade de Stanford vêm documentando desde 2019: "
                    "quanto mais ferramentas um trabalhador adota, menor tende "
                    "a ser sua produção efetiva.\n\n"
                    "O fenômeno tem nome — \"productivity paradox\" — e "
                    "explicação conhecida. Cada aplicativo cobra um custo de "
                    "manutenção: configurar, organizar, migrar dados, aprender "
                    "atalhos. Esse custo raramente entra na conta de quem "
                    "instala.\n\n"
                    "A pesquisadora Gloria Mark, autora de estudo seminal "
                    "sobre atenção, mediu o tempo médio de foco contínuo em "
                    "trabalhadores de escritório: 47 segundos. Em 2004, eram "
                    "dois minutos e meio. Os aplicativos, projetados para "
                    "capturar atenção, dificilmente são neutros nesse declínio.")
        r = GW.avaliar_texto(ancorado)
        self.assertGreaterEqual(r["dens_ancoras"], 1.5)
        self.assertEqual(r["veredito_autoria"], "PROVAVELMENTE HUMANO")


class TestLimparSaida(unittest.TestCase):
    """Os modelos :free abrem com frase de serviço apesar do prompt — e ela ia
    inteira pro arquivo do ``-o``."""

    def test_tira_preambulo(self):
        self.assertEqual(GW.limpar_saida("Claro! Aqui está o texto:\nO texto real."),
                         "O texto real.")

    def test_tira_cerca_markdown(self):
        self.assertEqual(GW.limpar_saida("```\nO texto real.\n```"), "O texto real.")

    def test_preserva_texto_legitimo_com_dois_pontos(self):
        # uma primeira linha que termina em ":" mas não é preâmbulo fica
        original = "O problema é simples:\nfalta orçamento."
        self.assertEqual(GW.limpar_saida(original), original)

    def test_nao_come_linha_unica(self):
        self.assertEqual(GW.limpar_saida("Aqui está:"), "Aqui está:")


class TestLavarDelta(unittest.TestCase):
    """``lavar`` roda o ``checar`` na entrada e na saída — sem isso a ferramenta
    não tinha como dizer se a reescrita funcionou."""

    IA = ("É importante notar que o processo é fundamental. Além disso, a "
          "solução é crucial. Portanto, o resultado é essencial. Em suma, "
          "vale ressaltar que a jornada é crucial.")

    def _lavar(self, resposta, finish_reason="stop"):
        """Roda cmd_lavar com o transporte trocado por uma resposta fixa."""
        original = GW._llm.chat
        GW._llm.chat = lambda *a, **k: (resposta, "modelo-fake")
        GW._llm.last_finish_reason = finish_reason
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
                GW.cmd_lavar("media", self.IA, "")
        finally:
            GW._llm.chat = original
        return buf.getvalue()

    def test_mostra_delta_e_nao_avisa_quando_melhora(self):
        saida = self._lavar("Curto. O time levou meses pra fechar o contrato "
                            "com o fornecedor novo. Deu certo. Enfim.")
        self.assertIn("ANTES -> DEPOIS", saida.upper())
        self.assertIn("CARA DE IA", saida.upper())
        self.assertNotIn("SEM GANHO", saida.upper())

    def test_avisa_quando_reescrita_nao_melhora(self):
        saida = self._lavar(self.IA)          # devolveu o mesmo texto
        self.assertIn("SEM GANHO", saida.upper())

    def test_avisa_truncamento(self):
        saida = self._lavar("Texto cortado no meio pelo", finish_reason="length")
        self.assertIn("TRUNCADO", saida.upper())

    def test_preambulo_nao_vaza_pra_saida(self):
        saida = self._lavar("Claro! Aqui está o texto reescrito:\nO conteúdo real.")
        self.assertIn("O conteúdo real.", saida)
        self.assertNotIn("Aqui está o texto reescrito", saida)

    def test_nota_de_honestidade_no_delta(self):
        # o delta é Goodhart por construção (mede o que a reescrita ataca) —
        # a nota que avisa isso não pode sumir
        original = GW._llm.chat
        GW._llm.chat = lambda *a, **k: ("Texto reescrito qualquer aqui.", "modelo-fake")
        GW._llm.last_finish_reason = "stop"
        err = io.StringIO()
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                GW.cmd_lavar("media", self.IA, "")
        finally:
            GW._llm.chat = original
        self.assertIn("detector externo", err.getvalue())

    def test_loop_ate_insiste_e_escala_a_intensidade(self):
        intensidades, respostas = [], [
            # 1ª volta continua com cara de IA, 2ª entrega texto humano
            "É importante notar que é fundamental. Além disso, é crucial. "
            "Portanto, vale ressaltar que a jornada é essencial.",
            "Levei meses pra entender isso. No começo achei bobagem. Depois vi "
            "o estrago que dava — edital republicado três vezes, sei lá.",
        ]

        def espiao(msgs, **_kw):
            intensidades.append("PROFUNDA" if "PROFUNDA" in msgs[0]["content"]
                                else ("LEVE" if "LEVE" in msgs[0]["content"] else "MÉDIA"))
            return (respostas.pop(0) if respostas else "fim", "modelo-fake")

        original = GW._llm.chat
        GW._llm.chat = espiao
        GW._llm.last_finish_reason = "stop"
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
                GW.cmd_lavar("leve", self.IA, "", ate=30, tentativas=3)
        finally:
            GW._llm.chat = original
        self.assertEqual(intensidades, ["LEVE", "MÉDIA"])   # escalou e parou ao bater
        self.assertNotIn("META NÃO BATIDA", buf.getvalue().upper())

    def test_loop_ate_avisa_quando_nao_bate_a_meta(self):
        original = GW._llm.chat
        GW._llm.chat = lambda *a, **k: (self.IA, "modelo-fake")   # nunca melhora
        GW._llm.last_finish_reason = "stop"
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
                GW.cmd_lavar("leve", self.IA, "", ate=5, tentativas=2)
        finally:
            GW._llm.chat = original
        self.assertIn("META NÃO BATIDA", buf.getvalue().upper())

    def test_teto_de_tokens_acompanha_o_tamanho(self):
        vistos = []

        def espiao(_msgs, **kw):
            vistos.append(kw.get("max_tokens"))
            return ("ok", "modelo-fake")

        original = GW._llm.chat
        GW._llm.chat = espiao
        GW._llm.last_finish_reason = "stop"
        try:
            with contextlib.redirect_stdout(io.StringIO()), \
                 contextlib.redirect_stderr(io.StringIO()):
                GW.cmd_lavar("media", "palavra " * 2000, "")
        finally:
            GW._llm.chat = original
        # o teto fixo de 3200 cortava texto grande no meio, em silêncio
        self.assertGreater(vistos[0], 3200)


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

    def test_temas_sobrevive_codepage_legado(self):
        # o catálogo desenha '►' (U+25BA), que não existe em cp1252. No windows a
        # stdout de um pipe usa o encoding do locale, então isso morria com
        # UnicodeEncodeError (exit 1). retro.py fixa utf-8 na saída.
        out = _rodar("temas", amb_extra={"PYTHONIOENCODING": "cp1252"})
        self.assertEqual(out.returncode, 0, out.stderr.decode(errors="replace"))
        self.assertIn("►".encode(), out.stdout)

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

    def test_arquivo_ganha_do_stdin_vazio(self):
        # regressão: fora de um terminal (cron, CI, xargs) o stdin nunca é tty,
        # então o stdin vazio era lido primeiro e engolia o --arquivo, matando o
        # comando com "não recebi texto".
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
            fh.write("além disso, a solução é crucial e fundamental.")
            caminho = fh.name
        try:
            out = _rodar("checar", "--arquivo", caminho, entrada=b"")
            self.assertEqual(out.returncode, 0, out.stderr.decode(errors="replace"))
            self.assertIn(b"FORMULAS", out.stdout)
        finally:
            os.unlink(caminho)

    def test_avaliar_offline_exit0(self):
        out = _rodar("avaliar", TestAvaliar.IA)
        self.assertEqual(out.returncode, 0, out.stderr.decode(errors="replace"))
        self.assertIn(b"VEREDITO", out.stdout)
        self.assertIn("NÃO É PROVA".encode(), out.stdout)

    def test_avaliar_llm_sem_chave_cai_pro_offline(self):
        # --llm sem chave não pode matar o comando: a parte offline vale sozinha
        out = _rodar("avaliar", "--llm", TestAvaliar.IA)
        self.assertEqual(out.returncode, 0)
        self.assertIn(b"OPENROUTER_API_KEY", out.stderr)
        self.assertIn(b"VEREDITO", out.stdout)

    def test_ate_fora_da_faixa_e_recusado(self):
        out = _rodar("--ate", "150", "meu texto")
        self.assertEqual(out.returncode, 1)
        self.assertIn(b"--ate", out.stderr)

    def test_checar_mostra_veredito(self):
        out = _rodar("checar", "além disso, portanto, em suma, é importante notar.")
        self.assertEqual(out.returncode, 0)
        self.assertIn(b"CARA DE IA", out.stdout)


if __name__ == "__main__":
    unittest.main()
