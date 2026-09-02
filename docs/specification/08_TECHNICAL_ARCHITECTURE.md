# TECHNICAL_ARCHITECTURE.md

**Status:** APPROVED  
**Architecture:** Local Modular Monolith

## 1. Princípio

Uma aplicação local, um processo principal e módulos internos.

Não utilizar no MVP:

- microservices;
- API server;
- web application;
- message broker;
- database server;
- distributed workers;
- cloud backend obrigatório.

## 2. Stack

Linguagem recomendada:

Python

Versão exata definida no bootstrap conforme compatibilidade das dependências.

## 3. Componentes

CLI
→ Audit Orchestrator
→ Discovery Engine
→ HTTP Acquisition
→ Browser Renderer
→ Snapshot Builder
→ Content Extractor
→ Evidence Manager
→ Rules Engine
→ Semantic Analysis Service
→ Desktop/Mobile Comparator
→ Finding Engine
→ Scoring Engine
→ Prioritization Engine
→ Recommendation Engine
→ Remediation Grouper
→ Report Builder

## 4. Persistência

SQLite embarcado + filesystem.

SQLite:

- sem servidor;
- sem serviço Windows;
- sem porta;
- sem instalação de engine externo.

Filesystem:

- response.html;
- rendered.html;
- main_content.txt;
- structured_data.json;
- logs;
- report.html.

## 5. Abstração de persistência

Business Logic
→ Repository
→ Persistence Adapter
→ SQLite/filesystem

## 6. CLI

Interface inicial:

`searchgeo audit <target>`

Opções futuras do MVP:

- --project
- --language
- --market
- --max-pages
- --config
- --ai-provider

## 7. Configuração

Configuração externa ao código.

Formato sugerido:

`searchgeo.toml`

Segredos preferencialmente em environment variables.

## 8. Audit Orchestrator

Coordena workflows.

Não implementa Business Rules diretamente.

## 9. Capability Detector

Detecta:

- filesystem;
- SQLite;
- browser;
- renderer;
- AI provider.

Determina:

- FULL;
- DEGRADED;
- NO_AI.

## 10. Discovery Engine

Responsabilidades:

- seed;
- robots;
- sitemap;
- internal links;
- normalization;
- deduplication;
- max_pages.

Seleção determinística quando excede limite:

1. seed;
2. sitemap;
3. menor crawl depth;
4. maior quantidade de referências internas;
5. desempate estável.

## 11. HTTP Acquisition

Separada da renderização.

Produz:

- requested URL;
- final URL;
- status;
- headers;
- redirects;
- body;
- network errors;
- timings.

## 12. Browser Renderer

Baseline:

Playwright + Chromium

Responsável por:

- JavaScript;
- DOM;
- controlled settling;
- bounded scrolling;
- rendered capture;
- diagnostics relevantes.

## 13. Desktop/Mobile Profiles

Perfis independentes.

Mobile não é apenas redução de viewport.

## 14. Content Extractor

Extrai:

- main content;
- metadata;
- headings;
- links;
- Dados Estruturados;
- text blocks.

Não realiza análise semântica profunda.

## 15. Evidence Manager

Cria `EV-GEO-*`.

Evidence não é log.

## 16. Rules Engine

Componentes:

- Rule Registry;
- Check/Validator;
- Applicability Resolver;
- Dependency Resolver;
- Rule Executor;
- Finding Engine.

## 17. Semantic Analysis

Interface:

SemanticAnalysisProvider

MVP:

- NoneProvider;
- OpenAIProvider.

Futuro:

- Anthropic;
- Gemini;
- Azure OpenAI;
- Bedrock;
- Local.

Business Rules nunca importam diretamente provider específico.

## 18. Semantic Normalization

Provider
→ normalized result
→ schema validation
→ evidence validation
→ SemanticAssessment

Falha do provider não encerra auditoria.

## 19. Scoring

Scoring Engine não faz chamadas a LLM.

## 20. Reporting

Relatório:

- HTML5;
- CSS local/inline;
- JavaScript mínimo;
- SVG inline quando útil;
- sem backend;
- sem CDN;
- sem remote fonts;
- sem internet obrigatória.

## 21. Logging

Cada auditoria produz `audit.log`.

Logs não substituem Evidence.

## 22. Segurança

API keys/tokens nunca devem ir para:

- report;
- evidence;
- log;
- artifacts.

## 23. Distribuição

Meta:

SearchGEO/
├── searchgeo.exe
├── runtime/
├── browser/
├── config/
└── audits/

Preferencialmente copiar/extrair/executar.

Não assumir Python instalado na máquina final.

## 24. Estrutura de código sugerida

src/searchgeo/
├── cli/
├── config/
├── domain/
├── workflows/
├── discovery/
├── acquisition/
├── rendering/
├── extraction/
├── evidence/
├── rules/
│   ├── checks/
│   └── definitions/
├── semantic/
│   └── providers/
├── comparison/
├── scoring/
├── prioritization/
├── recommendations/
├── persistence/
├── reporting/
└── diagnostics/

Não criar módulos futuros vazios durante M0 apenas para reproduzir esta árvore.

## 25. Complexidade a evitar

- event bus;
- DI framework pesado;
- ORM sofisticado sem necessidade;
- async generalizado prematuramente;
- plugin framework completo;
- cloud abstractions;
- microservices.
