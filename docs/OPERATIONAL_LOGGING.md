# Log operacional do SearchGEO

O SearchGEO mantém um log operacional persistente por auditoria para facilitar diagnóstico sem depender do histórico do terminal.

## Localização

```text
audits/<AUD-ID>/logs/audit.log
```

A CLI imprime esse caminho ao final da execução quando o arquivo existe.

## Formato

O arquivo usa **JSON Lines (JSONL)**: cada linha é um objeto JSON independente.

Exemplo sanitizado:

```json
{"timestamp":"2026-09-04T01:11:05+00:00","level":"WARNING","event":"M21_EXTERNAL_ATTEMPT","service":"PAGESPEED_INSIGHTS","status":"ERROR","device":"DESKTOP","url":"https://example.com/","duration_ms":60233,"error_code":"TIMEOUTERROR"}
```

Isso permite leitura humana e também processamento com PowerShell, Python ou ferramentas de observabilidade.

## Eventos principais

O ciclo principal pode registrar:

```text
AUDIT_STARTED
RENDERING_COMPLETED
AI_RUNTIME_RECORDED
REPORT_SITE_GENERATED
AUDIT_COMPLETED
AUDIT_FAILED
```

A camada M21 pode registrar:

```text
M21_STARTED
M21_EXTERNAL_ATTEMPT
M21_COMPLETED
M21_REPORT_GENERATED
M21_RUNTIME_FAILURE
```

## Diagnóstico M21

Para cada tentativa PageSpeed/CrUX são registrados, quando aplicáveis:

- serviço;
- URL auditada;
- contexto Mobile/Desktop;
- status `SUCCESS`/`ERROR`;
- status HTTP;
- duração em milissegundos;
- código e mensagem de erro sanitizados;
- referência do artifact de resposta.

Exemplo de cenário parcial:

```text
PAGESPEED_INSIGHTS / MOBILE → ERROR / TIMEOUTERROR
CRUX_API / MOBILE           → SUCCESS / HTTP 200
M21                         → PARTIAL
```

Nesse caso os dados CrUX continuam válidos e são preservados. A falha PageSpeed não deve ser mascarada por `successful_contexts` e não transforma a auditoria principal em erro.

## Segurança

O log não deve conter:

- `OPENAI_API_KEY`;
- `DEEPSEEK_API_KEY`;
- `MIMO_API_KEY`;
- `SEARCHGEO_PAGESPEED_API_KEY`;
- `SEARCHGEO_CRUX_API_KEY`;
- Authorization headers;
- access tokens;
- passwords;
- request URLs que contenham chaves.

Campos cujo nome representa credencial são redigidos como:

```text
[REDACTED]
```

É permitido registrar somente a existência da configuração como booleano, por exemplo:

```json
{"pagespeed_api_key_configured":true,"crux_api_key_configured":true}
```

## Fail-open

O log é telemetria auxiliar. Uma falha de escrita do próprio `audit.log` não pode:

- alterar `SCORE-GEO-002`;
- criar Finding/Recommendation;
- mudar RuleExecution;
- invalidar uma auditoria que poderia ser concluída normalmente.

## Consultas rápidas no PowerShell

Últimas linhas:

```powershell
Get-Content .\audits\<AUD-ID>\logs\audit.log -Tail 30
```

Somente eventos com erro ou warning:

```powershell
Get-Content .\audits\<AUD-ID>\logs\audit.log |
  ForEach-Object { $_ | ConvertFrom-Json } |
  Where-Object { $_.level -in @('WARNING','ERROR') } |
  Format-List
```

Somente PageSpeed/CrUX:

```powershell
Get-Content .\audits\<AUD-ID>\logs\audit.log |
  ForEach-Object { $_ | ConvertFrom-Json } |
  Where-Object { $_.event -eq 'M21_EXTERNAL_ATTEMPT' } |
  Format-Table service,device,status,http_status,duration_ms,error_code -AutoSize
```

## Timeout PageSpeed

O default M21 permanece 60 segundos por chamada. PageSpeed pode eventualmente exigir mais tempo, dependendo da URL e do serviço externo.

Para permitir espera maior de forma explícita:

```powershell
searchgeo audit "https://example.com" `
  --web-performance `
  --web-performance-timeout-seconds 180
```

Não há retry automático após timeout.
