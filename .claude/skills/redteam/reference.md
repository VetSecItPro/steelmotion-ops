# /redteam - report, finding schema, SITREP

## Report

`.redteam-reports/RT-<YYYYMMDD-HHMM>.md`, written progressively so it survives compaction and a lost
session. This is a sensitive document - it is a map of how to attack the app. Keep it in the
gitignored reports directory; never commit it.

```markdown
# Red Team Report: <project> (LOCAL instance)
**Target:** http://localhost:<port>  (operator-owned, confirmed Phase 0)
**Run / Date / Mode:** ...
**Scope:** <classes tested>  |  Code-reviewed (not live): <classes>

## Confirmed findings
### RT-<n> - <title>  [CRITICAL|HIGH|MEDIUM|LOW]
**Class:** <authz | injection | ssrf | logic | ...>
**Basis:** live PoC | code review
**Impact:** <what an attacker actually achieves>
**PoC:** <setup, steps, result - reproducible>
**Fix direction:** <root cause, for /sec-ship or the operator>

## Chains
### CHAIN-<n> - <end impact>  [severity of the END state]
<finding> -> grants <x> -> enables <finding> -> ... -> <impact>
**Status:** confirmed (every hop demonstrated) | hypothesis (missing: <hop>)

## Hypotheses (unproven - NOT vulnerabilities)
- <finding> - <why unproven> - <what would confirm it>

## Cleanup
- test users removed: <ids>
- planted data removed: <what>
- state restored: <confirmation>
```

## Severity by demonstrated impact

| Severity | Means |
|---|---|
| CRITICAL | PoC achieves RCE, full auth bypass, mass data access, or account takeover |
| HIGH | PoC accesses another user's data, escalates privilege, or a confirmed chain reaching those |
| MEDIUM | real but bounded - one record, requires an unlikely precondition, limited blast radius |
| LOW | confirmed but low impact - info leak with no downstream use demonstrated |
| (hypothesis) | not demonstrated; ranked below every confirmed finding |

Severity is what the PoC **did**, never what a payload category is "usually" rated.

## SITREP

Confirmed findings first, by severity, each with its one-line demonstrated impact. Then chains - a
chain reaching CRITICAL from three LOWs is the headline result and the reason this skill exists. Then
hypotheses, clearly separated. Then the cleanup confirmation - a red-team run that left test users
behind is not done.

### Suggested next

| Outcome | Recommend |
|---|---|
| Confirmed findings to fix | `/sec-ship --fix <id>` per finding, then re-run `/redteam --verify <id>` |
| A confirmed chain | fix the cheapest hop to break the chain; re-test the whole chain |
| Only hypotheses | `/sec-ship --comprehensive` - passive depth may confirm what live testing could not reach |
| Clean, nothing found | genuinely good; note the classes code-reviewed vs live-tested so coverage is honest |

## Design notes

**Prove or downgrade.** The failure mode of red-teaming is a report full of "possible" findings that
waste the operator's time. A finding is CONFIRMED only with a PoC or a code-review basis; everything
else is a labelled hypothesis. This is what makes the report worth acting on.

**Chains are the whole point of a separate skill.** `/sec-ship` finds individual issues. Only active,
stateful testing shows that three low findings compose into account takeover. If a run produces no
chain analysis, it did not do the job that distinguishes it from a scan.

**Clean up, always.** Active testing creates test users, tokens and planted records. A run that does
not remove them has degraded the target and left evidence that looks like a real compromise later.

**Localhost is not a limitation, it is the design.** Every technique works against a local instance;
none of the legal or data risk of live testing does. The boundary is what makes autonomous red-teaming
safe to run at all.
