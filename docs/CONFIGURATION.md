# CONFIGURATION.md

Configuração operacional do SearchGEO Readiness Auditor.

## Defaults da CLI

| Configuração | Default |
|---|---|
| idioma | `pt-BR` |
| mercado | `BR` |
| `--max-pages` | `100` |
| `--audits-root` | `audits` |
| `--device-context` | `mobile` |
| `--ai-provider` | `none` |
| `--ai-content-remediation` | `false` |
| timeout IA | `180` s |

## Contexto de dispositivo

Variável:

```text
SEARCHGEO_DEVICE_CONTEXT
```

Valores:

```text
mobile
desktop
both
```

Precedência:

1. `--device-context`;
2. `SEARCHGEO_DEVICE_CONTEXT`;
3. `mobile`.

Exemplos:

```powershell
searchgeo audit https://example.com --device-context mobile
searchgeo audit https://example.com --device-context desktop
searchgeo audit https://example.com --device-context both
```

```powershell
$env:SEARCHGEO_DEVICE_CONTEXT = "mobile"
searchgeo audit https://example.com
```

A seleção limita M3 aos snapshots escolhidos. M7 recebe apenas os snapshots existentes e, portanto, chamadas de IA são feitas somente para os dispositivos selecionados. M20 textual também respeita esse mesmo universo. `mobile` é o default para reduzir custo e tempo quando comparação Desktop × Mobile não é necessária.

Chamadas internas diretas a M3 sem a variável continuam usando ambos os dispositivos por compatibilidade interna.

## Configuração de IA

### Desabilitada

```powershell
searchgeo audit https://example.com --ai-provider none
```

Nenhuma API externa é chamada. A revisão determinística de JSON-LD continua sendo produzida porque não depende de provider externo.

### OpenAI

```powershell
$env:OPENAI_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider openai
```

Default: `gpt-5.6-terra`.

### DeepSeek

```powershell
$env:DEEPSEEK_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider deepseek
```

Default: `deepseek-v4-pro`.

### Xiaomi MiMo

```powershell
$env:MIMO_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider mimo
```

Default: `mimo-v2.5-pro`.

### AUTO

```powershell
$env:OPENAI_API_KEY = "<chave>"
$env:DEEPSEEK_API_KEY = "<chave>"
$env:MIMO_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider auto
```

O AUTO:

- considera somente providers com token e configuração válida;
- fixa a cadeia no início do audit;
- chama sequencialmente;
- para no primeiro resultado válido do contexto;
- não permite que provider posterior sobrescreva o resultado aceito;
- quarantina provider após falha qualificadora.

## M20 — sugestões textuais opcionais

Variável:

```text
SEARCHGEO_AI_CONTENT_REMEDIATION
```

Default:

```text
false
```

Valores aceitos:

```text
true / false
1 / 0
yes / no
on / off
```

Precedência:

1. `--ai-content-remediation` ou `--no-ai-content-remediation`;
2. `SEARCHGEO_AI_CONTENT_REMEDIATION`;
3. `false`.

Exemplos:

```powershell
$env:OPENAI_API_KEY = "<chave>"
searchgeo audit https://example.com `
  --ai-provider openai `
  --ai-content-remediation
```

```powershell
$env:SEARCHGEO_AI_CONTENT_REMEDIATION = "true"
searchgeo audit https://example.com --ai-provider auto
```

M20 é executado depois de findings e scoring. O recurso:

- não altera `RuleExecution`, `Finding`, `Score`, Coverage ou Confidence;
- não é disparado apenas por Confidence LOW;
- recebe somente findings contentuais/semânticos elegíveis e suas evidências persistidas;
- não publica nem aplica texto automaticamente;
- exige revisão humana;
- herda model, reasoning, timeout, quarantine e roteamento dos providers já configurados para M18;
- mantém telemetria própria para separar custo de avaliação semântica do custo de remediação textual.

Se M20 for habilitado com `--ai-provider none`, a auditoria não falha: a etapa textual registra `NOT_CONFIGURED`, não chama API e mantém a revisão JSON-LD determinística.

## JSON-LD por página

A revisão JSON-LD não precisa de IA e é materializada para cada snapshot/dispositivo efetivamente auditado.

Quando não há JSON-LD, o SearchGEO pode propor um baseline conservador `WebPage` usando apenas dados observados/persistidos, como:

- URL canônica/normalizada;
- idioma da auditoria;
- `<title>`;
- meta description;
- entidade principal apenas quando a evidência persistida for suficientemente inequívoca.

Quando já há JSON-LD, o auditor evita reescrita destrutiva e aponta problemas verificáveis, como parse error, blocos idênticos repetidos, ausência global de `@context`, nós sem `@type` e propriedades genéricas ausentes de um nó `WebPage` quando os valores correspondentes já são conhecidos.

Para rich results, as propriedades obrigatórias/recomendadas dependem do tipo/feature e devem ser validadas contra a documentação específica do Google e Schema.org. JSON-LD não é requisito universal de GEO e markup correto não garante exibição de rich result.

## Modelos suportados

```text
OPENAI:   gpt-5.6-sol | gpt-5.6-terra | gpt-5.6-luna
DEEPSEEK: deepseek-v4-pro | deepseek-v4-flash
MIMO:     mimo-v2.5-pro | mimo-v2.5
```

`--ai-model` funciona somente para provider explícito. Em `auto`, use as variáveis de modelo específicas.

## Variáveis de provider

```text
OPENAI_API_KEY
DEEPSEEK_API_KEY
MIMO_API_KEY

SEARCHGEO_OPENAI_MODEL
SEARCHGEO_DEEPSEEK_MODEL
SEARCHGEO_MIMO_MODEL
```

Nunca versionar as chaves.

## Timeout de IA

```text
SEARCHGEO_AI_TIMEOUT_SECONDS
```

Default da CLI:

```text
180
```

Exemplo:

```powershell
$env:SEARCHGEO_AI_TIMEOUT_SECONDS = "240"
```

Deve ser número finito > 0. Com `--ai-provider none`, não existe chamada externa e o timeout não tem efeito prático. Timeout não gera retry automático. M20 reutiliza o mesmo timeout dos providers selecionados.

## Provider selecionado sem credencial

Provider explícito:

- fica `NOT_CONFIGURED` na etapa semântica quando não existe credencial;
- nenhuma chamada externa é realizada;
- a auditoria segue com capacidade semântica reduzida;
- ausência das chaves dos outros providers não interfere.

AUTO:

- provider sem chave não entra na cadeia;
- se nenhum for elegível, nenhuma chamada externa é feita.

M20 não reativa provider quarantined pela etapa semântica e não cria credencial separada.

## Dispositivo × IA

Para uma auditoria de uma página:

```text
mobile  -> no máximo um contexto semântico externo da página por finalidade
 desktop -> no máximo um contexto semântico externo da página por finalidade
both    -> até dois contextos, Mobile e Desktop, por finalidade
```

O número real depende de snapshots disponíveis, provider habilitado, findings M20 elegíveis, quarantine, URL lock e resultados anteriores.

Essa seleção é a principal configuração para evitar custo de IA de um dispositivo que não precisa ser analisado.

## Logging

O `--config PATH` aponta para `searchgeo.toml` usado pelo módulo atual de logging. API keys e Authorization não devem ser gravados.

A baseline não materializa `audit.log` automaticamente. Os dados persistentes da auditoria ficam em:

```text
audit.db
artifacts/
report/
```

## Report site

Estrutura:

```text
report/
├─ index.html
├─ mobile.html
├─ desktop.html
├─ remediation.html
├─ content-suggestions.html
├─ ai-usage.html
├─ references.html
└─ css/
   └─ site.css
```

`mobile.html` e `desktop.html` somente são materializados quando o dispositivo correspondente foi auditado.

A telemetria de M18 e M20 fica em `ai-usage.html`; não é misturada aos findings do website. Sugestões textuais e revisão JSON-LD ficam em `content-suggestions.html`.

## Configurações não expostas como promessa de produto

Não há atualmente configuração pública para:

- serviço web/backend;
- banco remoto;
- Docker daemon;
- execução distribuída;
- retry automático de IA;
- publicação/aplicação automática de conteúdo sugerido;
- criação automática de Structured Data diretamente no website.
