# M18 — Multi-AI Provider Abstraction, Reliability Routing & Usage Telemetry

M18 é uma extensão aditiva de infraestrutura de IA. Não altera Business Rules, SCORE-GEO-001, PRIORITY-GEO-001, actionability, Desktop/Mobile ou UNKNOWN.

## Providers e contrato
Runtime aprovado: OPENAI, DEEPSEEK, MIMO, NONE. GitHub Copilot não é SemanticProvider. Todos os adapters produzem contrato normalizado e a aceitação exige exatamente as 22 BR-GEO semânticas, sem regra ausente/duplicada/desconhecida, enums válidos e evidence_ids existentes. HTTP 200 ou JSON parseável isoladamente não significam AVAILABLE.

## Routing default
1. OPENAI/gpt-5.6-sol HIGH/XHIGH QUALIFIED-A+
2. OPENAI/gpt-5.6-terra HIGH QUALIFIED-A
3. DEEPSEEK/deepseek-v4-pro HIGH PROVISIONAL-A-
4. MIMO/mimo-v2.5-pro THINKING_ENABLED PROVISIONAL-B+
5. OPENAI/gpt-5.6-luna HIGH QUALIFIED-B+
6. DEEPSEEK/deepseek-v4-flash HIGH PROVISIONAL-B
7. MIMO/mimo-v2.5 THINKING_ENABLED PROVISIONAL-B

A classificação é política inicial SearchGEO, não benchmark científico. DeepSeek/MiMo só deixam PROVISIONAL após benchmark específico com rule agreement, evidence fidelity, completeness, schema compliance, hallucination rate, repeatability, UNKNOWN discipline, PT-BR, entity/intent accuracy e operational success rate. Estrutura prevê qualification/version/reliability score.

## Failover e URL lock
AUTO detecta somente keys presentes e configuração válida, ordena a cadeia uma vez no início e não reintroduz provider quarantined. Falha antes de resultado válido permite fallback na mesma URL. O primeiro resultado válido fixa PINNED_TO_URL; demais devices usam esse provider. Se o pinned falhar no outro device, não há provider alternativo para aquela URL; a lacuna é DEGRADED/UNKNOWN e o provider é quarantined para próximas URLs. Provider explícito nunca faz failover cruzado.

## Telemetria e custo
`ai_provider_attempts` registra tentativa, URL/device, provider/model/depth/rank, timestamps/duração, status, diagnóstico sanitizado, usage reportado, ESTIMATED_COST, pricing version, summary bounded, hash e semantic contract version. Nunca persistir secret, Authorization, corpo sensível integral ou chain-of-thought. Tokens ausentes ficam NULL. Custo usa catálogo local versionado e nunca billing externo nem score.

## Reporting
report.html distingue habilitado/configurado/tentado/sucesso, estratégia, provider inicial/efetivo, modelo/depth/status/failover e tabela de uso. remediation.html contém somente contexto operacional, nunca finding/recommendation por falha da IA. Chain exhausted adiciona `AI_PROVIDER_CHAIN_EXHAUSTED`, mantém determinísticas e UNKNOWN para dependências semânticas, sem penalidade de score.
