# M16 — Root Cause + Element-Level Remediation

**Status:** PLANNED AFTER OPENAI HOTFIX  
**Baseline de entrada:** M15 + OpenAI provider hardening integrado em `main`

Este arquivo reserva o escopo do próximo marco para impedir mistura acidental com o hotfix de IA. A implementação completa deve ocorrer em branch própria criada após o merge do hotfix.

Objetivo: elevar a remediação de finding/regra para diagnóstico técnico por ocorrência, com causa raiz evidence-backed, elementos afetados, selector quando determinável, HTML observado quando persistido, mudança exata, exemplo pós-correção, critérios de aceite e revalidação.

Invariantes: não inventar selector, HTML observado, causa raiz, conteúdo, canonical, dados estruturados ou fatos; propriedades de documento/conjunto de nós podem ter múltiplos elementos e selector único `NÃO DETERMINADO`; M16 não altera `SCORE-GEO-001`, Business Rules ou actionability.
