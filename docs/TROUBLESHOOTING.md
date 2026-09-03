# TROUBLESHOOTING.md

## `searchgeo` não é reconhecido

Ative o virtualenv e reinstale o package:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
searchgeo --version
```

## Chromium não encontrado

```powershell
python -m playwright install chromium
```

## Python incompatível

O package exige CPython 3.13.x:

```powershell
py -3.13 --version
```

## Report não está na raiz do AUD-ID

Correto no contrato atual. O ponto de entrada é:

```text
audits/<AUD-ID>/report/index.html
```

Os antigos `report.html` e `remediation.html` da raiz são intermediários internos e são removidos quando `run_audit` finaliza o report site.

## `desktop.html` não existe

Verifique o contexto usado.

Default:

```text
mobile
```

Para Desktop:

```powershell
searchgeo audit https://example.com --device-context desktop
```

Para ambos:

```powershell
searchgeo audit https://example.com --device-context both
```

## O relatório mostra apenas Mobile

É esperado com o default atual da CLI. Isso reduz rendering e chamadas de IA desnecessárias.

Use `both` somente quando a comparação Desktop × Mobile for necessária.

## Quero definir o dispositivo por ambiente

```powershell
$env:SEARCHGEO_DEVICE_CONTEXT = "mobile"
```

Valores válidos:

```text
mobile
desktop
both
```

A flag `--device-context` tem precedência.

## Confidence está LOW — o texto está ruim?

Não necessariamente.

`Confidence LOW` indica baixa força da conclusão do auditor, normalmente por Coverage/evidência/erros insuficientes. Não é uma nota de qualidade textual.

Verifique:

- Coverage;
- limitations;
- regras `UNKNOWN`/`ERROR`;
- findings evidence-backed;
- `report/mobile.html` ou `report/desktop.html`;
- `report/ai-usage.html` se IA estava habilitada.

Não reescreva conteúdo apenas para elevar Confidence. A alteração precisa ser sustentada por um finding/regra específica.

## Score alto com Confidence LOW

Leia como “boa qualidade na parte avaliada, mas conclusão limitada”, não como aprovação plena.

O report site mantém Score, Coverage e Confidence separados para evitar essa confusão.

## Provider explícito sem token

Exemplo:

```powershell
searchgeo audit https://example.com --ai-provider openai
```

Sem `OPENAI_API_KEY`, o estado operacional será `NOT_CONFIGURED` e não haverá chamada externa.

Confira sem imprimir a chave:

```powershell
Test-Path Env:OPENAI_API_KEY
```

## DeepSeek/MiMo sem token interferem no OpenAI explícito?

Não.

Com:

```text
--ai-provider openai
```

somente OpenAI participa. Chaves ausentes dos outros providers não sobrescrevem nem anulam resultado OpenAI.

## AUTO ignora provider sem token?

Sim. A cadeia inclui somente providers elegíveis/configurados no início da auditoria.

## `TIMEOUT_ERROR`

Timeout não equivale a falta de crédito nem erro de autenticação.

Default:

```text
180 s
```

Ajuste:

```powershell
$env:SEARCHGEO_AI_TIMEOUT_SECONDS = "240"
```

O runtime não repete automaticamente uma chamada após timeout para evitar consumo potencialmente duplicado.

## Crédito/saldo existe, mas a chamada falha

Saldo positivo não garante sucesso de uma requisição específica. Verifique a classe de erro em:

```text
report/ai-usage.html
```

Distinguir:

- auth;
- credit/quota;
- rate limit;
- timeout;
- network/server;
- model/permission;
- resposta inválida/contrato.

## Onde está a telemetria de IA?

```text
report/ai-usage.html
```

No banco:

```text
ai_audit_sessions
ai_provider_attempts
provider_pricing_catalog
```

## A telemetria diz que IA falhou. Isso reduz o Score?

Não diretamente. Falha de provider é limitação operacional e não cria finding do website.

Ela pode deixar regras semantic-only como `UNKNOWN`, reduzindo Coverage/Consolidation.

## Custo estimado difere da cobrança real

Esperado. `ESTIMATED_COST` usa catálogo local versionado e não substitui invoice/billing do provider.

## Report sem CSS

Confirme que você preservou a pasta inteira:

```text
report/css/site.css
```

Não copie somente `index.html`. Os links são relativos.

## Screenshot não abre ao mover só `report/`

Os snapshots visuais continuam em `../artifacts/`. Para portabilidade completa, mova o workspace inteiro:

```text
AUD-ID/
├─ artifacts/
└─ report/
```

## Layout invade menu/sidebar

O report site final usa um único stylesheet externo e largura de conteúdo calculada descontando a navegação fixa. Se ocorrer sobreposição:

1. confirme que está abrindo os arquivos novos em `report/`;
2. confirme que `css/site.css` é da mesma auditoria;
3. evite abrir um `report.html` legado salvo de auditoria antiga;
4. teste em largura mobile, onde o menu vira barra sticky.

## `references.html` diz que algumas regras são heurísticas

Correto. O SearchGEO não deve promover heurística interna a standard oficial.

A documentação atual do Google para recursos generativos mantém SEO como base e não define score GEO universal ou markup especial GEO/AEO.

## Resultados Mobile e Desktop diferentes

Diferença não é automaticamente defeito. Verifique a classificação da comparação e as evidências. Conteúdo/layout responsivo pode diferir legitimamente.

## URL_SET excede `--max-pages`

O auditor rejeita a execução para não omitir URL fornecida silenciosamente. Aumente o limite.

## Target com path sem scheme é rejeitado

Use:

```text
https://example.com/path
```

Em vez de:

```text
example.com/path
```

## Logs

Logging do processo segue `log_level`. A baseline não cria `audit.log` automaticamente.

Não registre chaves, Authorization ou payload integral sensível.
