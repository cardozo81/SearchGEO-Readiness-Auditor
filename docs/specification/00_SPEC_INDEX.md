# SearchGEO Readiness Auditor — Specification Index

**Status:** APPROVED BASELINE + M14/M15/M16/M17/M18 + SCORE-GEO-002 + REPORT-SITE-GEO-001  
**Baseline:** MVP Functional Specification  
**Idioma normativo:** Português, preservando identificadores e termos técnicos quando necessário.

## 1. Objetivo

Este diretório constitui a fonte normativa do SearchGEO Readiness Auditor.

Uma IA, desenvolvedor ou ferramenta que assuma o projeto não deve depender do histórico de chats para descobrir requisitos formalizados.

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
Propósito, escopo, princípios, exclusões e critérios de aceite.

### `02_DOMAIN_MODEL.md`
Entidades, relacionamentos, identificadores, estados e invariantes.

### `03_BUSINESS_RULES.md`
Business Rules `BR-GEO-001` a `BR-GEO-054`.

### `04_WORKFLOWS.md`
Workflows `WF-GEO-001` a `WF-GEO-012` e ordem de execução.

### `05_SCORING_MODEL.md`
Score, Coverage, Confidence, Consolidation, aplicabilidade e agregações. Baseline vigente: `SCORE-GEO-002`. Confidence representa força da conclusão, não qualidade textual isolada.

### `06_PRIORITIZATION_MODEL.md`
Severity, Impact, Effort, Confidence e Priority.

### `07_FUNCTIONAL_REQUIREMENTS.md`
Requisitos `FR-GEO-*` e `NFR-GEO-*`. Inclui `FR-GEO-073..079` para device context e report site.

### `08_TECHNICAL_ARCHITECTURE.md`
Arquitetura local/modular, seleção de dispositivo e finalização do report site.

### `09_IMPLEMENTATION_PLAN.md`
Baseline de marcos e evoluções formalizadas. Quando descrição histórica de output conflitar com `FR-GEO-046`/REPORT-SITE-GEO-001, prevalece o contrato final `report/`.

### `10_DECISIONS.md`
Decisões humanas consolidadas e pendências corporativas. D-037 formaliza `SCORE-GEO-002`.

### `11_REPORTING_LANGUAGE_GLOSSARY.md`
Linguagem e apresentação do relatório.

### `12_AI_HANDOFF.md`
Instruções para continuidade por IA/desenvolvedor.

### `13_MODEL_ROUTING_POLICY.md`
Política de uso de modelos conforme esforço/criticidade.

### `14_MULTI_URL_VISUAL_EVIDENCE_REMEDIATION.md`
Evolução M14: multi-URL, recursos de domínio, screenshots, ElementObservation, actionability, referências e distinção entre zero calculado e ausência de cálculo.

### `15_ERROR_CENTRIC_REPORT_UX.md`
M15 histórico evoluído por `REPORT-SITE-GEO-001`: visão por domínio, páginas Mobile/Desktop, remediação, telemetria IA, referências, menu compartilhado e CSS externo.

### `16_ROOT_CAUSE_ELEMENT_REMEDIATION.md`
M16: causa raiz evidence-backed, localização, observado versus esperado, mudança exata, aceite e revalidação.

### `17_REMEDIATION_PRECISION_REPORT_CONSISTENCY.md`
M17: reason code, observado versus alvo técnico, consistência e redução de duplicação.

### `18_MULTI_AI_PROVIDER_ROUTING.md`
M18: multi-provider, routing determinístico, failover, quarantine, URL lock e telemetria. Não altera scoring.

### `19_SCORE_APPLICABILITY_GEO_MINIMUMS.md`
`SCORE-GEO-002`, `NOT_APPLICABLE` versus `NOT_CONSOLIDATED`, JSON-LD opcional e premissas mínimas/contextuais.

## 5. REPORT-SITE-GEO-001

A evolução de apresentação está formalizada por `FR-GEO-046`, `FR-GEO-047`, `FR-GEO-063`, `FR-GEO-070` e `FR-GEO-073..079`, além de `08_TECHNICAL_ARCHITECTURE.md` e `15_ERROR_CENTRIC_REPORT_UX.md`.

Contrato público:

```text
<AUD-ID>/report/index.html
<AUD-ID>/report/mobile.html       # condicional
<AUD-ID>/report/desktop.html      # condicional
<AUD-ID>/report/remediation.html
<AUD-ID>/report/ai-usage.html
<AUD-ID>/report/references.html
<AUD-ID>/report/css/site.css
```

Default de dispositivo da CLI: `mobile`. `desktop` e `both` são seleções explícitas/parametrizáveis.

## 6. Fonte externa e heurística

O SearchGEO não deve representar seu score ou thresholds como standard GEO/AEO universal.

Referências primárias atuais incluem Google Search Central, OpenAI Help Center, Schema.org, WHATWG e IETF/RFC. O guia oficial do Google de 2026 para recursos generativos reforça fundamentos de SEO e não cria markup especial GEO/AEO obrigatório.

Heurísticas BR-GEO sem equivalente normativo devem permanecer identificadas como heurísticas/baseline interna.

## 7. Regra de mudança

Mudanças que afetem escopo, Business Rules, scoring, priorização, interpretação do relatório, device context público ou requisitos corporativos devem ser reconciliadas nesta baseline antes da conclusão do merge.

Decisões puramente internas de implementação podem ser tomadas sem aprovação humana quando não alterarem comportamento funcional.

## M18 — Multi-AI Provider Abstraction, Reliability Routing & Usage Telemetry

Fonte normativa específica: `18_MULTI_AI_PROVIDER_ROUTING.md`. M18 não altera Business Rules, PRIORITY-GEO-001, actionability nem semântica de UNKNOWN.

## SCORE-GEO-002 — Aplicabilidade e premissas mínimas GEO

Fonte normativa específica: `19_SCORE_APPLICABILITY_GEO_MINIMUMS.md`. Mantém as dez dimensões, mas dimensões integralmente e legitimamente `NOT_APPLICABLE` não bloqueiam nem reduzem o Overall.
