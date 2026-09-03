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

A seleção limita M3 aos snapshots escolhidos. M7 recebe apenas os snapshots existentes e, portanto, chamadas de IA são feitas somente para os dispositivos selecionados. `mobile` é o default para reduzir custo e tempo quando comparação Desktop × Mobile não é necessária.

Chamadas internas diretas a M3 sem a variável continuam usando ambos os dispositivos por compatibilidade interna.

## Configuração de IA

### Desabilitada

```powershell
searchgeo audit https://example.com --ai-provider none
```

Nenhuma API externa é chamada.

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

Deve ser número finito > 0. Com `--ai-provider none`, não existe chamada externa e o timeout não tem efeito prático. Timeout não gera retry automático.

## Provider selecionado sem credencial

Provider explícito:

- fica `NOT_CONFIGURED`;
- nenhuma chamada externa é realizada;
- a auditoria segue com capacidade semântica reduzida;
- ausência das chaves dos outros providers não interfere.

AUTO:

- provider sem chave não entra na cadeia;
- se nenhum for elegível, nenhuma chamada externa é feita.

## Dispositivo × IA

Para uma auditoria de uma página:

```text
mobile  -> no máximo um contexto semântico externo da página
 desktop -> no máximo um contexto semântico externo da página
both    -> até dois contextos, Mobile e Desktop
```

O número real depende de snapshots disponíveis, provider habilitado, quarantine, URL lock e resultados anteriores.

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
├─ ai-usage.html
├─ references.html
└─ css/
   └─ site.css
```

`mobile.html` e `desktop.html` somente são materializados quando o dispositivo correspondente foi auditado.

A telemetria de IA fica em `ai-usage.html`; não é misturada aos findings do website.

## Configurações não expostas como promessa de produto

Não há atualmente configuração pública para:

- serviço web/backend;
- banco remoto;
- Docker daemon;
- execução distribuída;
- retry automático de IA;
- geração automática de conteúdo por IA.

A futura sugestão opcional de conteúdo por IA está fora do baseline atual e deve permanecer desligada por padrão quando implementada.
