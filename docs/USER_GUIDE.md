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

## 4. Executar uma auditoria multi-URL diretamente no comando

Várias URLs do mesmo normalized origin podem ser auditadas em um único `audit_id`. Elas são normalizadas e deduplicadas antes da aquisição.

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
Relatório por problemas: audits\AUD-...\remediation.html
```

Uma auditoria com várias URLs gera **um único** `AUD-...` e os dois HTMLs usam o mesmo estado persistido.

`COMPLETE_WITH_LIMITATIONS` não significa necessariamente falha do website. Pode refletir, por exemplo, `NO_AI`, provider indisponível, `max_pages` atingido ou avaliações não consolidadas.

## 9. Identificar a auditoria criada

Cada execução cria um ID novo no formato `AUD-<UUID>` e um workspace próprio:

```text
<audits-root>/<AUD-ID>/
```

O workspace não é reutilizado automaticamente. Reexecutar o comando cria nova auditoria.

## 10. Localizar os resultados

Na raiz do workspace:

- `audit.db` — dados persistidos primários;
- `report.html` — visão principal orientada a página;
- `remediation.html` — visão transversal orientada a regra/problema;
- `artifacts/http/` — respostas RAW preservadas quando disponíveis;
- `artifacts/rendered/` — HTML/DOM renderizado por página/dispositivo;
- `artifacts/visual/` — screenshots PNG de viewport por página/dispositivo;
- demais subdiretórios de `artifacts/` — extrações e evidências materializadas pelos marcos anteriores.

Abra os relatórios localmente:

```powershell
Start-Process .\audits\AUD-...\report.html
Start-Process .\audits\AUD-...\remediation.html
```

Os dois HTMLs possuem links relativos entre si. Screenshots também são referenciados por paths relativos. Para portabilidade, copie/compacte a pasta do audit inteira.

Consulte [OUTPUTS_AND_ARTIFACTS.md](OUTPUTS_AND_ARTIFACTS.md) para paths detalhados.

## 11. Como interpretar `report.html`

`report.html` é a visão orientada a página. A partir do M15, em desktop ele possui menu lateral fixo com as URLs auditadas representadas por **path/query**, sem repetir o domínio. Paths longos são truncados apenas visualmente.

Em viewport estreita, a navegação se torna compacta no topo para não consumir uma coluna lateral permanente.

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

Quando não for possível associar um único elemento DOM, o relatório mostra `NÃO DETERMINADO` e explica a razão. O auditor não inventa selector.

### Guia do Score GEO

No final de `report.html`, o M15 inclui uma seção que explica as dez dimensões oficiais do Score GEO. Para cada dimensão, o relatório descreve:

- o que ela mede;
- como melhorar a condição/evidência avaliada;
- estado Desktop/Mobile quando score estiver persistido;
- referências técnicas oficiais quando houver uma fonte verificada aplicável.

A seção final **Como interpretar** diferencia Score, Coverage, Confidence, Consolidation, Actionability e Desktop/Mobile.

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

## 12. Como interpretar `remediation.html`

`remediation.html` muda o ângulo da análise: em vez de começar pela página, começa pelo **problema/regra**.

Ele separa:

- **Problemas globais** — findings sem `page_id`, ligados ao domínio ou a recurso global;
- **Problemas por página** — findings ligados a páginas concretas.

Quando a mesma regra/actionability aparece em várias páginas, o relatório cria um único grupo e lista as ocorrências, permitindo distinguir rapidamente um padrão recorrente de um problema pontual.

Cada grupo pode mostrar paths afetados, dispositivo, resultado, prioridade, selector, orientação de correção, critério de aceite e referências técnicas. Os paths apontam de volta para a seção correspondente em `report.html`.

O agrupamento **não recalcula** score, finding, prioridade ou actionability; é somente outra projeção do mesmo `audit.db`.

## 13. Recursos do domínio

Em `URL_SET`, `robots.txt` e sitemap(s) são adquiridos no escopo do domínio/audit, não repetidos para cada página.

O relatório mostra a URL consultada, estado HTTP/interpretação, sitemaps declarados e a política observada para crawlers baseline. `OAI-SearchBot` e `GPTBot` aparecem separadamente.

Ausência válida de `robots.txt` ou sitemap não é automaticamente defeito: o resultado depende da Business Rule aplicável.

## 14. Execução sem IA

É o comportamento padrão:

```powershell
searchgeo audit https://example.com --ai-provider none
```

A auditoria continua. Regras semantic-only que dependam de provider ficam `UNKNOWN` quando não houver base determinística suficiente. Isso reduz cobertura/consolidação aplicável, mas **não transforma ausência de IA em FAIL do site**.

## 15. Execução com OpenAI

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

M14/M15 não adicionam uma chamada livre ao LLM para escrever recomendações ou reorganizar o relatório. Os HTMLs reutilizam análises persistidas e remediação determinística.

Consulte [AI_GUIDE.md](AI_GUIDE.md) e [CONFIGURATION.md](CONFIGURATION.md) para os modelos/variáveis suportados pela versão instalada.

## 16. Sucesso, limitação e falha

- `COMPLETE`: pipeline encerrada sem limitações que impeçam consolidação prevista.
- `COMPLETE_WITH_LIMITATIONS`: auditoria encerrada com limitações explícitas.
- erro da CLI / status interno `FAILED`: falha operacional não absorvida pela pipeline.
- falhas localizadas de página, HTTP, rendering, screenshot, extração ou provider são registradas e, quando possível, não derrubam a auditoria inteira.

`UNKNOWN`, `ERROR` e `NOT_APPLICABLE` de uma regra não equivalem a `FAIL`.

## 17. Reexecutar

Corrija a causa desejada e execute o comando novamente. A baseline não possui comando de "resume" nem atualização in-place do workspace anterior.

```powershell
searchgeo audit https://example.com --project "Revalidação"
```

Compare `report.html` e `remediation.html` entre auditorias e, para análise técnica reproduzível, compare também os dados persistidos/artifacts de cada workspace.

<!-- M18_MULTI_AI_PROVIDER_ROUTING -->
## M18 — escolher IA
Use `none` para IA desabilitada, um provider explícito para execução única sem failover, ou `auto` para seleção/fallback por confiabilidade SearchGEO. O relatório distingue provider configurado, tentado e efetivamente usado, mostra profundidade, status, tokens reportados, `ESTIMATED_COST`, duração e erro sanitizado. Falhas de IA são limitações da auditoria, não problemas do website.

