# SCORING_GUIDE.md

Guia operacional do baseline `SCORE-GEO-002`.

## Princípio

Score, Coverage, Confidence e Consolidation são métricas diferentes. Nenhuma deve ser usada como sinônimo da outra.

O modelo é interno ao SearchGEO e reprodutível a partir das RuleExecutions persistidas. Não é um score oficial de Google, OpenAI ou outro mantenedor.

## Dimensões

1. `TECHNICAL_ACCESSIBILITY`
2. `INDEXABILITY`
3. `CONTENT_EXTRACTABILITY`
4. `SEMANTIC_STRUCTURE`
5. `ENTITY_CLARITY`
6. `STRUCTURED_DATA`
7. `ANSWERABILITY`
8. `CITATION_READINESS`
9. `EVIDENCE_TRUST`
10. `INTENT_COVERAGE`

O modelo conceitual mantém Desktop e Mobile separados. A CLI pode executar somente o dispositivo selecionado; o report site mostra apenas os contextos realmente auditados.

## RuleResult

```text
PASS
WARNING
FAIL
UNKNOWN
ERROR
NOT_APPLICABLE
```

Somente `PASS`, `WARNING` e `FAIL` participam do denominador do Score.

`UNKNOWN` e `ERROR` reduzem capacidade de avaliação/Coverage; não são FAIL.

`NOT_APPLICABLE` sai do universo aplicável quando legítimo.

## Fatores

Baseline:

```text
PASS    = 1.00
WARNING = 0.50
FAIL    = 0.00
```

O `warning_factor` pode ser específico por regra e deve permanecer versionado.

## Fórmula da dimensão

```text
Σ(weight × result_factor)
------------------------- × 100
Σ(weight evaluated)
```

## Coverage

```text
evaluated applicable weight
---------------------------
total applicable weight
```

`evaluated`:

```text
PASS
WARNING
FAIL
```

`applicable`:

```text
PASS
WARNING
FAIL
UNKNOWN
ERROR
```

`NOT_APPLICABLE` fica fora.

### Interpretação

Coverage baixa significa que parte relevante do universo aplicável não pôde ser avaliada. Ela **não significa baixa qualidade do website**.

## Confidence

Estados:

```text
HIGH
MEDIUM
LOW
UNAVAILABLE
```

No algoritmo atual:

- `HIGH`: Coverage >= 90%, evidência completa e nenhum erro;
- `MEDIUM`: Coverage >= 80% e nenhum erro;
- `LOW`: existe alguma avaliação, mas os critérios acima não foram satisfeitos;
- `UNAVAILABLE`: Coverage <= 0.

### O que Confidence significa

Confidence mede **a força da conclusão do auditor**.

**Confidence LOW não significa que o conteúdo textual está “ruim”, “não aderente a GEO” ou que deve ser reescrito.**

Exemplo:

```text
Score: 90/100
Coverage: 55%
Confidence: LOW
```

Interpretação: as regras que puderam ser avaliadas tiveram resultado alto, mas a conclusão geral é fraca porque a cobertura é limitada.

Uma recomendação de alteração de conteúdo deve vir de um finding/RuleExecution evidence-backed, especialmente regras semânticas aplicáveis; nunca apenas do estado `LOW`.

A confidence devolvida por um LLM em uma avaliação individual também não é automaticamente a Confidence final do auditor.

## Consolidation

Baseline:

```text
NOT_CONSOLIDATED: Confidence UNAVAILABLE ou Coverage < 0,50
CONSOLIDATED:     Coverage >= 0,80 e Confidence HIGH/MEDIUM
PARTIAL:          demais estados avaliáveis
NOT_APPLICABLE:   dimensão integralmente e legitimamente fora do universo aplicável
```

Uma dimensão com pré-requisito bloqueado não deve ser promovida a `NOT_APPLICABLE` benigno.

## Sem RuleExecution

Se nenhuma execução da dimensão existe para o dispositivo:

```text
Value = null
Coverage = 0
Confidence = UNAVAILABLE
Consolidation = NOT_CONSOLIDATED
limitation = NO_RULE_EXECUTIONS
```

## Dimensão legitimamente não aplicável

Quando todas as execuções são legitimamente `NOT_APPLICABLE`:

```text
Value = null
Coverage = 0 na dimensão isolada
Confidence = UNAVAILABLE
Consolidation = NOT_APPLICABLE
limitation = NO_APPLICABLE_RULES
```

A dimensão não recebe 0 nem 100 e é excluída do Overall.

## Pré-requisito bloqueado

Reason codes com `PREREQUISITE_BLOCKED` mantêm:

```text
Value = null
Consolidation = NOT_CONSOLIDATED
limitation = APPLICABILITY_UNRESOLVED:PREREQUISITE_BLOCKED
```

## Double counting

Regras correlacionadas usam `scoring_group`. Baseline:

```text
MAX_IMPACT
```

Isso evita somar várias vezes o mesmo problema causal dentro do mesmo escopo.

## Overall

`OVERALL_READINESS` é calculado separadamente por dispositivo.

Processo:

1. materializar as dez dimensões no modelo;
2. excluir somente dimensões `NOT_APPLICABLE` legítimas;
3. exigir Value e estado diferente de `NOT_CONSOLIDATED` para as dimensões aplicáveis;
4. calcular média simples dos Values aplicáveis;
5. calcular Coverage como média das coverages aplicáveis;
6. usar a menor Confidence entre as dimensões aplicáveis;
7. persistir limitações de aplicabilidade/consolidação.

Se uma dimensão aplicável necessária está `NOT_CONSOLIDATED`, o Overall não é publicado como consolidado.

## Structured Data

JSON-LD não é requisito universal para um Overall calculável.

Quando Structured Data está ausente e `BR-GEO-034..037` são legitimamente não aplicáveis:

- `STRUCTURED_DATA = NOT_APPLICABLE`;
- a dimensão fica fora do Overall;
- ausência isolada não recebe penalização.

Quando Structured Data existe, a dimensão volta ao universo aplicável e sua qualidade pode influenciar o resultado.

Esse comportamento também evita transformar Structured Data em requisito artificial para recursos generativos, em desacordo com a documentação oficial atual do Google.

## Sem IA

Ausência de IA:

- pode reduzir Coverage;
- pode reduzir Confidence/Consolidation;
- não atribui qualidade baixa ao website;
- não converte regra semantic-only automaticamente em FAIL.

## Dispositivo selecionado

Default CLI:

```text
mobile
```

Opções:

```text
mobile
desktop
both
```

Somente snapshots selecionados entram em M7. Isso reduz custo de IA quando apenas Mobile é necessário.

O engine ainda mantém o modelo conceitual de dimensões por dispositivo; o report site evita exibir um contexto não auditado como se fosse resultado válido.

## Classificação visual

A UI atual usa thresholds internos para comunicação de um Score consolidado:

```text
>= 90  Excelente
>= 75  Alta
>= 60  Moderada
>= 40  Baixa
<  40  Crítica
```

Essas faixas **não são padrão oficial GEO/AEO**. Alterá-las é decisão de produto/calibração do SearchGEO e não mudança em documentação externa.

## Critical blockers

Blockers críticos são mostrados separadamente. Um score alto não deve ocultar um blocker comprovado.

## Reprodutibilidade

Persistidos:

- `Score`;
- `ScoreContribution`;
- `rule_execution_id`;
- `rule_id` e versão;
- pesos/fatores/grupos;
- limitations;
- `scoring_version = SCORE-GEO-002`.

`BR-GEO-054` verifica reprodutibilidade sem reexecutar website ou IA.

O HTML apenas exibe a projeção; a reprodutibilidade está em `audit.db`.
