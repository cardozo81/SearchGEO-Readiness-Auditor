# SearchGEO Readiness Auditor

Auditor local de **Search/GEO Readiness** com evidência persistida, scoring reproduzível, análise semântica opcional por IA, remediação advisory evidence-backed e camada opcional de evidência externa de Web Performance. O produto avalia acessibilidade técnica, extraibilidade, estrutura semântica, entidades, answerability, citation readiness e outros sinais úteis para Search e sistemas generativos sem prometer ranking, tráfego, citação ou presença em respostas de IA.

## Status atual

**Baseline funcional atual: M21 + M20 + SCORE-GEO-002 + extensão segura de providers.**

Capacidades principais:

- auditoria ponta a ponta por CLI;
- Mobile como contexto padrão; `mobile`, `desktop` ou `both`;
- `audit.db` + `artifacts/` como fonte de verdade;
- mini-site estático em `report/`;
- execução sem IA, provider explícito ou `auto`;
- M20 advisory, sem alterar automaticamente site/score/findings;
- M21 Lighthouse/CrUX como evidência externa, default OFF e fora do `SCORE-GEO-002`;
- providers M18 homologados preservados: OpenAI, DeepSeek e MiMo;
- providers de extensão explicit-only: xAI/Grok, Alibaba Qwen, Google Gemini e Anthropic Claude.

> O Score SearchGEO é um modelo interno de readiness. Não existe um score GEO/AEO normativo universal publicado por Google, OpenAI, Schema.org, WHATWG ou IETF. Lighthouse e Core Web Vitals possuem metodologia externa para seus fenômenos específicos e são exibidos separadamente.

## Compatibilidade

| Item | Estado |
|---|---|
| Windows + PowerShell | target operacional principal |
| CPython 3.13.x | obrigatório; `>=3.13,<3.14` |
| Playwright `>=1.57,<2` | obrigatório |
| Chromium | obrigatório para rendering real |
| SQLite | embarcado/local |
| OpenAI | opcional; API Platform; `QUALIFIED` |
| DeepSeek | opcional; API; baseline M18 `PROVISIONAL` |
| Xiaomi MiMo | opcional; PAYG `sk-...`; baseline M18 `PROVISIONAL` |
| xAI / Grok | opcional; `PROVISIONAL`, explicit-only |
| Alibaba Qwen | opcional; `PROVISIONAL`, explicit-only |
| Google Gemini | opcional; `PROVISIONAL`, explicit-only |
| Anthropic Claude | opcional; `PROVISIONAL`, explicit-only |
| PageSpeed Insights | opcional M21 |
| Chrome UX Report API | opcional M21 |
| Docker / web server | não requeridos |

### Regra de segurança do AUTO

O comportamento já homologado permanece:

```text
OpenAI -> DeepSeek -> MiMo
```

Mesmo que `XAI_API_KEY`, `DASHSCOPE_API_KEY`, `GEMINI_API_KEY` ou `ANTHROPIC_API_KEY` existam no ambiente, xAI/Qwen/Gemini/Anthropic **não entram em `--ai-provider auto`** enquanto estiverem `PROVISIONAL`.

A extensão foi implementada fora do núcleo M18. `searchgeo.m18_ai` e `searchgeo.cli` permanecem como baseline legado; o entrypoint público usa um shim aditivo para expor novos providers e M20 sem modificar o comportamento antigo.

## Plano comercial não é sinônimo de API compatível

Compatibilidade depende de **provider + produto/plano + credencial + endpoint + modelo**.

| Provider | Credencial | Observação |
|---|---|---|
| OpenAI | `OPENAI_API_KEY` | ChatGPT e API possuem billing separado |
| DeepSeek | `DEEPSEEK_API_KEY` | key não garante saldo/quota |
| Xiaomi MiMo | `MIMO_API_KEY` `sk-...` | Token Plan `tp-...` não é suportado pelo adapter PAYG atual |
| xAI | `XAI_API_KEY` | acesso a `grok-4.6` necessário |
| Qwen | `DASHSCOPE_API_KEY` | key e endpoint devem corresponder à mesma região/workspace |
| Gemini | `GEMINI_API_KEY` | independente das chaves Google PageSpeed/CrUX |
| Anthropic | `ANTHROPIC_API_KEY` | credencial da Claude API |

Detalhes: [docs/AI_GUIDE.md](docs/AI_GUIDE.md), [docs/AI_PROVIDER_EXTENSIONS.md](docs/AI_PROVIDER_EXTENSIONS.md), [docs/CONFIGURATION.md](docs/CONFIGURATION.md) e [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md).

## Instalação rápida — PowerShell

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m playwright install chromium
searchgeo --version
```

Os novos providers usam HTTP da biblioteca padrão e não acrescentam SDK obrigatório ao `pyproject.toml`.

## Execução rápida

### Defaults: Mobile, sem IA e sem M21

```powershell
searchgeo audit https://example.com --project "Exemplo"
```

Equivale a `--device-context mobile --ai-provider none --no-web-performance`. M20 textual fica OFF; a revisão JSON-LD determinística continua disponível.

### Desktop

```powershell
searchgeo audit https://example.com --device-context desktop
```

### Mobile + Desktop

```powershell
searchgeo audit https://example.com --device-context both
```

### Várias URLs

```powershell
searchgeo audit `
  https://example.com/ `
  https://example.com/produto `
  https://example.com/faq `
  --project "Exemplo" `
  --max-pages 3
```

## Providers de IA

### OpenAI

```powershell
$env:OPENAI_API_KEY = "<api-key>"
searchgeo audit https://example.com --ai-provider openai
```

### DeepSeek

```powershell
$env:DEEPSEEK_API_KEY = "<api-key>"
searchgeo audit https://example.com --ai-provider deepseek
```

### Xiaomi MiMo PAYG

```powershell
$env:MIMO_API_KEY = "<sk-api-key>"
searchgeo audit https://example.com --ai-provider mimo
```

### xAI / Grok — provisional explicit-only

```powershell
$env:XAI_API_KEY = "<api-key>"
searchgeo audit https://example.com --ai-provider xai
```

Alias: `--ai-provider grok`.

### Alibaba Qwen — provisional explicit-only

```powershell
$env:DASHSCOPE_API_KEY = "<api-key>"
searchgeo audit https://example.com --ai-provider qwen
```

Qwen pode exigir `SEARCHGEO_QWEN_ENDPOINT` específico da região/workspace da key.

### Google Gemini — provisional explicit-only

```powershell
$env:GEMINI_API_KEY = "<api-key>"
searchgeo audit https://example.com --ai-provider gemini
```

### Anthropic Claude — provisional explicit-only

```powershell
$env:ANTHROPIC_API_KEY = "<api-key>"
searchgeo audit https://example.com --ai-provider anthropic
```

Alias: `--ai-provider claude`.

### AUTO — baseline preservada

```powershell
searchgeo audit https://example.com --ai-provider auto
```

Cadeia: OpenAI -> DeepSeek -> MiMo. Os providers novos não são considerados por AUTO.

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

Model ID aceito não garante acesso comercial da conta.

## Sugestões textuais M20

```powershell
$env:OPENAI_API_KEY = "<api-key>"
searchgeo audit https://example.com `
  --ai-provider openai `
  --ai-content-remediation
```

M20 também possui adapter aditivo para xAI/Qwen/Gemini/Anthropic quando o provider correspondente é selecionado explicitamente.

Exemplo:

```powershell
$env:ANTHROPIC_API_KEY = "<api-key>"
searchgeo audit https://example.com `
  --ai-provider anthropic `
  --ai-content-remediation
```

`--ai-content-remediation` é **OFF por padrão**. O gatilho é finding contentual/semântico elegível e evidence-backed; `Confidence LOW` sozinho nunca é gatilho.

## Lighthouse + Core Web Vitals M21

```powershell
searchgeo audit https://example.com `
  --ai-provider none `
  --web-performance
```

`--web-performance` é **OFF por padrão**. M21 não chama provider de LLM.

Para controlar volume:

```powershell
searchgeo audit https://example.com `
  --web-performance `
  --web-performance-max-pages 5 `
  --web-performance-timeout-seconds 45
```

Para CrUX direto:

```powershell
$env:SEARCHGEO_CRUX_API_KEY = "<google-api-key>"
searchgeo audit https://example.com `
  --web-performance `
  --web-performance-field-source crux
```

Consulte [docs/GOOGLE_API_KEYS.md](docs/GOOGLE_API_KEYS.md).

## Contexto de dispositivo

Precedência: `--device-context` -> `SEARCHGEO_DEVICE_CONTEXT` -> `mobile`.

A seleção controla rendering e os contextos de M7/M20. No M21, Mobile é enviado como PageSpeed `mobile`/CrUX `PHONE`; Desktop como PageSpeed `desktop`/CrUX `DESKTOP`.

## Estrutura de saída

```text
audits/<AUD-ID>/
├─ audit.db
├─ artifacts/
└─ report/
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

`audit.db` + `artifacts/` são a fonte de verdade. O report é projeção humana e não recalcula scoring/findings.

## Score, Coverage, Confidence e evidência externa

- **Score / Readiness (`SCORE-GEO-002`)**: índice interno sobre regras avaliadas;
- **Coverage**: quanto do universo aplicável pôde ser avaliado;
- **Confidence**: força da conclusão;
- **Consolidation**: suficiência para publicar dimensão/Overall;
- **Lighthouse**: medição de laboratório externa;
- **Core Web Vitals/CrUX**: experiência real agregada quando existe amostra suficiente.

Lighthouse/CWV não são adicionados matematicamente ao Overall SearchGEO.

## Core Web Vitals M21

Thresholds de boa experiência usados para p75:

```text
LCP <= 2.5 s
INP <= 200 ms
CLS <= 0.10
```

Dado faltante produz `INCOMPLETE`/`UNAVAILABLE`, não FAIL artificial.

## Telemetria M18/M20/M21

`report/ai-usage.html` separa M18 e M20. Providers de extensão persistem provider/model/status/duração e usage quando o endpoint fornece tokens.

Enquanto xAI/Qwen/Gemini/Anthropic estiverem `PROVISIONAL`, preços não são promovidos automaticamente ao catálogo homologado M18; `estimated_cost` pode ficar indisponível para evitar preço incorreto por região, tier, cache ou promoção.

A sugestão M20:

- não altera o site;
- não altera Score/RuleExecution/Finding;
- deve citar evidence IDs válidos;
- não pode inventar claims;
- exige revisão humana.

## Segurança

Não versionar/persistir API keys ou Authorization. Presença de variável não prova compatibilidade do plano.

```powershell
Test-Path Env:OPENAI_API_KEY
Test-Path Env:DEEPSEEK_API_KEY
Test-Path Env:MIMO_API_KEY
Test-Path Env:XAI_API_KEY
Test-Path Env:DASHSCOPE_API_KEY
Test-Path Env:GEMINI_API_KEY
Test-Path Env:ANTHROPIC_API_KEY
Test-Path Env:SEARCHGEO_PAGESPEED_API_KEY
Test-Path Env:SEARCHGEO_CRUX_API_KEY
```

## Smoke dos providers novos

A implementação/CI pode liberar a branch para smoke, mas os providers novos permanecem `PROVISIONAL` até execução humana com credenciais reais. Consulte [docs/AI_PROVIDER_EXTENSIONS.md](docs/AI_PROVIDER_EXTENSIONS.md) e [docs/SMOKE_TEST.md](docs/SMOKE_TEST.md).

## Documentação

- [CLI](docs/CLI_REFERENCE.md)
- [Compatibilidade](docs/COMPATIBILITY.md)
- [Instalação](docs/INSTALLATION.md)
- [Guia do usuário](docs/USER_GUIDE.md)
- [Configuração](docs/CONFIGURATION.md)
- [Providers de extensão](docs/AI_PROVIDER_EXTENSIONS.md)
- [Chaves Google](docs/GOOGLE_API_KEYS.md)
- [Report](docs/REPORT_GUIDE.md)
- [Scoring](docs/SCORING_GUIDE.md)
- [Validação de scoring](docs/SCORING_VALIDATION.md)
- [IA e M20](docs/AI_GUIDE.md)
- [Outputs](docs/OUTPUTS_AND_ARTIFACTS.md)
- [Guia técnico](docs/TECHNICAL_GUIDE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Smoke](docs/SMOKE_TEST.md)
- [Especificações](docs/specification/00_SPEC_INDEX.md)
