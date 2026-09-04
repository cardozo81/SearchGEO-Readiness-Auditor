# Variáveis de ambiente — referência completa

Referência operacional da superfície de variáveis reconhecida pelo console do SearchGEO Readiness Auditor.

Verificação documental: **2026-09-04**. Para credenciais e endpoints externos, as instruções abaixo foram conferidas contra documentação pública oficial dos respectivos provedores.

## Regra de uso

Variável de ambiente é uma camada de **override avançado**, não uma lista de 45 campos obrigatórios. Quando existe default seguro, o SearchGEO aplica esse default internamente e o novo menu mostra `default efetivo` mesmo que a variável não exista no sistema operacional.

Isso é intencional: materializar todos os defaults no ambiente criaria configuração redundante e poderia transformar um default opcional em obrigação. O caso mais importante é `SEARCHGEO_CONFIG`: sem a variável, `searchgeo.toml` é opcional; se a variável for definida, o arquivo indicado passa a ser explicitamente exigido.

No console:

```text
E. Variáveis de ambiente
  1. Aplicação e execução
  2. IA — credenciais
  3. IA — modelos e reasoning
  4. IA — endpoints avançados
  5. Web Performance / Google APIs
  6. Synthetic Apdex
  7. Browser / Playwright
  A. Todas as variáveis
  D. Abrir esta documentação detalhada
```

Ao selecionar uma variável, o console informa finalidade, tipo, domínio aceito, default, dependências, sensibilidade, custo/impacto, exemplo e origem do dado. Para enums, a seleção é guiada; não é necessário memorizar valores.

## Segurança

- API keys, tokens, senhas e credentials nunca são exibidos em claro no menu; aparecem como `[SET]`.
- Secrets inseridos no console são voláteis à sessão e não são gravados em `searchgeo-console.ini`.
- Não grave chaves em Git, README, issue, screenshot, log ou arquivo versionado.
- O fato de uma chave existir não prova saldo, quota, plano compatível ou acesso ao modelo.
- O console valida domínios conhecidos antes de aceitar o override.

## 1. Aplicação e execução

| Variável | Para que serve | Tipo / valores | Default efetivo | Quando definir | Impacto |
|---|---|---|---|---|---|
| `SEARCHGEO_CONFIG` | força um TOML geral, hoje usado principalmente para logging | caminho para arquivo existente | `searchgeo.toml` é procurado opcionalmente quando a variável não existe | apenas para usar um TOML específico | sem custo; se a variável existir e o arquivo não existir, a configuração é inválida |
| `SEARCHGEO_LOG_LEVEL` | controla verbosidade do log | `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG` | `INFO` | somente para alterar verbosidade | `DEBUG` aumenta volume de log local |
| `SEARCHGEO_DEVICE_CONTEXT` | default do contexto de dispositivo | `mobile`, `desktop`, `both` | `mobile` | quando não quiser definir pelo menu/CLI | `both` multiplica contextos e pode ampliar tempo/chamadas externas |
| `SEARCHGEO_AI_TIMEOUT_SECONDS` | timeout de cada tentativa de IA | número finito `>0`, segundos | `180` | override de timeout | não cria chamadas; timeout não garante que o provider não tenha processado/faturado a chamada |
| `SEARCHGEO_AI_CONTENT_REMEDIATION` | default da remediação textual por IA | `true` / `false` | `false` | somente para ligar por ambiente | `true` pode gerar chamadas adicionais de IA |

### `SEARCHGEO_CONFIG`

Exemplo:

```powershell
$env:SEARCHGEO_CONFIG = "C:\searchgeo\searchgeo.toml"
```

Defina somente se o arquivo já existir. Se não precisa de TOML próprio, deixe a variável ausente e use os defaults do programa/INI do console.

## 2. IA — credenciais

As sete credenciais abaixo são secrets. Não possuem default.

| Variável | Provider | Obrigatória quando | Observação operacional |
|---|---|---|---|
| `OPENAI_API_KEY` | OpenAI | `--ai-provider openai`; em `auto`, torna OpenAI elegível | uso da API é separado de assinatura ChatGPT |
| `DEEPSEEK_API_KEY` | DeepSeek | `--ai-provider deepseek`; em `auto`, torna DeepSeek elegível | saldo insuficiente pode retornar HTTP 402 |
| `MIMO_API_KEY` | Xiaomi MiMo | `--ai-provider mimo`; em `auto`, torna MiMo elegível | adapter atual exige **PAYG `sk-...`**; Token Plan `tp-...` não é intercambiável |
| `XAI_API_KEY` | xAI / Grok | `--ai-provider xai`/`grok` | provider explicit-only no SearchGEO atual |
| `DASHSCOPE_API_KEY` | Alibaba Qwen | `--ai-provider qwen` | provider explicit-only; endpoint default atual é DashScope US |
| `GEMINI_API_KEY` | Google Gemini | `--ai-provider gemini` | provider explicit-only; use chave atual compatível com Gemini API |
| `ANTHROPIC_API_KEY` | Anthropic Claude | `--ai-provider anthropic`/`claude` | provider explicit-only; Console/API é produto separado de claude.ai |

### Como obter `OPENAI_API_KEY`

Fonte oficial: <https://help.openai.com/pt-br/articles/4936850> e <https://platform.openai.com/api-keys>.

1. Entre na OpenAI Platform.
2. Se sua organização usa projetos, selecione o projeto que deve concentrar uso, limites e billing do SearchGEO.
3. Abra **API Keys**.
4. Selecione **Create new secret key**.
5. Defina as permissões adequadas ao projeto; a integração do SearchGEO precisa conseguir chamar o endpoint/modelo configurado.
6. Copie a chave no momento da criação; a OpenAI informa que o segredo completo não fica disponível novamente depois.
7. Confirme billing/créditos, limites e permissão do modelo no mesmo projeto.
8. No SearchGEO, use `E > IA — credenciais > OPENAI_API_KEY` ou configure a variável na sessão do PowerShell.

### Como obter `DEEPSEEK_API_KEY`

Fontes oficiais: <https://api-docs.deepseek.com/> e link de API key da própria documentação para <https://platform.deepseek.com/api_keys>.

1. Entre na DeepSeek Platform.
2. Abra a área de **API Keys**.
3. Crie uma nova API key e copie-a para armazenamento seguro.
4. Verifique o saldo/Top up antes de testar. A documentação oficial classifica HTTP `402` como saldo insuficiente.
5. Configure `DEEPSEEK_API_KEY`.
6. O SearchGEO usa os modelos homologados no registry; não cole o nome de um modelo não listado no menu.

### Como obter `MIMO_API_KEY`

Fonte oficial: <https://mimo.mi.com/docs/en-US/quick-start/faq/api-integration>.

1. Entre na Xiaomi MiMo API Open Platform.
2. Para o adapter atual do SearchGEO, escolha **Pay-as-you-go API Calls**.
3. Abra **Console > API Keys** e crie uma chave PAYG.
4. Confirme que a chave começa com `sk-`.
5. Configure `MIMO_API_KEY` com essa chave.
6. Não use uma chave Token Plan `tp-...` no adapter PAYG atual. A documentação MiMo declara que os dois tipos usam produtos/base URLs diferentes e não podem ser misturados.

O endpoint PAYG usado pelo adapter atual é `https://api.xiaomimimo.com/v1/responses`.

### Como obter `XAI_API_KEY`

Fonte oficial: <https://docs.x.ai/developers/quickstart>.

1. Crie/acesse a conta em <https://console.x.ai/>.
2. Adicione créditos à conta/equipe quando necessário; o quickstart oficial orienta carregar créditos antes do uso.
3. Abra a página **API Keys**.
4. Crie a chave e copie o segredo no momento da criação.
5. Configure `XAI_API_KEY`.
6. O SearchGEO usa por default o endpoint Responses `https://api.x.ai/v1/responses`.

### Como obter `DASHSCOPE_API_KEY` para Qwen

Fonte oficial: <https://www.alibabacloud.com/help/en/model-studio/first-api-call-to-qwen>.

1. Crie/acesse uma conta Alibaba Cloud.
2. Abra o Alibaba Cloud Model Studio.
3. Aceite os termos/ative o Model Studio se solicitado.
4. Abra a página **API Key**.
5. Selecione **Create API key**; não é necessário escolher o modelo durante a criação da chave.
6. Copie a chave e configure `DASHSCOPE_API_KEY`.
7. O adapter atual usa por default o endpoint US `https://dashscope-us.aliyuncs.com/compatible-mode/v1/chat/completions`. Se sua organização exige outra região, trate `SEARCHGEO_QWEN_ENDPOINT` como override avançado e valide a compatibilidade oficial antes de alterar.

### Como obter `GEMINI_API_KEY`

Fonte oficial atual: <https://ai.google.dev/gemini-api/docs/api-key> e <https://aistudio.google.com/apikey>.

1. Entre no Google AI Studio.
2. Abra **Dashboard > Projects** e escolha/importe o Google Cloud project que deve concentrar a API.
3. Abra **API Keys**.
4. Selecione **Create API key**.
5. Copie a nova chave e configure `GEMINI_API_KEY`.
6. Confirme quota/billing no projeto quando usar tier pago.

A documentação do Gemini atualizada em 2026-09-02 informa que novas chaves criadas no AI Studio são **auth keys** e que a migração para esse formato é obrigatória em setembro de 2026. Para uma instalação atual do SearchGEO, não crie uma nova dependência em chave Standard legada.

### Como obter `ANTHROPIC_API_KEY`

Fontes oficiais: <https://support.anthropic.com/pt/articles/8114521-como-posso-acessar-a-api-da-anthropic> e <https://console.anthropic.com/>.

1. Crie/acesse a conta no Anthropic API Console.
2. Garanta uma função com permissão para gerenciar API keys (por exemplo Developer/Admin, conforme a política da organização).
3. Configure créditos/billing da organização do Console quando necessário.
4. Abra a área de API keys e crie a chave.
5. Copie o segredo e configure `ANTHROPIC_API_KEY`.
6. Não assuma que uma assinatura paga do claude.ai inclui créditos de API; a Anthropic documenta esses produtos separadamente.

## 3. IA — modelos e reasoning

Essas variáveis são overrides. Se ausentes, o SearchGEO aplica o modelo mais simples definido pela política pública atual e o menor esforço suportado.

| Variável | Valores aceitos no registry atual | Default efetivo |
|---|---|---|
| `SEARCHGEO_OPENAI_MODEL` | `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna` | `gpt-5.6-luna` |
| `SEARCHGEO_OPENAI_REASONING_EFFORT` | `NONE`, `LOW`, `MEDIUM`, `HIGH`, `XHIGH`, `MAX` | `NONE` |
| `SEARCHGEO_DEEPSEEK_MODEL` | `deepseek-v4-pro`, `deepseek-v4-flash` | `deepseek-v4-flash` |
| `SEARCHGEO_DEEPSEEK_REASONING_EFFORT` | `NONE`, `LOW`, `HIGH`, `MAX` | `NONE` |
| `SEARCHGEO_MIMO_MODEL` | `mimo-v2.5-pro`, `mimo-v2.5` | `mimo-v2.5` |
| `SEARCHGEO_MIMO_REASONING_EFFORT` | `NONE`, `LOW`, `MEDIUM`, `HIGH` | `NONE` |
| `SEARCHGEO_XAI_MODEL` | `grok-4.6` | `grok-4.6` |
| `SEARCHGEO_XAI_REASONING_EFFORT` | `LOW`, `MEDIUM`, `HIGH`, `XHIGH` | `LOW` |
| `SEARCHGEO_QWEN_MODEL` | `qwen3.8-max`, `qwen3.8-flash` | `qwen3.8-flash` |
| `SEARCHGEO_GEMINI_MODEL` | `gemini-3.8-flash` | `gemini-3.8-flash` |
| `SEARCHGEO_GEMINI_REASONING_EFFORT` | `LOW`, `MEDIUM`, `HIGH` | `LOW` |
| `SEARCHGEO_ANTHROPIC_MODEL` | `claude-sonnet-5` | `claude-sonnet-5` |
| `SEARCHGEO_ANTHROPIC_REASONING_EFFORT` | `LOW`, `MEDIUM`, `HIGH`, `XHIGH`, `MAX` | `LOW` |

Qwen não possui variável de reasoning no contrato atual porque o adapter mantém `PROVIDER_DEFAULT`; não invente uma variável `SEARCHGEO_QWEN_REASONING_EFFORT`.

### Regra de configuração

- No console, prefira configurar provider/modelo/esforço pela opção **4. IA**.
- Use as variáveis acima para AUTO, automação externa ou override avançado.
- O menu só aceita modelos declarados no registry; um nome fora da lista é rejeitado antes da execução.
- Esforço maior pode aumentar latência, tokens e custo. O default público privilegia o menor nível efetivamente suportado.

## 4. IA — endpoints avançados

Somente providers extension expõem override de endpoint. No uso normal, **não defina essas variáveis**.

| Variável | Default embutido | Tipo | Uso |
|---|---|---|---|
| `SEARCHGEO_XAI_ENDPOINT` | `https://api.x.ai/v1/responses` | URL HTTP(S) absoluta | proxy/endpoint xAI compatível explicitamente controlado |
| `SEARCHGEO_QWEN_ENDPOINT` | `https://dashscope-us.aliyuncs.com/compatible-mode/v1/chat/completions` | URL HTTP(S) absoluta | alteração de endpoint/região Qwen compatível |
| `SEARCHGEO_GEMINI_ENDPOINT` | `https://generativelanguage.googleapis.com/v1beta/interactions` | URL HTTP(S) absoluta | endpoint Gemini Interactions compatível |
| `SEARCHGEO_ANTHROPIC_ENDPOINT` | `https://api.anthropic.com/v1/messages` | URL HTTP(S) absoluta | endpoint Messages compatível |

Risco: um endpoint incorreto pode causar falha, enviar dados a destino indevido ou gerar cobrança em serviço diferente. O console valida ao menos que o valor seja URL absoluta `http://` ou `https://`, mas compatibilidade funcional continua sendo responsabilidade do endpoint escolhido.

## 5. Web Performance / Google APIs

| Variável | Para que serve | Tipo / domínio | Default efetivo | Dependência / impacto |
|---|---|---|---|---|
| `SEARCHGEO_WEB_PERFORMANCE` | habilita PageSpeed/Lighthouse/CrUX por ambiente | booleano | `false` | `true` consome integração/quota externa |
| `SEARCHGEO_WEB_PERFORMANCE_MAX_PAGES` | teto de páginas enviadas às APIs | inteiro `>=0`; `0=todas` | `10` | multiplica chamadas potenciais |
| `SEARCHGEO_WEB_PERFORMANCE_TIMEOUT_SECONDS` | timeout por request externo | número `>0` | `120` | não cria request adicional |
| `SEARCHGEO_WEB_PERFORMANCE_FIELD_SOURCE` | política de field data | `auto`, `pagespeed`, `crux`, `none` | `auto` | `crux` exige `SEARCHGEO_CRUX_API_KEY` |
| `SEARCHGEO_LIGHTHOUSE_CATEGORIES` | categorias solicitadas ao Lighthouse remoto | CSV com `performance`, `accessibility`, `best-practices`, `seo` | as quatro | o console rejeita categoria desconhecida ou duplicada |
| `SEARCHGEO_PAGESPEED_API_KEY` | autenticação/quota PageSpeed | secret | nenhum | opcional para uso ad hoc; recomendada para automação recorrente |
| `SEARCHGEO_CRUX_API_KEY` | autenticação CrUX direta | secret | nenhum | obrigatória para chamada CrUX direta |

### Como obter as chaves Google

O passo a passo completo e específico para restrições, APIs habilitadas, IP de saída e rotação está em [GOOGLE_API_KEYS.md](GOOGLE_API_KEYS.md).

Resumo:

1. Abra <https://console.cloud.google.com/> e selecione/crie o projeto.
2. Em **APIs & Services > Library**, habilite **PageSpeed Insights API** e/ou **Chrome UX Report API**.
3. Em **APIs & Services > Credentials**, crie a API key.
4. Restrinja cada chave à API correspondente; para a CLI, não use HTTP referrer como substituto de uma restrição apropriada.
5. Prefira duas chaves separadas (`searchgeo-pagespeed` e `searchgeo-crux`).
6. Configure as variáveis pelo console ou ambiente.

## 6. Synthetic Apdex

Synthetic Apdex está OFF por default. Seus parâmetros de tuning não precisam ser definidos enquanto a feature estiver desligada.

| Variável | Finalidade | Tipo / domínio | Default quando aplicável | Impacto |
|---|---|---|---|---|
| `SEARCHGEO_SYNTHETIC_APDEX` | habilita a medição | booleano | `false` | gera navegações reais repetidas contra o alvo |
| `SEARCHGEO_APDEX_THRESHOLD_SECONDS` | threshold T | número `>0` | **sem default** | obrigatório quando Apdex está ON |
| `SEARCHGEO_APDEX_SAMPLES_PER_CONTEXT` | amostras válidas por URL/device | inteiro `>=1` | `100` | maior valor aumenta carga/duração |
| `SEARCHGEO_APDEX_MAX_ATTEMPTS_PER_CONTEXT` | teto de reposição de amostras inválidas | inteiro `>= samples` | `ceil(1.25 × samples)` | teto direto de navegações |
| `SEARCHGEO_APDEX_MAX_PAGES` | páginas medidas | inteiro `>=0`; `0=todas` | `1` | multiplica contextos |
| `SEARCHGEO_APDEX_TIMEOUT_SECONDS` | timeout por navegação | número `>0` e efetivamente `>4T` | `max(45, 4T+5)` | valor baixo demais trunca a faixa Frustrated |
| `SEARCHGEO_APDEX_DELAY_SECONDS` | intervalo mínimo entre inícios | número `>=0` | `1` | maior delay reduz pressão e aumenta duração |
| `SEARCHGEO_APDEX_CONCURRENCY` | workers simultâneos | `1` ou `2` | `1` | `2` aumenta carga concorrente |

Para configuração normal, use **11. Synthetic Apdex** no menu principal: a tela calcula valores derivados e explica carga projetada. Use as variáveis somente para automação/override.

## 7. Browser / Playwright

### `PLAYWRIGHT_CHROMIUM_EXECUTABLE`

- **Finalidade:** indicar um executável Chromium específico.
- **Tipo:** caminho para arquivo existente.
- **Default:** nenhum override; Playwright/SearchGEO usa sua descoberta/instalação normal.
- **Quando definir:** somente quando houver necessidade de fixar um Chromium externo.
- **Validação:** o console rejeita caminho que não seja arquivo existente.
- **Custo:** nenhum custo externo direto; afeta apenas execução local/rendering.

Exemplo:

```powershell
$env:PLAYWRIGHT_CHROMIUM_EXECUTABLE = "C:\Program Files\Chromium\chrome.exe"
```

## Defaults iniciais da aplicação

Uma instalação nova do console já nasce utilizável sem preencher 45 variáveis. O `searchgeo-console.ini` é criado com defaults não sensíveis e a camada de runtime possui defaults adicionais. A configuração mínima para uma auditoria local sem IA e sem APIs externas é essencialmente informar o alvo.

Defaults principais:

```text
device                         = mobile
ai-provider                    = none
ai timeout                     = 180 s
ai content remediation         = false
web performance                = false
web performance max pages      = 10
web performance timeout        = 120 s
field source                   = auto
lighthouse categories          = performance,accessibility,best-practices,seo
synthetic apdex                = false
language                       = pt-BR
market                         = BR
max-pages                      = 100
audits-root                    = audits
```

Os modelos e reasoning defaults são os da tabela de IA acima. **Credenciais nunca recebem default**.

## Exemplos no PowerShell

### Sessão atual

```powershell
$env:OPENAI_API_KEY = "<chave>"
$env:SEARCHGEO_OPENAI_MODEL = "gpt-5.6-luna"
$env:SEARCHGEO_OPENAI_REASONING_EFFORT = "NONE"
```

### Remover override

```powershell
Remove-Item Env:SEARCHGEO_OPENAI_MODEL -ErrorAction SilentlyContinue
```

Ao remover um override com default conhecido, o SearchGEO volta ao default interno; não é necessário recriar a variável com o valor default.

## Fontes oficiais externas verificadas

- OpenAI API keys: <https://help.openai.com/pt-br/articles/4936850>
- OpenAI projects/API keys: <https://help.openai.com/en/articles/9186755>
- DeepSeek quick start/API key: <https://api-docs.deepseek.com/>
- DeepSeek erros/balance: <https://api-docs.deepseek.com/quick_start/error_codes/>
- Xiaomi MiMo API key e diferença PAYG/Token Plan: <https://mimo.mi.com/docs/en-US/quick-start/faq/api-integration>
- xAI quickstart/API key: <https://docs.x.ai/developers/quickstart>
- Alibaba Cloud Model Studio/Qwen API key: <https://www.alibabacloud.com/help/en/model-studio/first-api-call-to-qwen>
- Google Gemini API keys: <https://ai.google.dev/gemini-api/docs/api-key>
- Anthropic API access: <https://support.anthropic.com/pt/articles/8114521-como-posso-acessar-a-api-da-anthropic>
- Google PageSpeed/CrUX: veja [GOOGLE_API_KEYS.md](GOOGLE_API_KEYS.md).
