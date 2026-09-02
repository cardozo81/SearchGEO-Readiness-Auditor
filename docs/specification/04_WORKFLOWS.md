# WORKFLOWS.md

**Status:** APPROVED — extended by M13 Actionable GEO Report

## 1. Princípios

- Evidence before conclusion.
- Failure isolation.
- Desktop/Mobile isolation.
- AI optionality.
- Reliability disclosure.
- Actionable remediation must remain evidence-bound.

## 2. Catálogo

- WF-GEO-001 Execute Website Audit
- WF-GEO-002 Initialize Audit
- WF-GEO-003 Discover URLs
- WF-GEO-004 Acquire Page Snapshot
- WF-GEO-005 Execute Technical Analysis
- WF-GEO-006 Extract Page Content
- WF-GEO-007 Execute Semantic Analysis
- WF-GEO-008 Compare Desktop and Mobile
- WF-GEO-009 Consolidate Findings and Scores
- WF-GEO-010 Generate Recommendations and Remediation
- WF-GEO-011 Generate Static Actionable HTML Report
- WF-GEO-012 Complete Audit

## 3. WF-GEO-001

Fluxo:

Initialize
→ Discover
→ For each Page
→ Desktop Snapshot
→ Mobile Snapshot
→ Technical
→ Extract
→ Semantic/Fallback
→ Compare
→ Findings
→ Scores
→ Priority
→ Remediation
→ HTML
→ Complete

## 4. WF-GEO-002 Initialize Audit

- validar target;
- gerar Audit ID;
- criar diretórios;
- inicializar persistência;
- detectar capabilities;
- determinar FULL / DEGRADED / NO_AI.

Falha de BR-GEO-001 encerra a auditoria.

## 5. WF-GEO-003 Discover URLs

Fontes:

- seed;
- robots/sitemap;
- sitemap;
- internal links;
- redirects elegíveis.

Depois:

- normalize;
- deduplicate;
- apply scope;
- apply max_pages.

Se descobertas > max_pages, registrar total descoberto e total auditado.

O estado necessário para explicar discovery no relatório deve ser persistido como Page, Evidence e Audit limitation; WF-GEO-011 não depende do objeto M2 em memória.

## 6. WF-GEO-004 Acquire Page Snapshot

Executar separadamente:

- DESKTOP;
- MOBILE.

Passos:

1. HTTP acquisition;
2. RAW preservation;
3. browser render;
4. rendered DOM capture;
5. snapshot metadata.

## 7. WF-GEO-005 Technical Analysis

Ordem:

Retrievability
→ HTTP
→ Redirect
→ HTML
→ Indexability
→ Canonical
→ Robots
→ Rendering
→ SPA/Routes

Sempre verificar applicability e dependencies antes da regra.

## 8. WF-GEO-006 Extract Page Content

Entrada:

- RAW;
- Rendered DOM.

Saída:

- main content;
- metadata;
- headings;
- links;
- Dados Estruturados;
- evidence.

Distinguir falha do site de falha do extrator.

## 9. WF-GEO-007 Semantic Analysis

### FULL

Evidence
→ Input Builder
→ Semantic Provider
→ Strict schema validation
→ Evidence validation
→ SemanticAssessment
→ normalized RuleExecution/Finding

### NO_AI

Deterministic components
→ safe heuristics
→ semantic-only UNKNOWN

### DEGRADED

Provider falhou
→ fallback
→ limitation codes
→ UNKNOWN quando necessário

Business Rules nunca dependem diretamente de provider específico.

O relatório reutiliza SemanticAssessment, reasoning_summary, entities, intents e evidence_ids já persistidos. Não existe segunda chamada livre de IA apenas para redigir recomendações.

## 10. WF-GEO-008 Desktop × Mobile

Compara resultados dos snapshots e avaliações.

Resultado:

- SAME;
- DIFFERENT;
- NOT_APPLICABLE;
- UNKNOWN.

Finding somente para diferença material.

## 11. WF-GEO-009 Findings and Scores

- validar BR-GEO-053;
- deduplicar efeitos de causa raiz;
- calcular contribuições;
- calcular score;
- calcular coverage;
- calcular confidence;
- resolver consolidation;
- validar BR-GEO-054.

M13 não altera `SCORE-GEO-001`.

## 12. WF-GEO-010 Recommendations and Remediation

Fluxo aprovado:

```text
Finding evidence-backed
→ Root Cause
→ Remediation Group
→ Severity / Impact / Effort / Confidence
→ Priority
→ Remediation Recipe por rule_id
→ Recommendation persistida
```

A `RemediationRecipe` deve tentar responder, quando aplicável:

- alvo técnico;
- elemento/localização;
- ação;
- descrição;
- exemplo seguro;
- critérios de aceite;
- revalidação;
- decisão humana necessária.

Invariantes:

- recipe não altera score ou priority;
- recipe não cria evidence;
- example não é HTML observado;
- ausência de recipe específica usa fallback explícito;
- canonical, noindex, structured data, autoria, freshness e fontes não podem ser inventados ou alterados sem base suficiente.

Sem IA, recipes técnicas continuam funcionando.

## 13. WF-GEO-011 Actionable HTML Report

Saída:

`report.html`

Sem backend, servidor, CDN ou internet obrigatória.

Ordem executiva de referência:

1. Compatibilidade GEO geral por dispositivo;
2. Cobertura e confiabilidade;
3. Principais oportunidades;
4. Score GEO — Desktop;
5. Score GEO — Mobile;
6. Plano de correção priorizado;
7. Correções técnicas detalhadas;
8. Análise de conteúdo e semântica;
9. Entidades e intenções;
10. Citation Readiness / Evidence Trust;
11. Cobertura do Crawl;
12. Limitações;
13. Detalhes técnicos;
14. Metodologia/interpretação;
15. Glossário.

### Regra de compatibilidade

`OVERALL_READINESS` somente é exibido como nota quando o score persistido está consolidado.

Quando não for consolidável:

```text
COMPATIBILIDADE GEO: NÃO DETERMINADA
```

Coverage não pode substituir a nota.

### Regra de HTML observado

O report deve separar:

- HTML efetivamente persistido como evidência;
- exemplo de correção recomendado.

Se o trecho original não estiver persistido na Evidence:

```text
Trecho HTML original não persistido para esta evidência.
```

### Crawl

WF-GEO-011 reabre Pages, Audit limitations e Evidence de robots/sitemap/HTTP para explicar descoberta, max_pages, fontes e limitações de crawl. Não recebe `DiscoveryResult` em memória.

## 14. WF-GEO-012 Complete Audit

Verificar:

- report;
- metadata;
- finding integrity;
- score reproducibility;
- limitations;
- artifacts.

Resultados:

COMPLETED + COMPLETE

ou

COMPLETED + COMPLETE_WITH_LIMITATIONS

FAILED somente quando não foi possível executar auditoria funcional mínima.
