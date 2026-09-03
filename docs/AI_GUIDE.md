# AI_GUIDE.md

Guia da análise semântica M18/M7 e da remediação textual opcional M20.

## Princípio

IA externa é complementar. Falha, quota, timeout, credencial ausente ou provider indisponível é limitação operacional do auditor; **não é finding do website**.

Há duas finalidades distintas:

1. **M18/M7:** análise semântica que pode materializar assessments/entidades/intents usados pelas regras;
2. **M20:** remediação textual advisory, executada depois de findings/scoring e incapaz de alterar retroativamente a avaliação.

A revisão/proposta JSON-LD de M20 é determinística e não depende de API externa.

## Compatibilidade de produto, plano e credencial

Compatibilidade = **provider + produto/plano de API + credencial + endpoint + modelo**.

| Provider | Produto/plano | SearchGEO atual | Limitação principal |
|---|---|---|---|
| OpenAI | API Platform com API key da organização/projeto e billing/quota/model access | **Suportado** | billing de ChatGPT e API é separado |
| OpenAI | ChatGPT Free/Go/Plus/Pro/Business/Enterprise/Edu e créditos do produto ChatGPT/Codex | **Não são saldo de API** | assinatura/crédito interativo não substitui billing da API |
| DeepSeek | DeepSeek API com `granted_balance` e/ou `topped_up_balance` | **Suportado** | `402` indica saldo insuficiente |
| Xiaomi MiMo | PAYG, chave `sk-...`, `https://api.xiaomimimo.com/v1` | **Suportado** | exige saldo PAYG e acesso ao modelo |
| Xiaomi MiMo | Token Plan `tp-...`, Base URL `token-plan-...` | **Não suportado / não usar** | produto, endpoint e créditos independentes; termos/restrições próprios |

Antes de habilitar um provider, confirme produto/plano, credencial, endpoint, saldo/quota/permissões e acesso ao modelo. Não altere endpoint/credencial para contornar restrições comerciais ou de uso.

Fontes oficiais de plano/billing:

- OpenAI: <https://help.openai.com/en/articles/9039756-managing-billing-settings-on-chatgpt-web-and-platform>
- OpenAI API limits: <https://help.openai.com/en/articles/6614457>
- DeepSeek pricing: <https://api-docs.deepseek.com/quick_start/pricing/>
- DeepSeek balance: <https://api-docs.deepseek.com/api/get-user-balance/>
- MiMo Token Plan: <https://mimo.mi.com/docs/en-US/tokenplan/Token%20Plan/subscription>
- MiMo `tp-...` × `sk-...`: <https://mimo.mi.com/docs/en-US/tokenplan/Token%20Plan/quick-access>
- MiMo errors: <https://mimo.mi.com/docs/en-US/api/guidance/error-codes>

Planos/termos externos podem mudar; a documentação do provider prevalece.

## Dispositivo e custo

Default CLI: `mobile`. Valores: `mobile`, `desktop`, `both`.

M7 e M20 só trabalham em snapshots materializados. Logo `mobile` não gera chamada Desktop e vice-versa; `both` pode gerar dois contextos por página/finalidade.

## Sem IA

```powershell
searchgeo audit https://example.com --ai-provider none
```

Nenhuma chamada externa. Regras semânticas sem base suficiente podem ficar `UNKNOWN`; isso não vira FAIL. A revisão JSON-LD determinística continua em `report/content-suggestions.html`.

## OpenAI

```powershell
$env:OPENAI_API_KEY = "<chave-da-API-Platform>"
searchgeo audit https://example.com --ai-provider openai
```

Default: `gpt-5.6-terra` / `HIGH`. Modelos: `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`.

Uma assinatura ChatGPT não transfere saldo para a API. Mesmo com billing ativo, a chamada pode falhar por saldo, limites da organização/projeto, rate limit ou ausência de acesso ao modelo.

## DeepSeek

```powershell
$env:DEEPSEEK_API_KEY = "<chave-da-DeepSeek-API>"
searchgeo audit https://example.com --ai-provider deepseek
```

Default `deepseek-v4-pro` / `HIGH`; `deepseek-v4-flash` também é aceito. Qualificação SearchGEO `PROVISIONAL`.

## Xiaomi MiMo

Modo suportado:

```powershell
$env:MIMO_API_KEY = "<chave-sk-PAYG>"
searchgeo audit https://example.com --ai-provider mimo
```

Default `mimo-v2.5-pro` / `THINKING_ENABLED`; `mimo-v2.5` também é aceito. Endpoint atual: `https://api.xiaomimimo.com/v1/responses`.

**Não use Token Plan `tp-...`.** Ele possui Base URL e créditos separados. `tp-...` no endpoint PAYG pode resultar em `401`; `sk-...` com saldo PAYG insuficiente pode resultar em `402`.

## Isolamento de credenciais

Cada provider usa somente sua própria credencial. Ausência de `DEEPSEEK_API_KEY` ou `MIMO_API_KEY` nunca autoriza fallback para `OPENAI_API_KEY`. O mesmo princípio vale para testes: fixtures de ausência de token neutralizam credenciais reais do ambiente para impedir chamadas pagas acidentais.

## Provider explícito e AUTO

Provider explícito não faz cross-provider fallback. Uma falha qualificadora pode colocar o provider em `QUARANTINED_FOR_AUDIT`.

`auto` cria uma cadeia imutável com providers elegíveis/configurados. O primeiro resultado válido encerra o contexto; provider falho pode ser quarantined. URL lock evita completar a mesma URL com provedores diferentes depois de pinning válido.

Preferência default: OpenAI `gpt-5.6-terra` → DeepSeek `deepseek-v4-pro` → MiMo `mimo-v2.5-pro`.

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

Precedência: flag CLI → ambiente → `false`.

M20 recebe somente estado persistido da página/snapshot/device: URL, title, conteúdo principal limitado, findings contentuais/semânticos elegíveis, observed/expected e suas evidências.

`Confidence LOW` isolado **não é gatilho**.

Uma sugestão aceita contém `finding_id`, objetivo, local sugerido, texto exato proposto, `evidence_ids`, confidence da sugestão, review note e provider/model.

### Segurança factual

O contrato proíbe keyword stuffing, word count arbitrário, reescrita só “para IA”, chunking artificial, fake freshness e claims/preços/datas/estatísticas/garantias/credenciais/experiência/fontes inventadas.

A validação local rejeita finding/evidence IDs fora do universo fornecido e novos tokens numéricos não sustentados pelo conteúdo/evidência. Isso é contenção adicional; revisão humana continua obrigatória.

Falha M20 não altera Score/findings e não invalida o audit. M20 não reativa provider quarantined.

## JSON-LD por página

### Ausente

M20 pode propor um baseline conservador:

```json
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "url": "<canonical-ou-url-normalizada>",
  "inLanguage": "pt-BR",
  "name": "<title-observado>",
  "description": "<description-observada>"
}
```

Campos sem evidência são omitidos. `mainEntity` só é usado quando sustentado de forma inequívoca.

### Existente

Não há substituição destrutiva. A revisão pode apontar parse errors, blocos idênticos duplicados, ausência global de `@context`, nós sem `@type`, propriedades genéricas ausentes de `WebPage` quando seus valores já são conhecidos e necessidade de validar propriedades específicas do tipo.

JSON-LD é **opcional/reforço**, não requisito universal GEO nem garantia de rich result. Structured Data deve corresponder ao conteúdo visível.

Referências: Google structured data policies/introduction, Schema.org e Google AI optimization guide.

## Confidence

Confidence do SCORE-GEO-002 é força da conclusão do auditor, não qualidade textual. Confidence de assessment do provider é outra grandeza. Nenhuma delas, sozinha, autoriza reescrita.

## Telemetria

`report/ai-usage.html` separa tentativas M18 e M20. Quando disponíveis mostra provider/model, URL/device, status, tokens, duração, custo estimado e erro sanitizado.

SQLite M18: `ai_audit_sessions`, `ai_provider_attempts`, `provider_pricing_catalog`.

SQLite M20: `content_remediation_runs`, `content_remediation_attempts`, `content_remediation_suggestions`, `jsonld_remediation_suggestions`.

`ESTIMATED_COST` não é invoice.

## Segurança

Nunca persistir API key, Authorization ou erro bruto sensível. Presença da variável não prova compatibilidade do plano.
