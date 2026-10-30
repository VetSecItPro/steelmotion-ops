# /qatest - scoring, report, SITREP

## Scoring

Weighted across the dimensions actually exercised. A dimension not applicable to the app is N/A with
its weight redistributed (never 0, never 100).

| Dimension | Weight | 100 means |
|---|---|---|
| Page health | 20% | every route 2xx + content, no console/network errors |
| Interactive elements | 20% | every element does something correct; nothing dead |
| User journeys | 25% | every critical flow completes end to end |
| API surface | 15% | every endpoint handles auth/validation/happy/error |
| Accessibility | 10% | `/a11y` automated clean + keyboard flows pass |
| Responsive | 5% | no breakage at key widths, 320px, 200% |
| Performance | 5% | key routes within budget |

Grade: A+ (95+) down to F (<60). **A dead critical journey caps the score regardless of the
average** - the same blocker-beats-average rule as `/launch`.

## Report

`.qatest-reports/QA-<YYYYMMDD-HHMM>.md`.

```markdown
# QA Report: <project>
**Score: <n>/100 (<grade>)**  |  **Verdict: <ship | fix-first | blocked>**
**Surfaces:** <routes/journeys driven>  |  **Mode:** <full | flows | pages | api>

## Dimension scores
| Dimension | Score | Findings |

## Findings (by severity)
### <title>  [BLOCKER|HIGH|MED|LOW]
**Where:** <route/element/flow>
**Reproduced:** <the exact interaction> - <what happened> (console: <...>, network: <...>)
**Fix:** <applied + re-verified | reported for judgment>

## Journeys
| Flow | Result |
| signup -> first value | PASS |
| checkout | **FAIL at payment step - <what>** |

## Regression tests added
- <path> - <what it guards>
```

## SITREP

Score and verdict first. Then the journey results - a reader wants "checkout works / checkout is
broken" before any dimension breakdown. Then findings by severity, then what was auto-fixed vs
reported.

### Suggested next

| Outcome | Recommend |
|---|---|
| A / A+ | `/gh-ship` then `/monitor` |
| A broken journey | fix it; re-run `/qatest --flows` on that path |
| Accessibility findings | `/a11y` for the full manual protocol |
| Performance below budget | `/perf` |
| Pre-launch overall | `/launch` for the scored go/no-go gate |

## Design notes

**Drive, don't infer.** The one discipline that separates QA from code review. A button's handler can
look perfectly wired and still do nothing because of a runtime error three layers down. Only clicking
it finds that.

**Journeys are the point.** Individual pages passing is necessary but not sufficient; users move
through flows, and flows break at the seams between pages that each look fine. Phase 3.5 is why this
skill exists.

**Compose, don't duplicate.** Accessibility, performance and security each have a skill. `/qatest`
runs their logic on the routes it drives rather than maintaining a second, drifting copy.

**Blocker beats average.** A 90/100 with a dead checkout is not shippable. The score serves the
verdict; it does not override it.
