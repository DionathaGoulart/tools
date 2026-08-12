# tools

Coleção de ferramentas de terminal pro meu dia a dia como desenvolvedor. Scripts leves, portáteis e sem dependências — funcionam em macOS, Linux e Windows (Git Bash / WSL).

## Índice

| Ferramenta | Comando | O que faz |
|---|---|---|
| **Terminal** | | |
| [goodhelp](./goodhelp) | `goodhelp` | Mapa da família good*: lista o que está instalado e abre a ajuda de cada uma — vem junto automaticamente com qualquer ferramenta |
| [goodcheats](./goodcheats) | `good` / `goodcheat` / `goodharness` | Kit de utilidades da família good: fetch de sistema + cheatsheets + styleguides |
| [goodpomo](./goodpomo) | `goodpomo` | Pomodoro com notificação nativa e estatísticas |
| [goodnerd](./goodnerd) | `goodnerd` | Teatro de "hacker" fake no terminal, pra impressionar os leigos |
| **IA** (OpenRouter `:free`) | | |
| [goodprof](./goodprof) | `goodprof` | Estudo Feynman invertido: te sabatina até você dominar |
| [goodbio](./goodbio) | `goodbio` | Sua autobiografia, uma pergunta por dia |
| [goodvocab](./goodvocab) | `goodvocab` | Uma palavra de inglês por dia, com revisão espaçada |
| [goodzap](./goodzap) | `goodzap` | Retrô de uma conversa exportada do WhatsApp |
| [goodivers](./goodivers) | `goodivers` | Copiloto do canal de Helldivers 2: radar ao vivo do jogo + ideias, títulos e thumbs |
| [goodjob](./goodjob) | `goodjob` | Copiloto de busca de emprego: radar de vagas ao vivo (Gupy, LinkedIn, Remotive, RemoteOK) + aderência, carta, CV e prep |
| [dark](./dark) | `dark` | Copiloto do Instagram @darkning.art (horror art): radar do nicho + ideias, pacotes, captions e stories em inglês |
| [goodwash](./goodwash) | `goodwash` | Reescreve texto de IA pra soar humano e sair da marca d'água estatística (lista verde/vermelha) |
| **Imagens** | | |
| [images/goodpixel](./images/goodpixel) | `goodpixel` | Transforma imagens (png/jpg/svg/webp/…) em pixel art com paletas clássicas |
| [images/goodprofile](./images/goodprofile) | `goodprofile` | Encaixa imagens nos tamanhos prontos de perfil/rede social: presets de avatar/capa/favicon, corte com foco, troca de cor, centralização e máscara redonda |
| **Senhas** | | |
| [goodpen](./goodpen) | `cofre` / `pass` | Cofre de senhas criptografado, backup em pendrive (2 versões) |

Toda ferramenta responde a `<ferramenta> help` (ex: `goodivers help`, `goodpomo help`) — e `goodhelp` lista as que você tem instaladas. Ele não se instala sozinho: vem junto, automaticamente, ao instalar qualquer ferramenta. O contador `N/M` conta só o que o instalador da raiz oferece; o goodpen tem setup próprio e só entra na conta depois de instalado. `goodhelp doctor` checa a instalação inteira quando algo não aparece no `PATH`.

## Instalação

Clone onde quiser — o repo não precisa ficar em lugar nenhum específico:

```bash
git clone https://github.com/DionathaGoulart/tools.git
cd tools
```

Jeito rápido: o instalador interativo da raiz lista tudo, você marca o que quer (`1-9` marca, `a` todos, `n` nenhum, `Enter` instala). Ele se ajusta à altura do terminal (mostra mais itens por página em janelas altas) e marca com `[✓]` verde o que já está instalado:

```bash
bash setup.sh        # instalar (marque e dê Enter)
bash setup.sh -u     # desinstalar (lista só as instaladas)
```

Ou individualmente — cada ferramenta tem um `setup.sh` que a adiciona ao `PATH`:

```bash
bash goodcheats/setup.sh
bash goodpomo/setup.sh
bash goodnerd/setup.sh
bash goodprof/setup.sh
bash goodbio/setup.sh
bash goodvocab/setup.sh
bash goodzap/setup.sh
bash goodivers/setup.sh
bash goodivers/setup.sh --skill   # skill /goodivers do Claude Code
bash goodjob/setup.sh
bash goodjob/setup.sh --skill     # skill /goodjob do Claude Code
bash goodwash/setup.sh
bash goodwash/setup.sh --skill    # skill /goodwash do Claude Code
bash images/goodpixel/setup.sh
bash images/goodprofile/setup.sh
```

Depois abra um terminal novo (ou `source ~/.zshrc`). O goodpen tem setup próprio e fica de fora do instalador.

### Onde isso mexe

O instalador escreve **um bloco só** no seu rc (`~/.zshrc` ou `~/.bashrc`), ancorado num symlink `~/.goodtools` que aponta pro repo:

```bash
# >>> good tools >>>
export GOODTOOLS_ROOT="$HOME/.goodtools"
if [ -r "$GOODTOOLS_ROOT/load.sh" ]; then
  . "$GOODTOOLS_ROOT/load.sh"
  goodtools_load goodcheats goodivers images/goodpixel
else
  echo "good tools: $GOODTOOLS_ROOT não resolve — repo moveu ou sumiu?" >&2
fi
# <<< good tools <<<
```

Consequências práticas:

- **Mudou o repo de lugar?** Um comando, e o rc não muda: `ln -sfn /caminho/novo/tools ~/.goodtools`
- **Alguma coisa quebrou?** O shell avisa na abertura, com o conserto na mensagem — nunca falha calado. `goodhelp doctor` mostra âncora, bloco do rc, PATH e skills, item por item.
- **Instalou na versão antiga** (uma linha com caminho absoluto por ferramenta)? Rodar qualquer `setup.sh` migra sozinho: as linhas velhas saem, o que ainda existe entra na lista do bloco.
- **Desinstalar** tira o nome da lista; a última ferramenta leva o bloco e o symlink junto. Backup do rc em `<rc>.tools-backup`.
- **Windows sem Developer Mode**, onde o symlink não rola: o bloco cai pro caminho absoluto do repo e o instalador avisa. Funciona igual, só que mover o repo pede reinstalar.

**Ferramentas de IA** também precisam de uma chave grátis da [OpenRouter](https://openrouter.ai/keys). No seu rc:

```bash
export OPENROUTER_API_KEY="sk-or-..."
```

Ou, por ferramenta, copie o `.env.example` da pasta pra `.env` e preencha (o `.env` não é versionado; o env do shell tem prioridade):

```bash
cp ~/Desktop/tools/goodprof/.env.example ~/Desktop/tools/goodprof/.env
```

> ⚠️ Prompts enviados a modelos `:free` podem ser usados pra treino. Nenhuma ferramenta manda dado sensível por padrão — mas leia a nota de privacidade no README de cada uma antes de colar coisa pessoal.

## Visual

Todas as ferramentas seguem o mesmo style guide de terminal retrô — bordas retas,
sombra offset, rótulos em CAIXA ALTA, uma cor de acento só. A especificação está em
[`.harness/styleguide-terminal.md`](./.harness/styleguide-terminal.md) e o código
compartilhado em [`lib/retro.sh`](./lib/retro.sh) (bash) e [`lib/retro.py`](./lib/retro.py) (python).

Nove paletas, as mesmas do portfólio. Troque global ou por ferramenta:

```bash
export RETRO_TEMA=cyber-teal     # vale pra todas
export GOODPOMO_TEMA=noir-rose       # só o goodpomo (<FERRAMENTA>_TEMA tem prioridade)
goodpomo temas                       # catálogo com swatches; qualquer ferramenta aceita `temas`
```

Paletas: `vault-gold` `noir-rose` `midnight-ember` `cyber-teal` `velvet-purple`
`abyss-frost` `crimson-chalk` `forest-mist` `sand-dusk`.
`NO_COLOR=1` ou saída redirecionada derruba tudo pra texto puro.

---

## Terminal

### [goodcheats](./goodcheats)
Kit de utilidades da família good — uma pasta, um `setup.sh`, vários comandos com prefixo `good` (todos também acessíveis como subcomando: `good cheat …`, `good harness …`):

- **`good`** — fetch de sistema estilo neofetch, com o logo good em ASCII art colorido. Mostra OS, kernel, uptime, CPU, GPU, memória, disco, pacotes e bateria.
- **`goodcheat`** — cheatsheets de comandos que eu sempre esqueço. Mais rápido que abrir o Google.
- **`goodharness`** — biblioteca de styleguides: copia o styleguide de um projeto como predefinição e instala em outro (`.harness/styleguide.md`).

```bash
good               # logo + infos do sistema
good -c fbee23     # logo em outra cor (ou gradiente: fbee23,ff5500)
goodcheat tar      # ver colinha (= good cheat tar)
goodcheat -l       # listar todas
goodcheat -s porta # buscar termo dentro de todas
goodcheat -e docker # editar ou criar nova
good harness list                       # predefinições de styleguide salvas
good harness copy meu-tema ~/meu/site   # salva styleguide do projeto
good harness install meu-tema .         # instala no projeto atual
```

### [goodpomo](./goodpomo)
Pomodoro no terminal: barra de progresso ASCII, notificação nativa (com som no macOS) quando o tempo acaba, estatísticas dos últimos dias. `p` pausa, `q` aborta; a cada 4 focos ele sugere a pausa longa.

```bash
goodpomo               # foco de 25 min
goodpomo 50 estudar    # foco de 50 min com rótulo
goodpomo pausa         # pausa de 5 min
goodpomo -l            # hoje + últimos 14 dias
```

### [goodnerd](./goodnerd)
Teatro de "hacker" no terminal — puro efeito visual, **nada real acontece** (sem rede, sem tocar arquivo). Varredura de portas, quebra de senha, compilação/deploy e chuva de código estilo Matrix, pra impressionar quem não programa. `goodnerd` sozinho encadeia tudo numa "operação completa".

```bash
goodnerd               # op completa: scan → crack → deploy → matrix
goodnerd scan          # varredura de portas + invasão + ACCESS GRANTED
goodnerd crack         # quebra de senha, char por char
goodnerd deploy        # compilando/deployando estilo make
goodnerd matrix [seg]  # chuva de código (para com tecla, ou N segundos)
```

---

## IA

Usam a [OpenRouter](https://openrouter.ai) com modelos `:free` — de graça, sem cartão. Precisam do `OPENROUTER_API_KEY` (veja [Instalação](#instalação)). Todas aceitam `-m` pra listar os modelos disponíveis no momento e `OPENROUTER_MODEL` pra escolher outro.

### [goodprof](./goodprof)
Estudo pela técnica Feynman invertida: você explica um assunto, ele fura sua explicação com perguntas socráticas até você travar ou provar que domina. Nunca entrega a resposta.

```bash
goodprof "DNS"    # nova sessão
goodprof -r       # revisão do tópico mais esquecido
goodprof -l       # lista o que já estudou
```

### [goodbio](./goodbio)
Sua autobiografia, uma pergunta por dia. Responde offline; depois de algumas dezenas de respostas, `goodbio capitulo` costura tudo em capítulos escritos na sua voz.

```bash
goodbio           # a pergunta de hoje
goodbio capitulo  # gera a biografia
goodbio -l        # histórico
```

### [goodvocab](./goodvocab)
Uma palavra de inglês por dia, com revisão espaçada (caixas de Leitner). O quiz mostra o significado e a frase com lacuna; você digita a palavra. Revisar é offline — o modelo só gera lotes de palavras novas (~1 request a cada 20 dias).

```bash
goodvocab              # revisão do dia + palavra nova
goodvocab -q           # só a revisão
goodvocab -l           # baralho e status
```

### [goodzap](./goodzap)
Retrô estilo Spotify Wrapped de uma conversa exportada do WhatsApp: quem fala mais, horários, tempo de resposta, quem puxa assunto, maior vácuo. Stats 100% locais; `--roast` adiciona a camada divertida via LLM (anonimizada por padrão).

```bash
goodzap conversa.txt                    # só as estatísticas (offline)
goodzap conversa.txt --roast            # + resumo e roast
goodzap conversa.txt --html retro.html  # retrô visual
```

### [goodivers](./goodivers)
Copiloto de conteúdo do canal Goodivers (Helldivers 2). O radar puxa o estado ao vivo do jogo (Ordem Maior, patch notes, r/Helldivers) e dos canais gringos do nicho (RSS do YouTube com detecção de vídeo-outlier 🔥); `inspirar` cruza o que performa lá fora com o buraco de conteúdo PT-BR e devolve planos de adaptação. Tudo on-demand (zero cron). A coleta do radar e as buscas do YouTube são sem chave e cacheadas (6h); por padrão o radar é **exibido traduzido em PT-BR** por uma chamada de LLM (`--original` mostra o dado cru em inglês, sem chave/LLM). A geração usa LLM, via OpenRouter no terminal **ou** via skill `/goodivers` no Claude Code (o Claude da sessão gera; sem chave).

```bash
goodivers                # radar do jogo e do nicho (traduzido PT-BR)
goodivers --original     # radar cru em inglês, sem LLM
goodivers ideias         # 10 ideias rankeadas (com link do vídeo nas adaptações)
goodivers ideias --ver   # revê a última leva salva, sem regerar
goodivers ideias --hist  # histórico de levas (--hist N abre uma antiga)
goodivers inspirar       # vídeos gringos performando → plano de adaptação PT-BR
goodivers pacote 3       # títulos + thumbs + descrição + hook + roteiro
goodivers buscar "x" -s  # busca no YouTube (semana; --br = como o público BR vê)
goodivers canais add @x  # monitorar outro canal
# no Claude Code: /goodivers ideias · /goodivers pacote 3 · … (mesmos comandos)
```

### [goodwash](./goodwash)
Reescreve texto gerado por IA pra soar naturalmente humano — destruindo a assinatura estatística da marca d'água de texto ("lista verde / lista vermelha"). A watermark não carimba caracteres: ela enviesa a **escolha de tokens** na geração (lista "verde" privilegiada via hash do contexto + chave secreta), e o detector mede se o texto usa tokens verdes acima do acaso. Como o sinal mora nas escolhas de tokens, **reescrita genuína** (variar léxico, quebrar ritmo uniforme, desmontar paralelismos/tríades, trocar transições fórmula) apaga o viés — é o ataque documentado nos papers de watermarking. O goodwash reescreve de verdade (nada de trocar sinônimo por sinônimo), preservando fatos e tom, em três intensidades. `checar` aponta os "tells" de IA offline (0 LLM, sem chave); dever de casa honesto, não é detecção da watermark real (que exige a chave secreta).

```bash
goodwash "seu texto"           # reescrita média (padrão)
goodwash leve "texto"          # leve: lixa arestas de IA
goodwash profunda "texto"      # profunda: parece escrito do zero
goodwash arquivo.txt           # de arquivo · echo "x" | goodwash · stdin
goodwash -o saida.txt "texto"  # salva em arquivo
goodwash checar "texto"        # tells de IA offline (0 LLM, sem chave)
# no Claude Code: /goodwash [leve|media|profunda] <texto> · /goodwash checar <texto>
```

---

## Senhas

### [goodpen](./goodpen) — cofre de senhas em duas versões

**Duas** ferramentas pra guardar senhas criptografadas com backup em pendrive.
Fazem a mesma coisa — mudam só o "como":

- [**standalone**](./goodpen/standalone) (`cofre`) — binário único, zero
  dependências, roda nativo até no Windows. Criptografia age, interface web
  local e backup da chave por **QR code**. Compile com
  `bash goodpen/standalone/build.sh`.
- [**pass-store**](./goodpen/pass-store) (`pass`) — o padrão consagrado do
  Unix (`pass` + `gpg` + `git`), com pendrive como remote e acesso ao
  ecossistema de apps de celular e extensões de browser. Configure com
  `bash goodpen/pass-store/setup.sh`.

```bash
# standalone
cofre          # menu no terminal
cofre web      # interface no navegador
```

Comparação completa e regra de escolha em [goodpen/README.md](./goodpen/README.md).

---

## Comandos

Prefixo (comando de entrada) e subcomandos de cada ferramenta. `-h` em qualquer
uma abre a ajuda completa; `<tool> temas` lista as paletas do terminal.

### Terminal

| Ferramenta | Prefixo | Subcomandos principais |
|---|---|---|
| goodcheats | `good` | `good` (logo+infos) · `good cheat <sub>` · `good harness <sub>` · `good temas` · `good --refresh` · `good -c HEX` |
| | `goodcheat` | `<topico>` · `-e` editar/criar · `-l` listar · `-s <termo>` buscar |
| | `goodharness` | `init [dest] [--from N]` · `copy <nome> [--files a,b]` · `install <nome> [--link]` · `list` · `show <nome>` · `rm <nome>` · `config <show\|get\|set> [dest]` · `diff <nome>` · `update <nome>` · `sync [preset]` · `status` |
| goodpomo | `goodpomo` | `[min] [rotulo]` foco · `pausa [min]` · `-l` estatísticas · `temas` |
| goodnerd | `goodnerd` | (operação completa) · `matrix [seg]` · `scan` · `crack` · `deploy` · `temas` · `--fast`/`--slow` |

### IA (OpenRouter `:free`)

| Ferramenta | Prefixo | Subcomandos principais |
|---|---|---|
| goodprof | `goodprof` | `"<assunto>"` nova sessão · `-r ["<assunto>"]` revisa · `-l` lista · `-m` modelos · `temas` |
| goodbio | `goodbio` | (pergunta do dia) · `-f` follow-up · `-x` extra · `-l` respostas · `capitulo` · `perguntas` · `-m` · `temas` |
| goodvocab | `goodvocab` | (revisão + palavra) · `palavras` reabastece · `-q` quiz · `-x` extra · `-l` baralho · `-m` · `temas` |
| goodzap | `goodzap` | `<arquivo.txt>` · `--roast` · `--reais` · `--html ARQ` · `-m` · `temas` |
| goodivers | `goodivers` | (radar, PT-BR) · `--original` cru · `ideias` · `ideias --ver/--hist` · `inspirar` · `pacote <N\|"ideia">` · `titulos "<tema>"` · `buscar "<termo>"` · `canais` · `temas` |
| dark | `dark` | (radar) · `ideias` · `pacote <N\|"ideia">` · `legendas "<tema>"` · `stories` · `buscar "<termo>"` · `refs` · `temas` |
| goodwash | `goodwash` | (padrão `lavar`, média) · `leve\|media\|profunda` · `-o/--saida` · `--arquivo` · `checar` · `temas` |

Comuns às de IA: `-m` (modelos `:free` no ar), env `OPENROUTER_API_KEY` /
`OPENROUTER_MODEL`. Skills no Claude Code: `/goodivers`, `/dark` e `/goodwash`
usam os mesmos
subcomandos, gerando com o Claude da sessão (sem chave).

### Imagens

| Ferramenta | Prefixo | Subcomandos principais |
|---|---|---|
| goodpixel | `goodpixel` | `[imagens...]` · `-w/--width` · `-c/--colors` · `--palette mono\|gameboy\|cga\|pico8` · `-d` dither · `-s/--scale` · `--temas` |
| goodprofile | `goodprofile` | `[imagens...] [preset\|kit\|LxA]` · `presets` catálogo · `--modo cobrir\|conter\|esticar` · `--gravidade`/`--foco X,Y` · `--centralizar`/`--margem` · `--cor-de/--cor-para` · `--tint` · `--pb` · `--circulo`/`--raio` · `--formato png\|jpg\|webp` · `--temas` |

### Senhas

| Ferramenta | Prefixo | Subcomandos principais |
|---|---|---|
| goodpen (standalone) | `cofre` | `cofre` menu · `cofre web` navegador · `cofre frase` gera passphrase · `cofre temas` |
| goodpen (pass-store) | `pass` | ecossistema `pass` padrão (ver [pass-store](./goodpen/pass-store)) |

Paleta global de qualquer ferramenta: `export RETRO_TEMA=<nome>` (cada uma
também aceita seu `<TOOL>_TEMA`). `NO_COLOR` desliga as cores.

---

## Estrutura

```
tools/
  setup.sh           ← instalador interativo: marca e instala/desinstala qualquer ferramenta
  load.sh            ← o que o rc chama a cada shell novo (goodtools_load)
  .harness/
    styleguide.md          ← style guide do portfólio (origem do visual)
    styleguide-terminal.md ← como ele vira UI de terminal (spec que todas seguem)
  lib/
    rcblock.sh         ← escreve/remove o bloco do rc e a âncora ~/.goodtools
    retro.sh           ← tema compartilhado das ferramentas em bash
    retro.py           ← tema compartilhado das ferramentas em python
    llm.py             ← cliente OpenRouter compartilhado (ferramentas de IA)
  tests/             ← suíte unittest (stdlib) de lib/ + guard de compilação
  Makefile           ← atalhos de dev (make check roda tudo que o CI roda)
  ruff.toml          ← config do ruff (lint python, inclui entrypoints sem .py)
  .shellcheckrc      ← config do shellcheck (desliga ruído SC2034/SC1090)
  .pre-commit-config.yaml ← hooks opcionais que espelham o CI
  .github/workflows/ ← CI: testes + ruff + bash -n + shellcheck
  goodcheats/        ← kit de utilidades da família good
    setup.sh           ← adiciona ao PATH (instala todos os comandos)
    good               ← fetch de sistema com logo (+ dispatcher good <sub>)
    logo.svg           ← o logo original
    goodcheat          ← cheatsheets de comandos
    sheets/            ← as colinhas (uma por arquivo)
    compose/           ← docker compose files prontos
    goodharness        ← biblioteca de styleguides
    styleguides/       ← predefinições de styleguide (uma por .md)
  goodpomo/              ← pomodoro no terminal
    goodpomo               ← o CLI
    setup.sh           ← adiciona ao PATH
  goodnerd/              ← teatro de hacker fake (só efeito visual)
    goodnerd               ← o CLI
    setup.sh           ← adiciona ao PATH
  goodprof/              ← estudo Feynman invertido (OpenRouter :free)
    goodprof               ← o CLI
    setup.sh           ← adiciona ao PATH
    .env.example       ← modelo de config local
  goodbio/               ← autobiografia, 1 pergunta por dia (OpenRouter :free)
    goodbio                ← o CLI
    setup.sh           ← adiciona ao PATH (+ lembrete diário opcional)
    .env.example       ← modelo de config local
  goodvocab/             ← inglês diário com revisão espaçada (OpenRouter :free)
    goodvocab              ← o CLI
    setup.sh           ← adiciona ao PATH (+ lembrete diário opcional)
    .env.example       ← modelo de config local
  goodzap/               ← retrô de conversa do WhatsApp (OpenRouter :free)
    goodzap                ← o CLI
    setup.sh           ← adiciona ao PATH
    .env.example       ← modelo de config local
  goodivers/         ← copiloto do canal de Helldivers 2 (OpenRouter :free)
    goodivers          ← o CLI
    skill/SKILL.md     ← skill /goodivers do Claude Code (gera com o Claude da sessão)
    setup.sh           ← CLI no PATH (+ lembrete opcional) · --skill instala só o skill
    .env.example       ← modelo de config local
  goodwash/          ← reescritor anti-watermark de texto de IA (OpenRouter :free)
    goodwash           ← o CLI (lavar|checar|temas)
    skill/SKILL.md     ← skill /goodwash do Claude Code (reescreve com o Claude da sessão)
    setup.sh           ← CLI no PATH · --skill instala só o skill
    .env.example       ← modelo de config local
  goodpen/           ← cofre de senhas (duas versões)
    README.md          ← comparação e regra de escolha
    standalone/        ← binário único `cofre` (Go), backup por QR
      *.go               ← o código
      build.sh           ← cross-compila pra todas as plataformas → dist/
      README.md          ← uso, build e modelo de segurança
    pass-store/        ← pass + gpg + git com pendrive
      setup.sh           ← setup interativo
      README.md          ← guia completo
      cheatsheet         ← colinha do pass
  images/
    goodpixel/         ← imagem → pixel art (Pillow/ImageMagick)
      goodpixel          ← o CLI
      setup.sh         ← adiciona ao PATH
    goodprofile/       ← imagem → tamanhos de perfil/rede social
      goodprofile        ← o CLI
      setup.sh         ← adiciona ao PATH
```

---

## Desenvolvimento

As ferramentas são scripts de arquivo único, **sem dependências de runtime** (só
a biblioteca padrão do Python/bash). O código compartilhado mora em `lib/`:

- `lib/retro.py` · `lib/retro.sh` — tema retrô do terminal (python e bash)
- `lib/llm.py` — cliente OpenRouter compartilhado pelas ferramentas de IA:
  chave, fallback entre modelos, timeout, tratamento de 401, parse de JSON e
  **cache de respostas** num lugar só (antes era copiado em cada tool)

### Atalho: `make`

Um `Makefile` na raiz roda tudo que o CI roda. Precisa de `ruff` e `shellcheck`
no PATH (`brew install ruff shellcheck`):

```bash
make check      # test + lint (ruff + shellcheck) + bash -n — o pacote todo
make test       # só os testes
make lint       # só ruff + shellcheck
make fix        # aplica o que o ruff consegue consertar sozinho
```

Opcional, pra rodar os linters a cada commit: `pip install pre-commit &&
pre-commit install` (a config em `.pre-commit-config.yaml` chama os mesmos
alvos do `make`).

### Testes

Suíte em `tests/`, usando o `unittest` da stdlib (nada de pytest):

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Cobre `lib/llm.py` (fallback de modelo, erro sem chave, extração de JSON, cache
de respostas, modelos `:free`), `lib/retro.py` (largura ANSI/caracteres largos,
mix de cor, temas) e um guard que compila todos os CLIs python.

### Cache de LLM

`lib/llm.py` guarda respostas em disco por prompt idêntico — economiza cota
`:free` e serve **offline** num acerto. Desligado por padrão; liga por chamada
(`chat(..., cache_ttl=3600)`) ou global:

```bash
export GOODTOOLS_LLM_CACHE_TTL=21600      # TTL em segundos (6h); 0/vazio desliga
export GOODTOOLS_CACHE_DIR=~/.cache/goodtools   # opcional; este é o default
```

A chave inclui título, lista de modelos e parâmetros — trocar `OPENROUTER_MODEL`
ou o prompt invalida o cache.

### CI e lint

`.github/workflows/ci.yml` roda em todo push/PR:

- **python** — testes (3 OSes) + `ruff` (imports/nomes mortos + bugs óbvios)
- **shell** — `bash -n` (sintaxe, 3 OSes) + `shellcheck --severity=warning` +
  smoke test do goodharness

Config dos linters: `ruff.toml` (inclui os entrypoints sem extensão) e
`.shellcheckrc` (desliga SC2034/SC1090, ruído pro estilo desses scripts). Antes
de abrir PR: `make check`.
