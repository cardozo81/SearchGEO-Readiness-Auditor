# Configuração operacional

O SearchGEO pode ser configurado por CLI, console interativo, arquivo INI do console e variáveis de ambiente. Credenciais permanecem fora do arquivo INI.

## Prioridade prática

Para `searchgeo audit`, argumentos CLI explícitos prevalecem sobre defaults de ambiente quando o parâmetro possui equivalente CLI.

Para `searchgeo-console`:

1. `searchgeo-console.ini` fornece parâmetros persistidos não sensíveis;
2. variáveis de ambiente ficam disponíveis para credenciais e overrides avançados;
3. alterações de sessão valem imediatamente para o processo atual;
4. `S. Salvar configuração INI` persiste somente estado não sensível;
5. no Windows, secrets podem opcionalmente ser persistidos no ambiente **User** somente por ação explícita no menu de credenciais.

O console nunca grava API keys, tokens, senhas ou credentials no INI.

## Variáveis de ambiente: referência detalhada

A referência completa de **todas as variáveis expostas pelo console**, incluindo finalidade, tipo, domínio aceito, default efetivo, dependências, custo/impacto, exemplos e passo a passo para obtenção das credenciais, está em:

- [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md)

O menu `E. Variáveis de ambiente / credenciais` usa a mesma organização por fronteira funcional:

```text
1. Aplicação e execução
2. IA — credenciais
3. IA — modelos e reasoning
4. IA — endpoints avançados
5. Web Performance / Google APIs
6. Synthetic Apdex
7. Browser / Playwright
A. Todas as variáveis
D. Abrir documentação detalhada
V. Voltar
```

Quando existe um default seguro, o menu mostra o **default efetivo** em vez de induzir o usuário a criar uma variável redundante. Variáveis de segredo e valores semanticamente obrigatórios sem default, como o threshold T do Synthetic Apdex quando a medição é habilitada, continuam exigindo entrada explícita.

## Arquivo INI do console

Arquivo padrão:

```text
searchgeo-console.ini
```

Se não existir, o console o cria com defaults. O arquivo armazena parâmetros como:

```text
entrada / arquivo de URLs
projeto
idioma / mercado
max-pages
raiz de auditorias
dispositivo
provider/modelo/esforço de IA
timeout de IA
remediação textual
Web Performance
WebPerf max-pages
field source
timeout PageSpeed/Lighthouse
categorias Lighthouse
Synthetic Apdex
T / samples / attempts / páginas / timeout / delay / concorrência
```

Não armazena:

```text
OPENAI_API_KEY
DEEPSEEK_API_KEY
MIMO_API_KEY
XAI_API_KEY
DASHSCOPE_API_KEY
GEMINI_API_KEY
ANTHROPIC_API_KEY
SEARCHGEO_PAGESPEED_API_KEY
SEARCHGEO_CRUX_API_KEY
qualquer variável reconhecida como TOKEN / SECRET / PASSWORD / CREDENTIAL
```

## Defaults gerais

```text
device                  = mobile
ai-provider             = none
ai-content-remediation  = off
Web Performance         = off
max-pages               = 100
WebPerf max-pages       = 10
Web Performance timeout = 120 s
language                = pt-BR
market                  = BR
audits-root             = audits
Synthetic Apdex         = off
```

Esses defaults tornam possível uma primeira auditoria local sem preencher a lista de variáveis: para o cenário sem IA e sem integrações externas, basta informar o alvo.

## IA

Providers concretos suportados pelo registry:

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

AUTO permanece:

```text
OpenAI -> DeepSeek -> MiMo
```

Providers adicionais permanecem explicit-only até promoção formal de qualificação.

### Credenciais

```text
OPENAI_API_KEY
DEEPSEEK_API_KEY
MIMO_API_KEY
XAI_API_KEY
DASHSCOPE_API_KEY
GEMINI_API_KEY
ANTHROPIC_API_KEY
```

A existência da variável não garante saldo, quota, plano compatível ou acesso ao modelo. Consulte [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md) para o procedimento de criação de cada chave.

### Modelos defaults públicos

Sem override explícito:

```text
OPENAI     gpt-5.6-luna
DEEPSEEK   deepseek-v4-flash
MIMO       mimo-v2.5
XAI        grok-4.6
QWEN       qwen3.8-flash
GEMINI     gemini-3.8-flash
ANTHROPIC  claude-sonnet-5
```

Os demais modelos declarados pelo registry continuam selecionáveis quando suportados pela conta/provider.

### Esforço / profundidade

Default público: menor nível efetivamente suportado pelo adapter/modelo.

```text
OPENAI     NONE
DEEPSEEK   NONE
MIMO       NONE
XAI        LOW
QWEN       PROVIDER_DEFAULT
GEMINI     LOW
ANTHROPIC  LOW
```

Variáveis de reasoning continuam sendo respeitadas como overrides quando o adapter possui controle validado. Qwen permanece `PROVIDER_DEFAULT` porque o adapter atual não expõe um controle de reasoning validado.

### Timeout de IA

```text
SEARCHGEO_AI_TIMEOUT_SECONDS
```

Default público:

```text
180 s por tentativa
```

O timeout limita uma tentativa contra o provider. Não encerra a auditoria inteira.

## Remediação textual por IA

A remediação textual é OFF por padrão e só pode ser habilitada quando existe provider de IA apto.

```text
SEARCHGEO_AI_CONTENT_REMEDIATION
```

No console, a opção 5 informa explicitamente que depende da configuração da opção 4.

## Web Performance, Lighthouse e CrUX

```text
SEARCHGEO_WEB_PERFORMANCE
SEARCHGEO_WEB_PERFORMANCE_MAX_PAGES
SEARCHGEO_WEB_PERFORMANCE_TIMEOUT_SECONDS
SEARCHGEO_WEB_PERFORMANCE_FIELD_SOURCE
SEARCHGEO_LIGHTHOUSE_CATEGORIES
SEARCHGEO_PAGESPEED_API_KEY
SEARCHGEO_CRUX_API_KEY
```

### Timeout

Default operacional:

```text
SEARCHGEO_WEB_PERFORMANCE_TIMEOUT_SECONDS=120
```

Também pode ser configurado diretamente na opção 6 do console.

O valor é o limite de espera do cliente SearchGEO pela resposta externa PageSpeed/CrUX. A chamada PageSpeed executa Lighthouse remotamente; o endpoint usado pelo SearchGEO não fornece um parâmetro separado para configurar o timeout interno de carregamento da página dentro do Lighthouse.

Um timeout PageSpeed pode deixar:

- Lighthouse lab indisponível;
- Acessibilidade automatizada indisponível, pois usa a categoria `accessibility` do mesmo artifact;
- CrUX direto ainda disponível quando configurado e bem-sucedido;
- status de Web Performance `PARTIAL` em vez de fabricar dados ausentes.

### Field source

Valores:

```text
auto
pagespeed
crux
none
```

`crux` direto exige `SEARCHGEO_CRUX_API_KEY`.

### Categorias Lighthouse

Default:

```text
performance,accessibility,best-practices,seo
```

O editor de variáveis rejeita categorias desconhecidas ou duplicadas. A ausência de uma categoria configurada deve aparecer como **não solicitada**, não como falha do website.

## Synthetic Apdex

Variáveis:

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

Quando habilitado:

```text
T                      = obrigatório
amostras válidas       = 100
máximo de tentativas   = ceil(1.25 × alvo)
máximo de páginas      = 1
timeout por navegação  = max(45 s, 4T + 5 s)
delay                  = 1 s
concorrência           = 1; máximo 2
```

O timeout do Synthetic Apdex é distinto do timeout PageSpeed e do timeout de IA. T não recebe um valor arbitrário: ele precisa ser informado quando a feature é habilitada.

## Dispositivo

```text
SEARCHGEO_DEVICE_CONTEXT
```

Valores:

```text
mobile
desktop
both
```

Default: `mobile`.

## Segurança

- use variáveis de ambiente ou secret manager apropriado para credenciais;
- o console permite inserir/remover credenciais sem gravá-las no INI;
- no Windows, a persistência opcional de secret usa somente o escopo `User` e exige confirmação explícita;
- a sessão atual prevalece sobre valores herdados do SO durante o processo aberto;
- secrets são mascarados como `[SET]` e a origem é exibida sem revelar o valor;
- logs e relatórios não devem registrar valores de segredo;
- não assuma que uma credencial configurada implica crédito/quota;
- variáveis de ambiente persistidas não equivalem a um secret manager.

## Identificadores internos

Tabelas, eventos, módulos e documentação normativa podem manter identificadores históricos para compatibilidade e rastreabilidade. A documentação operacional e a interface pública devem preferir nomes funcionais como **Web Performance**, **Acessibilidade**, **Remediação textual** e **Synthetic Apdex**.

## Documentos relacionados

- [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md)
- [INTERACTIVE_CONSOLE.md](INTERACTIVE_CONSOLE.md)
- [CLI_REFERENCE.md](CLI_REFERENCE.md)
- [AI_GUIDE.md](AI_GUIDE.md)
- [GOOGLE_API_KEYS.md](GOOGLE_API_KEYS.md)
- [SYNTHETIC_APDEX.md](SYNTHETIC_APDEX.md)
