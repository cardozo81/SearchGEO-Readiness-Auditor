# SearchGEO Readiness Auditor — Specification Index

**Status:** APPROVED BASELINE + M14 EVOLUTION  
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

Define Score, Coverage, Confidence, Consolidation Status e agregações.

### `06_PRIORITIZATION_MODEL.md`

Define Severity, Impact, Effort, Confidence e Priority.

### `07_FUNCTIONAL_REQUIREMENTS.md`

Define requisitos `FR-GEO-*` e `NFR-GEO-*`.

### `08_TECHNICAL_ARCHITECTURE.md`

Define a arquitetura local, modular e sem serviços obrigatórios.

### `09_IMPLEMENTATION_PLAN.md`

Define M0 a M14.

### `10_DECISIONS.md`

Registra decisões humanas consolidadas e pendências corporativas.

### `11_REPORTING_LANGUAGE_GLOSSARY.md`

Define linguagem e apresentação do relatório HTML.

### `12_AI_HANDOFF.md`

Instrui qualquer IA que passe a trabalhar no projeto.

### `13_MODEL_ROUTING_POLICY.md`

Define qual classe de IA/modelo deve ser usada de acordo com esforço e criticidade.

### `14_MULTI_URL_VISUAL_EVIDENCE_REMEDIATION.md`

Define a evolução M14: auditoria explícita multi-URL em um único `audit_id`, recursos de domínio, screenshots, `ElementObservation`, actionability, referências técnicas e a distinção obrigatória entre zero calculado e ausência de cálculo.

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
