# /investigate - root-cause record, SITREP

## Report

`.investigate-reports/INV-<YYYYMMDD-HHMM>.md`.

```markdown
# Investigation: <symptom>
**Tier:** quick | standard | deep
**Reproduced:** yes - <exact steps> | intermittent - <trigger found>

## Root cause
<the mechanism, traced to its origin - not just the file and line>

## Evidence chain
1. <observation> -> 2. <observation> -> 3. <the pattern> -> <the mechanism>

## Hypotheses
- CONFIRMED: <theory> - proven by <test>
- disproven: <theory> - ruled out by <test>   (kept so it is not re-tried)

## Fix
<the minimal change, and why it addresses the cause not the symptom>
Files: <paths>

## Regression test
<path> - fails on old code, passes on fix. Verified both.

## Pattern learned
<if there is one worth remembering across sessions>
```

## History

`.investigate-reports/history.json`: `patterns_observed` for recurring bug shapes and their
mechanism - "null after migration = unbackfilled rows", "flaky test = shared fixture state". A known
shape gets its confirmed mechanism tried first next time.

## SITREP

Root cause first - the mechanism, in one sentence. Then the fix, then the regression test proving it
holds, then any pattern worth carrying forward. Disproven hypotheses go in the report, not the SITREP,
but the fact that the cause is *confirmed* (not assumed) is stated.

### Suggested next

| Outcome | Recommend |
|---|---|
| Fixed and tested | `/gh-ship` |
| The bug revealed a coverage gap | `/test-ship` on that seam |
| Root cause was a dependency | `/deps` to check for a fixed version |
| Turns out to be a live outage | `/incident` - triage and mitigate first |
| Three tiers deep, still unproven | surface the assumptions tested; a second pair of eyes |

## Design notes

**Evidence before theory** is the whole skill. Every other rule serves it. The single most expensive
debugging mistake is committing to the first plausible cause and confirmation-biasing toward it for an
hour; gathering evidence first makes that mistake structurally hard.

**Reproduce, then fix, then re-reproduce.** Without a reproduction there is no way to know the fix
worked - "it doesn't crash anymore" might mean fixed, or might mean the trigger did not happen this
time.

**Root, not symptom.** A null check that hides a null without explaining it relocates the bug to
wherever the value is next used. Tracing to the origin costs more now and far less later.

**Record disproven theories.** They are not waste - they are the map of where the bug is not, and they
stop the next investigation re-walking the same dead ends.
