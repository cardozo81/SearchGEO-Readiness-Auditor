# Troubleshooting

Use este guia para distinguir defeito de ambiente, falha localizada do target e limitação legítima da auditoria.

## `searchgeo`: comando não encontrado

**Sintoma**  
PowerShell não reconhece `searchgeo`.

**Causa provável**  
Package não instalado no ambiente ativo ou venv não ativado.

**Diagnóstico**

```powershell
python --version
python -m pip show searchgeo-readiness-auditor
Get-Command searchgeo -ErrorAction SilentlyContinue
```

**Correção**

```powershell
python -m pip install -e .
```

Ou use `.\.venv\Scripts\searchgeo.exe` diretamente.

**Limitação vs defeito**  
Não é limitação do target; é preparação do ambiente.

---

## Python incompatível

**Sintoma**  
`pip` rejeita instalação ou comportamento diverge do ambiente validado.

**Causa provável**  
Python fora de `>=3.13,<3.14`.

**Diagnóstico**

```powershell
python --version
```

**Correção**  
Instale/ative CPython 3.13.

**Limitação**  
Suporte a outras versões está fora da Stable Local Baseline.

---

## Package/Playwright não instalado

**Sintoma**  
ImportError para `playwright` ou package.

**Diagnóstico**

```powershell
python -m pip show playwright
python -m pip show searchgeo-readiness-auditor
```

**Correção**

```powershell
python -m pip install -e .
```

---

## Chromium ausente

**Sintoma**  
Rendering registra `BROWSER_UNAVAILABLE`.

**Causa provável**  
Browser do Playwright não instalado.

**Diagnóstico**

```powershell
python -m playwright install --dry-run chromium
```

**Correção**

```powershell
python -m playwright install chromium
```

Ou configure `PLAYWRIGHT_CHROMIUM_EXECUTABLE` para executável compatível.

**Limitação vs defeito**  
Sem Chromium, a auditoria perde capacidade RENDERED; isso é limitação de ambiente e pode reduzir Coverage, não prova falha do site.

---

## Chromium bloqueado por política/antivírus

**Sintoma**  
Browser está instalado, mas não inicia; `BROWSER_UNAVAILABLE` ou falha de launch.

**Diagnóstico**  
Teste um script/instalação Playwright no mesmo usuário e verifique políticas de execução/EDR.

**Correção**  
Liberar o executável/processo conforme política corporativa ou apontar para Chromium permitido via `PLAYWRIGHT_CHROMIUM_EXECUTABLE`.

**Limitação**  
Se a política não permitir browser automation, rendering real não pode ser homologado nesse ambiente.

---

## Timeout de rendering

**Sintoma**  
`NAVIGATION_TIMEOUT` em um snapshot.

**Causa provável**  
Página não chega a `domcontentloaded` dentro de 15 s, rede lenta ou comportamento do site.

**Diagnóstico**  
Verifique HTTP RAW, acesso manual e se o problema ocorre em Desktop/Mobile.

**Correção**  
Corrija conectividade/target. O timeout não é configurável pela CLI atual.

**Limitação vs defeito**  
Timeout localizado é evidência de indisponibilidade naquele contexto; não deve ser automaticamente extrapolado para outras páginas/devices.

---

## `networkidle` não é atingido

**Sintoma**  
Browser metadata mostra `settle_outcome = BOUNDED_TIMEOUT`.

**Causa provável**  
Conexões persistentes/analytics/long polling.

**Correção**  
Normalmente nenhuma. A implementação limita `networkidle` a 2 s e ainda captura o DOM.

**Limitação**  
É comportamento previsto, não erro por si só.

---

## DNS / conexão

**Sintoma**  
BR-GEO-005 falha; Evidence HTTP possui network error.

**Causa provável**  
Hostname inválido/não resolvido, porta recusada ou rede indisponível.

**Diagnóstico**

```powershell
Resolve-DnsName example.com
Test-NetConnection example.com -Port 443
```

**Correção**  
Corrigir DNS, URL, conectividade ou infraestrutura do target.

**Limitação vs defeito**  
Se o erro for específico do ambiente/proxy, é limitação da observação; se reproduzível externamente, pode ser problema real de acessibilidade.

---

## TLS

**Sintoma**  
Aquisição não obtém resposta utilizável e registra erro TLS.

**Diagnóstico**  
Abra o endpoint com ferramenta corporativa/browser e valide certificado/cadeia/hostname.

**Correção**  
Corrigir certificado/chain no target ou trust/proxy do ambiente quando o problema for local.

---

## Proxy ou firewall

**Sintoma**  
HTTP/Chromium falham para targets que funcionam em outro ambiente.

**Diagnóstico**  
Compare aquisição por PowerShell/browser no mesmo host, revise proxy corporativo, DNS split-horizon e regras de egress.

**Correção**  
Ajustar rede. A baseline não expõe flags próprias de proxy.

**Limitação**  
Ambiente sem egress suficiente não é adequado para smoke test externo.

---

## Site retorna 4xx/5xx

**Sintoma**  
HTTP status final evidencia resposta não utilizável; regras derivadas podem ficar bloqueadas.

**Diagnóstico**  
Abra `artifacts/http/page-*.response` e consulte Evidence/RuleExecution no `audit.db`.

**Correção**  
Depende do target: rota, autenticação, rate limit, WAF ou falha de aplicação.

**Limitação vs defeito**  
Um 4xx/5xx observado é dado técnico real; regras semânticas derivadas em `NOT_APPLICABLE`/`UNKNOWN` são prevenção de cascading failure, não ausência de problema técnico.

---

## robots.txt ausente

**Sintoma**  
robots state `ABSENT`/404.

**Interpretação**  
Ausência de robots não é automaticamente FAIL nem bloqueio.

**Correção**  
Só é necessária se a política/site deveria publicar robots por requisito próprio.

---

## robots.txt inválido/ininterpretável

**Sintoma**  
BR-GEO-017 pode alertar/falhar conforme evidência.

**Diagnóstico**  
Consulte Evidence `ROBOTS_RULE` e artifact `artifacts/http/robots.response`, quando disponível.

**Correção**  
Corrigir sintaxe/política do arquivo.

---

## Sitemap ausente ou inválido

**Sintoma**  
Sitemap não encontrado ou state `INVALID`.

**Interpretação**  
Ausência de sitemap não é FAIL automático. Sitemap malformado é registrado sem abortar Discovery.

**Diagnóstico**  
Evidence `SITEMAP_ENTRY` + artifact `sitemap-*.response`.

---

## Rendering ausente para um device

**Sintoma**  
Desktop ou Mobile não possui rendered artifact.

**Diagnóstico**  
Verifique PageSnapshot/browser metadata e `artifacts/rendered`.

**Correção**  
Resolver browser/rede/target conforme error kind.

**Limitação**  
Comparação BR-GEO-052 pode ficar `UNKNOWN`; isso não deve virar diferença negativa inventada.

---

## Site SPA/CSR parece diferente no RAW

**Sintoma**  
RAW contém shell mínimo, RENDERED contém conteúdo completo.

**Interpretação**  
Isso pode ser válido. A baseline não penaliza SPA/CSR apenas pela arquitetura. BR-GEO-019..024 avaliam recuperabilidade, direct routes, navegação, soft-404 e lazy loading.

---

## API key OpenAI ausente

**Sintoma**  
Modo `NO_AI`/`AI_NOT_CONFIGURED`.

**Diagnóstico**

```powershell
Test-Path Env:OPENAI_API_KEY
```

**Correção**  
Configure a variável apenas se IA for desejada.

**Limitação vs defeito**  
Ausência de IA é suportada; não é erro do site.

---

## Model OpenAI ausente

**Sintoma**  
CLI encerra: `--ai-model or SEARCHGEO_OPENAI_MODEL is required when --ai-provider=openai`.

**Correção**

```powershell
$env:SEARCHGEO_OPENAI_MODEL = "<modelo>"
```

Ou `--ai-model`.

---

## Erro do OpenAIProvider

**Sintoma**  
`AI_PROVIDER_UNAVAILABLE:<tipo>`; análise semântica degrada.

**Causas**  
HTTP error, timeout, rede, resposta inválida, schema/evidence inválida ou JSON inválido.

**Diagnóstico**  
Confirme credencial/model/conectividade. Não aceite saída inválida manualmente como finding.

**Correção**  
Resolver provider/configuração ou executar sem IA.

**Limitação**  
Provider indisponível reduz capacidade analítica; não reduz qualidade do website por si só.

---

## Problemas com `audit.db`

**Sintoma**  
Workspace não reabre, database ausente/corrompido ou erro de permissão.

**Diagnóstico**

```powershell
Test-Path .\audits\AUD-...\audit.db
Get-Item .\audits\AUD-...\audit.db
```

**Correção**  
Garanta espaço/permissão. Não substitua o DB por `report.html`; reexecute a auditoria se a fonte primária foi perdida.

---

## Filesystem/permissões

**Sintoma**  
Falha ao criar `audits/<AUD-ID>` ou artifacts.

**Causa provável**  
Diretório read-only, ACL, path inválido, espaço em disco.

**Correção**

```powershell
searchgeo audit https://example.com --audits-root D:\SearchGEO\audits
```

Use path com permissão de criação/escrita.

---

## `report.html` ausente

**Sintoma**  
Workspace existe, mas report não foi materializado.

**Diagnóstico**  
Confira status do Audit no SQLite, stdout/stderr da execução e se pipeline chegou a REPORTING/M11.

**Correção**  
Corrija a falha operacional e reexecute. Não há comando de regeneração isolada exposto pela CLI atual.

**Limitação**  
Auditoria interrompida antes de M11 pode ter dados parciais úteis, mas não é uma Stable Local Baseline concluída.

---

## Auditoria `COMPLETE_WITH_LIMITATIONS`

**Sintoma**  
Execução conclui, mas status possui limitações.

**Diagnóstico**  
Leia a seção Reliability/Limitations do report e o Audit persistido.

Causas normais incluem:

- `max_pages` atingido;
- `NO_AI`;
- rules UNKNOWN/ERROR;
- dimensões não consolidadas.

**Correção**  
Só corrija quando a limitação for indesejada. Não trate automaticamente `COMPLETE_WITH_LIMITATIONS` como defeito do site.

## Escalonamento técnico

Antes de abrir correção de produto, preserve:

1. comando exato executado, sem secrets;
2. versão do Python/package;
3. Audit ID;
4. `audit.db`;
5. artifacts relevantes;
6. RuleExecution/Evidence IDs;
7. error kind estruturado;
8. indicação de Desktop/Mobile;
9. informação se IA estava FULL/DEGRADED/NO_AI.
