# TECHNICAL_ARCHITECTURE.md

**Status:** APPROVED — M20 + REPORT-SITE-GEO-001

## 1. Estilo arquitetural

Aplicação local, modular, CLI-first, single-machine no baseline.

Não exige:

- web server;
- database server;
- Docker;
- daemon/background worker;
- IA externa.

## 2. Runtime

- CPython 3.13.x;
- Playwright + Chromium;
- SQLite embarcado;
- filesystem local;
- HTTP/HTTPS para target;
- HTTPS para provider externo somente quando habilitado.

## 3. Pipeline

```text
CLI
→ configuração/contexto de dispositivo
→ discovery/acquisition
→ rendering
→ extraction/evidence
→ deterministic rules
→ semantic provider opcional (M7/M18)
→ device comparison quando ambos existem
→ scoring (M9)
→ prioritization/remediation base (M10/M16/M17)
→ M20 opcional: sugestão textual evidence-bound + revisão JSON-LD determinística
→ M11/M18 intermediate reporting
→ report-site finalization
→ M20 report projection/navigation enrichment
```

Invariante: M20 começa somente depois de scoring/findings/priorização concluídos. A etapa pode criar apenas objetos auxiliares M20; não altera os objetos já avaliados.

## 4. Device context

A CLI resolve exatamente um dos valores:

```text
mobile
desktop
both
```

Default de usuário:

```text
mobile
```

Precedência:

1. `--device-context`;
2. `SEARCHGEO_DEVICE_CONTEXT`;
3. `mobile`.

M3 renderiza somente o conjunto selecionado. Downstream trabalha sobre os snapshots realmente materializados. Nenhum provider semântico nem M20 deve ser chamado para dispositivo não renderizado.

Chamadas internas diretas a M3 sem variável preservam `both` para compatibilidade interna/testes.

## 5. Persistência

Workspace:

```text
<AUD-ID>/
├─ audit.db
├─ artifacts/
└─ report/
```

SQLite guarda entidades estruturadas; filesystem guarda payloads/artefatos grandes.

M20 adiciona entidades reabríveis separadas:

```text
content_remediation_runs
content_remediation_suggestions
content_remediation_attempts
jsonld_remediation_suggestions
```

Essas tabelas são auxiliares e não participam do denominador de scoring.

## 6. Artifacts

Podem incluir:

- RAW HTTP/HTML;
- rendered HTML;
- conteúdo principal;
- structured data;
- screenshots;
- evidence materializada.

Os artifacts são referenciados por caminhos relativos ao workspace.

M20 reutiliza artifacts persistidos e não refaz crawling/rendering.

## 7. IA

`SemanticAnalysisProvider` é abstração independente de fornecedor.

Providers suportados na baseline operacional:

```text
NONE
OPENAI
DEEPSEEK
MIMO
AUTO router
```

M18 persiste sessão/tentativas da finalidade de análise semântica. IA não executa scoring.

M20, quando habilitado, cria uma sessão de remediação derivada dos providers M18 ainda saudáveis. Não existe segunda credencial/model surface. M20 preserva quarantine anterior e executa failover/URL pinning próprio para a finalidade de remediação, mantendo telemetria separada.

## 8. M20

### 8.1 Texto

Input por snapshot/device:

```text
URL + title + conteúdo principal persistido
+ findings elegíveis
+ evidence IDs/observed values desses findings
```

Output validado:

```text
finding_id
objective
target_location
proposed_text
evidence_ids
confidence
review_note
```

Respostas que escapem do finding/evidence universe são rejeitadas. Tokens numéricos novos ausentes do corpus persistido também são rejeitados como contenção contra fabricação factual.

### 8.2 JSON-LD

A orientação JSON-LD é determinística e independente da ativação da chamada textual por IA.

Sem JSON-LD, o módulo pode produzir um baseline conservador `WebPage` com valores persistidos. Com JSON-LD, realiza revisão genérica não destrutiva e não substitui graphs existentes.

## 9. Scoring

`SCORE-GEO-002` é determinístico sobre RuleExecutions persistidas.

A camada de scoring não deve reexecutar website ou IA.

M20 é estritamente downstream e não pode invalidar ou recalcular scoring já concluído.

## 10. Reporting interno

M11/M15/M16/M17/M18 preservam seus contratos intermediários para compatibilidade de testes/módulos.

Durante `run_audit`, esses HTMLs intermediários não são o contrato final do usuário.

## 11. Report site final

O contrato final materializa:

```text
report/
├─ index.html
├─ mobile.html             # condicional
├─ desktop.html            # condicional
├─ remediation.html
├─ content-suggestions.html
├─ ai-usage.html
├─ references.html
└─ css/
   └─ site.css
```

`report/index.html` é o `AuditRunResult.report_path` e o `reports.file_path` persistido.

Após materialização bem-sucedida, intermediários `report.html` e `remediation.html` da raiz são removidos.

`m20_reporting` é uma projeção sobre dados já persistidos: escreve `content-suggestions.html`, conecta a navegação compartilhada e inclui a telemetria M20 em `ai-usage.html`. O renderer não chama provider.

## 12. Separação de domínio na apresentação

- `index.html`: visão executiva/readiness;
- `mobile.html`: evidência e resultados Mobile;
- `desktop.html`: evidência e resultados Desktop;
- `remediation.html`: causa/prioridade/correção;
- `content-suggestions.html`: texto opcional e JSON-LD advisory;
- `ai-usage.html`: operação/telemetria M18 e M20, separadas por finalidade;
- `references.html`: fontes e metodologia.

Essa separação impede que falha de provider seja percebida como finding do website.

## 13. CSS

Todas as páginas finais referenciam:

```text
report/css/site.css
```

CSS inline/embutido não pertence ao contrato final do report site.

## 14. Segurança

Secrets nunca devem ser persistidos em:

- audit.db como valor de credencial;
- artifacts;
- report site;
- logging operacional.

Payload estruturado exibido deve passar por escaping/redaction apropriado.

M20 não persiste headers de autenticação nem bodies de erro de provider não sanitizados.

## 15. Fonte de verdade

```text
audit.db + artifacts
```

HTML é projeção. Report generation não pode recalcular Score/Finding nem chamar provider externo.

M20 external calls, quando habilitadas, ocorrem **antes** da materialização final e persistem o resultado; a projeção HTML apenas lê o estado reabrível.

## 16. Reprodutibilidade

Versionar:

- auditor;
- ruleset;
- rendering policy;
- prompt/contract semântico quando aplicável;
- contrato M20;
- scoring;
- prioritization;
- reporting contract.
