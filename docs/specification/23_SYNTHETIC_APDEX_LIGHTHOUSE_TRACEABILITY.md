# M23 — Synthetic Navigation Apdex + Lighthouse Traceability

**Status:** CANDIDATE — implementação exige smoke humano controlado antes de merge.  
**Escopo:** Web Performance sintética e rastreabilidade de configuração Lighthouse.  
**Não altera:** `BR-GEO-*`, `SCORE-GEO-002`, Coverage, Confidence, Consolidation, findings GEO ou recomendações GEO.

## 1. Objetivo

M23 adiciona uma medição sintética de Apdex baseada em uma Task explícita de navegação e torna auditável a configuração efetiva de execução Lighthouse já persistida pelo M21.

M23 existe porque M22 corretamente proíbe inferir Apdex de Lighthouse/Core Web Vitals. Um índice Apdex só é calculável quando existe:

1. uma Task definida;
2. threshold `T` explícito;
3. população de tempos de resposta dessa Task;
4. classificação Satisfied/Tolerating/Frustrated segundo a especificação Apdex.

## 2. Task medida

`TASK_ID = NAVIGATION_LOAD`.

- início: imediatamente antes de `page.goto`;
- término: conclusão de `page.goto(..., wait_until="load")`;
- unidade persistida: milissegundos;
- cada amostra usa BrowserContext novo;
- cache do browser é explicitamente desabilitado;
- perfis de CPU/rede são determinísticos e versionados;
- não há randomização de RTT/throughput/CPU na baseline M23.

A Task mede navegação sintética controlada. Ela não deve ser apresentada como RUM, APM, experiência real de usuário ou tempo de transação de negócio.

## 3. Fórmula

Para `N` amostras válidas:

```text
Apdex = (Satisfied + 0.5 × Tolerating) / N
```

Classificação:

```text
Satisfied : duração <= T
Tolerating: duração > T e <= 4T
Frustrated: duração > 4T
```

Erros de aplicação/servidor, timeout e erro de navegação são `FRUSTRATED` quando o perfil sintético foi aplicado e a tentativa representa uma execução válida da Task.

Falha da ferramenta em iniciar/aplicar browser, CPU ou rede é amostra inválida e fica fora do denominador. A exclusão precisa permanecer persistida e auditável.

## 4. Threshold T

M23 é default OFF.

Quando habilitado, `T` é obrigatório via CLI ou ambiente. O SearchGEO não inventa T a partir de Lighthouse, LCP, INP, CLS ou tempos históricos.

O timeout por amostra deve ser estritamente maior que `4T` para não truncar artificialmente a faixa Frustrated.

## 5. Tamanho do grupo

Default operacional:

```text
100 amostras válidas por URL/dispositivo
```

Grupos com 1–99 amostras válidas podem ser calculados para diagnóstico, mas são marcados como `small_group=*` e não constituem o grupo final normal.

A baseline tenta substituir amostras inválidas até o orçamento `max_attempts_per_context`. O default desse orçamento é `ceil(1.25 × target_valid_samples)`.

## 6. Perfis e reprodutibilidade

Perfis sintéticos Mobile/Desktop têm versão explícita. O executor registra:

- viewport e device properties;
- User-Agent;
- CPU slowdown;
- RTT;
- download/upload throughput;
- connection type;
- cache policy;
- versão do profile;
- ambiente do host e versão Chromium/Playwright quando disponível.

A implementação não deve afirmar equivalência entre o perfil M23 e o profile efetivo de Lighthouse.

## 7. Pacing, concorrência e carga

Default:

```text
max_pages    = 1
delay        = 1 s entre inícios
concurrency  = 1
maximum      = 2 workers
```

O pacer controla inícios de navegação. Uma navegação pode carregar HTML, CSS, JavaScript, imagens, fontes e terceiros; portanto `N` amostras não equivale a `N` requests HTTP.

O console deve mostrar carga sintética separadamente da exposição financeira. M23:

- não chama LLM;
- não chama PageSpeed/CrUX por si só;
- não tem preço monetário de API próprio;
- usa CPU/RAM/tempo local e tráfego HTTP real contra o alvo.

Execução de grupo grande em produção depende de autorização e capacidade do ambiente auditado.

## 8. CLI

Flags:

```text
--synthetic-apdex / --no-synthetic-apdex
--apdex-threshold-seconds
--apdex-samples-per-context
--apdex-max-attempts-per-context
--apdex-max-pages
--apdex-timeout-seconds
--apdex-delay-seconds
--apdex-concurrency
```

Variáveis:

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

Precedência: CLI > ambiente > defaults seguros.

Variáveis de tuning inválidas não devem quebrar auditorias quando M23 está OFF.

## 9. Persistência

Tabelas aditivas:

```text
synthetic_apdex_runs
synthetic_apdex_samples
synthetic_apdex_summaries
lighthouse_execution_profiles
```

Cada amostra mantém status, classificação, duração, HTTP status, URL final, profile, métodos CPU/rede, cache policy, erro sanitizado e timestamp.

Nenhum secret deve ser persistido.

## 10. Lighthouse traceability

M23 lê exclusivamente artifacts M21 já existentes e extrai `lighthouseResult.configSettings`/environment/timing quando disponíveis.

Campos não observados permanecem `NULL`/ausentes. É proibido inventar:

- throttling method;
- RTT/throughput;
- CPU slowdown;
- viewport;
- User-Agent;
- benchmark index;
- duração do Lighthouse.

O tempo total de execução Lighthouse é telemetria do Lighthouse e não entra no Apdex.

## 11. Reporting

Quando M23 está habilitado e chega ao estágio de reporting, gera:

```text
report/apdex.html
```

A página deve mostrar:

- estado M23;
- `T` e `4T`;
- tamanho do grupo;
- Satisfied/Tolerating/Frustrated;
- Apdex;
- min/max/mean/median;
- p75/p90/p95/p99;
- desvio padrão/CV;
- tendência entre metades da amostra;
- perfil sintético;
- rastreabilidade Lighthouse quando existente;
- ambiente do executor;
- aviso de carga;
- separação explícita de SCORE-GEO-002, Lighthouse, CrUX e IA.

`apdex.html` deve participar do menu canônico somente quando o arquivo existir.

## 12. Fail-open

M23 é downstream da auditoria SearchGEO principal.

Falha de M23:

- não transforma o site em FAIL GEO;
- não altera findings/scoring;
- não invalida o audit principal;
- deve ser registrada no log operacional;
- deve produzir status de limitação operacional quando possível.

M21 e M23 são independentes: falha de PageSpeed/CrUX não impede, por si só, Synthetic Apdex; falha de Synthetic Apdex não invalida M21.

## 13. Console

O console deve expor M23 como item próprio e manter:

- uma tela lógica por vez;
- T obrigatório quando ON;
- amostras/tentativas/páginas/timeout/delay/concorrência;
- teto estimado de navegações;
- aviso de que subresources multiplicam requests;
- zero custo de API próprio;
- observabilidade de progresso `M23_APDEX_SAMPLE`;
- totais reais persistidos no resumo final.

## 14. Gate de smoke humano

O primeiro smoke humano não deve usar 100 amostras em produção.

Gate inicial recomendado:

```text
1 URL autorizada
1 device
T explícito
3–5 amostras válidas
concurrency=1
delay >= 1s
```

Critérios:

1. execução completa sem traceback;
2. `small_group=*` explícito;
3. amostras e contagens persistidas;
4. Apdex reproduzível a partir de S/T/F;
5. `apdex.html` no menu canônico;
6. nenhum impacto em SCORE-GEO-002;
7. console mostra carga, início/fim/duração e resultados;
8. nenhum token/secret novo;
9. 0 chamadas LLM adicionais;
10. 0 chamadas PageSpeed/CrUX adicionadas por M23.

Uma execução de 100 amostras contra ambiente real requer autorização humana específica de carga/capacidade.

## 15. Referências

- Apdex Technical Specification v1.1: https://www.apdex.org/wp-content/uploads/2020/09/ApdexTechnicalSpecificationV11_000.pdf
- Chrome DevTools Protocol — Emulation: https://chromedevtools.github.io/devtools-protocol/tot/Emulation/
- Chrome DevTools Protocol — Network: https://chromedevtools.github.io/devtools-protocol/tot/Network/
- Lighthouse — Understanding results: https://github.com/GoogleChrome/lighthouse/blob/main/docs/understanding-results.md
- Lighthouse — Emulation: https://github.com/GoogleChrome/lighthouse/blob/main/docs/emulation.md
