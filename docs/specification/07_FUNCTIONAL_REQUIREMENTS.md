# FUNCTIONAL_REQUIREMENTS.md

**Status:** APPROVED — extended by M13 Actionable GEO Report

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

### FR-GEO-053
Exibir `COMPATIBILIDADE GEO: NÃO DETERMINADA` quando `OVERALL_READINESS` não possuir valor consolidado; nunca substituir o score por Coverage.

### FR-GEO-054
Exibir e explicar separadamente Compatibilidade GEO, Coverage e Confidence.

### FR-GEO-055
Aplicar classificação textual e semântica visual a scores válidos: 90–100 Excelente, 75–89 Alta, 60–74 Moderada, 40–59 Baixa, 0–39 Crítica; estado sem resultado válido permanece Não Determinado.

### FR-GEO-056
Produzir seção de principais oportunidades derivada somente de findings e prioridades persistidos, sem transformar UNKNOWN em problema.

### FR-GEO-057
Associar findings aplicáveis a `RemediationRecipe` determinística por `rule_id`, contendo alvo, ação, descrição, aceite e validação e, quando seguro, elemento/localização/exemplo.

### FR-GEO-058
Distinguir no relatório HTML efetivamente observado de exemplo recomendado. Se o trecho original não estiver persistido na Evidence, exibir explicitamente `Trecho HTML original não persistido para esta evidência.`

### FR-GEO-059
Para canonical ausente/conflitante, fornecer remediação acionável sem inventar URL preferencial. Quando a URL preferencial não for determinável pelas evidências, exigir decisão humana antes de preencher `href`.

### FR-GEO-060
Reutilizar SemanticAssessment, reasoning_summary, entidades, intents e evidence_ids persistidos para enriquecer remediação sem executar segunda chamada livre de IA.

### FR-GEO-061
Preservar segurança factual das recomendações: não inventar autor, fonte, freshness, claim, preço, cobertura comercial, structured data ou outra informação ausente das evidências.

### FR-GEO-062
Gerar diagnóstico de crawl reabrível a partir do estado persistido, incluindo URLs descobertas/auditadas, max_pages, limite atingido, fontes de descoberta, robots, sitemaps e redirects quando disponíveis.

### FR-GEO-063
Manter scorecard Desktop e Mobile independentes, exibindo por dimensão score, classificação, Coverage, Confidence e Consolidation.

### FR-GEO-064
Ordenar o relatório com resultado executivo antes de metodologia, seguido de oportunidades, scorecards e plano de correção.

### FR-GEO-065
Identificar explicitamente recipes de fallback quando ainda não houver recipe específica para uma regra.

### FR-GEO-066
Preservar IDs de Evidence e rastreabilidade no fluxo `evidence → finding → priority → remediation → report`.

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

### NFR-GEO-011
O relatório acionável deve permanecer autocontido, responsivo, imprimível e sem dependências externas obrigatórias.

### NFR-GEO-012
RemediationRecipe e apresentação do relatório devem ser determinísticas e reproduzíveis a partir do estado persistido e da versão do código/ruleset.
