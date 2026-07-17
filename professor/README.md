# professor

Estudo pela **técnica Feynman invertida** no terminal. Você explica um assunto
com suas palavras; um professor socrático fura sua explicação com perguntas até
você travar ou provar que domina. No fim, dá um veredito: o que você sabe, onde
enrolou e o que estudar.

A regra de ouro: **ele nunca explica o assunto.** Só interroga. Quem tem que
descobrir os buracos é você.

```bash
professor "DNS"        # nova sessão sobre um assunto
professor -r           # revisão: sabatina sobre o tópico mais esquecido
professor -r "DNS"     # revisão de um tópico específico
professor -l           # lista tópicos já estudados
professor -m           # lista modelos :free disponíveis agora
```

## Como funciona uma sessão

1. `professor "TCP handshake"` — você digita sua explicação (várias linhas;
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
# 1. chave da API no seu rc (~/.zshrc, ~/.bashrc, ~/.bash_profile):
export OPENROUTER_API_KEY="sk-or-..."

# 2. coloca o comando no PATH (uma vez):
bash ~/Desktop/tools/professor/setup.sh
```

Abra um terminal novo e rode `professor "qualquer coisa"`.

## Configuração

| Variável | Pra quê | Padrão |
|---|---|---|
| `OPENROUTER_API_KEY` | sua chave (obrigatória) | — |
| `OPENROUTER_MODEL` | modelos a tentar, separados por vírgula (fallback em ordem) | lista de modelos `:free` |
| `PROFESSOR_DIR` | onde salvar as sessões | `~/.professor` |

Os modelos `:free` da OpenRouter mudam com o tempo e às vezes caem. O script
tenta uma lista em ordem; se todos falharem, rode `professor -m` pra ver os que
estão no ar e ajuste `OPENROUTER_MODEL`.

## Dica

`~/.professor` é uma pasta de Markdown — vira um `git init` e você tem backup e
histórico de tudo que já estudou de graça.
