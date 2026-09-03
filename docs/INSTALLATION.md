# Instalação

Este guia descreve a instalação da baseline local atual do SearchGEO Readiness Auditor, incluindo M18 multi-provider.

## Ambiente de referência

O fluxo operacional documentado usa Windows + PowerShell. Ubuntu é usado em validação automatizada, mas não substitui o target operacional de handoff.

Consulte [COMPATIBILITY.md](COMPATIBILITY.md) para o contrato completo.

## Requisitos

| Componente | Obrigatório | Contrato atual |
|---|---:|---|
| CPython | Sim | `>=3.13,<3.14` |
| pip | Sim | instalação do package |
| Playwright | Sim | `>=1.57,<2` |
| Chromium | Sim para rendering real | gerenciado pelo Playwright ou path explícito |
| SQLite | Sim | embarcado no Python |
| Filesystem local | Sim | workspace, DB, artifacts e HTMLs |
| OpenAI | Não | provider semântico opcional |
| DeepSeek | Não | provider semântico opcional |
| Xiaomi MiMo | Não | provider semântico opcional |
| Docker | Não | não fornecido/requerido |
| Database server | Não | SQLite local |
| Web server | Não | CLI + HTML estático |

# Instalar dependências ausentes no Windows

## 1. Verificar ambiente

```powershell
winget --version
py --version
python --version
python -m pip --version
```

## 2. Instalar Python 3.13

```powershell
winget install 9NQ7512CXL7T -e --accept-package-agreements --accept-source-agreements
py install 3.13
py -3.13 --version
```

Se `winget` não estiver disponível, valide o App Installer:

```powershell
Get-AppxPackage Microsoft.DesktopAppInstaller
```

Ou abra o Python Install Manager na Microsoft Store:

```powershell
Start-Process "ms-windows-store://pdp/?ProductId=9NQ7512CXL7T"
```

Depois:

```powershell
py install 3.13
```

## 3. Restaurar `pip`, se necessário

```powershell
py -3.13 -m ensurepip --upgrade
py -3.13 -m pip install --upgrade pip
```

## 4. Criar ambiente virtual

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
```

Se a política do PowerShell bloquear ativação:

```powershell
.\.venv\Scripts\python.exe --version
```

## 5. Instalar o projeto

```powershell
python -m pip install --upgrade pip
python -m pip install -e .
```

Valide:

```powershell
python -m pip show searchgeo-readiness-auditor
python -m pip show playwright
searchgeo --version
```

## 6. Instalar Chromium

```powershell
python -m playwright install chromium
```

Executável corporativo alternativo:

```powershell
$env:PLAYWRIGHT_CHROMIUM_EXECUTABLE = "C:\caminho\para\chrome.exe"
```

## 7. Validar SQLite

```powershell
python -c "import sqlite3; print(sqlite3.sqlite_version)"
```

# Teste mínimo sem IA

Após instalar:

```powershell
searchgeo --version
searchgeo audit https://example.com --max-pages 1 --ai-provider none
```

Nenhum token de IA é necessário para esse teste.

# Habilitar IA — opcional

Não instale SDK Python específico de OpenAI/DeepSeek/MiMo. Os adapters usam HTTP.

## OpenAI

```powershell
$env:OPENAI_API_KEY = "<chave>"
searchgeo audit https://example.com --max-pages 1 --ai-provider openai
```

Default: `gpt-5.6-terra`.

## DeepSeek

```powershell
$env:DEEPSEEK_API_KEY = "<chave>"
searchgeo audit https://example.com --max-pages 1 --ai-provider deepseek
```

Default: `deepseek-v4-pro`.

## Xiaomi MiMo

```powershell
$env:MIMO_API_KEY = "<chave>"
searchgeo audit https://example.com --max-pages 1 --ai-provider mimo
```

Default: `mimo-v2.5-pro`.

## AUTO com vários providers

```powershell
$env:OPENAI_API_KEY = "<chave-openai>"
$env:DEEPSEEK_API_KEY = "<chave-deepseek>"
$env:MIMO_API_KEY = "<chave-mimo>"
searchgeo audit https://example.com --max-pages 1 --ai-provider auto
```

Providers sem token são omitidos da cadeia AUTO. Um provider explícito sem token fica `NOT_CONFIGURED` e nenhuma chamada externa é feita.

Consulte [AI_GUIDE.md](AI_GUIDE.md) antes de habilitar IA em conteúdo corporativo.

# Instalação normal — ambiente já provisionado

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
python -m playwright install chromium
searchgeo --version
```

# Executar a aplicação

Exemplo padrão:

```powershell
searchgeo audit https://example.com --project "Exemplo"
```

Várias URLs:

```powershell
searchgeo audit https://example.com/ https://example.com/produto --project "Exemplo"
```

Arquivo de URLs:

```powershell
searchgeo audit --urls-file .\urls.txt --project "Exemplo"
```

A referência completa de **todos os parâmetros de execução** está em [CLI_REFERENCE.md](CLI_REFERENCE.md).

# Executar testes do projeto

```powershell
python -m compileall -q src tests
python -m unittest discover -s tests -v
```

# Dependências Python

A dependência externa declarada de runtime é Playwright. HTTP, SQLite, TOML, JSON e adapters de IA usam recursos da biblioteca padrão/implementação do projeto.

# O que não existe nesta baseline

- MSI/EXE standalone;
- binário portátil sem Python;
- imagem Docker oficial;
- database server;
- serviço web;
- daemon/background worker;
- `audit.log` persistido automaticamente.

Os registros persistentes de uma auditoria são o workspace (`audit.db`, artifacts, `report.html`, `remediation.html`).
