# OUTPUTS_AND_ARTIFACTS.md

## Workspace

Cada auditoria possui:

```text
<audits-root>/<AUD-ID>/
├─ audit.db
├─ artifacts/
└─ report/
   ├─ index.html
   ├─ mobile.html          # condicional
   ├─ desktop.html         # condicional
   ├─ remediation.html
   ├─ ai-usage.html
   ├─ references.html
   └─ css/
      └─ site.css
```

`audit.db` e `artifacts/` são dados/evidências persistentes. `report/` é projeção humana.

## `audit.db`

SQLite local, reabrível. Contém entidades do pipeline, incluindo conforme aplicável:

- audit/target/pages/snapshots;
- RuleExecutions;
- Evidence;
- findings;
- semantic assessments/entities;
- scores e contributions;
- remediation groups/recommendations;
- materialização M16/M17;
- report metadata;
- sessão/tentativas M18 e catálogo de preço.

O report site não substitui o banco e não recalcula o conteúdo persistido.

## `artifacts/`

Contém evidência materializada pelo pipeline, por exemplo:

- respostas RAW;
- HTML renderizado;
- conteúdo extraído;
- Structured Data;
- screenshots;
- outros artefatos referenciados por Evidence/PageSnapshot.

A estrutura interna pode incluir subdiretórios por page/device/snapshot. Referências persistidas usam caminhos relativos ao workspace.

## `report/index.html`

Ponto de entrada do mini-site. Dashboard executivo com:

- dispositivos efetivamente auditados;
- Overall quando consolidado;
- Coverage;
- Confidence;
- Consolidation;
- dimensões;
- contagens de actionability;
- links para os outros domínios.

## `report/mobile.html`

Materializado somente quando existem snapshots Mobile. Contém:

- scorecard Mobile;
- dimensões Mobile;
- páginas auditadas;
- snapshots visuais quando disponíveis;
- findings Mobile/BOTH aplicáveis;
- avaliações semânticas Mobile não aprovadas.

## `report/desktop.html`

Equivalente para Desktop e só existe quando Desktop foi auditado.

## `report/remediation.html`

Visão transversal por causa/problema. Reutiliza dados persistidos de priorização e M16/M17.

Pode apresentar por ocorrência:

- causa raiz;
- reason code;
- selector observado;
- alvo técnico/local esperado;
- mudança recomendada;
- observado vs esperado;
- exemplo;
- critérios de aceite;
- revalidação;
- decisão humana.

## `report/ai-usage.html`

Telemetria operacional M18 separada do readiness do website:

- estratégia;
- provider/model efetivo;
- status;
- cadeia inicial;
- chamadas por URL/device;
- tokens;
- duração;
- custo estimado;
- erros sanitizados.

Essa página não cria finding nem altera Score.

## `report/references.html`

Referência técnica gerada junto com a auditoria:

- fontes oficiais/primárias;
- distinção entre regras oficiais, standards e heurísticas internas;
- fórmula do Score;
- Coverage;
- Confidence;
- Overall;
- limites das classificações internas.

## `report/css/site.css`

Único stylesheet estrutural do report site final.

Os HTMLs finais referenciam:

```html
<link rel="stylesheet" href="css/site.css">
```

Não há CSS final inline/embutido no `<head>` das páginas do report site.

## Por que não existem `report.html` e `remediation.html` na raiz

M11/M18 ainda podem construir HTML intermediário como parte do pipeline interno para preservar contratos existentes. Ao final de `run_audit`, o `report_site` materializa as páginas definitivas e remove esses intermediários da raiz.

O contrato público de saída é:

```text
report/index.html
report/remediation.html
```

## Metadado de report

A tabela `reports` aponta `file_path` para:

```text
report/index.html
```

Isso mantém o ponto de entrada reabrível a partir do banco.

## Seleção de dispositivo e artifacts

CLI default:

```text
mobile
```

Com `mobile`, artifacts de rendering/visual são produzidos apenas para Mobile. Com `desktop`, apenas Desktop. Com `both`, ambos.

Consequentemente, M7/IA trabalha somente sobre os snapshots selecionados.

## Segurança

Não devem ser persistidos em outputs:

- API key;
- Authorization header;
- senha;
- secret/token de credencial;
- body integral de requisição externa contendo segredo.

Dados exibidos em HTML passam por sanitização/redaction conforme o contrato vigente.

## Portabilidade

O report site usa caminhos relativos e pode ser aberto localmente. Para preservar links de screenshots/artifacts, mova o workspace inteiro, não somente a pasta `report/`.

## Fonte de verdade

Ordem de autoridade operacional:

```text
audit.db + artifacts
        ↓
report site
```

O HTML é descartável/regerável conceitualmente; nunca deve ser usado como única fonte para recalcular o score.
