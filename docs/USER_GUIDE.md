# Guia do Usuário

Este guia descreve o uso da baseline atual do SearchGEO Readiness Auditor. Para a lista exaustiva dos parâmetros, consulte [CLI_REFERENCE.md](CLI_REFERENCE.md).

# Preparar o terminal

No Windows PowerShell:

```powershell
cd C:\caminho\SearchGEO-Readiness-Auditor
.\.venv\Scripts\Activate.ps1
searchgeo --version
searchgeo audit --help
```

Se o ambiente não estiver instalado, siga [INSTALLATION.md](INSTALLATION.md).

# Executar uma URL

```powershell
searchgeo audit https://example.com --project "Projeto Exemplo"
```

Também é aceito domínio sem scheme:

```powershell
searchgeo audit example.com
```

Quando houver path/query/fragment, informe `http://` ou `https://`.

# Executar várias URLs no mesmo audit

```powershell
searchgeo audit `
  https://example.com/ `
  https://example.com/produto-a `
  https://example.com/produto-b `
  --project "Projeto Exemplo"
```

As URLs explícitas são normalizadas/deduplicadas e pertencem ao mesmo `audit_id`. O conjunto deve respeitar as regras de origem da auditoria.

# Executar por arquivo

`urls.txt`:

```text
# páginas principais
https://example.com/
https://example.com/produto-a
https://example.com/produto-b
```

Execução:

```powershell
searchgeo audit --urls-file .\urls.txt --project "Projeto Exemplo"
```

Linhas vazias e comentários iniciados por `#` são ignorados. `--urls-file` caracteriza `URL_SET`, mesmo se só uma URL válida permanecer.

É permitido combinar positionals e arquivo.

# Parâmetros disponíveis

Resumo:

```text
searchgeo [--config PATH] audit [target ...]
          [--urls-file PATH]
          [--project TEXT]
          [--language CODE]
          [--market CODE]
          [--max-pages N]
          [--audits-root PATH]
          [--ai-provider none|openai|deepseek|mimo|auto]
          [--ai-model MODEL_ID]
```

Defaults:

```text
language = pt-BR
market = BR
max-pages = 100
audits-root = audits
ai-provider = none
```

A descrição detalhada de cada argumento, inclusive `--config`, `--version` e `--help`, está em [CLI_REFERENCE.md](CLI_REFERENCE.md).

# Exemplo operacional completo

```powershell
searchgeo audit https://example.com `
  --project "Projeto Exemplo" `
  --language pt-BR `
  --market BR `
  --max-pages 25 `
  --audits-root .\audits `
  --ai-provider none
```

# IA desabilitada

```powershell
searchgeo audit https://example.com --ai-provider none
```

Esse é o default. A pipeline determinística continua. Dependências semantic-only sem base suficiente ficam `UNKNOWN`; ausência de IA não é falha do website.

# Um único provider de IA

## OpenAI

```powershell
$env:OPENAI_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider openai
```

Default: `gpt-5.6-terra`.

## DeepSeek

```powershell
$env:DEEPSEEK_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider deepseek
```

Default: `deepseek-v4-pro`.

## Xiaomi MiMo

```powershell
$env:MIMO_API_KEY = "<chave>"
searchgeo audit https://example.com --ai-provider mimo
```

Default: `mimo-v2.5-pro`.

Provider explícito usa somente o fornecedor escolhido. Se falhar, não troca para outro provider; após falha qualificadora ele fica quarantined durante o restante do audit.

# Override de modelo

Somente com provider explícito:

```powershell
searchgeo audit https://example.com --ai-provider openai --ai-model gpt-5.6-sol
searchgeo audit https://example.com --ai-provider deepseek --ai-model deepseek-v4-flash
searchgeo audit https://example.com --ai-provider mimo --ai-model mimo-v2.5
```

`--ai-model` com `--ai-provider auto` é rejeitado. Em AUTO, use as variáveis por provider.

# Vários providers com AUTO

```powershell
$env:OPENAI_API_KEY = "<chave-openai>"
$env:DEEPSEEK_API_KEY = "<chave-deepseek>"
$env:MIMO_API_KEY = "<chave-mimo>"
searchgeo audit --urls-file .\urls.txt --project "Projeto Exemplo" --ai-provider auto
```

O AUTO:

1. ignora providers sem token;
2. exclui configurações inválidas;
3. ordena providers elegíveis pelo rank SearchGEO do modelo;
4. chama sequencialmente, não em paralelo;
5. quarantina provider que falha;
6. tenta o próximo saudável quando permitido;
7. nunca reintroduz provider quarantined no mesmo audit.

Para os defaults, a ordem é OpenAI Terra → DeepSeek V4 Pro → MiMo V2.5 Pro.

# Provider selecionado sem token

Provider explícito sem token:

- nenhuma chamada externa;
- estado `NOT_CONFIGURED`;
- auditoria continua sem IA efetiva.

AUTO:

- provider sem token não entra na cadeia;
- se nenhum provider for elegível, nenhuma chamada externa acontece.

# Sem créditos, quota, timeout ou erro

Falhas são classificadas e sanitizadas.

Provider explícito:

```text
SINGLE_PROVIDER -> DEGRADED
```

Não existe cross-provider fallback.

AUTO:

```text
provider falho -> QUARANTINED_FOR_AUDIT
próximo saudável -> pode ser tentado
```

Se todos os providers AUTO falharem:

```text
CHAIN_EXHAUSTED
AI_PROVIDER_CHAIN_EXHAUSTED
```

Isso é limitação da auditoria, não finding do site.

# Lock por URL entre Desktop/Mobile

Quando um provider entrega a primeira análise válida de uma URL, ele fica fixado para Desktop/Mobile dessa URL.

Se falhar no segundo device:

- outro provider não completa a mesma URL;
- o contexto faltante fica degradado/`UNKNOWN` quando aplicável;
- o provider é quarantined para URLs seguintes;
- a próxima URL pode usar o próximo provider saudável.

# Saída da CLI

A conclusão normal imprime:

```text
Auditoria concluída: AUD-...
Status: ...
Páginas auditadas: N
Problemas identificados: N
Recomendações: N
Relatório: audits\AUD-...\report.html
Relatório por problemas: audits\AUD-...\remediation.html
```

Cada nova execução cria um novo workspace.

# Workspace

```text
<audits-root>/<AUD-ID>/
  audit.db
  report.html
  remediation.html
  artifacts/
```

Os dados primários são `audit.db` + artifacts. Os HTMLs são projeções.

# `report.html`

Visão orientada à auditoria/páginas. Inclui, conforme evidência disponível:

- compatibilidade GEO;
- Score/Coverage/Confidence/Consolidation;
- Desktop/Mobile separados;
- findings, actionability e prioridade;
- screenshots/DOM/evidence;
- causa raiz e correção;
- recursos de domínio;
- contexto e telemetria de IA.

A seção M18 **Uso de IA — execução e telemetria** diferencia:

- IA habilitada;
- estratégia;
- provider inicial e efetivo;
- modelo/depth;
- status;
- cadeia inicial;
- failover;
- tentativas por URL/device;
- tokens;
- custo estimado;
- duração;
- erro sanitizado.

# `remediation.html`

Visão transversal por problema/regra. Agrupa ocorrências e mantém contexto operacional da IA apenas de forma informativa. Falha de provider não vira finding nem recommendation.

# Telemetria no `audit.db`

M18 persiste:

```text
ai_audit_sessions
ai_provider_attempts
provider_pricing_catalog
```

API keys e Authorization não são persistidos.

# Logging

Quando `log_level` permite, o processo emite logs sanitizados por tentativa/sessão de IA com provider/model/status/duração/tokens/custo estimado/error_class.

A aplicação não cria `audit.log` automaticamente. O registro persistente é `audit.db` + `report.html`.

# Interpretar limitações

`COMPLETE_WITH_LIMITATIONS` não significa automaticamente website ruim. Pode refletir, entre outros:

- IA desabilitada/indisponível;
- provider sem token;
- falha/quarantine de provider;
- chain exhausted AUTO;
- falta de rendering/evidence;
- max pages;
- score não consolidável.

`UNKNOWN`, `ERROR` e `NOT_APPLICABLE` não equivalem a `FAIL`.

# Reexecutar

Não existe resume/update in-place. Corrija o contexto e execute nova auditoria:

```powershell
searchgeo audit https://example.com --project "Revalidação"
```

Compare os workspaces/HTMLs entre execuções.

# Referências

- [Referência completa da CLI](CLI_REFERENCE.md)
- [Configuração](CONFIGURATION.md)
- [Guia de IA](AI_GUIDE.md)
- [Guia do relatório](REPORT_GUIDE.md)
- [Outputs e artifacts](OUTPUTS_AND_ARTIFACTS.md)
