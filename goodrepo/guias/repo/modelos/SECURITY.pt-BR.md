<!--
  Modelo do goodrepo (.harness/repo/modelos). Regras: .harness/repo/seguranca.md.
  Troque todo {{...}}, mantenha o escopo honesto, apague estes comentários. Precisa do
  "Private vulnerability reporting" ligado em Settings > Advanced Security.
-->

# Segurança

## Como reportar uma vulnerabilidade

**Não abra issue pública.** Uma issue fica visível para todo mundo antes da correção sair, e
{{a instância pública atende pessoas reais}}.

- **De preferência:** pelo próprio GitHub, aba **Security** do repositório → **Report a
  vulnerability**. Só você e o mantenedor veem o relato.
- **Ou por e-mail:** dionatha.work@gmail.com, com `[{{PROJETO}} segurança]` no assunto.

Ajuda muito incluir:

- o que dá para fazer com a falha ({{ler dado de outra pessoa, agir sem permissão, derrubar o
  serviço}});
- os passos para reproduzir, ou uma prova de conceito mínima (um `curl` vale mais que um relatório
  de scanner);
- a versão ou o commit em que você testou.

Teste numa instância sua, local ou hospedada, não em {{DOMINIO}}.

## O que esperar

- Resposta inicial em até **7 dias**.
- Se a falha for confirmada, a correção sai na versão seguinte e o relato vira um advisory público
  depois do deploy, com crédito para quem reportou (se você quiser).

Este é um projeto mantido por uma pessoa só, no tempo livre. Os prazos são um compromisso de
boa-fé, não um SLA.

## Escopo

Entram:

- {{qualquer coisa que deixe alguém ler ou mudar dado que não é seu}}
- {{contornar login, sessão, CSRF, CORS ou permissão}}
- {{segredo alcançável pelo app, pelo repo ou por log de workflow}}

Não entram:

- negação de serviço ou teste de carga contra a instância pública;
- engenharia social, ou acesso por credencial vazada do mantenedor;
- falha em dependência já corrigida upstream e só aguardando atualização;
- achado de scanner automático sem impacto demonstrado.

## Limites conhecidos

<!-- O que já é sabido e documentado, para não virar relato. Apague se não houver. -->

- **{{Limite.}}** {{Por que é aceito.}}

## Versões com suporte

Só a versão mais recente e a `main` recebem correção de segurança.
