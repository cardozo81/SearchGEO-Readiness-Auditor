# Guia de IA

## Compatibilidade de IA

IA é **opcional**. A Stable Local Baseline funciona sem API key e sem serviço de IA.

Providers implementados:

| Provider | Seleção CLI | Dependência externa | Estado sem credencial |
|---|---|---|---|
| `NoneProvider` | `--ai-provider none` | nenhuma | `NO_AI` suportado |
| `OpenAIProvider` | `--ai-provider openai` | OpenAI Responses API por HTTPS | `NOT_CONFIGURED` / sem penalidade ao site |

Não existe dependência Python `openai`: o adapter usa HTTP da biblioteca padrão.

O projeto **não fixa um nome de modelo**. O operador deve fornecer um modelo aceito pelo provider/endpoint no momento da execução. Compatibilidade de modelos externos pode mudar independentemente do código do auditor; valide o modelo escolhido antes da homologação.

## O que a IA faz

O provider semântico produz avaliações auxiliares para regras `BR-GEO-028..049`. O scoring oficial é executado posteriormente pelo `ScoringEngine` determinístico.

## O que a IA não faz

O LLM não:

- calcula o Score oficial;
- escolhe pesos de scoring;
- muda fatores PASS/WARNING/FAIL;
- garante ranking/citação/tráfego;
- inventa evidências aceitas pelo pipeline;
- substitui o contrato das Business Rules.

# Configurar OpenAI — passo a passo

## 1. Confirmar dependências locais

Antes de habilitar IA, confirme Python/package/Chromium:

```powershell
python --version
searchgeo --version
python -m pip show playwright
```

Se alguma dependência estiver ausente, siga [INSTALLATION.md](INSTALLATION.md), seção **Instalar dependências ausentes no Windows**.

## 2. Confirmar conectividade HTTPS

A máquina precisa ter egress HTTPS para o serviço externo. Em ambientes com proxy/firewall corporativo, valide a política antes do smoke test.

A baseline não possui flag própria de proxy.

## 3. Definir API key no ambiente

No PowerShell da sessão que executará a auditoria:

```powershell
$env:OPENAI_API_KEY = "<chave>"
```

Valide **sem imprimir o valor**:

```powershell
Test-Path Env:OPENAI_API_KEY
```

O resultado esperado é `True`.

Não use:

```powershell
Write-Output $env:OPENAI_API_KEY
```

em logs de homologação.

## 4. Definir o modelo

Opção A — variável de ambiente:

```powershell
$env:SEARCHGEO_OPENAI_MODEL = "<modelo-configurado>"
```

Valide:

```powershell
$env:SEARCHGEO_OPENAI_MODEL
```

Opção B — flag por execução:

```powershell
--ai-model "<modelo-configurado>"
```

`--ai-model` tem precedência sobre `SEARCHGEO_OPENAI_MODEL`.

## 5. Executar com OpenAI

Com model na variável:

```powershell
searchgeo audit https://example.com --ai-provider openai
```

Com model na CLI:

```powershell
searchgeo audit https://example.com `
  --ai-provider openai `
  --ai-model "<modelo-configurado>"
```

Se `--ai-provider openai` for selecionado sem model em nenhuma das duas fontes, a CLI rejeita a execução antes da auditoria.

## 6. Verificar o modo resultante

Após a execução, consulte o relatório e o Audit persistido:

- `FULL`: provider disponível e respostas válidas no universo aplicável;
- `DEGRADED`: parte da análise semântica ficou indisponível/rejeitada;
- `NO_AI`: provider não configurado/NoneProvider.

`DEGRADED` e `NO_AI` podem reduzir Coverage/Confidence/Consolidation, mas não são FAIL do website.

## 7. Desabilitar IA

A forma explícita e suportada é:

```powershell
searchgeo audit https://example.com --ai-provider none
```

Esse também é o default.

Para remover a credencial da sessão PowerShell:

```powershell
Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:SEARCHGEO_OPENAI_MODEL -ErrorAction SilentlyContinue
```

# Providers implementados

## NoneProvider

Provider obrigatório de fallback. Retorna:

```text
state = NOT_CONFIGURED
reason = AI_NOT_CONFIGURED
```

A auditoria segue em modo `NO_AI` quando não há provider semântico configurado.

## OpenAIProvider

Adapter implementado sobre OpenAI Responses API.

Defaults internos:

- endpoint: `https://api.openai.com/v1/responses`;
- timeout: 45 s;
- configuration version: `1`;
- prompt id: `searchgeo-semantic-v1`;
- prompt version: `1`;
- Structured Output: JSON Schema estrito (`strict=true`).

Endpoint, timeout e versões são parâmetros internos do provider e **não são flags CLI da Stable Local Baseline**.

# Segurança da API key

- A key é obtida por argumento interno do provider ou `OPENAI_API_KEY`.
- A CLI não aceita key como flag.
- Não coloque key em `searchgeo.toml`.
- Não grave key no repositório, artifacts, fixtures ou scripts versionados.
- A key é usada no header `Authorization` da chamada HTTP.
- O provider não inclui a key no payload semântico.
- Report/payloads exibidos possuem redaction defensiva para nomes sensíveis.

# Dados enviados externamente

Quando OpenAI é efetivamente usado, o payload semântico pode incluir, para cada snapshot:

- `snapshot_id`;
- URL da página;
- title;
- conteúdo principal extraído;
- Dados Estruturados extraídos;
- idioma primário;
- mercado;
- Evidence fornecida ao provider, incluindo ID, tipo, source, observed value e artifact reference.

A instrução enviada ao provider exige `UNKNOWN` quando a evidência for insuficiente e proíbe inventar evidence IDs.

Ao habilitar OpenAI, considere que **conteúdo do site auditado e evidências derivadas podem ser transmitidos ao serviço externo**. A política de dados da organização deve autorizar esse envio.

# Dados que permanecem locais

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

O provider recebe o payload construído para a análise semântica, não o `audit.db` inteiro como arquivo.

# Schema validation

A resposta aceita precisa obedecer schema rígido, incluindo:

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

# Evidence validation

Todo `evidence_id` retornado precisa pertencer ao conjunto fornecido naquela chamada.

Se a resposta referenciar evidence inexistente/inventada, ela é rejeitada por `SemanticEvidenceError` e não é transformada em finding válido.

Resultados diferentes de `UNKNOWN`/`NOT_APPLICABLE` exigem source evidence. Entity observations também exigem evidence.

# Fallback e estados

## FULL

Provider configurado, disponível e produzindo respostas válidas no universo aplicável.

## DEGRADED

Provider selecionado, mas parte das análises fica indisponível/rejeitada. Falha HTTP, timeout, schema inválido, evidence inválida, JSON inválido etc. não viram FAIL do site; a análise correspondente degrada.

## NO_AI

Nenhum provider configurado ou `NoneProvider`. Regras semantic-only sem fallback determinístico ficam `UNKNOWN`.

# Impacto em Coverage, Confidence e Consolidation

Ausência/indisponibilidade de IA pode reduzir a quantidade de regras efetivamente avaliadas. Isso pode reduzir:

- Coverage;
- Confidence;
- Consolidation;
- possibilidade de calcular Overall.

Isso representa **limitação da auditoria**, não baixa qualidade do site. O ScoringEngine não converte `UNKNOWN` em zero.

# Falha do provider

Erros capturados pelo adapter retornam estado `UNAVAILABLE` com motivo do tipo:

```text
AI_PROVIDER_UNAVAILABLE:<ErrorType>
```

A estratégia é fail-safe: preservar rastreabilidade e reduzir capacidade analítica em vez de publicar conclusão negativa sem evidência.
