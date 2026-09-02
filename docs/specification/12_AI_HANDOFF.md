# AI_HANDOFF.md

## 1. Objetivo do produto

Construir um auditor local de Search/GEO Readiness baseado em evidence, regras reproduzíveis e análise semântica opcional.

## 2. Fonte de verdade

Leia primeiro:

`00_SPEC_INDEX.md`

Depois siga a ordem obrigatória indicada nele.

Não derive requisitos do histórico de chats quando houver definição normativa nestes arquivos.

## 3. Estado atual

Especificação funcional:
APPROVED

Domain Model:
APPROVED

Business Rules:
APPROVED

Workflows:
APPROVED

Scoring:
APPROVED

Prioritization:
APPROVED

Technical Architecture:
APPROVED

Implementation Plan:
APPROVED

Código:
M0 COMPLETED

## 4. Próximo marco

`M1 — Audit + Persistence`

Não avance automaticamente para M2.

## 5. Restrições principais

- Windows;
- aplicação local;
- não web;
- CLI;
- uma máquina;
- um operador;
- SQLite embarcado + filesystem;
- sem database server;
- sem Docker obrigatório;
- Git/GitHub utilizados para versionamento do desenvolvimento, sem dependência de runtime;
- Desktop/Mobile independentes;
- RAW + RENDERED;
- Playwright + Chromium;
- SPA/non-SPA no mesmo pipeline;
- Evidence First;
- Deterministic First;
- IA opcional;
- NoneProvider obrigatório;
- OpenAI primeiro provider real;
- relatório HTML estático em português;
- testes mínimos.

## 6. Não reabrir decisões

Não solicitar decisão humana para:

- nomes internos de classes;
- estrutura interna simples;
- pequenas bibliotecas;
- refactors sem impacto funcional;
- organização de arquivos sem alteração de contrato.

Escolha a solução técnica mais simples compatível com a baseline.

## 7. Solicitar decisão humana somente quando houver

1. alteração de escopo;
2. conflito entre requisitos aprovados;
3. impossibilidade técnica relevante;
4. mudança material de scoring;
5. mudança material de prioridade;
6. alteração na experiência/natureza do relatório;
7. política ou restrição corporativa.

## 8. Pendências humanas atuais

Somente para homologação corporativa:

- acesso técnico à OpenAI;
- autorização corporativa de IA externa;
- provider permitido;
- execução de browser/Chromium;
- distribuição portátil;
- filesystem;
- SQLite;
- EDR/políticas.

Não bloqueiam M1 local.

## 9. M0 — CONCLUÍDO

M0 entregou:

- estrutura mínima;
- package Python;
- configuração;
- logging;
- CLI;
- --version;
- audit <target>;
- validação básica.

Não foram criados módulos futuros vazios apenas porque aparecem em TECHNICAL_ARCHITECTURE.

O próximo marco permitido é M1, conforme `09_IMPLEMENTATION_PLAN.md`.
