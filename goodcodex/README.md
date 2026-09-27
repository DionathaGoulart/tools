# goodcodex

Ferramenta local para descobrir projetos e registrar evidências para o Codex. Requer Python 3.11+. Execute diretamente do checkout: `./goodcodex/goodcodex help`. A instalação na família good fica para a etapa 5.

## Comandos disponíveis

```sh
./goodcodex/goodcodex scan --root /caminho/dos/projetos --realm work
./goodcodex/goodcodex projects
./goodcodex/goodcodex inspect /caminho/do/projeto
./goodcodex/goodcodex scan --json
./goodcodex/goodcodex context /caminho/do/projeto/apps/api --json
./goodcodex/goodcodex doctor /caminho/do/projeto --json
./goodcodex/goodcodex doctor
```

`--json` funciona antes ou depois do subcomando. `scan` aceita vários `--root`. Se omitidos, usa `roots` de `${XDG_CONFIG_HOME:-~/.config}/goodcodex/preferences.json`; sem preferências, examina o diretório atual. `projects`, `inspect`, `context` e `doctor` leem o último registro. `inspect` e `context` aceitam caminho dentro de um checkout ou ID. A saída informa stack, branch, comandos declarados, fontes de contexto e avisos. **Comandos são apenas identificados, nunca executados.** Não há instalação de configurações Codex nesta etapa.

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

`plan`, `apply`, `status`, `update`, `rollback`, `recommend`, `explain` e `run` pertencem às etapas seguintes.
