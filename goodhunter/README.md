# goodhunter

**Caçador de software de monitoramento no Windows.** Escaneia seu sistema
atrás de programas conhecidos de vigilância corporativa, stalkerware,
keyloggers, grabadores de tela e qualquer software que monitore o que você faz
no PC.

```bash
goodhunter              # varredura completa (detecta + relatório)
goodhunter scan         # só detectar
goodhunter list         # lista o banco de dados completo (200+ ferramentas)
goodhunter report       # mostra o último relatório salvo
goodhunter cat teramind # detalhes de uma ferramenta específica
goodhunter --json       # saída em JSON (combina com scan/list)
```

## Como funciona

1. **Banco de dados** com 200+ assinaturas de software de monitoramento
   (processos, serviços, chaves de registro, diretórios, entradas de startup).
2. **Detecção ativa** (Windows): usa PowerShell para consultar processos em
   execução, serviços instalados, programas instalados, chaves de registro,
   programas de inicialização e diretórios.
3. **Classificação por risco**:
   - **Crítico** / stalkerware — keyloggers, espiões comerciais (FlexiSPY, mSpy, etc.)
   - **Alto** / corporate — monitoramento corporativo (Teramind, ActivTrak, etc.)
   - **Médio** — remote access, software de ponto eletrônico
   - **Baixo** / info — telemetria do Windows, EDRs legítimos
4. **Relatório salvo** em `~/.goodhunter/last_scan.json` para consulta posterior.

> Em macOS/Linux a varredura é limitada (sem acesso a processo/registro do
> Windows). O banco de dados completo fica disponível com `goodhunter list`.

## Instalação

```bash
# do diretório do repo (git clone … && cd tools)
bash goodhunter/setup.sh
```

Abra um terminal novo e rode `goodhunter`.

## Windows

No Windows (via Git Bash ou PowerShell), o `goodhunter` faz a varredura real
do sistema: lista todos os processos, serviços, registros e compara com o banco
de dados. É aí que a ferramenta entrega todo o valor.

## Configuração

| Variável | Pra quê | Padrão |
|---|---|---|
| `GOODHUNTER_DB` | onde salvar relatórios | `~/.goodhunter` |
| `GOODHUNTER_TEMA` | paleta | `RETRO_TEMA` |
| `GOODHUNTER_JSON` | saída JSON sempre | `0` |
| `NO_COLOR` | desliga as cores | — |

## Privacidade

O goodhunter é **100% offline**. O banco de dados é local. Nada sai da sua
máquina. Nenhuma requisição de rede é feita. Os relatórios ficam em
`~/.goodhunter/`.

---

↩ [Voltar pro índice de ferramentas](../README.md)
