# SearchGEO Readiness Auditor

Auditor local de **Search/GEO Readiness** com evidência persistida, scoring reproduzível, análise semântica opcional por IA, remediação advisory evidence-backed e camada opcional de evidência externa de Web Performance. O produto avalia acessibilidade técnica, extraibilidade, estrutura semântica, entidades, answerability, citation readiness e outros sinais úteis para Search e sistemas generativos sem prometer ranking, tráfego, citação ou presença em respostas de IA.

## Status atual

**Baseline funcional atual: M21 + M20 + SCORE-GEO-002.**  
**Capacidades integradas:** `REPORT-SITE-GEO-001`, seleção configurável de dispositivo, `M20` para sugestões textuais opcionais + revisão/proposta determinística de JSON-LD e `M21` para Lighthouse/Core Web Vitals externos, default OFF e sem alterar scoring.

A aplicação:

- executa auditoria ponta a ponta por CLI;
- usa **Mobile como contexto padrão**;
- permite `mobile`, `desktop` ou `both`;
- persiste `audit.db` + `artifacts/`;
- gera mini-site estático em `report/` com CSS externo compartilhado;
- separa visão geral, Mobile, Desktop, remediações, conteúdo/JSON-LD, Web Performance, telemetria de IA e referências;
- suporta execução sem IA, provider explícito ou `auto`;
- mantém Score, Coverage e Confidence distintos;
- preserva rastreabilidade Evidence → RuleExecution → Finding → Priority → Remediation → Report;
- mantém sugestões M20 advisory: não alteram automaticamente site, score ou findings;
- mantém M21 como evidência externa aditiva: Lighthouse/CrUX não substituem, recalculam nem homologam `SCORE-GEO-002`.

> O Score SearchGEO é um modelo interno de readiness. Não existe um score GEO/AEO normativo universal publicado por Google, OpenAI, Schema.org, WHATWG ou IETF. Lighthouse e Core Web Vitals possuem metodologia externa para seus fenômenos específicos e são exibidos separadamente.

## Base técnica GEO/AEO/SEO

`report/references.html` documenta fontes e metodologia. O SearchGEO não trata como requisito oficial universal markup especial de GEO/AEO, `llms.txt`, chunking artificial, reescrita feita apenas para IA ou Structured Data específico para sistemas generativos.

JSON-LD é tratado como **opcional/reforço**. Quando ausente, M20 pode propor um baseline conservador baseado apenas em dados observados. Quando existente, aponta melhorias sem substituição destrutiva.

M21 usa documentação oficial de PageSpeed Insights, Chrome UX Report, Lighthouse e Core Web Vitals. Essas métricas complementam o diagnóstico técnico, mas não são convertidas automaticamente em Score GEO nem em probabilidade de citação.

## Compatibilidade

| Item | Estado |
|---|---|
| Windows + PowerShell | target operacional principal |
| CPython 3.13.x | obrigatório; `>=3.13,<3.14` |
| Playwright `>=1.57,<2` | obrigatório |
| Chromium | obrigatório para rendering real |
| SQLite | embarcado/local |
| OpenAI | opcional; OpenAI API Platform |
| DeepSeek | opcional; DeepSeek API; qualificação SearchGEO `PROVISIONAL` |
| Xiaomi MiMo | opcional; **Pay-as-you-go `sk-...`**; qualificação `PROVISIONAL` |
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

As chaves Google de M21 são independentes das chaves dos providers de IA. O SearchGEO não envia uma credencial de um provider/serviço para endpoint de outro. Testes também isolam credenciais do ambiente para evitar chamadas externas acidentais.

Detalhes: [docs/AI_GUIDE.md](docs/AI_GUIDE.md), [docs/CONFIGURATION.md](docs/CONFIGURATION.md) e [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md).

## Instalação rápida — PowerShell

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m playwright install chromium
searchgeo --version
```

M21 não adiciona dependência Python nova: os clients HTTP PageSpeed/CrUX usam a biblioteca padrão do Python.

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

`--web-performance` também é **OFF por padrão**. M21 adiciona zero chamadas de OpenAI/DeepSeek/MiMo. O consumo externo adicional é apenas PageSpeed/CrUX.

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
- **Core Web Vitals/CrUX:** experiência real agregada no p75 quando existe amostra suficiente.

**Confidence LOW não significa texto ruim ou não-GEO.** Uma sugestão de conteúdo exige finding/evidência específica.

Da mesma forma, Lighthouse/CWV não são adicionados matematicamente ao Overall SearchGEO e não significam chance de citação.

## Core Web Vitals M21

Thresholds oficiais atuais de boa experiência usados para o p75:

```text
LCP <= 2.5 s
INP <= 200 ms
CLS <= 0.10
```

M21 usa `PASS` somente quando as três métricas existem e atendem aos thresholds. Dado faltante produz `INCOMPLETE`/`UNAVAILABLE`, nunca FAIL artificial.

## IA e planos

OpenAI usa API Platform; ChatGPT e API possuem billing separado. DeepSeek exige saldo da API. MiMo atual usa PAYG `sk-...`; não use Token Plan `tp-...` no endpoint PAYG.

Modelos aceitos:

```text
OPENAI:   gpt-5.6-sol | gpt-5.6-terra | gpt-5.6-luna
DEEPSEEK: deepseek-v4-pro | deepseek-v4-flash
MIMO:     mimo-v2.5-pro | mimo-v2.5
```

Timeout default IA: 180 s por chamada externa (`SEARCHGEO_AI_TIMEOUT_SECONDS`).

M21 tem timeout separado, default 60 s (`SEARCHGEO_WEB_PERFORMANCE_TIMEOUT_SECONDS`).

## Telemetria M18/M20/M21

`report/ai-usage.html` separa telemetria M18 e M20. `report/content-suggestions.html` contém propostas textuais advisory e revisão/proposta JSON-LD.

`report/web-performance.html` contém PageSpeed/Lighthouse/CrUX, field/lab data, status operacional e referências a artifacts. Esses serviços não são tratados como uso de LLM.

A sugestão M20:

- não altera o site;
- não altera Score/RuleExecution/Finding;
- deve citar evidence IDs válidos;
- não pode inventar autor, preço, data, rating, estatística, garantia ou claim;
- exige revisão humana.

M21:

- não altera Score/RuleExecution/Finding;
- não chama SemanticProvider;
- não persiste API keys;
- não transforma falha/quota/sem amostra em finding do website;
- preserva raw response JSON quando a chamada retorna payload válido.

## Segurança

Não versionar/persistir API keys ou Authorization. Presença de variável não prova compatibilidade do plano.

```powershell
Test-Path Env:OPENAI_API_KEY
Test-Path Env:DEEPSEEK_API_KEY
Test-Path Env:MIMO_API_KEY
Test-Path Env:SEARCHGEO_PAGESPEED_API_KEY
Test-Path Env:SEARCHGEO_CRUX_API_KEY
```

## Documentação

- [CLI](docs/CLI_REFERENCE.md)
- [Compatibilidade](docs/COMPATIBILITY.md)
- [Instalação](docs/INSTALLATION.md)
- [Guia do usuário](docs/USER_GUIDE.md)
- [Configuração](docs/CONFIGURATION.md)
- [Report](docs/REPORT_GUIDE.md)
- [Scoring](docs/SCORING_GUIDE.md)
- [Validação de scoring](docs/SCORING_VALIDATION.md)
- [IA e M20](docs/AI_GUIDE.md)
- [Outputs](docs/OUTPUTS_AND_ARTIFACTS.md)
- [Guia técnico](docs/TECHNICAL_GUIDE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Smoke](docs/SMOKE_TEST.md)
- [Especificações](docs/specification/00_SPEC_INDEX.md)
- [M21 — Web Performance externo](docs/specification/21_EXTERNAL_WEB_PERFORMANCE_EVIDENCE.md)
