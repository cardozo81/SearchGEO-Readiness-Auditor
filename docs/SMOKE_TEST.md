# Smoke Test Humano — Baseline Atual

Este roteiro homologa a baseline atual, incluindo M18. A existência deste documento não significa smoke aprovado.

# Registro

| Campo | Valor |
|---|---|
| Data/hora | |
| Operador | |
| Máquina/OS | |
| Python | |
| Package/version | |
| Chromium/Playwright | |
| Commit de `main` | |
| Targets | |
| Providers com credencial disponível | |

Use `PASS`, `FAIL` ou `NOT_APPLICABLE` e preserve evidência/path sem secrets.

# 1. Preparação

```powershell
python --version
python -m pip show searchgeo-readiness-auditor
python -m pip show playwright
searchgeo --version
searchgeo audit --help
```

Validar:

- CPython 3.13;
- package instalado;
- Chromium inicia;
- filesystem gravável;
- acesso aos targets;
- egress aos providers apenas quando IA for testada;
- nenhuma API key aparece em comando/log compartilhado.

# 2. Caso A — execução sem IA

```powershell
searchgeo audit https://<target-a> `
  --project "Smoke A — NO_AI" `
  --max-pages 3 `
  --ai-provider none `
  --audits-root .\smoke-audits
```

Validar:

- nenhuma API key necessária;
- pipeline determinístico conclui;
- Desktop/Mobile independentes;
- `audit.db`, `report.html`, `remediation.html` e artifacts existem;
- semantic-only insuficiente fica `UNKNOWN`, não `FAIL`;
- ausência de IA não recebe penalidade artificial;
- relatório explica limitação de cobertura quando aplicável.

# 3. Caso B — URL_SET / múltiplas páginas

```powershell
searchgeo audit `
  https://<origin>/ `
  https://<origin>/produto `
  https://<origin>/faq `
  --project "Smoke B — URL_SET" `
  --max-pages 3 `
  --ai-provider none `
  --audits-root .\smoke-audits
```

Também validar por arquivo:

```powershell
searchgeo audit --urls-file .\urls.txt --project "Smoke B arquivo" --ai-provider none --audits-root .\smoke-audits
```

Validar:

- um único `AUD-ID`;
- URLs normalizadas/deduplicadas;
- recursos de domínio não duplicados por página;
- menu/report/remediation mostram todas as páginas;
- screenshots/DOM por device não se sobrescrevem.

# 4. Caso C — SPA/CSR

```powershell
searchgeo audit https://<target-spa> --project "Smoke C — SPA" --max-pages 3 --ai-provider none --audits-root .\smoke-audits
```

Validar:

- RAW e RENDERED distinguíveis;
- shell RAW + conteúdo RENDERED não é penalizado só por CSR;
- arquitetura persistida;
- direct routes/navegação/lazy/soft-404 seguem evidência;
- falha em um device não apaga o outro.

# 5. Caso D — provider explícito

Execute somente se houver credencial real disponível e autorização para transmitir o conteúdo do target ao provider.

## OpenAI

```powershell
$env:OPENAI_API_KEY = "<chave>"
searchgeo audit https://<target-d> --project "Smoke D — OpenAI" --max-pages 1 --ai-provider openai --audits-root .\smoke-audits
```

## DeepSeek

```powershell
$env:DEEPSEEK_API_KEY = "<chave>"
searchgeo audit https://<target-d> --project "Smoke D — DeepSeek" --max-pages 1 --ai-provider deepseek --audits-root .\smoke-audits
```

## MiMo

```powershell
$env:MIMO_API_KEY = "<chave>"
searchgeo audit https://<target-d> --project "Smoke D — MiMo" --max-pages 1 --ai-provider mimo --audits-root .\smoke-audits
```

Para cada provider disponível, validar:

- model default correto;
- tentativa aparece em `ai_provider_attempts`;
- provider/model/depth/status aparecem no `report.html`;
- tokens aparecem somente se reportados;
- `ESTIMATED_COST` aparece somente quando calculável;
- nenhuma API key/Authorization aparece em DB/HTML/log;
- falha externa não vira finding do website.

Se a conta estiver sem créditos/quota, registrar o smoke como falha/limitação externa do provider, preservando `error_class` sanitizado. Não simular aprovação.

# 6. Caso E — provider explícito sem token

Remova a variável no shell do smoke:

```powershell
Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
searchgeo audit https://<target-e> --project "Smoke E — sem token" --max-pages 1 --ai-provider openai --audits-root .\smoke-audits
```

Validar:

- nenhuma chamada externa;
- provider `NOT_CONFIGURED`;
- auditoria continua;
- sem cross-provider fallback;
- ausência de token não é finding do website.

# 7. Caso F — AUTO multi-provider

Execute apenas se houver pelo menos duas credenciais reais autorizadas.

```powershell
$env:OPENAI_API_KEY = "<chave-openai>"
$env:DEEPSEEK_API_KEY = "<chave-deepseek>"
$env:MIMO_API_KEY = "<chave-mimo>"
searchgeo audit --urls-file .\urls.txt --project "Smoke F — AUTO" --ai-provider auto --audits-root .\smoke-audits
```

Validar:

- cadeia inicial contém somente providers elegíveis;
- ordem corresponde ao rank do model configurado;
- não há chamadas paralelas desnecessárias;
- primeiro sucesso encerra a cadeia daquele contexto;
- falha quarantina provider;
- provider quarantined não é chamado novamente;
- próximo saudável pode ser promovido;
- provider lock mantém Desktop/Mobile da mesma URL no mesmo provider;
- se pinned falhar no segundo device, outro provider não completa aquela URL;
- se todos AUTO falharem, status `CHAIN_EXHAUSTED` e limitação `AI_PROVIDER_CHAIN_EXHAUSTED` aparecem.

Se menos de duas credenciais estiverem disponíveis, marque este caso `NOT_APPLICABLE`/`SKIPPED_NO_CREDENTIALS`, não como PASS live.

# 8. Caso G — falha localizada controlada

Use fixture/target autorizado onde uma página/device falhe e outra parte continue.

Validar:

- erro associado ao recurso correto;
- páginas/devices independentes continuam quando possível;
- dependencies derivadas ficam `UNKNOWN`/`NOT_APPLICABLE` quando necessário;
- não há cascata artificial de FAIL;
- auditoria pode concluir `COMPLETE_WITH_LIMITATIONS`.

# 9. Verificação dos relatórios

No `report.html` validar:

- Compatibilidade GEO separada de Coverage/Confidence/Consolidation;
- Desktop/Mobile separados;
- score zero diferente de não calculado;
- findings/evidence rastreáveis;
- screenshots/DOM coerentes;
- actionability/prioridade coerentes;
- seção **Uso de IA — execução e telemetria** coerente com o modo usado;
- nenhuma chave/Authorization.

No `remediation.html` validar:

- grupos por problema/regra;
- links para páginas;
- causa raiz/remediação;
- contexto IA somente informativo;
- falha de IA não aparece como finding/recommendation.

# 10. Verificação do `audit.db`

Para pelo menos um finding, um score e, se IA foi usada, uma tentativa:

- Finding reabre;
- RuleExecution existe;
- Evidence existe;
- Score/ScoreContribution reabrem;
- `ai_audit_sessions` corresponde ao relatório;
- `ai_provider_attempts` corresponde às chamadas;
- `provider_pricing_catalog` contém versão de preço usada;
- secrets não estão persistidos.

# 11. Logging

Com `log_level=INFO`, quando IA foi tentada, verificar linhas sanitizadas de tentativa e sessão contendo provider/model/status/duração/tokens/custo/error_class.

A baseline não cria `audit.log` automaticamente; preserve stdout/stderr apenas se necessário para a homologação.

# 12. Resultado humano

```text
SMOKE TEST HUMANO — APROVADO
```

ou

```text
SMOKE TEST HUMANO — REPROVADO
```

Registrar separadamente casos `NOT_APPLICABLE` por ausência de credenciais externas.

| Campo | Valor |
|---|---|
| Operador | |
| Data | |
| Commit homologado | |
| Resultado | |
| Limitações externas | |

# Referências

- [Referência completa da CLI](CLI_REFERENCE.md)
- [Guia de IA](AI_GUIDE.md)
- [Troubleshooting](TROUBLESHOOTING.md)
