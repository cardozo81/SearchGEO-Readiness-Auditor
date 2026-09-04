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
| `--synthetic-apdex` | `false` |
| `--apdex-threshold-seconds` | nenhum; obrigatório quando M23 ON |
| `--apdex-samples-per-context` | `100` quando M23 ON |
| `--apdex-max-attempts-per-context` | `ceil(1.25 × alvo)` |
| `--apdex-max-pages` | `1` |
| `--apdex-timeout-seconds` | `max(45, 4T+5)` |
| `--apdex-delay-seconds` | `1` s |
| `--apdex-concurrency` | `1` |

## Device context

`SEARCHGEO_DEVICE_CONTEXT`: `mobile`, `desktop`, `both`.

Precedência:

```text
flag CLI -> ambiente -> mobile
```

A seleção limita M3 e, por consequência, M7/M20 aos snapshots escolhidos. M21 e M23 também operam somente sobre contextos materializados.

## Antes de configurar IA

Não trate “tenho plano/créditos” como “tenho API utilizável”. Valide produto/plano, tipo de credencial, endpoint, saldo/quota/permissão/model access e termos do workload automatizado.

| Provider | Aceito | Não confundir |
|---|---|---|
| OpenAI | API key da API Platform com billing/quota | ChatGPT/Créditos ChatGPT, billing separado |
| DeepSeek | DeepSeek API com saldo | chave sem saldo disponível |
| MiMo | PAYG `sk-...` para `https://api.xiaomimimo.com/v1` | Token Plan `tp-...` com Base URL/créditos separados |
| xAI | API key xAI compatível | acesso ao produto Grok sem credencial/API compatível |
| Qwen | DashScope/Model Studio compatível | assinatura de produto final |
| Gemini | Gemini API key compatível | credenciais Google de outros serviços |
| Anthropic | Anthropic API key compatível | assinatura Claude |

Detalhes: [AI_GUIDE.md](AI_GUIDE.md) e [AI_PROVIDER_EXTENSIONS.md](AI_PROVIDER_EXTENSIONS.md).

## Provider registry

O registry canônico define providers, aliases, envs, modelos, qualification e elegibilidade AUTO.

Providers concretos:

```text
openai
deepseek
mimo
xai
qwen
gemini
anthropic
```

Aliases:

```text
grok   -> xai
claude -> anthropic
```

AUTO permanece:

```text
OpenAI -> DeepSeek -> MiMo
```

xAI/Qwen/Gemini/Anthropic são `PROVISIONAL`, `explicit-only`, `auto_eligible=false`.

## IA desabilitada

```powershell
searchgeo audit https://example.com --ai-provider none
```

Nenhuma chamada de IA externa. JSON-LD determinístico M20 continua disponível. M21 e M23 permanecem OFF por default.

## Providers e modelos

### OpenAI

```powershell
$env:OPENAI_API_KEY = "<chave-da-API-Platform>"
searchgeo audit https://example.com --ai-provider openai
```

Default `gpt-5.6-terra`.

### DeepSeek

```powershell
$env:DEEPSEEK_API_KEY = "<chave-da-DeepSeek-API>"
searchgeo audit https://example.com --ai-provider deepseek
```

Default `deepseek-v4-pro`.

### MiMo

```powershell
$env:MIMO_API_KEY = "<chave-sk-PAYG>"
searchgeo audit https://example.com --ai-provider mimo
```

Default `mimo-v2.5-pro`; adapter PAYG. Não configure Token Plan `tp-...` para esse adapter.

### Extensions explícitas

```powershell
$env:XAI_API_KEY = "<key>"
searchgeo audit https://example.com --ai-provider xai

$env:DASHSCOPE_API_KEY = "<key>"
searchgeo audit https://example.com --ai-provider qwen

$env:GEMINI_API_KEY = "<key>"
searchgeo audit https://example.com --ai-provider gemini

$env:ANTHROPIC_API_KEY = "<key>"
searchgeo audit https://example.com --ai-provider anthropic
```

Esses providers não entram em AUTO enquanto `PROVISIONAL/explicit-only`.

## Isolamento de credenciais

Cada adapter usa exclusivamente a credencial do próprio provider. Uma key não preenche ausência de outra.

IA:

```text
OPENAI_API_KEY
DEEPSEEK_API_KEY
MIMO_API_KEY
XAI_API_KEY
DASHSCOPE_API_KEY
GEMINI_API_KEY
ANTHROPIC_API_KEY
```

M21:

```text
SEARCHGEO_PAGESPEED_API_KEY
SEARCHGEO_CRUX_API_KEY
```

M23 não exige API key própria.

As chaves Google M21 não são credenciais de IA. Consulte [GOOGLE_API_KEYS.md](GOOGLE_API_KEYS.md).

## Modelos

```text
OPENAI:    gpt-5.6-sol | gpt-5.6-terra | gpt-5.6-luna
DEEPSEEK:  deepseek-v4-pro | deepseek-v4-flash
MIMO:      mimo-v2.5-pro | mimo-v2.5
XAI:       grok-4.6
QWEN:      qwen3.8-max | qwen3.8-flash
GEMINI:    gemini-3.8-flash
ANTHROPIC: claude-sonnet-5
```

Model ID aceito não garante acesso da conta/plano.

## Timeout IA

`SEARCHGEO_AI_TIMEOUT_SECONDS`, default `180` s, número finito > 0. Sem retry automático. M20 reutiliza o timeout do provider.

Esse timeout é independente de M21 e M23.

## M20 textual

`SEARCHGEO_AI_CONTENT_REMEDIATION`, default `false`; aceita `true/false`, `1/0`, `yes/no`, `on/off`.

Precedência:

```text
--ai-content-remediation / --no-ai-content-remediation
-> SEARCHGEO_AI_CONTENT_REMEDIATION
-> false
```

M20:

- roda depois de findings/scoring;
- não altera RuleExecution/Finding/Score/Coverage/Confidence;
- não é disparado por Confidence LOW isolado;
- usa apenas findings contentuais/semânticos elegíveis + evidências;
- exige revisão humana;
- não aplica/publica texto;
- reutiliza provider/model/timeout e respeita quarantine.

## JSON-LD

Para cada snapshot auditado, M20 revisa Structured Data. Se ausente, pode propor `WebPage` com URL, idioma, title e description observados/persistidos. Se existente, aponta problemas verificáveis sem reescrever destrutivamente o graph.

JSON-LD é opcional/reforço, não requisito universal GEO nem garantia de rich result.

## M21 — Core Web Vitals e Lighthouse

M21 é **evidência externa complementar** e não recalcula `SCORE-GEO-002`.

Default:

```text
SEARCHGEO_WEB_PERFORMANCE=false
```

Ativação:

```powershell
searchgeo audit https://example.com --web-performance
```

Precedência:

1. `--web-performance` / `--no-web-performance`;
2. `SEARCHGEO_WEB_PERFORMANCE`;
3. `false`.

### Limite de páginas

```text
SEARCHGEO_WEB_PERFORMANCE_MAX_PAGES
```

Default `10`; `0` significa todas as páginas auditadas.

### Timeout

```text
SEARCHGEO_WEB_PERFORMANCE_TIMEOUT_SECONDS
```

Default `60` s por request externo; número finito > 0; sem retry automático.

### Lighthouse categories

```text
SEARCHGEO_LIGHTHOUSE_CATEGORIES
```

Valores suportados:

```text
performance
accessibility
best-practices
seo
```

### PageSpeed / CrUX

PageSpeed key opcional:

```powershell
$env:SEARCHGEO_PAGESPEED_API_KEY = "<google-api-key>"
```

CrUX direto:

```powershell
$env:SEARCHGEO_CRUX_API_KEY = "<google-api-key>"
```

Fonte de field data:

```text
auto
pagespeed
crux
none
```

`crux` exige `SEARCHGEO_CRUX_API_KEY`.

### Status M21

```text
DISABLED
NO_CONTEXTS
SUCCESS
PARTIAL
UNAVAILABLE
```

Esses estados qualificam a coleta; não são Finding e não alteram `SCORE-GEO-002`.

### Core Web Vitals

```text
LCP <= 2500 ms
INP <= 200 ms
CLS <= 0.10
```

Estados:

```text
PASS
FAIL
INCOMPLETE
UNAVAILABLE
```

Ausência de amostra não vira `FAIL`.

## M22 — domínios separados

M22 reutiliza artifacts M21 para projetar:

- `accessibility.html`;
- diagnósticos técnicos em `web-performance.html`.

M22 não faz segunda chamada Google, não inventa selector/snippet ausente e não declara conformidade WCAG com base apenas em Lighthouse.

M22 também não calcula Apdex a partir de Lighthouse/CrUX. Após M23, essa fronteira continua válida: Apdex é calculado somente pelo domínio M23 quando explicitamente habilitado.

## M23 — Synthetic Navigation Apdex

M23 é default OFF e mede repetidamente uma Task explícita de navegação em Chromium.

### Ativação

```powershell
searchgeo audit https://example.com `
  --synthetic-apdex `
  --apdex-threshold-seconds 1.5
```

`T` é obrigatório quando M23 está ON.

Precedência:

```text
CLI -> ambiente -> defaults
```

### Variáveis

```text
SEARCHGEO_SYNTHETIC_APDEX
SEARCHGEO_APDEX_THRESHOLD_SECONDS
SEARCHGEO_APDEX_SAMPLES_PER_CONTEXT
SEARCHGEO_APDEX_MAX_ATTEMPTS_PER_CONTEXT
SEARCHGEO_APDEX_MAX_PAGES
SEARCHGEO_APDEX_TIMEOUT_SECONDS
SEARCHGEO_APDEX_DELAY_SECONDS
SEARCHGEO_APDEX_CONCURRENCY
```

### Defaults e validação

| Item | Default | Validação |
|---|---:|---|
| enabled | OFF | opt-in |
| `T` | nenhum | > 0 e explícito |
| amostras válidas/contexto | `100` | >= 1 |
| max attempts | `ceil(1.25 × alvo)` | >= alvo |
| max pages | `1` | >= 0; `0` = todas |
| timeout | `max(45, 4T+5)` | estritamente > `4T` |
| delay | `1` s | >= 0 |
| concurrency | `1` | 1–2 |

### Task e profiles

```text
NAVIGATION_LOAD
início = imediatamente antes de page.goto
fim    = conclusão de wait_until=load
```

Cada amostra usa BrowserContext novo, cache desabilitado e profile CPU/rede determinístico/versionado.

### Fórmula

```text
Apdex = (Satisfied + 0.5 × Tolerating) / Total de amostras válidas

Satisfied  <= T
Tolerating > T e <= 4T
Frustrated > 4T
```

Timeout/erro de navegação ou erro de aplicação/servidor é `FRUSTRATED` quando o profile foi aplicado. Falha da ferramenta/profile é amostra inválida fora do denominador.

### Small group

Grupo normal: >= 100 amostras válidas por URL/device. Grupos de 1–99 recebem `*` e são diagnósticos de grupo pequeno.

Um smoke 5/5 pode terminar `PARTIAL` por small group sem significar falha operacional.

### Carga e custo

M23 produz:

```text
0 chamadas LLM adicionais
0 tokens IA
0 chamadas PageSpeed/CrUX adicionais
```

Não há API paga própria no contrato atual. Porém há consumo local de CPU/RAM/tempo e **tráfego HTTP real contra o alvo**. Cada navegação pode carregar muitos subrecursos.

Antes de run de 100 amostras em produção, valide autorização, capacidade e janela operacional.

Detalhes: [SYNTHETIC_APDEX.md](SYNTHETIC_APDEX.md).

## Log operacional persistente

Cada workspace pode materializar:

```text
audits/<AUD-ID>/logs/audit.log
```

JSONL sanitizado e fail-open. Pode registrar ciclo principal, tentativas M21 e progresso M23. Chaves, Authorization headers, tokens e passwords não podem ser registrados.

## Provider sem credencial

Provider explícito sem key fica `NOT_CONFIGURED` e não chama API. AUTO exclui provider sem key. Extensions sem key ficam indisponíveis e não entram em AUTO.

Credencial de produto incompatível não deve ser considerada operacionalmente válida só porque a variável existe.

## Report

```text
report/
├─ index.html
├─ mobile.html
├─ desktop.html
├─ remediation.html
├─ content-suggestions.html
├─ accessibility.html
├─ web-performance.html
├─ apdex.html              # quando M23 materializado
├─ ai-usage.html
├─ references.html
└─ css/site.css
```

- `web-performance.html`: M21/M22;
- `accessibility.html`: M22;
- `apdex.html`: M23;
- `ai-usage.html`: M18/M20.

## Fora do contrato público

Sem web/backend, banco remoto, Docker daemon, execução distribuída, retry automático, publicação automática de conteúdo, criação automática de JSON-LD no website ou MiMo Token Plan `tp-...` no adapter PAYG atual.

M23 não é RUM/APM de usuários reais e não deve ser apresentado como experiência real de produção. Para Apdex de usuários reais é necessária telemetria de aplicação/RUM/APM adequada.
