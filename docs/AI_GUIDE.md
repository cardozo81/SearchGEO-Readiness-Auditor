# AI_GUIDE.md

Guia de uso da camada semântica opcional do SearchGEO.

## Princípio

IA externa é capacidade complementar. O auditor permanece funcional sem IA.

Falha, indisponibilidade, quota, timeout ou credencial ausente de um provider é limitação operacional da auditoria; **não é finding do website**.

A compatibilidade do SearchGEO é definida pela combinação **provider + produto/plano de API + tipo de credencial + endpoint + modelo**, e não apenas pelo nome comercial da IA. Ter uma assinatura, créditos ou acesso interativo a um produto do fornecedor não significa automaticamente possuir saldo ou autorização para uso via API no SearchGEO.

## Compatibilidade de produto, plano e credencial

Estado documentado em 2026-09-03:

| Provider | Produto/plano do fornecedor | Credencial / cobrança | SearchGEO atual | Limitação principal |
|---|---|---|---|---|
| OpenAI | API Platform — prepaid, pay-as-you-go/automatic card ou contrato Enterprise API/Scale Tier quando aplicável | API key da organização/projeto; faturamento da API | **Suportado**, desde que a organização/projeto tenha acesso ao modelo, saldo/quota e limites de gasto compatíveis | ChatGPT e API possuem faturamento separado; limites de organização/projeto/modelo continuam valendo |
| OpenAI | ChatGPT Free/Go/Plus/Pro/Business/Enterprise/Edu e créditos de recursos do ChatGPT/Codex | assinatura/créditos do produto ChatGPT | **Não são saldo de API para o SearchGEO** | assinatura ou crédito do ChatGPT não substitui billing da API Platform |
| DeepSeek | DeepSeek API | API key; saldo concedido (`granted`) e/ou recarregado (`topped-up`) | **Suportado** | 402 indica saldo total insuficiente; limites de concorrência são aplicados no nível da conta |
| Xiaomi MiMo | Pay-as-you-go API | chave `sk-...`; Base URL padrão `https://api.xiaomimimo.com/v1` | **Suportado** | requer saldo PAYG e acesso ao modelo; créditos de Token Plan não financiam esta chave |
| Xiaomi MiMo | Token Plan | chave `tp-...`; Base URL dedicada por região (`token-plan-...`) | **Não suportado pelo SearchGEO atual e não deve ser usado** | é um produto separado; a MiMo restringe o pacote a ferramentas de programação e proíbe uso em automated scripts/custom application backends fora desse escopo |

### Regra operacional

Antes de habilitar um provider, confirme quatro itens:

1. o produto/plano comprado realmente cobre **API programática** para o caso de uso do SearchGEO;
2. a credencial pertence a esse produto/plano;
3. o endpoint usado pelo SearchGEO corresponde à credencial;
4. saldo, quota, permissões, limites de gasto e acesso ao modelo estão disponíveis.

O SearchGEO não tenta converter automaticamente uma assinatura interativa em acesso de API e não deve contornar restrições comerciais ou de uso do fornecedor.

### Fontes oficiais de plano/billing

- OpenAI — billing de ChatGPT e API são separados: <https://help.openai.com/en/articles/9039756-managing-billing-settings-on-chatgpt-web-and-platform>
- OpenAI — diagnóstico de saldo/limites de API: <https://help.openai.com/en/articles/6614457>
- DeepSeek — pricing e regras de dedução: <https://api-docs.deepseek.com/quick_start/pricing/>
- DeepSeek — saldo de API: <https://api-docs.deepseek.com/api/get-user-balance/>
- Xiaomi MiMo — Token Plan e restrições de uso: <https://mimo.mi.com/docs/en-US/tokenplan/Token%20Plan/subscription>
- Xiaomi MiMo — diferenças entre `tp-...` e `sk-...`: <https://mimo.mi.com/docs/en-US/tokenplan/Token%20Plan/quick-access>
- Xiaomi MiMo — códigos 401/402/429: <https://mimo.mi.com/docs/en-US/api/guidance/error-codes>

Planos, preços, limites e termos externos podem mudar. A documentação oficial do provider prevalece sobre exemplos históricos do SearchGEO.

## Dispositivo e custo

A CLI usa Mobile por padrão:

```text
--device-context mobile
```

Valores:

```text
mobile
desktop
both
```

A seleção acontece antes do rendering. M7 analisa somente snapshots existentes. Consequência prática:

- `mobile`: nenhuma chamada semântica Desktop;
- `desktop`: nenhuma chamada semântica Mobile;
- `both`: os dois contextos quando disponíveis.

Para auditoria inicial com IA, `mobile` é a opção de menor custo entre os modos que executam análise de página.

Variável equivalente:

```powershell
$env:SEARCHGEO_DEVICE_CONTEXT = "mobile"
```

## Sem IA

```powershell
searchgeo audit https://example.com --ai-provider none
```

Com `none`:

- nenhuma chamada externa;
- regras determinísticas continuam;
- regras semantic-only sem base suficiente ficam `UNKNOWN`;
- Coverage/Consolidation podem reduzir;
- o website não recebe FAIL por ausência de provider.

## OpenAI

```powershell
$env:OPENAI_API_KEY = "<chave-da-API-Platform>"
searchgeo audit https://example.com --ai-provider openai
```

Default:

```text
model: gpt-5.6-terra
reasoning: HIGH
```

Modelos aceitos:

```text
gpt-5.6-sol
gpt-5.6-terra
gpt-5.6-luna
```

### Limitações de plano OpenAI

O SearchGEO usa a **OpenAI API Platform**. Uma assinatura ChatGPT, inclusive paga, não transfere automaticamente saldo para a API. Créditos adquiridos para recursos do ChatGPT/Codex também não devem ser tratados como créditos de API.

Mesmo com billing de API ativo, uma chamada pode falhar por:

- saldo pré-pago esgotado;
- limite de gasto da organização;
- limite de gasto do projeto;
- limite de uso aprovado;
- rate limit;
- ausência de acesso/permissão ao modelo configurado.

Portanto, validar apenas que “há uma assinatura OpenAI” é insuficiente; é necessário validar o billing e os limites da **organização/projeto de API** associados à chave usada pelo SearchGEO.

## DeepSeek

```powershell
$env:DEEPSEEK_API_KEY = "<chave-da-DeepSeek-API>"
searchgeo audit https://example.com --ai-provider deepseek
```

Modelos:

```text
deepseek-v4-pro
deepseek-v4-flash
```

Default `deepseek-v4-pro` / `HIGH`.

A qualificação SearchGEO permanece `PROVISIONAL`.

### Limitações de plano DeepSeek

O SearchGEO usa a DeepSeek API padrão. O saldo disponível pode conter `granted_balance` e `topped_up_balance`; a documentação oficial informa que ambos compõem o saldo total e que o saldo concedido é consumido primeiro quando disponível.

`HTTP 402` significa saldo insuficiente da conta de API. A existência de uma API key, isoladamente, não garante saldo disponível. Limites de concorrência são aplicados no nível da conta, independentemente de qual API key seja usada.

Não há no contrato atual do SearchGEO um modo alternativo de assinatura DeepSeek com endpoint próprio. Se o fornecedor introduzir produto/plano com credencial ou Base URL diferente, ele deve ser tratado como **não homologado** até documentação e validação específicas.

## Xiaomi MiMo

### Pay-as-you-go — modo suportado

```powershell
$env:MIMO_API_KEY = "<chave-sk-...>"
searchgeo audit https://example.com --ai-provider mimo
```

Modelos:

```text
mimo-v2.5-pro
mimo-v2.5
```

Default `mimo-v2.5-pro` / `THINKING_ENABLED`.

A qualificação SearchGEO permanece `PROVISIONAL`.

O adapter atual usa o endpoint Pay-as-you-go:

```text
https://api.xiaomimimo.com/v1/responses
```

Logo, a credencial operacional esperada é uma chave MiMo Pay-as-you-go no formato `sk-...`, com saldo PAYG disponível.

### Token Plan `tp-...` — não usar no SearchGEO atual

O MiMo Token Plan é um produto separado. Ele usa:

```text
API key: tp-...
Base URL: https://token-plan-<região>.xiaomimimo.com/v1
```

A MiMo informa que `tp-...` e `sk-...` são independentes e não podem ser misturados. O Token Plan também possui Base URL dedicada por região.

**O SearchGEO atual não implementa seleção desse Base URL e não deve receber uma chave `tp-...`.** Além da incompatibilidade técnica atual, a documentação oficial do Token Plan restringe o pacote a ferramentas de programação e proíbe chamadas de automated scripts/custom application backends fora desse escopo. O SearchGEO é um auditor automatizado; portanto o Token Plan não deve ser usado como forma de financiar as chamadas do produto sem autorização explícita do fornecedor que cubra esse caso de uso.

Consequências práticas:

- `tp-...` no endpoint PAYG pode retornar `401` por mistura de Token Plan e Pay-as-you-go;
- `sk-...` no endpoint PAYG pode retornar `402` quando o saldo PAYG estiver insuficiente;
- créditos exibidos no Token Plan não são saldo da chave PAYG `sk-...`;
- mudar apenas a chave sem mudar o produto de billing não transfere créditos entre os dois modos.

Não alterar endpoint/credencial para contornar restrição de plano.

## Provider explícito

Quando um provider é selecionado explicitamente:

- somente ele pode atender a análise;
- ausência das chaves dos outros providers não interfere;
- não existe cross-provider fallback;
- após falha qualificadora, o provider pode ficar `QUARANTINED_FOR_AUDIT`;
- não há retries sucessivos em novas URLs após quarantine.

Provider explícito sem token fica `NOT_CONFIGURED` e não realiza chamada.

## AUTO

```powershell
searchgeo audit https://example.com --ai-provider auto
```

A cadeia é construída uma vez com providers elegíveis. Providers sem token ou configuração inválida são excluídos.

Default de preferência para os modelos default:

```text
OpenAI gpt-5.6-terra
→ DeepSeek deepseek-v4-pro
→ MiMo mimo-v2.5-pro
```

A ordem é política SearchGEO, não benchmark científico universal.

No caso MiMo, “configurado” deve ser entendido operacionalmente como credencial PAYG `sk-...` adequada ao endpoint suportado. O runtime atual não faz validação preventiva do prefixo da chave; por isso a documentação deve ser seguida antes de configurar `MIMO_API_KEY`.

### Fluxo de uma tentativa

1. selecionar primeiro provider saudável da cadeia;
2. fazer uma chamada estruturada;
3. validar resposta/contrato/evidências;
4. se válida, aceitar e encerrar o contexto;
5. se falhar de forma qualificadora, quarantinar e tentar próximo provider quando permitido.

**Um resultado válido não é sobrescrito por providers posteriores.**

## URL lock

Quando uma URL recebe primeiro resultado válido, o provider fica associado àquela URL para consistência entre contextos.

Se o mesmo provider falhar no segundo dispositivo da mesma URL em `both`, outro provider não completa essa URL com semântica de fornecedor diferente. O contexto faltante permanece degradado/UNKNOWN e o provider pode ser quarantined para URLs seguintes.

Em modo `mobile` ou `desktop`, existe apenas um contexto por URL e esse caso não ocorre dentro da mesma execução.

## Timeout

Variável:

```text
SEARCHGEO_AI_TIMEOUT_SECONDS
```

Default CLI:

```text
180
```

Exemplo:

```powershell
$env:SEARCHGEO_AI_TIMEOUT_SECONDS = "240"
```

Número finito > 0.

Não há retry automático após timeout. A API pode ter recebido/processado a chamada mesmo quando o cliente local expirou; repetir automaticamente poderia duplicar consumo.

## Classes operacionais de erro

O runtime normaliza falhas como, conforme o caso:

- autenticação;
- quota/crédito;
- rate limit;
- modelo/permissão;
- rede;
- timeout;
- servidor;
- contrato/resposta inválida/vazia.

Mensagem sensível do provider não deve ser copiada integralmente ao report.

Antes de interpretar um erro como “sem créditos”, confirme também produto/plano, tipo de chave e endpoint. Em especial, no MiMo, `401` pode indicar mistura Token Plan/PAYG e `402` representa saldo insuficiente do modo de cobrança efetivamente chamado.

## Evidência

A resposta do provider só é aceita se satisfizer o contrato estruturado e referenciar evidências válidas do contexto fornecido. Evidência inventada degrada a análise para estado semântico inválido/UNKNOWN; não é usada para criar FAIL.

## Confidence

A confidence retornada pelo provider em uma avaliação semântica individual **não é automaticamente a Confidence do SCORE-GEO-002**.

Da mesma forma, `Confidence LOW` no score não deve disparar, sozinha, uma recomendação para reescrever conteúdo. Alteração de conteúdo deve ser sustentada por RuleExecution/finding e evidência específica.

## Telemetria

A saída final fica em:

```text
report/ai-usage.html
```

A página pode mostrar:

- IA habilitada;
- estratégia;
- provider/model efetivo;
- status;
- cadeia inicial;
- URL/device por tentativa;
- input/output/reasoning tokens;
- duração;
- custo estimado;
- erro sanitizado.

No SQLite:

```text
ai_audit_sessions
ai_provider_attempts
provider_pricing_catalog
```

O `ESTIMATED_COST` não é invoice e não identifica automaticamente qual produto/plano comercial externo está financiando a chamada.

## Separação do readiness

`report/index.html`, `mobile.html` e `desktop.html` apresentam qualidade/readiness do website.

`report/ai-usage.html` apresenta funcionamento do provider.

Essa separação é deliberada: provider indisponível reduz o que o auditor consegue concluir, mas não é defeito do conteúdo auditado.

## Segurança

Nunca persistir:

- API key;
- Authorization;
- body integral com segredo;
- resposta de erro não sanitizada quando puder conter informação sensível.

Validação de presença:

```powershell
Test-Path Env:OPENAI_API_KEY
Test-Path Env:DEEPSEEK_API_KEY
Test-Path Env:MIMO_API_KEY
```

Presença da variável não prova compatibilidade do plano. Para MiMo, valide também que a chave destinada ao SearchGEO é PAYG (`sk-...`) e não Token Plan (`tp-...`). Não imprima a chave completa para diagnosticar prefixo ou existência.

## Conteúdo gerado por IA

O baseline atual **não gera texto para publicação**.

Uma evolução posterior está no backlog para, opcionalmente e com default OFF, sugerir texto/local de inserção com base em findings semânticos. Essa capacidade não deve:

- alterar automaticamente o site;
- recalcular score retrospectivamente;
- transformar sugestão em finding;
- ser acionada apenas por Confidence LOW;
- produzir texto artificial “para IA” sem benefício real ao usuário.

Isso também mantém alinhamento com o guia do Google de 2026, que não exige reescrever conteúdo especificamente para sistemas generativos.
