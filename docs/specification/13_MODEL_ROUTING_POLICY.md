# MODEL_ROUTING_POLICY.md

**Status:** BASELINE OPERACIONAL + SAFE PROVIDER EXTENSIONS  
**Objetivo:** escolher IA/modelo de acordo com esforço, risco e necessidade de acesso ao repositório, mantendo separado o routing do produto em runtime.

## 1. Separar dois usos de IA

### A. IA usada para desenvolver o SearchGEO Auditor

É a IA/agente que:

- lê especificações;
- cria ou modifica código;
- revisa arquitetura;
- executa testes;
- diagnostica problemas.

### B. IA usada pelo SearchGEO Auditor em runtime

É o `SemanticAnalysisProvider` utilizado para avaliar páginas e, quando explicitamente habilitado, apoiar M20.

As duas coisas não devem ser confundidas.

## 2. Roteamento por esforço — desenvolvimento

### Esforço baixo

Exemplos:

- correção textual;
- ajuste isolado;
- formatação;
- pequenas alterações de configuração;
- tarefas mecânicas sem impacto arquitetural.

Usar configuração rápida/default disponível. Não consumir raciocínio avançado sem necessidade.

### Esforço médio

Exemplos:

- implementação de módulo isolado;
- revisão de código;
- testes;
- diagnóstico de bug não trivial;
- decisões técnicas locais.

Modelo recomendado atualmente: `GPT-5.6 Sol` ou modelo equivalente de raciocínio disponível no ambiente.

### Esforço alto / crítico

Exemplos:

- bootstrap estrutural;
- alteração transversal;
- Rules Engine;
- scoring;
- fallback/routing de IA;
- arquitetura de persistência;
- Desktop/Mobile;
- debugging complexo;
- revisão de consistência entre múltiplos documentos;
- migração que possa alterar comportamento funcional.

Utilizar `GPT-5.6 Sol` com a maior capacidade de raciocínio disponível no ambiente, ou agente de código equivalente.

Quando a tarefa exigir criar/editar arquivos no repositório, utilizar ferramenta/agente com acesso real ao repositório/filesystem. Um chat sem esse acesso não deve afirmar que gravou arquivos locais.

## 3. Runtime do produto

Arquitetura atual:

```text
SemanticAnalysisProvider
├── NONE
├── M18 legacy
│   ├── OPENAI
│   ├── DEEPSEEK
│   ├── MIMO
│   └── AUTO = OpenAI -> DeepSeek -> MiMo
└── provider extensions — explicit-only
    ├── XAI / GROK
    ├── QWEN
    ├── GEMINI
    └── ANTHROPIC / CLAUDE
```

O modelo específico deve continuar configurável porque:

- modelos mudam;
- disponibilidade muda;
- política corporativa pode mudar;
- provider corporativo pode ser diferente;
- endpoints/regiões podem variar.

O modelo escolhido em runtime deve possuir capacidade suficiente para:

- saída estruturada compatível com o contrato do adapter;
- interpretação semântica;
- evidence-grounded analysis;
- baixa propensão a inventar referências;
- usage/telemetria adequada quando disponível.

## 4. Baseline M18 e AUTO

A cadeia homologada permanece:

```text
OPENAI gpt-5.6-terra
→ DEEPSEEK deepseek-v4-pro
→ MIMO mimo-v2.5-pro
```

Provider configurado mas ausente de credencial não entra na cadeia. O primeiro resultado válido encerra o contexto. Quarantine e URL lock permanecem conforme M18.

A configuração de `XAI_API_KEY`, `DASHSCOPE_API_KEY`, `GEMINI_API_KEY` ou `ANTHROPIC_API_KEY` **não pode alterar AUTO**.

## 5. Providers de extensão

Enquanto `PROVISIONAL`, devem ser selecionados explicitamente:

```text
xai | grok
qwen
gemini
anthropic | claude
```

Defaults da qualificação atual:

```text
XAI       grok-4.6
QWEN      qwen3.8-max
GEMINI    gemini-3.8-flash
ANTHROPIC claude-sonnet-5
```

Qwen também admite `qwen3.8-flash` nesta qualificação.

A promoção para `QUALIFIED` ou inclusão em AUTO exige D-039: regressão, smoke humano real e mudança versionada/documentada.

## 6. Fallback e estados

Provider não configurado:

```text
NO_AI / NOT_CONFIGURED
```

Provider configurado mas indisponível:

```text
DEGRADED / UNAVAILABLE
```

Provider operacional:

```text
FULL / AVAILABLE
```

Em NO_AI ou DEGRADED:

- deterministic analysis continua;
- safe heuristics continuam;
- semantic-only rules podem virar UNKNOWN;
- website nunca recebe penalidade por ausência de capacidade da auditoria.

Provider explicit-only não faz cross-provider fallback.

## 7. Regra de extensão

Adicionar provider não deve exigir mudança em:

- Business Rules;
- Finding;
- Score;
- Report scoring semantics;
- Domain Model.

Para a expansão regida por M22, também não deve exigir mudança no comportamento homologado de `m18_ai.py`, `cli.py`, `m20_ai.py` ou AUTO.

Diferenças de Responses API, Chat Completions, Interactions ou Messages API devem ser encapsuladas pelo adapter e normalizadas para os tipos do SearchGEO.

## 8. M20

M20 reutiliza o provider selecionado/saudável e não introduz credencial alternativa.

- legacy M18 -> router M20 legado;
- extension explicit-only -> adapter M20 de extensão;
- quarantine anterior deve ser respeitada;
- M20 continua downstream de scoring e advisory.

## 9. Preço/usage

Usage é normalizado quando retornado pelo provider.

Preço só deve ser estimado quando houver catálogo versionado/qualificado para aquele provider/model/contexto. Provider de extensão provisório pode registrar tokens com `estimated_cost = null`; estimativa falsa é pior que ausência de estimativa.

## 10. Política de revisão

Para mudanças críticas:

1. ler especificação pertinente;
2. implementar em branch isolada;
3. executar testes mínimos orientados a risco;
4. revisar contra requisitos;
5. comparar explicitamente com `main` quando houver risco de regressão;
6. cumprir gates de PR/merge e smoke definidos pela especificação aplicável;
7. avançar somente quando blockers obrigatórios estiverem resolvidos.

Para provider extensions, seguir `22_SAFE_AI_PROVIDER_EXTENSIONS.md` e D-039.

## 11. Nota sobre esta política

A seleção exata de nomes comerciais/modelos pode mudar com disponibilidade do ambiente, mas qualquer alteração na allow-list do produto deve ser explícita e documentada.

A regra normativa permanece capability-based:

- tarefa simples → modelo rápido;
- tarefa não trivial → reasoning model;
- tarefa crítica/transversal → reasoning model forte;
- escrita no repositório → agente com acesso real;
- runtime semântico → provider configurável;
- ausência de provider → fallback obrigatório;
- provider novo → adapter isolado + qualificação;
- provider `PROVISIONAL` → explicit-only até gate humano.
