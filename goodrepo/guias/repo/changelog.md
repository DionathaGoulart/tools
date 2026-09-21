# CHANGELOG.md

Como manter o `CHANGELOG.md` de um repo nosso. Modelos:
[`modelos/CHANGELOG.en.md`](modelos/CHANGELOG.en.md) e
[`modelos/CHANGELOG.pt-BR.md`](modelos/CHANGELOG.pt-BR.md), no idioma do README
([escrita](escrita.md#idioma)). O fluxo de lançar uma versão está em [git.md](git.md).

## Formato

[Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) com [SemVer](https://semver.org/).

- **O mais novo em cima.** Primeiro `## [Unreleased]` (`## [Não lançado]`), sempre presente,
  mesmo vazio.
- **Uma seção por versão:** `## [X.Y.Z] - AAAA-MM-DD`.
- **Links no fim** do arquivo, um por versão, para a tag e para o compare do Unreleased.

Dentro de uma versão, só as seções que têm item, nesta ordem:

| Inglês | pt-BR | O quê |
|---|---|---|
| Breaking | Quebra | O que obriga quem usa ou hospeda a mudar algo. Sempre primeiro |
| Added | Adicionado | Coisa nova |
| Changed | Alterado | Comportamento que mudou |
| Fixed | Corrigido | Bug corrigido |
| Removed | Removido | Coisa que saiu |
| Security | Segurança | Correção de segurança |

Primeira versão pública de um projeto grande pode agrupar por área (Messaging, Encryption,
Accounts...) em vez de Added, porque tudo é novo.

## Como escrever um item

- **Para quem usa, não para quem programa.** "O alerta mostrava `v0.0.0`", não "fix VERSION
  constant".
- **Sintoma e causa** num item de correção: o que a pessoa via, e o que mudou.
- **Uma linha por mudança**, duas quando precisa do porquê.
- **Breaking diz o que fazer:** "Rode `npm run db:migrate` antes do deploy", "A variável `X` virou
  `Y`".
- **Sem hash de commit, sem nome de PR.** O changelog é a versão legível do `git log`, não uma
  cópia.
- Dependência atualizada só entra se muda algo para quem usa, ou em um item só no fim.

## Quando escrever

**No mesmo commit da mudança**, embaixo de Unreleased. Reconstituir o changelog na hora do release
esquece metade. No release, Unreleased vira a versão nova ([git.md](git.md#lançando-uma-versão)).

## Referências

- Goodbot (`CHANGELOG.md`, pt-BR): itens com sintoma e causa, bem escritos.
- GoodChat (`CHANGELOG.md`): primeira versão agrupada por área.
