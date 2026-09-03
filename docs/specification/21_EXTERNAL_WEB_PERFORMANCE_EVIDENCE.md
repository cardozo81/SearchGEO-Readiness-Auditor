# M21 — External Web Performance Evidence: Core Web Vitals + Lighthouse

**Status:** APPROVED EVOLUTION  
**Identifier:** `M21`  
**Dependency:** M18 + M20 + `SCORE-GEO-002` + `REPORT-SITE-GEO-001`  
**Nature:** additive external evidence; non-scoring by default

## 1. Objective

M21 adds externally documented web-performance evidence to the SearchGEO audit without removing, replacing or silently recalibrating `SCORE-GEO-002`.

The feature collects, when explicitly enabled:

- Lighthouse lab scores through PageSpeed Insights API v5;
- Lighthouse lab metrics such as FCP, Speed Index, LCP, Total Blocking Time and CLS;
- Core Web Vitals field data from CrUX when available;
- LCP, INP and CLS p75 and their official good-experience assessment;
- operational telemetry for every external measurement request;
- raw bounded/reopenable JSON response artifacts under the audit workspace.

M21 answers a different question from `SCORE-GEO-002`:

```text
SCORE-GEO-002
→ internal heuristic readiness index over SearchGEO RuleExecutions

M21 Lighthouse
→ externally defined lab measurement and score

M21 CrUX / Core Web Vitals
→ aggregated real-user field experience when a sufficient CrUX sample exists
```

These outputs must remain distinguishable in persistence, HTML and documentation.

## 2. Non-destructive scoring contract

M21 does **not** change:

- Business Rules;
- RuleExecution results;
- findings;
- recommendations;
- priority;
- rule weights;
- `PASS = 1.00`, `WARNING = 0.50`, `FAIL = 0.00`;
- dimension scores;
- Coverage;
- Confidence;
- Consolidation;
- Overall Readiness;
- `scoring_version = SCORE-GEO-002`.

No Lighthouse, PageSpeed or Core Web Vitals value is automatically converted into a `SCORE-GEO-002` contribution.

`SCORE-GEO-002` therefore remains available as the stable heuristic readiness index even when M21 is enabled. When M21 is disabled or unavailable, the existing audit behavior remains functional.

## 3. Official external basis

### 3.1 PageSpeed Insights API v5

Official reference:

- <https://developers.google.com/speed/docs/insights/v5/reference/pagespeedapi/runpagespeed>
- <https://developers.google.com/speed/docs/insights/v5/get-started>

The official API runs Lighthouse against a supplied URL and supports the categories:

```text
performance
accessibility
best-practices
seo
```

The current SearchGEO default requests all four categories in the same PageSpeed context request.

Google documents that PageSpeed Insights can be used with or without an API key, while a key is recommended for frequent automated queries.

### 3.2 Chrome UX Report API

Official references:

- <https://developer.chrome.com/docs/crux/api/>
- <https://developer.chrome.com/docs/crux/guides/crux-api>

The direct CrUX API:

```text
POST https://chromeuxreport.googleapis.com/v1/records:queryRecord
```

requires an API key and supports field data by URL/origin and form factor.

M21 requests the current Core Web Vitals metric set:

```text
largest_contentful_paint
interaction_to_next_paint
cumulative_layout_shift
```

Device mapping:

```text
SearchGEO MOBILE  → CrUX PHONE
SearchGEO DESKTOP → CrUX DESKTOP
```

Tablet is not introduced as a SearchGEO device context by M21.

### 3.3 Core Web Vitals assessment

Official methodology uses the 75th percentile of real-user distributions.

Current good-experience thresholds used by M21:

```text
LCP <= 2500 ms
INP <= 200 ms
CLS <= 0.10
```

The combined M21 state is:

```text
PASS
```

only when LCP, INP and CLS are all available and each satisfies the corresponding good threshold.

If one or more metrics are unavailable:

```text
INCOMPLETE
```

or, when no usable field metric exists:

```text
UNAVAILABLE
```

Missing CrUX data is never transformed into a website failure. CrUX may legitimately have insufficient samples for a URL/form factor.

### 3.4 Lighthouse Performance Score

Official reference:

- <https://developer.chrome.com/docs/lighthouse/performance/performance-scoring>

Lighthouse Performance is an external 0–100 score computed by Lighthouse. Its metric score curves and weights are maintained by the Chrome/Lighthouse project and can evolve by Lighthouse version.

SearchGEO persists the reported Lighthouse version and does not duplicate a fixed private copy of Lighthouse weighting as `SCORE-GEO-002`.

Lighthouse Performance must be labeled as `Lighthouse Performance`, never as `GEO Score`.

## 4. Activation and no-surprise network policy

M21 external collection is OFF by default.

Public controls:

```text
--web-performance
--no-web-performance
SEARCHGEO_WEB_PERFORMANCE
```

Precedence:

1. explicit CLI flag;
2. environment variable;
3. `false`.

Accepted boolean environment values:

```text
true / false
1 / 0
yes / no
on / off
```

When disabled:

- no PageSpeed request is made;
- no CrUX request is made;
- no new LLM request is made;
- M21 persists `DISABLED` for traceability;
- the report explains that the feature was disabled;
- `SCORE-GEO-002` remains fully available.

## 5. Consumption controls

### 5.1 Maximum pages

```text
--web-performance-max-pages N
SEARCHGEO_WEB_PERFORMANCE_MAX_PAGES
```

Default:

```text
10
```

Meaning:

- `N > 0`: only the first N audited pages in deterministic URL order are sent to external performance services;
- `0`: all audited pages are eligible.

The page limit applies to logical pages. For `--device-context both`, each selected page may generate one PageSpeed request for Mobile and one for Desktop.

Therefore a practical PageSpeed upper bound is:

```text
selected_pages × selected_device_contexts
```

Direct CrUX fallback can add one CrUX request per context only when its policy requires it.

### 5.2 Timeout

```text
--web-performance-timeout-seconds SECONDS
SEARCHGEO_WEB_PERFORMANCE_TIMEOUT_SECONDS
```

Default:

```text
60
```

The value must be finite and greater than zero.

M21 does not automatically retry a timed-out measurement, preventing an implicit second external request whose first execution state may be unknown.

### 5.3 Lighthouse categories

```text
--lighthouse-categories performance,accessibility,best-practices,seo
SEARCHGEO_LIGHTHOUSE_CATEGORIES
```

Supported values:

```text
performance
accessibility
best-practices
seo
```

Default requests all four.

The categories affect Lighthouse work performed by the PageSpeed service but do not create any LLM call.

## 6. API credential controls

### 6.1 PageSpeed

Optional environment variable:

```text
SEARCHGEO_PAGESPEED_API_KEY
```

The key is passed only to PageSpeed Insights.

It is never:

- persisted to SQLite;
- written to raw response artifacts;
- shown in HTML;
- logged as a request URL;
- reused as an AI provider credential.

PageSpeed can operate without a key at lower/ad-hoc usage, subject to provider service policy/quota.

### 6.2 CrUX

Environment variable:

```text
SEARCHGEO_CRUX_API_KEY
```

Direct CrUX API use requires this key.

The key is isolated from:

```text
OPENAI_API_KEY
DEEPSEEK_API_KEY
MIMO_API_KEY
SEARCHGEO_PAGESPEED_API_KEY
```

No fallback between credential families is permitted.

## 7. Field-data source policy

Control:

```text
--web-performance-field-source auto|pagespeed|crux|none
SEARCHGEO_WEB_PERFORMANCE_FIELD_SOURCE
```

Default:

```text
auto
```

### `auto`

1. PageSpeed is called for Lighthouse;
2. if PageSpeed still returns usable CrUX field data, M21 uses it;
3. if PageSpeed field data is absent and `SEARCHGEO_CRUX_API_KEY` exists, M21 calls the direct CrUX API;
4. if neither produces field data, Core Web Vitals remains `UNAVAILABLE`/`INCOMPLETE` without a website penalty.

This policy is intentionally migration-friendly because Google has announced its intention to stop returning CrUX field data through PageSpeed Insights and recommends direct CrUX APIs for field data.

### `pagespeed`

Use only field data present in the PageSpeed response. Never add a direct CrUX call.

### `crux`

Use direct CrUX field data. Requires `SEARCHGEO_CRUX_API_KEY`. PageSpeed is still used for Lighthouse lab data.

### `none`

Disable field-data processing while retaining Lighthouse lab collection.

## 8. AI policy

M21 adds **zero** LLM calls.

It does not call:

- OpenAI;
- DeepSeek;
- MiMo;
- any M18 SemanticProvider;
- M20 content-remediation provider.

Existing AI controls continue unchanged.

M21 therefore cannot create an unexpected LLM bill merely because Web Performance was enabled.

If a future version adds AI interpretation of external metrics, that capability must be:

- independently opt-in;
- separately metered;
- reflected in `ai-usage.html` by purpose;
- unable to alter source measurements;
- unable to change `SCORE-GEO-002` unless a later explicitly approved scoring contract says otherwise.

## 9. Execution placement and failure isolation

The current CLI integration executes M21 after the existing audit pipeline has completed and after the baseline report site exists.

Reason:

- preserve existing audit behavior;
- prevent PageSpeed/CrUX availability from blocking RuleExecution/scoring;
- make external performance evidence an enrichment layer;
- keep failures attributable to the measurement service rather than the audited website.

Operational states include:

```text
DISABLED
NO_CONTEXTS
SUCCESS
PARTIAL
UNAVAILABLE
```

A PageSpeed/CrUX error is persisted in M21 telemetry and does not create SearchGEO Finding or Recommendation.

## 10. Persistence

M21 adds additive SQLite tables:

```text
web_performance_runs
web_performance_observations
web_performance_attempts
```

### `web_performance_runs`

Stores audit-level M21 configuration/result summary:

- enabled;
- status;
- field source policy;
- page limit;
- pages considered;
- context attempts;
- successful contexts;
- PageSpeed successes;
- CrUX successes;
- Lighthouse categories;
- reason/status detail;
- timestamp.

### `web_performance_observations`

Stores one observation per audited page snapshot/device selected by M21, including:

- URL;
- device/strategy;
- Lighthouse version/fetch time;
- Performance/Accessibility/Best Practices/SEO score when returned;
- FCP, Speed Index, LCP, TBT and CLS lab metrics when returned;
- field source/scope;
- LCP p75;
- INP p75;
- CLS p75;
- component assessments;
- combined CWV assessment;
- service HTTP status;
- artifact references;
- sanitized error summary.

### `web_performance_attempts`

Stores operational telemetry per service request:

- service (`PAGESPEED_INSIGHTS` or `CRUX_API`);
- URL/device/snapshot;
- success/error state;
- HTTP status;
- duration;
- sanitized error code/message;
- response artifact reference;
- timestamp.

Credentials are never persisted.

## 11. Raw artifacts

Successful external responses are written under:

```text
artifacts/web-performance/
```

Examples:

```text
WPE-....pagespeed.json
WPE-....crux.json
```

These artifacts preserve the external source payload used to build the projection and make the result auditable after the network request.

The report does not require a live API call to reopen an existing audit.

## 12. Report contract

M21 extends the static report site with:

```text
report/web-performance.html
```

Shared navigation is updated so the page is reachable from all report pages.

### `index.html`

Receives a compact Web Performance summary with:

- enabled/disabled state;
- M21 run status;
- count of valid Core Web Vitals PASS/FAIL contexts;
- average Lighthouse Performance only across contexts that actually returned the external score;
- link to details.

The average Lighthouse number is labeled as Lighthouse evidence. It is not the SearchGEO Overall.

### `web-performance.html`

Must visibly distinguish:

1. Lighthouse lab results;
2. CrUX/Core Web Vitals field results;
3. field source and URL/origin scope;
4. unavailable/incomplete data;
5. operational external-service telemetry;
6. consumption/credential policy;
7. explicit non-scoring language.

### `references.html`

Receives official references for:

- PageSpeed Insights API;
- PageSpeed Get Started;
- CrUX API;
- CrUX guide;
- Lighthouse Performance scoring;
- Core Web Vitals.

The section explicitly states that these sources validate their respective phenomena and **do not homologate `SCORE-GEO-002` as a universal GEO score**.

## 13. Interpretation rules

Allowed:

```text
Lighthouse Performance: 91/100
Core Web Vitals: PASS
LCP p75: 2.4 s
Source: CrUX
SearchGEO Readiness: 78/100 (SCORE-GEO-002; internal heuristic)
```

Not allowed:

```text
GEO score = Lighthouse 91
Core Web Vitals PASS = guaranteed AI citation
SearchGEO 78 + Lighthouse 91 = official GEO 84.5
Missing CrUX = website FAIL
```

No arithmetic combination is created by M21.

## 14. PageSpeed versus CrUX caveat

PageSpeed Insights currently can return both:

- Lighthouse lab data;
- CrUX field data.

Google has publicly documented the plan to discontinue the field-data portion in PageSpeed Insights and recommends CrUX API/CrUX History API for real-world data.

M21 therefore records the field source and supports direct CrUX fallback rather than treating PageSpeed field data as permanent API behavior.

## 15. Security and privacy

M21 must not persist:

- API keys;
- Authorization headers;
- request URLs containing API keys;
- cookies from the audited site;
- secrets from local environment.

Only target URL, external measurement response, sanitized telemetry and derived metrics are persisted.

## 16. Backward compatibility

With default configuration:

```text
SEARCHGEO_WEB_PERFORMANCE=false
```

there are no new PageSpeed/CrUX network calls.

Existing commands remain valid.

Existing AI provider behavior remains valid.

`SCORE-GEO-002` remains the scoring baseline.

M21's new HTML is additive to the report site and does not remove existing pages.

## 17. Minimum acceptance tests

M21 is acceptable only when regression coverage proves:

1. default OFF produces zero PageSpeed/CrUX requests;
2. disabled run is persisted;
3. PageSpeed response produces Lighthouse scores/metrics;
4. PageSpeed CrUX field data produces LCP/INP/CLS p75;
5. PSI CLS percentile normalization is handled;
6. direct CrUX is used by `auto` only when PageSpeed field data is absent and a CrUX key/client is available;
7. device mapping Mobile→PHONE and Desktop→DESKTOP is deterministic;
8. missing one CWV metric produces `INCOMPLETE`, not `FAIL`;
9. unavailable field data does not alter RuleExecution/Finding/Score;
10. raw response artifacts are persisted after successful calls;
11. credentials do not appear in persistence/report;
12. `web-performance.html` explains non-scoring semantics;
13. `index.html` links to the new evidence page;
14. `references.html` lists primary official sources;
15. existing SCORE-GEO-002 code/content is not removed or recalculated.

## 18. Future calibrated scoring

M21 is intentionally a prerequisite for empirical calibration, not itself `SCORE-GEO-003`.

A future scoring version may study correlations between SearchGEO readiness features, external performance evidence and observed generative outcomes. Any such version requires a separately approved empirical protocol and must preserve the historical `SCORE-GEO-002` result for comparison when feasible.

M21 alone does not justify changing weights or claiming citation probability.
