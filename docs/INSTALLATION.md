# INSTALLATION.md

## Requisitos

- Windows com PowerShell para o target operacional principal;
- CPython 3.13.x (`>=3.13,<3.14`);
- `pip`;
- filesystem local gravável;
- Playwright `>=1.57,<2`;
- Chromium;
- acesso HTTP/HTTPS ao target;
- egress HTTPS adicional somente se IA externa for usada.

## Criar ambiente

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

A versão Python deve ser 3.13.x.

## Primeiro smoke sem IA

```powershell
searchgeo audit https://example.com `
  --project "Smoke" `
  --max-pages 1
```

A CLI usa Mobile por padrão.

Saída esperada inclui:

```text
Contexto de dispositivo: MOBILE
Relatório: audits\AUD-...\report\index.html
Relatório por problemas: audits\AUD-...\report\remediation.html
```

## Abrir o resultado

```text
audits/<AUD-ID>/report/index.html
```

Estrutura mínima:

```text
AUD-ID/
├─ audit.db
├─ artifacts/
└─ report/
   ├─ index.html
   ├─ mobile.html
   ├─ remediation.html
   ├─ ai-usage.html
   ├─ references.html
   └─ css/site.css
```

`desktop.html` só existe quando Desktop também foi selecionado.

## Testar Desktop + Mobile

```powershell
searchgeo audit https://example.com `
  --project "Smoke Both" `
  --max-pages 1 `
  --device-context both
```

O report deve conter `mobile.html` e `desktop.html`.

## IA — opcional

Nenhum SDK adicional de provider é necessário.

OpenAI:

```powershell
$env:OPENAI_API_KEY = "<chave>"
searchgeo audit https://example.com --max-pages 1 --ai-provider openai
```

DeepSeek:

```powershell
$env:DEEPSEEK_API_KEY = "<chave>"
searchgeo audit https://example.com --max-pages 1 --ai-provider deepseek
```

MiMo:

```powershell
$env:MIMO_API_KEY = "<chave>"
searchgeo audit https://example.com --max-pages 1 --ai-provider mimo
```

Telemetria:

```text
report/ai-usage.html
```

## Timeout

```powershell
$env:SEARCHGEO_AI_TIMEOUT_SECONDS = "240"
```

Default: 180 segundos.

## Dependências quando ausentes

### Python 3.13

Instale CPython 3.13 por canal corporativo/instalador aprovado. Confirme:

```powershell
py -3.13 --version
```

### Playwright package

```powershell
python -m pip install "playwright>=1.57,<2"
```

O `pip install -e .` já instala a dependência declarada do projeto.

### Chromium do Playwright

```powershell
python -m playwright install chromium
```

Em ambientes Linux de CI pode ser necessário:

```bash
python -m playwright install --with-deps chromium
```

## Validar a suíte

```powershell
python -m compileall -q src tests
python -m unittest discover -s tests -v
```

## Não requeridos

A aplicação não exige:

- Docker;
- database server;
- serviço web;
- daemon/background worker;
- SDK OpenAI/DeepSeek/MiMo;
- `audit.log` persistido automaticamente.

Os registros persistentes de uma auditoria são `audit.db`, `artifacts/` e `report/`.
