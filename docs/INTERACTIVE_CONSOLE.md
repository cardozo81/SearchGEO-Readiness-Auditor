# Console interativo de execução

O SearchGEO mantém `searchgeo audit` como interface estável e oferece o console textual opcional:

```powershell
searchgeo-console
```

O console é uma camada de orquestração e segurança operacional. Ele não implementa um segundo pipeline: após o preflight, executa a mesma superfície `searchgeo audit` do produto.

## Princípios

- uma tela lógica por vez; menus anteriores não ficam empilhados;
- configuração explícita antes da execução;
- segredo nunca é exibido em claro;
- integração externa indisponível é bloqueada antes de executar;
- erro de provider não vira finding do website;
- Score, Coverage, Confidence, regras e persistência pertencem ao pipeline estável;
- custo prévio é indicador de exposição, não invoice;
- tokens/custos finais vêm da telemetria persistida;
- M23 é tratado como **carga sintética**, não como custo financeiro de API.

## Provider registry canônico

A descoberta de providers do console usa:

```text
src/searchgeo/provider_registry.py
```

O console não mantém lista independente de providers, modelos ou credenciais.

Providers concretos:

```text
openai
deepseek
mimo
xai
qwen
gemini
anthropic
```

Aliases aceitos pela CLI:

```text
grok   -> xai
claude -> anthropic
```

## Qualification e AUTO

A cadeia `AUTO` permanece deliberadamente restrita a:

```text
OpenAI -> DeepSeek -> MiMo
```

xAI, Qwen, Gemini e Anthropic permanecem:

```text
PROVISIONAL
explicit-only
auto_eligible = false
```

Configurar suas keys pode habilitar seleção explícita, mas não os inclui em `AUTO`.

## Credenciais e disponibilidade

`none` está sempre disponível.

Provider explícito fica apto somente quando registry e ambiente indicam configuração válida: key correspondente, modelo compatível, reasoning válido quando aplicável e ausência de bloqueio transitório da sessão.

Principais keys:

| Provider | Variável |
|---|---|
| OpenAI | `OPENAI_API_KEY` |
| DeepSeek | `DEEPSEEK_API_KEY` |
| MiMo | `MIMO_API_KEY` |
| xAI | `XAI_API_KEY` |
| Qwen | `DASHSCOPE_API_KEY` |
| Gemini | `GEMINI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |

MiMo exige credencial PAYG compatível com `sk-...`. Token Plan `tp-...` não deve ser enviado ao adapter PAYG atual.

## Variáveis de ambiente

Menu:

```text
E. Variáveis de ambiente
```

Ações:

```text
S = setar/alterar
R = remover
H = ajuda/custo
V = voltar
```

Alterações valem somente para a sessão do console e subprocessos filhos. O console não grava permanentemente o perfil do Windows/PowerShell.

Secrets aparecem como:

```text
[SET]
```

Nunca como valor real.

Além das variáveis de providers e M21, o menu incorpora as variáveis M23:

```text
SEARCHGEO_SYNTHETIC_APDEX
SEARCHGEO_APDEX_THRESHOLD_SECONDS
SEARCHGEO_APDEX_SAMPLES_PER_CONTEXT
SEARCHGEO_APDEX_MAX_ATTEMPTS_PER_CONTEXT
SEARCHGEO_APDEX_MAX_PAGES
SEARCHGEO_APDEX_TIMEOUT_SECONDS
SEARCHGEO_APDEX_DELAY_SECONDS
SEARCHGEO_APDEX_CONCURRENCY
```

## Defaults

```text
entrada             = URL única
device              = mobile
IA                  = none
remediação M20      = off
Web Performance M21 = off
Synthetic Apdex M23 = off
max-pages           = 100
web max-pages       = 10
idioma              = pt-BR
mercado             = BR
audits root         = audits
```

Quando M23 é habilitado no console:

```text
T                   = obrigatório
amostras válidas    = 100 por default
max attempts        = ceil(1.25 × alvo)
max pages           = 1
timeout              = max(45 s, 4T+5 s)
delay                = 1 s
concorrência         = 1; máximo 2
```

## Menu principal

O menu canônico contém:

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
11. Synthetic Apdex M23

H. Ajuda / custos
E. Variáveis de ambiente
R. Executar [APTO|INDISPONÍVEL]
Q. Sair
```

Após uma auditoria da sessão:

```text
P. Abrir pasta da auditoria
I. Abrir relatório HTML
```

## Navegação em tela única

Ao entrar em configuração, provider, modelo, ajuda, variáveis ou ações pós-execução, o console limpa a tela anterior e redesenha o contexto atual. O objetivo é evitar empilhamento de menus no terminal.

`NO_COLOR` remove coloração sem remover textos de status.

## Cores

| Cor/ênfase | Significado |
|---|---|
| verde | pronto, sucesso, opção ativa/apta |
| amarelo | atenção, execução, custo/carga relevante |
| vermelho | erro, bloqueio, indisponibilidade |
| magenta | API externa |
| ciano/azul | informação, dispositivo, integração/processamento local |
| dim/neutro | desligado, não configurado, secundário |

## Cabeçalho operacional

O cabeçalho acompanha versão, status, URL, device, operação, ambiente relevante com secrets mascarados, início, fim, duração e erro operacional quando houver.

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

Duração usa relógio monotônico; início/fim usam timestamp timezone-aware.

## Entrada URL e TXT

### URL única

Uma URL/domínio é seed de crawl. Antes da execução conhece-se uma página e o teto `max-pages`.

### TXT

UTF-8, uma URL/domínio por linha. Vazias e comentários `#` são ignorados.

O preflight valida arquivo, UTF-8, targets, origem normalizada e compatibilidade com `max-pages`.

## Dispositivo

```text
mobile
desktop
both
```

`both` duplica contextos potenciais por página e é sinalizado como multiplicador de volume. Em M23, uma página com `both` pode gerar dois grupos independentes de amostragem.

## Preflight

`R. Executar` só inicia se a configuração estiver apta.

Bloqueios incluem:

- target ausente/inválido;
- TXT inexistente/inválido;
- origens misturadas;
- `max-pages` insuficiente;
- provider inexistente/indisponível;
- provider sem key ou key incompatível;
- modelo/reasoning inválido;
- `none` com M20 textual;
- `auto` com `--ai-model`;
- CrUX direto sem `SEARCHGEO_CRUX_API_KEY`;
- Chromium configurado em caminho inexistente;
- M23 ON sem threshold `T` explícito;
- M23 com amostras < 1;
- max attempts M23 menor que alvo;
- timeout M23 <= `4T`;
- delay negativo;
- concorrência M23 fora de 1–2.

Nenhum workspace deve ser criado por execução bloqueada no preflight.

## Remediação M20

M20 é opcional e pode acrescentar chamadas de IA para findings elegíveis. Só pode ser ativado quando o provider selecionado está apto.

Não altera Score, Coverage, Confidence, RuleExecution ou Finding.

## Web Performance M21

M21 é integração externa independente de LLM. O console mostra PageSpeed/CrUX como consumo de API/quota e não inventa preço monetário quando não há base confiável.

`field_source=crux` exige `SEARCHGEO_CRUX_API_KEY`.

## Synthetic Apdex M23

Item:

```text
11. Synthetic Apdex M23
```

Ao habilitar, o console solicita/configura:

```text
T
amostras válidas por contexto
máximo de tentativas por contexto
máximo de páginas M23
timeout por navegação
delay mínimo entre inícios
concorrência
```

### Regras

- M23 é default OFF;
- `T` é obrigatório;
- timeout deve ser > `4T`;
- concorrência máxima = 2;
- default normal = 100 válidas por URL/device;
- grupo com 1–99 é small group `*`;
- cada amostra usa navegação real Chromium com BrowserContext novo e cache desabilitado;
- M23 não usa LLM e não exige PageSpeed/CrUX.

### Fórmula

```text
Apdex = (Satisfied + 0.5 × Tolerating) / Total de amostras válidas

Satisfied  <= T
Tolerating > T e <= 4T
Frustrated > 4T
```

### Carga

M23 não altera a classificação financeira `NENHUM/BAIXO/MÉDIO/ALTO/EXCESSIVO`, porque essa faixa representa exposição financeira externa, não CPU local ou tráfego do alvo.

Em vez disso, o console mostra uma linha separada de **Carga M23 potencial**, considerando páginas, devices, alvo de amostras e orçamento máximo de tentativas.

Uma navegação pode carregar muitos subrecursos; por isso a projeção não trata “100 amostras” como “100 requests HTTP”.

## Exposição financeira antes da execução

Faixa:

```text
NENHUM | BAIXO | MÉDIO | ALTO | EXCESSIVO
```

É heurística operacional, não previsão de invoice.

Entram na projeção financeira:

1. quantidade conhecida/teto de páginas;
2. device;
3. provider explícito ou cadeia AUTO elegível;
4. modelo/pricing conhecido;
5. M20;
6. M21 e limites externos.

M23 é exibido separadamente como carga sintética.

Para modelo sem pricing catalogado, o console informa que o preço unitário não está catalogado; não converte ausência de preço em custo zero.

## AUTO e teto potencial

Em `AUTO`, o teto considera somente:

```text
OpenAI -> DeepSeek -> MiMo
```

O primeiro resultado válido encerra a cadeia naquele contexto. Providers extension `PROVISIONAL` não participam da conta AUTO.

## Quarantine

Quando telemetria indica `QUARANTINED_FOR_AUDIT`, o console bloqueia aquele provider na sessão e mostra motivo sanitizado. Alterar/remover a credencial correspondente limpa o bloqueio transitório para nova avaliação.

## Monitoramento da execução

O console observa:

```text
audit.db
logs/audit.log
```

Mapeamento resumido:

```text
DISCOVERING / ACQUIRING -> INTEGRATION:HTTP
ANALYZING + IA           -> API:<provider efetivo>
ANALYZING sem IA         -> LOCAL:SEMANTIC_RULES
COMPARING / SCORING      -> LOCAL:RULES/SCORE
REPORTING                -> LOCAL:REPORT
M21                      -> API:PAGESPEED/CRUX
M23                      -> LOCAL/HTTP:SYNTHETIC_APDEX
```

M23 não é rotulado como API paga; a operação representa browser local + tráfego HTTP real.

## Consumo após execução

A tela final consolida telemetria persistida de IA/M20/M21 e M23.

Pode exibir:

- tentativas IA;
- sucessos;
- input/cached/output/reasoning/total tokens;
- custo estimado por moeda quando persistido;
- tentativas IA sem custo estimável;
- chamadas M21 por serviço;
- tentativas de navegação M23;
- amostras válidas/inválidas M23;
- contextos/status M23.

Mensagem M23:

```text
Custo M23 monetário : sem API paga própria; há CPU/tempo local e tráfego HTTP real contra o alvo.
```

O console não recalcula billing e não duplica os totais em uma segunda fonte de verdade.

## Abertura de artefatos

Após execução:

```text
P. Abrir pasta da auditoria
I. Abrir relatório HTML
M. Voltar ao menu
Q. Sair
```

`P` resolve `audits/<AUD-ID>/`. `I` prefere `audits/<AUD-ID>/report/index.html`.

M23, quando materializado, aparece no menu HTML como `Apdex` e em `report/apdex.html`.

## Instalação

```powershell
python -m pip install -e .
python -m playwright install chromium
```

Entrypoints:

```text
searchgeo         -> searchgeo.cli_extensions:main
searchgeo-console -> searchgeo.interactive_console:main
```

## Segurança operacional

- não exibir secrets em claro;
- não persistir API key em report/log;
- não assumir que key configurada implica crédito/compatibilidade;
- não executar M23 com volume relevante em produção sem autorização;
- para smoke M23, preferir 1 URL, 1 device, 3–5 amostras, concurrency 1 e alvo controlado/local.

## Leituras relacionadas

- [CLI_REFERENCE.md](CLI_REFERENCE.md)
- [CONFIGURATION.md](CONFIGURATION.md)
- [CONSOLE_COST_AND_USAGE.md](CONSOLE_COST_AND_USAGE.md)
- [SYNTHETIC_APDEX.md](SYNTHETIC_APDEX.md)
- [PROVIDER_REGISTRY.md](PROVIDER_REGISTRY.md)
- [AI_PROVIDER_EXTENSIONS.md](AI_PROVIDER_EXTENSIONS.md)
