# TECHNICAL_ARCHITECTURE.md

**Status:** APPROVED — SAFE PROVIDER EXTENSIONS + M21 + M20 + REPORT-SITE-GEO-001

## 1. Estilo arquitetural

Aplicação local, modular, CLI-first, single-machine no baseline.

Não exige:

- web server;
- database server;
- Docker;
- daemon/background worker;
- IA externa;
- PageSpeed Insights ou CrUX para a auditoria SearchGEO principal.

## 2. Runtime

- CPython 3.13.x;
- Playwright + Chromium;
- SQLite embarcado;
- filesystem local;
- HTTP/HTTPS para target;
- HTTPS para provider externo somente quando habilitado;
- HTTPS para PageSpeed/CrUX somente quando M21 external collection estiver habilitada.

## 3. Pipeline

```text
CLI
→ configuração/contexto de dispositivo
→ discovery/acquisition
→ rendering
→ extraction/evidence
→ deterministic rules
→ semantic provider opcional (M7/M18 + extensions explicit-only)
→ device comparison quando ambos existem
→ scoring (M9)
→ prioritization/remediation base (M10/M16/M17)
→ M20 opcional: sugestão textual evidence-bound + revisão JSON-LD determinística
→ M11/M18 intermediate reporting
→ report-site finalization
→ M20 report projection/navigation enrichment
→ M21 optional external Web Performance enrichment
   → PageSpeed Insights/Lighthouse lab
   → CrUX field data quando disponível/configurado
   → persistence + raw JSON artifacts
   → web-performance.html + summary/references enrichment
```

Invariantes:

- M20 começa somente depois de scoring/findings/priorização concluídos e não altera os objetos já avaliados;
- M21 ocorre depois da auditoria principal e é fail-open;
- M21 não cria RuleExecution, Finding, Recommendation ou ScoreContribution;
- M21 não executa LLM;
- PageSpeed/CrUX indisponível não invalida `SCORE-GEO-002`.

## 4. Device context

A CLI resolve exatamente um dos valores:

```text
mobile
desktop
both
```

Default de usuário:

```text
mobile
```

Precedência:

1. `--device-context`;
2. `SEARCHGEO_DEVICE_CONTEXT`;
3. `mobile`.

M3 renderiza somente o conjunto selecionado. Downstream trabalha sobre os snapshots realmente materializados. Nenhum provider semântico nem M20 deve ser chamado para dispositivo não renderizado.

M21 também usa somente snapshots existentes:

```text
MOBILE  → PageSpeed strategy=mobile  → CrUX formFactor=PHONE
DESKTOP → PageSpeed strategy=desktop → CrUX formFactor=DESKTOP
```

Chamadas internas diretas a M3 sem variável preservam `both` para compatibilidade interna/testes.

## 5. Persistência

Workspace:

```text
<AUD-ID>/
├─ audit.db
├─ artifacts/
└─ report/
```

SQLite guarda entidades estruturadas; filesystem guarda payloads/artefatos grandes.

M20 adiciona entidades reabríveis separadas:

```text
content_remediation_runs
content_remediation_suggestions
content_remediation_attempts
jsonld_remediation_suggestions
```

M21 adiciona entidades auxiliares separadas:

```text
web_performance_runs
web_performance_observations
web_performance_attempts
```

Tabelas M20/M21 não participam do denominador de scoring nem substituem as tabelas normativas de RuleExecution/Score.

## 6. Artifacts

Podem incluir:

- RAW HTTP/HTML;
- rendered HTML;
- conteúdo principal;
- structured data;
- screenshots;
- evidence materializada;
- respostas JSON PageSpeed/CrUX quando M21 executar coleta externa com sucesso.

Os artifacts são referenciados por caminhos relativos ao workspace.

M20 reutiliza artifacts persistidos e não refaz crawling/rendering.

M21 escreve respostas externas reabríveis em:

```text
artifacts/web-performance/
```

Esses JSONs preservam o payload utilizado na projeção sem persistir API key.

## 7. IA

`SemanticAnalysisProvider` é abstração independente de fornecedor.

### 7.1 Baseline M18 homologada

O núcleo `searchgeo.m18_ai` permanece responsável por:

```text
NONE
OPENAI
DEEPSEEK
MIMO
AUTO router
```

`AUTO` mantém cadeia restrita a:

```text
OPENAI → DEEPSEEK → MIMO
```

Nenhum provider de extensão pode ingressar silenciosamente nessa cadeia.

M18 persiste sessão/tentativas da finalidade de análise semântica. IA não executa scoring.

### 7.2 Extensão aditiva de providers

A extensão segura é materializada fora do núcleo homologado:

```text
searchgeo.provider_extensions
searchgeo.provider_extensions_m20
searchgeo.cli_extensions
```

Providers extension atuais:

```text
XAI / GROK      → grok-4.6
QWEN            → qwen3.8-max | qwen3.8-flash
GEMINI          → gemini-3.8-flash
ANTHROPIC       → claude-sonnet-5
```

Todos são `PROVISIONAL` e `explicit-only` até smoke humano. Suas API keys não os tornam candidatos de `AUTO`.

O entrypoint público usa `cli_extensions`, que amplia as escolhas e delega toda seleção legacy (`none`, `openai`, `deepseek`, `mimo`, `auto`) ao builder M18 original. `src/searchgeo/cli.py`, `src/searchgeo/m18_ai.py` e `src/searchgeo/m20_ai.py` permanecem baseline não modificada pela extensão.

Os adapters de extensão reutilizam o mesmo contrato semântico normalizado, schema/evidence validation, `ProviderAttempt`, quarantine e telemetria compatível. Diferenças de API ficam encapsuladas no adapter nativo do fornecedor.

### 7.3 M20

M20, quando habilitado, cria sessão de remediação a partir do provider selecionado ainda saudável.

- OpenAI/DeepSeek/MiMo continuam pelo router M20 homologado;
- xAI/Qwen/Gemini/Anthropic usam `provider_extensions_m20`;
- provider quarantined na finalidade M7 não é reativado para M20;
- a finalidade M20 mantém telemetria separada e não altera scoring.

### 7.4 M21

M21 não usa `SemanticAnalysisProvider`, não chama qualquer provider LLM e não acrescenta consumo LLM.

## 8. M20

### 8.1 Texto

Input por snapshot/device:

```text
URL + title + conteúdo principal persistido
+ findings elegíveis
+ evidence IDs/observed values desses findings
```

Output validado:

```text
finding_id
objective
target_location
proposed_text
evidence_ids
confidence
review_note
```

Respostas que escapem do finding/evidence universe são rejeitadas. Tokens numéricos novos ausentes do corpus persistido também são rejeitados como contenção contra fabricação factual.

### 8.2 JSON-LD

A orientação JSON-LD é determinística e independente da ativação da chamada textual por IA.

Sem JSON-LD, o módulo pode produzir um baseline conservador `WebPage` com valores persistidos. Com JSON-LD, realiza revisão genérica não destrutiva e não substitui graphs existentes.

## 9. M21 — External Web Performance Evidence

### 9.1 Ativação

Coleta externa é `false` por padrão. Os controles públicos incluem:

```text
--web-performance / --no-web-performance
--web-performance-max-pages
--web-performance-timeout-seconds
--web-performance-field-source auto|pagespeed|crux|none
--lighthouse-categories
```

Com M21 desligado, auditorias reais podem materializar estado `DISABLED` e a página explicativa, mas não fazem requisição PageSpeed/CrUX.

### 9.2 PageSpeed Insights

Uma chamada por snapshot/dispositivo selecionado solicita as categorias configuradas, com default:

```text
performance
accessibility
best-practices
seo
```

Persistem-se somente valores efetivamente retornados, incluindo versão/fetch time Lighthouse e métricas de laboratório relevantes.

### 9.3 Core Web Vitals / CrUX

Política default `auto`:

1. usar field data CrUX devolvido pelo PageSpeed quando utilizável;
2. se ausente e existir `SEARCHGEO_CRUX_API_KEY`, consultar CrUX API direta;
3. sem dados suficientes, manter `INCOMPLETE`/`UNAVAILABLE` sem website finding.

`pagespeed`, `crux` e `none` permitem controlar explicitamente a fonte/ausência de field data.

### 9.4 Credenciais e consumo

Credenciais M21 isoladas:

```text
SEARCHGEO_PAGESPEED_API_KEY
SEARCHGEO_CRUX_API_KEY
```

Elas nunca substituem nem reutilizam credenciais LLM:

```text
OPENAI_API_KEY
DEEPSEEK_API_KEY
MIMO_API_KEY
XAI_API_KEY
DASHSCOPE_API_KEY
GEMINI_API_KEY
ANTHROPIC_API_KEY
```

`--web-performance-max-pages` limita logical pages externas; `0` significa todas. Em `both`, cada página pode produzir dois contextos PageSpeed. Timeout não gera retry automático.

### 9.5 Falha

Após `run_audit` concluir, M21 é enrichment. Falha inesperada deve ser registrada/logada como problema operacional de coleta e não destruir o resultado principal já produzido.

## 10. Scoring

`SCORE-GEO-002` é determinístico sobre RuleExecutions persistidas.

A camada de scoring não deve reexecutar website ou IA.

M20 é estritamente downstream e não pode invalidar ou recalcular scoring já concluído.

M21 também é estritamente externo ao scoring. Nenhum Lighthouse score, LCP/INP/CLS, PageSpeed category score ou estado CWV é automaticamente convertido em peso, RuleResult, ScoreContribution, Coverage, Confidence ou Overall Readiness.

## 11. Reporting interno

M11/M15/M16/M17/M18 preservam seus contratos intermediários para compatibilidade de testes/módulos.

Durante `run_audit`, esses HTMLs intermediários não são o contrato final do usuário.

## 12. Report site final

O contrato final materializa:

```text
report/
├─ index.html
├─ mobile.html             # condicional
├─ desktop.html            # condicional
├─ remediation.html
├─ content-suggestions.html
├─ web-performance.html
├─ ai-usage.html
├─ references.html
└─ css/
   └─ site.css
```

`report/index.html` é o `AuditRunResult.report_path` e o `reports.file_path` persistido.

Após materialização bem-sucedida, intermediários `report.html` e `remediation.html` da raiz são removidos.

`m20_reporting` é uma projeção sobre dados já persistidos: escreve `content-suggestions.html`, conecta a navegação compartilhada e inclui a telemetria M20 em `ai-usage.html`. O renderer não chama provider.

`m21_reporting` projeta `web-performance.html`, adiciona resumo ao `index.html`, referências oficiais em `references.html` e link de navegação compartilhada. Não reexecuta PageSpeed/CrUX e não recalcula `SCORE-GEO-002`.

## 13. Separação de domínio na apresentação

- `index.html`: visão executiva/readiness + resumo M21 claramente externo;
- `mobile.html`: evidência e resultados Mobile;
- `desktop.html`: evidência e resultados Desktop;
- `remediation.html`: causa/prioridade/correção;
- `content-suggestions.html`: texto opcional e JSON-LD advisory;
- `web-performance.html`: Lighthouse lab, CrUX/Core Web Vitals e telemetria de coleta externa;
- `ai-usage.html`: operação/telemetria M18 e M20, separadas por finalidade;
- `references.html`: fontes, metodologia e referências M21.

Essa separação impede confundir falha de provider IA ou serviço de medição externa com finding do website.

## 14. CSS

Todas as páginas finais referenciam:

```text
report/css/site.css
```

CSS inline/embutido não pertence ao contrato final do report site.

## 15. Segurança

Secrets nunca devem ser persistidos em:

- audit.db como valor de credencial;
- artifacts;
- report site;
- logging operacional.

Payload estruturado exibido deve passar por escaping/redaction apropriado.

M20 não persiste headers de autenticação nem bodies de erro de provider não sanitizados.

M21 não persiste API keys, URL de requisição contendo `key=`, headers de autenticação ou corpo de erro externo não sanitizado. Artifacts são apenas respostas de sucesso utilizadas na projeção.

## 16. Fonte de verdade

```text
audit.db + artifacts
```

HTML é projeção. Report generation não pode recalcular Score/Finding nem chamar provider externo.

M20 external calls, quando habilitadas, ocorrem **antes** da materialização final e persistem o resultado; a projeção HTML apenas lê o estado reabrível.

M21 external calls, quando habilitadas, ocorrem como enrichment após a auditoria principal. Depois de persistidas as tabelas/artifacts M21, `web-performance.html` é reabrível sem nova chamada.

## 17. Reprodutibilidade

Versionar:

- auditor;
- ruleset;
- rendering policy;
- prompt/contract semântico quando aplicável;
- provider adapter/qualification contract;
- contrato M20;
- contrato M21 e interpretação de field/lab data;
- scoring;
- prioritization;
- reporting contract.

A promoção de um provider de extensão de `PROVISIONAL` para `QUALIFIED` ou sua entrada em `AUTO` exige qualificação/smoke explícitos e mudança versionada; não pode ocorrer por simples presença de credencial.
