# Validação e reversibilidade - relatórios consolidados

## Estado atual

O relatório consolidado faz parte do baseline de desenvolvimento em `main`.

Formato materializado vigente:

```text
CONS-4
```

Contrato temporal associado:

```text
TEMPORAL-APDEX-001
```

`CONS-3` permanece como formato/base anterior. Ele pode ser lido/reutilizado pelo renderizador base, mas não deve ser reescrito em lugar para adquirir semântica `CONS-4`.

## Fonte de verdade e escrita

As fontes são os `AUD-*/audit.db`, abertas em modo somente leitura (`SQLite mode=ro` e `PRAGMA query_only=ON`). A consolidação não recalcula auditorias, não migra schema e não grava nos bancos fonte.

Artefatos derivados:

```text
.rasai/consolidated-index.db
consolidated/CONS-*/report.html
consolidated/CONS-*/manifest.json
```

O índice e os snapshots consolidados são reconstruíveis.

## Contrato comportamental CONS-4

- SARI mostra pontuação, Coverage, Confidence e estado de Consolidation persistidos;
- score parcial não é apresentado como SARI consolidado;
- séries de readiness exigem `scoring_version` e universo de URLs comparáveis;
- filtro parcial de URL não reutiliza score calculado sobre páginas excluídas;
- Lighthouse/lab e Core Web Vitals/field continuam separados;
- Navigation e User Experience Apdex continuam domínios separados;
- Apdex do período usa soma de Satisfied/Tolerating/Frustrated sobre amostras válidas comparáveis;
- p50/p75/p90/p95/p99, média, desvio-padrão e CV do período usam o pool bruto por URL/contexto, nunca média de percentis individuais;
- grupos `small_group` continuam explicitamente identificados;
- findings permanecem contextualizados pelo universo auditado;
- dado ausente não vira zero;
- extremos não são eliminados automaticamente;
- mudanças materiais de método criam fronteiras de comparabilidade;
- `CONS-3` legado não é mutado ao materializar `CONS-4`.

## Comparabilidade do Apdex

### Synthetic Navigation Apdex

A série deve preservar, no mínimo:

```text
URL
+ device
+ task
+ profile
+ T / 4T
+ pacing relevante
```

### Synthetic User Experience Apdex

A série deve preservar, no mínimo:

```text
URL
+ device/POPULATION
+ task
+ profile
+ KPM
+ Satisfied/Frustrated thresholds
+ session mode
+ errors_affect_apdex/error scope
+ pacing/settle
+ device mix para POPULATION
```

Contextos incompatíveis não podem entrar no mesmo denominador nem no mesmo pool de durações/KPM.

## Estatística

### Apdex do período

```text
Apdex = (ΣSatisfied + 0,5 × ΣTolerating) / ΣValid
```

Se as contagens S/T/F persistidas não fecharem com `valid_samples`, o denominador persistido é preservado e a limitação deve aparecer no output.

### Distribuição temporal

Amostras válidas com duração/KPM numérica formam o pool usado para:

- média;
- mediana/p50;
- p75/p90/p95/p99;
- mínimo/máximo;
- desvio-padrão populacional;
- coeficiente de variação.

Amostra válida sem valor temporal continua no Apdex, mas fica fora da distribuição; a diferença deve ser declarada.

### Demais métricas

Readiness, Web Performance, findings, estados categóricos e dados externos mantêm suas políticas específicas. O consolidado não aplica uma média universal a todos os tipos de indicador.

## Integridade do snapshot e dedupe

O fingerprint `CONS-4` depende de:

```text
CONS-4
+ TEMPORAL-APDEX-001
+ filtros canônicos
+ source_fingerprint dos AUDs elegíveis
```

Comportamento esperado:

- mesma requisição + mesmas fontes: reutiliza o mesmo `CONS-4`;
- novo AUD/filtro/contrato: novo fingerprint;
- se o gerador base retornar um `CONS-3` reutilizado, o materializador cria outro diretório `CONS-*`, copia HTML/manifest e só então aplica `CONS-4`;
- hashes/bytes do `CONS-3` original permanecem iguais;
- `request_fingerprint`, `report_format_version`, `cons_id` e `generated_at` do novo snapshot permanecem coerentes;
- o manifest não duplica as amostras brutas.

## Gates automatizados

Workflow principal:

```text
.github/workflows/consolidated-reporting-ci.yml
```

O gate deve cobrir:

- compile da superfície de consolidação;
- geração read-only e hash dos `audit.db` inalterado;
- dedupe e invalidação por novo AUD/filtro/contrato;
- segregação de método/universo de URLs;
- Snapshot com N=1 sem falsa tendência;
- série histórica apenas quando comparável;
- Apdex calculado pelas contagens persistidas;
- percentis recalculados do pool bruto;
- separação de thresholds incompatíveis;
- Experience `POPULATION` baseada na união das amostras elegíveis;
- preservação byte a byte de `CONS-3` reutilizado ao materializar `CONS-4`;
- findings normalizados/contextualizados;
- HTML/manifest com metodologia e limitações;
- regressões de console/configuração previstas pelo workflow.

## Testes pontuais mínimos

1. dois AUDs Navigation com durações conhecidas e quantidades diferentes de S/T/F;
2. confirmar Apdex do período por contagens e p95 pelo pool bruto;
3. alterar `T` em um AUD e confirmar duas séries;
4. repetir para Experience/`POPULATION`;
5. calcular hash dos `audit.db` antes/depois;
6. partir de um `CONS-3` existente e confirmar criação de outro snapshot `CONS-4` sem alterar bytes do legado;
7. repetir a mesma solicitação e confirmar reuse do `CONS-4`;
8. conferir que seções não relacionadas do HTML permanecem presentes;
9. validar `manifest.json` e ausência de raw samples completos.

## Smoke humano

Quando necessário validar visualmente no ambiente local:

1. atualizar checkout de `main`;
2. gerar consolidado com 1 AUD e confirmar **Snapshot**;
3. gerar com 2 AUDs comparáveis e confirmar comparação sem narrativa de tendência;
4. gerar com 3+ AUDs e confirmar série histórica descritiva;
5. validar seção Apdex por URL/contexto, p95 e amostras válidas;
6. conferir SARI/Coverage/Confidence contra um `audit.db` fonte;
7. testar pesquisa/paginação das auditorias consideradas;
8. repetir filtros e confirmar dedupe `CONS-4`;
9. comparar hashes dos `audit.db` antes/depois;
10. abrir o HTML com o console fechado e confirmar funcionamento estático.

## SaaS/control plane

Nenhuma migração de schema é necessária para esta evolução. Scheduling já permite distribuir N execuções pelo período. A consolidação usa os `AUD-*` resultantes.

Quando o produto executar medições por hubs/regiões distintas, a origem/região deverá entrar no contrato de comparabilidade assim que essa proveniência existir de forma persistida.

## Reversibilidade

O consolidado é derivado. Reversão não exige migração dos `AUD-*`: cache e `CONS-*` podem ser removidos e reconstruídos.

Veja também [`CONSOLIDATED_REPORTING.md`](CONSOLIDATED_REPORTING.md), [`CONSOLIDATED_REPORTING_TEMPORAL.md`](CONSOLIDATED_REPORTING_TEMPORAL.md), [`REPORT_GUIDE.md`](REPORT_GUIDE.md), [`SCORING_GUIDE.md`](SCORING_GUIDE.md) e [`SYNTHETIC_APDEX.md`](SYNTHETIC_APDEX.md).
