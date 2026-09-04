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

Providers disponíveis:

| CLI | Provider | Default | Observação |
|---|---|---|---|
| `openai` | OpenAI | `gpt-5.6-terra` | API Platform |
| `deepseek` | DeepSeek | `deepseek-v4-pro` | baseline M18 |
| `mimo` | Xiaomi MiMo | `mimo-v2.5-pro` | somente PAYG `sk-...` |
| `auto` | routing M18 | — | somente OpenAI -> DeepSeek -> MiMo |
| `xai` / `grok` | xAI / Grok | `grok-4.6` | `PROVISIONAL`, explicit-only |
| `qwen` | Alibaba Qwen | `qwen3.8-max` | `PROVISIONAL`, explicit-only |
| `gemini` | Google Gemini | `gemini-3.8-flash` | `PROVISIONAL`, explicit-only |
| `anthropic` / `claude` | Anthropic Claude | `claude-sonnet-5` | `PROVISIONAL`, explicit-only |

Os quatro providers novos não participam de `auto`, mesmo que suas keys estejam configuradas.

### Exemplos

```powershell
$env:XAI_API_KEY = "<api-key>"
searchgeo audit https://example.com --ai-provider xai
```

```powershell
$env:DASHSCOPE_API_KEY = "<api-key>"
searchgeo audit https://example.com --ai-provider qwen
```

```powershell
$env:GEMINI_API_KEY = "<api-key>"
searchgeo audit https://example.com --ai-provider gemini
```

```powershell
$env:ANTHROPIC_API_KEY = "<api-key>"
searchgeo audit https://example.com --ai-provider anthropic
```

Qwen pode exigir `SEARCHGEO_QWEN_ENDPOINT` compatível com a região/workspace da key. Consulte [AI_PROVIDER_EXTENSIONS.md](AI_PROVIDER_EXTENSIONS.md).

## M20 textual

```powershell
$env:OPENAI_API_KEY = "<chave-da-API-Platform>"
searchgeo audit https://example.com `
  --ai-provider openai `
  --ai-content-remediation
```

Os providers de extensão também suportam M20 quando explicitamente selecionados. Exemplo:

```powershell
$env:ANTHROPIC_API_KEY = "<api-key>"
searchgeo audit https://example.com `
  --ai-provider anthropic `
  --ai-content-remediation
```

M20 só tenta sugerir texto para findings elegíveis/evidence-backed. `Confidence LOW` sozinho não aciona M20. Sugestões exigem revisão humana e nunca são aplicadas automaticamente. Provider quarantined no M7 não é reativado para M20.

## JSON-LD

`report/content-suggestions.html` é produzido mesmo com M20 textual OFF. Se JSON-LD estiver ausente, pode existir proposta conservadora `WebPage` baseada em URL/idioma/title/description observados. Se já existir, o relatório aponta melhorias sem substituir o graph.

## Saída

```text
report/index.html
report/mobile.html ou desktop.html
report/remediation.html
report/content-suggestions.html
report/web-performance.html
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

`ai-usage.html`: tentativas M18/M20, tokens, duração, custo estimado quando disponível e erros sanitizados. Erro de provider não é finding do site.

Providers novos podem ter `estimated_cost` indisponível enquanto `PROVISIONAL`; isso evita estimativa incorreta antes da qualificação de preço por região/tier/cache.

### Referências

`references.html`: fontes oficiais, metodologia, fórmula e distinção entre standards e heurísticas.

## Segurança

Nunca salve chaves em Git/HTML/scripts compartilhados. Cada provider usa sua própria credencial. A ausência da key selecionada resulta em `NOT_CONFIGURED`; outra key disponível no ambiente não a substitui.

## Smoke dos providers novos

Antes de qualquer promoção para `AUTO`/`QUALIFIED`, execute o roteiro humano de [AI_PROVIDER_EXTENSIONS.md](AI_PROVIDER_EXTENSIONS.md) e [SMOKE_TEST.md](SMOKE_TEST.md), incluindo regressão explícita de OpenAI, DeepSeek e MiMo.

## Próximas leituras

[CLI_REFERENCE.md](CLI_REFERENCE.md), [CONFIGURATION.md](CONFIGURATION.md), [AI_PROVIDER_EXTENSIONS.md](AI_PROVIDER_EXTENSIONS.md), [REPORT_GUIDE.md](REPORT_GUIDE.md), [AI_GUIDE.md](AI_GUIDE.md), [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
