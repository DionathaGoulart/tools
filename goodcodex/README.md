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
```

`--json` funciona antes ou depois do subcomando. `scan` aceita vários `--root`. Se omitidos, usa `roots` de `${XDG_CONFIG_HOME:-~/.config}/goodcodex/preferences.json`; sem preferências, examina o diretório atual. `projects`, `inspect`, `context` e `doctor` leem o último registro. `inspect` e `context` aceitam caminho dentro de um checkout ou ID. A saída informa stack, branch, comandos declarados, fontes de contexto e avisos. **Comandos são apenas identificados, nunca executados.** `plan` continua somente leitura; `apply` é a ação explícita que instala os arquivos nativos.

`context` seleciona o checkout pelo caminho mais específico e o pacote mais próximo do alvo. Retorna apenas fontes cujo escopo é ancestral desse alvo. `AGENTS.md` é identificado como instrução nativa do Codex; `CLAUDE.md`, README e `.harness` são referências para revisão, sem importação automática. A saída inclui o alvo canônico de links internos, mas não inclui o corpo dos documentos. Links externos ao checkout são diagnosticados e excluídos. Um contexto de cliente não é acrescentado ao de outro checkout. O campo `precedence` explica a composição sugerida pelo goodcodex; a precedência efetiva do Codex continua sendo a nativa e depende do pedido e da configuração em uso.

`doctor` consulta `codex --version` e `codex --help` localmente, lê TOML de configuração global e do checkout selecionado e diagnostica perfis antigos, overrides de modelo/esforço, fontes ausentes, referências Markdown ausentes/externas, comandos próprios de CLAUDE e alegações de stack que divergem do manifesto. As pistas de documentação são heurísticas para revisão, não prova de erro. Sem caminho, examina somente CLI e configuração global. Não consulta autenticação, modelos remotos, integrações pagas ou o app; a disponibilidade dos modelos e a aplicação de configuração de projeto continuam incertas. `doctor` não executa o `codex doctor` nativo nem altera arquivos.

O scanner reconhece Git normal e worktrees com gitfile, pacotes Node/Flutter/Dart/Rust/Go/Python, Terraform e Wrangler; registra lockfiles e detecta conflito entre gerenciadores Node. Monorepos são um checkout com vários pacotes; checkouts aninhados e irmãos têm IDs distintos. A busca tem profundidade limitada, ignora dependências e artefatos gerados e não segue symlinks. Symlinks de `.harness` são registrados com alvo canônico sem copiar o conteúdo. Um diretório inacessível, manifesto inválido ou link quebrado gera aviso; informação ausente não vira certeza.

`scan` não escreve nos projetos examinados. O registro fica em `${XDG_DATA_HOME:-~/.local/share}/goodcodex/registry.json`, com permissão de arquivo 0600 e troca atômica. Contém caminhos locais, nomes de pacotes e scripts declarados: trate esse arquivo como privado. O scanner lê somente `package.json` para sinais e comandos, além de metadados de diretório/Git; não lê `.env`, credenciais, conteúdo de AGENTS/CLAUDE, dumps nem backups. Um `package.json` pode conter texto sensível nos scripts; revise antes de compartilhar a saída JSON. A ferramenta não exporta conteúdo de contexto.

## Contrato de dados v1

Os schemas em `schemas/` definem documentos separados:

| Arquivo | Responsabilidade |
|---|---|
| `preferences.schema.json` | Raízes, ambiente e modo pessoal. |
| `registry.schema.json` | Evidências do scanner, com um registro por checkout e avisos. |
| `overrides.schema.json` | Escolhas manuais por `projectId`; um novo scan não as substitui. |

Todos trazem `schemaVersion: 1`. Versão diferente é recusada com diagnóstico, sem sobrescrever o arquivo em comandos de leitura. `id` é derivado do caminho absoluto do checkout; `group` é uma sugestão baseada no nome do diretório. `root` preserva o caminho observado, `canonicalRoot` indica o caminho resolvido e `gitDir`/`gitCommonDir` distinguem worktrees. `contextSources` guarda referências, tipo, escopo e alvo, sem texto dos arquivos. Overrides aparecem na visualização sob `override` e permanecem no arquivo próprio. As fixtures sintéticas não incluem dados de clientes.

Defaults provisórios: modo `balanced`, CLI primeiro, configuração local antes de perfis globais e até dois subagentes sugeridos quando instruções aplicáveis autorizarem. A configuração global existente permanece intacta. Os formatos nativos de perfil/agente foram validados na etapa 1 com Codex 0.157.1; suporte no app ainda não foi verificado.

## Preview de agentes, perfis e presets

`plan` mostra o conteúdo completo e o diff unificado de sete arquivos propostos em `${CODEX_HOME:-~/.codex}`: `gc-fast`, `gc-balanced` e `gc-deep` como perfis `*.config.toml`, mais quatro agentes em `agents/`. Cada arquivo aparece como `create`, `identical` ou `change`. O comando apenas lê; não instala, reescreve ou cria diretórios de destino. `--json` inclui `files`, `modelPolicy`, `agentPolicy`, avisos e a ordem de precedência. A aplicação reversível está disponível nos comandos abaixo. O preview marca cada arquivo com `applyAction`: `write`, `none` ou `conflict`. Um arquivo preexistente diferente exige `apply --replace`; um arquivo gerenciado editado precisa ser preservado/resolvido manualmente antes de `update` ou `rollback`.

Os perfis sugerem Luna/high para trabalho focado (`gc-fast`), Sol/medium para implementação comum (`gc-balanced`) e Astra/low como ponto inicial para problemas difíceis (`gc-deep`). São hipóteses para avaliação, não troca automática do seu modelo atual. Os agentes têm escolha explícita própria: explorer e researcher usam Luna/high; implementer usa Sol/medium; reviewer usa Sol/high. No agente personalizado, o modelo e esforço do arquivo prevalecem sobre valores do spawn e do pai. O agente só atua quando uma delegação for solicitada ou prevista por instrução aplicável. Os templates não alteram política de aprovação, permissões do pai nem autorizam ações externas.

Com um caminho registrado, `plan` também recomenda os presets iniciais a partir da stack do pacote selecionado: `web-react`, `web-next`, `api-node`, `data`, `mobile-expo` e `cli`. Esses textos são instruções curtas para o contrato de delegação, exibidas no JSON como `presetInstructions`; não são importados automaticamente nem copiados para `AGENTS.md`. Um pacote pode receber mais de um preset. Verifique sempre o framework e as regras locais antes de aplicá-los, especialmente diferenças entre ORMs e restrições de Expo.

O agente principal coordena o pedido e integra os resultados. Uma delegação útil informa objetivo, checkout/pacote, arquivos de responsabilidade, restrições, critério de conclusão e formato de retorno. O retorno inclui alterações ou achados, evidência, verificações e pendências. Tarefas simples ficam com um agente; quando houver autorização para delegar, o limite sugerido é dois subagentes simultâneos. Trabalhos no mesmo contrato ou arquivo são sequenciais. Explorer e reviewer são somente leitura. O implementer testa a própria mudança; researcher cita documentação primária e versão. Skills existentes continuam sendo a fonte dos procedimentos especializados, sem cópia integral nos agentes.

A [documentação oficial de configuração](https://learn.chatgpt.com/docs/config-file/config-basic) define a ordem: flags CLI, configuração do projeto confiável, perfil, configuração global e defaults. `plan` mostra a composição sugerida de modelo/esforço para cada perfil e sinaliza overrides do projeto. Confiança do projeto, flags futuras, disponibilidade dos modelos e suporte do app não são verificados. Os perfis separados exigem Codex 0.134.0 ou posterior. O formato dos arquivos foi conferido com o CLI 0.157.1 em `CODEX_HOME` temporário via `codex --profile ... debug prompt-input`; isso valida carregamento local sem executar inferência. A sintaxe dos [agentes personalizados](https://learn.chatgpt.com/docs/agent-configuration/subagents) foi validada com TOML e documentação oficial. `--strict-config` não funciona com `debug prompt-input` nesta versão do CLI.

## Instalação reversível

`bash goodcodex/setup.sh` instala somente o comando no PATH pelo bloco compartilhado de tools. Também é possível selecioná-lo no `bash setup.sh` da raiz. Isso não altera `~/.codex`, não escolhe perfil e não inicia o Codex. `goodhelp goodcodex` abre a ajuda; `goodcodex temas` abre o catálogo visual compartilhado com `goodhelp temas`. O CLI atual imprime texto simples e JSON e não aplica cores aos dados.

Depois de revisar `goodcodex plan`, use `goodcodex apply` para instalar os três perfis e quatro agentes em `${CODEX_HOME:-~/.codex}`. `apply --replace` aceita arquivos preexistentes diferentes e guarda uma cópia integral antes de substituí-los. `status` mostra `managed`, `modified`, `missing`, `unmanaged` ou `absent`. `update` aplica versões novas dos templates aos arquivos gerenciados. `rollback` devolve os arquivos originais e remove apenas os arquivos criados pelo goodcodex. A configuração global `config.toml` não é editada. O perfil continua opt-in pelo comando `codex --profile gc-balanced`, por exemplo.

O manifesto `installation.json` e backups ficam em `${XDG_DATA_HOME:-~/.local/share}/goodcodex/`, com hashes SHA-256. Escritas usam troca atômica e um lock exclusivo; um journal permite recuperar uma operação interrompida no próximo comando de escrita. Se um arquivo gerenciado mudou ou sumiu, o comando para com conflito antes de escrever qualquer destino. Preserve a edição, restaure o conteúdo instalado e tente de novo. Backups originais permanecem até o rollback. Não edite manifesto/journal manualmente; eles são dados locais privados.

`recommend`, `explain` e `run` pertencem à etapa seguinte.
