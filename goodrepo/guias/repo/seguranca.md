# SECURITY.md

Como escrever o `SECURITY.md` de um repo nosso. Todo repo público tem um; projeto que lida com
conta, dado de outra pessoa ou criptografia tem um desde o primeiro dia. Modelos:
[`modelos/SECURITY.en.md`](modelos/SECURITY.en.md) e
[`modelos/SECURITY.pt-BR.md`](modelos/SECURITY.pt-BR.md), no idioma do README
([escrita](escrita.md#idioma)).

## Para que serve

Dizer a quem achou uma falha **como contar sem expor**, e o que esperar depois. Sem ele, a pessoa
abre issue pública e a falha fica visível antes da correção.

## Estrutura

Nesta ordem, com estes títulos:

1. **Como reportar** (`Reporting a vulnerability`): começa com "**Não abra issue pública.**" e o
   motivo concreto do projeto ("a instância pública atende servidores reais"). Dois canais: o
   relato privado do GitHub (preferido) e o e-mail `dionatha.work@gmail.com` com
   `[<Projeto> segurança]` no assunto. O que ajuda incluir: impacto, passos, versão.
2. **Onde testar:** na instância da própria pessoa, nunca na nossa em produção.
3. **O que esperar:** primeira resposta em até **7 dias**, correção na versão seguinte, advisory
   público depois do deploy, crédito se a pessoa quiser. Fecha com "projeto mantido por uma pessoa
   só, no tempo livre; prazo é compromisso de boa-fé, não SLA".
4. **Escopo:** listas "Entram" e "Não entram", específicas do projeto. Genérico ("qualquer bug de
   segurança") não ajuda ninguém.
5. **Limites conhecidos** (se houver): o que já é sabido e aceito, com o porquê, para não virar
   relato. Criptografia sem auditoria, metadado visível, ausência de forward secrecy.
6. **Versões com suporte:** só a mais recente e a `main`.
7. **Para quem hospeda** (se o projeto é self-hosted): segredo que precisa ser definido e o que
   acontece se não for. Com o código público, todo fallback do código é público.

## Escopo: como pensar

Pergunte "o que alguém ganha?" para cada parte do sistema.

**Costuma entrar:**

- ler ou mudar dado que não é seu (isolamento entre contas, servidores, conversas);
- contornar login, sessão, CSRF, CORS, rate limit, permissão ou papel de admin;
- segredo alcançável pelo app, pelo repo, por log de workflow ou pela API;
- tudo que quebra a promessa central do produto (a criptografia de um chat, a integridade do dado
  de uma API).

**Costuma não entrar:**

- DoS e teste de carga contra a instância pública;
- engenharia social e credencial vazada do mantenedor;
- dependência já corrigida upstream esperando atualização;
- scanner automático sem impacto demonstrado;
- comportamento documentado como deliberado (CORS aberto de uma API pública, por exemplo).

## No GitHub

O canal preferido só funciona ligado: **Settings → Advanced Security → Private vulnerability
reporting → Enable**. Confira depois de criar o arquivo; o repo mostra o `SECURITY.md` na aba
**Security** e no **About** ("Security policy").

## Referências

- GoodChat (`SECURITY.md`): limites conhecidos da criptografia, seção para quem hospeda.
- Goodbot (`SECURITY.md`, pt-BR): escopo por parte do sistema.
- Helldivers-api (`SECURITY.md`): escopo de uma API pública sem conta.
