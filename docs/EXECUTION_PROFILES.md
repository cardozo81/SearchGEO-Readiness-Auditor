# Perfis de Execução do console

## Objetivo

Os **Perfis de Execução** simplificam a configuração de uma auditoria sem criar uma segunda fonte de verdade para o RASAi.

O perfil é uma camada temporária sobre a configuração normal:

```text
defaults canônicos do RASAi
        +
configuração normal da sessão/INI/SO
        +
perfil selecionado para a próxima execução
        +
ajustes finos feitos depois da seleção
        =
configuração efetiva da execução
```

O perfil existe somente em memória. Ele **não**:

- grava valores no `rasai-console.ini`;
- altera defaults do runtime;
- cria ou apaga variáveis em Windows/User;
- modifica Windows/Machine;
- grava credenciais;
- inventa termos SERP;
- inventa contexto YMYL/editorial;
- inventa parâmetros Synthetic Apdex;
- habilita silenciosamente Improvement Intelligence.

## Escopo: URL única

Perfis ficam disponíveis somente quando o item **1. Entrada** possui uma URL única explícita.

Se a entrada estiver em modo TXT/arquivo ou ainda não houver URL informada, o menu mostra o recurso como `INDISPONÍVEL`.

Se o operador trocar de URL para arquivo enquanto um perfil estiver ativo, o perfil é removido da sessão para impedir que um overlay pensado para uma URL seja aplicado a múltiplos targets.

## Estados visíveis antes da seleção

Todos os presets permanecem visíveis no catálogo para que o operador saiba quais capacidades existem e o que precisa parametrizar.

Exemplo:

```text
 1. [APTO] SEO / Search Readiness
 2. [APTO] GEO / AI Readiness
 ...
 8. [CONFIGURAR] Search Intelligence / SERP
     Falta : Search Intelligence selecionado: configure os termos transitórios no item T
 9. [CONFIGURAR] Experiência sintética
     Falta : Experiência sintética selecionada: configure Synthetic/Experience Apdex antes da execução
10. [CONFIGURAR] Análise profunda URL
     Falta : Análise profunda selecionada: habilite/configure o item 13 antes da execução
12. [CONFIGURAR] Completo máximo
     Falta : ...
```

Semântica:

- `APTO`: o preset pode ser selecionado;
- `CONFIGURAR`: o preset continua visível, mas **não pode ser aplicado** enquanto houver dependência obrigatória ausente;
- `INDISPONÍVEL`: o próprio recurso de perfis não pode ser usado no contexto atual, por exemplo entrada em arquivo/múltiplas URLs.

Ao tentar abrir um preset `CONFIGURAR`, o console mostra as pendências e orienta o item de configuração correspondente. O operador deve voltar ao menu principal, parametrizar o recurso e retornar a `F. Perfil da execução`.

Essa validação antecipada não substitui o preflight do runtime. Ela evita a situação em que uma execução aparentemente "completa" termina e só no HTML o usuário descobre que uma capacidade nunca foi solicitada.

## Acesso

No menu principal:

```text
F. Perfil da execução
```

Sem perfil:

```text
F. Perfil da execução : NENHUM | disponível para URL única | sessão apenas
```

Com perfil ativo:

```text
F. Perfil da execução : APTO | <perfil> | SEM IA|IA SE DISPONÍVEL | SESSÃO
```

Perfis com dependência obrigatória faltante não entram no estado ativo.

## Perfis prontos

### SEO / Search Readiness

Envolve core determinístico de search readiness, Lighthouse SEO e Best Practices. Serviços já configurados, como GSC, continuam obedecendo seus próprios contratos.

Pode gerar chamadas PageSpeed/Lighthouse e CrUX conforme configuração/credenciais. IA é opcional e independente.

### GEO / AI Readiness

Envolve sinais para descoberta/consumo por agentes/IA, Lighthouse SEO, Best Practices, `agentic-browsing` e contexto semântico disponível.

`RASAI_CONTENT_RISK_PROFILE`, `RASAI_YMYL_CATEGORY` e demais campos editoriais continuam sob controle explícito do operador. `AUTO` permanece hipótese, não fato.

### Performance

Envolve Lighthouse Performance, Best Practices e field data conforme a configuração Web Performance vigente.

### Acessibilidade

Envolve Lighthouse Accessibility, Best Practices e as demais evidências determinísticas já existentes.

### Web Quality

Combina Best Practices, SEO e Accessibility. Validadores e observability já habilitados continuam com seus próprios contratos.

### SEO + GEO

Combina os módulos SEO e GEO na mesma execução.

### SEO + GEO + Performance

Combina search readiness, AI readiness e performance.

### Search Intelligence / SERP

O perfil **não cria termos**.

Para ficar `APTO`, exige:

- termos informados no item `T` da sessão;
- `RASAI_SERP_MODE` compatível com a execução;
- provider SERP válido;
- credencial quando `RASAI_SERP_MODE=live`;
- limites de queries/depth/requests válidos.

A validação do catálogo usa o mesmo contrato operacional do Search Intelligence; portanto termos presentes, mas provider/key/modo inválidos, continuam resultando em `CONFIGURAR`.

### Experiência sintética

O perfil **não cria threshold, amostras, tentativas, concorrência ou carga**.

Exige Synthetic Navigation Apdex e/ou Synthetic User Experience Apdex previamente configurado. A carga HTTP real contra o alvo permanece explícita.

### Análise profunda URL

Integra Improvement Intelligence somente quando o item **13. Análise profunda URL** já estiver habilitado e válido.

O perfil não inventa provider/model/reasoning. Quando o item 13 está ligado, o catálogo também valida a disponibilidade da IA exclusiva da análise profunda, incluindo credencial/provider/modelo conforme o contrato vigente.

Improvement Intelligence permanece evidence-bound, advisory/non-scoring e com segurança passiva.

### Completo seguro

Combina:

- SEO;
- GEO;
- Performance;
- Acessibilidade;
- Web Quality.

Deliberadamente **não ativa automaticamente**:

- Search Intelligence/SERP;
- Synthetic Apdex;
- Improvement Intelligence.

Esses grupos têm dependências, carga ou custo adicional que justificam opt-in explícito.

### Completo máximo

Combina **todos os módulos do catálogo**:

- SEO;
- GEO;
- Performance;
- Acessibilidade;
- Web Quality;
- Search Intelligence / SERP;
- Experiência sintética;
- Análise profunda URL.

O nome "máximo" descreve cobertura funcional; não significa relaxar segurança, limites ou metodologia.

O preset fica `CONFIGURAR` e **não pode ser selecionado** até que todas as dependências dos módulos opcionais estejam válidas. Isso normalmente inclui:

- termos e provider/credencial SERP;
- configuração Synthetic/Experience Apdex;
- item 13 habilitado com provider/model/reasoning válidos.

Depois que essas dependências ficam aptas, o operador ainda escolhe se a **IA padrão do perfil** será `SEM IA` ou `IA SE DISPONÍVEL`. A IA própria de Improvement Intelligence continua independente.

## Perfil personalizado

`C. Compor perfil personalizado` abre a lista guiada de módulos.

Cada módulo mostra finalidade, custo/exposição e dependências. Uma composição personalizada com dependência obrigatória ausente também permanece `CONFIGURAR` e não é aplicada até a parametrização ser concluída.

## IA padrão do perfil

Depois que um preset está apto, o console oferece:

```text
1. Não usar IA padrão nesta execução
2. Usar IA padrão se houver provider APTO
```

### Não usar IA

Durante a execução efetiva do perfil, `ai_provider` é projetado como `none`; a configuração persistida do usuário não é alterada.

### Usar se disponível

A regra é:

1. se o provider já selecionado pelo usuário estiver `APTO`, preservá-lo;
2. caso contrário, usar `AI=auto` somente se existir provider elegível/APTO;
3. se nenhum provider estiver apto, seguir sem IA padrão.

Esse modo não bloqueia o core quando não existe IA padrão disponível.

Credenciais nunca são criadas, trocadas ou persistidas pelo perfil.

Improvement Intelligence possui IA própria e independente no item 13.

## Dependências e `CONFIGURAR`

Uma capacidade explicitamente solicitada não deve ser silenciosamente omitida.

| Módulo | Dependência | Comportamento no catálogo |
|---|---|---|
| Search Intelligence | termos, modo, provider, credencial e limites | `CONFIGURAR`; preset não selecionável |
| Experiência sintética | Apdex previamente configurado | `CONFIGURAR`; preset não selecionável |
| Análise profunda | item 13 + IA deep válida | `CONFIGURAR`; preset não selecionável |
| GEO | contexto YMYL/editorial | `AUTO` é permitido e informado |
| IA padrão `se disponível` | provider apto | não bloqueia; fallback seguro para sem IA padrão |

O runtime continua executando sua validação final depois do catálogo. Se algo mudar entre a visualização e a aplicação, o preset é revalidado antes de entrar no estado ativo.

## Ajuste fino

Depois de escolher um perfil `APTO`, as opções normais continuam disponíveis. Ajustes explícitos feitos depois da seleção vencem o preset no domínio correspondente, por exemplo:

- item `4` → IA;
- item `5` → remediações;
- item `6` → Web Performance;
- item `11` → experiência sintética;
- item `13` → análise profunda;
- item `T` → Search Intelligence.

Alterações avançadas de Web Performance/Lighthouse também são respeitadas quando diferem da configuração-base capturada no momento da seleção.

## Precedência

Durante uma execução com perfil:

```text
ajuste manual posterior à seleção
> overlay do perfil
> configuração normal carregada na sessão
> default canônico do RASAi
```

Essa precedência existe somente para a execução.

## Persistência

Selecionar/remover um perfil não marca o INI como alterado porque o perfil não modifica o estado persistível.

O preset nunca é salvo. Um ajuste manual real continua podendo ser salvo somente pela ação explícita normal do usuário.

## Custos

Cada preset e módulo apresenta descrição de custo/exposição antes da aplicação. Quando aplicável, o detalhe mostra:

- nível de exposição;
- intervalo potencial de chamadas Web Performance;
- intervalo potencial de tentativas de IA;
- pricing unitário catalogado quando disponível;
- carga Synthetic Apdex já configurada;
- quantidade de termos SERP;
- aviso de chamadas adicionais da análise profunda.

O RASAi não inventa quantidade de tokens antes da execução e não converte quota em preço quando o provider não fornece base suficiente.

## Compatibilidade com os relatórios HTML

Perfis são uma superfície de **orquestração do console**, não uma nova fonte de evidência. Por isso não criam schema, score ou relatório paralelo.

Os relatórios continuam materializados a partir do estado/evidência realmente persistidos no `AUD-*`:

- `search-intelligence.html` apresenta observação SERP quando executada ou estado explícito sem observações;
- `apdex.html` apresenta Synthetic Navigation Apdex ou estado explícito de não execução;
- `apdex-experience.html` apresenta Synthetic User Experience Apdex ou estado explícito de não execução;
- `improvement-intelligence.html` apresenta a análise profunda ou estado explícito de não execução/falha conforme persistência;
- `ai-usage.html` distingue finalidade não solicitada/desabilitada de tentativa externa, resposta aceita, falha de provider/contrato, tokens e custo quando mensuráveis;
- as demais páginas recebem o quadro padronizado de consumo de IA atribuído à superfície proprietária, sem duplicar custo entre relatórios.

O novo `Completo máximo` não exige mudança de metodologia ou renderer: ele apenas impede que o usuário aplique o preset enquanto alguma capacidade obrigatória ainda não estiver configurada. Uma vez executada, cada superfície continua obedecendo seu contrato de evidência e reporting vigente.

Falha em runtime após um preset ter ficado `APTO` continua sendo possível (rede, provider, timeout, bloqueio do alvo etc.). Nesse caso o relatório deve mostrar falha/parcialidade; o console não fabrica dados para preencher uma capacidade que não concluiu.

## Segurança metodológica

Perfis selecionam **o que executar**, não alteram a metodologia.

Não modificam:

- `SARI-001`;
- `SCORE-GEO-004`;
- pesos de scoring;
- regras históricas;
- thresholds metodológicos sem ação explícita do operador.

A ausência/presença de evidência continua obedecendo ao contrato normal de cobertura/confiabilidade.