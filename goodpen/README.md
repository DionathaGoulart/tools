# goodpen — cofre de senhas em duas versões

Duas ferramentas pra guardar senhas criptografadas com backup em pendrive.
Fazem **a mesma coisa** — mudam só o "como". Escolha uma:

| | [**standalone**](./standalone) | [**pass-store**](./pass-store) |
|---|---|---|
| O que é | Um programa próprio (binário único) | Guia + script que configuram ferramentas prontas |
| Motor | age (embutido no binário) | `pass` + `gpg` + `git` (instala no sistema) |
| Dependências | **Zero** — só baixar o executável | Precisa instalar 3 programas |
| Windows | Roda nativo (`.exe`) | Só via WSL / Git Bash |
| Interface | Menu no terminal **+ web no navegador** | Linha de comando pura |
| Criptografia | X25519 (age) | RSA 4096 (GPG) — as duas são fortes |
| Backup da chave | **QR code** (cabe no Bitwarden) | Arquivo de ~7KB (sem QR) |
| Esqueceu a passphrase | Recupera com o QR da chave | Perdeu tudo |
| Gera passphrase forte | Sim (`cofre frase`) | Não |
| Histórico git completo | Não (espelho simples) | Sim |
| Apps de celular / browser | Não (formato próprio) | Sim (ecossistema `pass`) |

**Regra rápida:**

- Quer simplicidade, QR e rodar em qualquer sistema sem instalar nada → **[standalone](./standalone)**
- Quer o padrão consagrado do Unix, apps de celular e extensão de browser → **[pass-store](./pass-store)**

São independentes; teste os dois e fique com o que gostar.

## Começar

```bash
# standalone — executável único (compile com build.sh ou pegue em dist/)
cofre          # menu no terminal
cofre web      # interface no navegador

# pass-store — pass + gpg + git com pendrive como cofre
bash ~/Desktop/tools/goodpen/pass-store/setup.sh
```

Detalhes em [standalone/README.md](./standalone/README.md) e
[pass-store/README.md](./pass-store/README.md).

---

↩ [Voltar pro índice de ferramentas](../README.md)
