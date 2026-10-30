# /perf - report, history, SITREP

## Report

`.perf-reports/PERF-<YYYYMMDD-HHMM>.md`, written progressively.

```markdown
# Performance Report: <project>
**Run ID / Date / Mode / Scope:** ...
**Method:** <exact tool, settings, median-of-N>
**Budgets:** <project budgets if declared, else skill defaults>

## Before / After
| Metric | Before | After | Delta | Budget | Status |
|---|---|---|---|---|---|
| LCP (lab) | 4.1s | 2.2s | -46% | <2.5s | PASS |
| INP (lab) | 310ms | 180ms | -42% | <200ms | PASS |
| CLS | 0.04 | 0.02 | -50% | <0.1 | PASS |
| JS initial (gz) | 612 KB | 288 KB | -53% | <300 KB | PASS |
| API p95 | 780ms | 410ms | -47% | <500ms | PASS |

**Field confirmation:** p75 CrUX will reflect these over ~28 days from <date>.

## Changes applied
- <change> - <measured effect> - <files>

## Reverted
- <change> - no measurable effect (<before> -> <after>, within noise)

## Not fixed
- <finding> - <estimated cost> - <why deferred>
```

## History

`.perf-reports/history.json`: per-run metrics plus `baselines` per route. Update a baseline only
when a run passes its budgets, so a slow run cannot become the new normal.

## SITREP

Grade against budgets, not against a curve: every budget met = PASS; any Core Web Vital in "poor" =
FAIL regardless of the rest. List the before/after table, then what was reverted, then what remains.

### Suggested next

| Outcome | Recommend |
|---|---|
| All budgets met | `/monitor` to confirm in the field over the next weeks |
| Backend dominated the findings | `/db` for query and index work |
| Bundle dominated | `/deps` - a heavy dependency is often the cause |
| Nothing improved measurably | `/investigate` - the model of the bottleneck is wrong |
| Regression appeared after a deploy | `/monitor --deep`, then the deploy diff |

## Design notes

**Median of three, always.** One Lighthouse run varies by enough to invent a regression or hide one.
A number reported from a single run is not evidence.

**Lab and field are different claims.** Conflating them is the most common dishonesty in performance
reporting: the lab number moves today, the grade moves in a month.

**Revert what did not work.** A change that costs complexity and buys nothing measurable is a
liability. The report says so rather than quietly keeping it.
