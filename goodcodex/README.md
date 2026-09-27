# goodcodex

Ferramenta local para descobrir projetos e registrar evidências para o Codex. Requer Python 3.11+. Execute diretamente do checkout: `./goodcodex/goodcodex help`. Instale o comando com `bash goodcodex/setup.sh` ou pelo instalador da raiz; a ativação dos arquivos nativos é separada.

## Comandos disponíveis

```sh
./goodcodex/goodcodex scan --root /caminho/dos/projetos --realm work
./goodcodex/goodcodex projects
./goodcodex/goodcodex inspect /caminho/do/projeto
./goodcodex/goodcodex scan --json
./goodcodex/goodcodex context /caminho/do/projeto/apps/api --json
./goodcodex/goodcodex doctor /caminho/do/projeto --json
./goodcodex/goodcodex doctor
./goodcodex/goodcodex plan --json
./goodcodex/goodcodex plan /caminho/do/projeto/apps/web
./goodcodex/goodcodex recommend "corrigir login no mobile" --path /caminho/do/projeto
./goodcodex/goodcodex explain /caminho/do/projeto --task "investigar corrida entre API e app" --json
./goodcodex/goodcodex run "corrigir login no mobile" --path /caminho/do/projeto --dry-run
./goodcodex/goodcodex run "corrigir login no mobile" --path /caminho/do/projeto --model gpt-6-sol
./goodcodex/goodcodex evaluate add medicao.json
./goodcodex/goodcodex evaluate report --json
```

`--json` funciona antes ou depois do subcomando. `scan` aceita vários `--root`. Se omitidos, usa `roots` de `${XDG_CONFIG_HOME:-~/.config}/goodcodex/preferences.json`; sem preferências, examina o diretório atual. `projects`, `inspect`, `context` e `doctor` leem o último registro. `inspect` e `context` aceitam caminho dentro de um checkout ou ID. A saída informa stack, branch, comandos declarados, fontes de contexto e avisos. **Comandos são apenas identificados, nunca executados.** `plan` continua somente leitura; `apply` é a ação explícita que instala os arquivos nativos.

`context` seleciona o checkout pelo caminho mais específico e o pacote mais próximo do alvo. Retorna apenas fontes cujo escopo é ancestral desse alvo. `AGENTS.md` é identificado como instrução nativa do Codex; `CLAUDE.md`, README e `.harness` são referências para revisão, sem importação automática. A saída inclui o alvo canônico de links internos, mas não inclui o corpo dos documentos. Links externos ao checkout são diagnosticados e excluídos. Um contexto de cliente não é acrescentado ao de outro checkout. O campo `precedence` explica a composição sugerida pelo goodcodex; a precedência efetiva do Codex continua sendo a nativa e depende do pedido e da configuração em uso.

`doctor` consulta `codex --version` e `codex --help` localmente, lê TOML de configuração global e do checkout selecionado e diagnostica perfis antigos, overrides de modelo/esforço, fontes ausentes, referências Markdown ausentes/externas, comandos próprios de CLAUDE e alegações de stack que divergem do manifesto. As pistas de documentação são heurísticas para revisão, não prova de erro. Sem caminho, examina somente CLI e configuração global. A saída `surfaces` separa CLI consultado localmente, app/IDE descritos na documentação e ChatGPT Work hospedado. Não consulta autenticação, modelos remotos, integrações pagas ou o app; a disponibilidade dos modelos e a aplicação de configuração de projeto continuam incertas. `doctor` não executa o `codex doctor` nativo nem altera arquivos.

O scanner reconhece Git normal e worktrees com gitfile, pacotes Node/Flutter/Dart/Rust/Go/Python, Terraform, Railway e Wrangler; registra lockfiles e detecta conflito entre gerenciadores Node. Monorepos são um checkout com vários pacotes; checkouts aninhados e irmãos têm IDs distintos. A busca tem profundidade limitada, ignora dependências e artefatos gerados e não segue symlinks. Symlinks de `.harness` são registrados com alvo canônico sem copiar o conteúdo. Um diretório inacessível, manifesto inválido ou link quebrado gera aviso; informação ausente não vira certeza.

`scan` não escreve nos projetos examinados. O registro fica em `${XDG_DATA_HOME:-~/.local/share}/goodcodex/registry.json`, com permissão de arquivo 0600 e troca atômica. Contém caminhos locais, nomes de pacotes e scripts declarados: trate esse arquivo como privado. O scanner lê somente `package.json` para sinais e comandos, além de metadados de diretório/Git; não lê `.env`, credenciais, conteúdo de AGENTS/CLAUDE, dumps nem backups. Um `package.json` pode conter texto sensível nos scripts; revise antes de compartilhar a saída JSON. A ferramenta não exporta conteúdo de contexto.

## Contrato de dados v1

Os schemas em `schemas/` definem documentos separados:

| Arquivo | Responsabilidade |
|---|---|
| `preferences.schema.json` | Raízes, ambiente e modo pessoal. |
| `registry.schema.json` | Evidências do scanner, com um registro por checkout e avisos. |
| `overrides.schema.json` | Escolhas manuais por `projectId`; um novo scan não as substitui. |
| `evaluation.schema.json` | Resultado observado de uma execução de avaliação, fornecido manualmente. |

Todos trazem `schemaVersion: 1`. Versão diferente é recusada com diagnóstico, sem sobrescrever o arquivo em comandos de leitura. `id` é derivado do caminho absoluto do checkout; `group` é uma sugestão baseada no nome do diretório. `root` preserva o caminho observado, `canonicalRoot` indica o caminho resolvido e `gitDir`/`gitCommonDir` distinguem worktrees. `contextSources` guarda referências, tipo, escopo e alvo, sem texto dos arquivos. Overrides aparecem na visualização sob `override` e permanecem no arquivo próprio. As fixtures sintéticas não incluem dados de clientes.

Defaults provisórios: modo `balanced`, CLI primeiro, configuração local antes de perfis globais e até dois subagentes sugeridos quando instruções aplicáveis autorizarem. A configuração global existente permanece intacta. Os formatos nativos de perfil/agente foram validados na etapa 1 com Codex 0.157.1; suporte no app ainda não foi verificado.

## Preview de agentes, perfis e presets

`plan` mostra o conteúdo completo e o diff unificado de sete arquivos propostos em `${CODEX_HOME:-~/.codex}`: `gc-fast`, `gc-balanced` e `gc-deep` como perfis `*.config.toml`, mais quatro agentes em `agents/`. Cada arquivo aparece como `create`, `identical` ou `change`. O comando apenas lê; não instala, reescreve ou cria diretórios de destino. `--json` inclui `files`, `modelPolicy`, `agentPolicy`, avisos e a ordem de precedência. A aplicação reversível está disponível nos comandos abaixo. O preview marca cada arquivo com `applyAction`: `write`, `none` ou `conflict`. Um arquivo preexistente diferente exige `apply --replace`; um arquivo gerenciado editado precisa ser preservado/resolvido manualmente antes de `update` ou `rollback`.

Os perfis sugerem Luna/high para trabalho focado (`gc-fast`), Sol/medium para implementação comum (`gc-balanced`) e Astra/low como ponto inicial para problemas difíceis (`gc-deep`). São hipóteses para avaliação, não troca automática do seu modelo atual. Os agentes têm escolha explícita própria: explorer e researcher usam Luna/high; implementer usa Sol/medium; reviewer usa Sol/high. No agente personalizado, o modelo e esforço do arquivo prevalecem sobre valores do spawn e do pai. O agente só atua quando uma delegação for solicitada ou prevista por instrução aplicável. Os templates não alteram política de aprovação, permissões do pai nem autorizam ações externas.

Com um caminho registrado, `plan` recomenda presets a partir da stack do pacote selecionado: `web-react` (inclui sinal TanStack Start), `web-next`, `web-static` (Astro), `web-lit`, `api-node`, `data`, `mobile-expo`, `mobile-flutter`, `cli`, `native-rust`, `native-go`, `edge-cloudflare`, `infra` (Terraform/Railway), `ai-media` e `sdk`. Esses textos são instruções curtas para o contrato de delegação, exibidas no JSON como `presetInstructions`; não são importados automaticamente nem copiados para `AGENTS.md`. Um pacote pode receber mais de um preset. `docs-release` está disponível para escolha humana por tipo de tarefa, pois nenhum manifesto prova que uma mudança é um relatório ou release. Ruby, Dart sem Flutter e React Native sem Expo ficam sem preset específico; registre as regras locais no pedido. Pipelines de IA/mídia em Python também podem não ser detectados automaticamente. Sinais de IA/mídia e SDK em Node são heurísticas de dependências e exports/types, não prova do workflow real. Verifique sempre o framework e as regras locais antes de aplicar um preset, especialmente diferenças entre ORMs e restrições de Expo.

O agente principal coordena o pedido e integra os resultados. A delegação só é acionada por pedido explícito ou instrução aplicável de `AGENTS.md`/skill. Antes de iniciar, o principal delimita objetivo, checkout/pacote, arquivos de responsabilidade, restrições, critério de conclusão e formato de retorno. O retorno inclui alterações ou achados, evidência, verificações e pendências. Tarefas simples ficam com um agente. Trabalhos no mesmo contrato ou arquivo são sequenciais. Explorer e reviewer são somente leitura. O implementer testa a própria mudança; researcher cita documentação primária e versão. Skills existentes continuam sendo a fonte dos procedimentos especializados, sem cópia integral nos agentes. `plan --json` expõe este contrato em `delegation`.

Os três perfis gerados configuram `agents.max_concurrent_threads_per_session = 2`, que limita threads de subagentes simultâneas e exclui o principal. `goodcodex run` passa o mesmo limite por `--config`, mesmo sem perfil selecionado. `maxSuggestedSubagents` nas preferências pode ajustar o limite de `run` de 1 a 8; valor 0 passa `agents.enabled=false`. A configuração de um projeto confiável pode mudar o limite quando uma sessão é iniciada fora do launcher ou sem perfil. O goodcodex não cria subagentes por si nem instala um limite global. Consulte `doctor` e `/debug-config` na sessão para conferir camadas efetivas.

A [documentação oficial de configuração](https://learn.chatgpt.com/docs/config-file/config-basic) define a ordem: flags CLI, configuração do projeto confiável, perfil, configuração global e defaults. `plan` mostra a composição sugerida de modelo/esforço para cada perfil e sinaliza overrides do projeto. Confiança do projeto, flags futuras, disponibilidade dos modelos e carregamento dos arquivos no app não foram verificados localmente. Os perfis separados exigem Codex 0.134.0 ou posterior. O formato dos arquivos, inclusive o limite de subagentes, foi conferido com o CLI 0.157.1 em `CODEX_HOME` temporário via `codex --profile ... debug prompt-input`; isso valida carregamento local sem executar inferência. A sintaxe dos [agentes personalizados](https://learn.chatgpt.com/docs/agent-configuration/subagents) foi validada com TOML e documentação oficial. `--strict-config` não funciona com `debug prompt-input` nesta versão do CLI.

## Instalação reversível

`bash goodcodex/setup.sh` instala somente o comando no PATH pelo bloco compartilhado de tools. Também é possível selecioná-lo no `bash setup.sh` da raiz. Isso não altera `~/.codex`, não escolhe perfil e não inicia o Codex. `goodhelp goodcodex` abre a ajuda; `goodcodex temas` abre o catálogo visual compartilhado com `goodhelp temas`. O CLI atual imprime texto simples e JSON e não aplica cores aos dados.

Depois de revisar `goodcodex plan`, use `goodcodex apply` para instalar os três perfis e quatro agentes em `${CODEX_HOME:-~/.codex}`. `apply --replace` aceita arquivos preexistentes diferentes e guarda uma cópia integral antes de substituí-los. `status` mostra `managed`, `modified`, `missing`, `unmanaged` ou `absent`. `update` aplica versões novas dos templates aos arquivos gerenciados. `rollback` devolve os arquivos originais e remove apenas os arquivos criados pelo goodcodex. A configuração global `config.toml` não é editada. O perfil continua opt-in pelo comando `codex --profile gc-balanced`, por exemplo.

O manifesto `installation.json` e backups ficam em `${XDG_DATA_HOME:-~/.local/share}/goodcodex/`, com hashes SHA-256. Escritas usam troca atômica e um lock exclusivo; um journal permite recuperar uma operação interrompida no próximo comando de escrita. Se um arquivo gerenciado mudou ou sumiu, o comando para com conflito antes de escrever qualquer destino. Preserve a edição, restaure o conteúdo instalado e tente de novo. Backups originais permanecem até o rollback. Não edite manifesto/journal manualmente; eles são dados locais privados.

## Recomendação e execução no terminal

`recommend` classifica a descrição da tarefa por escopo focado, investigação e sinais de risco (como autenticação, pagamentos, RLS e migração). O modo de `preferences.json` (`economy`, `balanced` ou `quality`) ajusta essa sugestão. A saída mostra motivo, modelo, esforço e alertas. A classificação é uma heurística curta; revise tarefas ambíguas. `explain` acrescenta as camadas de configuração observadas: configuração global e `.codex/config.toml` do checkout até o pacote mais próximo. O projeto só prevalece se o Codex confiar nele. A saída indica o valor que essas camadas produziriam sem as flags do launcher e a escolha efetiva com flags. Não lê regras administrativas, estado de confiança nem a disponibilidade remota.

`run` exibe a decisão e inicia o Codex interativo no diretório selecionado. Passa `--model`, `--config model_reasoning_effort=...` e o limite de subagentes como argumentos separados, para que a escolha explícita prevaleça sobre projeto, perfil e configuração global. O prompt é um único argumento literal depois de `--`; não há shell nem `eval`. `--dry-run` mostra o array sem iniciar uma sessão. `--json` imprime os metadados de decisão; em execução real, a saída subsequente pertence ao Codex. O código de saída do Codex é propagado. `run` não altera permissões, sandbox, política de aprovação nem inicia deploy ou publicação por conta própria; a sessão obedece às configurações e instruções aplicáveis do Codex.

`--model` aceita um ID exato e tem precedência sobre a recomendação. Sem esse override, se `availableModels` estiver definido em `preferences.json`, o goodcodex escolhe uma alternativa registrada quando o modelo preferido não aparece. Um override ausente dessa lista é mostrado como indisponível e bloqueia `run`. Exemplo: `"availableModels": ["gpt-6-sol", "gpt-6-luna"]`. A lista é declaração local do usuário, não descoberta nem prova de acesso; sem ela, a disponibilidade aparece como `unknown`, e o serviço ainda pode recusar o modelo. Falta de acesso deve ser corrigida na lista ou no modelo escolhido, não por escaladas repetidas. Nenhuma inferência é feita em `recommend`, `explain` ou `--dry-run`.

A [documentação oficial de configuração](https://learn.chatgpt.com/docs/config-file/config-basic) confirma a precedência de flags, projeto confiável, perfil e configuração global. A [referência de comandos](https://learn.chatgpt.com/docs/developer-commands) descreve `--model`, `--config` e `--cd`. A [página de modelos](https://learn.chatgpt.com/docs/models) descreve Astra, Sol e Luna, mas a disponibilidade varia por conta e cliente. Os perfis em arquivo são selecionáveis no CLI; o launcher usa flags para evitar ambiguidade. O app não recebe a seleção feita por `goodcodex run`. A [documentação de configurações](https://learn.chatgpt.com/docs/developer-settings) afirma que os agentes no app compartilham configuração com CLI/IDE, e a [documentação de subagentes](https://learn.chatgpt.com/docs/agent-configuration/subagents) descreve atividade visível no app. O carregamento destes arquivos gerados, a escolha de perfil e o limite efetivo ainda não foram verificados em uma sessão do app. Use controles do app e `/debug-config` para conferir o modelo e as camadas. Chats do ChatGPT Work são hospedados e não leem arquivos locais do Codex.

## Avaliação opcional

`evaluate add` aceita um JSON com métricas **observadas** e salva uma cópia privada em `${XDG_DATA_HOME:-~/.local/share}/goodcodex/evaluations/`. `evaluate report` agrega baseline e política proposta; `--json` fornece contagens de qualidade, retrabalho, tempo e uso. Tempo/tokens ausentes aparecem como `null` e “não medido”. O comando não inicia Codex nem estima custo. Veja [EVALUATION.md](./EVALUATION.md) para os dez casos preparados, o protocolo de pilotos, limitações e backlog. A suíte local verifica a ferramenta; nenhuma comparação real de modelos foi executada.
