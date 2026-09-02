# Guia de IA

## Princípio

IA é **opcional**. A Stable Local Baseline precisa funcionar sem API key e sem serviço de IA.

O provider semântico produz avaliações auxiliares para regras BR-GEO-028..049; o scoring oficial é executado depois pelo `ScoringEngine` determinístico.

## Providers implementados

### NoneProvider

Provider obrigatório de fallback. Retorna:

```text
state = NOT_CONFIGURED
reason = AI_NOT_CONFIGURED
```

A auditoria segue em modo `NO_AI` quando não há provider semântico configurado.

### OpenAIProvider

Adapter implementado sobre OpenAI Responses API.

Defaults internos:

- endpoint: `https://api.openai.com/v1/responses`;
- timeout: 45 s;
- configuration version: `1`;
- prompt id: `searchgeo-semantic-v1`;
- prompt version: `1`;
- Structured Output: JSON Schema estrito (`strict=true`).

O model **não é fixado no código**. É configuração obrigatória quando OpenAI é selecionado.

## Configuração operacional

```powershell
$env:OPENAI_API_KEY = "<chave>"
$env:SEARCHGEO_OPENAI_MODEL = "<modelo>"
searchgeo audit https://example.com --ai-provider openai
```

Ou:

```powershell
searchgeo audit https://example.com --ai-provider openai --ai-model "<modelo>"
```

`--ai-model` tem precedência sobre `SEARCHGEO_OPENAI_MODEL`.

## Segurança da API key

- A key é obtida por argumento interno do provider ou `OPENAI_API_KEY`.
- A CLI da baseline não aceita key como flag.
- Não coloque key em `searchgeo.toml`.
- A key é usada somente no header `Authorization` da chamada HTTP.
- O provider não inclui a key no payload semântico.
- Report e payloads exibidos possuem redaction defensiva para nomes sensíveis.

Nunca use segredo real em documentação, fixture ou commit.

## Dados enviados externamente

Quando OpenAI é efetivamente usado, o payload semântico pode incluir, para cada snapshot:

- `snapshot_id`;
- URL da página;
- title;
- conteúdo principal extraído;
- Dados Estruturados extraídos;
- idioma primário;
- mercado;
- Evidence fornecida ao provider, incluindo ID, tipo, source, observed value e artifact reference.

O objetivo é avaliar apenas o material fornecido. A instrução enviada ao provider exige `UNKNOWN` quando a evidência for insuficiente e proíbe inventar evidence IDs.

Portanto, ao habilitar OpenAI, considere que **conteúdo do site auditado e evidências derivadas podem ser transmitidos ao serviço externo**.

## Dados que permanecem locais

A persistência primária continua local:

- `audit.db`;
- RAW HTTP artifacts;
- rendered HTML;
- extrações;
- RuleExecutions;
- Findings;
- Scores;
- Recommendations;
- `report.html`.

O provider recebe somente o payload construído para análise semântica, não o `audit.db` inteiro como arquivo.

## Schema validation

A resposta aceita deve obedecer schema rígido, incluindo:

- assessments somente para `BR-GEO-028..049`;
- resultado permitido;
- confidence entre 0 e 1;
- evidence IDs;
- reasoning summary;
- observed value estruturado;
- entidades tipadas;
- no máximo 5 secondary intents;
- nenhum campo inesperado.

O provider não pode publicar `ERROR` como avaliação da qualidade do website.

## Evidence validation

Todo `evidence_id` retornado deve pertencer ao conjunto fornecido naquela chamada.

Se a resposta referenciar evidence inexistente/inventada, ela é rejeitada por `SemanticEvidenceError` e não é transformada em finding válido.

Resultados diferentes de `UNKNOWN`/`NOT_APPLICABLE` exigem source evidence. Entity observations também exigem evidence.

## Fallback e estados

### FULL

Provider configurado, disponível e produzindo respostas válidas no universo aplicável.

### DEGRADED

A execução possui provider selecionado, mas parte das análises fica indisponível/rejeitada. Falha de HTTP, timeout, schema inválido, evidence inválida, JSON inválido etc. não viram FAIL do site; a análise correspondente degrada.

### NO_AI

Nenhum provider configurado ou `NoneProvider`. Regras semantic-only sem fallback determinístico ficam `UNKNOWN`.

## Impacto em Coverage, Confidence e Consolidation

Ausência/indisponibilidade de IA pode reduzir a quantidade de regras efetivamente avaliadas. Isso pode reduzir:

- Coverage;
- Confidence;
- Consolidation;
- possibilidade de calcular Overall.

Isso representa **limitação da auditoria**, não baixa qualidade do site.

O ScoringEngine não converte `UNKNOWN` em zero.

## O que a IA não faz

O LLM não:

- calcula o Score oficial;
- escolhe pesos de scoring;
- muda fatores PASS/WARNING/FAIL;
- garante ranking/citação/tráfego;
- inventa evidências aceitas pelo pipeline;
- substitui o contrato das Business Rules.

## Falha do provider

Erros capturados pelo adapter retornam estado `UNAVAILABLE` com motivo do tipo:

```text
AI_PROVIDER_UNAVAILABLE:<ErrorType>
```

A estratégia é fail-safe: preservar rastreabilidade e reduzir capacidade analítica em vez de publicar conclusão negativa sem evidência.
