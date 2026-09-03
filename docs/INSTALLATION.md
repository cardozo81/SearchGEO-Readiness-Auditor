# INSTALLATION.md

## Requisitos

Windows/PowerShell, CPython 3.13.x, pip, filesystem local, Playwright `>=1.57,<2`, Chromium e HTTP/HTTPS. Egress adicional só é necessário para IA externa.

## Instalar

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
python -m playwright install chromium
```

## Validar

```powershell
python --version
searchgeo --version
searchgeo audit --help
```

## Primeiro smoke — Mobile, sem IA

```powershell
searchgeo audit https://example.com --project "Smoke" --max-pages 1
```

Esperado: `Contexto de dispositivo: MOBILE`, M20 textual `DESABILITADAS`, `report/index.html`, `report/mobile.html`, `report/remediation.html`, `report/content-suggestions.html`, `report/ai-usage.html`, `report/references.html` e `report/css/site.css`.

`content-suggestions.html` deve existir mesmo sem IA porque a revisão JSON-LD é determinística.

## IA opcional

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

## M20 textual

```powershell
$env:OPENAI_API_KEY = "<chave-da-API-Platform>"
searchgeo audit https://example.com `
  --max-pages 1 `
  --ai-provider openai `
  --ai-content-remediation
```

A saída é advisory e exige revisão humana.

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

O projeto não requer Docker, database server, web server, daemon nem SDK específico de provider.
