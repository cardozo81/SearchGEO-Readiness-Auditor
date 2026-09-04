# CONFIGURATION.md

Configuração operacional do SearchGEO Readiness Auditor.

## Defaults

| Configuração | Default |
|---|---|
| idioma | `pt-BR` |
| mercado | `BR` |
| `--max-pages` | `100` |
| `--audits-root` | `audits` |
| `--device-context` | `mobile` |
| `--ai-provider` | `none` |
| `--ai-content-remediation` | `false` |
| timeout IA | `180` s |
| `--web-performance` | `false` |
| `--web-performance-max-pages` | `10` |
| `--web-performance-timeout-seconds` | `60` s |
| `--web-performance-field-source` | `auto` |
| `--lighthouse-categories` | `performance,accessibility,best-practices,seo` |

## Device context

`SEARCHGEO_DEVICE_CONTEXT`: `mobile`, `desktop`, `both`. Precedência flag → ambiente → `mobile`.

A seleção limita M3 e, por consequência, M7/M20 aos snapshots escolhidos. A mesma seleção limita M21 aos snapshots realmente materializados. Chamada interna direta a M3 sem variável preserva `both` por compatibilidade interna.

## Antes de configurar IA

Não trate “tenho plano/créditos” como “tenho API utilizável”. Valide produto/plano, tipo de credencial, endpoint, saldo/quota/permissão/model access e termos do workload automatizado.

| Provider | Aceito | Não confundir |
|---|---|---|
| OpenAI | API key da API Platform com billing/quota | ChatGPT/Créditos ChatGPT, billing separado |
| DeepSeek | DeepSeek API com saldo | chave sem saldo disponível |
| MiMo | PAYG `sk-...` para `https://api.xiaomimimo.com/v1` | Token Plan `tp-...` com Base URL/créditos separados |

Detalhes: [AI_GUIDE.md](AI_GUIDE.md).

### Desabilitada

```powershell
searchgeo audit https://example.com --ai-provider none
```

Nenhuma chamada de IA externa; JSON-LD determinístico M20 continua disponível. M21 Web Performance também permanece desligado por default e não chama PageSpeed/CrUX.

### OpenAI

```powershell
$env:OPENAI_API_KEY = "<chave-da-API-Platform>"
searchgeo audit https://example.com --ai-provider openai
```

Default `gpt-5.6-terra`.

### DeepSeek

```powershell
$env:DEEPSEEK_API_KEY = "<chave-da-DeepSeek-API>"
searchgeo audit https://example.com --ai-provider deepseek
```

Default `deepseek-v4-pro`.

### MiMo

```powershell
$env:MIMO_API_KEY = "<chave-sk-PAYG>"
searchgeo audit https://example.com --ai-provider mimo
```

Default `mimo-v2.5-pro`; adapter PAYG em `https://api.xiaomimimo.com/v1/responses`. Não configure Token Plan `tp-...`.

### AUTO

Somente providers elegíveis/configurados entram na cadeia imutável. Primeiro resultado válido encerra contexto; falha qualificadora pode quarantinar provider.

## Isolamento de credenciais

Cada adapter usa exclusivamente a credencial do próprio provider. `OPENAI_API_KEY` não pode preencher ausência de `DEEPSEEK_API_KEY`/`MIMO_API_KEY`, e vice-versa.

As credenciais de medição externa M21 também são isoladas:

```text
SEARCHGEO_PAGESPEED_API_KEY
SEARCHGEO_CRUX_API_KEY
```

Elas não são credenciais de IA, não são reutilizadas pelos SemanticProviders e nunca devem substituir `OPENAI_API_KEY`, `DEEPSEEK_API_KEY` ou `MIMO_API_KEY`.

Para criar corretamente essas chaves no Google Cloud — incluindo projeto, ativação das APIs, caminhos de menu, restrições e configuração no PowerShell — consulte [GOOGLE_API_KEYS.md](GOOGLE_API_KEYS.md).

## M20 textual

`SEARCHGEO_AI_CONTENT_REMEDIATION`, default `false`; aceita `true/false`, `1/0`, `yes/no`, `on/off`.

Precedência: flags `--ai-content-remediation`/`--no-ai-content-remediation` → ambiente → `false`.

M20:

- roda depois de findings/scoring;
- não altera RuleExecution/Finding/Score/Coverage/Confidence;
- não é disparado por Confidence LOW isolado;
- usa apenas findings contentuais/semânticos elegíveis + evidências;
- exige revisão humana;
- não aplica/publica texto;
- reutiliza provider/model/reasoning/timeout e respeita quarantine.

Com `--ai-provider none`, M20 textual fica `NOT_CONFIGURED` sem abortar; JSON-LD determinístico permanece.

## JSON-LD

Para cada snapshot auditado, M20 revisa Structured Data. Se ausente, pode propor `WebPage` com URL, idioma, title e description efetivamente observados/persistidos. Se existente, aponta problemas verificáveis sem reescrever destrutivamente o graph.

JSON-LD é opcional/reforço, não requisito universal GEO nem garantia de rich result.

## M21 — Core Web Vitals e Lighthouse

M21 é uma camada de **evidência externa complementar**. Não substitui nem recalcula `SCORE-GEO-002`.

Por padrão:

```text
SEARCHGEO_WEB_PERFORMANCE=false
```

Logo uma execução existente continua sem chamadas PageSpeed/CrUX e sem consumo externo adicional.

Ativação:

```powershell
searchgeo audit https://example.com --web-performance
```

Equivalente por ambiente:

```powershell
$env:SEARCHGEO_WEB_PERFORMANCE = "true"
searchgeo audit https://example.com
```

Precedência:

1. `--web-performance` / `--no-web-performance`;
2. `SEARCHGEO_WEB_PERFORMANCE`;
3. `false`.

### Limite de páginas externas

```powershell
searchgeo audit https://example.com `
  --web-performance `
  --web-performance-max-pages 5
```

Variável equivalente:

```text
SEARCHGEO_WEB_PERFORMANCE_MAX_PAGES
```

Default `10`. Valor `0` significa todas as páginas auditadas.

O limite se aplica a páginas lógicas. Com `--device-context both`, cada página selecionada pode gerar uma medição Mobile e uma Desktop.

### Timeout externo

```text
SEARCHGEO_WEB_PERFORMANCE_TIMEOUT_SECONDS
```

ou:

```powershell
--web-performance-timeout-seconds 60
```

Default `60` segundos por request externo. Deve ser número finito > 0. Não existe retry automático de timeout.

O default é um limite operacional, não uma garantia de tempo de resposta do PageSpeed. Se a telemetria indicar `TIMEOUTERROR` próximo do limite configurado, aumente-o explicitamente, por exemplo:

```powershell
searchgeo audit https://example.com `
  --web-performance `
  --web-performance-timeout-seconds 180
```

Não é feito retry automático: elevar o timeout afeta a próxima execução, não repete silenciosamente uma requisição anterior.

### Lighthouse categories

```text
SEARCHGEO_LIGHTHOUSE_CATEGORIES
```

ou:

```powershell
--lighthouse-categories performance,accessibility,best-practices,seo
```

Valores suportados:

```text
performance
accessibility
best-practices
seo
```

Default: todas as quatro categorias oficiais. Elas são solicitadas no mesmo contexto PageSpeed; não geram chamadas de LLM.

### PageSpeed API key

Opcional:

```powershell
$env:SEARCHGEO_PAGESPEED_API_KEY = "<google-api-key>"
```

PageSpeed Insights pode ser usado sem chave em uso ad hoc/baixo volume; para automação frequente a documentação oficial recomenda chave. O SearchGEO nunca persiste nem exibe essa chave.

Criação, habilitação da **PageSpeed Insights API**, restrições e validação: [GOOGLE_API_KEYS.md](GOOGLE_API_KEYS.md).

### CrUX API key

Para CrUX direto:

```powershell
$env:SEARCHGEO_CRUX_API_KEY = "<google-api-key>"
```

A CrUX API direta exige chave Google Cloud provisionada para **Chrome UX Report API**.

Criação, habilitação da API, restrições e validação: [GOOGLE_API_KEYS.md](GOOGLE_API_KEYS.md).

### Fonte de field data

```text
SEARCHGEO_WEB_PERFORMANCE_FIELD_SOURCE
```

ou:

```powershell
--web-performance-field-source auto|pagespeed|crux|none
```

Comportamento:

| Valor | Comportamento |
|---|---|
| `auto` | Usa field data CrUX presente no PageSpeed; se faltar e houver `SEARCHGEO_CRUX_API_KEY`, tenta CrUX API direta. |
| `pagespeed` | Usa apenas field data retornado pelo PageSpeed; não faz chamada CrUX separada. |
| `crux` | Usa CrUX API direta para field data; requer `SEARCHGEO_CRUX_API_KEY`. PageSpeed continua sendo usado para Lighthouse lab. |
| `none` | Não processa field data; mantém Lighthouse lab. |

O default `auto` prepara a migração para CrUX direto porque o Google já documentou a retirada futura de field data CrUX da PageSpeed Insights API.

### Status operacional M21

A execução M21 usa:

```text
DISABLED
NO_CONTEXTS
SUCCESS
PARTIAL
UNAVAILABLE
```

`SUCCESS` exige que todos os contextos selecionados tenham evidência útil e que nenhum componente externo solicitado tenha falhado.

`PARTIAL` significa que existe evidência útil, mas houve ao menos uma falha/indisponibilidade de componente ou contexto. Exemplo:

```text
PageSpeed → TIMEOUTERROR
CrUX      → HTTP 200
M21       → PARTIAL
```

Portanto, `successful_contexts == context_attempts` não mascara timeout PageSpeed se o contexto ficou `PARTIAL`.

`UNAVAILABLE` significa que nenhum contexto produziu evidência externa útil.

Esses estados qualificam a coleta; não são Finding e não alteram `SCORE-GEO-002`.

### Consumo e IA

M21 adiciona **zero chamadas de OpenAI/DeepSeek/MiMo**.

O consumo adicional de `--web-performance` é somente dos serviços PageSpeed/CrUX e é controlado por:

- flag de habilitação default OFF;
- limite de páginas;
- device context;
- timeout;
- política de field data;
- credenciais Google opcionais/necessárias conforme serviço.

Falha, quota, timeout ou falta de amostra CrUX não são findings do website e não reduzem `SCORE-GEO-002`.

### Core Web Vitals

M21 usa os thresholds oficiais atuais de boa experiência no percentil 75:

```text
LCP <= 2500 ms
INP <= 200 ms
CLS <= 0.10
```

Estados:

```text
PASS        # as três métricas disponíveis e boas
FAIL        # as três disponíveis e ao menos uma excede o threshold bom
INCOMPLETE  # falta ao menos uma das três métricas
UNAVAILABLE # nenhum conjunto utilizável de field data
```

Ausência de amostra CrUX não é convertida em `FAIL`.

### Lighthouse

Os scores e métricas Lighthouse são apresentados como medição externa de laboratório, incluindo quando disponíveis:

- Performance 0–100;
- Accessibility 0–100;
- Best Practices 0–100;
- SEO 0–100;
- FCP;
- Speed Index;
- LCP;
- Total Blocking Time;
- CLS;
- versão do Lighthouse.

Nenhum desses números é somado, multiplicado ou promediado com o `SCORE-GEO-002`.

## Log operacional persistente

Cada workspace pode materializar:

```text
audits/<AUD-ID>/logs/audit.log
```

O arquivo usa JSONL e registra o ciclo principal da auditoria e, quando M21 está habilitado, as tentativas PageSpeed/CrUX com status, HTTP, duração e erro sanitizado.

A CLI imprime o caminho do log ao final quando o arquivo existe.

O log é fail-open: erro ao escrevê-lo não invalida a auditoria. Chaves, Authorization headers, tokens, passwords e request URLs com credenciais não podem ser registrados.

Detalhes e exemplos PowerShell: [OPERATIONAL_LOGGING.md](OPERATIONAL_LOGGING.md).

## Modelos

```text
OPENAI:   gpt-5.6-sol | gpt-5.6-terra | gpt-5.6-luna
DEEPSEEK: deepseek-v4-pro | deepseek-v4-flash
MIMO:     mimo-v2.5-pro | mimo-v2.5
```

Model ID aceito não garante acesso da conta/plano.

## Timeout IA

`SEARCHGEO_AI_TIMEOUT_SECONDS`, default 180 s, número finito > 0. Sem retry automático. M20 reutiliza o timeout do provider.

Esse timeout é independente de `SEARCHGEO_WEB_PERFORMANCE_TIMEOUT_SECONDS`.

## Provider sem credencial

Provider explícito: `NOT_CONFIGURED`, zero chamada; chaves de outros providers não interferem. AUTO exclui provider sem chave. Credencial de produto incompatível não é configuração operacional válida.

## Report

```text
report/
├─ index.html
├─ mobile.html
├─ desktop.html
├─ remediation.html
├─ content-suggestions.html
├─ web-performance.html
├─ ai-usage.html
├─ references.html
└─ css/site.css
```

`web-performance.html` separa Lighthouse lab, Core Web Vitals field, telemetria de medição e limitações de coleta. `references.html` identifica as fontes oficiais e declara que elas não homologam o score heurístico global do SearchGEO.

## Fora do contrato público

Sem web/backend, banco remoto, Docker daemon, execução distribuída, retry automático, publicação automática de conteúdo, criação automática de JSON-LD no website, Base URL customizada por CLI ou MiMo Token Plan `tp-...`.

M21 também não cria combinação matemática entre Lighthouse/CWV e `SCORE-GEO-002`, não transforma ausência de CrUX em falha e não cria interpretação por LLM sem opt-in futuro explícito.
