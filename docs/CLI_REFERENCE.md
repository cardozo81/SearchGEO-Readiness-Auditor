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

## Contexto de dispositivo

A precedência é:

1. `--device-context`;
2. `SEARCHGEO_DEVICE_CONTEXT`;
3. default CLI `mobile`.

Valores válidos:

```text
mobile
desktop
both
```

Forma recomendada:

```powershell
searchgeo audit https://example.com --device-context mobile
searchgeo audit https://example.com --device-context desktop
searchgeo audit https://example.com --device-context both
```

Ou por ambiente:

```powershell
$env:SEARCHGEO_DEVICE_CONTEXT = "mobile"
```

`mobile` produz apenas snapshots Mobile. Com IA habilitada, somente esses snapshots entram no fluxo semântico, reduzindo chamadas e custo em comparação a `both`.

`desktop` faz o mesmo para Desktop. `both` produz os dois contextos e habilita a comparação Desktop × Mobile completa.

Chamadas internas diretas a M3 sem a variável preservam o comportamento legado `both`; essa exceção existe para compatibilidade de API interna/testes e não altera o default da CLI.

## Exemplos de execução

### Mobile + sem IA — defaults

```powershell
searchgeo audit https://example.com --project "Exemplo"
```

### Mobile + OpenAI

```powershell
$env:OPENAI_API_KEY = "<chave-da-API-Platform>"
searchgeo audit https://example.com `
  --project "Exemplo" `
  --device-context mobile `
  --ai-provider openai
```

### Desktop apenas

```powershell
searchgeo audit https://example.com --device-context desktop
```

### Comparação completa

```powershell
searchgeo audit https://example.com --device-context both
```

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

## Providers de IA

Antes de preencher uma variável de credencial, confirme o produto/plano. A referência detalhada está em [AI_GUIDE.md](AI_GUIDE.md).

### `none`

Nenhuma chamada externa. Regras semantic-only sem evidência suficiente permanecem `UNKNOWN`. Isso pode reduzir Coverage/Consolidation, mas não é `FAIL` do website.

### `openai`

```powershell
$env:OPENAI_API_KEY = "<chave-da-API-Platform>"
searchgeo audit https://example.com --ai-provider openai
```

Default:

```text
gpt-5.6-terra
```

Requisito comercial: billing/quota da **OpenAI API Platform**. Assinaturas e créditos do ChatGPT são separados da API e não substituem saldo/quota da organização/projeto de API.

### `deepseek`

```powershell
$env:DEEPSEEK_API_KEY = "<chave-da-DeepSeek-API>"
searchgeo audit https://example.com --ai-provider deepseek
```

Default:

```text
deepseek-v4-pro
```

O saldo da API pode incluir saldo concedido e recarregado. `HTTP 402` indica saldo insuficiente.

### `mimo`

```powershell
$env:MIMO_API_KEY = "<chave-sk-PAYG>"
searchgeo audit https://example.com --ai-provider mimo
```

Default:

```text
mimo-v2.5-pro
```

O adapter atual usa MiMo **Pay-as-you-go** em `https://api.xiaomimimo.com/v1/responses`; portanto a credencial esperada é `sk-...`.

**MiMo Token Plan `tp-...` não é suportado pelo SearchGEO atual.** Ele usa Base URL dedicada por região e créditos independentes. A documentação oficial da MiMo restringe esse pacote a ferramentas de programação e proíbe automated scripts/custom application backends fora desse escopo.

### `auto`

```powershell
searchgeo audit https://example.com --ai-provider auto
```

A cadeia é formada uma vez por audit com providers que possuem token e configuração válida. Execução sequencial; primeiro resultado válido encerra o contexto. Providers posteriores não sobrescrevem o resultado aceito.

A existência da variável não prova compatibilidade comercial da credencial. Em particular, não configure `MIMO_API_KEY` com `tp-...`.

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

Em `auto`, modelos são definidos pelas variáveis específicas de provider; `--ai-model` é rejeitado.

Model ID aceito pelo SearchGEO não garante que toda conta/plano tenha acesso ao modelo. O provider pode aplicar permissões, tiers, quotas, limites de gasto ou rate limits próprios.

## Variáveis de ambiente

| Variável | Default | Uso |
|---|---|---|
| `SEARCHGEO_DEVICE_CONTEXT` | `mobile` na CLI | `mobile`, `desktop`, `both`. |
| `SEARCHGEO_AI_TIMEOUT_SECONDS` | `180` | Timeout por chamada externa de IA; número finito > 0. |
| `OPENAI_API_KEY` | — | Credencial da OpenAI API Platform. |
| `DEEPSEEK_API_KEY` | — | Credencial da DeepSeek API. |
| `MIMO_API_KEY` | — | Credencial MiMo Pay-as-you-go `sk-...`; Token Plan `tp-...` não suportado. |
| `SEARCHGEO_OPENAI_MODEL` | `gpt-5.6-terra` | Model OpenAI no AUTO/configuração por env. |
| `SEARCHGEO_DEEPSEEK_MODEL` | `deepseek-v4-pro` | Model DeepSeek. |
| `SEARCHGEO_MIMO_MODEL` | `mimo-v2.5-pro` | Model MiMo. |

Variáveis adicionais de reasoning/depth existentes no contrato M18 continuam documentadas em [AI_GUIDE.md](AI_GUIDE.md).

## Provider sem chave

Provider explícito sem token:

- fica operacionalmente `NOT_CONFIGURED`;
- não chama API;
- auditoria continua em modo sem IA efetiva/degradado conforme o restante do pipeline;
- outras chaves ausentes não interferem.

Em `auto`, providers sem token são excluídos da cadeia.

Uma credencial de produto/plano incompatível não deve ser tratada como configuração válida apenas porque a variável existe.

## Falha / quota / crédito / timeout

Provider explícito:

- não faz cross-provider fallback;
- após falha qualificadora é quarantined para o restante do audit.

`auto`:

- provider falho é quarantined;
- próximo provider saudável pode atender URLs/contextos elegíveis seguintes;
- se a cadeia inteira falhar, estado operacional `CHAIN_EXHAUSTED`.

Não há retry automático de timeout, evitando potencial duplicação de consumo.

Antes de concluir que uma falha é “falta de crédito”, verifique também produto/plano, endpoint, tipo de chave, limite de gasto e acesso ao modelo. Para MiMo, `401` pode representar mistura Token Plan/PAYG e `402` no endpoint PAYG representa saldo PAYG insuficiente.

## Saída da CLI

Exemplo:

```text
Auditoria concluída: AUD-...
Status: COMPLETE_WITH_LIMITATIONS
Páginas auditadas: ...
Contexto de dispositivo: MOBILE
Problemas identificados: ...
Recomendações: ...
Relatório: audits\AUD-...\report\index.html
Relatório por problemas: audits\AUD-...\report\remediation.html
```

O ponto de entrada é `report/index.html`.

## Estrutura do report site

```text
report/
├─ index.html
├─ mobile.html          # se Mobile foi auditado
├─ desktop.html         # se Desktop foi auditado
├─ remediation.html
├─ ai-usage.html
├─ references.html
└─ css/
   └─ site.css
```

A telemetria de IA fica em `ai-usage.html`, separada do readiness do website. Referências oficiais, metodologia e fórmulas ficam em `references.html`.

## Regras de target

- somente HTTP/HTTPS;
- domínio sem scheme é aceito quando não contém path/query/fragment;
- URL com path/query/fragment deve incluir `http://` ou `https://`;
- credenciais embutidas na URL são rejeitadas;
- URLs de um mesmo audit `URL_SET` devem pertencer à mesma origem normalizada.

## Ajuda local

```powershell
searchgeo --help
searchgeo audit --help
```
