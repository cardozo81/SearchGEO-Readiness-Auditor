# Registry canônico de providers

## Objetivo

`src/searchgeo/provider_registry.py` é a interface canônica para qualquer superfície que precise descobrir providers, aliases, modelos, variáveis de ambiente, elegibilidade de AUTO ou restrições de configuração.

A regra é deliberada: CLI, console interativo, help, preflight e novas integrações **não devem manter listas próprias de providers**.

## Fontes preservadas

O registry não altera o comportamento homologado:

- M18 continua sendo a fonte normativa de comportamento dos providers legados OpenAI, DeepSeek e MiMo e da cadeia `AUTO`;
- `provider_extensions.py` continua encapsulando os adapters explicit-only xAI/Grok, Qwen, Gemini e Anthropic/Claude;
- o registry normaliza essas fontes numa API pública única para consumidores.

Isso evita duplicar a lista de providers em cada camada sem reabrir o núcleo M18.

## Metadados expostos

Cada `ProviderRegistration` informa:

- `id` canônico;
- nome técnico e nome de exibição;
- aliases CLI;
- variável da API key;
- variável de model override;
- variável de endpoint override, quando aplicável;
- variável e valores de reasoning, quando aplicável;
- modelos suportados e modelo default;
- qualification;
- se é `explicit_only`;
- se é elegível para `AUTO`;
- restrições de prefixo de chave quando existentes.

Nenhum valor de credencial é armazenado no registry.

## AUTO

`auto_provider_ids()` deve permanecer:

```text
openai -> deepseek -> mimo
```

Providers de extensão permanecem fora de `AUTO` enquanto estiverem em qualificação provisória. Configurar `XAI_API_KEY`, `DASHSCOPE_API_KEY`, `GEMINI_API_KEY` ou `ANTHROPIC_API_KEY` não altera a cadeia AUTO.

## CLI

`cli_extensions.py` obtém as opções explicit-only por `extension_cli_choices()`. Portanto, a CLI não possui mais uma segunda lista hardcoded dos novos providers.

## Console interativo

Após o merge seguro da expansão de providers, `feature/interactive-execution-console` deve ser sincronizada com `main` e substituir seu `PROVIDERS` hardcoded pelo registry.

O console deverá derivar do registry, no mínimo:

- menu de provider;
- aliases;
- disponibilidade por key;
- modelos/defaults;
- variáveis de ambiente editáveis;
- regras de reasoning;
- restrições específicas como MiMo PAYG `sk-...`;
- indicação `explicit-only`/`AUTO`;
- classificação/ajuda de configuração.

## Dependência de timezone no Windows

O SearchGEO usa `ZoneInfo("America/Sao_Paulo")` nos reports. Windows não fornece necessariamente a base IANA utilizada pelo Python. Por isso `tzdata>=2026.1` é dependência formal do package no `pyproject.toml`; uma instalação limpa com `python -m pip install -e .` deve disponibilizar essa timezone sem instalação manual adicional.
