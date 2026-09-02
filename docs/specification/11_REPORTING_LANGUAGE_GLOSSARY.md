# REPORTING_LANGUAGE_GLOSSARY.md

**Status:** APPROVED — extended by M13 Actionable GEO Report

## 1. Regra editorial

O relatório destinado ao usuário deverá ser prioritariamente em português.

Inglês somente quando:

- nome técnico é consagrado;
- nome oficial não deve ser traduzido;
- tradução poderia reduzir precisão;
- valor deriva diretamente de protocolo/HTML/API.

O usuário deve descobrir o resultado executivo antes de metodologia detalhada.

## 2. Tradução da interface

Overall Readiness
→ Compatibilidade GEO

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

Remediation Recipe
→ Receita de Remediação / Remediation Recipe

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

## 3. Estado geral quando Overall não é consolidável

Quando `OVERALL_READINESS` não possuir valor consolidado, o relatório deve usar explicitamente:

```text
COMPATIBILIDADE GEO
NÃO DETERMINADA
```

Não usar somente `—` como estado principal.

Não apresentar Coverage como substituto de Compatibilidade GEO.

`NÃO DETERMINADA` significa informação insuficiente para conclusão geral; não equivale a zero, FAIL ou resultado crítico.

## 4. Semântica visual

Cores de referência:

- sucesso / aprovado / resultado forte: verde (`#16803C`);
- atenção: amarelo (`#D99A00`);
- problema relevante: laranja (`#D65A00`);
- erro / crítico: vermelho (`#C62828`);
- não determinado / informação insuficiente: cinza (`#667085`);
- informação metodológica: azul (`#2563EB`).

Todo estado visual deve incluir texto. Cor isolada nunca é suficiente.

Estados textuais possíveis incluem:

- APROVADO;
- ALERTA;
- PROBLEMA;
- CRÍTICO;
- PARCIAL;
- NÃO DETERMINADO;
- NÃO CONSOLIDADO.

## 5. Classificação textual de score válido

| Faixa | Termo |
|---:|---|
| 90–100 | Excelente |
| 75–89 | Alta |
| 60–74 | Moderada |
| 40–59 | Baixa |
| 0–39 | Crítica |
| sem resultado válido | Não Determinada |

A cor do resultado geral deve respeitar também Consolidation. Um valor não consolidável não deve receber apresentação de resultado geral válido.

## 6. Termos técnicos preservados

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

## 7. Seção de interpretação

Título deve incluir:

`Como interpretar este relatório`

Deve explicar separadamente:

### Compatibilidade GEO

Quão preparado está o site segundo score consolidado.

### Cobertura da Análise

Quanto do universo aplicável pôde ser efetivamente analisado.

Baixa Coverage não significa necessariamente baixa qualidade do site.

### Confiabilidade

Grau de segurança da conclusão com base em evidence, método e limitações.

### Consolidado

Há cobertura e confiabilidade suficientes para apresentar o resultado como consolidado.

### Parcial

Parte relevante da avaliação está disponível, mas existem limitações.

### Não Consolidado / Não Determinado

Não há base suficiente para apresentar conclusão agregada. O estado não é score zero.

### Severidade

Gravidade intrínseca do problema.

### Prioridade

Ordem recomendada de ação considerando gravidade, impacto, confiabilidade e facilidade.

### Desktop e Mobile

São contextos independentes e podem apresentar resultados diferentes.

## 8. Linguagem de remediação

Correções detalhadas devem preferir a sequência:

```text
Página
Dispositivo
Regra
Severidade
Prioridade
Categoria GEO
Alvo / elemento / local
Problema encontrado
Valor observado
Correção recomendada
Critério de aceite
Como revalidar
Evidências
```

Quando o trecho HTML original não estiver persistido:

`Trecho HTML original não persistido para esta evidência.`

Quando houver código recomendado, rotular:

`Estrutura recomendada (exemplo)`

Nunca rotular exemplo como HTML observado.

Fallback deve ser explicitamente identificado como `FALLBACK DE REMEDIAÇÃO` ou equivalente.

## 9. Disclaimer de IA

Quando não houver IA:

`Algumas avaliações semânticas não foram executadas porque não havia um provedor de inteligência artificial disponível ou configurado. Essa limitação reduz a cobertura da auditoria e não representa um problema do website analisado.`

Quando IA externa for usada, o relatório deve indicar que análises semânticas utilizaram provider externo, sem revelar credenciais.

O relatório não deve sugerir que a IA “deu a nota GEO”; score oficial continua determinístico.

## 10. Restrições

Nunca usar linguagem que prometa:

- ranking;
- citação;
- visibilidade;
- presença em mecanismo generativo.

Nunca recomendar ou afirmar sem base:

- canonical preferencial;
- remoção de noindex;
- structured data incompatível;
- autoria;
- data de atualização;
- fonte;
- claim factual;
- informação comercial.

O produto mede readiness e oferece remediação evidence-backed.
