# AI_GUIDE.md

Guia de uso da camada semântica opcional do SearchGEO.

## Princípio

IA externa é capacidade complementar. O auditor permanece funcional sem IA.

Falha, indisponibilidade, quota, timeout ou credencial ausente de um provider é limitação operacional da auditoria; **não é finding do website**.

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
$env:OPENAI_API_KEY = "<chave>"
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

## DeepSeek

```powershell
$env:DEEPSEEK_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider deepseek
```

Modelos:

```text
deepseek-v4-pro
deepseek-v4-flash
```

Default `deepseek-v4-pro` / `HIGH`.

A qualificação SearchGEO permanece `PROVISIONAL`.

## Xiaomi MiMo

```powershell
$env:MIMO_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider mimo
```

Modelos:

```text
mimo-v2.5-pro
mimo-v2.5
```

Default `mimo-v2.5-pro` / `THINKING_ENABLED`.

A qualificação SearchGEO permanece `PROVISIONAL`.

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

O `ESTIMATED_COST` não é invoice.

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

## Conteúdo gerado por IA

O baseline atual **não gera texto para publicação**.

Uma evolução posterior está no backlog para, opcionalmente e com default OFF, sugerir texto/local de inserção com base em findings semânticos. Essa capacidade não deve:

- alterar automaticamente o site;
- recalcular score retrospectivamente;
- transformar sugestão em finding;
- ser acionada apenas por Confidence LOW;
- produzir texto artificial “para IA” sem benefício real ao usuário.

Isso também mantém alinhamento com o guia do Google de 2026, que não exige reescrever conteúdo especificamente para sistemas generativos.
