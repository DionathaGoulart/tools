# goodprofessor

Estudo pela **técnica Feynman invertida** no terminal. Você explica um assunto
com suas palavras; um professor socrático fura sua explicação com perguntas até
você travar ou provar que domina. No fim, dá um veredito: o que você sabe, onde
enrolou e o que estudar.

A regra de ouro: **ele nunca explica o assunto.** Só interroga. Quem tem que
descobrir os buracos é você.

```bash
goodprofessor "DNS"        # nova sessão sobre um assunto
goodprofessor -r           # revisão: sabatina sobre o tópico mais esquecido
goodprofessor -r "DNS"     # revisão de um tópico específico
goodprofessor -l           # lista tópicos já estudados
goodprofessor -m           # lista modelos :free disponíveis agora
goodprofessor temas        # paletas disponíveis
```

## Como funciona uma sessão

1. `goodprofessor "TCP handshake"` — você digita sua explicação (várias linhas;
   termina com uma linha contendo só `.` ou `Ctrl-D`).
2. O professor aponta o que ficou vago/circular/errado e faz 2-3 perguntas.
3. Você responde. Ele desce um nível e pergunta de novo.
4. Repete até você dominar ou travar. Digite `/fim` numa linha pra forçar o veredito.
5. A sessão inteira fica salva em `~/.professor/<tópico>/<data>.md`.

O modo revisão (`-r`) lê o veredito da última sessão daquele tópico e ataca
justamente os pontos fracos — repetição espaçada de graça. Sem argumento, ele
escolhe o tópico que você estudou há mais tempo.

## Instalação

Precisa de Python 3 e uma chave da [OpenRouter](https://openrouter.ai/keys)
(grátis).

```bash
# 1. chave da API. Duas formas (escolha uma):
#    a) no seu rc (~/.zshrc, ~/.bashrc, ~/.bash_profile):
export OPENROUTER_API_KEY="sk-or-..."
#    b) ou num .env dentro desta pasta:
cp ~/Desktop/tools/goodprofessor/.env.example ~/Desktop/tools/goodprofessor/.env
#    e edite o .env com sua chave (o .env não é versionado).

# 2. coloca o comando no PATH (uma vez):
bash ~/Desktop/tools/goodprofessor/setup.sh
```

> A variável exportada no shell tem prioridade sobre o `.env`.

Abra um terminal novo e rode `goodprofessor "qualquer coisa"`.

## Configuração

| Variável | Pra quê | Padrão |
|---|---|---|
| `OPENROUTER_API_KEY` | sua chave (obrigatória) | — |
| `OPENROUTER_MODEL` | modelos a tentar, separados por vírgula (fallback em ordem) | lista de modelos `:free` |
| `GOODPROFESSOR_DIR` | onde salvar as sessões | `~/.professor` |
| `GOODPROFESSOR_TEMA` | paleta (veja `goodprofessor temas`) | `vault-gold` |
| `RETRO_TEMA` | paleta pra todas as ferramentas do repo (fallback) | `vault-gold` |
| `NO_COLOR` | qualquer valor desliga as cores | — |

Os modelos `:free` da OpenRouter mudam com o tempo e às vezes caem. O script
tenta uma lista em ordem; se todos falharem, rode `goodprofessor -m` pra ver os que
estão no ar e ajuste `OPENROUTER_MODEL`.

## Temas

Nove paletas vindas do style guide (`goodprofessor temas` lista com swatch):

| Escuras | Claras |
|---|---|
| `vault-gold` (padrão), `noir-rose`, `midnight-ember`, `cyber-teal`, `velvet-purple` | `abyss-frost`, `crimson-chalk`, `forest-mist`, `sand-dusk` |

```bash
export GOODPROFESSOR_TEMA=cyber-teal   # só o goodprofessor
export RETRO_TEMA=cyber-teal       # todas as ferramentas
```

`GOODPROFESSOR_TEMA` tem prioridade sobre `RETRO_TEMA`. Cores true-color (24-bit)
quando `COLORTERM=truecolor`; senão cai pro ANSI básico de 8 cores. Fora de TTY
ou com `NO_COLOR`, a saída vira texto puro.

## Privacidade

Tudo que você digita numa sessão vai pro modelo — é assim que ele te sabatina.
A API `:free` da OpenRouter pode usar prompts pra treino, então trate a sessão
como pública: ótimo pra estudar DNS, TCP, SOLID; péssimo pra colar trecho de
código proprietário ou dado de cliente. As sessões salvas em `~/.professor/`
ficam só na sua máquina.

## Dica

`~/.professor` é uma pasta de Markdown — vira um `git init` e você tem backup e
histórico de tudo que já estudou de graça.

---

↩ [Voltar pro índice de ferramentas](../README.md)
