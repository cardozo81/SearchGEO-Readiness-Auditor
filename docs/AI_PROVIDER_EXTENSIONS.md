# AI_PROVIDER_EXTENSIONS.md

Guia operacional dos providers semânticos adicionais integrados ao SearchGEO por meio do `provider_registry` canônico.

## Estado atual

Os providers abaixo estão implementados, mas permanecem **PROVISIONAL** e **explicit-only**. Eles não participam de `--ai-provider auto` enquanto não houver qualificação humana com credenciais reais de cada provider.

| CLI | Provider | Modelo default | API usada | Estado SearchGEO |
|---|---|---|---|---|
| `xai` / `grok` | xAI / Grok | `grok-4.6` | Responses API | `PROVISIONAL` |
| `qwen` | Alibaba Cloud Model Studio / Qwen | `qwen3.8-max` | OpenAI-compatible Chat Completions | `PROVISIONAL` |
| `gemini` | Google Gemini | `gemini-3.8-flash` | Gemini Interactions API | `PROVISIONAL` |
| `anthropic` / `claude` | Anthropic Claude | `claude-sonnet-5` | Messages API | `PROVISIONAL` |

O contrato semântico continua sendo `M18-SEMANTIC-22-v1`: exatamente BR-GEO-028..049, validação local de schema, proibição de `evidence_id` inventado e fail-closed em saída incompleta ou inválida.

## AUTO permanece legado

A cadeia homologada não foi ampliada:

```text
OpenAI -> DeepSeek -> MiMo
```

Mesmo que `XAI_API_KEY`, `DASHSCOPE_API_KEY`, `GEMINI_API_KEY` ou `ANTHROPIC_API_KEY` estejam configuradas, xAI/Qwen/Gemini/Anthropic não entram em `AUTO` enquanto permanecerem provisórios.

O console interativo consome o mesmo registry canônico da CLI. Portanto não deve manter uma lista independente de providers, aliases, variáveis, modelos ou endpoints.

## Evidência de smoke disponível

No gate humano executado antes da consolidação do baseline:

- `none`: aprovado;
- OpenAI explícito: aprovado com chamada real;
- DeepSeek explícito: aprovado com chamada real;
- `auto`: aprovado com chamada real e parada no primeiro sucesso;
- xAI: fail-closed sem key aprovado;
- Qwen: fail-closed sem key aprovado;
- Gemini: fail-closed sem key aprovado;
- Anthropic: fail-closed sem key aprovado;
- alias `grok -> xai`: aprovado sem key, zero chamada;
- alias `claude -> anthropic`: aprovado sem key, zero chamada;
- MiMo: não qualificado nesta máquina por ausência de credencial PAYG compatível.

O caminho de **sucesso real** de xAI/Qwen/Gemini/Anthropic permanece `PENDING_EXTERNAL_CREDENTIAL`. Isso não é falha do software e não autoriza promovê-los para `AUTO`.

## xAI / Grok

Configuração:

```powershell
$env:XAI_API_KEY = "<xai-api-key>"
searchgeo audit https://example.com --ai-provider xai
```

Alias:

```powershell
searchgeo audit https://example.com --ai-provider grok
```

Modelo suportado nesta qualificação:

```text
grok-4.6
```

Variáveis:

```text
XAI_API_KEY
SEARCHGEO_XAI_MODEL
SEARCHGEO_XAI_ENDPOINT
```

Endpoint default:

```text
https://api.x.ai/v1/responses
```

Referências oficiais:

- Structured Outputs: https://docs.x.ai/developers/model-capabilities/text/structured-outputs
- modelo: https://docs.x.ai/developers/models/grok-4.6
- pricing: https://docs.x.ai/developers/pricing

## Alibaba Qwen

Configuração:

```powershell
$env:DASHSCOPE_API_KEY = "<model-studio-api-key>"
searchgeo audit https://example.com --ai-provider qwen
```

Modelos:

```text
qwen3.8-max
qwen3.8-flash
```

Default: `qwen3.8-max`.

Variáveis:

```text
DASHSCOPE_API_KEY
SEARCHGEO_QWEN_MODEL
SEARCHGEO_QWEN_ENDPOINT
```

Endpoint default do adapter:

```text
https://dashscope-us.aliyuncs.com/compatible-mode/v1/chat/completions
```

A API key precisa pertencer à região/workspace do endpoint usado. Para outra região, configure explicitamente `SEARCHGEO_QWEN_ENDPOINT`; não misture key e endpoint de regiões diferentes.

Referências oficiais:

- API reference: https://www.alibabacloud.com/help/en/model-studio/qwen-api-reference
- Responses compatibility: https://www.alibabacloud.com/help/en/model-studio/compatibility-with-openai-responses-api
- Structured Output: https://www.alibabacloud.com/help/en/model-studio/qwen-structured-output

## Google Gemini

Configuração:

```powershell
$env:GEMINI_API_KEY = "<gemini-api-key>"
searchgeo audit https://example.com --ai-provider gemini
```

Modelo:

```text
gemini-3.8-flash
```

Variáveis:

```text
GEMINI_API_KEY
SEARCHGEO_GEMINI_MODEL
SEARCHGEO_GEMINI_ENDPOINT
```

Endpoint default:

```text
https://generativelanguage.googleapis.com/v1beta/interactions
```

A key é enviada no header `x-goog-api-key`; ela não deve ser persistida em URL, SQLite, HTML ou log.

Referências oficiais:

- modelo: https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash
- Structured Outputs: https://ai.google.dev/gemini-api/docs/structured-output
- pricing: https://ai.google.dev/gemini-api/docs/pricing

## Anthropic Claude

Configuração:

```powershell
$env:ANTHROPIC_API_KEY = "<anthropic-api-key>"
searchgeo audit https://example.com --ai-provider anthropic
```

Alias:

```powershell
searchgeo audit https://example.com --ai-provider claude
```

Modelo:

```text
claude-sonnet-5
```

Variáveis:

```text
ANTHROPIC_API_KEY
SEARCHGEO_ANTHROPIC_MODEL
SEARCHGEO_ANTHROPIC_ENDPOINT
```

Endpoint default:

```text
https://api.anthropic.com/v1/messages
```

O parser considera blocos de conteúdo por `type=text`. `stop_reason=refusal` em HTTP 200 é indisponibilidade da tentativa, não avaliação negativa do website.

Referências oficiais:

- Messages API: https://platform.claude.com/docs/en/api/messages/create
- Structured Outputs: https://platform.claude.com/docs/en/build-with-claude/structured-outputs
- pricing: https://platform.claude.com/docs/en/about-claude/pricing

## Ausência de credencial

Selecionar explicitamente um provider sem sua key resulta em `NOT_CONFIGURED`, zero chamada externa e zero custo. Não existe fallback para uma key de outro provider.

O comportamento esperado é:

```text
SINGLE_PROVIDER
NOT_CONFIGURED
attempts = 0
estimated_cost = 0
```

## Modelo explícito

Exemplo:

```powershell
searchgeo audit https://example.com --ai-provider qwen --ai-model qwen3.8-flash
```

Model IDs fora da allow-list do SearchGEO são rejeitados antes da chamada externa.

## Telemetria e custo

Os adapters normalizam, quando fornecidos pelo provider:

- input tokens;
- cached input tokens;
- output tokens;
- reasoning tokens;
- duração;
- status/erro sanitizado.

Enquanto o provider estiver `PROVISIONAL`, o SearchGEO não inventa preço nem amplia automaticamente o catálogo homologado de pricing. `estimated_cost` pode permanecer indisponível mesmo quando a contagem de tokens existe.

`estimated_cost` nunca deve ser interpretado como invoice.

## Falhas e quarantine

Para provider explícito:

- key ausente -> `NOT_CONFIGURED`, sem request;
- 401 -> `AUTH_ERROR`;
- 403 -> `PERMISSION_ERROR`;
- 429 -> quota/rate-limit conforme diagnóstico disponível;
- timeout/network/server -> indisponibilidade operacional;
- JSON inválido, schema incompleto, evidência inventada ou saída ausente -> falha de contrato;
- falha qualificadora pode colocar o provider em `QUARANTINED_FOR_AUDIT`.

Falha de provider nunca vira Finding do website por si só.

## Gate para promoção de provider

Antes de remover `PROVISIONAL` ou incluir um provider adicional em `AUTO`, é obrigatório obter credencial real e validar ao menos uma URL controlada com:

1. conclusão da auditoria sem exceção;
2. `report/ai-usage.html` com provider/model corretos;
3. BR-GEO-028..049 com exatamente um assessment por regra quando a chamada é válida;
4. ausência de credencial/token em HTML, SQLite e logs;
5. erro de key inválida classificado e sanitizado;
6. ausência de retry indevido após quarantine;
7. regressão explícita confirmando que `AUTO` continua somente OpenAI/DeepSeek/MiMo até decisão de promoção.

Não simular homologação quando a credencial externa não está disponível.