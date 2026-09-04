# Instalação

## Requisitos

- Windows/PowerShell como alvo operacional principal;
- CPython `>=3.13,<3.14`;
- pip;
- filesystem local;
- Playwright `>=1.57,<2`;
- Chromium;
- acesso HTTP/HTTPS às URLs auditadas;
- egress adicional somente para integrações externas efetivamente habilitadas.

## Instalar

```powershell
cd C:\IA-PROJETOS\github\SearchGEO-Readiness-Auditor
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m playwright install chromium
```

Validar:

```powershell
searchgeo --version
searchgeo audit --help
searchgeo-console
```

## Execução mínima

```powershell
searchgeo audit https://example.com `
  --project "Smoke" `
  --max-pages 1 `
  --device-context mobile `
  --ai-provider none `
  --no-ai-content-remediation `
  --no-web-performance
```

A execução deve gerar `audit.db`, `logs/audit.log` e o mini-site em `report/`.

## Console interativo

```powershell
searchgeo-console
```

Na primeira abertura, o console cria `searchgeo-console.ini` com defaults não sensíveis. O arquivo é ignorado pelo Git e não armazena API keys/tokens.

## Integrações opcionais

Para IA, configure somente as credenciais dos providers que pretende usar. Não é obrigatório configurar todos.

Para PageSpeed/CrUX, use as variáveis descritas em [GOOGLE_API_KEYS.md](GOOGLE_API_KEYS.md).

## Atualização da instalação editável

Após atualizar o repositório:

```powershell
git fetch origin --prune
git switch main
git pull --ff-only origin main
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m playwright install chromium
```

## Diagnóstico

Se `searchgeo` não for reconhecido, confirme que a `.venv` está ativada e repita `python -m pip install -e .`.

Se Chromium estiver ausente:

```powershell
python -m playwright install chromium
```

Consulte [TROUBLESHOOTING.md](TROUBLESHOOTING.md) para falhas de provider, PageSpeed/Lighthouse, CrUX e artifacts.
