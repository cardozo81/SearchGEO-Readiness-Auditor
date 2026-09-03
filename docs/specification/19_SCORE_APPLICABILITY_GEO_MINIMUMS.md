# SCORE-GEO-002 — Aplicabilidade de Dimensões e Premissas Mínimas GEO

**Status:** APPROVED  
**Scoring baseline:** `SCORE-GEO-002`  
**Supersede:** `SCORE-GEO-001` somente quanto à aplicabilidade/agregação de dimensões.

## 1. Motivação

`SCORE-GEO-001` tratava uma dimensão sem nenhuma regra aplicável como `NOT_CONSOLIDATED`. Isso confundia dois estados distintos:

1. o auditor não conseguiu avaliar uma dimensão que deveria ser avaliada;
2. a dimensão está legitimamente fora do universo aplicável daquela URL.

O caso mais evidente é Dados Estruturados. Quando não existe JSON-LD observado, `BR-GEO-034..037` podem ser `NOT_APPLICABLE`. A ausência de Structured Data não é, por si só, FAIL e não deve impedir a Compatibilidade GEO de ser calculada.

## 2. Princípio normativo

`NOT_APPLICABLE` não é falha, não é ausência de evidência e não é score zero.

Uma dimensão é:

- `APPLICABLE` quando existe pelo menos uma RuleExecution aplicável à dimensão;
- `NOT_APPLICABLE` quando RuleExecutions da dimensão existem e todas estão legitimamente `NOT_APPLICABLE`;
- `NOT_CONSOLIDATED` quando faltam RuleExecutions necessárias, a aplicabilidade não pôde ser resolvida, ou a cobertura/confiabilidade aplicável é insuficiente.

A ausência completa de RuleExecutions nunca deve ser interpretada como `NOT_APPLICABLE`.

## 3. Pré-requisito bloqueado não equivale a não aplicável

Se regras retornarem `NOT_APPLICABLE` apenas porque uma dependência técnica/conteúdo impediu a avaliação, a dimensão permanece `NOT_CONSOLIDATED`.

Exemplos de razão bloqueante:

- `SEMANTIC_PREREQUISITE_BLOCKED`;
- `CONTENT_EXTRACTION_PREREQUISITE_BLOCKED`;
- outros reason codes versionados contendo `PREREQUISITE_BLOCKED`.

Isso impede que uma falha de aquisição/rendering seja artificialmente convertida em exclusão benigna da dimensão.

## 4. Overall Readiness

As dez dimensões continuam fazendo parte do modelo SearchGEO.

Para um dispositivo:

1. materializar as dez dimensões;
2. separar as dimensões `NOT_APPLICABLE`;
3. exigir que todas as dimensões restantes possuam `value` e não estejam `NOT_CONSOLIDATED`;
4. calcular Overall pela média aritmética das dimensões aplicáveis;
5. calcular Coverage pela média das dimensões aplicáveis;
6. calcular Confidence a partir das dimensões aplicáveis;
7. persistir explicitamente quais dimensões foram excluídas por não aplicabilidade.

Limitação persistida:

`DIMENSION_NOT_APPLICABLE:<DIMENSION>`

Uma dimensão `NOT_APPLICABLE`:

- não recebe 0;
- não recebe 100;
- não reduz score;
- não reduz Coverage;
- não bloqueia Overall;
- não é removida do modelo conceitual das dez dimensões.

## 5. Dados Estruturados / JSON-LD

### 5.1 Obrigatoriedade

JSON-LD **não é requisito universal para uma URL ser funcional em GEO**.

O baseline SearchGEO adota essa posição porque:

- mecanismos de busca/IA podem compreender conteúdo sem Structured Data;
- Structured Data é um sinal explícito adicional de significado, entidade e propriedades;
- mecanismos externos não garantem visibilidade, grounding ou rich result apenas porque Structured Data existe.

### 5.2 Quando não existe

Quando Structured Data não é observado e `BR-GEO-034..037` são legitimamente `NOT_APPLICABLE`:

- a dimensão `STRUCTURED_DATA` fica `NOT_APPLICABLE`;
- ela não participa do denominador do Overall;
- a ausência, isoladamente, não cria finding nem penalidade.

### 5.3 Quando existe

Quando JSON-LD é observado:

- `STRUCTURED_DATA` passa a ser aplicável;
- BR-GEO-034 avalia interpretabilidade/sintaxe;
- BR-GEO-035 avalia tipos/propriedades identificáveis;
- BR-GEO-036 avalia coerência com conteúdo visível;
- BR-GEO-037 avalia coerência das entidades;
- resultados PASS/WARNING/FAIL participam normalmente do Score GEO;
- UNKNOWN/ERROR podem reduzir Coverage/Consolidation;
- markup inválido ou contraditório pode reduzir a nota.

Adicionar JSON-LD apenas para "destravar" score não é uma prática válida.

### 5.4 Coerência factual

Structured Data pode normalizar a forma da informação, mas não pode inventar fatos.

Exemplos legítimos:

- `R$ 27,50` no HTML e `price=27.50`, `priceCurrency=BRL` no JSON-LD;
- data textual no HTML e ISO-8601 no JSON-LD;
- nome abreviado visível e nome jurídico completo quando a relação estiver sustentada.

Exemplos inválidos:

- preço divergente;
- produto/serviço não apresentado;
- review/rating inexistente;
- autoria, data, benefício ou claim não sustentado;
- entidade diferente da observada.

## 6. Formato estruturado coberto pelo baseline

O parser Structured Data do baseline atual é orientado a JSON-LD em `script[type="application/ld+json"]`.

Google também aceita Microdata e RDFa, mas esses formatos não devem ser declarados como plenamente cobertos pelo SearchGEO enquanto não houver implementação/testes equivalentes. Essa limitação deve permanecer explícita na documentação.

## 7. Premissas mínimas para uma URL GEO funcional

As premissas abaixo não são promessa de ranking/citação. Elas representam o mínimo operacional para a URL poder ser analisada e potencialmente recuperada por sistemas de busca/IA.

| Tópico | Classe | Efeito no SearchGEO |
| --- | --- | --- |
| URL tecnicamente recuperável | MÍNIMO | Falha material compromete readiness técnico. |
| Resposta HTML/conteúdo analisável | MÍNIMO | Sem documento/conteúdo utilizável, dimensões dependentes não podem consolidar. |
| Conteúdo essencial disponível após rendering | MÍNIMO quando há JS | Conteúdo dependente de JS precisa permanecer recuperável. |
| Conteúdo principal identificável e significativo | MÍNIMO | Sem conteúdo principal não há base semântica/answerability confiável. |
| Conteúdo textual importante disponível | MÍNIMO | Informação crítica somente visual/oculta reduz recuperabilidade. |
| Indexabilidade compatível com a intenção pública da URL | MÍNIMO para presença em busca pública | `noindex`/bloqueios intencionais podem tornar a URL inelegível para experiências públicas. |
| Tópico/intenção principal identificável | MÍNIMO semântico | Necessário para interpretar o que a URL responde. |
| Claims e valores materialmente coerentes | MÍNIMO de confiança | Contradições factuais comprometem citation/evidence readiness. |
| JSON-LD | OPCIONAL / REFORÇO | Quando presente, entra no score e deve ser válido/coerente. Ausência legítima não penaliza. |
| Sitemap XML | OPCIONAL / DESCOBERTA | Ajuda descoberta/freshness; ausência isolada não é FAIL. |
| Canonical | CONTEXTUALMENTE RECOMENDADO | Importante quando há duplicidade/URL preferencial; ausência isolada não é blocker universal. |
| robots.txt | OPCIONAL COMO ARQUIVO | Ausência não significa bloqueio; políticas presentes precisam ser interpretáveis. |
| Autor/publisher explícito | CONTEXTUAL | Aplicabilidade depende do tipo de página e claims. |
| Data de publicação/atualização | CONTEXTUAL | Relevante para conteúdo temporal/editorial; não universal. |
| `llms.txt` ou arquivo específico para IA | NÃO OBRIGATÓRIO | Não impacta score automaticamente. |
| GPTBot liberado | NÃO OBRIGATÓRIO para Search readiness | GPTBot e OAI-SearchBot têm finalidades distintas; bloqueio de treinamento não equivale a bloqueio de search. |

## 8. Obrigatório versus recomendado

O relatório e a documentação devem evitar a frase "obrigatório para GEO" quando o requisito for apenas recomendação de um mecanismo, enriquecimento opcional ou aplicável somente a determinados tipos de página.

Usar as classes:

- `MÍNIMO`;
- `CONTEXTUAL`;
- `OPCIONAL / REFORÇO`;
- `NÃO OBRIGATÓRIO`.

## 9. Relatório

O relatório deve distinguir:

- `NÃO DETERMINADO`: deveria haver conclusão, mas a análise não consolidou;
- `NÃO APLICÁVEL`: o tópico está fora do universo aplicável;
- score `0.0`: avaliação efetivamente calculada como zero.

Quando houver dimensão `NOT_APPLICABLE`, o Overall pode ser calculado e deve registrar a exclusão na rastreabilidade.

## 10. Reprodutibilidade

BR-GEO-054 deve usar `SCORE-GEO-002`.

Dadas as mesmas RuleExecutions e metadados, a decisão de aplicabilidade, os scores de dimensão, Overall, Coverage, Confidence e limitations devem ser reproduzíveis sem reexecutar website ou IA.

## 11. Testes mínimos

Obrigatório validar:

1. dimensão sem RuleExecutions continua bloqueando Overall;
2. dimensão com todas as regras legitimamente `NOT_APPLICABLE` não bloqueia Overall;
3. dimensão `NOT_APPLICABLE` por pré-requisito bloqueado continua bloqueando Overall;
4. JSON-LD/Structured Data presente torna `STRUCTURED_DATA` aplicável;
5. PASS/WARNING/FAIL em Structured Data entra no cálculo;
6. ausência legítima de Structured Data não recebe zero nem cem;
7. Overall registra dimensões excluídas;
8. BR-GEO-054 permanece reproduzível.
