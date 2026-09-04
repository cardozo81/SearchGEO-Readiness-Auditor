# Console — custo, quota e telemetria de execução

Este documento define a fonte de verdade usada pelo `searchgeo-console` para projeção pré-execução e consolidação pós-execução.

## Regra de não duplicação

O console **não cria uma segunda cópia de tokens, custo real estimado ou tentativas externas**.

A telemetria já materializada pelo pipeline permanece como fonte normativa:

| Domínio | Tabela existente | Dados usados pelo console |
|---|---|---|
| M18 análise semântica | `ai_provider_attempts` | provider/model, status, tokens, duração, `estimated_cost`, moeda, pricing version |
| Catálogo de preço IA | `provider_pricing_catalog` | preço unitário e versão/referência pública |
| M20 remediação textual | `content_remediation_attempts` | provider/model, status, tokens, duração, `estimated_cost`, moeda |
| M21 Web Performance | `web_performance_attempts` | serviço, URL/device, status, HTTP, duração e quantidade de chamadas |
| M21 execução | `web_performance_runs` | limites, páginas/contextos considerados e sucessos |

O resumo exibido ao final é calculado por `SELECT/SUM/COUNT` sobre essas tabelas. Ele não é persistido novamente como total, evitando divergência entre detalhe e agregado.

## Dado novo persistido pelo console

O único dado adicional de custo/execução que não existia no pipeline é a **projeção feita antes da execução** e o **tempo observado pelo console**.

Por isso o console cria, dentro do `audit.db` da própria auditoria, a tabela:

```text
console_execution_projections
```

Ela contém somente:

- `audit_id`;
- timestamp em que a projeção foi calculada;
- início e fim da execução do subprocesso;
- duração total em ms;
- faixa `NENHUM|BAIXO|MÉDIO|ALTO|EXCESSIVO`;
- mínimo/máximo de páginas considerados;
- quantidade de contextos de dispositivo;
- mínimo/máximo de tentativas de IA projetadas;
- mínimo/máximo de chamadas M21 projetadas;
- provider/modelos considerados;
- configuração não sensível usada na projeção;
- razões da classificação;
- versão do catálogo de pricing.

A tabela **não possui** colunas `input_tokens`, `output_tokens`, `total_tokens` ou `estimated_cost`. Esses dados continuam somente nas tabelas M18/M20 que realmente registraram as tentativas.

Nenhuma API key, token, Authorization ou secret é persistido.

## Projeção versus realizado

A estrutura permite posteriormente montar no report uma comparação como:

```text
Antes da execução
  exposição: MÉDIO
  IA projetada: 6–12 tentativas
  M21 projetado: 4–8 chamadas

Realizado
  IA: 7 tentativas / 5 sucessos
  tokens: 54.210
  custo IA estimado: USD 0.1834
  PageSpeed: 4 chamadas
  CrUX: 2 chamadas
  duração: 00:02:48
```

A coluna de realizado deve sempre ser derivada das tabelas de tentativas, e não copiada para `console_execution_projections`.

## Consulta de custo IA consolidado

Exemplo conceitual para uma moeda:

```sql
SELECT cost_currency, SUM(estimated_cost) AS estimated_cost
FROM (
    SELECT cost_currency, estimated_cost
    FROM ai_provider_attempts
    WHERE estimated_cost IS NOT NULL
    UNION ALL
    SELECT cost_currency, estimated_cost
    FROM content_remediation_attempts
    WHERE estimated_cost IS NOT NULL
)
GROUP BY cost_currency;
```

Não somar moedas distintas numa única grandeza sem conversão cambial explícita.

## Consulta de tokens consolidada

```sql
SELECT
    SUM(input_tokens) AS input_tokens,
    SUM(cached_input_tokens) AS cached_input_tokens,
    SUM(output_tokens) AS output_tokens,
    SUM(reasoning_tokens) AS reasoning_tokens,
    SUM(total_tokens) AS total_tokens
FROM (
    SELECT input_tokens,cached_input_tokens,output_tokens,reasoning_tokens,total_tokens
    FROM ai_provider_attempts
    UNION ALL
    SELECT input_tokens,cached_input_tokens,output_tokens,reasoning_tokens,total_tokens
    FROM content_remediation_attempts
);
```

## Consulta de consumo M21

```sql
SELECT service, COUNT(*) AS attempts
FROM web_performance_attempts
GROUP BY service
ORDER BY service;
```

O console usa essa tabela, e não a contagem de linhas do log, para evitar dupla contagem ou divergência entre log e banco.

## Quota não é invoice

A quantidade de requests pode ser comparada com limites publicados pelo serviço, mas quota e cobrança são conceitos distintos.

A documentação oficial da CrUX API informa limite de 150 consultas/minuto por projeto Google Cloud e declara que essa quota é oferecida sem custo, sem opção de pagar por aumento:

- <https://developer.chrome.com/docs/crux/api>

A documentação da PageSpeed Insights API informa que o serviço pode ser utilizado com ou sem API key e recomenda chave para consultas frequentes/automatizadas:

- <https://developers.google.com/speed/docs/insights/v5/get-started>

O SearchGEO não converte chamadas PageSpeed/CrUX em valor monetário sem uma fonte de pricing aplicável e persistida.

## Preparação para o report

Quando a camada de report for atualizada, ela deve:

1. ler `console_execution_projections` quando existir;
2. ler M18/M20 para tokens/custo realizado;
3. ler M21 para chamadas/quota realizada;
4. manter preços por moeda;
5. sinalizar tentativas com tokens mas sem preço estimável;
6. mostrar `ESTIMATED_COST` como estimativa, nunca como invoice;
7. funcionar também para auditorias executadas pelo CLI original, nas quais `console_execution_projections` pode não existir.

Dessa forma o report continuará compatível com `searchgeo audit` e o console acrescentará apenas uma projeção opcional quando tiver sido a interface de execução.
