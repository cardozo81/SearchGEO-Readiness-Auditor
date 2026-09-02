# Instalação

Este guia descreve a instalação da **Stable Local Baseline** realmente implementada. Não descreve empacotamento futuro.

## Ambiente de desenvolvimento/handoff atual

O fluxo operacional de referência é Windows + PowerShell. A suíte M12 também foi validada em GitHub Actions com CPython 3.13.15 e Chromium, mas isso não transforma outros sistemas em targets formais de distribuição.

## Requisitos

| Componente | Obrigatório | Contrato atual |
|---|---:|---|
| CPython | Sim | `>=3.13,<3.14` |
| pip | Sim | instalação do package |
| Playwright | Sim | `>=1.57,<2`, dependência do package |
| Chromium | Sim para rendering real | instalado/gerenciado pelo Playwright ou path explícito |
| SQLite | Sim | módulo embarcado do Python; não exige servidor |
| Filesystem local | Sim | workspace, database, artifacts e report |
| OpenAI | Não | serviço externo opcional para análise semântica |
| Git/GitHub | Não em runtime | somente desenvolvimento/versionamento |
| Docker | Não | não existe requisito Docker |
| Database server | Não | SQLite é local/embarcado |
| Web server | Não | CLI + HTML estático |

## 1. Confirmar Python

```powershell
py -3.13 --version
```

Use Python 3.13. A declaração do package rejeita Python 3.12 e Python 3.14+.

## 2. Criar virtual environment

Na raiz do repositório:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
```

Se a política do PowerShell impedir ativação, é possível invocar diretamente `.\.venv\Scripts\python.exe` e `.\.venv\Scripts\searchgeo.exe`.

## 3. Instalar o package

Para desenvolvimento/handoff local:

```powershell
python -m pip install --upgrade pip
python -m pip install -e .
```

O `pyproject.toml` registra o comando:

```text
searchgeo = searchgeo.cli:main
```

Verifique:

```powershell
searchgeo --version
```

## 4. Instalar Chromium

```powershell
python -m playwright install chromium
```

O renderer inicia Chromium headless. Por padrão usa o browser gerenciado pelo Playwright.

### Chromium explicitamente instalado

Se houver necessidade operacional de usar outro executável Chromium compatível:

```powershell
$env:PLAYWRIGHT_CHROMIUM_EXECUTABLE = "C:\caminho\para\chrome.exe"
```

Essa variável é lida pelo `BrowserRenderer`. Não confundir com uma opção CLI: não existe flag `--chromium-path` na baseline atual.

## 5. Teste mínimo da instalação

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

### Opcional: OpenAI

Não há package Python `openai` obrigatório. O adapter implementado chama a Responses API por HTTP e requer apenas:

```powershell
$env:OPENAI_API_KEY = "<chave>"
$env:SEARCHGEO_OPENAI_MODEL = "<modelo>"
```

A auditoria funciona sem esses valores usando `NoneProvider`/`NO_AI`.

## O que não existe nesta baseline

- instalador MSI/EXE;
- binário portátil sem Python;
- imagem Docker oficial;
- database server;
- serviço web do auditor;
- daemon/background worker;
- CI permanente como requisito de runtime.

Portanto, se o ambiente final exigir distribuição sem Python instalado, isso é trabalho futuro e está fora da Stable Local Baseline.
