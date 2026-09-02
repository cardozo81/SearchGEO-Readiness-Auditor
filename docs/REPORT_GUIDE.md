# Guia do Relatório

O `report.html` é um relatório HTML5 estático e autocontido, gerado a partir do estado persistido da auditoria. Ele é uma **projeção para leitura humana**; a fonte primária continua sendo `audit.db` + artifacts.

## Como abrir

No Windows:

```powershell
Start-Process .\audits\AUD-...\report.html
```

Não é necessário web server nem acesso à internet para abrir o arquivo gerado.

## Resumo

O topo identifica projeto, auditoria, quantidade de páginas, findings e recomendações e inclui o disclaimer de finalidade.

A ferramenta mede **Search/GEO Readiness**. O resultado não garante:

- ranking;
- tráfego orgânico;
- citação por um sistema generativo;
- inclusão em respostas de IA;
- visibilidade ou presença em mecanismo generativo.

## Desktop e Mobile

Desktop e Mobile são contextos independentes desde o rendering até o scoring. O relatório não deve ser lido como um único score indiferenciado.

Uma diferença entre dispositivos não é automaticamente um defeito. `BR-GEO-052` classifica a diferença e só produz finding quando a implementação a considera materialmente problemática e evidence-backed.

## Scorecards e 10 dimensões

A baseline usa:

1. Acessibilidade Técnica;
2. Capacidade de Indexação;
3. Extração de Conteúdo;
4. Estrutura Semântica;
5. Clareza de Entidades;
6. Dados Estruturados;
7. Capacidade de Resposta;
8. Preparação para Citação;
9. Evidências e Confiabilidade;
10. Cobertura de Intenções.

Cada dispositivo possui score por dimensão e, quando todas as condições forem satisfeitas, `Overall Readiness`.

## Overall

`Overall` só recebe valor quando as 10 dimensões necessárias possuem valor e não estão `NOT_CONSOLIDATED`. A implementação calcula a média simples das 10 dimensões.

Se uma dimensão necessária não puder ser consolidada, o Overall permanece sem valor consolidado. Isso evita transformar ausência de observação em uma nota artificialmente baixa.

## Coverage

Coverage representa quanto do peso aplicável foi efetivamente avaliado por resultados de qualidade (`PASS`, `WARNING`, `FAIL`).

- `UNKNOWN` não entra como falha;
- `ERROR` não entra como falha;
- `NOT_APPLICABLE` é removido do universo aplicável;
- baixa Coverage limita a confiança/consolidação.

Coverage é sobre **capacidade de avaliar**, não sobre qualidade do website.

## Confidence

Na implementação atual:

- `HIGH`: Coverage >= 90%, evidências completas e nenhum ERROR;
- `MEDIUM`: Coverage >= 80% e nenhum ERROR;
- `LOW`: demais casos com alguma Coverage;
- `UNAVAILABLE`: Coverage zero.

Não confundir Confidence do score com confiança de uma inferência semântica individual.

## Consolidation Status

- `CONSOLIDATED`: Coverage >= 80% com Confidence HIGH ou MEDIUM;
- `PARTIAL`: existe informação útil, mas o gate de consolidação completa não foi atingido;
- `NOT_CONSOLIDATED`: Coverage < 50% ou Confidence indisponível.

## Resultados das regras

| Resultado | Interpretação |
|---|---|
| `PASS` | condição esperada comprovada no escopo avaliado |
| `FAIL` | problema comprovado conforme regra e evidência |
| `WARNING` | condição de atenção/materialidade limitada, conforme regra |
| `UNKNOWN` | evidência/capacidade insuficiente para concluir |
| `NOT_APPLICABLE` | regra não se aplica ou foi bloqueada por dependência |
| `ERROR` | erro na execução da análise; não é FAIL do site |

## Findings

Finding é um problema/alerta publicado pela pipeline e deve estar ligado a:

- `rule_id`;
- `RuleExecution`;
- uma ou mais `Evidence`;
- página/dispositivo quando aplicável;
- severity;
- observed value;
- expected condition.

A política geral é não criar finding para simples ausência de capacidade de análise. `UNKNOWN` e `ERROR` não devem ser transformados mecanicamente em problema do site.

## Evidence

Evidence registra o que foi observado e de onde veio. Pode referenciar:

- resposta/headers HTTP;
- robots/sitemap;
- DOM/HTML/meta/canonical/headings/links;
- Dados Estruturados;
- conteúdo principal;
- análise semântica aceita;
- comparação Desktop/Mobile;
- artifact persistido.

Use o ID e o `artifact_reference` para rastrear um finding até a fonte técnica.

## Severity

Severidade do finding:

- `CRITICAL`;
- `HIGH`;
- `MEDIUM`;
- `LOW`;
- `INFO`.

Severity expressa gravidade do problema identificado; não é a mesma coisa que Priority.

## Impact, Effort e Priority

A priorização M10 combina quatro componentes:

- Severity — 45%;
- Impact — 30%;
- Confidence — 15%;
- Ease — 10% (derivada de Effort).

Classes:

- `P0`: reservado a caso crítico/blocker técnico material;
- `P1`: prioridade muito alta;
- `P2`: alta;
- `P3`: média;
- `P4`: baixa;
- `INFO`: informacional.

Priority não altera o score de qualidade calculado pelo M9.

## Remediation Groups

Findings são consolidados por regra + causa determinística. Um Remediation Group pode reunir várias páginas/dispositivos afetados e receber uma única recomendação operacional.

O objetivo é evitar uma lista repetitiva de correções iguais.

## Recommendations

As recomendações da baseline são geradas por templates determinísticos conforme categoria/root cause. Elas incluem impacto, esforço, confiança e prioridade, e apontam para o Remediation Group correspondente.

São orientação de remediação, não garantia de resultado externo após a implementação.

## FULL, DEGRADED e NO_AI

### FULL

Provider semântico disponível e respostas válidas para o universo aplicável. Isso não significa Coverage 100% obrigatoriamente: outras limitações técnicas ainda podem existir.

### DEGRADED

O provider foi selecionado, mas alguma análise semântica ficou indisponível/inválida em parte do universo. Saídas inválidas, schema incorreto ou evidence IDs inventados são descartados.

### NO_AI

IA não configurada. O auditor continua com análise determinística/heurística. Regras semantic-only podem ficar `UNKNOWN`.

**NO_AI não significa baixa qualidade do site.**

## Limitações

A seção de reliability/limitações pode incluir, entre outros:

- `MAX_PAGES_REACHED:...`;
- rules em `UNKNOWN`/`ERROR` refletidas no score;
- ausência de IA;
- dimensões não consolidadas;
- falhas técnicas localizadas.

Leia limitações antes de interpretar qualquer score isoladamente.

## Glossário essencial

- **RAW**: resposta HTTP preservada antes de rendering JavaScript.
- **RENDERED**: DOM/HTML após execução no Chromium.
- **Evidence First**: conclusão precisa apontar para observação rastreável.
- **Readiness**: condição técnica/semântica para acesso, compreensão e reutilização; não resultado de ranking.
- **Coverage**: proporção do universo aplicável efetivamente avaliado.
- **Confidence**: confiança operacional do score a partir de Coverage/evidência/erros.
- **Consolidation**: estado que determina se o score possui base suficiente para uso agregado.
