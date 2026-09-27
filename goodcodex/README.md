# goodcodex

Fundação da ferramenta que prepara contexto e configuração do Codex por projeto. A primeira entrega oferece apenas `goodcodex help`, `goodcodex --help` e `goodcodex --version`. A entrada ainda é executada diretamente do checkout: `./goodcodex/goodcodex help`. Ela não instala nem modifica configurações.

Requisito: Python 3.11 ou superior. O núcleo planejado usa `tomllib` da biblioteca padrão; não há dependências de execução externas. A integração com o instalador da família good fica para a etapa 5.

## Contrato de dados v1

Os schemas JSON em `schemas/` definem arquivos locais separados:

| Arquivo | Responsabilidade |
|---|---|
| `preferences.schema.json` | Raízes configuradas, modo e opções pessoais. |
| `registry.schema.json` | Evidências determinísticas do scanner, com um registro por checkout. |
| `overrides.schema.json` | Escolhas manuais por `projectId`; um novo scan não as substitui. |

Cada documento traz `schemaVersion: 1`. Campos desconhecidos são rejeitados nesta versão para evitar interpretar dados de uma versão futura de forma errada. `id` identifica o checkout no registro; `group` pode agrupar checkouts do mesmo produto. `root` é o caminho observado e `canonicalRoot` é o alvo resolvido. `gitDir` e `gitCommonDir` são distintos para representar worktrees. `contextSources` guarda caminhos, tipo, escopo, confiança e alvo canônico, sem copiar o texto dos arquivos. `evidence` aponta para arquivos e sinais observados, sem guardar segredos. O registro pode conter caminhos privados e deve permanecer fora do repositório. As fixtures em `tests/fixtures/goodcodex/` usam apenas nomes fictícios.

Os locais previstos são `${XDG_CONFIG_HOME:-~/.config}/goodcodex` para preferências e overrides e `${XDG_DATA_HOME:-~/.local/share}/goodcodex` para registro e manifestos. A implementação da persistência virá nas etapas seguintes. Nenhuma raiz pessoal é constante do código.

## Defaults provisórios

Enquanto o usuário não escolher outra opção: `balanced` para recomendações; CLI como primeira interface; configuração local do projeto antes de perfis globais; delegação apenas quando pedida ou prevista por instrução aplicável, com sugestão inicial de até dois subagentes. Projetos em foco são definidos pelo uso real, sem lista fixa. O modo não muda permissões. A configuração global existente continua intacta até uma instalação explícita.

## Compatibilidade do Codex

Os exemplos em `tests/fixtures/goodcodex/native/` mostram um perfil e um agente sem informações de projeto. O formato de perfil em arquivo separado vale no Codex 0.134.0 ou superior conforme a [documentação oficial de perfis](https://learn.chatgpt.com/docs/config-file/config-advanced#profiles). O formato de agente segue a [documentação oficial de subagentes](https://learn.chatgpt.com/docs/agent-configuration/subagents). A compatibilidade local foi conferida com `codex-cli 0.157.1`: `codex --profile balanced debug prompt-input` aceitou o perfil em um `CODEX_HOME` temporário, e `codex doctor --json` carregou o agente sem aviso; controles com TOML inválido foram rejeitados ou sinalizados. O diagnóstico geral do `doctor` pode falhar nesse ambiente descartável por ausência de autenticação; não houve chamada a modelo. Outras versões e o comportamento do app ainda exigem diagnóstico nas próximas etapas. A CLI do goodcodex não depende do Codex para mostrar ajuda.

Comandos `scan`, `projects`, `inspect`, `doctor`, `plan`, `apply`, `status`, `update`, `rollback`, `recommend`, `explain` e `run` pertencem às etapas futuras e não são anunciados pela ajuda atual.
