# USER_GUIDE.md

## Fluxo recomendado

1. instalar Python 3.13, package, Playwright e Chromium;
2. escolher o universo de URLs;
3. escolher o contexto de dispositivo;
4. decidir se IA será usada;
5. executar a auditoria;
6. abrir `report/index.html`;
7. navegar para Mobile/Desktop, remediações, IA ou referências conforme a necessidade.

## Execução padrão

```powershell
searchgeo audit https://example.com --project "Exemplo"
```

Defaults relevantes:

```text
device = mobile
AI = none
language = pt-BR
market = BR
max-pages = 100
audits-root = audits
```

## Dispositivo

### Mobile — padrão

```powershell
searchgeo audit https://example.com --device-context mobile
```

Gera somente contexto Mobile. É a opção recomendada para análise inicial e reduz custo/tempo quando IA está habilitada.

### Desktop

```powershell
searchgeo audit https://example.com --device-context desktop
```

### Ambos

```powershell
searchgeo audit https://example.com --device-context both
```

Use `both` quando a comparação Desktop × Mobile for requisito da auditoria.

Também é possível:

```powershell
$env:SEARCHGEO_DEVICE_CONTEXT = "mobile"
```

A flag `--device-context` tem precedência sobre a variável.

## Múltiplas URLs

```powershell
searchgeo audit `
  https://example.com/ `
  https://example.com/produto `
  https://example.com/faq `
  --project "Exemplo" `
  --max-pages 3
```

Ou:

```powershell
searchgeo audit --urls-file .\urls.txt --project "Exemplo"
```

Todas as URLs de um `URL_SET` devem pertencer à mesma origem normalizada.

## Sem IA

```powershell
searchgeo audit https://example.com --ai-provider none
```

A auditoria continua com regras determinísticas. Regras semânticas sem evidência suficiente ficam `UNKNOWN`; isso não equivale a FAIL do site.

## Com OpenAI

```powershell
$env:OPENAI_API_KEY = "<chave>"
searchgeo audit https://example.com `
  --device-context mobile `
  --ai-provider openai
```

O default OpenAI é `gpt-5.6-terra`.

## Com AUTO multi-provider

```powershell
$env:OPENAI_API_KEY = "<chave>"
$env:DEEPSEEK_API_KEY = "<chave>"
$env:MIMO_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider auto
```

Providers sem token/configuração válida são excluídos. O primeiro resultado válido encerra a cadeia naquele contexto.

## Saída esperada

```text
Auditoria concluída: AUD-...
Status: ...
Páginas auditadas: ...
Contexto de dispositivo: MOBILE
Problemas identificados: ...
Recomendações: ...
Relatório: audits\AUD-...\report\index.html
Relatório por problemas: audits\AUD-...\report\remediation.html
```

## Abrindo o relatório

Abra diretamente:

```text
audits/<AUD-ID>/report/index.html
```

O report site não precisa de servidor.

Menu:

- **Visão geral** — dashboard executivo;
- **Relatório Mobile** — aparece quando Mobile foi auditado;
- **Relatório Desktop** — aparece quando Desktop foi auditado;
- **Remediações** — causas e ações agrupadas;
- **Uso de IA** — telemetria operacional;
- **Referências e metodologia** — fontes e fórmulas.

## Como interpretar a visão geral

Não leia somente o número do Score.

### Score

Qualidade observada nas regras efetivamente avaliadas.

### Coverage

Quanto do universo aplicável realmente foi avaliado.

Coverage baixa significa análise incompleta, não site ruim.

### Confidence

Força da conclusão do auditor.

**Confidence LOW não significa que o texto não é válido para GEO.** Pode ocorrer por baixa Coverage, evidência incompleta ou erros de execução. Uma mudança de conteúdo só deve ser recomendada quando um finding/RuleExecution sustenta essa alteração.

### Consolidation

Indica se a base é suficiente para publicar o resultado como consolidado.

## Mobile × Desktop

Com `both`, leia os relatórios separadamente. Uma diferença entre dispositivos não é automaticamente problema.

A página Mobile nunca mistura finding exclusivamente Desktop, e vice-versa.

## Remediações

Abra:

```text
report/remediation.html
```

A página agrupa causas e, quando disponível, apresenta:

- reason code;
- selector observado;
- alvo técnico;
- mudança recomendada;
- observado versus esperado;
- critérios de aceite;
- passos de revalidação;
- decisão humana necessária.

## IA

Abra:

```text
report/ai-usage.html
```

Essa página é operacional. Timeout, quota, auth ou provider ausente não são problemas GEO do site.

O custo mostrado é estimativa local, não fatura.

## Referências

Abra:

```text
report/references.html
```

Ali estão fontes oficiais e a distinção entre norma/standard e heurística interna.

O SearchGEO não promete uma “nota oficial GEO”. O guia atual do Google para recursos generativos reforça fundamentos de SEO e não exige markup GEO/AEO especial, chunking artificial ou conteúdo reescrito apenas para IA.

## Segurança

Nunca salve API keys em HTML, Git ou scripts compartilhados.

Valide somente presença:

```powershell
Test-Path Env:OPENAI_API_KEY
Test-Path Env:DEEPSEEK_API_KEY
Test-Path Env:MIMO_API_KEY
```

## Próximas leituras

- [CLI_REFERENCE.md](CLI_REFERENCE.md)
- [CONFIGURATION.md](CONFIGURATION.md)
- [REPORT_GUIDE.md](REPORT_GUIDE.md)
- [SCORING_GUIDE.md](SCORING_GUIDE.md)
- [AI_GUIDE.md](AI_GUIDE.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
