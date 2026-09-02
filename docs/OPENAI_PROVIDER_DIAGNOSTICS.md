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
