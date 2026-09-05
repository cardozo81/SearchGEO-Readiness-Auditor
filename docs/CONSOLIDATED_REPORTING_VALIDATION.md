# Validação e reversibilidade — relatórios consolidados

## Escopo da mudança

Branch:

```text
feature/consolidated-reporting
```

PR de integração:

```text
#67
```

A mudança é aditiva e isolada. O único arquivo runtime preexistente alterado é `src/searchgeo/console_entrypoint.py`, que instala o adapter do novo submenu antes de delegar ao mesmo `interactive_console.main()` existente.

Não há alteração em:

- `audit_runner.py`;
- `persistence.py`;
- `scoring.py` / `scoring_persistence.py`;
- acquisition/rendering;
- providers de IA;
- PageSpeed/CrUX;
- Synthetic Apdex;
- schemas dos `AUD-*/audit.db`.

## Fonte de verdade e escrita

A fonte de verdade permanece:

```text
AUD-*/audit.db
```

A leitura usa:

```text
SQLite mode=ro
PRAGMA query_only=ON
```

O pacote de consolidação só escreve em:

```text
.searchgeo/consolidated-index.db
consolidated/CONS-*/report.html
consolidated/CONS-*/manifest.json
```

O índice é derivado e reconstruível.

## Comparabilidade estatística implementada

### Score GEO

Score é persistido em nível de auditoria/dispositivo/dimensão. Por isso a consolidação não recalcula score por URL.

Uma série numérica de score é considerada comparável somente dentro da combinação mais recente de:

```text
scoring_version
+
fingerprint do conjunto completo de URLs da auditoria
```

Se houver mudança de `scoring_version` ou do universo de URLs, o relatório informa a limitação e não mistura os valores incompatíveis na mesma média/série resumida.

Quando o usuário aplica filtro explícito de URL, um score audit-level só pode entrar se o universo completo daquela auditoria estiver contido no filtro. Caso contrário o score é omitido, sem fabricar um recálculo parcial.

### Web Performance

Média/mediana/mínimo/máximo usam observações persistidas do período. Para representar `Inicial` e `Atual` em um conjunto de URLs, o consolidador usa a média transversal da observação válida mais antiga e mais recente de **cada URL**, evitando que a última linha de uma única URL represente todo o domínio.

Lab e field continuam separados por métrica. `field_source` e `field_scope` permanecem visíveis.

### Synthetic Apdex

Só são agregados profile e threshold T compatíveis. O Apdex consolidado do período é ponderado por amostras válidas.

Para duração/percentis, `Inicial` e `Atual` também usam a observação mais antiga/recente por URL.

### Findings

Findings são estatística histórica de ocorrência e não alteram/recalculam Score GEO.

## Dedupe de relatório

O dedupe exige igualdade de:

```text
report_format_version
+ filtros canônicos
+ conjunto/fingerprint dos AUDs elegíveis
```

Portanto:

- mesmos filtros + mesmas fontes: reutiliza o `CONS-*` existente;
- novo AUD elegível: novo snapshot;
- alteração de filtro: novo snapshot;
- mudança de formato: novo snapshot.

## Testes automatizados específicos

O workflow `.github/workflows/consolidated-reporting-ci.yml` é restrito à própria feature e executa:

1. instalação do pacote em CPython 3.13;
2. `compileall` do novo pacote e entrypoint alterado;
3. todos os testes `test_consolidation*.py`;
4. regressões existentes do console interativo/configuração.

Cobertura funcional específica inclui:

- geração read-only com hash dos `audit.db` antes/depois;
- dedupe de requisição idêntica;
- invalidação do dedupe por novo AUD elegível;
- proteção de score audit-level em filtro parcial de URL;
- segregação por `scoring_version`;
- segregação por universo de URLs;
- estado Web Performance calculado pela observação mais recente por URL;
- isolamento de `audit.db` inválido;
- filtro temporal inclusivo;
- delegação intacta das opções antigas do console;
- falha de consolidação `fail-open`.

## Gate de merge

O PR deve permanecer sem merge se qualquer condição abaixo não for comprovada:

- CI específico verde no HEAD final;
- branch baseada no `main` corrente ou revisada contra mudanças posteriores;
- diff sem alteração dos motores de auditoria/scoring/persistência;
- nenhum `AUD-*/audit.db` escrito pelos testes;
- sem chamadas de rede no pacote `consolidation`;
- integração do console preservando as escolhas preexistentes;
- revisão do diff final sem arquivo inesperado.

A existência de testes verdes reduz risco, mas não autoriza afirmar risco matematicamente zero. Se houver qualquer dúvida material sobre impacto, o PR deve permanecer draft/sem merge.

## Rollback

Se o PR for integrado e for necessário remover somente esta funcionalidade:

1. reverter o merge/squash do PR #67;
2. não executar qualquer migration em `AUD-*` — nenhuma existe;
3. opcionalmente excluir `.searchgeo/consolidated-index.db`;
4. opcionalmente arquivar/excluir `consolidated/CONS-*`;
5. nenhuma restauração de banco de auditoria é necessária.

Como o pipeline de auditoria não depende da feature, o rollback é restrito ao código/artefatos derivados do consolidado.
