# COMPATIBILITY.md

## Runtime

| Item | Compatibilidade atual |
|---|---|
| CPython | `>=3.13,<3.14` |
| Windows + PowerShell | target operacional principal |
| Playwright | `>=1.57,<2` |
| Chromium | obrigatório para rendering real |
| SQLite | embarcado/local |
| Filesystem | local e gravável |
| HTTP/HTTPS egress | targets/providers externos |
| Docker / web server | não requeridos |

## Dispositivos

CLI: `mobile`, `desktop`, `both`; default `mobile`. Snapshot não selecionado não é materializado e não pode gerar chamada M7/M20.

## Providers semânticos

| CLI | Provider | Estado | AUTO |
|---|---|---|---|
| `none` | sem IA | suportado/default | — |
| `openai` | OpenAI | suportado / `QUALIFIED` | sim |
| `deepseek` | DeepSeek | suportado / baseline `PROVISIONAL` | sim |
| `mimo` | Xiaomi MiMo PAYG | suportado / baseline `PROVISIONAL` | sim |
| `auto` | routing M18 | suportado | OpenAI -> DeepSeek -> MiMo |
| `xai`, `grok` | xAI / Grok | `PROVISIONAL`, explicit-only | **não** |
| `qwen` | Alibaba Qwen | `PROVISIONAL`, explicit-only | **não** |
| `gemini` | Google Gemini | `PROVISIONAL`, explicit-only | **não** |
| `anthropic`, `claude` | Anthropic Claude | `PROVISIONAL`, explicit-only | **não** |

A presença das chaves dos providers de extensão não muda o conteúdo ou a ordem do `AUTO` homologado.

## Produto/plano/credencial

| Provider | Produto/credencial compatível | Observação |
|---|---|---|
| OpenAI | API Platform + `OPENAI_API_KEY` + billing/quota/model access | assinatura/créditos ChatGPT não equivalem a saldo de API |
| DeepSeek | DeepSeek API + `DEEPSEEK_API_KEY` | key não garante saldo/quota |
| MiMo | PAYG `sk-...` + `MIMO_API_KEY` | Token Plan `tp-...` não é suportado pelo adapter atual |
| xAI | xAI API + `XAI_API_KEY` | acesso ao modelo precisa existir na conta |
| Qwen | Model Studio/DashScope + `DASHSCOPE_API_KEY` | key e endpoint devem pertencer à mesma região/workspace |
| Gemini | Gemini Developer API + `GEMINI_API_KEY` | independente das chaves PageSpeed/CrUX |
| Anthropic | Claude API + `ANTHROPIC_API_KEY` | requer acesso ao modelo selecionado |

Credenciais são isoladas por provider; nenhuma chave pode ser reutilizada implicitamente em endpoint de outro fornecedor.

## Modelos aceitos

```text
OPENAI:    gpt-5.6-sol | gpt-5.6-terra | gpt-5.6-luna
DEEPSEEK:  deepseek-v4-pro | deepseek-v4-flash
MIMO:      mimo-v2.5-pro | mimo-v2.5
XAI:       grok-4.6
QWEN:      qwen3.8-max | qwen3.8-flash
GEMINI:    gemini-3.8-flash
ANTHROPIC: claude-sonnet-5
```

Model ID aceito não garante acesso comercial ou quota.

## Endpoints dos providers de extensão

Defaults:

```text
XAI        https://api.x.ai/v1/responses
QWEN       https://dashscope-us.aliyuncs.com/compatible-mode/v1/chat/completions
GEMINI     https://generativelanguage.googleapis.com/v1beta/interactions
ANTHROPIC  https://api.anthropic.com/v1/messages
```

Overrides explícitos:

```text
SEARCHGEO_XAI_ENDPOINT
SEARCHGEO_QWEN_ENDPOINT
SEARCHGEO_GEMINI_ENDPOINT
SEARCHGEO_ANTHROPIC_ENDPOINT
```

Qwen pode exigir endpoint específico da região/workspace. Endpoint customizado deve ser compatível e documentado pelo fornecedor.

## M20

M20 textual é default OFF. OpenAI/DeepSeek/MiMo continuam pelo router M20 legado. xAI/Qwen/Gemini/Anthropic possuem adapters aditivos e só são usados quando o respectivo provider é explicitamente selecionado.

Provider quarantined no M7 não é reativado para M20.

## Custos/telemetria

Todos os providers podem registrar `ProviderAttempt` e usage quando retornado pela API. O catálogo homologado de preços M18 não é ampliado automaticamente pelos providers de extensão enquanto estiverem `PROVISIONAL`; nesses casos `estimated_cost` pode ficar indisponível para evitar estimativa incorreta por região/tier/cache/promoção.

## Saída

```text
<AUD-ID>/audit.db
<AUD-ID>/artifacts/
<AUD-ID>/report/index.html
<AUD-ID>/report/remediation.html
<AUD-ID>/report/content-suggestions.html
<AUD-ID>/report/web-performance.html
<AUD-ID>/report/ai-usage.html
<AUD-ID>/report/references.html
<AUD-ID>/report/css/site.css
```

`mobile.html`/`desktop.html` são condicionais.

## Structured Data / M20

Parser operacional específico: JSON-LD. M20 pode propor baseline JSON-LD quando ausente e revisar markup existente. Isso é advisory; não publica alteração no site. JSON-LD continua opcional/reforço e ausência legítima não é FAIL universal.

## Segurança

Provider externo requer credencial do produto correto, endpoint compatível, saldo/quota/permissão e termos que autorizem o workload. Secrets não devem aparecer em artifacts/report/logs.

## Gate dos providers novos

xAI/Qwen/Gemini/Anthropic permanecem `PROVISIONAL` e fora de `AUTO` até conclusão do smoke humano definido em [AI_PROVIDER_EXTENSIONS.md](AI_PROVIDER_EXTENSIONS.md) e [SMOKE_TEST.md](SMOKE_TEST.md).

## Fora do escopo

Executável standalone sem Python, banco remoto, execução distribuída, web backend, Docker oficial, publicação/aplicação automática de conteúdo/Structured Data e MiMo Token Plan `tp-...`.
