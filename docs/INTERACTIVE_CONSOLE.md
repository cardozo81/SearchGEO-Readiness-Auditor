# Console interativo de execução

O SearchGEO mantém `searchgeo audit` como interface de linha de comando estável e oferece o console textual opcional:

```powershell
searchgeo-console
```

O console é uma camada de orquestração e segurança operacional. Ele não implementa um segundo pipeline: após o preflight, executa o mesmo `python -m searchgeo audit ...` do produto.

## Princípios

- uma tela lógica por vez; menus anteriores são limpos e não ficam empilhados;
- configuração explícita antes da execução;
- segredo nunca é exibido em claro;
- integração externa indisponível bloqueia a opção antes de executar;
- erro de provider não vira finding do website;
- Score, Coverage, Confidence, regras e persistência pertencem ao pipeline estável;
- custo prévio é indicador de exposição, não invoice;
- custo/tokens finais são derivados da telemetria persistida, sem inventar consumo.

## Provider registry canônico

A descoberta de providers do console é dinâmica e usa exclusivamente:

```text
src/searchgeo/provider_registry.py
```

O console não mantém uma lista independente de providers, modelos ou credenciais. O registry fornece:

- id canônico;
- nome de exibição;
- aliases;
- variável da API key;
- variável de modelo;
- variável de endpoint quando aplicável;
- variável e valores de reasoning quando aplicável;
- modelos suportados;
- modelo default;
- qualification;
- flag `explicit_only`;
- flag `auto_eligible`;
- restrições de formato de chave.

A ordem corrente de providers concretos é:

```text
openai
deepseek
mimo
xai
qwen
gemini
anthropic
```

O menu apresenta os ids canônicos. Os aliases continuam aceitos pela CLI, por exemplo:

```text
grok   -> xai
claude -> anthropic
```

Adicionar um provider ao registry, com adapter e contrato válidos, faz o console descobrir seus metadados sem exigir nova lista hardcoded em `interactive_console.py` ou `console_config.py`.

## Qualification e AUTO

A cadeia `AUTO` permanece homologada e deliberadamente restrita a:

```text
OpenAI -> DeepSeek -> MiMo
```

xAI, Qwen, Gemini e Anthropic permanecem:

```text
PROVISIONAL
explicit-only
auto_eligible = false
```

Enquanto estiverem nesse estado, configurar suas keys pode habilitar seleção explícita no console, mas nunca os inclui em `AUTO`.

A projeção de custo/volume de `AUTO` usa somente providers `auto_eligible`. Keys de providers PROVISIONAL não aumentam artificialmente o teto do `AUTO`.

## Credenciais e disponibilidade

`none` está sempre disponível.

Um provider explícito fica apto somente quando o registry e o ambiente indicam configuração válida:

1. API key correspondente presente;
2. formato de key compatível quando houver restrição;
3. modelo default/override pertencente ao catálogo do provider;
4. reasoning válido quando o adapter expõe essa configuração;
5. provider não bloqueado por quarantine da sessão.

Principais keys correntes:

| Provider | Variável |
|---|---|
| OpenAI | `OPENAI_API_KEY` |
| DeepSeek | `DEEPSEEK_API_KEY` |
| MiMo | `MIMO_API_KEY` |
| xAI | `XAI_API_KEY` |
| Qwen | `DASHSCOPE_API_KEY` |
| Gemini | `GEMINI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |

MiMo exige chave PAYG compatível com `sk-...`. Token Plan `tp-...` é tratado como indisponível pelo console e não deve ser enviado ao adapter.

Ausência de key resulta em opção indisponível no menu. O console não faz fallback silencioso de provider explícito.

## Variáveis de ambiente

O menu:

```text
E. Variáveis de ambiente
```

é gerado a partir das variáveis gerais do SearchGEO e das variáveis expostas pelo provider registry. Isso inclui automaticamente keys, model envs, endpoint envs e reasoning envs dos providers registrados.

Ações:

```text
S = setar/alterar
R = remover
H = ajuda/custo
V = voltar
```

Alterações valem somente para a sessão atual do console e subprocessos filhos. O console não grava permanentemente o perfil do Windows/PowerShell.

Variáveis sensíveis aparecem como:

```text
[SET]
```

Nunca como valor real.

A detecção de segredo cobre explicitamente as credenciais registradas e também nomes contendo `API_KEY`, `TOKEN`, `SECRET`, `PASSWORD` ou `CREDENTIAL`.

## Defaults

Na ausência de override:

```text
entrada            = URL única
device             = mobile
IA                 = none
remediação M20     = off
Web Performance    = off
max-pages          = 100
web max-pages      = 10
idioma             = pt-BR
mercado            = BR
audits root        = audits
```

## Menu principal

O menu contém:

```text
1. Entrada
2. Projeto
3. Dispositivo
4. IA
5. Remediação textual IA
6. Web Performance
7. max-pages
8. WebPerf max-pages
9. Idioma / mercado
10. Raiz auditorias

H. Ajuda / custos
E. Variáveis de ambiente
R. Executar [APTO|INDISPONÍVEL]
Q. Sair
```

Após uma auditoria desta sessão, também ficam disponíveis:

```text
P. Abrir pasta da auditoria
I. Abrir relatório HTML
```

Esses atalhos permanecem disponíveis ao voltar para o menu enquanto o `AUD-ID` da sessão estiver associado ao estado do console.

## Navegação em tela única

Ao entrar em configuração, provider, modelo, ajuda, variáveis ou ações pós-execução, o console limpa a tela anterior e redesenha o contexto atual. O objetivo é impedir o empilhamento de múltiplos menus no terminal.

Em saída não-TTY/testes, a interface não depende de ANSI para transmitir significado.

`NO_COLOR` remove coloração sem remover textos de status.

## Cores

Convenção operacional:

| Cor/ênfase | Significado |
|---|---|
| verde | pronto, sucesso, opção ativa/apta |
| amarelo | execução, atenção, custo estimado |
| vermelho | erro, bloqueio, indisponibilidade |
| magenta | API externa |
| ciano/azul | informação, dispositivo, integração/processamento local |
| dim/neutro | desligado, não configurado, secundário |

## Cabeçalho operacional

O cabeçalho acompanha:

- versão;
- status;
- URL corrente/mais recente;
- dispositivo;
- operação;
- ambiente relevante com segredos mascarados;
- início;
- fim;
- duração;
- erro operacional, quando houver.

Exemplo:

```text
====================================================================================================
SearchGEO Readiness Auditor | versão 0.1.0
Status      : ANALYZING
URL         : https://example.com/produto
Dispositivo : MOBILE
Operação    : API:OPENAI
Ambiente    : OPENAI_API_KEY=[SET]
Início      : 2026-09-04 08:00:00 -0300
Fim         : -
Duração     : 00:01:37
====================================================================================================
```

A duração usa relógio monotônico; início/fim usam timestamp local timezone-aware.

## Entrada URL e TXT

### URL única

Uma URL/domínio é seed de crawl. Antes da execução conhece-se uma página e o teto configurado:

```text
1 página conhecida -> teto max-pages
```

### TXT

O arquivo é UTF-8, uma URL/domínio por linha. Linhas vazias e comentários `#` são ignorados.

O preflight valida:

- arquivo existente;
- conteúdo UTF-8 legível;
- pelo menos um target;
- targets válidos;
- mesma origem normalizada;
- quantidade de URLs únicas menor ou igual a `max-pages`.

Para TXT, a quantidade exata de URLs únicas alimenta a projeção prévia.

## Dispositivo

Valores:

```text
mobile
desktop
both
```

`both` duplica contextos potenciais por página e é sinalizado como multiplicador de volume.

## Preflight

`R. Executar` somente inicia o subprocesso se toda a configuração estiver apta.

Entre os bloqueios:

- target ausente/inválido;
- TXT inexistente ou inválido;
- origens misturadas;
- `max-pages` insuficiente;
- provider inexistente ou indisponível;
- provider sem key;
- key incompatível;
- modelo inválido;
- reasoning inválido;
- `none` com remediação M20;
- `auto` com `--ai-model`;
- CrUX direto sem `SEARCHGEO_CRUX_API_KEY`;
- Chromium configurado em caminho inexistente.

Nenhum workspace deve ser criado por uma execução bloqueada no preflight.

## Remediação M20

M20 é opcional e pode acrescentar chamadas de IA para findings elegíveis.

Só pode ser ativado quando o provider selecionado está apto. Não altera Score, Coverage, Confidence, RuleExecution ou Finding.

O custo potencial de M20 aparece separadamente como incremento de exposição.

## Web Performance M21

M21 é integração externa independente de LLM.

O console mostra PageSpeed/CrUX como consumo de API/quota externa e não inventa preço monetário quando não existe base confiável persistida.

`field_source=crux` exige `SEARCHGEO_CRUX_API_KEY`.

## Exposição financeira antes da execução

A classificação é:

```text
NENHUM | BAIXO | MÉDIO | ALTO | EXCESSIVO
```

É uma heurística operacional, não previsão de invoice.

Entram na projeção:

1. quantidade conhecida/teto de páginas;
2. dispositivo;
3. provider explícito ou cadeia AUTO elegível;
4. modelo;
5. pricing catalogado quando disponível;
6. M20;
7. M21 e seus limites.

Para provider cujo modelo não possui linha no `PRICING_CATALOG`, o console informa explicitamente:

```text
preço unitário não catalogado; custo monetário prévio não estimável
```

Ele não transforma ausência de preço em custo zero.

Antes da execução, quantidades de tokens não são inventadas.

## AUTO e teto potencial

Em `AUTO`, o teto considera somente providers homologados e disponíveis da cadeia:

```text
OpenAI -> DeepSeek -> MiMo
```

O primeiro resultado válido encerra a cadeia naquele contexto. A projeção é conservadora porque falhas podem avançar para o provider seguinte.

Providers PROVISIONAL explicit-only não participam dessa conta.

## Quarantine

Quando a telemetria persistida indica:

```text
QUARANTINED_FOR_AUDIT
```

o console bloqueia novamente aquele provider durante a sessão e mostra um motivo sanitizado, como classe de erro/status HTTP.

Alterar/remover a credencial correspondente limpa o bloqueio transitório no estado do console para nova avaliação.

## Monitoramento da execução

O console observa o workspace produzido pelo pipeline:

```text
audit.db
logs/audit.log
```

Mapeamento operacional resumido:

```text
DISCOVERING / ACQUIRING -> INTEGRATION:HTTP
ANALYZING + IA           -> API:<provider efetivo>
ANALYZING sem IA         -> LOCAL:SEMANTIC_RULES
COMPARING / SCORING      -> LOCAL:RULES/SCORE
REPORTING                -> LOCAL:REPORT
M21                      -> API:PAGESPEED/CRUX
```

## Consumo após execução

A tela final consolida a telemetria persistida de:

```text
ai_provider_attempts
content_remediation_attempts
web_performance_attempts
```

São exibidos:

- tentativas IA;
- sucessos;
- input tokens;
- cached input tokens;
- output tokens;
- reasoning tokens;
- total tokens;
- custo estimado por moeda quando persistido;
- número de tentativas com tokens mas sem custo estimável;
- chamadas M21 por serviço.

O console não recalcula billing do provider e não duplica os totais em uma segunda fonte de verdade.

A projeção/configuração do console é persistida separadamente em:

```text
console_execution_projections
```

sem duplicar colunas de tokens ou custo real.

## Abertura de artefatos

Após execução:

```text
P. Abrir pasta da auditoria
I. Abrir relatório HTML
M. Voltar ao menu
Q. Sair
```

`P` resolve exclusivamente:

```text
audits/<AUD-ID>/
```

`I` prefere:

```text
audits/<AUD-ID>/report/index.html
```

e mantém fallback para layout legado quando necessário.

## Instalação

Instalação editable:

```powershell
python -m pip install -e .
```

O package declara `tzdata` formalmente, necessário para `ZoneInfo("America/Sao_Paulo")` em instalações Windows sem base IANA do sistema.

Entrypoints:

```text
searchgeo         -> searchgeo.cli_extensions:main
searchgeo-console -> searchgeo.interactive_console:main
```

Assim, o console executa a mesma superfície CLI capaz de resolver os providers do registry.

## Estado de qualificação

A integração estrutural do console com o registry foi validada automaticamente em Windows/Python 3.13 com:

- instalação limpa editable;
- compileall;
- timezone;
- integridade do registry;
- testes do console;
- testes específicos de provider registry no console;
- superfície CLI dos providers;
- inicialização e saída limpa do console.

A liberação funcional continua sujeita ao smoke humano do console.

Providers PROVISIONAL que ainda não tiveram caminho real de sucesso validado com credencial permanecem explicit-only e fora de AUTO. Ausência de credencial deve ser exibida como indisponibilidade, não como falha do website.

## Smoke humano obrigatório antes de merge

Validar, no mínimo:

1. `git pull` da branch e instalação editable limpa;
2. `searchgeo --version`;
3. `searchgeo audit --help` com providers novos;
4. `searchgeo-console`;
5. uma tela lógica por vez, sem empilhamento;
6. cores e `NO_COLOR`;
7. cabeçalho com início/fim/duração;
8. menu de IA contendo os sete ids canônicos mais `none` e `auto`;
9. OpenAI e DeepSeek aptos quando as respectivas keys estiverem configuradas;
10. MiMo indisponível sem PAYG `sk-...`;
11. xAI/Qwen/Gemini/Anthropic indisponíveis quando sem key e identificados como PROVISIONAL/explicit-only;
12. `AUTO` apto somente pela cadeia homologada e sem considerar keys de extensions;
13. seleção de modelo por provider;
14. menu de ambiente contendo as variáveis dos providers novos;
15. segredos exibidos somente como `[SET]`;
16. preflight bloqueando combinação inválida;
17. exposição `NENHUM` com IA/M21 desligados;
18. exposição alterada ao habilitar IA/dispositivos/limites;
19. TXT usando quantidade exata de URLs válidas;
20. M21 contabilizando quota sem inventar custo;
21. execução mínima `none/mobile/M21 off`;
22. execução mínima com provider real já homologado;
23. tokens/custos finais reconciliados com `audit.db`;
24. custo parcial sinalizado quando pricing estiver ausente;
25. `P` abrindo exatamente o workspace do `AUD-ID`;
26. `I` abrindo o report da mesma sessão;
27. P/I permanecendo disponíveis após retorno ao menu;
28. quarantine exibido sem segredo;
29. nenhum segredo em tela, report, SQLite ou log;
30. resultado da auditoria equivalente ao CLI com a mesma configuração.
