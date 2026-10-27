# goodmon

Monitor portátil de CPU, RAM, swap, disco, rede, uptime e processos para terminal.

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
goodmon                         # atualiza a cada 1 s
goodmon --once --sort ram        # uma amostra
goodmon --json --disk /dados     # integração com scripts
goodmon --interval 2 --top 15
goodmon temas
```

`GOODMON_TEMA` e `RETRO_TEMA` escolhem a paleta. `NO_COLOR`, `--no-color` e `TERM=dumb` produzem uma amostra em texto, sem ANSI nem animação. `GOODMON_SEM_ANIM=1` mantém o tema e produz uma amostra estática. Saída redirecionada também gera só uma amostra. A execução procura `goodmon/.venv` se o Python atual não tiver psutil; no Windows, o launcher prioriza o ambiente virtual ativo, depois o ambiente local.

CPU e rede usam duas leituras. A primeira amostra do painel espera 0,1 s; snapshots usam `--interval` (1 s por padrão). `--json` aplica `--sort` e `--top`. Durante o painel, `q` sai, `c`/`m` mudam a ordem por CPU/RAM e Ctrl-C interrompe. Janelas pequenas reduzem a quantidade de processos visíveis; o JSON mantém o limite solicitado.

RAM usada corresponde a `total - disponível`. Disco mostra ocupação do volume escolhido por `--disk`; rede mostra a soma das interfaces em bytes por segundo. Métricas opcionais indisponíveis aparecem como `N/D` (ou `null` no JSON). Processos que encerram ou negam acesso são ignorados; CPU por processo pode passar de 100% quando usa vários núcleos. Os números em KiB/MiB/GiB usam base 1024. O monitor apenas consulta métricas e não encerra processos.
