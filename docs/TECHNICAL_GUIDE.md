# TECHNICAL_GUIDE.md

## Pipeline

```text
CLI
→ target validation
→ device-context resolution
→ M2 discovery/acquisition
→ M3 rendering selected device(s)
→ M4 extraction/evidence
→ M5/M6 deterministic analysis
→ content extractability
→ M7 semantic provider
→ M8 device comparison when possible
→ pre-scoring rules
→ M9 SCORE-GEO-002
→ M10 prioritization
→ M14 element linking
→ M11/M16/M17 report/remediation materialization
→ M18 telemetry enrichment
→ report_site finalization
```

## Device context

Module:

```text
src/searchgeo/device_context.py
```

Variable:

```text
SEARCHGEO_DEVICE_CONTEXT
```

Values:

```text
mobile
desktop
both
```

The CLI resolves one value per invocation. It temporarily places the resolved value in the process environment so M3 and downstream consumers see the same universe, then restores the previous environment value after `run_audit` returns or fails.

Default CLI: `mobile`.

Direct M3 invocation without environment value: legacy `both` for compatibility.

## Rendering

M3 no longer has to render both devices for every user-facing audit. It obtains runtime devices from `device_context.runtime_devices()`.

Each persisted snapshot includes device-specific metadata and the selected audit device universe in browser metadata.

Because M7 consumes M3 snapshot IDs, no semantic-provider call exists for an unrendered device.

## Cost implication

For N successfully rendered pages and a healthy explicit provider:

```text
mobile/desktop: up to N semantic contexts
both:           up to 2N semantic contexts
```

Actual attempt count may be lower due to provider disabled/not configured, quarantine, missing snapshots or other pipeline conditions.

## Scoring

M9 remains deterministic and provider-independent once RuleExecutions are persisted.

`SCORE-GEO-002`:

- separates Score, Coverage, Confidence and Consolidation;
- distinguishes `NOT_APPLICABLE` from missing/unresolved execution;
- prevents missing IA from becoming website FAIL;
- uses `scoring_group` to reduce correlated double counting;
- computes Overall separately by device.

The report site only exposes devices actually captured by the audit, even though the scoring model itself remains defined for Desktop and Mobile.

## Confidence semantics

Current score confidence is an **auditor reliability indicator**. It is not a direct content-quality metric.

`LOW` can result from limited Coverage/evidence/errors. Therefore no component should infer “rewrite this text” from Confidence alone.

## Intermediate M11/M18 HTML

The existing M11/M18 builder contracts are intentionally preserved internally to minimize regression risk. `execute_m11()` can still materialize the historical intermediate HTML files; M18 enriches those files as before.

In a complete `run_audit`, these are intermediate projections only.

## Final report-site materialization

Module:

```text
src/searchgeo/report_site.py
```

After M18 enrichment:

1. read persisted `audit.db` state;
2. generate `report/css/site.css`;
3. generate all domain pages;
4. update `reports.file_path` to `report/index.html`;
5. only after successful materialization, remove intermediate root `report.html` and `remediation.html`;
6. return `report/index.html` as `AuditRunResult.report_path`.

The final public output is therefore:

```text
report/index.html
report/mobile.html       # conditional
report/desktop.html      # conditional
report/remediation.html
report/ai-usage.html
report/references.html
report/css/site.css
```

## Why finalization happens after M18

M18 previously enriched `report.html` and `remediation.html`. Keeping this ordering allows existing direct M11/M18 unit contracts to remain testable while the user-facing projection moves to a multi-page site.

The final report site reads M18 tables from SQLite rather than copying the enriched legacy DOM.

## Report domains

### Overview

Executive score/reliability only.

### Device pages

Page-level snapshots/findings/semantic state isolated by Mobile or Desktop.

### Remediation

Loads:

```text
remediation_groups
recommendations
root_cause_analyses
root_cause_precision
findings
```

and projects M16/M17 diagnostic detail without recalculating it.

### AI telemetry

Loads:

```text
ai_audit_sessions
ai_provider_attempts
```

No provider call is made during report generation.

### References

Uses versioned `rule_references.py` plus the curated primary-authority catalog in `report_site.py`.

## CSS architecture

Final CSS exists only at:

```text
report/css/site.css
```

Every final page uses:

```html
<link rel="stylesheet" href="css/site.css">
```

This removes the previous accumulation of embedded CSS fragments from the final user-facing pages.

## Security

`report_site` uses HTML escaping for dynamic values and the reporting redaction helper when rendering persisted structured payloads.

Do not add raw provider bodies, headers or secrets to the final projection.

## M18 routing

Explicit provider:

- no cross-provider fallback;
- failure can quarantine provider for audit;
- missing other provider keys irrelevant.

AUTO:

- immutable eligible chain;
- sequential calls;
- first valid result ends the context;
- failed provider quarantined;
- URL lock prevents mixed-provider completion of a previously pinned URL.

## Timeout

CLI applies `SEARCHGEO_AI_TIMEOUT_SECONDS`, default 180 s, to constructed provider(s). No automatic retry after timeout.

## Reproducibility

The report site is not used as scoring input. Reproducibility remains based on:

```text
audit.db
artifacts
rule versions
scoring version
```

`BR-GEO-054` checks score reconstruction from persisted state.

## Testing strategy

Minimum stabilization suite:

```powershell
python -m compileall -q src tests
python -m unittest discover -s tests -v
```

Regression coverage includes:

- old direct M11/M18 contracts;
- final `run_audit` report-site paths;
- no root legacy report after finalization;
- shared external CSS;
- Mobile/Desktop conditional pages;
- provider telemetry separation;
- mobile-only provider-call reduction;
- environment restoration by CLI.
