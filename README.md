# SearchGEO Readiness Auditor

Auditor local de **Search/GEO Readiness** com evidência persistida, scoring reproduzível, análise semântica opcional por IA e remediação advisory evidence-backed. O produto avalia acessibilidade técnica, extraibilidade, estrutura semântica, entidades, answerability, citation readiness e outros sinais úteis para Search e sistemas generativos sem prometer ranking, tráfego, citação ou presença em respostas de IA.

## Status atual

**Baseline funcional atual: M20 + SCORE-GEO-002.**  
**Capacidades integradas:** `REPORT-SITE-GEO-001`, seleção configurável de dispositivo e `M20` para sugestões textuais opcionais + revisão/proposta determinística de JSON-LD.

A aplicação:

- executa auditoria ponta a ponta por CLI;
- usa **Mobile como contexto padrão**;
- permite `mobile`, `desktop` ou `both`;
- persiste `audit.db` + `artifacts/`;
- gera mini-site estático em `report/` com CSS externo compartilhado;
- separa visão geral, Mobile, Desktop, remediações, conteúdo/JSON-LD, telemetria de IA e referências;
- suporta execução sem IA, provider explícito ou `auto`;
- mantém Score, Coverage e Confidence distintos;
- preserva rastreabilidade Evidence → RuleExecution → Finding → Priority → Remediation → Report;
- mantém sugestões M20 advisory: não alteram automaticamente site, score ou findings.

> O Score SearchGEO é um modelo interno de readiness. Não existe um score GEO/AEO normativo universal publicado por Google, OpenAI, Schema.org, WHATWG ou IETF.

## Base técnica GEO/AEO/SEO

`report/references.html` documenta fontes e metodologia. O SearchGEO não trata como requisito oficial universal markup especial de GEO/AEO, `llms.txt`, chunking artificial, reescrita feita apenas para IA ou Structured Data específico para sistemas generativos.

JSON-LD é tratado como **opcional/reforço**. Quando ausente, M20 pode propor um baseline conservador baseado apenas em dados observados. Quando existente, aponta melhorias sem substituição destrutiva.

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
| Docker / web server | não requeridos |

### Plano comercial não é sinônimo de API compatível

A compatibilidade depende de **provider + produto/plano + credencial + endpoint + modelo**.

| Provider | Suportado | Não confundir |
|---|---|---|
| OpenAI | API Platform com API key, billing/quota e acesso ao modelo | assinatura/créditos do ChatGPT não são saldo da API |
| DeepSeek | DeepSeek API com saldo disponível | API key isolada não garante saldo/quota |
| Xiaomi MiMo | PAYG `sk-...` em `https://api.xiaomimimo.com/v1` | Token Plan `tp-...`, com Base URL/créditos separados e fora do adapter atual |

O SearchGEO não envia uma credencial de um provider para endpoint de outro provider. Testes também isolam credenciais do ambiente para evitar chamadas externas acidentais.

Detalhes: [docs/AI_GUIDE.md](docs/AI_GUIDE.md) e [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md).

## Instalação rápida — PowerShell

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m playwright install chromium
searchgeo --version
```

## Execução rápida

### Mobile, sem IA — defaults

```powershell
searchgeo audit https://example.com --project "Exemplo"
```

Equivale a `--device-context mobile --ai-provider none`. M20 textual fica OFF; a revisão JSON-LD determinística continua disponível.

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

## Contexto de dispositivo

Precedência: `--device-context` → `SEARCHGEO_DEVICE_CONTEXT` → `mobile`.

A seleção controla rendering e os contextos de M7/M20. `both` habilita BR-GEO-052; em `mobile`/`desktop` ela fica `NOT_APPLICABLE` com `DEVICE_COMPARISON_DISABLED_BY_CONTEXT`.

## Estrutura de saída

```text
audits/<AUD-ID>/
├─ audit.db
├─ artifacts/
└─ report/
   ├─ index.html
   ├─ mobile.html              # condicional
   ├─ desktop.html             # condicional
   ├─ remediation.html
   ├─ content-suggestions.html
   ├─ ai-usage.html
   ├─ references.html
   └─ css/site.css
```

`audit.db` + `artifacts/` são a fonte de verdade. O report é projeção humana e não recalcula scoring/findings.

## Score, Coverage e Confidence

- **Score / Readiness:** qualidade observada nas regras avaliadas;
- **Coverage:** quanto do universo aplicável pôde ser avaliado;
- **Confidence:** força da conclusão do auditor;
- **Consolidation:** se há base suficiente para publicar a dimensão/Overall.

**Confidence LOW não significa texto ruim ou não-GEO.** Uma sugestão de conteúdo exige finding/evidência específica.

## IA e planos

OpenAI usa API Platform; ChatGPT e API possuem billing separado. DeepSeek exige saldo da API. MiMo atual usa PAYG `sk-...`; não use Token Plan `tp-...` no endpoint PAYG.

Modelos aceitos:

```text
OPENAI:   gpt-5.6-sol | gpt-5.6-terra | gpt-5.6-luna
DEEPSEEK: deepseek-v4-pro | deepseek-v4-flash
MIMO:     mimo-v2.5-pro | mimo-v2.5
```

Timeout default: 180 s por chamada externa (`SEARCHGEO_AI_TIMEOUT_SECONDS`).

## Telemetria e M20

`report/ai-usage.html` separa telemetria M18 e M20. `report/content-suggestions.html` contém propostas textuais advisory e revisão/proposta JSON-LD.

A sugestão M20:

- não altera o site;
- não altera Score/RuleExecution/Finding;
- deve citar evidence IDs válidos;
- não pode inventar autor, preço, data, rating, estatística, garantia ou claim;
- exige revisão humana.

## Segurança

Não versionar/persistir API keys ou Authorization. Presença de variável não prova compatibilidade do plano.

```powershell
Test-Path Env:OPENAI_API_KEY
Test-Path Env:DEEPSEEK_API_KEY
Test-Path Env:MIMO_API_KEY
```

## Documentação

- [CLI](docs/CLI_REFERENCE.md)
- [Compatibilidade](docs/COMPATIBILITY.md)
- [Instalação](docs/INSTALLATION.md)
- [Guia do usuário](docs/USER_GUIDE.md)
- [Configuração](docs/CONFIGURATION.md)
- [Report](docs/REPORT_GUIDE.md)
- [Scoring](docs/SCORING_GUIDE.md)
- [IA e M20](docs/AI_GUIDE.md)
- [Outputs](docs/OUTPUTS_AND_ARTIFACTS.md)
- [Guia técnico](docs/TECHNICAL_GUIDE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Smoke](docs/SMOKE_TEST.md)
- [Especificações](docs/specification/00_SPEC_INDEX.md)
