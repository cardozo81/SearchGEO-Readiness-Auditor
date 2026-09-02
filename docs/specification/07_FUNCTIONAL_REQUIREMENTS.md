# FUNCTIONAL_REQUIREMENTS.md

**Status:** APPROVED

## Requisitos Funcionais

### FR-GEO-001
Criar auditoria com target, project, language, market e max_pages.

### FR-GEO-002
Gerar identificador único de auditoria.

### FR-GEO-003
Operar localmente em Windows, sem servidor web ou banco externo obrigatório.

### FR-GEO-004
Persistir dados localmente utilizando SQLite embarcado + filesystem.

### FR-GEO-005
Descobrir URLs por seed, links internos e sitemap.

### FR-GEO-006
Limitar universo a max_pages de forma determinística e informar limitação.

### FR-GEO-007
Avaliar Desktop e Mobile separadamente.

### FR-GEO-008
Capturar HTTP, headers, redirects, final URL, status e erros.

### FR-GEO-009
Preservar RAW HTML.

### FR-GEO-010
Renderizar página com browser controlado.

### FR-GEO-011
Preservar DOM renderizado.

### FR-GEO-012
Suportar HTML, SSR, SSG, hydration, CSR, SPA e híbridos.

### FR-GEO-013
Comparar RAW × RENDERED.

### FR-GEO-014
Extrair conteúdo principal.

### FR-GEO-015
Interpretar robots.txt e crawlers configurados.

### FR-GEO-016
Avaliar indexabilidade.

### FR-GEO-017
Avaliar problemas materiais de JavaScript e SPA.

### FR-GEO-018
Detectar e validar Dados Estruturados quando presentes.

### FR-GEO-019
Executar BR-GEO-001..054.

### FR-GEO-020
Padronizar resultados PASS, FAIL, WARNING, UNKNOWN, NOT_APPLICABLE, ERROR.

### FR-GEO-021
Evitar cascading failures.

### FR-GEO-022
Registrar evidências rastreáveis.

### FR-GEO-023
Possuir SemanticAnalysisProvider independente de fornecedor.

### FR-GEO-024
Funcionar sem IA.

### FR-GEO-025
Possuir fallback determinístico/heurístico seguro.

### FR-GEO-026
Permitir múltiplos providers; MVP implementa NONE + OpenAI.

### FR-GEO-027
Validar schema e evidence_ids da saída da IA.

### FR-GEO-028
Avaliar estrutura semântica.

### FR-GEO-029
Avaliar entidades.

### FR-GEO-030
Avaliar capacidade de resposta.

### FR-GEO-031
Avaliar preparação para citação.

### FR-GEO-032
Avaliar evidência e confiança.

### FR-GEO-033
Avaliar 1 primary intent + até 5 secondary intents.

### FR-GEO-034
Comparar Desktop × Mobile.

### FR-GEO-035
Criar findings estruturados.

### FR-GEO-036
Calcular scores nas 10 dimensões por dispositivo.

### FR-GEO-037
Informar Coverage.

### FR-GEO-038
Informar Confidence.

### FR-GEO-039
Informar Consolidation Status.

### FR-GEO-040
Calcular Overall Desktop e Overall Mobile somente com cobertura suficiente.

### FR-GEO-041
Evitar dupla penalização via scoring groups.

### FR-GEO-042
Associar Severity, Impact, Effort, Confidence e Priority.

### FR-GEO-043
Aplicar modelo de priorização aprovado.

### FR-GEO-044
Consolidar recomendações repetitivas por causa raiz.

### FR-GEO-045
Gerar recomendações técnicas mesmo sem IA.

### FR-GEO-046
Gerar `report.html` estático.

### FR-GEO-047
Produzir relatório autocontido sempre que viável.

### FR-GEO-048
Utilizar português na camada de apresentação.

### FR-GEO-049
Fornecer legenda e glossário.

### FR-GEO-050
Explicar limitações provocadas por indisponibilidade de IA.

### FR-GEO-051
Preservar termos técnicos quando tradução prejudicar precisão.

### FR-GEO-052
Produzir relatório profissional com resumo, scorecard, findings, evidence, prioridades, recomendações, limitações e detalhes técnicos.

## Requisitos Não Funcionais

### NFR-GEO-001
Executar em Windows.

### NFR-GEO-002
Preferencialmente sem privilégios administrativos.

### NFR-GEO-003
Não exigir banco server, web server, Docker, IA ou GitHub.

### NFR-GEO-004
Priorizar distribuição portátil.

### NFR-GEO-005
Resultados determinísticos devem ser reproduzíveis.

### NFR-GEO-006
Toda conclusão deve ser rastreável.

### NFR-GEO-007
Versionar auditor, ruleset, prompts, rendering policy, scoring, prioritization e template do relatório.

### NFR-GEO-008
Falhas localizadas não devem encerrar toda auditoria quando for possível continuar.

### NFR-GEO-009
Dados permanecem locais, exceto conteúdo explicitamente enviado a provider configurado.

### NFR-GEO-010
Resultado com cobertura/confiabilidade insuficiente não pode ser apresentado como conclusivo.
