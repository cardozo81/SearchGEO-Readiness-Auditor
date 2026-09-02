# IMPLEMENTATION_PLAN.md

**Status:** APPROVED

## M0 — Bootstrap

Objetivo:

- estrutura mínima;
- package Python;
- configuração;
- logging;
- CLI;
- --version;
- `audit <target>`;
- validação básica.

Não implementar módulos futuros vazios.

## M1 — Audit + Persistence

Implementar:

- Audit;
- AuditTarget;
- Page;
- PageSnapshot;
- Evidence;
- RuleExecution;
- Finding;
- repositories mínimos;
- audit.db;
- estrutura filesystem.

Critério:

criar, persistir, encerrar, reabrir e recuperar Audit.

## M2 — Discovery + HTTP

Implementar:

- seed;
- normalization;
- robots;
- sitemap;
- internal links;
- provenance;
- max_pages;
- HTTP;
- redirects;
- headers;
- network errors.

Primeiras regras técnicas.

## M3 — Rendering Desktop/Mobile

Implementar:

- Playwright;
- Chromium;
- Desktop profile;
- Mobile profile;
- RAW;
- rendered;
- PageSnapshot independente.

## M4 — Extraction + Evidence

Implementar:

- content extraction;
- metadata;
- headings;
- links;
- Dados Estruturados;
- Evidence Manager.

## M5 — Deterministic Rules Engine

Implementar:

- Rule Registry;
- Check;
- Rule Executor;
- dependencies;
- applicability;
- findings.

Principalmente BR-GEO-001..018.

Checkpoint:

Technical Auditor Alpha funcional sem IA.

## M6 — JavaScript / SPA

Implementar:

- BR-GEO-019..024;
- RAW × RENDERED;
- direct routes;
- soft-404;
- lazy loading;
- crawlable navigation.

## M7 — Semantic Provider + Fallback

Implementar:

- SemanticAnalysisProvider;
- NoneProvider;
- OpenAIProvider;
- FULL / DEGRADED / NO_AI;
- schema validation;
- evidence validation;
- BR-GEO-028..049 progressivamente.

Teste obrigatório com IA e sem IA.

## M8 — Desktop × Mobile Comparison

Implementar DeviceComparator e BR-GEO-052.

## M9 — Scoring + Reliability

Implementar:

- ScoringEngine;
- ScoreContribution;
- Coverage;
- Confidence;
- Consolidation;
- scoring groups;
- Overall por dispositivo.

## M10 — Prioritization + Recommendations

Implementar:

- Severity;
- Impact;
- Effort;
- Priority;
- deterministic recommendation templates;
- RemediationGroup.

## M11 — Static HTML Report

Implementar:

- ReportBuilder;
- localization pt-BR;
- glossary;
- reliability section;
- scorecard;
- findings;
- evidence;
- recommendations;
- limitations.

## M12 — Critical Tests + Stable Local Baseline

Testar minimamente:

- parsing;
- Rules Engine;
- scoring;
- Desktop/Mobile;
- AI fallback;
- report;
- regressões críticas.

## Stable Local Baseline

Critérios:

- recebe domínio;
- descobre URLs;
- respeita max_pages;
- Desktop/Mobile;
- RAW/rendered;
- SPA/non-SPA;
- evidence;
- rules;
- findings;
- IA opcional;
- coverage/confidence;
- scoring;
- prioritization;
- report HTML pt-BR;
- limitações explícitas;
- testes críticos.

Somente depois do M12 avaliar Git/GitHub.

## Regra operacional

Cada marco deve ser:

1. implementado;
2. validado;
3. comparado com critérios;
4. encerrado.

Não avançar automaticamente ao marco seguinte.
