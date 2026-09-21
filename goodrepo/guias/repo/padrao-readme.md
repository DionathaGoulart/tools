# Padrão de README

Como um README nosso é montado. Vale junto com as [regras de escrita](escrita.md). Os modelos
prontos para copiar estão em [`modelos/README.en.md`](modelos/README.en.md) e
[`modelos/README.pt-BR.md`](modelos/README.pt-BR.md).

A régua é o README do GoodChat, do Goodbot e da Helldivers-api: quem chega entende o que é em duas
frases, roda em um bloco de comandos e acha o resto por tabela.

## Esqueleto

Nesta ordem. Seção que não se aplica sai inteira; não deixe título vazio.

| # | Seção (en / pt-BR) | Obrigatória | O que vai |
|---|---|---|---|
| 1 | `# Nome` | sim | Só o nome do projeto, igual ao do repo |
| 2 | Badges | não | No máximo CI e versão, logo abaixo do H1 |
| 3 | Abertura | sim | Um ou dois parágrafos: o que é, com o quê, onde roda |
| 4 | Links e ponte | se houver | Link ao vivo em negrito, linha-ponte de idioma |
| 5 | Status | se < 1.0 | Blockquote `> **Status: vX.Y.Z.** ...` |
| 6 | Imagem | app com UI | Um print ou GIF do produto |
| 7 | Features / O que faz | sim | Lista do que o produto faz |
| 8 | Tech stack / Stack | sim | Tabela `Camada \| Tecnologia` |
| 9 | Architecture / Como é por dentro | se não trivial | Diagrama em `text` + link para `docs/` |
| 10 | Repository layout / Estrutura | monorepo | Árvore em `text`, uma linha por pasta |
| 11 | Quickstart / Rodando localmente | sim | Linha de requisitos + um bloco `bash` |
| 12 | Scripts | se houver | Tabela `Script \| Para quê` |
| 13 | Testing / Testes | se houver | Como rodar, e o que cada suíte cobre |
| 14 | Documentation / Documentação | se houver `docs/` | Tabela `Documento \| Conteúdo` |
| 15 | Deployment / Deploy | se tem deploy | Resumo + link para o guia |
| 16 | Contributing / Contribuindo | repo público | Uma linha para o `CONTRIBUTING.md`, ou o fluxo curto |
| 17 | Security / Segurança | repo público | Uma linha para o `SECURITY.md` |
| 18 | License / Licença | sim | Resumo da licença (modelos abaixo) |

## Seção por seção

### 1 a 5: o topo

O topo responde três perguntas antes da primeira rolagem: o que é, onde vejo funcionando, dá para
confiar.

```markdown
# GoodChat

Private real-time 1:1 chat with a retro terminal look. Built on Cloudflare Workers, Durable
Objects, D1 and Backblaze B2, all within free tiers.

Live instance: **[goodchat.dionatha.com.br](https://goodchat.dionatha.com.br)**. The interface is
in Brazilian Portuguese; code and docs are in English.

> **Status: v0.9.0.** In daily use and feature-complete for its scope, but the encryption has not
> been audited. See [SECURITY.md](SECURITY.md) and [CHANGELOG.md](CHANGELOG.md).
```

- **Abertura** diz o custo quando ele é um argumento ("all within free tiers", "cabe no plano
  gratuito").
- **Sem tagline de marketing.** A primeira frase é a definição do produto.
- **Badge** só de coisa que muda sozinha (CI, versão, dado). Badge de tecnologia não informa nada
  que a tabela de stack não diga.
- **Status** some quando o projeto chega na 1.0 e não tem ressalva.

### 7: features

Lista com bullet. Cada item começa pelo que o usuário ganha, depois como. Limite importante vira
sub-bullet com lead em negrito, logo abaixo da feature que ele limita.

### 11: rodando localmente

Uma linha de requisitos e **um** bloco `bash` que vai do clone ao app rodando. Mais de um processo
vira comentário de terminal dentro do mesmo bloco:

```bash
# Terminal 1: backend (porta 8000)
cd worker
npm install
cp .env.example .dev.vars   # config local, sem conta externa
npm run dev

# Terminal 2: frontend (porta 5173)
cd app
npm install
npm run dev
```

Termine dizendo onde abrir e com qual login de teste (`alice` / `bob`).

### 14: documentação

Tabela com link relativo e uma frase de conteúdo. `docs/` em kebab-case, no idioma do README
(`docs/deployment.md` em inglês, `docs/primeiros-passos.md` em pt-BR).

### 18: licença

Resumo em bullets com lead em negrito, e o arquivo `LICENSE` como fonte. Modelos:

**CC BY-NC-SA 4.0, em inglês:**

```markdown
## License

Made by [Dionatha Goulart](https://github.com/DionathaGoulart).
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/), see [LICENSE](LICENSE).
In short:

- **Free for non-commercial use.** Clone it, run it, change it and share it. No need to ask.
- **No commercial use.** For commercial terms, write to dionatha.work@gmail.com.
- **Credit the author.** A public fork's README says "Based on {{PROJETO}} by Dionatha Goulart"
  with a link to this repository; a running instance shows "Built with {{PROJETO}} by Dionatha
  Goulart" somewhere visible.
- **Share alike.** Modified versions you share keep this license.
```

**CC BY-NC-SA 4.0, em pt-BR:**

```markdown
## Licença

Feito por [Dionatha Goulart](https://github.com/DionathaGoulart).
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.pt-br), veja o
[LICENSE](LICENSE). Em resumo:

- **Livre para uso não comercial.** Clone, rode, mude e compartilhe. Não precisa pedir.
- **Sem uso comercial.** Para usar comercialmente, fale com dionatha.work@gmail.com.
- **Dê o crédito.** Um fork público diz "Baseado no {{PROJETO}} de Dionatha Goulart" no README,
  com link para este repositório; uma instância no ar mostra "Feito com {{PROJETO}} por Dionatha
  Goulart" em algum lugar visível.
- **Compartilhe igual.** Versão modificada que você compartilha segue com esta licença.
```

**MIT:**

```markdown
## License

[MIT](LICENSE) © 2026 Dionatha Goulart.
```

Qual licença usar em cada projeto: [licenca.md](licenca.md).

## Não faça

- Título com emoji, seção vazia, "TODO" no README.
- Instalação espalhada em cinco blocos com texto entre eles.
- Lista de tecnologias em badge.
- "Feito com ❤️". O crédito já está na licença.
- Copiar o README de outro projeto sem trocar nome, domínio e link. Procure `{{` antes do commit.
