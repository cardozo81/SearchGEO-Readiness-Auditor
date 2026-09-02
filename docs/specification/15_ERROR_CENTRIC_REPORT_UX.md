# M15 — Error-Centric Report + Report UX

**Status:** APPROVED EVOLUTION  
**Baseline de entrada:** M14 integrado em `main`  
**Contratos preservados:** `SCORE-GEO-001`, `REPORT-GEO-003`

## 1. Objetivo

Melhorar a capacidade humana de navegar, interpretar e priorizar uma auditoria multi-URL sem alterar findings, scoring, coverage, confidence ou consolidation já persistidos.

M15 adiciona uma segunda projeção HTML, orientada a problema, e melhora a apresentação do relatório orientado a página.

## 2. Dois ângulos complementares

O workspace deve conter, no mesmo nível:

```text
<AUD-ID>/
├─ report.html
└─ remediation.html
```

`report.html` continua sendo a visão principal orientada a página.

`remediation.html` é uma projeção derivada orientada a regra/problema e usa o contrato:

```text
REMEDIATION-GEO-001
```

O segundo HTML não recalcula regra, finding ou score.

## 3. Agrupamento por problema

`remediation.html` deve agrupar findings compatíveis por:

- escopo (`GLOBAL` ou `PAGE`);
- `rule_id`;
- actionability.

Para cada grupo deve mostrar, quando disponível:

- título do problema;
- regra;
- actionability;
- quantidade de páginas afetadas;
- paths afetados;
- device por ocorrência;
- resultado bruto;
- prioridade;
- selector quando determinável;
- orientação de remediação;
- critério de aceite;
- referências técnicas.

Um mesmo problema presente em várias páginas deve ser apresentado uma vez como grupo, com suas ocorrências listadas.

## 4. Global versus pontual

O relatório transversal deve separar visualmente:

- **Problemas globais:** findings sem `page_id`, associados ao domínio/recurso global;
- **Problemas por página:** findings associados a uma ou mais páginas concretas.

A quantidade de páginas afetadas deve ser explícita para permitir identificar recorrência.

Não promover um finding de página a problema global apenas porque se repete em várias páginas.

## 5. Navegação do `report.html`

Em desktop, deve existir menu lateral fixo durante scroll vertical.

O menu deve:

- listar as páginas auditadas;
- ocultar visualmente scheme e domínio;
- mostrar somente path e query quando existir;
- limitar visualmente paths longos com ellipsis;
- manter o destino real do anchor;
- incluir acesso ao guia do Score GEO;
- incluir acesso a `remediation.html`.

Em viewport estreita, a navegação deve deixar de ocupar uma coluna lateral fixa e passar para apresentação compacta no topo.

## 6. Tipografia e layout

O relatório deve evitar quebra arbitrária de tokens como:

- `NÃO DETERMINADO`;
- `INDISPONÍVEL`;
- valores de score;
- estados de consolidação quando houver espaço de layout alternativo.

Os grids de score devem priorizar colunas adequadas em desktop e empilhamento em viewport estreita.

Requisitos:

- hierarquia tipográfica consistente;
- cards e métricas alinhados;
- `min-width: 0` onde necessário;
- quebra de URLs/HTML/JSON controlada;
- labels e valores curtos sem `word-break` agressivo;
- layout print sem menu lateral.

## 7. Guia das dimensões do Score GEO

`report.html` deve conter seção de referência para as dez dimensões oficiais de `SCORE-GEO-001`:

1. Acessibilidade Técnica;
2. Capacidade de Indexação;
3. Extração de Conteúdo;
4. Estrutura Semântica;
5. Clareza de Entidades;
6. Dados Estruturados;
7. Capacidade de Resposta;
8. Preparação para Citação;
9. Evidências e Confiabilidade;
10. Cobertura de Intenções.

Para cada dimensão, mostrar:

- o que ela mede;
- como melhorar a evidência/condição avaliada;
- estado observado por Desktop/Mobile quando score estiver persistido;
- links técnicos oficiais quando existir referência verificada para regras representativas da dimensão.

Não inventar referência externa para heurísticas sem fonte normativa específica.

## 8. Interpretação no fim do relatório

O fim de `report.html` deve explicar de forma objetiva:

- Score;
- Coverage;
- Confidence;
- Consolidation;
- Actionability;
- Desktop versus Mobile;
- impacto da ausência de IA.

Deve permanecer explícito que:

```text
Score 0.0 calculado != score não calculado
Coverage != Score
UNKNOWN != FAIL
ERROR != FAIL
NOT_APPLICABLE != FAIL
```

## 9. Portabilidade

`report.html` e `remediation.html` devem usar links relativos entre si.

O workspace continua sendo a unidade portátil; nenhum dos dois relatórios deve exigir backend, CDN ou fonte remota para leitura.

## 10. Documentação de execução multi-URL

A documentação operacional deve conter exemplos genéricos para:

- múltiplas URLs declaradas diretamente no comando;
- carga por arquivo `--urls-file`.

Exemplos não devem depender de domínio corporativo real usado em smoke test.

## 11. Invariantes

M15 não altera:

- Business Rules;
- fatores/weights;
- scoring groups;
- fórmula de Score;
- Coverage;
- Confidence;
- Consolidation;
- actionability M14;
- evidências persistidas;
- política de IA.

Os dois HTMLs são projeções do mesmo estado persistido.

## 12. Aceite mínimo

1. `report.html` continua sendo gerado.
2. `remediation.html` é gerado no mesmo diretório.
3. regra repetida em duas páginas aparece como um grupo transversal com duas páginas afetadas.
4. finding global aparece na seção global e não é atribuído artificialmente a página.
5. menu do `report.html` mostra paths, não domínio.
6. paths longos usam truncamento visual.
7. Score GEO possui guia das dez dimensões.
8. interpretação final diferencia Score/Coverage/Confidence/Consolidation/Actionability.
9. viewport estreita não mantém sidebar fixa ocupando a lateral.
10. suíte de regressão permanece verde.
