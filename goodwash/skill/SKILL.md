---
name: goodwash
description: "Avalia se um texto foi escrito por IA (veredito + confiança + evidência) e reescreve pra soar humano, diluindo a assinatura estatística da marca d'água (lista verde/vermelha) — tudo feito por VOCÊ (o modelo desta sessão), sem OpenRouter. Rewrite em 3 intensidades com auto-avaliação. Args: [lavar [leve|media|profunda] <texto>|avaliar <texto>|checar <texto>|help]"
user_invocable: true
---

# /goodwash

Faz duas coisas: **avalia** se um texto foi escrito por IA (`avaliar`) e
**reescreve** texto de IA pra que ele soe naturalmente escrito por uma pessoa
(`lavar`) — se auto-avaliando ao fim. Tudo é feito por VOCÊ (o modelo desta
sessão), diretamente: sem CLI, sem OpenRouter, sem chave. O CLI `goodwash`
existe no terminal pra quem quiser gerar via OpenRouter `:free` ou rodar os
detectores offline; aqui dentro basta o texto.

## Como a marca d'água funciona (pra reescrever certo)

A watermark "lista verde / lista vermelha" (técnica acadêmica de Kirchenbauer
et al., usada em larga escala pela indústria) **não carimba caracteres nem
frases** — ela enviesa a *escolha de tokens* na hora da geração:

1. Durante a geração, um hash do contexto (tokens anteriores) + uma chave
   secreta divide o vocabulário do modelo em duas listas: **verde** (roubada
   a favor) e **vermelha** (desfavorecida).
2. O modelo é enviesado a escolher tokens da lista verde — o texto sai com uma
   proporção de tokens "verdes" acima do acaso.
3. O detector, com a mesma chave secreta, recalcula as listas e mede essa
   proporção: acima do limiar = veio de IA.

**A consequência direta (e o que o goodwash explora):** o sinal mora nas
escolhas de tokens, não nos caracteres. Uma **reescrita genuína** — que muda as
palavras, a ordem, a estrutura das frases — dilui o sinal: os tokens novos não
foram sorteados com o viés verde. É o ataque de paráfrase, documentado nos
papers.

**Seja honesto sobre o limite quando o usuário perguntar:** dilui, não zera. O
follow-up dos próprios autores (arXiv:2306.04634) mostra que, após paráfrase
humana forte, a watermark ainda é detectável observando ~800 tokens a 1e-5 de
falso positivo — paráfrases vazam n-grams. Texto curto sai limpo; texto longo
só perde confiança. E lembre: quem reescreve é outro LLM, então contra detector
*estilométrico* (GPTZero, Turnitin — o que a maioria enfrenta de fato) o risco é
trocar estilo de IA A por estilo de IA B. Por isso as diretrizes abaixo importam
mais que o ato de reescrever.

Traduzo essa intuição pra reescrita:

- **Varie o vocabulário de verdade.** Troque jargão e palavra batida por
  palavras comuns e precisas; use sinônimos que o contexto aceite.
- **Quebre o ritmo uniforme.** Texto de IA tende a frases de comprimento
  equilibrado. Alterne frases curtas e longas de forma orgânica.
- **Desmonte estruturas paralelas e tríades.** ("não apenas X, mas também Y";
  listas de três termos). Humanos não falam tão certinho.
- **Troque transições fórmula.** "Além disso", "portanto", "é importante
  notar", "em conclusão" — substitua por conectivos naturais ou nenhum.
- **Varie o tamanho dos parágrafos**, mude a ordem das ideias onde ficar
  natural, troque os ganchos e fechamentos.
- **Use linguagem concreta e específica**, expressões idiomáticas, leve
  informalidade quando o tom permitir. Escreva como uma pessoa real.

Regras inegociáveis: **preserve significado, tom e fatos**; NUNCA adicione
informação que não está no original (não invente nome, número, fato); responda
só com o texto reescrito, sem prefácio. Uso responsável: evite usar pra
fraude acadêmica, spam ou desinformação.

## Comandos

Sem argumento = `lavar` (intensidade `media`) esperando o texto.

### lavar `[leve|media|profunda] <texto>`

O usuário cola o texto (ou o já veio na conversa). Reescreva conforme a
intensidade:

- **leve** — mantenha estrutura e ordem das ideias; mexa no vocabulário e
  quebre os paralelismos/transições mais óbvios. Parece o mesmo texto, só com
  as arestas de IA lixadas.
- **media** (padrão) — reescreva frase a frase: reestruture sentenças, varie
  ritmo e léxico, mantenha a ordem geral e os parágrafos.
- **profunda** — reescreva por completo: quebre parágrafos noutro lugar,
  reordene ideias onde ficar natural, troque ganchos e fechamentos. Soa
  escrito do zero por um humano, com os mesmos fatos e tom.

Aplique sempre as diretrizes da seção acima, principalmente a variação de
vocabulário e ritmo — é isso que derruba o sinal estatístico. Mostre o
resultado em markdown, num bloco de texto limpo, e feche perguntando se quer
ajustar o tom/intensidade ou mostrar o que mudou.

Depois de reescrever, **avalie o seu próprio resultado** (seção `avaliar`
abaixo) e diga o veredito antes/depois em uma linha — ex.: "estilo: alto → baixo
(sumiram 5 transições fórmula, ritmo variou)". Se o texto reescrito ainda te
parecer IA, diga isso e ofereça outra passada mais profunda em vez de entregar
como se estivesse pronto. E seja honesto sobre o delta: ele mede os mesmos
eixos que a reescrita ataca — cair é o esperado, não aprovação em detector
externo (GPTZero, Turnitin).

### avaliar `<texto>`

O usuário quer saber: **isso foi escrito por IA ou por uma pessoa?** Julgue por
evidência de estilo, nesses eixos:

| Eixo | Puxa pra IA quando… |
|---|---|
| Transições fórmula | "além disso", "portanto", "é importante notar", "em suma" aparecem com frequência |
| Ritmo das frases | comprimentos parecidos demais; falta frase curta de uma linha |
| Palavras batidas | "fundamental", "crucial", "no cenário atual", "jornada", "ecossistema" |
| Paralelismo/tríade | "rápido, simples e barato"; "não apenas X, mas também Y" |
| Voz passiva | "foi considerado", "são utilizados" em excesso |
| Marcas humanas | AUSÊNCIA de coloquialismo, 1ª pessoa, detalhe concreto, opinião, hesitação |
| Parágrafos | todos do mesmo tamanho |
| Pontuação | só ponto e vírgula; nenhum travessão, parêntese, reticência |
| Estrutura markdown | listicle com rótulo em negrito ("**Foco**: …"), cabeçalho + bullets no formato resposta-de-chat |

Cuidado com dois falsos positivos estruturais: enumeração banal ("pão, leite e
ovos") e oração coordenada ("comprei tomate e voltei") NÃO são tríade retórica;
bullet sozinho NÃO é listicle de IA — humano também anota assim.

Entregue: **veredito** (provavelmente IA / incerto / provavelmente humano),
**confiança** em %, os eixos que mais pesaram e **trechos citados do texto** como
evidência. Prefira "incerto" a chutar.

Três regras que você não pode quebrar aqui:

1. **Texto curto (menos de ~60 palavras) é sempre incerto.** Não existe sinal
   suficiente. Diga isso.
2. **Prosa formal, técnica, acadêmica ou traduzida dá falso positivo** — ela usa
   as mesmas transições e a mesma voz passiva. Considere o gênero antes de
   julgar e baixe a confiança.
3. **Feche sempre com o aviso:** isto não é prova, detectores de texto de IA
   erram, e o resultado não serve pra acusar ninguém — só pra a pessoa medir o
   próprio texto.

O CLI tem o mesmo comando offline (`goodwash avaliar`, com `--llm` pra pedir a
segunda opinião de um modelo).

### checar `<texto>`

Versão enxuta do `avaliar`, focada em *o que consertar* em vez de "é IA?". Rode
quando o usuário quiser ver o que "delata" o texto antes de reescrever (ou pra
checar um texto já reescrito). Liste, em PT-BR:

- **🔁 Transições/fórmulas** encontradas (ex.: "além disso", "portanto", "é
  importante notar", "em conclusão", "vale ressaltar") — mostre um ou dois
  exemplos no próprio texto.
- **🔤 Palavras batidas** (jargão de IA: "fundamental", "crucial", "de forma
  eficaz", "cada vez mais", "no cenário atual"…).
- **📏 Ritmo homogêneo** — se as frases têm comprimento parecido demais
  (tamanho entre a menor e a maior é pequeno) e/ou parágrafos uniformes.
- **➗ Paralelismos** óbvios (tríades, estruturas "não apenas… mas também").
- **🧊 Frieza** — excesso de voz passiva, ausência de linguagem concreta.
- **🧱 Estrutura de resposta de chat** — cabeçalhos + bullets com rótulo em
  negrito ("**Foco**: …"), o esqueleto clássico de saída de IA.

Lembrete honesto ao fechar: o check é **heurística de estilo** — a watermark
real precisa da chave secreta do detector e não dá pra medir localmente. O
que ele aponta é exatamente o que a reescrita deve atacar. Feche com
sugestão: `/goodwash lavar media "<texto>"`.

### help

Resumo do que a ferramenta faz e das intensidades.

## CLI no terminal (opcional)

No terminal, o CLI `goodwash` faz a mesma reescrita via OpenRouter `:free`
(mesma persona) e traz o `checar` offline:

```bash
echo "texto" | goodwash              # reescrita média via OpenRouter
goodwash leve "texto"                # intensidade leve
goodwash profunda arquivo.txt        # profunda, de arquivo
goodwash --ate 30 "texto"            # reescreve até a auto-avaliação bater a meta
goodwash avaliar "texto"             # IA ou humano? veredito + confiança (offline)
goodwash avaliar --llm "texto"       # + segunda opinião do modelo
goodwash checar "texto"              # tells de IA offline (0 LLM, sem chave)
goodwash -o saida.txt "texto"        # salva em arquivo
```

Aqui no Claude Code o `/goodwash lavar` reescreve mais caprichado (o modelo
desta sessão) e sem chave — prefira o skill.