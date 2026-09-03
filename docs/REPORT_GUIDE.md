# Guia do Relatório

O SearchGEO gera dois relatórios HTML estáticos a partir do estado persistido:

```text
report.html
remediation.html
```

A fonte primária continua sendo `audit.db` + artifacts. Os HTMLs são projeções para leitura humana.

# Abrir os relatórios

```powershell
Start-Process .\audits\AUD-...\report.html
Start-Process .\audits\AUD-...\remediation.html
```

Não é necessário web server.

# `report.html`

É a visão principal orientada à auditoria e às páginas.

Pode apresentar:

- projeto/audit ID;
- domínio/origin e modo de entrada;
- URLs fornecidas/auditadas;
- limitações;
- Compatibilidade GEO;
- Score, Coverage, Confidence e Consolidation;
- Desktop/Mobile separados;
- recursos do domínio;
- inventário de páginas;
- findings/evidence;
- screenshots/DOM;
- actionability/prioridade;
- causa raiz/remediação;
- contexto semântico;
- telemetria M18 de IA.

# `remediation.html`

É a visão transversal orientada a problema/regra.

Agrupa ocorrências por escopo/regra/actionability e mostra, quando disponível:

- páginas afetadas;
- devices;
- resultado;
- prioridade;
- causa raiz;
- selector/alvo quando determinável;
- orientação de correção;
- critérios de aceite/revalidação;
- referências técnicas.

Falha de provider de IA aparece somente como **contexto operacional**, nunca como finding/recommendation do website.

# Compatibilidade GEO, Coverage, Confidence e Consolidation

Esses conceitos não são equivalentes.

## Compatibilidade GEO

Representa readiness quando `OVERALL_READINESS` está metodologicamente consolidado.

## Coverage

Representa quanto do universo aplicável foi efetivamente avaliado.

Coverage baixa não significa website ruim.

## Confidence

Representa a confiabilidade da conclusão considerando evidência/capacidade analítica.

## Consolidation

Indica se existe base suficiente para consolidar a dimensão/overall.

# Score zero versus não calculado

Score válido igual a zero:

```text
Score: 0.0
Estado: CALCULADO
```

Sem base suficiente:

```text
Score: NÃO DETERMINADO
Estado: NÃO CALCULADO
```

`Coverage: 0%` não significa `Score GEO: 0`.

# Desktop e Mobile

São avaliados separadamente desde rendering até scoring. Não existe média artificial.

Exemplo válido:

```text
Desktop: 82 / Alta / Consolidado
Mobile: NÃO DETERMINADA
```

# Actionability

| Valor | Interpretação |
|---|---|
| `REQUIRED_FIX` | correção evidence-backed requerida |
| `REVIEW_RECOMMENDED` | revisão humana/contextual necessária |
| `OPTIONAL_IMPROVEMENT` | melhoria não bloqueante |
| `NO_ACTION` | nenhuma ação necessária |
| `INSUFFICIENT_EVIDENCE` | não há base para ordenar mudança |

Actionability não altera o score.

# Evidência e selector

O auditor pode exibir:

- URL/device;
- Evidence/RuleExecution;
- selector observado;
- tag/id/classes;
- trecho HTML persistido;
- bounding box;
- screenshot local.

Quando um único elemento não pode ser determinado com segurança, o relatório usa `NÃO DETERMINADO` em vez de inventar selector.

# Uso de IA — M18

O `report.html` possui a seção:

```text
Uso de IA — execução e telemetria
```

Ela é operacional e separada dos findings do website.

## Campos de sessão

O relatório diferencia:

- IA habilitada: `SIM`/`NÃO`;
- estratégia: `NONE`, `SINGLE_PROVIDER` ou `AUTO`;
- provider inicialmente selecionado;
- provider efetivamente utilizado;
- modelo efetivo;
- reasoning/depth;
- status operacional da sessão;
- quantidade de URLs analisadas com sucesso por provider;
- cadeia inicial imutável;
- cobertura semântica externa;
- eventos de failover.

## Tabela de tentativas

Cada tentativa persistida pode aparecer com:

| Campo | Significado |
|---|---|
| URL | página associada ao snapshot |
| Device | Desktop/Mobile |
| Provider | OpenAI, DeepSeek ou MiMo |
| Model | model ID efetivamente configurado |
| Depth | reasoning profile normalizado |
| Status | sucesso/erro contratual/técnico etc. |
| Tokens input | somente se provider reportou |
| Tokens output | somente se provider reportou |
| Tokens reasoning | somente se provider reportou |
| Estimated cost | estimativa local quando calculável |
| Duration | duração da tentativa |
| Error | diagnóstico sanitizado |

Tokens ausentes ficam vazios/`—`; não são inventados.

# Interpretação dos estados de IA

## `NO_AI`

Nenhum provider efetivo. Pode ocorrer por:

- `--ai-provider none`;
- provider explícito sem token;
- AUTO sem providers elegíveis.

Regras semantic-only podem ficar `UNKNOWN`. Isso não é `FAIL` do website.

## `FULL`

Provider produziu respostas válidas para o universo aplicável necessário ao modo FULL.

## `DEGRADED`

Parte da análise semântica ficou indisponível/rejeitada.

Exemplos:

- provider explícito falhou;
- pinned provider falhou no segundo device;
- resposta violou contrato/schema/evidence.

## `CHAIN_EXHAUSTED`

Exclusivo da estratégia `AUTO`: todos os providers elegíveis foram quarantined após falhas.

A auditoria registra:

```text
AI_PROVIDER_CHAIN_EXHAUSTED
```

Isso continua sendo limitação operacional da auditoria.

# Provider explícito sem token

O relatório não deve afirmar que houve chamada externa.

Comportamento:

```text
strategy = SINGLE_PROVIDER
provider = configurado conceitualmente
chamada externa = nenhuma
estado = NOT_CONFIGURED / sem IA efetiva
```

# Provider explícito com erro/crédito

Exemplo:

```text
OpenAI -> CREDIT_ERROR
```

O relatório deve mostrar tentativa sem sucesso/estado degradado, não ausência fictícia de configuração.

Não existe fallback para outro fornecedor nesse modo.

# AUTO e failover

Exemplo:

```text
OpenAI -> CREDIT_ERROR
DeepSeek -> SUCCESS
```

O relatório pode indicar:

```text
OpenAI (CREDIT_ERROR) → DeepSeek
```

OpenAI permanece quarantined pelo restante do audit.

# Lock por URL

Exemplo:

```text
URL A Desktop -> DeepSeek SUCCESS
URL A Mobile  -> DeepSeek TIMEOUT
```

MiMo não é usado para completar URL A Mobile. O relatório deve refletir a perda de cobertura daquele contexto. MiMo pode ser usado em URL seguinte se for o próximo provider saudável.

# `ESTIMATED_COST`

É calculado com catálogo local versionado e usage reportado pelo provider.

Não é:

- invoice;
- billing oficial;
- valor garantido;
- componente do score.

Quando os campos necessários não existirem, o custo permanece não calculado.

# Diagnósticos de erro de IA

Podem aparecer classes como:

```text
AUTH_ERROR
QUOTA_ERROR
CREDIT_ERROR
RATE_LIMIT_ERROR
MODEL_ERROR
PERMISSION_ERROR
NETWORK_ERROR
TIMEOUT_ERROR
SERVER_ERROR
CONTRACT_ERROR
EMPTY_RESPONSE
INVALID_RESPONSE
UNKNOWN_PROVIDER_ERROR
```

Mensagens potencialmente sensíveis não precisam ser reproduzidas para classificar o erro.

# `audit.db` e relatório

A seção de IA é construída a partir das tabelas:

```text
ai_audit_sessions
ai_provider_attempts
provider_pricing_catalog
```

Se for necessário diagnóstico técnico mais profundo, consulte o DB. O HTML não substitui a persistência.

# Logging versus relatório

M18 também emite logging operacional sanitizado quando `log_level` permite.

Logs podem conter:

- audit ID;
- URL/device;
- provider/model/depth;
- status;
- duração;
- tokens reportados;
- custo estimado;
- error class.

Não contêm API key, Authorization ou corpo integral da requisição.

A baseline não cria `audit.log` automaticamente. Portanto:

```text
registro persistente = audit.db + report.html
logging do processo = console/handler configurado
```

# `COMPLETE_WITH_LIMITATIONS`

Esse status não significa necessariamente falha do website. Pode resultar de:

- NO_AI;
- provider indisponível;
- AUTO chain exhausted;
- rendering/evidence incompleto;
- max pages;
- regras UNKNOWN/ERROR;
- score não consolidado.

# Segurança visual

O relatório deve permanecer sanitizado:

- sem API keys;
- sem Authorization;
- sem secrets de provider;
- conteúdo dinâmico HTML-escaped;
- sem chain-of-thought.

# Portabilidade

Screenshots/artifacts são locais e referenciados por paths relativos. Para transportar uma auditoria, copie/compacte o workspace completo, não apenas `report.html`.

# Referências

- [Guia do usuário](USER_GUIDE.md)
- [Referência completa da CLI](CLI_REFERENCE.md)
- [Guia de IA](AI_GUIDE.md)
- [Outputs e artifacts](OUTPUTS_AND_ARTIFACTS.md)
- [Troubleshooting](TROUBLESHOOTING.md)
