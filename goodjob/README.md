# goodjob

Copiloto de **busca de emprego** no terminal — e dentro do Claude Code.

Puxa vagas **ao vivo** de várias fontes, casa com o **seu perfil** (cargo,
stack, senioridade, local, remoto) e vira um radar rankeado. Em cima de cada
vaga o modelo gera aderência (CV × vaga), carta pro recrutador, adaptação de CV
pra ATS e kit de entrevista. Um tracker local segura o funil de candidaturas.

A **coleta é 100% APIs/feeds públicos** — sem login, sem LLM. O modelo entra só
na geração. No Claude Code, o skill `/goodjob` gera com o **Claude da sessão**
(sem chave nenhuma); no CLI standalone, a geração usa a OpenRouter.

## Fontes

| Fonte | Foco | Como |
|---|---|---|
| **Gupy** | Brasil (CLT/PJ) | API pública do portal (`employability-portal.gupy.io`) — JSON rico, com total |
| **LinkedIn** | Brasil/global | endpoint público de *guest jobs* (cards da busca sem login) |
| **Remotive** | remoto internacional | API pública `remotive.com/api` |
| **RemoteOK** | remoto internacional | API pública `remoteok.com/api` (busca por tag em inglês) |

As vagas das 4 fontes são deduplicadas (por título+empresa) e rankeadas pelo
seu perfil (keyword no título/descrição + frescor + remoto). Fonte fora do ar
não derruba o radar — o snapshot segue com as outras e registra a falha.

## Instalação

```bash
# CLI (adiciona goodjob/ ao PATH via seu rc)
bash setup.sh
source ~/.zshrc            # ou abra um terminal novo

# skill /goodjob do Claude Code (opcional, independente do CLI)
bash setup.sh --skill
```

CLI e skill são independentes: instale um, o outro, ou os dois.

## Configuração (perfil + CV)

O radar precisa saber **o que você busca**. Duas formas:

```bash
# 1) rápido: variável de ambiente
export GOODJOB_QUERY="desenvolvedor python"

# 2) completo: ~/.goodjob/perfil.json
```

```json
{
  "query": "desenvolvedor python",
  "stack": ["python", "django", "postgres", "aws"],
  "senioridade": "pleno",
  "local": "Brasil",
  "remoto": true,
  "salario_alvo": "R$ 12k",
  "evitar": ["estágio", "presencial sp"]
}
```

Cole seu **CV em texto/markdown** em `~/.goodjob/cv.md` (ou aponte `GOODJOB_CV`).
`match` e `cv` exigem o CV; `carta` e `prep` funcionam sem, mas ficam melhores
com ele.

## Comandos

```bash
goodjob                          # radar: vagas do seu perfil, rankeadas
goodjob buscar "dev react" --remoto   # busca avulsa nas 4 fontes
goodjob vagas                    # reexibe o último radar (com o índice N)
goodjob perfil                   # mostra/guia a configuração do perfil

goodjob match 3                  # aderência CV × vaga #3 + veredito
goodjob carta 3                  # carta + mensagem pro recrutador
goodjob cv 3                     # adapta o CV pra vaga (keywords/ATS)
goodjob prep 3                   # kit de entrevista (técnica + STAR)

goodjob tracker                  # funil de candidaturas
goodjob tracker add 3            # salva a vaga #3 do radar no funil
goodjob tracker mv stefanini entrevista
goodjob tracker nota stefanini "recrutador respondeu"

goodjob temas                    # paletas do tema retro
goodjob -m                       # modelos :free da OpenRouter no ar
```

O `N` de `match/carta/cv/prep/tracker add` é o número da vaga no último radar
(`goodjob vagas` pra ver). Estágios do tracker: `salvo`, `aplicado`,
`entrevista`, `oferta`, `rejeitado` — candidaturas paradas há ≥7 dias em
`aplicado`/`entrevista` acendem um alerta de **follow-up**.

### Dentro do Claude Code

`/goodjob` roda os mesmos comandos, mas a **geração é feita pelo Claude da
sessão** (o CLI só coleta via `--json`) — sem OpenRouter. O skill lê seu perfil
e CV, monta o radar e escreve match/carta/cv/prep no chat.

## Variáveis de ambiente

| Var | Pra quê |
|---|---|
| `OPENROUTER_API_KEY` | só pra geração no **CLI** (match/carta/cv/prep) |
| `OPENROUTER_MODEL` | ids `:free` separados por vírgula (sobrescreve o padrão) |
| `GOODJOB_QUERY` | o que buscar (fallback do `perfil.json`) |
| `GOODJOB_LOCAL` | local padrão da busca (LinkedIn) |
| `GOODJOB_CV` | caminho do CV (padrão `~/.goodjob/cv.md`) |
| `GOODJOB_CONTEXTO` | contexto extra do candidato, injetado na geração |
| `GOODJOB_DIR` | onde salvar perfil, cache e funil (padrão `~/.goodjob`) |
| `GOODJOB_TEMA` / `RETRO_TEMA` | paleta do terminal (`goodjob temas`) |
| `NO_COLOR` | desliga as cores |

## Privacidade

Perfil, CV, radar e funil ficam **na sua máquina** (`~/.goodjob`). No skill
`/goodjob`, nada sai pra OpenRouter — a geração é local à sessão do Claude. No
CLI, só o texto do prompt (perfil + CV + a vaga) vai pro modelo escolhido na
OpenRouter quando você roda match/carta/cv/prep. A coleta só bate nas APIs
públicas das fontes com um User-Agent de navegador.

> Endpoints públicos e não-oficiais (Gupy, LinkedIn *guest*) podem mudar sem
> aviso; quando uma fonte quebra, o radar segue com as demais e mostra a falha.
