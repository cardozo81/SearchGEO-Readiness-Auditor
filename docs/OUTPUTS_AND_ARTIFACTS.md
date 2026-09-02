# Outputs e Artifacts

Cada execução cria um workspace exclusivo:

```text
<audits-root>/<AUD-ID>/
```

Default:

```text
audits/<AUD-ID>/
```

## Estrutura materializada

```text
<AUD-ID>/
├─ audit.db
├─ report.html
└─ artifacts/
   ├─ http/
   │  ├─ page-<PGE-ID>.response
   │  ├─ robots.response                 # quando body disponível
   │  └─ sitemap-<digest>.response       # quando body disponível
   ├─ rendered/
   │  └─ <PGE-ID>/
   │     ├─ desktop/
   │     │  └─ <SNP-ID>.html
   │     └─ mobile/
   │        └─ <SNP-ID>.html
   └─ extraction/
      └─ <PGE-ID>/
         ├─ desktop/
         │  └─ <SNP-ID>/
         │     ├─ main_content.txt       # se houver conteúdo
         │     └─ structured_data.json   # se houver blocos JSON-LD
         └─ mobile/
            └─ <SNP-ID>/
               ├─ main_content.txt
               └─ structured_data.json
```

A presença de um arquivo é condicionada à existência do conteúdo correspondente. Uma falha localizada pode gerar Evidence/estado técnico sem gerar determinado artifact.

## `audit.db`

SQLite embarcado é a principal persistência estruturada. Contém, conforme os marcos executados:

- Audit e AuditTarget;
- Page;
- PageSnapshot Desktop/Mobile;
- Evidence;
- RuleExecution;
- Finding;
- dados semânticos (`SemanticAssessment`, `EntityObservation`);
- Score e ScoreContribution;
- RemediationGroup e Recommendation;
- metadata do Report.

O schema é inicializado/evoluído pelos componentes de persistência da própria baseline. Não existe database server externo.

## RAW HTTP artifacts

O M2 preserva body HTTP disponível em:

```text
artifacts/http/page-<PGE-ID>.response
```

Robots e sitemaps também podem ser preservados nessa pasta.

RAW representa aquisição HTTP antes do rendering JavaScript. Headers, status, redirects, network errors e timings ficam estruturados em Evidence/RuleExecution/SQLite; o `.response` preserva o body.

## Rendered Desktop/Mobile

M3 grava DOM/HTML após Chromium:

```text
artifacts/rendered/<PGE-ID>/desktop/<SNP-ID>.html
artifacts/rendered/<PGE-ID>/mobile/<SNP-ID>.html
```

Desktop e Mobile usam snapshots e paths independentes. Um não deve sobrescrever o outro.

## Extração

M4 prioriza RENDERED DOM e usa RAW como fallback controlado quando necessário.

### Conteúdo principal

```text
artifacts/extraction/<PGE-ID>/<device>/<SNP-ID>/main_content.txt
```

### Dados Estruturados

```text
artifacts/extraction/<PGE-ID>/<device>/<SNP-ID>/structured_data.json
```

O arquivo de Dados Estruturados preserva blocos JSON-LD, incluindo raw, parsed, tipos e `parse_error` quando aplicável; conteúdo inválido não é silenciosamente descartado.

## Evidence

Evidence é entidade persistida em `audit.db`, não um diretório independente. Cada registro contém:

- ID `EV-GEO-*`;
- audit/page/snapshot/device quando aplicável;
- `evidence_type`;
- source;
- observed value;
- optional `artifact_reference`;
- timestamp.

O artifact é material bruto/reaberto; Evidence é a ponte rastreável entre observação, RuleExecution e Finding.

## Semântica

`SemanticAssessment` e `EntityObservation` são persistidos no SQLite sem criar arquivos semânticos paralelos obrigatórios. Quando uma saída de IA influencia uma RuleExecution, a pipeline pode criar Evidence `AI_ANALYSIS` com provenance controlada.

## Scores e recomendações

Scores, ScoreContributions, Remediation Groups e Recommendations são dados estruturados persistidos em SQLite. Eles são posteriormente projetados no HTML.

## `report.html`

Gravado na raiz do workspace:

```text
<AUD-ID>/report.html
```

É HTML5 autocontido, sem CDN, fonte remota, backend ou internet obrigatória para leitura.

**`report.html` não é fonte primária dos dados.**

Se houver divergência durante diagnóstico técnico, use:

1. `audit.db`;
2. artifacts referenciados;
3. Evidence/RuleExecution persistidas;
4. metadata versionada;
5. somente então o HTML como projeção de apresentação.

## Logs

A implementação atual usa `logging.basicConfig` no processo, com nível configurável. **Não existe writer que materialize `audit.log` dentro do workspace na Stable Local Baseline.**

Se uma specification/arquitetura de referência mencionar `audit.log`, trate isso como objetivo não materializado nesta baseline, não como arquivo que o operador deve esperar encontrar.

## Rastreabilidade prática

Para investigar um finding:

```text
Finding
  -> rule_execution_id
     -> RuleExecution
        -> evidence_ids
           -> Evidence
              -> artifact_reference (quando houver)
                 -> arquivo sob artifacts/
```

Para score:

```text
Score
  -> ScoreContribution
     -> rule_execution_id
        -> RuleExecution + rule_version
```

## Fonte primária versus projeções

| Item | Papel |
|---|---|
| `audit.db` | fonte primária estruturada |
| RAW/rendered/extraction artifacts | evidência material/reprodutível |
| Evidence | provenance estruturada das observações |
| RuleExecution | resultado versionado da regra |
| `report.html` | projeção humana do estado persistido |
