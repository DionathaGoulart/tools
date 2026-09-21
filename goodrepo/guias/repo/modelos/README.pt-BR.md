<!--
  Modelo do goodrepo (.harness/repo/modelos). Regras: .harness/repo/readme.md.
  Troque todo {{...}}, apague as seções que não se aplicam, apague estes comentários.
  Antes do commit: grep -n '{{' README.md
-->

# {{PROJETO}}

{{Um ou dois parágrafos: o que é, com o que é feito, onde roda e quanto custa.}}

> **English:** {{o que é, em uma ou duas frases}}.

No ar em **[{{DOMINIO}}](https://{{DOMINIO}})**.

> **Status: v{{VERSAO}}.** {{O que funciona, e a ressalva que quem chega precisa saber antes de
> confiar.}} Veja o [SECURITY.md](SECURITY.md) e o [CHANGELOG.md](CHANGELOG.md).

<!-- App com interface: um print ou GIF aqui. -->

## O que faz

- {{O que a pessoa ganha, depois como.}}
  - **{{Limite.}}** {{O que custa ou o que não faz.}}

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | {{...}} |
| Backend | {{...}} |
| Banco | {{...}} |

## Como é por dentro

```text
{{diagrama ASCII}}
```

O detalhe está em [docs/arquitetura.md](docs/arquitetura.md).

## Estrutura

```text
{{pasta}}/     {{o que mora ali}}
docs/          Guias de arquitetura, desenvolvimento e deploy
```

## Rodando localmente

Requisitos: {{Node.js 24 ou mais novo}}.

```bash
{{comandos, do clone ao app rodando, com comentários alinhados}}
```

Abra {{http://localhost:5173}} e entre como `alice` / `{{senha}}`.

## Scripts

| Script | Para quê |
|---|---|
| `{{npm run dev}}` | {{...}} |

## Testes

{{Como rodar os testes e o que cada suíte cobre.}}

## Documentação

| Guia | Para quê |
|---|---|
| [docs/primeiros-passos.md](docs/primeiros-passos.md) | Subir o projeto do zero |
| [docs/arquitetura.md](docs/arquitetura.md) | Onde cada coisa mora e por quê |
| [docs/deploy.md](docs/deploy.md) | Produção, e o que um fork precisa trocar |

## Deploy

{{Um parágrafo: onde roda e como vai ao ar.}} Veja [docs/deploy.md](docs/deploy.md).

## Contribuindo

Issues e PRs são bem-vindos; veja o [CONTRIBUTING.md](CONTRIBUTING.md).

## Segurança

Falha de segurança se reporta em privado; veja o [SECURITY.md](SECURITY.md).

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
