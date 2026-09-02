# DOMAIN_MODEL.md

**Status:** APPROVED

## 1. Objetivo

Definir entidades, relacionamentos e invariantes do SearchGEO Readiness Auditor sem acoplar o domínio a banco, ORM ou framework.

## 2. Modelo principal

Audit
├── AuditTarget
├── Page
│   ├── PageSnapshot [DESKTOP]
│   │   ├── Evidence
│   │   ├── EntityObservation
│   │   └── SemanticAssessment
│   └── PageSnapshot [MOBILE]
│       ├── Evidence
│       ├── EntityObservation
│       └── SemanticAssessment
├── RuleExecution
│   ├── Rule
│   ├── Evidence
│   └── Finding
├── Score
│   └── ScoreContribution
├── Recommendation
│   └── RemediationGroup
└── Report

## 3. Identificadores

- Audit: `AUD-*`
- AuditTarget: `TGT-*`
- Page: `PGE-*`
- PageSnapshot: `SNP-*`
- Evidence: `EV-GEO-*`
- Rule: `BR-GEO-*`
- RuleExecution: `REX-*`
- Finding: `FND-*`
- Score: `SCR-*`
- ScoreContribution: `SCON-*`
- Recommendation: `REC-*`
- EntityObservation: `ENT-*`
- SemanticAssessment: `SMA-*`
- Report: `RPT-*`
- RemediationGroup: `RMG-*`

## 4. Audit

Campos conceituais:

- audit_id;
- project_name;
- status;
- completion_status;
- primary_language;
- market;
- max_pages;
- audit_mode;
- capabilities;
- limitations;
- created_at;
- started_at;
- completed_at;
- auditor_version;
- ruleset_version.

Status:

- CREATED
- INITIALIZING
- DISCOVERING
- ACQUIRING
- ANALYZING
- COMPARING
- SCORING
- RECOMMENDING
- REPORTING
- COMPLETED
- FAILED
- CANCELLED

Completion:

- COMPLETE
- COMPLETE_WITH_LIMITATIONS

## 5. AuditTarget

Campos:

- target_id;
- audit_id;
- input_url;
- normalized_origin;
- target_type.

Tipos:

- DOMAIN
- URL
- URL_SET

## 6. Page

Representa a identidade lógica da URL.

Campos:

- page_id;
- audit_id;
- normalized_url;
- discovered_url;
- discovery_sources;
- depth.

Discovery sources:

- SEED
- SITEMAP
- INTERNAL_LINK
- REDIRECT
- MANUAL

## 7. DeviceContext

- DESKTOP
- MOBILE

Para findings:

- DESKTOP
- MOBILE
- BOTH
- NOT_APPLICABLE

Para comparação:

- SAME
- DIFFERENT
- NOT_APPLICABLE
- UNKNOWN

## 8. PageSnapshot

Representa uma observação da página em um dispositivo.

Campos conceituais:

- snapshot_id;
- page_id;
- device;
- requested_url;
- final_url;
- captured_at;
- http_status;
- content_type;
- title;
- description;
- canonical;
- meta_robots;
- rendering_mode;
- raw_artifact_ref;
- rendered_artifact_ref;
- main_content_ref;
- structured_data_ref;
- browser_metadata;
- architecture_classification.

Architecture classification:

- STATIC_OR_SSR
- HYDRATED
- CSR_SPA
- MIXED
- UNKNOWN

A classificação é diagnóstica e não afeta score por si só.

## 9. Evidence

Entidade de primeira classe.

Campos:

- evidence_id;
- audit_id;
- page_id;
- snapshot_id;
- device;
- evidence_type;
- source;
- observed_value;
- artifact_reference;
- captured_at.

Tipos possíveis:

- HTTP_RESPONSE
- HTTP_HEADER
- ROBOTS_RULE
- SITEMAP_ENTRY
- HTML_ELEMENT
- DOM_ELEMENT
- META_TAG
- CANONICAL
- HEADING
- LINK
- STRUCTURED_DATA
- MAIN_CONTENT
- TEXT_EXCERPT
- AI_ANALYSIS
- COMPARISON

## 10. Rule

Definição versionada.

Campos:

- rule_id;
- version;
- name;
- category;
- dimension;
- execution_type;
- device_scope;
- architecture_scope;
- engine_scope;
- basis_type;
- dependencies;
- scoring_metadata;
- enabled.

Execution type:

- DETERMINISTIC
- SEMANTIC
- HYBRID

Basis:

- OFFICIAL
- STANDARD
- HEURISTIC
- EXPERIMENTAL

## 11. Check

Check é a menor observação/validação utilizada por uma Business Rule.

Não precisa necessariamente ser entidade persistida.

Fluxo:

Evidence
→ Check
→ Business Rule
→ RuleExecution
→ Finding

## 12. RuleExecution

Campos:

- rule_execution_id;
- audit_id;
- rule_id;
- rule_version;
- page_id;
- snapshot_id;
- device;
- result;
- observed_value;
- expected_condition;
- evidence_ids;
- executed_at;
- error.

Resultados:

- PASS
- FAIL
- WARNING
- NOT_APPLICABLE
- UNKNOWN
- ERROR

## 13. Finding

Campos:

- finding_id;
- audit_id;
- rule_id;
- rule_execution_id;
- page_id;
- device;
- category;
- severity;
- source;
- title;
- observed_value;
- expected_condition;
- evidence_ids;
- status.

Severity:

- CRITICAL
- HIGH
- MEDIUM
- LOW
- INFO

## 14. EntityObservation

Campos:

- entity_observation_id;
- snapshot_id;
- name;
- entity_type;
- confidence;
- evidence_ids.

Tipos:

- ORGANIZATION
- PERSON
- PRODUCT
- SERVICE
- PLACE
- BRAND
- TOPIC
- OTHER

## 15. SemanticAssessment

Campos:

- assessment_id;
- snapshot_id;
- assessment_type;
- result;
- confidence;
- evidence_ids;
- prompt_id;
- prompt_version;
- provider;
- model;
- configuration_version;
- reasoning_summary.

## 16. Score

Campos:

- score_id;
- audit_id;
- dimension;
- device;
- value;
- coverage;
- confidence;
- consolidation_status;
- scoring_version;
- calculated_at;
- limitations.

Confidence:

- HIGH
- MEDIUM
- LOW
- UNAVAILABLE

Consolidation:

- CONSOLIDATED
- PARTIAL
- NOT_CONSOLIDATED

## 17. ScoreContribution

Registra contribuição de regra para score.

Campos:

- contribution_id;
- score_id;
- rule_id;
- rule_execution_id;
- dimension;
- device;
- weight;
- result;
- result_factor;
- effective_contribution;
- scoring_group.

## 18. Recommendation

Campos:

- recommendation_id;
- audit_id;
- finding_id ou remediation_group_id;
- device;
- title;
- description;
- impact;
- effort;
- confidence;
- priority_score;
- priority_class;
- status.

## 19. RemediationGroup

Agrupa findings relacionados à mesma causa.

Campos:

- group_id;
- rule_id;
- root_cause;
- affected_findings;
- affected_pages;
- devices;
- severity;
- impact;
- confidence;
- effort;
- priority_score;
- priority_class.

## 20. Report

Campos:

- report_id;
- audit_id;
- format;
- status;
- generated_at;
- template_version;
- auditor_version;
- file_path.

O Report nunca é fonte primária dos dados.

## 21. Invariantes

1. Todo PageSnapshot pertence a uma Page.
2. Todo PageSnapshot possui DeviceContext.
3. Todo finding válido possui evidência.
4. Nenhum LLM calcula diretamente score oficial.
5. Todo score registra scoring_version.
6. Toda RuleExecution registra rule_version.
7. Recommendation deve ser rastreável a finding ou remediation group.
8. Desktop e Mobile não podem sobrescrever um ao outro.
9. Report não é fonte primária.
10. UNKNOWN não equivale a FAIL.
11. ERROR não equivale a FAIL.
12. NOT_APPLICABLE não equivale a FAIL.
13. Ausência de IA é limitação da auditoria.
14. Finding sem evidência não pode ser publicado.
