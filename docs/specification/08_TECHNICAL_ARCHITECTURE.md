# TECHNICAL_ARCHITECTURE.md

**Status:** APPROVED — REPORT-SITE-GEO-001

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
→ semantic provider opcional
→ device comparison quando ambos existem
→ scoring
→ prioritization
→ root cause/precision
→ M11/M18 intermediate reporting
→ report-site finalization
```

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

M3 renderiza somente o conjunto selecionado. Downstream deve trabalhar sobre os snapshots realmente materializados. Nenhum provider semântico deve ser chamado para dispositivo não renderizado.

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

## 6. Artifacts

Podem incluir:

- RAW HTTP/HTML;
- rendered HTML;
- conteúdo principal;
- structured data;
- screenshots;
- evidence materializada.

Os artifacts são referenciados por caminhos relativos ao workspace.

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

M18 persiste sessão e tentativas. IA não executa scoring.

## 8. Scoring

`SCORE-GEO-002` é determinístico sobre RuleExecutions persistidas.

A camada de scoring não deve reexecutar website ou IA.

## 9. Reporting interno

M11/M15/M16/M17/M18 preservam seus contratos intermediários para compatibilidade de testes/módulos.

Durante `run_audit`, esses HTMLs intermediários não são o contrato final do usuário.

## 10. Report site final

O módulo `report_site` materializa:

```text
report/
├─ index.html
├─ mobile.html          # condicional
├─ desktop.html         # condicional
├─ remediation.html
├─ ai-usage.html
├─ references.html
└─ css/
   └─ site.css
```

`report/index.html` é o `AuditRunResult.report_path` e o `reports.file_path` persistido.

Após materialização bem-sucedida, intermediários `report.html` e `remediation.html` da raiz são removidos.

## 11. Separação de domínio na apresentação

- `index.html`: visão executiva/readiness;
- `mobile.html`: evidência e resultados Mobile;
- `desktop.html`: evidência e resultados Desktop;
- `remediation.html`: causa/prioridade/correção;
- `ai-usage.html`: operação da IA;
- `references.html`: fontes e metodologia.

Essa separação impede que falha de provider seja percebida como finding do website.

## 12. CSS

Todas as páginas finais referenciam:

```text
report/css/site.css
```

CSS inline/embutido não pertence ao contrato final do report site.

## 13. Segurança

Secrets nunca devem ser persistidos em:

- audit.db como valor de credencial;
- artifacts;
- report site;
- logging operacional.

Payload estruturado exibido deve passar por escaping/redaction apropriado.

## 14. Fonte de verdade

```text
audit.db + artifacts
```

HTML é projeção. Report generation não pode recalcular Score/Finding nem chamar provider externo.

## 15. Reprodutibilidade

Versionar:

- auditor;
- ruleset;
- rendering policy;
- prompt/contract semântico quando aplicável;
- scoring;
- prioritization;
- reporting contract.
