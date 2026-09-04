# OUTPUTS_AND_ARTIFACTS.md

## Workspace

```text
<audits-root>/<AUD-ID>/
├─ audit.db
├─ artifacts/
│  └─ web-performance/       # quando M21 obtém respostas externas válidas
├─ logs/
│  └─ audit.log              # log operacional JSONL, sanitizado e fail-open
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

`audit.db` + `artifacts/` são fonte persistente de evidência/estado; `logs/` é telemetria operacional auxiliar; `report/` é projeção humana.

## audit.db

Inclui audit/target/pages/snapshots, RuleExecutions, Evidence, findings, semântica, scores, recomendações, M16/M17, report metadata, M18, M20 e M21.

Tabelas M20:

```text
content_remediation_runs
content_remediation_attempts
content_remediation_suggestions
jsonld_remediation_suggestions
```

Tabelas M21:

```text
web_performance_runs
web_performance_observations
web_performance_attempts
```

M21 é aditivo e não escreve em `scores`, `score_contributions`, `rule_executions`, `findings` ou `recommendations`.

## artifacts

RAW, rendered HTML, conteúdo principal, Structured Data, screenshots e outras evidências referenciadas por caminhos relativos.

Quando M21 está habilitado e uma chamada externa retorna JSON válido, a resposta é preservada em:

```text
artifacts/web-performance/
├─ WPE-....pagespeed.json
└─ WPE-....crux.json         # quando CrUX API direta foi chamada com sucesso
```

Esses artefatos permitem reabrir a origem dos números de Lighthouse/Core Web Vitals sem repetir a chamada externa.

Chaves de API não são gravadas nesses arquivos.

## logs/audit.log

Log operacional persistente em formato **JSON Lines (JSONL)**. Não é fonte de scoring e não substitui `audit.db`.

Registra, quando aplicável:

- início/fim/falha da auditoria;
- resumo de rendering;
- runtime do provider de IA sem credenciais;
- materialização do report site;
- início/fim do M21;
- cada tentativa PageSpeed/CrUX com URL alvo, device, status, HTTP, duração e erro sanitizado;
- geração do `web-performance.html`;
- falha operacional fail-open do enriquecimento M21.

O log permite distinguir, por exemplo:

```text
PageSpeed → TIMEOUTERROR
CrUX      → HTTP 200
M21       → PARTIAL
```

Campos sensíveis são redigidos. API keys, Authorization headers, tokens, passwords e URLs contendo credenciais não podem ser registrados.

Falha ao escrever o log é fail-open e não muda score, findings ou conclusão da auditoria.

Consulte também `docs/OPERATIONAL_LOGGING.md`.

## report/index.html

Dashboard executivo: devices, Overall, Coverage, Confidence, Consolidation, dimensões/actionability e links.

Com M21 materializado, recebe também um resumo explicitamente separado de Web Performance. Lighthouse/Core Web Vitals não substituem o Overall do `SCORE-GEO-002`.

## mobile.html / desktop.html

Gerados somente para devices auditados; contêm scorecard, páginas, snapshots, findings e estado semântico do contexto.

## remediation.html

Plano técnico evidence-backed baseado em prioridade e M16/M17.

## content-suggestions.html

Projeção advisory M20:

- status M20;
- sugestões textuais aceitas, com finding/evidence/provider/model;
- proposta JSON-LD quando ausente;
- melhorias quando JSON-LD existe;
- aviso de revisão humana.

A página não altera Score/findings e não aplica alterações ao website.

## web-performance.html

Projeção M21 de evidência externa:

- estado de habilitação e execução;
- limite de páginas e contextos medidos;
- Lighthouse Performance/Accessibility/Best Practices/SEO quando retornados;
- métricas lab FCP, Speed Index, LCP, TBT e CLS quando retornadas;
- Core Web Vitals de campo LCP/INP/CLS no p75 quando disponíveis;
- assessment `PASS`, `FAIL`, `INCOMPLETE` ou `UNAVAILABLE` sem transformar ausência de amostra em falha;
- origem do field data (`PAGESPEED_CRUX` ou `CRUX_API`);
- escopo URL/origin quando determinável;
- telemetria operacional de PageSpeed/CrUX;
- references dos artefatos JSON;
- política de quota/credenciais;
- aviso explícito de que M21 não recalcula `SCORE-GEO-002` e não representa probabilidade de citação.

O status agregado M21 segue regra distinta do assessment CWV. `PARTIAL` significa que existe evidência externa útil, mas ao menos um componente/contexto solicitado falhou ou ficou indisponível. Portanto, PageSpeed timeout + CrUX success é `PARTIAL`, ainda que todos os contextos tenham algum dado útil.

M21 não utiliza LLM. A telemetria de PageSpeed/CrUX não pertence a `ai-usage.html` porque não é consumo de IA generativa do SearchGEO.

## ai-usage.html

Telemetria operacional separada do readiness, incluindo M18 e M20: estratégia/provider/model, URL/device, status, tokens, duração, custo estimado e erros sanitizados.

M21 não adiciona linhas de PageSpeed/CrUX nesta página; sua telemetria operacional fica em `web-performance.html` e `logs/audit.log` para não confundir medição web com uso de SemanticProvider.

## references.html

Fontes oficiais/primárias, natureza das regras, fórmulas e limites do modelo interno.

M21 adiciona referências oficiais de PageSpeed Insights, CrUX, Lighthouse Performance e Core Web Vitals e registra o limite de inferência: essas fontes validam suas métricas específicas, não homologam um score GEO universal nem o `SCORE-GEO-002`.

## CSS e navegação

Todos os HTMLs finais usam `report/css/site.css`; não há CSS final embutido no head. A navegação final usa o core canônico compartilhado do report site, inclusive `web-performance.html`.

## Device selection

Artifacts e chamadas externas só existem para devices selecionados/materializados.

No M21:

```text
mobile  → PageSpeed strategy=mobile; CrUX formFactor=PHONE
desktop → PageSpeed strategy=desktop; CrUX formFactor=DESKTOP
both    → mede os dois contextos quando a página estiver dentro do limite M21
```

## Controle de consumo externo M21

M21 é default OFF.

Controles:

```text
SEARCHGEO_WEB_PERFORMANCE
SEARCHGEO_WEB_PERFORMANCE_MAX_PAGES
SEARCHGEO_WEB_PERFORMANCE_TIMEOUT_SECONDS
SEARCHGEO_WEB_PERFORMANCE_FIELD_SOURCE
SEARCHGEO_LIGHTHOUSE_CATEGORIES
SEARCHGEO_PAGESPEED_API_KEY
SEARCHGEO_CRUX_API_KEY
```

PageSpeed/CrUX não geram tokens OpenAI/DeepSeek/MiMo. Nenhuma chamada LLM adicional é introduzida pelo M21.

O timeout default permanece 60 segundos por request e não há retry automático. Em execução real em que PageSpeed exceda esse intervalo, o operador pode elevar explicitamente `--web-performance-timeout-seconds`, por exemplo para `180`.

## Segurança

Não persistir API key, Authorization, senha/secret ou body integral sensível. Credenciais permanecem isoladas por provider/serviço.

M21 não persiste request URL contendo `key=...`; persiste somente URL alvo, status/duração/erro sanitizado e o payload de resposta válido.

## Portabilidade

Para preservar screenshots, respostas externas M21 e diagnóstico operacional, mova o workspace inteiro, incluindo `audit.db`, `artifacts/`, `logs/` e `report/`.
