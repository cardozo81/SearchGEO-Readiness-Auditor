# REPORT_GUIDE.md

Guia de leitura do report site do SearchGEO Readiness Auditor.

## Ponto de entrada

Abra:

```text
<audits-root>/<AUD-ID>/report/index.html
```

Não é necessário servidor web. Os arquivos usam links relativos e um CSS compartilhado.

## Estrutura

```text
report/
├─ index.html
├─ mobile.html             # quando Mobile foi auditado
├─ desktop.html            # quando Desktop foi auditado
├─ remediation.html
├─ content-suggestions.html
├─ ai-usage.html
├─ references.html
└─ css/
   └─ site.css
```

O menu é comum às páginas existentes naquela auditoria.

## Por que o relatório foi separado

Cada página responde a um domínio diferente:

| Página | Domínio |
|---|---|
| `index.html` | visão executiva, Overall, Coverage, Confidence e dimensões |
| `mobile.html` | evidência, findings e semântica do contexto Mobile |
| `desktop.html` | evidência, findings e semântica do contexto Desktop |
| `remediation.html` | causa raiz, prioridade, alvo de correção, aceite e revalidação |
| `content-suggestions.html` | sugestões textuais M20 opcionais e revisão JSON-LD por página/device |
| `ai-usage.html` | telemetria operacional M18/M20, separada por finalidade |
| `references.html` | fontes oficiais, natureza das regras e fórmulas do auditor |

A separação evita navegação excessivamente longa e mistura entre falha operacional da IA, sugestões advisory e qualidade do website.

## `index.html`

É o dashboard executivo. Deve ser lido nesta ordem:

1. dispositivo efetivamente auditado;
2. Readiness/Overall quando consolidado;
3. Coverage;
4. Confidence;
5. Consolidation;
6. dimensões;
7. findings/remediações quando existirem.

## Score / Readiness

O Score representa somente as regras efetivamente avaliadas que participam do cálculo.

Baseline:

```text
PASS    = 1,00
WARNING = 0,50 por padrão
FAIL    = 0,00
```

`UNKNOWN`, `ERROR` e `NOT_APPLICABLE` não são convertidos em `FAIL`.

As faixas visuais `Excelente / Alta / Moderada / Baixa / Crítica` são classificação interna do SearchGEO. Não são thresholds oficiais de Google, OpenAI ou outro mantenedor.

## Coverage

Coverage responde:

> quanto do universo aplicável realmente foi avaliado?

```text
evaluated applicable weight / total applicable weight
```

Coverage baixa significa **análise incompleta**, não qualidade baixa do site.

Exemplo:

```text
Score:      90/100
Coverage:   45%
Confidence: LOW
```

A leitura correta não é “site excelente”. A leitura correta é: a parte avaliada teve resultado alto, porém menos da metade do universo aplicável foi suficientemente avaliada e a conclusão é fraca.

## Confidence

Confidence responde:

> quão forte é a conclusão do auditor com as evidências disponíveis?

No SCORE-GEO-002 atual ela considera principalmente Coverage, completude de evidência e erros de execução.

**Confidence LOW não significa que o texto do website é ruim, não confiável ou não aderente a GEO.**

Ela significa que o auditor não possui base suficiente para sustentar uma conclusão forte. O conteúdo do site é avaliado por RuleExecutions, findings e Score; Confidence qualifica a conclusão.

Também não deve ser confundida com o campo de confidence devolvido por um provider de IA em uma avaliação semântica individual ou com a confiança de uma sugestão M20.

## Consolidation

Estados:

```text
CONSOLIDATED
PARTIAL
NOT_CONSOLIDATED
NOT_APPLICABLE
```

Uma dimensão `NOT_APPLICABLE` legítima não recebe 0 nem 100 e fica fora do Overall.

Uma dimensão aplicável `NOT_CONSOLIDATED` pode impedir publicação de um Overall.

## Mobile e Desktop

Quando `--device-context mobile`:

- existe `mobile.html`;
- `desktop.html` não é gerado;
- o report não apresenta Desktop como se tivesse sido auditado.

Quando `desktop`, vale o inverso.

Quando `both`, existem as duas páginas e a comparação entre contextos pode ser interpretada.

Diferença Mobile × Desktop não é automaticamente defeito. A regra BR-GEO-052 distingue diferença material de falha.

M20 trabalha sobre os mesmos snapshots existentes, portanto não gera chamada/sugestão para device não selecionado.

## Página por dispositivo

`mobile.html` e `desktop.html` apresentam:

- scorecard do dispositivo;
- dimensões;
- páginas/URLs auditadas;
- HTTP/final URL;
- snapshot visual quando disponível;
- findings aplicáveis ao dispositivo;
- avaliações semânticas não aprovadas.

Detalhes extensos ficam recolhidos em `details`, reduzindo poluição visual sem remover rastreabilidade.

## Remediações

`remediation.html` organiza por problema/causa, não por tamanho do crawl.

Quando M16/M17 conseguiu materializar a causa, a ocorrência pode exibir:

- causa precisa;
- reason code;
- escopo;
- selector observado;
- alvo técnico;
- localização esperada;
- diagnostic confidence;
- mudança recomendada;
- observado versus esperado;
- exemplo pós-correção;
- decisão humana;
- critérios de aceite;
- revalidação.

Uma condição `UNKNOWN`/evidência insuficiente não deve ser transformada artificialmente em ordem de alteração do site.

`remediation.html` contém link para a página M20 quando o usuário quiser revisar propostas textuais/JSON-LD separadamente.

## Conteúdo e JSON-LD

`content-suggestions.html` é advisory e não participa do score.

### Sugestões textuais

Quando M20 textual está desabilitado, a página declara explicitamente o estado e não apresenta conteúdo como se tivesse sido gerado por IA.

Quando habilitado e houver findings elegíveis/evidência suficiente, cada proposta pode mostrar:

- URL/device;
- `rule_id`/finding;
- objetivo;
- local sugerido;
- texto exato proposto;
- evidence IDs;
- provider/model;
- confidence da sugestão;
- aviso de revisão humana obrigatória.

`Confidence LOW` do auditor, sozinha, nunca é gatilho da seção.

A proposta não é aplicada automaticamente e não altera Score, Coverage, Confidence ou Finding.

### JSON-LD ausente

Quando o snapshot não possui JSON-LD persistido, a página pode exibir um baseline conservador `WebPage`, por exemplo:

```json
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "url": "https://example.com/pagina",
  "inLanguage": "pt-BR",
  "name": "Título observado",
  "description": "Description observada"
}
```

Somente valores persistidos/observados são usados. Campos inexistentes devem ser omitidos; propriedades específicas não devem ser inventadas.

### JSON-LD existente

Quando markup já existe, o report não o substitui integralmente. Pode apontar:

- parse errors;
- blocos idênticos duplicados;
- ausência de `@context` no documento/graph;
- nós sem `@type`;
- propriedades genéricas ausentes de um `WebPage` quando o valor já é conhecido;
- necessidade de conferir requisitos/recomendações do tipo específico.

JSON-LD é reforço opcional. Não existe markup especial GEO/AEO obrigatório e markup correto não garante rich result.

## Uso de IA

`ai-usage.html` é operacional e separa finalidades.

### M18 — análise semântica

Pode exibir:

- IA habilitada ou não;
- estratégia;
- provider/model efetivo;
- status da sessão;
- cadeia inicial;
- chamadas;
- tokens;
- custo estimado;
- duração;
- erro sanitizado.

### M20 — remediação textual

Pode exibir:

- se M20 estava habilitado;
- status M20;
- tentativas por URL/device;
- provider/model;
- tokens;
- custo estimado;
- duração;
- erro sanitizado.

Falha, quota, timeout ou provider não configurado **não é finding GEO do website**.

`ESTIMATED_COST` é estimativa local, não invoice.

## Referências e metodologia

`references.html` explica:

- fontes primárias oficiais;
- natureza `OFFICIAL`, `STANDARD`, `HEURISTIC` ou baseline interna das BR-GEO;
- fórmula do Score;
- Coverage;
- Confidence;
- Overall;
- limites das classificações internas.

A página inclui o guia oficial do Google de 2026 sobre recursos generativos. O posicionamento adotado pelo SearchGEO é compatível com esse material: práticas fundamentais de SEO continuam relevantes, não há markup GEO/AEO especial obrigatório, nem necessidade de reescrever conteúdo apenas para IA.

Para JSON-LD, `content-suggestions.html` também aponta Google General Structured Data Guidelines e Schema.org. Validação de rich result deve usar documentação específica da feature/tipo.

## Cores

Cores indicam mensagem, não decoração:

- verde: estado positivo/evidência suficiente;
- âmbar: atenção, parcialidade ou confiança reduzida;
- vermelho: problema/ação de alta gravidade;
- azul: informação contextual;
- cinza: indisponível/não determinado.

Cor nunca substitui o texto do estado.

## CSS

Todos os HTMLs finais referenciam:

```text
css/site.css
```

Não existe CSS final inline/embutido nos `<head>` do report site. Isso mantém layout e navegação consistentes e reduz duplicação estrutural.

## Fonte de verdade

O HTML é projeção. A fonte de verdade permanece:

```text
audit.db
artifacts/
```

O report site não recalcula score, finding ou recommendation. Chamadas M20, quando habilitadas, terminam e persistem antes da projeção HTML final.
