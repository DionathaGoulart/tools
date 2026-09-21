# Deixar um repo público

Checklist para abrir um repo privado. Siga na ordem: a visibilidade muda por último, quando não
sobrou nada para esconder. Foi o caminho do GoodChat em 2026-09-21.

## 1. Segredos

- [ ] Histórico inteiro, não só a árvore atual (arquivo apagado continua no histórico):

  ```bash
  gitleaks git -v .     # todos os commits
  gitleaks dir -v .     # a árvore atual, incluindo o que não foi commitado
  ```

- [ ] Arquivos que já existiram e sumiram, e o que tinha neles:

  ```bash
  git log --all --pretty=format: --name-only --diff-filter=D | sort -u
  ```

- [ ] `.env`, `.dev.vars` e afins nunca commitados (`git log --all -- '**/.env'`).
- [ ] Autores do histórico: `git log --all --format='%an <%ae>' | sort -u`.

Achou segredo no histórico? **Revogue e gere outro primeiro**, depois pense em reescrever o
histórico. Segredo que já saiu não volta.

## 2. O que fica exposto com o código aberto

- [ ] Senha de teste que o README ensina (`alice-...`, `good-...`) **não** é a de nenhuma conta de
  produção.
- [ ] Todo valor com fallback no código (salt, chave de HMAC, segredo "padrão") está definido em
  produção. Com o código público, o fallback é público.

  ```bash
  npx wrangler secret list      # Cloudflare Workers
  ```

- [ ] Rota de admin e endpoint sem autenticação conferidos: o que alguém consegue lendo o código?

## 3. Valores que são só seus

Domínio, ID de banco, bucket, chave pública VAPID, e-mail de contato. Não precisam sumir, mas quem
fizer fork precisa saber que tem que trocar:

- [ ] Uma seção **Make it yours** / **Para rodar o seu** no guia de deploy, com cada valor e onde
  ele mora.
- [ ] Nada fixo em workflow que aponte para a sua instância (a CI de um fork testaria o seu site).
  Leia do config do projeto.

## 4. Documentação

- [ ] README no [padrão](padrao-readme.md).
- [ ] `docs/` batem com o código: número, limite, variável, nome de script. Doc velho que
  contradiz o código é pior que doc nenhum.
- [ ] Fora da árvore: log de desenvolvimento (`plan.md`), caminho local, nome real em exemplo,
  instrução para agente de IA ([escrita](escrita.md#o-que-não-vai-para-o-repo-público)).
- [ ] Link quebrado: nenhum `](arquivo)` apontando para arquivo apagado.

## 5. Arquivos padrão

- [ ] `LICENSE` ([qual](licenca.md)) e o campo `license` do `package.json` / `Cargo.toml`.
- [ ] `SECURITY.md` ([como](seguranca.md)): como reportar em privado.
- [ ] `CHANGELOG.md` ([como](changelog.md)) com a primeira versão.
- [ ] `.editorconfig` ([modelo](modelos/.editorconfig)): copie para a raiz do projeto.
- [ ] `.env.example` que funciona com `cp` para o dev local.

## 6. Limpeza

- [ ] Sobra de template (logo do Vite, `hero.png`, ícones que ninguém importa).
- [ ] `console.log` de debug, `debugger`, código comentado, TODO esquecido.
- [ ] Typecheck, lint, build e testes verdes.

## 7. Versão

- [ ] Decida a versão ([0.x ou 1.0](git.md#0x-ou-10)), suba nos manifests, commit
  `chore(release): X.Y.Z`, push e tag `vX.Y.Z`.
- [ ] CI verde no commit da tag.

## 8. GitHub

No repo, engrenagem ao lado de **About**:

- [ ] **Description:** uma frase, até 350 caracteres, no idioma do README. O que é e com o quê.
- [ ] **Website:** a instância no ar, se houver.
- [ ] **Topics:** 8 a 20, minúsculas com hífen (`cloudflare-workers`, `self-hosted`,
  `disappearing-messages`). Linguagem, plataforma, domínio do problema.
- [ ] Desmarque **Packages** e **Deployments** se estão vazios.

Depois:

- [ ] **Releases → Draft a new release** na tag, com o trecho do CHANGELOG.
- [ ] **Settings → Change visibility → Public.** Pede o código do 2FA. Lembre: os logs do
  GitHub Actions também ficam públicos.
- [ ] **Settings → Advanced Security** (algumas só aparecem com o repo público):
  - [ ] Private vulnerability reporting (o `SECURITY.md` aponta para cá)
  - [ ] Dependency graph
  - [ ] Dependabot alerts
  - [ ] Secret Protection e Push protection

Dependabot abrindo PR sozinho e CodeQL são opcionais. Em repo que faz deploy a cada push na
`main`, cada PR aceito vai ao ar.

## 9. Conferir

- [ ] Abra o repo numa janela anônima: carrega, README renderiza, links funcionam.
- [ ] `curl -s https://api.github.com/repos/DionathaGoulart/<repo>` mostra `"visibility":
  "public"`, a descrição e os topics.
