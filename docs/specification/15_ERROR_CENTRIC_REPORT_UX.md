# ERROR_CENTRIC_REPORT_UX.md

**Status:** APPROVED — M15 historical contract evolved by REPORT-SITE-GEO-001

## 1. Objetivo

M15 introduziu uma visão orientada a problemas além da visão orientada a página. A evolução REPORT-SITE-GEO-001 preserva o princípio de separação por domínio, mas substitui o contrato público de dois HTMLs soltos por um mini-site estático.

## 2. Contrato final de saída

```text
<AUD-ID>/
├─ audit.db
├─ artifacts/
└─ report/
   ├─ index.html
   ├─ mobile.html          # quando aplicável
   ├─ desktop.html         # quando aplicável
   ├─ remediation.html
   ├─ ai-usage.html
   ├─ references.html
   └─ css/
      └─ site.css
```

`report.html` e `remediation.html` na raiz não são mais contrato público final. Podem existir apenas transitoriamente durante a orquestração interna M11/M18 e devem ser removidos após finalização bem-sucedida do report site.

## 3. Navegação

Todas as páginas finais devem compartilhar:

- mesma arquitetura de menu;
- mesmo stylesheet externo;
- mesma área estrutural de conteúdo;
- estados visuais semanticamente consistentes.

O menu deve conter apenas páginas materializadas. Ex.: `desktop.html` não deve aparecer em auditoria Mobile-only.

## 4. Visão geral

`index.html` é dashboard executivo.

Conteúdo prioritário:

- dispositivo(s) efetivamente auditado(s);
- Overall quando consolidado;
- Coverage;
- Confidence;
- Consolidation;
- dimensões;
- contagens acionáveis;
- ligação para domínios de detalhe.

Não deve concentrar toda evidência, telemetria e remediação em uma página longa.

## 5. Mobile e Desktop

Resultados por dispositivo ficam separados:

```text
mobile.html
desktop.html
```

Cada página pode conter:

- scorecard do dispositivo;
- dimensões;
- páginas auditadas;
- screenshots;
- findings aplicáveis;
- avaliações semânticas relevantes.

Resultados do outro dispositivo não devem ser misturados.

## 6. Remediation

`remediation.html` é a visão orientada a problema/causa.

Deve preservar:

- agrupamento global versus página quando aplicável;
- actionability;
- prioridade;
- causa raiz;
- reason code;
- elemento/selector observado;
- alvo técnico;
- observado vs esperado;
- mudança recomendada;
- critérios de aceite;
- revalidação;
- decisão humana quando necessária.

Detalhes extensos podem ser colapsados com HTML nativo (`details/summary`) para reduzir ruído sem perder rastreabilidade.

## 7. IA

Telemetria operacional não pertence à mesma hierarquia visual dos findings do site.

`ai-usage.html` deve conter provider/model/status/tokens/custo/duração/erro sanitizado.

Falha de IA não pode receber cor/mensagem de defeito do website.

## 8. Referências

`references.html` deve reunir:

- fontes primárias/standards;
- natureza da base de cada regra;
- fórmula de Score/Coverage/Confidence/Overall;
- avisos sobre heurísticas internas;
- distinção entre recomendações SearchGEO e requisitos oficiais.

## 9. Tipografia

Requisitos:

- evitar heading excessivamente grande;
- negrito reservado a hierarquia/estado/valor importante;
- tabelas com tipografia compacta;
- texto de leitura com line-height confortável;
- detalhes técnicos longos recolhidos quando adequado.

## 10. Cores

Estados determinantes devem usar semântica estável:

- positivo: verde;
- atenção/parcial: âmbar;
- problema: vermelho;
- informação: azul;
- não determinado/indisponível: cinza.

Cor nunca substitui texto.

## 11. Layout

Desktop:

- navegação fixa;
- conteúdo deve descontar explicitamente a largura da navegação;
- tabelas largas usam overflow interno;
- nenhum bloco deve invadir a sidebar.

Mobile:

- navegação pode virar barra sticky/horizontal;
- conteúdo ocupa 100%;
- grids colapsam para uma coluna quando necessário.

## 12. CSS

Contrato final:

```text
report/css/site.css
```

Proibido no report site final:

- `<style>` duplicado em cada página;
- CSS estrutural inline;
- dependência de CDN obrigatória.

## 13. Score e reliability

A UI deve explicar:

- Score = qualidade observada na parcela avaliada;
- Coverage = quanto do universo aplicável foi avaliado;
- Confidence = força da conclusão;
- Consolidation = se o resultado é publicável como consolidado.

`Confidence LOW` não significa baixa qualidade textual e não autoriza ordem de reescrita sem finding específico.

## 14. Thresholds

As faixas visuais de score são internas ao SearchGEO. A UI/metodologia deve evitar linguagem que sugira certificação oficial GEO/AEO.

## 15. Fontes externas

A fundamentação atual deve reconhecer o guia do Google para recursos generativos de Search e não inventar requisitos especiais de GEO/AEO. Structured Data, chunking, `llms.txt` e escrita “para IA” não podem ser apresentados como requisitos universais quando a fonte oficial não os exige.

## 16. Fonte de verdade

O report site é projeção sobre dados persistidos. Não recalcula findings, scores, recommendations nem executa IA.
