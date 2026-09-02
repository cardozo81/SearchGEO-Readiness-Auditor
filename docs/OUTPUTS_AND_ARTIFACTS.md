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
   ├─ visual/
   │  └─ <PGE-ID>/
   │     ├─ desktop/
   │     │  └─ <SNP-ID>.png
   │     └─ mobile/
   │        └─ <SNP-ID>.png
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

A presença de um arquivo é condicionada à existência do conteúdo correspondente. Uma falha localizada pode gerar Evidence/estado técnico sem gerar determinado artifact. O workspace deve ser tratado como unidade portátil: `report.html`, `audit.db` e `artifacts/` devem permanecer juntos quando a auditoria for copiada.

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
- metadata do Report;
- universo de entrada multi-URL (`audit_input_urls` e `audit_input_summary`);
- observações concretas do DOM (`element_observations`);
- vínculo determinístico Finding → ElementObservation (`finding_element_observations`).

O schema é inicializado/evoluído pelos componentes de persistência da própria baseline. Não existe database server externo. As tabelas introduzidas no M14 são aditivas e não alteram a semântica dos registros históricos.

### Universo de entrada multi-URL

Quando a auditoria é iniciada em modo `URL_SET`, o SQLite preserva:

- ordem das URLs normalizadas e deduplicadas;
- quantidade bruta fornecida pelo operador;
- quantidade única efetivamente considerada;
- modo de entrada.

Esses dados permitem distinguir, por exemplo, `6 URLs fornecidas / 5 únicas` sem duplicar páginas no processamento.

## RAW HTTP artifacts

O M2 preserva body HTTP disponível em:

```text
artifacts/http/page-<PGE-ID>.response
```

Robots e sitemaps também podem ser preservados nessa pasta.

RAW representa aquisição HTTP antes do rendering JavaScript. Headers, status, redirects, network errors e timings ficam estruturados em Evidence/RuleExecution/SQLite; o `.response` preserva o body.

`robots.txt` e sitemap são recursos de domínio. No modo multi-URL eles não são replicados artificialmente uma vez por página.

## Rendered Desktop/Mobile

M3 grava DOM/HTML após Chromium:

```text
artifacts/rendered/<PGE-ID>/desktop/<SNP-ID>.html
artifacts/rendered/<PGE-ID>/mobile/<SNP-ID>.html
```

Desktop e Mobile usam snapshots e paths independentes. Um não deve sobrescrever o outro.

## Screenshots Desktop/Mobile

M14 acrescenta captura visual da viewport renderizada:

```text
artifacts/visual/<PGE-ID>/desktop/<SNP-ID>.png
artifacts/visual/<PGE-ID>/mobile/<SNP-ID>.png
```

Cada PNG é ligado ao `page_id`, `snapshot_id` e dispositivo corretos. O relatório referencia esses arquivos por caminho relativo, portanto não depende de CDN ou de upload externo para exibir a evidência visual.

A ausência de PNG por falha de rendering não deve gerar imagem fictícia. A limitação deve permanecer explícita no estado técnico/evidência.

## ElementObservation

M14 persiste observações de nós DOM realmente capturados. Entre os campos persistidos estão:

- `element_observation_id`;
- audit/page/snapshot/device;
- URL;
- selector quando determinável;
- tag, id e classes;
- `outer_html` limitado e sanitizado;
- trecho de texto limitado;
- bounding box quando o elemento está localizável na viewport;
- referência ao screenshot relacionado;
- timestamp.

O auditor não inventa selector. Quando não há selector determinístico, o valor permanece não determinado e o relatório deve explicar a limitação.

O vínculo Finding → ElementObservation só é criado quando uma associação concreta e não ambígua pode ser feita. Regras que representam estrutura global, como hierarquia de headings, podem permanecer sem um único elemento associado.

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

O M14 acrescenta `VISUAL_SNAPSHOT` como tipo de evidência para o screenshot. O artifact é material bruto/reaberto; Evidence é a ponte rastreável entre observação, RuleExecution e Finding.

## Semântica

`SemanticAssessment` e `EntityObservation` são persistidos no SQLite sem criar arquivos semânticos paralelos obrigatórios. Quando uma saída de IA influencia uma RuleExecution, a pipeline pode criar Evidence `AI_ANALYSIS` com provenance controlada.

O M14 não cria uma segunda chamada livre de IA apenas para preencher selectors, HTML observado ou referências. Esses dados devem vir de evidência real ou permanecer não determinados.

## Scores, actionability e recomendações

Scores, ScoreContributions, Remediation Groups e Recommendations são dados estruturados persistidos em SQLite. Eles são posteriormente projetados no HTML.

Actionability é uma projeção independente do scoring. Um resultado pode ser classificado como ação necessária, revisão recomendada, melhoria opcional, nenhuma ação ou ação não determinada sem alterar pesos, score ou coverage.

## `report.html`

Gravado na raiz do workspace:

```text
<AUD-ID>/report.html
```

A partir do M14 o template é `REPORT-GEO-003` e pode referenciar screenshots locais sob `artifacts/visual/`. O HTML continua sem CDN, fonte remota, backend ou internet obrigatória para leitura; para manter as imagens, copie o workspace inteiro e não apenas o arquivo isolado.

**`report.html` não é fonte primária dos dados.**

Se houver divergência durante diagnóstico técnico, use:

1. `audit.db`;
2. artifacts referenciados;
3. Evidence/RuleExecution persistidas;
4. ElementObservation e vínculos persistidos;
5. metadata versionada;
6. somente então o HTML como projeção de apresentação.

## Logs

A implementação atual usa `logging.basicConfig` no processo, com nível configurável. **Não existe writer que materialize `audit.log` dentro do workspace na Stable Local Baseline/M14.**

Se uma specification/arquitetura de referência mencionar `audit.log`, trate isso como objetivo não materializado, não como arquivo que o operador deve esperar encontrar.

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
  -> finding_element_observations (quando determinístico)
     -> ElementObservation
        -> selector / outer_html / bounding_box / visual artifact
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
| RAW/rendered/visual/extraction artifacts | evidência material/reprodutível |
| Evidence | provenance estruturada das observações |
| ElementObservation | evidência concreta de elemento DOM quando disponível |
| RuleExecution | resultado versionado da regra |
| `report.html` | projeção humana do estado persistido |
