# Console interativo de execução

O SearchGEO mantém `searchgeo audit` como interface estável e oferece o console textual opcional:

```powershell
searchgeo-console
```

O console é uma camada de configuração, preflight, observabilidade e execução sobre o mesmo pipeline da CLI. Ele não implementa um segundo motor de auditoria.

## Princípios

- uma tela lógica por vez;
- configuração explícita antes da execução;
- progresso/etapa durante a execução sem polling externo adicional;
- secrets nunca são exibidos em claro;
- credenciais não são gravadas no arquivo INI;
- persistência opcional de credenciais no Windows exige confirmação explícita e usa apenas o escopo `User`;
- integração externa indisponível é explicada e não vira finding do website;
- custo prévio é estimativa de exposição, não invoice;
- consumo real exibido após a execução vem da telemetria persistida;
- Synthetic Apdex é tratado como carga sintética, não como custo financeiro de API.

## Arquivo de configuração do usuário

O console usa por padrão:

```text
searchgeo-console.ini
```

Ao iniciar:

1. se o arquivo não existir, ele é criado com defaults não sensíveis;
2. os parâmetros persistíveis são carregados;
3. configurações de ambiente válidas continuam disponíveis para a sessão;
4. API keys, tokens, senhas e outros secrets não são lidos nem gravados pelo INI.

O menu mostra o estado do arquivo:

```text
Arquivo INI: ...\searchgeo-console.ini | SALVO
```

ou:

```text
Arquivo INI: ...\searchgeo-console.ini | ALTERAÇÕES NÃO SALVAS
```

Para persistir os parâmetros não sensíveis:

```text
S. Salvar configuração INI [SEM CHAVES]
```

A gravação é atômica: o conteúdo é produzido em arquivo temporário e substitui o INI somente após a escrita concluir.

Ao sair com alterações pendentes, o console pede uma decisão explícita. Credenciais que diferem da persistência do Windows continuam sendo tratadas como alterações voláteis da sessão.

## Credenciais

Principais variáveis:

| Serviço | Variável |
|---|---|
| OpenAI | `OPENAI_API_KEY` |
| DeepSeek | `DEEPSEEK_API_KEY` |
| MiMo | `MIMO_API_KEY` |
| xAI | `XAI_API_KEY` |
| Qwen | `DASHSCOPE_API_KEY` |
| Gemini | `GEMINI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| PageSpeed | `SEARCHGEO_PAGESPEED_API_KEY` |
| CrUX | `SEARCHGEO_CRUX_API_KEY` |

As credenciais podem ser inseridas/alteradas no menu:

```text
E. Variáveis de ambiente / credenciais
```

Secrets são lidos com entrada sem eco e aparecem somente como `[SET]`.

### Sessão × persistência no Windows

O valor efetivamente usado pela auditoria é sempre o valor presente no processo atual. Portanto, quando uma key já existe no Windows e o usuário a altera dentro do console, **o valor da sessão aberta prevalece imediatamente**.

O menu representa a origem sem exibir o segredo:

```text
[SET] [SO:USER]
[SET] [SO:MACHINE]
[SET] [SESSÃO]
[SET] [SESSÃO | SO:USER existente]
```

Se uma credencial persistida foi removida apenas da sessão atual, o console também pode indicar que ela continua persistida no SO, mas não está ativa naquele processo.

Dentro do menu de ambiente:

```text
S = setar/alterar somente a sessão atual
R = remover somente da sessão atual
P = persistir/remover credencial no Windows
```

A opção `P` é restrita a secrets. Para persistir, o usuário precisa primeiro ter um valor válido na sessão e confirmar explicitamente digitando `SIM`. A gravação é feita no ambiente **User** do Windows, equivalente à persistência de variável de ambiente do usuário; não usa o escopo `Machine` e não exige execução como Administrador.

A remoção de persistência também exige confirmação e remove somente o valor do escopo Windows/User. O valor da sessão atual é preservado até que o processo seja encerrado ou o usuário o remova pela opção `R`.

A persistência no Windows não transforma a variável em secret manager: processos e ferramentas com acesso ao mesmo perfil do usuário podem ler variáveis de ambiente persistidas. O SearchGEO nunca grava essas chaves em `searchgeo-console.ini`, reports ou logs.

MiMo exige credencial PAYG compatível com `sk-...` no adapter atual. Token Plan `tp-...` usa produto/endpoint diferente e não é tratado como credencial PAYG válida.

## Provider registry e AUTO

O console deriva providers, modelos e variáveis do registry canônico. Providers concretos:

```text
openai
deepseek
mimo
xai
qwen
gemini
anthropic
```

Aliases:

```text
grok   -> xai
claude -> anthropic
```

A cadeia `AUTO` permanece:

```text
OpenAI -> DeepSeek -> MiMo
```

xAI, Qwen, Gemini e Anthropic permanecem explicit-only enquanto sua qualificação externa não for promovida.

## Defaults públicos de IA

Quando o usuário não define override, o produto privilegia o modelo mais simples disponível no adapter e o menor esforço de raciocínio efetivamente suportado:

| Provider | Modelo default | Esforço default |
|---|---|---|
| OpenAI | `gpt-5.6-luna` | `NONE` |
| DeepSeek | `deepseek-v4-flash` | `NONE` |
| MiMo | `mimo-v2.5` | `NONE` |
| xAI | `grok-4.6` | `LOW` |
| Qwen | `qwen3.8-flash` | `PROVIDER_DEFAULT` |
| Gemini | `gemini-3.8-flash` | `LOW` |
| Anthropic | `claude-sonnet-5` | `LOW` |

Overrides explícitos de modelo/esforço continuam prevalecendo quando o adapter aceita o valor.

## Menu principal

A superfície funcional é:

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
11. Synthetic Apdex

H. Ajuda / custos
E. Variáveis de ambiente / credenciais
S. Salvar configuração INI [SEM CHAVES]
R. Executar [APTO|INDISPONÍVEL]
Q. Sair
```

Após uma auditoria:

```text
P. Abrir pasta da auditoria
I. Abrir relatório HTML
M. Voltar ao menu
Q. Sair
```

## Opção 4 — IA

A configuração de IA reúne:

```text
provider
modelo
esforço/profundidade, quando suportado
timeout por tentativa
```

O menu principal resume a configuração efetiva, por exemplo:

```text
4. IA : openai [APTO] | modelo=gpt-5.6-luna | esforço=NONE | timeout=180s
```

`SEARCHGEO_AI_TIMEOUT_SECONDS` continua disponível como configuração avançada. O timeout limita cada tentativa contra o provider; não é um timeout global da auditoria.

Em `AUTO`, OpenAI, DeepSeek e MiMo mantêm sua própria configuração de modelo/esforço. Um fallback não herda parâmetros incompatíveis do provider anterior.

## Opção 5 — Remediação textual por IA

A remediação só pode ser habilitada quando a opção 4 possui um provider apto. Com IA=`none` ou provider indisponível, o menu informa explicitamente:

```text
INDISPONÍVEL [REQUER IA CONFIGURADA E ATIVA NO ITEM 4]
```

A remediação é advisory/evidence-bound, pode gerar chamadas adicionais e não altera automaticamente Score, Coverage, Confidence, RuleExecution ou Finding.

## Opção 6 — Web Performance

Configura coleta externa PageSpeed/Lighthouse e dados de campo CrUX.

O console permite definir:

```text
habilitado/desabilitado
field source
timeout PageSpeed/Lighthouse por URL
```

Default operacional de timeout:

```text
120 segundos
```

Esse valor controla quanto o cliente SearchGEO aguarda a resposta completa da chamada PageSpeed/CrUX. A API PageSpeed executa o Lighthouse remotamente e não expõe ao SearchGEO um parâmetro separado para definir o timeout interno de carregamento da página usado pelo Lighthouse.

`field_source=crux` exige `SEARCHGEO_CRUX_API_KEY`.

Quando PageSpeed falha, mas CrUX direto funciona, o resultado de Web Performance fica parcial. Métricas Lighthouse e Acessibilidade que dependem do artifact PageSpeed permanecem indisponíveis e o relatório mostra a causa persistida, como timeout, HTTP, quota ou outro erro operacional.

## Opção 11 — Synthetic Apdex

Synthetic Apdex mede repetidamente uma Task de navegação real em Chromium e gera tráfego HTTP contra o alvo.

Ao habilitar, o console explica e solicita:

- **T**: tempo-alvo; `<=T` Satisfied, `>T e <=4T` Tolerating, `>4T` Frustrated;
- **amostras válidas por contexto**: tamanho desejado do grupo por URL/device;
- **máximo de tentativas**: teto para substituir amostras inválidas;
- **máximo de páginas**: limite de páginas que recebem a medição;
- **timeout por navegação**: deve ser `>4T`;
- **delay**: intervalo mínimo entre inícios;
- **concorrência**: 1 é conservador; 2 aumenta carga simultânea.

Defaults quando habilitado:

```text
T                    = obrigatório
amostras válidas     = 100
max attempts         = ceil(1.25 × alvo)
max pages            = 1
timeout                = max(45 s, 4T + 5 s)
delay                  = 1 s
concorrência           = 1; máximo 2
```

Grupos com 1–99 amostras válidas são diagnóstico small-group e recebem `*`.

Synthetic Apdex não usa LLM e não adiciona chamadas PageSpeed/CrUX, mas pode gerar muitos requests de subrecursos contra o site. Use volume relevante em produção somente com autorização.

## Progresso durante a execução

O console atualiza a mesma tela aproximadamente uma vez por segundo e apresenta:

```text
Status
URL
Dispositivo
Operação
Início
Fim
Duração
Etapa
Progresso
Detalhe
```

A atualização não realiza polling HTTP adicional. Ela usa estado do subprocesso, leitura SQLite em modo somente leitura e tail limitado do log operacional.

Quando não existe contador exato, o percentual é identificado como estimativa por etapa. Synthetic Apdex usa os contadores persistidos de contexto/amostras/tentativas e pode exibir progresso medido.

## Configuração × resultado obtido

Depois da execução, o console e o relatório diferenciam **configurado** de **materializado**.

São mostrados separadamente:

- tentativas/sucessos de IA;
- tokens e custo IA estimado;
- chamadas PageSpeed;
- chamadas CrUX;
- cobertura de Acessibilidade;
- causa quando Acessibilidade não foi obtida;
- tentativas/amostras Synthetic Apdex.

Uma fonte configurada que falhou por timeout, quota, HTTP, ausência de artifact ou falta de dado não é silenciosamente apresentada como sucesso nem como problema do website.

## Segurança e persistência

- o INI não armazena secrets;
- reports/logs não devem conter chaves em claro;
- o console não pressupõe que uma key configurada possua saldo/quota;
- a sessão atual prevalece sobre valores herdados do SO durante a execução aberta;
- persistência opcional de credencial no Windows usa somente `User`, mediante confirmação explícita;
- remoção da persistência `User` não apaga automaticamente o valor já carregado na sessão atual;
- o console informa `SO:USER`, `SO:MACHINE` ou `SESSÃO` sem revelar o secret;
- variáveis de ambiente não são equivalentes a um secret manager;
- valores não sensíveis podem ser salvos no INI;
- alterações não salvas são avisadas antes da saída.

## Identificadores internos históricos

Nomes de módulos, tabelas, eventos e documentos normativos podem manter identificadores históricos de implementação para compatibilidade de schema/rastreabilidade. Esses identificadores não constituem nomenclatura funcional da interface pública e não devem ser usados como rótulos do menu ou dos relatórios.

## Leituras relacionadas

- [CONFIGURATION.md](CONFIGURATION.md)
- [CLI_REFERENCE.md](CLI_REFERENCE.md)
- [CONSOLE_COST_AND_USAGE.md](CONSOLE_COST_AND_USAGE.md)
- [SYNTHETIC_APDEX.md](SYNTHETIC_APDEX.md)
- [PROVIDER_REGISTRY.md](PROVIDER_REGISTRY.md)
- [AI_GUIDE.md](AI_GUIDE.md)
