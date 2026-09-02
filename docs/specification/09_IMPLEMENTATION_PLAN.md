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

Git/GitHub já são utilizados a partir do M0 para controle de versão e repositório de desenvolvimento.

A adoção antecipada de Git/GitHub é uma decisão de processo de desenvolvimento e não torna GitHub dependência de execução do produto.

## Regra operacional

Cada marco deve ser tratado como unidade independente e somente pode ser considerado concluído após:

1. implementação integral do escopo permitido;
2. validação e testes obrigatórios;
3. comparação com seus critérios e gates;
4. revisão de escopo, regressões, rastreabilidade, dependências e segredos;
5. integração integral em `main` por PR validado;
6. confirmação pós-merge de que `main` contém o resultado aprovado;
7. confirmação de que a branch não possui conteúdo exclusivo e registro da branch para limpeza manual diferida conforme D-036;
8. encerramento sem pendências bloqueantes.

Quando todos esses gates forem satisfeitos, o avanço automático ao marco seguinte é autorizado conforme D-034, sem necessidade de nova aprovação humana.

Durante a cascata M4 → M12, a exclusão física das branches não bloqueia o avanço quando os controles de D-036 forem satisfeitos. A lista acumulada de branches encerradas deve ser apresentada ao humano ao final para exclusão manual.

A cascata deve interromper diante dos blockers reais definidos em D-034 ou em outra decisão normativa aplicável. Problemas técnicos ordinários e solucionáveis devem ser diagnosticados, corrigidos, revalidados e não constituem, por si só, motivo para solicitar aprovação humana.

Nenhum marco pode ser declarado concluído apenas para permitir avanço, e nenhum escopo do marco seguinte deve ser antecipado materialmente antes do encerramento do marco atual, salvo infraestrutura estritamente necessária e já permitida pela especificação.
