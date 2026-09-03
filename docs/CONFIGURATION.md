# Configuração

Este documento descreve apenas configurações efetivamente expostas na baseline atual. A referência exaustiva dos argumentos CLI está em [CLI_REFERENCE.md](CLI_REFERENCE.md).

# Precedência operacional

A configuração do SearchGEO vem de três superfícies distintas:

1. parâmetros CLI da auditoria;
2. variáveis de ambiente para browser/providers;
3. arquivo TOML para configuração de aplicação atualmente suportada.

Não existe arquivo único que substitua todos os parâmetros da CLI.

# Arquivo TOML

Use a opção global antes do subcomando:

```powershell
searchgeo --config .\searchgeo.toml audit https://example.com
```

A configuração TOML atual é usada para settings da aplicação, notadamente logging conforme `src/searchgeo/config.py`. Parâmetros como target, max pages e provider são passados pela CLI/environment.

# Parâmetros CLI

Sintaxe resumida:

```text
searchgeo [--config PATH] audit [target ...]
  [--urls-file PATH]
  [--project TEXT]
  [--language CODE]
  [--market CODE]
  [--max-pages N]
  [--audits-root PATH]
  [--ai-provider none|openai|deepseek|mimo|auto]
  [--ai-model MODEL_ID]
```

Defaults:

| Parâmetro | Default |
|---|---|
| `--language` | `pt-BR` |
| `--market` | `BR` |
| `--max-pages` | `100` |
| `--audits-root` | `audits` |
| `--ai-provider` | `none` |

Para tipos, obrigatoriedade, validações e combinações, consulte [CLI_REFERENCE.md](CLI_REFERENCE.md).

# Targets e URL_SET

Uma URL/domain positional:

```powershell
searchgeo audit https://example.com
```

Várias:

```powershell
searchgeo audit https://example.com/ https://example.com/produto https://example.com/faq
```

Arquivo:

```powershell
searchgeo audit --urls-file .\urls.txt
```

`--urls-file` sempre caracteriza entrada explícita `URL_SET`, mesmo se apenas uma URL permanecer após remover comentários/linhas vazias. Positionals e arquivo podem ser combinados.

# Browser

A variável operacional disponível é:

```powershell
$env:PLAYWRIGHT_CHROMIUM_EXECUTABLE = "C:\caminho\para\chrome.exe"
```

Quando omitida, o renderer usa o browser provisionado pelo Playwright conforme a implementação.

# IA

## Timeout de chamada externa

A CLI aplica um timeout operacional mais amplo às chamadas semânticas externas para evitar falsos `TIMEOUT_ERROR` em respostas estruturadas com reasoning.

| Variável | Função | Default |
|---|---|---:|
| `SEARCHGEO_AI_TIMEOUT_SECONDS` | timeout por chamada externa de IA, em segundos, aplicado a provider explícito e a todos os candidatos elegíveis de `auto` | `180` |

O valor deve ser numérico, finito e maior que zero. Quando `--ai-provider none` é usado, essa variável é ignorada porque nenhuma chamada externa é feita.

Exemplo:

```powershell
$env:SEARCHGEO_AI_TIMEOUT_SECONDS = "240"
searchgeo audit https://example.com --ai-provider openai
```

O timeout não cria retry automático. Se a chamada expirar, a falha continua sendo classificada como `TIMEOUT_ERROR`, preservando a política de quarantine/failover sem duplicar requisições automaticamente.

## Desabilitada

```powershell
searchgeo audit https://example.com --ai-provider none
```

Esse é o default.

## OpenAI

```powershell
$env:OPENAI_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider openai
```

Configuração:

| Variável | Função | Default |
|---|---|---|
| `OPENAI_API_KEY` | credencial | nenhuma |
| `SEARCHGEO_OPENAI_MODEL` | model ID | `gpt-5.6-terra` |
| `SEARCHGEO_OPENAI_REASONING_EFFORT` | reasoning | `HIGH` |

Modelos aceitos:

```text
gpt-5.6-sol
gpt-5.6-terra
gpt-5.6-luna
```

## DeepSeek

```powershell
$env:DEEPSEEK_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider deepseek
```

| Variável | Função | Default |
|---|---|---|
| `DEEPSEEK_API_KEY` | credencial | nenhuma |
| `SEARCHGEO_DEEPSEEK_MODEL` | model ID | `deepseek-v4-pro` |
| `SEARCHGEO_DEEPSEEK_REASONING_EFFORT` | reasoning | `HIGH` |

Modelos aceitos:

```text
deepseek-v4-pro
deepseek-v4-flash
```

## Xiaomi MiMo

```powershell
$env:MIMO_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider mimo
```

| Variável | Função | Default |
|---|---|---|
| `MIMO_API_KEY` | credencial | nenhuma |
| `SEARCHGEO_MIMO_MODEL` | model ID | `mimo-v2.5-pro` |
| `SEARCHGEO_MIMO_REASONING_EFFORT` | reasoning | `HIGH` |

Modelos aceitos:

```text
mimo-v2.5-pro
mimo-v2.5
```

MiMo reporta LOW/MEDIUM/HIGH como perfil normalizado `THINKING_ENABLED`.

# Override de modelo por CLI

Provider explícito:

```powershell
searchgeo audit https://example.com --ai-provider openai --ai-model gpt-5.6-sol
searchgeo audit https://example.com --ai-provider deepseek --ai-model deepseek-v4-flash
searchgeo audit https://example.com --ai-provider mimo --ai-model mimo-v2.5
```

`--ai-model` **não pode** ser usado com `--ai-provider auto`.

No `auto`, use as variáveis específicas:

```powershell
$env:SEARCHGEO_OPENAI_MODEL = "gpt-5.6-luna"
$env:SEARCHGEO_DEEPSEEK_MODEL = "deepseek-v4-pro"
$env:SEARCHGEO_MIMO_MODEL = "mimo-v2.5-pro"
searchgeo audit https://example.com --ai-provider auto
```

# AUTO multi-provider

Exemplo com três providers:

```powershell
$env:OPENAI_API_KEY = "<chave-openai>"
$env:DEEPSEEK_API_KEY = "<chave-deepseek>"
$env:MIMO_API_KEY = "<chave-mimo>"
searchgeo audit --urls-file .\urls.txt --ai-provider auto
```

Regras de configuração:

- provider sem token é omitido da cadeia;
- provider com token mas model/reasoning inválido é excluído como configuração inválida;
- cadeia é ordenada uma vez no início pelo rank SearchGEO do model;
- a cadeia não muda para reintroduzir provider quarantined;
- chamadas são sequenciais, não paralelas;
- o primeiro resultado válido encerra a tentativa de outros providers naquele contexto e fixa o provider da URL para os demais devices.

Se nenhum token elegível existir, nenhuma chamada externa é feita.

# Reasoning aceito

OpenAI/DeepSeek passam pelo perfil compatível com o adapter. A baseline M18 reconhece os níveis implementados no adapter; os defaults documentados são `HIGH`.

MiMo aceita:

```text
NONE
LOW
MEDIUM
HIGH
```

No relatório:

- `NONE` -> `NONE`;
- `LOW`, `MEDIUM`, `HIGH` -> `THINKING_ENABLED`.

# Estados operacionais da IA

| Situação | Estratégia | Resultado esperado |
|---|---|---|
| `none` | `NONE` | IA desabilitada; `NO_AI` |
| provider explícito sem key | `SINGLE_PROVIDER` | `NOT_CONFIGURED`; sem chamada externa |
| provider explícito com sucesso | `SINGLE_PROVIDER` | sucesso/FULL conforme universo aplicável |
| provider explícito falha | `SINGLE_PROVIDER` | `DEGRADED`; provider quarantined; sem fallback cruzado |
| `auto` sem provider elegível | `AUTO` | nenhuma chamada externa; sem IA efetiva |
| `auto` com failover bem-sucedido | `AUTO` | provider falho quarantined; próximo pode ser efetivo |
| todos providers AUTO falham | `AUTO` | `CHAIN_EXHAUSTED` + `AI_PROVIDER_CHAIN_EXHAUSTED` |

# Logging

O nível de logging é configurado pela configuração de aplicação. O formato padrão é:

```text
<timestamp> <LEVEL> <logger>: <message>
```

M18 emite logs sanitizados de tentativa e sessão quando o nível permite. Eles podem conter:

- audit ID;
- URL/device;
- provider/model/depth;
- status;
- duração;
- token counts reportados;
- custo estimado;
- `error_class`.

Não contêm API key, Authorization ou body integral.

A aplicação não cria `audit.log` automaticamente. Para registro persistente de IA, consulte `audit.db` e `report.html`.

# Segurança

Nunca coloque credenciais em arquivos versionados. Valide presença sem imprimir valores:

```powershell
Test-Path Env:OPENAI_API_KEY
Test-Path Env:DEEPSEEK_API_KEY
Test-Path Env:MIMO_API_KEY
```

# Configurações não expostas pela interface operacional

A menos que sejam adicionadas explicitamente à CLI/configuração em versão futura, não há flags públicas para:

- viewport customizado;
- lista customizada de crawlers;
- pesos de scoring;
- thresholds de consolidação;
- endpoint customizado de provider via CLI;
- prompt customizado;
- diretório individual de artifacts;
- formato de relatório diferente de HTML;
- desabilitar screenshots isoladamente;
- forçar selector inventado.

# Referências

- [Referência completa da CLI](CLI_REFERENCE.md)
- [Guia de IA](AI_GUIDE.md)
- [Compatibilidade](COMPATIBILITY.md)
- [Troubleshooting](TROUBLESHOOTING.md)