# Console interativo de execução

O SearchGEO mantém `searchgeo audit` como interface estável e oferece, opcionalmente, um console textual para configuração, pré-validação e acompanhamento de auditorias:

```powershell
searchgeo-console
```

O console é uma camada de orquestração. Ele **não implementa um segundo pipeline**: após validar a configuração, chama o mesmo `python -m searchgeo audit ...` usado pela CLI estável.

## Objetivo

Reduzir erros operacionais de combinação de parâmetros, tornar visível o estado corrente da execução, explicar o impacto de cada opção e facilitar o acesso aos artefatos finais sem alterar scoring, regras, persistência ou relatórios.

O cabeçalho é reexibido durante a execução e contém no mínimo:

- versão do aplicativo;
- status da auditoria;
- URL atual/mais recentemente materializada;
- dispositivo;
- operação corrente, distinguindo processamento local, integração HTTP e APIs externas;
- variáveis de ambiente relevantes configuradas.

Credenciais nunca são exibidas. Variáveis sensíveis aparecem somente como `[SET]`.

## Defaults

Na ausência de override correspondente por variável de ambiente, o console inicia com:

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

Valores de ambiente reconhecidos para dispositivo, M20 e M21 são sincronizados no estado visual do menu na inicialização. Assim, o console não exibe uma opção e executa outra por precedência silenciosa.

**URL única é o default.** Arquivo TXT precisa ser selecionado explicitamente.

## Menu principal

Além das opções de configuração, o menu contém:

```text
H. Ajuda / custos
E. Variáveis de ambiente
R. Executar [APTO|BLOQUEADO] <motivo>
Q. Sair
```

`R` só inicia o subprocesso quando o preflight está apto. Se a configuração for inválida ou incompatível, o menu mostra `BLOQUEADO`, e pressionar `R` não cria a auditoria.

O menu também usa marcadores curtos para tornar visíveis configurações que ampliam consumo:

```text
[CUSTO EXTERNO]        provider de IA habilitado
[CUSTO IA ADICIONAL]   remediação textual M20 habilitada
[QUOTA EXTERNA]        Web Performance M21 habilitado
[VOLUME↑]              mobile + desktop
[VOLUME]               limite que amplia o teto de processamento
[LIMITE QUOTA]         teto de páginas do Web Performance
```

Os marcadores são alertas operacionais. Eles **não são invoice, cotação nem garantia de cobrança**.

## Ajuda contextual e custos

`H. Ajuda / custos` descreve, para cada parâmetro do menu:

1. para que serve;
2. o que altera na execução;
3. se possui custo externo direto, potencial;
4. se consome quota externa;
5. se funciona como multiplicador de volume.

A ajuda diferencia quatro conceitos:

- **sem custo externo direto:** configuração/local processing sem chamada paga por si só;
- **pode gerar custo externo:** integração de IA sujeita ao preço/plano do provider;
- **consome API/quota externa:** serviço externo cuja quota/billing pertence ao provedor do serviço;
- **multiplicador de consumo:** opção que não tem preço próprio, mas pode aumentar o número de contextos, páginas ou chamadas.

### Resumo de exposição da configuração atual

A mesma tela produz um resumo dinâmico da seleção corrente. Exemplos:

```text
IA externa: OFF — nenhuma chamada de IA configurada.
M20 textual: OFF — sem chamadas adicionais de remediação textual.
Dispositivo: MOBILE — um único contexto de dispositivo por etapa aplicável.
Web Performance: OFF — sem chamadas PageSpeed/CrUX pelo M21.
```

ou:

```text
IA externa: ON (openai) — pode haver cobrança por uso conforme provider/modelo/plano.
M20 textual: ON — pode acrescentar chamadas de IA para findings elegíveis.
Dispositivo: BOTH — pode multiplicar contextos mobile/desktop e o consumo associado.
Web Performance: ON — até 10 páginas; consome API/quota externa.
```

O SearchGEO não converte configuração em valor monetário antecipado porque preço, crédito, quota, cobrança mínima e regras comerciais pertencem aos serviços externos e podem mudar. A telemetria persistida da auditoria continua sendo a fonte para uso/custo estimado quando o provider fornece dados suficientes.

### Impactos de custo mais relevantes

| Parâmetro | Classificação | Impacto |
|---|---|---|
| IA = `none` | sem custo de IA externa | não chama provider de IA |
| IA = provider/AUTO | custo externo potencial | chamadas podem ser cobradas conforme modelo/tokens/plano |
| M20 textual = ON | custo IA adicional potencial | pode criar chamadas adicionais para findings elegíveis |
| device = `both` | multiplicador | pode produzir contextos mobile + desktop |
| `max-pages` | multiplicador | aumenta o teto potencial de crawl/snapshots/IA |
| Web Performance = ON | quota/API externa | PageSpeed/CrUX são serviços externos |
| `web-performance-max-pages` | limitador de quota | reduz/amplia o teto de páginas submetidas ao M21 |
| idioma/mercado/projeto | sem custo externo direto | metadados/contexto local |
| audits root | sem custo externo direto | apenas armazenamento local |

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

Na implementação corrente desta branch, `openai`, `deepseek` e `mimo` exigem:

1. credencial correspondente configurada;
2. modelo configurado/default pertencente ao catálogo suportado;
3. reasoning effort válido para o adapter.

`auto` só fica disponível quando existe ao menos um provider explícito elegível.

Regras específicas correntes:

```text
OPENAI_API_KEY   -> OpenAI
DEEPSEEK_API_KEY -> DeepSeek
MIMO_API_KEY     -> MiMo PAYG
```

Para MiMo, o adapter atual aceita a família PAYG `sk-...`. Chave Token Plan `tp-...` é rejeitada no preflight e não aparece como configuração executável.

> A lista de providers será sincronizada com o contrato/registry definitivo do adapter após a conclusão da branch específica de novos providers. O console não deve ser mergeado antes dessa integração e do smoke humano.

### Remediação textual M20

Só pode ser ativada quando o provider de IA selecionado está apto. `none + remediação textual` é bloqueado antes da criação da auditoria.

M20 pode gerar chamadas adicionais de IA e por isso é marcado como possível custo adicional. A revisão/proposta JSON-LD determinística não depende de API externa.

### Web Performance M21

PageSpeed/Lighthouse pode ser habilitado sem chave em cenários suportados pelo serviço.

`field_source=crux` só fica disponível quando `SEARCHGEO_CRUX_API_KEY` está configurada.

PageSpeed/CrUX são tratados pelo console como **API/quota externa**, não como IA. O console não presume preço monetário: quota e eventual billing são administrados pelo projeto Google Cloud e pela política vigente do serviço.

## Variáveis de ambiente

O menu `E. Variáveis de ambiente` permite alterar/remover variáveis suportadas **somente para a sessão corrente do console e os subprocessos que ele iniciar**. Ele não grava permanentemente o perfil do PowerShell/Windows.

São expostas as variáveis SearchGEO conhecidas, credenciais de providers/Google e `PLAYWRIGHT_CHROMIUM_EXECUTABLE`.

O submenu agora contém:

```text
S = setar/alterar
R = remover
H = ajuda/custo
V = voltar
```

Em `H`, o usuário pode informar o número de uma variável ou `0` para consultar todas. Para cada variável, o console explica finalidade e impacto de custo/consumo.

A classificação de ajuda também possui regras genéricas para futuras variáveis de providers:

- nomes contendo `API_KEY`, `TOKEN`, `SECRET`, `PASSWORD` ou `CREDENTIAL` são tratados como credenciais e mascarados;
- variáveis terminadas em `_MODEL` são descritas como seleção de modelo, potencialmente com preço distinto;
- variáveis terminadas em `_REASONING_EFFORT` são descritas como controle de esforço que pode afetar processamento/custo conforme provider.

Isso reduz a dependência da ajuda em nomes fixos de providers, embora a seleção dinâmica do menu de IA ainda dependa da refatoração futura do registry.

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
- durante `ANALYZING`, a tentativa mais recente em `ai_provider_attempts` permite mostrar o provider efetivamente chamado, inclusive sob `AUTO`;
- `audit.log` informa integrações M21 e erros operacionais;
- eventos `M21_EXTERNAL_ATTEMPT` permitem mostrar serviço, URL e dispositivo exatos para PageSpeed/CrUX.

Mapeamento operacional resumido:

```text
DISCOVERING / ACQUIRING -> INTEGRATION:HTTP
ANALYZING + IA           -> API:<provider efetivo>
ANALYZING sem IA         -> LOCAL:SEMANTIC_RULES
COMPARING/SCORING        -> LOCAL:RULES/SCORE
REPORTING                -> LOCAL:REPORT
M21                      -> API:PAGESPEED/CRUX
```

## Acesso direto à auditoria concluída

Quando a execução termina, o console apresenta um submenu específico da auditoria da sessão:

```text
P. Abrir pasta da auditoria [OK|INDISPONÍVEL]
I. Abrir relatório HTML     [OK|INDISPONÍVEL]
M. Voltar ao menu
Q. Sair
```

### `P. Abrir pasta da auditoria`

Abre diretamente:

```text
audits/<AUD-ID>/
```

no gerenciador de arquivos padrão do sistema operacional.

O console usa **somente o `AUD-ID` da sessão corrente**. Ele não abre simplesmente a pasta mais recente do diretório, evitando levar o usuário para uma auditoria concorrente ou anterior.

### `I. Abrir relatório HTML`

Abre o entrypoint do relatório no handler padrão do sistema, normalmente o navegador. A resolução prefere a estrutura corrente:

```text
audits/<AUD-ID>/report/index.html
```

Para compatibilidade com workspaces antigos, também reconhece:

```text
audits/<AUD-ID>/report.html
audits/<AUD-ID>/index.html
```

O formato atual `report/index.html` sempre tem precedência quando existe.

Depois de voltar ao menu principal, os atalhos `P` e `I` continuam disponíveis enquanto a auditoria daquela sessão puder ser resolvida.

A abertura é implementada pelo mecanismo nativo do SO:

- Windows: handler padrão do sistema;
- macOS: `open`;
- Linux: `xdg-open`.

Falha ao abrir pasta/HTML não altera a auditoria nem o report; o console apenas informa o erro operacional.

## Segurança

O console não imprime valores de:

- `OPENAI_API_KEY`;
- `DEEPSEEK_API_KEY`;
- `MIMO_API_KEY`;
- `SEARCHGEO_PAGESPEED_API_KEY`;
- `SEARCHGEO_CRUX_API_KEY`;
- nomes adicionais que indiquem token, secret, password ou credential.

O subprocesso recebe uma cópia do ambiente corrente e continua usando os adapters existentes. Nenhum endpoint ou regra de isolamento de credenciais foi alterado.

Os atalhos de artefatos não executam HTML como código da aplicação: solicitam ao sistema operacional que abra um arquivo já produzido no workspace da auditoria.

## Smoke humano obrigatório antes do merge

A branch desta feature só deve ser integrada após smoke humano em Windows/PowerShell e após sincronização com a implementação definitiva dos novos providers.

Checklist mínimo:

1. atualizar a branch com a base aprovada após conclusão/merge dos novos providers;
2. instalar a branch em editable mode;
3. executar `searchgeo --version` e confirmar que a CLI histórica segue funcionando;
4. abrir `searchgeo-console`;
5. confirmar cabeçalho com versão/status/URL/dispositivo/operação/ambiente;
6. confirmar que URL única é o default;
7. confirmar `H. Ajuda / custos` e revisar explicações dos 10 parâmetros;
8. ativar IA/M20/M21/both e confirmar os marcadores de custo/volume correspondentes;
9. abrir `E -> H` e confirmar ajuda individual e `0=todas` sem exposição de secrets;
10. executar uma URL com `none`, Mobile e Web Performance OFF;
11. ao concluir, usar `I` e confirmar abertura de `report/index.html`;
12. usar `P` e confirmar abertura de `audits/<AUD-ID>/` correto;
13. voltar ao menu e confirmar que `P/I` continuam apontando para a última auditoria da sessão;
14. executar TXT com duas URLs da mesma origem;
15. tentar TXT com origens diferentes e confirmar bloqueio antes da auditoria;
16. sem keys, confirmar providers/AUTO indisponíveis segundo o registry definitivo;
17. configurar uma key válida e confirmar habilitação somente do provider correspondente;
18. validar regras específicas de credencial/plano definidas pelo adapter final;
19. habilitar `crux` sem `SEARCHGEO_CRUX_API_KEY` e confirmar indisponibilidade;
20. provocar/usar um erro de provider já conhecido e confirmar bloqueio transitório no menu;
21. alterar a key do provider e confirmar que o bloqueio transitório é limpo;
22. confirmar que nenhum valor de credencial aparece no cabeçalho, ajuda ou saída;
23. confirmar que o relatório final e `audit.db` são equivalentes aos produzidos pela CLI para a mesma combinação.

Somente após esse smoke e a revisão do diff a branch deve ser considerada candidata a merge.
