# Console interativo de execução

O SearchGEO mantém `searchgeo audit` como interface estável e oferece, opcionalmente, um console textual para configuração, pré-validação e acompanhamento de auditorias:

```powershell
searchgeo-console
```

O console é uma camada de orquestração. Ele **não implementa um segundo pipeline**: após validar a configuração, chama o mesmo `python -m searchgeo audit ...` usado pela CLI estável.

## Objetivo

Reduzir erros operacionais de combinação de parâmetros e tornar visível o estado corrente da execução sem alterar scoring, regras, persistência ou relatórios.

O cabeçalho é reexibido durante a execução e contém no mínimo:

- versão do aplicativo;
- status da auditoria;
- URL atual/mais recentemente materializada;
- dispositivo;
- operação corrente, distinguindo processamento local, integração HTTP e APIs externas;
- variáveis de ambiente relevantes configuradas.

Credenciais nunca são exibidas. Variáveis sensíveis aparecem somente como `[SET]`.

## Defaults

O console inicia com:

```text
entrada            = URL única
mobile             = ativo
IA                 = none
remediação textual = off
Web Performance    = off
max-pages          = 100
idioma              = pt-BR
mercado             = BR
```

**URL única é o default.** Arquivo TXT precisa ser selecionado explicitamente.

## Entrada URL ou TXT

### URL única

A URL/domínio é enviada como target posicional ao `searchgeo audit`.

### Arquivo TXT

O arquivo é enviado por `--urls-file` e mantém a semântica atual de `URL_SET`.

Antes de iniciar, o console valida:

- arquivo existente e UTF-8 legível;
- pelo menos uma URL/domínio útil;
- sintaxe dos targets;
- todas as URLs na mesma origem normalizada;
- `max-pages` suficiente para todas as URLs únicas fornecidas.

## Disponibilidade dinâmica das opções

O menu mostra opções válidas como `OK` e impede selecionar opções `INDISPONÍVEL`.

### IA

`none` está sempre disponível.

`openai`, `deepseek` e `mimo` exigem:

1. credencial correspondente configurada;
2. modelo configurado/default pertencente ao catálogo suportado;
3. reasoning effort válido para o adapter.

`auto` só fica disponível quando existe ao menos um provider explícito elegível.

Regras específicas:

```text
OPENAI_API_KEY   -> OpenAI
DEEPSEEK_API_KEY -> DeepSeek
MIMO_API_KEY     -> MiMo PAYG
```

Para MiMo, o adapter atual aceita a família PAYG `sk-...`. Chave Token Plan `tp-...` é rejeitada no preflight e não aparece como configuração executável.

### Remediação textual M20

Só pode ser ativada quando o provider de IA selecionado está apto. `none + remediação textual` é bloqueado antes da criação da auditoria.

### Web Performance M21

PageSpeed/Lighthouse pode ser habilitado sem chave em cenários suportados pelo serviço.

`field_source=crux` só fica disponível quando `SEARCHGEO_CRUX_API_KEY` está configurada.

## Variáveis de ambiente

O menu `E. Variáveis de ambiente` permite alterar/remover variáveis suportadas **somente para a sessão corrente do console e os subprocessos que ele iniciar**. Ele não grava permanentemente o perfil do PowerShell/Windows.

São expostas as variáveis SearchGEO conhecidas, credenciais de providers/Google e `PLAYWRIGHT_CHROMIUM_EXECUTABLE`.

Validações locais incluem, conforme a variável:

- booleanos reconhecidos;
- dispositivo `mobile|desktop|both`;
- limites inteiros não negativos;
- timeouts positivos;
- field source permitido;
- modelo suportado;
- reasoning effort suportado;
- formato MiMo PAYG;
- existência do executável Chromium quando um caminho explícito é informado.

Essas validações verificam **aptidão de configuração local**, não saldo comercial, quota ou autenticação remota. Isso só pode ser conhecido quando a API responde.

## Erros detectados durante a execução

O console observa `audit.db` e `logs/audit.log` produzidos pelo pipeline estável.

Quando uma sessão M18 registra um provider como `QUARANTINED_FOR_AUDIT`, esse provider é bloqueado no menu pelo restante da sessão do console. O motivo persistido mais recente, como `AUTH_ERROR/HTTP 401` ou erro de crédito/quota, é apresentado como causa do bloqueio.

Alterar ou remover a credencial correspondente limpa esse bloqueio transitório e força nova avaliação local de capacidade.

Isso evita repetir imediatamente uma opção que acabou de falhar, sem alterar a política M18 do pipeline.

## Atualização do cabeçalho

O console acompanha o workspace criado pela execução:

- `audits.status` fornece a fase atual;
- o snapshot mais recente fornece URL/dispositivo corrente ou mais recentemente materializado;
- `audit.log` informa integrações M21 e erros operacionais;
- eventos `M21_EXTERNAL_ATTEMPT` permitem mostrar serviço, URL e dispositivo exatos para PageSpeed/CrUX.

Mapeamento operacional resumido:

```text
DISCOVERING / ACQUIRING -> INTEGRATION:HTTP
ANALYZING + IA           -> API:<provider>
ANALYZING sem IA         -> LOCAL:SEMANTIC_RULES
COMPARING/SCORING        -> LOCAL:RULES/SCORE
REPORTING                -> LOCAL:REPORT
M21                      -> API:PAGESPEED/CRUX
```

## Segurança

O console não imprime valores de:

- `OPENAI_API_KEY`;
- `DEEPSEEK_API_KEY`;
- `MIMO_API_KEY`;
- `SEARCHGEO_PAGESPEED_API_KEY`;
- `SEARCHGEO_CRUX_API_KEY`;
- nomes adicionais que indiquem token, secret, password ou credential.

O subprocesso recebe uma cópia do ambiente corrente e continua usando os adapters existentes. Nenhum endpoint ou regra de isolamento de credenciais foi alterado.

## Smoke humano obrigatório antes do merge

A branch desta feature só deve ser integrada após smoke humano em Windows/PowerShell.

Checklist mínimo:

1. atualizar/instalar a branch em editable mode;
2. executar `searchgeo --version` e confirmar que a CLI histórica segue funcionando;
3. abrir `searchgeo-console`;
4. confirmar cabeçalho com versão/status/URL/dispositivo/operação/ambiente;
5. confirmar que URL única é o default;
6. executar uma URL com `none`, Mobile e Web Performance OFF;
7. executar TXT com duas URLs da mesma origem;
8. tentar TXT com origens diferentes e confirmar bloqueio antes da auditoria;
9. sem keys, confirmar OpenAI/DeepSeek/MiMo/AUTO indisponíveis;
10. configurar uma key válida e confirmar habilitação somente do provider correspondente;
11. configurar MiMo `tp-...` e confirmar rejeição;
12. habilitar `crux` sem `SEARCHGEO_CRUX_API_KEY` e confirmar indisponibilidade;
13. provocar/usar um erro de provider já conhecido e confirmar bloqueio transitório no menu;
14. alterar a key do provider e confirmar que o bloqueio transitório é limpo;
15. confirmar que nenhum valor de credencial aparece no cabeçalho ou saída;
16. confirmar que o relatório final e `audit.db` são equivalentes aos produzidos pela CLI para a mesma combinação.

Somente após esse smoke e a revisão do diff a branch deve ser considerada candidata a merge.
