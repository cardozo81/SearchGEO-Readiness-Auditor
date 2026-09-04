# SearchGEO Readiness Auditor — Specification Index

**Status:** APPROVED BASELINE + M14/M15/M16/M17/M18/M20/M21 + SAFE PROVIDER EXTENSIONS + SCORE-GEO-002 + REPORT-SITE-GEO-001  
**Baseline:** MVP Functional Specification  
**Idioma normativo:** Português, preservando identificadores e termos técnicos quando necessário.

## 1. Objetivo

Este diretório constitui a fonte normativa do SearchGEO Readiness Auditor.

Uma IA, desenvolvedor ou ferramenta que assuma o projeto não deve depender do histórico de chats para descobrir requisitos formalizados.

Os documentos presentes neste diretório prevalecem sobre interpretações informais do histórico de conversa.

## 2. Ordem obrigatória de leitura

1. `00_SPEC_INDEX.md`
2. `12_AI_HANDOFF.md`
3. `10_DECISIONS.md`
4. `01_PROJECT_CHARTER_SCOPE.md`
5. `07_FUNCTIONAL_REQUIREMENTS.md`
6. `02_DOMAIN_MODEL.md`
7. `03_BUSINESS_RULES.md`
8. `04_WORKFLOWS.md`
9. `05_SCORING_MODEL.md`
10. `06_PRIORITIZATION_MODEL.md`
11. `08_TECHNICAL_ARCHITECTURE.md`
12. `09_IMPLEMENTATION_PLAN.md`
13. `11_REPORTING_LANGUAGE_GLOSSARY.md`
14. `13_MODEL_ROUTING_POLICY.md`
15. `14_MULTI_URL_VISUAL_EVIDENCE_REMEDIATION.md`
16. `15_ERROR_CENTRIC_REPORT_UX.md`
17. `16_ROOT_CAUSE_ELEMENT_REMEDIATION.md`
18. `17_REMEDIATION_PRECISION_REPORT_CONSISTENCY.md`
19. `18_MULTI_AI_PROVIDER_ROUTING.md`
20. `19_SCORE_APPLICABILITY_GEO_MINIMUMS.md`
21. `20_AI_CONTENT_REMEDIATION.md`
22. `21_EXTERNAL_WEB_PERFORMANCE_EVIDENCE.md`
23. `22_SAFE_AI_PROVIDER_EXTENSIONS.md`

## 3. Precedência documental

Em caso de conflito:

1. decisões explicitamente aprovadas em `10_DECISIONS.md`;
2. requisitos funcionais em `07_FUNCTIONAL_REQUIREMENTS.md`;
3. escopo em `01_PROJECT_CHARTER_SCOPE.md`;
4. modelos normativos de domínio, regras, workflows, scoring e priorização;
5. arquitetura técnica;
6. plano de implementação;
7. AI handoff e política operacional de modelos;
8. especificações de evolução de marco, quando não conflitarem com os itens anteriores.

Nenhuma decisão funcional deve ser alterada silenciosamente durante implementação.

A especificação `22_SAFE_AI_PROVIDER_EXTENSIONS.md` complementa M18/M20 sem substituir suas invariantes de routing, scoring, quarantine, telemetria ou segurança. Onde M18 enumera apenas a baseline histórica de providers, M22 formaliza providers adicionais explicit-only sem alterar `AUTO`.

## 4. Documentos

### `01_PROJECT_CHARTER_SCOPE.md`
Propósito, escopo, princípios, exclusões e critérios de aceite.

### `02_DOMAIN_MODEL.md`
Entidades, relacionamentos, identificadores, estados e invariantes.

### `03_BUSINESS_RULES.md`
Business Rules `BR-GEO-001` a `BR-GEO-054`.

### `04_WORKFLOWS.md`
Workflows `WF-GEO-001` a `WF-GEO-012` e ordem de execução.

### `05_SCORING_MODEL.md`
Score, Coverage, Confidence, Consolidation, aplicabilidade e agregações. Baseline vigente: `SCORE-GEO-002`. Confidence representa força da conclusão, não qualidade textual isolada.

### `06_PRIORITIZATION_MODEL.md`
Severity, Impact, Effort, Confidence e Priority.

### `07_FUNCTIONAL_REQUIREMENTS.md`
Requisitos `FR-GEO-*` e `NFR-GEO-*`. Inclui device context, report site, contrato M20 de remediação opcional, expansão M21 de evidência externa de Web Performance e requisitos gerais de provider independente/múltiplos providers.

### `08_TECHNICAL_ARCHITECTURE.md`
Arquitetura local/modular, seleção de dispositivo, finalização do report site, etapa M20 downstream de scoring/findings, enriquecimento M21 externo não-scoring e isolamento aditivo dos providers de extensão em relação ao núcleo M18 homologado.

### `09_IMPLEMENTATION_PLAN.md`
Baseline de marcos e evoluções formalizadas. Quando descrição histórica de output conflitar com `FR-GEO-046`/REPORT-SITE-GEO-001, prevalece o contrato final `report/`.

### `10_DECISIONS.md`
Decisões humanas consolidadas e pendências corporativas. D-037 formaliza `SCORE-GEO-002`; M21 não o substitui nem recalibra implicitamente.

### `11_REPORTING_LANGUAGE_GLOSSARY.md`
Linguagem e apresentação do relatório.

### `12_AI_HANDOFF.md`
Instruções para continuidade por IA/desenvolvedor.

### `13_MODEL_ROUTING_POLICY.md`
Política de uso de modelos conforme esforço/criticidade.

### `14_MULTI_URL_VISUAL_EVIDENCE_REMEDIATION.md`
Evolução M14: multi-URL, recursos de domínio, screenshots, ElementObservation, actionability, referências e distinção entre zero calculado e ausência de cálculo.

### `15_ERROR_CENTRIC_REPORT_UX.md`
M15 histórico evoluído por `REPORT-SITE-GEO-001`: visão por domínio, páginas Mobile/Desktop, remediação, telemetria IA, referências, menu compartilhado e CSS externo.

### `16_ROOT_CAUSE_ELEMENT_REMEDIATION.md`
M16: causa raiz evidence-backed, localização, observado versus esperado, mudança exata, aceite e revalidação.

### `17_REMEDIATION_PRECISION_REPORT_CONSISTENCY.md`
M17: reason code, observado versus alvo técnico, consistência e redução de duplicação.

### `18_MULTI_AI_PROVIDER_ROUTING.md`
M18: baseline multi-provider OpenAI/DeepSeek/MiMo, routing determinístico, failover, quarantine, URL lock e telemetria. Não altera scoring.

### `19_SCORE_APPLICABILITY_GEO_MINIMUMS.md`
`SCORE-GEO-002`, `NOT_APPLICABLE` versus `NOT_CONSOLIDATED`, JSON-LD opcional e premissas mínimas/contextuais.

### `20_AI_CONTENT_REMEDIATION.md`
M20: sugestões textuais opcionais/evidence-bound, default OFF, separação de scoring, reutilização do routing/provider selecionado, telemetria por finalidade e orientação determinística de JSON-LD por página/dispositivo.

### `21_EXTERNAL_WEB_PERFORMANCE_EVIDENCE.md`
M21: coleta opcional e controlada de Lighthouse via PageSpeed Insights e Core Web Vitals/CrUX, com persistência própria, artifacts, `report/web-performance.html`, zero chamadas LLM adicionais e separação rígida de `SCORE-GEO-002`.

### `22_SAFE_AI_PROVIDER_EXTENSIONS.md`
Extensão segura/aditiva para xAI/Grok, Alibaba Qwen, Google Gemini e Anthropic Claude. Define explicit-only, `PROVISIONAL`, isolamento de credenciais, contratos nativos, M20, regressão obrigatória, preservação de `AUTO` e gate de smoke humano antes de promoção/merge.

## 5. REPORT-SITE-GEO-001

A evolução de apresentação está formalizada por `FR-GEO-046`, `FR-GEO-047`, `FR-GEO-063`, `FR-GEO-070`, `FR-GEO-073..079` e pelos requisitos M20/M21, além de `08_TECHNICAL_ARCHITECTURE.md`, `15_ERROR_CENTRIC_REPORT_UX.md`, `20_AI_CONTENT_REMEDIATION.md` e `21_EXTERNAL_WEB_PERFORMANCE_EVIDENCE.md`.

Contrato público:

```text
<AUD-ID>/report/index.html
<AUD-ID>/report/mobile.html              # condicional
<AUD-ID>/report/desktop.html             # condicional
<AUD-ID>/report/remediation.html
<AUD-ID>/report/content-suggestions.html
<AUD-ID>/report/web-performance.html
<AUD-ID>/report/ai-usage.html
<AUD-ID>/report/references.html
<AUD-ID>/report/css/site.css
```

Default de dispositivo da CLI: `mobile`. `desktop` e `both` são seleções explícitas/parametrizáveis.

## 6. Fonte externa e heurística

O SearchGEO não deve representar seu score ou thresholds como standard GEO/AEO universal.

Referências primárias atuais incluem Google Search Central, OpenAI Help Center, Schema.org, WHATWG, IETF/RFC, Chrome Developers, PageSpeed Insights e Chrome UX Report. O guia oficial do Google de 2026 para recursos generativos reforça fundamentos de SEO e não cria markup especial GEO/AEO obrigatório.

Structured Data/JSON-LD é reforço opcional, não requisito universal de GEO. Quando M20 propõe ou revisa JSON-LD, deve usar somente conteúdo/evidência persistidos e manter a distinção entre Schema.org válido e elegibilidade de rich result específica de Search.

M21 introduz métricas externas documentadas para fenômenos específicos. Lighthouse e Core Web Vitals não devem ser apresentados como homologação do `SCORE-GEO-002`, nem combinados silenciosamente com ele. `SCORE-GEO-002` permanece índice interno heurístico/reprodutível; M21 permanece evidência externa complementar.

Heurísticas BR-GEO sem equivalente normativo devem permanecer identificadas como heurísticas/baseline interna.

## 7. Regra de mudança

Mudanças que afetem escopo, Business Rules, scoring, priorização, interpretação do relatório, device context público, conteúdo sugerido por IA, lista/routing de providers, consumo externo M21 ou requisitos corporativos devem ser reconciliadas nesta baseline antes da conclusão do merge.

Decisões puramente internas de implementação podem ser tomadas sem aprovação humana quando não alterarem comportamento funcional.

## M18 — Multi-AI Provider Abstraction, Reliability Routing & Usage Telemetry

Fonte normativa específica: `18_MULTI_AI_PROVIDER_ROUTING.md`. M18 não altera Business Rules, PRIORITY-GEO-001, actionability nem semântica de UNKNOWN.

A baseline automática M18 permanece OpenAI/DeepSeek/MiMo. Providers adicionais explicit-only são regidos por `22_SAFE_AI_PROVIDER_EXTENSIONS.md` e não alteram essa cadeia enquanto provisórios.

## SCORE-GEO-002 — Aplicabilidade e premissas mínimas GEO

Fonte normativa específica: `19_SCORE_APPLICABILITY_GEO_MINIMUMS.md`. Mantém as dez dimensões, mas dimensões integralmente e legitimamente `NOT_APPLICABLE` não bloqueiam nem reduzem o Overall.

## M20 — Optional AI Content Remediation + JSON-LD Guidance

Fonte normativa específica: `20_AI_CONTENT_REMEDIATION.md`. Sugestões textuais são default OFF, downstream de scoring e sempre dependentes de finding/evidência. A revisão JSON-LD é determinística e disponível mesmo sem provider externo.

M22 adiciona adapters M20 explicit-only sem modificar o router legado dos providers M18 existentes.

## M21 — External Web Performance Evidence

Fonte normativa específica: `21_EXTERNAL_WEB_PERFORMANCE_EVIDENCE.md`.

M21:

- é default OFF para evitar consumo externo não solicitado;
- usa PageSpeed Insights/Lighthouse e CrUX quando habilitado/configurado;
- possui limite de páginas, timeout e política de field data configuráveis;
- adiciona zero chamadas LLM de qualquer provider;
- persiste telemetria e raw response artifacts próprios;
- cria `report/web-performance.html`;
- não altera RuleExecution, Finding, Recommendation, Score, Coverage, Confidence, Consolidation ou `SCORE-GEO-002`.

## Safe AI Provider Extensions

Fonte normativa específica: `22_SAFE_AI_PROVIDER_EXTENSIONS.md`.

A extensão:

- adiciona xAI/Grok, Qwen, Gemini e Anthropic/Claude;
- mantém todos inicialmente `PROVISIONAL` e explicit-only;
- preserva `AUTO = OpenAI -> DeepSeek -> MiMo`;
- isola credenciais/modelos/endpoints;
- mantém schema/evidence validation e fail-closed;
- adiciona M20 nativo sem reativar provider quarantined;
- exige regressão automatizada e smoke humano antes de promoção/merge.
