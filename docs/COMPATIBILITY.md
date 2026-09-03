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
| OpenAI | suportado via OpenAI API Platform |
| DeepSeek | suportado via DeepSeek API; qualificação SearchGEO `PROVISIONAL` |
| Xiaomi MiMo | suportado via MiMo Pay-as-you-go API (`sk-...`); qualificação SearchGEO `PROVISIONAL` |
| `auto` | suportado; roteamento sequencial/failover controlado |

Não é necessário SDK Python específico desses providers; os adapters usam HTTP.

### Compatibilidade por produto/plano

A existência de uma assinatura ou saldo no ecossistema do fornecedor não é suficiente. O SearchGEO depende do produto de API efetivamente associado à chave e ao endpoint.

| Provider | Produto/plano | Compatibilidade atual | Observação |
|---|---|---|---|
| OpenAI | API Platform com billing/quota/model access válidos | **Suportado** | prepaid, cobrança automática ou contrato Enterprise/Scale Tier podem financiar a API conforme a conta; limites de organização/projeto continuam valendo |
| OpenAI | ChatGPT Free/Go/Plus/Pro/Business/Enterprise/Edu e créditos de recursos do ChatGPT/Codex | **Não equivalem a saldo de API** | billing do ChatGPT e da API é separado |
| DeepSeek | DeepSeek API com `granted_balance` e/ou `topped_up_balance` | **Suportado** | ambos compõem o saldo da API; `402` indica saldo insuficiente |
| Xiaomi MiMo | Pay-as-you-go API, chave `sk-...`, Base URL `https://api.xiaomimimo.com/v1` | **Suportado** | é o modo implementado pelo adapter atual |
| Xiaomi MiMo | Token Plan, chave `tp-...`, Base URL dedicada `https://token-plan-<região>.xiaomimimo.com/v1` | **Não suportado / não usar** | produto separado; além do endpoint diferente, a MiMo restringe o Token Plan a ferramentas de programação e proíbe automated scripts/custom application backends fora desse escopo |

Consequências importantes para MiMo:

- `tp-...` e `sk-...` são credenciais de produtos independentes;
- créditos do Token Plan não financiam uma chamada PAYG feita com `sk-...`;
- misturar chave Token Plan com endpoint PAYG pode resultar em `401`;
- `402` no endpoint PAYG indica saldo insuficiente da conta PAYG chamada;
- o SearchGEO atual não seleciona Base URL de Token Plan e não deve ser configurado com `tp-...`.

Detalhes operacionais e fontes oficiais: [AI_GUIDE.md](AI_GUIDE.md).

## Modelos aceitos

```text
OPENAI:   gpt-5.6-sol | gpt-5.6-terra | gpt-5.6-luna
DEEPSEEK: deepseek-v4-pro | deepseek-v4-flash
MIMO:     mimo-v2.5-pro | mimo-v2.5
```

Model ID diferente deve ser considerado não suportado pelo contrato atual, mesmo que a API externa possua outros modelos.

Suporte ao model ID também não garante que toda conta/plano possua acesso operacional a ele; permissões, tiers, quota, saldo e limites do provider podem variar por conta.

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
- credencial válida para o produto/plano correto;
- endpoint compatível com a credencial;
- saldo/quota/permissão compatível;
- acesso ao modelo configurado;
- política organizacional e termos do fornecedor que autorizem o caso de uso e o envio do contexto persistido ao provider.

Secrets não devem aparecer em artifacts, report site ou logs.

## Não homologado / fora do escopo

- executável standalone sem Python;
- macOS como target formal de handoff;
- banco de dados remoto;
- execução distribuída;
- interface web/backend do SearchGEO;
- Docker oficial;
- geração automática de conteúdo como parte do baseline atual;
- uso do Xiaomi MiMo Token Plan `tp-...` no auditor automatizado atual.
