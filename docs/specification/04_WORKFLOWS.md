# WORKFLOWS.md

**Status:** APPROVED

## 1. Princípios

- Evidence before conclusion.
- Failure isolation.
- Desktop/Mobile isolation.
- AI optionality.
- Reliability disclosure.

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
- WF-GEO-010 Generate Recommendations
- WF-GEO-011 Generate Static HTML Report
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
→ Recommendations
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
- internal links.

Depois:

- normalize;
- deduplicate;
- apply scope;
- apply max_pages.

Se descobertas > max_pages, registrar total descoberto e total auditado.

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
→ Schema validation
→ Evidence validation
→ SemanticAssessment

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

## 12. WF-GEO-010 Recommendations

Finding
→ Root Cause
→ Recommendation
→ Severity
→ Impact
→ Effort
→ Confidence
→ Priority

Sem IA, templates técnicos continuam funcionando.

## 13. WF-GEO-011 HTML Report

Saída:

`report.html`

Sem backend, servidor ou internet obrigatória.

Seções mínimas:

- identificação;
- resumo executivo;
- como interpretar;
- confiabilidade da auditoria;
- scorecard;
- Desktop × Mobile;
- blockers;
- findings;
- evidence;
- recomendações;
- limitações;
- detalhes técnicos;
- glossário.

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
