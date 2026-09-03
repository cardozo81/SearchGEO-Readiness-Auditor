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
| HTTP/HTTPS egress | necessário para targets e providers externos |
| Docker | não requerido/não fornecido |
| Web server | não requerido |

O `pyproject.toml` é a fonte de verdade para versão Python/dependência do package.

## Contextos de dispositivo

A CLI suporta:

```text
mobile
desktop
both
```

Default:

```text
mobile
```

Perfis reais de navegador continuam definidos em `rendering.py`. Quando somente um contexto é selecionado, não é criado snapshot do outro dispositivo.

Chamadas internas a M3 sem `SEARCHGEO_DEVICE_CONTEXT` preservam `both` por compatibilidade interna; isso não altera o default de usuário da CLI.

## Providers de IA

| Provider | Estado |
|---|---|
| `none` | suportado/default |
| OpenAI | suportado |
| DeepSeek | suportado; qualificação SearchGEO `PROVISIONAL` |
| Xiaomi MiMo | suportado; qualificação SearchGEO `PROVISIONAL` |
| `auto` | suportado; roteamento sequencial/failover controlado |

Não é necessário SDK Python específico desses providers; os adapters usam HTTP.

## Modelos aceitos

```text
OPENAI:   gpt-5.6-sol | gpt-5.6-terra | gpt-5.6-luna
DEEPSEEK: deepseek-v4-pro | deepseek-v4-flash
MIMO:     mimo-v2.5-pro | mimo-v2.5
```

Model ID diferente deve ser considerado não suportado pelo contrato atual, mesmo que a API externa possua outros modelos.

## Saída persistente

Contrato público:

```text
<audits-root>/<AUD-ID>/audit.db
<audits-root>/<AUD-ID>/artifacts/
<audits-root>/<AUD-ID>/report/index.html
<audits-root>/<AUD-ID>/report/remediation.html
<audits-root>/<AUD-ID>/report/ai-usage.html
<audits-root>/<AUD-ID>/report/references.html
<audits-root>/<AUD-ID>/report/css/site.css
```

Condicionalmente:

```text
report/mobile.html
report/desktop.html
```

A página correspondente existe apenas se o dispositivo foi auditado.

## HTML/CSS

O report site final:

- é estático;
- usa links relativos;
- não exige JavaScript para navegação básica;
- não exige web server;
- usa stylesheet externo compartilhado;
- não embute CSS final no `<head>` de cada página.

## Dados primários

O HTML não é fonte primária. A reprodutibilidade depende de:

```text
audit.db
artifacts/
```

## Structured Data

A cobertura operacional específica do parser é JSON-LD. Microdata e RDFa não devem ser tratados como equivalentes automaticamente pelo auditor atual.

JSON-LD também não é requisito universal para um Overall SearchGEO: quando ausente e as regras correspondentes são legitimamente `NOT_APPLICABLE`, a dimensão Structured Data fica fora da agregação.

## GEO/AEO externo

O produto não declara compatibilidade com um “padrão GEO” universal porque esse padrão normativo não existe.

A referência oficial mais direta do Google para recursos generativos é:

<https://developers.google.com/search/docs/fundamentals/ai-optimization-guide>

O guia mantém SEO como base e não cria requisito especial de AEO/GEO, `llms.txt`, chunking obrigatório ou Structured Data específico para IA.

## Rede e segurança

Para provider externo são necessários:

- DNS;
- HTTPS egress;
- credencial válida;
- saldo/quota/permissão compatível;
- política organizacional que autorize envio do contexto persistido ao provider.

Secrets não devem aparecer em artifacts, report site ou logs.

## Não homologado / fora do escopo

- executável standalone sem Python;
- macOS como target formal de handoff;
- banco de dados remoto;
- execução distribuída;
- interface web/backend do SearchGEO;
- Docker oficial;
- geração automática de conteúdo como parte do baseline atual.
