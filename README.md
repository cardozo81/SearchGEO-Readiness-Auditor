# SearchGEO Readiness Auditor

Auditor local de **Search/GEO Readiness** com evidência persistida, scoring reproduzível, análise semântica opcional por IA, remediação advisory evidence-backed, domínios separados de Acessibilidade/Web Performance e Synthetic Navigation Apdex opcional.

O produto avalia acessibilidade técnica, extraibilidade, estrutura semântica, entidades, answerability, citation readiness e outros sinais úteis para Search e sistemas generativos sem prometer ranking, tráfego, citação ou presença em respostas de IA.

## Status atual

**Baseline funcional atual: M23 + M22 + M21 + M20 + SCORE-GEO-002.**

Capacidades integradas:

- `REPORT-SITE-GEO-001` com mini-site HTML e navegação canônica;
- seleção `mobile`, `desktop` ou `both`;
- console interativo de execução;
- provider registry canônico;
- M20 para sugestões textuais opcionais e revisão/proposta determinística de JSON-LD;
- M21 para Lighthouse/Core Web Vitals externos;
- M22 para projeção separada de Acessibilidade e diagnósticos técnicos de Web Performance;
- M23 para `Synthetic Navigation Apdex`, com navegações reais repetidas em Chromium, persistência auditável e relatório dedicado;
- `SCORE-GEO-002` preservado como modelo interno de readiness GEO.

A aplicação:

- executa auditoria ponta a ponta por CLI ou console interativo;
- usa **Mobile como contexto padrão**;
- persiste `audit.db`, `artifacts/`, `logs/` e `report/`;
- gera mini-site estático com CSS compartilhado;
- separa GEO, Conteúdo/JSON-LD, Acessibilidade, Web Performance, Apdex e telemetria de IA;
- suporta execução sem IA, provider explícito ou `auto`;
- mantém Score, Coverage e Confidence distintos;
- preserva rastreabilidade Evidence → RuleExecution → Finding → Priority → Remediation → Report;
- mantém M20 advisory: não aplica conteúdo nem altera score/findings;
- mantém M21/M22 como evidência/projeção separada: Lighthouse/CrUX não homologam nem recalculam `SCORE-GEO-002`;
- mantém M23 separado: Apdex não é inferido de Lighthouse/CrUX e não entra no Score GEO.

> O Score SearchGEO é um modelo interno de readiness. Não existe um score GEO/AEO normativo universal publicado por Google, OpenAI, Schema.org, WHATWG ou IETF. Lighthouse, Core Web Vitals e Apdex possuem metodologias próprias para fenômenos específicos e são exibidos separadamente.

## Base técnica GEO/AEO/SEO

`report/references.html` documenta fontes e metodologia. O SearchGEO não trata como requisito oficial universal markup especial de GEO/AEO, `llms.txt`, chunking artificial, reescrita feita apenas para IA ou Structured Data específico para sistemas generativos.

JSON-LD é tratado como **opcional/reforço**. Quando ausente, M20 pode propor baseline conservador baseado apenas em dados observados. Quando existente, aponta melhorias sem substituição destrutiva.

M21 usa documentação oficial de PageSpeed Insights, Chrome UX Report, Lighthouse e Core Web Vitals. M22 reutiliza esses artifacts para separar Acessibilidade e diagnósticos de Performance sem nova chamada externa.

M23 usa a especificação Apdex para fórmula/classificação e Chrome DevTools Protocol/Playwright para perfis sintéticos controlados. M23 mede uma Task explícita de navegação e não converte LCP, INP, CLS, TBT ou duração do PageSpeed em Apdex.

## Compatibilidade

| Item | Estado |
|---|---|
| Windows + PowerShell | target operacional principal |
| CPython 3.13.x | obrigatório; `>=3.13,<3.14` |
| Playwright `>=1.57,<2` | obrigatório |
| Chromium | obrigatório para rendering e M23 |
| SQLite | embarcado/local |
| OpenAI | opcional; API Platform; `QUALIFIED` |
| DeepSeek | opcional; `PROVISIONAL` |
| Xiaomi MiMo | opcional; PAYG `sk-...`; `PROVISIONAL` |
| xAI / Grok | opcional; `PROVISIONAL`, explícito |
| Alibaba Qwen | opcional; `PROVISIONAL`, explícito |
| Google Gemini | opcional; `PROVISIONAL`, explícito |
| Anthropic Claude | opcional; `PROVISIONAL`, explícito |
| PageSpeed Insights | opcional M21 |
| Chrome UX Report API | opcional M21; chave Google para API direta |
| Synthetic Apdex M23 | opcional; local/Chromium; sem API paga própria |
| Docker / web server | não requeridos |

### Provider registry e AUTO

Providers concretos atuais:

```text
openai
deepseek
mimo
xai
qwen
gemini
anthropic
```

Aliases CLI:

```text
grok   -> xai
claude -> anthropic
```

A cadeia homologada `AUTO` permanece:

```text
OpenAI -> DeepSeek -> MiMo
```

xAI, Qwen, Gemini e Anthropic permanecem `PROVISIONAL`, `explicit-only` e fora de `AUTO` até qualificação real de sucesso com credencial externa.

### Plano comercial não é sinônimo de API compatível

A compatibilidade depende de **provider + produto/plano + credencial + endpoint + modelo**.

| Provider | Suportado | Não confundir |
|---|---|---|
| OpenAI | API Platform com API key, billing/quota e acesso ao modelo | assinatura/créditos do ChatGPT não são saldo da API |
| DeepSeek | DeepSeek API com saldo disponível | API key isolada não garante saldo/quota |
| Xiaomi MiMo | PAYG `sk-...` em `https://api.xiaomimimo.com/v1` | Token Plan `tp-...`, com Base URL/créditos separados |
| xAI | API key xAI e modelo suportado | disponibilidade no produto Grok não implica credencial/API compatível |
| Qwen | DashScope/Model Studio com key, região e endpoint compatíveis | assinatura de produto final não substitui a API |
| Gemini | Gemini API com key e endpoint/modelo suportados | outras credenciais Google não são intercambiáveis automaticamente |
| Anthropic | Anthropic API com key e modelo suportado | assinatura Claude não é saldo da API |

As chaves Google de M21 são independentes das chaves dos providers de IA. O SearchGEO não envia uma credencial de um provider/serviço para endpoint de outro.

Detalhes:

- [docs/AI_GUIDE.md](docs/AI_GUIDE.md)
- [docs/AI_PROVIDER_EXTENSIONS.md](docs/AI_PROVIDER_EXTENSIONS.md)
- [docs/PROVIDER_REGISTRY.md](docs/PROVIDER_REGISTRY.md)
- [docs/CONFIGURATION.md](docs/CONFIGURATION.md)
- [docs/GOOGLE_API_KEYS.md](docs/GOOGLE_API_KEYS.md)

## Instalação rápida — PowerShell

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m playwright install chromium
searchgeo --version
```

`tzdata` é dependência formal do package para garantir `ZoneInfo("America/Sao_Paulo")` também em instalações Windows sem base IANA do sistema.

## Console interativo

```powershell
searchgeo-console
```

O console não implementa pipeline alternativo; ele configura e executa a mesma superfície `searchgeo audit`.

Recursos:

- uma tela lógica por vez;
- preflight antes de executar;
- secrets exibidos somente como `[SET]`;
- seleção dinâmica de providers pelo registry;
- estimativa de exposição financeira de IA/M21;
- projeção separada de carga sintética M23;
- início/fim/duração;
- tokens/custo IA persistidos;
- chamadas M21 persistidas;
- navegações M23 persistidas;
- atalhos para abrir pasta e report.

M23 aparece como:

```text
11. Synthetic Apdex M23
```

Detalhes: [docs/INTERACTIVE_CONSOLE.md](docs/INTERACTIVE_CONSOLE.md).

## Execução rápida

### Mobile, sem IA, sem M21 e sem M23 — defaults

```powershell
searchgeo audit https://example.com --project "Exemplo"
```

Equivale operacionalmente a Mobile, IA `none`, M20 textual OFF, M21 OFF e M23 OFF. A revisão JSON-LD determinística continua disponível. `SCORE-GEO-002` continua sendo o scoring baseline.

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

### Sugestões textuais M20

```powershell
$env:OPENAI_API_KEY = "<chave-da-API-Platform>"
searchgeo audit https://example.com `
  --ai-provider openai `
  --ai-content-remediation
```

`--ai-content-remediation` é OFF por padrão. O gatilho é finding contentual/semântico elegível e evidence-backed; `Confidence LOW` sozinho nunca é gatilho.

### Lighthouse + Core Web Vitals M21

```powershell
searchgeo audit https://example.com `
  --ai-provider none `
  --web-performance
```

M21 é OFF por padrão e adiciona zero chamadas LLM. O consumo externo adicional é PageSpeed/CrUX conforme configuração.

### Synthetic Navigation Apdex M23

```powershell
searchgeo audit https://example.com `
  --ai-provider none `
  --no-web-performance `
  --synthetic-apdex `
  --apdex-threshold-seconds 1.5 `
  --apdex-samples-per-context 5 `
  --apdex-max-attempts-per-context 7 `
  --apdex-max-pages 1 `
  --apdex-delay-seconds 1 `
  --apdex-concurrency 1
```

Esse exemplo usa 5 amostras válidas e é adequado para smoke controlado; grupos com menos de 100 válidas recebem marcador `*`.

Default M23 quando habilitado:

```text
amostras válidas/contexto = 100
max attempts              = ceil(1.25 × alvo)
max pages                 = 1
timeout                   = max(45 s, 4T + 5 s)
delay                     = 1 s
concurrency               = 1 (máximo 2)
```

`T` é obrigatório. M23 gera 0 tokens IA e 0 chamadas PageSpeed/CrUX adicionais, mas realiza navegações reais e pode carregar muitos subrecursos. Não execute volume relevante contra produção sem autorização.

Detalhes: [docs/SYNTHETIC_APDEX.md](docs/SYNTHETIC_APDEX.md).

## Fórmula M23

```text
Apdex = (Satisfied + 0.5 × Tolerating) / Total de amostras válidas

Satisfied  <= T
Tolerating > T e <= 4T
Frustrated > 4T
```

Falha da ferramenta/profile fica fora do denominador. Timeout/erro de navegação ou erro de aplicação/servidor conta como `FRUSTRATED` quando o profile sintético foi efetivamente aplicado.

## Contexto de dispositivo

Precedência: `--device-context` → `SEARCHGEO_DEVICE_CONTEXT` → `mobile`.

A seleção controla rendering e os contextos de M7/M20. Em M21, Mobile é enviado como PageSpeed `mobile`/CrUX `PHONE`; Desktop como PageSpeed `desktop`/CrUX `DESKTOP`.

Em M23, cada URL/device materializado dentro de `--apdex-max-pages` forma um contexto de amostragem próprio.

## Estrutura de saída

```text
audits/<AUD-ID>/
├─ audit.db
├─ artifacts/
│  └─ web-performance/        # quando M21 possui respostas externas
├─ logs/
│  └─ audit.log
└─ report/
   ├─ index.html
   ├─ mobile.html              # condicional
   ├─ desktop.html             # condicional
   ├─ remediation.html
   ├─ content-suggestions.html
   ├─ accessibility.html       # quando M22 materializa a projeção
   ├─ web-performance.html
   ├─ apdex.html               # quando M23 está habilitado/materializado
   ├─ ai-usage.html
   ├─ references.html
   └─ css/site.css
```

`audit.db` + `artifacts/` são a fonte persistida principal. O report é projeção humana e não recalcula scoring/findings.

M23 persiste:

```text
synthetic_apdex_runs
synthetic_apdex_samples
synthetic_apdex_summaries
lighthouse_execution_profiles
```

## Score, Coverage, Confidence e domínios auxiliares

- **Score / Readiness (`SCORE-GEO-002`)**: índice interno sobre regras avaliadas;
- **Coverage**: quanto do universo aplicável pôde ser avaliado;
- **Confidence**: força da conclusão;
- **Consolidation**: se há base suficiente para publicar dimensão/Overall;
- **Lighthouse**: medição de laboratório externa;
- **Core Web Vitals/CrUX**: experiência real agregada no p75 quando existe amostra suficiente;
- **Acessibilidade M22**: projeção separada de diagnostics Lighthouse;
- **Synthetic Apdex M23**: índice de Task sintética repetida com `T` explícito.

Nenhum score Lighthouse/CWV/Acessibilidade/Apdex é adicionado matematicamente ao Overall SearchGEO.

## Core Web Vitals M21

Thresholds de boa experiência usados para o p75:

```text
LCP <= 2.5 s
INP <= 200 ms
CLS <= 0.10
```

Dado faltante produz `INCOMPLETE`/`UNAVAILABLE`, nunca FAIL artificial.

## Modelos de IA aceitos

```text
OPENAI:    gpt-5.6-sol | gpt-5.6-terra | gpt-5.6-luna
DEEPSEEK:  deepseek-v4-pro | deepseek-v4-flash
MIMO:      mimo-v2.5-pro | mimo-v2.5
XAI:       grok-4.6
QWEN:      qwen3.8-max | qwen3.8-flash
GEMINI:    gemini-3.8-flash
ANTHROPIC: claude-sonnet-5
```

Model ID aceito pelo código não garante acesso operacional da conta/plano.

## Telemetria

- `report/ai-usage.html`: M18/M20;
- `report/web-performance.html`: M21/M22;
- `report/accessibility.html`: M22 Accessibility;
- `report/apdex.html`: M23;
- `logs/audit.log`: telemetria operacional sanitizada.

Custos IA são estimativas técnicas dos adapters, não invoice. M23 não possui preço de API próprio; sua carga é local + tráfego real contra o alvo.

## Documentação

- [docs/INSTALLATION.md](docs/INSTALLATION.md)
- [docs/USER_GUIDE.md](docs/USER_GUIDE.md)
- [docs/CLI_REFERENCE.md](docs/CLI_REFERENCE.md)
- [docs/CONFIGURATION.md](docs/CONFIGURATION.md)
- [docs/INTERACTIVE_CONSOLE.md](docs/INTERACTIVE_CONSOLE.md)
- [docs/REPORT_GUIDE.md](docs/REPORT_GUIDE.md)
- [docs/OUTPUTS_AND_ARTIFACTS.md](docs/OUTPUTS_AND_ARTIFACTS.md)
- [docs/SYNTHETIC_APDEX.md](docs/SYNTHETIC_APDEX.md)
- [docs/AI_GUIDE.md](docs/AI_GUIDE.md)
- [docs/AI_PROVIDER_EXTENSIONS.md](docs/AI_PROVIDER_EXTENSIONS.md)
- [docs/GOOGLE_API_KEYS.md](docs/GOOGLE_API_KEYS.md)
- [docs/SCORING_GUIDE.md](docs/SCORING_GUIDE.md)
- [docs/SCORING_VALIDATION.md](docs/SCORING_VALIDATION.md)

Normativa M23: [docs/specification/23_SYNTHETIC_APDEX_LIGHTHOUSE_TRACEABILITY.md](docs/specification/23_SYNTHETIC_APDEX_LIGHTHOUSE_TRACEABILITY.md).
