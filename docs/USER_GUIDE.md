# Guia do Usuário

## 1. Abrir o terminal

No Windows, abra PowerShell e vá até o repositório/ambiente onde o package foi instalado.

```powershell
cd C:\caminho\SearchGEO-Readiness-Auditor
.\.venv\Scripts\Activate.ps1
```

Consulte [INSTALLATION.md](INSTALLATION.md) se o ambiente ainda não estiver preparado.

## 2. Verificar o comando

```powershell
searchgeo --version
searchgeo audit --help
```

## 3. Executar uma auditoria

Exemplo mínimo:

```powershell
searchgeo audit https://example.com
```

Também é aceito um domínio sem scheme:

```powershell
searchgeo audit example.com
```

Quando o target contém path, query ou fragment, informe `http://` ou `https://` explicitamente.

## 4. Opções reais da CLI

```text
searchgeo [--config PATH] audit TARGET
          [--project NAME]
          [--language LANGUAGE]
          [--market MARKET]
          [--max-pages N]
          [--audits-root PATH]
          [--ai-provider {none,openai}]
          [--ai-model MODEL]
```

| Opção | Default | Função |
|---|---|---|
| `TARGET` | obrigatório | domínio ou URL HTTP(S) |
| `--project` | hostname/target | nome humano do projeto |
| `--language` | `pt-BR` | contexto de idioma primário |
| `--market` | `BR` | contexto de mercado |
| `--max-pages` | `100` | máximo determinístico de páginas auditadas; deve ser > 0 |
| `--audits-root` | `audits` | diretório pai dos workspaces |
| `--ai-provider` | `none` | provider semântico: `none` ou `openai` |
| `--ai-model` | sem default | modelo OpenAI; também pode vir de `SEARCHGEO_OPENAI_MODEL` |
| `--config` | `searchgeo.toml`, se existir | arquivo TOML usado atualmente para logging |

## 5. Exemplo operacional

```powershell
searchgeo audit https://example.com `
  --project "Projeto Exemplo" `
  --language pt-BR `
  --market BR `
  --max-pages 25 `
  --audits-root .\audits
```

Durante a execução a pipeline realiza Discovery/HTTP, rendering Desktop/Mobile, extração, regras, análise SPA, semântica conforme provider, comparação, scoring, priorização e reporting.

## 6. Saída da CLI

Em conclusão normal, a CLI imprime valores como:

```text
Auditoria concluída: AUD-...
Status: COMPLETE ou COMPLETE_WITH_LIMITATIONS
Páginas auditadas: N
Problemas identificados: N
Recomendações: N
Relatório: audits\AUD-...\report.html
```

`COMPLETE_WITH_LIMITATIONS` não significa necessariamente falha do website. Pode refletir, por exemplo, `NO_AI`, `max_pages` atingido ou avaliações não consolidadas.

## 7. Identificar a auditoria criada

Cada execução cria um ID novo no formato `AUD-<UUID>` e um workspace próprio:

```text
<audits-root>/<AUD-ID>/
```

O workspace não é reutilizado automaticamente. Reexecutar o comando cria nova auditoria.

## 8. Localizar os resultados

Na raiz do workspace:

- `audit.db` — dados persistidos primários;
- `report.html` — relatório estático para leitura humana;
- `artifacts/` — RAW HTTP, rendered DOM e extrações materializadas.

Abra o relatório localmente no browser:

```powershell
Start-Process .\audits\AUD-...\report.html
```

Consulte [OUTPUTS_AND_ARTIFACTS.md](OUTPUTS_AND_ARTIFACTS.md) para paths detalhados.

## 9. Execução sem IA

É o comportamento padrão:

```powershell
searchgeo audit https://example.com --ai-provider none
```

A auditoria continua. Regras semantic-only que dependam de provider ficam `UNKNOWN` quando não houver base determinística suficiente. Isso reduz cobertura/consolidação aplicável, mas **não transforma ausência de IA em FAIL do site**.

## 10. Execução com OpenAI

```powershell
$env:OPENAI_API_KEY = "<chave>"
$env:SEARCHGEO_OPENAI_MODEL = "<modelo>"
searchgeo audit https://example.com --ai-provider openai
```

Ou informe o modelo por CLI:

```powershell
searchgeo audit https://example.com --ai-provider openai --ai-model "<modelo>"
```

Sem model, a CLI rejeita `--ai-provider openai`. Sem API key, o provider degrada para estado não configurado; a ausência de IA não é penalidade do website.

## 11. Sucesso, limitação e falha

- `COMPLETE`: pipeline encerrada sem limitações que impeçam consolidação prevista.
- `COMPLETE_WITH_LIMITATIONS`: auditoria encerrada com limitações explícitas.
- erro da CLI / status interno `FAILED`: falha operacional não absorvida pela pipeline.
- falhas localizadas de página, HTTP, rendering, extração ou provider são registradas e, quando possível, não derrubam a auditoria inteira.

`UNKNOWN`, `ERROR` e `NOT_APPLICABLE` de uma regra não equivalem a `FAIL`.

## 12. Reexecutar

Corrija a causa desejada e execute o comando novamente. A baseline não possui comando de "resume" nem atualização in-place do workspace anterior.

```powershell
searchgeo audit https://example.com --project "Revalidação"
```

Compare os relatórios e, para análise técnica reproduzível, compare também os dados persistidos/artifacts de cada auditoria.
