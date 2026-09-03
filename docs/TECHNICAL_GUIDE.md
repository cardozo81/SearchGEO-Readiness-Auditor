# Guia Técnico

Este documento descreve a baseline implementada até M18. Para requisitos normativos, prevalece [`docs/specification`](specification/00_SPEC_INDEX.md).

# Arquitetura atual

```text
searchgeo CLI
  -> AuditRunner.run_audit
     -> M2 Discovery + HTTP
     -> M3 Rendering Desktop/Mobile
     -> M4 Extraction + Evidence
     -> M5 Deterministic Rules BR-GEO-001..018
     -> M6 JavaScript/SPA BR-GEO-019..024
     -> Content Extractability BR-GEO-025..027
     -> M7 Semantic Rules BR-GEO-028..049
        -> M18 provider abstraction/routing/telemetry
     -> M8 Desktop/Mobile Comparison BR-GEO-052
     -> Pre-scoring BR-GEO-050/051/053
     -> M9 Scoring + BR-GEO-054
     -> M10 Prioritization + Recommendations
     -> M14 Visual/DOM evidence + URL_SET
     -> M15 Report UX + remediation.html
     -> M16 Root Cause / element-level remediation
     -> M17 Precision/report consistency
     -> M11/M18 report projections
```

`AuditRunner` continua sendo o orquestrador ponta a ponta. M18 é aditivo: não muda Business Rules nem `SCORE-GEO-001`.

# Principais módulos

| Módulo | Responsabilidade |
|---|---|
| `cli.py` | parser, validação, seleção de provider e chamada do runner |
| `audit_runner.py` | pipeline ponta a ponta |
| `domain.py` | entidades/enums/IDs |
| `persistence.py` | SQLite base + workspace |
| `acquisition.py` / `discovery.py` | HTTP, robots, sitemap, links |
| `rendering.py` / `m3.py` | Chromium + snapshots Desktop/Mobile |
| `extraction.py` / `m4.py` | extração + Evidence |
| `rules.py` / `m5.py` | regras determinísticas |
| `javascript_spa.py` / `m6.py` | SPA/CSR/direct routes/lazy/soft-404 |
| `content_extractability.py` | BR-GEO-025..027 |
| `semantic.py` / `m7.py` | contrato semântico e aplicação das BR-GEO-028..049 |
| `m18_ai.py` | adapters OpenAI/DeepSeek/MiMo, routing AUTO, quarantine, URL lock, usage/cost |
| `m18_persistence.py` | sessões/tentativas/catálogo de preços e logging sanitizado |
| `m18_reporting.py` | projeção operacional da IA nos HTMLs |
| `comparison.py` / `m8.py` | Desktop/Mobile |
| `pre_scoring_rules.py` | BR-GEO-050/051/053 |
| `scoring.py` / `m9.py` | SCORE-GEO-001, Coverage, Confidence, Consolidation |
| `prioritization.py` / `m10.py` | prioridade/grupos/recomendações |
| `m14_*` | visual/DOM linking, URL_SET e evidência |
| `m16_*` | causa raiz/escopo de elemento |
| `m17_*` | precisão e consistência de reporting |
| `reporting.py` / `m11.py` | report principal base |
| `remediation.py` | remediation transversal |

# CLI

A interface atual aceita uma URL, múltiplas URLs ou `--urls-file`, com parâmetros operacionais e seleção de IA.

A referência completa está em [CLI_REFERENCE.md](CLI_REFERENCE.md).

# Modelo de dados principal

## Audit

Raiz da execução. Persiste lifecycle, projeto, idioma, mercado, `max_pages`, `audit_mode`, capabilities e limitations.

## AuditTarget

Pode representar target clássico ou `URL_SET` explícito.

## Page / PageSnapshot

`Page` representa URL auditada. `PageSnapshot` representa observação Desktop/Mobile com HTTP/rendering/extraction e artifacts.

## Evidence / RuleExecution / Finding

Evidence First permanece invariante. Finding precisa ser rastreável a RuleExecution/Evidence.

## SemanticAssessment / EntityObservation

Persistência M7 de resultados semânticos aceitos.

## Score / ScoreContribution

Scoring determinístico por device/dimensão; LLM não calcula score.

## Root cause / remediation

M16/M17 adicionam projeções/materializações de causa/localização/ação sem alterar semântica das Business Rules.

# Persistência M18

M18 acrescenta:

```text
ai_audit_sessions
ai_provider_attempts
provider_pricing_catalog
```

`ai_audit_sessions` descreve estratégia, cadeia inicial, provider efetivo e estados.

`ai_provider_attempts` descreve cada chamada materializada com URL/device/provider/model/depth/status/duração/diagnóstico/usage/custo estimado.

`provider_pricing_catalog` versiona preços usados para `ESTIMATED_COST`.

Nunca persistir:

- API key;
- Authorization;
- body integral sensível;
- chain-of-thought.

# Provider abstraction M18

Adapters implementados:

```text
OpenAIProvider
DeepSeekProvider
MiMoProvider
NoneProvider
```

`GitHub Copilot` não é SemanticProvider.

Modelos suportados:

```text
OPENAI:   gpt-5.6-sol | gpt-5.6-terra | gpt-5.6-luna
DEEPSEEK: deepseek-v4-pro | deepseek-v4-flash
MIMO:     mimo-v2.5-pro | mimo-v2.5
```

# SINGLE_PROVIDER

Provider explícito:

- não faz fallback para outro fornecedor;
- sem key -> `NOT_CONFIGURED`;
- falha qualificadora -> `QUARANTINED_FOR_AUDIT`;
- após quarantine, não há nova chamada naquele audit;
- sessão insuficiente -> `DEGRADED`;
- `CHAIN_EXHAUSTED` não é usado para `SINGLE_PROVIDER`.

# AUTO

`ProviderRoutingSession`:

1. considera apenas providers com key/configuração válida;
2. ordena por rank SearchGEO do model;
3. mantém cadeia inicial imutável;
4. tenta candidatos sequencialmente;
5. quarantina provider falho;
6. promove fallback saudável quando permitido;
7. não reintroduz provider quarantined.

Se todos forem quarantined:

```text
CHAIN_EXHAUSTED
AI_PROVIDER_CHAIN_EXHAUSTED
```

# URL provider lock

A primeira resposta válida fixa o provider da URL. Desktop/Mobile da mesma URL devem usar o mesmo provider.

Se o pinned provider falhar no segundo device, não existe cross-provider completion naquela URL. O provider é quarantined para URLs seguintes.

# Contrato de aceitação semântica

Resposta válida exige exatamente BR-GEO-028..049, sem duplicidade/omissão/ID estranho, enums válidos e evidence IDs existentes.

HTTP 200 sozinho não implica `AVAILABLE`.

OpenAI usa JSON Schema estrito nativo. DeepSeek usa modo estruturado compatível com o adapter e validação local. MiMo usa JSON object + validação local estrita do schema SearchGEO.

# Error taxonomy

```text
AUTH_ERROR
QUOTA_ERROR
CREDIT_ERROR
RATE_LIMIT_ERROR
MODEL_ERROR
PERMISSION_ERROR
NETWORK_ERROR
TIMEOUT_ERROR
SERVER_ERROR
CONTRACT_ERROR
EMPTY_RESPONSE
INVALID_RESPONSE
UNKNOWN_PROVIDER_ERROR
```

Diagnósticos são sanitizados.

# Usage e custo

`ProviderUsage` normaliza:

- input tokens;
- cached input tokens;
- output tokens;
- reasoning tokens;
- total tokens.

Campos não reportados ficam `None`/`NULL`.

`ESTIMATED_COST` usa catálogo local versionado e não é billing oficial nem componente do score.

# Logging M18

`m18_persistence.py` emite logs INFO sanitizados por tentativa e sessão quando o nível configurado permite.

Inclui somente dados operacionais como provider/model/status/duração/tokens/custo/error_class.

A baseline não materializa `audit.log` automaticamente.

# Reporting M18

`m18_reporting.py` enriquece os HTMLs depois da projeção base.

`report.html` recebe seção operacional detalhada.

`remediation.html` recebe apenas contexto da análise semântica; falha do provider nunca vira finding/recommendation.

# Princípios de falha

```text
UNKNOWN != FAIL
ERROR != FAIL
NOT_APPLICABLE != FAIL
```

Falha de infraestrutura/provider pode reduzir Coverage/Confidence/Consolidation sem reduzir qualidade do website artificialmente.

# Prevenção de cascading failures

Dependências bloqueadas produzem estado não conclusivo em derivadas em vez de multiplicar FAILs.

Exemplo:

```text
HTTP não recuperável
  -> finding técnico de acesso quando aplicável
  -> semântica derivada UNKNOWN/NOT_APPLICABLE
```

# Report e artifacts

Workspace atual:

```text
<AUD-ID>/
  audit.db
  report.html
  remediation.html
  artifacts/
```

Screenshots/rendered/raw/extractions são paths relativos ao workspace.

# Pontos de extensão

## Nova Business Rule

Atualize specification antes de implementar; preserve evidence/dependency/scoring invariants.

## Novo provider

Implemente contrato provider-neutral, validação local, error taxonomy, usage e política de segurança. Não faça Business Rule importar fornecedor específico.

## Novo model

Adicione explicitamente ao allowlist/policy/pricing/qualificação e valide contrato. Não basta aceitar string arbitrária.

## Nova Evidence

Preserve scope e provenance.

## Nova seção de relatório

Consuma estado persistido; não use HTML como fonte primária.

# Limitações técnicas atuais

- Python 3.13 obrigatório;
- CLI é a interface do produto;
- sem web UI/server;
- sem resume de audit interrompido;
- logging process-level, sem `audit.log` automático;
- endpoints/timeouts/viewports não expostos como flags públicas;
- live compatibility de provider depende também de credencial/conta/egress externos;
- DeepSeek/MiMo permanecem PROVISIONAL até benchmark SearchGEO específico.

# Referências

- [Referência completa da CLI](CLI_REFERENCE.md)
- [Guia de IA](AI_GUIDE.md)
- [Configuração](CONFIGURATION.md)
- [Guia do relatório](REPORT_GUIDE.md)
- [Especificação M18](specification/18_MULTI_AI_PROVIDER_ROUTING.md)
