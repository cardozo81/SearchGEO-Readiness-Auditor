# Guia de Causa Raiz e Remediação por Elemento

M16 adiciona uma camada de diagnóstico técnico sobre os findings já persistidos. Ela não recalcula Business Rules, Score, Coverage, Confidence, Consolidation, prioridade ou actionability.

## Onde aparece

Os dois relatórios do audit utilizam a mesma materialização `root_cause_analyses`:

- `report.html` — diagnóstico dentro de cada finding da página;
- `remediation.html` — diagnóstico por ocorrência dentro de cada problema agrupado.

## Como interpretar a localização

### ELEMENTO EXATO

Existe um único `ElementObservation` associado com segurança ao finding.

O relatório pode mostrar:

- selector CSS observado;
- tag/id/classes;
- `outer_html` observado;
- snapshot/device;
- mudança exata recomendada.

Exemplo conceitual:

```text
Escopo: EXACT_ELEMENT
Selector: title
Elemento: title
Relação: EXACT
```

### CONJUNTO DE ELEMENTOS

A condição pertence ao conjunto/estrutura, não a um nó isolado.

Exemplos:

- hierarquia de headings;
- vários blocos JSON-LD igualmente relacionados à regra.

O relatório lista os elementos observados relevantes com `relation=SET_MEMBER` e não escolhe um elemento arbitrário como causa única.

### REGIÃO CONTEXTUAL

A regra é semântica/editorial e o elemento observado apenas delimita onde o conteúdo foi avaliado.

Exemplo:

```text
Escopo: CONTENT_REGION
Selector: main
Relação: CONTEXT_REGION
```

Isso **não** significa que a tag `<main>` esteja tecnicamente defeituosa. Significa que o conteúdo dentro dessa região sustenta a avaliação semântica.

### DOCUMENTO / RECURSO GLOBAL

HTTP, headers, `robots.txt`, sitemap e outras condições não DOM não recebem selector artificial.

```text
Escopo: DOMAIN_RESOURCE
Selector: NÃO APLICÁVEL
```

Quando a causa é documental/conteúdo mas não há nó comprovável:

```text
Selector: NÃO DETERMINADO
```

## Causa raiz

A causa raiz é materializada a partir de:

```text
RuleExecution.observed_value
+ Finding
+ Evidence
+ ElementObservation(s), quando houver
+ expected_condition da Business Rule
+ RemediationRecipe
```

O texto não deve declarar fatos que não estejam sustentados por esse conjunto.

## Observado versus esperado

Cada diagnóstico mostra separadamente:

- **Observado** — estado persistido pela execução da regra;
- **Esperado** — condição que a Business Rule exige;
- **Evidências-base** — IDs rastreáveis usados no diagnóstico.

Essa distinção ajuda a equipe a verificar a causa antes de alterar o site.

## Mudança exata recomendada

A recomendação deriva da recipe determinística da regra e pode combinar:

- tipo da ação;
- alvo técnico;
- elemento/estrutura;
- localização;
- descrição da mudança;
- exemplo pós-correção quando seguro;
- decisão humana obrigatória quando necessária.

Exemplo conceitual para canonical ausente:

```text
Ação: ADD_OR_CORRECT
Alvo: Documento HTML
Elemento/estrutura: <link rel="canonical">
Local: <head>
```

A URL preferencial não é inventada pelo auditor. Quando a decisão depende da estratégia de canonicalização, o relatório exige decisão humana.

## HTML observado

`outer_html` aparece somente quando o elemento foi realmente persistido. O relatório escapa o HTML e não o executa.

Quando não existe trecho capturado, a ferramenta não reconstrói um HTML fictício para parecer mais precisa.

## Dados Estruturados

Para `BR-GEO-034..037`, M16 prioriza os elementos:

```css
script[type="application/ld+json"]
```

Quando existe um único bloco relacionado, ele pode ser `EXACT`. Quando existem vários blocos igualmente relacionados, são mostrados como conjunto (`SET_MEMBER`). Essas regras não usam `<main>` como substituto genérico de localização.

## Regras semânticas

Regras de entidade, answerability, citation readiness, evidence/trust e intent coverage podem usar `<main>` como região contextual quando o snapshot contém esse elemento.

O selector de contexto indica **onde a análise foi feita**, não necessariamente qual tag deve ser removida ou recriada.

A correção vem da causa raiz + recipe e pode exigir alteração de conteúdo dentro da região.

## Critério de aceite e revalidação

Cada diagnóstico preserva:

- critérios de aceite da recipe;
- passos de revalidação;
- decisão humana quando aplicável.

A correção deve ser considerada concluída somente após nova auditoria confirmar que a condição da Business Rule foi satisfeita ou que a revisão contextual resultou em decisão intencional documentada.

## Persistência

M16 adiciona de forma aditiva a tabela SQLite:

```text
root_cause_analyses
```

Há no máximo uma análise materializada por `finding_id`. Ela contém causa, escopo, elementos afetados, selector status, observado, esperado, mudança, exemplo, aceite, revalidação, decisão humana e confiança diagnóstica.

`diagnostic_confidence` mede a precisão da localização/causa do M16. Não é `Confidence` do modelo de scoring e não entra em `SCORE-GEO-001`.
