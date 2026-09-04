# AI_GUIDE.md

Guia da análise semântica M18/M7, dos providers de IA e da remediação textual opcional M20.

## Princípio

IA externa é complementar. Falha, quota, timeout, credencial ausente ou provider indisponível é limitação operacional do auditor; **não é finding do website**.

Há duas finalidades distintas:

1. **M18/M7:** análise semântica que pode materializar assessments/entidades/intents usados pelas regras;
2. **M20:** remediação textual advisory, executada depois de findings/scoring e incapaz de alterar retroativamente a avaliação.

A revisão/proposta JSON-LD de M20 é determinística e não depende de API externa.

## Providers e estado de qualificação

| Provider | CLI | Modelo default | Estado | Participa de `auto`? |
|---|---|---|---|---|
| OpenAI | `openai` | `gpt-5.6-terra` | `QUALIFIED` | **Sim** |
| DeepSeek | `deepseek` | `deepseek-v4-pro` | `PROVISIONAL` | **Sim** — baseline M18 existente |
| Xiaomi MiMo | `mimo` | `mimo-v2.5-pro` | `PROVISIONAL` | **Sim** — baseline M18 existente |
| xAI / Grok | `xai` ou `grok` | `grok-4.6` | `PROVISIONAL` | **Não** |
| Alibaba Qwen | `qwen` | `qwen3.8-max` | `PROVISIONAL` | **Não** |
| Google Gemini | `gemini` | `gemini-3.8-flash` | `PROVISIONAL` | **Não** |
| Anthropic Claude | `anthropic` ou `claude` | `claude-sonnet-5` | `PROVISIONAL` | **Não** |

Os quatro providers adicionados na extensão são **explicit-only** até smoke humano. A implementação não altera `searchgeo.m18_ai`; `none`, OpenAI, DeepSeek, MiMo e `auto` continuam delegados ao builder M18 homologado.

Detalhes técnicos, endpoints, aliases, variáveis e roteiro de smoke: [AI_PROVIDER_EXTENSIONS.md](AI_PROVIDER_EXTENSIONS.md).

## Compatibilidade de produto, plano e credencial

Compatibilidade = **provider + produto/plano de API + credencial + endpoint + modelo**.

| Provider | Produto/plano aceito | Limitação principal |
|---|---|---|
| OpenAI | API Platform com API key e billing/quota/model access | billing de ChatGPT e API é separado |
| DeepSeek | DeepSeek API com saldo/quota | `402` pode indicar saldo insuficiente |
| Xiaomi MiMo | PAYG, chave `sk-...`, endpoint PAYG | Token Plan `tp-...` não é suportado pelo adapter atual |
| xAI | xAI API com `XAI_API_KEY` e acesso a `grok-4.6` | key/produto precisam pertencer à API xAI |
| Alibaba Qwen | Model Studio/DashScope API key da mesma região/workspace do endpoint | endpoints e keys variam por região/workspace |
| Google Gemini | Gemini Developer API key com acesso ao modelo | não reutilizar chave PageSpeed/CrUX como key Gemini |
| Anthropic | Claude API key com acesso a `claude-sonnet-5` | assinatura Claude de produto interativo não substitui credencial da API |

Antes de habilitar um provider, confirme produto/plano, credencial, endpoint, saldo/quota/permissões e acesso ao modelo. Não altere endpoint/credencial para contornar restrições comerciais ou de uso.

Fontes oficiais principais:

- OpenAI billing: <https://help.openai.com/en/articles/9039756-managing-billing-settings-on-chatgpt-web-and-platform>
- DeepSeek pricing: <https://api-docs.deepseek.com/quick_start/pricing/>
- MiMo Token Plan: <https://mimo.mi.com/docs/en-US/tokenplan/Token%20Plan/subscription>
- xAI Structured Outputs: <https://docs.x.ai/developers/model-capabilities/text/structured-outputs>
- Qwen Structured Output: <https://www.alibabacloud.com/help/en/model-studio/qwen-structured-output>
- Gemini Structured Outputs: <https://ai.google.dev/gemini-api/docs/structured-output>
- Claude Structured Outputs: <https://platform.claude.com/docs/en/build-with-claude/structured-outputs>

Planos/termos externos podem mudar; a documentação do provider prevalece.

## Dispositivo e consumo

Default CLI: `mobile`. Valores: `mobile`, `desktop`, `both`.

M7 e M20 só trabalham em snapshots materializados. Logo `mobile` não gera chamada Desktop e vice-versa; `both` pode gerar dois contextos por página/finalidade.

## Sem IA

```powershell
searchgeo audit https://example.com --ai-provider none
```

Nenhuma chamada de LLM. Regras semânticas sem base suficiente podem ficar `UNKNOWN`; isso não vira FAIL. A revisão JSON-LD determinística continua disponível.

## OpenAI

```powershell
$env:OPENAI_API_KEY = "<chave-da-API-Platform>"
searchgeo audit https://example.com --ai-provider openai
```

Default: `gpt-5.6-terra` / `HIGH`.

Modelos aceitos:

```text
gpt-5.6-sol
gpt-5.6-terra
gpt-5.6-luna
```

Uma assinatura ChatGPT não transfere saldo para a API.

## DeepSeek

```powershell
$env:DEEPSEEK_API_KEY = "<chave-da-DeepSeek-API>"
searchgeo audit https://example.com --ai-provider deepseek
```

Default `deepseek-v4-pro` / `HIGH`; `deepseek-v4-flash` também é aceito.

## Xiaomi MiMo

```powershell
$env:MIMO_API_KEY = "<chave-sk-PAYG>"
searchgeo audit https://example.com --ai-provider mimo
```

Default `mimo-v2.5-pro` / `THINKING_ENABLED`; `mimo-v2.5` também é aceito. Endpoint atual: `https://api.xiaomimimo.com/v1/responses`.

**Não use Token Plan `tp-...`.** Ele possui Base URL e créditos separados.

## xAI / Grok

```powershell
$env:XAI_API_KEY = "<xai-api-key>"
searchgeo audit https://example.com --ai-provider xai
```

Alias: `--ai-provider grok`.

Default e único modelo qualificado nesta extensão: `grok-4.6`. Endpoint default: `https://api.x.ai/v1/responses`. Usa Responses API + JSON Schema strict.

## Alibaba Qwen

```powershell
$env:DASHSCOPE_API_KEY = "<model-studio-api-key>"
searchgeo audit https://example.com --ai-provider qwen
```

Default `qwen3.8-max`; `qwen3.8-flash` também é aceito. O adapter usa OpenAI-compatible Chat Completions com JSON Schema strict.

O endpoint depende da região/workspace Alibaba. O default SearchGEO é US/Virginia; use `SEARCHGEO_QWEN_ENDPOINT` quando sua key pertencer a outro deployment scope. Key e endpoint devem pertencer à mesma região/workspace.

## Google Gemini

```powershell
$env:GEMINI_API_KEY = "<gemini-api-key>"
searchgeo audit https://example.com --ai-provider gemini
```

Default `gemini-3.8-flash`. O adapter usa a Gemini Interactions API atual e Structured Outputs com JSON Schema.

`GEMINI_API_KEY` é independente de `SEARCHGEO_PAGESPEED_API_KEY` e `SEARCHGEO_CRUX_API_KEY`.

## Anthropic Claude

```powershell
$env:ANTHROPIC_API_KEY = "<anthropic-api-key>"
searchgeo audit https://example.com --ai-provider anthropic
```

Alias: `--ai-provider claude`.

Default `claude-sonnet-5`. Usa Messages API + `output_config.format` JSON Schema. Sonnet 5 opera com adaptive thinking por default; o SearchGEO não envia os antigos controles incompatíveis de extended thinking nem sampling não-default.

## Isolamento de credenciais

Cada provider usa somente sua própria credencial:

```text
OPENAI_API_KEY
DEEPSEEK_API_KEY
MIMO_API_KEY
XAI_API_KEY
DASHSCOPE_API_KEY
GEMINI_API_KEY
ANTHROPIC_API_KEY
```

A ausência da key do provider selecionado resulta em `NOT_CONFIGURED` e **zero chamada**. Nenhuma key de outro provider é usada como fallback implícito.

## Provider explícito e AUTO

Provider explícito não faz cross-provider fallback. Uma falha qualificadora pode colocar o provider em `QUARANTINED_FOR_AUDIT`.

`auto` mantém a cadeia M18 homologada:

```text
OpenAI gpt-5.6-terra
  -> DeepSeek deepseek-v4-pro
  -> MiMo mimo-v2.5-pro
```

xAI, Qwen, Gemini e Anthropic **não participam de AUTO**, mesmo quando suas keys estão configuradas. Essa restrição é intencional até qualificação/smoke humano.

## Modelos e variáveis de override

```text
OPENAI:    gpt-5.6-sol | gpt-5.6-terra | gpt-5.6-luna
DEEPSEEK:  deepseek-v4-pro | deepseek-v4-flash
MIMO:      mimo-v2.5-pro | mimo-v2.5
XAI:       grok-4.6
QWEN:      qwen3.8-max | qwen3.8-flash
GEMINI:    gemini-3.8-flash
ANTHROPIC: claude-sonnet-5
```

Variáveis de modelo:

```text
SEARCHGEO_OPENAI_MODEL
SEARCHGEO_DEEPSEEK_MODEL
SEARCHGEO_MIMO_MODEL
SEARCHGEO_XAI_MODEL
SEARCHGEO_QWEN_MODEL
SEARCHGEO_GEMINI_MODEL
SEARCHGEO_ANTHROPIC_MODEL
```

Novos providers também aceitam endpoint override explícito:

```text
SEARCHGEO_XAI_ENDPOINT
SEARCHGEO_QWEN_ENDPOINT
SEARCHGEO_GEMINI_ENDPOINT
SEARCHGEO_ANTHROPIC_ENDPOINT
```

Use endpoint override somente para deployment compatível/documentado pelo provider.

## Timeout

`SEARCHGEO_AI_TIMEOUT_SECONDS`, default CLI `180`. Deve ser número finito > 0. Não há retry automático após timeout, evitando consumo potencialmente duplicado.

## M20 — remediação textual opcional

Default **OFF**.

```powershell
searchgeo audit https://example.com `
  --ai-provider openai `
  --ai-content-remediation
```

ou:

```powershell
$env:SEARCHGEO_AI_CONTENT_REMEDIATION = "true"
```

Precedência: flag CLI -> ambiente -> `false`.

M20 recebe somente estado persistido da página/snapshot/device. `Confidence LOW` isolado não é gatilho. A validação local rejeita finding/evidence IDs fora do universo fornecido e conteúdo incompatível com o contrato factual.

Falha M20 não altera Score/findings e não invalida o audit. M20 não reativa provider quarantined.

## JSON-LD por página

Se JSON-LD estiver ausente, M20 pode propor baseline conservador `WebPage` usando apenas valores observados. Se existir, não há substituição destrutiva: a revisão aponta problemas verificáveis.

JSON-LD é **opcional/reforço**, não requisito universal GEO nem garantia de rich result. Structured Data deve corresponder ao conteúdo visível.

## Confidence

Confidence do SCORE-GEO-002 é força da conclusão do auditor, não qualidade textual. Confidence de assessment do provider é outra grandeza. Nenhuma delas, sozinha, autoriza reescrita.

## Telemetria e custos

`report/ai-usage.html` separa tentativas M18 e M20. Quando disponíveis, mostra provider/model, URL/device, status, tokens, duração, custo estimado e erro sanitizado.

SQLite M18: `ai_audit_sessions`, `ai_provider_attempts`, `provider_pricing_catalog`.

SQLite M20: `content_remediation_runs`, `content_remediation_attempts`, `content_remediation_suggestions`, `jsonld_remediation_suggestions`.

Os providers de extensão normalizam usage/tokens quando a API fornece esses dados. Enquanto estiverem `PROVISIONAL`, seu preço não é automaticamente inserido no catálogo homologado M18; `estimated_cost` pode ficar indisponível para evitar estimativa incorreta por região, cache, tier ou promoção.

`ESTIMATED_COST` não é invoice.

## Smoke humano dos providers de extensão

Antes de qualquer promoção para `AUTO` ou remoção de `PROVISIONAL`, executar o roteiro de [AI_PROVIDER_EXTENSIONS.md](AI_PROVIDER_EXTENSIONS.md) com credenciais reais e confirmar também a baseline OpenAI/DeepSeek/MiMo.

## Segurança

Nunca persistir API key, Authorization ou erro bruto sensível. Presença da variável não prova compatibilidade do plano.
