# dark 🕯

Copiloto de conteúdo do Instagram [@darkning.art](https://instagram.com/darkning.art) — artista de horror com estilo autoral (traço que lembra Junji Ito), público que fala inglês. Portfolio: [dark.art.br](https://dark.art.br) (prints, camisetas e commissions).

A conta é de uma artista **tímida e introvertida**: a ferramenta nunca sugere conteúdo que exija rosto, voz ou performance. Tudo gira em torno do que funciona pra ela — mãos desenhando, timelapse, close de tinta, text overlay, narrativa silenciosa.

O `dark` junta:

- **calendário sazonal do nicho** (Inktober, Halloween, Friday the 13th, aniversário do Junji Ito…) — computado localmente, sempre disponível;
- **pulso da comunidade** (subreddits de horror art via API pública do Reddit);
- **persona da artista** embutida no prompt (estilo, regras duras, playbook de Instagram pra conta pequena de arte);

…e injeta tudo no modelo pra gerar ideias de reels/carrosséis/stories, pacotes de produção completos e captions prontas **em inglês** (estratégia explicada em PT-BR).

Radar é 100% sem LLM. O modelo (OpenRouter `:free`) entra em `ideias`, `pacote`, `legendas` e `stories`.

## Comandos

```bash
dark                          # radar: janelas sazonais + pulso do nicho (grátis)
dark ideias                   # 10 ideias rankeadas (reel/carrossel/post/story)
dark pacote 3                 # pacote da ideia 3: hook + shot list + caption + hashtags + alt text + stories de apoio
dark pacote "spiral reveal"   # ou de uma ideia sua
dark legendas "<tema>"        # 8 captions EN A/B com gatilho explicado
dark stories                  # plano de 7 stories pra semana (sem rosto/voz)
dark buscar "<termo>" -s      # busca YouTube como proxy de demanda (grátis)
dark refs add HorrorArt       # gerencia subreddits monitorados (grátis)
dark temas                    # lista as paletas do tema retro-terminal
```

Flags: `-f` recoleta o radar ignorando cache (6h) · `-m` lista modelos `:free` no ar · `--json` saída crua (radar/buscar/refs) pra scripts e pro skill.

## Fluxo típico

```bash
dark                 # 1. onde está a janela? (Inktober chegando? sub bombando espirais?)
dark ideias          # 2. 10 ideias rankeadas com hook pronto
dark pacote 2        # 3. pacote completo da melhor → gravar/postar
dark stories         # 4. domingo: planejar os stories da semana
```

## Instalação

```bash
# do diretório do repo (git clone … && cd tools)
bash setup.sh            # CLI no PATH (escreve 1 linha no seu rc)
bash setup.sh --skill    # só o skill /dark do Claude Code (symlink)
```

Chave (só pra geração): grátis em [openrouter.ai/keys](https://openrouter.ai/keys) →

```bash
cp .env.example .env     # e cole a OPENROUTER_API_KEY
```

## Skill /dark (Claude Code)

Mesmos comandos dentro do Claude Code (`/dark ideias`), mas quem gera é o Claude da sessão — sem chave da OpenRouter, sem limite do free tier, qualidade maior. O CLI entra só como coletor (`--json`). Estado compartilhado em `~/.dark/`: ideias geradas num lado funcionam com `pacote N` no outro.

## Configuração (.env ou shell)

| variável | pra quê |
|---|---|
| `OPENROUTER_API_KEY` | geração via CLI (radar não precisa) |
| `OPENROUTER_MODEL` | modelos a tentar, em ordem, separados por vírgula |
| `DARK_CONTEXTO` | contexto extra da artista injetado em toda geração (materiais, ritmo, séries em andamento…) |
| `DARK_DIR` | onde salvar cache/config (padrão `~/.dark`) |
| `DARK_LEMBRETE=1` | lembrete diário ao abrir o terminal se o radar do dia não foi visto |
| `DARK_TEMA` | paleta do terminal (`dark temas` lista todas; padrão `vault-gold`) |
| `RETRO_TEMA` | paleta padrão de todas as ferramentas do repo — usada quando `DARK_TEMA` não está definida |
| `NO_COLOR` | desliga todas as cores/escapes |

## Visual

A saída segue o style guide retro-terminal do repo (`.harness/styleguide-terminal.md`)
via a lib compartilhada `lib/retro.py`: paleta de um acento só, cantos retos, rótulos
em maiúsculo, zero emoji decorativo. Troque a paleta com:

```bash
dark temas                    # lista as 9 paletas com swatch
export DARK_TEMA=noir-rose    # só o dark
export RETRO_TEMA=noir-rose   # todas as ferramentas do repo
```

## Notas

- Instagram não tem API pública de leitura — por isso o pulso vem do Reddit (proxy honesto do nicho) e a demanda de formato do YouTube. Fonte fora do ar não derruba o radar: reaproveita a última coleta boa e avisa.
- Reddit bloqueia rajadas de requisição e IP de nuvem de vez em quando; o calendário sazonal é local e sempre existe.
- Free tier da OpenRouter: ~50 requests/dia sem crédito (cada `ideias`/`pacote`/`legendas`/`stories` = 1 request; fallback de modelo conta extra).
