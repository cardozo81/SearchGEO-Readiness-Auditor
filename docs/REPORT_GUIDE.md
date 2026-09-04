# REPORT_GUIDE.md

Guia de leitura do report site do SearchGEO Readiness Auditor.

## Ponto de entrada

Abra:

```text
<audits-root>/<AUD-ID>/report/index.html
```

Não é necessário servidor web. Os arquivos usam links relativos e um CSS compartilhado.

## Estrutura

```text
report/
├─ index.html
├─ mobile.html             # quando Mobile foi auditado
├─ desktop.html            # quando Desktop foi auditado
├─ remediation.html
├─ content-suggestions.html
├─ accessibility.html
├─ web-performance.html
├─ ai-usage.html
├─ references.html
└─ css/
   └─ site.css
```

O menu é comum às páginas existentes naquela auditoria.

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
| `web-performance.html` | Lighthouse Performance, Core Web Vitals/CrUX e diagnósticos técnicos de performance |
| `ai-usage.html` | telemetria operacional M18/M20, separada por finalidade |
| `references.html` | fontes oficiais, natureza das regras e fórmulas/metodologias do auditor |

A mesma evidência física pode ser útil em mais de um domínio. Isso não autoriza misturar score, severidade ou conclusão. Uma relação entre GEO, Acessibilidade e Performance deve ser apresentada como cross-reference explícito, não como penalização implícita.

## `index.html`

É o dashboard executivo. Para GEO, deve ser lido nesta ordem:

1. dispositivo efetivamente auditado;
2. Readiness/Overall quando consolidado;
3. Coverage;
4. Confidence;
5. Consolidation;
6. dimensões;
7. findings/remediações quando existirem.

Resumos de Acessibilidade e Web Performance são rotulados como domínios independentes e não entram no Overall GEO.

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

Lighthouse Accessibility, Lighthouse Performance, Core Web Vitals e Apdex não são incorporados matematicamente ao SCORE-GEO-002.

## Coverage

Coverage responde:

> quanto do universo aplicável realmente foi avaliado?

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

Confidence responde:

> quão forte é a conclusão do auditor com as evidências disponíveis?

No SCORE-GEO-002 atual ela considera principalmente Coverage, completude de evidência e erros de execução.

**Confidence LOW não significa que o texto do website é ruim, não confiável ou não aderente a GEO.**

Ela significa que o auditor não possui base suficiente para sustentar uma conclusão forte. O conteúdo do site é avaliado por RuleExecutions, findings e Score; Confidence qualifica a conclusão.

Também não deve ser confundida com o campo de confidence devolvido por um provider de IA, score Lighthouse ou classificação de Core Web Vitals.

## Consolidation

Estados:

```text
CONSOLIDATED
PARTIAL
NOT_CONSOLIDATED
NOT_APPLICABLE
```

Uma dimensão `NOT_APPLICABLE` legítima não recebe 0 nem 100 e fica fora do Overall.

Uma dimensão aplicável `NOT_CONSOLIDATED` pode impedir publicação de um Overall.

## Mobile e Desktop

Quando `--device-context mobile`:

- existe `mobile.html`;
- `desktop.html` não é gerado;
- o report não apresenta Desktop como se tivesse sido auditado.

Quando `desktop`, vale o inverso.

Quando `both`, existem as duas páginas e a comparação entre contextos pode ser interpretada.

Diferença Mobile × Desktop não é automaticamente defeito. A regra BR-GEO-052 distingue diferença material de falha.

M20, M21 e M22 preservam os contextos existentes; não fabricam resultado para device não materializado.

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

Quando M16/M17 conseguiu materializar a causa, a ocorrência pode exibir:

- causa precisa;
- reason code;
- escopo;
- selector observado;
- HTML observado quando persistido;
- alvo técnico;
- localização esperada;
- diagnostic confidence;
- mudança recomendada;
- observado versus esperado;
- exemplo pós-correção;
- decisão humana;
- critérios de aceite;
- revalidação.

Uma condição `UNKNOWN`/evidência insuficiente não deve ser transformada artificialmente em ordem de alteração do site.

## Conteúdo e JSON-LD

`content-suggestions.html` é advisory e não participa do score.

### Sugestões textuais

Quando M20 textual está desabilitado, a página declara explicitamente o estado e não apresenta conteúdo como se tivesse sido gerado por IA.

Quando habilitado e houver findings elegíveis/evidência suficiente, cada proposta pode mostrar:

- URL/device;
- `rule_id`/finding;
- objetivo;
- local sugerido;
- texto exato proposto;
- evidence IDs;
- provider/model;
- confidence da sugestão;
- aviso de revisão humana obrigatória.

`Confidence LOW` do auditor, sozinha, nunca é gatilho da seção.

A proposta não é aplicada automaticamente e não altera Score, Coverage, Confidence ou Finding.

### JSON-LD

Quando o snapshot não possui JSON-LD persistido, a página pode exibir um baseline conservador `WebPage` usando somente valores observados. Quando markup já existe, o report não o substitui integralmente; pode apontar erros de parse, duplicação idêntica, ausência de `@context`, nós sem `@type` e propriedades genéricas ausentes quando o valor já é conhecido.

JSON-LD é reforço opcional. Não existe markup especial GEO/AEO obrigatório e markup correto não garante rich result.

## Acessibilidade

`accessibility.html` pertence a um domínio próprio.

A fonte automatizada é a categoria Accessibility do Lighthouse já coletada pelo M21 quando `--web-performance` está habilitado. M22 **não executa nova chamada PageSpeed/CrUX** para criar esta página.

Cada falha automatizada pode apresentar:

- URL e device;
- score Lighthouse Accessibility do contexto;
- audit ID Lighthouse;
- título/descrição da falha;
- selector observado, quando a fonte fornece;
- snippet HTML, quando a fonte fornece;
- node label/explanation, quando fornecidos;
- sugestão de tratamento;
- referência W3C/WAI específica quando mapeada.

### Regra de evidência

O SearchGEO não inventa selector ou HTML para uma ocorrência Lighthouse. Quando a fonte não fornece esses campos, o report diz explicitamente que não foram fornecidos.

### ARIA

`aria-label` não é uma correção universal. Para nome acessível, a solução pode envolver texto nativo, `<label>`, `aria-labelledby`, `aria-label` ou outro mecanismo previsto pela plataforma. O report deve preferir semântica HTML nativa quando suficiente.

### Limite da automação

Lighthouse é uma ferramenta automatizada e possui verificações que exigem revisão manual. Por isso:

```text
Conformidade WCAG: NÃO DETERMINADA
```

Mesmo um score Lighthouse 100/100 não deve ser comunicado como comprovação de conformidade WCAG.

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

A página mostra, quando disponíveis:

- Performance score;
- FCP;
- Speed Index;
- LCP;
- TBT;
- CLS.

O Accessibility score coletado no mesmo payload não é apresentado como métrica de Performance; ele é projetado em `accessibility.html`.

### Diagnósticos técnicos M22

A página pode detalhar, quando o artifact Lighthouse fornecer evidência:

- render-blocking requests;
- critical path/network dependency;
- LCP discovery/subparts/element/resource;
- layout shift;
- JavaScript/main thread;
- CSS;
- imagens;
- fontes;
- terceiros;
- latência do documento/servidor;
- DOM;
- cache.

Por ocorrência, preserva somente dados realmente presentes na fonte, como URL do recurso, selector, snippet, `wastedMs`, `wastedBytes`, tamanho e duração.

### Primeira dobra

O report não declara que todo elemento visualmente na primeira dobra causa baixa performance. A causalidade é baseada em diagnósticos do navegador/Lighthouse, como render blocking, caminho crítico, LCP e layout shift.

### Causalidade

É válido afirmar “o Lighthouse classificou este recurso como render-blocking” quando o artifact demonstra isso. Não é válido afirmar “este recurso é a única causa do LCP ruim” sem evidência específica.

## Apdex

Apdex fica:

```text
NÃO CALCULADO
```

M21/M22 não usam LCP, INP, CLS, TBT, duração da chamada PageSpeed ou uma única execução Lighthouse como substitutos de Apdex.

A especificação Apdex requer amostras de tempo de resposta de uma Task/Task Chain e threshold `T` explícito; a zona Frustrated inicia em `4T` e a fórmula considera Satisfied + metade de Tolerating sobre o total de amostras.

Uma evolução futura de Apdex precisa definir jornada/Task, começo/fim, fonte e quantidade das amostras, `T`, tratamento de erro e segmentação.

## Uso de IA

`ai-usage.html` é operacional e separa finalidades.

### M18 — análise semântica

Pode exibir:

- IA habilitada ou não;
- estratégia;
- provider/model efetivo;
- status da sessão;
- cadeia inicial;
- chamadas;
- tokens;
- custo estimado;
- duração;
- erro sanitizado.

### M20 — remediação textual

Pode exibir:

- se M20 estava habilitado;
- status M20;
- tentativas por URL/device;
- provider/model;
- tokens;
- custo estimado;
- duração;
- erro sanitizado.

Falha, quota, timeout ou provider não configurado **não é finding GEO do website**.

`ESTIMATED_COST` é estimativa local, não invoice.

## Referências e metodologia

`references.html` explica:

- fontes primárias oficiais;
- natureza `OFFICIAL`, `STANDARD`, `HEURISTIC` ou baseline interna das BR-GEO;
- fórmula do Score;
- Coverage;
- Confidence;
- Overall;
- limites das classificações internas;
- fontes W3C/WAI usadas pelo domínio Acessibilidade;
- fontes Chrome/web.dev usadas pelo domínio Performance;
- especificação Apdex usada apenas para justificar por que Apdex não é inferido sem `T` e amostras adequadas.

A página inclui o guia oficial do Google de 2026 sobre recursos generativos. O posicionamento adotado pelo SearchGEO é compatível com esse material: práticas fundamentais de SEO continuam relevantes, não há markup GEO/AEO especial obrigatório, nem necessidade de reescrever conteúdo apenas para IA.

Para JSON-LD, `content-suggestions.html` também aponta Google General Structured Data Guidelines e Schema.org. Validação de rich result deve usar documentação específica da feature/tipo.

## Cores

Cores indicam mensagem, não decoração:

- verde: estado positivo/evidência suficiente;
- âmbar: atenção, parcialidade ou confiança reduzida;
- vermelho: problema/ação de alta gravidade;
- azul: informação contextual;
- cinza: indisponível/não determinado.

Cor nunca substitui o texto do estado.

## CSS e navegação

Todos os HTMLs finais referenciam:

```text
css/site.css
```

O menu canônico é compartilhado. Quando `accessibility.html` existe, `Acessibilidade` aparece como item próprio antes de `Web Performance`.

## Fonte de verdade

O HTML é projeção. A fonte de verdade permanece:

```text
audit.db
artifacts/
```

O report site não recalcula score, finding ou recommendation. Chamadas M20/M21, quando habilitadas, terminam e persistem antes das projeções finais; M22 somente reutiliza artifacts M21 e não chama provider externo.
