# SMOKE_TEST.md

Smoke test humano mínimo após instalação/merge.

## 1. Ambiente

```powershell
.\.venv\Scripts\Activate.ps1
python --version
searchgeo --version
searchgeo audit --help
```

Esperado: Python 3.13.x e help contendo `--device-context` e `--ai-provider`.

## 2. Mobile sem IA — default

```powershell
searchgeo audit https://example.com `
  --project "Smoke Mobile" `
  --max-pages 1
```

Esperado na CLI:

```text
Contexto de dispositivo: MOBILE
Relatório: audits\AUD-...\report\index.html
```

Validar no workspace:

```text
report/index.html          existe
report/mobile.html         existe
report/desktop.html        não existe
report/remediation.html    existe
report/ai-usage.html       existe
report/references.html     existe
report/css/site.css        existe
report.html                não existe na raiz
remediation.html           não existe na raiz
```

Abrir `report/index.html` e confirmar menu/layout.

## 3. CSS compartilhado

Inspecionar fonte de `index.html`:

```html
<link rel="stylesheet" href="css/site.css">
```

Não deve existir `<style>` embutido nas páginas finais do report site.

## 4. Confidence

Na visão geral, confirmar texto explícito de que:

- Coverage baixa não é nota baixa do website;
- Confidence LOW não significa texto ruim/não-GEO;
- Score, Coverage e Confidence são indicadores distintos.

## 5. Both

```powershell
searchgeo audit https://example.com `
  --project "Smoke Both" `
  --max-pages 1 `
  --device-context both
```

Esperado:

```text
report/mobile.html
report/desktop.html
```

O menu deve expor ambos.

## 6. Desktop apenas

```powershell
searchgeo audit https://example.com `
  --project "Smoke Desktop" `
  --max-pages 1 `
  --device-context desktop
```

Esperado:

```text
report/desktop.html existe
report/mobile.html não existe
```

## 7. OpenAI Mobile

Pré-requisito:

```powershell
Test-Path Env:OPENAI_API_KEY
```

Deve retornar `True` sem imprimir segredo.

Executar:

```powershell
searchgeo audit https://example.com `
  --project "Smoke OpenAI Mobile" `
  --max-pages 1 `
  --device-context mobile `
  --ai-provider openai
```

Abrir:

```text
report/ai-usage.html
```

Validar:

- provider/model;
- status;
- tentativas;
- device Mobile;
- tokens quando reportados;
- duração;
- custo estimado quando calculável;
- nenhuma API key.

Para uma página com um snapshot Mobile e provider saudável, não deve haver tentativa Desktop.

## 8. Timeout opcional

```powershell
$env:SEARCHGEO_AI_TIMEOUT_SECONDS = "240"
```

Repetir o teste somente se necessário. Default é 180 s.

## 9. AUTO

Com pelo menos duas chaves válidas:

```powershell
searchgeo audit https://example.com `
  --max-pages 1 `
  --device-context mobile `
  --ai-provider auto
```

Validar em `ai-usage.html`:

- cadeia inicial;
- primeiro resultado válido encerra o contexto;
- ausência de provider não configurado na cadeia;
- failover somente quando aplicável.

## 10. Remediation

Abrir:

```text
report/remediation.html
```

Para findings com M16/M17, confirmar presença de detalhes colapsáveis com:

- causa;
- reason code;
- selector observado/alvo;
- mudança recomendada;
- observado/esperado;
- critério de aceite;
- revalidação.

## 11. References

Abrir:

```text
report/references.html
```

Confirmar:

- fontes oficiais;
- Google generative AI optimization guide;
- OpenAI Publishers/Developers FAQ;
- RFC/WHATWG/Schema.org quando aplicáveis;
- fórmula SCORE-GEO-002;
- aviso de que thresholds visuais são internos;
- distinção entre standard oficial e heurística SearchGEO.

## 12. Suíte automatizada

```powershell
python -m compileall -q src tests
python -m unittest discover -s tests -v
```

Nenhum merge deve ocorrer com falha conhecida nessa suíte.
