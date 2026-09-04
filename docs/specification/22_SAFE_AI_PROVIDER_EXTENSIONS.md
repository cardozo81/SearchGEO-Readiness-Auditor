# 22_SAFE_AI_PROVIDER_EXTENSIONS.md

**Status:** APPROVED FOR IMPLEMENTATION / HUMAN SMOKE GATE  
**Scope:** additive provider expansion without regression of M18 homologated routing  
**Does not alter:** Business Rules, `SCORE-GEO-002`, prioritization, report scoring semantics or M21

## 1. Objective

Expand the SearchGEO semantic-provider surface with high-adherence providers while preserving the previously homologated behavior of OpenAI, DeepSeek, MiMo and `AUTO`.

Providers introduced by this extension:

```text
XAI / GROK
QWEN
GEMINI
ANTHROPIC / CLAUDE
```

They are initially `PROVISIONAL` and `explicit-only`.

## 2. Non-regression invariant

The feature must not require behavioral changes to:

```text
src/searchgeo/m18_ai.py
src/searchgeo/cli.py
src/searchgeo/m20_ai.py
```

The M18 routing baseline remains:

```text
OPENAI -> DEEPSEEK -> MIMO
```

The presence of extension-provider API keys must not add them to `AUTO`, change ranking of existing providers, change default models, change existing error/quarantine behavior or cause additional provider requests after a valid result.

Any violation of this invariant is a release blocker.

## 3. Additive architecture

The extension is isolated in:

```text
src/searchgeo/provider_extensions.py
src/searchgeo/provider_extensions_m20.py
src/searchgeo/cli_extensions.py
```

Responsibilities:

- `provider_extensions.py`: explicit provider selection, native request/response adaptation, local schema/evidence validation, normalized usage/diagnostics and delegation of every legacy selection to M18;
- `provider_extensions_m20.py`: M20 support for extension providers while delegating legacy M20 routing unchanged;
- `cli_extensions.py`: public entrypoint shim that adds CLI choices without changing the original CLI module.

Package entrypoints may point to `cli_extensions:main`, but internal imports/tests of `searchgeo.cli` retain the legacy parser surface.

## 4. Provider selection

Public CLI values:

```text
xai
grok
qwen
gemini
anthropic
claude
```

Aliases:

```text
grok      -> XAI
claude    -> ANTHROPIC
```

The legacy values remain:

```text
none
openai
deepseek
mimo
auto
```

## 5. Qualification state

All extension models enter as `PROVISIONAL` with rank outside the legacy AUTO ranking space.

Supported initial qualification set:

```text
XAI       grok-4.6
QWEN      qwen3.8-max
QWEN      qwen3.8-flash
GEMINI    gemini-3.8-flash
ANTHROPIC claude-sonnet-5
```

A provider/model can move to `QUALIFIED` only after automated tests plus human smoke using real credentials and review of semantic completeness/telemetry/security.

A `PROVISIONAL` extension provider must never become an AUTO candidate by configuration alone.

## 6. Credential isolation

Each extension provider has its own API-key variable:

```text
XAI_API_KEY
DASHSCOPE_API_KEY
GEMINI_API_KEY
ANTHROPIC_API_KEY
```

Legacy variables remain isolated:

```text
OPENAI_API_KEY
DEEPSEEK_API_KEY
MIMO_API_KEY
```

Absence of the selected provider key must return `NOT_CONFIGURED` and produce zero external request. No credential can fill another provider's missing key.

Secrets, Authorization headers, API-key headers and unsanitized provider error bodies must never be persisted to SQLite, artifacts, report HTML or operational logs.

## 7. Model and endpoint configuration

Model variables:

```text
SEARCHGEO_XAI_MODEL
SEARCHGEO_QWEN_MODEL
SEARCHGEO_GEMINI_MODEL
SEARCHGEO_ANTHROPIC_MODEL
```

Endpoint variables:

```text
SEARCHGEO_XAI_ENDPOINT
SEARCHGEO_QWEN_ENDPOINT
SEARCHGEO_GEMINI_ENDPOINT
SEARCHGEO_ANTHROPIC_ENDPOINT
```

Default endpoints:

```text
XAI        https://api.x.ai/v1/responses
QWEN       https://dashscope-us.aliyuncs.com/compatible-mode/v1/chat/completions
GEMINI     https://generativelanguage.googleapis.com/v1beta/interactions
ANTHROPIC  https://api.anthropic.com/v1/messages
```

Endpoint overrides are configuration for a documented compatible deployment, not a mechanism to bypass provider restrictions.

Qwen keys/endpoints must belong to the same region/workspace.

## 8. Semantic contract

Extension adapters use the same SearchGEO semantic contract as M18:

```text
M18-SEMANTIC-22-v1
BR-GEO-028..049 exactly once each
```

Required safeguards:

1. structured JSON output requested through the provider's supported native contract;
2. local schema normalization through the existing SearchGEO validator;
3. exactly one assessment for every semantic rule;
4. no unknown/duplicate rule IDs;
5. no invented `evidence_id`;
6. output incomplete/invalid -> fail closed;
7. provider failure -> operational limitation, never website Finding;
8. no scoring performed by LLM.

Provider API mapping:

| Provider | API contract | Structured output |
|---|---|---|
| xAI | Responses | JSON Schema strict |
| Qwen | OpenAI-compatible Chat Completions | JSON Schema strict |
| Gemini | Interactions API | JSON MIME + schema |
| Anthropic | Messages API | `output_config.format` JSON Schema |

## 9. Error and quarantine behavior

At minimum normalize:

```text
AUTH_ERROR
PERMISSION_ERROR
CREDIT_ERROR
QUOTA_ERROR
RATE_LIMIT_ERROR
MODEL_ERROR
NETWORK_ERROR
TIMEOUT_ERROR
SERVER_ERROR
CONTRACT_ERROR
EMPTY_RESPONSE
INVALID_RESPONSE
UNKNOWN_PROVIDER_ERROR
```

A qualifying failure may set the explicit provider to `QUARANTINED_FOR_AUDIT` so a later URL/context does not silently generate another paid attempt.

Anthropic `stop_reason=refusal` in a nominal HTTP-success response must be treated as provider unavailability/invalid output, not as a website assessment.

## 10. M20

When `--ai-content-remediation` is enabled:

- legacy providers continue through the homologated M20 router;
- extension providers use the provider-native structured-output adapter;
- the selected provider/model/key/timeout are reused;
- M20 never reactivates a provider quarantined by M7/M18 semantic analysis;
- M20 output continues to be validated by the existing evidence-bound contract;
- M20 remains advisory and downstream of scoring/findings.

## 11. Usage and cost

Extension providers normalize usage tokens when the provider response supplies usable counters and persist them via the existing `ProviderAttempt` contract.

While a provider is `PROVISIONAL`, its current commercial price must not be injected into the homologated M18 pricing catalog without a separate price-normalization qualification because pricing can vary by region, tier, cache treatment, promotion or context.

Therefore `estimated_cost` may be `null` for extension-provider attempts even when tokens are available. This is preferable to publishing a false estimate.

## 12. Tests required before human smoke

Automated tests must cover:

- legacy explicit defaults unchanged;
- legacy AUTO remains exactly OpenAI/DeepSeek/MiMo, including when every extension key is present;
- CLI legacy parser remains unchanged when imported directly;
- public extension CLI exposes all explicit values/aliases;
- missing key -> `NOT_CONFIGURED` without transport call;
- correct native structured-output request for each provider;
- successful output normalization;
- usage normalization;
- incomplete schema -> contract error;
- invalid output -> fail closed;
- quarantine prevents repeated attempts;
- M20 extension request/response contract;
- M20 does not reactivate M7-quarantined provider;
- existing M18/M20/OpenAI regression suite remains green.

## 13. Human smoke gate

Automated CI is necessary but not sufficient for promotion/merge of the provider expansion.

With real provider credentials, smoke must verify for xAI, Qwen, Gemini and Anthropic:

1. real authentication and endpoint compatibility;
2. model availability;
3. complete BR-GEO-028..049 output;
4. correct provider/model telemetry;
5. usage availability/shape where returned;
6. no secret leakage to report/SQLite/artifacts/log;
7. controlled failure classification;
8. M20 support when enabled;
9. no silent retry after quarantine.

The same smoke cycle must revalidate OpenAI, DeepSeek and MiMo and confirm that AUTO still contains only those three providers.

## 14. Merge gate

Merge is permitted only when all are true:

```text
CI/regression = GREEN
legacy core diff = NONE for m18_ai.py, cli.py, m20_ai.py
documentation = UPDATED/CONSISTENT
human smoke new providers = PASS
human smoke legacy providers/AUTO = PASS
secret leakage = NONE
blocking issue = NONE
```

Until then, the branch/PR may be declared **READY FOR HUMAN SMOKE**, but not fully released/qualified.

## 15. Documentation contract

The change is not complete unless at minimum these remain consistent:

```text
README.md
docs/AI_GUIDE.md
docs/AI_PROVIDER_EXTENSIONS.md
docs/CONFIGURATION.md
docs/CLI_REFERENCE.md
docs/COMPATIBILITY.md
docs/INSTALLATION.md
docs/USER_GUIDE.md
docs/SMOKE_TEST.md
docs/TECHNICAL_GUIDE.md
docs/specification/00_SPEC_INDEX.md
docs/specification/08_TECHNICAL_ARCHITECTURE.md
docs/specification/22_SAFE_AI_PROVIDER_EXTENSIONS.md
```

Provider-specific official documentation links must be used for API contract/model/plan guidance. External commercial terms may change and provider documentation prevails.
