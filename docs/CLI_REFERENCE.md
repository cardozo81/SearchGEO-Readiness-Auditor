# CLI_REFERENCE.md

Referência operacional da linha de comando do SearchGEO Readiness Auditor.

## Sintaxe global

```text
searchgeo [--config PATH] [--version] [-h|--help] audit [target ...] [opções]
```

## `searchgeo audit`

```text
searchgeo audit [target ...]
  [--urls-file PATH]
  [--project TEXT]
  [--language CODE]
  [--market CODE]
  [--max-pages N]
  [--audits-root PATH]
  [--device-context mobile|desktop|both]
  [--ai-provider none|openai|deepseek|mimo|auto|xai|grok|qwen|gemini|anthropic|claude]
  [--ai-model MODEL_ID]
  [--ai-content-remediation | --no-ai-content-remediation]
  [--web-performance | --no-web-performance]
  [--web-performance-max-pages N]
  [--web-performance-timeout-seconds SECONDS]
  [--web-performance-field-source auto|pagespeed|crux|none]
  [--lighthouse-categories LIST]
```

## Glossário completo

| Argumento | Tipo / valores | Default | Regra |
|---|---|---|---|
| `target` | domínio ou URL HTTP(S), zero ou mais | — | Ao menos um target deve vir por posição ou `--urls-file`. |
| `--urls-file PATH` | arquivo UTF-8 | — | Uma URL/domínio por linha; vazias e linhas iniciadas por `#` são ignoradas. |
| `--project TEXT` | texto | hostname/target | Nome humano da auditoria. |
| `--language CODE` | texto | `pt-BR` | Contexto primário de idioma. |
| `--market CODE` | texto | `BR` | Contexto de mercado. |
| `--max-pages N` | inteiro > 0 | `100` | Limite determinístico da auditoria. |
| `--audits-root PATH` | diretório | `audits` | Raiz dos workspaces. |
| `--device-context` | `mobile`, `desktop`, `both` | `mobile`* | Controla rendering e contextos semânticos. `*` Pode vir de `SEARCHGEO_DEVICE_CONTEXT`. |
| `--ai-provider` | ver tabela abaixo | `none` | Provider semântico. Novos providers provisórios são explicit-only. |
| `--ai-model MODEL_ID` | model ID suportado | default do provider | Somente provider explícito; não pode ser usado com `auto`. |
| `--ai-content-remediation` | boolean flag | `false`* | Habilita M20 textual. `*` Pode vir de `SEARCHGEO_AI_CONTENT_REMEDIATION`. |
| `--no-ai-content-remediation` | boolean flag | — | Força M20 textual desligado. |
| `--web-performance` | boolean flag | `false`* | Habilita M21; não altera `SCORE-GEO-002`. |
| `--no-web-performance` | boolean flag | — | Força M21 desligado. |
| `--web-performance-max-pages N` | inteiro >= 0 | `10`* | `0` = todas as páginas. |
| `--web-performance-timeout-seconds` | número finito > 0 | `60`* | Timeout por request PageSpeed/CrUX; sem retry automático. |
| `--web-performance-field-source` | `auto`, `pagespeed`, `crux`, `none` | `auto`* | Política de field data. |
| `--lighthouse-categories LIST` | CSV | todas | `performance,accessibility,best-practices,seo`. |

## Providers de IA

| Valor CLI | Provider | Modelo default | Key | AUTO |
|---|---|---|---|---|
| `none` | sem IA | — | — | — |
| `openai` | OpenAI | `gpt-5.6-terra` | `OPENAI_API_KEY` | sim |
| `deepseek` | DeepSeek | `deepseek-v4-pro` | `DEEPSEEK_API_KEY` | sim |
| `mimo` | Xiaomi MiMo PAYG | `mimo-v2.5-pro` | `MIMO_API_KEY` | sim |
| `auto` | cadeia M18 | — | keys acima | OpenAI -> DeepSeek -> MiMo |
| `xai` / `grok` | xAI / Grok | `grok-4.6` | `XAI_API_KEY` | **não** |
| `qwen` | Alibaba Qwen | `qwen3.8-max` | `DASHSCOPE_API_KEY` | **não** |
| `gemini` | Google Gemini | `gemini-3.8-flash` | `GEMINI_API_KEY` | **não** |
| `anthropic` / `claude` | Anthropic Claude | `claude-sonnet-5` | `ANTHROPIC_API_KEY` | **não** |

Os quatro providers novos permanecem `PROVISIONAL` e só são executados quando selecionados explicitamente. Configurar suas keys não altera `auto`.

## Model IDs aceitos

```text
OPENAI:    gpt-5.6-sol | gpt-5.6-terra | gpt-5.6-luna
DEEPSEEK:  deepseek-v4-pro | deepseek-v4-flash
MIMO:      mimo-v2.5-pro | mimo-v2.5
XAI:       grok-4.6
QWEN:      qwen3.8-max | qwen3.8-flash
GEMINI:    gemini-3.8-flash
ANTHROPIC: claude-sonnet-5
```

Exemplo de override:

```powershell
searchgeo audit https://example.com --ai-provider qwen --ai-model qwen3.8-flash
```

## Exemplos

### Defaults: mobile, sem IA e sem M21

```powershell
searchgeo audit https://example.com --project "Exemplo"
```

### OpenAI

```powershell
$env:OPENAI_API_KEY = "<api-key>"
searchgeo audit https://example.com --ai-provider openai
```

### xAI / Grok

```powershell
$env:XAI_API_KEY = "<api-key>"
searchgeo audit https://example.com --ai-provider xai
```

### Qwen

```powershell
$env:DASHSCOPE_API_KEY = "<api-key>"
searchgeo audit https://example.com --ai-provider qwen
```

### Gemini

```powershell
$env:GEMINI_API_KEY = "<api-key>"
searchgeo audit https://example.com --ai-provider gemini
```

### Anthropic Claude

```powershell
$env:ANTHROPIC_API_KEY = "<api-key>"
searchgeo audit https://example.com --ai-provider anthropic
```

### AUTO — comportamento preservado

```powershell
searchgeo audit https://example.com --ai-provider auto
```

A cadeia é somente OpenAI -> DeepSeek -> MiMo. xAI/Qwen/Gemini/Anthropic não são candidatos AUTO enquanto provisórios.

### Mobile + IA + M20

```powershell
searchgeo audit https://example.com `
  --device-context mobile `
  --ai-provider openai `
  --ai-content-remediation
```

M20 não altera Score, Coverage, Confidence, RuleExecution ou Finding e exige revisão humana.

### M21 sem IA

```powershell
searchgeo audit https://example.com `
  --ai-provider none `
  --web-performance
```

M21 não chama LLM.

### URL_SET

```powershell
searchgeo audit `
  https://example.com/ `
  https://example.com/produto `
  https://example.com/faq `
  --project "Exemplo" `
  --max-pages 3
```

### Arquivo

```powershell
searchgeo audit --urls-file .\urls.txt --project "Exemplo"
```

## Variáveis de IA

```text
OPENAI_API_KEY
DEEPSEEK_API_KEY
MIMO_API_KEY
XAI_API_KEY
DASHSCOPE_API_KEY
GEMINI_API_KEY
ANTHROPIC_API_KEY

SEARCHGEO_OPENAI_MODEL
SEARCHGEO_DEEPSEEK_MODEL
SEARCHGEO_MIMO_MODEL
SEARCHGEO_XAI_MODEL
SEARCHGEO_QWEN_MODEL
SEARCHGEO_GEMINI_MODEL
SEARCHGEO_ANTHROPIC_MODEL

SEARCHGEO_XAI_ENDPOINT
SEARCHGEO_QWEN_ENDPOINT
SEARCHGEO_GEMINI_ENDPOINT
SEARCHGEO_ANTHROPIC_ENDPOINT

SEARCHGEO_AI_TIMEOUT_SECONDS
SEARCHGEO_AI_CONTENT_REMEDIATION
```

Endpoints customizados dos providers de extensão devem ser compatíveis e oficialmente documentados pelo fornecedor. Qwen pode exigir endpoint específico de região/workspace.

## Isolamento e falhas

Provider explícito sem key -> `NOT_CONFIGURED`, zero request. Nenhuma key de outro provider é reutilizada. Provider explícito não faz cross-provider fallback.

Falhas técnicas/contratuais podem colocar o provider em `QUARANTINED_FOR_AUDIT`; não há retry automático silencioso após timeout.

Falha de provider é limitação operacional e não Finding do website.

## Web Performance

Variáveis principais:

```text
SEARCHGEO_WEB_PERFORMANCE
SEARCHGEO_WEB_PERFORMANCE_MAX_PAGES
SEARCHGEO_WEB_PERFORMANCE_TIMEOUT_SECONDS
SEARCHGEO_WEB_PERFORMANCE_FIELD_SOURCE
SEARCHGEO_LIGHTHOUSE_CATEGORIES
SEARCHGEO_PAGESPEED_API_KEY
SEARCHGEO_CRUX_API_KEY
```

M21 permanece separado do `SCORE-GEO-002` e da camada de LLM. Consulte [CONFIGURATION.md](CONFIGURATION.md).

## Documentação relacionada

- [AI_GUIDE.md](AI_GUIDE.md) — regras de uso e compatibilidade de IA.
- [AI_PROVIDER_EXTENSIONS.md](AI_PROVIDER_EXTENSIONS.md) — xAI, Qwen, Gemini e Anthropic, endpoints e smoke.
- [GOOGLE_API_KEYS.md](GOOGLE_API_KEYS.md) — chaves PageSpeed/CrUX.
- [SMOKE_TEST.md](SMOKE_TEST.md) — validação operacional antes de merge/release.
