# USER_GUIDE.md

Guia operacional do SearchGEO Readiness Auditor para execução local e leitura dos resultados.

## Fluxo recomendado

1. instalar Python 3.13, package, Playwright e Chromium;
2. escolher URLs e o limite de páginas;
3. escolher `mobile`, `desktop` ou `both`;
4. decidir se análise semântica por IA será usada;
5. se usar IA, confirmar produto/plano, credencial, endpoint, saldo/quota e acesso ao modelo;
6. decidir se M20 textual será habilitado — default OFF;
7. decidir se M21 Web Performance externo será habilitado — default OFF;
8. decidir se M23 Synthetic Navigation Apdex será habilitado — default OFF e exige `T` explícito;
9. executar;
10. abrir `report/index.html` e navegar pelos domínios do report.

## Default

```powershell
searchgeo audit https://example.com --project "Exemplo"
```

Defaults principais:

```text
Device                 = mobile
IA                     = none
M20 textual            = OFF
M21 Web Performance    = OFF
M23 Synthetic Apdex    = OFF
Idioma                 = pt-BR
Mercado                = BR
max-pages              = 100
```

Sem opt-in, M23 não executa navegações sintéticas adicionais.

## Dispositivo

```powershell
searchgeo audit https://example.com --device-context mobile
searchgeo audit https://example.com --device-context desktop
searchgeo audit https://example.com --device-context both
```

`both` é necessário para comparação Desktop × Mobile completa. M20, M21 e M23 só operam sobre contextos realmente materializados.

## Múltiplas URLs

```powershell
searchgeo audit https://example.com/ https://example.com/produto --max-pages 2
```

Ou:

```powershell
searchgeo audit --urls-file .\urls.txt --max-pages 2
```

Todas as URLs devem pertencer à mesma origem normalizada.

## IA

Sem IA:

```powershell
searchgeo audit https://example.com --ai-provider none
```

Providers concretos atuais:

```text
OpenAI
DeepSeek
Xiaomi MiMo
xAI / Grok
Alibaba Qwen
Google Gemini
Anthropic Claude
```

A cadeia `auto` permanece:

```text
OpenAI -> DeepSeek -> MiMo
```

xAI, Qwen, Gemini e Anthropic permanecem `PROVISIONAL`, `explicit-only` e fora de `AUTO` até qualificação real. OpenAI usa API Platform; assinatura ChatGPT não é saldo da API. MiMo atual usa PAYG `sk-...`; Token Plan `tp-...` não é compatível com o adapter PAYG atual.

Consulte [AI_GUIDE.md](AI_GUIDE.md) e [AI_PROVIDER_EXTENSIONS.md](AI_PROVIDER_EXTENSIONS.md).

## M20 textual

```powershell
$env:OPENAI_API_KEY = "<chave-da-API-Platform>"
searchgeo audit https://example.com `
  --ai-provider openai `
  --ai-content-remediation
```

M20 só tenta sugerir texto para findings elegíveis/evidence-backed. `Confidence LOW` sozinho não aciona M20. Sugestões exigem revisão humana e nunca são aplicadas automaticamente.

## JSON-LD

`report/content-suggestions.html` é produzido mesmo com M20 textual OFF. Se JSON-LD estiver ausente, pode existir proposta conservadora `WebPage` baseada em URL/idioma/title/description observados. Se já existir, o relatório aponta melhorias sem substituir destrutivamente o graph.

## M21 — Web Performance externo

```powershell
searchgeo audit https://example.com `
  --ai-provider none `
  --web-performance
```

M21 é default OFF. Pode coletar Lighthouse/PageSpeed e Core Web Vitals/CrUX quando disponíveis. É evidência externa separada de `SCORE-GEO-002` e não gera chamadas de LLM.

Para limitar volume:

```powershell
searchgeo audit https://example.com `
  --web-performance `
  --web-performance-max-pages 5
```

## M23 — Synthetic Navigation Apdex

M23 mede repetidamente a Task de navegação `NAVIGATION_LOAD` com Chromium e perfil sintético determinístico. É independente de IA, M21 e `SCORE-GEO-002`.

Execução controlada:

```powershell
searchgeo audit https://example.com `
  --ai-provider none `
  --no-web-performance `
  --synthetic-apdex `
  --apdex-threshold-seconds 1.5 `
  --apdex-samples-per-context 5 `
  --apdex-max-attempts-per-context 7 `
  --apdex-max-pages 1 `
  --apdex-delay-seconds 1 `
  --apdex-concurrency 1
```

Regras essenciais:

- `T` é obrigatório quando M23 está ON;
- default de amostras válidas por URL/device: `100`;
- grupos com 1–99 amostras válidas recebem `*` e são diagnósticos de grupo pequeno;
- timeout por amostra deve ser estritamente maior que `4T`;
- concorrência default `1`, máximo `2`;
- cada amostra usa BrowserContext novo e cache desabilitado;
- M23 adiciona `0` tokens e `0` chamadas LLM;
- M23 não exige chamada PageSpeed/CrUX adicional;
- existe carga HTTP real contra o site, porque cada navegação carrega HTML e subrecursos;
- runs de 100 amostras em produção devem respeitar autorização, capacidade e janela operacional do alvo.

Fórmula:

```text
Apdex = (Satisfied + 0.5 × Tolerating) / Total de amostras válidas

Satisfied  <= T
Tolerating > T e <= 4T
Frustrated > 4T
```

Detalhes: [SYNTHETIC_APDEX.md](SYNTHETIC_APDEX.md).

## Console interativo

```powershell
searchgeo-console
```

O console oferece configuração em tela única, preflight, indicação de exposição financeira e atalhos para abrir a pasta/report da auditoria.

M23 aparece como:

```text
11. Synthetic Apdex M23
```

O console separa **exposição financeira** de IA/M21 da **carga sintética** M23. CPU/tempo local e tráfego contra o alvo não são apresentados como invoice de API.

## Saída

O mini-site pode conter:

```text
report/index.html
report/mobile.html              # condicional
report/desktop.html             # condicional
report/remediation.html
report/content-suggestions.html
report/accessibility.html       # quando materializada
report/web-performance.html
report/apdex.html               # quando M23 está habilitado/materializado
report/ai-usage.html
report/references.html
```

### Visão geral

Leia Score, Coverage, Confidence e Consolidation separadamente. Confidence LOW é força reduzida da conclusão, não nota textual.

### Remediações

`remediation.html`: causa, reason code, alvo técnico, observado/esperado, aceite e revalidação.

### Conteúdo e JSON-LD

`content-suggestions.html`: sugestões M20 advisory, provider/model/evidence e revisão/proposta JSON-LD.

### Acessibilidade

`accessibility.html`: projeção Lighthouse Accessibility quando a evidência M21 existe. Não é certificação WCAG.

### Web Performance

`web-performance.html`: Lighthouse Performance, Core Web Vitals/CrUX e diagnósticos técnicos M22. Não calcula Apdex em nome do M21/M22.

### Apdex

`apdex.html`: M23 Synthetic Navigation Apdex, S/T/F, distribuição, percentis, estabilidade, perfil sintético, ambiente executor e rastreabilidade Lighthouse quando disponível. A existência desta página não altera Score GEO.

### IA

`ai-usage.html`: tentativas M18/M20, tokens, duração, custo estimado e erros sanitizados. Erro de provider não é finding do site.

### Referências

`references.html`: fontes oficiais, metodologia, fórmulas e distinção entre standards e heurísticas.

## Segurança

Nunca salve chaves em Git, HTML ou scripts compartilhados. Presença de variável não prova compatibilidade do plano e nenhuma credencial deve ser reutilizada implicitamente por outro provider.

M23 não usa API key própria, mas gera tráfego real contra o alvo. Não faça execução de carga relevante sem autorização.

## Próximas leituras

- [CLI_REFERENCE.md](CLI_REFERENCE.md)
- [CONFIGURATION.md](CONFIGURATION.md)
- [REPORT_GUIDE.md](REPORT_GUIDE.md)
- [SYNTHETIC_APDEX.md](SYNTHETIC_APDEX.md)
- [INTERACTIVE_CONSOLE.md](INTERACTIVE_CONSOLE.md)
- [AI_GUIDE.md](AI_GUIDE.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
