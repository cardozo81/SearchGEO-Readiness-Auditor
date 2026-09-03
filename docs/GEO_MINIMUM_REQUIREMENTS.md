# Premissas mínimas e reforços para GEO

Este guia classifica os principais sinais técnicos e semânticos avaliados pelo SearchGEO como **mínimos**, **contextuais**, **opcionais/reforço** ou **não obrigatórios**.

O foco primário do baseline é Google Search e seus recursos de IA. Referências a outros mecanismos são secundárias e não alteram a regra principal de scoring.

O SearchGEO mede readiness. Ele não garante rastreamento, indexação, ranking, rich result, citação ou presença em respostas generativas.

## Regra principal de aplicabilidade

Uma característica opcional ausente não deve virar falha artificial.

A partir de `SCORE-GEO-002`:

- uma dimensão integralmente e legitimamente fora do universo aplicável fica `NOT_APPLICABLE`;
- `NOT_APPLICABLE` não recebe 0 nem 100;
- a dimensão não reduz Coverage nem bloqueia o Overall;
- se o tópico passar a existir na URL, ele se torna aplicável e seus resultados entram normalmente no Score GEO;
- ausência de RuleExecutions ou pré-requisito bloqueado continua sendo `NOT_CONSOLIDATED`, nunca `NOT_APPLICABLE` benigno.

## Matriz de aderência

| Tópico | Classificação SearchGEO | Papel para Google/GEO | Como entra no cálculo |
| --- | --- | --- | --- |
| URL tecnicamente recuperável | MÍNIMO | Pré-condição para rastreamento/análise. | Falha material afeta Acessibilidade Técnica. |
| Resposta HTML/conteúdo utilizável | MÍNIMO | A página precisa fornecer conteúdo processável. | Sem documento utilizável, dimensões dependentes não consolidam. |
| Conteúdo essencial recuperável após JavaScript | MÍNIMO quando aplicável | Em páginas JS/SPA, o conteúdo importante precisa permanecer recuperável. | Entra em Extração de Conteúdo. |
| Conteúdo principal identificável | MÍNIMO | Base para compreensão semântica. | Afeta Extração, Semântica, Answerability e intents. |
| Conteúdo importante disponível em texto | MÍNIMO | Google recomenda que conteúdo importante esteja em forma textual. | Informação não recuperável reduz cobertura/readiness. |
| Indexabilidade e elegibilidade a snippet | MÍNIMO para participação pública em AI Overviews/AI Mode | Google exige que a página esteja indexada e elegível a aparecer com snippet. | Afeta Indexability e pode impedir consolidação útil para presença pública. |
| Tópico/intenção principal identificável | MÍNIMO semântico | Necessário para compreender o propósito da URL. | Entra em Estrutura Semântica, Answerability e Intent Coverage. |
| Claims, números e condições coerentes | MÍNIMO de confiança | Reduz ambiguidade e risco de informação conflitante. | Afeta Citation Readiness e Evidence Trust. |
| JSON-LD / Structured Data | OPCIONAL / REFORÇO | Google recomenda Structured Data para compreensão e rich results; não é requisito adicional para AI Overviews/AI Mode. | Ausente legitimamente: `STRUCTURED_DATA=NOT_APPLICABLE`; presente: BR-GEO-034..037 entram no score. |
| Sitemap XML | OPCIONAL / DESCOBERTA | Ajuda descoberta e sinais de atualização. | Ausência isolada não é FAIL. |
| Canonical | CONTEXTUALMENTE RECOMENDADO | Importante quando há duplicidade, variantes ou URL preferencial. | Ausência isolada não é blocker universal; conflitos podem afetar Indexability. |
| robots.txt como arquivo | OPCIONAL COMO ARQUIVO | Ausência/404 não significa bloqueio; regras presentes precisam permitir a intenção desejada. | Política observada entra em Acessibilidade/Robots. |
| Autor/publisher | CONTEXTUAL | Importância depende do tipo de página e dos claims. | Entra em Evidence Trust quando aplicável. |
| Data de publicação/atualização | CONTEXTUAL | Relevante para conteúdo temporal/editorial. | Entra em Freshness quando aplicável. |
| `llms.txt` ou arquivo especial para IA | NÃO OBRIGATÓRIO | Google declara que não é necessário criar arquivo de IA/markup especial para seus recursos de IA. | Não afeta score automaticamente. |
| Schema.org especial para IA | NÃO OBRIGATÓRIO | Google declara que não há schema especial necessário para AI Overviews/AI Mode. | Não existe regra que exija schema especial. |
| GPTBot liberado | NÃO OBRIGATÓRIO para Google Search/GEO | Não é crawler do Google; no SearchGEO é tratado separadamente de search crawlers. | Não penaliza Search readiness por si só. |

## Google: JSON-LD é obrigatório?

Não de forma universal.

Para aparecer como link de suporte em AI Overviews ou AI Mode, a documentação do Google exige que a página esteja indexada e elegível a aparecer na Pesquisa Google com snippet, atendendo aos requisitos técnicos gerais de Search. O Google afirma que não existem requisitos técnicos adicionais para esses recursos e que não é necessário adicionar schema.org especial, arquivo de IA ou nova marcação específica.

Structured Data continua relevante porque:

- fornece sinais explícitos sobre entidades, tipos e propriedades;
- pode habilitar rich results e outras experiências de Search;
- ajuda o mecanismo a compreender conteúdo de forma mais estruturada;
- precisa corresponder ao conteúdo visível e não pode ser enganoso.

Google aceita JSON-LD, Microdata e RDFa e recomenda JSON-LD na maioria dos casos por facilidade de implementação/manutenção.

## Bing: papel do JSON-LD

Bing também usa Structured Data como um dos sinais para compreender conteúdo e entidades. A documentação do Bing Webmaster descreve JSON-LD como uma forma de ajudar o mecanismo a entender melhor a página. Em cenários verticais, como Shopping, Bing recomenda fortemente markup completo e coerente.

Isso não deve ser interpretado como requisito universal para toda URL ser rastreada ou indexada. No SearchGEO, Google permanece a referência primária do baseline; Bing é sinal complementar.

## Quando JSON-LD existe

O baseline atual do SearchGEO detecta Structured Data em blocos:

```html
<script type="application/ld+json">
...
</script>
```

Quando existe JSON-LD:

- BR-GEO-034 avalia interpretabilidade/sintaxe;
- BR-GEO-035 avalia tipos e propriedades;
- BR-GEO-036 avalia coerência com conteúdo visível;
- BR-GEO-037 avalia coerência das entidades declaradas e observadas;
- PASS/WARNING/FAIL participam do `STRUCTURED_DATA` Score;
- UNKNOWN/ERROR reduzem Coverage/Consolidation conforme as regras gerais;
- markup inválido, enganoso ou contraditório pode reduzir a Compatibilidade GEO.

Adicionar JSON-LD apenas para aumentar cobertura não é prática válida.

## JSON-LD pode usar valores diferentes do HTML?

Pode usar **representação diferente**, mas não **fato diferente**.

Exemplos coerentes:

- HTML: `R$ 27,50`; JSON-LD: `price=27.50`, `priceCurrency=BRL`;
- HTML: `3 de setembro de 2026`; JSON-LD: `2026-09-03`;
- HTML usa nome comercial; JSON-LD usa nome jurídico completo, desde que a relação esteja sustentada.

Não é aceitável divergir ou inventar:

- preço;
- disponibilidade;
- benefícios;
- ratings/reviews;
- autoria;
- datas;
- identidade do produto/serviço;
- entidade responsável;
- claims promocionais ou factuais.

## Cobertura de formatos

Embora Google aceite JSON-LD, Microdata e RDFa, o parser Structured Data do baseline atual do SearchGEO é especificamente orientado a JSON-LD. Até Microdata/RDFa receberem parser e testes equivalentes, a documentação não deve afirmar cobertura integral desses formatos.

## Como o relatório deve se comportar

Exemplo sem JSON-LD, com as demais dimensões aplicáveis consolidadas:

```text
Compatibilidade GEO — Desktop: 88,9/100
Dimensões aplicáveis: 9 de 10
Dados Estruturados: NÃO APLICÁVEL
```

A nota é calculada somente sobre dimensões aplicáveis.

Exemplo com JSON-LD presente:

```text
Dados Estruturados: 75,0/100
Consolidação: CONSOLIDADO
```

Nesse caso `STRUCTURED_DATA` passa a integrar o Overall.

`NÃO DETERMINADO` continua reservado para situações em que a avaliação deveria ocorrer, mas cobertura/confiança não foram suficientes. Isso pode bloquear a Compatibilidade GEO.
