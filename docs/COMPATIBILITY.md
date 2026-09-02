# Compatibilidade e Dependências

Este é o contrato operacional da **Stable Local Baseline**. A distinção entre `suportado`, `validado` e `não homologado` é intencional.

## Matriz de compatibilidade

| Item | Estado | Contrato/observação |
|---|---|---|
| Windows + PowerShell | **Target operacional de handoff** | documentação e smoke test humano foram preparados para este ambiente; homologação humana ainda deve ser executada |
| Ubuntu `ubuntu-latest` | **Validado por teste automatizado** | run M12 `33663565821`: instalação, Chromium, compileall e 47/47 testes passaram; isso não o torna target formal de distribuição |
| macOS | **Não homologado** | nenhuma garantia operacional nesta baseline |
| CPython 3.13.x | **Obrigatório/suportado pelo package** | `requires-python = ">=3.13,<3.14"`; gate M12 usou 3.13.15 |
| Python 3.12 ou anterior | **Incompatível pelo contrato do package** | instalação deve ser rejeitada |
| Python 3.14+ | **Incompatível pelo contrato do package** | instalação deve ser rejeitada até alteração explícita do projeto |
| Playwright `>=1.57,<2` | **Obrigatório** | única dependência Python externa declarada em runtime |
| Chromium | **Obrigatório para rendering real** | instalar pelo Playwright ou informar executável compatível por variável de ambiente |
| SQLite | **Obrigatório e embarcado** | usa `sqlite3` da biblioteca padrão; não requer database server |
| Filesystem local gravável | **Obrigatório** | `audit.db`, artifacts e `report.html` são locais |
| HTTP/HTTPS para o target | **Obrigatório para auditoria real** | Discovery, aquisição e rendering dependem de conectividade ao site auditado |
| OpenAI | **Opcional** | apenas para análise semântica quando `--ai-provider openai` é selecionado |
| Docker | **Não requerido / não fornecido** | não existe imagem oficial nesta baseline |
| Web server/backend | **Não requerido / não fornecido** | produto opera por CLI e gera HTML estático |
| Git/GitHub | **Não requerido em runtime** | usados para engenharia/versionamento |

## Dependências obrigatórias

### 1. Python

Instale **CPython 3.13**.

```powershell
py -3.13 --version
```

Não use Python 3.12 ou 3.14+ para considerar o ambiente homologado nesta baseline.

### 2. Package Python

```powershell
python -m pip install -e .
```

A instalação traz:

```text
playwright>=1.57,<2
```

Não existe dependência Python externa separada para HTTP, SQLite, TOML, JSON ou OpenAI; esses componentes usam biblioteca padrão.

### 3. Chromium

Instalação recomendada:

```powershell
python -m playwright install chromium
```

Sem Chromium funcional:

- aquisição HTTP RAW ainda pode ocorrer;
- rendering real Desktop/Mobile não fica disponível;
- snapshots podem registrar `BROWSER_UNAVAILABLE`;
- Coverage/Confidence/Consolidation podem cair;
- essa perda de capacidade **não deve ser interpretada como FAIL do website**.

É possível indicar um executável já provisionado:

```powershell
$env:PLAYWRIGHT_CHROMIUM_EXECUTABLE = "C:\caminho\para\chrome.exe"
```

O projeto não fixa uma versão de Chromium separada do Playwright; a compatibilidade operacional do browser alternativo deve ser validada no smoke test.

### 4. Filesystem

O usuário/processo precisa poder criar e gravar:

```text
<audits-root>/<AUD-ID>/audit.db
<audits-root>/<AUD-ID>/artifacts/
<audits-root>/<AUD-ID>/report.html
```

Não há fallback para database remoto.

### 5. Rede

Para auditoria real, o host precisa alcançar:

- target HTTP/HTTPS;
- recursos do mesmo site necessários à navegação/rendering;
- OpenAI somente quando IA for habilitada.

Para instalação inicial, pode ser necessário acesso ao índice Python e ao download do Chromium do Playwright, salvo ambiente previamente provisionado.

## Dependências opcionais

### OpenAI

Não é necessária para executar a Stable Local Baseline.

Quando habilitada, não é usado o SDK Python `openai`; o adapter chama a Responses API por HTTP.

Configuração mínima:

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

O projeto **não fixa um nome de modelo**. O operador deve configurar um modelo aceito pelo endpoint/contrato do provider usado no momento da execução. Compatibilidade de modelos externos pode mudar independentemente deste repositório e deve ser validada antes da homologação.

Sem IA:

```powershell
searchgeo audit https://example.com --ai-provider none
```

Esse é o default e é um modo suportado.

## Configuração de IA — checklist explícito

Para usar OpenAI, todos os passos abaixo precisam ser verdadeiros:

1. Python/Playwright/Chromium estão funcionais.
2. A máquina possui egress HTTPS para o endpoint do provider.
3. `OPENAI_API_KEY` está definida no ambiente do processo.
4. Um model foi definido por `--ai-model` **ou** `SEARCHGEO_OPENAI_MODEL`.
5. O comando usa `--ai-provider openai`.
6. A política de dados permite transmitir ao provider o conteúdo/evidence descrito em [AI_GUIDE.md](AI_GUIDE.md).
7. A chave **não** foi colocada em repositório, TOML, comando persistido em script versionado ou artifact.

Validação sem revelar segredo:

```powershell
Test-Path Env:OPENAI_API_KEY
$env:SEARCHGEO_OPENAI_MODEL
```

Não execute `Write-Output $env:OPENAI_API_KEY` em logs de homologação.

## Modos de IA e compatibilidade operacional

| Situação | Modo esperado | Efeito |
|---|---|---|
| `--ai-provider none` | `NO_AI` | pipeline segue; semantic-only pode ficar UNKNOWN |
| OpenAI selecionado, sem key | `NO_AI`/provider NOT_CONFIGURED | não é FAIL do site |
| OpenAI configurado e válido | `FULL` quando o universo aplicável é atendido | semântica pode contribuir para regras |
| OpenAI selecionado, mas com falhas parciais | `DEGRADED` | saídas inválidas/indisponíveis não viram FAIL artificial |

## O que significa "compatível"

Para esta baseline, compatibilidade exige simultaneamente:

- instalação aceita pelo `pyproject.toml`;
- dependências obrigatórias presentes;
- Chromium capaz de iniciar para rendering;
- filesystem local gravável;
- conectividade necessária ao target;
- suíte automatizada sem regressão;
- smoke test humano aprovado no ambiente de destino.

Até o smoke test humano, o estado correto é **baseline automatizadamente validada, pendente de homologação operacional humana**.
