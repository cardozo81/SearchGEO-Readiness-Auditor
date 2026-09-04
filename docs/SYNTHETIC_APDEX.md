# Synthetic Apdex — M23

Guia operacional do `Synthetic Navigation Apdex` do SearchGEO.

> M23 é **default OFF**. Ele não altera `SCORE-GEO-002`, findings GEO, Coverage ou Confidence. O índice mede uma Task sintética de navegação e não deve ser confundido com RUM/APM de usuários reais.

## Execução mínima

O threshold `T` é obrigatório quando M23 está habilitado:

```powershell
searchgeo audit https://example.com `
  --ai-provider none `
  --synthetic-apdex `
  --apdex-threshold-seconds 1.5 `
  --apdex-samples-per-context 5 `
  --apdex-max-attempts-per-context 7 `
  --apdex-max-pages 1 `
  --apdex-delay-seconds 1 `
  --apdex-concurrency 1
```

Esse exemplo usa somente cinco amostras válidas por contexto e, portanto, gera um **small group `*`**. Ele é apropriado para smoke funcional controlado; não é o grupo final normal de 100 amostras.

## Parâmetros

| Parâmetro | Default quando M23 ON | Regra |
|---|---:|---|
| `--synthetic-apdex` | OFF | habilita M23 |
| `--apdex-threshold-seconds` | nenhum | `T` obrigatório, número > 0 |
| `--apdex-samples-per-context` | `100` | alvo de amostras válidas por URL/device |
| `--apdex-max-attempts-per-context` | `ceil(1.25 × alvo)` | deve ser >= alvo |
| `--apdex-max-pages` | `1` | `0` significa todas as páginas auditadas |
| `--apdex-timeout-seconds` | `max(45, 4T+5)` | deve ser estritamente > `4T` |
| `--apdex-delay-seconds` | `1` | intervalo mínimo entre inícios; >= 0 |
| `--apdex-concurrency` | `1` | máximo `2` |

Variáveis equivalentes:

```text
SEARCHGEO_SYNTHETIC_APDEX
SEARCHGEO_APDEX_THRESHOLD_SECONDS
SEARCHGEO_APDEX_SAMPLES_PER_CONTEXT
SEARCHGEO_APDEX_MAX_ATTEMPTS_PER_CONTEXT
SEARCHGEO_APDEX_MAX_PAGES
SEARCHGEO_APDEX_TIMEOUT_SECONDS
SEARCHGEO_APDEX_DELAY_SECONDS
SEARCHGEO_APDEX_CONCURRENCY
```

Precedência: CLI > ambiente > defaults.

## Fórmula

```text
Apdex = (Satisfied + 0.5 × Tolerating) / Total de amostras válidas

Satisfied  <= T
Tolerating > T e <= 4T
Frustrated > 4T
```

Timeout/erro de navegação ou erro de aplicação/servidor é `FRUSTRATED` quando o profile sintético foi efetivamente aplicado. Falha do browser/ferramenta ao materializar o profile é amostra inválida e fica fora do denominador.

## Task e cache

Task medida:

```text
NAVIGATION_LOAD
início: imediatamente antes de page.goto
fim: conclusão de wait_until=load
```

Cada amostra usa BrowserContext novo e cache do browser desabilitado. Profiles de CPU/rede são determinísticos e versionados para favorecer reprodutibilidade.

## Carga e custo

M23 produz:

- `0` chamadas LLM adicionais;
- `0` chamadas PageSpeed/CrUX adicionais;
- `0` tokens de IA;
- nenhum preço de API próprio conhecido.

Entretanto, produz **tráfego HTTP real contra o site** e consumo local de CPU/RAM/tempo. Uma navegação pode carregar dezenas ou centenas de subrecursos, portanto 100 amostras não significam apenas 100 requests.

Antes de um run de 100 amostras em produção, valide autorização, capacidade e janela operacional do alvo.

## Console interativo

`searchgeo-console` possui o item:

```text
11. Synthetic Apdex M23
```

O console mostra separadamente:

- exposição financeira de IA/M21;
- carga sintética potencial M23;
- `T`;
- alvo de válidas;
- máximo de tentativas;
- páginas;
- timeout;
- delay;
- concorrência;
- navegações reais persistidas no resumo final.

M23 não muda a faixa `NENHUM/BAIXO/MÉDIO/ALTO/EXCESSIVO` de custo financeiro porque essa faixa não representa CPU local/tráfego do alvo.

## Report

Quando habilitado, M23 materializa:

```text
report/apdex.html
```

A página apresenta Apdex, S/T/F, distribuição, p75/p90/p95/p99, estabilidade/tendência, profile sintético, host executor e rastreabilidade Lighthouse quando `lighthouseResult.configSettings` estiver disponível em artifacts M21.

O menu inclui `Apdex` somente quando `apdex.html` existe.

## Relação com Lighthouse e CrUX

M23 não calcula Apdex a partir de Lighthouse/CrUX. Quando M21 já coletou um artifact PageSpeed, M23 apenas extrai e persiste a configuração efetiva Lighthouse para comparação auditável. Campos ausentes não são inferidos.

O tempo total do Lighthouse não entra na fórmula Apdex.

## Smoke recomendado

Primeiro smoke humano:

```text
1 URL autorizada
mobile
T explícito
3–5 amostras válidas
max attempts = 5–7
max pages = 1
delay >= 1 s
concurrency = 1
IA = none
```

Esperado:

- audit principal conclui;
- M23 `PARTIAL` por small group, não por erro;
- `small_group=*` visível;
- `audit.db` contém samples/summaries;
- `report/apdex.html` existe;
- menu consistente em todas as páginas;
- Score GEO permanece idêntico ao audit sem M23;
- nenhuma chamada LLM/PageSpeed/CrUX causada por M23.

## Referência normativa

Consulte `docs/specification/23_SYNTHETIC_APDEX_LIGHTHOUSE_TRACEABILITY.md`.
