# goodzapstats

Retrospectiva de uma conversa do WhatsApp — estilo Spotify Wrapped, no
terminal. Passe o `.txt` do "Exportar conversa" e receba quem fala mais,
horários, tempo de resposta, quem puxa assunto, emojis, palavras, maior vácuo,
maior sequência de dias e mais.

**Tudo é calculado localmente.** Nada sai da sua máquina — a menos que você peça
a camada de roast com `--roast`.

```bash
goodzapstats conversa.txt                       # só as estatísticas (100% offline)
goodzapstats conversa.txt --roast               # + resumo, frases icônicas e roast (LLM)
goodzapstats conversa.txt --roast --reais       # roast com os nomes reais (menos privado)
goodzapstats conversa.txt --html retro.html     # também gera um retrô visual em HTML
goodzapstats -m                                 # lista modelos :free disponíveis
goodzapstats temas                              # lista as paletas do terminal
```

## Como exportar a conversa

No WhatsApp: abra a conversa → menu → **Exportar conversa** → **Sem mídia**.
Você recebe um `.txt`. É esse arquivo que o `goodzapstats` lê. Funciona com export
de iPhone e de Android (formatos diferentes, ambos suportados), com datas
`dd/mm` ou `mm/dd` (detecta sozinho olhando o arquivo inteiro) e com conversas
de duas pessoas ou de grupo.

## O que ele calcula (offline)

- Ranking de quem mais manda mensagem
- Distribuição por horário do dia e por dia da semana
- Tempo mediano de resposta de cada pessoa
- Quem puxa assunto (primeira mensagem depois de 6h+ de silêncio)
- Emojis e palavras mais usadas
- Maior vácuo (mais tempo sem falar) e maior sequência de dias seguidos
- Mensagens de madrugada, risadas (kkk/haha), perguntas

## A camada `--roast` (opcional, usa LLM)

Adiciona um resumo narrativo da dinâmica, frases icônicas reais, apelidos
detectados e um roast bem-humorado de cada um.

## Aparência

O `goodzapstats` segue o style guide de terminal retrô do repositório
(`.harness/styleguide-terminal.md`): janela de terminal, barras `█`/`▒` em
tom de acento, rótulos em maiúsculas, `[ OK ]` / `[ ERRO ]`.

```bash
goodzapstats temas                 # mostra as 9 paletas, marcando a atual com ►
export GOODZAPSTATS_TEMA=cyber-teal    # só o goodzapstats
export RETRO_TEMA=noir-rose        # todas as ferramentas do repo
```

Paletas: `vault-gold` (padrão) · `noir-rose` · `midnight-ember` · `cyber-teal`
· `velvet-purple` · `abyss-frost` · `crimson-chalk` · `forest-mist` ·
`sand-dusk`. `NO_COLOR=1`, saída redirecionada pra arquivo ou terminal estreito
degradam pra texto puro sem perder a leitura.

## Privacidade

- **Sem `--roast`**: 100% offline. Nada sai da máquina, nunca.
- **Com `--roast`**: por padrão os nomes são trocados por "Pessoa A/B" **antes**
  de sair da máquina, e recolocados no texto final localmente. Só uma amostra
  de mensagens (as mais longas) é enviada, nunca a conversa inteira.
- Ainda assim, a API `:free` da OpenRouter pode usar prompts pra treino — não
  rode `--roast` em conversa com dado sensível.
- `--reais` desliga a anonimização (mais divertido, menos privado).

## Instalação

Precisa de Python 3. A camada `--roast` também precisa de uma chave da
[OpenRouter](https://openrouter.ai/keys) (grátis) — sem ela, tudo o mais roda.

```bash
# 1. (só pra --roast) chave da API. Duas formas (escolha uma):
#    a) no seu rc (~/.zshrc, ~/.bashrc, ~/.bash_profile):
export OPENROUTER_API_KEY="sk-or-..."
#    b) ou num .env dentro desta pasta:
cp ~/Desktop/tools/goodzapstats/.env.example ~/Desktop/tools/goodzapstats/.env
#    e edite o .env com sua chave (o .env não é versionado).

# 2. coloca o comando no PATH (uma vez):
bash ~/Desktop/tools/goodzapstats/setup.sh
```

> A variável exportada no shell tem prioridade sobre o `.env`.

## Configuração

| Variável | Pra quê | Padrão |
|---|---|---|
| `OPENROUTER_API_KEY` | sua chave (só necessária pra `--roast`) | — |
| `OPENROUTER_MODEL` | modelos a tentar, separados por vírgula | lista de modelos `:free` |
| `GOODZAPSTATS_TEMA` | paleta do terminal (veja `goodzapstats temas`) | `vault-gold` |
| `RETRO_TEMA` | paleta padrão de todas as ferramentas (fallback) | `vault-gold` |
| `NO_COLOR` | qualquer valor desliga as cores | desligado |

---

↩ [Voltar pro índice de ferramentas](../README.md)
