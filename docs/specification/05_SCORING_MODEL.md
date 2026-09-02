# SCORING_MODEL.md

**Status:** APPROVED  
**Scoring baseline:** SCORE-GEO-001

## 1. Estrutura

Todo resultado de score possui:

- Value;
- Coverage;
- Confidence;
- Consolidation Status;
- Contributions;
- Limitations;
- Scoring Version.

## 2. Dimensões

1. Acessibilidade Técnica
2. Capacidade de Indexação
3. Extração de Conteúdo
4. Estrutura Semântica
5. Clareza de Entidades
6. Dados Estruturados
7. Capacidade de Resposta
8. Preparação para Citação
9. Evidências e Confiabilidade
10. Cobertura de Intenções

Desktop e Mobile separados.

## 3. RuleExecution

PASS = avaliado positivamente  
WARNING = avaliado com perda parcial  
FAIL = problema comprovado  
UNKNOWN = insuficiente para concluir  
ERROR = auditor não conseguiu executar  
NOT_APPLICABLE = regra fora do universo aplicável

UNKNOWN, ERROR e NOT_APPLICABLE não são FAIL.

## 4. Fatores

Baseline:

PASS = 1.00  
WARNING = 0.50 por padrão  
FAIL = 0.00

warning_factor pode ser sobrescrito por regra e é versionado.

## 5. Fórmula

Dimension Score:

Σ(weight × result_factor)
/
Σ(weight evaluated)
× 100

Apenas PASS, WARNING e FAIL participam do denominador do score.

## 6. Coverage

Coverage:

evaluated applicable weight
/
total applicable weight

Evaluated:

- PASS
- WARNING
- FAIL

Applicable:

- PASS
- WARNING
- FAIL
- UNKNOWN
- ERROR

NOT_APPLICABLE fica fora.

## 7. Confidence

Níveis:

- HIGH
- MEDIUM
- LOW
- UNAVAILABLE

Considerar:

- evidence quality;
- analysis method;
- execution reliability;
- coverage;
- contradictions;
- limitations.

Confidence do LLM não é automaticamente a confidence final do auditor.

## 8. Consolidation

Baseline:

Coverage >= 80% e Confidence HIGH/MEDIUM
→ CONSOLIDATED

Coverage 50–79%
→ PARTIAL

Coverage >= 80% mas Confidence LOW
→ PARTIAL ou NOT_CONSOLIDATED conforme dimensão

Coverage < 50%
→ NOT_CONSOLIDATED

Confidence UNAVAILABLE
→ NOT_CONSOLIDATED

## 9. Sem IA

Ausência de IA:

- reduz coverage;
- pode reduzir consolidation;
- não reduz qualidade atribuída ao website.

Resultados semânticos sem capacidade suficiente ficam UNKNOWN.

## 10. ScoreContribution

Toda contribuição registra:

- score_id;
- rule_id;
- rule_execution_id;
- dimension;
- device;
- weight;
- result;
- factor;
- effective contribution;
- scoring_group.

## 11. Double Counting

Regras correlacionadas utilizam `scoring_group`.

Políticas suportadas conceitualmente:

- MAX_IMPACT
- SUM
- FIRST_FAILURE
- EXCLUSIVE

Baseline para regras correlacionadas:

MAX_IMPACT

## 12. Cascading Failures

Falha de pré-requisito não pode multiplicar penalizações.

## 13. Site-level rules

Regras globais como robots/sitemap não devem ser replicadas artificialmente por página.

## 14. Aggregation

No MVP:

- páginas possuem peso equivalente;
- não existe page importance subjetiva.

## 15. Overall

Existem:

- Overall Readiness — Desktop
- Overall Readiness — Mobile

Nunca uma única nota misturando dispositivos.

Overall exige consolidação suficiente das 10 dimensões.

Se uma dimensão necessária estiver NOT_CONSOLIDATED:

Overall = NOT_CONSOLIDATED

## 16. Technical Readiness

Pode resumir:

- Technical Accessibility;
- Indexability;
- Content Extractability;
- Structured Data.

Somente se suficientemente consolidadas.

## 17. Semantic Readiness

Pode resumir:

- Semantic Structure;
- Entity Clarity;
- Answerability;
- Citation Readiness;
- Evidence & Trust;
- Intent Coverage.

## 18. Pesos entre dimensões

MVP:

equal weight

Não inventar pesos “científicos” antes de calibração empírica.

## 19. Blockers

Critical blockers são mostrados separadamente.

Um score relativamente alto não pode esconder um blocker crítico.

## 20. Reprodutibilidade

Dadas:

- evidências;
- RuleExecutions;
- rule versions;
- scoring version;

o score deve poder ser recalculado sem reexecutar website ou IA.
