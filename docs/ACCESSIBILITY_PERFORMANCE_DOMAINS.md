# Acessibilidade, Web Performance e Synthetic Apdex — domínios separados

## Objetivo

O SearchGEO mantém contextos analíticos independentes:

| Domínio | Finalidade | Fonte principal | Altera SCORE-GEO-002? |
| --- | --- | --- | --- |
| GEO | readiness técnico/semântico para descoberta, extração, entendimento e citação | BR-GEO, evidências locais e providers explicitamente configurados | **Sim**, somente pelas regras e contrato de scoring GEO |
| Acessibilidade M22 | identificar problemas automatizáveis e apontar elementos afetados quando a fonte fornece evidência | Lighthouse Accessibility + referências W3C/WCAG/WAI-ARIA | **Não** |
| Web Performance M21/M22 | medir laboratório/campo e diagnosticar recursos/caminho crítico | Lighthouse/PageSpeed + CrUX + documentação Chrome/web.dev | **Não** |
| Synthetic Navigation Apdex M23 | medir repetidamente uma Task explícita de navegação sob profile sintético controlado | Chromium/Playwright + Apdex Technical Specification + CDP | **Não** |

Compartilhar evidência não significa compartilhar semântica. M21 pode solicitar categorias Lighthouse na mesma chamada PageSpeed; M22 projeta Acessibilidade e Performance separadamente; M23 usa navegações próprias e só reutiliza artifact M21 para rastreabilidade de `configSettings` Lighthouse quando ele já existe.

## Ativação

M21/M22:

```text
--web-performance
--no-web-performance
```

M23:

```text
--synthetic-apdex
--no-synthetic-apdex
--apdex-threshold-seconds T
```

M21 e M23 são default OFF.

Quando M21 está OFF:

- nenhuma chamada PageSpeed/CrUX é feita;
- Acessibilidade/Performance ficam limitadas ao que já existe localmente;
- ausência de dados não é falha do website;
- `SCORE-GEO-002` continua independente.

Quando M23 está OFF:

- nenhuma navegação sintética adicional é executada;
- não existe população Synthetic Apdex;
- M21/M22 continuam sem inferir Apdex de Lighthouse/CrUX.

M22/M23 não chamam LLM.

---

# 1. Domínio de Acessibilidade

## Saída

```text
report/accessibility.html
```

A página pode conter URL/device, Lighthouse Accessibility score, audit reprovado, selector/snippet somente quando a fonte fornece, explicação, sugestão, referência W3C/WAI e quantidade de checks manuais declarados pelo Lighthouse.

## Regra de evidência

O SearchGEO **não inventa selector ou HTML**. Se o artifact Lighthouse não contiver selector/snippet, o report registra que a fonte não forneceu o dado.

O identificador `A11Y-LH-<lighthouse-audit-id>` representa audit Lighthouse projetado pelo SearchGEO; não é Success Criterion WCAG nem certificação externa.

## `aria-label` não é correção universal

Nome acessível pode vir de texto nativo, `<label>`, `aria-labelledby`, `aria-label` ou outro mecanismo previsto pela plataforma. A correção deve priorizar HTML nativo quando suficiente.

## Limitação obrigatória

```text
Lighthouse 100/100 ≠ conformidade WCAG comprovada
Conformidade WCAG: NÃO DETERMINADA
```

A automação não substitui avaliação manual suficiente.

## Referências oficiais

- WCAG 2.2: <https://www.w3.org/TR/WCAG22/>
- Name, Role, Value: <https://www.w3.org/WAI/WCAG22/Understanding/name-role-value>
- WAI-ARIA 1.2: <https://www.w3.org/TR/wai-aria-1.2/>
- Lighthouse Accessibility scoring: <https://developer.chrome.com/docs/lighthouse/accessibility/scoring>

---

# 2. Domínio de Web Performance M21/M22

## Saída

```text
report/web-performance.html
```

### Campo — CrUX/Core Web Vitals

- LCP p75;
- INP p75;
- CLS p75;
- escopo URL/origin;
- fonte de field data;
- PASS/FAIL/INCOMPLETE/UNAVAILABLE.

### Laboratório — Lighthouse

- Performance score;
- FCP;
- Speed Index;
- LCP;
- TBT;
- CLS.

### Diagnóstico técnico M22

Quando o artifact fornece evidência, M22 pode projetar render-blocking, cadeias críticas, LCP, layout shift, JavaScript/main thread, CSS, imagens, fontes, terceiros, documento/servidor, DOM e cache.

Por ocorrência, preserva somente dados presentes na fonte: URL, selector, snippet, label, `wastedMs`, `wastedBytes`, tamanho, duração, descrição e `displayValue`.

## Primeira dobra e causalidade

M22 não classifica arbitrariamente todo elemento “above the fold”. A causalidade depende de sinais sustentados pelo Lighthouse/Chrome.

É válido afirmar que um recurso foi classificado como render-blocking quando o artifact demonstra isso; não é válido atribuir causalidade exclusiva de LCP sem evidência específica.

## Referências oficiais

- Chrome Performance Insights: <https://developer.chrome.com/docs/performance/insights>
- Render-blocking requests: <https://developer.chrome.com/docs/performance/insights/render-blocking>
- Network dependency tree: <https://developer.chrome.com/docs/performance/insights/network-dependency-tree>
- Lighthouse Performance scoring: <https://developer.chrome.com/docs/lighthouse/performance/performance-scoring>
- Core Web Vitals: <https://web.dev/articles/vitals>
- PageSpeed Insights API v5: <https://developers.google.com/speed/docs/insights/v5/reference/pagespeedapi/runpagespeed>
- Chrome UX Report API: <https://developer.chrome.com/docs/crux/api/>

---

# 3. Synthetic Navigation Apdex M23

## Fronteira metodológica

M21/M22 **não calculam Apdex a partir de Lighthouse, LCP, INP, CLS, TBT ou duração da chamada PageSpeed**. Essa decisão permanece válida.

O M23 é a implementação separada que passou a fornecer os insumos que faltavam ao domínio M21/M22:

1. Task explícita;
2. início/fim definidos;
3. população de amostras de navegação;
4. threshold `T` explícito;
5. classificação Satisfied/Tolerating/Frustrated;
6. persistência de samples e summaries;
7. segmentação por URL/device.

## Saída

```text
report/apdex.html
```

## Task

```text
NAVIGATION_LOAD
início = imediatamente antes de page.goto
fim    = conclusão de wait_until=load
```

Cada amostra usa BrowserContext novo e cache desabilitado. Perfis CPU/rede são determinísticos e versionados.

## Fórmula

```text
Apdex = (Satisfied + 0.5 × Tolerating) / Total de amostras válidas

Satisfied  <= T
Tolerating > T e <= 4T
Frustrated > 4T
```

`F = 4T`.

Timeout/erro de navegação ou erro de aplicação/servidor é `FRUSTRATED` quando o profile foi aplicado. Falha de browser/ferramenta/profile é amostra inválida e fica fora do denominador.

## Tamanho de grupo

Default normal:

```text
100 amostras válidas por URL/device
```

Grupos com 1–99 recebem `*` e são diagnósticos de grupo pequeno. Por isso um smoke 5/5 pode ter M23 `PARTIAL` sem falha operacional.

## Custo e carga

M23 adiciona:

```text
0 chamadas LLM
0 tokens IA
0 chamadas PageSpeed/CrUX
```

Não há API paga própria no contrato atual. Porém existe CPU/RAM/tempo local e tráfego HTTP real contra o alvo; cada navegação pode carregar muitos subrecursos.

## Relação com Lighthouse

Quando M21 já preservou artifact PageSpeed, M23 pode extrair `lighthouseResult.configSettings` para comparação/rastreabilidade. Não presume igualdade entre profile Lighthouse e profile Apdex; campos ausentes não são inventados.

O tempo total Lighthouse não entra na fórmula Apdex.

## Referências

- Apdex Technical Specification v1.1: <https://www.apdex.org/wp-content/uploads/2020/09/ApdexTechnicalSpecificationV11_000.pdf>
- Chrome DevTools Protocol — Emulation: <https://chromedevtools.github.io/devtools-protocol/tot/Emulation/>
- Chrome DevTools Protocol — Network: <https://chromedevtools.github.io/devtools-protocol/tot/Network/>

Detalhes operacionais: [SYNTHETIC_APDEX.md](SYNTHETIC_APDEX.md).

---

# 4. Interdependências entre domínios

Interdependência é permitida apenas como **rastreabilidade**, não mistura de score.

| Evidência | Domínio primário | Relação possível | Regra |
| --- | --- | --- | --- |
| CSS/JS render-blocking | Performance | pode atrasar conteúdo relevante ao crawler | cross-reference; não alterar BR-GEO automaticamente |
| elemento LCP | Performance | pode ser conteúdo principal | manter IDs/evidências separados |
| botão sem accessible name | Acessibilidade | pode coexistir com HTML semanticamente pobre | não criar BR-GEO automaticamente |
| falha de rendering que oculta conteúdo essencial | GEO | pode ter causa de performance | evidenciar Performance quando houver prova; manter resultado GEO independente |
| navegação lenta sob profile M23 | Apdex | pode coexistir com Lighthouse/CWV ruins ou bons | comparar, não combinar scores |
| configSettings Lighthouse | Performance | pode ser comparado ao profile M23 | rastreabilidade; não assumir equivalência |

A mesma evidência física pode ser referenciada por mais de um domínio. Interpretação, regra, severidade, score e remediação continuam pertencendo ao domínio que fez a afirmação.
