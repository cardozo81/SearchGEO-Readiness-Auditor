# Guia de Scoring e Reliability

A Stable Local Baseline usa o engine versionado `SCORE-GEO-001`. O LLM não calcula o score oficial.

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

Na implementação atual:

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

A implementação de `SCORE-GEO-001` não atribui dimensão de qualidade diretamente a `BR-GEO-001`, `002`, `004`, `052`, `053` e `054`, pois são principalmente integridade/aquisição bookkeeping/comparação/reprodutibilidade.

## Coverage

Para cada dimensão:

```text
Coverage = peso avaliado / peso aplicável
```

- `NOT_APPLICABLE` não adiciona peso aplicável;
- `UNKNOWN`/`ERROR` adicionam universo aplicável, mas não peso avaliado;
- `PASS`/`WARNING`/`FAIL` contam como avaliados.

Coverage é arredondada e persistida em escala 0..1.

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

```text
NOT_CONSOLIDATED: Confidence UNAVAILABLE ou Coverage < 0,50
CONSOLIDATED:     Coverage >= 0,80 e Confidence HIGH/MEDIUM
PARTIAL:          demais estados com alguma base útil
```

## Overall

Para cada device, `OVERALL_READINESS` só possui valor quando:

- existem exatamente as 10 dimensões esperadas;
- nenhuma delas está `NOT_CONSOLIDATED`;
- todas possuem valor.

Quando o gate é satisfeito:

```text
Overall = média simples dos valores das 10 dimensões
```

As dimensões têm peso igual no Overall da Stable Local Baseline.

A Coverage do Overall é a média das Coverages das 10 dimensões. A Confidence do Overall é a menor Confidence entre as dimensões.

## UNKNOWN, ERROR e NOT_APPLICABLE

Esses estados foram desenhados para evitar falso score:

- `UNKNOWN`: não foi possível concluir com evidência/capacidade disponível;
- `ERROR`: o auditor falhou ao executar aquela análise;
- `NOT_APPLICABLE`: regra fora do contexto ou bloqueada por dependência.

Nenhum dos três equivale a `FAIL`.

## Ausência de IA

Quando IA não está configurada:

- checks determinísticos continuam;
- semantic-only pode ficar `UNKNOWN`;
- Coverage e, por consequência, Confidence/Consolidation podem diminuir;
- a qualidade do site **não recebe fator zero** por ausência do provider.

Essa distinção é central: ausência de capacidade de análise não é ausência de qualidade do website.

## Reprodutibilidade

`BR-GEO-054` exige score reconstruível. A implementação persiste:

- `scoring_version = SCORE-GEO-001`;
- Score;
- ScoreContribution;
- `rule_execution_id`;
- `rule_id` e rule version na RuleExecution;
- fatores, pesos e grupos efetivos.

O `report.html` exibe os resultados, mas a reprodutibilidade está nos dados persistidos.
