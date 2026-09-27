# Avaliação da primeira versão

## Estado da evidência

A suíte local e o smoke sintético verificam o funcionamento da ferramenta, sem inferência paga. Não há benchmark real de modelos nesta versão. Tempo de solução, qualidade comparada e uso de tokens de sessões reais continuam **não medidos**. Não inferir custo de assinatura a partir de tokens ou preço da API.

## Casos preparados

Cada caso abaixo exige um snapshot isolado, um pedido idêntico para as duas variantes e critérios definidos antes da execução. Os IDs são genéricos e não contêm nomes de clientes. Os patches concretos devem ser escolhidos e autorizados antes dos pilotos. Nenhum caso abaixo foi executado como tarefa de modelo.

| ID | Área | Tarefa no snapshot | Critérios de aceite |
|---|---|---|---|
| `cli-paths-01` | CLI | Corrigir um caminho com espaços e acentos | Fluxo funciona; teste de regressão passa; sem escrita fora do alvo |
| `cli-install-02` | CLI | Corrigir atualização de instalação já existente | Segunda aplicação é idempotente; rollback conserva edição humana |
| `web-state-03` | Web | Ajustar estado vazio e erro em uma lista | Estados visíveis e acessíveis; contrato de dados preservado; revisão visual humana |
| `web-route-04` | Web | Corrigir navegação e fronteira server/client | Rota funciona; build/testes relevantes passam; revisão visual humana |
| `mobile-offline-05` | Mobile | Corrigir estado offline de uma tela | Sem perda de dados; navegação e estados verificados em simulador; revisão humana |
| `api-auth-06` | API | Corrigir autorização de um endpoint | Casos permitido/negado cobertos; sem exposição entre usuários |
| `data-migrate-07` | Banco | Ajustar uma migração e consulta relacionada | Migração reversível conforme projeto; constraints e query verificadas em base de teste |
| `edge-retry-08` | Edge | Corrigir retry e idempotência de uma operação | Repetição não duplica efeito; teste local cobre erro transitório |
| `investigate-09` | Investigação | Localizar causa de falha entre duas camadas | Hipótese sustentada por arquivos/logs; correção mínima demonstrada |
| `review-docs-10` | Revisão e docs | Revisar diff e atualizar instruções de uso | Achados reproduzíveis; texto corresponde ao comportamento; sem alegar validação não feita |

## Protocolo dos pilotos

1. Escolher de 8 a 12 casos representativos em projetos autorizados. Salvar snapshot, pedido, critérios e comandos de verificação fora do repositório público. Para UI/arquitetura, definir responsável por revisão humana. Dados privados ficam no ambiente do projeto.
2. Executar cada caso isoladamente e sem subagentes em duas variantes: baseline Astra/medium e política proposta do goodcodex. Alternar a ordem entre casos. Usar o mesmo snapshot, orçamento, ferramentas, tempo máximo e critérios. Registrar o modelo e esforço **efetivos** vistos na sessão, inclusive fallback ou recusa de acesso.
3. Cronometrar do início da sessão até a decisão de aceite, incluindo correções. Registrar tentativas, correções manuais, bugs encontrados, critérios atendidos e revisão humana. Usar contadores de tokens somente se retornados pelo runtime; caso contrário, deixar `null`/omitir.
4. Para cada execução, criar um JSON no formato `schemas/evaluation.schema.json` e chamar `goodcodex evaluate add arquivo.json`. Depois usar `goodcodex evaluate report --json`. O arquivo de entrada e os registros locais em XDG são privados. Registrar somente ID do caso e métricas; não incluir prompts, código, nomes de clientes ou credenciais.
5. Comparar apenas casos pareados. Revisar qualidade crítica caso a caso antes de olhar médias ou tempo. O relatório agrega observações, mas não declara vencedor. Variantes com modelo indisponível precisam ser anotadas fora do registro como execução não realizada, sem fabricar um resultado.
6. Só depois, em tarefas decomponíveis, repetir uma rodada com delegação para medir seu efeito separadamente. Não misturar esses resultados com a comparação inicial de modelos.

Exemplo sintético: `../tests/fixtures/goodcodex/evaluation.json`. `outcome=pass` requer todos os critérios atendidos; revisão humana pendente continua visível. `elapsedSeconds`, `inputTokens` e `outputTokens` são opcionais. O relatório usa `null` quando falta qualquer medição da soma do grupo e informa quantas execuções forneceram cada métrica. `comparisonStatus=paired_records_available` indica apenas que existem IDs nas duas variantes, não que a comparação seja justa ou conclusiva.

## Limitações e backlog pós-MVP

- Validar carregamento dos perfis e agentes no app/IDE, confiança de configuração de projeto e outras versões do CLI em sessões reais.
- Confirmar disponibilidade real de modelos por conta e superfície. A lista local `availableModels` é uma declaração, não descoberta remota.
- Executar pilotos autorizados antes de afirmar ganho de qualidade, tempo ou uso. Revisões visuais e arquiteturais exigem julgamento humano.
- A medição é manual: não captura automaticamente relógio, tokens ou resultado de `run`. O relatório soma registros e não avalia diferenças estatísticas nem impede duas execuções do mesmo caso/variante.
- Presets para Ruby, Dart sem Flutter, React Native sem Expo e pipelines de IA/mídia em Python continuam sem cobertura especializada automática.
- O scanner usa heurísticas e referências de contexto; não substitui revisão das regras do projeto ou diagnóstico de permissões de comandos descobertos.
