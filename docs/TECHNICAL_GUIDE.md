# Guia Técnico

Este documento descreve a Stable Local Baseline M1–M12 como está implementada. Para requisitos normativos, prevalece [`docs/specification`](specification/00_SPEC_INDEX.md).

## Arquitetura real

```text
searchgeo CLI
  -> AuditRunner.run_audit
     -> M2 Discovery + HTTP
     -> M3 Rendering Desktop/Mobile
     -> M4 Extraction + Evidence
     -> M5 Deterministic Rules BR-GEO-001..018
     -> M6 JavaScript/SPA BR-GEO-019..024
     -> Content Extractability BR-GEO-025..027
     -> M7 Semantic Provider BR-GEO-028..049
     -> M8 Desktop/Mobile Comparison BR-GEO-052
     -> Pre-scoring Rules BR-GEO-050/051/053
     -> M9 Scoring + BR-GEO-054/reproducibility contract
     -> M10 Prioritization + Recommendations
     -> M11 Static HTML Report
```

`AuditRunner` é o orquestrador da Stable Local Baseline. Ele cria o workspace/Audit/AuditTarget, chama os marcos na ordem prevista, atualiza lifecycle status, finaliza como `COMPLETE`/`COMPLETE_WITH_LIMITATIONS` ou marca `FAILED` em exceção não absorvida.

## Principais módulos

| Arquivo/módulo | Responsabilidade |
|---|---|
| `cli.py` | parser, validação inicial, configuração de logging e chamada do AuditRunner |
| `audit_runner.py` | pipeline ponta a ponta M2→M11 |
| `domain.py` | entidades centrais, enums e IDs |
| `persistence.py` | SQLite M1 + workspace filesystem + integridade referencial |
| `url_utils.py` | normalização/resolução conservadora de URLs |
| `acquisition.py` | HTTP, redirects, headers, erros de rede |
| `discovery.py` | seed, robots, sitemaps, links, deduplicação e seleção por budget |
| `m2.py` | persistência da descoberta/HTTP e primeiras RuleExecutions técnicas |
| `rendering.py` | Playwright/Chromium, perfis Desktop/Mobile e falhas de rendering |
| `m3.py` | materialização de PageSnapshots e rendered artifacts |
| `extraction.py` | parser determinístico de metadata, links, headings, main content e JSON-LD |
| `evidence.py` | criação consistente de Evidence |
| `m4.py` | extração por snapshot + artifacts + Evidence |
| `rules.py` | RuleDefinition/Registry/DependencyResolver para bloco determinístico inicial |
| `m5.py` | BR-GEO-001..018 e Findings evidence-backed |
| `javascript_spa.py` | comparação RAW×RENDERED, SPA/CSR, soft-404, lazy loading |
| `m6.py` | BR-GEO-019..024 |
| `content_extractability.py` | BR-GEO-025..027 |
| `semantic.py` | contrato provider-independent, NoneProvider, OpenAIProvider e validação |
| `semantic_persistence.py` | SemanticAssessment e EntityObservation em SQLite |
| `m7.py` | BR-GEO-028..049 + FULL/DEGRADED/NO_AI |
| `comparison.py` | comparação Desktop/Mobile |
| `m8.py` | BR-GEO-052 |
| `pre_scoring_rules.py` | BR-GEO-050/051/053 |
| `scoring.py` | SCORE-GEO-001, Coverage, Confidence, Consolidation e contributions |
| `scoring_persistence.py` | persistência de Score/ScoreContribution |
| `m9.py` | execução/persistência do scoring e integridade de reprodutibilidade |
| `prioritization.py` | PRIORITY-GEO-001, groups e recommendation templates |
| `recommendation_persistence.py` | persistência M10 |
| `m10.py` | orquestra priorização/recomendações |
| `reporting.py` | HTML estático, escaping/redaction, queries e metadata REPORT-GEO-001 |
| `m11.py` | grava `report.html` e metadata |

## Modelo de domínio

### Audit

Raiz da execução. Guarda projeto, status, completion status, idioma, mercado, `max_pages`, `audit_mode`, capabilities, limitações e versões.

Lifecycle implementado inclui `INITIALIZING`, `DISCOVERING`, `ACQUIRING`, `COMPARING`, `SCORING`, `RECOMMENDING`, `REPORTING`, `COMPLETED` e `FAILED`, entre outros estados disponíveis no domínio.

### AuditTarget

Target normalizado e origin associado ao Audit. A CLI atual cria `DOMAIN` ou `URL`; `URL_SET` existe no domínio, mas não é exposto pela CLI da Stable Local Baseline.

### Page

URL selecionada para o universo auditado, com URL normalizada, URL descoberta, provenance (`SEED`, `SITEMAP`, `INTERNAL_LINK` etc.) e depth.

### PageSnapshot

Observação de uma Page em `DESKTOP` ou `MOBILE`, contendo HTTP/rendering/extraction refs e classificação arquitetural (`STATIC_OR_SSR`, `HYDRATED`, `CSR_SPA`, `MIXED`, `UNKNOWN`).

### Evidence

Observação rastreável. Relaciona audit/page/snapshot/device, tipo, source, observed value, optional artifact reference e timestamp.

### RuleExecution

Execução versionada de uma Business Rule: resultado, observed value, expected condition, Evidence e erro técnico quando aplicável.

### Finding

Problema/alerta publicado. O domínio rejeita Finding sem Evidence; a persistência também valida consistência com RuleExecution/page/device/evidence.

### SemanticAssessment / EntityObservation

Persistência M7 de avaliações provider-independent, provenance do provider/model/prompt/configuração, confidence/evidence e entidades observadas.

### Score / ScoreContribution

Resultado por dimensão/device e unidade que liga o cálculo a uma RuleExecution. `SCORE-GEO-001` é determinístico.

### RemediationGroup / Recommendation

Agrupamento por causa + regra e ação recomendada com Severity/Impact/Effort/Confidence/Priority.

### Report

A implementação usa `ReportRecord` para metadata (`REPORT-GEO-001`) e `report.html` para a projeção estática. HTML não é fonte primária.

## Persistência

### SQLite

`audit.db` usa `sqlite3` embutido. As tabelas cobrem domínio, Evidence, RuleExecution, Finding e entidades adicionadas pelos marcos posteriores. Foreign keys e validações na camada Repository preservam integridade de scope.

### Filesystem

`AuditWorkspace` materializa:

```text
<AUD-ID>/audit.db
<AUD-ID>/artifacts/
<AUD-ID>/report.html
```

Artifacts de HTTP/rendering/extraction são apontados por paths relativos persistidos.

## Pipelines por marco

### M1 — Audit + Persistence

Cria/reabre workspaces, round-trip das entidades e integridade referencial.

### M2 — Discovery + HTTP

Descobre universo, respeita `max_pages`, persiste provenance/HTTP/robots/sitemap/RAW. Falhas HTTP/rede são dados de aquisição, não exceções globais por padrão.

### M3 — Rendering

Para cada Page, cria snapshots Desktop e Mobile independentes. Um Chromium pode ser reutilizado, mas cada render usa browser context independente.

### M4 — Extraction + Evidence

Prioriza rendered DOM, usa RAW fallback, materializa main content/Structured Data e Evidence.

### M5 — Deterministic Rules

Registry, dependencies e findings. Falha de pré-requisito bloqueia derivadas em vez de multiplicar FAIL.

### M6 — JavaScript/SPA

RAW×RENDERED, arquitetura, direct routes, navegação crawlable, soft-404 e lazy loading bounded. CSR/SPA válido não recebe penalidade por arquitetura em si.

### Content Extractability

BR-GEO-025..027: conteúdo principal, boilerplate e preservação de qualificadores sem threshold arbitrário de palavras.

### M7 — Semantic

Provider independent. Determinístico/híbrido continua sem IA; semantic-only usa fallback seguro. Output externo precisa passar schema + evidence validation.

### M8 — Device Comparison

Classifica SAME/DIFFERENT/NOT_APPLICABLE/UNKNOWN e separa diferença observada de problema material.

### Pre-scoring

Internal links no universo conhecido, duplicates/near-duplicates somente no universo auditado e integridade de Findings.

### M9 — Scoring

Produz Score/Contributions por device e dimensão, controla double counting e reliability.

### M10 — Prioritization

Agrupa findings por root cause e cria recommendation determinística. Priority não altera score.

### M11 — Report

Consulta estado persistido, aplica escaping/redaction e grava HTML estático autocontido + metadata.

### M12 — Stable Local Baseline

Integra todos os blocos em `AuditRunner` e conecta a CLI real. A suíte crítica valida pipeline e delegação operacional.

## Tratamento de erros

Princípios implementados:

```text
UNKNOWN != FAIL
ERROR != FAIL
NOT_APPLICABLE != FAIL
```

- Página inacessível pode gerar FAIL técnico de retrievability, enquanto regras derivadas ficam NOT_APPLICABLE/UNKNOWN.
- Rendering Desktop pode falhar sem apagar o snapshot Mobile.
- Extração falha por snapshot.
- Provider indisponível degrada análise sem publicar FAIL do site.
- M8 trata ausência de um device como UNKNOWN.
- AuditRunner marca Audit `FAILED` somente quando uma exceção escapa da pipeline.

## Prevenção de cascading failures

`DependencyResolver` bloqueia regra derivada quando dependency retorna FAIL/ERROR/UNKNOWN/NOT_APPLICABLE. O objetivo é publicar a causa observável e evitar sintomas semânticos artificiais.

Exemplo:

```text
HTTP não recuperável -> finding técnico
entity/answerability dependentes -> NOT_APPLICABLE/UNKNOWN
```

## Pontos de extensão

### Nova Business Rule

1. Atualize primeiro a specification normativa.
2. Defina ID/version/category/dimension/scope/basis/dependencies/severity/scoring group.
3. Implemente checks e Evidence.
4. Garanta fallback e no-cascade.
5. Adicione mapping de scoring somente se normativamente aplicável.
6. Teste persistência/rastreabilidade.

Não reutilize IDs existentes nem altere semanticamente BR-GEO-* sem decisão normativa.

### Novo provider semântico

Implemente o protocolo `SemanticAnalysisProvider` e retorne `ProviderCallResult`. Preserve validação de schema/evidence antes de aceitar output. Business Rules não devem importar provider específico.

### Nova Evidence

Use `EvidenceManager`/domínio e mantenha scope audit/page/snapshot/device consistente. Artifacts devem usar path relativo ao workspace.

### Nova extração

Adicione ao `ContentExtractor`/persistência de snapshot de forma determinística; preserve RAW e RENDERED como fontes distinguíveis.

### Nova seção do relatório

`ReportBuilder` deve consumir estado persistido, não recalcular fonte primária no HTML. Preserve escaping, redaction, autocontenção e `REPORT-GEO-*` versionamento quando houver mudança de contrato.

## Limitações técnicas atuais

- Python 3.13 continua obrigatório.
- CLI é a única interface de produto.
- Não há web UI/server.
- Não há resume de auditoria interrompida.
- Logging atual é process-level; não há `audit.log` materializado.
- Ajustes internos de timeout/browser/provider não estão expostos como flags de usuário.
