# Instalação

Este guia descreve a instalação da **Stable Local Baseline** realmente implementada. Não descreve empacotamento futuro.

## Ambiente de desenvolvimento/handoff atual

O fluxo operacional de referência é Windows + PowerShell. A suíte M12 também foi validada em GitHub Actions com CPython 3.13.15 e Chromium, mas isso não transforma outros sistemas em targets formais de distribuição.

Consulte também [COMPATIBILITY.md](COMPATIBILITY.md) para a matriz completa de compatibilidade.

## Requisitos

| Componente | Obrigatório | Contrato atual |
|---|---:|---|
| CPython | Sim | `>=3.13,<3.14` |
| pip | Sim | instalação do package; pode ser restaurado via `ensurepip` |
| Playwright | Sim | `>=1.57,<2`, dependência do package |
| Chromium | Sim para rendering real | instalado/gerenciado pelo Playwright ou path explícito |
| SQLite | Sim | módulo embarcado do Python; não exige servidor |
| Filesystem local | Sim | workspace, database, artifacts e report |
| OpenAI | Não | serviço externo opcional para análise semântica |
| Git/GitHub | Não em runtime | somente desenvolvimento/versionamento |
| Docker | Não | não existe requisito Docker |
| Database server | Não | SQLite é local/embarcado |
| Web server | Não | CLI + HTML estático |

# Instalar dependências ausentes no Windows

Esta seção deve ser usada quando uma máquina nova **não possuir as dependências necessárias**.

## 1. Verificar o que já existe

No PowerShell:

```powershell
winget --version
py --version
python --version
python -m pip --version
```

Se `py`/`python` não existirem, instale Python 3.13 conforme a próxima seção.

## 2. Instalar Python 3.13 quando não existir

Em Windows suportado, a forma recomendada é instalar o **Python Install Manager** via WinGet e depois instalar runtime 3.13.

```powershell
winget install 9NQ7512CXL7T -e --accept-package-agreements --accept-source-agreements
py install 3.13
```

Valide:

```powershell
py -3.13 --version
```

O projeto exige Python `>=3.13,<3.14`; não use 3.14 para esta baseline.

### Se `winget` não estiver disponível

Verifique se o Windows App Installer está presente:

```powershell
Get-AppxPackage Microsoft.DesktopAppInstaller
```

Se estiver ausente/corrompido, abra a página do Python Install Manager na Microsoft Store por comando:

```powershell
Start-Process "ms-windows-store://pdp/?ProductId=9NQ7512CXL7T"
```

Após instalar o manager, execute:

```powershell
py install 3.13
```

## 3. Restaurar/instalar `pip` quando necessário

Uma instalação normal do Python 3.13 já inclui suporte a `pip`. Se `pip` estiver indisponível:

```powershell
py -3.13 -m ensurepip --upgrade
py -3.13 -m pip install --upgrade pip
```

Valide:

```powershell
py -3.13 -m pip --version
```

## 4. Criar ambiente virtual

Na raiz do repositório:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
```

Se a política do PowerShell impedir ativação, use os executáveis diretamente:

```powershell
.\.venv\Scripts\python.exe --version
```

## 5. Instalar as dependências Python do projeto

Com a venv ativa:

```powershell
python -m pip install --upgrade pip
python -m pip install -e .
```

Isso instala o package e a dependência externa declarada:

```text
playwright>=1.57,<2
```

Valide:

```powershell
python -m pip show searchgeo-readiness-auditor
python -m pip show playwright
searchgeo --version
```

## 6. Instalar Chromium quando não existir

O Chromium usado pelo Playwright **não é instalado apenas com `pip install`**. Execute:

```powershell
python -m playwright install chromium
```

Esse é o comando obrigatório para provisionar o browser gerenciado pelo Playwright.

Se a organização já possui Chromium/Chrome homologado e quiser usá-lo explicitamente:

```powershell
$env:PLAYWRIGHT_CHROMIUM_EXECUTABLE = "C:\caminho\para\chrome.exe"
```

A compatibilidade desse executável alternativo deve ser confirmada no smoke test humano.

## 7. SQLite

Não há pacote de sistema para instalar. A baseline usa `sqlite3` da biblioteca padrão do Python.

Valide:

```powershell
python -c "import sqlite3; print(sqlite3.sqlite_version)"
```

Se esse comando falhar em um Python padrão 3.13, a instalação do Python está incompleta/corrompida; reinstale o runtime.

## 8. OpenAI — somente se IA for desejada

Não existe dependência Python `openai` obrigatória. O adapter usa HTTP da biblioteca padrão.

Para habilitar IA:

```powershell
$env:OPENAI_API_KEY = "<chave>"
$env:SEARCHGEO_OPENAI_MODEL = "<modelo>"
searchgeo audit https://example.com --ai-provider openai
```

Ou:

```powershell
$env:OPENAI_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider openai --ai-model "<modelo>"
```

Consulte [AI_GUIDE.md](AI_GUIDE.md) antes de habilitar IA, especialmente a seção de dados enviados externamente.

# Instalação normal — ambiente já provisionado

Se Python 3.13 já estiver instalado:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
python -m playwright install chromium
searchgeo --version
```

## Teste mínimo da instalação

```powershell
searchgeo --version
searchgeo audit https://example.com --max-pages 1
```

Uma auditoria real requer acesso HTTP/HTTPS ao target e permissão de escrita no diretório de saída.

## Dependências Python

### Runtime obrigatório

A única dependência Python externa declarada é:

```text
playwright>=1.57,<2
```

HTTP, SQLite, parsing TOML, HTML básico, JSON e integração OpenAI usam biblioteca padrão do Python.

### Desenvolvimento/testes

A suíte usa `unittest` e utilitários da biblioteca padrão. Não existe extra `dev` ou dependência de testes separada no `pyproject.toml` da Stable Local Baseline.

Para executar a suíte:

```powershell
python -m compileall -q src tests
python -m unittest discover -s tests -v
```

## O que não existe nesta baseline

- instalador MSI/EXE do SearchGEO Auditor;
- binário portátil sem Python;
- imagem Docker oficial;
- database server;
- serviço web do auditor;
- daemon/background worker;
- CI permanente como requisito de runtime.

Portanto, se o ambiente final exigir distribuição sem Python instalado, isso é trabalho futuro e está fora da Stable Local Baseline.
