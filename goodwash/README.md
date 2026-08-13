# goodwash

Reescreve texto gerado por IA para que soe naturalmente humano — destruindo a
**assinatura estatística** da marca d'água de texto ("lista verde / lista
vermelha").

**Como funciona a watermark:** a marca d'água não carimba caracteres nem frases.
Na geração, o modelo usa um hash do contexto + chave secreta pra dividir o
vocabulário em duas listas — **verde** (privilegiada) e **vermelha** — e é
enviesado a escolher tokens verdes. O detector, com a mesma chave, mede se o
texto usa tokens verdes acima do acaso. O sinal mora na **escolha de tokens**,
então uma **reescrita genuína** — que muda palavras, ordem e estrutura das
frases — dilui o viés verde. É o ataque de paráfrase, documentado nos papers.

**O que dá pra prometer honestamente:** dilui, não zera. O follow-up dos próprios
autores ([arXiv:2306.04634](https://arxiv.org/abs/2306.04634)) mediu isso: depois
de paráfrase **humana forte**, a watermark segue detectável observando ~800
tokens a 1e-5 de falso positivo — paráfrases vazam n-grams. Na prática: **texto
curto (algumas centenas de tokens) sai limpo; texto longo só perde confiança.**

Dois avisos que valem mais que a watermark no dia a dia:

- Quem reescreve é **outro LLM**. Contra detector *estatístico* de watermark
  isso funciona; contra detector *estilométrico* (GPTZero, Turnitin — que é o
  que a maioria enfrenta, já que só o Google publica watermark de texto em
  escala) você pode trocar estilo de IA A por estilo de IA B. Por isso o `lavar`
  roda o `checar` na entrada **e na saída** e mostra o delta: se o score não
  caiu, não adiantou.
- Se o modelo reescritor for watermarked, você troca uma marca por outra. Os
  modelos `:free` padrão daqui são open-weights (Llama/Qwen/Nemotron), sem
  watermark — trocou de modelo, confira.

O goodwash reescreve de verdade: varia vocabulário, quebra ritmo uniforme,
desmonta paralelismos e tríades, troca transições fórmula e mantém **os mesmos
fatos e o tom**. Nada de trocar sinônimo por sinônimo.

> Uso responsável: a força da ferramenta é tornar o texto natural e legível.
> Não é pra fraudar avaliação acadêmica, spam ou desinformação.

```bash
goodwash "seu texto aqui"         # reescrita média (padrão)
goodwash leve "seu texto"         # leve: lixa as arestas de IA
goodwash profunda "seu texto"     # profunda: parece escrito do zero
goodwash arquivo.txt              # reescreve o conteúdo do arquivo
echo "texto" | goodwash           # ou leia do stdin
goodwash -o saida.txt "texto"     # salva a reescrita em arquivo
goodwash --ate 30 "texto"         # reescreve até a auto-avaliação bater a meta
goodwash avaliar "texto"          # IA ou humano? veredito + confiança (offline)
goodwash avaliar --llm "texto"    # + segunda opinião do modelo
goodwash checar "texto"           # tells de IA offline (0 LLM, sem chave)
goodwash temas                    # paletas do terminal retrô
goodwash -m                       # modelos :free disponíveis no momento
```

---

## Comandos

### `goodwash lavar [leve|media|profunda]` — a reescrita

Pega o texto de três jeitos: argumento, arquivo ou stdin (pipe). Intensidade
`leve` lixa só as arestas, `profunda` reescreve do zero — a média é o padrão.

O prompt de reescrita (o mesmo no CLI e no skill) ataca os rastros de texto IA:

- **vocabulário** — troca jargão e palavra batida por palavra comum e precisa
- **ritmo** — frases de tamanhos variados, não o comprimento equilibrado de IA
- **estrutura** — quebra paralelismos, tríades e transições fórmula
- **parágrafos** — tamanhos variados, ordem das ideias mexida onde ficar natural
- **voz** — linguagem concreta, expressões idiomáticas, leve informalidade

Regras inegociáveis (codificadas no prompt): **sem inventar nada** — preserva
significado, tom e fatos; responde só com o texto reescrito.

**Auto-avaliação.** Ao fim, o `lavar` roda o `avaliar` na entrada e na saída e
imprime o delta de cada eixo. Se o score não caiu, ele avisa em vez de fingir
sucesso. O teto de tokens acompanha o tamanho do texto e, se ainda assim o
modelo cortar no meio, sai um aviso de `truncado`.

> Honestidade sobre o delta: ele mede **os mesmos eixos que o prompt de
> reescrita ataca** — cair é o esperado, não uma prova. Score baixo aqui não é
> aprovação em detector externo (GPTZero, Turnitin medem perplexidade e
> burstiness, que ficam fora do alcance offline).

Com `--ate` ele fecha o loop sozinho: reescreve, se avalia, e **insiste com a
intensidade escalada** (`leve` → `media` → `profunda`) enquanto não bater a
meta. Fica com a melhor tentativa e avisa se não chegou lá.

```bash
goodwash --ate 30 "seu texto"                 # até 3 tentativas (padrão do --ate)
goodwash --ate 20 --tentativas 5 arquivo.txt  # insiste mais
```

### `goodwash avaliar` — IA ou humano?

O detector. Roda offline, dá **veredito + confiança** e mostra os eixos que
levaram até ele:

| Eixo | O que mede | Peso |
|---|---|---|
| Transições fórmula | por 100 palavras ("além disso", "portanto"…) | 22% |
| Ritmo das frases | coeficiente de variação do tamanho | 22% |
| Palavras batidas | jargão de IA por 100 palavras, com flexão de plural | 13% |
| Marcas humanas | coloquialismo e 1ª pessoa (`pra`, `né`, `acho que`) | 13% |
| Paralelismo/tríade | "rápido, simples e barato", "não apenas… mas também" | 12% |
| Estrutura markdown | rótulo em negrito ("**Foco**: …"), cabeçalho + lista | 12% |
| Voz passiva | "foi considerado", "são utilizados" | 10% |
| Uniformidade dos parágrafos | CV do tamanho dos parágrafos | 10% |
| Ancoragem concreta | número, nome próprio, sigla por 100 palavras — humano ancora, IA genérica evita | 8% |
| Repetitividade lexical | root TTR numa janela de 200 tokens | 8% |
| Variedade de pontuação | quantos tipos expressivos (`—`, `(`, `;`, `…`) | 8% |

As transições fórmula combinam lista literal com **famílias por padrão**
("é importante/fundamental/essencial + notar/ressaltar/destacar/lembrar…",
"ademais", "dito isso", "em síntese") — variante trivial não escapa mais da
lista fixa.

Eixo que não dá pra medir (texto curto, menos de 4 frases, menos de 3
parágrafos, prosa corrida sem markdown) tem o peso **redistribuído** entre os
que sobraram, em vez de contar como zero. Uma enumeração isolada ("pão, leite
e ovos") e oração coordenada ("comprei tomate e voltei") não contam como
tríade; bullet sozinho pesa pouco no eixo de markdown — humano também anota
assim. Linha de bullet/cabeçalho conta como frase própria no ritmo. Confiança cresce com o tamanho do texto e com a distância do
meio-termo; abaixo de 60 palavras o veredito é sempre `INCERTO`.

Faixas: `≥65` provavelmente IA · `36-64` incerto · `≤35` **com evidência
positiva** (marca humana ou ancoragem concreta) provavelmente humano. Score
baixo **sem** evidência positiva sai como `SEM TELLS DE IA` — não é selo de
humanidade: IA moderna instruída a soar casual zera os eixos lexicais, e
ausência de tell não prova autor.

```bash
goodwash avaliar "texto"          # offline, 0 LLM, sem chave
goodwash avaliar --llm "texto"    # + segunda opinião do modelo (JSON: veredito,
                                  #   confiança, motivos, trechos citados)
```

> ⚠️ **Não é prova.** Detector de texto de IA erra, e erra pro lado feio. Prosa
> formal, técnica ou traduzida é o falso positivo clássico — usa as mesmas
> transições e a mesma voz passiva que os eixos punem. Nas amostras de teste um
> texto jurídico escrito por humano dá **46 (incerto)**, não "humano": a
> ferramenta é calibrada pra dizer *não sei* em vez de acusar. Use pra medir o
> **seu** texto, nunca pra julgar o de outra pessoa.

### `goodwash checar` — tells de IA (offline)

Versão enxuta do `avaliar`, focada em *o que consertar*: só fórmulas de
transição, palavras batidas e ritmo (pesos 40/25/35), com o contexto de cada
ocorrência no texto. Use `avaliar` pra saber "é IA?" e `checar` pra saber "onde
mexer".

> Honestidade: a watermark *real* precisa da chave secreta do detector e não dá
> pra medir localmente. Os dois comandos são score de estilo — não detecção
> oficial de watermark.

## Skill do Claude Code: `/goodwash`

Os mesmos comandos dentro do Claude Code, com uma troca: quem reescreve é o
**modelo da sessão**, não a OpenRouter. Sem chave, sem modelo `:free` — e a
conversa continua de onde o comando parou ("mais natural", "fica no tom do meu
canal").

```
/goodwash                          # reescreve o texto com intensidade média
/goodwash leve <texto>             # intensidade leve
/goodwash profunda <texto>         # intensidade profunda
/goodwash avaliar <texto>          # IA ou humano? veredito + confiança + evidência
/goodwash checar <texto>           # tells de IA na hora (sem chave)
```

O skill conta como a watermark funciona e entrega as diretrizes de reescrita
dentro da persona — não precisa do CLI pra nada.

Instalação:

```bash
# do diretório do repo (git clone … && cd tools)
bash goodwash/setup.sh          # só o CLI (PATH no rc)
bash goodwash/setup.sh --skill  # só o skill (symlink em ~/.claude/skills)
bash setup.sh                   # instalador do repo: marque goodwash e/ou goodwash-skill
```

## Instalação

Precisa de Python 3. Chave da [OpenRouter](https://openrouter.ai/keys) (grátis)
só pra reescrita no CLI — o skill e o `checar` funcionam sem.

```bash
# 1. chave da API (só pro CLI lavar). Duas formas:
export OPENROUTER_API_KEY="sk-or-..."    # a) no seu rc
cp goodwash/.env.example goodwash/.env   # b) ou no .env

# 2. coloca o comando no PATH (uma vez):
bash goodwash/setup.sh

# 3. (opcional) skill /goodwash no Claude Code — reescreve com o modelo da sessão:
bash goodwash/setup.sh --skill
```

## Configuração

| Variável | Pra quê | Padrão |
|---|---|---|
| `OPENROUTER_API_KEY` | reescrita via CLI (`lavar`) | — |
| `OPENROUTER_MODEL` | modelos a tentar, separados por vírgula | lista de modelos `:free` |
| `GOODWASH_TEMA` | paleta do terminal só pro goodwash | `vault-gold` |
| `RETRO_TEMA` | paleta padrão de todas as ferramentas do repo | `vault-gold` |
| `NO_COLOR` | desliga as cores | desligado |

## Privacidade

O texto que você manda pro modelo vai pra OpenRouter (`:free` pode ser usado pra
treino) — não cole informação sensível. O `checar` roda 100% local.

---

↩ [Voltar pro índice de ferramentas](../README.md)