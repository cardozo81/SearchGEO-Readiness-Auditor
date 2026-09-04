# Guia de leitura dos relatórios

O SearchGEO gera um mini-site HTML estático por auditoria. O report é projeção humana derivada da persistência; não recalcula scoring nem inventa dados ausentes.

## Entrada principal

```text
report/index.html
```

A página inicial resume:

- contexto da auditoria;
- Score, Coverage e Confidence;
- findings e recomendações;
- links para domínios complementares;
- **Configuração × resultado obtido**.

## Estrutura

```text
report/
├─ index.html
├─ mobile.html              # condicional
├─ desktop.html             # condicional
├─ remediation.html
├─ content-suggestions.html
├─ accessibility.html       # quando materializado
├─ web-performance.html
├─ apdex.html               # quando habilitado/materializado
├─ ai-usage.html
├─ references.html
└─ css/site.css
```

## Score GEO

O Score GEO é modelo interno de readiness e deve ser interpretado junto com Coverage e Confidence. Dados de Lighthouse, CrUX, Acessibilidade e Apdex não são somados ao Overall.

## Configuração × resultado obtido

A seção compara o que foi solicitado com o que realmente foi coletado/materializado.

Exemplos de estados legítimos:

```text
IA: não solicitada
IA: configurada, mas provider indisponível
Web Performance: SUCCESS
Web Performance: PARTIAL
Acessibilidade: NÃO OBTIDA — PageSpeed timeout
Synthetic Apdex: small-group
```

A causa deve ser persistida e apresentada. Timeout, quota, HTTP, ausência de artifact ou falta de dado da fonte não são convertidos em problema do website.

## Acessibilidade

`accessibility.html` apresenta somente evidência de acessibilidade automatizada realmente disponível no artifact Lighthouse.

Quando PageSpeed/Lighthouse falha, a página deve apresentar a causa concreta por URL/device, por exemplo:

```text
PageSpeed/Lighthouse falhou: TIMEOUTERROR
```

A página não representa certificação WCAG e não deve declarar conformidade com base somente no Lighthouse.

## Web Performance

`web-performance.html` reúne:

- status das tentativas PageSpeed;
- status das tentativas CrUX;
- Lighthouse lab quando disponível;
- Core Web Vitals de campo quando disponíveis;
- artifacts e limitações persistidas;
- diagnósticos técnicos de performance.

Synthetic Apdex não deve aparecer nessa página como métrica derivada de Lighthouse. O link de navegação para `apdex.html` é correto; conteúdo analítico de Apdex pertence à página dedicada.

## Synthetic Apdex

`apdex.html` apresenta:

- `T` e `4T`;
- Satisfied/Tolerating/Frustrated;
- amostras válidas/inválidas;
- tentativas;
- score Apdex;
- percentis e dispersão quando disponíveis;
- marcador `*` para small-group;
- rastreabilidade de perfil quando possível.

Apdex não é inferido de LCP, INP, CLS, FCP, TBT ou duração da chamada PageSpeed.

## Uso de IA

`ai-usage.html` apresenta finalidades de IA em linguagem funcional, incluindo:

- provider/modelo;
- esforço efetivo quando persistido;
- tentativas/sucessos;
- tokens;
- custo estimado;
- status/diagnóstico sanitizado.

Rótulos históricos de marcos não devem ser usados como nomes de funcionalidade na interface pública.

## Conteúdo e JSON-LD

`content-suggestions.html` reúne sugestões advisory e revisão/proposta estruturada. Nenhuma sugestão deve ser tratada como alteração automática do website.

## Remediações

`remediation.html` agrupa findings por causa/ação e deve preservar selector/evidência somente quando realmente observados.

## Referências

`references.html` documenta base metodológica e fontes públicas relevantes. A existência de uma referência não transforma uma prática em requisito universal de GEO/AEO.

## Consistência visual

Todas as páginas devem compartilhar:

- mesma navegação e ordem dos links;
- item atual selecionado;
- largura de conteúdo equilibrada;
- cards com acabamento consistente;
- tabelas legíveis e sem arredondamento excessivo;
- footer como último elemento do conteúdo principal;
- comportamento responsivo desktop/tablet/mobile.

## Falha de coleta

Quando uma integração configurada falha, o report deve responder quatro perguntas:

1. foi solicitada?
2. houve tentativa?
3. qual foi o status/erro?
4. qual informação ficou indisponível por causa disso?

Isso evita confundir ausência de evidence com resultado positivo, negativo ou zero.

## Fonte de verdade

Prioridade de evidência:

```text
audit.db + artifacts + audit.log
→ projeção HTML
```

O HTML não deve criar uma segunda fonte de verdade para telemetria, tokens, custos ou estado de coleta.
