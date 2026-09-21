# Escrita

Regras de escrita para todo Markdown dos repos: README, `docs/`, `SECURITY.md`, `CHANGELOG.md`,
`.harness/`. É a base dos outros guias do goodrepo (`padrao-readme.md`, `git.md`, `changelog.md`,
`seguranca.md`): eles partem daqui e não repetem estas regras.

## Idioma

| O quê | Idioma |
|---|---|
| Código, identificadores, commits | inglês, sempre |
| Interface (UI, mensagens do bot, saída de CLI) | pt-BR |
| `.harness/` (PRD, arquitetura, plano, styleguide) | pt-BR |
| README e `docs/` | o idioma do público (abaixo) |

O README segue quem vai ler:

- **Inglês:** projeto vitrine ou técnico que outro dev de fora vai clonar ou consumir (API pública,
  app open source, lib). Exemplos: GoodChat, Helldivers-api.
- **pt-BR:** projeto para usuário final brasileiro ou de uso pessoal. Exemplos: Goodbot, Macro
  Helldivers 2, tools.

Logo depois da abertura, uma linha-ponte para quem fala o outro idioma:

- README em pt-BR: `> **English:** <o que é, em uma ou duas frases>.`
- README em inglês de produto com UI em pt-BR: `The interface is in Brazilian Portuguese; code and
  docs are in English.`

Um arquivo, um idioma. Fora a linha-ponte, não misture.

## Tom

- **Seco e preciso.** O que faz, como faz, onde para. Sem adjetivo de marketing ("poderoso",
  "incrível", "rápido como um raio").
- **Honesto sobre limites.** O que não faz, quanto custa, o que quebra. Quando o limite importa,
  em negrito: "**Perdeu a senha, perdeu o histórico.**"
- **Explica o porquê** quando a regra não é óbvia. Regra sem motivo vira regra ignorada.
- **Primeira pessoa só em projeto pessoal** (tools). Projeto público fala do projeto, não de mim.
- **Nada de "simplesmente", "basta", "é fácil".** Se fosse, não precisava de documentação.

## Pontuação

- **Sem travessão (—).** Use vírgula, dois-pontos, parênteses ou ponto. Os repos mais novos já
  não usam, e os antigos estão sendo limpos.
- Intervalo numérico com "a": "fases 3 a 18", não "3–18".
- Aspas retas (`"`), não curvas.
- Datas em ISO: `2026-09-21`.

## Formatação

- **Quebra em 100 colunas**, o mesmo limite do Prettier, Biome e rustfmt dos repos. Tabela e URL
  longa podem passar.
- **Um H1 só**, o nome do projeto. H2 em frase curta ("Rodando localmente"), sem emoji.
- **Numere seções** (`## 1. Idioma`) só em documento citado por número (§3): PRD, CONTRIBUTING.
- **Bloco de código sempre com linguagem:** `bash` para shell (nunca `sh`), `json`, `ts`, `rust`.
  Árvore de pastas e diagrama ASCII vão em `text`.
- **Comentários de shell alinhados** na mesma coluna:

  ```bash
  npm install
  npm run db:migrate    # aplica as migrations locais
  npm run dev           # porta 8000
  ```

- **Tabela compacta** (`|---|`). Se o repo roda Prettier em Markdown, deixe ele alinhar.
- **Negrito** marca o termo que o leitor procura ou o limite que ele precisa ver, não ênfase solta.
- **Sem emoji** em título e texto corrido. Emoji só quando é o conteúdo (um sticker, um ícone).
- **Links relativos** para arquivos do repo: `[deployment](docs/deployment.md)`.
- **Bullet com lead em negrito** para lista de regras ou propriedades:
  `- **Sem recuperação.** Perdeu a senha, perdeu o histórico.`

## Nomes

- **Família Good\*:** produto em PascalCase (GoodChat, GoodMusic, GoodEconomy), CLI em minúsculo
  com prefixo (`goodpomo`, `goodharness`).
- **Um nome por projeto:** pasta local = repo no GitHub = H1 do README = nome no LICENSE. Divergir
  confunde quem chega (hoje: `CoBot`/`GoodBot`/`Goodbot`, `helldivers2-api`/`Helldivers-api`).
- **Autor:** "Dionatha Goulart" no texto. O handle `DionathaGoulart` só em URL.
- **Domínio:** `<projeto>.dionatha.com.br`.
- **Contas de exemplo:** `alice` e `bob`. Nunca nome real.

## O que não vai para o repo público

- Caminho local (`~/Desktop/...`), nome de pasta da sua máquina.
- Instrução escrita para agente de IA ("o agente deve ler..."), narração de sessão, handoff.
- Log de desenvolvimento (`plan.md` com fases e handoffs): fica fora da árvore ou no
  `.git/info/exclude`. O histórico do git guarda.
- Senha, token, chave privada, `.env`. Só `.env.example`, comentado.
