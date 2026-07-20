# vocab

Uma palavra de inglês por dia, com **revisão espaçada**. Todo dia ele te
ensina uma palavra nova (significado, pronúncia IPA, frase de exemplo) e te
sabatina nas anteriores que estão vencendo. Acertou, a palavra volta mais
longe; errou, volta amanhã — caixas de Leitner clássicas.

```bash
vocab              # revisão do dia + palavra nova
vocab -q           # só a revisão, sem palavra nova
vocab -x           # aprender outra palavra mesmo já tendo aprendido hoje
vocab -l           # lista o baralho e o status da revisão
vocab palavras     # reabastece a fila de palavras manualmente
vocab -m           # lista modelos :free disponíveis agora
```

## Como funciona

O quiz mostra o significado em português e a frase de exemplo com a palavra
escondida — você digita a palavra em inglês:

```
🔁 revisão: 2 palavra(s) pra hoje

1/2  adiar, enrolar pra fazer algo
     I always _____________ my taxes until April.
     palavra: procrastinate
     ✅ procrastinate /prəˈkræstɪneɪt/
```

- **Palavra do dia:** vem de um lote de 20 gerado pelo modelo (nível e temas
  configuráveis). Quando a fila acaba, gera mais 20 (1 request a cada ~20
  dias). Ou seja: o uso diário é **offline** quase sempre.
- **Repetição espaçada:** cada palavra tem uma caixa. Acertos sobem a caixa e
  esticam o intervalo (1 → 2 → 4 → 7 → 15 → 30 dias); erro derruba pra
  caixa 0 e a palavra volta amanhã.
- **Dominada:** palavra na última caixa (revisão a cada 30 dias).

## Privacidade

Seu progresso fica em `~/.vocab/` e não sai da máquina. O modelo só é chamado
pra gerar palavras novas, e o prompt leva apenas a lista de palavras que você
já viu (pra não repetir) — nenhum dado pessoal.

## Instalação

Precisa de Python 3 e uma chave da [OpenRouter](https://openrouter.ai/keys)
(grátis — só usada pra gerar palavras novas).

```bash
# 1. chave da API. Duas formas (escolha uma):
#    a) no seu rc (~/.zshrc, ~/.bashrc, ~/.bash_profile):
export OPENROUTER_API_KEY="sk-or-..."
#    b) ou num .env dentro desta pasta:
cp ~/Desktop/tools/vocab/.env.example ~/Desktop/tools/vocab/.env
#    e edite o .env com sua chave (o .env não é versionado).

# 2. coloca o comando no PATH (uma vez):
bash ~/Desktop/tools/vocab/setup.sh
```

> A variável exportada no shell tem prioridade sobre o `.env`.

### Lembrete diário (opcional)

Adicione antes da linha de `source` no seu rc pra ser lembrado uma vez por
dia, ao abrir o terminal:

```bash
export VOCAB_LEMBRETE=1
```

## Configuração

| Variável | Pra quê | Padrão |
|---|---|---|
| `OPENROUTER_API_KEY` | sua chave (obrigatória só p/ gerar palavras) | — |
| `OPENROUTER_MODEL` | modelos a tentar, separados por vírgula | lista de modelos `:free` |
| `VOCAB_NIVEL` | nível das palavras geradas | `intermediário` |
| `VOCAB_TEMA` | temas preferidos (texto livre) | nenhum |
| `VOCAB_DIR` | onde salvar tudo | `~/.vocab` |
| `VOCAB_LEMBRETE` | `1` liga o lembrete diário no terminal | desligado |

## Dica

`~/.vocab` é só JSON — rode `git init` lá dentro e você ganha backup e
histórico do seu baralho de graça.

---

↩ [Voltar pro índice de ferramentas](../README.md)
