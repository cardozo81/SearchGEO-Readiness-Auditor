# Guia de IA — M18

Este documento descreve o contrato operacional atual de IA do SearchGEO Readiness Auditor. IA é **opcional** e nunca calcula o Score oficial.

## Modos disponíveis

| Seleção CLI | Comportamento |
|---|---|
| `--ai-provider none` | IA desabilitada. Nenhuma chamada externa. |
| `--ai-provider openai` | Usa somente OpenAI. Sem cross-provider fallback. |
| `--ai-provider deepseek` | Usa somente DeepSeek. Sem cross-provider fallback. |
| `--ai-provider mimo` | Usa somente Xiaomi MiMo. Sem cross-provider fallback. |
| `--ai-provider auto` | Cria cadeia determinística com providers elegíveis e permite failover controlado. |

O default é `none`.

## O que a IA faz

Os providers semânticos produzem avaliações auxiliares para `BR-GEO-028..049`, usando apenas o contexto/evidence fornecido pelo auditor.

Uma resposta só é aceita quando satisfaz o contrato SearchGEO, incluindo:

- exatamente 22 assessments semânticos;
- nenhuma regra ausente;
- nenhuma regra duplicada;
- nenhum `rule_id` desconhecido;
- enums válidos;
- `evidence_ids` existentes no contexto enviado;
- estrutura JSON válida;
- normalização local concluída.

HTTP `200` ou JSON parseável, isoladamente, não significam análise válida.

## O que a IA não faz

O LLM não:

- calcula `SCORE-GEO-001`;
- altera pesos;
- converte `UNKNOWN` em `FAIL`;
- define severity/actionability/prioridade por conta própria;
- garante ranking, citação, tráfego ou visibilidade;
- inventa evidence válida;
- substitui Business Rules;
- fornece chain-of-thought persistido ao auditor.

# Providers e modelos suportados

O M18 usa allowlist explícito de model IDs. Valores fora da lista são rejeitados.

| Provider | Model IDs suportados | Default | Reasoning default | Qualificação SearchGEO |
|---|---|---|---|---|
| OpenAI | `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna` | `gpt-5.6-terra` | `HIGH` | `QUALIFIED` |
| DeepSeek | `deepseek-v4-pro`, `deepseek-v4-flash` | `deepseek-v4-pro` | `HIGH` | `PROVISIONAL` |
| Xiaomi MiMo | `mimo-v2.5-pro`, `mimo-v2.5` | `mimo-v2.5-pro` | `HIGH` | `PROVISIONAL` |

MiMo normaliza qualquer reasoning habilitado (`LOW`, `MEDIUM`, `HIGH`) para o perfil operacional `THINKING_ENABLED` no relatório; não se infere superioridade entre esses níveis.

GitHub Copilot **não** é `SemanticProvider` do SearchGEO.

## Política de confiabilidade SearchGEO

A ordenação M18 é política inicial de adequação ao contrato do auditor, não benchmark científico universal.

| Rank | Provider | Modelo | Perfil | Classe |
|---:|---|---|---|---|
| 1 | OpenAI | `gpt-5.6-sol` | `HIGH/XHIGH` | `QUALIFIED-A+` |
| 2 | OpenAI | `gpt-5.6-terra` | `HIGH` | `QUALIFIED-A` |
| 3 | DeepSeek | `deepseek-v4-pro` | `HIGH` | `PROVISIONAL-A-` |
| 4 | MiMo | `mimo-v2.5-pro` | `THINKING_ENABLED` | `PROVISIONAL-B+` |
| 5 | OpenAI | `gpt-5.6-luna` | `HIGH` | `QUALIFIED-B+` |
| 6 | DeepSeek | `deepseek-v4-flash` | `HIGH` | `PROVISIONAL-B` |
| 7 | MiMo | `mimo-v2.5` | `THINKING_ENABLED` | `PROVISIONAL-B` |

DeepSeek/MiMo permanecem `PROVISIONAL` até benchmark SearchGEO específico.

# Configuração por provider

## OpenAI

```powershell
$env:OPENAI_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider openai
```

Variáveis opcionais:

```powershell
$env:SEARCHGEO_OPENAI_MODEL = "gpt-5.6-terra"
$env:SEARCHGEO_OPENAI_REASONING_EFFORT = "HIGH"
```

Ou model override por execução:

```powershell
searchgeo audit https://example.com --ai-provider openai --ai-model gpt-5.6-sol
```

## DeepSeek

```powershell
$env:DEEPSEEK_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider deepseek
```

Variáveis opcionais:

```powershell
$env:SEARCHGEO_DEEPSEEK_MODEL = "deepseek-v4-pro"
$env:SEARCHGEO_DEEPSEEK_REASONING_EFFORT = "HIGH"
```

Override por execução:

```powershell
searchgeo audit https://example.com --ai-provider deepseek --ai-model deepseek-v4-flash
```

## Xiaomi MiMo

```powershell
$env:MIMO_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider mimo
```

Variáveis opcionais:

```powershell
$env:SEARCHGEO_MIMO_MODEL = "mimo-v2.5-pro"
$env:SEARCHGEO_MIMO_REASONING_EFFORT = "HIGH"
```

Override por execução:

```powershell
searchgeo audit https://example.com --ai-provider mimo --ai-model mimo-v2.5
```

## Timeout das chamadas externas

A CLI aplica `180` segundos por chamada de IA por padrão. O timeout pode ser alterado para provider explícito e para todos os candidatos elegíveis de `auto`:

```powershell
$env:SEARCHGEO_AI_TIMEOUT_SECONDS = "240"
searchgeo audit https://example.com --ai-provider openai
```

O valor deve ser numérico, finito e maior que zero. Com `--ai-provider none`, a variável é ignorada porque não existe chamada externa.

Timeout não gera retry automático. Uma chamada pode expirar no cliente e ainda ter sido recebida/processada pelo provider; repetir silenciosamente criaria risco de consumo duplicado.

# Sem IA

```powershell
searchgeo audit https://example.com --ai-provider none
```

Ou simplesmente:

```powershell
searchgeo audit https://example.com
```

A auditoria continua em modo sem IA. Regras semantic-only sem fallback determinístico suficiente ficam `UNKNOWN`. Isso pode reduzir Coverage/Confidence/Consolidation, mas não reduz qualidade do website artificialmente.

# Um provider explícito

Provider explícito é `SINGLE_PROVIDER`.

Regras:

1. só o provider escolhido pode receber requisições;
2. não existe fallback para outro fornecedor;
3. sem token, o estado é `NOT_CONFIGURED` e nenhuma requisição externa é realizada;
4. model inválido é rejeitado antes da execução efetiva;
5. após falha qualificadora, o provider entra em `QUARANTINED_FOR_AUDIT`;
6. após quarantine, ele não é chamado novamente em URLs seguintes do mesmo audit;
7. sessão semântica insuficiente permanece `DEGRADED`, não `CHAIN_EXHAUSTED`;
8. chaves ausentes de outros providers não interferem no provider explicitamente selecionado.

Exemplo:

```powershell
$env:OPENAI_API_KEY = "<chave>"
searchgeo audit --urls-file .\urls.txt --ai-provider openai
```

Se a OpenAI retornar falta de créditos na primeira chamada, nenhuma DeepSeek/MiMo será usada e OpenAI não será consultada nas URLs seguintes daquele audit.

# Vários providers — `auto`

Configure uma ou mais chaves:

```powershell
$env:OPENAI_API_KEY = "<chave-openai>"
$env:DEEPSEEK_API_KEY = "<chave-deepseek>"
$env:MIMO_API_KEY = "<chave-mimo>"
searchgeo audit --urls-file .\urls.txt --ai-provider auto
```

## Como a cadeia é montada

No início do audit:

1. cada provider sem API key é ignorado;
2. cada provider com configuração/model inválido é excluído e aparece em `excluded_configurations`;
3. os providers elegíveis são ordenados pelo rank SearchGEO do modelo configurado;
4. a cadeia resultante fica imutável durante aquele audit.

Para defaults com três tokens:

```text
OpenAI gpt-5.6-terra
  -> DeepSeek deepseek-v4-pro
  -> MiMo mimo-v2.5-pro
```

`AUTO` **não chama todos em paralelo**.

## Falha e failover

Para uma URL ainda sem provider fixado:

1. tenta o provider saudável de maior prioridade;
2. se houver resposta válida, encerra a cadeia para aquele contexto e nenhum provider posterior é chamado para sobrescrever o resultado;
3. se houver erro técnico/contratual, o provider fica `QUARANTINED_FOR_AUDIT`;
4. o próximo provider saudável pode ser tentado;
5. provider quarantined nunca é reintroduzido no mesmo audit.

Se todos os providers forem quarantined:

```text
status da sessão: CHAIN_EXHAUSTED
limitação: AI_PROVIDER_CHAIN_EXHAUSTED
```

As regras determinísticas continuam. Dependências semantic-only ficam `UNKNOWN` quando não existe base suficiente.

# Provider lock por URL — Desktop/Mobile

O primeiro provider que produz resultado válido para uma URL fica `PINNED_TO_URL` conceitualmente.

Exemplo:

```text
URL A Desktop -> OpenAI SUCCESS
URL A Mobile  -> deve usar OpenAI
```

Se OpenAI falhar no Mobile:

```text
URL A Mobile -> DEGRADED/UNKNOWN quando aplicável
OpenAI -> QUARANTINED_FOR_AUDIT para URLs seguintes
DeepSeek NÃO completa URL A Mobile
URL B -> pode iniciar em DeepSeek
```

Isso evita produzir Desktop e Mobile da mesma URL com providers diferentes.

# Estados e cenários

| Cenário | Chamada externa? | Resultado operacional |
|---|---:|---|
| `none` | Não | `NO_AI` / IA desabilitada |
| explícito sem token | Não | `NOT_CONFIGURED`; sem IA efetiva |
| `auto` sem nenhum token | Não | nenhuma cadeia elegível; sem IA efetiva |
| explícito válido com sucesso | Sim | `FULL` quando universo aplicável é atendido |
| explícito com erro/crédito | Sim, até falhar | `DEGRADED`; provider quarantined; sem fallback cruzado |
| `auto` com primeiro provider falhando e segundo funcionando | Sim | failover; primeiro quarantined; segundo pode se tornar efetivo |
| `auto` com todos falhando | Sim | `CHAIN_EXHAUSTED`; `AI_PROVIDER_CHAIN_EXHAUSTED` |
| pinned provider falha no segundo device | Sim | sem fallback para mesma URL; contexto degradado |

# Classes de erro

O M18 normaliza diagnósticos em:

```text
AUTH_ERROR
QUOTA_ERROR
CREDIT_ERROR
RATE_LIMIT_ERROR
MODEL_ERROR
PERMISSION_ERROR
NETWORK_ERROR
TIMEOUT_ERROR
SERVER_ERROR
CONTRACT_ERROR
EMPTY_RESPONSE
INVALID_RESPONSE
UNKNOWN_PROVIDER_ERROR
```

Exemplos:

- token inválido -> `AUTH_ERROR`;
- conta sem saldo/créditos -> `CREDIT_ERROR` quando identificável;
- rate limit -> `RATE_LIMIT_ERROR`;
- timeout -> `TIMEOUT_ERROR`;
- resposta incompleta/schema inválido/evidence inventada -> `CONTRACT_ERROR`/`INVALID_RESPONSE` conforme o caso.

`TIMEOUT_ERROR` não equivale a erro de crédito ou autenticação. Ele informa apenas que a chamada não terminou dentro do limite do cliente.

Texto bruto potencialmente sensível da mensagem do provider não é necessário para classificar a falha e não deve ser usado como relatório de diagnóstico.

# Telemetria e custo

Cada tentativa materializável pode registrar:

- URL/device/snapshot;
- provider;
- model;
- reasoning profile;
- rank;
- timestamps e duração;
- status;
- diagnóstico sanitizado;
- input tokens;
- cached input tokens;
- output tokens;
- reasoning tokens;
- total tokens;
- custo estimado quando calculável;
- versão do catálogo de preços;
- hash da requisição;
- versão do contrato semântico.

Se o provider não reportar tokens, o campo fica `NULL`; o SearchGEO não inventa contagem.

`ESTIMATED_COST`:

- usa catálogo local versionado;
- só é exibido quando os dados necessários existem;
- não representa invoice/billing externo;
- não altera score.

# Onde consultar o uso da IA

## `report.html`

A seção **Uso de IA — execução e telemetria** contém:

- habilitação;
- estratégia;
- provider inicial/efetivo;
- modelo;
- profundidade;
- status;
- cadeia inicial;
- cobertura;
- failover;
- tabela de tentativas;
- tokens;
- `ESTIMATED_COST`;
- duração;
- erro sanitizado.

O bloco é inserido dentro de `<main>`. A tabela usa overflow horizontal interno e o conteúdo principal é limitado à largura disponível ao lado da sidebar fixa.

## `remediation.html`

Exibe apenas **contexto informativo** da análise semântica. Falha de provider não vira finding nem recommendation do website.

## `audit.db`

Tabelas M18:

```text
ai_audit_sessions
ai_provider_attempts
provider_pricing_catalog
```

## logging do processo

O SearchGEO emite linhas INFO sanitizadas para tentativas/sessão M18 quando o `log_level` permite. O registro inclui provider/model/status/duração/tokens/custo estimado/error_class, nunca API key ou corpo integral da requisição.

A baseline não cria `audit.log` automaticamente. O registro persistente é o `audit.db` e o `report.html`.

# Segurança e privacidade

Nunca persistir ou imprimir:

- API key;
- `Authorization`;
- header `api-key`;
- corpo integral sensível da requisição;
- chain-of-thought.

Valide apenas a presença das variáveis:

```powershell
Test-Path Env:OPENAI_API_KEY
Test-Path Env:DEEPSEEK_API_KEY
Test-Path Env:MIMO_API_KEY
```

# Dados enviados ao provider

Ao habilitar IA externa, conteúdo/evidence do site auditado necessários ao contrato semântico são transmitidos ao provider selecionado. Antes de usar IA em conteúdo corporativo, confirme a política de dados/privacidade aplicável.

# Structured Output por provider

- OpenAI: Responses API com JSON Schema estrito.
- DeepSeek: Responses API em modo estruturado compatível com o adapter e validação local SearchGEO.
- MiMo: Responses API com JSON object e validação local estrita pelo schema SearchGEO; não se presume garantia nativa de JSON Schema equivalente à OpenAI.

Em todos os casos, a validação local SearchGEO é obrigatória antes de aceitar a análise.

# Referências internas

- [Referência completa da CLI](CLI_REFERENCE.md)
- [Configuração](CONFIGURATION.md)
- [Compatibilidade](COMPATIBILITY.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [Outputs e artifacts](OUTPUTS_AND_ARTIFACTS.md)
- [Especificação M18](specification/18_MULTI_AI_PROVIDER_ROUTING.md)
