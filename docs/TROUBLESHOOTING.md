# TROUBLESHOOTING.md

## `searchgeo` não é reconhecido

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

Use CPython 3.13.x.

## Report

Ponto de entrada: `audits/<AUD-ID>/report/index.html`. `desktop.html` só existe quando Desktop foi selecionado; `mobile` é o default.

`report/content-suggestions.html` é esperado em auditorias M20 mesmo com IA OFF porque a revisão JSON-LD é determinística.

## Confidence LOW

Não significa texto ruim/não-GEO. Significa conclusão do auditor com base limitada. Não reescreva conteúdo apenas para elevar Confidence; a mudança exige finding/evidência específica.

## Provider explícito sem token

Deve ficar `NOT_CONFIGURED` e não chamar API. Ausência de chave de outro provider não interfere. O runtime isola credenciais: `OPENAI_API_KEY` nunca deve preencher DeepSeek/MiMo ausentes.

## Tenho plano/créditos mas a API falha

Confirme primeiro produto de API, credencial, endpoint, saldo/quota e acesso ao modelo.

- **OpenAI:** ChatGPT e API Platform possuem billing separado.
- **DeepSeek:** `402` indica saldo insuficiente da API.
- **MiMo:** `tp-...` pertence a Token Plan e não deve ser usado no endpoint PAYG; `sk-...` é PAYG e `402` indica saldo PAYG insuficiente.

Detalhes: [AI_GUIDE.md](AI_GUIDE.md).

## M20 não gerou texto

Verifique `report/content-suggestions.html` e `report/ai-usage.html`.

Estados legítimos incluem:

- `DISABLED`: default OFF;
- `NO_ELIGIBLE_FINDINGS`: não havia finding contentual/semântico elegível;
- `NOT_CONFIGURED`: M20 habilitado sem provider saudável;
- `NO_SAFE_SUGGESTIONS`: provider respondeu mas nenhuma proposta passou pelo contrato;
- `DEGRADED`/`PARTIAL`: falha operacional localizada.

`Confidence LOW` isolado não é elegível.

## JSON-LD proposto mas não aplicado

Correto. O SearchGEO não edita o website. A proposta é advisory. Revise tipo/propriedades contra conteúdo visível e documentação do tipo antes de publicar.

## JSON-LD existente só mostra melhorias

Correto. O auditor evita reescrita destrutiva e aponta problemas verificáveis. Structured Data válido não garante rich result.

## TIMEOUT

Default 180 s (`SEARCHGEO_AI_TIMEOUT_SECONDS`). Não há retry automático.

## Custo

`ESTIMATED_COST` é estimativa local, não invoice nem identificação do plano comercial.

## Windows: `audit.db` bloqueado durante testes

A suíte foi corrigida para fechar conexões SQLite transitórias antes de `TemporaryDirectory` remover o workspace. Atualize a branch e repita a suíte. Um novo `WinError 32` deve ser tratado como regressão de lifecycle de conexão.

## Teste sem token fez chamada externa

Isso não deve ocorrer. Os testes de ausência de credencial neutralizam chaves reais do ambiente e existe regressão específica para isolamento entre OpenAI/DeepSeek/MiMo. Se aparecer token/custo real em um teste “sem token”, interrompa e reporte como falha de segurança do teste.

## Report sem CSS

Preserve `report/css/site.css` e, para screenshots, mova o workspace inteiro porque artifacts ficam em `../artifacts/`.

## URL_SET excede max-pages

Aumente `--max-pages`; o auditor rejeita omissão silenciosa de URL explícita.

## Logs

Não registre chaves, Authorization ou payload integral sensível.
