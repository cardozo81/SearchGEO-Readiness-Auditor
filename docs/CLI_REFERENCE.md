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
  [--ai-provider none|openai|deepseek|mimo|auto|xai|grok|qwen|gemini|anthropic|claude]
  [--ai-model MODEL_ID]
  [--ai-content-remediation | --no-ai-content-remediation]
  [--web-performance | --no-web-performance]
  [--web-performance-max-pages N]
  [--web-performance-timeout-seconds SECONDS]
  [--web-performance-field-source auto|pagespeed|crux|none]
  [--lighthouse-categories LIST]
```

### Glossário completo de argumentos

| Argumento | Tipo / valores | Default | Regra |
|---|---|---|---|
| `target` | domínio ou URL HTTP(S), zero ou mais posicionais | — | Ao menos um target deve vir por posição ou `--urls-file`. Um target posicional usa modo tradicional; dois ou mais formam `URL_SET`. |
| `--urls-file PATH` | arquivo UTF-8 | — | Uma URL/domínio por linha; vazias e linhas iniciadas por `#` são ignoradas. O modo é `URL_SET` mesmo se sobrar uma URL válida. |
| `--project TEXT` | texto | hostname/target | Nome humano da auditoria. |
| `--language CODE` | texto | `pt-BR` | Contexto primário de idioma. |
| `--market CODE` | texto | `BR` | Contexto de mercado. |
| `--max-pages N` | inteiro > 0 | `100` | Limite determinístico da auditoria. Em `URL_SET`, deve ser >= quantidade de URLs únicas fornecidas. |
| `--audits-root PATH` | diretório | `audits` | Raiz local dos workspaces. |
| `--device-context` | `mobile`, `desktop`, `both` | `mobile`* | Controla rendering e os contextos semânticos/IA; também limita M21 aos snapshots realmente materializados. `*` Pode ser definido por `SEARCHGEO_DEVICE_CONTEXT` quando a flag não é passada. |
| `--ai-provider` | `none`, `openai`, `deepseek`, `mimo`, `auto`, `xai`, `grok`, `qwen`, `gemini`, `anthropic`, `claude` | `none` | Provider semântico. xAI/Qwen/Gemini/Anthropic são `PROVISIONAL` e explicit-only; não entram em `auto`. |
| `--ai-model MODEL_ID` | model ID suportado | default do provider | Somente para provider explícito. Não pode ser combinado com `--ai-provider auto`. |
| `--ai-content-remediation` | boolean flag | `false`* | Habilita M20 para sugerir texto exato com base em findings/evidências persistidos. `*` Pode ser definido por `SEARCHGEO_AI_CONTENT_REMEDIATION`. |
| `--no-ai-content-remediation` | boolean flag | — | Força M20 textual desligado mesmo quando a variável de ambiente está habilitada. |
| `--web-performance` | boolean flag | `false`* | Habilita M21: PageSpeed/Lighthouse + Core Web Vitals/CrUX quando disponível. `*` Pode ser definido por `SEARCHGEO_WEB_PERFORMANCE`. Não altera `SCORE-GEO-002`. |
| `--no-web-performance` | boolean flag | — | Força M21 desligado mesmo quando `SEARCHGEO_WEB_PERFORMANCE=true`. |
| `--web-performance-max-pages N` | inteiro >= 0 | `10`* | Limita páginas lógicas enviadas aos serviços externos M21; `0` = todas. `*` Pode vir de `SEARCHGEO_WEB_PERFORMANCE_MAX_PAGES`. |
| `--web-performance-timeout-seconds SECONDS` | número finito > 0 | `60`* | Timeout por request PageSpeed/CrUX. `*` Pode vir de `SEARCHGEO_WEB_PERFORMANCE_TIMEOUT_SECONDS`. Sem retry automático. |
| `--web-performance-field-source` | `auto`, `pagespeed`, `crux`, `none` | `auto`* | Política de field data. `crux` exige `SEARCHGEO_CRUX_API_KEY`. `*` Pode vir de `SEARCHGEO_WEB_PERFORMANCE_FIELD_SOURCE`. |
| `--lighthouse-categories LIST` | lista separada por vírgulas | `performance,accessibility,best-practices,seo`* | Categorias oficiais aceitas. `*` Pode vir de `SEARCHGEO_LIGHTHOUSE_CATEGORIES`. |

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

Quando M21 está habilitado, o mesmo universo de snapshots controla PageSpeed/CrUX:

```text
MOBILE  → PageSpeed strategy=mobile  → CrUX PHONE
DESKTOP → PageSpeed strategy=desktop → CrUX DESKTOP
```

Chamadas internas diretas a M3 sem a variável preservam `both` por compatibilidade interna/testes; isso não altera o default público da CLI.

## Exemplos de execução

### Mobile + sem IA + sem medição externa — defaults

```powershell
searchgeo audit https://example.com --project "Exemplo"
```

Não há chamada de IA nem PageSpeed/CrUX por default. A revisão determinística de JSON-LD continua disponível em `report/content-suggestions.html`. `SCORE-GEO-002` continua sendo calculado conforme as regras aplicáveis.

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

### xAI / Grok — explicit-only

```powershell
$env:XAI_API_KEY = "<xai-api-key>"
searchgeo audit https://example.com --ai-provider xai
```

Alias: `--ai-provider grok`. Default: `grok-4.6`.

### Alibaba Qwen — explicit-only

```powershell
$env:DASHSCOPE_API_KEY = "<model-studio-api-key>"
searchgeo audit https://example.com --ai-provider qwen
```

Default: `qwen3.8-max`. Se a key pertencer a outra região/workspace, configure `SEARCHGEO_QWEN_ENDPOINT` compatível com o mesmo deployment.

### Google Gemini — explicit-only

```powershell
$env:GEMINI_API_KEY = "<gemini-api-key>"
searchgeo audit https://example.com --ai-provider gemini
```

Default: `gemini-3.8-flash`.

### Anthropic Claude — explicit-only

```powershell
$env:ANTHROPIC_API_KEY = "<anthropic-api-key>"
searchgeo audit https://example.com --ai-provider anthropic
```

Alias: `--ai-provider claude`. Default: `claude-sonnet-5`.

### Provider de extensão + M20

```powershell
$env:ANTHROPIC_API_KEY = "<anthropic-api-key>"
searchgeo audit https://example.com `
  --ai-provider anthropic `
  --ai-content-remediation
```

Provider quarantined durante M7 não é reativado para M20.

### Mobile + Lighthouse/Core Web Vitals, sem IA

```powershell
searchgeo audit https://example.com `
  --ai-provider none `
  --device-context mobile `
  --web-performance
```

M21 não chama LLM. O consumo externo adicional é PageSpeed e, conforme a política configurada e disponibilidade de chave, CrUX.

### Web Performance com limite de consumo

```powershell
searchgeo audit https://example.com `
  --max-pages 100 `
  --web-performance `
  --web-performance-max-pages 5 `
  --web-performance-timeout-seconds 45
```

Neste exemplo o crawl pode auditar até 100 páginas, porém no máximo 5 páginas lógicas entram em M21. Com `--device-context mobile`, isso representa no máximo 5 contextos PageSpeed; com `both`, até 10 contextos PageSpeed.

### Lighthouse somente, sem field data

```powershell
searchgeo audit https://example.com `
  --web-performance `
  --web-performance-field-source none
```

### CrUX direto como field data

```powershell
$env:SEARCHGEO_CRUX_API_KEY = "<google-api-key>"
searchgeo audit https://example.com `
  --web-performance `
  --web-performance-field-source crux
```

PageSpeed continua sendo usado para Lighthouse lab; CrUX API direta fornece field data.

### PageSpeed com chave opcional

```powershell
$env:SEARCHGEO_PAGESPEED_API_KEY = "<google-api-key>"
searchgeo audit https://example.com --web-performance
```

A chave PageSpeed não é credencial de IA e nunca é persistida no `audit.db`, artifacts ou HTML.

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

## M21 — Web Performance externo

### Natureza

M21 apresenta métricas externas de web performance separadas do modelo heurístico SearchGEO:

```text
SCORE-GEO-002  → readiness heurístico interno
Lighthouse     → laboratório externo
CrUX/CWV       → experiência real agregada quando há amostra suficiente
```

Nenhum cálculo faz média ou combinação automática entre esses três conceitos.

### Precedência de ativação

1. `--web-performance` ou `--no-web-performance`;
2. `SEARCHGEO_WEB_PERFORMANCE`;
3. `false`.

Valores booleanos aceitos na variável:

```text
true / false
1 / 0
yes / no
on / off
```

### Field source

`auto`:

1. executa PageSpeed para Lighthouse;
2. usa CrUX field data vindo na resposta PageSpeed enquanto disponível;
3. se não vier field data e `SEARCHGEO_CRUX_API_KEY` existir, consulta CrUX API direta;
4. sem amostra, registra `UNAVAILABLE/INCOMPLETE`, não website FAIL.

`pagespeed`: não faz fallback CrUX direto.

`crux`: exige `SEARCHGEO_CRUX_API_KEY`; field data vem da CrUX API direta.

`none`: Lighthouse lab continua, field data fica desabilitado.

### Core Web Vitals

Thresholds oficiais atuais de boa experiência no percentil 75:

```text
LCP <= 2500 ms
INP <= 200 ms
CLS <= 0.10
```

Assessment M21:

```text
PASS
FAIL
INCOMPLETE
UNAVAILABLE
```

`INCOMPLETE`/`UNAVAILABLE` qualificam a medição e não são penalidade do website.

### Lighthouse

Quando retornados pelo PageSpeed, são persistidos/exibidos:

```text
Performance
Accessibility
Best Practices
SEO
FCP
Speed Index
LCP
TBT
CLS
Lighthouse version/fetch time
```

O score Lighthouse é apresentado exatamente como score Lighthouse; não recebe o nome `Score GEO`.

### Custos/quota

M21 não gera tokens de nenhum provider LLM.

O consumo potencial é de APIs Google:

- PageSpeed Insights;
- CrUX API direta somente quando configurada/política exigir.

Use `--web-performance-max-pages` para limitar volume. `0` significa todos os pages auditados e deve ser usado conscientemente em auditorias grandes.

PageSpeed suporta uso sem chave em cenário ad hoc/baixo volume segundo documentação oficial, mas chave é recomendada para automação frequente. CrUX API direta exige chave.

## Providers de IA e compatibilidade de plano

Antes de preencher uma variável de credencial, confirme o produto/plano. Consulte [AI_GUIDE.md](AI_GUIDE.md) e [AI_PROVIDER_EXTENSIONS.md](AI_PROVIDER_EXTENSIONS.md).

### `none`

Nenhuma chamada de IA externa. Regras semantic-only sem evidência suficiente permanecem `UNKNOWN`. Se M20 textual estiver habilitado, ele registra `NOT_CONFIGURED` sem abortar; JSON-LD determinístico permanece disponível.

A opção `--web-performance` é independente de `--ai-provider`: pode ser usada com `none`, porque PageSpeed/CrUX não são SemanticProviders.

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

### `xai` / `grok`

```powershell
$env:XAI_API_KEY = "<xai-api-key>"
searchgeo audit https://example.com --ai-provider xai
```

Default `grok-4.6`. Estado `PROVISIONAL`, explicit-only.

### `qwen`

```powershell
$env:DASHSCOPE_API_KEY = "<model-studio-api-key>"
searchgeo audit https://example.com --ai-provider qwen
```

Default `qwen3.8-max`; `qwen3.8-flash` também é aceito. Estado `PROVISIONAL`, explicit-only. Endpoint pode variar por região/workspace.

### `gemini`

```powershell
$env:GEMINI_API_KEY = "<gemini-api-key>"
searchgeo audit https://example.com --ai-provider gemini
```

Default `gemini-3.8-flash`. Estado `PROVISIONAL`, explicit-only.

### `anthropic` / `claude`

```powershell
$env:ANTHROPIC_API_KEY = "<anthropic-api-key>"
searchgeo audit https://example.com --ai-provider anthropic
```

Default `claude-sonnet-5`. Estado `PROVISIONAL`, explicit-only.

### `auto`

```powershell
searchgeo audit https://example.com --ai-provider auto
```

A cadeia homologada continua **exatamente**:

```text
OpenAI -> DeepSeek -> MiMo
```

Ela é formada uma vez com providers legacy elegíveis/configurados. O primeiro resultado válido encerra o contexto. xAI/Qwen/Gemini/Anthropic não entram em AUTO enquanto estiverem provisórios, mesmo que suas keys existam.

## Isolamento de credenciais

Cada provider/serviço usa apenas sua própria credencial:

```text
OPENAI_API_KEY                 → OpenAI SemanticProvider/M20
DEEPSEEK_API_KEY               → DeepSeek SemanticProvider/M20
MIMO_API_KEY                   → MiMo SemanticProvider/M20
XAI_API_KEY                    → xAI/Grok SemanticProvider/M20
DASHSCOPE_API_KEY              → Qwen SemanticProvider/M20
GEMINI_API_KEY                 → Gemini SemanticProvider/M20
ANTHROPIC_API_KEY              → Anthropic/Claude SemanticProvider/M20
SEARCHGEO_PAGESPEED_API_KEY    → PageSpeed Insights M21
SEARCHGEO_CRUX_API_KEY         → CrUX API M21
```

Não existe fallback de uma família de credencial para outra.

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

XAI
  grok-4.6

QWEN
  qwen3.8-max
  qwen3.8-flash

GEMINI
  gemini-3.8-flash

ANTHROPIC
  claude-sonnet-5
```

Em `auto`, modelos são definidos pelas variáveis específicas dos providers M18; `--ai-model` é rejeitado. Model ID aceito pelo código não garante acesso operacional da conta/plano.

## Variáveis de ambiente

| Variável | Default | Uso |
|---|---|---|
| `SEARCHGEO_DEVICE_CONTEXT` | `mobile` na CLI | `mobile`, `desktop`, `both`. |
| `SEARCHGEO_AI_TIMEOUT_SECONDS` | `180` | Timeout por chamada de IA externa; número finito > 0. |
| `SEARCHGEO_AI_CONTENT_REMEDIATION` | `false` | Habilita/desabilita M20 textual quando a flag não é usada. |
| `OPENAI_API_KEY` | — | Credencial da OpenAI API Platform. |
| `DEEPSEEK_API_KEY` | — | Credencial da DeepSeek API. |
| `MIMO_API_KEY` | — | MiMo PAYG `sk-...`; Token Plan `tp-...` não suportado. |
| `XAI_API_KEY` | — | Credencial da xAI API. |
| `DASHSCOPE_API_KEY` | — | Credencial Alibaba Model Studio/DashScope. |
| `GEMINI_API_KEY` | — | Credencial Gemini Developer API. |
| `ANTHROPIC_API_KEY` | — | Credencial Claude API. |
| `SEARCHGEO_OPENAI_MODEL` | `gpt-5.6-terra` | Model OpenAI no AUTO/env. |
| `SEARCHGEO_DEEPSEEK_MODEL` | `deepseek-v4-pro` | Model DeepSeek. |
| `SEARCHGEO_MIMO_MODEL` | `mimo-v2.5-pro` | Model MiMo. |
| `SEARCHGEO_XAI_MODEL` | `grok-4.6` | Model xAI explicit-only. |
| `SEARCHGEO_QWEN_MODEL` | `qwen3.8-max` | Model Qwen explicit-only. |
| `SEARCHGEO_GEMINI_MODEL` | `gemini-3.8-flash` | Model Gemini explicit-only. |
| `SEARCHGEO_ANTHROPIC_MODEL` | `claude-sonnet-5` | Model Anthropic explicit-only. |
| `SEARCHGEO_XAI_ENDPOINT` | endpoint xAI | Override compatível/documentado. |
| `SEARCHGEO_QWEN_ENDPOINT` | endpoint US default | Override de região/workspace compatível. |
| `SEARCHGEO_GEMINI_ENDPOINT` | endpoint Interactions | Override compatível/documentado. |
| `SEARCHGEO_ANTHROPIC_ENDPOINT` | endpoint Messages | Override compatível/documentado. |
| `SEARCHGEO_WEB_PERFORMANCE` | `false` | Habilita M21 externo. |
| `SEARCHGEO_WEB_PERFORMANCE_MAX_PAGES` | `10` | Máximo de páginas lógicas no M21; `0` = todas. |
| `SEARCHGEO_WEB_PERFORMANCE_TIMEOUT_SECONDS` | `60` | Timeout PageSpeed/CrUX por chamada. |
| `SEARCHGEO_WEB_PERFORMANCE_FIELD_SOURCE` | `auto` | `auto`, `pagespeed`, `crux`, `none`. |
| `SEARCHGEO_LIGHTHOUSE_CATEGORIES` | todas as quatro | Lista CSV de categorias Lighthouse. |
| `SEARCHGEO_PAGESPEED_API_KEY` | — | Chave Google opcional para PageSpeed. Nunca persistida. |
| `SEARCHGEO_CRUX_API_KEY` | — | Chave Google necessária para CrUX API direta. Nunca persistida. |

## Provider sem chave

Provider explícito sem token fica `NOT_CONFIGURED`, não chama API e não é afetado por chaves ausentes/presentes de outros providers. Em `auto`, apenas providers M18 sem token são excluídos; providers de extensão não são candidatos.

Credencial de produto/plano incompatível não deve ser tratada como válida apenas porque a variável existe.

M21 possui regra diferente porque PageSpeed pode operar sem chave. `field_source=crux` é rejeitado antes da auditoria se `SEARCHGEO_CRUX_API_KEY` não estiver configurada.

## Falha / quota / crédito / timeout

Provider de IA explícito não faz cross-provider fallback. `auto` pode quarantinar provider M18 falho e seguir para outro saudável conforme contrato. Não há retry automático de timeout.

Antes de concluir “sem crédito”, verifique produto/plano, endpoint, tipo de chave, limite de gasto e model access. No MiMo, `401` pode indicar mistura Token Plan/PAYG e `402` no endpoint PAYG representa saldo PAYG insuficiente.

Providers de extensão usam o mesmo princípio fail-closed: erro técnico/contratual é limitação operacional e não finding do website. Após falha qualificadora, podem permanecer quarantined durante a auditoria.

PageSpeed/CrUX são fail-open em relação à auditoria principal: falha/quota/timeout é registrada como estado operacional M21 e não cria finding do website nem recalcula SCORE-GEO-002.

## Saída da CLI

Exemplo com M21 desligado:

```text
Auditoria concluída: AUD-...
Status: COMPLETE_WITH_LIMITATIONS
Páginas auditadas: ...
Contexto de dispositivo: MOBILE
Sugestões de conteúdo por IA: DESABILITADAS
Web Performance externo: DESABILITADO (DISABLED; páginas 0; contextos 0/0)
Problemas identificados: ...
Recomendações: ...
Relatório: audits\AUD-...\report\index.html
Relatório por problemas: audits\AUD-...\report\remediation.html
Conteúdo e JSON-LD: audits\AUD-...\report\content-suggestions.html
Core Web Vitals e Lighthouse: audits\AUD-...\report\web-performance.html
```

Exemplo habilitado com coleta parcial:

```text
Web Performance externo: HABILITADO (PARTIAL; páginas 5; contextos 4/5)
```

`PARTIAL` não significa baixa qualidade do website; significa que pelo menos um contexto externo não produziu medição utilizável.

## Estrutura do report site

```text
report/
├─ index.html
├─ mobile.html             # condicional
├─ desktop.html            # condicional
├─ remediation.html
├─ content-suggestions.html
├─ web-performance.html
├─ ai-usage.html
├─ references.html
└─ css/
   └─ site.css
```

M18/M20 telemetry fica em `ai-usage.html`; sugestões textuais e revisão JSON-LD ficam em `content-suggestions.html`; PageSpeed/Lighthouse/CrUX e sua telemetria ficam em `web-performance.html`.

Providers de extensão podem registrar tokens/usage; enquanto `PROVISIONAL`, `estimated_cost` pode ficar indisponível até qualificação específica do catálogo de preços.

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

## Gate de provider extension

xAI/Qwen/Gemini/Anthropic permanecem `PROVISIONAL` e fora de AUTO até os gates de [AI_PROVIDER_EXTENSIONS.md](AI_PROVIDER_EXTENSIONS.md), [SMOKE_TEST.md](SMOKE_TEST.md) e `docs/specification/22_SAFE_AI_PROVIDER_EXTENSIONS.md` serem satisfeitos.
