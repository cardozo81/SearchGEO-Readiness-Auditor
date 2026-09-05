# Qualidade da origem, redirecionamentos e bloqueios técnicos

## Objetivo

O SearchGEO deve distinguir claramente:

1. a URL informada pelo usuário;
2. a cadeia HTTP efetivamente observada;
3. a URL final alcançada;
4. a existência de falha de transporte que impeça uma análise representativa do conteúdo.

Essa camada é anterior a interpretações GEO, Web Performance e Synthetic Apdex. Ela existe para impedir que uma falha de infraestrutura seja apresentada como ausência de conteúdo, baixa performance ou resultado estatístico normal.

## Fonte da evidência

A aquisição HTTP de M2 continua sendo a fonte determinística. `HttpClient` mantém validação TLS normal e registra:

- URL solicitada;
- cada salto de redirecionamento;
- status HTTP de cada salto;
- valor `Location`;
- URL de destino de cada salto;
- URL final;
- status HTTP final, quando obtido;
- classe do erro de rede/transporte;
- mensagem técnica sanitizada.

O SearchGEO **não desabilita validação TLS** para conseguir auditar um site com certificado inválido.

## Redirecionamento não é erro por definição

Um 301/302/307/308 pode representar comportamento correto, por exemplo migração de hostname ou canonicalização operacional.

O relatório, portanto, separa:

- **observação:** houve redirecionamento;
- **fato técnico:** cadeia, statuses e destino final;
- **avaliação determinística:** se a cadeia termina de forma tecnicamente utilizável;
- **validação humana:** se a mudança de hostname/domínio é a intenção de negócio correta.

Troca de hostname e salto `HTTPS → HTTP` recebem destaque porque merecem revisão, mas não são automaticamente tratados como falha quando a cadeia termina corretamente.

## Bloqueios técnicos determinísticos

A política `SOURCE-QUALITY-1` considera bloqueadores fortes, entre outros:

- `TLS` — certificado/cadeia/hostname não validável;
- `DNS` — hostname não resolvido;
- `REDIRECT_LOOP` — cadeia circular;
- `TOO_MANY_REDIRECTS` — limite de saltos excedido;
- `INVALID_REDIRECT` — `Location` ausente ou inválido;
- `PROTOCOL` — falha do protocolo HTTP antes de resposta utilizável.

`TIMEOUT` e erro genérico de conexão não são tratados automaticamente como bloqueadores definitivos nessa política, pois podem ser transitórios. Eles continuam registrados e analisáveis.

## Fail-fast

Quando **todas as páginas do universo auditado** estão bloqueadas por uma condição determinística de origem:

1. M2 preserva a evidência original;
2. o SearchGEO grava `artifacts/source-quality.json`;
3. o audit recebe limitação explícita;
4. Chromium não é novamente acionado apenas para reproduzir o mesmo bloqueio;
5. a análise semântica completa por IA não é chamada sobre conteúdo inexistente;
6. M20 não tenta remediar texto sem corpus confiável;
7. PageSpeed/CrUX não são chamados;
8. Synthetic Apdex não executa 100/125 navegações redundantes;
9. M21 e M23 registram `SKIPPED_SOURCE_BLOCKER`, com zero tentativas correspondentes;
10. o audit termina como `COMPLETE_WITH_LIMITATIONS`, preservando o diagnóstico produzido.

Essa política economiza tráfego, tempo e custo de API sem converter a falha do site em sucesso.

### Escopo parcial

Se somente parte das URLs estiver bloqueada, o SearchGEO não interrompe globalmente o audit. O fail-fast global é aplicado somente quando todo o universo auditado está tecnicamente bloqueado. As URLs problemáticas continuam identificadas individualmente.

## Synthetic Apdex

A metodologia M23 não foi modificada.

A especificação existente permite classificar uma tentativa de Task como `FRUSTRATED` quando ocorre erro de aplicação, timeout ou erro de navegação após o perfil sintético ter sido aplicado.

A correção de qualidade da origem atua **antes** dessa medição: se M2 já comprovou um bloqueio determinístico como TLS inválido, M23 não inicia a população repetitiva e persiste:

```text
status = SKIPPED_SOURCE_BLOCKER
attempted_samples = 0
valid_samples = 0
```

Dessa forma, o SearchGEO não produz um Apdex 0,000 baseado em cem repetições da mesma incompatibilidade TLS conhecida.

## Web Performance externo

Quando a origem está totalmente bloqueada:

```text
web_performance_runs.status = SKIPPED_SOURCE_BLOCKER
context_attempts = 0
PageSpeed attempts = 0
CrUX attempts = 0
```

O objetivo é não gastar chamadas externas para um alvo que o próprio audit já comprovou não ser tecnicamente utilizável.

## Explicação opcional por IA

Quando um provider compatível está ativo, o SearchGEO pode fazer **uma análise complementar de infraestrutura** com base exclusivamente na evidência determinística persistida.

Contrato atual:

```text
SOURCE-QUALITY-AI-v1
```

A IA recebe:

- URL solicitada;
- URL final;
- cadeia de redirecionamentos;
- status HTTP observados;
- classe determinística do erro;
- texto técnico do erro sanitizado;
- flags de troca de hostname e downgrade HTTPS→HTTP.

A IA pode explicar:

- causa provável dentro dos limites das evidências;
- se a cadeia parece tecnicamente coerente;
- quais ações devem ser verificadas por infraestrutura;
- quais pontos dependem de confirmação humana de intenção de negócio.

### Limites obrigatórios

A IA:

- **não altera** a classificação HTTP/TLS determinística;
- não pode declarar um certificado inválido como comportamento normal;
- não pode recomendar desabilitar validação TLS;
- não pode inventar CDN, proxy, servidor, SAN/CN ou configuração não observada;
- não altera SCORE-GEO-002;
- é fail-open: se indisponível, o diagnóstico determinístico continua completo.

O consumo dessa chamada é persistido em `ai_provider_attempts` com tokens/custo estimado quando o provider fornece telemetria.

Providers com wire format que ainda não possuem contrato homologado para essa explicação permanecem sem chamada extra; o relatório continua com diagnóstico determinístico.

## Relatórios individuais

Quando houver diferença entre URL solicitada e URL final ou qualquer erro técnico, **todas as páginas HTML do report** recebem o bloco:

> Origem, redirecionamentos e integridade de transporte

O bloco apresenta:

- URL solicitada;
- URL final observada;
- status HTTP final ou indicação de que não foi obtido;
- classe técnica;
- mensagem do erro;
- tabela da cadeia de redirects;
- recomendações determinísticas;
- explicação complementar de IA, quando disponível.

O bloco é idempotente e é aplicado após os enriquecimentos M21/M23 para cobrir também as páginas de Web Performance e Apdex.

## Exemplo que motivou a proteção

A evidência observada em smoke mostrou:

```text
https://mdsgroup.com/
  301 → http://www.mdsgroup.com/
  301 → https://mds.pt/
  TLS  → certificado não validável para o hostname final
```

Antes da correção, o audit avançava, Synthetic Apdex repetia 100 navegações e o audit podia terminar como `COMPLETE` sem limitação explícita.

Com `SOURCE-QUALITY-1`:

- a cadeia continua registrada;
- a falha TLS é destacada;
- a auditoria termina `COMPLETE_WITH_LIMITATIONS`;
- Chromium repetitivo, PageSpeed/CrUX e M23 são evitados quando todo o universo está bloqueado;
- o usuário recebe orientação técnica para corrigir a origem antes de reexecutar.

## Console interativo

O console normal não exibe mais o `stdout` bruto como `Saída recente`/`Saída final`.

Durante execução ele mostra somente estado operacional estruturado:

- Status;
- URL;
- dispositivo;
- operação;
- início/fim/duração;
- etapa;
- progresso;
- detalhe acionável;
- Audit ID;
- caminho do log técnico.

Logs internos completos continuam em:

```text
audits/<AUD-ID>/logs/audit.log
```

Em caso de bloqueio de origem, o cabeçalho informa que etapas repetitivas/externas foram interrompidas e aponta para o diagnóstico do report.

## Reversibilidade

A implementação é aditiva e não cria migration no schema base de `audit.db`.

Novos artefatos:

```text
artifacts/source-quality.json
artifacts/source-quality-ai.json   # somente quando a camada opcional é executada
```

M21/M23 utilizam suas tabelas aditivas já existentes para registrar `SKIPPED_SOURCE_BLOCKER`.

Não há alteração na fórmula de `SCORE-GEO-002` ou na fórmula Apdex.
