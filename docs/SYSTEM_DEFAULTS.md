# Padrões canônicos do sistema

O `rasai-console` possui uma baseline versionada em `src/rasai/config/rasai-defaults.ini`.

Esse arquivo representa a configuração padrão do produto para uma instalação nova e para a ação **Restaurar padrões do RASAi**. Ele não substitui o `rasai-console.ini` do usuário e nunca contém secrets.

## Precedência

A configuração efetiva do console local segue:

1. argumento/ação explícita da sessão, quando aplicável;
2. variável de ambiente/processo ou valor persistido no SO;
3. `rasai-console.ini` do usuário;
4. `rasai-defaults.ini` versionado do produto;
5. fallback defensivo interno do código.

O `rasai-console.ini` continua sendo salvo pelo writer canônico já existente. API keys, bearer tokens, passwords, DSNs com credencial e demais secrets não são escritos nele.

Uma configuração explícita de maior precedência também governa dependências do baseline. Exemplo: `RASAI_SYNTHETIC_APDEX=false` desativa efetivamente o Experience Apdex herdado dos padrões quando o usuário não definiu Experience explicitamente. Se o operador definir ao mesmo tempo Navigation `false` e Experience `true`, a combinação continua sendo rejeitada como configuração contraditória; o RASAi não altera silenciosamente duas escolhas explícitas.

## Política do baseline

A baseline procura habilitar o máximo de capacidade de auditoria sem exigir credencial:

- capacidade interna/local sem credencial: habilitada;
- serviço externo gratuito sem credencial: habilitado;
- integração que exige credencial: continua dirigida por requisitos/AUTO ou desabilitada até a configuração obrigatória existir;
- superfície administrativa/de segurança: permanece fail-closed;
- valores específicos do cliente que não podem ser inventados permanecem vazios/AUTO.

Por isso W3C Nu HTML Checker, W3C CSS Validator, MDN HTTP Observatory, métricas derivadas, métricas de Information Retrieval, Open Web Metrics e Web Platform Baseline permanecem habilitados por padrão. Indisponibilidade, rate limit, egress bloqueado ou ausência de dataset deve ser tratada como limitação/NO_DATA/UNAVAILABLE, nunca como finding artificial do website.

PageSpeed, CrUX e Google Search Console não recebem hard-on/hard-off no arquivo de padrões. Eles continuam elegíveis automaticamente quando suas credenciais e demais requisitos existem.

## Synthetic Apdex

Synthetic Navigation Apdex e Synthetic User Experience Apdex ficam habilitados no baseline, porém com carga inicial deliberadamente baixa.

### Navigation Apdex

- habilitado: `true`;
- threshold `T`: `3 s`;
- amostras válidas por URL/dispositivo: `1`;
- máximo de tentativas: `2`;
- máximo de páginas: `1`;
- concorrência: `1`;
- delay: `1 s`.

`T=3 s` é uma baseline RASAi compatível com a referência temporal Dynatrace usada pelo produto; não é apresentado como SLO universal. Quando a organização conhece seu SLO/Task target real, esse valor deve prevalecer.

Com `T=3 s`, o Navigation Apdex classifica `Satisfied <= 3 s`, `Tolerating > 3 s e <= 12 s` e `Frustrated > 12 s`.

### Experience Apdex

- habilitado: `true`;
- amostras válidas por página: `20`;
- máximo de tentativas: `25`;
- máximo de páginas: `1`;
- device mix: `mobile=60,desktop=35,tablet=5`;
- sessão: `cold`;
- KPM executável: `USER_ACTION_DURATION`;
- Satisfied: `3 s`;
- Frustrated: `12 s`;
- erros qualificáveis afetam Apdex: `true`;
- escopo de erro: `first-party`;
- concorrência: `1`.

As 20 amostras foram escolhidas como baseline de baixa carga porque preservam a população 60/35/5 com pelo menos uma amostra de Tablet. O runtime continua marcando grupos abaixo de 100 como `small-group`.

O console deve informar que **100 ou mais amostras válidas** é a referência normal/recomendada para um grupo mais representativo. O número 100 não é atribuído à Dynatrace; é a baseline metodológica do RASAi para sair de `small-group`.

A referência Dynatrace continua correta: `VISUALLY_COMPLETE` é preservado como KPM primário de referência do fornecedor, mas o RASAi usa `USER_ACTION_DURATION` como fallback executável porque não reproduz `Visually Complete` com semântica vendor-equivalent.

## Restaurar padrões do RASAi

O menu principal expõe **D. Restaurar padrões do RASAi**.

Há duas modalidades:

1. restaurar configurações e preservar credenciais;
2. restaurar configurações e remover credenciais gerenciadas da sessão e, no Windows, de `Windows/User`.

Em ambas as modalidades, overrides **não secretos** conhecidos do RASAi são removidos da sessão e, no Windows, de `Windows/User`. Isso é necessário porque ambiente/SO tem precedência sobre o INI; apenas regravar o INI não garantiria que os padrões se tornassem efetivos.

`Windows/Machine` nunca é removido automaticamente. Se houver override nesse escopo, o console informa que ele foi preservado e que pode voltar a prevalecer em um novo processo.

`RASAI_CONSOLE_INI` e `RASAI_CONFIG` são tratados como localizadores/bootstrap e não são limpos pelo reset operacional.

Depois da confirmação textual `RESTAURAR`, o console:

1. limpa os overrides aplicáveis;
2. carrega a baseline da versão instalada;
3. aplica os valores ao estado da sessão;
4. salva a configuração restaurada com o writer canônico em `rasai-console.ini`;
5. mantém secrets fora do INI.

A restauração não apaga auditorias, `AUD-*/audit.db`, HTML reports, bancos do control plane ou arquivos de projeto.

## Distribuição e validação

O arquivo `src/rasai/config/rasai-defaults.ini` é package data do pacote `rasai`, portanto faz parte da instalação Python e não depende do diretório do repositório existir ao lado do executável.

A versão do arquivo é validada antes do uso. Testes de contrato verificam os valores de baixa carga do Apdex, a ativação das capacidades sem credencial, a precedência do `rasai-console.ini`, a precedência de overrides explícitos e a preservação/remoção opcional de credenciais.

Documentos relacionados:

- [CONFIGURATION.md](CONFIGURATION.md)
- [CONSOLE_VARIABLE_RESET.md](CONSOLE_VARIABLE_RESET.md)
- [INTERACTIVE_CONSOLE.md](INTERACTIVE_CONSOLE.md)
- [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md)
- [SYNTHETIC_APDEX.md](SYNTHETIC_APDEX.md)
- [SYNTHETIC_USER_EXPERIENCE_APDEX.md](SYNTHETIC_USER_EXPERIENCE_APDEX.md)
