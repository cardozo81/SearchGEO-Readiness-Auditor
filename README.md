# SearchGEO Readiness Auditor

Auditor local de **Search/GEO Readiness** para avaliar, com rastreabilidade técnica, quão acessível, extraível, semanticamente compreensível e reutilizável um site é para mecanismos de busca e sistemas generativos.

## Status atual

**Baseline local estável até M18 + SCORE-GEO-002.** A aplicação executa auditoria ponta a ponta por CLI, separa Desktop e Mobile, persiste estado em SQLite + filesystem, gera `report.html` e `remediation.html`, possui integração opcional com múltiplos providers de IA semântica e distingue dimensões aplicáveis de dimensões legitimamente fora do universo aplicável.

> Readiness não é promessa de ranking, tráfego, citação, presença ou visibilidade em mecanismos generativos.

## Compatibilidade — leia antes de instalar

| Item | Estado |
|---|---|
| Windows + PowerShell | target operacional de handoff |
| CPython 3.13.x | obrigatório; `>=3.13,<3.14` |
| Python 3.12 ou 3.14+ | incompatível pelo contrato atual do package |
| Playwright `>=1.57,<2` | obrigatório |
| Chromium | obrigatório para rendering real Desktop/Mobile |
| Ubuntu `ubuntu-latest` | validado por suíte automatizada; não é target formal de distribuição |
| macOS | não homologado |
| SQLite | embarcado/local; nenhum database server necessário |
| OpenAI | opcional; provider semântico suportado |
| DeepSeek | opcional; provider semântico suportado, qualificação SearchGEO `PROVISIONAL` |
| Xiaomi MiMo | opcional; provider semântico suportado, qualificação SearchGEO `PROVISIONAL` |
| Docker / web server | não requeridos e não fornecidos |

O contrato completo está em [Compatibilidade e Dependências](docs/COMPATIBILITY.md).

## Premissas mínimas para GEO e JSON-LD

O foco primário do baseline é **Google Search e seus recursos de IA**.

JSON-LD **não é requisito universal para GEO funcional**. O SearchGEO classifica Structured Data como **OPCIONAL / REFORÇO**: ausência legítima não recebe zero nem impede, sozinha, uma Compatibilidade GEO mensurável. Quando JSON-LD existe, `BR-GEO-034..037` tornam-se aplicáveis e podem melhorar, manter ou reduzir o resultado conforme interpretabilidade e coerência com o conteúdo visível.

`SCORE-GEO-002` mantém as dez dimensões, mas distingue:

- dimensão sem execução ou com aplicabilidade não resolvida: `NOT_CONSOLIDATED`, podendo bloquear Overall;
- dimensão integralmente e legitimamente fora do universo aplicável: `NOT_APPLICABLE`, fora do denominador do Overall, sem nota artificial 0 ou 100;
- tópico opcional que passa a existir: volta automaticamente ao universo aplicável e entra no scoring.

O `report.html` informa quantas dimensões foram efetivamente consideradas. Consulte [Premissas mínimas e reforços para GEO](docs/GEO_MINIMUM_REQUIREMENTS.md) e [Scoring e Reliability](docs/SCORING_GUIDE.md).

## Dependências obrigatórias

- CPython 3.13;
- `pip`;
- package do projeto;
- Playwright `>=1.57,<2`;
- Chromium funcional para rendering real;
- filesystem local gravável;
- acesso HTTP/HTTPS ao target.

IA é opcional. Não é necessário instalar SDK Python de OpenAI, DeepSeek ou MiMo: os adapters usam HTTP.

## Capacidades principais

- Discovery por seed, `robots.txt`, sitemap e links internos, limitado por `max_pages`.
- Auditoria de uma URL, múltiplas URLs posicionais ou `--urls-file` em um mesmo `audit_id`.
- Aquisição HTTP com redirects, headers, body e erros de rede rastreáveis.
- Rendering real com Playwright/Chromium para Desktop e Mobile independentes.
- Screenshots e observações de elementos DOM quando determináveis.
- Extração de metadata, canonical, robots, headings, links, conteúdo principal e JSON-LD.
- Evidence First: findings apontam para RuleExecution e Evidence persistidas.
- Business Rules `BR-GEO-001..054`.
- Scoring determinístico `SCORE-GEO-002` por dispositivo em 10 dimensões, com Coverage, Confidence, Consolidation e aplicabilidade explícita.
- Priorização, causa raiz, remediation groups e recomendações determinísticas.
- IA opcional com `none`, OpenAI, DeepSeek, MiMo ou `auto` multi-provider.
- Failover controlado, quarantine por audit e lock de provider por URL.
- Telemetria de IA persistida e exibida no relatório.
- `report.html` orientado à auditoria e `remediation.html` orientado aos problemas.

## Arquitetura resumida

```text
CLI
  -> AuditRunner
  -> Discovery + HTTP
  -> Rendering Desktop/Mobile
  -> Extraction + Evidence
  -> Deterministic Rules
  -> JavaScript/SPA + Content Extractability
  -> Semantic Provider (none | single provider | AUTO)
  -> Desktop/Mobile Comparison
  -> Scoring + Applicability
  -> Prioritization + Root Cause + Recommendations
  -> report.html + remediation.html
```

Os dados primários ficam em `audit.db` e nos artifacts. Os HTMLs são projeções para leitura humana.

# Instalação rápida — PowerShell

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m playwright install chromium
searchgeo --version
```

# Execução rápida

Sem IA, que é o default:

```powershell
searchgeo audit https://example.com --project "Exemplo"
```

Com várias URLs:

```powershell
searchgeo audit `
  https://example.com/ `
  https://example.com/produto `
  https://example.com/faq `
  --project "Exemplo"
```

Por arquivo:

```powershell
searchgeo audit --urls-file .\urls.txt --project "Exemplo"
```

Defaults relevantes:

- idioma: `pt-BR`;
- mercado: `BR`;
- limite: `100` páginas;
- raiz de saída: `audits`;
- IA: `none`.

Ao concluir, a CLI informa o ID da auditoria, status, páginas auditadas, quantidade de problemas/recomendações e paths dos relatórios.

Estrutura principal:

```text
audits/<AUD-ID>/
  audit.db
  report.html
  remediation.html
  artifacts/
```

# Referência completa da linha de comando

A lista de **todos os parâmetros expostos**, defaults, regras de combinação, formatos de target e exemplos fica em:

**[Referência completa da CLI](docs/CLI_REFERENCE.md)**

Resumo do `audit`:

```text
searchgeo [--config PATH] audit [target ...]
  [--urls-file PATH]
  [--project TEXT]
  [--language CODE]
  [--market CODE]
  [--max-pages N]
  [--audits-root PATH]
  [--ai-provider none|openai|deepseek|mimo|auto]
  [--ai-model MODEL_ID]
```

Use também:

```powershell
searchgeo --help
searchgeo audit --help
```

# Como configurar IA

## 1. Não usar IA

```powershell
searchgeo audit https://example.com --ai-provider none
```

`none` é o default. A auditoria continua com regras determinísticas. Regras semantic-only sem base suficiente ficam `UNKNOWN`; ausência de IA não é `FAIL` do website.

## 2. Usar somente um provider

### OpenAI

```powershell
$env:OPENAI_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider openai
```

Default: `gpt-5.6-terra` / `HIGH`.

### DeepSeek

```powershell
$env:DEEPSEEK_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider deepseek
```

Default: `deepseek-v4-pro` / `HIGH`.

### Xiaomi MiMo

```powershell
$env:MIMO_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider mimo
```

Default: `mimo-v2.5-pro` / `HIGH`, normalizado no relatório como `THINKING_ENABLED`.

Um provider explícito **não faz fallback para outro fornecedor**. Após falha qualificadora ele entra em `QUARANTINED_FOR_AUDIT` e não é chamado novamente dentro daquele audit. A ausência das chaves dos outros providers não interfere na execução explícita escolhida.

## Timeout das chamadas de IA

A CLI usa `180` segundos por chamada semântica externa. O valor pode ser alterado por ambiente:

```powershell
$env:SEARCHGEO_AI_TIMEOUT_SECONDS = "240"
searchgeo audit https://example.com --ai-provider openai
```

O valor deve ser numérico, finito e maior que zero. Timeout não dispara retry automático, evitando uma segunda cobrança potencial quando a primeira chamada expirou localmente mas pode ter continuado no provider.

## 3. Usar vários providers com fallback

Configure duas ou três chaves e selecione `auto`:

```powershell
$env:OPENAI_API_KEY = "<chave-openai>"
$env:DEEPSEEK_API_KEY = "<chave-deepseek>"
$env:MIMO_API_KEY = "<chave-mimo>"
searchgeo audit --urls-file .\urls.txt --project "Exemplo" --ai-provider auto
```

`AUTO` monta uma cadeia imutável no início do audit com apenas providers que possuem token e configuração válida. As chamadas são sequenciais, não paralelas. O primeiro resultado válido encerra a cadeia naquele contexto; providers posteriores não são chamados para sobrescrever o resultado.

Para os modelos default, a ordem atual é:

1. OpenAI `gpt-5.6-terra`;
2. DeepSeek `deepseek-v4-pro`;
3. MiMo `mimo-v2.5-pro`.

A política completa inclui também OpenAI Sol/Luna, DeepSeek Flash e MiMo V2.5 conforme o model configurado. A classificação é uma política de adequação ao contrato SearchGEO, não um benchmark científico universal.

## Modelos aceitos pelo código

```text
OPENAI:   gpt-5.6-sol | gpt-5.6-terra | gpt-5.6-luna
DEEPSEEK: deepseek-v4-pro | deepseek-v4-flash
MIMO:     mimo-v2.5-pro | mimo-v2.5
```

`--ai-model` é permitido somente para provider explícito. Em `auto`, configure o model via variável específica do provider.

## Provider selecionado sem token

- provider explícito: fica `NOT_CONFIGURED`, nenhuma chamada externa ocorre e a auditoria segue sem IA efetiva;
- `auto`: o provider sem token não entra na cadeia;
- se nenhum provider for elegível em `auto`, nenhuma chamada externa é feita.

Isso reduz capacidade semântica/cobertura quando aplicável, mas não transforma o website em `FAIL`.

## Erro, quota, sem créditos ou timeout

O runtime classifica falhas como autenticação, quota/crédito, rate limit, modelo/permissão, rede/timeout/server ou contrato/resposta inválida.

- provider explícito: sessão semântica fica `DEGRADED`; não há cross-provider fallback;
- `auto`: provider falho fica `QUARANTINED_FOR_AUDIT` e o próximo provider saudável pode ser usado;
- se todos os providers do `auto` falharem, o estado operacional fica `CHAIN_EXHAUSTED` e a auditoria registra `AI_PROVIDER_CHAIN_EXHAUSTED`.

## Lock de provider por URL

Quando uma URL recebe a primeira análise válida, o provider fica fixado para Desktop/Mobile dessa URL. Se ele falhar no segundo device, outro provider **não** completa a mesma URL; o provider é quarantined para URLs seguintes e o contexto faltante permanece degradado/`UNKNOWN` quando aplicável.

# Relatório, persistência e log de uso da IA

O `report.html` contém a seção **Uso de IA — execução e telemetria**, com:

- estratégia;
- provider/model inicial e efetivo;
- profundidade/reasoning;
- cadeia inicial;
- status e failover;
- cobertura por URL/device;
- tentativa por tentativa;
- tokens reportados;
- duração;
- `ESTIMATED_COST` quando calculável;
- erro sanitizado.

A seção de telemetria é inserida dentro de `<main>`. Quando a tabela excede a largura disponível, a rolagem horizontal ocorre dentro do próprio bloco, sem invadir a sidebar fixa.

No `audit.db`, M18 persiste:

```text
ai_audit_sessions
ai_provider_attempts
provider_pricing_catalog
```

A execução também emite logging sanitizado conforme `log_level`, sem API key, Authorization ou corpo integral da requisição. A baseline **não materializa `audit.log` automaticamente**; o registro persistente de uso é `audit.db` + `report.html`.

`ESTIMATED_COST` é estimativa local versionada e não equivale a billing/invoice do provider nem participa do score.

# Segurança das chaves

Não grave API keys em:

- repositório;
- TOML versionado;
- artifacts;
- HTML;
- scripts compartilhados;
- logs.

Valide presença sem imprimir o segredo:

```powershell
Test-Path Env:OPENAI_API_KEY
Test-Path Env:DEEPSEEK_API_KEY
Test-Path Env:MIMO_API_KEY
```

# Documentação

- [Premissas mínimas e reforços para GEO](docs/GEO_MINIMUM_REQUIREMENTS.md)
- [Referência completa da CLI](docs/CLI_REFERENCE.md)
- [Compatibilidade e dependências](docs/COMPATIBILITY.md)
- [Instalação](docs/INSTALLATION.md)
- [Guia do usuário](docs/USER_GUIDE.md)
- [Configuração](docs/CONFIGURATION.md)
- [Interpretação do relatório](docs/REPORT_GUIDE.md)
- [Business Rules](docs/RULES_GUIDE.md)
- [Scoring e Reliability](docs/SCORING_GUIDE.md)
- [IA, routing e fallback](docs/AI_GUIDE.md)
- [Outputs e artifacts](docs/OUTPUTS_AND_ARTIFACTS.md)
- [Guia técnico](docs/TECHNICAL_GUIDE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Smoke test humano](docs/SMOKE_TEST.md)

## Fonte normativa

A documentação operacional explica o uso da implementação. A fonte normativa permanece em [`docs/specification`](docs/specification/00_SPEC_INDEX.md). Em caso de conflito, `docs/specification` prevalece.

## Limitações atuais

- não existe executável standalone/portátil; Python 3.13 continua necessário;
- não existe interface web/backend HTTP do produto;
- logging é do processo; não existe `audit.log` persistido automaticamente por auditoria;
- configuração TOML continua restrita ao escopo exposto pelo módulo de configuração; parâmetros de auditoria são CLI/environment;
- providers externos exigem egress HTTPS, credencial e política de dados compatível;
- DeepSeek e MiMo permanecem `PROVISIONAL` na política de qualificação SearchGEO até benchmark específico;
- o parser de Structured Data do SearchGEO possui cobertura operacional específica para JSON-LD; Microdata/RDFa ainda não devem ser tratados como equivalentes no auditor;
- smoke live de M18 com providers reais depende de credenciais disponíveis no ambiente de homologação.
