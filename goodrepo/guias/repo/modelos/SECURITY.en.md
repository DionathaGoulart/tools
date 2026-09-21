<!--
  Template from goodrepo (.harness/repo/modelos). Rules: .harness/repo/seguranca.md.
  Replace every {{...}}, keep the scope honest, delete these comments. Needs "Private
  vulnerability reporting" turned on in Settings > Advanced Security.
-->

# Security

## Reporting a vulnerability

**Do not open a public issue.** An issue is visible to everyone before the fix ships, and
{{the public instance serves real people}}.

- **Preferred:** GitHub's private vulnerability reporting, on this repository's **Security** tab →
  **Report a vulnerability**.
- **Or email:** dionatha.work@gmail.com, with `[{{PROJETO}} security]` in the subject.

It helps a lot to include:

- what an attacker gains ({{read someone else's data, act without permission, take it down}});
- the steps to reproduce, or a minimal proof of concept (a `curl` beats a scanner report);
- the version or commit you tested.

Test against your own local or self-hosted instance, not against {{DOMINIO}}.

## What to expect

- A first answer within **7 days**.
- If the report is confirmed, the fix ships in the next release and the report becomes a public
  advisory after the deploy, crediting you if you want.

This is a one-person project, maintained in spare time. The timelines are a good-faith commitment,
not an SLA.

## Scope

In scope:

- {{anything that lets someone read or change data that is not theirs}}
- {{authentication, session, CSRF and CORS bypasses, privilege escalation}}
- {{secrets reachable through the app, the repo or a workflow log}}

Out of scope:

- denial-of-service or load tests against the public instance;
- social engineering, or access through a leaked credential of the maintainer;
- vulnerabilities in dependencies already fixed upstream and waiting for an update;
- findings from automated scanners with no demonstrated impact.

## Known limitations

<!-- What is known and documented, so it is not reported as a finding. Delete if none. -->

- **{{Limit.}}** {{Why it is accepted.}}

## Supported versions

Only the latest release and `main` get security fixes.
