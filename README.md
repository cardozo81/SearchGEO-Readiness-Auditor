# SearchGEO Readiness Auditor

Auditor local de **Search/GEO Readiness** com evidência persistida, scoring reproduzível, análise semântica opcional por IA, remediação advisory evidence-backed e camada opcional de evidência externa de Web Performance. O produto avalia acessibilidade técnica, extraibilidade, estrutura semântica, entidades, answerability, citation readiness e outros sinais úteis para Search e sistemas generativos sem prometer ranking, tráfego, citação ou presença em respostas de IA.

## Status atual

**Baseline funcional atual: M22 + M21 + M20 + SCORE-GEO-002.**  
**Capacidades integradas:** `REPORT-SITE-GEO-001`, seleção configurável de dispositivo, console interativo, provider registry canônico, `M20` para sugestões textuais opcionais + revisão/proposta determinística de JSON-LD, `M21` para Lighthouse/Core Web Vitals externos e `M22` para projeção separada de Acessibilidade e diagnósticos de Web Performance, sem alterar o scoring GEO.

A aplicação:

- executa auditoria ponta a ponta por CLI ou console interativo;
- usa **Mobile como contexto padrão**;
- permite `mobile`, `desktop` ou `both`;
- persiste `audit.db` + `artifacts/`;
- gera mini-site estático em `report/` com CSS externo compartilhado;
- separa visão geral, Mobile, Desktop, remediações, conteúdo/JSON-LD, Acessibilidade, Web Performance, telemetria de IA e referências;
- suporta execução sem IA, provider explícito ou `auto`;
- mantém Score, Coverage e Confidence distintos;
- preserva rastreabilidade Evidence → RuleExecution → Finding → Priority → Remediation → Report;
- mantém sugestões M20 advisory: não alteram automaticamente site, score ou findings;
- mantém M21 como evidência externa aditiva: Lighthouse/CrUX não substituem, recalculam nem homologam `SCORE-GEO-002`;
- mantém M22 como projeção de domínio: Acessibilidade e Web Performance não viram Score GEO nem findings GEO automaticamente.

> O Score SearchGEO é um modelo interno de readiness. Não existe um score GEO/AEO normativo universal publicado por Google, OpenAI, Schema.org, WHATWG ou IETF. Lighthouse e Core Web Vitals possuem metodologia externa para seus fenômenos específicos e são exibidos separadamente.

## Base técnica GEO/AEO/SEO

`report/references.html` documenta fontes e metodologia. O SearchGEO não trata como requisito oficial universal markup especial de GEO/AEO, `llms.txt`, chunking artificial, reescrita feita apenas para IA ou Structured Data específico para sistemas generativos.

JSON-LD é tratado como **opcional/reforço**. Quando ausente, M20 pode propor um baseline conservador baseado apenas em dados observados. Quando existente, aponta melhorias sem substituição destrutiva.

M21 usa documentação oficial de PageSpeed Insights, Chrome UX Report, Lighthouse e Core Web Vitals. M22 reutiliza esses artifacts para separar Acessibilidade e diagnósticos de Performance sem nova chamada externa. Essas métricas complementam o diagnóstico técnico, mas não são convertidas automaticamente em Score GEO nem em probabilidade de citação.

## Compatibilidade

| Item | Estado |
|---|---|
| Windows + PowerShell | target operacional principal |
| CPython 3.13.x | obrigatório; `>=3.13,<3.14` |
| Playwright `>=1.57,<2` | obrigatório |
| Chromium | obrigatório para rendering real |
| SQLite | embarcado/local |
| OpenAI | opcional; OpenAI API Platform; `QUALIFIED` |
| DeepSeek | opcional; DeepSeek API; qualificação SearchGEO `PROVISIONAL` |
| Xiaomi MiMo | opcional; **Pay-as-you-go `sk-...`**; qualificação `PROVISIONAL` |
| xAI / Grok | opcional; `PROVISIONAL`, somente seleção explícita |
| Alibaba Qwen | opcional; `PROVISIONAL`, somente seleção explícita |
| Google Gemini | opcional; `PROVISIONAL`, somente seleção explícita |
| Anthropic Claude | opcional; `PROVISIONAL`, somente seleção explícita |
| PageSpeed Insights | opcional M21; pode operar sem chave em uso ad hoc, chave recomendada para automação frequente |
| Chrome UX Report API | opcional M21; chave Google necessária para API direta |
| Docker / web server | não requeridos |

### Plano comercial não é sinônimo de API compatível

A compatibilidade depende de **provider + produto/plano + credencial + endpoint + modelo**.

| Provider | Suportado | Não confundir |
|---|---|---|
| OpenAI | API Platform com API key, billing/quota e acesso ao modelo | assinatura/créditos do ChatGPT não são saldo da API |
| DeepSeek | DeepSeek API com saldo disponível | API key isolada não garante saldo/quota |
| Xiaomi MiMo | PAYG `sk-...` em `https://api.xiaomimimo.com/v1` | Token Plan `tp-...`, com Base URL/créditos separados e fora do adapter atual |
| xAI | API key xAI e modelo suportado | disponibilidade no produto Grok não implica credencial/API compatível |
| Qwen | DashScope/Model Studio com key, região e endpoint compatíveis | assinatura de produto final não substitui a API |
| Gemini | Gemini API com key e endpoint/modelo suportados | outras credenciais Google não são intercambiáveis automaticamente |
| Anthropic | Anthropic API com key e modelo suportado | assinatura Claude não é saldo da API |

Os quatro providers novos permanecem `PROVISIONAL`, `explicit-only` e **fora de `AUTO`** até qualificação real. A cadeia homologada continua `OpenAI -> DeepSeek -> MiMo`.

As chaves Google de M21 são independentes das chaves dos providers de IA. O SearchGEO não envia uma credencial de um provider/serviço para endpoint de outro. Testes também isolam credenciais do ambiente para evitar chamadas externas acidentais.

Detalhes: [docs/AI_GUIDE.md](docs/AI_GUIDE.md), [docs/AI_PROVIDER_EXTENSIONS.md](docs/AI_PROVIDER_EXTENSIONS.md), [docs/CONFIGURATION.md](docs/CONFIGURATION.md), [docs/GOOGLE_API_KEYS.md](docs/GOOGLE_API_KEYS.md), [docs/PROVIDER_REGISTRY.md](docs/PROVIDER_REGISTRY.md) e [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md).

## Instalação rápida — PowerShell

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m playwright install chromium
searchgeo --version
```

`tzdata` é dependência formal do package para garantir `ZoneInfo("America/Sao_Paulo")` também em instalações Windows sem base IANA do sistema. M21 não exige client HTTP Python adicional: PageSpeed/CrUX usam a biblioteca padrão.

### Console interativo opcional

A instalação também registra:

```powershell
searchgeo-console
```

Esse console não substitui nem altera `searchgeo audit`. Ele oferece navegação em tela única, preflight de combinações, edição de variáveis somente para a sessão, cabeçalho de acompanhamento, classificação de exposição financeira potencial, cronômetro, resumo final de tokens/custo e bloqueio transitório de providers que terminem `QUARANTINED_FOR_AUDIT`. URL única é o default; TXT precisa ser selecionado explicitamente. Credenciais aparecem apenas como `[SET]`.

A seleção de IA do console é derivada do registry canônico, não de uma lista independente. Providers `PROVISIONAL` sem key aparecem indisponíveis; configurá-los permite seleção explícita, mas não os inclui em `AUTO`.

O menu inclui `H. Ajuda / custos`, com explicação da finalidade de cada parâmetro e marcadores para custo externo potencial, quota de API e multiplicadores de volume. A projeção considera URLs conhecidas/teto de crawl, dispositivos, IA/M20 e M21. Ao término, tokens/custo IA são consolidados das tabelas M18/M20 já existentes e chamadas M21 vêm de `web_performance_attempts`, sem duplicar telemetria. Apenas projeção prévia e timing, que não existiam no pipeline, são persistidos em `console_execution_projections`.

Ao término de uma auditoria, `I` abre diretamente `report/index.html` no navegador padrão e `P` abre a pasta `audits/<AUD-ID>/` da própria sessão; os atalhos permanecem disponíveis ao voltar ao menu.

Detalhes: [docs/INTERACTIVE_CONSOLE.md](docs/INTERACTIVE_CONSOLE.md), [docs/CONSOLE_COST_AND_USAGE.md](docs/CONSOLE_COST_AND_USAGE.md) e [docs/PROVIDER_REGISTRY.md](docs/PROVIDER_REGISTRY.md).

## Execução rápida

### Mobile, sem IA e sem Web Performance externo — defaults

```powershell
searchgeo audit https://example.com --project "Exemplo"
```

Equivale a `--device-context mobile --ai-provider none --no-web-performance`. M20 textual fica OFF; a revisão JSON-LD determinística continua disponível. `SCORE-GEO-002` continua sendo o scoring baseline.

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

`--ai-content-remediation` é **OFF por padrão**. O gatilho é finding contentual/semântico elegível e evidence-backed; `Confidence LOW` sozinho nunca é gatilho.

### Lighthouse + Core Web Vitals M21

```powershell
searchgeo audit https://example.com `
  --ai-provider none `
  --web-performance
```

`--web-performance` também é **OFF por padrão**. M21 adiciona zero chamadas de LLM. O consumo externo adicional é apenas PageSpeed/CrUX.

Para controlar volume:

```powershell
searchgeo audit https://example.com `
  --web-performance `
  --web-performance-max-pages 5 `
  --web-performance-timeout-seconds 45
```

Default M21: no máximo 10 páginas lógicas; `0` significa todas as páginas auditadas.

Para usar CrUX API direta:

```powershell
$env:SEARCHGEO_CRUX_API_KEY = "<google-api-key>"
searchgeo audit https://example.com `
  --web-performance `
  --web-performance-field-source crux
```

Para criar e restringir corretamente as chaves Google usadas pelo M21, consulte [docs/GOOGLE_API_KEYS.md](docs/GOOGLE_API_KEYS.md).

## Contexto de dispositivo

Precedência: `--device-context` → `SEARCHGEO_DEVICE_CONTEXT` → `mobile`.

A seleção controla rendering e os contextos de M7/M20. `both` habilita BR-GEO-052; em `mobile`/`desktop` ela fica `NOT_APPLICABLE` com `DEVICE_COMPARISON_DISABLED_BY_CONTEXT`.

No M21, Mobile é enviado como PageSpeed `mobile`/CrUX `PHONE`; Desktop como PageSpeed `desktop`/CrUX `DESKTOP`. Somente snapshots materializados entram na coleta externa.

## Estrutura de saída

```text
audits/<AUD-ID>/
├─ audit.db
├─ artifacts/
│  └─ web-performance/        # quando M21 possui respostas externas
└─ report/
   ├─ index.html
   ├─ mobile.html              # condicional
   ├─ desktop.html             # condicional
   ├─ remediation.html
   ├─ content-suggestions.html
   ├─ accessibility.html       # quando M22 materializa a projeção
   ├─ web-performance.html
   ├─ ai-usage.html
   ├─ references.html
   └─ css/site.css
```

`audit.db` + `artifacts/` são a fonte de verdade. O report é projeção humana e não recalcula scoring/findings.

## Score, Coverage, Confidence e evidência externa

- **Score / Readiness (`SCORE-GEO-002`):** índice interno sobre regras avaliadas;
- **Coverage:** quanto do universo aplicável pôde ser avaliado;
- **Confidence:** força da conclusão do auditor;
- **Consolidation:** se há base suficiente para publicar a dimensão/Overall;
- **Lighthouse:** medição de laboratório com metodologia externa do Chrome;
- **Core Web Vitals/CrUX:** experiência real agregada no p75 quando existe amostra suficiente;
- **Acessibilidade M22:** projeção separada dos diagnostics Lighthouse quando disponíveis, sem declarar conformidade WCAG.

**Confidence LOW não significa texto ruim ou não-GEO.** Uma sugestão de conteúdo exige finding/evidência específica.

Da mesma forma, Lighthouse/CWV/Acessibilidade não são adicionados matematicamente ao Overall SearchGEO e não significam chance de citação.

## Core Web Vitals M21

Thresholds oficiais atuais de boa experiência usados para o p75:

```text
LCP <= 2.5 s
INP <= 200 ms
CLS <= 0.10
```

M21 usa `PASS` somente quando as três métricas existem e atendem aos thresholds. Dado faltante produz `INCOMPLETE`/`UNAVAILABLE`, nunca FAIL artificial.

## IA, providers e planos

OpenAI usa API Platform; ChatGPT e API possuem billing separado. DeepSeek exige saldo da API. MiMo atual usa PAYG `sk-...`; não use Token Plan `tp-...` no endpoint PAYG.

Modelos aceitos atualmente:

```text
OPENAI:    gpt-5.6-sol | gpt-5.6-terra | gpt-5.6-luna
DEEPSEEK:  deepseek-v4-pro | deepseek-v4-flash
MIMO:      mimo-v2.5-pro | mimo-v2.5
XAI:       grok-4.6
QWEN:      qwen3.8-max | qwen3.8-flash
GEMINI:    gemini-3.8-flash
ANTHROPIC: claude-sonnet-5
```

Aliases CLI: `grok -> xai` e `claude -> anthropic`. xAI/Qwen/Gemini/Anthropic permanecem `PROVISIONAL`, somente explícitos e fora do `AUTO`.

Timeout default IA: 180 s por chamada externa (`SEARCHGEO_AI_TIMEOUT_SECONDS`).

M21 tem timeout separado, default 60 s (`SEARCHGEO_WEB_PERFORMANCE_TIMEOUT_SECONDS`).

## Telemetria M18/M20/M21

`report/ai-usage.html` separa telemetria M18 e M20. `report/content-suggestions.html` contém propostas textuais advisory e revisão/proposta JSON-LD.

`report/web-performance.html` contém PageSpeed/Lighthouse/CrUX, field/lab data, status operacional e referências a artifacts. `report/accessibility.html` apresenta Acessibilidade como domínio separado quando a projeção M22 existe. Esses serviços não são tratados como uso de LLM.

A sugestão M20:

- não altera o site;
- não altera Score/RuleExecution/Finding;
- deve citar evidence IDs válidos;
- não pode inventar autor, preço, data, rating, estatística, garantia ou claim;
- exige revisão humana.

M21/M22:

- não alteram Score/RuleExecution/Finding;
- M21 não chama SemanticProvider;
- M22 não cria chamada externa adicional;
- não persistem API keys;
- não transformam falha/quota/sem amostra em finding do website;
- preservam a separação entre evidência externa e `SCORE-GEO-002`.

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

## Documentação

- [CLI](docs/CLI_REFERENCE.md)
- [Console interativo](docs/INTERACTIVE_CONSOLE.md)
- [Console — custo e telemetria](docs/CONSOLE_COST_AND_USAGE.md)
- [Provider registry canônico](docs/PROVIDER_REGISTRY.md)
- [Providers adicionais](docs/AI_PROVIDER_EXTENSIONS.md)
- [Compatibilidade](docs/COMPATIBILITY.md)
- [Instalação](docs/INSTALLATION.md)
- [Guia do usuário](docs/USER_GUIDE.md)
- [Configuração](docs/CONFIGURATION.md)
- [Chaves Google — PageSpeed e CrUX](docs/GOOGLE_API_KEYS.md)
- [Report](docs/REPORT_GUIDE.md)
- [Acessibilidade e Performance](docs/ACCESSIBILITY_PERFORMANCE_DOMAINS.md)
- [Scoring](docs/SCORING_GUIDE.md)
- [Validação de scoring](docs/SCORING_VALIDATION.md)
- [IA e M20](docs/AI_GUIDE.md)
- [Outputs](docs/OUTPUTS_AND_ARTIFACTS.md)
- [Guia técnico](docs/TECHNICAL_GUIDE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Smoke](docs/SMOKE_TEST.md)
- [Especificações](docs/specification/00_SPEC_INDEX.md)
- [M21 — Web Performance externo](docs/specification/21_EXTERNAL_WEB_PERFORMANCE_EVIDENCE.md)
- [M22 — diagnósticos separados por domínio](docs/specification/22_DOMAIN_SEPARATED_WEB_QUALITY_DIAGNOSTICS.md)
