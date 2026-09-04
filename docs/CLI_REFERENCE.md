# CLI_REFERENCE.md

Referência operacional da linha de comando do SearchGEO Readiness Auditor.

## Sintaxe global

```text
searchgeo [--config PATH] [--version] [-h|--help] audit [target ...] [opções]
```

## Parâmetros globais

| Parâmetro | Default | Descrição |
|---|---|---|
| `-h`, `--help` | — | Ajuda do comando atual. |
| `--version` | — | Exibe versão do package. |
| `--config PATH` | — | Caminho de `searchgeo.toml`; configuração local compatível com o pipeline. |

## `searchgeo audit`

Superfície pública consolidada:

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
  [--synthetic-apdex | --no-synthetic-apdex]
  [--apdex-threshold-seconds T]
  [--apdex-samples-per-context N]
  [--apdex-max-attempts-per-context N]
  [--apdex-max-pages N]
  [--apdex-timeout-seconds SECONDS]
  [--apdex-delay-seconds SECONDS]
  [--apdex-concurrency N]
```

## Glossário completo de argumentos

### Entrada e escopo

| Argumento | Tipo / valores | Default | Regra |
|---|---|---|---|
| `target` | domínio ou URL HTTP(S), zero ou mais posicionais | — | Ao menos um target deve vir por posição ou `--urls-file`. Dois ou mais formam `URL_SET`. |
| `--urls-file PATH` | arquivo UTF-8 | — | Uma URL/domínio por linha; vazias e linhas iniciadas por `#` são ignoradas. |
| `--project TEXT` | texto | hostname/target | Nome humano da auditoria. |
| `--language CODE` | texto | `pt-BR` | Contexto primário de idioma. |
| `--market CODE` | texto | `BR` | Contexto de mercado. |
| `--max-pages N` | inteiro > 0 | `100` | Limite determinístico da auditoria. Em `URL_SET`, deve ser >= quantidade de URLs únicas fornecidas. |
| `--audits-root PATH` | diretório | `audits` | Raiz local dos workspaces. |
| `--device-context` | `mobile`, `desktop`, `both` | `mobile`* | Controla rendering e contextos M7/M20/M21/M23. `*` Pode vir de `SEARCHGEO_DEVICE_CONTEXT`. |

### IA e M20

| Argumento | Valores | Default | Regra |
|---|---|---|---|
| `--ai-provider` | `none`, `openai`, `deepseek`, `mimo`, `auto`, `xai`, `grok`, `qwen`, `gemini`, `anthropic`, `claude` | `none` | Provider semântico. `grok` resolve para xAI; `claude` resolve para Anthropic. Extensions são explícitas e fora de AUTO. |
| `--ai-model MODEL_ID` | model ID suportado | default do provider | Somente provider explícito. Não combinar com `auto`. |
| `--ai-content-remediation` | boolean flag | `false`* | Habilita sugestões textuais M20 para findings elegíveis. |
| `--no-ai-content-remediation` | boolean flag | — | Força M20 textual OFF. |

Precedência M20: CLI → `SEARCHGEO_AI_CONTENT_REMEDIATION` → `false`.

### M21 — Web Performance externo

| Argumento | Valores | Default | Regra |
|---|---|---|---|
| `--web-performance` | boolean flag | `false`* | Habilita M21 PageSpeed/Lighthouse + field data conforme política. Não altera `SCORE-GEO-002`. |
| `--no-web-performance` | boolean flag | — | Força M21 OFF. |
| `--web-performance-max-pages N` | inteiro >= 0 | `10`* | Páginas lógicas enviadas ao M21; `0` = todas. |
| `--web-performance-timeout-seconds SECONDS` | número finito > 0 | `60`* | Timeout por request PageSpeed/CrUX; sem retry automático. |
| `--web-performance-field-source` | `auto`, `pagespeed`, `crux`, `none` | `auto`* | Política de field data. `crux` exige `SEARCHGEO_CRUX_API_KEY`. |
| `--lighthouse-categories LIST` | CSV | `performance,accessibility,best-practices,seo`* | Categorias Lighthouse suportadas. |

Precedência M21: CLI → variáveis `SEARCHGEO_WEB_PERFORMANCE*` → defaults.

### M23 — Synthetic Navigation Apdex

| Argumento | Tipo / valores | Default quando ON | Regra |
|---|---|---:|---|
| `--synthetic-apdex` | boolean flag | OFF | Habilita M23. |
| `--no-synthetic-apdex` | boolean flag | — | Força M23 OFF quando o ambiente o habilitaria. |
| `--apdex-threshold-seconds T` | número finito > 0 | nenhum | `T` é obrigatório quando M23 está ON. |
| `--apdex-samples-per-context N` | inteiro >= 1 | `100` | Alvo de amostras **válidas** por URL/device. |
| `--apdex-max-attempts-per-context N` | inteiro >= alvo | `ceil(1.25 × alvo)` | Orçamento para substituir amostras inválidas de ferramenta/profile. |
| `--apdex-max-pages N` | inteiro >= 0 | `1` | Máximo de páginas M23; `0` = todas as páginas auditadas. |
| `--apdex-timeout-seconds SECONDS` | número finito > `4T` | `max(45, 4T+5)` | Timeout de cada navegação sintética. |
| `--apdex-delay-seconds SECONDS` | número finito >= 0 | `1` | Intervalo mínimo determinístico entre inícios de amostras. |
| `--apdex-concurrency N` | inteiro `1` ou `2` | `1` | Workers sintéticos; máximo `2` para limitar carga. |

Precedência M23: CLI → ambiente → defaults seguros.

Variáveis equivalentes:

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

Quando M23 está OFF, tuning M23 inativo não deve quebrar a execução normal.

## Contexto de dispositivo

Precedência:

1. `--device-context`;
2. `SEARCHGEO_DEVICE_CONTEXT`;
3. default `mobile`.

```text
mobile
desktop
both
```

M7/M20 operam somente nos snapshots materializados. M21 preserva a mesma seleção:

```text
MOBILE  → PageSpeed strategy=mobile  → CrUX PHONE
DESKTOP → PageSpeed strategy=desktop → CrUX DESKTOP
```

M23 forma contextos por URL/device materializado dentro do seu próprio limite `--apdex-max-pages`.

## Providers de IA

### `none`

Nenhuma chamada de IA externa. Regras semantic-only podem permanecer `UNKNOWN` quando não houver evidência suficiente. JSON-LD determinístico M20 continua disponível.

### `openai`

```powershell
$env:OPENAI_API_KEY = "<chave-da-API-Platform>"
searchgeo audit https://example.com --ai-provider openai
```

Default: `gpt-5.6-terra`.

### `deepseek`

```powershell
$env:DEEPSEEK_API_KEY = "<chave-da-DeepSeek-API>"
searchgeo audit https://example.com --ai-provider deepseek
```

Default: `deepseek-v4-pro`.

### `mimo`

```powershell
$env:MIMO_API_KEY = "<chave-sk-PAYG>"
searchgeo audit https://example.com --ai-provider mimo
```

Default: `mimo-v2.5-pro`. O adapter atual usa MiMo PAYG; Token Plan `tp-...` não é suportado por esse endpoint/adapter.

### Extensions explícitas

```powershell
searchgeo audit https://example.com --ai-provider xai
searchgeo audit https://example.com --ai-provider qwen
searchgeo audit https://example.com --ai-provider gemini
searchgeo audit https://example.com --ai-provider anthropic
```

Aliases:

```text
grok   -> xai
claude -> anthropic
```

xAI/Qwen/Gemini/Anthropic permanecem `PROVISIONAL`, `explicit-only`, `auto_eligible=false`.

### `auto`

```powershell
searchgeo audit https://example.com --ai-provider auto
```

Cadeia homologada:

```text
OpenAI -> DeepSeek -> MiMo
```

O primeiro resultado válido encerra o contexto. Extensions não entram em AUTO.

## Modelos aceitos

```text
OPENAI
  gpt-5.6-sol
  gpt-5.6-terra
  gpt-5.6-luna

DEEPSEEK
  deepseek-v4-pro
  deepseek-v4-flash

MIMO
  mimo-v2.5-pro
  mimo-v2.5

XAI
  grok-4.6

QWEN
  qwen3.8-max
  qwen3.8-flash

GEMINI
  gemini-3.8-flash

ANTHROPIC
  claude-sonnet-5
```

Model ID aceito pelo código não garante acesso operacional da conta/plano.

## Variáveis de ambiente

### Gerais / IA

| Variável | Default | Uso |
|---|---|---|
| `SEARCHGEO_DEVICE_CONTEXT` | `mobile` | `mobile`, `desktop`, `both`. |
| `SEARCHGEO_AI_TIMEOUT_SECONDS` | `180` | Timeout por chamada de IA externa. |
| `SEARCHGEO_AI_CONTENT_REMEDIATION` | `false` | M20 textual. |
| `OPENAI_API_KEY` | — | OpenAI API Platform. |
| `DEEPSEEK_API_KEY` | — | DeepSeek API. |
| `MIMO_API_KEY` | — | MiMo PAYG `sk-...`. |
| `XAI_API_KEY` | — | xAI. |
| `DASHSCOPE_API_KEY` | — | Qwen/DashScope. |
| `GEMINI_API_KEY` | — | Gemini API. |
| `ANTHROPIC_API_KEY` | — | Anthropic API. |
| `SEARCHGEO_OPENAI_MODEL` | `gpt-5.6-terra` | Modelo OpenAI. |
| `SEARCHGEO_DEEPSEEK_MODEL` | `deepseek-v4-pro` | Modelo DeepSeek. |
| `SEARCHGEO_MIMO_MODEL` | `mimo-v2.5-pro` | Modelo MiMo. |
| `SEARCHGEO_XAI_MODEL` | `grok-4.6` | Modelo xAI. |
| `SEARCHGEO_QWEN_MODEL` | `qwen3.8-max` | Modelo Qwen. |
| `SEARCHGEO_GEMINI_MODEL` | `gemini-3.8-flash` | Modelo Gemini. |
| `SEARCHGEO_ANTHROPIC_MODEL` | `claude-sonnet-5` | Modelo Anthropic. |

As extensions também expõem variáveis de endpoint próprias documentadas em [AI_PROVIDER_EXTENSIONS.md](AI_PROVIDER_EXTENSIONS.md).

### M21

```text
SEARCHGEO_WEB_PERFORMANCE
SEARCHGEO_WEB_PERFORMANCE_MAX_PAGES
SEARCHGEO_WEB_PERFORMANCE_TIMEOUT_SECONDS
SEARCHGEO_WEB_PERFORMANCE_FIELD_SOURCE
SEARCHGEO_LIGHTHOUSE_CATEGORIES
SEARCHGEO_PAGESPEED_API_KEY
SEARCHGEO_CRUX_API_KEY
```

### M23

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

## Exemplos

### Default: Mobile, sem IA, M21 OFF, M23 OFF

```powershell
searchgeo audit https://example.com --project "Exemplo"
```

### M20 com OpenAI

```powershell
$env:OPENAI_API_KEY = "<chave-da-API-Platform>"
searchgeo audit https://example.com `
  --ai-provider openai `
  --ai-content-remediation
```

### M21 sem IA

```powershell
searchgeo audit https://example.com `
  --ai-provider none `
  --web-performance `
  --web-performance-max-pages 5
```

### M23 smoke controlado

```powershell
searchgeo audit https://example.com `
  --ai-provider none `
  --no-ai-content-remediation `
  --no-web-performance `
  --synthetic-apdex `
  --apdex-threshold-seconds 1.0 `
  --apdex-samples-per-context 5 `
  --apdex-max-attempts-per-context 7 `
  --apdex-max-pages 1 `
  --apdex-delay-seconds 1 `
  --apdex-concurrency 1
```

Com 5 amostras válidas, o grupo recebe `*` por ser menor que o grupo normal de 100.

### M23 com `both`

```powershell
searchgeo audit https://example.com `
  --device-context both `
  --synthetic-apdex `
  --apdex-threshold-seconds 1.5 `
  --apdex-samples-per-context 100 `
  --apdex-max-pages 1
```

Uma página com `both` pode gerar dois contextos M23 independentes. Antes de executar 100 amostras em produção, considere que cada navegação carrega subrecursos e valide autorização/capacidade do alvo.

## Fórmula M23

```text
Apdex = (Satisfied + 0.5 × Tolerating) / Total de amostras válidas

Satisfied  <= T
Tolerating > T e <= 4T
Frustrated > 4T
```

Erro de aplicação/servidor, timeout ou erro de navegação é `FRUSTRATED` quando o profile foi aplicado. Falha de ferramenta/profile fica fora do denominador.

## Custo, quota e carga

### IA

Pode consumir tokens e gerar custo do provider. `ESTIMATED_COST` é estimativa técnica, não invoice.

### M21

Não gera tokens de IA; usa PageSpeed/CrUX e suas quotas conforme configuração.

### M23

Gera:

```text
0 chamadas LLM adicionais
0 tokens IA
0 chamadas PageSpeed/CrUX adicionais
```

Não possui API paga própria no contrato atual, mas produz CPU/RAM/tempo local e tráfego HTTP real contra o site. Uma navegação pode carregar dezenas ou centenas de requests.

## Saída da CLI

Com M23 habilitado, além da saída normal, existe resumo semelhante a:

```text
Synthetic Apdex M23: HABILITADO (PARTIAL; páginas 1; contextos 1; amostras válidas 5/5)
Synthetic Apdex aviso: há grupo(s) pequeno(s) com menos de 100 amostras válidas; resultado é diagnóstico e recebe marcador *.
Relatório Apdex: audits\AUD-...\report\apdex.html
```

`PARTIAL` pode significar small group mesmo com alvo configurado atingido. Interprete juntamente com `valid_samples`, `invalid_samples`, reason/status e marcador `*`.

## Estrutura do report site

```text
report/
├─ index.html
├─ mobile.html             # condicional
├─ desktop.html            # condicional
├─ remediation.html
├─ content-suggestions.html
├─ accessibility.html      # quando materializada
├─ web-performance.html
├─ apdex.html              # quando M23 materializado
├─ ai-usage.html
├─ references.html
└─ css/
   └─ site.css
```

M18/M20 ficam em `ai-usage.html`; M21/M22 em `web-performance.html`/`accessibility.html`; M23 em `apdex.html`.

## Regras de target

- somente HTTP/HTTPS;
- domínio sem scheme é aceito sem path/query/fragment;
- URL com path/query/fragment deve incluir scheme;
- credenciais embutidas são rejeitadas;
- URL_SET deve pertencer à mesma origem normalizada.

## Ajuda local

```powershell
searchgeo --help
searchgeo audit --help
```

Leituras relacionadas: [CONFIGURATION.md](CONFIGURATION.md), [SYNTHETIC_APDEX.md](SYNTHETIC_APDEX.md), [AI_GUIDE.md](AI_GUIDE.md) e [INTERACTIVE_CONSOLE.md](INTERACTIVE_CONSOLE.md).
