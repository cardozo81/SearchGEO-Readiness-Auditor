# REPORT_GUIDE.md

Guia de leitura do report site do SearchGEO Readiness Auditor.

## Ponto de entrada

Abra:

```text
<audits-root>/<AUD-ID>/report/index.html
```

Não é necessário servidor web. Os arquivos usam links relativos e CSS compartilhado.

## Estrutura

```text
report/
├─ index.html
├─ mobile.html               # quando Mobile foi auditado
├─ desktop.html              # quando Desktop foi auditado
├─ remediation.html
├─ content-suggestions.html
├─ accessibility.html        # quando M22 materializa a projeção
├─ web-performance.html
├─ apdex.html                # quando M23 está habilitado/materializado
├─ ai-usage.html
├─ references.html
└─ css/
   └─ site.css
```

O menu é comum às páginas existentes naquela auditoria. `Apdex` aparece somente quando `apdex.html` existe.

## Fronteiras de domínio

O report separa contextos que usam metodologias diferentes:

| Página | Domínio |
|---|---|
| `index.html` | visão executiva GEO + links/resumos explicitamente rotulados dos domínios auxiliares |
| `mobile.html` | evidência, findings e semântica GEO do contexto Mobile |
| `desktop.html` | evidência, findings e semântica GEO do contexto Desktop |
| `remediation.html` | causa raiz GEO, prioridade, alvo de correção, aceite e revalidação |
| `content-suggestions.html` | sugestões textuais M20 opcionais e revisão JSON-LD por página/device |
| `accessibility.html` | acessibilidade automatizada Lighthouse, separada de GEO e Performance |
| `web-performance.html` | Lighthouse Performance, Core Web Vitals/CrUX e diagnósticos técnicos de performance M21/M22 |
| `apdex.html` | M23 Synthetic Navigation Apdex com amostras reais de navegação em Chromium |
| `ai-usage.html` | telemetria operacional M18/M20, separada por finalidade |
| `references.html` | fontes oficiais, natureza das regras e fórmulas/metodologias do auditor |

A mesma evidência física pode ser útil em mais de um domínio. Isso não autoriza misturar score, severidade ou conclusão. Relações entre GEO, Acessibilidade, Performance e Apdex devem ser apresentadas como cross-reference explícito, não como penalização implícita.

## `index.html`

É o dashboard executivo. Para GEO, leia nesta ordem:

1. dispositivo efetivamente auditado;
2. Readiness/Overall quando consolidado;
3. Coverage;
4. Confidence;
5. Consolidation;
6. dimensões;
7. findings/remediações quando existirem.

Resumos de Acessibilidade, Web Performance e M23 são rotulados como domínios independentes e não entram no Overall GEO.

## Score / Readiness GEO

O Score representa somente as regras GEO efetivamente avaliadas que participam do cálculo.

Baseline:

```text
PASS    = 1,00
WARNING = 0,50 por padrão
FAIL    = 0,00
```

`UNKNOWN`, `ERROR` e `NOT_APPLICABLE` não são convertidos em `FAIL`.

As faixas visuais `Excelente / Alta / Moderada / Baixa / Crítica` são classificação interna do SearchGEO. Não são thresholds oficiais de Google, OpenAI ou outro mantenedor.

Lighthouse Accessibility, Lighthouse Performance, Core Web Vitals e Synthetic Apdex M23 não são incorporados matematicamente ao `SCORE-GEO-002`.

## Coverage

Coverage responde: quanto do universo aplicável realmente foi avaliado?

```text
evaluated applicable weight / total applicable weight
```

Coverage baixa significa **análise incompleta**, não qualidade baixa do site.

Exemplo:

```text
Score:      90/100
Coverage:   45%
Confidence: LOW
```

A leitura correta não é “site excelente”. A leitura correta é: a parte avaliada teve resultado alto, porém menos da metade do universo aplicável foi suficientemente avaliada e a conclusão é fraca.

## Confidence

Confidence responde: quão forte é a conclusão do auditor com as evidências disponíveis?

No `SCORE-GEO-002` ela considera principalmente Coverage, completude de evidência e erros de execução.

**Confidence LOW não significa que o texto do website é ruim, não confiável ou não aderente a GEO.** Significa que o auditor não possui base suficiente para sustentar uma conclusão forte.

Também não deve ser confundida com confidence de provider de IA, score Lighthouse, CWV ou Apdex.

## Consolidation

Estados:

```text
CONSOLIDATED
PARTIAL
NOT_CONSOLIDATED
NOT_APPLICABLE
```

Uma dimensão `NOT_APPLICABLE` legítima não recebe 0 nem 100 e fica fora do Overall. Uma dimensão aplicável `NOT_CONSOLIDATED` pode impedir publicação de um Overall.

## Mobile e Desktop

Quando `--device-context mobile`:

- existe `mobile.html`;
- `desktop.html` não é gerado;
- o report não apresenta Desktop como se tivesse sido auditado.

Quando `desktop`, vale o inverso. Quando `both`, existem as duas páginas e a comparação entre contextos pode ser interpretada.

Diferença Mobile × Desktop não é automaticamente defeito. A regra BR-GEO-052 distingue diferença material de falha.

M20, M21, M22 e M23 preservam os contextos existentes; não fabricam resultado para device não materializado.

## Página por dispositivo

`mobile.html` e `desktop.html` apresentam:

- scorecard GEO do dispositivo;
- dimensões GEO;
- páginas/URLs auditadas;
- HTTP/final URL;
- snapshot visual quando disponível;
- findings aplicáveis ao dispositivo;
- avaliações semânticas não aprovadas.

Detalhes extensos ficam recolhidos em `details`, reduzindo poluição visual sem remover rastreabilidade.

## Remediações GEO

`remediation.html` organiza por problema/causa, não por tamanho do crawl.

Quando M16/M17 conseguiu materializar a causa, a ocorrência pode exibir causa precisa, reason code, escopo, selector observado, HTML observado quando persistido, alvo técnico, localização esperada, diagnostic confidence, mudança recomendada, observado versus esperado, exemplo pós-correção, decisão humana, critérios de aceite e revalidação.

Uma condição `UNKNOWN`/evidência insuficiente não deve ser transformada artificialmente em ordem de alteração do site.

## Conteúdo e JSON-LD

`content-suggestions.html` é advisory e não participa do score.

### Sugestões textuais

Quando M20 textual está desabilitado, a página declara explicitamente o estado e não apresenta conteúdo como se tivesse sido gerado por IA.

Quando habilitado e houver findings elegíveis/evidência suficiente, cada proposta pode mostrar URL/device, `rule_id`/finding, objetivo, local sugerido, texto exato, evidence IDs, provider/model, confidence da sugestão e aviso de revisão humana obrigatória.

`Confidence LOW` do auditor, sozinha, nunca é gatilho da seção. A proposta não é aplicada automaticamente e não altera Score, Coverage, Confidence ou Finding.

### JSON-LD

Quando o snapshot não possui JSON-LD persistido, a página pode exibir um baseline conservador `WebPage` usando somente valores observados. Quando markup já existe, o report não o substitui integralmente; pode apontar problemas verificáveis.

JSON-LD é reforço opcional. Não existe markup especial GEO/AEO obrigatório e markup correto não garante rich result.

## Acessibilidade

`accessibility.html` pertence a um domínio próprio.

A fonte automatizada é a categoria Accessibility do Lighthouse já coletada pelo M21 quando `--web-performance` está habilitado. M22 **não executa nova chamada PageSpeed/CrUX** para criar esta página.

Cada falha automatizada pode apresentar URL/device, score Lighthouse Accessibility, audit ID Lighthouse, título/descrição, selector/snippet apenas quando a fonte fornece, node label/explanation, sugestão de tratamento e referência W3C/WAI quando mapeada.

### Regra de evidência

O SearchGEO não inventa selector ou HTML para uma ocorrência Lighthouse. Quando a fonte não fornece esses campos, o report registra a ausência.

### ARIA

`aria-label` não é correção universal. Para nome acessível, a solução pode envolver texto nativo, `<label>`, `aria-labelledby`, `aria-label` ou outro mecanismo previsto pela plataforma. Prefira semântica HTML nativa quando suficiente.

### Limite da automação

Lighthouse é ferramenta automatizada e possui verificações que exigem revisão manual. Por isso:

```text
Conformidade WCAG: NÃO DETERMINADA
```

Mesmo Lighthouse 100/100 não deve ser comunicado como comprovação de conformidade WCAG.

## Web Performance

`web-performance.html` pertence ao domínio Performance e permanece fora do Score GEO.

### Campo — CrUX/Core Web Vitals

Quando houver amostra suficiente:

- LCP p75;
- INP p75;
- CLS p75;
- escopo URL/origin;
- fonte;
- PASS/FAIL/INCOMPLETE/UNAVAILABLE.

Thresholds de “boa” experiência usados pelo M21:

```text
LCP <= 2.5 s
INP <= 200 ms
CLS <= 0.10
```

Dado faltante não vira FAIL artificial.

### Laboratório — Lighthouse Performance

A página mostra, quando disponíveis, Performance score, FCP, Speed Index, LCP, TBT e CLS.

O Accessibility score coletado no mesmo payload não é métrica de Performance; ele é projetado em `accessibility.html`.

### Diagnósticos técnicos M22

A página pode detalhar, quando o artifact Lighthouse fornece evidência, render-blocking, critical path, LCP, layout shift, JavaScript/main thread, CSS, imagens, fontes, terceiros, latência do documento/servidor, DOM e cache.

Por ocorrência, preserva somente dados realmente presentes na fonte, como URL do recurso, selector, snippet, `wastedMs`, `wastedBytes`, tamanho e duração.

### Primeira dobra e causalidade

O report não declara que todo elemento visualmente na primeira dobra causa baixa performance. A causalidade é baseada em diagnósticos do navegador/Lighthouse.

É válido afirmar “o Lighthouse classificou este recurso como render-blocking” quando o artifact demonstra isso. Não é válido afirmar “este recurso é a única causa do LCP ruim” sem evidência específica.

### Relação M21/M22 com Apdex

M21/M22 não calculam Apdex a partir de LCP, INP, CLS, TBT, duração da chamada PageSpeed ou uma execução Lighthouse isolada. Essa fronteira metodológica permanece válida após o M23.

Quando M23 está OFF, não há Synthetic Apdex. Quando M23 está ON, o cálculo é materializado separadamente em `apdex.html` usando amostras reais de navegação e `T` explícito.

## Synthetic Navigation Apdex — M23

`apdex.html` é um domínio separado de Web Performance sintética.

### Ativação

M23 é default OFF e exige `T` explícito:

```powershell
searchgeo audit https://example.com `
  --synthetic-apdex `
  --apdex-threshold-seconds 1.5
```

### Task

```text
NAVIGATION_LOAD
início = imediatamente antes de page.goto
fim    = conclusão de wait_until=load
```

Cada amostra usa BrowserContext novo e cache do browser desabilitado. Perfis CPU/rede são determinísticos e versionados.

### Fórmula

```text
Apdex = (Satisfied + 0.5 × Tolerating) / Total de amostras válidas

Satisfied  <= T
Tolerating > T e <= 4T
Frustrated > 4T
```

Timeout/erro de navegação ou erro de aplicação/servidor conta como `FRUSTRATED` quando o profile foi efetivamente aplicado. Falha de browser/ferramenta/profile é excluída do denominador como amostra inválida.

### Grupo pequeno

O default normal é 100 amostras válidas por URL/device. Grupos com 1–99 recebem `*`. Um smoke com 5/5 válidas pode ter status M23 `PARTIAL` exclusivamente por ser small group, sem indicar falha operacional.

### Leitura da página

A página pode apresentar:

- estado M23;
- `T` e `4T`;
- score Apdex por URL/device;
- S/T/F;
- válidas, inválidas e tentativas;
- p75/p90/p95/p99;
- média/mediana/dispersão/CV/tendência;
- profile sintético e versão;
- host executor;
- rastreabilidade Lighthouse quando já existe artifact M21.

O tempo total Lighthouse não entra na fórmula Apdex.

### Custo e carga

M23 gera `0` chamadas LLM, `0` tokens IA e `0` chamadas PageSpeed/CrUX adicionais. Porém produz tráfego HTTP real contra o alvo e uso local de CPU/RAM/tempo. Uma navegação pode carregar muitos subrecursos; 100 amostras não equivalem a 100 requests HTTP.

Consulte [SYNTHETIC_APDEX.md](SYNTHETIC_APDEX.md).

## Uso de IA

`ai-usage.html` é operacional e separa finalidades.

### M18 — análise semântica

Pode exibir IA habilitada ou não, estratégia, provider/model efetivo, status da sessão, cadeia inicial, chamadas, tokens, custo estimado, duração e erro sanitizado.

### M20 — remediação textual

Pode exibir habilitação/status M20, tentativas por URL/device, provider/model, tokens, custo estimado, duração e erro sanitizado.

Falha, quota, timeout ou provider não configurado **não é finding GEO do website**. `ESTIMATED_COST` é estimativa local, não invoice.

M23 não é consumo de SemanticProvider e não entra como token/custo IA.

## Referências e metodologia

`references.html` explica fontes primárias oficiais, natureza `OFFICIAL`, `STANDARD`, `HEURISTIC` ou baseline interna das BR-GEO, fórmula do Score, Coverage, Confidence, Overall, fontes W3C/WAI, fontes Chrome/web.dev e a especificação Apdex usada pelo M23.

As referências Apdex validam a fórmula e a semântica S/T/F; não homologam `SCORE-GEO-002` nem transformam Synthetic Apdex em métrica GEO.

## Cores

Cores indicam mensagem, não decoração:

- verde: estado positivo/evidência suficiente;
- âmbar: atenção, parcialidade ou confiança reduzida;
- vermelho: problema/ação de alta gravidade;
- azul: informação contextual;
- cinza: indisponível/não determinado.

Cor nunca substitui o texto do estado.

## CSS e navegação

Todos os HTMLs finais referenciam `css/site.css`. O menu canônico é compartilhado. Quando `accessibility.html` existe, `Acessibilidade` aparece como item próprio antes de `Web Performance`. Quando `apdex.html` existe, `Apdex` aparece como domínio separado.

## Fonte de verdade

O HTML é projeção. A fonte de verdade permanece:

```text
audit.db
artifacts/
```

O report site não recalcula score, finding ou recommendation. M20/M21/M23, quando habilitados, persistem seus próprios dados antes das projeções finais; M22 reutiliza artifacts M21 e não chama provider externo.
