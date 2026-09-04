# CONFIGURATION.md

Configuração operacional do SearchGEO Readiness Auditor.

## Defaults

| Configuração | Default |
|---|---|
| idioma | `pt-BR` |
| mercado | `BR` |
| `--max-pages` | `100` |
| `--audits-root` | `audits` |
| `--device-context` | `mobile` |
| `--ai-provider` | `none` |
| `--ai-content-remediation` | `false` |
| timeout IA | `180` s |
| `--web-performance` | `false` |
| `--web-performance-max-pages` | `10` |
| `--web-performance-timeout-seconds` | `60` s |
| `--web-performance-field-source` | `auto` |
| `--lighthouse-categories` | `performance,accessibility,best-practices,seo` |

## Device context

`SEARCHGEO_DEVICE_CONTEXT`: `mobile`, `desktop`, `both`. Precedência flag -> ambiente -> `mobile`.

A seleção limita M3 e, por consequência, M7/M20 aos snapshots escolhidos. A mesma seleção limita M21 aos snapshots materializados.

## IA — regra de compatibilidade

Não trate “tenho plano/créditos” como “tenho API utilizável”. Valide produto/plano, tipo de credencial, endpoint, saldo/quota/permissão, região/workspace quando aplicável e model access.

| Provider | CLI | Credencial | Modelo default | Estado |
|---|---|---|---|---|
| OpenAI | `openai` | `OPENAI_API_KEY` | `gpt-5.6-terra` | `QUALIFIED` |
| DeepSeek | `deepseek` | `DEEPSEEK_API_KEY` | `deepseek-v4-pro` | baseline M18 `PROVISIONAL` |
| MiMo PAYG | `mimo` | `MIMO_API_KEY` (`sk-...`) | `mimo-v2.5-pro` | baseline M18 `PROVISIONAL` |
| xAI/Grok | `xai` / `grok` | `XAI_API_KEY` | `grok-4.6` | extensão `PROVISIONAL`, explicit-only |
| Qwen | `qwen` | `DASHSCOPE_API_KEY` | `qwen3.8-max` | extensão `PROVISIONAL`, explicit-only |
| Gemini | `gemini` | `GEMINI_API_KEY` | `gemini-3.8-flash` | extensão `PROVISIONAL`, explicit-only |
| Anthropic/Claude | `anthropic` / `claude` | `ANTHROPIC_API_KEY` | `claude-sonnet-5` | extensão `PROVISIONAL`, explicit-only |

Detalhes de planos/contratos: [AI_GUIDE.md](AI_GUIDE.md). Detalhes dos quatro novos adapters: [AI_PROVIDER_EXTENSIONS.md](AI_PROVIDER_EXTENSIONS.md).

### Sem IA

```powershell
searchgeo audit https://example.com --ai-provider none
```

Nenhuma chamada de LLM externa. JSON-LD determinístico M20 continua disponível. M21 também permanece desligado por default.

### OpenAI

```powershell
$env:OPENAI_API_KEY = "<chave-da-API-Platform>"
searchgeo audit https://example.com --ai-provider openai
```

Modelos:

```text
gpt-5.6-sol
gpt-5.6-terra
gpt-5.6-luna
```

Default: `gpt-5.6-terra`.

### DeepSeek

```powershell
$env:DEEPSEEK_API_KEY = "<chave-da-DeepSeek-API>"
searchgeo audit https://example.com --ai-provider deepseek
```

Modelos: `deepseek-v4-pro`, `deepseek-v4-flash`. Default `deepseek-v4-pro`.

### MiMo PAYG

```powershell
$env:MIMO_API_KEY = "<chave-sk-PAYG>"
searchgeo audit https://example.com --ai-provider mimo
```

Modelos: `mimo-v2.5-pro`, `mimo-v2.5`. Default `mimo-v2.5-pro`.

O adapter usa `https://api.xiaomimimo.com/v1/responses`. **Token Plan `tp-...` não é suportado** por este adapter.

### xAI / Grok

```powershell
$env:XAI_API_KEY = "<xai-api-key>"
searchgeo audit https://example.com --ai-provider xai
```

Alias `grok`. Modelo suportado: `grok-4.6`.

Variáveis:

```text
SEARCHGEO_XAI_MODEL
SEARCHGEO_XAI_ENDPOINT
```

Endpoint default: `https://api.x.ai/v1/responses`.

### Alibaba Qwen

```powershell
$env:DASHSCOPE_API_KEY = "<model-studio-api-key>"
searchgeo audit https://example.com --ai-provider qwen
```

Modelos: `qwen3.8-max`, `qwen3.8-flash`. Default `qwen3.8-max`.

Variáveis:

```text
SEARCHGEO_QWEN_MODEL
SEARCHGEO_QWEN_ENDPOINT
```

Endpoint default do adapter: `https://dashscope-us.aliyuncs.com/compatible-mode/v1/chat/completions`.

Para outra região/workspace Alibaba, `SEARCHGEO_QWEN_ENDPOINT` deve apontar para o endpoint OpenAI-compatible daquele deployment; a key deve pertencer à mesma região/workspace.

### Google Gemini

```powershell
$env:GEMINI_API_KEY = "<gemini-api-key>"
searchgeo audit https://example.com --ai-provider gemini
```

Modelo: `gemini-3.8-flash`.

Variáveis:

```text
SEARCHGEO_GEMINI_MODEL
SEARCHGEO_GEMINI_ENDPOINT
```

Endpoint default: `https://generativelanguage.googleapis.com/v1beta/interactions`.

`GEMINI_API_KEY` não é `SEARCHGEO_PAGESPEED_API_KEY` nem `SEARCHGEO_CRUX_API_KEY`.

### Anthropic Claude

```powershell
$env:ANTHROPIC_API_KEY = "<anthropic-api-key>"
searchgeo audit https://example.com --ai-provider anthropic
```

Alias `claude`. Modelo: `claude-sonnet-5`.

Variáveis:

```text
SEARCHGEO_ANTHROPIC_MODEL
SEARCHGEO_ANTHROPIC_ENDPOINT
```

Endpoint default: `https://api.anthropic.com/v1/messages`.

### Override de modelo por CLI

Provider explícito pode receber:

```powershell
searchgeo audit https://example.com --ai-provider qwen --ai-model qwen3.8-flash
```

Model ID fora da allow-list do SearchGEO é rejeitado antes da chamada.

### AUTO — contrato preservado

```powershell
searchgeo audit https://example.com --ai-provider auto
```

A cadeia continua **exatamente**:

```text
OpenAI -> DeepSeek -> MiMo
```

xAI, Qwen, Gemini e Anthropic/Claude não entram em `AUTO`, mesmo com suas keys configuradas. São explicit-only enquanto `PROVISIONAL`.

## Isolamento de credenciais

Cada adapter usa exclusivamente a credencial do próprio provider:

```text
OPENAI_API_KEY
DEEPSEEK_API_KEY
MIMO_API_KEY
XAI_API_KEY
DASHSCOPE_API_KEY
GEMINI_API_KEY
ANTHROPIC_API_KEY
```

Ausência da key do provider explícito -> `NOT_CONFIGURED`, zero request. Nenhuma key de outro provider é utilizada como fallback implícito.

Credenciais M21 são independentes:

```text
SEARCHGEO_PAGESPEED_API_KEY
SEARCHGEO_CRUX_API_KEY
```

Para criação correta das chaves Google de PageSpeed/CrUX, consulte [GOOGLE_API_KEYS.md](GOOGLE_API_KEYS.md).

## Timeout IA

```text
SEARCHGEO_AI_TIMEOUT_SECONDS
```

Default `180` segundos. Deve ser número finito > 0. Sem retry automático após timeout. M20 reutiliza o timeout do provider.

## M20 textual

`SEARCHGEO_AI_CONTENT_REMEDIATION`, default `false`; aceita `true/false`, `1/0`, `yes/no`, `on/off`.

Precedência: `--ai-content-remediation` / `--no-ai-content-remediation` -> ambiente -> `false`.

M20:

- roda depois de findings/scoring;
- não altera RuleExecution/Finding/Score/Coverage/Confidence;
- não é disparado por Confidence LOW isolado;
- usa apenas findings/evidências persistidos;
- exige revisão humana;
- não aplica/publica texto;
- respeita quarantine do provider.

Com `--ai-provider none`, M20 textual fica `NOT_CONFIGURED` sem abortar; JSON-LD determinístico permanece.

## M21 — Core Web Vitals e Lighthouse

M21 é evidência externa complementar. Não substitui nem recalcula `SCORE-GEO-002`.

Ativação:

```powershell
searchgeo audit https://example.com --web-performance
```

Variáveis/flags:

| Configuração | Default | Regra |
|---|---:|---|
| `SEARCHGEO_WEB_PERFORMANCE` | `false` | liga/desliga M21 |
| `SEARCHGEO_WEB_PERFORMANCE_MAX_PAGES` | `10` | `0` = todas as páginas |
| `SEARCHGEO_WEB_PERFORMANCE_TIMEOUT_SECONDS` | `60` | > 0, sem retry automático |
| `SEARCHGEO_WEB_PERFORMANCE_FIELD_SOURCE` | `auto` | `auto`, `pagespeed`, `crux`, `none` |
| `SEARCHGEO_LIGHTHOUSE_CATEGORIES` | todas | `performance,accessibility,best-practices,seo` |
| `SEARCHGEO_PAGESPEED_API_KEY` | — | chave PageSpeed opcional conforme uso/quota |
| `SEARCHGEO_CRUX_API_KEY` | — | necessária para CrUX direto |

Flags equivalentes:

```text
--web-performance / --no-web-performance
--web-performance-max-pages N
--web-performance-timeout-seconds SECONDS
--web-performance-field-source auto|pagespeed|crux|none
--lighthouse-categories LIST
```

Field source:

- `auto`: usa CrUX do PageSpeed e, se necessário/configurado, CrUX direto;
- `pagespeed`: usa apenas field data retornado pelo PageSpeed;
- `crux`: usa CrUX API direta para field data;
- `none`: desabilita field data e mantém Lighthouse lab.

Status operacionais M21: `DISABLED`, `NO_CONTEXTS`, `SUCCESS`, `PARTIAL`, `UNAVAILABLE`.

Falha/quota/timeout/ausência de amostra de M21 não são findings do website.

Core Web Vitals de boa experiência no p75:

```text
LCP <= 2500 ms
INP <= 200 ms
CLS <= 0.10
```

M21 adiciona **zero chamadas de LLM**.

## Telemetria de IA

`report/ai-usage.html` e `ai_provider_attempts` registram, quando disponíveis, provider/model, status, duração, tokens e diagnóstico sanitizado.

Os providers de extensão normalizam usage, mas enquanto `PROVISIONAL` seu catálogo de preço não é promovido automaticamente para `provider_pricing_catalog`; o custo pode aparecer indisponível para evitar estimativa incorreta por região/tier/cache/promoção.

## Report

```text
report/
├─ index.html
├─ mobile.html
├─ desktop.html
├─ remediation.html
├─ content-suggestions.html
├─ web-performance.html
├─ ai-usage.html
├─ references.html
└─ css/site.css
```

## Smoke humano obrigatório para extensions

Antes de promover xAI/Qwen/Gemini/Anthropic para AUTO ou `QUALIFIED`, siga [AI_PROVIDER_EXTENSIONS.md](AI_PROVIDER_EXTENSIONS.md). O smoke deve validar também que OpenAI/DeepSeek/MiMo mantêm a baseline.

## Fora do contrato público

Sem backend remoto, execução distribuída, retry automático, publicação automática de conteúdo ou mudança silenciosa de provider.

Endpoints customizados dos novos providers são permitidos somente por variável explícita de ambiente e devem ser compatíveis/documentados pelo respectivo fornecedor. MiMo Token Plan `tp-...` continua fora do contrato.
