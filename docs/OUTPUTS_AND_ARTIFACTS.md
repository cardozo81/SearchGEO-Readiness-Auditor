# OUTPUTS_AND_ARTIFACTS.md

## Workspace

```text
<audits-root>/<AUD-ID>/
├─ audit.db
├─ artifacts/
└─ report/
   ├─ index.html
   ├─ mobile.html              # condicional
   ├─ desktop.html             # condicional
   ├─ remediation.html
   ├─ content-suggestions.html
   ├─ ai-usage.html
   ├─ references.html
   └─ css/site.css
```

`audit.db` + `artifacts/` são fonte persistente; `report/` é projeção humana.

## audit.db

Inclui audit/target/pages/snapshots, RuleExecutions, Evidence, findings, semântica, scores, recomendações, M16/M17, report metadata, M18 e M20.

Tabelas M20:

```text
content_remediation_runs
content_remediation_attempts
content_remediation_suggestions
jsonld_remediation_suggestions
```

## artifacts

RAW, rendered HTML, conteúdo principal, Structured Data, screenshots e outras evidências referenciadas por caminhos relativos.

## report/index.html

Dashboard executivo: devices, Overall, Coverage, Confidence, Consolidation, dimensões/actionability e links.

## mobile.html / desktop.html

Gerados somente para devices auditados; contêm scorecard, páginas, snapshots, findings e estado semântico do contexto.

## remediation.html

Plano técnico evidence-backed baseado em prioridade e M16/M17.

## content-suggestions.html

Projeção advisory M20:

- status M20;
- sugestões textuais aceitas, com finding/evidence/provider/model;
- proposta JSON-LD quando ausente;
- melhorias quando JSON-LD existe;
- aviso de revisão humana.

A página não altera Score/findings e não aplica alterações ao website.

## ai-usage.html

Telemetria operacional separada do readiness, incluindo M18 e M20: estratégia/provider/model, URL/device, status, tokens, duração, custo estimado e erros sanitizados.

## references.html

Fontes oficiais/primárias, natureza das regras, fórmulas e limites do modelo interno.

## CSS

Todos os HTMLs finais usam `report/css/site.css`; não há CSS final embutido no head.

## Device selection

Artifacts e chamadas externas só existem para devices selecionados/materializados.

## Segurança

Não persistir API key, Authorization, senha/secret ou body integral sensível. Credenciais permanecem isoladas por provider.

## Portabilidade

Para preservar screenshots, mova o workspace inteiro; `report/` usa caminhos relativos a `../artifacts/`.
