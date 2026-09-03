# SearchGEO Readiness Auditor — Specification Index

**Status:** APPROVED BASELINE + M14/M15/M16/M17/M18 + SCORE-GEO-002 EVOLUTIONS  
**Baseline:** MVP Functional Specification  
**Idioma normativo:** Português, preservando identificadores e termos técnicos quando necessário.

## 1. Objetivo

Este diretório constitui a fonte normativa do SearchGEO Readiness Auditor.

Uma IA, desenvolvedor ou ferramenta que assuma o projeto não deve depender do histórico de chats para descobrir requisitos já formalizados.

Os documentos presentes neste diretório prevalecem sobre interpretações informais do histórico de conversa.

## 2. Ordem obrigatória de leitura

1. `00_SPEC_INDEX.md`
2. `12_AI_HANDOFF.md`
3. `10_DECISIONS.md`
4. `01_PROJECT_CHARTER_SCOPE.md`
5. `07_FUNCTIONAL_REQUIREMENTS.md`
6. `02_DOMAIN_MODEL.md`
7. `03_BUSINESS_RULES.md`
8. `04_WORKFLOWS.md`
9. `05_SCORING_MODEL.md`
10. `06_PRIORITIZATION_MODEL.md`
11. `08_TECHNICAL_ARCHITECTURE.md`
12. `09_IMPLEMENTATION_PLAN.md`
13. `11_REPORTING_LANGUAGE_GLOSSARY.md`
14. `13_MODEL_ROUTING_POLICY.md`
15. `14_MULTI_URL_VISUAL_EVIDENCE_REMEDIATION.md`
16. `15_ERROR_CENTRIC_REPORT_UX.md`
17. `16_ROOT_CAUSE_ELEMENT_REMEDIATION.md`
18. `17_REMEDIATION_PRECISION_REPORT_CONSISTENCY.md`
19. `18_MULTI_AI_PROVIDER_ROUTING.md`
20. `19_SCORE_APPLICABILITY_GEO_MINIMUMS.md`

## 3. Precedência documental

Em caso de conflito:

1. decisões explicitamente aprovadas em `10_DECISIONS.md`;
2. requisitos funcionais em `07_FUNCTIONAL_REQUIREMENTS.md`;
3. escopo em `01_PROJECT_CHARTER_SCOPE.md`;
4. modelos normativos de domínio, regras, workflows, scoring e priorização;
5. arquitetura técnica;
6. plano de implementação;
7. AI handoff e política operacional de modelos;
8. especificações de evolução de marco, quando não conflitarem com os itens anteriores.

Nenhuma decisão funcional deve ser alterada silenciosamente durante implementação.

## 4. Documentos

### `01_PROJECT_CHARTER_SCOPE.md`
Define propósito, escopo, princípios, MVP, exclusões e critérios de aceite.

### `02_DOMAIN_MODEL.md`
Define entidades, relacionamentos, identificadores, estados e invariantes.

### `03_BUSINESS_RULES.md`
Define as 54 Business Rules `BR-GEO-001` a `BR-GEO-054`.

### `04_WORKFLOWS.md`
Define `WF-GEO-001` a `WF-GEO-012` e a ordem de execução.

### `05_SCORING_MODEL.md`
Define Score, Coverage, Confidence, Consolidation Status, aplicabilidade de dimensão e agregações. Baseline vigente: `SCORE-GEO-002`.

### `06_PRIORITIZATION_MODEL.md`
Define Severity, Impact, Effort, Confidence e Priority.

### `07_FUNCTIONAL_REQUIREMENTS.md`
Define requisitos `FR-GEO-*` e `NFR-GEO-*`.

### `08_TECHNICAL_ARCHITECTURE.md`
Define a arquitetura local, modular e sem serviços obrigatórios.

### `09_IMPLEMENTATION_PLAN.md`
Define a baseline de marcos e suas evoluções formalizadas.

### `10_DECISIONS.md`
Registra decisões humanas consolidadas e pendências corporativas. D-037 formaliza `SCORE-GEO-002`.

### `11_REPORTING_LANGUAGE_GLOSSARY.md`
Define linguagem e apresentação do relatório HTML.

### `12_AI_HANDOFF.md`
Instrui qualquer IA que passe a trabalhar no projeto.

### `13_MODEL_ROUTING_POLICY.md`
Define qual classe de IA/modelo deve ser usada de acordo com esforço e criticidade.

### `14_MULTI_URL_VISUAL_EVIDENCE_REMEDIATION.md`
Define a evolução M14: auditoria explícita multi-URL em um único `audit_id`, recursos de domínio, screenshots, `ElementObservation`, actionability, referências técnicas e a distinção obrigatória entre zero calculado e ausência de cálculo.

### `15_ERROR_CENTRIC_REPORT_UX.md`
Define a evolução M15: segundo HTML orientado a problema (`remediation.html`), separação global versus página, navegação lateral por path, refinamento tipográfico, guia das dez dimensões do Score GEO e interpretação consolidada ao fim do relatório.

### `16_ROOT_CAUSE_ELEMENT_REMEDIATION.md`
Define a evolução M16: causa raiz evidence-backed por finding, classificação de precisão da localização, mapeamento de elemento(s)/selector quando comprovável, observado versus esperado, mudança exata, critérios de aceite e revalidação em `report.html` e `remediation.html`.

### `17_REMEDIATION_PRECISION_REPORT_CONSISTENCY.md`
Define a evolução M17: reason code específico, separação entre elemento/selector observado e alvo técnico, semântica coerente de actionability/prioridade/IA, redução de duplicação e diagnóstico de integridade RuleExecution → Finding.

### `18_MULTI_AI_PROVIDER_ROUTING.md`
Define M18: multi-provider, roteamento determinístico, failover, quarantine por audit, URL lock e telemetria de uso/custo de IA. M18 não altera scoring.

### `19_SCORE_APPLICABILITY_GEO_MINIMUMS.md`
Define `SCORE-GEO-002`, separando `NOT_APPLICABLE` legítimo de `NOT_CONSOLIDATED`, formalizando JSON-LD como reforço opcional e documentando premissas mínimas/contextuais de GEO.

## 5. Regra de mudança

Mudanças que afetem:

- escopo;
- Business Rules;
- scoring;
- priorização;
- interpretação do relatório;
- requisitos corporativos;

devem ser registradas como decisão explícita antes de alterar a baseline.

Decisões puramente internas de implementação podem ser tomadas sem aprovação humana quando não alterarem comportamento funcional.

## M18 — Multi-AI Provider Abstraction, Reliability Routing & Usage Telemetry
Fonte normativa específica: `18_MULTI_AI_PROVIDER_ROUTING.md`. M18 é extensão de infraestrutura; não altera Business Rules, PRIORITY-GEO-001, actionability, Desktop/Mobile nem a semântica de UNKNOWN.

## SCORE-GEO-002 — Aplicabilidade e premissas mínimas GEO
Fonte normativa específica: `19_SCORE_APPLICABILITY_GEO_MINIMUMS.md`. Mantém as dez dimensões, mas dimensões integralmente e legitimamente `NOT_APPLICABLE` não bloqueiam nem reduzem o Overall.
