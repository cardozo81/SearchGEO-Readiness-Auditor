# Guia de IA

## Compatibilidade de IA

IA é **opcional**. A Stable Local Baseline funciona sem API key e sem serviço de IA.

Providers implementados:

| Provider | Seleção CLI | Dependência externa | Estado sem credencial |
|---|---|---|---|
| `NoneProvider` | `--ai-provider none` | nenhuma | `NO_AI` suportado |
| `OpenAIProvider` | `--ai-provider openai` | OpenAI Responses API por HTTPS | `NOT_CONFIGURED` / sem penalidade ao site |

Não existe dependência Python `openai`: o adapter usa HTTP da biblioteca padrão.

## Requisito técnico do modelo OpenAI

O campo `--ai-model` / `SEARCHGEO_OPENAI_MODEL` **não aceita qualquer tipo de modelo de IA de forma segura**. O `OpenAIProvider` desta baseline usa simultaneamente:

1. endpoint `POST /v1/responses`;
2. entrada e saída textual;
3. Structured Outputs por `text.format`;
4. `type = json_schema`;
5. `strict = true`;
6. o JSON Schema definido pelo próprio auditor.

Portanto, o operador deve selecionar um modelo de texto compatível com **Responses API + Structured Outputs/JSON Schema estrito**.

Modelos de imagem, áudio, transcrição, TTS, realtime, embeddings, moderação e outros modelos especializados **não devem ser preenchidos** em `--ai-model`.

## Modelos recomendados para esta baseline

Compatibilidade documental revisada em **2026-09-02** contra a documentação pública atual da OpenAI. A família GPT-5.6 é a família geral atual indicada pela OpenAI e está disponível pela Responses API.

Use preferencialmente um dos valores abaixo:

| Valor exato a preencher | Uso recomendado no SearchGEO | Observação operacional |
|---|---|---|
| `gpt-5.6-terra` | **recomendado como default operacional** | equilíbrio entre qualidade e custo para análise semântica em volume |
| `gpt-5.6-sol` | máxima qualidade | usar quando qualidade analítica for mais importante que custo |
| `gpt-5.6-luna` | menor custo / maior volume | usar quando custo for o principal limitador; validar qualidade no smoke test |

### Recomendação padrão

Para evitar dúvida na instalação inicial, configure:

```powershell
$env:SEARCHGEO_OPENAI_MODEL = "gpt-5.6-terra"
```

ou por execução:

```powershell
searchgeo audit https://example.com `
  --ai-provider openai `
  --ai-model "gpt-5.6-terra"
```

### Alias `gpt-5.6`

A documentação atual da OpenAI publica `gpt-5.6` como alias de GPT-5.6 Sol. O auditor tecnicamente aceita esse valor como string de modelo, mas para operação e troubleshooting deste projeto prefira o ID explícito:

```text
gpt-5.6-sol
```

Isso deixa claro qual perfil foi escolhido no handoff e nos registros operacionais.

## Outros modelos OpenAI

O código **não possui allowlist interna de nomes de modelo**: qualquer string não vazia pode chegar ao endpoint. Isso não equivale a suporte homologado.

Modelos anteriores ou alternativos podem funcionar se, na conta/região utilizada, suportarem exatamente o contrato exigido pelo auditor. Entretanto, para evitar conflito de compatibilidade, esta documentação considera **fora da configuração recomendada da Stable Local Baseline** qualquer modelo que não seja um dos três GPT-5.6 listados acima.

Se houver necessidade de usar outro modelo, trate-o como configuração não homologada e valide antes do uso real:

- disponibilidade do model ID na conta;
- suporte a `/v1/responses`;
- suporte a `text.format = json_schema`;
- suporte a `strict = true`;
- resposta válida para o schema do SearchGEO;
- comportamento da auditoria em `FULL` sem `AI_PROVIDER_UNAVAILABLE`.

## Valores que não devem ser usados

Não preencha `SEARCHGEO_OPENAI_MODEL` / `--ai-model` com nomes de produtos ou categorias que não sejam model IDs válidos para o contrato acima.

Exemplos de categorias inadequadas para este campo:

- modelos `gpt-image-*`;
- modelos `gpt-realtime-*`;
- modelos de transcrição;
- modelos de TTS;
- modelos `text-embedding-*`;
- modelos de moderação;
- nomes de planos ChatGPT, como `Plus`, `Pro`, `Business` ou `Enterprise`;
- nomes informais como `ChatGPT`, `GPT latest`, `OpenAI` ou `auto`.

O valor deve ser um **model ID da API**, por exemplo:

```text
gpt-5.6-terra
```

## O que a IA faz

O provider semântico produz avaliações auxiliares para regras `BR-GEO-028..049`. O scoring oficial é executado posteriormente pelo `ScoringEngine` determinístico.

## O que a IA não faz

O LLM não:

- calcula o Score oficial;
- escolhe pesos de scoring;
- muda fatores PASS/WARNING/FAIL;
- garante ranking/citação/tráfego;
- inventa evidências aceitas pelo pipeline;
- substitui o contrato das Business Rules.

# Configurar OpenAI — passo a passo

## 1. Confirmar dependências locais

Antes de habilitar IA, confirme Python/package/Chromium:

```powershell
python --version
searchgeo --version
python -m pip show playwright
```

Se alguma dependência estiver ausente, siga [INSTALLATION.md](INSTALLATION.md), seção **Instalar dependências ausentes no Windows**.

## 2. Confirmar conectividade HTTPS

A máquina precisa ter egress HTTPS para o serviço externo. Em ambientes com proxy/firewall corporativo, valide a política antes do smoke test.

A baseline não possui flag própria de proxy.

## 3. Definir API key no ambiente

No PowerShell da sessão que executará a auditoria:

```powershell
$env:OPENAI_API_KEY = "<chave>"
```

Valide **sem imprimir o valor**:

```powershell
Test-Path Env:OPENAI_API_KEY
```

O resultado esperado é `True`.

Não use:

```powershell
Write-Output $env:OPENAI_API_KEY
```

em logs de homologação.

## 4. Definir o modelo

### Configuração recomendada

```powershell
$env:SEARCHGEO_OPENAI_MODEL = "gpt-5.6-terra"
```

Alternativas suportadas pela orientação operacional atual:

```text
gpt-5.6-sol
gpt-5.6-terra
gpt-5.6-luna
```

Opção A — variável de ambiente:

```powershell
$env:SEARCHGEO_OPENAI_MODEL = "gpt-5.6-terra"
```

Valide:

```powershell
$env:SEARCHGEO_OPENAI_MODEL
```

Opção B — flag por execução:

```powershell
--ai-model "gpt-5.6-terra"
```

`--ai-model` tem precedência sobre `SEARCHGEO_OPENAI_MODEL`.

## 5. Executar com OpenAI

Com model na variável:

```powershell
searchgeo audit https://example.com --ai-provider openai
```

Com model na CLI:

```powershell
searchgeo audit https://example.com `
  --ai-provider openai `
  --ai-model "gpt-5.6-terra"
```

Se `--ai-provider openai` for selecionado sem model em nenhuma das duas fontes, a CLI rejeita a execução antes da auditoria.

## 6. Verificar o modo resultante

Após a execução, consulte o relatório e o Audit persistido:

- `FULL`: provider disponível e respostas válidas no universo aplicável;
- `DEGRADED`: parte da análise semântica ficou indisponível/rejeitada;
- `NO_AI`: provider não configurado/NoneProvider.

`DEGRADED` e `NO_AI` podem reduzir Coverage/Confidence/Consolidation, mas não são FAIL do website.

Se a execução com OpenAI resultar em `DEGRADED` ou `AI_PROVIDER_UNAVAILABLE`, confira primeiro:

1. API key;
2. model ID digitado exatamente;
3. disponibilidade do modelo na conta/região;
4. conectividade HTTPS;
5. compatibilidade do modelo com Responses API e Structured Outputs estrito.

## 7. Desabilitar IA

A forma explícita e suportada é:

```powershell
searchgeo audit https://example.com --ai-provider none
```

Esse também é o default.

Para remover a credencial da sessão PowerShell:

```powershell
Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
Remove-Item Env:SEARCHGEO_OPENAI_MODEL -ErrorAction SilentlyContinue
```

# Providers implementados

## NoneProvider

Provider obrigatório de fallback. Retorna:

```text
state = NOT_CONFIGURED
reason = AI_NOT_CONFIGURED
```

A auditoria segue em modo `NO_AI` quando não há provider semântico configurado.

## OpenAIProvider

Adapter implementado sobre OpenAI Responses API.

Defaults internos:

- endpoint: `https://api.openai.com/v1/responses`;
- timeout: 45 s;
- configuration version: `1`;
- prompt id: `searchgeo-semantic-v1`;
- prompt version: `1`;
- Structured Output: JSON Schema estrito (`strict=true`).

Endpoint, timeout e versões são parâmetros internos do provider e **não são flags CLI da Stable Local Baseline**.

# Segurança da API key

- A key é obtida por argumento interno do provider ou `OPENAI_API_KEY`.
- A CLI não aceita key como flag.
- Não coloque key em `searchgeo.toml`.
- Não grave key no repositório, artifacts, fixtures ou scripts versionados.
- A key é usada no header `Authorization` da chamada HTTP.
- O provider não inclui a key no payload semântico.
- Report/payloads exibidos possuem redaction defensiva para nomes sensíveis.

# Dados enviados externamente

Quando OpenAI é efetivamente usado, o payload semântico pode incluir, para cada snapshot:

- `snapshot_id`;
- URL da página;
- title;
- conteúdo principal extraído;
- Dados Estruturados extraídos;
- idioma primário;
- mercado;
- Evidence fornecida ao provider, incluindo ID, tipo, source, observed value e artifact reference.

A instrução enviada ao provider exige `UNKNOWN` quando a evidência for insuficiente e proíbe inventar evidence IDs.

Ao habilitar OpenAI, considere que **conteúdo do site auditado e evidências derivadas podem ser transmitidos ao serviço externo**. A política de dados da organização deve autorizar esse envio.

# Dados que permanecem locais

A persistência primária continua local:

- `audit.db`;
- RAW HTTP artifacts;
- rendered HTML;
- extrações;
- RuleExecutions;
- Findings;
- Scores;
- Recommendations;
- `report.html`.

O provider recebe o payload construído para a análise semântica, não o `audit.db` inteiro como arquivo.

# Schema validation

A resposta aceita precisa obedecer schema rígido, incluindo:

- assessments somente para `BR-GEO-028..049`;
- resultado permitido;
- confidence entre 0 e 1;
- evidence IDs;
- reasoning summary;
- observed value estruturado;
- entidades tipadas;
- no máximo 5 secondary intents;
- nenhum campo inesperado.

O provider não pode publicar `ERROR` como avaliação da qualidade do website.

# Evidence validation

Todo `evidence_id` retornado precisa pertencer ao conjunto fornecido naquela chamada.

Se a resposta referenciar evidence inexistente/inventada, ela é rejeitada por `SemanticEvidenceError` e não é transformada em finding válido.

Resultados diferentes de `UNKNOWN`/`NOT_APPLICABLE` exigem source evidence. Entity observations também exigem evidence.

# Fallback e estados

## FULL

Provider configurado, disponível e produzindo respostas válidas no universo aplicável.

## DEGRADED

Provider selecionado, mas parte das análises fica indisponível/rejeitada. Falha HTTP, timeout, schema inválido, evidence inválida, JSON inválido etc. não viram FAIL do site; a análise correspondente degrada.

## NO_AI

Nenhum provider configurado ou `NoneProvider`. Regras semantic-only sem fallback determinístico ficam `UNKNOWN`.

# Impacto em Coverage, Confidence e Consolidation

Ausência/indisponibilidade de IA pode reduzir a quantidade de regras efetivamente avaliadas. Isso pode reduzir:

- Coverage;
- Confidence;
- Consolidation;
- possibilidade de calcular Overall.

Isso representa **limitação da auditoria**, não baixa qualidade do site. O ScoringEngine não converte `UNKNOWN` em zero.

# Falha do provider

Erros capturados pelo adapter retornam estado `UNAVAILABLE` com motivo do tipo:

```text
AI_PROVIDER_UNAVAILABLE:<ErrorType>
```

A estratégia é fail-safe: preservar rastreabilidade e reduzir capacidade analítica em vez de publicar conclusão negativa sem evidência.

<!-- M18_MULTI_AI_PROVIDER_ROUTING -->
## M18 — Multi-AI Provider, routing e telemetria
Providers de runtime: `OPENAI`, `DEEPSEEK`, `MIMO`, `NONE`; `AUTO` usa somente providers com API key e configuração válida, em ordem determinística de confiabilidade SearchGEO. Provider explícito não faz failover cruzado. Após falha em AUTO o provider fica `QUARANTINED_FOR_AUDIT`; o primeiro resultado válido fixa o provider da URL para Desktop/Mobile. A mesma URL nunca recebe duas análises válidas de providers diferentes.

| Provider | Modelo | Profundidade recomendada | Structured Output | Responses API | Classe | Qualificação | Uso |
|---|---|---|---|---|---|---|---|
| OPENAI | gpt-5.6-sol | HIGH/XHIGH | SIM | SIM | A+ | QUALIFIED | máxima qualidade |
| OPENAI | gpt-5.6-terra | HIGH | SIM | SIM | A | QUALIFIED | default |
| DEEPSEEK | deepseek-v4-pro | HIGH | SIM | SIM | A- | PROVISIONAL | alternativa forte |
| MIMO | mimo-v2.5-pro | thinking enabled | SIM | SIM | B+ | PROVISIONAL | alternativa forte |
| OPENAI | gpt-5.6-luna | HIGH | SIM | SIM | B+ | QUALIFIED | volume/custo |
| DEEPSEEK | deepseek-v4-flash | HIGH | SIM | SIM | B | PROVISIONAL | volume/custo |
| MIMO | mimo-v2.5 | thinking enabled | SIM | SIM | B | PROVISIONAL | volume/multimodal |

“Confiabilidade SearchGEO” é política inicial de adequação ao contrato específico do auditor, não benchmark científico geral. DeepSeek/MiMo permanecem PROVISIONAL até SearchGEO Provider Benchmark. MiMo normaliza LOW/MEDIUM/HIGH para `THINKING_ENABLED`; não se afirma profundidade relativa entre esses níveis.
