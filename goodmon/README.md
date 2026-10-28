# goodmon

Monitor visual de CPU e RAM do computador inteiro, com gráficos de histórico e pizza dos cinco maiores processos.

Requer Python 3.10+ e [psutil](https://psutil.io/). Execute a instalação abaixo na raiz deste repositório.

```bash
# macOS/Linux
python3 -m venv goodmon/.venv
goodmon/.venv/bin/python -m pip install -r goodmon/requirements.txt
goodmon/goodmon
```

```powershell
# PowerShell
py -3 -m venv goodmon/.venv
.\goodmon\.venv\Scripts\python.exe -m pip install -r goodmon\requirements.txt
.\goodmon\goodmon.cmd
```

No macOS/Linux/Git Bash, instale no PATH da família com `bash goodmon/setup.sh` e abra um terminal novo. O comando também aparece no instalador central e no `goodhelp`.

No PowerShell, acrescente a pasta ao PATH da sessão: `$env:Path = "$(Resolve-Path .\goodmon);$env:Path"`. No CMD, use `set "PATH=%CD%\goodmon;%PATH%"` a partir da raiz do repositório. Também é possível executar `goodmon\goodmon.cmd` diretamente. O Windows usa Python nativo; no WSL, as métricas representam o ambiente Linux do WSL.

```bash
goodmon                         # painel visual: CPU, RAM e top 5 por RAM
goodmon --once --sort cpu        # uma amostra por CPU
goodmon --json --disk /dados     # integração com scripts
goodmon --interval 2             # atualização a cada 2 s
goodmon --json --top 15          # mais processos na saída para scripts
goodmon temas
```

`GOODMON_TEMA` e `RETRO_TEMA` escolhem a paleta. `NO_COLOR`, `--no-color` e `TERM=dumb` produzem uma amostra em texto, sem ANSI nem animação. `GOODMON_SEM_ANIM=1` mantém o tema e produz uma amostra estática. Saída redirecionada também gera só uma amostra. A execução procura `goodmon/.venv` se o Python atual não tiver psutil; no Windows, o launcher prioriza o ambiente virtual ativo, depois o ambiente local.

CPU e rede usam duas leituras. A primeira amostra do painel espera 0,1 s; snapshots usam `--interval` (1 s por padrão). O histórico cresce com amostras reais, em escala de 0 a 100%. A pizza mostra a proporção de uso **entre os cinco processos exibidos**, não a divisão de toda a memória do computador. RAM é a visão inicial; `m` e `c` alternam RAM/CPU, e `q` sai. Os botões também aceitam clique em terminais macOS/Linux compatíveis com mouse SGR. Trocar a visão mantém a cadência das amostras.

Janelas menores compactam os gráficos; em larguras muito estreitas, fica a lista dos maiores processos. Sem cores, os números das fatias correspondem à legenda. O painel mostra no máximo cinco processos; `--top 0` oculta a pizza. `--json` preserva todas as métricas e aplica `--sort` e `--top` integralmente (até 50 processos).

RAM usada corresponde a `total - disponível`. No JSON, disco mostra a ocupação do volume escolhido por `--disk`; rede mostra a soma das interfaces em bytes por segundo. Métricas opcionais indisponíveis aparecem como `null`. Processos que encerram ou negam acesso são ignorados; CPU por processo pode passar de 100% quando usa vários núcleos. Os números em KiB/MiB/GiB usam base 1024. O monitor apenas consulta métricas e não encerra processos.
