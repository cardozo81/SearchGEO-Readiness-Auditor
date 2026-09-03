# CLI_REFERENCE.md

Referência operacional da CLI do SearchGEO.

## Sintaxe

```text
searchgeo [--config PATH] [--version] [-h|--help] audit [target ...] [opções]
```

```text
searchgeo audit [target ...]
  [--urls-file PATH]
  [--project TEXT]
  [--language CODE]
  [--market CODE]
  [--max-pages N]
  [--audits-root PATH]
  [--device-context mobile|desktop|both]
  [--ai-provider none|openai|deepseek|mimo|auto]
  [--ai-model MODEL_ID]
  [--ai-content-remediation | --no-ai-content-remediation]
```

## Glossário completo

| Argumento | Valores/default | Regra |
|---|---|---|
| `target` | domínio/URL HTTP(S) | ao menos um target por posição ou `--urls-file`; múltiplos formam `URL_SET` |
| `--urls-file PATH` | UTF-8 | uma URL/domínio por linha; ignora vazias e `#` |
| `--project TEXT` | hostname/target | nome humano |
| `--language CODE` | `pt-BR` | idioma primário |
| `--market CODE` | `BR` | mercado |
| `--max-pages N` | `100` | inteiro > 0; URL_SET exige limite >= URLs únicas |
| `--audits-root PATH` | `audits` | raiz dos workspaces |
| `--device-context` | `mobile` | `mobile`, `desktop`, `both`; ambiente pode definir quando flag ausente |
| `--ai-provider` | `none` | `none`, `openai`, `deepseek`, `mimo`, `auto`; credencial deve pertencer ao produto de API compatível |
| `--ai-model MODEL_ID` | default do provider | só provider explícito; incompatível com `auto` |
| `--ai-content-remediation` | `false` | habilita sugestões M20 evidence-backed |
| `--no-ai-content-remediation` | — | força M20 textual OFF |

## Device context

Precedência: `--device-context` → `SEARCHGEO_DEVICE_CONTEXT` → `mobile`.

`mobile`/`desktop` geram somente o snapshot escolhido; `both` gera ambos e habilita comparação Desktop × Mobile. M7/M20 nunca devem chamar provider para device sem snapshot.

## M20

Precedência: `--ai-content-remediation`/`--no-ai-content-remediation` → `SEARCHGEO_AI_CONTENT_REMEDIATION` → `false`.

Valores de ambiente aceitos: `true/false`, `1/0`, `yes/no`, `on/off`.

Exemplo:

```powershell
$env:OPENAI_API_KEY = "<chave-da-API-Platform>"
searchgeo audit https://example.com `
  --device-context mobile `
  --ai-provider openai `
  --ai-content-remediation
```

M20 roda depois de scoring/findings, não altera avaliação, não é disparado apenas por Confidence LOW, exige finding/evidence elegível e não aplica texto automaticamente.

A revisão JSON-LD é determinística mesmo com M20 textual OFF.

## Providers e planos

Antes de configurar chave, valide [AI_GUIDE.md](AI_GUIDE.md).

### OpenAI

```powershell
$env:OPENAI_API_KEY = "<chave-da-API-Platform>"
searchgeo audit https://example.com --ai-provider openai
```

Default `gpt-5.6-terra`. ChatGPT e API possuem billing separado.

### DeepSeek

```powershell
$env:DEEPSEEK_API_KEY = "<chave-da-DeepSeek-API>"
searchgeo audit https://example.com --ai-provider deepseek
```

Default `deepseek-v4-pro`; `402` indica saldo insuficiente da API.

### MiMo

```powershell
$env:MIMO_API_KEY = "<chave-sk-PAYG>"
searchgeo audit https://example.com --ai-provider mimo
```

Default `mimo-v2.5-pro`. O adapter usa PAYG `https://api.xiaomimimo.com/v1/responses`. Token Plan `tp-...` não é suportado e não deve ser usado.

### AUTO

```powershell
searchgeo audit https://example.com --ai-provider auto
```

Cadeia imutável com providers elegíveis; primeiro resultado válido encerra o contexto. A existência de uma variável não prova que o plano/credencial seja compatível.

## Modelos aceitos

```text
OPENAI:   gpt-5.6-sol | gpt-5.6-terra | gpt-5.6-luna
DEEPSEEK: deepseek-v4-pro | deepseek-v4-flash
MIMO:     mimo-v2.5-pro | mimo-v2.5
```

## Variáveis de ambiente

| Variável | Default | Uso |
|---|---|---|
| `SEARCHGEO_DEVICE_CONTEXT` | `mobile` na CLI | device |
| `SEARCHGEO_AI_TIMEOUT_SECONDS` | `180` | timeout externo |
| `SEARCHGEO_AI_CONTENT_REMEDIATION` | `false` | M20 textual |
| `OPENAI_API_KEY` | — | OpenAI API Platform |
| `DEEPSEEK_API_KEY` | — | DeepSeek API |
| `MIMO_API_KEY` | — | MiMo PAYG `sk-...` |
| `SEARCHGEO_OPENAI_MODEL` | `gpt-5.6-terra` | modelo AUTO/env |
| `SEARCHGEO_DEEPSEEK_MODEL` | `deepseek-v4-pro` | modelo |
| `SEARCHGEO_MIMO_MODEL` | `mimo-v2.5-pro` | modelo |

Provider explícito sem chave fica `NOT_CONFIGURED`; outras chaves não interferem. Credenciais são isoladas por provider e nunca devem fazer fallback entre endpoints.

Timeout não gera retry automático.

## Saída

```text
Auditoria concluída: AUD-...
Status: ...
Páginas auditadas: ...
Contexto de dispositivo: MOBILE
Sugestões de conteúdo por IA: DESABILITADAS
Problemas identificados: ...
Recomendações: ...
Relatório: audits\AUD-...\report\index.html
Relatório por problemas: audits\AUD-...\report\remediation.html
Conteúdo e JSON-LD: audits\AUD-...\report\content-suggestions.html
```

## Report site

```text
report/
├─ index.html
├─ mobile.html             # condicional
├─ desktop.html            # condicional
├─ remediation.html
├─ content-suggestions.html
├─ ai-usage.html
├─ references.html
└─ css/site.css
```

## Target

Somente HTTP/HTTPS; credenciais embutidas são rejeitadas; URL_SET deve manter mesma origem normalizada.

## Ajuda

```powershell
searchgeo --help
searchgeo audit --help
```
