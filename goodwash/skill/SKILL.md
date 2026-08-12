---
name: goodwash
description: "Reescreve texto para soar humano e destruir a assinatura estatística da marca d'água de IA (lista verde/vermelha) — a reescrita é feita por VOCÊ (o modelo desta sessão), sem OpenRouter. Rewritas em 3 intensidades + check offline de tells de IA. Args: [lavar [leve|media|profunda] <texto>|checar <texto>|help]"
user_invocable: true
---

# /goodwash

Ferramenta que reescreve texto gerado por IA para que ele soe naturalmente
escrito por uma pessoa. A geração é feita por VOCÊ (o modelo desta sessão),
diretamente — sem CLI, sem OpenRouter, sem chave. O CLI `goodwash` existe no
terminal pra quem quiser gerar via OpenRouter `:free` ou usar o `checar`
offline; aqui dentro basta o texto.

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
escolhas de tokens, não nos caracteres. Qualquer **reescrita genuína** — que
muda as palavras, a ordem, a estrutura das frases — destroi o sinal: os tokens
novos não foram sorteados com o viés verde. Papers de watermarking documentam
explicitamente que parafrasear/reescrever é o ataque que derruba esse método.
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

### checar `<texto>`

Rode quando o usuário quiser ver o que "delata" o texto como IA antes de
reescrever (ou pra checar um texto já reescrito). Liste, em PT-BR:

- **🔁 Transições/fórmulas** encontradas (ex.: "além disso", "portanto", "é
  importante notar", "em conclusão", "vale ressaltar") — mostre um ou dois
  exemplos no próprio texto.
- **🔤 Palavras batidas** (jargão de IA: "fundamental", "crucial", "de forma
  eficaz", "cada vez mais", "no cenário atual"…).
- **📏 Ritmo homogêneo** — se as frases têm comprimento parecido demais
  (tamanho entre a menor e a maior é pequeno) e/ou parágrafos uniformes.
- **➗ Paralelismos** óbvios (tríades, estruturas "não apenas… mas também").
- **🧊 Frieza** — excesso de voz passiva, ausência de linguagem concreta.

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
goodwash checar "texto"              # tells de IA offline (0 LLM, sem chave)
goodwash -o saida.txt "texto"        # salva em arquivo
```

Aqui no Claude Code o `/goodwash lavar` reescreve mais caprichado (o modelo
desta sessão) e sem chave — prefira o skill.