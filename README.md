# tools

Coleção de ferramentas de terminal pro meu dia a dia como desenvolvedor. Scripts leves, portáteis e sem dependências — funcionam em macOS, Linux e Windows (Git Bash / WSL).

## Índice

| Ferramenta | Comando | O que faz |
|---|---|---|
| **Terminal** | | |
| [goodcheats](./goodcheats) | `good` / `goodcheat` / `goodharness` | Kit de utilidades da família good: fetch de sistema + cheatsheets + styleguides |
| [goodpomo](./goodpomo) | `goodpomo` | Pomodoro com notificação nativa e estatísticas |
| [goodnerd](./goodnerd) | `goodnerd` | Teatro de "hacker" fake no terminal, pra impressionar os leigos |
| **IA** (OpenRouter `:free`) | | |
| [goodprofessor](./goodprofessor) | `goodprofessor` | Estudo Feynman invertido: te sabatina até você dominar |
| [goodbiografo](./goodbiografo) | `goodbiografo` | Sua autobiografia, uma pergunta por dia |
| [goodvocab](./goodvocab) | `goodvocab` | Uma palavra de inglês por dia, com revisão espaçada |
| [goodzapstats](./goodzapstats) | `goodzapstats` | Retrô de uma conversa exportada do WhatsApp |
| [goodivers](./goodivers) | `goodivers` | Copiloto do canal de Helldivers 2: radar ao vivo do jogo + ideias, títulos e thumbs |
| [dark](./dark) | `dark` | Copiloto do Instagram @darkning.art (horror art): radar do nicho + ideias, pacotes, captions e stories em inglês |
| **Imagens** | | |
| [images/goodpixelart](./images/goodpixelart) | `goodpixelart` | Transforma imagens (png/jpg/svg/webp/…) em pixel art com paletas clássicas |
| **Senhas** | | |
| [goodpen](./goodpen) | `cofre` / `pass` | Cofre de senhas criptografado, backup em pendrive (2 versões) |

## Instalação

Jeito rápido — o instalador interativo da raiz lista tudo, você marca o que quer (`1-9` marca, `a` todos, `n` nenhum, `Enter` instala):

```bash
bash ~/Desktop/tools/setup.sh        # instalar (marque e dê Enter)
bash ~/Desktop/tools/setup.sh -u     # desinstalar (lista só as instaladas)
```

Ou individualmente — cada ferramenta tem um `setup.sh` que a adiciona ao `PATH`:

```bash
bash ~/Desktop/tools/goodcheats/setup.sh
bash ~/Desktop/tools/goodpomo/setup.sh
bash ~/Desktop/tools/goodnerd/setup.sh
bash ~/Desktop/tools/goodprofessor/setup.sh
bash ~/Desktop/tools/goodbiografo/setup.sh
bash ~/Desktop/tools/goodvocab/setup.sh
bash ~/Desktop/tools/goodzapstats/setup.sh
bash ~/Desktop/tools/goodivers/setup.sh
bash ~/Desktop/tools/goodivers/setup.sh --skill   # skill /goodivers do Claude Code
bash ~/Desktop/tools/images/goodpixelart/setup.sh
```

Depois abra um terminal novo (ou `source ~/.zshrc`). Os `setup.sh` detectam o próprio caminho — se clonar o repo em outro lugar, funciona igual. A desinstalação remove as linhas do seu rc (com backup em `<rc>.tools-backup`); o goodpen tem setup próprio e fica de fora do instalador.

**Ferramentas de IA** também precisam de uma chave grátis da [OpenRouter](https://openrouter.ai/keys). No seu rc:

```bash
export OPENROUTER_API_KEY="sk-or-..."
```

Ou, por ferramenta, copie o `.env.example` da pasta pra `.env` e preencha (o `.env` não é versionado; o env do shell tem prioridade):

```bash
cp ~/Desktop/tools/goodprofessor/.env.example ~/Desktop/tools/goodprofessor/.env
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

### [goodprofessor](./goodprofessor)
Estudo pela técnica Feynman invertida: você explica um assunto, ele fura sua explicação com perguntas socráticas até você travar ou provar que domina. Nunca entrega a resposta.

```bash
goodprofessor "DNS"    # nova sessão
goodprofessor -r       # revisão do tópico mais esquecido
goodprofessor -l       # lista o que já estudou
```

### [goodbiografo](./goodbiografo)
Sua autobiografia, uma pergunta por dia. Responde offline; depois de algumas dezenas de respostas, `goodbiografo capitulo` costura tudo em capítulos escritos na sua voz.

```bash
goodbiografo           # a pergunta de hoje
goodbiografo capitulo  # gera a biografia
goodbiografo -l        # histórico
```

### [goodvocab](./goodvocab)
Uma palavra de inglês por dia, com revisão espaçada (caixas de Leitner). O quiz mostra o significado e a frase com lacuna; você digita a palavra. Revisar é offline — o modelo só gera lotes de palavras novas (~1 request a cada 20 dias).

```bash
goodvocab              # revisão do dia + palavra nova
goodvocab -q           # só a revisão
goodvocab -l           # baralho e status
```

### [goodzapstats](./goodzapstats)
Retrô estilo Spotify Wrapped de uma conversa exportada do WhatsApp: quem fala mais, horários, tempo de resposta, quem puxa assunto, maior vácuo. Stats 100% locais; `--roast` adiciona a camada divertida via LLM (anonimizada por padrão).

```bash
goodzapstats conversa.txt                    # só as estatísticas (offline)
goodzapstats conversa.txt --roast            # + resumo e roast
goodzapstats conversa.txt --html retro.html  # retrô visual
```

### [goodivers](./goodivers)
Copiloto de conteúdo do canal Goodivers (Helldivers 2). O radar puxa o estado ao vivo do jogo (Ordem Maior, patch notes, r/Helldivers) e dos canais gringos do nicho (RSS do YouTube com detecção de vídeo-outlier 🔥); `inspirar` cruza o que performa lá fora com o buraco de conteúdo PT-BR e devolve planos de adaptação. Tudo on-demand (zero cron); radar e busca sem chave, só a geração usa LLM — via OpenRouter no terminal **ou** via skill `/goodivers` no Claude Code (o Claude da sessão gera; sem chave).

```bash
goodivers                # radar do jogo e do nicho
goodivers ideias         # 10 ideias rankeadas
goodivers inspirar       # vídeos gringos performando → plano de adaptação PT-BR
goodivers pacote 3       # títulos + thumbs + descrição + hook + roteiro
goodivers buscar "x" -s  # busca no YouTube (semana; --br = como o público BR vê)
goodivers canais add @x  # monitorar outro canal
# no Claude Code: /goodivers ideias · /goodivers pacote 3 · … (mesmos comandos)
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

## Estrutura

```
tools/
  setup.sh           ← instalador interativo: marca e instala/desinstala qualquer ferramenta
  .harness/
    styleguide.md          ← style guide do portfólio (origem do visual)
    styleguide-terminal.md ← como ele vira UI de terminal (spec que todas seguem)
  lib/
    retro.sh           ← tema compartilhado das ferramentas em bash
    retro.py           ← tema compartilhado das ferramentas em python
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
  goodprofessor/         ← estudo Feynman invertido (OpenRouter :free)
    goodprofessor          ← o CLI
    setup.sh           ← adiciona ao PATH
    .env.example       ← modelo de config local
  goodbiografo/          ← autobiografia, 1 pergunta por dia (OpenRouter :free)
    goodbiografo           ← o CLI
    setup.sh           ← adiciona ao PATH (+ lembrete diário opcional)
    .env.example       ← modelo de config local
  goodvocab/             ← inglês diário com revisão espaçada (OpenRouter :free)
    goodvocab              ← o CLI
    setup.sh           ← adiciona ao PATH (+ lembrete diário opcional)
    .env.example       ← modelo de config local
  goodzapstats/          ← retrô de conversa do WhatsApp (OpenRouter :free)
    goodzapstats           ← o CLI
    setup.sh           ← adiciona ao PATH
    .env.example       ← modelo de config local
  goodivers/         ← copiloto do canal de Helldivers 2 (OpenRouter :free)
    goodivers          ← o CLI
    skill/SKILL.md     ← skill /goodivers do Claude Code (gera com o Claude da sessão)
    setup.sh           ← CLI no PATH (+ lembrete opcional) · --skill instala só o skill
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
```
