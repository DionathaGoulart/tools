# goodpet

Tamagotchi no terminal. Você adota um ovo, ele choca e vira bebê, criança e
adulto — se você cuidar. Fome, felicidade, energia e higiene caem com o tempo
**mesmo com o terminal fechado**: descuido vira doença, doença sem cura vira
lápide. Comandos rápidos pro dia a dia e um modo vivo com o bicho animado na
tela. Zero dependências — Python puro, nenhum request de rede.

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ● ● ●  root@goodpet: ~/bilu             12:04:31 ┃▒
┠──────────────────────────────────────────────────┨▒
┃                     .---.  *                     ┃▒
┃                    ( ^ ^ )                       ┃▒
┃                    _\_u_/_                       ┃▒
┃                    / |   | \                     ┃▒
┃                      d   b                       ┃▒
┃                                                  ┃▒
┃ BILU  [CRIANÇA]  idade 1d 6h                     ┃▒
┃                                                  ┃▒
┃ FOME       ██████████████▒▒▒▒   80%              ┃▒
┃ FELICIDADE ██████████████████  100%              ┃▒
┃ ENERGIA    ███████████▒▒▒▒▒▒▒   64%              ┃▒
┃ HIGIENE    █████████████▒▒▒▒▒   75%              ┃▒
┃                                                  ┃▒
┃ tudo em ordem                                    ┃▒
┠──────────────────────────────────────────────────┨▒
┃ [F]EED [P]LAY [L]IMPAR [S]ONO [H]EAL [Q] SAIR    ┃▒
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛▒
 ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
```

```bash
goodpet new Bilu           # adota um ovo (nome opcional)
goodpet                    # card do pet: arte + barras + fase
goodpet feed               # alimenta (fome +30)
goodpet play               # brinca (felicidade +25, cansa)
goodpet clean              # dá banho (higiene 100)
goodpet sleep              # põe pra dormir (energia sobe dormindo)
goodpet wake               # acorda
goodpet heal               # dá remédio quando doente
goodpet watch              # modo vivo: tela animada, teclas de ação
goodpet log                # últimos eventos + totais de cuidado
goodpet temas              # paletas disponíveis
```

## Como funciona

O pet vive num JSON e o tempo passa por **timestamp**: qualquer comando primeiro
simula tudo que aconteceu desde a última vez (em passos de 60 s), então não
existe daemon — mas o bicho sente sua ausência. Eventos ocorridos offline
aparecem no card ("enquanto você esteve fora: …").

Taxas por hora (acordado / dormindo):

| Stat | Acordado | Dormindo |
|---|---|---|
| Fome | −2.5 | −1.25 |
| Energia | −5 | **+12.5** (0→100 em 8h) |
| Higiene | −1.5 | −0.75 |
| Felicidade | −1.5 (extra: −3 fome baixa, −3 sujeira, −4 doente) | congela |

Regras de vida:

- **Evolução** por idade: ovo choca em `1h` → bebê · criança em `24h` · adulto
  em `72h`. Doente não evolui (cura primeiro).
- **Desmaio**: energia zerada derruba o bicho no sono (felicidade −10). Dormindo
  até encher, ele acorda sozinho.
- **Doença**: higiene < 20 por 6h contínuas, ou fome zerada por 12h.
- **Morte**: fome zerada por 24h, ou doença sem remédio por 48h. Sem nenhum
  cuidado o pet dura ~2,7 dias. `goodpet new` recomeça.

## Aparência

Segue o style guide da casa: janela em box-drawing com sombra offset, barras
`█▒`, chips `[MAIUSCULA]`, paleta de um acento só. A arte tem 2 frames por pose
(normal, feliz, triste, doente, dormindo) que alternam a cada segundo no modo
`watch`. Fora de TTY ou em terminal estreito, cai pra texto plano.

## Privacidade

Tudo fica em `~/.goodpet/pet.json` na sua máquina. Nenhum request de rede,
nenhuma telemetria — só você e o bicho.

## Instalação

```bash
bash ~/Desktop/tools/games/goodpet/setup.sh
```

Abra um terminal novo (ou `source ~/.zshrc`) e rode `goodpet new`.

## Configuração

| Variável | Pra quê | Padrão |
|---|---|---|
| `GOODPET_DIR` | onde o pet mora | `~/.goodpet` |
| `GOODPET_TEMA` | paleta (veja `goodpet temas`) | `vault-gold` |
| `GOODPET_SEM_ANIM` | qualquer valor desliga animação e reveal | — |
| `NO_COLOR` | qualquer valor desliga as cores | — |

## Temas

Nove paletas vindas do style guide (`goodpet temas` lista com swatch):

| Escuras | Claras |
|---|---|
| `vault-gold` (padrão), `noir-rose`, `midnight-ember`, `cyber-teal`, `velvet-purple` | `abyss-frost`, `crimson-chalk`, `forest-mist`, `sand-dusk` |

```bash
export GOODPET_TEMA=cyber-teal
```

Cores true-color (24-bit) quando `COLORTERM=truecolor`; senão cai pro ANSI
básico de 8 cores.

---

↩ [Voltar pro índice de ferramentas](../../README.md)
