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
   ├─ accessibility.html
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

M22 não exige tabela própria: projeta deterministically os artifacts M21 já persistidos. M21/M22 não escrevem em `scores`, `score_contributions`, `rule_executions`, `findings` ou `recommendations` GEO.

## artifacts

RAW, rendered HTML, conteúdo principal, Structured Data, screenshots e outras evidências referenciadas por caminhos relativos.

Quando M21 está habilitado e uma chamada externa retorna JSON válido, a resposta é preservada em:

```text
artifacts/web-performance/
├─ WPE-....pagespeed.json
└─ WPE-....crux.json         # quando CrUX API direta foi chamada com sucesso
```

Esses artefatos permitem reabrir a origem dos números e diagnósticos de Lighthouse/Core Web Vitals e também a projeção de Acessibilidade M22 sem repetir a chamada externa.

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

M22 não gera nova chamada externa, portanto não cria uma segunda telemetria de rede para a mesma evidência Lighthouse.

Campos sensíveis são redigidos. API keys, Authorization headers, tokens, passwords e URLs contendo credenciais não podem ser registrados.

## report/index.html

Dashboard executivo GEO: devices, Overall, Coverage, Confidence, Consolidation, dimensões/actionability e links.

Quando M21/M22 estão materializados, recebe resumos explicitamente separados de Web Performance e Acessibilidade. Nenhum desses resumos substitui o Overall do `SCORE-GEO-002`.

## mobile.html / desktop.html

Gerados somente para devices auditados; contêm scorecard GEO, páginas, snapshots, findings e estado semântico do contexto.

## remediation.html

Plano técnico GEO evidence-backed baseado em prioridade e M16/M17.

## content-suggestions.html

Projeção advisory M20:

- status M20;
- sugestões textuais aceitas, com finding/evidence/provider/model;
- proposta JSON-LD quando ausente;
- melhorias quando JSON-LD existe;
- aviso de revisão humana.

A página não altera Score/findings e não aplica alterações ao website.

## accessibility.html

Projeção M22 do domínio Acessibilidade, reutilizando o artifact Lighthouse M21.

Pode conter:

- Lighthouse Accessibility score por URL/device;
- audits automatizados reprovados;
- selector e snippet apenas quando fornecidos pela fonte;
- node label/explanation quando fornecidos;
- sugestão de tratamento;
- referência W3C/WAI específica quando mapeada;
- quantidade de checks manuais declarados pelo Lighthouse;
- aviso `Conformidade WCAG: NÃO DETERMINADA`.

M22 não inventa selector ou HTML observado. Um score Lighthouse 100/100 não é apresentado como certificação WCAG.

## web-performance.html

Projeção M21/M22 do domínio Performance:

- estado de habilitação e execução;
- limite de páginas e contextos medidos;
- Lighthouse **Performance** e métricas lab FCP, Speed Index, LCP, TBT e CLS quando retornadas;
- Core Web Vitals de campo LCP/INP/CLS no p75 quando disponíveis;
- assessment `PASS`, `FAIL`, `INCOMPLETE` ou `UNAVAILABLE` sem transformar ausência de amostra em falha;
- origem do field data (`PAGESPEED_CRUX` ou `CRUX_API`);
- escopo URL/origin quando determinável;
- telemetria operacional de PageSpeed/CrUX;
- referências dos artifacts JSON;
- diagnósticos M22 de render blocking, critical path, LCP, layout shift, JavaScript/main thread, CSS, imagens, fontes, terceiros, documento/servidor, DOM e cache quando presentes no Lighthouse;
- por ocorrência, URL/selector/snippet/savings/tamanho/duração somente quando a fonte fornece;
- aviso explícito de que M21/M22 não recalculam `SCORE-GEO-002`.

O Accessibility score coletado pelo PageSpeed não pertence ao scorecard de Performance; M22 o projeta em `accessibility.html`.

O status agregado M21 segue regra distinta do assessment CWV. `PARTIAL` significa que existe evidência externa útil, mas ao menos um componente/contexto solicitado falhou ou ficou indisponível.

## Apdex

Não existe artifact ou valor Apdex calculado pelo M22.

Estado público:

```text
Apdex: NÃO CALCULADO
```

Motivo: Lighthouse/CrUX não fornecem, para o contrato atual, a população de tempos de resposta transacionais de uma Task/Task Chain com threshold `T` explicitamente aprovado. LCP, INP, CLS, TBT e duração da chamada PageSpeed não são tratados como substitutos de Apdex.

## ai-usage.html

Telemetria operacional separada do readiness, incluindo M18 e M20: estratégia/provider/model, URL/device, status, tokens, duração, custo estimado e erros sanitizados.

M21/M22 não adicionam linhas PageSpeed/CrUX/Acessibilidade nesta página; medição web não é consumo de SemanticProvider.

## references.html

Fontes oficiais/primárias, natureza das regras, fórmulas e limites do modelo interno.

M21 adiciona referências oficiais de PageSpeed Insights, CrUX, Lighthouse Performance e Core Web Vitals. M22 adiciona W3C/WAI para Acessibilidade, Chrome Performance Insights para diagnósticos técnicos e a especificação pública Apdex somente para governar a semântica de cálculo/não cálculo.

Essas fontes validam fenômenos específicos; não homologam um score GEO universal nem o `SCORE-GEO-002`.

## CSS e navegação

Todos os HTMLs finais usam `report/css/site.css`; não há CSS final embutido no head. A navegação final usa o core canônico compartilhado. `Acessibilidade` e `Web Performance` são itens separados.

## Device selection

Artifacts e chamadas externas só existem para devices selecionados/materializados.

No M21:

```text
mobile  → PageSpeed strategy=mobile; CrUX formFactor=PHONE
desktop → PageSpeed strategy=desktop; CrUX formFactor=DESKTOP
both    → mede os dois contextos quando a página estiver dentro do limite M21
```

M22 mantém o mesmo URL/device da observação persistida.

## Controle de consumo externo M21/M22

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

PageSpeed/CrUX não geram tokens OpenAI/DeepSeek/MiMo. Nenhuma chamada LLM adicional é introduzida pelo M21/M22. M22 não realiza segunda chamada Google; somente lê o artifact M21.

O timeout default M21 permanece 60 segundos por request e não há retry automático. Em execução real em que PageSpeed exceda esse intervalo, o operador pode elevar explicitamente `--web-performance-timeout-seconds`.

## Segurança

Não persistir API key, Authorization, senha/secret ou body integral sensível. Credenciais permanecem isoladas por provider/serviço.

M21 não persiste request URL contendo `key=...`; persiste somente URL alvo, status/duração/erro sanitizado e o payload de resposta válido. M22 só lê paths relativos persistidos dentro do workspace.

## Portabilidade

Para preservar screenshots, respostas externas M21, projeções M22 e diagnóstico operacional, mova o workspace inteiro, incluindo `audit.db`, `artifacts/`, `logs/` e `report/`.
