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

## 3. Executar uma auditoria de uma URL/domínio

O comportamento clássico permanece válido:

```powershell
searchgeo audit https://example.com
```

Também é aceito um domínio sem scheme:

```powershell
searchgeo audit example.com
```

Quando o target contém path, query ou fragment, informe `http://` ou `https://` explicitamente.

## 4. Executar uma auditoria multi-URL em um único audit_id

M14 permite informar explicitamente várias URLs do mesmo origin. Elas são normalizadas e deduplicadas antes da aquisição e permanecem no mesmo workspace/audit_id.

```powershell
searchgeo audit `
  "https://example.com/" `
  "https://example.com/produto-a" `
  "https://example.com/produto-b" `
  --project "Projeto Exemplo" `
  --max-pages 3
```

O conjunto explícito é o universo de páginas da auditoria: sitemap e links internos não expandem silenciosamente a lista fornecida.

Todas as URLs de um `URL_SET` devem pertencer ao mesmo normalized origin. Um conjunto misto é rejeitado antes da aquisição.

`--max-pages` deve ser pelo menos igual à quantidade de URLs únicas após normalização/deduplicação; o auditor não descarta silenciosamente uma URL explicitamente fornecida.

## 5. Executar por arquivo de URLs

Crie, por exemplo, `urls.txt`:

```text
https://example.com/
https://example.com/produto-a
https://example.com/produto-b
```

Linhas em branco e linhas iniciadas por `#` são ignoradas.

```powershell
searchgeo audit `
  --urls-file .\urls.txt `
  --project "Projeto Exemplo" `
  --max-pages 3
```

`--urls-file` é tratado como entrada explícita `URL_SET` mesmo quando, após normalização/deduplicação, reste apenas uma URL única.

É possível combinar URLs posicionais e `--urls-file`; o conjunto final é normalizado/deduplicado de modo determinístico.

## 6. Opções reais da CLI

```text
searchgeo [--config PATH] audit [TARGET ...]
          [--urls-file PATH]
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
| `TARGET ...` | opcional se `--urls-file` for usado | um ou mais domínios/URLs HTTP(S); uma posição mantém modo clássico, várias posições criam `URL_SET` |
| `--urls-file` | nenhum | arquivo UTF-8 com uma URL/domínio por linha; ativa entrada explícita `URL_SET` |
| `--project` | hostname/target | nome humano do projeto |
| `--language` | `pt-BR` | contexto de idioma primário |
| `--market` | `BR` | contexto de mercado |
| `--max-pages` | `100` | máximo determinístico de páginas auditadas; deve ser > 0 e cobrir todo URL_SET explícito |
| `--audits-root` | `audits` | diretório pai dos workspaces |
| `--ai-provider` | `none` | provider semântico: `none` ou `openai` |
| `--ai-model` | sem default | modelo OpenAI; também pode vir de `SEARCHGEO_OPENAI_MODEL` |
| `--config` | `searchgeo.toml`, se existir | arquivo TOML usado atualmente para logging |

## 7. Exemplo operacional

```powershell
searchgeo audit https://example.com `
  --project "Projeto Exemplo" `
  --language pt-BR `
  --market BR `
  --max-pages 25 `
  --audits-root .\audits
```

Durante a execução a pipeline realiza Discovery/HTTP, aquisição única dos recursos de domínio aplicáveis, rendering Desktop/Mobile, screenshots de viewport quando disponíveis, observações DOM, extração, regras, análise SPA, semântica conforme provider, comparação, scoring, priorização e reporting.

## 8. Saída da CLI

Em conclusão normal, a CLI imprime valores como:

```text
Auditoria concluída: AUD-...
Status: COMPLETE ou COMPLETE_WITH_LIMITATIONS
Páginas auditadas: N
Problemas identificados: N
Recomendações: N
Relatório: audits\AUD-...\report.html
```

Uma auditoria com várias URLs gera **um único** `AUD-...`.

`COMPLETE_WITH_LIMITATIONS` não significa necessariamente falha do website. Pode refletir, por exemplo, `NO_AI`, `max_pages` atingido ou avaliações não consolidadas.

## 9. Identificar a auditoria criada

Cada execução cria um ID novo no formato `AUD-<UUID>` e um workspace próprio:

```text
<audits-root>/<AUD-ID>/
```

O workspace não é reutilizado automaticamente. Reexecutar o comando cria nova auditoria.

## 10. Localizar os resultados

Na raiz do workspace:

- `audit.db` — dados persistidos primários;
- `report.html` — relatório estático para leitura humana;
- `artifacts/http/` — respostas RAW preservadas quando disponíveis;
- `artifacts/rendered/` — HTML/DOM renderizado por página/dispositivo;
- `artifacts/visual/` — screenshots PNG de viewport por página/dispositivo;
- demais subdiretórios de `artifacts/` — extrações e evidências materializadas pelos marcos anteriores.

Abra o relatório localmente no browser:

```powershell
Start-Process .\audits\AUD-...\report.html
```

Os screenshots são referenciados por paths relativos. Para portabilidade, copie/compacte a pasta do audit inteira, não apenas `report.html`.

Consulte [OUTPUTS_AND_ARTIFACTS.md](OUTPUTS_AND_ARTIFACTS.md) para paths detalhados.

## 11. Como interpretar o relatório M14

O relatório `REPORT-GEO-003` adiciona navegação orientada por domínio/página e evidência técnica concreta.

Cada finding pode mostrar, quando determinável:

- URL;
- Desktop/Mobile;
- regra e categoria GEO;
- resultado bruto;
- actionability;
- prioridade;
- selector CSS observado;
- elemento;
- HTML efetivamente persistido;
- screenshot do snapshot e destaque do elemento quando houver bounding box válido;
- problema, impacto, alteração, critério de aceite e revalidação;
- fonte técnica oficial ou indicação explícita de heurística interna.

Quando não for possível associar um único elemento DOM, o relatório mostra `NÃO DETERMINADO` e explica a razão. Isso é intencional; o auditor não inventa selector.

### Actionability

- **AÇÃO NECESSÁRIA** — correção comprovadamente requerida pela semântica da regra.
- **REVISÃO RECOMENDADA** — condição contextual/política; revisar antes de alterar o site.
- **MELHORIA OPCIONAL** — não bloqueante e não é FAIL automático.
- **NENHUMA AÇÃO NECESSÁRIA** — passou ou não se aplica.
- **AÇÃO NO SITE NÃO DETERMINADA** — evidência insuficiente; não autoriza inventar correção.

### Score zero versus não calculado

```text
Score: 0.0
Estado: CALCULADO
```

é diferente de:

```text
Score: NÃO DETERMINADO
Estado: NÃO CALCULADO
```

`Coverage: 0%` é cobertura e não deve ser lida como `Score GEO: 0`.

## 12. Recursos do domínio

Em `URL_SET`, `robots.txt` e sitemap(s) são adquiridos no escopo do domínio/audit, não repetidos para cada página.

O relatório mostra a URL consultada, estado HTTP/interpretação, sitemaps declarados e a política observada para crawlers baseline. `OAI-SearchBot` e `GPTBot` aparecem separadamente.

Ausência válida de `robots.txt` ou sitemap não é automaticamente defeito: o resultado depende da Business Rule aplicável.

## 13. Execução sem IA

É o comportamento padrão:

```powershell
searchgeo audit https://example.com --ai-provider none
```

A auditoria continua. Regras semantic-only que dependam de provider ficam `UNKNOWN` quando não houver base determinística suficiente. Isso reduz cobertura/consolidação aplicável, mas **não transforma ausência de IA em FAIL do site**.

## 14. Execução com OpenAI

```powershell
$env:OPENAI_API_KEY = "<chave>"
$env:SEARCHGEO_OPENAI_MODEL = "<modelo suportado>"
searchgeo audit https://example.com --ai-provider openai
```

Ou informe o modelo por CLI:

```powershell
searchgeo audit https://example.com --ai-provider openai --ai-model "<modelo suportado>"
```

Sem model, a CLI rejeita `--ai-provider openai`. Sem API key, o provider degrada para estado não configurado; a ausência de IA não é penalidade do website.

M14 não adiciona uma chamada livre ao LLM para escrever recomendações. O relatório reutiliza análises persistidas e remediação determinística.

Consulte [AI_GUIDE.md](AI_GUIDE.md) e [CONFIGURATION.md](CONFIGURATION.md) para os modelos/variáveis suportados pela versão instalada.

## 15. Sucesso, limitação e falha

- `COMPLETE`: pipeline encerrada sem limitações que impeçam consolidação prevista.
- `COMPLETE_WITH_LIMITATIONS`: auditoria encerrada com limitações explícitas.
- erro da CLI / status interno `FAILED`: falha operacional não absorvida pela pipeline.
- falhas localizadas de página, HTTP, rendering, screenshot, extração ou provider são registradas e, quando possível, não derrubam a auditoria inteira.

`UNKNOWN`, `ERROR` e `NOT_APPLICABLE` de uma regra não equivalem a `FAIL`.

## 16. Reexecutar

Corrija a causa desejada e execute o comando novamente. A baseline não possui comando de "resume" nem atualização in-place do workspace anterior.

```powershell
searchgeo audit https://example.com --project "Revalidação"
```

Compare os relatórios e, para análise técnica reproduzível, compare também os dados persistidos/artifacts de cada auditoria.
