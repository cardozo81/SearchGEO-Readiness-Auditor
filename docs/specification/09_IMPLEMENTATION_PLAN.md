# IMPLEMENTATION_PLAN.md

**Status:** APPROVED — extended through M15

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

Critério: criar, persistir, encerrar, reabrir e recuperar Audit.

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

Checkpoint: Technical Auditor Alpha funcional sem IA.

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

## M13 — Actionable GEO Remediation Report

Objetivo: evoluir a Stable Local Baseline de `GEO scoring/reporting` para `GEO scoring + evidence-backed actionable remediation`, sem alterar arbitrariamente o scoring aprovado.

Implementar:

- `RemediationRecipe` determinística por `rule_id` ou família de regras;
- recomendações M10 específicas por regra sempre que houver recipe;
- fallback explicitamente identificado;
- `REPORT-GEO-002`;
- resumo executivo com Compatibilidade GEO, Coverage e Confidence separados;
- `NÃO DETERMINADA` quando Overall não for consolidável;
- classificação textual/visual de score;
- principais oportunidades derivadas dos dados persistidos;
- scorecards Desktop/Mobile independentes;
- plano de correção priorizado;
- correções técnicas detalhadas com página, dispositivo, regra, alvo, observado, exemplo, aceite e revalidação;
- separação explícita entre HTML observado e exemplo recomendado;
- canonical acionável e conservadora;
- reutilização de SemanticAssessment, reasoning_summary, entidades e intents persistidos;
- Citation Readiness / Evidence Trust no report;
- diagnóstico de crawl reabrível a partir de estado persistido;
- documentação e testes mínimos de regressão.

Restrições:

- preservar `SCORE-GEO-001`;
- preservar `PRIORITY-GEO-001`;
- não converter UNKNOWN/ERROR/NOT_APPLICABLE em FAIL;
- ausência de IA não penaliza o website;
- não criar segunda chamada livre de IA para redação;
- não inventar HTML observado, canonical, noindex policy, structured data, autor, fonte, data ou fatos;
- relatório continua estático, autocontido, responsivo e sem dependência externa obrigatória.

## M14 — Multi-URL + Visual/DOM Evidence + Actionability

Objetivo: permitir auditoria explícita de várias URLs do mesmo origin em um único `audit_id` e melhorar a rastreabilidade visual/técnica das correções.

Implementar:

- `URL_SET` explícito por múltiplos targets e `--urls-file`;
- normalização/deduplicação determinística;
- aquisição global única de `robots.txt`/sitemaps;
- screenshots Desktop/Mobile;
- `ElementObservation` e vínculo Finding → elemento quando determinístico;
- actionability independente de RuleResult/scoring;
- referências técnicas versionadas;
- `REPORT-GEO-003`;
- distinção obrigatória entre zero calculado e ausência de cálculo.

Restrições:

- preservar `SCORE-GEO-001`;
- não expandir silenciosamente URL_SET por links/sitemap;
- não inventar selector, HTML observado ou referência técnica;
- recursos de domínio não são findings duplicados por página.

## M15 — Error-Centric Report + Report UX

Objetivo: melhorar navegação, legibilidade e priorização humana sem alterar dados persistidos, scoring ou findings.

Implementar:

- `report.html` preservado como visão principal orientada a página;
- menu lateral fixo em desktop com paths/query das URLs auditadas;
- navegação compacta em viewport estreita;
- tipografia e grid de Score GEO reequilibrados;
- guia das dez dimensões oficiais de `SCORE-GEO-001`;
- seção final explicando Score, Coverage, Confidence, Consolidation e Actionability;
- `remediation.html` no mesmo nível do `report.html`;
- contrato `REMEDIATION-GEO-001`;
- agrupamento transversal por escopo (`GLOBAL`/`PAGE`), `rule_id` e actionability;
- lista das páginas/paths afetados e ocorrências Desktop/Mobile;
- links relativos entre `report.html` e `remediation.html`;
- CLI informando o path dos dois relatórios;
- documentação operacional com exemplos genéricos de múltiplas URLs diretas e `--urls-file`.

Restrições:

- preservar `REPORT-GEO-003` para a projeção principal;
- preservar `SCORE-GEO-001`, Coverage, Confidence, Consolidation e actionability;
- `remediation.html` não recalcula regras, findings ou prioridades;
- não promover repetição em páginas a finding global;
- não introduzir nova chamada de IA;
- problemas do OpenAIProvider permanecem fora do escopo deste marco.

Critérios de conclusão:

1. ambos os HTMLs são gerados no mesmo workspace;
2. problema repetido em duas páginas aparece em um grupo transversal com duas ocorrências/páginas;
3. finding global permanece global;
4. sidebar usa paths sem repetir domínio e trunca somente visualmente;
5. layout do score não quebra tokens curtos de forma agressiva;
6. guia das dez dimensões e interpretação final estão presentes;
7. CLI exibe `report.html` e `remediation.html`;
8. exemplos de execução documental não usam domínio corporativo de smoke;
9. suíte determinística permanece verde;
10. diff final não contém workflow temporário nem secrets.

## Stable Local Baseline

Critérios:

- recebe domínio ou URL_SET explícito;
- descobre/processa URLs conforme o modo de entrada;
- respeita max_pages;
- Desktop/Mobile;
- RAW/rendered/visual;
- SPA/non-SPA;
- evidence;
- rules;
- findings;
- IA opcional;
- coverage/confidence;
- scoring;
- prioritization;
- `report.html` orientado a página;
- `remediation.html` orientado a problema;
- limitações explícitas;
- testes críticos.

Após M15, a baseline de reporting possui duas projeções complementares do mesmo estado persistido.

Git/GitHub já são utilizados a partir do M0 para controle de versão e repositório de desenvolvimento. A adoção antecipada de Git/GitHub é uma decisão de processo de desenvolvimento e não torna GitHub dependência de execução do produto.

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

A exclusão física das branches não bloqueia o avanço quando os controles de D-036 forem satisfeitos. Quando o humano solicitar exclusão manual, a automação não deve excluir a branch.

A lista acumulada de branches encerradas deve ser apresentada ao humano ao final para exclusão manual.

A execução deve interromper diante dos blockers reais definidos em D-034 ou em outra decisão normativa aplicável. Problemas técnicos ordinários e solucionáveis devem ser diagnosticados, corrigidos, revalidados e não constituem, por si só, motivo para solicitar aprovação humana.

Nenhum marco pode ser declarado concluído apenas para permitir avanço, e nenhum escopo do marco seguinte deve ser antecipado materialmente antes do encerramento do marco atual, salvo infraestrutura estritamente necessária e já permitida pela especificação.
