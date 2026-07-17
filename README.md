# tools

Coleção de ferramentas de terminal pro meu dia a dia como desenvolvedor. Scripts leves, portáteis e sem dependências — funcionam em macOS, Linux e Windows (Git Bash / WSL).

## Índice

| Ferramenta | Comando | O que faz |
|---|---|---|
| **Terminal** | | |
| [cheats](./cheats) | `cheat` | Cheatsheets de comandos que eu sempre esqueço |
| [good](./good) | `good` | Fetch de sistema estilo neofetch com logo em ASCII |
| **IA** (OpenRouter `:free`) | | |
| [professor](./professor) | `professor` | Estudo Feynman invertido: te sabatina até você dominar |
| [biografo](./biografo) | `biografo` | Sua autobiografia, uma pergunta por dia |
| [zapstats](./zapstats) | `zapstats` | Retrô de uma conversa exportada do WhatsApp |
| **Senhas** | | |
| [goodpen](./goodpen) | `cofre` / `pass` | Cofre de senhas criptografado, backup em pendrive (2 versões) |

## Instalação

Cada ferramenta tem um `setup.sh` que a adiciona ao `PATH`. Rode uma vez a(s) que quiser:

```bash
bash ~/Desktop/tools/cheats/setup.sh
bash ~/Desktop/tools/good/setup.sh
bash ~/Desktop/tools/professor/setup.sh
bash ~/Desktop/tools/biografo/setup.sh
bash ~/Desktop/tools/zapstats/setup.sh
```

Depois abra um terminal novo (ou `source ~/.zshrc`). Os `setup.sh` detectam o próprio caminho — se clonar o repo em outro lugar, funciona igual.

**Ferramentas de IA** também precisam de uma chave grátis da [OpenRouter](https://openrouter.ai/keys). No seu rc:

```bash
export OPENROUTER_API_KEY="sk-or-..."
```

Ou, por ferramenta, copie o `.env.example` da pasta pra `.env` e preencha (o `.env` não é versionado; o env do shell tem prioridade):

```bash
cp ~/Desktop/tools/professor/.env.example ~/Desktop/tools/professor/.env
```

> ⚠️ Prompts enviados a modelos `:free` podem ser usados pra treino. Nenhuma ferramenta manda dado sensível por padrão — mas leia a nota de privacidade no README de cada uma antes de colar coisa pessoal.

---

## Terminal

### [cheats](./cheats)
Cheatsheets de comandos que eu sempre esqueço. Mais rápido que abrir o Google.

```bash
cheat tar          # ver colinha
cheat -l           # listar todas
cheat -s porta     # buscar termo dentro de todas
cheat -e docker    # editar ou criar nova
```

### [good](./good)
Fetch de sistema estilo neofetch, com o logo good em ASCII art colorido. Mostra OS, kernel, uptime, CPU, GPU, memória, disco, pacotes e bateria.

```bash
good            # logo + infos do sistema
good --refresh  # refaz o cache de hardware
```

---

## IA

Usam a [OpenRouter](https://openrouter.ai) com modelos `:free` — de graça, sem cartão. Precisam do `OPENROUTER_API_KEY` (veja [Instalação](#instalação)). Todas aceitam `-m` pra listar os modelos disponíveis no momento e `OPENROUTER_MODEL` pra escolher outro.

### [professor](./professor)
Estudo pela técnica Feynman invertida: você explica um assunto, ele fura sua explicação com perguntas socráticas até você travar ou provar que domina. Nunca entrega a resposta.

```bash
professor "DNS"    # nova sessão
professor -r       # revisão do tópico mais esquecido
professor -l       # lista o que já estudou
```

### [biografo](./biografo)
Sua autobiografia, uma pergunta por dia. Responde offline; depois de algumas dezenas de respostas, `biografo capitulo` costura tudo em capítulos escritos na sua voz.

```bash
biografo           # a pergunta de hoje
biografo capitulo  # gera a biografia
biografo -l        # histórico
```

### [zapstats](./zapstats)
Retrô estilo Spotify Wrapped de uma conversa exportada do WhatsApp: quem fala mais, horários, tempo de resposta, quem puxa assunto, maior vácuo. Stats 100% locais; `--roast` adiciona a camada divertida via LLM (anonimizada por padrão).

```bash
zapstats conversa.txt                    # só as estatísticas (offline)
zapstats conversa.txt --roast            # + resumo e roast
zapstats conversa.txt --html retro.html  # retrô visual
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
  cheats/            ← cheatsheets de comandos
    cheat              ← o CLI
    setup.sh           ← adiciona ao PATH
    sheets/            ← as colinhas (uma por arquivo)
    compose/           ← docker compose files prontos
  good/              ← fetch de sistema com logo
    good               ← o CLI
    setup.sh           ← adiciona ao PATH
    logo.svg           ← o logo original
  professor/         ← estudo Feynman invertido (OpenRouter :free)
    professor          ← o CLI
    setup.sh           ← adiciona ao PATH
    .env.example       ← modelo de config local
  biografo/          ← autobiografia, 1 pergunta por dia (OpenRouter :free)
    biografo           ← o CLI
    setup.sh           ← adiciona ao PATH (+ lembrete diário opcional)
    .env.example       ← modelo de config local
  zapstats/          ← retrô de conversa do WhatsApp (OpenRouter :free)
    zapstats           ← o CLI
    setup.sh           ← adiciona ao PATH
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
