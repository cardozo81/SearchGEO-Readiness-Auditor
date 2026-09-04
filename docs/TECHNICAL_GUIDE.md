# TECHNICAL_GUIDE.md

## Pipeline

```text
CLI público (cli_extensions)
→ target/device config
→ M2 acquisition
→ M3 rendering
→ M4 evidence
→ M5/M6 deterministic analysis
→ content extractability
→ M7 semantic provider (M18 legacy ou extension explicit-only)
→ M8 device comparison
→ pre-scoring
→ M9 SCORE-GEO-002
→ M10 prioritization
→ M14 element linking
→ M20 advisory generation (downstream de findings/scoring)
→ M11/M16/M17 intermediate reporting
→ M18 telemetry enrichment
→ report_site finalization
→ M20 report-site enrichment
→ M21 optional external Web Performance enrichment
```

M20/M21 não participam do scoring. `audit.db` e artifacts continuam fonte de verdade.

## Device context

CLI default `mobile`; valores `mobile`, `desktop`, `both`. M3 materializa apenas o selecionado e M7/M20 só podem atuar nos snapshots existentes.

## Provider architecture

### Núcleo M18 preservado

```text
src/searchgeo/m18_ai.py
src/searchgeo/cli.py
src/searchgeo/m20_ai.py
```

O comportamento homologado continua:

```text
none
openai
deepseek
mimo
auto = OpenAI -> DeepSeek -> MiMo
```

A extensão de providers não modifica esses três módulos.

### Extensão aditiva

```text
src/searchgeo/provider_extensions.py
src/searchgeo/provider_extensions_m20.py
src/searchgeo/cli_extensions.py
```

Providers explicit-only:

```text
xai / grok      -> XAI / grok-4.6
qwen            -> QWEN / qwen3.8-max|qwen3.8-flash
gemini          -> GEMINI / gemini-3.8-flash
anthropic/claude-> ANTHROPIC / claude-sonnet-5
```

Todos permanecem `PROVISIONAL` até smoke humano. O builder de extensão intercepta somente essas seleções e delega `none/openai/deepseek/mimo/auto` diretamente ao builder M18 legado.

O entrypoint de package aponta para `searchgeo.cli_extensions:main`; `python -m searchgeo` usa o mesmo shim. Importar `searchgeo.cli` diretamente preserva a superfície legada, o que permite regressão explícita do core.

## Contrato semântico

Todos os adapters devem convergir para o mesmo contrato SearchGEO:

```text
M18-SEMANTIC-22-v1
BR-GEO-028..049 exatamente uma vez
SemanticProviderResult
ProviderUsage
ProviderDiagnostic
ProviderAttempt
```

Saída incompleta, schema inválido ou `evidence_id` fora do universo fornecido falha fechado e não vira Finding do website.

Diferenças de API ficam no adapter:

```text
XAI       Responses API + JSON Schema strict
QWEN      OpenAI-compatible Chat Completions + JSON Schema strict
GEMINI    Interactions API + response_format JSON/schema
ANTHROPIC Messages API + output_config.format JSON Schema
```

## Credenciais e configuração

Legacy:

```text
OPENAI_API_KEY
DEEPSEEK_API_KEY
MIMO_API_KEY
```

Extensions:

```text
XAI_API_KEY
DASHSCOPE_API_KEY
GEMINI_API_KEY
ANTHROPIC_API_KEY
```

Cada provider usa apenas a própria credencial. Key ausente no provider explicitamente selecionado -> `NOT_CONFIGURED`, zero request.

Model overrides:

```text
SEARCHGEO_XAI_MODEL
SEARCHGEO_QWEN_MODEL
SEARCHGEO_GEMINI_MODEL
SEARCHGEO_ANTHROPIC_MODEL
```

Endpoint overrides:

```text
SEARCHGEO_XAI_ENDPOINT
SEARCHGEO_QWEN_ENDPOINT
SEARCHGEO_GEMINI_ENDPOINT
SEARCHGEO_ANTHROPIC_ENDPOINT
```

Qwen pode exigir endpoint regional/workspace; key e endpoint devem pertencer ao mesmo deployment scope.

## Routing e quarantine

M18 explicit/auto mantém quarantine, failover e URL lock exatamente como antes.

Providers de extensão são single-provider explicit-only. Uma falha qualificadora pode quarantinar o provider na auditoria, impedindo tentativas silenciosas em URLs posteriores.

As API keys dos providers de extensão não alteram `AUTO`.

## M20

Modules legacy:

```text
src/searchgeo/m20.py
src/searchgeo/m20_ai.py
src/searchgeo/m20_persistence.py
src/searchgeo/m20_reporting.py
```

Adapter adicional:

```text
src/searchgeo/provider_extensions_m20.py
```

M20 roda depois de M9/M10/findings e cria apenas entidades auxiliares. A remediação textual é default OFF. JSON-LD determinístico é sempre materializado.

OpenAI/DeepSeek/MiMo continuam usando o router M20 legado. xAI/Qwen/Gemini/Anthropic usam o adapter M20 nativo da extensão. Provider quarantined no M7 não é reativado para M20.

### Contrato factual

Request limitado ao contexto persistido; resposta deve referenciar finding/evidence válidos. Validação local impede IDs externos e novos tokens numéricos não suportados. A saída é advisory e exige revisão humana.

### JSON-LD

Ausência: baseline conservador `WebPage` com dados persistidos. Existente: revisão não destrutiva. Nenhuma alteração é aplicada ao site.

## Usage e custo

Usage/tokens dos providers de extensão são normalizados quando retornados pela API e persistidos via `ProviderAttempt`.

Enquanto esses providers estiverem `PROVISIONAL`, o catálogo homologado de preços M18 não é alterado automaticamente. `estimated_cost` pode permanecer `null` para não inventar preço diante de variação por região, tier, cache ou promoção.

## SQLite lifecycle

Conexões transitórias devem ser fechadas explicitamente. O context manager nativo de `sqlite3.Connection` controla transação, **não fecha o handle**. Isso é especialmente relevante no Windows, onde um `audit.db` aberto impede remoção do `TemporaryDirectory`.

## Report final

```text
report/index.html
report/mobile.html       # condicional
report/desktop.html      # condicional
report/remediation.html
report/content-suggestions.html
report/web-performance.html
report/ai-usage.html
report/references.html
report/css/site.css
```

`report_site` não chama IA. `m20_reporting` projeta somente o estado M20 já persistido. M21 continua separado de qualquer provider LLM.

## Confidence

É reliability da conclusão do auditor, não métrica direta de qualidade textual. Não pode ser gatilho isolado para M20.

## Testing

```powershell
python -m compileall -q src tests
python -m unittest discover -s tests -v
```

A regressão específica da extensão inclui:

```text
tests/test_provider_extensions.py
tests/test_provider_extensions_m20.py
tests/test_cli_provider_extensions.py
```

E deve preservar integralmente os testes M18/M20 existentes, especialmente routing, defaults, error classification, credential isolation, quarantine, URL lock, persistence e report telemetry.

## Release gate

CI verde não promove provider automaticamente. Antes de merge da extensão, exigir:

1. diff comprovando ausência de alteração em `m18_ai.py`, `cli.py` e `m20_ai.py`;
2. suíte completa verde;
3. documentação alinhada;
4. smoke humano real de xAI/Qwen/Gemini/Anthropic;
5. smoke humano de OpenAI/DeepSeek/MiMo/AUTO;
6. nenhuma key vazada em outputs.

Fonte normativa: [specification/22_SAFE_AI_PROVIDER_EXTENSIONS.md](specification/22_SAFE_AI_PROVIDER_EXTENSIONS.md).
