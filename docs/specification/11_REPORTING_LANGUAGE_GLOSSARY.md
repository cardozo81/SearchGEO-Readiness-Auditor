# REPORTING_LANGUAGE_GLOSSARY.md

**Status:** APPROVED

## 1. Regra editorial

O relatório destinado ao usuário deverá ser prioritariamente em português.

Inglês somente quando:

- nome técnico é consagrado;
- nome oficial não deve ser traduzido;
- tradução poderia reduzir precisão;
- valor deriva diretamente de protocolo/HTML/API.

## 2. Tradução da interface

Technical Accessibility
→ Acessibilidade Técnica

Indexability
→ Capacidade de Indexação

Content Extractability
→ Extração de Conteúdo

Semantic Structure
→ Estrutura Semântica

Entity Clarity
→ Clareza de Entidades

Structured Data
→ Dados Estruturados

Answerability
→ Capacidade de Resposta

Citation Readiness
→ Preparação para Citação

Evidence & Trust
→ Evidências e Confiabilidade

Intent Coverage
→ Cobertura de Intenções

Finding
→ Problema Identificado

Recommendation
→ Recomendação

Severity
→ Severidade

Impact
→ Impacto

Effort
→ Esforço

Confidence
→ Confiabilidade

Coverage
→ Cobertura da Análise

Consolidated
→ Consolidado

Partial
→ Parcial

Not Consolidated
→ Não Consolidado

Unknown
→ Não Determinado

Warning
→ Alerta

PASS
→ Aprovado

FAIL
→ Problema identificado

NOT_APPLICABLE
→ Não aplicável

ERROR
→ Erro de execução da análise

## 3. Termos técnicos preservados

Exemplos:

- HTTP;
- robots.txt;
- canonical;
- noindex;
- JSON-LD;
- Googlebot;
- OAI-SearchBot;
- GPTBot;
- SPA;
- SSR;
- CSR;
- Playwright;
- Chromium.

Primeira ocorrência pode usar:

Canonical (URL canônica)

Soft 404 (página com semântica de erro sem status HTTP apropriado)

Client-Side Rendering — CSR (renderização no navegador)

## 4. Seção obrigatória

Título:

`Como interpretar este relatório`

Deve explicar:

### Nota

Resultado quantitativo das regras efetivamente avaliadas.

### Cobertura da Análise

Quanto do universo aplicável pôde ser efetivamente analisado.

Baixa coverage não significa necessariamente baixa qualidade do site.

### Confiabilidade

Grau de segurança da conclusão com base em evidence, método e limitações.

### Consolidado

Há cobertura e confiabilidade suficientes para apresentar o resultado como consolidado.

### Parcial

Parte relevante da avaliação está disponível, mas existem limitações.

### Não Consolidado

Não há base suficiente para apresentar uma nota conclusiva.

### Severidade

Gravidade intrínseca do problema.

### Prioridade

Ordem recomendada de ação considerando gravidade, impacto, confiabilidade e facilidade.

### Desktop e Mobile

São contextos independentes e podem apresentar resultados diferentes.

## 5. Disclaimer de IA

Quando não houver IA:

`Algumas avaliações semânticas não foram executadas porque não havia um provedor de inteligência artificial disponível ou configurado. Essa limitação reduz a cobertura da auditoria e não representa um problema do website analisado.`

Quando IA externa for usada, o relatório deve indicar que análises semânticas utilizaram provider externo, sem revelar credenciais.

## 6. Restrições

Nunca usar no relatório linguagem que prometa:

- ranking;
- citação;
- visibilidade;
- presença em mecanismo generativo.

O produto mede readiness.
