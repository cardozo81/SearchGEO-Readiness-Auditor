# M21 — Evidência Externa de Web Performance: Core Web Vitals + Lighthouse

**Status:** EVOLUÇÃO APROVADA  
**Identificador:** `M21`  
**Dependências:** M18 + M20 + `SCORE-GEO-002` + `REPORT-SITE-GEO-001`  
**Natureza:** evidência externa aditiva; sem impacto no scoring por padrão

## 1. Objetivo

O M21 adiciona à auditoria SearchGEO evidências de Web Performance fundamentadas em documentação externa oficial, sem remover, substituir ou recalibrar silenciosamente o `SCORE-GEO-002`.

Quando explicitamente habilitado, o recurso coleta:

- scores de laboratório do Lighthouse por meio da PageSpeed Insights API v5;
- métricas de laboratório do Lighthouse, como FCP, Speed Index, LCP, Total Blocking Time e CLS;
- dados de campo de Core Web Vitals provenientes do CrUX, quando disponíveis;
- LCP, INP e CLS no percentil 75 (`p75`) e sua avaliação segundo os thresholds oficiais de boa experiência;
- telemetria operacional de cada requisição de medição externa;
- artefatos JSON brutos, limitados e reabríveis, armazenados no workspace da auditoria.

O M21 responde a uma pergunta diferente daquela respondida pelo `SCORE-GEO-002`:

```text
SCORE-GEO-002
→ índice heurístico interno de prontidão baseado nas RuleExecutions do SearchGEO

M21 Lighthouse
→ medição e score de laboratório definidos externamente

M21 CrUX / Core Web Vitals
→ experiência agregada de usuários reais em campo quando existe amostra CrUX suficiente
```

Essas saídas devem permanecer claramente distinguíveis na persistência, no HTML e na documentação.

## 2. Contrato não destrutivo de scoring

O M21 **não altera**:

- Business Rules;
- resultados de RuleExecution;
- findings;
- recomendações;
- prioridade;
- pesos das regras;
- `PASS = 1.00`, `WARNING = 0.50`, `FAIL = 0.00`;
- scores das dimensões;
- Coverage;
- Confidence;
- Consolidation;
- Overall Readiness;
- `scoring_version = SCORE-GEO-002`.

Nenhum valor de Lighthouse, PageSpeed ou Core Web Vitals é convertido automaticamente em contribuição para o `SCORE-GEO-002`.

Portanto, o `SCORE-GEO-002` permanece disponível como índice heurístico estável de prontidão mesmo quando o M21 está habilitado. Quando o M21 está desabilitado ou indisponível, o comportamento existente da auditoria continua funcional.

## 3. Fundamentação externa oficial

### 3.1 PageSpeed Insights API v5

Referências oficiais:

- <https://developers.google.com/speed/docs/insights/v5/reference/pagespeedapi/runpagespeed>
- <https://developers.google.com/speed/docs/insights/v5/get-started>

A API oficial executa Lighthouse sobre uma URL fornecida e suporta as categorias:

```text
performance
accessibility
best-practices
seo
```

O padrão atual do SearchGEO solicita as quatro categorias na mesma requisição PageSpeed para cada contexto.

A documentação do Google informa que o PageSpeed Insights pode ser usado com ou sem API key, embora recomende chave para consultas automatizadas frequentes.

### 3.2 Chrome UX Report API

Referências oficiais:

- <https://developer.chrome.com/docs/crux/api/>
- <https://developer.chrome.com/docs/crux/guides/crux-api>

A CrUX API direta utiliza:

```text
POST https://chromeuxreport.googleapis.com/v1/records:queryRecord
```

A chamada exige API key e suporta dados de campo por URL/origin e form factor.

O M21 solicita o conjunto atual de métricas Core Web Vitals:

```text
largest_contentful_paint
interaction_to_next_paint
cumulative_layout_shift
```

Mapeamento de dispositivo:

```text
SearchGEO MOBILE  → CrUX PHONE
SearchGEO DESKTOP → CrUX DESKTOP
```

O M21 não introduz Tablet como novo contexto de dispositivo do SearchGEO.

### 3.3 Avaliação de Core Web Vitals

A metodologia oficial utiliza o percentil 75 das distribuições observadas de usuários reais.

Thresholds atuais de boa experiência utilizados pelo M21:

```text
LCP <= 2500 ms
INP <= 200 ms
CLS <= 0.10
```

O estado combinado do M21 é:

```text
PASS
```

somente quando LCP, INP e CLS estão todos disponíveis e cada um atende ao respectivo threshold de boa experiência.

Se uma ou mais métricas estiverem indisponíveis:

```text
INCOMPLETE
```

ou, quando não houver nenhuma métrica de campo utilizável:

```text
UNAVAILABLE
```

Ausência de dados CrUX nunca é convertida em falha do website. O CrUX pode legitimamente não possuir amostra suficiente para determinada URL/form factor.

### 3.4 Lighthouse Performance Score

Referência oficial:

- <https://developer.chrome.com/docs/lighthouse/performance/performance-scoring>

Lighthouse Performance é um score externo de 0 a 100 calculado pelo Lighthouse. As curvas de scoring das métricas e seus pesos são mantidos pelo projeto Chrome/Lighthouse e podem evoluir conforme a versão do Lighthouse.

O SearchGEO persiste a versão Lighthouse retornada e não duplica uma cópia privada e fixa dos pesos do Lighthouse dentro do `SCORE-GEO-002`.

Lighthouse Performance deve ser identificado como `Lighthouse Performance`, nunca como `GEO Score`.

## 4. Ativação e política de rede sem consumo inesperado

A coleta externa do M21 fica desabilitada por padrão.

Controles públicos:

```text
--web-performance
--no-web-performance
SEARCHGEO_WEB_PERFORMANCE
```

Precedência:

1. flag explícita de CLI;
2. variável de ambiente;
3. `false`.

Valores booleanos aceitos em variável de ambiente:

```text
true / false
1 / 0
yes / no
on / off
```

Quando desabilitado:

- nenhuma requisição PageSpeed é realizada;
- nenhuma requisição CrUX é realizada;
- nenhuma nova requisição a LLM é realizada;
- o M21 persiste `DISABLED` para rastreabilidade;
- o relatório informa que o recurso estava desabilitado;
- o `SCORE-GEO-002` permanece integralmente disponível.

## 5. Controles de consumo

### 5.1 Máximo de páginas

```text
--web-performance-max-pages N
SEARCHGEO_WEB_PERFORMANCE_MAX_PAGES
```

Padrão:

```text
10
```

Significado:

- `N > 0`: somente as primeiras N páginas auditadas, em ordem determinística de URL, são enviadas aos serviços externos de performance;
- `0`: todas as páginas auditadas são elegíveis.

O limite é aplicado a páginas lógicas. Com `--device-context both`, cada página selecionada pode gerar uma requisição PageSpeed para Mobile e uma para Desktop.

Portanto, um limite superior prático de requisições PageSpeed é:

```text
selected_pages × selected_device_contexts
```

O fallback CrUX direto pode adicionar uma requisição CrUX por contexto somente quando a política configurada exigir essa chamada.

### 5.2 Timeout

```text
--web-performance-timeout-seconds SECONDS
SEARCHGEO_WEB_PERFORMANCE_TIMEOUT_SECONDS
```

Padrão:

```text
60
```

O valor deve ser finito e maior que zero.

O M21 não realiza retry automático de uma medição que expirou por timeout. Isso evita uma segunda requisição externa implícita quando o estado real da primeira execução pode ser desconhecido.

### 5.3 Categorias Lighthouse

```text
--lighthouse-categories performance,accessibility,best-practices,seo
SEARCHGEO_LIGHTHOUSE_CATEGORIES
```

Valores suportados:

```text
performance
accessibility
best-practices
seo
```

O padrão solicita as quatro categorias.

As categorias afetam o trabalho de Lighthouse executado pelo serviço PageSpeed, mas não criam nenhuma chamada a LLM.

## 6. Controles de credenciais de API

### 6.1 PageSpeed

Variável de ambiente opcional:

```text
SEARCHGEO_PAGESPEED_API_KEY
```

A chave é enviada somente ao PageSpeed Insights.

Ela nunca é:

- persistida no SQLite;
- escrita nos artefatos de resposta bruta;
- exibida no HTML;
- registrada em log como parte da URL de requisição;
- reutilizada como credencial de provider de IA.

O PageSpeed pode operar sem chave em uso reduzido/ad hoc, sujeito às políticas e quotas do serviço externo.

### 6.2 CrUX

Variável de ambiente:

```text
SEARCHGEO_CRUX_API_KEY
```

O uso da CrUX API direta exige essa chave.

A credencial é isolada de:

```text
OPENAI_API_KEY
DEEPSEEK_API_KEY
MIMO_API_KEY
SEARCHGEO_PAGESPEED_API_KEY
```

Não é permitido fallback entre famílias de credenciais.

## 7. Política de fonte dos dados de campo

Controle:

```text
--web-performance-field-source auto|pagespeed|crux|none
SEARCHGEO_WEB_PERFORMANCE_FIELD_SOURCE
```

Padrão:

```text
auto
```

### `auto`

1. PageSpeed é chamado para obter Lighthouse;
2. se o PageSpeed ainda retornar dados de campo CrUX utilizáveis, o M21 usa esses dados;
3. se os dados de campo estiverem ausentes no PageSpeed e existir `SEARCHGEO_CRUX_API_KEY`, o M21 chama a CrUX API direta;
4. se nenhuma das fontes produzir dados de campo, Core Web Vitals permanece `UNAVAILABLE`/`INCOMPLETE`, sem penalidade ao website.

Essa política foi projetada para facilitar migração porque o Google anunciou a intenção de deixar de retornar dados CrUX de campo via PageSpeed Insights e recomenda as APIs diretas do CrUX para dados de campo.

### `pagespeed`

Usa somente os dados de campo presentes na resposta PageSpeed. Nunca adiciona uma chamada direta ao CrUX.

### `crux`

Usa dados de campo pela CrUX API direta. Exige `SEARCHGEO_CRUX_API_KEY`. O PageSpeed continua sendo utilizado para os dados de laboratório do Lighthouse.

### `none`

Desabilita o processamento de dados de campo, mantendo a coleta de laboratório do Lighthouse.

## 8. Política de IA

O M21 adiciona **zero** chamadas a LLM.

Ele não chama:

- OpenAI;
- DeepSeek;
- MiMo;
- qualquer SemanticProvider do M18;
- o provider de remediação de conteúdo do M20.

Os controles existentes de IA permanecem inalterados.

Portanto, habilitar Web Performance não pode, por si só, gerar cobrança inesperada de LLM.

Se uma versão futura adicionar interpretação por IA das métricas externas, essa capacidade deverá ser:

- habilitada por opt-in independente;
- contabilizada separadamente;
- refletida em `ai-usage.html` por finalidade;
- incapaz de alterar as medições-fonte;
- incapaz de alterar `SCORE-GEO-002`, salvo se um contrato de scoring posterior e explicitamente aprovado determinar o contrário.

## 9. Posicionamento da execução e isolamento de falhas

A integração atual de CLI executa o M21 depois que o pipeline existente da auditoria foi concluído e depois que o report site baseline já foi materializado.

Motivos:

- preservar o comportamento existente da auditoria;
- impedir que disponibilidade de PageSpeed/CrUX bloqueie RuleExecution/scoring;
- tratar a evidência externa de performance como camada de enriquecimento;
- manter falhas atribuíveis ao serviço de medição, em vez de atribuí-las incorretamente ao website auditado.

Estados operacionais incluem:

```text
DISABLED
NO_CONTEXTS
SUCCESS
PARTIAL
UNAVAILABLE
```

Um erro de PageSpeed/CrUX é persistido na telemetria M21 e não cria SearchGEO Finding ou Recommendation.

## 10. Persistência

O M21 adiciona tabelas SQLite de forma aditiva:

```text
web_performance_runs
web_performance_observations
web_performance_attempts
```

### `web_performance_runs`

Armazena a configuração e o resumo do resultado M21 no nível da auditoria:

- enabled;
- status;
- política de field source;
- limite de páginas;
- páginas consideradas;
- tentativas por contexto;
- contextos concluídos com sucesso;
- sucessos PageSpeed;
- sucessos CrUX;
- categorias Lighthouse;
- detalhe de reason/status;
- timestamp.

### `web_performance_observations`

Armazena uma observação para cada snapshot/dispositivo de página auditada selecionado pelo M21, incluindo:

- URL;
- device/strategy;
- versão Lighthouse/fetch time;
- score de Performance/Accessibility/Best Practices/SEO quando retornado;
- métricas lab FCP, Speed Index, LCP, TBT e CLS quando retornadas;
- field source/scope;
- LCP p75;
- INP p75;
- CLS p75;
- avaliações de cada componente;
- avaliação combinada de CWV;
- status HTTP do serviço;
- referências a artefatos;
- resumo sanitizado de erro.

### `web_performance_attempts`

Armazena telemetria operacional por requisição a serviço:

- serviço (`PAGESPEED_INSIGHTS` ou `CRUX_API`);
- URL/device/snapshot;
- estado success/error;
- status HTTP;
- duração;
- código/mensagem de erro sanitizados;
- referência ao artefato de resposta;
- timestamp.

Credenciais nunca são persistidas.

## 11. Artefatos brutos

Respostas externas bem-sucedidas são gravadas em:

```text
artifacts/web-performance/
```

Exemplos:

```text
WPE-....pagespeed.json
WPE-....crux.json
```

Esses artefatos preservam o payload da fonte externa utilizado para construir a projeção e tornam o resultado auditável depois que a requisição de rede terminou.

O relatório não exige nova chamada à API para reabrir uma auditoria já existente.

## 12. Contrato do relatório

O M21 amplia o report site estático com:

```text
report/web-performance.html
```

A navegação compartilhada é atualizada para que a página possa ser acessada a partir das demais páginas do relatório.

### `index.html`

Recebe um resumo compacto de Web Performance contendo:

- estado habilitado/desabilitado;
- status da execução M21;
- quantidade de contextos válidos Core Web Vitals PASS/FAIL;
- média de Lighthouse Performance somente entre contextos que realmente retornaram o score externo;
- link para os detalhes.

O número médio de Lighthouse deve ser identificado como evidência Lighthouse. Ele não é o Overall do SearchGEO.

### `web-performance.html`

Deve distinguir visualmente:

1. resultados de laboratório do Lighthouse;
2. resultados de campo CrUX/Core Web Vitals;
3. field source e escopo URL/origin;
4. dados indisponíveis/incompletos;
5. telemetria operacional dos serviços externos;
6. política de consumo/credenciais;
7. linguagem explícita informando que as métricas não alteram o scoring.

### `references.html`

Recebe referências oficiais para:

- PageSpeed Insights API;
- PageSpeed Get Started;
- CrUX API;
- guia do CrUX;
- Lighthouse Performance scoring;
- Core Web Vitals.

A seção deve informar explicitamente que essas fontes validam os fenômenos específicos que documentam e **não homologam o `SCORE-GEO-002` como score GEO universal**.

## 13. Regras de interpretação

Permitido:

```text
Lighthouse Performance: 91/100
Core Web Vitals: PASS
LCP p75: 2.4 s
Fonte: CrUX
SearchGEO Readiness: 78/100 (SCORE-GEO-002; heurística interna)
```

Não permitido:

```text
GEO score = Lighthouse 91
Core Web Vitals PASS = citação por IA garantida
SearchGEO 78 + Lighthouse 91 = GEO oficial 84.5
CrUX ausente = website FAIL
```

O M21 não cria nenhuma combinação aritmética entre essas métricas.

## 14. Ressalva PageSpeed versus CrUX

Atualmente, o PageSpeed Insights pode retornar simultaneamente:

- dados de laboratório do Lighthouse;
- dados de campo do CrUX.

O Google documentou publicamente o plano de descontinuar a parcela de dados de campo no PageSpeed Insights e recomenda CrUX API/CrUX History API para dados de experiência real.

Por esse motivo, o M21 registra a fonte dos dados de campo e suporta fallback direto para CrUX, em vez de tratar os dados CrUX retornados pelo PageSpeed como comportamento permanente da API.

## 15. Segurança e privacidade

O M21 não deve persistir:

- API keys;
- headers Authorization;
- URLs de requisição contendo API keys;
- cookies do site auditado;
- secrets do ambiente local.

Somente URL-alvo, resposta externa de medição, telemetria sanitizada e métricas derivadas são persistidas.

## 16. Compatibilidade retroativa

Com a configuração padrão:

```text
SEARCHGEO_WEB_PERFORMANCE=false
```

não existem novas chamadas de rede PageSpeed/CrUX.

Os comandos existentes permanecem válidos.

O comportamento existente dos providers de IA permanece válido.

`SCORE-GEO-002` permanece como baseline de scoring.

O novo HTML do M21 é aditivo ao report site e não remove páginas existentes.

## 17. Testes mínimos de aceitação

O M21 somente é considerado aceitável quando a cobertura de regressão comprova:

1. default OFF produz zero requisições PageSpeed/CrUX;
2. execução desabilitada é persistida;
3. resposta PageSpeed produz scores/métricas Lighthouse;
4. dados de campo CrUX recebidos via PageSpeed produzem LCP/INP/CLS p75;
5. normalização do percentil CLS da PSI é tratada;
6. CrUX direto é usado por `auto` somente quando dados de campo PageSpeed estão ausentes e existe chave/client CrUX disponível;
7. mapeamento Mobile→PHONE e Desktop→DESKTOP é determinístico;
8. ausência de uma métrica CWV produz `INCOMPLETE`, não `FAIL`;
9. indisponibilidade de dados de campo não altera RuleExecution/Finding/Score;
10. artefatos de resposta bruta são persistidos depois de chamadas bem-sucedidas;
11. credenciais não aparecem na persistência nem no relatório;
12. `web-performance.html` explica explicitamente a semântica sem impacto no scoring;
13. `index.html` contém link para a nova página de evidências;
14. `references.html` lista as fontes oficiais primárias;
15. código/conteúdo existente de `SCORE-GEO-002` não é removido nem recalculado.

## 18. Scoring calibrado futuro

O M21 é deliberadamente um pré-requisito para calibração empírica; ele próprio não é o `SCORE-GEO-003`.

Uma versão futura de scoring poderá estudar correlações entre features de readiness do SearchGEO, evidências externas de performance e outcomes generativos observados. Qualquer versão desse tipo exige protocolo empírico aprovado separadamente e, quando viável, deve preservar o resultado histórico do `SCORE-GEO-002` para comparação.

O M21 isoladamente não justifica alteração de pesos nem alegação de probabilidade de citação.
