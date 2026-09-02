# SearchGEO Readiness Auditor

Auditor local de **Search/GEO Readiness** para avaliar, com rastreabilidade técnica, quão acessível, extraível, semanticamente compreensível e reutilizável um site é para mecanismos de busca e sistemas generativos.

## Status

**Stable Local Baseline — implementada.** A baseline M1–M12 executa a auditoria ponta a ponta por CLI, persiste dados em SQLite + filesystem, analisa Desktop e Mobile separadamente e produz `report.html` estático.

> Readiness não é promessa de ranking, tráfego, citação, presença ou visibilidade em mecanismos generativos.

## Compatibilidade — leia antes de instalar

| Item | Estado |
|---|---|
| Windows + PowerShell | target operacional de handoff |
| CPython 3.13.x | obrigatório; `>=3.13,<3.14` |
| Python 3.12 ou 3.14+ | incompatível pelo contrato atual do package |
| Playwright `>=1.57,<2` | obrigatório |
| Chromium | obrigatório para rendering real Desktop/Mobile |
| Ubuntu `ubuntu-latest` | suíte M12 validada em CI; não é target formal de distribuição |
| macOS | não homologado |
| SQLite | embarcado/local; nenhum database server necessário |
| OpenAI | opcional; a auditoria funciona sem IA |
| Docker / web server | não requeridos e não fornecidos nesta baseline |

O contrato completo, incluindo rede, filesystem, Chromium e estado de homologação, está em [Compatibilidade e Dependências](docs/COMPATIBILITY.md).

## Dependências

Obrigatórias:

- CPython 3.13;
- `pip`;
- package do projeto, que declara `playwright>=1.57,<2`;
- Chromium funcional para rendering real;
- filesystem local gravável;
- acesso HTTP/HTTPS ao target.

Opcional:

- OpenAI para análise semântica via `OpenAIProvider`.

Não são obrigatórios: Docker, database server, web server, SDK Python `openai`, Git ou GitHub em runtime.

## Capacidades principais

- Discovery por seed, `robots.txt`, sitemap e links internos, limitado por `max_pages`.
- Aquisição HTTP com redirects, headers, body e erros de rede rastreáveis.
- Rendering real com Playwright/Chromium para Desktop e Mobile em contextos independentes.
- Extração de metadata, canonical, robots, headings, links, conteúdo principal e JSON-LD.
- Evidence First: findings apontam para RuleExecution e Evidence persistidas.
- Business Rules `BR-GEO-001..054`, incluindo JavaScript/SPA, semântica, entidades, Dados Estruturados, answerability, citation readiness e comparação Desktop/Mobile.
- Scoring determinístico por dispositivo em 10 dimensões, com Coverage, Confidence e Consolidation.
- Priorização, Remediation Groups e recomendações determinísticas.
- IA opcional: `NoneProvider` por padrão e `OpenAIProvider` opcional.
- Relatório HTML5 estático, autocontido e prioritariamente pt-BR.

## Arquitetura resumida

```text
CLI
  -> AuditRunner
  -> Discovery + HTTP
  -> Rendering Desktop/Mobile
  -> Extraction + Evidence
  -> Deterministic Rules
  -> JavaScript/SPA + Content Extractability
  -> Semantic Provider
  -> Desktop/Mobile Comparison
  -> Scoring
  -> Prioritization + Recommendations
  -> report.html
```

Os dados primários ficam em `audit.db` e nos artifacts. `report.html` é uma projeção desses dados, não a fonte primária.

## Quick start — PowerShell

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m playwright install chromium
searchgeo --version
searchgeo audit https://example.com --project "Exemplo"
```

Por padrão:

- idioma: `pt-BR`;
- mercado: `BR`;
- limite: `100` páginas;
- raiz de saída: `audits`;
- IA: desativada (`--ai-provider none`).

Ao concluir, a CLI informa o ID da auditoria e o caminho do relatório. A estrutura básica é:

```text
audits/<AUD-ID>/
  audit.db
  report.html
  artifacts/
```

Consulte [Outputs e Artifacts](docs/OUTPUTS_AND_ARTIFACTS.md) para a estrutura detalhada.

## Exemplo com opções

```powershell
searchgeo audit https://example.com `
  --project "Site Institucional" `
  --language pt-BR `
  --market BR `
  --max-pages 50 `
  --audits-root .\audits
```

## Como configurar IA

IA é opcional. Sem IA:

```powershell
searchgeo audit https://example.com --ai-provider none
```

Esse é o default. A auditoria continua em `NO_AI`; avaliações semantic-only sem dados suficientes ficam `UNKNOWN`, sem transformar ausência de IA em falha do website.

Para usar OpenAI:

```powershell
$env:OPENAI_API_KEY = "<sua-chave>"
$env:SEARCHGEO_OPENAI_MODEL = "<modelo-configurado>"
searchgeo audit https://example.com --ai-provider openai
```

Alternativamente, forneça o model na CLI:

```powershell
$env:OPENAI_API_KEY = "<sua-chave>"
searchgeo audit https://example.com --ai-provider openai --ai-model "<modelo-configurado>"
```

Requisitos para IA efetiva:

1. `--ai-provider openai`;
2. `OPENAI_API_KEY` definida no ambiente;
3. model definido por `--ai-model` ou `SEARCHGEO_OPENAI_MODEL`;
4. egress HTTPS disponível para o provider;
5. política de dados permitindo transmitir conteúdo/evidence do site auditado ao serviço externo.

Não grave API keys no repositório, TOML, artifacts ou scripts versionados. O projeto não fixa um nome de modelo; a compatibilidade do modelo configurado deve ser validada no momento da homologação. Consulte [AI Guide](docs/AI_GUIDE.md) e [Compatibilidade](docs/COMPATIBILITY.md).

## Documentação

- [Compatibilidade e dependências](docs/COMPATIBILITY.md)
- [Instalação](docs/INSTALLATION.md)
- [Guia do usuário](docs/USER_GUIDE.md)
- [Configuração](docs/CONFIGURATION.md)
- [Interpretação do relatório](docs/REPORT_GUIDE.md)
- [Business Rules](docs/RULES_GUIDE.md)
- [Scoring e Reliability](docs/SCORING_GUIDE.md)
- [IA e fallback](docs/AI_GUIDE.md)
- [Outputs e artifacts](docs/OUTPUTS_AND_ARTIFACTS.md)
- [Guia técnico](docs/TECHNICAL_GUIDE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Smoke test humano](docs/SMOKE_TEST.md)

## Fonte normativa

A documentação acima explica uso e engenharia da Stable Local Baseline. A fonte normativa do produto permanece em [`docs/specification`](docs/specification/00_SPEC_INDEX.md). Em caso de conflito, **`docs/specification` prevalece**.

## Limitações atuais

- Não existe executável portátil/distribuição standalone: Python 3.13 continua necessário.
- Não existe interface web nem backend HTTP do produto.
- Logging é configurado no processo; a baseline atual não materializa um `audit.log` por auditoria.
- A configuração TOML atual expõe somente `log_level`; parâmetros de auditoria são passados pela CLI.
- IA é opcional e depende de serviço externo somente quando `OpenAIProvider` é selecionado.
- Compatibilidade operacional final em Windows ainda depende da execução humana de `docs/SMOKE_TEST.md`.
