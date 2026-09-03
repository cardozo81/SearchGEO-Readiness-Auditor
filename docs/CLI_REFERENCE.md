# CLI_REFERENCE.md

Referência operacional da linha de comando do SearchGEO Readiness Auditor.

## Sintaxe global

```text
searchgeo [--config PATH] [--version] [-h|--help] audit [target ...] [opções]
```

## Parâmetros globais

| Parâmetro | Default | Descrição |
|---|---|---|
| `-h`, `--help` | — | Ajuda do comando atual. |
| `--version` | — | Exibe versão do package. |
| `--config PATH` | — | Caminho de `searchgeo.toml`; atualmente usado para configuração de logging. |

## `searchgeo audit`

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

### Glossário completo de argumentos

| Argumento | Tipo / valores | Default | Regra |
|---|---|---|---|
| `target` | domínio ou URL HTTP(S), zero ou mais posicionais | — | Ao menos um target deve vir por posição ou `--urls-file`. Um target posicional usa modo tradicional; dois ou mais formam `URL_SET`. |
| `--urls-file PATH` | arquivo UTF-8 | — | Uma URL/domínio por linha; vazias e linhas iniciadas por `#` são ignoradas. O modo é `URL_SET` mesmo se sobrar uma URL válida. |
| `--project TEXT` | texto | hostname/target | Nome humano da auditoria. |
| `--language CODE` | texto | `pt-BR` | Contexto primário de idioma. |
| `--market CODE` | texto | `BR` | Contexto de mercado. |
| `--max-pages N` | inteiro > 0 | `100` | Limite determinístico. Em `URL_SET`, deve ser >= quantidade de URLs únicas fornecidas. |
| `--audits-root PATH` | diretório | `audits` | Raiz local dos workspaces. |
| `--device-context` | `mobile`, `desktop`, `both` | `mobile`* | Controla rendering e os contextos semânticos/IA. `*` Pode ser definido por `SEARCHGEO_DEVICE_CONTEXT` quando a flag não é passada. |
| `--ai-provider` | `none`, `openai`, `deepseek`, `mimo`, `auto` | `none` | Provider semântico. A credencial deve pertencer ao produto/plano de API compatível. |
| `--ai-model MODEL_ID` | model ID suportado | default do provider | Somente para provider explícito. Não pode ser combinado com `--ai-provider auto`. |
| `--ai-content-remediation` | boolean flag | `false`* | Habilita M20 para sugerir texto exato com base em findings/evidências persistidos. `*` Pode ser definido por `SEARCHGEO_AI_CONTENT_REMEDIATION`. |
| `--no-ai-content-remediation` | boolean flag | — | Força M20 textual desligado mesmo quando a variável de ambiente está habilitada. |

## Contexto de dispositivo

Precedência:

1. `--device-context`;
2. `SEARCHGEO_DEVICE_CONTEXT`;
3. default CLI `mobile`.

Valores válidos:

```text
mobile
desktop
both
```

Exemplos:

```powershell
searchgeo audit https://example.com --device-context mobile
searchgeo audit https://example.com --device-context desktop
searchgeo audit https://example.com --device-context both
```

`mobile` produz apenas snapshots Mobile; `desktop`, apenas Desktop; `both`, ambos e habilita a comparação Desktop × Mobile completa. M7/M20 só podem chamar provider para snapshots realmente materializados.

Chamadas internas diretas a M3 sem a variável preservam `both` por compatibilidade interna/testes; isso não altera o default público da CLI.

## Exemplos de execução

### Mobile + sem IA — defaults

```powershell
searchgeo audit https://example.com --project "Exemplo"
```

Nenhuma chamada externa. A revisão determinística de JSON-LD continua disponível em `report/content-suggestions.html`.

### Mobile + OpenAI

```powershell
$env:OPENAI_API_KEY = "<chave-da-API-Platform>"
searchgeo audit https://example.com `
  --project "Exemplo" `
  --device-context mobile `
  --ai-provider openai
```

### Mobile + OpenAI + sugestões M20

```powershell
$env:OPENAI_API_KEY = "<chave-da-API-Platform>"
searchgeo audit https://example.com `
  --device-context mobile `
  --ai-provider openai `
  --ai-content-remediation
```

M20 é uma finalidade posterior à avaliação: não altera Score, Coverage, Confidence, RuleExecution ou Finding e exige revisão humana antes de qualquer publicação.

### URL_SET

```powershell
searchgeo audit `
  https://example.com/ `
  https://example.com/produto `
  https://example.com/faq `
  --project "Exemplo" `
  --max-pages 3
```

### Arquivo

```powershell
searchgeo audit --urls-file .\urls.txt --project "Exemplo"
```

## M20 — remediação de conteúdo

Precedência:

1. `--ai-content-remediation` ou `--no-ai-content-remediation`;
2. `SEARCHGEO_AI_CONTENT_REMEDIATION`;
3. `false`.

Valores aceitos para a variável:

```text
true / false
1 / 0
yes / no
on / off
```

Regras operacionais:

- `Confidence LOW` isoladamente nunca dispara sugestão;
- entram somente findings contentuais/semânticos elegíveis já persistidos;
- evidence IDs retornados precisam pertencer ao finding;
- proposta não pode inventar claims, preços, datas, estatísticas, garantias, credenciais ou experiência;
- novos tokens numéricos ausentes do conteúdo/evidência são rejeitados pelo contrato local;
- provider/model/timeout seguem a configuração já selecionada;
- quarantine é respeitada e provider não é reativado só para M20;
- falha M20 não vira finding do website;
- texto nunca é aplicado automaticamente.

### JSON-LD

A revisão JSON-LD é determinística e independe de habilitar M20 textual.

Se JSON-LD não existe, o auditor pode propor um baseline `WebPage` com dados efetivamente observados/persistidos, como URL, idioma, `<title>` e meta description. Se existe, o auditor não sobrescreve o graph: aponta parse errors, duplicações e oportunidades estruturais verificáveis.

JSON-LD é `OPCIONAL / REFORÇO`, não requisito universal GEO nem garantia de rich result.

## Providers de IA e compatibilidade de plano

Antes de preencher uma variável de credencial, confirme o produto/plano. Consulte [AI_GUIDE.md](AI_GUIDE.md).

### `none`

Nenhuma chamada externa. Regras semantic-only sem evidência suficiente permanecem `UNKNOWN`. Se M20 textual estiver habilitado, ele registra `NOT_CONFIGURED` sem abortar; JSON-LD determinístico permanece disponível.

### `openai`

```powershell
$env:OPENAI_API_KEY = "<chave-da-API-Platform>"
searchgeo audit https://example.com --ai-provider openai
```

Default: `gpt-5.6-terra`.

Requisito comercial: billing/quota da **OpenAI API Platform**. Assinaturas/créditos do ChatGPT são separados e não substituem saldo/quota da API.

### `deepseek`

```powershell
$env:DEEPSEEK_API_KEY = "<chave-da-DeepSeek-API>"
searchgeo audit https://example.com --ai-provider deepseek
```

Default: `deepseek-v4-pro`. `HTTP 402` indica saldo insuficiente da DeepSeek API.

### `mimo`

```powershell
$env:MIMO_API_KEY = "<chave-sk-PAYG>"
searchgeo audit https://example.com --ai-provider mimo
```

Default: `mimo-v2.5-pro`.

O adapter atual usa MiMo Pay-as-you-go em `https://api.xiaomimimo.com/v1/responses`; portanto a credencial esperada é `sk-...`.

**MiMo Token Plan `tp-...` não é suportado pelo SearchGEO atual.** Ele usa Base URL e créditos separados e não deve ser configurado em `MIMO_API_KEY` para este adapter.

### `auto`

```powershell
searchgeo audit https://example.com --ai-provider auto
```

A cadeia é formada uma vez com providers elegíveis/configurados. O primeiro resultado válido encerra o contexto. A existência da variável não prova compatibilidade comercial da credencial.

## Isolamento de credenciais

Cada provider usa apenas sua própria credencial. `OPENAI_API_KEY` não pode preencher ausência de `DEEPSEEK_API_KEY` ou `MIMO_API_KEY`, e vice-versa. Essa regra também é coberta por teste de regressão para impedir chamadas externas acidentais com credencial ambiental.

## Modelos aceitos

```text
OPENAI
  gpt-5.6-sol
  gpt-5.6-terra
  gpt-5.6-luna

DEEPSEEK
  deepseek-v4-pro
  deepseek-v4-flash

MIMO
  mimo-v2.5-pro
  mimo-v2.5
```

Em `auto`, modelos são definidos pelas variáveis específicas do provider; `--ai-model` é rejeitado. Model ID aceito pelo código não garante acesso operacional da conta/plano.

## Variáveis de ambiente

| Variável | Default | Uso |
|---|---|---|
| `SEARCHGEO_DEVICE_CONTEXT` | `mobile` na CLI | `mobile`, `desktop`, `both`. |
| `SEARCHGEO_AI_TIMEOUT_SECONDS` | `180` | Timeout por chamada externa; número finito > 0. |
| `SEARCHGEO_AI_CONTENT_REMEDIATION` | `false` | Habilita/desabilita M20 textual quando a flag não é usada. |
| `OPENAI_API_KEY` | — | Credencial da OpenAI API Platform. |
| `DEEPSEEK_API_KEY` | — | Credencial da DeepSeek API. |
| `MIMO_API_KEY` | — | MiMo PAYG `sk-...`; Token Plan `tp-...` não suportado. |
| `SEARCHGEO_OPENAI_MODEL` | `gpt-5.6-terra` | Model OpenAI no AUTO/env. |
| `SEARCHGEO_DEEPSEEK_MODEL` | `deepseek-v4-pro` | Model DeepSeek. |
| `SEARCHGEO_MIMO_MODEL` | `mimo-v2.5-pro` | Model MiMo. |

## Provider sem chave

Provider explícito sem token fica `NOT_CONFIGURED`, não chama API e não é afetado por chaves ausentes/presentes de outros providers. Em `auto`, providers sem token são excluídos.

Credencial de produto/plano incompatível não deve ser tratada como válida apenas porque a variável existe.

## Falha / quota / crédito / timeout

Provider explícito não faz cross-provider fallback. `auto` pode quarantinar provider falho e seguir para outro saudável conforme contrato. Não há retry automático de timeout.

Antes de concluir “sem crédito”, verifique produto/plano, endpoint, tipo de chave, limite de gasto e model access. No MiMo, `401` pode indicar mistura Token Plan/PAYG e `402` no endpoint PAYG representa saldo PAYG insuficiente.

## Saída da CLI

```text
Auditoria concluída: AUD-...
Status: COMPLETE_WITH_LIMITATIONS
Páginas auditadas: ...
Contexto de dispositivo: MOBILE
Sugestões de conteúdo por IA: DESABILITADAS
Problemas identificados: ...
Recomendações: ...
Relatório: audits\AUD-...\report\index.html
Relatório por problemas: audits\AUD-...\report\remediation.html
Conteúdo e JSON-LD: audits\AUD-...\report\content-suggestions.html
```

## Estrutura do report site

```text
report/
├─ index.html
├─ mobile.html             # condicional
├─ desktop.html            # condicional
├─ remediation.html
├─ content-suggestions.html
├─ ai-usage.html
├─ references.html
└─ css/
   └─ site.css
```

M18/M20 telemetry fica em `ai-usage.html`; sugestões textuais e revisão JSON-LD ficam em `content-suggestions.html`.

## Regras de target

- somente HTTP/HTTPS;
- domínio sem scheme é aceito sem path/query/fragment;
- URL com path/query/fragment deve incluir scheme;
- credenciais embutidas são rejeitadas;
- URL_SET deve pertencer à mesma origem normalizada.

## Ajuda local

```powershell
searchgeo --help
searchgeo audit --help
```
