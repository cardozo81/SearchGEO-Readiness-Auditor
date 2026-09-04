# INSTALLATION.md

## Requisitos

Windows/PowerShell, CPython 3.13.x, pip, filesystem local, Playwright `>=1.57,<2`, Chromium e HTTP/HTTPS. Egress adicional só é necessário para serviços externos efetivamente habilitados.

## Instalar

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
python -m playwright install chromium
```

Os adapters de IA usam HTTP da biblioteca padrão; não exigem SDK Python específico de OpenAI, Anthropic, Google, xAI ou Alibaba.

## Validar

```powershell
python --version
searchgeo --version
searchgeo audit --help
```

O help deve listar os providers existentes e os novos providers explicit-only: `xai`, `grok`, `qwen`, `gemini`, `anthropic`, `claude`.

## Primeiro smoke — Mobile, sem IA

```powershell
searchgeo audit https://example.com --project "Smoke" --max-pages 1
```

Esperado: `Contexto de dispositivo: MOBILE`, M20 textual `DESABILITADAS`, `report/index.html`, `report/mobile.html`, `report/remediation.html`, `report/content-suggestions.html`, `report/ai-usage.html`, `report/references.html` e `report/css/site.css`.

`content-suggestions.html` deve existir mesmo sem IA porque a revisão JSON-LD é determinística.

## IA opcional — baseline M18

Antes de configurar credencial, valide produto/plano em [AI_GUIDE.md](AI_GUIDE.md).

```powershell
$env:OPENAI_API_KEY = "<chave-da-API-Platform>"
searchgeo audit https://example.com --max-pages 1 --ai-provider openai
```

```powershell
$env:DEEPSEEK_API_KEY = "<chave-da-DeepSeek-API>"
searchgeo audit https://example.com --max-pages 1 --ai-provider deepseek
```

```powershell
$env:MIMO_API_KEY = "<chave-sk-PAYG>"
searchgeo audit https://example.com --max-pages 1 --ai-provider mimo
```

Não use MiMo Token Plan `tp-...`.

## IA opcional — providers de extensão

Esses providers são `PROVISIONAL` e explicit-only. Eles não entram em `--ai-provider auto`.

### xAI / Grok

```powershell
$env:XAI_API_KEY = "<api-key>"
searchgeo audit https://example.com --max-pages 1 --ai-provider xai
```

### Alibaba Qwen

```powershell
$env:DASHSCOPE_API_KEY = "<api-key>"
searchgeo audit https://example.com --max-pages 1 --ai-provider qwen
```

Se a key não for do deployment US default, configure `SEARCHGEO_QWEN_ENDPOINT` de acordo com a região/workspace da conta.

### Google Gemini

```powershell
$env:GEMINI_API_KEY = "<api-key>"
searchgeo audit https://example.com --max-pages 1 --ai-provider gemini
```

### Anthropic Claude

```powershell
$env:ANTHROPIC_API_KEY = "<api-key>"
searchgeo audit https://example.com --max-pages 1 --ai-provider anthropic
```

Detalhes de modelos/endpoints: [AI_PROVIDER_EXTENSIONS.md](AI_PROVIDER_EXTENSIONS.md).

## AUTO — regressão obrigatória

```powershell
searchgeo audit https://example.com --max-pages 1 --ai-provider auto
```

Mesmo com as keys dos providers de extensão no ambiente, `AUTO` deve continuar contendo somente OpenAI -> DeepSeek -> MiMo.

## M20 textual

Baseline:

```powershell
$env:OPENAI_API_KEY = "<chave-da-API-Platform>"
searchgeo audit https://example.com `
  --max-pages 1 `
  --ai-provider openai `
  --ai-content-remediation
```

Provider de extensão:

```powershell
$env:XAI_API_KEY = "<api-key>"
searchgeo audit https://example.com `
  --max-pages 1 `
  --ai-provider xai `
  --ai-content-remediation
```

A saída é advisory e exige revisão humana. Provider quarantined no M7 não deve ser reativado para M20.

## Timeout

```powershell
$env:SEARCHGEO_AI_TIMEOUT_SECONDS = "240"
```

Default 180 s.

## Dependências ausentes

Playwright package:

```powershell
python -m pip install "playwright>=1.57,<2"
```

Chromium:

```powershell
python -m playwright install chromium
```

Linux CI:

```bash
python -m playwright install --with-deps chromium
```

## Suíte

```powershell
python -m compileall -q src tests
python -m unittest discover -s tests -v
```

A suíte deve incluir `test_provider_extensions.py`, `test_provider_extensions_m20.py` e `test_cli_provider_extensions.py`, além da regressão M18/M20 existente.

O projeto não requer Docker, database server, web server, daemon nem SDK específico de provider.
