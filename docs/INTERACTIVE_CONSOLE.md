# Console interativo de execução

O SearchGEO mantém `searchgeo audit` como interface estável e oferece, opcionalmente, um console textual para configuração, pré-validação e acompanhamento de auditorias:

```powershell
searchgeo-console
```

O console é uma camada de orquestração. Ele **não implementa um segundo pipeline**: após validar a configuração, chama o mesmo `python -m searchgeo audit ...` usado pela CLI estável.

## Objetivo

Reduzir erros operacionais de combinação de parâmetros, tornar visível o estado corrente da execução, explicar o impacto de cada opção, antecipar exposição financeira/volume quando possível e facilitar o acesso aos artefatos finais sem alterar scoring, regras, persistência ou relatórios.

## Navegação em tela única

O console trabalha como uma interface de **uma tela lógica por vez**. Ao selecionar menu, ajuda, provider, modelo, variável de ambiente ou ação pós-execução, a tela anterior é limpa e a nova visão é redesenhada no topo do terminal.

Não é esperado empilhar sucessivos menus verticalmente durante uso interativo.

A limpeza usa ANSI em terminal TTY moderno. Em ambientes sem TTY, como redirecionamento para arquivo/teste automatizado, o console preserva saída textual e não depende de cor para transmitir significado.

## Cores e significado visual

Cores são reforço visual; os textos continuam explícitos para acessibilidade/fallback.

Convenção:

| Cor/ênfase | Uso |
|---|---|
| verde | `READY`, `COMPLETE`, `APTO`, variável/feature ativa |
| amarelo | execução em andamento, atenção, custo estimado |
| vermelho | erro, bloqueio, indisponibilidade, condição crítica |
| magenta | chamada de API externa |
| ciano/azul | informação, dispositivo, integração/local processing |
| dim/neutro | feature OFF, variável não definida, informação secundária |

`NO_COLOR` desabilita a coloração sem remover os rótulos textuais.

## Cabeçalho operacional

O cabeçalho é redesenhado durante a execução e contém:

- versão do aplicativo;
- status da auditoria;
- URL atual/mais recentemente materializada;
- dispositivo;
- operação corrente, distinguindo processamento local, integração HTTP e APIs externas;
- variáveis de ambiente relevantes configuradas;
- horário de início quando a execução foi iniciada;
- horário de fim após o encerramento;
- duração total, atualizada durante a execução;
- erro operacional, quando houver.

Exemplo:

```text
====================================================================================================
SearchGEO Readiness Auditor | versão 0.1.0
Status      : ANALYZING
URL         : https://example.com/produto
Dispositivo : MOBILE
Operação    : API:OPENAI
Ambiente    : OPENAI_API_KEY=[SET] | SEARCHGEO_WEB_PERFORMANCE=true
Início      : 2026-09-03 23:40:12 -0300
Fim         : -
Duração     : 00:01:37
====================================================================================================
```

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
idioma             = pt-BR
mercado            = BR
```

Valores de ambiente reconhecidos para dispositivo, M20 e M21 são sincronizados no estado visual do menu na inicialização. Assim, o console não exibe uma opção e executa outra por precedência silenciosa.

**URL única é o default.** Arquivo TXT precisa ser selecionado explicitamente.

## Menu principal

Além das opções de configuração, o menu contém:

```text
H. Ajuda / custos
E. Variáveis de ambiente
R. Executar [APTO|INDISPONÍVEL] <motivo>
Q. Sair
```

`R` só inicia o subprocesso quando o preflight está apto. Se a configuração for inválida ou incompatível, pressionar `R` não cria a auditoria.

O menu usa marcadores curtos:

```text
[CUSTO EXTERNO]        provider de IA habilitado
[CUSTO IA ADICIONAL]   remediação textual M20 habilitada
[QUOTA EXTERNA]        Web Performance M21 habilitado
[VOLUME↑]              mobile + desktop
[VOLUME]               limite que amplia o teto de processamento
[LIMITE QUOTA]         teto de páginas do Web Performance
```

Os marcadores são alertas operacionais. Eles **não são invoice, cotação nem garantia de cobrança**.

## Exposição financeira antes da execução

O menu calcula uma classificação qualitativa:

```text
NENHUM | BAIXO | MÉDIO | ALTO | EXCESSIVO
```

Essa classificação é um **índice interno de exposição financeira potencial**, não um preço cobrado pelo provider.

### O que entra no cálculo

A estimativa considera somente dados conhecidos antes da execução:

1. modo de entrada;
2. quantidade de URLs explícitas quando é usado TXT;
3. `max-pages` quando uma URL única é seed de crawl;
4. `mobile`, `desktop` ou `both`;
5. provider explícito ou cadeia elegível de `AUTO`;
6. modelo selecionado e faixa de preço unitário existente no `PRICING_CATALOG`;
7. M20 textual ligado/desligado;
8. Web Performance ligado/desligado;
9. `web-performance-max-pages`;
10. `field_source` e possibilidade de PageSpeed/CrUX direto.

### URL única versus TXT

Para URL única o número final de páginas ainda depende do crawl. O console apresenta:

```text
1 página conhecida → teto max-pages
```

Para TXT, depois de ler o arquivo localmente, o console conhece a quantidade de URLs únicas explícitas e usa esse número na projeção.

Exemplo:

```text
TXT = 12 URLs únicas
Device = both
```

produz 24 contextos potenciais de dispositivo antes de considerar IA/M20/M21.

### AUTO

Para `AUTO`, a projeção do teto considera a cadeia de providers elegíveis, porque uma falha pode fazer o contexto avançar para outro provider.

Isso é deliberadamente conservador: o primeiro resultado válido pode encerrar a cadeia e reduzir o consumo real.

### M20

M20 só chama IA quando existem findings elegíveis. Por isso ele entra no **teto** da projeção, mas não é presumido como chamada obrigatória.

### Web Performance

M21 é contabilizado como chamada/quota externa. PageSpeed é a chamada base; `auto`/`crux` podem exigir consulta direta adicional à CrUX.

O console **não inventa custo monetário para PageSpeed/CrUX** quando a execução não possui telemetria/preço monetário confiável persistido. Quota externa continua visível separadamente.

### Por que não há uma previsão de tokens em USD antes da execução

O tamanho real de prompt, conteúdo útil, cache, output e reasoning ainda não é conhecido. O console não assume uma quantidade arbitrária de tokens.

Quando o modelo selecionado possui preço no catálogo, a ajuda mostra o preço unitário público armazenado pelo SearchGEO, por exemplo:

```text
OPENAI/<modelo>: input USD X/1M tokens; output USD Y/1M tokens
```

A faixa `BAIXO/MÉDIO/ALTO/EXCESSIVO` usa volume máximo de tentativas potenciais combinado com a faixa relativa de preço do modelo. A fórmula é heurística interna de proteção operacional e não representa invoice.

## Ajuda contextual

`H. Ajuda / custos` descreve, para cada parâmetro:

1. para que serve;
2. o que altera na execução;
3. custo externo potencial;
4. quota externa;
5. efeito como multiplicador de volume.

A ajuda diferencia:

- **sem custo externo direto**;
- **pode gerar custo externo**;
- **consome API/quota externa**;
- **multiplicador de consumo**.

Também exibe o resumo dinâmico da configuração corrente, incluindo páginas conhecidas/teto, contextos de dispositivo, tentativas de IA potenciais, chamadas M21 potenciais e preços unitários catalogados.

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

A quantidade de URLs únicas válidas também alimenta a projeção de exposição antes da execução.

## Disponibilidade dinâmica das opções

O menu impede selecionar opções `INDISPONÍVEL`.

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

Para MiMo, o adapter atual aceita PAYG `sk-...`. Token Plan `tp-...` é rejeitado.

> A lista de providers será sincronizada com o contrato/registry definitivo do adapter após a conclusão da branch específica de novos providers. O console não deve ser mergeado antes dessa integração e do smoke humano.

### Remediação textual M20

Só pode ser ativada quando o provider selecionado está apto. `none + remediação textual` é bloqueado antes da criação da auditoria.

A revisão/proposta JSON-LD determinística não depende de API externa.

### Web Performance M21

PageSpeed/Lighthouse pode ser habilitado sem chave em cenários suportados pelo serviço.

`field_source=crux` exige `SEARCHGEO_CRUX_API_KEY`.

PageSpeed/CrUX são tratados como **API/quota externa**, não como IA.

## Variáveis de ambiente

O menu `E. Variáveis de ambiente` permite alterar/remover variáveis suportadas **somente para a sessão corrente do console e subprocessos filhos**. Ele não grava permanentemente perfil do PowerShell/Windows.

O submenu contém:

```text
S = setar/alterar
R = remover
H = ajuda/custo
V = voltar
```

Valores sensíveis aparecem como `[SET]`. Booleanos ligados recebem destaque de ativo; desligados/não definidos ficam visualmente secundários.

Em `H`, o usuário pode escolher uma variável ou `0` para consultar todas.

A ajuda possui regras genéricas para futuras variáveis:

- `API_KEY`, `TOKEN`, `SECRET`, `PASSWORD`, `CREDENTIAL` → credencial mascarada;
- `_MODEL` → seleção de modelo e possível diferença de preço;
- `_REASONING_EFFORT` → esforço de reasoning e possível impacto em processamento/tokens.

Isso reduz dependência da ajuda em nomes fixos, embora a seleção de providers ainda deva ser refatorada para o registry definitivo.

## Erros durante a execução

O console observa `audit.db` e `logs/audit.log` produzidos pelo pipeline estável.

Quando M18 registra `QUARANTINED_FOR_AUDIT`, o provider é bloqueado pelo restante da sessão do console. O motivo persistido, como `AUTH_ERROR/HTTP 401`, é exibido.

Alterar/remover a credencial correspondente limpa o bloqueio transitório e força nova avaliação local.

## Atualização do cabeçalho

O console acompanha:

- `audits.status`;
- snapshot mais recente para URL/dispositivo;
- `ai_provider_attempts` para provider efetivo durante `ANALYZING`, inclusive em `AUTO`;
- `audit.log` para M21 e erros;
- `M21_EXTERNAL_ATTEMPT` para serviço/URL/device exatos.

Mapeamento resumido:

```text
DISCOVERING / ACQUIRING -> INTEGRATION:HTTP
ANALYZING + IA           -> API:<provider efetivo>
ANALYZING sem IA         -> LOCAL:SEMANTIC_RULES
COMPARING/SCORING        -> LOCAL:RULES/SCORE
REPORTING                -> LOCAL:REPORT
M21                      -> API:PAGESPEED/CRUX
```

## Tempo de execução

O cronômetro começa imediatamente antes do subprocesso estável ser iniciado.

Durante a execução:

```text
Início  : timestamp local
Fim     : -
Duração : HH:MM:SS crescente
```

Ao terminar ou falhar após início:

```text
Início  : <timestamp>
Fim     : <timestamp>
Duração : <tempo total>
```

O tempo é medido por relógio monotônico para duração e relógio local timezone-aware para apresentação de início/fim.

## Consumo e custo ao final

Depois da auditoria o console consolida a telemetria persistida de:

```text
ai_provider_attempts
content_remediation_attempts
```

A tela final mostra:

- número total de tentativas de IA M18 + M20;
- tentativas bem-sucedidas;
- input tokens;
- cached input tokens;
- output tokens;
- reasoning tokens;
- total tokens;
- custo estimado por moeda, quando persistido;
- quantidade de tentativas com tokens mas sem custo estimável;
- número de chamadas M21 por serviço observadas em `M21_EXTERNAL_ATTEMPT`.

Exemplo conceitual:

```text
CONSUMO REAL / ESTIMADO PERSISTIDO
Tentativas IA       : 8 (sucesso: 6)
Tokens input        : 52,410
Tokens input cache  : 14,100
Tokens output       : 8,230
Tokens reasoning    : 3,180
Tokens total        : 60,640
Custo IA estimado   : USD 0.18420000
Chamadas M21        : 4 (PAGESPEED=2, CRUX=2)
Custo M21 monetário : não presumido
```

O valor de IA é a soma das estimativas persistidas pelos adapters usando seu catálogo de pricing e usage retornado pelo provider. **Não é invoice.**

Se uma tentativa tiver tokens mas não tiver preço/custo calculável, o console sinaliza explicitamente que o total monetário é parcial.

## Acesso direto à auditoria concluída

Ao terminar:

```text
P. Abrir pasta da auditoria [APTO|INDISPONÍVEL]
I. Abrir relatório HTML     [APTO|INDISPONÍVEL]
M. Voltar ao menu
Q. Sair
```

`P` abre:

```text
audits/<AUD-ID>/
```

`I` prefere:

```text
audits/<AUD-ID>/report/index.html
```

com fallbacks legados:

```text
audits/<AUD-ID>/report.html
audits/<AUD-ID>/index.html
```

O console usa somente o `AUD-ID` da sessão, não simplesmente a pasta mais recente.

Depois de voltar ao menu, `P/I` continuam disponíveis para a última auditoria resolvida da sessão.

A abertura usa o handler nativo do SO:

- Windows: handler padrão;
- macOS: `open`;
- Linux: `xdg-open`.

## Segurança

O console não imprime valores de credenciais/tokens/secrets.

O subprocesso recebe cópia do ambiente corrente e continua usando os adapters existentes. Nenhum endpoint, scoring ou regra de isolamento de credenciais foi alterado pelo console.

Os atalhos de artefatos apenas solicitam ao SO a abertura de arquivo/pasta já produzido.

## Smoke humano obrigatório antes do merge

A branch só deve ser integrada após smoke humano em Windows/PowerShell e após sincronização com a implementação definitiva dos novos providers.

Checklist mínimo:

1. atualizar a branch com a base aprovada após conclusão/merge dos novos providers;
2. refatorar provider selection para consumir o registry definitivo;
3. instalar a branch em editable mode;
4. executar `searchgeo --version` e confirmar que a CLI histórica segue funcionando;
5. abrir `searchgeo-console`;
6. navegar por todas as opções e confirmar que **cada ação redesenha uma única tela**, sem empilhar menus;
7. confirmar cores em terminal compatível e legibilidade equivalente com `NO_COLOR`;
8. confirmar cabeçalho com versão/status/URL/device/operação/ambiente;
9. confirmar início/fim/duração e atualização do cronômetro durante execução;
10. confirmar URL única como default;
11. confirmar exposição `NENHUM` com IA OFF e M21 OFF;
12. configurar IA e validar mudança de faixa conforme provider/modelo/volume;
13. usar TXT com múltiplas URLs e confirmar que o número exato de URLs únicas entra na projeção;
14. alternar mobile/desktop/both e confirmar multiplicador de contextos;
15. ativar M20 e confirmar aumento apenas do teto de tentativas potenciais;
16. ativar M21 e confirmar faixa de chamadas PageSpeed/CrUX sem preço monetário inventado;
17. revisar `H. Ajuda / custos` e preços unitários catalogados quando disponíveis;
18. abrir `E -> H` e confirmar ajuda sem exposição de secrets;
19. confirmar bloqueio de `R` para configuração inválida;
20. executar URL com `none`, Mobile e M21 OFF;
21. executar combinação com provider real em volume mínimo controlado;
22. ao final, reconciliar tokens/custo exibidos com `ai_provider_attempts` + `content_remediation_attempts`;
23. confirmar que tentativas sem pricing aparecem como custo parcial/não estimável;
24. confirmar contagem M21 contra eventos `M21_EXTERNAL_ATTEMPT`;
25. usar `I` e confirmar abertura de `report/index.html`;
26. usar `P` e confirmar abertura do `AUD-ID` correto;
27. voltar ao menu e confirmar que `P/I` continuam corretos;
28. tentar TXT com origens diferentes e confirmar bloqueio prévio;
29. validar disponibilidade dinâmica de todos os providers do registry final;
30. provocar provider quarantined e confirmar bloqueio transitório + limpeza ao alterar key;
31. confirmar que nenhum secret aparece em cabeçalho, menus, ajuda, saída ou resumo final;
32. confirmar equivalência de `audit.db` e report com `searchgeo audit` para a mesma configuração.

Somente após esse smoke e revisão final do diff a branch deve ser considerada candidata a merge.
