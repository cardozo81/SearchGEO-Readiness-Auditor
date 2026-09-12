# Cancelamento de credenciais e restauração/reset no console

Este documento descreve o comportamento seguro do gerenciamento de credenciais, do reset avançado por variável/grupo e da restauração integral dos padrões do produto no `rasai-console`.

A baseline oficial do produto está documentada em [SYSTEM_DEFAULTS.md](SYSTEM_DEFAULTS.md) e é distribuída em `src/rasai/config/rasai-defaults.ini`.

## 1. Cancelamento ao definir Key/token/secret

A edição de um secret é transacional do ponto de vista do operador.

Fluxo esperado:

1. o usuário escolhe **Definir/alterar**;
2. digita ou cola o valor;
3. o terminal mostra apenas `*` para os caracteres recebidos;
4. o valor é validado em memória;
5. o console apresenta:

```text
C. Confirmar alteração
V. Cancelar e manter o valor atual
```

Somente `C` grava o novo valor na sessão.

Ao escolher `V`:

- o valor anterior permanece intacto;
- um secret que ainda não existia continua ausente;
- nada é persistido no Windows/User;
- nada é escrito no `rasai-console.ini`;
- o valor digitado é descartado após sair do fluxo.

O conteúdo real do secret nunca é exibido.

## 2. Restaurar padrões do RASAi

O menu principal oferece:

```text
D. Restaurar padrões do RASAi
```

Esse fluxo é diferente do reset avançado por grupo. Ele reconstrói a configuração operacional a partir do `rasai-defaults.ini` da versão instalada e salva o resultado usando o writer canônico do `rasai-console.ini`.

O usuário escolhe entre:

1. **Restaurar padrões e preservar credenciais**;
2. **Restaurar padrões e remover credenciais** da sessão e, no Windows, de `Windows/User`.

Antes de executar, é exigida a confirmação textual:

```text
RESTAURAR
```

### Overrides não secretos

Overrides não secretos conhecidos pelo catálogo RASAi são removidos da sessão e, no Windows, de `Windows/User` em ambas as modalidades.

Isso é necessário porque a precedência normal continua sendo ambiente/SO sobre o INI. Se o console apenas regravasse o `rasai-console.ini`, um `RASAI_*` persistido no SO poderia continuar prevalecendo e a restauração não seria efetiva.

`RASAI_CONSOLE_INI` e `RASAI_CONFIG` são localizadores/bootstrap e não participam dessa limpeza operacional.

### Credenciais

Na opção **preservar**, secrets da sessão/Windows permanecem como estão.

Na opção **remover**, o console remove secrets conhecidos da sessão e, no Windows, do escopo `Windows/User`. O arquivo restaurado nunca recebe esses valores.

## 3. Reset avançado de variáveis

O menu **E. Variáveis de ambiente / credenciais** continua oferecendo:

```text
R. Resetar variáveis por grupo ou todas
```

Esse fluxo é mantido para diagnóstico e administração granular. Ele usa o catálogo `EnvironmentSpec` vigente e só atua sobre variáveis conhecidas pelo RASAi; não executa limpeza genérica do ambiente do sistema operacional.

### Escopo

O usuário pode selecionar:

- um grupo funcional, por exemplo `Web Performance / Google APIs`, `Métricas e padrões`, `IA - credenciais` ou `Synthetic Apdex`;
- **Todas as variáveis conhecidas**.

### Camadas

Após escolher o escopo, o usuário escolhe:

1. somente sessão atual;
2. sessão + persistência do estado resetado no `rasai-console.ini`;
3. no Windows, sessão + INI + Windows/User.

Esse reset granular continua exigindo a confirmação textual `RESETAR`.

## 4. Windows/User versus Windows/Machine

O RASAi só gerencia persistência no escopo **Windows/User**.

Nenhum dos fluxos remove valores de **Windows/Machine**.

Motivos:

- `Machine` pode exigir privilégio administrativo;
- a alteração afetaria outros usuários e processos;
- uma ferramenta de auditoria local não deve realizar esse tipo de limpeza global implicitamente.

Quando uma variável existe em `Machine`, o console informa que o valor foi preservado. Um novo processo pode herdar novamente esse valor e ele poderá prevalecer sobre o INI restaurado.

A remoção administrativa de `Machine` permanece responsabilidade explícita do operador/sistema.

## 5. Efeito sobre defaults e AUTO

A restauração integral usa a baseline versionada do produto.

A política vigente é:

- capacidade interna/local sem credencial: habilitada quando tecnicamente aplicável;
- serviço externo gratuito sem credencial: habilitado;
- integração dependente de credencial: AUTO/dirigida por requisitos ou inativa até cumprir os requisitos;
- segurança/administração: fail-closed;
- valores específicos do cliente que não podem ser inventados: vazio/AUTO.

Synthetic Navigation Apdex e Synthetic User Experience Apdex ficam habilitados no baseline com carga reduzida. O console informa que `>=100` amostras válidas é o alvo recomendado para sair de `small-group` e obter resultado mais representativo. Consulte [SYSTEM_DEFAULTS.md](SYSTEM_DEFAULTS.md).

O reset granular continua significando retornar ao default/AUTO vigente da variável selecionada.

## 6. INI e secrets

O writer canônico do `rasai-console.ini` é usado tanto no Save normal quanto na restauração integral e no reset granular que solicita persistência.

Secrets permanecem fora do arquivo em qualquer cenário.

Nenhum fluxo converte credencial em texto persistente e nenhum backup de configuração deve conter secrets.

## 7. Operações que não fazem parte do reset/restauração

Os fluxos não apagam:

- auditorias existentes;
- `AUD-*/audit.db`;
- relatórios HTML;
- banco do control plane;
- arquivos de projeto do usuário;
- variáveis Windows/Machine;
- credenciais externas no fornecedor original.

Remover uma API key do RASAi não revoga a credencial no provider. Revogação deve ser feita no painel oficial do fornecedor.

## 8. Segurança e rastreabilidade

O fluxo preserva os seguintes princípios:

- secrets nunca aparecem em claro;
- a troca de secret só ocorre depois de confirmação;
- remoção de Windows/User requer escolha explícita quando envolve credenciais;
- Windows/Machine é fail-safe/preservado;
- erros de remoção são exibidos e não são mascarados como sucesso;
- o catálogo canônico continua sendo a fonte de quais variáveis pertencem ao RASAi;
- o arquivo de padrões é versionado e não contém secrets;
- o INI restaurado é materializado pelo mesmo writer usado no Save normal.

Documentos relacionados:

- [SYSTEM_DEFAULTS.md](SYSTEM_DEFAULTS.md)
- [CONSOLE_CONFIGURATION_UX.md](CONSOLE_CONFIGURATION_UX.md)
- [INTERACTIVE_CONSOLE.md](INTERACTIVE_CONSOLE.md)
- [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md)
- [WEB_PLATFORM_BASELINE.md](WEB_PLATFORM_BASELINE.md)
