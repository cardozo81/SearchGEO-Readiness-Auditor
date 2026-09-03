# COMPATIBILITY.md

## Runtime

| Item | Compatibilidade atual |
|---|---|
| CPython | `>=3.13,<3.14` |
| Windows + PowerShell | target operacional principal |
| Playwright | `>=1.57,<2` |
| Chromium | obrigatório para rendering real |
| SQLite | embarcado/local |
| Filesystem | local e gravável |
| HTTP/HTTPS egress | targets/providers externos |
| Docker / web server | não requeridos |

## Dispositivos

CLI: `mobile`, `desktop`, `both`; default `mobile`. Snapshot não selecionado não é materializado e não pode gerar chamada M7/M20.

## Providers

| Provider | Estado |
|---|---|
| `none` | suportado/default |
| OpenAI | API Platform suportada |
| DeepSeek | API suportada; qualificação `PROVISIONAL` |
| Xiaomi MiMo | PAYG `sk-...` suportado; qualificação `PROVISIONAL` |
| `auto` | suportado |

### Produto/plano

| Provider | Produto | Compatibilidade |
|---|---|---|
| OpenAI | API Platform com billing/quota/model access | suportado |
| OpenAI | assinaturas/créditos ChatGPT | não equivalem a saldo de API |
| DeepSeek | DeepSeek API com saldo | suportado |
| MiMo | PAYG `sk-...`, `https://api.xiaomimimo.com/v1` | suportado |
| MiMo | Token Plan `tp-...`, Base URL dedicada | não suportado/não usar |

Credenciais são isoladas por provider; nenhuma chave pode ser reutilizada implicitamente em endpoint de outro fornecedor.

## Modelos

```text
OPENAI:   gpt-5.6-sol | gpt-5.6-terra | gpt-5.6-luna
DEEPSEEK: deepseek-v4-pro | deepseek-v4-flash
MIMO:     mimo-v2.5-pro | mimo-v2.5
```

## Saída

```text
<AUD-ID>/audit.db
<AUD-ID>/artifacts/
<AUD-ID>/report/index.html
<AUD-ID>/report/remediation.html
<AUD-ID>/report/content-suggestions.html
<AUD-ID>/report/ai-usage.html
<AUD-ID>/report/references.html
<AUD-ID>/report/css/site.css
```

`mobile.html`/`desktop.html` são condicionais.

## Structured Data / M20

Parser operacional específico: JSON-LD. M20 pode propor baseline JSON-LD quando ausente e revisar markup existente. Isso é advisory; não publica alteração no site. JSON-LD continua opcional/reforço e ausência legítima não é FAIL universal.

## Segurança

Provider externo requer credencial do produto correto, endpoint compatível, saldo/quota/permissão e termos que autorizem o workload. Secrets não devem aparecer em artifacts/report/logs.

## Fora do escopo

Executável standalone sem Python, banco remoto, execução distribuída, web backend, Docker oficial, publicação/aplicação automática de conteúdo/Structured Data e MiMo Token Plan `tp-...`.
