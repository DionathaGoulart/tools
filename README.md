# tools

Coleção de ferramentas de terminal pro meu dia a dia como desenvolvedor. Scripts leves, portáteis e sem dependências — funcionam em macOS, Linux e Windows (Git Bash / WSL).

## Ferramentas

### [cheats](./cheats)
Cheatsheets de comandos que eu sempre esqueço. Mais rápido que abrir o Google.

```bash
cheat tar          # ver colinha
cheat -l           # listar todas
cheat -e docker    # editar ou criar nova
```

Instalação (uma vez):
```bash
bash ~/Desktop/tools/cheats/setup.sh   # instala no ~/.zshrc (ou ~/.bashrc)
```

### [good](./good)
Fetch de sistema estilo neofetch, com o logo good em ASCII art colorido. Mostra OS, kernel, uptime, CPU, GPU, memória, disco, pacotes e bateria.

```bash
good            # logo + infos do sistema
good --refresh  # refaz o cache de hardware
```

Instalação (uma vez):
```bash
bash ~/Desktop/tools/good/setup.sh     # instala no ~/.zshrc (ou ~/.bashrc)
```

> Os `setup.sh` detectam o próprio caminho — se clonar o repo em outro lugar, funciona igual. Depois de instalar, abra um terminal novo ou rode `source ~/.zshrc`.

## Ferramentas com IA

Usam a [OpenRouter](https://openrouter.ai) com modelos `:free` (sufixo `:free`) — de graça, sem cartão. Só precisam de uma chave e da variável `OPENROUTER_API_KEY` no seu rc:

```bash
export OPENROUTER_API_KEY="sk-or-..."   # chave grátis em https://openrouter.ai/keys
```

> ⚠️ Prompts enviados a modelos `:free` podem ser usados pra treino. Nenhuma destas ferramentas manda dado sensível por padrão — mas leia a nota de privacidade no README de cada uma antes de colar coisa pessoal.

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

Instalação (uma vez, cada uma):
```bash
bash ~/Desktop/tools/professor/setup.sh
bash ~/Desktop/tools/biografo/setup.sh
bash ~/Desktop/tools/zapstats/setup.sh
```

## [goodpen](./goodpen) — cofre de senhas em duas versões

Dentro de [`goodpen/`](./goodpen) tem **duas** ferramentas pra guardar senhas criptografadas com backup em pendrive. Fazem **a mesma coisa** — mudam só o "como". Escolha uma:

| | [**standalone**](./goodpen/standalone) | [**pass-store**](./goodpen/pass-store) |
|---|---|---|
| O que é | Um programa próprio (binário único) | Guia + script que configuram ferramentas prontas |
| Motor | age (embutido no binário) | `pass` + `gpg` + `git` (instala no sistema) |
| Dependências | **Zero** — só baixar o executável | Precisa instalar 3 programas |
| Windows | Roda nativo (`.exe`) | Só via WSL / Git Bash |
| Interface | Menu no terminal **+ web no navegador** | Linha de comando pura |
| Criptografia | X25519 (age) | RSA 4096 (GPG) — as duas são fortes |
| Backup da chave | **QR code** (cabe no Bitwarden) | Arquivo de ~7KB (sem QR) |
| Esqueceu a passphrase | Recupera com o QR da chave | Perdeu tudo |
| Gera passphrase forte | Sim (`cofre frase`) | Não |
| Apps de celular / browser | Não (formato próprio) | Sim (ecossistema `pass`) |

**Regra rápida:** quer simplicidade, QR e rodar em qualquer sistema sem instalar nada → **standalone**. Quer o padrão consagrado e usar apps de celular/extensão de browser → **pass-store**. São independentes; teste os dois e fique com o que gostar.

### [standalone](./goodpen/standalone) — a versão programinha (o `cofre`)

```bash
cofre          # menu no terminal
cofre web      # interface no navegador
```

Um executável único chamado `cofre` (Windows/macOS/Linux), zero dependências, backup da chave por QR code (escaneia e guarda no Bitwarden). Detalhes em [goodpen/standalone/README.md](./goodpen/standalone/README.md).

### [pass-store](./goodpen/pass-store) — a versão "ferramentas Unix"

```bash
bash ~/Desktop/tools/goodpen/pass-store/setup.sh
```

Configura `pass` (password-store) + GPG + git com um pendrive como cofre. Padrão da indústria, integra com apps de celular e browser. Guia completo em [goodpen/pass-store/README.md](./goodpen/pass-store/README.md).

## Estrutura

```
tools/
  cheats/
    cheat            ← o CLI
    setup.sh         ← adiciona ao PATH
    sheets/          ← as colinhas (uma por arquivo)
    compose/         ← docker compose files prontos
  good/
    good             ← o CLI (fetch de sistema com o logo)
    setup.sh         ← adiciona ao PATH
    logo.svg         ← o logo original
  professor/         ← estudo Feynman invertido (OpenRouter :free)
    professor        ← o CLI
    setup.sh         ← adiciona ao PATH
  biografo/          ← autobiografia, 1 pergunta por dia (OpenRouter :free)
    biografo         ← o CLI
    setup.sh         ← adiciona ao PATH
  zapstats/          ← retrô de conversa do WhatsApp (OpenRouter :free)
    zapstats         ← o CLI
    setup.sh         ← adiciona ao PATH
  goodpen/           ← cofre de senhas (duas versões)
    standalone/      ← versão programinha (binário único `cofre`, Go)
      *.go           ← o código
      README.md      ← uso, build e modelo de segurança
    pass-store/      ← versão pass + gpg + git
      setup.sh       ← setup interativo
      README.md      ← guia completo
      cheatsheet     ← colinha do pass
```
