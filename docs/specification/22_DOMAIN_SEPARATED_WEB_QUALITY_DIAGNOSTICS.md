# M22 — Diagnósticos de Qualidade Web com Fronteiras de Domínio

**Status:** EVOLUÇÃO APROVADA PARA IMPLEMENTAÇÃO  
**Identificador:** `M22`  
**Dependências:** M21 + REPORT-SITE-GEO-001  
**Natureza:** projeção aditiva de evidência; sem alteração de scoring GEO

## 1. Objetivo

M22 amplia a utilidade operacional dos relatórios sem misturar conceitos que possuem autoridades, métricas e critérios distintos.

Domínios obrigatoriamente separados:

```text
GEO
Acessibilidade
Web Performance
```

Interdependências podem ser exibidas por cross-reference de evidência, mas não autorizam:

- conversão automática de finding entre domínios;
- soma de scores;
- recalibração de `SCORE-GEO-002`;
- inferência causal não demonstrada;
- promoção de uma ferramenta automatizada a certificação normativa.

## 2. Princípio de coleta compartilhada, semântica separada

M21 pode obter em uma única chamada PageSpeed/Lighthouse categorias como:

```text
performance
accessibility
best-practices
seo
```

Essa otimização evita chamadas externas duplicadas.

M22 não cria nova chamada de rede. Ele lê somente:

```text
web_performance_observations.pagespeed_artifact_reference
artifacts/web-performance/*.pagespeed.json
```

e projeta os dados por domínio.

Compartilhar payload é permitido. Compartilhar score/conclusão não é.

## 3. Domínio GEO

M22 não altera:

- `BR-GEO-*`;
- RuleExecution;
- Finding GEO;
- Recommendation GEO;
- severity GEO;
- priority GEO;
- `SCORE-GEO-002`;
- Coverage;
- Confidence;
- Consolidation.

Nenhum audit Lighthouse de acessibilidade ou performance vira BR-GEO automaticamente.

## 4. Domínio Acessibilidade

### 4.1 Página própria

M22 materializa:

```text
report/accessibility.html
```

A página entra no menu canônico compartilhado do report site.

### 4.2 Fonte

Fonte automatizada:

```text
Lighthouse Accessibility
```

Autoridades de referência:

- W3C WCAG 2.2;
- WAI-ARIA 1.2;
- documentação oficial Lighthouse/Chrome.

### 4.3 Evidência por ocorrência

Quando presente no artifact Lighthouse, preservar:

- audit id;
- título/descrição;
- selector;
- snippet/HTML;
- node label;
- explanation/failure summary;
- score do audit;
- URL/device da execução.

O relatório não pode inventar selector ou snippet ausente.

### 4.4 Identificador de projeção

Formato visual:

```text
A11Y-LH-<lighthouse-audit-id>
```

Esse identificador não representa Success Criterion WCAG.

### 4.5 Semântica de conformidade

Lighthouse Accessibility é ferramenta automatizada e contém checks manuais fora do score automatizado.

Portanto, M22 deve mostrar:

```text
Conformidade WCAG: NÃO DETERMINADA
```

Um score Lighthouse de 100/100 não autoriza afirmar conformidade WCAG.

### 4.6 Correções ARIA

M22 não deve prescrever `aria-label` como solução universal.

Para accessible name, considerar conforme o caso:

- HTML nativo/texto do controle;
- `<label>`;
- `aria-labelledby`;
- `aria-label`;
- demais mecanismos previstos pelas especificações aplicáveis.

A recomendação deve preferir semântica HTML nativa quando suficiente.

## 5. Domínio Web Performance

### 5.1 Página própria

Permanece:

```text
report/web-performance.html
```

M22 adiciona diagnóstico técnico à página M21 existente, sem criar um score próprio do SearchGEO.

### 5.2 Campo e laboratório

Persistem separados:

```text
CrUX/Core Web Vitals
→ field data, experiência agregada real, p75

Lighthouse
→ lab data, execução controlada
```

### 5.3 Métricas principais

Campo:

- LCP p75;
- INP p75;
- CLS p75.

Laboratório:

- Performance score;
- FCP;
- Speed Index;
- LCP;
- TBT;
- CLS.

O Accessibility score não deve ser apresentado como métrica de Performance; ele é projetado na página Acessibilidade.

### 5.4 Diagnósticos técnicos

M22 pode projetar audits/insights Lighthouse quando o ID e os detalhes indicarem classes como:

- render blocking;
- critical request/network dependency;
- LCP;
- layout shift;
- JavaScript/main thread;
- CSS;
- imagens;
- fontes;
- terceiros;
- server/document latency;
- DOM;
- cache.

### 5.5 Detalhe por ocorrência

Preservar somente quando fornecido pela fonte:

- resource URL;
- selector;
- snippet;
- node label;
- explanation;
- `wastedMs`;
- `wastedBytes`;
- `totalBytes`/equivalente;
- duração;
- `displayValue`.

### 5.6 Primeira renderização

M22 não define arbitrariamente todos os elementos da primeira dobra como causa de performance.

Evidências autorizadas incluem:

- render-blocking requests;
- critical path/network dependency;
- LCP element/resource;
- LCP breakdown/discovery;
- layout shift culprits;
- outros insights explícitos do Lighthouse.

## 6. Causalidade

A linguagem do report deve separar:

```text
observação comprovada
recomendação técnica
causa não comprovada
```

Exemplo:

```text
O Lighthouse identificou app.css como render-blocking.
```

é permitido quando a fonte assim o classifica.

```text
app.css é a única causa do LCP ruim.
```

não é permitido sem evidência adicional que demonstre essa relação.

## 7. Apdex

M22 não calcula Apdex a partir de:

- LCP;
- INP;
- CLS;
- TBT;
- duração da chamada PageSpeed;
- uma única execução Lighthouse.

A especificação Apdex exige:

- uma população de amostras de tempo de resposta de Task/Task Chain;
- threshold `T` explícito;
- `F = 4T`;
- contagem Satisfied/Tolerating/Frustrated.

Fórmula:

```text
Apdex(T) = (Satisfied + Tolerating / 2) / Total Samples
```

Enquanto esses insumos não existirem:

```text
Apdex: NÃO CALCULADO
```

Uma evolução futura precisa especificar separadamente a fonte das amostras, definição da Task, threshold `T`, volume mínimo e segmentação.

## 8. Navegação

Ordem canônica relevante:

```text
Conteúdo e JSON-LD
Acessibilidade
Web Performance
Uso de IA
```

Acessibilidade é item opcional baseado na existência de `accessibility.html`, seguindo o mesmo contrato de navegação das demais páginas.

## 9. Referências públicas e oficiais

### Acessibilidade

- <https://www.w3.org/TR/WCAG22/>
- <https://www.w3.org/WAI/WCAG22/Understanding/name-role-value>
- <https://www.w3.org/TR/wai-aria-1.2/>
- <https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA14.html>
- <https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA16.html>
- <https://developer.chrome.com/docs/lighthouse/accessibility/scoring>
- <https://developer.chrome.com/docs/lighthouse/overview>

### Performance

- <https://developer.chrome.com/docs/performance/insights>
- <https://developer.chrome.com/docs/performance/insights/render-blocking>
- <https://developer.chrome.com/docs/performance/insights/network-dependency-tree>
- <https://developer.chrome.com/docs/lighthouse/performance/performance-scoring>
- <https://web.dev/articles/vitals>
- <https://developers.google.com/speed/docs/insights/v5/reference/pagespeedapi/runpagespeed>
- <https://developer.chrome.com/docs/crux/api/>

### Apdex

- <https://www.apdex.org/wp-content/uploads/2020/09/ApdexTechnicalSpecificationV11_000.pdf>

## 10. Critérios de conclusão

1. `accessibility.html` é materializado sem nova chamada externa;
2. menu canônico mostra Acessibilidade em todas as páginas quando o arquivo existe;
3. Accessibility score não é mais apresentado dentro do scorecard de Performance;
4. falha `button-name` preserva selector/snippet Lighthouse quando existentes;
5. ausência de selector não produz selector inventado;
6. checks manuais permanecem explicitamente fora da conclusão automatizada;
7. report não afirma conformidade WCAG;
8. diagnósticos de render blocking/recurso preservam URL e savings quando fornecidos;
9. diagnósticos A11Y não vazam para a coleção de Performance;
10. Apdex permanece `NÃO CALCULADO` sem amostras + T;
11. nenhuma alteração em `SCORE-GEO-002`;
12. M22 não cria chamada LLM ou Google adicional;
13. referências oficiais ficam acessíveis no report e na documentação;
14. suíte determinística permanece verde.
