# TECHNICAL_GUIDE.md

## Pipeline

```text
CLI
→ target/device config
→ M2 acquisition
→ M3 rendering
→ M4 evidence
→ M5/M6 deterministic analysis
→ content extractability
→ M7 semantic provider
→ M8 device comparison
→ pre-scoring
→ M9 SCORE-GEO-002
→ M10 prioritization
→ M14 element linking
→ M20 advisory generation (downstream de findings/scoring)
→ M11/M16/M17 intermediate reporting
→ M18 telemetry enrichment
→ report_site finalization
→ M20 report-site enrichment
```

M20 não participa do scoring. `audit.db` e artifacts continuam fonte de verdade.

## Device context

CLI default `mobile`; valores `mobile`, `desktop`, `both`. M3 materializa apenas o selecionado e M7/M20 só podem atuar nos snapshots existentes.

## M20

Modules:

```text
src/searchgeo/m20.py
src/searchgeo/m20_ai.py
src/searchgeo/m20_persistence.py
src/searchgeo/m20_reporting.py
```

M20 roda depois de M9/M10/findings e cria apenas entidades auxiliares. A remediação textual é default OFF. JSON-LD determinístico é sempre materializado.

### Contrato factual

Request limitado ao contexto persistido; resposta deve referenciar finding/evidence válidos. Validação local impede IDs externos e novos tokens numéricos não suportados. A saída é advisory e exige revisão humana.

### JSON-LD

Ausência: baseline conservador `WebPage` com dados persistidos. Existente: revisão não destrutiva. Nenhuma alteração é aplicada ao site.

## Provider routing e credenciais

M18 explicit/auto mantém quarantine e URL lock. M20 reutiliza providers elegíveis sem reativar quarantined.

Credenciais são isoladas por provider. A herança do adapter OpenAI foi endurecida para impedir que subclasses DeepSeek/MiMo consultem `OPENAI_API_KEY` quando sua própria chave está ausente.

## SQLite lifecycle

Conexões transitórias devem ser fechadas explicitamente. O context manager nativo de `sqlite3.Connection` controla transação, **não fecha o handle**. Isso é especialmente relevante no Windows, onde um `audit.db` aberto impede remoção do `TemporaryDirectory`.

## Report final

```text
report/index.html
report/mobile.html       # condicional
report/desktop.html      # condicional
report/remediation.html
report/content-suggestions.html
report/ai-usage.html
report/references.html
report/css/site.css
```

`report_site` não chama IA. `m20_reporting` projeta somente o estado M20 já persistido.

## Confidence

É reliability da conclusão do auditor, não métrica direta de qualidade textual. Não pode ser gatilho isolado para M20.

## Testing

```powershell
python -m compileall -q src tests
python -m unittest discover -s tests -v
```

A estabilização final exige Windows + Linux. Regressões cobrem lifecycle SQLite no Windows, credenciais ambientais isoladas, provider credential isolation, device context, M20 OFF/ON, JSON-LD e report site.
