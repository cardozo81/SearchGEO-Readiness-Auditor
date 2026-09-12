# Relatórios históricos e consolidados

## Objetivo

O consolidador reúne indicadores persistidos em auditorias `AUD-*` e gera um snapshot HTML estático para análise por domínio, período, dispositivo e URL. Ele é independente do pipeline de auditoria: não reexecuta crawl, regras, IA, scoring, PageSpeed, CrUX ou providers externos.

O formato materializado vigente é:

```text
CONS-4
```

`CONS-4` adiciona consolidação temporal de Apdex baseada em amostras brutas e possui fingerprint próprio. `CONS-3` permanece somente como contrato/base de renderização compatível para artefatos anteriores; um snapshot `CONS-3` já existente nunca é reescrito para virar `CONS-4`.

## Garantias de arquitetura

- `AUD-*/audit.db` permanece a fonte de verdade de cada auditoria;
- bancos fonte são abertos em modo somente leitura (`mode=ro` + `PRAGMA query_only=ON`);
- nenhum schema de `audit.db` é migrado pelo consolidador;
- `.rasai/consolidated-index.db` é cache derivado, descartável e reconstruível;
- a leitura temporal de amostras Apdex ocorre diretamente nos `AUD-*`, também somente leitura;
- falha do consolidador é independente do pipeline de auditoria;
- `CONS-*` não substitui `AUD-*`;
- séries metodologicamente incompatíveis nunca são fundidas silenciosamente;
- dados ausentes nunca são convertidos em zero.

```text
AUD-*/audit.db (fonte oficial, read-only)
        |\
        | +--> amostras Apdex brutas comparáveis
        |
        +----> .rasai/consolidated-index.db (cache reconstruível)
                    |
                    v
          filtros + comparabilidade
                    |
                    v
       consolidated/CONS-*/report.html
                     + manifest.json
```

## Elegibilidade e filtros

Somente auditorias concluídas participam. A data efetiva segue:

```text
completed_at -> started_at -> created_at
```

Os limites do período são inclusivos. Web Performance, Apdex e ocorrências page-level podem ser filtrados por URL. Readiness persistida em nível de auditoria/dispositivo não é recalculada para um subconjunto arbitrário de URLs; quando o universo original não está contido no filtro, o valor é omitido e a limitação é declarada.

## SARI-001 e SCORE-GEO-004

O índice público permanece **SARI-001 - Search & AI Readiness Index** e o motor vigente para novas auditorias permanece **SCORE-GEO-004**.

O consolidado não recalcula o Overall do período. Ele lê de cada `AUD-*` os valores já persistidos de Score, Coverage, Confidence, Consolidation, Critical Gates e `scoring_version`.

Séries de score exigem compatibilidade de versão metodológica e universo de URLs. `NOT_APPLICABLE`, ausência de evidência, `UNKNOWN` e `ERROR` não são tratados como zero.

## Comparabilidade histórica

O consolidado segmenta ou sinaliza, conforme o domínio:

- `scoring_version` e universo de URLs para readiness;
- dispositivo;
- URL para métricas page-level;
- metodologia lab/field e fonte/escopo para Web Performance;
- tipo de Apdex, task/KPM, perfil, thresholds, sessão/política de erros e pacing relevante;
- mix de dispositivos quando a série Experience usa `POPULATION`;
- versão do auditor/ruleset quando materialmente relevante.

Mudança material de contexto cria outra série em vez de contaminar a série anterior.

## Políticas estatísticas gerais

- não existe interpolação de datas sem auditoria;
- extremos não são descartados automaticamente;
- não há trimming, winsorization ou remoção por IQR/desvio-padrão apenas por distância da média;
- média, mediana, mínimo e máximo usam somente observações elegíveis/comparáveis;
- para métricas page-level, estado inicial/atual é resolvido por URL antes da agregação transversal, evitando que uma URL auditada mais vezes domine o domínio;
- percentis externos ou já agregados não são tratados como amostras brutas.

### Quantidade de auditorias

| Base | Interpretação |
|---|---|
| 1 AUD | **Snapshot**; não caracteriza tendência |
| 2 AUDs | **Comparação de dois pontos**; variação não equivale a tendência |
| 3+ AUDs comparáveis | **Série histórica descritiva**; não atribui causalidade |

## Web Performance

Permanecem separados por metodologia:

- Lighthouse Performance/Acessibilidade/Boas práticas/SEO;
- FCP, Speed Index, LCP, TBT e CLS de laboratório;
- LCP p75, INP p75 e CLS p75 de campo;
- Core Web Vitals assessment;
- fonte e escopo do dado de campo.

Lab e field data não são fundidos como se fossem a mesma população.

## Apdex temporal

Synthetic Navigation Apdex e Synthetic User Experience Apdex permanecem domínios distintos.

Para cada série comparável, o **Apdex do período** é recalculado pelas contagens persistidas:

```text
Apdex_periodo =
  (Σ Satisfied + 0,5 × Σ Tolerating)
  / Σ amostras_válidas
```

Isso é equivalente a uma ponderação correta pelo número de amostras quando a metodologia é a mesma, mas evita tratar cada execução como se tivesse o mesmo tamanho de população.

Percentis não são aditivos. Por isso `p95_periodo` não é média dos `p95` de cada execução. `TEMPORAL-APDEX-001` lê as amostras brutas dos `AUD-*` comparáveis e recalcula no pool do período:

- média;
- mediana/p50;
- p75, p90, p95 e p99;
- mínimo/máximo;
- desvio-padrão;
- coeficiente de variação.

A série é **por URL e contexto**. URLs diferentes não são juntadas em um único pool de tempos. Navigation preserva `T/4T`; Experience preserva KPM, thresholds, sessão, política de erros e população efetiva.

Grupos pequenos continuam identificados. Mais amostras não tornam automaticamente a evidência temporalmente representativa; para monitoramento é preferível distribuir a carga em N janelas agendadas ao longo do período.

Detalhes: [`CONSOLIDATED_REPORTING_TEMPORAL.md`](CONSOLIDATED_REPORTING_TEMPORAL.md), [`SYNTHETIC_APDEX.md`](SYNTHETIC_APDEX.md) e [`SYNTHETIC_USER_EXPERIENCE_APDEX.md`](SYNTHETIC_USER_EXPERIENCE_APDEX.md).

## Ocorrências

O consolidado pode exibir volume, severidade, categoria, páginas afetadas e evolução. O volume deve ser interpretado junto ao universo auditado; mais páginas podem gerar mais findings sem representar piora proporcional. Findings não recalculam SARI/SCORE-GEO.

## Confiabilidade analítica

O consolidado não cria outro score de confiabilidade. Ele apresenta, conforme disponível:

- fidelidade à fonte;
- comparabilidade metodológica;
- suficiência da base histórica;
- Coverage/Confidence persistidas;
- robustez/amostragem de Apdex;
- status de Consolidation persistido;
- limitações explícitas de cada série.

## Relação com RASAi Monitor

`CONS-*` e RASAi Monitor possuem papéis diferentes:

- consolidado: exploração histórica e estatística descritiva;
- `rasai monitor compare`: baseline → current;
- `rasai monitor gate`: release gate determinístico;
- `rasai monitor impact`: associação temporal entre regressões e outcomes, sem causalidade.

Nenhuma dessas superfícies altera o `audit.db` fonte.

## Relação com Search & AI Observability

Dados pós-auditoria como Search Console, URL Inspection, CrUX History e imports observacionais ficam em `observability.db`/artifacts próprios. Eles não são copiados para o consolidado como se fossem evidência original do AUD nem entram automaticamente em SARI/SCORE-GEO.

## Agendamento e SaaS

O scheduler/control plane já é suficiente para gerar N execuções independentes em horários distintos. Não é necessária migração de schema SaaS para `TEMPORAL-APDEX-001`.

Para uma campanha temporal, os jobs devem manter o contexto metodológico comparável e variar principalmente a janela de execução. O `CONS-*` usa depois os `AUD-*` materializados no período.

Em uma futura execução distribuída por hubs/regiões, região/origem de execução deve integrar a identidade de comparabilidade quando essa proveniência estiver persistida de forma estável. Até lá, populações de origens diferentes não devem ser fundidas silenciosamente.

## Snapshot, fingerprint e dedupe

`CONS-4` possui fingerprint próprio, derivado de:

```text
report_format_version
+ TEMPORAL-APDEX-001
+ filtros canônicos
+ fingerprint do conjunto de AUDs
```

Regras:

- mesma requisição + mesmas fontes + mesmo contrato: reutiliza `CONS-4`;
- novo AUD, novo filtro ou novo contrato: novo snapshot;
- se o renderizador base encontrar um `CONS-3` reutilizável, ele é **copiado** para um novo `CONS-4` antes da evolução; o `CONS-3` permanece byte a byte intacto.

## Saída estática

```text
audits/consolidated/CONS-*/
    report.html
    manifest.json
```

O manifest registra filtros, fingerprints, fontes, políticas de agregação, contrato temporal e limitações. As amostras brutas não são duplicadas no manifest. O HTML é estático e não relê bancos nem chama APIs ao ser aberto.

## Reversão e segurança

A feature é derivada. Remover `.rasai/consolidated-index.db` e/ou `consolidated/CONS-*` não remove evidência dos `AUD-*`; tudo pode ser reconstruído a partir das fontes imutáveis.

## Gate de integração

Mudanças do consolidador devem validar, no mínimo:

- testes específicos e regressões de consolidação;
- hashes dos `audit.db` inalterados;
- segregação de contextos incompatíveis;
- percentis do período calculados do pool bruto quando aplicável;
- preservação de `CONS-3` legado ao criar `CONS-4`;
- HTML reabrível, estático e com demais seções preservadas;
- manifest/fingerprint coerentes;
- ausência de dependência do audit runner em consolidação/monitoring/observability.

Veja também [`CONSOLIDATED_REPORTING_VALIDATION.md`](CONSOLIDATED_REPORTING_VALIDATION.md), [`CONSOLIDATED_REPORTING_TEMPORAL.md`](CONSOLIDATED_REPORTING_TEMPORAL.md), [`SCORING_GUIDE.md`](SCORING_GUIDE.md) e [`REPORT_GUIDE.md`](REPORT_GUIDE.md).
