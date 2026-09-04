# Acessibilidade e Web Performance — domínios separados

## Objetivo

O SearchGEO mantém três contextos analíticos independentes:

| Domínio | Finalidade | Fonte principal | Altera SCORE-GEO-002? |
| --- | --- | --- | --- |
| GEO | readiness técnico/semântico para descoberta, extração, entendimento e citação | BR-GEO, evidências locais e providers explicitamente configurados | **Sim**, somente pelas regras e pelo contrato de scoring GEO |
| Acessibilidade | identificar problemas automatizáveis de acessibilidade e apontar elementos afetados quando a fonte fornece evidência | Lighthouse Accessibility + referências W3C/WCAG/WAI-ARIA | **Não** |
| Web Performance | medir laboratório/campo e diagnosticar recursos/caminho crítico que interferem no carregamento e experiência | Lighthouse/PageSpeed + CrUX + documentação Chrome/web.dev | **Não** |

Compartilhar uma coleta não significa compartilhar semântica. M21 pode solicitar várias categorias Lighthouse na mesma chamada PageSpeed para evitar chamadas externas duplicadas, mas M22 projeta os resultados em páginas, linguagem e conclusões separadas.

## Ativação

Acessibilidade automatizada e os diagnósticos detalhados de performance reutilizam o artifact PageSpeed/Lighthouse do M21. Portanto, a coleta externa continua controlada por:

```text
--web-performance
--no-web-performance
```

Quando Web Performance está desabilitado:

- nenhuma nova chamada PageSpeed/CrUX é feita;
- `report/accessibility.html` declara que não existe artifact Lighthouse suficiente;
- `report/web-performance.html` mantém o estado da coleta;
- nenhuma ausência de dados é tratada como falha do website;
- SCORE-GEO-002 continua independente.

M22 não chama OpenAI, DeepSeek, MiMo ou qualquer outro LLM.

---

# 1. Domínio de Acessibilidade

## Saída

```text
report/accessibility.html
```

A página contém, quando o Lighthouse fornece os dados:

- URL;
- Mobile/Desktop;
- Lighthouse Accessibility score;
- audit Lighthouse reprovado;
- selector observado;
- trecho HTML observado (`snippet`);
- explicação da ocorrência;
- sugestão de correção;
- referência oficial W3C/WAI quando existe mapeamento específico;
- quantidade de checks manuais declarados pelo Lighthouse.

## Regra de evidência

O SearchGEO **não inventa selector ou HTML**.

Se o artifact Lighthouse não contiver selector/snippet para uma ocorrência, o report informa explicitamente que a fonte não forneceu o dado.

O identificador apresentado no report tem formato:

```text
A11Y-LH-<lighthouse-audit-id>
```

Esse identificador significa **audit Lighthouse projetado pelo SearchGEO**. Ele não é um Success Criterion WCAG nem uma certificação externa.

## `aria-label` não é correção universal

Um botão ou outro componente deve possuir nome acessível programaticamente determinável quando aplicável. Isso não significa adicionar `aria-label` indiscriminadamente.

Dependendo da semântica do elemento, o nome pode vir de:

- texto nativo do controle;
- `<label>` associado;
- `aria-labelledby`;
- `aria-label` quando um rótulo visível adequado não pode ser usado;
- outra relação prevista pela plataforma/acessibility API.

A correção deve priorizar HTML nativo e preservar a semântica apropriada.

## Limitação obrigatória

Lighthouse é uma ferramenta automatizada. Sua pontuação de acessibilidade não cobre todos os aspectos que exigem avaliação humana. Portanto:

```text
Lighthouse 100/100 ≠ conformidade WCAG comprovada
```

O SearchGEO apresenta:

```text
Conformidade WCAG: NÃO DETERMINADA
```

até que exista processo de conformidade específico com checks manuais suficientes.

## Referências oficiais

- WCAG 2.2 — W3C Recommendation: <https://www.w3.org/TR/WCAG22/>
- Understanding SC 4.1.2 — Name, Role, Value: <https://www.w3.org/WAI/WCAG22/Understanding/name-role-value>
- WAI-ARIA 1.2: <https://www.w3.org/TR/wai-aria-1.2/>
- Technique ARIA14: <https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA14.html>
- Technique ARIA16: <https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA16.html>
- Lighthouse Accessibility scoring: <https://developer.chrome.com/docs/lighthouse/accessibility/scoring>
- Lighthouse overview: <https://developer.chrome.com/docs/lighthouse/overview>

---

# 2. Domínio de Web Performance

## Saída

```text
report/web-performance.html
```

A página continua sendo o único contexto de performance e contém:

### Campo — CrUX/Core Web Vitals

- LCP p75;
- INP p75;
- CLS p75;
- escopo URL/origin;
- fonte de field data;
- estado PASS/FAIL/INCOMPLETE/UNAVAILABLE.

### Laboratório — Lighthouse

- Performance score;
- FCP;
- Speed Index;
- LCP;
- TBT;
- CLS.

### Diagnóstico técnico M22

M22 também projeta oportunidades/insights do artifact Lighthouse relacionados a:

- solicitações render-blocking;
- cadeias/dependências críticas;
- descoberta e subpartes de LCP;
- layout shift;
- JavaScript/main thread;
- CSS não utilizado/custos de CSS quando informado;
- imagens e entrega de imagens;
- fontes;
- recursos de terceiros;
- latência de documento/servidor;
- tamanho/complexidade DOM;
- cache;
- outros diagnósticos Lighthouse explicitamente identificados pela fonte.

Para cada ocorrência, o report preserva, quando disponível:

- URL do recurso;
- selector;
- snippet do elemento;
- label/descrição do nó;
- `wastedMs`;
- `wastedBytes`;
- tamanho transferido/observado;
- duração;
- descrição e `displayValue` do Lighthouse.

## Primeira dobra e renderização inicial

O M22 não tenta classificar arbitrariamente todos os elementos "above the fold".

A análise usa sinais que o navegador/Lighthouse consegue fundamentar, principalmente:

- recurso que bloqueou a renderização inicial;
- cadeia crítica;
- elemento/recurso associado a LCP quando informado;
- subpartes do LCP;
- layout shift culprits quando disponíveis.

Isso evita transformar apenas posição visual em causalidade de performance.

## Causalidade

O report distingue:

```text
observado pela fonte
→ recurso/elemento/tempo realmente devolvido pelo Lighthouse

recomendação
→ ação tecnicamente plausível sustentada pela classe do diagnóstico

causa não comprovada
→ não é afirmada como fato
```

Por exemplo, um recurso listado como render-blocking pode ser declarado como bloqueador da renderização inicial porque esse é o significado do insight do Chrome. O report não afirma que ele foi a única causa de um LCP ruim se o artifact não demonstrar essa relação.

## Referências oficiais

- Chrome Performance Insights: <https://developer.chrome.com/docs/performance/insights>
- Render-blocking requests: <https://developer.chrome.com/docs/performance/insights/render-blocking>
- Network dependency tree: <https://developer.chrome.com/docs/performance/insights/network-dependency-tree>
- Lighthouse Performance scoring: <https://developer.chrome.com/docs/lighthouse/performance/performance-scoring>
- Core Web Vitals: <https://web.dev/articles/vitals>
- PageSpeed Insights API v5: <https://developers.google.com/speed/docs/insights/v5/reference/pagespeedapi/runpagespeed>
- Chrome UX Report API: <https://developer.chrome.com/docs/crux/api/>

---

# 3. Apdex

O SearchGEO **não calcula Apdex a partir de Lighthouse, LCP, INP, CLS ou da duração da chamada PageSpeed**.

A especificação Apdex requer:

1. um conjunto de amostras de tempos de resposta de uma Task/Task Chain;
2. um threshold alvo `T` explicitamente definido;
3. a separação das amostras nas zonas Satisfied, Tolerating e Frustrated;
4. `F = 4T`;
5. cálculo sobre a população de amostras.

Fórmula definida pela especificação:

```text
Apdex(T) = (Satisfied + Tolerating / 2) / Total Samples
```

Referência:

- Apdex Technical Specification v1.1: <https://www.apdex.org/wp-content/uploads/2020/09/ApdexTechnicalSpecificationV11_000.pdf>

### Estado atual

```text
Apdex: NÃO CALCULADO
```

Motivo: M21 mede Lighthouse/CrUX, mas não possui uma população de tempos de resposta transacionais com `T` aprovado.

Uma implementação futura de Apdex só deve ser ativada após definir:

- qual jornada/Task será medida;
- início e fim da Task;
- origem das amostras;
- volume mínimo de amostras;
- `T` acordado para aquela Task;
- tratamento de erros/aborts;
- segmentação por dispositivo/contexto.

Inventar um `T` ou reutilizar a latência da API PageSpeed produziria um número formalmente calculável, mas semanticamente incorreto.

---

# 4. Interdependências entre domínios

Interdependência é permitida apenas como **rastreabilidade**, não como mistura de score.

Exemplos:

| Evidência | Domínio primário | Relação possível | Regra |
| --- | --- | --- | --- |
| CSS/JS render-blocking | Performance | pode atrasar renderização de conteúdo que também é relevante ao crawler | mostrar cross-reference; não alterar BR-GEO automaticamente |
| elemento LCP | Performance | pode ser também conteúdo principal/semântico | manter IDs/evidências separados |
| botão sem accessible name | Acessibilidade | pode coexistir com HTML semanticamente pobre | não criar BR-GEO a partir do A11Y automaticamente |
| HTML/ARIA inválido | Acessibilidade | pode dificultar interpretação por tecnologia assistiva | não converter em penalidade GEO sem regra GEO específica |
| falha de rendering que oculta conteúdo essencial | GEO | pode ter causa de performance | evidenciar Performance quando houver prova; manter resultado GEO independente |

A mesma evidência física pode ser referenciada por dois domínios. A interpretação, regra, severidade, score e remediação continuam pertencendo ao domínio que fez a afirmação.
