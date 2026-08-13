# goodvocab

Uma palavra de inglês por dia, com **revisão espaçada**. Todo dia ele te
ensina uma palavra nova (significado, pronúncia IPA, frase de exemplo) e te
sabatina nas anteriores que estão vencendo. Acertou, a palavra volta mais
longe; errou, volta amanhã — caixas de Leitner clássicas.

```bash
goodvocab              # revisão do dia + palavra nova
goodvocab -q           # só a revisão, sem palavra nova
goodvocab -x           # aprender outra palavra mesmo já tendo aprendido hoje
goodvocab -l           # lista o baralho e o status da revisão
goodvocab palavras     # reabastece a fila de palavras manualmente
goodvocab -m           # lista modelos :free disponíveis agora
goodvocab temas        # lista as paletas do terminal
```

## Como funciona

O quiz mostra o significado em português e a frase de exemplo com a palavra
escondida — você digita a palavra em inglês:

```
  [ MODULE: SPACED_REVIEW ]  DUE: 2

  [1/2]  adiar, enrolar pra fazer algo
      I always _____________ my taxes until April.
      > palavra: procrastinate
      [ OK ] PROCRASTINATE  /prəˈkræstɪneɪt/
```

- **Palavra do dia:** vem de um lote de 20 gerado pelo modelo (nível e temas
  configuráveis). Quando a fila acaba, gera mais 20 (1 request a cada ~20
  dias). Ou seja: o uso diário é **offline** quase sempre.
- **Repetição espaçada:** cada palavra tem uma caixa. Acertos sobem a caixa e
  esticam o intervalo (1 → 2 → 4 → 7 → 15 → 30 dias); erro derruba pra
  caixa 0 e a palavra volta amanhã.
- **Dominada:** palavra na última caixa (revisão a cada 30 dias).

## Aparência

O `goodvocab` segue o style guide de terminal retrô do repositório
(`.harness/styleguide-terminal.md`): a palavra do dia sai numa janela de
terminal, as caixas de Leitner viram barras `█`/`▒` em tom de acento, rótulos
em maiúsculas e `[ OK ]` / `[ ERRO ]` no lugar de emoji.

```bash
goodvocab temas                     # mostra as 9 paletas, marcando a atual com ►
export RETRO_TEMA=cyber-teal    # paleta de todas as ferramentas do repo
export GOODVOCAB_PALETA=noir-rose   # só o goodvocab
```

Paletas: `vault-gold` (padrão) · `noir-rose` · `midnight-ember` · `cyber-teal`
· `velvet-purple` · `abyss-frost` · `crimson-chalk` · `forest-mist` ·
`sand-dusk`. `NO_COLOR=1`, saída redirecionada pra arquivo ou terminal estreito
degradam pra texto puro sem perder a leitura.

> **Nota:** a paleta do terminal é `GOODVOCAB_PALETA`, não `GOODVOCAB_TEMA` — esta
> última já era dos *temas das palavras geradas* (texto livre, ex.:
> `tecnologia, viagem`) e continua com esse papel.

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
cp goodvocab/.env.example goodvocab/.env
#    e edite o .env com sua chave (o .env não é versionado).

# 2. coloca o comando no PATH (uma vez):
bash goodvocab/setup.sh
```

> A variável exportada no shell tem prioridade sobre o `.env`.

### Lembrete diário (opcional)

Adicione antes da linha de `source` no seu rc pra ser lembrado uma vez por
dia, ao abrir o terminal:

```bash
export GOODVOCAB_LEMBRETE=1
```

## Configuração

| Variável | Pra quê | Padrão |
|---|---|---|
| `OPENROUTER_API_KEY` | sua chave (obrigatória só p/ gerar palavras) | — |
| `OPENROUTER_MODEL` | modelos a tentar, separados por vírgula | lista de modelos `:free` |
| `GOODVOCAB_NIVEL` | nível das palavras geradas | `intermediário` |
| `GOODVOCAB_TEMA` | temas preferidos das palavras (texto livre) | nenhum |
| `GOODVOCAB_PALETA` | paleta do terminal só pro goodvocab (veja `goodvocab temas`) | `vault-gold` |
| `RETRO_TEMA` | paleta do terminal (veja `goodvocab temas`) | `vault-gold` |
| `GOODVOCAB_DIR` | onde salvar tudo | `~/.vocab` |
| `GOODVOCAB_LEMBRETE` | `1` liga o lembrete diário no terminal | desligado |
| `NO_COLOR` | qualquer valor desliga as cores | desligado |

## Dica

`~/.vocab` é só JSON — rode `git init` lá dentro e você ganha backup e
histórico do seu baralho de graça.

---

↩ [Voltar pro índice de ferramentas](../README.md)
