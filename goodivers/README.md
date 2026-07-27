# goodivers

Copiloto de conteúdo do canal [Goodivers](https://www.youtube.com/@Goodivers)
(Helldivers 2). Helldivers 2 é jogo-serviço: Ordem Maior, patch e warbond
mudam toda semana — e é dessa janela que nasce vídeo bom. O goodivers puxa o
estado **ao vivo** do jogo e do nicho e usa isso pra gerar ideias, títulos,
thumbnails e roteiro pensados pro algoritmo do YouTube em canal pequeno.

**Nada roda sozinho**: zero monitoramento em background, zero cron. Toda
coleta e toda chamada de modelo acontecem só quando você digita um comando.
A coleta de `radar`, `buscar` e `patch` não usa LLM (APIs públicas, sem
chave); o modelo (OpenRouter `:free`) entra em `ideias`, `inspirar`, `pacote`,
`titulos` — e numa chamada de tradução pra exibir radar e patch em PT-BR
(`--original` pula).

Dois jeitos de usar a parte com IA — mesmos comandos nos dois:

| Onde | Modelo | Precisa |
|---|---|---|
| Terminal: `goodivers ideias` | OpenRouter `:free` | `OPENROUTER_API_KEY` |
| Claude Code: `/goodivers ideias` | Claude da sessão | nada (usa sua sessão) |

```bash
goodivers                       # radar: guerra, patches, reddit e canais do nicho
goodivers ideias                # 10 ideias de vídeo rankeadas
goodivers inspirar              # vídeos gringos performando → plano de adaptação PT-BR
goodivers pacote 3              # pacote de produção completo da ideia 3
goodivers titulos "farm de sc"  # 8 variações de título pra teste A/B
goodivers buscar "hd2 leaks" -s # busca no YouTube (-s semana · --br como o público BR)
goodivers patch                 # lista os patch notes oficiais (Steam)
goodivers patch 2               # corpo completo de um patch em PT-BR (--original: cru)
goodivers canais                # gerencia os canais monitorados
goodivers temas                 # paletas do tema retro do terminal
```

---

## Comandos

### `goodivers` — o radar (padrão)

Fotografia do momento, coletada em paralelo (**a coleta é sem LLM e sem chave**):

| Seção | O que mostra | Fonte |
|---|---|---|
| Ordem Maior (janela do topo) | a missão comunitária ativa + prazo + medalhas | [api.helldivers2.dev](https://api.helldivers2.dev) |
| Despachos da Super Terra | as notícias in-game (a "TV" do jogo) | api.helldivers2.dev |
| Oficial · Steam | anúncios da Arrowhead no Steam — patch notes inclusos | Steam News API |
| Quente no r/Helldivers | posts em alta (best-effort: Reddit bloqueia alguns IPs; o radar segue sem) | Reddit |
| Canais do nicho | últimos vídeos de cada canal monitorado, com views e idade | RSS público do YouTube |
| Seu canal · Goodivers | seus vídeos e views, sempre à vista | RSS público do YouTube |

O chip **`[OUTLIER]`** é o sinal mais importante: vídeo com views/dia ≥ 2× a
mediana do próprio canal = formato que o algoritmo está empurrando **agora**.

Detalhes de comportamento:

- **Tradução PT-BR é o padrão:** o radar é exibido em português via uma chamada
  de LLM (mensagens do jogo traduzidas; títulos dos canais mostram o original +
  linha `↳ <PT-BR>`). Use **`--original`** pra ver o dado cru em inglês, sem
  LLM. `GOODIVERS_ORIGINAL=1` deixa o cru como padrão. Sem `OPENROUTER_API_KEY`
  o radar cai pro inglês automaticamente (avisa e segue). A **coleta** e o
  cache continuam crus; `--json` nunca traduz.
- O snapshot fica em cache por **6 horas** (`~/.goodivers/radar.json`) — os
  outros comandos reaproveitam sem recoletar. `-f` força recoleta.
- Fonte fora do ar? O radar reaproveita a última coleta boa daquela seção e
  avisa a idade do dado no rodapé. Nenhuma fonte derruba as outras.
- **Quando usar:** de manhã, todo dia. Ordem Maior nova ou patch = janela de
  newsjacking aberta.

### `goodivers ideias`

Injeta o radar inteiro no modelo e devolve **10 ideias rankeadas da melhor
pra pior**, misturando por design: 2–3 newsjacking da janela atual, 3–4
busca evergreen (dicas, guias, farm), 2 adaptações de vídeo gringo que está
performando (citando o original) e 1 short.

Cada ideia traz:

- **título pronto** (≤60 chars, keyword na frente)
- **ângulo** — o que o vídeo entrega e por que clicariam
- **por que agora** — amarrado aos dados ao vivo (patch, Ordem, outlier…)
- **esforço** de produção e **potencial** (baixo/médio/alto)
- **termos de busca** (em chips) — como o brasileiro pesquisaria isso
- **link** do vídeo original (só nas ideias de adaptação de vídeo gringo)

A última leva fica salva (`~/.goodivers/ideias.json`) e `goodivers pacote N`
puxa a ideia N direto. Toda leva também é arquivada no histórico
(`~/.goodivers/ideias_hist.jsonl`):

- `goodivers ideias --ver`: mostra a **última leva** sem regerar (0 LLM)
- `goodivers ideias --hist`: lista as levas anteriores (datadas)
- `goodivers ideias --hist N`: abre a leva N do histórico

### `goodivers inspirar`

A estratégia do canal em um comando: o nicho gringo de Helldivers 2 é
gigante e o PT-BR está quase vazio — então **o que performa lá fora é
matéria-prima validada** pra versão brasileira.

O que ele faz, na ordem:

1. Varre os canais monitorados (os `[OUTLIER]` do radar)
2. Busca no YouTube gringo os vídeos da semana: `helldivers 2` e
   `helldivers 2 leaks`
3. Busca o que **já existe em PT-BR** na semana (pra não repetir o que o BR
   já cobriu — e pra te mostrar o tamanho do buraco)
4. O modelo escolhe os **6 melhores candidatos a adaptação** e devolve, pra
   cada um: vídeo original + canal, por que performou, **título PT-BR
   pronto**, o que mudar/cortar/adicionar pro público BR, e **o que checar
   no jogo antes de gravar** (pra não publicar guia desatualizado).

> Adaptar = re-roteirizar com a sua gameplay e o seu contexto. Nunca
> tradução 1:1 — reused content mata canal.

**Fluxo:** `inspirar` → escolheu um plano → `pacote "<título escolhido>"`.

### `goodivers pacote <N | "ideia">`

Pacote de produção completo de UM vídeo. Aceita o número de uma ideia salva
(`pacote 3`) ou texto livre (`pacote "guia solo dificuldade 10"`). Devolve:

- **5 títulos** com ângulos diferentes (avisa em vermelho se passar de
  60 chars) — pra escolher ou testar
- **3 conceitos de thumbnail** — texto de ≤4 palavras em maiúsculas,
  composição descrita (fundo, ponto focal, cor, emoção) e **prompt de
  imagem em inglês pronto** pra colar numa IA de imagem. São 3 porque o
  YouTube testa até 3 thumbs no Test & Compare.
- **Descrição pronta** — 2 primeiras linhas carregam as keywords (é o
  que o YouTube lê primeiro)
- **12–18 tags** misto PT/EN
- **Hook dos primeiros 30s** — roteiro literal, em 1ª pessoa
- **Roteiro em beats** — minuto a minuto, cada beat com a razão de
  retenção

### `goodivers titulos "<tema>"`

Atalho quando você já sabe o vídeo e só quer packaging: 8 títulos com
ângulos variados (número, pergunta, contraste, urgência), todos ≤60 chars,
cada um com o gatilho de clique explicado. Mais rápido e barato que `pacote`.

### `goodivers buscar "<termo>" [-s] [--br]`

Busca real no YouTube (scraping da página de resultados — **sem chave, sem
LLM**). Mostra views, idade, duração, canal e título de até 15 resultados.

| Flag | Efeito | Uso típico |
|---|---|---|
| `-s` / `--semana` | só vídeos desta semana | o que está quente agora |
| `--br` | busca como o público BR vê (gl=BR, hl=pt) | medir concorrência PT-BR |
| (sem flags) | busca gringa, sem filtro de data | validar demanda evergreen |

Cada busca é cacheada por **6h** (`~/.goodivers/busca.json`, chave =
`termo + -s + --br`), então repetir a mesma busca é instantâneo e o `inspirar`
(que dispara 3 buscas fixas) reusa o cache. `-f` fura e recoleta.

Exemplos:

```bash
goodivers buscar "helldivers 2 leaks" -s      # novidades/vazamentos da semana
goodivers buscar "helldivers 2 dicas" --br    # o que o BR encontra ao buscar isso
goodivers buscar "helldivers 2 solo build"    # tem demanda? quem já cobriu?
```

### `goodivers patch [<N | url>]`

Patch notes oficiais da Arrowhead direto do Steam. Sem argumento, lista os
anúncios recentes numerados (mais novo primeiro) com título e idade — coleta
pura, sem LLM. Com um número (`1` = mais recente) ou a URL do anúncio colada,
baixa o **corpo inteiro** daquele patch — listas de buff/nerf e cabeçalhos
preservados — e exibe **traduzido pra PT-BR** (uma chamada de LLM; nomes
próprios do jogo ficam em inglês). `--original` mostra o texto cru em inglês,
sem LLM; sem `OPENROUTER_API_KEY` cai pro inglês sozinho, nunca quebra.

O **resumo estruturado pro vídeo de atualização** (TL;DR, buffs, nerfs, novo
conteúdo, fixes que importam, ângulo de título/thumb) é gerado pelo Claude via
skill: `/goodivers patch <N>`. O `--json` expõe a lista e o corpo crus.

A coleta é cacheada por **6h** (`~/.goodivers/patch.json`) — patch não sai
todo dia, e a mesma coleta serve a lista e o corpo de qualquer patch; `-f`
fura e recoleta. A **tradução** fica em cache **permanente** por anúncio
(`~/.goodivers/patch_pt.json`): patch note publicado não muda — mudança vem em
patch novo — então cada patch é traduzido uma única vez.

```bash
goodivers patch            # lista os patch notes oficiais recentes
goodivers patch 2          # corpo completo do 2º da lista, em PT-BR
goodivers patch 2 --original   # o mesmo, cru em inglês (sem LLM)
goodivers patch <url>      # ou cole a URL do anúncio do Steam
```

### `goodivers canais [add <x> | rm <x>]`

Gerencia os canais que o radar e o `inspirar` monitoram via RSS.

```bash
goodivers canais                 # lista
goodivers canais add @canal      # aceita @handle, URL de canal ou ID UC…
goodivers canais rm nome         # remove por nome (ou ID)
```

Seeds padrão (todos verificados, todos gringos de propósito — o que
performa lá é matéria-prima pra versão PT-BR):

| Canal | Perfil |
|---|---|
| Glitch Unlimited | news/leaks — o maior do nicho |
| MichelleFreeHugs | updates e testes |
| OhDough Plays | meta/loadouts |
| ThiccFilA | news/opinião |
| CommissarKai | gameplay/humor |

### `goodivers temas`

Lista as paletas do tema retro do terminal — o mesmo visual do resto das
ferramentas deste repo (`.harness/styleguide-terminal.md`). Mostra o swatch
de cada tema e marca com `►` o que está ativo.

```bash
goodivers temas                      # catálogo de paletas
export GOODIVERS_TEMA=midnight-ember # tema só do goodivers
export RETRO_TEMA=cyber-teal         # tema de todas as ferramentas
```

Temas disponíveis: `vault-gold` (padrão), `noir-rose`, `midnight-ember`,
`cyber-teal`, `velvet-purple`, `abyss-frost`, `crimson-chalk`,
`forest-mist`, `sand-dusk`.

`GOODIVERS_TEMA` tem prioridade sobre `RETRO_TEMA`. Com `NO_COLOR=1` ou
saída redirecionada (pipe, arquivo), a cor some e o layout continua legível.

### Flags globais

| Flag | Faz |
|---|---|
| `-f` / `--fresh` | ignora o cache de 6h e recoleta agora (radar e buscas) |
| `--original` | (radar) não traduz, mostra o dado cru em inglês, sem LLM (`GOODIVERS_ORIGINAL=1` liga por padrão) |
| `-m` / `--modelos` | lista os modelos `:free` disponíveis na OpenRouter agora |
| `--json` | saída JSON crua de `radar`, `buscar`, `patch` e `canais` — pra scripts e pro skill `/goodivers` |

## Skill do Claude Code: `/goodivers`

Os mesmos comandos dentro do Claude Code, com uma troca: quem gera é o
**Claude da sessão**, não a OpenRouter. Sem chave, sem modelo `:free`, sem
loteria de qual modelo está no ar — e a conversa continua de onde o comando
parou ("agora encurta esses títulos", "troca a thumb 2").

```
/goodivers                      # radar renderizado em markdown
/goodivers ideias               # 10 ideias rankeadas (geradas pelo Claude)
/goodivers pacote 3             # pacote completo da ideia 3
/goodivers inspirar             # gringo → plano de adaptação PT-BR
/goodivers titulos "farm de sc" # 8 variações A/B
```

Como funciona por baixo: o skill chama o CLI com `--json` só pra **coletar**
(radar, buscas) e o Claude assume a **geração** com a mesma persona e os
mesmos formatos do CLI. As ideias vão pro mesmo `~/.goodivers/ideias.json` —
`ideias` no terminal + `/goodivers pacote 2` no Claude Code (e vice-versa)
funcionam juntos.

CLI e skill instalam separado — um, outro ou os dois:

```bash
bash ~/Desktop/tools/goodivers/setup.sh          # só o CLI (PATH no rc)
bash ~/Desktop/tools/goodivers/setup.sh --skill  # só o skill (symlink em ~/.claude/skills)
bash ~/Desktop/tools/setup.sh                    # instalador do repo: marque goodivers e/ou goodivers-skill
```

O CLI precisa estar no PATH pro skill funcionar — é ele que coleta.

## Instalação

Precisa de Python 3. Chave da [OpenRouter](https://openrouter.ai/keys)
(grátis) só pros comandos de geração — `radar` e `buscar` funcionam sem.

```bash
# 1. chave da API. Duas formas (escolha uma):
#    a) no seu rc (~/.zshrc, ~/.bashrc, ~/.bash_profile):
export OPENROUTER_API_KEY="sk-or-..."
#    b) ou num .env dentro desta pasta:
cp ~/Desktop/tools/goodivers/.env.example ~/Desktop/tools/goodivers/.env
#    e edite o .env com sua chave (o .env não é versionado).

# 2. coloca o comando no PATH (uma vez) — direto:
bash ~/Desktop/tools/goodivers/setup.sh
#    ou pelo instalador interativo do repo (goodivers e goodivers-skill separados):
bash ~/Desktop/tools/setup.sh

# 3. (opcional) skill /goodivers no Claude Code — gera com o Claude, sem chave:
bash ~/Desktop/tools/goodivers/setup.sh --skill
```

> A variável exportada no shell tem prioridade sobre o `.env`.

### Lembrete diário (opcional)

Adicione antes da linha de `source` no seu rc pra ser avisado uma vez por
dia, ao abrir o terminal, se ainda não viu o radar:

```bash
export GOODIVERS_LEMBRETE=1
```

## Configuração

| Variável | Pra quê | Padrão |
|---|---|---|
| `OPENROUTER_API_KEY` | sua chave (obrigatória só p/ gerar) | — |
| `OPENROUTER_MODEL` | modelos a tentar, separados por vírgula | lista de modelos `:free` |
| `GOODIVERS_CONTEXTO` | contexto extra do canal injetado em toda geração (equipamento, estilo de edição, tempo disponível…) | nenhum |
| `GOODIVERS_DIR` | onde salvar cache e config | `~/.goodivers` |
| `GOODIVERS_ORIGINAL` | `1` mostra o radar cru em inglês por padrão (sem tradução/LLM) | desligado |
| `GOODIVERS_LEMBRETE` | `1` liga o lembrete diário no terminal | desligado |
| `GOODIVERS_TEMA` | paleta do terminal só pro goodivers (`goodivers temas` lista) | `vault-gold` |
| `RETRO_TEMA` | paleta padrão de todas as ferramentas do repo (fallback) | `vault-gold` |
| `NO_COLOR` | qualquer valor desliga a cor (layout segue legível) | desligado |

## Privacidade

Tudo que vai no prompt é público: estado da guerra, patch notes, posts do
Reddit e títulos/views de vídeos do YouTube. Nada pessoal. Cache e config
ficam em `~/.goodivers/`.

## Fluxo recomendado

```bash
goodivers                # manhã: patch novo? Ordem nova? outlier no nicho?
goodivers ideias         # janela aberta → ideias rankeadas
goodivers inspirar       # ou: o que o gringo provou que funciona esta semana?
goodivers pacote 2       # escolheu → pacote completo, só gravar
```

---

↩ [Voltar pro índice de ferramentas](../README.md)
