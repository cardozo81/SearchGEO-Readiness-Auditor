# DECISIONS.md

**Status:** CURRENT

## DECIDED

### D-001
Desktop e Mobile serão avaliados separadamente.

### D-002
Relatório oficial será HTML estruturado e profissional.

### D-003
Testes mínimos orientados a risco.

### D-004
GitHub somente após baseline local estável.

### D-005
Uma máquina e um operador humano no MVP.

### D-006
Arquitetura distribuída não é requisito inicial.

### D-007
Multiusuário não é requisito inicial.

### D-008
As 10 dimensões permanecem no MVP.

### D-009
Existirá Overall Readiness separado para Desktop e Mobile, somente quando consolidável.

### D-010
`max_pages` padrão = 100, configurável.

### D-011
Intent analysis entra no MVP de forma controlada: 1 primary + até 5 secondary intents.

### D-012
Benchmark de concorrentes fica para V1.

### D-013
Interface inicial será CLI, não aplicação web.

### D-014
Rendering baseline será Playwright + Chromium.

### D-015
Organização conceitual/física: Audit → Page → Device Context. Dados estruturados em SQLite embarcado; artefatos grandes em filesystem.

### D-016
Nenhum database server ou serviço externo de banco será obrigatório.

### D-017
IA é opcional. Auditor deve funcionar sem provider.

### D-018
Resultados relevantes devem informar Coverage, Confidence e Consolidation Status.

### D-019
Ausência de IA nunca representa baixa qualidade do website.

### D-020
Camada semântica será independente de fornecedor/modelo.

### D-021
MVP implementará NoneProvider e pelo menos um provider real; baseline real inicial: OpenAI.

### D-022
Score oficial deve conter Value, Coverage, Confidence e Consolidation.

### D-023
Ausência de IA reduz cobertura/consolidação, nunca score do website diretamente.

### D-024
Pesos iguais entre dimensões no MVP.

### D-025
Scoring groups impedem dupla penalização de causa correlacionada.

### D-026
Na máquina de desenvolvimento/MVP, uso de API externa de IA é permitido.

### D-027
OpenAI é o provider inicial previsto para o MVP, sem dependência arquitetural.

### D-030
Relatório destinado ao usuário será prioritariamente em português.

### D-031
Termos técnicos oficiais podem permanecer em inglês quando tradução reduzir precisão; glossário/contexto são obrigatórios.

## PENDING ENVIRONMENT VALIDATION

### D-028
Verificar acesso técnico à API OpenAI na máquina/rede corporativa.

Validar:

- DNS;
- TLS;
- proxy;
- firewall;
- endpoint API;
- authentication;
- timeout;
- políticas de saída.

Acessibilidade técnica não significa autorização corporativa.

## PENDING CORPORATE VALIDATION

### D-029
Identificar provider de IA permitido/preferido corporativamente.

Possibilidades arquiteturais:

- OpenAI;
- Azure OpenAI;
- Google;
- Anthropic;
- AWS Bedrock;
- modelo local;
- nenhum.

Também validar corporativamente:

- autorização para envio de conteúdo a IA externa;
- execução de Chromium/browser;
- executável portátil;
- escrita em filesystem;
- SQLite embarcado;
- antivírus/EDR;
- políticas de execução.

Essas pendências não bloqueiam desenvolvimento local do MVP.

## Restrições aprovadas adicionais

- aplicação local Windows;
- não web;
- sem Docker obrigatório;
- sem admin como objetivo de distribuição;
- relatório estático;
- SQLite não é considerado dependência de database server;
- RAW + RENDERED sempre preservados no baseline;
- arquitetura do site não gera penalidade por si só;
- `llms.txt` não impacta score automaticamente;
- GPTBot e OAI-SearchBot possuem papéis distintos;
- findings devem ser evidence-backed;
- LLM nunca é scoring engine;
- cascading failures devem ser controladas.
