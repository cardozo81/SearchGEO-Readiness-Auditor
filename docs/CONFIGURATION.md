# Configuração

Este documento lista somente configuração suportada pela Stable Local Baseline, incluindo M14.

## Parâmetros de auditoria

Os parâmetros funcionais de auditoria são atualmente expostos pela CLI, não pelo TOML.

| Parâmetro | CLI | Default | Observação |
|---|---|---|---|
| target(s) | argumentos posicionais | — | um domínio/URL mantém modo clássico; dois ou mais valores criam `URL_SET` explícito |
| URLs file | `--urls-file` | nenhum | arquivo UTF-8 com uma URL/domínio por linha; ativa `URL_SET` explícito |
| project | `--project` | hostname/target normalizado | nome humano persistido no Audit |
| language | `--language` | `pt-BR` | contexto primário de conteúdo/reporting |
| market | `--market` | `BR` | contexto de mercado |
| max_pages | `--max-pages` | `100` | deve ser maior que zero e cobrir todo conjunto explícito após deduplicação |
| audits root | `--audits-root` | `audits` | diretório pai dos workspaces |
| AI provider | `--ai-provider` | `none` | `none` ou `openai` |
| AI model | `--ai-model` | nenhum | com OpenAI, use preferencialmente `gpt-5.6-terra`, `gpt-5.6-sol` ou `gpt-5.6-luna` |

### Target e URL_SET

A CLI valida:

- scheme somente `http` ou `https` quando informado;
- hostname/IP/localhost válido;
- ausência de credenciais embutidas na URL;
- porta válida;
- target sem scheme só pode ser domínio/host sem path/query/fragment.

A normalização efetiva ocorre antes da criação do `AuditTarget`.

Para várias URLs posicionais:

```powershell
searchgeo audit `
  "https://example.com/" `
  "https://example.com/produto-a" `
  "https://example.com/produto-b" `
  --max-pages 3
```

Para arquivo:

```powershell
searchgeo audit --urls-file .\urls.txt --max-pages 3
```

Regras operacionais M14:

- entradas explícitas são normalizadas e deduplicadas;
- todas devem pertencer ao mesmo normalized origin;
- origin incompatível é rejeitado antes da aquisição;
- `--urls-file` permanece `URL_SET` mesmo que reste uma única URL única;
- um `URL_SET` cria um único `audit_id`;
- `max_pages` não pode ser menor que o número de URLs únicas explícitas;
- o relatório preserva separadamente quantidade bruta fornecida, universo único normalizado e quantidade efetivamente auditada.

O arquivo aceita linhas em branco e comentários cujo primeiro caractere não branco seja `#`.

### Project

Se `--project` for omitido, o `AuditRunner` usa o hostname do primeiro target normalizado; se isso não estiver disponível, usa o próprio target.

### max_pages

Default: `100`.

No modo clássico de discovery, quando o universo descoberto excede o budget, a auditoria persiste limitação no formato:

```text
MAX_PAGES_REACHED:discovered=<N>;audited=<N>
```

Isso informa cobertura limitada; não representa automaticamente defeito do site.

Em `URL_SET`, o auditor rejeita a execução se `max_pages` for menor que a quantidade de URLs únicas. Nenhuma URL explicitamente fornecida é silenciosamente descartada.

## Configuração de aplicação/logging

O arquivo padrão é `searchgeo.toml` no diretório corrente. A ausência do arquivo padrão é válida.

Conteúdo suportado atualmente:

```toml
[searchgeo]
log_level = "INFO"
```

Níveis válidos:

```text
CRITICAL
ERROR
WARNING
INFO
DEBUG
```

O TOML **não configura target(s), URLs file, project, language, market, max_pages, provider ou model** nesta baseline.

### Selecionar outro arquivo

Por CLI:

```powershell
searchgeo --config .\config\searchgeo.toml audit https://example.com
```

Por ambiente:

```powershell
$env:SEARCHGEO_CONFIG = "C:\config\searchgeo.toml"
```

Se um path for selecionado explicitamente e o arquivo não existir, a CLI encerra com erro.

## Environment variables

| Variável | Uso | Obrigatória |
|---|---|---:|
| `SEARCHGEO_CONFIG` | path do TOML | Não |
| `SEARCHGEO_LOG_LEVEL` | override do `log_level` | Não |
| `SEARCHGEO_OPENAI_MODEL` | model ID da OpenAI | somente se `--ai-provider openai` e `--ai-model` omitido |
| `OPENAI_API_KEY` | credencial do OpenAIProvider | somente para chamada OpenAI efetiva |
| `PLAYWRIGHT_CHROMIUM_EXECUTABLE` | executável Chromium explícito | Não |

`SEARCHGEO_LOG_LEVEL` prevalece sobre TOML.

## OpenAIProvider

### Modelo recomendado

Para a Stable Local Baseline, a configuração operacional recomendada é:

```powershell
$env:OPENAI_API_KEY = "<chave>"
$env:SEARCHGEO_OPENAI_MODEL = "gpt-5.6-terra"
searchgeo audit https://example.com --ai-provider openai
```

Valores recomendados documentados:

| Model ID | Quando usar |
|---|---|
| `gpt-5.6-terra` | default recomendado: equilíbrio entre qualidade e custo |
| `gpt-5.6-sol` | máxima qualidade analítica |
| `gpt-5.6-luna` | menor custo / maior volume |

O valor precisa ser um **model ID da API**, não um nome de plano ChatGPT nem uma categoria genérica.

Não use nesse campo modelos de imagem, realtime, áudio, transcrição, TTS, embeddings ou moderação.

O código atual não contém uma allowlist rígida: outras strings podem ser enviadas à API. Isso **não significa compatibilidade homologada**. Para evitar conflitos, use um dos três model IDs acima, salvo teste explícito com outro modelo.

O model escolhido precisa suportar o contrato técnico usado pelo provider:

- OpenAI Responses API (`/v1/responses`);
- texto;
- Structured Outputs;
- `text.format = json_schema`;
- `strict = true`.

Consulte [AI_GUIDE.md](AI_GUIDE.md) para detalhes, modelos a evitar e procedimento de validação.

### Precedência de configuração

A flag tem precedência sobre a variável de ambiente:

```powershell
searchgeo audit https://example.com `
  --ai-provider openai `
  --ai-model "gpt-5.6-sol"
```

Nesse caso, `gpt-5.6-sol` é usado mesmo que `SEARCHGEO_OPENAI_MODEL` esteja definido com outro valor.

O adapter real possui, internamente:

- endpoint default `https://api.openai.com/v1/responses`;
- timeout default de 45 s por chamada;
- Structured Output em JSON Schema estrito;
- `configuration_version = 1`;
- `prompt_id = searchgeo-semantic-v1`;
- `prompt_version = 1`.

Endpoint, timeout e versões são parâmetros do objeto `OpenAIProvider`, mas **não são flags da CLI da Stable Local Baseline**. Não os documente operacionalmente como configuráveis por usuário final via CLI.

M14 não adiciona outra chamada livre ao LLM para produzir recomendações. A actionability, receita técnica e referências são determinísticas/projetadas de estado persistido; o output semântico M7 continua sendo reutilizado.

## Rendering e evidência visual

O `BrowserRenderer` usa:

- Chromium headless;
- navegação `domcontentloaded`;
- timeout de navegação: 15 s;
- tentativa de `networkidle` limitada a 2 s;
- Desktop 1440×900, DPR 1.0;
- Mobile 412×915, DPR 2.625, `is_mobile` e touch ativados.

M14 também tenta capturar, para cada snapshot renderizado:

- PNG da viewport;
- metadados do viewport e perfil;
- observações DOM de elementos tecnicamente relevantes;
- selector CSS somente quando reproduzível;
- bounding box somente quando o elemento é visível e possui caixa válida.

Esses valores são implementação atual e não possuem flags CLI. RAW HTTP e rendered HTML continuam persistidos separadamente; screenshot não substitui nenhum deles.

## Paths

Default:

```text
./audits/<AUD-ID>/
```

Pode ser alterado somente no nível do diretório pai:

```powershell
searchgeo audit https://example.com --audits-root D:\SearchGEO\audits
```

O nome `<AUD-ID>` é gerado internamente; não existe opção para escolher ID manualmente.

Screenshots M14 são armazenados sob:

```text
artifacts/visual/<page_id>/<device>/<snapshot_id>.png
```

O relatório usa referência relativa ao workspace para manter a pasta/ZIP portátil e não incorpora imagens remotas.

## Configurações previstas versus expostas

A specification define um modelo de configuração mais amplo para evolução do produto. Na Stable Local Baseline, somente os argumentos/variáveis descritos neste documento estão operacionalmente expostos. Não existem, por exemplo, flags para:

- timeout HTTP;
- viewport customizado;
- lista customizada de crawlers;
- pesos de scoring;
- thresholds de consolidação;
- endpoint OpenAI;
- prompt customizado;
- diretório individual de artifacts;
- formato de relatório diferente de HTML;
- desabilitar screenshots isoladamente;
- alterar bounds de `ElementObservation`;
- forçar geração de selector quando não determinável.

Esses itens são **fora da interface operacional atual**, mesmo quando houver parâmetros internos em classes de baixo nível.
