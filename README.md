# SearchGEO Readiness Auditor

Auditor local de **Search/GEO Readiness** com evidência persistida, scoring reproduzível e análise semântica opcional por IA. O objetivo é avaliar acessibilidade técnica, extraibilidade, estrutura semântica, clareza de entidades, answerability, citation readiness e outros sinais úteis para Search e sistemas generativos sem prometer ranking, tráfego, citação ou presença em respostas de IA.

## Status atual

**Baseline funcional atual: M18 + SCORE-GEO-002.**  
**Capacidades integradas:** `REPORT-SITE-GEO-001` e seleção configurável de contexto de dispositivo.

A aplicação:

- executa auditoria ponta a ponta por CLI;
- usa **Mobile como contexto padrão da CLI** para evitar rendering e chamadas de IA de Desktop sem necessidade;
- permite `mobile`, `desktop` ou `both`;
- persiste `audit.db` + `artifacts/`;
- gera mini-site estático em `report/`, com navegação compartilhada e CSS externo;
- separa visão geral, Mobile, Desktop, remediações, telemetria de IA e referências/metodologia;
- suporta execução sem IA, provider explícito ou roteamento multi-provider `auto`;
- mantém Score, Coverage e Confidence como indicadores distintos;
- preserva rastreabilidade de Evidence → RuleExecution → Finding → Priority → Remediation → Report.

> O Score SearchGEO é um modelo interno de readiness. Não existe um score GEO/AEO normativo universal publicado por Google, OpenAI, Schema.org, WHATWG ou IETF.

## Base técnica GEO/AEO/SEO

A página `report/references.html` gerada em cada auditoria documenta fontes e metodologia. Entre as fontes primárias estão Google Search Central, OpenAI, Schema.org, WHATWG e RFCs relevantes.

O SearchGEO não trata como requisito oficial universal:

- markup especial de GEO/AEO;
- `llms.txt` como requisito de ranking/visibilidade;
- chunking artificial obrigatório;
- reescrita de conteúdo apenas para agradar modelos de IA;
- Structured Data como requisito universal para recursos generativos.

As heurísticas BR-GEO continuam úteis como modelo de readiness, mas são identificadas como heurísticas internas quando não existe norma externa equivalente.

## Compatibilidade

| Item | Estado |
|---|---|
| Windows + PowerShell | target operacional de handoff |
| CPython 3.13.x | obrigatório; `>=3.13,<3.14` |
| Python 3.12 ou 3.14+ | incompatível com o package atual |
| Playwright `>=1.57,<2` | obrigatório |
| Chromium | obrigatório para rendering real |
| SQLite | embarcado/local |
| OpenAI | opcional; via OpenAI API Platform |
| DeepSeek | opcional; via DeepSeek API; qualificação SearchGEO `PROVISIONAL` |
| Xiaomi MiMo | opcional; **Pay-as-you-go `sk-...`**; qualificação SearchGEO `PROVISIONAL` |
| Docker / web server | não requeridos |

### Atenção: plano comercial não é sinônimo de API compatível

A compatibilidade depende de **provider + produto/plano + credencial + endpoint + modelo**.

| Provider | Suportado pelo SearchGEO atual | Não usar/confundir |
|---|---|---|
| OpenAI | API Platform com API key, billing/quota e acesso ao modelo | assinatura/créditos do ChatGPT não são saldo da API |
| DeepSeek | DeepSeek API com saldo concedido e/ou recarregado | API key sem saldo/quota disponível |
| Xiaomi MiMo | Pay-as-you-go `sk-...` em `https://api.xiaomimimo.com/v1` | Token Plan `tp-...`; usa Base URL dedicada, créditos independentes e não é suportado/adequado ao auditor automatizado atual |

No MiMo, `tp-...` e `sk-...` pertencem a produtos independentes. O SearchGEO atual chama o endpoint PAYG; portanto configure apenas chave `sk-...`. A MiMo também restringe o Token Plan a ferramentas de programação e proíbe automated scripts/custom application backends fora desse escopo.

Detalhes e fontes oficiais: [docs/AI_GUIDE.md](docs/AI_GUIDE.md) e [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md).

## Instalação rápida — PowerShell

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m playwright install chromium
searchgeo --version
```

## Execução rápida

### Default: Mobile, sem IA

```powershell
searchgeo audit https://example.com --project "Exemplo"
```

Equivale a:

```text
--device-context mobile
--ai-provider none
```

### Desktop apenas

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
  --project "Exemplo"
```

### Arquivo de URLs

```powershell
searchgeo audit --urls-file .\urls.txt --project "Exemplo"
```

## Contexto de dispositivo

A seleção pode ser feita pela CLI ou por ambiente:

```powershell
$env:SEARCHGEO_DEVICE_CONTEXT = "mobile"   # mobile | desktop | both
```

Precedência:

1. `--device-context`, quando informado;
2. `SEARCHGEO_DEVICE_CONTEXT`;
3. default da CLI: `mobile`.

A seleção controla os snapshots produzidos por M3 e os contextos elegíveis para análise semântica. Em uma página auditada com IA, `mobile` evita a chamada correspondente a Desktop; `both` permite os dois contextos quando disponíveis.

A comparação BR-GEO-052 só é executada quando `both` foi selecionado. Em `mobile` ou `desktop`, ela fica `NOT_APPLICABLE` com reason code `DEVICE_COMPARISON_DISABLED_BY_CONTEXT`; isso não representa erro nem snapshot ausente.

Chamadas internas diretas a M3 sem variável preservam o comportamento legado de ambos os dispositivos para compatibilidade da API interna/testes. O contrato público da CLI permanece Mobile por padrão.

## Estrutura de saída

```text
audits/<AUD-ID>/
├─ audit.db
├─ artifacts/
└─ report/
   ├─ index.html
   ├─ mobile.html          # quando Mobile foi auditado
   ├─ desktop.html         # quando Desktop foi auditado
   ├─ remediation.html
   ├─ ai-usage.html
   ├─ references.html
   └─ css/
      └─ site.css
```

`report/index.html` é o ponto de entrada. Os HTMLs finais usam o mesmo menu e `report/css/site.css`; não dependem de servidor web nem de CSS inline/embutido.

`audit.db` e os artifacts persistidos continuam sendo a fonte de verdade. O report site é uma projeção para leitura humana e não recalcula score/findings nem chama IA.

## Como interpretar Score, Coverage e Confidence

Os indicadores respondem perguntas diferentes:

- **Score / Readiness:** qualidade observada nas regras efetivamente avaliadas;
- **Coverage:** proporção do universo aplicável que pôde ser avaliado;
- **Confidence:** força da conclusão do auditor considerando cobertura, evidências e erros de execução;
- **Consolidation:** se existe base suficiente para publicar aquela dimensão/Overall como consolidada.

**Confidence LOW não significa que o texto do site é ruim ou não aderente a GEO.** Significa que a conclusão do auditor possui base limitada. O conteúdo é julgado pelos RuleExecutions, findings e Score. Um score alto com Confidence LOW exige ressalva e não deve ser comunicado como aprovação irrestrita.

As classificações `Excelente / Alta / Moderada / Baixa / Crítica` são faixas internas do SearchGEO, não thresholds oficiais dos mantenedores externos.

Detalhes: [docs/SCORING_GUIDE.md](docs/SCORING_GUIDE.md) e [docs/REPORT_GUIDE.md](docs/REPORT_GUIDE.md).

## IA opcional

### Sem IA

```powershell
searchgeo audit https://example.com --ai-provider none
```

`none` é o default. Regras semantic-only sem evidência suficiente podem ficar `UNKNOWN`; isso reduz Coverage/Consolidation quando aplicável, mas ausência de IA nunca vira `FAIL` do website.

### OpenAI

```powershell
$env:OPENAI_API_KEY = "<chave-da-API-Platform>"
searchgeo audit https://example.com --ai-provider openai
```

Default: `gpt-5.6-terra` / `HIGH`.

A assinatura ChatGPT não substitui billing da API Platform.

### DeepSeek

```powershell
$env:DEEPSEEK_API_KEY = "<chave-da-DeepSeek-API>"
searchgeo audit https://example.com --ai-provider deepseek
```

Default: `deepseek-v4-pro` / `HIGH`.

### Xiaomi MiMo

```powershell
$env:MIMO_API_KEY = "<chave-sk-PAYG>"
searchgeo audit https://example.com --ai-provider mimo
```

Default: `mimo-v2.5-pro` / `THINKING_ENABLED`.

**Não use chave Token Plan `tp-...` no SearchGEO atual.**

### Multi-provider

```powershell
$env:OPENAI_API_KEY = "<chave-openai-api>"
$env:DEEPSEEK_API_KEY = "<chave-deepseek-api>"
$env:MIMO_API_KEY = "<chave-mimo-sk-PAYG>"
searchgeo audit https://example.com --ai-provider auto
```

`AUTO` monta cadeia imutável somente com providers configurados e utilizáveis. As tentativas são sequenciais. O primeiro resultado válido encerra a cadeia naquele contexto; providers posteriores não sobrescrevem o resultado aceito.

Provider explícito não faz fallback para outro fornecedor. Chaves ausentes de providers não selecionados não interferem no provider explícito.

Modelos aceitos pelo código:

```text
OPENAI:   gpt-5.6-sol | gpt-5.6-terra | gpt-5.6-luna
DEEPSEEK: deepseek-v4-pro | deepseek-v4-flash
MIMO:     mimo-v2.5-pro | mimo-v2.5
```

## Timeout de IA

Default da CLI: `180` segundos por chamada.

```powershell
$env:SEARCHGEO_AI_TIMEOUT_SECONDS = "240"
```

O valor deve ser numérico, finito e maior que zero. Timeout não dispara retry automático da mesma chamada para evitar consumo duplicado quando a requisição pode ter alcançado o provider.

## Telemetria de IA

A telemetria operacional fica isolada em:

```text
report/ai-usage.html
```

Quando disponíveis, são exibidos estratégia, provider/model efetivo, status, tentativas por URL/device, tokens, duração, custo estimado local e erros sanitizados.

`ESTIMATED_COST` é estimativa do catálogo versionado local e não equivale à invoice/billing do provider. Falha de IA é limitação operacional da auditoria, não finding do website.

## Remediação

`report/remediation.html` concentra causas e ações, preservando materialização M16/M17 quando disponível:

- causa raiz;
- reason code;
- selector observado;
- alvo técnico e localização esperada;
- observado versus esperado;
- mudança recomendada;
- critério de aceite;
- passos de revalidação;
- decisão humana quando necessária.

A futura sugestão opcional de texto por IA está registrada no backlog e permanece **OFF por padrão**. Ela deverá ser evidence-backed, respeitar o contexto de dispositivo, não alterar score retrospectivamente e seguir princípio people-first.

## Referência completa da CLI

```text
searchgeo [--config PATH] audit [target ...]
  [--urls-file PATH]
  [--project TEXT]
  [--language CODE]
  [--market CODE]
  [--max-pages N]
  [--audits-root PATH]
  [--device-context mobile|desktop|both]
  [--ai-provider none|openai|deepseek|mimo|auto]
  [--ai-model MODEL_ID]
```

Glossário completo: [docs/CLI_REFERENCE.md](docs/CLI_REFERENCE.md).

## Segurança

Não grave API keys em repositório, TOML versionado, artifacts, HTML ou logs. Para validar somente presença:

```powershell
Test-Path Env:OPENAI_API_KEY
Test-Path Env:DEEPSEEK_API_KEY
Test-Path Env:MIMO_API_KEY
```

Presença da variável não prova que o plano seja compatível. Consulte [docs/AI_GUIDE.md](docs/AI_GUIDE.md) antes de configurar providers com múltiplos produtos/planos.

## Documentação

- [Referência completa da CLI](docs/CLI_REFERENCE.md)
- [Compatibilidade e dependências](docs/COMPATIBILITY.md)
- [Instalação](docs/INSTALLATION.md)
- [Guia do usuário](docs/USER_GUIDE.md)
- [Configuração](docs/CONFIGURATION.md)
- [Interpretação do report site](docs/REPORT_GUIDE.md)
- [Business Rules](docs/RULES_GUIDE.md)
- [Scoring e Reliability](docs/SCORING_GUIDE.md)
- [IA, routing, fallback e compatibilidade de planos](docs/AI_GUIDE.md)
- [Outputs e artifacts](docs/OUTPUTS_AND_ARTIFACTS.md)
- [Guia técnico](docs/TECHNICAL_GUIDE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Smoke test](docs/SMOKE_TEST.md)
- [Premissas mínimas GEO](docs/GEO_MINIMUM_REQUIREMENTS.md)

A fonte normativa permanece em [`docs/specification`](docs/specification/00_SPEC_INDEX.md). Descrições históricas de milestones que mencionem outputs legados são superseded pelo contrato vigente `REPORT-SITE-GEO-001` quando houver conflito de path/apresentação.
