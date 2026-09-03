# SCORING_VALIDATION.md

## Objetivo

Este documento registra a natureza da validação do `SCORE-GEO-002`, separa métricas internas de métricas externas e define caminhos possíveis para uma futura calibração empírica do SearchGEO.

## 1. Conclusão normativa

Não existe, na data desta baseline, um **score universal de GEO/AEO Readiness 0–100 externamente homologado e calibrado de ponta a ponta** por Google, OpenAI, Microsoft, NIST, W3C ou outro mantenedor equivalente.

Consequentemente, o `SCORE-GEO-002` não deve alegar equivalência a um padrão externo inexistente.

É possível, porém, aumentar substancialmente o respaldo quantitativo do produto utilizando **métricas externas oficiais ou padronizadas para fenômenos específicos** e mantendo explícito o limite de aplicabilidade de cada uma.

## 2. Hierarquia de evidência

O SearchGEO deve classificar a origem de cada sinal quantitativo em uma das categorias abaixo.

### A. Requisito oficial do mecanismo

Regra diretamente documentada por quem opera a superfície avaliada.

Exemplos:

- requisitos técnicos e de indexação do Google Search;
- elegibilidade para snippets e recursos de IA do Google;
- controles de crawler documentados por mecanismos/provedores;
- dados observados fornecidos pelo próprio Bing Webmaster Tools.

Esse nível possui forte respaldo para responder **elegibilidade/comportamento documentado**, mas normalmente não fornece um score GEO 0–100.

### B. Métrica externa calibrada ou padronizada

Métrica cuja fórmula, thresholds ou curva de scoring possuem metodologia pública e dados externos de referência.

Exemplos:

- Core Web Vitals;
- Lighthouse Performance Score;
- nDCG, MRR, Precision, Recall e métricas relacionadas usadas por NIST/TREC;
- métricas de suporte/citação empregadas em avaliações de RAG do TREC.

Essas métricas são adequadas ao fenômeno para o qual foram construídas. Elas **não devem ser promovidas automaticamente a score GEO global**.

### C. Métrica acadêmica experimental

Métrica publicada em benchmark ou estudo científico, porém sem status de padrão operacional do mercado.

Exemplo:

- métricas de visibilidade do GEO-Bench.

Podem informar desenho experimental e validação, mas exigem cautela de generalização.

### D. Heurística SearchGEO

Peso, threshold, fator ou agregação definidos internamente.

Exemplos atuais:

- `PASS = 1.00`;
- `WARNING = 0.50`;
- `FAIL = 0.00`;
- pesos iguais entre dimensões;
- Coverage 80%/90%;
- classificação visual 90/75/60/40;
- média simples das dimensões no Overall.

Esses valores devem permanecer claramente identificados como internos até calibração empírica.

## 3. Métricas externas que podem ser utilizadas

### 3.1 Google Search / AI features — elegibilidade técnica

A documentação oficial do Google estabelece que, para aparecer como link de suporte em AI Overviews ou AI Mode, a página precisa estar indexada e elegível para aparecer no Google Search com snippet. O Google também declara que não existem requisitos técnicos adicionais específicos para essas superfícies de IA.

Uso recomendado no SearchGEO:

- tratar requisitos técnicos documentados como **gates de elegibilidade**, não como pesos arbitrários;
- separar `ELIGIBLE`, `NOT_ELIGIBLE` e `UNKNOWN/UNVERIFIED`;
- nunca afirmar que elegibilidade garante inclusão/citação.

Referência:

- https://developers.google.com/search/docs/appearance/ai-features

### 3.2 Core Web Vitals — experiência de página

Os Core Web Vitals possuem thresholds documentados pelo Google e usam o percentil 75 das experiências observadas:

- LCP bom: `<= 2.5 s`;
- INP bom: `<= 200 ms`;
- CLS bom: `<= 0.1`.

Uso recomendado no SearchGEO:

- substituir thresholds próprios de performance, quando houver, pelos thresholds oficiais de CWV;
- manter Mobile e Desktop separados;
- preferir dados de campo quando disponíveis;
- não converter aprovação em CWV em “probabilidade GEO”.

Referências:

- https://web.dev/articles/vitals
- https://web.dev/articles/defining-core-web-vitals-thresholds

### 3.3 Lighthouse Performance Score — score externo calibrado de performance

O Lighthouse converte métricas de performance em score 0–100 por curvas log-normais derivadas de dados reais do HTTP Archive. A documentação explica os pontos de controle e os pesos utilizados no score.

Uso recomendado no SearchGEO:

- pode compor ou substituir uma submétrica estritamente ligada à performance técnica;
- deve ser rotulado como `Lighthouse Performance`, não como `GEO Score`;
- não deve determinar sozinho compatibilidade GEO.

Referência:

- https://developer.chrome.com/docs/lighthouse/performance/performance-scoring

### 3.4 Bing Webmaster Tools AI Performance — outcome observado

O Bing disponibiliza dados sobre participação real do conteúdo em respostas generativas, incluindo:

- Total Citations;
- Average Cited Pages;
- grounding queries;
- citation activity por URL;
- tendência temporal de citações.

Essas métricas são particularmente relevantes porque medem **resultado observado**, não apenas prontidão inferida.

Uso recomendado no SearchGEO quando a integração/dado estiver disponível:

- manter `Observed AI Visibility` separado do Readiness Score;
- usar citações reais como variável de validação/calibração futura;
- não interpretar contagem de citações como ranking, autoridade ou posição quando o próprio Bing não fornece essa semântica.

Referência:

- https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview

## 4. Métricas de Information Retrieval aplicáveis a testes GEO

NIST/TREC utiliza métricas consolidadas para avaliar recuperação e ranking. Elas podem ser adaptadas a experimentos de visibilidade/citação em engines generativas, desde que o protocolo de coleta seja controlado.

### 4.1 Citation/Presence Rate

Para um conjunto de query-runs:

```text
Citation Rate = query-runs em que o site foi citado / total de query-runs válidos
```

Essa métrica é um outcome diretamente observável. A fórmula é simples e não precisa de pesos heurísticos.

Deve ser acompanhada de tamanho amostral e intervalo de confiança.

### 4.2 Mean Reciprocal Rank — MRR

Quando a resposta/superfície fornece uma ordenação interpretável de fontes:

```text
RR(q) = 1 / rank_da_primeira_citação_relevante
MRR   = média de RR(q)
```

MRR é métrica tradicional de Information Retrieval e Question Answering utilizada pelo TREC.

Uso recomendado:

- medir quão cedo a fonte aparece quando existe ranking/posição observável;
- não usar quando a superfície não expõe uma ordenação semanticamente válida.

### 4.3 nDCG@k

Quando existem posições e níveis graduados de relevância/prominência:

```text
DCG@k = Σ ((2^rel_i - 1) / log2(i + 1))
nDCG@k = DCG@k / IDCG@k
```

nDCG é amplamente utilizado pelo NIST/TREC para ranking com relevância graduada.

Uso recomendado:

- comparar qualidade de posicionamento de fontes em experimentos controlados;
- requer definição explícita e auditável de `rel_i`;
- não inventar níveis de relevância sem protocolo de julgamento.

### 4.4 Precision / Recall

Podem avaliar recuperação de páginas/fontes esperadas em um conjunto com ground truth.

```text
Precision = relevantes recuperados / recuperados
Recall    = relevantes recuperados / relevantes existentes no ground truth
```

São úteis principalmente em benchmark controlado, não em auditoria isolada de um site sem ground truth.

### 4.5 Weighted Citation Precision / Recall

O TREC RAG 2025 utiliza avaliação de suporte das citações com pesos:

- Full Support = `1.0`;
- Partial Support = `0.5`;
- No Support = `0.0`.

Uso recomendado no SearchGEO:

- avaliar se uma engine cita uma página e se a citação realmente sustenta a afirmação produzida;
- manter essa métrica como avaliação de qualidade/fidelidade de citação, não como peso automático do `SCORE-GEO-002`.

Referências NIST/TREC:

- https://trec.nist.gov/data/qa.html
- https://trec.nist.gov/pubs/trec34/appendices/trec2025-rag-retrieval.html
- https://trec.nist.gov/pubs/trec34/papers/Overview_rag.pdf

## 5. GEO-Bench e literatura acadêmica

O trabalho `GEO: Generative Engine Optimization` introduziu o GEO-Bench e métricas experimentais de visibilidade para estudar como alterações de conteúdo afetam sua presença em respostas generativas.

Referência:

- https://arxiv.org/abs/2311.09735

O benchmark é evidência acadêmica relevante, mas não equivale a um padrão oficial de mercado nem demonstra, sozinho, descobribilidade orgânica longitudinal e cross-platform.

Uma revisão crítica de 2026 destaca heterogeneidade de terminologia, métricas e padrões de evidência, além de variabilidade entre engines e execuções.

Referência:

- https://arxiv.org/abs/2607.14035

## 6. Arquitetura recomendada de métricas

Em vez de substituir `SCORE-GEO-002` por outro número arbitrário, a evolução recomendada é separar três camadas:

### 6.1 Readiness inferido

Mantém o papel atual do SearchGEO:

- auditabilidade;
- regras evidence-backed;
- diagnósticos técnicos/semânticos;
- Coverage/Confidence/Consolidation.

Saída:

```text
SearchGEO Readiness Index
```

Natureza:

```text
interno / heurístico até calibração
```

### 6.2 External Technical Evidence

Usa métricas e gates externos quando aplicáveis:

```text
Google eligibility status
Core Web Vitals
Lighthouse Performance
outros requisitos oficiais por engine
```

Natureza:

```text
externamente documentado/calibrado para o fenômeno específico
```

### 6.3 Observed Generative Visibility

Mede outcomes reais:

```text
Citation Rate
Engine Coverage
MRR, quando posição for observável
nDCG, quando houver relevância graduada e ranking válido
citation support precision/recall
Bing AI Performance citations
```

Natureza:

```text
observacional/experimental
```

Essa separação evita que um único número misture prontidão inferida, experiência de página e performance real de citação.

## 7. Se um único score calibrado for exigido

Um novo score único somente terá respaldo empírico se for **calibrado contra um outcome definido**.

Exemplo de outcome binário:

```text
Y = 1 se a URL/site é citado em uma query-run elegível
Y = 0 caso contrário
```

Possível processo para `SCORE-GEO-003`:

1. coletar grande amostra de sites/páginas e queries;
2. executar múltiplas engines e múltiplas repetições por query;
3. extrair as features atuais do SearchGEO;
4. separar treino, calibração e teste por domínio/site para evitar leakage;
5. estimar relação entre features e outcome, por exemplo com regressão logística ou outro modelo interpretável;
6. calibrar probabilidades em conjunto separado quando necessário;
7. medir discriminação e calibração no conjunto de teste;
8. verificar estabilidade temporal e por engine;
9. publicar intervalos de confiança e limitações;
10. versionar o modelo conforme período e superfícies avaliadas.

Nesse cenário, a saída poderia ser denominada, por exemplo:

```text
Estimated Citation Probability
```

somente se a validação demonstrar calibração adequada. Ela não deve substituir o Readiness diagnóstico: probabilidade observada e causa técnica são problemas diferentes.

## 8. Recomendação para o produto atual

Para o `SCORE-GEO-002`:

- manter a fórmula atual para continuidade e reprodutibilidade;
- explicitar que pesos/fatores/thresholds são heurísticos;
- incorporar métricas externas somente nas dimensões em que exista correspondência conceitual válida;
- não transformar Core Web Vitals, Lighthouse ou métricas TREC em “prova” do Overall Readiness;
- planejar `SCORE-GEO-003` como projeto de calibração, não como simples troca manual de pesos;
- preferir no report a apresentação conjunta de `Readiness`, `Coverage/Confidence`, `External Evidence` e, quando disponível, `Observed Generative Visibility`.

## 9. Critério de linguagem

Permitido:

> O SearchGEO calcula um índice interno e reprodutível de prontidão, fundamentado em evidências técnicas e semânticas. Algumas submétricas podem utilizar padrões ou thresholds externos documentados.

Não permitido sem validação adicional:

> Score GEO oficial.

> 85 pontos = 85% de chance de citação.

> Certificado pelo Google/OpenAI/Microsoft.

> Score cientificamente validado.

> Threshold GEO universal.
