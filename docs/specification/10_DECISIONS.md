# DECISIONS.md

**Status:** CURRENT

## DECIDED

### D-001
Desktop e Mobile serão avaliados separadamente.

### D-002
Relatório oficial será HTML estruturado e profissional.

### D-003
Testes mínimos orientados a risco.

### D-004
Decisão original: GitHub somente após baseline local estável.

Status: **SUPERSEDED por D-032**.

### D-005
Uma máquina e um operador humano no MVP.

### D-006
Arquitetura distribuída não é requisito inicial.

### D-007
Multiusuário não é requisito inicial.

### D-008
As 10 dimensões permanecem no MVP.

### D-009
Existirá Overall Readiness separado para Desktop e Mobile, somente quando consolidável.

### D-010
`max_pages` padrão = 100, configurável.

### D-011
Intent analysis entra no MVP de forma controlada: 1 primary + até 5 secondary intents.

### D-012
Benchmark de concorrentes fica para V1.

### D-013
Interface inicial será CLI, não aplicação web.

### D-014
Rendering baseline será Playwright + Chromium.

### D-015
Organização conceitual/física: Audit → Page → Device Context. Dados estruturados em SQLite embarcado; artefatos grandes em filesystem.

### D-016
Nenhum database server ou serviço externo de banco será obrigatório.

### D-017
IA é opcional. Auditor deve funcionar sem provider.

### D-018
Resultados relevantes devem informar Coverage, Confidence e Consolidation Status.

### D-019
Ausência de IA nunca representa baixa qualidade do website.

### D-020
Camada semântica será independente de fornecedor/modelo.

### D-021
MVP implementará NoneProvider e pelo menos um provider real; baseline real inicial: OpenAI.

### D-022
Score oficial deve conter Value, Coverage, Confidence e Consolidation.

### D-023
Ausência de IA reduz cobertura/consolidação, nunca score do website diretamente.

### D-024
Pesos iguais entre dimensões no MVP.

### D-025
Scoring groups impedem dupla penalização de causa correlacionada.

### D-026
Na máquina de desenvolvimento/MVP, uso de API externa de IA é permitido.

### D-027
OpenAI é o provider inicial previsto para o MVP, sem dependência arquitetural.

### D-030
Relatório destinado ao usuário será prioritariamente em português.

### D-031
Termos técnicos oficiais podem permanecer em inglês quando tradução reduzir precisão; glossário/contexto são obrigatórios.

### D-032
Git/GitHub são adotados a partir do M0 como controle de versão e repositório de desenvolvimento.

Essa adoção não altera o requisito de execução local e não torna GitHub dependência de runtime do produto.

### D-033
Quando um escopo ou marco implementado em branch estiver encerrado, validado e aprovado para integração, todo o conteúdo validado deve ser integrado em `main`.

Após o merge, deve-se confirmar que `main` contém integralmente o resultado aprovado e que a branch de trabalho não possui conteúdo exclusivo pendente.

A regra anterior de contingência que permitia manter branch sincronizada com `main` quando a ferramenta não pudesse removê-la foi **SUPERSEDED por D-035**.

### D-034
Após um marco ser implementado, validado, comparado com seus critérios, integrado integralmente em `main` e encerrado sem pendências bloqueantes, fica autorizado o avanço automático ao marco seguinte previsto em `09_IMPLEMENTATION_PLAN.md`, sem necessidade de nova aprovação humana.

Cada marco continua sendo unidade independente de implementação, validação, branch, PR, merge e encerramento.

O avanço automático deve interromper somente diante de conflito normativo não solucionável pela precedência documental, impossibilidade técnica relevante, alteração material de escopo ou comportamento funcional, falha persistente de validação obrigatória, necessidade de credencial/segredo indisponível, ação externa indispensável que a ferramenta não possa executar, impacto de política corporativa ou outra decisão/ação que dependa necessariamente de humano.

Problemas técnicos ordinários e solucionáveis não constituem motivo para solicitar aprovação humana. A execução deve diagnosticar, corrigir, revalidar e continuar automaticamente quando possível.

Nenhum marco pode ser considerado concluído apenas para permitir avanço. Todos os respectivos critérios e gates obrigatórios permanecem válidos.

### D-035
Toda branch criada especificamente para implementação de um marco ou alteração de governança é temporária.

Após o merge em `main`, é obrigatório:

1. confirmar que o merge foi concluído;
2. confirmar que `main` contém integralmente todo o conteúdo aprovado;
3. comparar a branch com `main`;
4. confirmar que a branch não contém commits, arquivos ou alterações exclusivas pendentes;
5. excluir a branch remota do GitHub;
6. quando aplicável, excluir também a branch local;
7. somente então considerar concluída a limpeza Git do marco ou alteração de governança.

Uma branch já integrada em `main` não deve permanecer existente apenas por estar sincronizada. O estado `identical / 0 ahead / 0 behind` comprova que a exclusão é segura, mas não constitui estado final aceitável.

Sincronizar a branch com `main` após o merge não substitui sua exclusão.

Se a ferramenta utilizada não permitir excluir a branch remota, deve-se registrar explicitamente a limitação e informar a ação manual necessária. Enquanto a branch permanecer existente, a limpeza Git fica pendente e o ciclo Git não pode ser apresentado como completamente encerrado.

A pendência de limpeza não invalida o código já integrado em `main`. Porém, quando a conclusão integral do marco ou da alteração de governança for gate para avanço em cascata, a execução deve interromper até que a exclusão obrigatória seja realizada e confirmada.

Nenhuma branch de marco encerrado deve permanecer no repositório, salvo exceção futura explicitamente justificada e documentada.

## PENDING ENVIRONMENT VALIDATION

### D-028
Verificar acesso técnico à API OpenAI na máquina/rede corporativa.

Validar:

- DNS;
- TLS;
- proxy;
- firewall;
- endpoint API;
- authentication;
- timeout;
- políticas de saída.

Acessibilidade técnica não significa autorização corporativa.

## PENDING CORPORATE VALIDATION

### D-029
Identificar provider de IA permitido/preferido corporativamente.

Possibilidades arquiteturais:

- OpenAI;
- Azure OpenAI;
- Google;
- Anthropic;
- AWS Bedrock;
- modelo local;
- nenhum.

Também validar corporativamente:

- autorização para envio de conteúdo a IA externa;
- execução de Chromium/browser;
- executável portátil;
- escrita em filesystem;
- SQLite embarcado;
- antivírus/EDR;
- políticas de execução.

Essas pendências não bloqueiam desenvolvimento local do MVP.

## Restrições aprovadas adicionais

- aplicação local Windows;
- não web;
- sem Docker obrigatório;
- sem admin como objetivo de distribuição;
- relatório estático;
- SQLite não é considerado dependência de database server;
- RAW + RENDERED sempre preservados no baseline;
- arquitetura do site não gera penalidade por si só;
- `llms.txt` não impacta score automaticamente;
- GPTBot e OAI-SearchBot possuem papéis distintos;
- findings devem ser evidence-backed;
- LLM nunca é scoring engine;
- cascading failures devem ser controladas.
