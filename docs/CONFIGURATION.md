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

## Device context

`SEARCHGEO_DEVICE_CONTEXT`: `mobile`, `desktop`, `both`. Precedência flag → ambiente → `mobile`.

A seleção limita M3 e, por consequência, M7/M20 aos snapshots escolhidos. Chamada interna direta a M3 sem variável preserva `both` por compatibilidade interna.

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

Nenhuma chamada externa; JSON-LD determinístico M20 continua disponível.

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

Para cada snapshot auditado, M20 revisa Structured Data. Se ausente, pode propor `WebPage` com URL, idioma, title e description efetivamente observados. Se existente, aponta problemas verificáveis sem reescrever destrutivamente o graph.

JSON-LD é opcional/reforço, não requisito universal GEO nem garantia de rich result.

## Modelos

```text
OPENAI:   gpt-5.6-sol | gpt-5.6-terra | gpt-5.6-luna
DEEPSEEK: deepseek-v4-pro | deepseek-v4-flash
MIMO:     mimo-v2.5-pro | mimo-v2.5
```

Model ID aceito não garante acesso da conta/plano.

## Timeout

`SEARCHGEO_AI_TIMEOUT_SECONDS`, default 180 s, número finito > 0. Sem retry automático. M20 reutiliza o timeout do provider.

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
├─ ai-usage.html
├─ references.html
└─ css/site.css
```

## Fora do contrato público

Sem web/backend, banco remoto, Docker daemon, execução distribuída, retry automático, publicação automática de conteúdo, criação automática de JSON-LD no website, Base URL customizada por CLI ou MiMo Token Plan `tp-...`.
