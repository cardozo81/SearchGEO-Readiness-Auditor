# SearchGEO Readiness Auditor

Auditor local de **Search/GEO Readiness** com evidência persistida, scoring reprodutível e análise opcional por IA. O objetivo é avaliar acessibilidade técnica, extraibilidade, estrutura semântica, clareza, answerability, citation readiness e outros sinais úteis para Search e sistemas generativos sem prometer ranking, tráfego, citação ou presença em respostas de IA.

## Status atual

**Baseline funcional: M18 + SCORE-GEO-002, com report site estático e seleção de contexto de dispositivo.**

A aplicação:

- executa auditoria ponta a ponta por CLI;
- usa **Mobile como contexto padrão** na CLI para evitar rendering e chamadas de IA de Desktop sem necessidade;
- permite `mobile`, `desktop` ou `both`;
- persiste `audit.db` + artifacts;
- gera um mini-site estático em `report/`, com CSS compartilhado externo;
- separa visão geral, Mobile, Desktop, remediações, telemetria de IA e referências/metodologia;
- suporta IA opcional com OpenAI, DeepSeek, Xiaomi MiMo ou roteamento `auto`;
- mantém Desktop e Mobile independentes quando ambos são selecionados.

> O Score SearchGEO é um modelo interno de readiness. Não existe um score GEO/AEO normativo universal publicado por Google, OpenAI, Schema.org, WHATWG ou IETF.

## Base técnica GEO/AEO/SEO

A página `report/references.html` gerada em cada auditoria documenta fontes e regras de cálculo. Entre as fontes primárias está o guia oficial do Google de 2026, **Optimizing your website for generative AI features on Google Search**:

<https://developers.google.com/search/docs/fundamentals/ai-optimization-guide>

O próprio Google esclarece nesse guia que AEO/GEO são termos de mercado e que, para os recursos generativos do Google Search, os fundamentos continuam sendo SEO. O SearchGEO, portanto, **não trata como requisito oficial**:

- markup especial de GEO/AEO;
- `llms.txt` como requisito de ranking/visibilidade no Google;
- “chunking” artificial obrigatório;
- reescrita de conteúdo apenas para agradar modelos de IA;
- Structured Data como requisito universal para recursos generativos.

As heurísticas semânticas BR-GEO continuam úteis como modelo de readiness, mas são identificadas como heurísticas internas quando não existe norma externa equivalente.

## Compatibilidade

| Item | Estado |
|---|---|
| Windows + PowerShell | target operacional de handoff |
| CPython 3.13.x | obrigatório; `>=3.13,<3.14` |
| Python 3.12 ou 3.14+ | incompatível com o package atual |
| Playwright `>=1.57,<2` | obrigatório |
| Chromium | obrigatório para rendering real |
| SQLite | embarcado/local |
| OpenAI | opcional |
| DeepSeek | opcional; qualificação SearchGEO `PROVISIONAL` |
| Xiaomi MiMo | opcional; qualificação SearchGEO `PROVISIONAL` |
| Docker / web server | não requeridos |

Detalhes: [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md).

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

Equivale ao contexto:

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

## Contexto de dispositivo e custo

A seleção pode ser feita pela CLI ou por ambiente:

```powershell
$env:SEARCHGEO_DEVICE_CONTEXT = "mobile"   # mobile | desktop | both
```

Precedência:

1. `--device-context`, quando informado;
2. `SEARCHGEO_DEVICE_CONTEXT`;
3. default da CLI: `mobile`.

A seleção controla os snapshots produzidos por M3 e, consequentemente, os contextos enviados ao provider semântico. Em uma página auditada com IA, `mobile` evita a chamada correspondente a Desktop; `both` executa os dois contextos quando disponíveis.

Chamadas internas diretas a M3 sem variável preservam o comportamento legado de ambos os dispositivos para compatibilidade de testes/API interna.

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

`report/index.html` é o ponto de entrada. Os HTMLs usam o mesmo menu e o mesmo `report/css/site.css`; não dependem de servidor web nem de CSS inline/embutido.

Os dados primários continuam sendo `audit.db` e os artifacts. O report site é uma projeção para leitura humana.

## Como interpretar Score, Coverage e Confidence

Esses indicadores respondem perguntas diferentes:

- **Score / Readiness:** qualidade observada nas regras efetivamente avaliadas;
- **Coverage:** proporção do universo aplicável que realmente pôde ser avaliado;
- **Confidence:** força da conclusão do auditor, considerando coverage, evidências e erros de execução;
- **Consolidation:** se existe base suficiente para publicar aquela dimensão/Overall como consolidada.

**Confidence LOW não significa que o texto do site é ruim ou não aderente a GEO.** Ela significa que a conclusão do auditor possui base limitada. O conteúdo é avaliado pelos RuleExecutions, findings e Score. Um score alto com Confidence LOW exige ressalva e não deve ser comunicado como aprovação sem restrições.

As classificações visuais `Excelente / Alta / Moderada / Baixa / Crítica` são faixas internas do SearchGEO, não thresholds oficiais dos mantenedores.

Detalhes: [docs/SCORING_GUIDE.md](docs/SCORING_GUIDE.md) e [docs/REPORT_GUIDE.md](docs/REPORT_GUIDE.md).

## IA opcional

### Sem IA

```powershell
searchgeo audit https://example.com --ai-provider none
```

`none` é o default. Regras semantic-only sem evidência suficiente ficam `UNKNOWN`; isso reduz Coverage/Consolidation quando aplicável, mas não transforma ausência de IA em `FAIL` do website.

### OpenAI

```powershell
$env:OPENAI_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider openai
```

Default: `gpt-5.6-terra` / `HIGH`.

### DeepSeek

```powershell
$env:DEEPSEEK_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider deepseek
```

Default: `deepseek-v4-pro` / `HIGH`.

### Xiaomi MiMo

```powershell
$env:MIMO_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider mimo
```

Default: `mimo-v2.5-pro` / `THINKING_ENABLED`.

### Multi-provider

```powershell
$env:OPENAI_API_KEY = "<chave-openai>"
$env:DEEPSEEK_API_KEY = "<chave-deepseek>"
$env:MIMO_API_KEY = "<chave-mimo>"
searchgeo audit https://example.com --ai-provider auto
```

`AUTO` monta uma cadeia imutável somente com providers configurados e válidos. As chamadas são sequenciais. O primeiro resultado válido encerra a cadeia naquele contexto; providers posteriores não sobrescrevem o resultado aceito.

Um provider explícito não faz fallback para outro fornecedor. Chaves ausentes de providers não selecionados não interferem no provider explícito.

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

O valor deve ser numérico, finito e maior que zero. Timeout não dispara retry automático para evitar consumo duplicado quando a chamada já chegou ao provider.

## Telemetria de IA

A telemetria operacional fica isolada em:

```text
report/ai-usage.html
```

A página apresenta, quando disponíveis:

- estratégia;
- provider/model efetivo;
- status;
- cadeia configurada;
- tentativas por URL/device;
- tokens;
- duração;
- custo estimado local;
- erros sanitizados.

`ESTIMATED_COST` é estimativa do catálogo versionado local e não equivale à invoice/billing do provider. Falha de IA é limitação da auditoria, não finding do website.

## Remediação

`report/remediation.html` concentra causas e ações, com materialização M16/M17 quando disponível:

- causa raiz;
- reason code;
- selector observado;
- alvo técnico e localização esperada;
- observado versus esperado;
- mudança recomendada;
- critério de aceite;
- passos de revalidação;
- decisão humana quando necessária.

Uma evolução futura para **sugestão opcional de texto por IA**, desligada por padrão e sem alterar score/findings, está registrada separadamente no backlog. Ela deverá propor conteúdo apenas quando houver evidência semântica suficiente e nunca gerar “texto para IA” sem valor real ao usuário.

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

## Documentação

- [Referência completa da CLI](docs/CLI_REFERENCE.md)
- [Compatibilidade e dependências](docs/COMPATIBILITY.md)
- [Instalação](docs/INSTALLATION.md)
- [Guia do usuário](docs/USER_GUIDE.md)
- [Configuração](docs/CONFIGURATION.md)
- [Interpretação do report site](docs/REPORT_GUIDE.md)
- [Business Rules](docs/RULES_GUIDE.md)
- [Scoring e Reliability](docs/SCORING_GUIDE.md)
- [IA, routing e fallback](docs/AI_GUIDE.md)
- [Outputs e artifacts](docs/OUTPUTS_AND_ARTIFACTS.md)
- [Guia técnico](docs/TECHNICAL_GUIDE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Smoke test humano](docs/SMOKE_TEST.md)
- [Premissas mínimas GEO](docs/GEO_MINIMUM_REQUIREMENTS.md)

A fonte normativa permanece em [`docs/specification`](docs/specification/00_SPEC_INDEX.md). Em caso de conflito com documentação operacional, a especificação aprovada deve ser atualizada ou prevalece até a reconciliação explícita.
