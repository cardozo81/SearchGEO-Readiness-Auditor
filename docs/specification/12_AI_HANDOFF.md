# AI_HANDOFF.md

## 1. Objetivo do produto

Construir um auditor local de Search/GEO Readiness baseado em evidence, regras reproduzíveis e análise semântica opcional.

## 2. Fonte de verdade

Leia primeiro:

`00_SPEC_INDEX.md`

Depois siga a ordem obrigatória indicada nele.

Não derive requisitos do histórico de chats quando houver definição normativa nestes arquivos.

## 3. Estado atual

A especificação funcional, Domain Model, Business Rules, Workflows, Scoring, Prioritization, Technical Architecture e Implementation Plan constituem baseline aprovada conforme seus respectivos documentos.

O estado real de implementação não deve ser inferido de texto histórico deste handoff.

Antes de qualquer novo trabalho:

1. confirme o HEAD corrente de `main`;
2. confirme os marcos efetivamente integrados em `main` por commits e PRs merged;
3. confirme que não existe branch ou PR de marco anterior com conteúdo exclusivo pendente;
4. derive o próximo marco exclusivamente de `09_IMPLEMENTATION_PLAN.md` e do estado confirmado de `main`.

`main` é a referência operacional para determinar o que está efetivamente integrado.

## 4. Execução dos marcos

Os marcos e sua ordem são definidos em `09_IMPLEMENTATION_PLAN.md`.

Cada marco continua sendo unidade independente de implementação, validação, branch, PR, merge e confirmação pós-merge.

O avanço automático ao marco seguinte é permitido somente depois de todos os gates funcionais e de integração do marco anterior terem sido satisfeitos, conforme D-034.

Durante a cascata M4 → M12, a branch encerrada deve ser comparada com `main`, confirmada sem conteúdo exclusivo e registrada na lista acumulada de exclusão manual conforme D-036. A exclusão física diferida não bloqueia o avanço.

Nenhum marco pode ser considerado concluído apenas para permitir avanço.

Bloqueio real interrompe a cascata antes de iniciar o marco seguinte.

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
- pequenas bibliotecas compatíveis;
- refactors sem impacto funcional;
- organização de arquivos sem alteração de contrato;
- fixtures e ajustes de testes orientados a risco;
- erros de programação ordinários e solucionáveis.

Escolha a solução técnica mais simples compatível com a baseline, corrija falhas solucionáveis, revalide e continue.

## 7. Interromper somente diante de blocker real

A execução deve interromper quando houver pelo menos uma condição que dependa necessariamente de decisão ou ação humana, incluindo:

1. conflito normativo real não solucionável pela precedência documental;
2. impossibilidade técnica material após investigação;
3. alteração necessária de escopo ou comportamento funcional aprovado;
4. mudança material em scoring, priorização ou interpretação oficial;
5. política ou autorização corporativa necessária;
6. credencial, segredo ou acesso externo indispensável e indisponível;
7. ação externa obrigatória que a ferramenta disponível não consiga executar, exceto exclusão física diferida de branches coberta por D-036;
8. falha persistente de validação obrigatória após diagnóstico e tentativas razoáveis de correção;
9. inconsistência de `main` que torne inseguro continuar;
10. risco de operação destrutiva não previamente autorizada;
11. qualquer decisão que a própria baseline determine explicitamente ser humana.

Problemas técnicos ordinários e solucionáveis não constituem blocker.

## 8. Pendências humanas de ambiente/corporativas

Permanecem sujeitas às decisões D-028 e D-029, entre elas:

- acesso técnico à OpenAI;
- autorização corporativa de IA externa;
- provider permitido;
- execução de browser/Chromium;
- distribuição portátil;
- filesystem;
- SQLite;
- EDR/políticas.

Essas pendências não bloqueiam automaticamente o desenvolvimento local. Tornam-se blocker somente quando impedirem um gate obrigatório do marco em execução.
