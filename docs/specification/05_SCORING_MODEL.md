# SCORING_MODEL.md

**Status:** APPROVED  
**Scoring baseline:** SCORE-GEO-002

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

As dez dimensões continuam pertencendo ao modelo. `SCORE-GEO-002` apenas distingue dimensão legitimamente não aplicável de dimensão que deveria ser avaliada mas não consolidou.

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

## 7. Aplicabilidade da dimensão

`SCORE-GEO-002` adiciona distinção explícita entre aplicabilidade e consolidação.

### 7.1 Sem RuleExecution

Se nenhuma RuleExecution da dimensão existir para o dispositivo:

- Value = null;
- Coverage = 0;
- Confidence = UNAVAILABLE;
- Consolidation = NOT_CONSOLIDATED;
- limitation = `NO_RULE_EXECUTIONS`.

Ausência de execução não pode ser convertida em `NOT_APPLICABLE`.

### 7.2 Todas as regras legitimamente NOT_APPLICABLE

Se RuleExecutions existem e todas as regras da dimensão estão legitimamente fora do universo aplicável:

- Value = null;
- Coverage = 0 na dimensão isolada;
- Confidence = UNAVAILABLE;
- Consolidation = NOT_APPLICABLE;
- limitation = `NO_APPLICABLE_RULES`.

A dimensão não recebe 0 nem 100 e é excluída da agregação Overall.

### 7.3 Pré-requisito bloqueado

Se `NOT_APPLICABLE` ocorreu porque um pré-requisito impediu a análise, isso não é não aplicabilidade benigna.

Reason codes contendo `PREREQUISITE_BLOCKED` mantêm a dimensão:

- Value = null;
- Consolidation = NOT_CONSOLIDATED;
- limitation = `APPLICABILITY_UNRESOLVED:PREREQUISITE_BLOCKED`.

Isso evita esconder falhas de aquisição/rendering como se a dimensão simplesmente não se aplicasse.

## 8. Confidence

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

## 9. Consolidation

Baseline para dimensões aplicáveis:

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

Dimensão integralmente não aplicável:

→ NOT_APPLICABLE

## 10. Sem IA

Ausência de IA:

- reduz coverage;
- pode reduzir consolidation;
- não reduz qualidade atribuída ao website.

Resultados semânticos sem capacidade suficiente ficam UNKNOWN.

## 11. ScoreContribution

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

## 12. Double Counting

Regras correlacionadas utilizam `scoring_group`.

Políticas suportadas conceitualmente:

- MAX_IMPACT
- SUM
- FIRST_FAILURE
- EXCLUSIVE

Baseline para regras correlacionadas:

MAX_IMPACT

## 13. Cascading Failures

Falha de pré-requisito não pode multiplicar penalizações e também não pode ser usada para remover artificialmente uma dimensão do universo aplicável.

## 14. Site-level rules

Regras globais como robots/sitemap não devem ser replicadas artificialmente por página.

## 15. Aggregation

No MVP:

- páginas possuem peso equivalente;
- não existe page importance subjetiva.

## 16. Overall

Existem:

- Overall Readiness — Desktop
- Overall Readiness — Mobile

Nunca uma única nota misturando dispositivos.

Overall exige materialização das dez dimensões e consolidação suficiente de todas as dimensões **aplicáveis**.

Fluxo:

1. materializar as dez dimensões;
2. excluir da agregação apenas dimensões `NOT_APPLICABLE` legítimas;
3. exigir Value e estado diferente de `NOT_CONSOLIDATED` para todas as dimensões restantes;
4. calcular média simples dos Values das dimensões aplicáveis;
5. calcular Overall Coverage pela média das coverages das dimensões aplicáveis;
6. persistir `DIMENSION_NOT_APPLICABLE:<DIMENSION>` para cada dimensão excluída.

Se uma dimensão aplicável necessária estiver NOT_CONSOLIDATED:

Overall = NOT_CONSOLIDATED

Uma dimensão `NOT_APPLICABLE` não reduz nota nem Coverage do Overall.

## 17. JSON-LD / Structured Data

JSON-LD não é requisito universal para Compatibilidade GEO calculável.

Quando Structured Data está ausente e `BR-GEO-034..037` são legitimamente `NOT_APPLICABLE`:

- `STRUCTURED_DATA = NOT_APPLICABLE`;
- a dimensão não participa do Overall;
- não há penalidade pela ausência isolada.

Quando Structured Data é observado:

- a dimensão torna-se aplicável;
- BR-GEO-034..037 entram normalmente no fluxo;
- PASS/WARNING/FAIL influenciam score;
- UNKNOWN/ERROR influenciam coverage/consolidation;
- markup inválido ou contraditório pode reduzir o Overall.

## 18. Technical Readiness

Pode resumir:

- Technical Accessibility;
- Indexability;
- Content Extractability;
- Structured Data quando aplicável.

Somente se suficientemente consolidadas.

## 19. Semantic Readiness

Pode resumir:

- Semantic Structure;
- Entity Clarity;
- Answerability;
- Citation Readiness;
- Evidence & Trust;
- Intent Coverage.

## 20. Pesos entre dimensões

MVP:

equal weight entre dimensões aplicáveis.

Não inventar pesos “científicos” antes de calibração empírica.

## 21. Blockers

Critical blockers são mostrados separadamente.

Um score relativamente alto não pode esconder um blocker crítico.

## 22. Reprodutibilidade

Dadas:

- evidências;
- RuleExecutions;
- rule versions;
- scoring version;

o score e a decisão de aplicabilidade devem poder ser recalculados sem reexecutar website ou IA.

`BR-GEO-054` deve registrar `SCORE-GEO-002`.
