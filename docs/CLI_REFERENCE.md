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
| `--ai-provider` | `none`, `openai`, `deepseek`, `mimo`, `auto` | `none` | Provider semântico. |
| `--ai-model MODEL_ID` | model ID suportado | default do provider | Somente para provider explícito. Não pode ser combinado com `--ai-provider auto`. |
| `--ai-content-remediation` | boolean flag | `false`* | Habilita M20 para sugerir texto exato com base em findings/evidências persistidos. `*` Pode ser definido por `SEARCHGEO_AI_CONTENT_REMEDIATION`. |
| `--no-ai-content-remediation` | boolean flag | — | Força M20 textual como desligado, mesmo quando a variável de ambiente está habilitada. |

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

`mobile` produz apenas snapshots Mobile. Com IA habilitada, somente esses snapshots entram no fluxo semântico e, quando M20 estiver habilitado, somente esses contextos podem gerar chamadas de remediação, reduzindo custo em comparação a `both`.

`desktop` faz o mesmo para Desktop. `both` produz os dois contextos e habilita a comparação Desktop × Mobile completa.

Chamadas internas diretas a M3 sem a variável preservam o comportamento legado `both`; essa exceção existe para compatibilidade de API interna/testes e não altera o default da CLI.

## Exemplos de execução

### Mobile + sem IA — defaults

```powershell
searchgeo audit https://example.com --project "Exemplo"
```

Neste modo não há chamada externa. A auditoria ainda produz a revisão determinística de JSON-LD por página em `report/content-suggestions.html`.

### Mobile + OpenAI

```powershell
$env:OPENAI_API_KEY = "<chave>"
searchgeo audit https://example.com `
  --project "Exemplo" `
  --device-context mobile `
  --ai-provider openai
```

### Mobile + OpenAI + sugestões textuais M20

```powershell
$env:OPENAI_API_KEY = "<chave>"
searchgeo audit https://example.com `
  --device-context mobile `
  --ai-provider openai `
  --ai-content-remediation
```

M20 é uma segunda finalidade de IA. Ele roda somente depois de scoring/findings, não altera retrospectivamente Score, Coverage, Confidence, RuleExecution ou Finding e exige revisão humana antes de qualquer publicação.

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

## Remediação de conteúdo M20

A precedência é:

1. `--ai-content-remediation` ou `--no-ai-content-remediation`;
2. `SEARCHGEO_AI_CONTENT_REMEDIATION`;
3. default `false`.

Valores aceitos para a variável:

```text
true / false
1 / 0
yes / no
on / off
```

Regras operacionais:

- `Confidence LOW` isoladamente nunca dispara sugestão;
- entram apenas findings contentuais/semânticos elegíveis já persistidos;
- evidence IDs retornados precisam pertencer ao próprio finding;
- a proposta não pode inventar claims, preços, datas, estatísticas, garantias, credenciais ou experiência;
- novos tokens numéricos ausentes do conteúdo/evidências fornecidos são rejeitados pelo contrato local;
- provider/model/timeout seguem a configuração M18 já selecionada;
- M20 herda provider quarantine e roteamento/URL lock do audit;
- falha de M20 é estado operacional e não vira finding do website;
- o texto nunca é aplicado automaticamente.

### JSON-LD

A revisão JSON-LD é **determinística e não depende de habilitar M20 textual**.

Quando JSON-LD não existe, o auditor pode propor um baseline seguro `WebPage` com dados observados/persistidos, como URL, idioma, `<title>` e meta description. Quando já existe, o auditor não o sobrescreve: aponta parse errors, duplicações e oportunidades estruturais genéricas verificáveis.

JSON-LD continua sendo reforço opcional. Não é requisito universal de GEO, não existe markup especial GEO/AEO e markup correto não garante rich result.

## Providers de IA

### `none`

Nenhuma chamada externa. Regras semantic-only sem evidência suficiente permanecem `UNKNOWN`. Isso pode reduzir Coverage/Consolidation, mas não é `FAIL` do website. Se `--ai-content-remediation` for passado com `--ai-provider none`, a etapa textual fica `NOT_CONFIGURED` sem abortar o audit; a revisão JSON-LD determinística permanece disponível.

### `openai`

```powershell
$env:OPENAI_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider openai
```

Default:

```text
gpt-5.6-terra
```

### `deepseek`

```powershell
$env:DEEPSEEK_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider deepseek
```

Default:

```text
deepseek-v4-pro
```

### `mimo`

```powershell
$env:MIMO_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider mimo
```

Default:

```text
mimo-v2.5-pro
```

### `auto`

```powershell
searchgeo audit https://example.com --ai-provider auto
```

A cadeia é formada uma vez por audit com providers que possuem token e configuração válida. Execução sequencial; primeiro resultado válido encerra o contexto. Providers posteriores não sobrescrevem o resultado aceito.

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

## Variáveis de ambiente

| Variável | Default | Uso |
|---|---|---|
| `SEARCHGEO_DEVICE_CONTEXT` | `mobile` na CLI | `mobile`, `desktop`, `both`. |
| `SEARCHGEO_AI_TIMEOUT_SECONDS` | `180` | Timeout por chamada externa de IA; número finito > 0. |
| `SEARCHGEO_AI_CONTENT_REMEDIATION` | `false` | Habilita/desabilita sugestões textuais M20 quando a flag CLI não é usada. |
| `OPENAI_API_KEY` | — | Credencial OpenAI. |
| `DEEPSEEK_API_KEY` | — | Credencial DeepSeek. |
| `MIMO_API_KEY` | — | Credencial MiMo. |
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

M20 não cria uma segunda credencial: reutiliza providers elegíveis do M18. Se o provider já foi colocado em quarantine pela etapa semântica, ele não é reativado só para gerar remediação.

## Falha / quota / crédito / timeout

Provider explícito:

- não faz cross-provider fallback;
- após falha qualificadora é quarantined para o restante do audit.

`auto`:

- provider falho é quarantined;
- próximo provider saudável pode atender contextos elegíveis;
- se a cadeia inteira falhar, a falha fica explícita na telemetria.

Não há retry automático de timeout, evitando potencial duplicação de consumo.

## Saída da CLI

Exemplo:

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

O ponto de entrada é `report/index.html`.

## Estrutura do report site

```text
report/
├─ index.html
├─ mobile.html             # se Mobile foi auditado
├─ desktop.html            # se Desktop foi auditado
├─ remediation.html
├─ content-suggestions.html
├─ ai-usage.html
├─ references.html
└─ css/
   └─ site.css
```

A telemetria M18 e M20 fica em `ai-usage.html`, separada do readiness do website. Sugestões de conteúdo e revisão JSON-LD ficam em `content-suggestions.html`. Referências oficiais, metodologia e fórmulas ficam em `references.html`.

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
