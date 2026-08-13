# goodnerd

Teatro de "hacker" no terminal — puro efeito visual, **nada real acontece**.
Você digita `goodnerd` e a tela enche de varredura de portas, quebra de senha,
compilação/deploy e chuva de código estilo Matrix. Serve pra impressionar quem
não programa (ou só pra brincar). Zero dependências — bash puro, usa o tema
retrô compartilhado (`lib/retro.sh`).

> ⚠️ Não faz nenhuma conexão de rede, não toca em arquivo nenhum, não invade
> nada. É 100% cenográfico, tipo os filmes de hacker.

```
  [ * ] nmap -sS -T4 -A -p- 128.120.18.179
  22/tcp   open     ssh              v7.4.2
  443/tcp  open     https            v1.1.0
  3306/tcp filtered mysql            v5.7.9
  [ ~ ] 4 exploitable services identified
  injecting payload      ██████████████████████▒▒▒▒▒▒  79%
  bypassing firewall...
  [OK ] kernel exploit landed — uid=0(root)

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ● ● ●  root@0day: ~/breach                          08:36:33 ┃▒
┠────────────────────────────────────────────────────────────────┨▒
┃                                                                ┃▒
┃                        ACCESS GRANTED                          ┃▒
┃         shell obtained on 128.120.18.179 · uid=0(root)         ┃▒
┃                                                                ┃▒
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛▒
 ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
```

```bash
goodnerd                   # operação completa: scan → crack → deploy → matrix
goodnerd scan              # varredura de portas + invasão + ACCESS GRANTED
goodnerd crack             # quebra de hash/senha, char por char
goodnerd deploy            # compilando/deployando estilo make/npm
goodnerd matrix            # chuva de código (para quando você aperta uma tecla)
goodnerd matrix 10         # chuva de código por 10 segundos
goodnerd temas             # paletas disponíveis
goodnerd -h                # ajuda
```

Velocidade: `--fast` / `--slow` (ou `export GOODNERD_VEL=fast|normal|slow`).
Tema: `export GOODNERD_TEMA=<nome>` (veja `goodnerd temas`) — o padrão é `cyber-teal`,
o clássico verde/ciano de terminal hacker.

Fora de um terminal de verdade (saída redirecionada) ele degrada pra uma linha
de texto simples, sem animação.

## Instalar

```bash
# do diretório do repo (git clone … && cd tools)
bash setup.sh          # adiciona o comando `goodnerd` ao seu PATH
```

Ou use o instalador da raiz do repo (`bash ../setup.sh`) e marque **goodnerd**.
