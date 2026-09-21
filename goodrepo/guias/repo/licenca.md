# Licenças

Qual licença cada projeto leva, e como aplicar.

| Licença | Quando | Exemplos |
|---|---|---|
| [CC BY-NC-SA 4.0](licencas/CC-BY-NC-SA-4.0.txt) | **Padrão.** App, serviço, API, dado, jogo, tudo que é produto | GoodChat, Helldivers-api |
| [MIT](licencas/MIT.txt) | Ferramenta ou lib que você quer ver usada em qualquer lugar, até em produto pago | tools, Goodbot |
| Nenhuma | Repo privado | GoodMusic, GoodEconomy |

Na dúvida, CC BY-NC-SA: uso pessoal e comunitário livre, uso comercial precisa pedir, crédito
obrigatório, e quem modificar e compartilhar mantém a mesma licença.

**Repo público precisa de licença.** Sem arquivo `LICENSE`, ninguém pode usar legalmente, nem para
uso pessoal.

**Não escreva licença própria.** Texto jurídico caseiro tem buraco que ninguém vê até precisar. O
Macro Helldivers 2 tem uma; o caminho é migrar para a CC BY-NC-SA, que diz o mesmo com texto que
já foi testado.

## Aplicando

1. Copie o arquivo de `licencas/` para a raiz do projeto com o nome `LICENSE` (sem extensão).
2. Troque os marcadores:

   | Marcador | Exemplo |
   |---|---|
   | `{{PROJETO}}` | `GoodChat` (o nome do H1 do README) |
   | `{{ANO}}` | `2026` (ano da primeira publicação) |
   | `{{REPO_URL}}` | `https://github.com/DionathaGoulart/GoodChat` |

3. Confira que não sobrou marcador: `grep -n '{{' LICENSE`.
4. Declare no manifesto:

   | Arquivo | CC BY-NC-SA | MIT |
   |---|---|---|
   | `package.json` | `"license": "CC-BY-NC-SA-4.0"` | `"license": "MIT"` |
   | `Cargo.toml` | `license = "CC-BY-NC-SA-4.0"` | `license = "MIT"` |
   | `pyproject.toml` | `license = "CC-BY-NC-SA-4.0"` | `license = "MIT"` |

5. Seção de licença no README: modelos em [padrao-readme.md](padrao-readme.md#18-licença).

## Na CC BY-NC-SA

- **Crédito a terceiros.** Se o projeto adapta material de outra fonte CC (como a Helldivers-api
  faz com a wiki), acrescente a fonte em `Credits`, com link e a atribuição sugerida. Imagem ou
  marca de terceiro (logo de jogo) vai em `Not covered`.
- **O texto que vale é o inglês.** O resumo do topo e o do README ajudam a ler; o legal code
  abaixo da linha `=====` é o que vincula. Não traduza nem edite essa parte.
- **O GitHub mostra "Other".** Ele não reconhece a CC BY-NC-SA (a API responde `NOASSERTION`). É
  esperado, não é erro.
- **Foi feita para obra, não para software.** Não fala de patente, por exemplo. Para projeto
  pessoal não faz diferença; se um dia virar produto com empresa atrás, reveja.

## Trocando a licença de um projeto que já existe

- Commit `chore: license under <licença>`, com o motivo no corpo.
- Entrada em **Changed** no CHANGELOG.
- A troca vale dali para frente. Quem já tinha baixado uma versão lançada continua com a licença
  daquela versão.
