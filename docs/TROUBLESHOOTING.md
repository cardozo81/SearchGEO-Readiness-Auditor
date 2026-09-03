# Troubleshooting

Use este guia para distinguir falha do ambiente, limitação da auditoria, falha do provider e problema real do target.

# CLI e instalação

## `searchgeo`: comando não encontrado

Diagnóstico:

```powershell
python --version
python -m pip show searchgeo-readiness-auditor
Get-Command searchgeo -ErrorAction SilentlyContinue
```

Correção:

```powershell
python -m pip install -e .
```

Ou use `.\.venv\Scripts\searchgeo.exe`.

## Python incompatível

```powershell
python --version
```

O contrato atual exige CPython `>=3.13,<3.14`.

## Playwright/package ausente

```powershell
python -m pip show playwright
python -m pip show searchgeo-readiness-auditor
python -m pip install -e .
```

## Chromium ausente

Sintoma típico: `BROWSER_UNAVAILABLE`.

```powershell
python -m playwright install chromium
```

Ou:

```powershell
$env:PLAYWRIGHT_CHROMIUM_EXECUTABLE = "C:\caminho\para\chrome.exe"
```

Sem browser funcional, a perda de rendering é limitação da auditoria, não `FAIL` automático do website.

# Target, rede e rendering

## DNS/conexão

```powershell
Resolve-DnsName example.com
Test-NetConnection example.com -Port 443
```

Falha local de rede/proxy não deve ser atribuída automaticamente ao website. Falha reproduzível no target pode ser problema real de acessibilidade.

## TLS

Valide certificado, cadeia e hostname no mesmo ambiente. Distinga falha do target de trust/proxy corporativo.

## Proxy/firewall

A baseline não expõe flags próprias de proxy. Se HTTP/Chromium/provider funcionam em outro host e falham no ambiente atual, revise egress, proxy, DNS split-horizon e EDR.

## Timeout de rendering

`NAVIGATION_TIMEOUT` é localizado ao snapshot/device. O timeout não é configurável pela CLI atual.

## `networkidle` limitado

`settle_outcome = BOUNDED_TIMEOUT` pode ocorrer com analytics/long polling. O renderer ainda captura o DOM conforme a política implementada; isso não é falha por si só.

## HTTP 4xx/5xx

Consulte Evidence/RuleExecution e artifacts RAW. Regras derivadas podem ficar `UNKNOWN`/`NOT_APPLICABLE` para evitar cascading failure.

# robots.txt e sitemap

## robots.txt ausente

Ausência/404 de `robots.txt` não é automaticamente `FAIL`.

## robots.txt inválido

Consulte Evidence `ROBOTS_RULE` e o artifact HTTP correspondente.

## sitemap ausente/inválido

Ausência de sitemap não é `FAIL` automático. Malformação é registrada sem abortar toda a auditoria.

# Desktop/Mobile e SPA

## Um device sem rendered artifact

Verifique PageSnapshot/browser metadata e `artifacts/rendered`. Comparação Desktop/Mobile pode ficar `UNKNOWN`; não se inventa diferença negativa.

## RAW mínimo e RENDERED completo em SPA/CSR

Isso pode ser arquitetura válida. O auditor avalia recuperabilidade/direct routes/navegação/soft-404/lazy loading, não penaliza CSR/SPA apenas por existir.

# IA — primeiro diagnóstico

Confira qual modo foi solicitado:

```text
none
openai
deepseek
mimo
auto
```

A referência completa está em [AI_GUIDE.md](AI_GUIDE.md).

## Verificar tokens sem revelá-los

```powershell
Test-Path Env:OPENAI_API_KEY
Test-Path Env:DEEPSEEK_API_KEY
Test-Path Env:MIMO_API_KEY
```

Nunca use `Write-Output` para imprimir API keys em logs de suporte.

# Provider explícito sem token

Exemplo:

```powershell
searchgeo audit https://example.com --ai-provider openai
```

sem `OPENAI_API_KEY`.

Comportamento esperado:

- provider `NOT_CONFIGURED`;
- nenhuma chamada externa;
- auditoria continua sem IA efetiva;
- semantic-only pode ficar `UNKNOWN`;
- não é falha do website.

O mesmo vale para DeepSeek/MiMo com suas chaves específicas.

# AUTO sem token

```powershell
searchgeo audit https://example.com --ai-provider auto
```

Comportamento:

- providers sem token não entram na cadeia;
- se nenhum token/configuração elegível existir, nenhuma chamada externa é feita;
- não há erro de website por ausência da IA.

# Model inválido

M18 possui allowlist.

Aceitos:

```text
OPENAI:   gpt-5.6-sol | gpt-5.6-terra | gpt-5.6-luna
DEEPSEEK: deepseek-v4-pro | deepseek-v4-flash
MIMO:     mimo-v2.5-pro | mimo-v2.5
```

Provider explícito com model inválido é rejeitado pela configuração.

Em `auto`, provider com model/reasoning inválido é excluído da cadeia e aparece em `excluded_configurations`; outros providers elegíveis continuam.

# `--ai-model` com AUTO

Isto é inválido:

```powershell
searchgeo audit https://example.com --ai-provider auto --ai-model gpt-5.6-terra
```

Configure por variáveis:

```powershell
$env:SEARCHGEO_OPENAI_MODEL = "gpt-5.6-terra"
$env:SEARCHGEO_DEEPSEEK_MODEL = "deepseek-v4-pro"
$env:SEARCHGEO_MIMO_MODEL = "mimo-v2.5-pro"
searchgeo audit https://example.com --ai-provider auto
```

# Falhas de provider

Classes normalizadas:

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

## Token inválido

Esperado: `AUTH_ERROR` ou `PERMISSION_ERROR` conforme resposta do serviço.

Confirme credencial, escopo e endpoint acessível. Não copie o token para ticket/log.

## Sem créditos / saldo

Esperado: `CREDIT_ERROR` quando o provider fornece sinal classificável; em outros casos pode aparecer classe de quota/rate limit compatível com a resposta.

Isso é estado da conta/provider, não problema do website.

### Provider explícito

- chamada falha;
- provider entra em `QUARANTINED_FOR_AUDIT`;
- não é chamado novamente no mesmo audit;
- não existe fallback para outro fornecedor;
- sessão semântica fica `DEGRADED` quando o universo necessário não foi atendido.

### AUTO

- provider falho entra em `QUARANTINED_FOR_AUDIT`;
- próximo provider saudável pode ser tentado;
- provider quarantined não retorna no mesmo audit.

Se todos falharem:

```text
CHAIN_EXHAUSTED
AI_PROVIDER_CHAIN_EXHAUSTED
```

# Timeout/rede do provider

Esperado: `TIMEOUT_ERROR`/`NETWORK_ERROR`.

Verifique egress HTTPS, proxy/firewall, DNS e disponibilidade do provider. Em AUTO, o próximo provider saudável pode ser utilizado conforme as regras de lock/failover.

# Resposta inválida/contrato

Pode aparecer:

```text
CONTRACT_ERROR
EMPTY_RESPONSE
INVALID_RESPONSE
```

Causas possíveis:

- resposta vazia;
- JSON inválido;
- assessments incompletos;
- `rule_id` ausente/duplicado/desconhecido;
- enum inválido;
- `evidence_id` inventado;
- schema incompatível.

O SearchGEO descarta a análise; não converta manualmente resposta inválida em finding.

# Provider lock por URL

Cenário:

```text
URL A Desktop -> Provider X SUCCESS
URL A Mobile  -> Provider X falha
```

Comportamento esperado:

- Provider Y não completa URL A Mobile;
- URL A fica parcialmente degradada;
- Provider X é quarantined para URLs seguintes;
- URL B pode usar Provider Y.

Isso é intencional para evitar Desktop/Mobile da mesma URL produzidos por providers diferentes.

# Onde diagnosticar uso da IA

## `report.html`

Seção **Uso de IA — execução e telemetria**:

- estratégia;
- provider/model inicial e efetivo;
- status;
- cadeia inicial;
- failover;
- URL/device;
- tokens;
- `ESTIMATED_COST`;
- duração;
- erro sanitizado.

## `audit.db`

```text
ai_audit_sessions
ai_provider_attempts
provider_pricing_catalog
```

## Logging do processo

Quando `log_level` permite, M18 emite linha por tentativa e resumo de sessão com provider/model/status/duração/tokens/custo estimado/error_class.

A baseline **não cria `audit.log` automaticamente**. Se o terminal/logging externo não foi preservado, use `audit.db` e `report.html` como registro persistente.

# `ESTIMATED_COST`

Se aparecer vazio/`—`, isso pode ser legítimo. O SearchGEO só estima custo quando possui os token fields necessários e preço aplicável no catálogo local versionado.

Não use esse valor como invoice oficial.

# `audit.db` / filesystem

## Database ausente/corrompido

```powershell
Test-Path .\audits\AUD-...\audit.db
Get-Item .\audits\AUD-...\audit.db
```

`report.html` não substitui a fonte primária.

## Sem permissão de escrita

Use raiz gravável:

```powershell
searchgeo audit https://example.com --audits-root D:\SearchGEO\audits
```

# Relatórios ausentes

Se `report.html`/`remediation.html` não foram materializados, confira stdout/stderr e status persistido. Não há comando público de regeneração isolada; corrija o problema e reexecute.

# `COMPLETE_WITH_LIMITATIONS`

Não equivale automaticamente a site ruim. Pode refletir:

- `NO_AI`;
- provider sem token;
- provider indisponível/quarantined;
- `AI_PROVIDER_CHAIN_EXHAUSTED`;
- `max_pages`;
- regra `UNKNOWN`/`ERROR`;
- perda de rendering/evidence;
- score não consolidado.

# Escalonamento técnico

Preserve, sem secrets:

1. comando executado;
2. versão de Python/package;
3. Audit ID;
4. `audit.db`;
5. artifacts relevantes;
6. RuleExecution/Evidence IDs;
7. Desktop/Mobile;
8. modo IA (`NO_AI`, `FULL`, `DEGRADED`);
9. estratégia IA (`NONE`, `SINGLE_PROVIDER`, `AUTO`);
10. error class sanitizado;
11. seção de telemetria do report.

# Referências

- [Referência completa da CLI](CLI_REFERENCE.md)
- [Guia de IA](AI_GUIDE.md)
- [Configuração](CONFIGURATION.md)
- [Compatibilidade](COMPATIBILITY.md)
