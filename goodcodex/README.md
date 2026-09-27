# goodcodex

Ferramenta local para descobrir projetos e registrar evidências para o Codex. Requer Python 3.11+. Execute diretamente do checkout: `./goodcodex/goodcodex help`. A instalação na família good fica para a etapa 5.

## Comandos disponíveis

```sh
./goodcodex/goodcodex scan --root /caminho/dos/projetos --realm work
./goodcodex/goodcodex projects
./goodcodex/goodcodex inspect /caminho/do/projeto
./goodcodex/goodcodex scan --json
```

`--json` funciona antes ou depois do subcomando. `scan` aceita vários `--root`. Se omitidos, usa `roots` de `${XDG_CONFIG_HOME:-~/.config}/goodcodex/preferences.json`; sem preferências, examina o diretório atual. `projects` e `inspect` leem o último registro. `inspect` aceita caminho dentro de um checkout ou ID. A saída informa stack, branch, comandos declarados, fontes de contexto e avisos. **Comandos são apenas identificados, nunca executados.** Não há instalação de configurações Codex nesta etapa.

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

`doctor`, `plan`, `apply`, `status`, `update`, `rollback`, `recommend`, `explain` e `run` pertencem às etapas seguintes.
