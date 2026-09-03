# Guia de Scoring e Reliability

A baseline vigente usa o engine versionado `SCORE-GEO-002`. O LLM não calcula o score oficial.

## 10 dimensões

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

As dez dimensões continuam pertencendo ao modelo. A diferença de `SCORE-GEO-002` é que uma dimensão pode estar legitimamente fora do universo aplicável sem ser confundida com uma falha de consolidação.

## Desktop e Mobile

O engine calcula cada dimensão separadamente para `DESKTOP` e `MOBILE`. RuleExecutions sem device explícito (site/global) são aplicadas a cada dispositivo quando a regra contribui para scoring.

Não existe mistura automática de Desktop e Mobile em um único valor anterior aos dois Overalls.

## ScoreContribution

A unidade persistida de contribuição registra:

- score e dimensão;
- device;
- rule_id;
- rule_execution_id;
- weight;
- result;
- result_factor;
- effective_contribution;
- scoring_group, quando houver.

Isso permite reconstruir o score a partir de RuleExecutions versionadas.

## Fatores de resultado

| Resultado | Fator de qualidade |
|---|---:|
| PASS | 1,0 |
| WARNING | 0,5 por default |
| FAIL | 0,0 |
| UNKNOWN | não entra no numerador/denominador de qualidade |
| ERROR | não entra no numerador/denominador de qualidade |
| NOT_APPLICABLE | removido do universo aplicável |

O fator de WARNING pertence ao metadata de scoring da regra e atualmente usa 0,5 como default.

## Fórmula de uma dimensão

Para os grupos efetivamente avaliados:

```text
Score = soma(weight * factor) / soma(weight avaliado) * 100
```

O valor é calculado somente quando existe peso avaliado.

### Exemplo compatível

Três contribuições independentes de peso 1 com `PASS`, `WARNING` e `FAIL`:

```text
(1*1,0 + 1*0,5 + 1*0,0) / 3 * 100 = 50
```

Esse exemplo não deve ser usado para regras que pertencem ao mesmo `scoring_group`, porque grupos correlacionados são consolidados antes da fórmula.

## Scoring groups e prevenção de dupla penalização

Regras correlacionadas usam grupos como `PAGE_ACCESS`, `REDIRECT`, `INDEX_DIRECTIVES`, `CANONICAL`, `JS_CONTENT`, `STRUCTURED_DATA_CONSISTENCY` etc.

Dentro do mesmo escopo página/global + scoring group:

- o peso aplicável é o maior peso das regras do bucket;
- se houver mais de uma execução avaliada, o representante é o de menor fator de qualidade — abordagem `MAX_IMPACT`;
- o grupo contribui uma vez.

Assim, uma mesma causa técnica não reduz o score repetidamente apenas porque várias regras correlacionadas a observam.

## Regras que não pontuam diretamente

A implementação não atribui dimensão de qualidade diretamente a `BR-GEO-001`, `002`, `004`, `052`, `053` e `054`, pois são principalmente integridade/aquisição bookkeeping/comparação/reprodutibilidade.

## Coverage

Para cada dimensão aplicável:

```text
Coverage = peso avaliado / peso aplicável
```

- `NOT_APPLICABLE` não adiciona peso aplicável;
- `UNKNOWN`/`ERROR` adicionam universo aplicável, mas não peso avaliado;
- `PASS`/`WARNING`/`FAIL` contam como avaliados.

Coverage é arredondada e persistida em escala 0..1.

## Aplicabilidade da dimensão

Há três situações distintas.

### 1. Dimensão sem RuleExecutions

```text
Value: null
Coverage: 0
Confidence: UNAVAILABLE
Consolidation: NOT_CONSOLIDATED
Limitation: NO_RULE_EXECUTIONS
```

Isso representa lacuna de execução/evidência e **bloqueia** o Overall.

### 2. Todas as regras legitimamente `NOT_APPLICABLE`

```text
Value: null
Coverage: 0 na dimensão isolada
Confidence: UNAVAILABLE
Consolidation: NOT_APPLICABLE
Limitation: NO_APPLICABLE_RULES
```

Essa dimensão:

- não recebe 0;
- não recebe 100;
- não reduz score;
- não reduz Coverage do Overall;
- não bloqueia Overall.

### 3. NOT_APPLICABLE porque um pré-requisito bloqueou a avaliação

Reason codes com `PREREQUISITE_BLOCKED` não são tratados como exclusão benigna.

```text
Consolidation: NOT_CONSOLIDATED
Limitation: APPLICABILITY_UNRESOLVED:PREREQUISITE_BLOCKED
```

Assim, uma falha de aquisição/rendering não pode desaparecer do gate de consolidação apenas porque as regras dependentes foram marcadas `NOT_APPLICABLE`.

## Confidence

Contrato atual:

```text
UNAVAILABLE: coverage <= 0
HIGH:        coverage >= 0,90 + evidência completa + 0 ERROR
MEDIUM:      coverage >= 0,80 + 0 ERROR
LOW:         demais casos com coverage > 0
```

Uma execução avaliada sem Evidence também impede `HIGH`.

## Consolidation

Para dimensões aplicáveis:

```text
NOT_CONSOLIDATED: Confidence UNAVAILABLE ou Coverage < 0,50
CONSOLIDATED:     Coverage >= 0,80 e Confidence HIGH/MEDIUM
PARTIAL:          demais estados com alguma base útil
```

Para dimensão integralmente fora do universo aplicável:

```text
NOT_APPLICABLE
```

## Overall

Para cada device, `OVERALL_READINESS` exige que as dez dimensões tenham sido materializadas.

Depois disso:

1. dimensões `NOT_APPLICABLE` legítimas são excluídas da agregação;
2. todas as dimensões restantes precisam ter `value` e não podem estar `NOT_CONSOLIDATED`;
3. o Overall é a média simples dos valores das dimensões aplicáveis;
4. Overall Coverage é a média das Coverages das dimensões aplicáveis;
5. Overall Confidence é a menor Confidence entre as dimensões aplicáveis;
6. dimensões excluídas ficam rastreáveis por `DIMENSION_NOT_APPLICABLE:<DIMENSION>`.

Exemplo:

```text
10 dimensões materializadas
9 aplicáveis e consolidadas
STRUCTURED_DATA = NOT_APPLICABLE

Overall = média das 9 dimensões aplicáveis
```

Isso não significa que Structured Data recebeu nota neutra. Significa apenas que ele ficou fora do denominador.

## JSON-LD / Structured Data

JSON-LD é `OPCIONAL / REFORÇO` no baseline geral de GEO.

### Sem JSON-LD

Se `BR-GEO-034..037` estiverem legitimamente `NOT_APPLICABLE`:

```text
STRUCTURED_DATA = NOT_APPLICABLE
```

A Compatibilidade GEO pode ser mensurável pelas outras dimensões aplicáveis.

### Com JSON-LD

Assim que Structured Data é observado:

- BR-GEO-034 avalia sintaxe/interpretabilidade;
- BR-GEO-035 avalia tipos/propriedades;
- BR-GEO-036 avalia coerência com conteúdo visível;
- BR-GEO-037 avalia coerência de entidades;
- `STRUCTURED_DATA` entra no Score GEO.

Portanto, adicionar markup inválido ou contraditório pode reduzir o resultado. Não se deve adicionar JSON-LD apenas para "destravar" uma nota.

Consulte `GEO_MINIMUM_REQUIREMENTS.md` para a matriz de requisitos mínimos, contextuais e opcionais.

## UNKNOWN, ERROR e NOT_APPLICABLE

Esses estados evitam falso score:

- `UNKNOWN`: não foi possível concluir com evidência/capacidade disponível;
- `ERROR`: o auditor falhou ao executar aquela análise;
- `NOT_APPLICABLE`: regra ou dimensão legitimamente fora do contexto.

Nenhum equivale a `FAIL`.

`NOT_APPLICABLE` por pré-requisito bloqueado não é tratado como dimensão legitimamente excluível.

## Ausência de IA

Quando IA não está configurada:

- checks determinísticos continuam;
- semantic-only pode ficar `UNKNOWN`;
- Coverage e, por consequência, Confidence/Consolidation podem diminuir;
- a qualidade do site **não recebe fator zero** por ausência do provider.

Essa distinção é central: ausência de capacidade de análise não é ausência de qualidade do website.

## Reprodutibilidade

`BR-GEO-054` exige score reconstruível. A implementação persiste:

- `scoring_version = SCORE-GEO-002`;
- Score;
- ScoreContribution;
- `rule_execution_id`;
- `rule_id` e rule version na RuleExecution;
- fatores, pesos e grupos efetivos;
- limitations de aplicabilidade/consolidação.

O `report.html` exibe os resultados, mas a reprodutibilidade está nos dados persistidos.
