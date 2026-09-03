# USER_GUIDE.md

## Fluxo recomendado

1. instalar Python 3.13, package, Playwright e Chromium;
2. escolher URLs;
3. escolher `mobile`, `desktop` ou `both`;
4. decidir se análise semântica por IA será usada;
5. se usar IA, confirmar produto/plano, credencial, endpoint, saldo/quota e acesso ao modelo;
6. decidir se M20 textual será habilitado — default OFF;
7. executar;
8. abrir `report/index.html` e navegar pelos domínios do report.

## Default

```powershell
searchgeo audit https://example.com --project "Exemplo"
```

Defaults: Mobile, IA `none`, M20 textual OFF, `pt-BR`, `BR`, `max-pages=100`.

## Dispositivo

```powershell
searchgeo audit https://example.com --device-context mobile
searchgeo audit https://example.com --device-context desktop
searchgeo audit https://example.com --device-context both
```

`both` é necessário para comparação Desktop × Mobile completa.

## Múltiplas URLs

```powershell
searchgeo audit https://example.com/ https://example.com/produto --max-pages 2
```

ou `--urls-file .\urls.txt`. Todas devem pertencer à mesma origem normalizada.

## IA

Sem IA:

```powershell
searchgeo audit https://example.com --ai-provider none
```

OpenAI usa API Platform; ChatGPT não é saldo de API. DeepSeek usa a DeepSeek API. MiMo atual usa PAYG `sk-...`; não use Token Plan `tp-...`.

## M20 textual

```powershell
$env:OPENAI_API_KEY = "<chave-da-API-Platform>"
searchgeo audit https://example.com `
  --ai-provider openai `
  --ai-content-remediation
```

M20 só tenta sugerir texto para findings elegíveis/evidence-backed. `Confidence LOW` sozinho não aciona M20. Sugestões exigem revisão humana e nunca são aplicadas automaticamente.

## JSON-LD

`report/content-suggestions.html` é produzido mesmo com M20 textual OFF. Se JSON-LD estiver ausente, pode existir proposta conservadora `WebPage` baseada em URL/idioma/title/description observados. Se já existir, o relatório aponta melhorias sem substituir o graph.

## Saída

```text
report/index.html
report/mobile.html ou desktop.html
report/remediation.html
report/content-suggestions.html
report/ai-usage.html
report/references.html
```

### Visão geral

Leia Score, Coverage, Confidence e Consolidation separadamente. Confidence LOW é força reduzida da conclusão, não nota textual.

### Remediações

`remediation.html`: causa, reason code, alvo técnico, observado/esperado, aceite e revalidação.

### Conteúdo e JSON-LD

`content-suggestions.html`: sugestões M20 advisory, provider/model/evidence e revisão/proposta JSON-LD.

### IA

`ai-usage.html`: tentativas M18/M20, tokens, duração, custo estimado e erros sanitizados. Erro de provider não é finding do site.

### Referências

`references.html`: fontes oficiais, metodologia, fórmula e distinção entre standards e heurísticas.

## Segurança

Nunca salve chaves em Git/HTML/scripts compartilhados. Presença de variável não prova compatibilidade do plano e nenhuma credencial deve ser reutilizada implicitamente por outro provider.

## Próximas leituras

[CLI_REFERENCE.md](CLI_REFERENCE.md), [CONFIGURATION.md](CONFIGURATION.md), [REPORT_GUIDE.md](REPORT_GUIDE.md), [AI_GUIDE.md](AI_GUIDE.md), [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
