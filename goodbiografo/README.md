# goodbiografo

Sua autobiografia, **uma pergunta por dia**. Todo dia ele te faz uma pergunta
evocativa sobre sua vida; você responde no terminal e a resposta fica salva.
Depois de algumas dezenas de respostas, ele costura tudo em capítulos de
biografia escritos em texto corrido, na sua voz.

```bash
goodbiografo               # a pergunta de hoje (responde e salva)
goodbiografo -f            # pergunta personalizada, baseada nas suas últimas respostas
goodbiografo -x            # responder outra mesmo já tendo respondido hoje (combina com -f)
goodbiografo capitulo      # gera a biografia a partir de tudo que você já respondeu
goodbiografo -l            # lista as respostas e o status da fila
goodbiografo perguntas     # reabastece o banco de perguntas manualmente
goodbiografo -m            # lista modelos :free disponíveis agora
goodbiografo temas         # paletas disponíveis
```

## A ideia

É um hábito de longo prazo, não uma sessão única. Um minuto por dia, e em alguns
meses você tem material pra uma biografia de verdade — coisas que você nunca
sentaria pra escrever de uma vez.

- **Pergunta do dia:** vem de um banco de 30 perguntas gerado pelo modelo. Quando
  a fila acaba, ele gera mais 30 (1 request). Ou seja: você responde **offline**
  quase sempre; o modelo só entra pra criar perguntas novas.
- **Modo follow-up (`-f`):** em vez de uma pergunta do banco, o modelo lê suas
  últimas respostas e faz uma pergunta que aprofunda algo que você mencionou.
  Mais íntimo, porém envia suas respostas recentes ao modelo.
- **Capítulos:** `goodbiografo capitulo` pega todas as respostas e escreve a
  biografia em primeira pessoa, agrupada por fases da vida.

## Privacidade

Suas respostas ficam em `~/.biografo/respostas/` e **não saem da máquina no uso
diário**. Elas só são enviadas ao modelo em dois casos, e você decide quando:

- `goodbiografo -f` (envia as últimas ~4 respostas pra gerar o follow-up)
- `goodbiografo capitulo` (envia as respostas pra escrever a biografia)

Como a API `:free` da OpenRouter pode usar prompts pra treino, evite escrever
segredos de verdade se for usar `-f`/`capitulo`. O fluxo padrão (responder a
pergunta do dia) não manda nada pra lugar nenhum.

## Instalação

Precisa de Python 3 e uma chave da [OpenRouter](https://openrouter.ai/keys)
(grátis — só usada pra gerar perguntas, follow-up e capítulos).

```bash
# 1. chave da API. Duas formas (escolha uma):
#    a) no seu rc (~/.zshrc, ~/.bashrc, ~/.bash_profile):
export OPENROUTER_API_KEY="sk-or-..."
#    b) ou num .env dentro desta pasta:
cp ~/Desktop/tools/goodbiografo/.env.example ~/Desktop/tools/goodbiografo/.env
#    e edite o .env com sua chave (o .env não é versionado).

# 2. coloca o comando no PATH (uma vez):
bash ~/Desktop/tools/goodbiografo/setup.sh
```

> A variável exportada no shell tem prioridade sobre o `.env`.

### Lembrete diário (opcional)

Adicione antes da linha de `source` no seu rc pra ser lembrado uma vez por dia,
ao abrir o terminal:

```bash
export GOODBIOGRAFO_LEMBRETE=1
```

## Configuração

| Variável | Pra quê | Padrão |
|---|---|---|
| `OPENROUTER_API_KEY` | sua chave (obrigatória p/ perguntas, follow-up, capítulos) | — |
| `OPENROUTER_MODEL` | modelos a tentar, separados por vírgula | lista de modelos `:free` |
| `GOODBIOGRAFO_DIR` | onde salvar tudo | `~/.biografo` |
| `GOODBIOGRAFO_LEMBRETE` | `1` liga o lembrete diário no terminal | desligado |
| `GOODBIOGRAFO_TEMA` | paleta (veja `goodbiografo temas`) | `vault-gold` |
| `RETRO_TEMA` | paleta pra todas as ferramentas do repo (fallback) | `vault-gold` |
| `NO_COLOR` | qualquer valor desliga as cores | — |

## Temas

Nove paletas vindas do style guide (`goodbiografo temas` lista com swatch):

| Escuras | Claras |
|---|---|
| `vault-gold` (padrão), `noir-rose`, `midnight-ember`, `cyber-teal`, `velvet-purple` | `abyss-frost`, `crimson-chalk`, `forest-mist`, `sand-dusk` |

```bash
export GOODBIOGRAFO_TEMA=cyber-teal   # só o goodbiografo
export RETRO_TEMA=cyber-teal      # todas as ferramentas
```

`GOODBIOGRAFO_TEMA` tem prioridade sobre `RETRO_TEMA`. Cores true-color (24-bit)
quando `COLORTERM=truecolor`; senão cai pro ANSI básico de 8 cores. Fora de TTY
ou com `NO_COLOR`, a saída vira texto puro.

## Dica

`~/.biografo` é só Markdown e JSON — rode `git init` lá dentro e você ganha
backup e histórico de toda a sua biografia de graça.

---

↩ [Voltar pro índice de ferramentas](../README.md)
