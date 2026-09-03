# Referência completa da CLI

Esta é a referência operacional dos parâmetros expostos pelo executável `searchgeo` na baseline atual. Em caso de divergência, `searchgeo --help`, `searchgeo audit --help` e `src/searchgeo/cli.py` representam a interface efetivamente implementada.

## Sintaxe

```text
searchgeo [opções globais] audit [target ...] [opções do audit]
```

No PowerShell, opções globais como `--config` devem ser colocadas antes do subcomando `audit`:

```powershell
searchgeo --config .\searchgeo.toml audit https://example.com --project "Exemplo"
```

## Opções globais

| Parâmetro | Tipo | Default | Obrigatório | Efeito |
|---|---|---:|---:|---|
| `-h`, `--help` | flag | — | Não | Exibe ajuda do nível atual e encerra. |
| `--version` | flag | — | Não | Exibe a versão instalada e encerra. |
| `--config PATH` | path | configuração interna padrão | Não | Carrega `searchgeo.toml`; atualmente o TOML expõe configuração de logging da aplicação. |

## Subcomando `audit`

O único subcomando operacional atual é:

```powershell
searchgeo audit ...
```

### Glossário de todos os parâmetros do `audit`

| Parâmetro | Tipo/valores | Default | Obrigatório | Descrição operacional |
|---|---|---:|---:|---|
| `target` | um ou mais domínios/URLs HTTP(S) posicionais | — | Condicional | Um target é obrigatório, diretamente ou via `--urls-file`. Um único positional mantém o modo clássico; múltiplos positionals formam `URL_SET`. |
| `--urls-file PATH` | arquivo UTF-8 | — | Condicional | Lê um domínio/URL por linha. Linhas vazias e linhas iniciadas por `#` são ignoradas. O uso deste parâmetro define `URL_SET`, mesmo que reste só uma URL válida. |
| `--project TEXT` | texto | — | Não | Nome humano do projeto gravado na auditoria e exibido nos relatórios. |
| `--language CODE` | texto | `pt-BR` | Não | Contexto de idioma principal para conteúdo/análise/relatório. Não traduz automaticamente o site. |
| `--market CODE` | texto | `BR` | Não | Contexto de mercado usado pela análise. |
| `--max-pages N` | inteiro `> 0` | `100` | Não | Limite determinístico de páginas auditadas. Valor `0` ou negativo é rejeitado. |
| `--audits-root PATH` | diretório | `audits` | Não | Raiz onde serão criados `AUD-*`, `audit.db`, relatórios e artifacts. |
| `--ai-provider` | `none`, `openai`, `deepseek`, `mimo`, `auto` | `none` | Não | Seleciona o modo de IA semântica. `none` desabilita IA; provider explícito usa apenas ele; `auto` monta cadeia elegível e permite failover. |
| `--ai-model MODEL_ID` | model ID suportado | default do provider | Não | Override apenas para provider explícito. É inválido com `--ai-provider auto`. O modelo precisa estar no allowlist do provider. |
| `-h`, `--help` | flag | — | Não | Exibe ajuda específica do subcomando `audit`. |

## Regras de `target`

O valor pode ser domínio ou URL HTTP(S):

```text
example.com
https://example.com/
https://example.com/produto?canal=web
http://localhost:8000/
```

Validações implementadas:

- apenas `http` e `https`;
- hostname, IP ou `localhost` válidos;
- credenciais embutidas na URL (`user:password@host`) são rejeitadas;
- porta inválida é rejeitada;
- domínio sem scheme não pode conter path, query ou fragment; nesses casos informe `http://` ou `https://`;
- espaços no target são rejeitados.

## Entrada de uma URL

```powershell
searchgeo audit https://example.com --project "Site"
```

## Entrada de várias URLs diretamente

```powershell
searchgeo audit `
  https://example.com/ `
  https://example.com/produto `
  https://example.com/faq `
  --project "Site"
```

As URLs explícitas pertencem ao mesmo `audit_id` e devem respeitar as regras de origem do auditor.

## Entrada por arquivo

`urls.txt`:

```text
# páginas comerciais
https://example.com/
https://example.com/produto

# suporte
https://example.com/faq
```

Execução:

```powershell
searchgeo audit --urls-file .\urls.txt --project "Site"
```

É permitido combinar positionals e `--urls-file`; os valores são reunidos antes da validação/deduplicação da auditoria.

# IA — parâmetros e variáveis relacionadas

As variáveis abaixo não são parâmetros CLI, mas alteram a execução de `--ai-provider`.

| Provider | API key | Modelo por ambiente | Reasoning por ambiente | Default atual |
|---|---|---|---|---|
| OpenAI | `OPENAI_API_KEY` | `SEARCHGEO_OPENAI_MODEL` | `SEARCHGEO_OPENAI_REASONING_EFFORT` | `gpt-5.6-terra` / `HIGH` |
| DeepSeek | `DEEPSEEK_API_KEY` | `SEARCHGEO_DEEPSEEK_MODEL` | `SEARCHGEO_DEEPSEEK_REASONING_EFFORT` | `deepseek-v4-pro` / `HIGH` |
| Xiaomi MiMo | `MIMO_API_KEY` | `SEARCHGEO_MIMO_MODEL` | `SEARCHGEO_MIMO_REASONING_EFFORT` | `mimo-v2.5-pro` / `HIGH` (`THINKING_ENABLED` no relatório) |

Modelos aceitos pelo código:

```text
OPENAI:   gpt-5.6-sol | gpt-5.6-terra | gpt-5.6-luna
DEEPSEEK: deepseek-v4-pro | deepseek-v4-flash
MIMO:     mimo-v2.5-pro | mimo-v2.5
```

## Sem IA

```powershell
searchgeo audit https://example.com --ai-provider none
```

É também o default quando `--ai-provider` é omitido. O pipeline determinístico continua; regras semantic-only sem evidência suficiente permanecem `UNKNOWN`. Ausência de IA não é `FAIL` do website.

## Um único provider

OpenAI:

```powershell
$env:OPENAI_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider openai
```

DeepSeek:

```powershell
$env:DEEPSEEK_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider deepseek
```

MiMo:

```powershell
$env:MIMO_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider mimo
```

Override explícito de modelo:

```powershell
$env:DEEPSEEK_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider deepseek --ai-model deepseek-v4-flash
```

Provider explícito **não faz fallback para outro fornecedor**. Se a primeira chamada qualificadora falhar, o provider fica `QUARANTINED_FOR_AUDIT` e não é consultado novamente no mesmo audit; contextos sem resultado válido degradam para `UNKNOWN` quando dependem da IA.

## Vários providers com `auto`

Configure quantos providers quiser e selecione `auto`:

```powershell
$env:OPENAI_API_KEY = "<chave-openai>"
$env:DEEPSEEK_API_KEY = "<chave-deepseek>"
$env:MIMO_API_KEY = "<chave-mimo>"
searchgeo audit --urls-file .\urls.txt --project "Site" --ai-provider auto
```

`AUTO` não significa chamada paralela a todos os providers. Ele cria, no início do audit, uma cadeia imutável apenas com configurações elegíveis e chama providers sequencialmente conforme necessidade.

Ordem inicial de confiabilidade SearchGEO para os defaults:

1. OpenAI `gpt-5.6-terra` — rank 2;
2. DeepSeek `deepseek-v4-pro` — rank 3;
3. MiMo `mimo-v2.5-pro` — rank 4.

Se um model environment override selecionar outro modelo suportado, o rank correspondente desse modelo é usado.

### Provider habilitado no comando, mas sem token

Provider explícito sem sua API key retorna `NOT_CONFIGURED`. Nenhuma chamada externa é feita. A auditoria segue em `NO_AI`/semântica não disponível conforme os contextos e isso não é falha do website.

Em `auto`, provider sem token simplesmente **não entra na cadeia**. Se nenhum provider tiver token/configuração elegível, `AUTO` opera sem chamadas externas e a análise semântica fica sem provider configurado.

### Configuração/modelo inválido

Provider explícito com model ID fora do allowlist falha na validação da CLI/configuração antes da auditoria efetiva.

Em `auto`, uma configuração de provider inválida é excluída da cadeia e registrada em `excluded_configurations`; os demais providers elegíveis continuam.

### Erro, timeout, quota ou ausência de créditos

Falhas são classificadas e sanitizadas. As classes atuais incluem:

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

Em provider explícito, não existe cross-provider fallback: a sessão fica `DEGRADED` quando a IA não consegue produzir o universo necessário.

Em `auto`, a falha coloca aquele provider em `QUARANTINED_FOR_AUDIT` e o próximo provider saudável pode ser tentado. Provider quarantined não volta para a cadeia durante o mesmo audit.

### Lock de provider por URL

Quando um provider produz a primeira análise válida de uma URL, essa URL fica fixada naquele provider para manter Desktop/Mobile comparáveis.

Se o mesmo provider falhar no segundo device da URL:

- nenhum provider alternativo completa aquela mesma URL;
- o contexto faltante fica degradado/`UNKNOWN` quando aplicável;
- o provider falho é quarantined para URLs seguintes;
- uma URL nova pode iniciar no próximo provider saudável.

Se todos os providers de `AUTO` forem quarantined, a sessão fica `CHAIN_EXHAUSTED` e a auditoria registra `AI_PROVIDER_CHAIN_EXHAUSTED`. Isso é uma limitação operacional da auditoria, não finding do website.

# Saída da execução

Ao terminar, a CLI imprime:

```text
Auditoria concluída: AUD-...
Status: ...
Páginas auditadas: ...
Problemas identificados: ...
Recomendações: ...
Relatório: audits\AUD-...\report.html
Relatório por problemas: audits\AUD-...\remediation.html
```

## Uso de IA no `report.html`

A seção **Uso de IA — execução e telemetria** mostra, quando M18 está materializado:

- IA habilitada;
- estratégia (`NONE`, `SINGLE_PROVIDER`, `AUTO`);
- provider/model inicial e efetivo;
- profundidade/reasoning normalizado;
- status da sessão;
- cadeia configurada;
- failover observado;
- cobertura por URL/device;
- uma linha por tentativa com URL, device, provider, model, status, tokens, custo estimado, duração e erro sanitizado.

`ESTIMATED_COST` é estimativa calculada pelo catálogo local versionado; não é invoice nem billing do provider e não participa do score.

## Persistência de uso de IA no `audit.db`

As tabelas M18 são:

```text
ai_audit_sessions
ai_provider_attempts
provider_pricing_catalog
```

Tokens ausentes no retorno do provider ficam `NULL`. API keys, header `Authorization`, corpo sensível integral e chain-of-thought não são persistidos.

## Logging do processo

O SearchGEO emite logging operacional sanitizado conforme `log_level`. Para M18, cada tentativa registra provider/model/status/duração/tokens/custo estimado/error_class e existe um resumo da sessão. O log não inclui API key, Authorization ou corpo integral da requisição.

A baseline atual **não cria um `audit.log` por auditoria**. O registro persistente de uso é `audit.db` + `report.html`; logs do processo seguem o handler padrão configurado pela aplicação.

# Exemplos completos

Sem IA, uma URL:

```powershell
searchgeo audit https://example.com --project "Institucional" --max-pages 10
```

Sem IA, conjunto de URLs:

```powershell
searchgeo audit --urls-file .\urls.txt --project "Institucional" --max-pages 20 --ai-provider none
```

OpenAI explícito:

```powershell
$env:OPENAI_API_KEY = "<chave>"
searchgeo audit https://example.com --project "Institucional" --ai-provider openai --ai-model gpt-5.6-terra
```

AUTO multi-provider:

```powershell
$env:OPENAI_API_KEY = "<chave-openai>"
$env:DEEPSEEK_API_KEY = "<chave-deepseek>"
searchgeo audit --urls-file .\urls.txt --project "Institucional" --ai-provider auto
```

Com configuração de logging:

```powershell
searchgeo --config .\searchgeo.toml audit https://example.com --project "Institucional" --ai-provider none
```
