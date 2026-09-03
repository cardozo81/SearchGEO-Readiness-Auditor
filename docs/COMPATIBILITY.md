# Compatibilidade e Dependências

Este é o contrato operacional da baseline atual do SearchGEO Readiness Auditor, incluindo M18 multi-provider.

## Matriz de compatibilidade

| Item | Estado | Contrato/observação |
|---|---|---|
| Windows + PowerShell | **Target operacional de handoff** | documentação e exemplos operacionais são preparados para este ambiente |
| Ubuntu `ubuntu-latest` | **Validado por testes automatizados** | usado em gates de regressão; não é target formal de distribuição |
| macOS | **Não homologado** | nenhuma garantia operacional nesta baseline |
| CPython 3.13.x | **Obrigatório/suportado** | `requires-python = ">=3.13,<3.14"` |
| Python 3.12 ou anterior | **Incompatível** | fora do contrato do package |
| Python 3.14+ | **Incompatível** | fora do contrato até decisão explícita |
| Playwright `>=1.57,<2` | **Obrigatório** | dependência externa de runtime declarada |
| Chromium | **Obrigatório para rendering real** | browser do Playwright ou executável compatível explícito |
| SQLite | **Obrigatório e embarcado** | módulo `sqlite3`; sem database server |
| Filesystem local gravável | **Obrigatório** | `audit.db`, artifacts e HTMLs são locais |
| HTTP/HTTPS para target | **Obrigatório para auditoria real** | discovery, aquisição e rendering dependem de rede |
| OpenAI | **Opcional / suportado** | provider M18; qualificação SearchGEO `QUALIFIED` |
| DeepSeek | **Opcional / suportado** | provider M18; qualificação SearchGEO `PROVISIONAL` |
| Xiaomi MiMo | **Opcional / suportado** | provider M18; qualificação SearchGEO `PROVISIONAL` |
| Docker | **Não requerido / não fornecido** | sem imagem oficial |
| Web server/backend | **Não requerido / não fornecido** | CLI + HTML estático |
| Git/GitHub | **Não requerido em runtime** | engenharia/versionamento somente |

## Dependências obrigatórias

### Python

```powershell
py -3.13 --version
```

### Package

```powershell
python -m pip install -e .
```

### Chromium

```powershell
python -m playwright install chromium
```

Sem Chromium funcional, aquisição HTTP pode ocorrer, mas rendering Desktop/Mobile perde capacidade e isso reduz cobertura/confiabilidade da auditoria; não é automaticamente `FAIL` do website.

Executável alternativo:

```powershell
$env:PLAYWRIGHT_CHROMIUM_EXECUTABLE = "C:\caminho\para\chrome.exe"
```

### Filesystem

O processo precisa conseguir criar:

```text
<audits-root>/<AUD-ID>/audit.db
<audits-root>/<AUD-ID>/artifacts/
<audits-root>/<AUD-ID>/report.html
<audits-root>/<AUD-ID>/remediation.html
```

### Rede

Sem IA, o host precisa alcançar o site auditado e seus recursos necessários ao rendering.

Com IA, precisa também de egress HTTPS ao provider selecionado.

# Compatibilidade de IA

IA não é dependência obrigatória. O default é:

```powershell
searchgeo audit https://example.com --ai-provider none
```

ou simplesmente:

```powershell
searchgeo audit https://example.com
```

## OpenAI

Modelos suportados pelo allowlist:

```text
gpt-5.6-sol
gpt-5.6-terra
gpt-5.6-luna
```

Default:

```text
gpt-5.6-terra / HIGH
```

Requer:

```text
OPENAI_API_KEY
```

## DeepSeek

Modelos suportados:

```text
deepseek-v4-pro
deepseek-v4-flash
```

Default:

```text
deepseek-v4-pro / HIGH
```

Requer:

```text
DEEPSEEK_API_KEY
```

Estado de qualificação SearchGEO: `PROVISIONAL` até benchmark específico.

## Xiaomi MiMo

Modelos suportados:

```text
mimo-v2.5-pro
mimo-v2.5
```

Default:

```text
mimo-v2.5-pro / HIGH
```

No relatório, reasoning habilitado é normalizado como `THINKING_ENABLED`.

Requer:

```text
MIMO_API_KEY
```

Estado de qualificação SearchGEO: `PROVISIONAL` até benchmark específico.

# Modos e efeitos

| Situação | Chamada externa | Modo/efeito |
|---|---:|---|
| `--ai-provider none` | Não | `NO_AI`; regras semantic-only podem ficar `UNKNOWN` |
| provider explícito sem key | Não | `NOT_CONFIGURED`; não é falha do site |
| provider explícito configurado e válido | Sim | pode chegar a `FULL` conforme universo aplicável |
| provider explícito falha | Sim até a falha | `DEGRADED`; provider quarantined; sem fallback para outro provider |
| `auto` sem tokens | Não | nenhuma cadeia elegível; sem IA efetiva |
| `auto` com failover | Sim | provider falho quarantined; próximo saudável pode ser promovido |
| todos AUTO falham | Sim | `CHAIN_EXHAUSTED`; limitação `AI_PROVIDER_CHAIN_EXHAUSTED` |

## Sem token

Provider explícito:

- retorna `NOT_CONFIGURED`;
- nenhuma requisição externa é realizada;
- pipeline determinístico continua.

`AUTO`:

- provider sem token é omitido;
- se nenhum provider possuir token/configuração válida, não há chamada externa.

## Sem créditos / quota / erro

O runtime classifica falhas de autenticação, quota/crédito, rate limit, modelo/permissão, rede/timeout/server e contrato/resposta.

Provider explícito não troca de fornecedor. `AUTO` pode fazer fallback, sempre respeitando quarantine e lock por URL.

# Homologação M18

A implementação M18 foi validada por suíte automatizada com adapters fakes/mocks e integração de persistência/relatório. O live smoke real de providers é condicionado à existência de credenciais no ambiente de homologação.

A ausência de credenciais no CI significa apenas que o smoke externo foi pulado; não autoriza afirmar homologação live de uma conta/provider específicos.

# Segurança

API keys devem existir apenas no ambiente do processo ou mecanismo seguro equivalente. Não devem ser gravadas em:

- Git;
- TOML versionado;
- artifacts;
- HTMLs;
- logs;
- scripts compartilhados.

Validação segura:

```powershell
Test-Path Env:OPENAI_API_KEY
Test-Path Env:DEEPSEEK_API_KEY
Test-Path Env:MIMO_API_KEY
```

# O que significa "compatível"

Para a aplicação local:

- Python/package dentro do contrato;
- Chromium funcional;
- filesystem gravável;
- rede disponível ao target;
- suíte sem regressão;
- smoke operacional no ambiente de destino quando exigido.

Para um provider/model de IA:

- model ID presente no allowlist M18;
- API key válida;
- endpoint acessível;
- conta com permissão/limite/crédito suficientes;
- resposta compatível com o contrato semântico;
- validação local SearchGEO concluída.

# Referências

- [Instalação](INSTALLATION.md)
- [Referência completa da CLI](CLI_REFERENCE.md)
- [Guia de IA](AI_GUIDE.md)
- [Configuração](CONFIGURATION.md)
