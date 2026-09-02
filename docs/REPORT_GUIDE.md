# Guia do Relatório

O `report.html` é um relatório HTML5 estático, responsivo e imprimível, gerado exclusivamente a partir do estado persistido da auditoria. Ele é uma **projeção para leitura humana**; a fonte primária continua sendo `audit.db` + artifacts.

A partir de M14/`REPORT-GEO-003`, screenshots são assets locais referenciados por paths relativos. Portanto, o relatório não depende da internet, mas a unidade portátil passa a ser o **workspace completo do audit** (ou ZIP), e não necessariamente o arquivo HTML isolado.

## Como abrir

No Windows:

```powershell
Start-Process .\audits\AUD-...\report.html
```

Não é necessário web server, CDN, fonte remota ou acesso à internet.

# Como ler o resultado em poucos segundos

O relatório M14 apresenta com destaque:

1. projeto, `audit_id`, domínio, modo de entrada, URLs fornecidas/auditadas, data/hora, IA/modelo e limitações;
2. Compatibilidade GEO, Coverage, Confidence e Consolidation sem misturá-los;
3. estado explícito do score: calculado, inclusive zero real, ou não calculado;
4. inventário clicável das URLs auditadas;
5. recursos do domínio (`robots.txt` e sitemap(s));
6. legenda textual de resultado/actionability;
7. principais ações/revisões e melhorias não bloqueantes;
8. score Desktop e Mobile quando metodologicamente disponível;
9. páginas individualizadas, com URL em destaque, screenshots, findings e evidência DOM;
10. plano de correção, análise semântica, crawl/coverage, limitações, metodologia e glossário.

A ferramenta mede **Search/GEO Readiness**. O resultado não garante ranking, tráfego, citação por sistemas generativos, inclusão em respostas de IA ou visibilidade externa.

## Identificação de domínio e URL_SET

Em auditoria multi-URL, todas as páginas pertencem ao mesmo `audit_id`.

O cabeçalho informa:

- quantidade bruta de URLs fornecidas pelo operador;
- modo `URL_SET` quando a entrada foi explícita;
- quantidade efetivamente auditada.

O inventário representa o conjunto normalizado/deduplicado. Cada URL aponta para sua seção de página.

`robots.txt` e sitemap(s) aparecem como recursos de domínio, não duplicados artificialmente em cada página.

# Três conceitos que não devem ser confundidos

### Compatibilidade GEO

Responde: **quão preparado está o site?**

É o `OVERALL_READINESS` do dispositivo quando o score está efetivamente `CONSOLIDATED`.

### Cobertura da análise

Responde: **quanto do universo aplicável foi efetivamente avaliado?**

Coverage baixa reduz a capacidade de concluir, mas **não significa que o website tenha qualidade baixa**.

### Confiabilidade

Responde: **quanto podemos confiar na conclusão apresentada?**

Considera coverage, evidência, erros de execução e capacidade analítica disponível.

## Zero calculado versus NÃO DETERMINADO

Um score efetivamente calculado como zero é mostrado como:

```text
Score: 0.0
Estado: CALCULADO
```

Quando não há base suficiente:

```text
Score: NÃO DETERMINADO
Estado: NÃO CALCULADO
```

E Coverage permanece independente:

```text
Coverage: 0%
```

`None`/ausência nunca usa `0` como fallback visual. `Coverage: 0%` nunca é apresentado como `Score GEO: 0`.

Quando não existe base suficiente para consolidar `OVERALL_READINESS`, o relatório também usa linguagem equivalente a:

```text
COMPATIBILIDADE GEO
NÃO DETERMINADA
```

Isso significa **informação insuficiente para uma conclusão geral**. Não significa `FAIL` ou baixa qualidade do website.

## Classificação visual de scores válidos

| Score válido | Classificação | Semântica visual |
|---:|---|---|
| 90–100 | Excelente | sucesso / verde |
| 75–89 | Alta | sucesso / verde |
| 60–74 | Moderada | atenção / amarelo |
| 40–59 | Baixa | problema / laranja |
| 0–39 | Crítica | crítico / vermelho |
| sem score consolidado | Não Determinada | informação insuficiente / cinza |

As cores são sempre acompanhadas por texto. Informação metodológica utiliza azul.

## Desktop e Mobile

Desktop e Mobile permanecem independentes desde rendering até scoring. Não existe média artificial entre dispositivos.

É possível, por exemplo, haver:

```text
Desktop: 82 / Alta / Consolidado
Mobile: NÃO DETERMINADA
```

Isso não autoriza inferir uma nota combinada.

# Scorecard

A baseline utiliza dez dimensões:

1. Acessibilidade Técnica;
2. Capacidade de Indexação;
3. Extração de Conteúdo;
4. Estrutura Semântica;
5. Clareza de Entidades;
6. Dados Estruturados;
7. Capacidade de Resposta;
8. Preparação para Citação;
9. Evidências e Confiabilidade;
10. Cobertura de Intenções.

Cada linha mostra separadamente:

- score ou `NÃO DETERMINADO`;
- classificação textual;
- Coverage;
- Confidence;
- Consolidation Status.

`UNKNOWN`, `ERROR` e `NOT_APPLICABLE` não são convertidos em `FAIL`.

# Actionability: resultado técnico não é ordem de mudança

M14 adiciona uma classificação independente do `RuleResult`:

| Actionability | Texto do relatório | Interpretação |
|---|---|---|
| `REQUIRED_FIX` | **AÇÃO NECESSÁRIA** | problema evidence-backed cuja regra justifica correção |
| `REVIEW_RECOMMENDED` | **REVISÃO RECOMENDADA** | exige decisão humana/contextual antes de alterar o site |
| `OPTIONAL_IMPROVEMENT` | **MELHORIA OPCIONAL** | não bloqueante; não é defeito automático |
| `NO_ACTION` | **NENHUMA AÇÃO NECESSÁRIA** | passou ou não se aplica |
| `INSUFFICIENT_EVIDENCE` | **AÇÃO NO SITE NÃO DETERMINADA** | auditor não possui evidência suficiente para ordenar mudança |

A regra visual simples é sempre textual:

```text
PROBLEMA → deve ser corrigido quando actionability = AÇÃO NECESSÁRIA
ALERTA → revisar; pode ou não exigir alteração
MELHORIA OPCIONAL → boa prática não bloqueante
NÃO DETERMINADO → evidência insuficiente
NÃO APLICÁVEL → nenhuma ação necessária
APROVADO → nenhuma ação necessária
```

Actionability não altera score, severity, weight, Coverage, Confidence ou Consolidation.

# Evidência por página

Cada seção de página destaca a URL antes dos detalhes.

Para Desktop e Mobile, quando persistido, o relatório mostra:

- requested URL;
- final URL;
- HTTP status;
- estado do snapshot;
- dimensões da viewport;
- timestamp;
- screenshot PNG local.

A captura visual é complementar. Existem três planos distintos:

```text
RAW HTTP
→ verdade recebida do servidor

Rendered DOM
→ estado técnico após JavaScript

Visual Snapshot
→ estado visual observado pelo Chromium
```

Screenshot nunca substitui RAW ou DOM renderizado.

## Screenshot e bounding box

Quando um finding possui um `ElementObservation` único, selector reproduzível, elemento visível e bounding box válida, o relatório pode destacar a área correspondente no screenshot da viewport.

Findings não visuais — por exemplo canonical, meta robots, HTTP headers, `robots.txt`, sitemap ou JSON-LD invisível — não precisam de recorte/destaque visual específico.

Se não houver screenshot válido, o relatório mostra indisponibilidade; ele não fabrica uma imagem.

# ElementObservation e selector

Quando tecnicamente determinável, o finding pode apresentar:

- selector CSS observado;
- tag;
- id/classes relevantes;
- `outer_html` bounded/sanitizado;
- text excerpt;
- bounding box;
- artifact reference;
- snapshot/device de origem.

O auditor não escolhe um elemento arbitrário só para preencher o campo.

Quando a regra se aplica ao documento/conjunto de nós ou existem vários candidatos igualmente válidos:

```text
Seletor: NÃO DETERMINADO
Motivo: finding associado ao documento/conjunto de conteúdo ou nenhum único nó DOM pôde ser atribuído com segurança.
```

Isso é preferível a precisão inventada.

# Principais oportunidades e melhorias opcionais

A seção de ações é derivada somente de findings persistidos e classificados.

Uma dimensão apenas `UNKNOWN` não gera problema fictício.

M14 separa **Melhorias recomendadas — não bloqueantes** de defeitos. Ausência de uma capacidade opcional não é convertida automaticamente em `FAIL` nem reduz score apenas por não se aplicar.

Exemplos potenciais dependem das regras/evidências existentes: estrutura semântica, dados estruturados realmente aplicáveis, autoria/responsabilidade quando pertinente, freshness quando pertinente, citation readiness, intent coverage, respostas explícitas e clareza de entidades.

O relatório não inventa conteúdo, autor, datas, claims, fontes ou tipos Schema.org para preencher uma oportunidade.

# Actionable remediation

`REPORT-GEO-003` mantém o fluxo M13 e o amplia:

```text
Audit
  -> Domain resources
  -> Page
  -> PageSnapshot
  -> ElementObservation (quando aplicável)
  -> Evidence
  -> RuleExecution
  -> Finding
  -> Actionability
  -> Priority
  -> Remediation Recipe
  -> RuleReference
  -> Recommendation
  -> Actionable Report
```

## Remediation Recipe

Uma recipe determinística por `rule_id` pode informar:

- alvo técnico;
- elemento HTML;
- localização estrutural;
- tipo de ação;
- descrição da correção;
- exemplo técnico, quando seguro;
- critérios de aceite;
- como revalidar;
- decisão humana obrigatória, quando aplicável.

Recipes não alteram score nem severity. Elas explicam como tratar um finding já evidence-backed.

Regras sem recipe específica usam fallback claramente identificado.

## Exemplo: canonical ausente

Para `BR-GEO-013`, o relatório pode indicar:

```html
<link rel="canonical">
```

Local esperado:

```text
<head>
```

Se a canonical estiver ausente, o relatório explica que a equipe precisa definir qual URL é realmente preferencial antes de preencher o `href`.

Um exemplo estrutural pode ser mostrado como:

```html
<head>
  ...
  <link rel="canonical" href="https://URL-PREFERENCIAL.example/...">
</head>
```

O placeholder **não é uma canonical inferida pelo auditor**.

## HTML observado versus exemplo recomendado

Esses conceitos permanecem deliberadamente separados.

Quando o trecho original não foi persistido:

```text
Trecho HTML original não persistido para esta evidência.
```

Quando há `ElementObservation`/evidência concreta, o relatório pode mostrar o HTML **efetivamente observado** escapado como código.

Depois, quando seguro, apresenta uma **Estrutura recomendada — exemplo**.

O relatório não reconstrói nem fabrica HTML como se tivesse sido capturado.

# Fontes técnicas e heurísticas

M14 relaciona regras a referências técnicas versionadas quando existe fonte primária diretamente aplicável.

Prioridade:

- RFC/IETF;
- WHATWG;
- Google Search Central / documentação oficial de crawling;
- Schema.org quando aplicável;
- documentação oficial OpenAI para crawlers;
- documentação oficial da tecnologia analisada.

Quando uma regra é heurística ou não possui fonte normativa externa específica, o relatório informa explicitamente, por exemplo:

```text
Base: HEURISTIC
Fonte externa normativa: não aplicável / não identificada
Referência interna: BR-GEO-XXX
```

Uma fonte não é inventada para “fortalecer” a recomendação.

# robots.txt

A seção de domínio informa, quando persistido:

- URL consultada;
- estado;
- HTTP;
- interpretabilidade;
- sitemap(s) declarado(s);
- política observada para crawlers baseline;
- findings/actionability relacionados.

`OAI-SearchBot` e `GPTBot` são exibidos separadamente.

Ausência válida de `robots.txt` não é automaticamente defeito.

# Sitemaps

O relatório mostra:

- localizado ou `Sitemap: NÃO LOCALIZADO`;
- origem da descoberta (`ROBOTS_TXT`, caminho convencional ou sitemap index suportado);
- URL;
- HTTP;
- interpretabilidade;
- quantidade de URLs quando conhecida;
- URLs auditadas presentes/ausentes;
- parsing error;
- rastreabilidade de redirects/network via evidência HTTP persistida.

A baseline `BR-GEO-003` não transforma ausência de sitemap, isoladamente, em `FAIL` ou penalidade de score. Uma eventual sugestão pode ser classificada como melhoria opcional.

# Recomendações semânticas e de conteúdo

Quando M7 possui resultados persistidos, o relatório reutiliza:

- `reasoning_summary`;
- `evidence_ids`;
- entidades;
- intenção primária;
- intenções secundárias;
- assessments de estrutura semântica;
- answerability;
- citation readiness;
- evidence/trust;
- intent coverage.

Não existe segunda chamada livre de IA para “embelezar” o texto do relatório.

Exemplos semânticos são estruturais e não podem inventar:

- claims;
- preços;
- coberturas comerciais;
- datas;
- autor;
- fontes;
- condições de produto;
- fatos não sustentados;
- selector;
- HTML observado.

Quando uma correção depende de decisão editorial, jurídica ou de negócio, o relatório identifica isso como revisão/decisão humana.

# Uso de IA

## FULL

Provider semântico disponível e respostas válidas para o universo aplicável. Isso não implica Coverage 100% obrigatoriamente.

## DEGRADED

Parte da análise semântica ficou indisponível ou foi rejeitada. Saídas inválidas, schema incompatível ou evidence IDs inventados não viram defeito do website.

## NO_AI

A auditoria continua com regras determinísticas e heurísticas seguras. Regras semantic-only podem ficar `UNKNOWN`.

**NO_AI não reduz o score de qualidade atribuído ao website.** Pode reduzir Coverage, Confidence, Consolidation e impedir `OVERALL_READINESS`.

# Cobertura do Crawl e URL_SET

A seção de cobertura é reconstruída do estado persistido, sem depender do objeto M2 em memória.

No modo clássico, pode apresentar:

- URLs descobertas;
- URLs auditadas;
- `max_pages`;
- se o limite foi atingido;
- fontes de descoberta por seed, sitemap, links internos e redirects.

No modo `URL_SET`, o inventário explícito é o universo de páginas. O auditor também persiste a quantidade bruta fornecida e o número de URLs únicas após normalização/deduplicação.

Recursos de domínio continuam separados desse universo de páginas.

# Evidence e rastreabilidade

Cada correção detalhada preserva IDs de evidência. O desenvolvedor deve conseguir partir do report e rastrear:

```text
Audit
-> domínio
-> página
-> dispositivo/PageSnapshot
-> ElementObservation (quando aplicável)
-> rule_id / RuleExecution
-> Finding
-> Actionability
-> Priority
-> Remediation Recipe
-> RuleReference
-> aceite / revalidação
```

Evidence pode referenciar HTTP, headers, robots, sitemap, HTML/DOM, screenshot visual, canonical, headings, links, Dados Estruturados, conteúdo principal, análise semântica ou comparação Desktop/Mobile.

# Priority

A priorização continua usando `PRIORITY-GEO-001`:

- Severity — 45%;
- Impact — 30%;
- Confidence — 15%;
- Ease — 10%.

Classes:

- `P0`: blocker crítico material;
- `P1`: prioridade muito alta;
- `P2`: alta;
- `P3`: média;
- `P4`: baixa;
- `INFO`: informacional.

Priority não altera score de qualidade.

# Layout e portabilidade

O HTML deve tolerar URLs, selectors, JSON, HTML, IDs e model names longos sem expandir horizontalmente a página.

O contrato M14 usa, conforme componente:

- `min-width: 0`;
- `overflow-wrap: anywhere`;
- `word-break` quando apropriado;
- `overflow-x: auto` para `pre/code`;
- `clamp()` para tipografia responsiva;
- grids que colapsam em viewport estreita;
- `max-width: 100%` em screenshots.

O ZIP/workspace deve conter todos os assets locais necessários ao report.

# Limitações de segurança das sugestões

O relatório não deve recomendar mudanças apenas para aumentar score. Em particular:

- não escolhe canonical arbitrariamente;
- não remove `noindex` sem confirmar intenção;
- não cria structured data incompatível com conteúdo visível;
- não inventa autor;
- não inventa data de atualização;
- não inventa fonte;
- não inventa informação comercial;
- não inventa selector ou HTML observado;
- não recomenda conteúdo enganoso para sistemas de IA.

# Glossário essencial

- **RAW**: resposta HTTP preservada antes de rendering JavaScript.
- **RENDERED**: DOM/HTML após execução no Chromium.
- **Visual Snapshot**: screenshot PNG da viewport observada no Chromium; evidência complementar.
- **ElementObservation**: nó DOM concreto persistido com selector/HTML/bounding box quando tecnicamente determinável.
- **Actionability**: classificação independente do resultado bruto que informa se uma mudança no site é requerida, revisável, opcional, desnecessária ou indeterminada.
- **Evidence First**: conclusão precisa apontar para observação rastreável.
- **Readiness**: condição técnica/semântica para acesso, compreensão e reutilização; não resultado de ranking.
- **Coverage**: proporção do universo aplicável efetivamente avaliado.
- **Confidence**: confiança operacional do score a partir de Coverage/evidência/erros.
- **Consolidation**: estado que determina se o score possui base suficiente para uso agregado.
- **Remediation Recipe**: receita determinística e rastreável associada à regra para orientar correção e aceite.
- **RuleReference**: projeção de fonte técnica oficial aplicável ou identificação explícita de regra interna/heurística.
