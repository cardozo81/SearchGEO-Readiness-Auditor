# Guia do Relatório

O `report.html` é um relatório HTML5 estático, responsivo, imprimível e autocontido, gerado exclusivamente a partir do estado persistido da auditoria. Ele é uma **projeção para leitura humana**; a fonte primária continua sendo `audit.db` + artifacts.

## Como abrir

No Windows:

```powershell
Start-Process .\audits\AUD-...\report.html
```

Não é necessário web server, CDN, fonte remota ou acesso à internet para abrir o arquivo gerado.

# Como ler o resultado em poucos segundos

O topo do relatório responde primeiro ao estado de readiness. A ordem executiva é:

1. Compatibilidade GEO geral por dispositivo;
2. Cobertura e confiabilidade;
3. principais oportunidades;
4. score Desktop;
5. score Mobile;
6. plano de correção;
7. correções detalhadas;
8. análises semânticas;
9. crawl e limitações;
10. metodologia e glossário.

A ferramenta mede **Search/GEO Readiness**. O resultado não garante ranking, tráfego, citação por sistemas generativos, inclusão em respostas de IA ou visibilidade externa.

## Três conceitos que não devem ser confundidos

### Compatibilidade GEO

Responde: **quão preparado está o site?**

É o `OVERALL_READINESS` do dispositivo quando o score está efetivamente `CONSOLIDATED`.

### Cobertura da análise

Responde: **quanto do universo aplicável foi efetivamente avaliado?**

Coverage baixa reduz a capacidade de concluir, mas **não significa que o website tenha qualidade baixa**.

### Confiabilidade

Responde: **quanto podemos confiar na conclusão apresentada?**

Considera coverage, evidência, erros de execução e capacidade analítica disponível.

## NÃO DETERMINADO

Quando não existe base suficiente para consolidar `OVERALL_READINESS`, o relatório mostra explicitamente:

```text
COMPATIBILIDADE GEO
NÃO DETERMINADA
```

Isso significa **informação insuficiente para uma conclusão geral**. Não significa nota zero, `FAIL` ou baixa qualidade do website.

O relatório nunca apresenta Coverage, por exemplo `27%`, como se fosse a nota GEO.

## Classificação visual de scores válidos

| Score válido | Classificação | Semântica visual |
|---:|---|---|
| 90–100 | Excelente | sucesso / verde |
| 75–89 | Alta | sucesso / verde |
| 60–74 | Moderada | atenção / amarelo |
| 40–59 | Baixa | problema / laranja |
| 0–39 | Crítica | crítico / vermelho |
| sem score consolidado | Não Determinada | informação insuficiente / cinza |

As cores são sempre acompanhadas por texto. Informação metodológica utiliza azul.

## Desktop e Mobile

Desktop e Mobile permanecem independentes desde rendering até scoring. Não existe média artificial entre dispositivos.

É possível, por exemplo, haver:

```text
Desktop: 82 / Alta / Consolidado
Mobile: NÃO DETERMINADA
```

Isso não autoriza inferir uma nota combinada.

# Scorecard

A baseline utiliza dez dimensões:

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

Cada linha mostra separadamente:

- score ou `NÃO DETERMINADO`;
- classificação textual;
- Coverage;
- Confidence;
- Consolidation Status.

`UNKNOWN`, `ERROR` e `NOT_APPLICABLE` não são convertidos em `FAIL`.

# Principais oportunidades

A seção **Principais oportunidades de melhoria** é derivada somente de findings realmente persistidos e priorizados.

Uma dimensão apenas `UNKNOWN` não gera problema fictício.

A tabela resume:

- prioridade;
- área GEO;
- resultado conhecido para o dispositivo aplicável;
- problema principal.

# Actionable remediation

A evolução `REPORT-GEO-002` transforma o fluxo em:

```text
Evidence
  -> RuleExecution
  -> Finding
  -> Priority
  -> Remediation Recipe
  -> Recommendation
  -> Actionable Report
```

## Remediation Recipe

Uma recipe determinística por `rule_id` pode informar:

- alvo técnico;
- elemento HTML;
- localização estrutural;
- tipo de ação;
- descrição da correção;
- exemplo técnico, quando seguro;
- critérios de aceite;
- como revalidar;
- decisão humana obrigatória, quando aplicável.

Recipes não alteram score nem severity. Elas explicam como tratar um finding já evidence-backed.

Regras sem recipe específica usam fallback claramente identificado.

## Exemplo: canonical ausente

Para `BR-GEO-013`, o relatório pode indicar:

```html
<link rel="canonical">
```

Local esperado:

```text
<head>
```

Se a canonical estiver ausente, o relatório explica que a equipe precisa definir qual URL é realmente preferencial antes de preencher o `href`.

Um exemplo estrutural pode ser mostrado como:

```html
<head>
  ...
  <link rel="canonical" href="https://URL-PREFERENCIAL.example/...">
</head>
```

O placeholder **não é uma canonical inferida pelo auditor**.

Critérios típicos incluem:

- no máximo uma canonical efetiva quando aplicável;
- URL absoluta e tecnicamente válida;
- ausência de conflito;
- destino coerente com a URL preferencial aprovada;
- revalidação pelas regras relacionadas.

## HTML observado versus exemplo recomendado

Esses conceitos são deliberadamente separados.

Quando a evidência do finding não persiste o trecho HTML original, o relatório mostra:

```text
Trecho HTML original não persistido para esta evidência.
```

Depois, quando seguro, apresenta uma **Estrutura recomendada (exemplo)**.

O relatório não reconstrói nem fabrica HTML como se tivesse sido capturado.

# Recomendações semânticas e de conteúdo

Quando M7 possui resultados persistidos, o relatório reutiliza:

- `reasoning_summary`;
- `evidence_ids`;
- entidades;
- intenção primária;
- intenções secundárias;
- assessments de estrutura semântica;
- answerability;
- citation readiness;
- evidence/trust;
- intent coverage.

Não existe segunda chamada livre de IA para “embelezar” o texto do relatório.

Exemplos semânticos são estruturais e não podem inventar:

- claims;
- preços;
- coberturas comerciais;
- datas;
- autor;
- fontes;
- condições de produto;
- fatos não sustentados.

Quando uma correção depende de decisão editorial, jurídica ou de negócio, o relatório a identifica como decisão humana.

# Uso de IA

## FULL

Provider semântico disponível e respostas válidas para o universo aplicável. Isso não implica Coverage 100% obrigatoriamente.

## DEGRADED

Parte da análise semântica ficou indisponível ou foi rejeitada. Saídas inválidas, schema incompatível ou evidence IDs inventados não viram defeito do website.

## NO_AI

A auditoria continua com regras determinísticas e heurísticas seguras. Regras semantic-only podem ficar `UNKNOWN`.

**NO_AI não reduz o score de qualidade atribuído ao website.** Pode reduzir Coverage, Confidence, Consolidation e impedir `OVERALL_READINESS`.

# Cobertura do Crawl

A seção **Cobertura do Crawl** é reconstruída do estado persistido, sem depender do objeto M2 em memória.

Ela apresenta, quando disponível:

- URLs descobertas;
- URLs auditadas;
- `max_pages`;
- se o limite foi atingido;
- fontes de descoberta por seed, sitemap, links internos e redirects;
- estado de `robots.txt`;
- sitemaps declarados;
- estado dos recursos de sitemap;
- redirects observados;
- diagnóstico de possível limitação de descoberta.

Quando `MAX_PAGES_REACHED:discovered=N;audited=M` está persistido, os números são reutilizados diretamente.

Quando o limite não foi atingido, todas as URLs candidatas elegíveis foram selecionadas pelo M2, portanto o número de páginas persistidas representa o universo descoberto daquela execução.

# Evidence e rastreabilidade

Cada correção detalhada preserva os IDs de evidência do finding. O desenvolvedor deve conseguir partir do report e rastrear:

```text
Página
-> dispositivo
-> rule_id
-> finding
-> observed value
-> evidence_id
-> remediation
-> aceite
-> revalidação
```

Evidence pode referenciar HTTP, headers, robots, sitemap, HTML/DOM, canonical, headings, links, Dados Estruturados, conteúdo principal, análise semântica ou comparação Desktop/Mobile.

# Priority

A priorização continua usando `PRIORITY-GEO-001`:

- Severity — 45%;
- Impact — 30%;
- Confidence — 15%;
- Ease — 10%.

Classes:

- `P0`: blocker crítico material;
- `P1`: prioridade muito alta;
- `P2`: alta;
- `P3`: média;
- `P4`: baixa;
- `INFO`: informacional.

Priority não altera score de qualidade.

# Limitações de segurança das sugestões

O relatório não deve recomendar mudanças apenas para aumentar score. Em particular:

- não escolhe canonical arbitrariamente;
- não remove `noindex` sem confirmar intenção;
- não cria structured data incompatível com conteúdo visível;
- não inventa autor;
- não inventa data de atualização;
- não inventa fonte;
- não inventa informação comercial;
- não recomenda conteúdo enganoso para sistemas de IA.

# Glossário essencial

- **RAW**: resposta HTTP preservada antes de rendering JavaScript.
- **RENDERED**: DOM/HTML após execução no Chromium.
- **Evidence First**: conclusão precisa apontar para observação rastreável.
- **Readiness**: condição técnica/semântica para acesso, compreensão e reutilização; não resultado de ranking.
- **Coverage**: proporção do universo aplicável efetivamente avaliado.
- **Confidence**: confiança operacional do score a partir de Coverage/evidência/erros.
- **Consolidation**: estado que determina se o score possui base suficiente para uso agregado.
- **Remediation Recipe**: receita determinística e rastreável associada à regra para orientar correção e aceite.
