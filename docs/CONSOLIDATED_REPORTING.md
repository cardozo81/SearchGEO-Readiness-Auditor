# Relatórios históricos e consolidados

## Objetivo

A funcionalidade de consolidação reúne indicadores já persistidos em múltiplas auditorias `AUD-*` e gera um snapshot HTML estático para análise histórica por domínio, período, dispositivo e URL.

Ela foi deliberadamente implementada fora do pipeline de auditoria.

## Garantias de arquitetura

- `AUD-*/audit.db` permanece a fonte de verdade;
- cada `audit.db` é aberto com SQLite `mode=ro` e `PRAGMA query_only=ON`;
- nenhuma API externa é chamada durante indexação, filtro, cálculo ou geração do relatório;
- o pipeline `searchgeo audit`, scoring, persistence, PageSpeed/CrUX, IA e Synthetic Apdex não dependem do consolidador;
- nenhum schema de `audit.db` é migrado ou alterado para suportar consolidação;
- falha do consolidador é `fail-open` em relação ao console de auditoria;
- o índice analítico pode ser apagado e reconstruído sem perda de evidência;
- relatórios `CONS-*` são snapshots derivados e não substituem os relatórios `AUD-*`.

## Fluxo

```text
AUD-*/audit.db (fonte oficial, read-only)
        |
        v
.searchgeo/consolidated-index.db (cache analítico reconstruível)
        |
        v
filtros + políticas de comparabilidade
        |
        v
consolidated/CONS-*/report.html + manifest.json
```

## Acesso pelo console

O entrypoint `searchgeo-console` mantém o console já existente e adiciona a opção:

```text
C. Histórico / relatórios consolidados [OFFLINE | sem APIs]
```

A opção não altera a configuração da auditoria. O fluxo solicita, de forma dependente:

1. domínio;
2. período (`AAAA-MM-DD`);
3. dispositivo;
4. filtro opcional de URL/caminho;
5. confirmação da geração.

Os dispositivos são preservados como séries separadas; selecionar todos não cria uma média Mobile + Desktop.

## Descoberta e índice analítico

A raiz configurada em `Raiz auditorias` é percorrida apenas para diretórios `AUD-*` que contenham `audit.db`.

O índice é gravado em:

```text
audits/.searchgeo/consolidated-index.db
```

O índice contém somente projeções necessárias para consulta histórica:

- metadados da auditoria;
- domínio;
- URLs;
- dispositivos;
- versões do auditor/ruleset/scoring;
- scores persistidos, coverage, confidence e consolidation status;
- Web Performance/Lighthouse/CrUX persistidos;
- Synthetic Apdex persistido;
- contagens/classificações de findings persistidos.

Ele não contém evidência exclusiva. Se o arquivo for removido, a próxima atualização reconstrói seu conteúdo lendo novamente os `audit.db`.

### Atualização incremental

Cada fonte possui fingerprint técnico baseado no arquivo `audit.db`. AUDs sem alteração são reutilizados no índice; AUDs novos/alterados são reindexados; entradas cujo diretório foi removido também são removidas do cache.

Um banco inválido, incompatível ou ilegível não interrompe a indexação dos demais. O problema é registrado no resultado de atualização e posteriormente no `manifest.json` quando aplicável.

## Elegibilidade

Somente auditorias com `status=COMPLETED` participam de uma consolidação.

Os filtros de domínio, período e dispositivo reduzem o universo elegível antes da leitura das séries de indicadores.

O período usa a data efetiva da auditoria na seguinte ordem:

```text
completed_at -> started_at -> created_at
```

Os limites inicial e final são inclusivos.

## Filtro por URL

Web Performance, Apdex e findings vinculados a páginas podem ser filtrados diretamente por URL.

Scores são atualmente persistidos em nível de auditoria/dispositivo/dimensão, não em nível de URL. Portanto, com filtro explícito de URL, um score audit-level só é usado quando o universo completo de URLs daquela auditoria está contido no conjunto selecionado.

Essa regra evita atribuir à URL filtrada um score calculado com páginas que ficaram fora do filtro. Quando a condição não é atendida, o score é omitido e a limitação é explicitada no relatório.

O consolidador não reexecuta o motor de scoring para fabricar um score por URL.

## Políticas estatísticas

### Princípios gerais

- dado ausente não vira zero;
- Mobile e Desktop permanecem separados;
- observações só são agregadas quando semanticamente comparáveis;
- versão metodológica incompatível é segregada, não misturada por média;
- séries usam somente pontos realmente observados; não existe interpolação de dias/períodos sem auditoria.

### Score GEO

Por `device + dimension` o relatório mostra, para a versão de scoring compatível mais recente:

- quantidade de observações válidas;
- valor inicial;
- valor atual;
- média;
- mediana;
- mínimo;
- máximo;
- variação absoluta;
- variação percentual;
- coverage média;
- distribuição de confidence;
- distribuição de consolidation status.

Se houver mais de uma `scoring_version`, os valores de versões diferentes não são combinados. O relatório informa a mudança metodológica e resume numericamente somente a versão mais recente observada no intervalo.

### Web Performance

São consolidados, quando persistidos:

- Performance score;
- Accessibility score;
- Best Practices score;
- SEO score;
- FCP lab;
- Speed Index lab;
- LCP lab;
- TBT lab;
- CLS lab;
- LCP p75 field;
- INP p75 field;
- CLS p75 field;
- distribuição de `cwv_assessment`;
- distribuição de `field_source / field_scope`.

Lab e field data continuam identificados separadamente. URL scope e origin scope não são presumidos equivalentes.

### Synthetic Apdex

Apdex só é agregado entre observações do mesmo dispositivo com `profile_id` e threshold T compatíveis.

Quando existem perfis/thresholds diferentes no período, o conjunto numérico usa o perfil/threshold mais recente e registra a limitação.

O Apdex agregado é ponderado pelo número de amostras válidas:

```text
sum(apdex_score * valid_samples) / sum(valid_samples)
```

Também são mostrados amostras válidas/inválidas, small groups, final groups e estatísticas de duração/percentis já persistidos.

### Findings

Findings não recalculam SCORE GEO. O consolidado os usa somente como estatística histórica:

- total de ocorrências;
- páginas afetadas;
- distribuição por severidade;
- distribuição por categoria.

## Relatório estático

Cada resultado novo é salvo em:

```text
audits/consolidated/CONS-YYYYMMDD-HHMMSS-mmm/
    report.html
    manifest.json
```

`report.html` é autocontido e não relê banco, não chama API e não recalcula dados ao ser aberto posteriormente.

O `manifest.json` registra:

- `cons_id`;
- versão do formato do consolidado;
- data/hora de geração;
- filtros;
- fingerprint da requisição;
- fingerprint do conjunto de fontes;
- AUDs utilizados;
- versões de auditor/ruleset;
- período efetivamente observado;
- quantidade de URLs;
- limitações;
- resultado da atualização do índice e AUDs ignorados.

## Evitar relatórios duplicados

Antes de criar um novo `CONS-*`, o sistema calcula uma fingerprint a partir de:

```text
versão do formato do relatório
+ filtros canônicos
+ conjunto/fingerprint dos AUDs elegíveis
```

Se já existir um `manifest.json` com a mesma fingerprint e o respectivo `report.html` estiver presente, o relatório existente é reutilizado.

Consequências:

- repetir exatamente os mesmos filtros sem mudança nos AUDs não cria duplicata;
- um novo AUD elegível altera a fingerprint e gera novo snapshot;
- alteração de filtro gera novo snapshot;
- mudança futura do formato do consolidado pode invalidar a reutilização de forma controlada.

## Diretórios derivados

```text
audits/.searchgeo/
```

contém cache reconstruível.

```text
audits/consolidated/
```

contém snapshots históricos gerados pelo usuário.

Nenhum desses diretórios deve ser considerado parte de um workspace `AUD-*`.

## Reversão segura da funcionalidade

A implementação foi isolada na branch/PR de consolidação. Para remover a feature após eventual merge:

1. reverter o PR/merge commit da feature;
2. o pipeline de auditoria volta ao estado anterior, pois não depende do índice;
3. opcionalmente remover `audits/.searchgeo/consolidated-index.db`;
4. opcionalmente arquivar/remover `audits/consolidated/`;
5. nenhum `AUD-*/audit.db` precisa ser restaurado ou migrado.

Não é necessário desfazer dados dentro dos AUDs porque a funcionalidade não grava neles.

## Critérios de segurança para merge

A branch não deve ser integrada em `main` sem verificar:

- testes atuais do projeto sem regressão;
- testes específicos da consolidação;
- hashes dos `audit.db` inalterados após indexação/geração;
- `searchgeo audit` sem diferença funcional causada pela feature;
- console funcionando quando o consolidado falha;
- nenhum import do pacote `consolidation` em `audit_runner.py`, scoring ou persistence;
- diff do PR restrito ao novo pacote, testes, documentação e adaptador de entrypoint;
- ausência de migration em banco de auditoria;
- ausência de chamadas de rede no pacote de consolidação.

Sem essa evidência, o PR deve permanecer sem merge.
