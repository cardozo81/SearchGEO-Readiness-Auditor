# Smoke Test Humano — Stable Local Baseline

Este roteiro é para **homologação humana posterior**. A criação deste documento não aprova o smoke test.

## Registro da execução

| Campo | Valor |
|---|---|
| Data/hora | |
| Operador | |
| Máquina/OS | |
| Python | |
| Package/version | |
| Chromium/Playwright | |
| Commit de `main` | |
| Target Caso A | |
| Target Caso B | |
| Target Caso C | |
| Target Caso D | |

Para cada item use uma das opções:

```text
PASS
FAIL
NOT_APPLICABLE
```

Registre sempre **Observação** e **Evidência/path do artifact** quando aplicável.

---

# 1. Preparação

| Verificação | Resultado | Observação | Evidência/path |
|---|---|---|---|
| Windows/ambiente identificado | | | |
| CPython 3.13 ativo | | | |
| venv ativo ou executáveis explícitos | | | |
| package instalado | | | |
| `searchgeo --version` funciona | | | |
| Playwright instalado | | | |
| Chromium instalado e inicia | | | |
| acesso HTTP/HTTPS aos targets | | | |
| diretório de auditorias gravável | | | |
| espaço em disco suficiente | | | |
| configuração de logging conhecida | | | |
| secrets não estão em comandos/logs compartilhados | | | |

Comandos de referência:

```powershell
python --version
python -m pip show searchgeo-readiness-auditor
python -m pip show playwright
searchgeo --version
```

---

# 2. Caso A — site tradicional

Escolha um site tradicional/SSR acessível e autorizado para teste. Use budget pequeno, mas suficiente para observar Discovery.

Exemplo:

```powershell
searchgeo audit https://<target-a> `
  --project "Smoke A — tradicional" `
  --max-pages 5 `
  --audits-root .\smoke-audits
```

## Execução e Discovery/HTTP

| Verificação | Resultado | Observação | Evidência/path |
|---|---|---|---|
| CLI aceita target | | | |
| novo `AUD-ID` é criado | | | |
| `audit.db` existe | | | |
| `artifacts/` existe | | | |
| seed aparece no universo auditado | | | |
| robots é adquirido/registrado ou ausência tratada | | | |
| sitemap é processado quando disponível | | | |
| links internos participam do Discovery | | | |
| `max_pages` é respeitado | | | |
| se budget atingido, `MAX_PAGES_REACHED:` aparece | | | |
| RAW HTTP é preservado quando body existe | | | |
| status/headers/final URL/redirects são rastreáveis | | | |

## Desktop/Mobile

| Verificação | Resultado | Observação | Evidência/path |
|---|---|---|---|
| snapshot Desktop existe | | | |
| snapshot Mobile existe | | | |
| rendered Desktop existe quando render sucede | | | |
| rendered Mobile existe quando render sucede | | | |
| artifacts Desktop/Mobile não se sobrescrevem | | | |
| browser metadata identifica profiles | | | |

## Extraction/Evidence/Rules

| Verificação | Resultado | Observação | Evidência/path |
|---|---|---|---|
| title/metadata extraídos quando presentes | | | |
| canonical/robots extraídos quando presentes | | | |
| headings/links observados | | | |
| `main_content.txt` materializado quando aplicável | | | |
| `structured_data.json` materializado quando aplicável | | | |
| Evidence aponta para source/artifact | | | |
| RuleExecutions estão persistidas | | | |
| Findings possuem Evidence | | | |
| UNKNOWN não é exibido como FAIL | | | |
| ERROR não é exibido como FAIL | | | |
| NOT_APPLICABLE não é exibido como FAIL | | | |

## Scoring/Recommendations/Report

| Verificação | Resultado | Observação | Evidência/path |
|---|---|---|---|
| scores Desktop persistidos | | | |
| scores Mobile persistidos | | | |
| Coverage/Confidence/Consolidation visíveis | | | |
| Overall só existe se consolidável | | | |
| ScoreContributions rastreiam RuleExecutions | | | |
| Remediation Groups persistidos quando há findings | | | |
| Recommendations persistidas quando há findings | | | |
| `report.html` existe | | | |
| report abre sem web server | | | |

---

# 3. Caso B — JavaScript / SPA

Escolha SPA/CSR autorizada com conteúdo dependente de JavaScript e, quando possível, rota interna diretamente acessível.

```powershell
searchgeo audit https://<target-b> `
  --project "Smoke B — SPA" `
  --max-pages 5 `
  --audits-root .\smoke-audits
```

| Verificação | Resultado | Observação | Evidência/path |
|---|---|---|---|
| RAW e RENDERED podem ser comparados | | | |
| shell RAW + conteúdo RENDERED completo não é penalizado só por CSR | | | |
| architecture classification é persistida | | | |
| direct route relevante é avaliada quando aplicável | | | |
| navegação interna crawlable é avaliada | | | |
| soft-404 exige evidência forte | | | |
| título editorial com número `404` não vira soft-404 sem contexto de erro | | | |
| lazy loading é avaliado de forma bounded quando aplicável | | | |
| conteúdo essencial recuperado após JS é preservado | | | |
| diferença de arquitetura por si só não gera finding | | | |

Registrar ao menos um par RAW × RENDERED utilizado na verificação.

---

# 4. Caso C — execução sem IA

Execute explicitamente sem IA:

```powershell
searchgeo audit https://<target-c> `
  --project "Smoke C — NO_AI" `
  --max-pages 3 `
  --ai-provider none `
  --audits-root .\smoke-audits
```

| Verificação | Resultado | Observação | Evidência/path |
|---|---|---|---|
| auditoria não exige API key | | | |
| execução continua até reporting | | | |
| Audit registra `NO_AI` | | | |
| limitações de IA aparecem de forma compreensível | | | |
| regras determinísticas continuam avaliadas | | | |
| semantic-only insuficiente fica UNKNOWN, não FAIL | | | |
| ausência de IA não recebe fator 0 artificial | | | |
| Coverage/Confidence podem refletir menor capacidade | | | |
| report explica NO_AI | | | |

Critério central: **ausência de IA não deve ser interpretada como baixa qualidade do site**.

---

# 5. Caso D — falha localizada controlada

Use cenário seguro/autorizado em que uma página/recurso do universo falhe enquanto outra permanece válida. Pode ser fixture local ou target de homologação controlado.

Objetivo: confirmar que a falha não derruba toda a auditoria nem gera cascading failures.

| Verificação | Resultado | Observação | Evidência/path |
|---|---|---|---|
| falha HTTP/rede fica associada ao recurso correto | | | |
| outra página continua processada | | | |
| se um device falha, o outro permanece independente quando possível | | | |
| falha de extração fica localizada ao snapshot | | | |
| regra técnica causal registra resultado apropriado | | | |
| regras dependentes ficam UNKNOWN/NOT_APPLICABLE quando necessário | | | |
| não há cascata artificial de FAIL sem evidence | | | |
| auditoria pode chegar a `COMPLETE_WITH_LIMITATIONS` quando apropriado | | | |
| artifacts válidos das partes bem-sucedidas permanecem disponíveis | | | |

---

# 6. Verificação visual do `report.html`

Abra cada relatório relevante no browser local.

| Verificação | Resultado | Observação | Evidência/path |
|---|---|---|---|
| HTML abre localmente | | | |
| conteúdo prioritariamente em português | | | |
| tipografia/layout legíveis | | | |
| não depende de CDN/fontes remotas | | | |
| resumo identifica projeto/auditoria | | | |
| disclaimer de readiness está visível | | | |
| Desktop e Mobile aparecem separadamente | | | |
| 10 dimensões são compreensíveis | | | |
| Overall respeita consolidação | | | |
| Coverage exibida | | | |
| Confidence exibida | | | |
| Consolidation exibida | | | |
| findings mostram severity/contexto | | | |
| Evidence/rastreabilidade é compreensível | | | |
| prioridades P0–P4/INFO são legíveis quando existentes | | | |
| recommendations/remediation groups são legíveis | | | |
| limitações estão visíveis | | | |
| FULL/DEGRADED/NO_AI é interpretável | | | |
| glossário está presente | | | |
| nenhum segredo/API key aparece | | | |

---

# 7. Verificação da fonte primária

Para pelo menos um finding e um score:

| Verificação | Resultado | Observação | Evidência/path |
|---|---|---|---|
| Finding reabre em `audit.db` | | | |
| RuleExecution correspondente existe | | | |
| Evidence referenciada existe | | | |
| artifact reference reabre quando aplicável | | | |
| Score reabre em `audit.db` | | | |
| ScoreContribution aponta para RuleExecution | | | |
| report é compatível com o estado persistido | | | |

Não use `report.html` como substituto da fonte primária nessa validação.

---

# 8. Resultado humano

Preencher somente após execução real do roteiro.

```text
Resultado: ______________________________________
```

Valores permitidos:

```text
SMOKE TEST HUMANO — APROVADO
SMOKE TEST HUMANO — REPROVADO
```

## Pendências/defeitos encontrados

| ID | Caso | Descrição | Evidência | Severidade operacional | Ação |
|---|---|---|---|---|---|
| | | | | | |

## Assinatura da homologação

| Campo | Valor |
|---|---|
| Operador | |
| Data | |
| Commit homologado | |
| Resultado | |

> Este documento é o roteiro oficial de smoke test humano da Stable Local Baseline. Ele não autoriza V1 nem escopo posterior.
