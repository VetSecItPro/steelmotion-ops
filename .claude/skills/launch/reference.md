# /launch - scorecard, verdict, report

## Report

`.launch-reports/LAUNCH-<YYYYMMDD-HHMM>.md`.

```markdown
# Launch Readiness: <project>
**Verdict: GO | CONDITIONAL | NO-GO**
**Date / Mode:** ...

## Scorecard
| Domain | Weight | Score | Threshold | Status | Underlying report |
|---|---|---|---|---|---|
| Security | 20% | 88 | 85 | PASS | .sec-ship-reports/... |
| Test coverage | 12% | 74 | 70 | PASS | .test-reports/... |
| Performance | 12% | 91 | 80 | PASS | .perf-reports/... |
| Accessibility | 12% | 82 | 80 | PASS | .a11y-reports/... |
| Dependencies | 8% | 95 | 85 | PASS | .deps-reports/... |
| Content | 10% | 100 | 90 | PASS | this report |
| SEO | 6% | 88 | 80 | PASS | this report |
| User flow | 12% | 100 | 95 | PASS | this report |
| Payment | 8% | N/A | - | redistributed | free product |
| Legal | (see blockers) | 60 | 90 | **FAIL** | this report |
| **Weighted** | | **86** | | | |

## Hard blockers (each is NO-GO on its own)
- Legal: no privacy policy on a data-collecting product - <what it takes to clear>

## Conditional items (accepted, dated)
- Accessibility at 82 vs 80 target - contrast fixes scheduled by <date>, operator-accepted

## Verdict reasoning
<why GO/CONDITIONAL/NO-GO, in two sentences - the blocker dominates the average>
```

## Verdict computation

1. Any hard blocker → **NO-GO**. Stop. The weighted score is reported but does not override.
2. No hard blocker, every domain ≥ threshold → **GO**.
3. No hard blocker, some domain < threshold → **CONDITIONAL**, listing each gap and its accepted
   remediation. If the operator does not accept a remediation, that gap becomes a blocker → NO-GO.

The weighted average is context, never the verdict. A launch gate that returns "GO, 86%" while a
legal requirement is unmet has failed at its one job.

## SITREP

The verdict, first line, unmissable. Then the blockers (if any), then the scorecard, then the
conditional items with dates. Nobody reading a launch gate wants the scorecard before the verdict.

### Suggested next

| Verdict | Recommend |
|---|---|
| GO | `/gh-ship` then `/monitor` post-deploy |
| CONDITIONAL | clear the conditional items, then `/launch --recheck` on those domains |
| NO-GO (security) | `/sec-ship` (fix mode) on the blocker, then re-gate |
| NO-GO (a domain) | the domain's own skill in fix mode, then `/launch --recheck` |

## Design notes

**One verdict is the product.** Six audit reports are inputs; the launch decision is the output.
Collapsing them into a single defensible GO/CONDITIONAL/NO-GO is the entire value - anything less is
just running the audits.

**A blocker beats the average.** The gate's core discipline. Averaging is how a fatal flaw gets
launched under a comfortable overall number.

**Audit-only during the gate.** A readiness check that changes the thing it is assessing is measuring
a moving target. Fixes are a separate, deliberate pass after the verdict is known.

**N/A, not zero.** Redistributing an inapplicable domain's weight keeps the verdict honest; scoring it
0 fails healthy products, scoring it 100 hides unchecked ground.
