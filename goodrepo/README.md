# goodrepo

Padroniza um repo com o jeito da família good. Dentro de um projeto, `goodrepo` abre um menu com
os guias (README, licença, escrita, git e versões, CHANGELOG, SECURITY, checklist de publicação,
styleguide visual e de CLI); os marcados vão para o `.harness/` do projeto, onde você, ou um agente
de IA, lê e aplica.

Os guias não geram o README nem a licença sozinhos: eles dizem **como** cada coisa tem que ficar, e
trazem os modelos para copiar. Quem aplica é quem lê.

## Instalação (uma vez)

```bash
# do diretório do repo tools
bash goodrepo/setup.sh
```

Ou pelo instalador da raiz (`bash setup.sh`), marcando `goodrepo`.

## Uso

```bash
cd ~/projetos/meu-app
goodrepo                   # menu: marque os guias e confirme em [INSTALAR]
```

```text
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ● ● ●  root@goodrepo: ~/projetos/meu-app                         9 GUIAS ┃▒
┠──────────────────────────────────────────────────────────────────────────┨▒
┃ ► [x]  1. readme      padrão de README + modelos en e pt-BR              ┃▒
┃   [x]  2. styleguide  visual retro: base + skins retro e terminal        ┃▒
┃   [ ]  3. licenca     qual licença usar + textos CC BY-NC-SA 4.0 e MIT   ┃▒
┃   [✓]  4. escrita     escrita: idioma, tom, pontuação, nomes             ┃▒
┃   ...                                                                    ┃▒
┃   [  INSTALAR  ]                                                         ┃▒
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛▒
 ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
```

Teclas: `↑↓` (ou `j`/`k`) move, espaço ou `Enter` marca, `1-9` marca direto, `a` todos, `n`
nenhum, `q` sai. `[✓]` é guia já instalado no projeto.

Sem menu:

```bash
goodrepo add readme licenca    # instala (dependências vêm junto)
goodrepo list                  # guias disponíveis, com [✓] no que já está aqui
goodrepo status                # instalado x fonte
goodrepo update                # traz a versão nova dos guias instalados
goodrepo rm seguranca          # remove um guia
goodrepo -C ~/outro-projeto    # qualquer comando em outro projeto
goodrepo help
```

O projeto alvo é a raiz do git do diretório atual (ou o próprio diretório, fora de um repo). Na
sua home ele se recusa a instalar: quase certamente é engano.

## Os guias

| Guia | Vai para | O que padroniza | Traz junto |
|---|---|---|---|
| `readme` | `.harness/repo/padrao-readme.md` + `modelos/README.*.md` | o `README.md` | escrita, licenca |
| `styleguide` | `.harness/styleguide.md` + `styleguides/` | a interface: paletas, tipo, componentes | |
| `licenca` | `.harness/repo/licenca.md` + `licencas/` | `LICENSE` e o campo `license` | readme |
| `escrita` | `.harness/repo/escrita.md` | idioma, tom, pontuação, nomes | |
| `git` | `.harness/repo/git.md` | commits, identidade, versões e releases | changelog |
| `changelog` | `.harness/repo/changelog.md` + `modelos/CHANGELOG.*.md` | o `CHANGELOG.md` | escrita, git |
| `seguranca` | `.harness/repo/seguranca.md` + `modelos/SECURITY.*.md` | o `SECURITY.md` | escrita |
| `publicar` | `.harness/repo/publicar.md` + `modelos/.editorconfig` | o checklist antes de abrir o repo | todos os de repo |
| `cli` | `.harness/styleguide-cli.md` | a saída de terminal de uma CLI | styleguide |

**Dependências** existem porque um guia cita outro por link: vêm junto para nenhum link ficar
quebrado. O `goodrepo` avisa quais vieram.

Toda instalação (re)gera o **índice** `.harness/repo/README.md`: a ordem de leitura, a tabela do
que está instalado e a frase pronta para pedir a um agente ("Leia o .harness/repo/README.md e
padronize este repo seguindo os guias instalados.").

## Arquivos que já existem

O `goodrepo` nunca passa por cima de um arquivo que não é dele (um `styleguide.md` que o projeto
já tinha) nem de um guia que você editou no projeto:

- **no menu**, ele lista os conflitos e pergunta: sobrescrever com backup `.bak`, pular esses, ou
  cancelar;
- **no `add` e no `update`**, ele pula e avisa; `-f` sobrescreve, guardando o anterior em `.bak`.

## Status e update

O manifesto `.harness/repo/.goodrepo` guarda o hash de cada arquivo instalado. Com ele, o `status`
separa quatro situações:

| Estado | Quer dizer | `update` faz |
|---|---|---|
| `OK` | igual à fonte | nada |
| `DESATUALIZADO` | a fonte mudou, o arquivo daqui não | traz a versão nova |
| `EDITADO` | alguém mudou o arquivo aqui | pula (`-f` sobrescreve com `.bak`) |
| `FALTANDO` | o arquivo sumiu | reinstala |

Melhorou um guia? Edite em `goodrepo/guias/`, commite no tools e rode `goodrepo update` nos
projetos.

## Onde os guias moram

[`guias/`](guias) tem o mesmo layout que ganha no `.harness/` do projeto, então os links entre os
guias funcionam aqui e lá:

```text
guias/
  styleguide.md            ← base visual (paletas, tokens, componentes)
  styleguides/             ← skins retro e terminal
  styleguide-cli.md        ← saída de terminal
  repo/
    escrita.md  padrao-readme.md  licenca.md  git.md
    changelog.md  seguranca.md  publicar.md
    licencas/              ← CC-BY-NC-SA-4.0.txt, MIT.txt (com {{PROJETO}}, {{ANO}}, {{REPO_URL}})
    modelos/               ← README, SECURITY e CHANGELOG em en e pt-BR, .editorconfig
```

Guia novo: crie o arquivo em `guias/`, acrescente uma entrada nos arrays `IDS`, `DESCS`, `ARQS`,
`DEPS` e `ALVOS` do script, e rode `bash tests/test_goodrepo.sh` (ele confere que todo arquivo do
catálogo existe e que os links entre guias instalados resolvem).

## goodrepo e goodharness

O [`goodharness`](../goodcheats) guarda **presets** de `.harness/` copiados de um projeto para
outro (o styleguide de um app servindo de base para o próximo). O `goodrepo` instala os **guias
padrão** da família, que moram versionados aqui. Dá para usar os dois no mesmo projeto.

## Tema

Segue o tema retrô da família (`GOOD_TEMA` ou `RETRO_TEMA`, padrão `vault-gold`). `NO_COLOR=1` ou
saída redirecionada viram texto puro; sem terminal interativo, `goodrepo` mostra a ajuda em vez
do menu.
