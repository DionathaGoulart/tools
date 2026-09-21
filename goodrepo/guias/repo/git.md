# Git, versões e releases

Como commitar, versionar e lançar em qualquer repo nosso.

## Identidade

Todo commit sai como:

```text
DionathaGoulart <dionatha.work@gmail.com>
```

Não confie na config global da máquina: cada repo leva a identidade local.

```bash
git config --local user.name "DionathaGoulart"
git config --local user.email "dionatha.work@gmail.com"
```

- **Nunca outro e-mail.** Commit com e-mail que não está ligado à conta do GitHub aparece sem
  avatar e sem perfil.
- **Sem trailer de IA.** Nada de `Co-Authored-By: Claude` nem autor/committer de IA.

## Commits

[Conventional Commits](https://www.conventionalcommits.org/), **inteiramente em inglês**, mesmo em
repo pt-BR.

```text
feat(bot): add /say to publish a message as the bot
fix(app): keep the thread's key fingerprints when a conversation resolves
docs: bring architecture, development and deployment up to date
chore(release): 0.9.0
```

- **Assunto:** imperativo, minúsculo, sem ponto final, até 72 caracteres. Lê como frase
  ("fix(stats): show seconds for plays under a minute").
- **Corpo:** quebrado em 72 colunas, responde **por quê**. O diff já diz o quê.
- **Um commit por tarefa lógica.** Refactor e feature em commits separados.
- **Escopo** é a parte do repo (`app`, `worker`, `bot`, `web`, `db`, `ci`, `infra`, `readme`).
  Cada repo lista os seus no `CONTRIBUTING.md`.
- **`!`** depois do tipo quando quebra compatibilidade: `feat(worker)!: require an encryption
  envelope`.

| Tipo | Quando |
|---|---|
| `feat` | coisa nova para quem usa |
| `fix` | correção de comportamento |
| `docs` | só documentação |
| `refactor` | muda código sem mudar comportamento |
| `perf` | mesmo comportamento, mais rápido ou mais leve |
| `test` | só teste |
| `style` | só formatação, sem mudar lógica |
| `build` | dependência, bundler, empacotamento |
| `ci` | workflow do GitHub Actions |
| `chore` | manutenção que não cabe acima, e o commit de release |

## Branch e deploy

- **`main` é a verdade.** Repo com workflow de deploy publica a cada push na `main`, então push
  na `main` é deploy. Não suba para a `main` o que não pode ir ao ar.
- Trabalho grande ou arriscado: branch `feat/<nome>` ou `fix/<nome>`, merge quando estiver verde.
- Workflows com nome minúsculo: `ci`, `deploy`, `release`.

## Versões

[SemVer](https://semver.org/lang/pt-BR/): `MAJOR.MINOR.PATCH`.

- **Patch:** correção.
- **Minor:** feature, tela, comando ou módulo novo.
- **Major:** quebra algo para quem usa (comando que some ou muda) ou para quem hospeda (variável
  de ambiente, formato de config, migration com passo manual, formato de dado ou protocolo).

### 0.x ou 1.0?

A versão é uma promessa para quem chega. **1.0 diz "está estável, pode confiar, não mudo as
regras do nada".** Fique em 0.x enquanto qualquer um destes for verdade:

- o formato de dado, protocolo ou config ainda muda de forma incompatível com frequência;
- algo sensível (criptografia, pagamento, autenticação) nunca foi revisado por alguém de fora;
- quem quer rodar uma cópia precisa editar código à mão.

Dentro do 0.x o número conta o quanto falta: **0.1** é esboço que roda, **0.9** é "funciona, está
no ar, está se firmando". Em 0.x, uma minor pode quebrar; diga no CHANGELOG, em **Breaking**.

Projeto novo começa em `0.1.0`. Nunca publique `0.0.0`.

### Onde a versão mora

Um lugar só é a fonte, e o resto acompanha: `package.json` (raiz), `Cargo.toml`, `pubspec.yaml`,
`pyproject.toml`. Se o app mostra a versão na tela ou no `/health`, um teste compara as duas.
Pacote interno de workspace fica em `0.0.0`.

## Lançando uma versão

1. No `CHANGELOG.md` ([como escrever](changelog.md)), mova o que está em **Unreleased** (**Não
   lançado**) para a versão nova, com a data.
2. Suba a versão na fonte (acima). Com npm: `npm version X.Y.Z --no-git-tag-version`.
3. Commit `chore(release): X.Y.Z`.
4. Tag anotada e push **só dela**:

   ```bash
   git tag -a vX.Y.Z -m "<Projeto> X.Y.Z"
   git push origin main
   git push origin vX.Y.Z     # nunca --tags
   ```

5. GitHub Release a partir da tag: título `vX.Y.Z`, corpo = o trecho do CHANGELOG.

Tag publicada não se move: quem já baixou aquela versão ficaria com outra coisa. Errou? Lance a
próxima patch. A exceção é a tag recém-publicada que ninguém usou ainda (minutos, zero fork, zero
download): aí dá para mover, com `git tag -f` e `git push --force origin vX.Y.Z`, e o GitHub
Release acompanha.
