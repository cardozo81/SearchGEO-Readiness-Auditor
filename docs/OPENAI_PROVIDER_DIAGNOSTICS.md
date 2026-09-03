# OpenAI Provider Diagnostics

O SearchGEO utiliza a OpenAI somente para a camada semântica opcional. Falha do provider não deve ser convertida em defeito do website nem alterar `SCORE-GEO-001`.

A partir do hotfix do issue #23, o adapter usado pela CLI:

- envia o contrato explícito das 22 regras `BR-GEO-028..049`;
- exige exatamente uma avaliação por regra;
- rejeita saída parcial como indisponível;
- preserva diagnóstico sanitizado de HTTP sem persistir API key nem corpo/mensagem completa;
- diferencia no relatório `Uso de IA: SIM`, `NÃO` e `TENTATIVA SEM SUCESSO`.

Exemplo de limitação sanitizada:

```text
AI_PROVIDER_UNAVAILABLE:HTTP_429:type=insufficient_quota:code=credit_balance_exhausted:request_id=req_...
```

O `request_id` aparece somente quando fornecido pela API. Mensagens completas de erro não são persistidas por esse diagnóstico.

Um `HTTP_429` com `credit_balance_exhausted` indica indisponibilidade de quota/créditos da conta da API; a auditoria permanece `DEGRADED` e regras dependentes do provider podem ficar `UNKNOWN`.

## `TIMEOUT_ERROR` com chave configurada e saldo disponível

`TIMEOUT_ERROR` é diferente de erro de saldo, quota ou autenticação. Ele indica que a chamada HTTP não terminou dentro do limite operacional do cliente; por si só, não demonstra problema na API key nem ausência de créditos.

Na CLI atual, o timeout de chamadas semânticas externas é `180` segundos por padrão. Ele pode ser ajustado sem alterar o código:

```powershell
$env:SEARCHGEO_AI_TIMEOUT_SECONDS = "240"
searchgeo audit https://example.com --ai-provider openai --ai-model gpt-5.6-terra
```

O valor deve ser numérico, finito e maior que zero.

O SearchGEO não faz retry automático após timeout. Isso é intencional: uma chamada que expirou localmente pode ter sido processada pelo provider, portanto repetir silenciosamente poderia gerar consumo duplicado. Em provider explícito, a falha coloca o provider em `QUARANTINED_FOR_AUDIT`; em `auto`, o próximo provider saudável pode ser tentado conforme a política M18.

## Independência entre providers

Uma execução explícita:

```powershell
searchgeo audit https://example.com --ai-provider openai
```

depende somente da configuração OpenAI. A ausência de `DEEPSEEK_API_KEY` e `MIMO_API_KEY` não invalida nem sobrescreve o resultado OpenAI.

Em `auto`, providers sem key não entram na cadeia. Quando um provider retorna uma análise válida para um contexto, a cadeia é encerrada naquele ponto; nenhum provider posterior é chamado para sobrescrever o resultado. O provider também fica fixado à URL para manter Desktop/Mobile comparáveis.
