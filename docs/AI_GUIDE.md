# AI_GUIDE.md

Guia de uso da camada semântica opcional e da remediação textual M20 do SearchGEO.

## Princípio

IA externa é capacidade complementar. O auditor permanece funcional sem IA.

Falha, indisponibilidade, quota, timeout ou credencial ausente de um provider é limitação operacional da auditoria; **não é finding do website**.

Há duas finalidades distintas de IA:

1. **M18/M7 — análise semântica:** pode produzir SemanticAssessments/entidades/intents usados no universo de RuleExecutions;
2. **M20 — remediação textual opcional:** acontece somente depois de findings/scoring e produz sugestões advisory; não altera a avaliação já concluída.

A revisão JSON-LD de M20 é determinística e não depende de API externa.

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

A seleção acontece antes do rendering. M7 e M20 trabalham somente sobre snapshots existentes. Consequência prática:

- `mobile`: nenhuma chamada Desktop;
- `desktop`: nenhuma chamada Mobile;
- `both`: os dois contextos quando disponíveis/elegíveis.

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
- o website não recebe FAIL por ausência de provider;
- revisão JSON-LD determinística continua disponível em `report/content-suggestions.html`.

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

- somente ele pode atender a análise semântica;
- ausência das chaves dos outros providers não interfere;
- não existe cross-provider fallback para M18 explícito;
- após falha qualificadora, o provider pode ficar `QUARANTINED_FOR_AUDIT`;
- não há retries sucessivos em novas URLs após quarantine.

Provider explícito sem token fica `NOT_CONFIGURED` e não realiza chamada.

M20 não reativa um provider já quarantined pela análise semântica.

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

### Fluxo M18

1. selecionar primeiro provider saudável da cadeia;
2. fazer uma chamada estruturada;
3. validar resposta/contrato/evidências;
4. se válida, aceitar e encerrar o contexto;
5. se falhar de forma qualificadora, quarantinar e tentar próximo provider quando permitido.

**Um resultado válido não é sobrescrito por providers posteriores.**

## URL lock

Na finalidade M18, quando uma URL recebe primeiro resultado válido, o provider fica associado àquela URL para consistência entre contextos.

Se o mesmo provider falhar no segundo dispositivo da mesma URL em `both`, outro provider não completa essa URL com semântica de fornecedor diferente. O contexto faltante permanece degradado/UNKNOWN e o provider pode ser quarantined para URLs seguintes.

M20 possui pinning próprio por URL para sua finalidade. O primeiro provider M20 que retorna proposta válida fica associado à URL para contextos M20 subsequentes, sem misturar a finalidade de análise semântica com a de remediação.

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

M20 reutiliza o timeout do provider já configurado.

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

## Evidência M18

A resposta semântica só é aceita se satisfizer o contrato estruturado e referenciar evidências válidas do contexto fornecido. Evidência inventada degrada a análise para estado semântico inválido/UNKNOWN; não é usada para criar FAIL.

## M20 — remediação textual opcional

Default:

```text
OFF
```

Habilitação:

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

### O que entra no request

Somente estado persistido por página/snapshot/device:

- URL;
- title;
- conteúdo principal limitado;
- findings contentuais/semânticos elegíveis;
- observed/expected desses findings;
- evidence IDs e observed values vinculados.

`Confidence LOW` do score, isoladamente, **não entra como gatilho**.

### O que sai

Uma sugestão aceita contém:

```text
finding_id
objetivo
local sugerido
texto exato proposto
evidence_ids
confidence da sugestão
review_note
provider/model
```

A aplicação não escreve no website nem altera a recomendação/score original.

### Validação factual

O contrato do provider exige abordagem people-first e proíbe explicitamente:

- keyword stuffing;
- word count arbitrário;
- reescrita só “para IA”;
- chunking artificial;
- fake freshness;
- claims, preços, datas, estatísticas, garantias, credenciais, experiência ou fontes inventadas.

Além da instrução, a validação local rejeita `finding_id`/`evidence_id` fora do universo fornecido e rejeita novos tokens numéricos que não existam no conteúdo/evidências persistidos.

Esse filtro numérico é contenção adicional, não prova de factualidade completa. Revisão humana continua obrigatória.

### Falha M20

Se a etapa textual falhar ou não houver provider saudável:

- score/findings já calculados permanecem intactos;
- o audit não deve ser invalidado;
- a telemetria registra o estado operacional;
- JSON-LD determinístico continua disponível.

## JSON-LD

M20 não usa um prompt livre para inventar Structured Data.

### Quando ausente

O auditor pode propor um baseline conservador Schema.org `WebPage` com valores persistidos:

```json
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "url": "<canonical-ou-url-normalizada>",
  "inLanguage": "pt-BR",
  "name": "<title observado>",
  "description": "<description observada>"
}
```

Campos ausentes na página não são inventados. Um `mainEntity` só pode ser materializado quando a entidade persistida for única, de alta confiança e suficientemente sustentada; a omissão é preferida à especulação.

### Quando existente

O auditor não reescreve o graph. A revisão genérica pode apontar:

- parse errors;
- blocos idênticos duplicados;
- ausência global de `@context`;
- nós sem `@type`;
- `WebPage` sem `url`, `name`, `description` ou `inLanguage` quando os valores correspondentes já são conhecidos;
- necessidade de validar propriedades obrigatórias/recomendadas do tipo específico.

### Limites

JSON-LD é `OPCIONAL / REFORÇO`, não requisito universal de GEO. O Google aceita JSON-LD, Microdata e RDFa e recomenda JSON-LD pela facilidade de implementação. Structured Data deve representar conteúdo visível/relevante e markup válido não garante rich result.

Referências:

- `https://developers.google.com/search/docs/appearance/structured-data/sd-policies`
- `https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data`
- `https://schema.org/docs/documents.html`
- `https://developers.google.com/search/docs/fundamentals/ai-optimization-guide`

## Confidence

A confidence retornada pelo provider em uma avaliação semântica individual **não é automaticamente a Confidence do SCORE-GEO-002**.

Da mesma forma, `Confidence LOW` no score não dispara automaticamente M20. Alteração de conteúdo deve ser sustentada por RuleExecution/finding e evidência específica.

## Telemetria

A saída final fica em:

```text
report/ai-usage.html
```

A página separa:

- sessão/tentativas M18 de análise semântica;
- tentativas M20 de remediação textual.

Quando disponíveis, são exibidos provider/model, URL/device, status, tokens, duração, custo estimado local e erro sanitizado.

No SQLite, M18 usa:

```text
ai_audit_sessions
ai_provider_attempts
provider_pricing_catalog
```

M20 usa:

```text
content_remediation_runs
content_remediation_attempts
content_remediation_suggestions
jsonld_remediation_suggestions
```

O `ESTIMATED_COST` não é invoice.

## Separação do readiness

`report/index.html`, `mobile.html` e `desktop.html` apresentam qualidade/readiness do website.

`report/remediation.html` apresenta o plano técnico baseado em findings.

`report/content-suggestions.html` apresenta sugestões M20 e revisão JSON-LD advisory.

`report/ai-usage.html` apresenta funcionamento/custo do provider.

Essa separação é deliberada: provider indisponível reduz o que o auditor consegue concluir/sugerir, mas não é defeito do conteúdo auditado.

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

## Conteúdo sugerido por IA

M20 **gera proposta para revisão, não texto para publicação automática**.

A proposta:

- não altera o site;
- não recalcula score;
- não vira finding;
- não é acionada apenas por Confidence LOW;
- deve melhorar valor para o usuário real;
- deve ser descartada quando a evidência não sustenta texto exato seguro.

Isso mantém alinhamento com o guia do Google de 2026, que não exige reescrever conteúdo especificamente para sistemas generativos.
