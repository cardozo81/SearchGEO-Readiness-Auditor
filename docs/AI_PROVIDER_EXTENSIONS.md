# AI_PROVIDER_EXTENSIONS.md

Extensões de providers semânticos adicionadas de forma aditiva ao SearchGEO, sem alterar o núcleo M18 homologado.

## Estado operacional

Os providers abaixo são **PROVISIONAL** e **explicit-only** até a conclusão do smoke humano. Eles não participam de `--ai-provider auto`.

| CLI | Provider | Modelo default | API usada | Structured Output | Estado SearchGEO |
|---|---|---|---|---|---|
| `xai` / `grok` | xAI / Grok | `grok-4.6` | Responses API | JSON Schema strict | `PROVISIONAL` |
| `qwen` | Alibaba Cloud Model Studio / Qwen | `qwen3.8-max` | OpenAI-compatible Chat Completions | JSON Schema strict | `PROVISIONAL` |
| `gemini` | Google Gemini | `gemini-3.8-flash` | Gemini Interactions API | JSON Schema | `PROVISIONAL` |
| `anthropic` / `claude` | Anthropic Claude | `claude-sonnet-5` | Messages API | `output_config.format` JSON Schema | `PROVISIONAL` |

O contrato semântico continua sendo o mesmo `M18-SEMANTIC-22-v1`: exatamente BR-GEO-028..049, validação local de schema, proibição de `evidence_id` inventado e fail-closed em saída incompleta ou inválida.

## Garantia de isolamento do legado

A implementação foi deliberadamente separada em `searchgeo.provider_extensions` e exposta pelo shim `searchgeo.cli_extensions`.

O builder de extensão delega sem alteração as seleções existentes `none`, `openai`, `deepseek`, `mimo` e `auto` para `searchgeo.m18_ai.build_semantic_provider`.

`AUTO` continua, por contrato:

```text
OpenAI -> DeepSeek -> MiMo
```

Mesmo que `XAI_API_KEY`, `DASHSCOPE_API_KEY`, `GEMINI_API_KEY` ou `ANTHROPIC_API_KEY` estejam configuradas, esses providers **não entram em AUTO** enquanto forem provisórios.

## xAI / Grok

Configuração:

```powershell
$env:XAI_API_KEY = "<xai-api-key>"
searchgeo audit https://example.com --ai-provider xai
```

Alias aceito:

```powershell
searchgeo audit https://example.com --ai-provider grok
```

Modelo suportado nesta qualificação:

```text
grok-4.6
```

Override:

```powershell
$env:SEARCHGEO_XAI_MODEL = "grok-4.6"
```

Endpoint default:

```text
https://api.x.ai/v1/responses
```

Override operacional, somente quando exigido pelo ambiente:

```powershell
$env:SEARCHGEO_XAI_ENDPOINT = "<endpoint-compatível>"
```

Referências oficiais:

- Structured Outputs: https://docs.x.ai/developers/model-capabilities/text/structured-outputs
- Grok 4.6: https://docs.x.ai/developers/models/grok-4.6
- Pricing: https://docs.x.ai/developers/pricing

## Alibaba Qwen

Configuração:

```powershell
$env:DASHSCOPE_API_KEY = "<model-studio-api-key>"
searchgeo audit https://example.com --ai-provider qwen
```

Modelos suportados nesta qualificação:

```text
qwen3.8-max
qwen3.8-flash
```

Default:

```text
qwen3.8-max
```

Override:

```powershell
$env:SEARCHGEO_QWEN_MODEL = "qwen3.8-flash"
```

Endpoint default do adapter:

```text
https://dashscope-us.aliyuncs.com/compatible-mode/v1/chat/completions
```

Alibaba usa domínios diferentes por região/workspace. Para China, Singapore, Hong Kong ou outro deployment scope, configure explicitamente o endpoint compatível:

```powershell
$env:SEARCHGEO_QWEN_ENDPOINT = "https://<workspace>.<região>.maas.aliyuncs.com/compatible-mode/v1/chat/completions"
```

A API key precisa pertencer à região/workspace do endpoint. Não misture uma key de uma região com endpoint de outra.

Referências oficiais:

- API reference: https://www.alibabacloud.com/help/en/model-studio/qwen-api-reference
- Responses compatibility: https://www.alibabacloud.com/help/en/model-studio/compatibility-with-openai-responses-api
- Structured output: https://www.alibabacloud.com/help/en/model-studio/qwen-structured-output
- Qwen 3.8 Max: https://docs.modelstudio.console.alibabacloud.com/en/model-studio/qwen3-8-max

## Google Gemini

Configuração:

```powershell
$env:GEMINI_API_KEY = "<gemini-api-key>"
searchgeo audit https://example.com --ai-provider gemini
```

Modelo suportado nesta qualificação:

```text
gemini-3.8-flash
```

Override:

```powershell
$env:SEARCHGEO_GEMINI_MODEL = "gemini-3.8-flash"
```

Endpoint default:

```text
https://generativelanguage.googleapis.com/v1beta/interactions
```

Override:

```powershell
$env:SEARCHGEO_GEMINI_ENDPOINT = "<endpoint-compatível>"
```

O adapter usa `x-goog-api-key` no header e o `response_format` atual da Interactions API, com `mime_type=application/json` e JSON Schema. A key não é colocada na URL persistida/telemetria.

Referências oficiais:

- Gemini 3.8 Flash: https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash
- Structured Outputs: https://ai.google.dev/gemini-api/docs/structured-output
- Interactions API migration/current response schema: https://ai.google.dev/gemini-api/docs/interactions-breaking-changes-may-2026
- Pricing: https://ai.google.dev/gemini-api/docs/pricing

## Anthropic Claude

Configuração:

```powershell
$env:ANTHROPIC_API_KEY = "<anthropic-api-key>"
searchgeo audit https://example.com --ai-provider anthropic
```

Alias aceito:

```powershell
searchgeo audit https://example.com --ai-provider claude
```

Modelo suportado nesta qualificação:

```text
claude-sonnet-5
```

Override:

```powershell
$env:SEARCHGEO_ANTHROPIC_MODEL = "claude-sonnet-5"
```

Endpoint default:

```text
https://api.anthropic.com/v1/messages
```

Override:

```powershell
$env:SEARCHGEO_ANTHROPIC_ENDPOINT = "<endpoint-compatível>"
```

Claude Sonnet 5 usa adaptive thinking por default. O SearchGEO não força `temperature`, `top_p`, `top_k` nem o antigo `thinking: {type: enabled}`. O parser procura blocos de conteúdo por `type=text`, porque respostas podem conter blocos de thinking antes do texto.

`stop_reason=refusal` em HTTP 200 é tratado como indisponibilidade da tentativa, não como avaliação do website.

Referências oficiais:

- Messages API: https://platform.claude.com/docs/en/api/messages/create
- Structured Outputs: https://platform.claude.com/docs/en/build-with-claude/structured-outputs
- Sonnet 5 migration: https://platform.claude.com/docs/en/models/sonnet-5/migration-guide
- Pricing: https://platform.claude.com/docs/en/about-claude/pricing

## Variáveis de ambiente

| Provider | API key | Modelo | Endpoint opcional |
|---|---|---|---|
| xAI | `XAI_API_KEY` | `SEARCHGEO_XAI_MODEL` | `SEARCHGEO_XAI_ENDPOINT` |
| Qwen | `DASHSCOPE_API_KEY` | `SEARCHGEO_QWEN_MODEL` | `SEARCHGEO_QWEN_ENDPOINT` |
| Gemini | `GEMINI_API_KEY` | `SEARCHGEO_GEMINI_MODEL` | `SEARCHGEO_GEMINI_ENDPOINT` |
| Anthropic | `ANTHROPIC_API_KEY` | `SEARCHGEO_ANTHROPIC_MODEL` | `SEARCHGEO_ANTHROPIC_ENDPOINT` |

A ausência da key do provider selecionado resulta em `NOT_CONFIGURED` e zero chamada externa. Nenhuma key de outro provider é reutilizada como fallback.

## Uso de modelo explícito

```powershell
searchgeo audit https://example.com --ai-provider qwen --ai-model qwen3.8-flash
```

Model IDs fora da allow-list do SearchGEO são rejeitados antes de qualquer chamada externa.

## Telemetria e custos

Os adapters persistem, quando o provider retorna, contagem normalizada de input/output/cached/reasoning tokens e duração da tentativa através do contrato `ProviderAttempt` existente.

Enquanto estes providers estiverem `PROVISIONAL`, o catálogo homologado `provider_pricing_catalog` de M18 não é ampliado automaticamente. Portanto `estimated_cost` pode ficar indisponível para a tentativa mesmo quando tokens estão disponíveis. Isso evita publicar custo incorreto quando há preço por região, cache, tier, promoção ou contexto. A documentação oficial do provider prevalece.

Não interprete `estimated_cost` como invoice.

## Falhas e quarantine

Para provider explícito:

- ausência de key -> `NOT_CONFIGURED`, sem request;
- 401 -> `AUTH_ERROR`;
- 403 -> `PERMISSION_ERROR`;
- 429 -> quota/rate-limit conforme diagnóstico disponível;
- timeout/network/server -> indisponibilidade operacional;
- JSON inválido, schema incompleto, evidência inventada ou saída ausente -> falha de contrato;
- após falha qualificadora, o provider pode entrar em `QUARANTINED_FOR_AUDIT` e não é reativado silenciosamente durante a mesma auditoria.

Falha de provider nunca vira Finding do website por si só.

## Smoke humano obrigatório antes de AUTO/merge funcional

Executar ao menos uma URL controlada com cada provider e validar:

1. criação do audit e conclusão sem exceção;
2. `report/ai-usage.html` com provider/model corretos;
3. BR-GEO-028..049 com exatamente um assessment por regra quando a chamada é válida;
4. ausência de credencial/token nos HTML, SQLite e logs;
5. erro de key inválida classificado e sanitizado;
6. segundo URL/contexto não dispara retry indevido após quarantine;
7. execução `--ai-provider auto` continua usando somente OpenAI/DeepSeek/MiMo;
8. execução explícita OpenAI, DeepSeek e MiMo mantém resultados/telemetria esperados da baseline.

Comandos de smoke:

```powershell
searchgeo audit https://example.com --max-pages 1 --ai-provider xai
searchgeo audit https://example.com --max-pages 1 --ai-provider qwen
searchgeo audit https://example.com --max-pages 1 --ai-provider gemini
searchgeo audit https://example.com --max-pages 1 --ai-provider anthropic
searchgeo audit https://example.com --max-pages 1 --ai-provider auto
```

Não promover estes providers para AUTO nem remover `PROVISIONAL` apenas porque unit/CI passou. A promoção depende do smoke humano com credenciais reais e revisão do resultado semântico.
