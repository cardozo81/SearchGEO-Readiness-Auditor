# SMOKE_TEST.md

Smoke mínimo após instalação e gate obrigatório antes de merge/release dos providers de extensão.

## 1. Ambiente

```powershell
.\.venv\Scripts\Activate.ps1
python --version
searchgeo --version
searchgeo audit --help
```

Help deve conter `--device-context`, `--ai-provider`, `--ai-content-remediation` e as escolhas `xai`, `grok`, `qwen`, `gemini`, `anthropic`, `claude`.

## 2. Mobile sem IA — baseline

```powershell
searchgeo audit https://example.com --project "Smoke Mobile" --max-pages 1
```

Esperado:

```text
Contexto de dispositivo: MOBILE
Sugestões de conteúdo por IA: DESABILITADAS
```

Workspace:

```text
report/index.html                 existe
report/mobile.html                existe
report/desktop.html               não existe
report/remediation.html           existe
report/content-suggestions.html   existe
report/ai-usage.html              existe
report/references.html            existe
report/css/site.css               existe
```

Em `content-suggestions.html`, M20 textual deve estar DISABLED e a revisão JSON-LD deve existir.

## 3. Regressão dos providers M18 existentes — obrigatória

Com credenciais reais e válidas, executar individualmente:

```powershell
searchgeo audit https://URL-DE-TESTE --max-pages 1 --device-context mobile --ai-provider openai
searchgeo audit https://URL-DE-TESTE --max-pages 1 --device-context mobile --ai-provider deepseek
searchgeo audit https://URL-DE-TESTE --max-pages 1 --device-context mobile --ai-provider mimo
```

Validar em cada execução:

- provider/model corretos em `report/ai-usage.html`;
- exatamente um assessment BR-GEO-028..049 por regra quando a chamada é válida;
- nenhum provider adicional chamado depois do primeiro sucesso;
- nenhuma key/Authorization persistida;
- erro de API não vira Finding do website.

## 4. AUTO — isolamento obrigatório

Configure, se disponíveis, também as quatro keys dos providers novos e execute:

```powershell
searchgeo audit https://URL-DE-TESTE --max-pages 1 --ai-provider auto
```

O `configured_chain`/telemetria deve conter **somente**:

```text
OPENAI
DEEPSEEK
MIMO
```

É falha bloqueante se `XAI`, `QWEN`, `GEMINI` ou `ANTHROPIC` aparecerem como candidatos AUTO.

## 5. xAI / Grok — smoke humano

```powershell
$env:XAI_API_KEY = "<api-key>"
searchgeo audit https://URL-DE-TESTE --max-pages 1 --device-context mobile --ai-provider xai
```

Validar `XAI`, `grok-4.6`, structured output completo, usage quando retornado e ausência de segredo persistido.

## 6. Alibaba Qwen — smoke humano

```powershell
$env:DASHSCOPE_API_KEY = "<api-key>"
searchgeo audit https://URL-DE-TESTE --max-pages 1 --device-context mobile --ai-provider qwen
```

Se a conta não estiver no deployment US default, configurar `SEARCHGEO_QWEN_ENDPOINT` para o endpoint OpenAI-compatible da mesma região/workspace da key.

Validar `QWEN`, modelo esperado, structured output completo, usage e ausência de segredo persistido.

## 7. Google Gemini — smoke humano

```powershell
$env:GEMINI_API_KEY = "<api-key>"
searchgeo audit https://URL-DE-TESTE --max-pages 1 --device-context mobile --ai-provider gemini
```

Validar `GEMINI`, `gemini-3.8-flash`, structured output completo, usage e ausência de segredo persistido.

## 8. Anthropic Claude — smoke humano

```powershell
$env:ANTHROPIC_API_KEY = "<api-key>"
searchgeo audit https://URL-DE-TESTE --max-pages 1 --device-context mobile --ai-provider anthropic
```

Validar `ANTHROPIC`, `claude-sonnet-5`, structured output completo, usage e ausência de segredo persistido. Resposta `stop_reason=refusal` deve ser tratada como indisponibilidade operacional, não avaliação do website.

## 9. M20 com provider de extensão

Para cada provider que passou no M7, repetir uma execução elegível com:

```powershell
--ai-content-remediation
```

Validar em `content-suggestions.html`: finding, objetivo, localização, texto proposto, evidence IDs, provider/model e revisão humana. Em `ai-usage.html`, validar telemetria M20.

Provider que entrou em `QUARANTINED_FOR_AUDIT` no M7 **não pode ser reativado** apenas para M20.

## 10. Falha controlada / key inválida

Testar ao menos um provider novo com key inválida ou endpoint controladamente inválido.

Esperado:

- audit principal não se converte em Finding do website por causa da falha;
- diagnóstico é sanitizado;
- key e mensagem bruta sensível não são persistidas;
- a mesma auditoria não executa retry silencioso após quarantine.

## 11. Desktop e Both

```powershell
searchgeo audit https://example.com --max-pages 1 --device-context desktop
searchgeo audit https://example.com --max-pages 1 --device-context both
```

Validar páginas condicionais e BR-GEO-052 somente em `both`.

## 12. JSON-LD ausente/existente

Em página sem JSON-LD, confirmar proposta `WebPage` somente com valores observados/persistidos. Não aceitar autor/preço/rating/data/claim inventado.

Em página com JSON-LD, confirmar preservação do graph e revisão não destrutiva de parse, duplicações, `@context`, `@type` e propriedades genéricas quando sustentadas.

## 13. Segurança

Nenhuma API key/Authorization nos HTMLs/DB/artifacts/logs. Um teste “sem token” nunca deve executar chamada real mesmo que o terminal tenha outras keys exportadas.

Variáveis relevantes:

```text
OPENAI_API_KEY
DEEPSEEK_API_KEY
MIMO_API_KEY
XAI_API_KEY
DASHSCOPE_API_KEY
GEMINI_API_KEY
ANTHROPIC_API_KEY
```

## 14. CSS/Confidence/References

Validar CSS externo, ausência de `<style>` final, explicação de Coverage/Confidence e fontes oficiais em `references.html`.

## 15. Suíte automatizada

```powershell
python -m compileall -q src tests
python -m unittest discover -s tests -v
```

Devem passar também:

```text
tests/test_m18_multi_ai_provider.py
tests/test_m18_operational_contract.py
tests/test_openai_provider_hardening.py
tests/test_provider_extensions.py
tests/test_provider_extensions_m20.py
tests/test_cli_provider_extensions.py
```

Nenhum merge com falha conhecida.

## Gate de merge

Para a extensão de providers, CI verde é necessário, mas **não suficiente**. Merge só é permitido após:

1. regressão automatizada completa verde;
2. comparação com `main` comprovando que `src/searchgeo/m18_ai.py`, `src/searchgeo/cli.py` e `src/searchgeo/m20_ai.py` não foram alterados pela feature;
3. documentação atualizada e coerente;
4. smoke humano dos quatro providers novos com credenciais reais;
5. smoke/regressão explícita de OpenAI, DeepSeek, MiMo e AUTO;
6. ausência de segredo nos outputs;
7. nenhum blocker funcional/contratual pendente.

Até esses gates serem satisfeitos, os providers novos permanecem `PROVISIONAL`, explicit-only e fora de AUTO.
