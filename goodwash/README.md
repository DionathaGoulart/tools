# goodwash

Reescreve texto gerado por IA para que soe naturalmente humano — destruindo a
**assinatura estatística** da marca d'água de texto ("lista verde / lista
vermelha").

**Como funciona a watermark (e por que reescrever resolve):** a marca d'água não
carimba caracteres nem frases. Na geração, o modelo usa um hash do contexto +
chave secreta pra dividir o vocabulário em duas listas — **verde** (privilegiada)
e **vermelha** — e é enviesado a escolher tokens verdes. O detector, com a mesma
chave, mede se o texto usa tokens verdes acima do acaso. O sinal mora na
**escolha de tokens**, então qualquer **reescrita genuína** — que muda as
palavras, a ordem e a estrutura das frases — apaga o viés verde. Os papers de
watermarking documentam exatamente esse ataque (paráfrase/rewrite).

O goodwash faz isso de verdade: varia vocabulário, quebra ritmo uniforme,
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

### `goodwash checar` — tells de IA (offline)

Heurística local, sem LLM e sem chave, que aponta os padrões de estilo comuns
em texto de IA: transições/fórmulas, palavras batidas, ritmo homogêneo,
paralelismos. Material bruto do que a reescrita precisa atacar.

> Honestidade: a watermark *real* precisa da chave secreta do detector e não dá
> pra medir localmente. O `checar` é guia de estilo — não detecção oficial.

## Skill do Claude Code: `/goodwash`

Os mesmos comandos dentro do Claude Code, com uma troca: quem reescreve é o
**modelo da sessão**, não a OpenRouter. Sem chave, sem modelo `:free` — e a
conversa continua de onde o comando parou ("mais natural", "fica no tom do meu
canal").

```
/goodwash                          # reescreve o texto com intensidade média
/goodwash leve <texto>             # intensidade leve
/goodwash profunda <texto>         # intensidade profunda
/goodwash checar <texto>           # tells de IA na hora (sem chave)
```

O skill conta como a watermark funciona e entrega as diretrizes de reescrita
dentro da persona — não precisa do CLI pra nada.

Instalação:

```bash
bash ~/Desktop/tools/goodwash/setup.sh          # só o CLI (PATH no rc)
bash ~/Desktop/tools/goodwash/setup.sh --skill  # só o skill (symlink em ~/.claude/skills)
bash ~/Desktop/tools/setup.sh                   # instalador do repo: marque goodwash e/ou goodwash-skill
```

## Instalação

Precisa de Python 3. Chave da [OpenRouter](https://openrouter.ai/keys) (grátis)
só pra reescrita no CLI — o skill e o `checar` funcionam sem.

```bash
# 1. chave da API (só pro CLI lavar). Duas formas:
export OPENROUTER_API_KEY="sk-or-..."     # a) no seu rc
cp ~/Desktop/tools/goodwash/.env.example ~/Desktop/tools/goodwash/.env   # b) ou no .env

# 2. coloca o comando no PATH (uma vez):
bash ~/Desktop/tools/goodwash/setup.sh

# 3. (opcional) skill /goodwash no Claude Code — reescreve com o modelo da sessão:
bash ~/Desktop/tools/goodwash/setup.sh --skill
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