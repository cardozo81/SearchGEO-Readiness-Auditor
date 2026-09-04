# OUTPUTS_AND_ARTIFACTS.md

## Workspace

```text
<audits-root>/<AUD-ID>/
├─ audit.db
├─ artifacts/
│  └─ web-performance/         # quando M21 obtém respostas externas válidas
├─ logs/
│  └─ audit.log                # log operacional JSONL, sanitizado e fail-open
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

`audit.db` + `artifacts/` são fonte persistente de evidência/estado; `logs/` é telemetria operacional auxiliar; `report/` é projeção humana.

## audit.db

Inclui audit/target/pages/snapshots, RuleExecutions, Evidence, findings, semântica, scores, recomendações, M16/M17, report metadata, M18, M20, M21 e M23.

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

Tabelas M23:

```text
synthetic_apdex_runs
synthetic_apdex_samples
synthetic_apdex_summaries
lighthouse_execution_profiles
```

M22 não exige tabela própria: projeta deterministicamente os artifacts M21 já persistidos. M21/M22/M23 não escrevem em `scores`, `score_contributions`, `rule_executions`, `findings` ou `recommendations` GEO.

M23 persiste sua própria medição e classificação sem recalcular `SCORE-GEO-002`.

## artifacts

RAW, rendered HTML, conteúdo principal, Structured Data, screenshots e outras evidências referenciadas por caminhos relativos.

Quando M21 está habilitado e uma chamada externa retorna JSON válido, a resposta é preservada em:

```text
artifacts/web-performance/
├─ WPE-....pagespeed.json
└─ WPE-....crux.json         # quando CrUX API direta foi chamada com sucesso
```

Esses artefatos permitem reabrir a origem dos números e diagnósticos de Lighthouse/Core Web Vitals e também a projeção de Acessibilidade M22 sem repetir a chamada externa.

Quando M23 encontra artifacts PageSpeed já persistidos, pode extrair `lighthouseResult.configSettings` para `lighthouse_execution_profiles`. Essa rastreabilidade é leitura local do artifact existente; não dispara nova chamada PageSpeed/CrUX.

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
- falha operacional fail-open do enriquecimento M21;
- início/fim do M23;
- progresso das amostras Synthetic Apdex;
- classificação/status/duração de amostra M23 sem segredo;
- falhas operacionais M23 fail-open.

M22 não gera nova chamada externa. M23 também não cria chamada PageSpeed/CrUX; ele executa navegações Chromium próprias somente quando explicitamente habilitado.

Campos sensíveis são redigidos. API keys, Authorization headers, tokens, passwords e URLs contendo credenciais não podem ser registrados.

## report/index.html

Dashboard executivo GEO: devices, Overall, Coverage, Confidence, Consolidation, dimensões/actionability e links.

Quando M21/M22/M23 estão materializados, recebe resumos/links explicitamente separados. Nenhum desses domínios substitui o Overall do `SCORE-GEO-002`.

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

- estado de habilitação e execução M21;
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

### Relação com Apdex

M21/M22 **não calculam Apdex a partir de Lighthouse ou CrUX**. Se M23 estiver desligado, não existe população Synthetic Apdex. Se M23 estiver habilitado, o cálculo aparece no domínio separado `apdex.html`.

Portanto, uma mensagem M22 equivalente a “Apdex não calculado por este domínio” não contradiz a existência de M23; significa apenas que Lighthouse/CrUX não são usados como substitutos metodológicos para Apdex.

## apdex.html — M23

Quando M23 está habilitado/materializado, o report contém:

```text
report/apdex.html
```

A página apresenta, conforme dados persistidos:

- estado M23;
- threshold `T` e fronteira `4T`;
- alvo de amostras válidas e tentativas;
- Apdex por URL/device;
- contagens Satisfied/Tolerating/Frustrated;
- amostras válidas e inválidas;
- p75/p90/p95/p99;
- média, mediana, dispersão, coeficiente de variação e tendência;
- perfil sintético determinístico e versão;
- host executor/versões quando disponíveis;
- rastreabilidade de `lighthouseResult.configSettings` quando M21 já forneceu artifact;
- aviso de grupo pequeno (`*`) quando houver 1–99 amostras válidas.

Fórmula:

```text
Apdex = (Satisfied + 0.5 × Tolerating) / Total de amostras válidas

Satisfied  <= T
Tolerating > T e <= 4T
Frustrated > 4T
```

Timeout/erro de navegação ou erro de aplicação/servidor é `FRUSTRATED` quando o profile sintético foi aplicado. Falha da própria ferramenta/profile produz amostra inválida e fica fora do denominador.

M23 não altera `SCORE-GEO-002`, Coverage, Confidence, RuleExecution ou Finding GEO.

## ai-usage.html

Telemetria operacional separada do readiness, incluindo M18 e M20: estratégia/provider/model, URL/device, status, tokens, duração, custo estimado e erros sanitizados.

M21/M22/M23 não adicionam linhas de uso de SemanticProvider nessa página. M23 gera `0` tokens de IA.

## references.html

Fontes oficiais/primárias, natureza das regras, fórmulas e limites do modelo interno.

M21 adiciona referências oficiais de PageSpeed Insights, CrUX, Lighthouse Performance e Core Web Vitals. M22 adiciona W3C/WAI para Acessibilidade e Chrome Performance Insights para diagnósticos técnicos. M23 adiciona a especificação Apdex e referências de Chrome DevTools Protocol/Lighthouse pertinentes aos profiles e rastreabilidade.

Essas fontes validam fenômenos específicos; não homologam um score GEO universal nem o `SCORE-GEO-002`.

## CSS e navegação

Todos os HTMLs finais usam `report/css/site.css` como folha compartilhada. A navegação final usa o core canônico compartilhado. `Acessibilidade` e `Web Performance` são itens separados; `Apdex` entra somente quando `apdex.html` existe.

## Device selection

Artifacts e chamadas/medições só existem para devices selecionados/materializados.

No M21:

```text
mobile  → PageSpeed strategy=mobile; CrUX formFactor=PHONE
desktop → PageSpeed strategy=desktop; CrUX formFactor=DESKTOP
both    → mede os dois contextos quando a página estiver dentro do limite M21
```

M22 mantém o mesmo URL/device da observação persistida.

No M23, cada URL/device selecionado dentro de `--apdex-max-pages` forma um contexto Synthetic Apdex independente.

## Controle de consumo M21/M22/M23

M21 e M23 são default OFF.

M21:

```text
SEARCHGEO_WEB_PERFORMANCE
SEARCHGEO_WEB_PERFORMANCE_MAX_PAGES
SEARCHGEO_WEB_PERFORMANCE_TIMEOUT_SECONDS
SEARCHGEO_WEB_PERFORMANCE_FIELD_SOURCE
SEARCHGEO_LIGHTHOUSE_CATEGORIES
SEARCHGEO_PAGESPEED_API_KEY
SEARCHGEO_CRUX_API_KEY
```

M23:

```text
SEARCHGEO_SYNTHETIC_APDEX
SEARCHGEO_APDEX_THRESHOLD_SECONDS
SEARCHGEO_APDEX_SAMPLES_PER_CONTEXT
SEARCHGEO_APDEX_MAX_ATTEMPTS_PER_CONTEXT
SEARCHGEO_APDEX_MAX_PAGES
SEARCHGEO_APDEX_TIMEOUT_SECONDS
SEARCHGEO_APDEX_DELAY_SECONDS
SEARCHGEO_APDEX_CONCURRENCY
```

PageSpeed/CrUX não geram tokens de SemanticProvider. M22 não realiza segunda chamada Google. M23 adiciona `0` chamadas LLM e `0` chamadas PageSpeed/CrUX, mas gera tráfego HTTP real de navegador contra o alvo e consumo local de CPU/RAM/tempo.

Uma navegação M23 pode carregar muitos subrecursos. Logo 100 amostras não equivalem a 100 requests HTTP. Execuções relevantes contra produção exigem autorização e controle de carga.

## Segurança

Não persistir API key, Authorization, senha/secret ou body integral sensível. Credenciais permanecem isoladas por provider/serviço.

M21 não persiste request URL contendo `key=...`; persiste somente URL alvo, status/duração/erro sanitizado e o payload de resposta válido. M22 só lê paths relativos persistidos dentro do workspace.

M23 não exige API key própria, mas navega contra a URL auditada. O operador deve garantir autorização para a carga sintética planejada.

## Portabilidade

Para preservar screenshots, respostas externas M21, projeções M22, dados M23 e diagnóstico operacional, mova o workspace inteiro, incluindo `audit.db`, `artifacts/`, `logs/` e `report/`.
