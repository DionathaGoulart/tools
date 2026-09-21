<!--
  Template from goodrepo (.harness/repo/modelos). Rules: .harness/repo/readme.md.
  Replace every {{...}}, delete sections that do not apply, delete these comments.
  Check before committing: grep -n '{{' README.md
-->

# {{PROJETO}}

{{One or two paragraphs: what it is, what it is built with, where it runs and what it costs.}}

Live instance: **[{{DOMINIO}}](https://{{DOMINIO}})**. {{Bridge line if the UI is in pt-BR: The
interface is in Brazilian Portuguese; code and docs are in English.}}

> **Status: v{{VERSAO}}.** {{What works, and the one caveat a newcomer must know before relying on
> it.}} See [SECURITY.md](SECURITY.md) and [CHANGELOG.md](CHANGELOG.md).

<!-- App with a UI: one screenshot or GIF here. -->

## Features

- {{What the user gets, then how.}}
  - **{{Limit.}}** {{What it costs or does not do.}}

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | {{...}} |
| Backend | {{...}} |
| Database | {{...}} |

## Architecture

```text
{{ASCII diagram}}
```

Full details in [docs/architecture.md](docs/architecture.md).

## Repository layout

```text
{{folder}}/    {{what lives there}}
docs/          Architecture, development and deployment guides
```

## Quickstart

Requirements: {{Node.js 24 or newer}}.

```bash
{{commands, from clone to running app, with aligned comments}}
```

Open {{http://localhost:5173}} and sign in as `alice` / `{{password}}`.

## Scripts

| Script | Purpose |
|---|---|
| `{{npm run dev}}` | {{...}} |

## Testing

{{How to run the tests and what each suite covers.}}

## Documentation

| Document | Content |
|---|---|
| [docs/architecture.md](docs/architecture.md) | System design, data model, protocol |
| [docs/development.md](docs/development.md) | Local setup, workflows, conventions |
| [docs/deployment.md](docs/deployment.md) | Production deployment, and what a fork must change |

## Deployment

{{One paragraph: where it runs and how it ships.}} See [docs/deployment.md](docs/deployment.md).

## Contributing

Issues and PRs are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

Please report vulnerabilities privately; see [SECURITY.md](SECURITY.md).

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
