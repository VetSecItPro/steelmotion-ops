# /monitor - report format, history, SITREP

Read at Stage 0.6 (initialise the report) and Stage 7 (finalise it).

## Report file

`.monitor-reports/MON-<YYYYMMDD-HHMM>.md`. Written progressively so it survives compaction and a
lost session. Append-only across runs; never overwrite a prior report.

```markdown
# Monitor Report: <project>
**Run ID:** MON-<YYYYMMDD-HHMM>
**Date:** <local time + tz>
**Target class:** <paas(vercel) | kubernetes | compose | systemd | poll-cron | static>
**Surfaces:** <hostnames / namespaces checked>
**Observability:** <datadog | sentry | platform-native | prometheus | none>
**Capabilities:** <cluster reachable? APM reachable? what was skipped and why>
**Reusing:** <project verify scripts run, if any>
**Baseline:** <prior run id | "none - this run establishes one">
**Trigger:** <post-deploy after <pr/sha> | scheduled | manual | post-incident>
**Mode:** <full | quick | deep | routes | infra | errors>

## Health Score: <N>/100 (<grade>)

| Category | Weight | Score | Note |
|---|---|---|---|
| Route Health | 25% | <n> | <n>/<m> routes 2xx + marker present |
| Response Time | 20% | <n> | P50 <x>s / P95 <y>s |
| Function/Service Health | 15% | <n> | |
| Environment Config | 15% | <n> | |
| Infrastructure | 15% | <n> | SSL <d>d, headers <n>/5 |
| Error Rate | 10% | <n> | |

<if any category DEFERRED>
**Renormalised over <k> of 6 categories** (weights rescaled). DEFERRED:
- <Category> - <capability that was missing>
</if>

## Findings
### <Category> - <SEVERITY>
<what, where, evidence, and what it implies. Never a bare status code.>

## Deferred
- <route or check> - <why: auth-gated / no value available / capability unavailable>

## Trend vs <prior run id>
- Score: <prev> -> <now> (<delta>)
- Changed state: <routes that flipped>
- Regressed: <routes over baseline x1.5>
```

## History

`.monitor-reports/history.json`, appended at Stage 7.

```json
{
  "schema_version": 1,
  "runs": [{
    "run_id": "MON-20260728-1412",
    "score": 94,
    "grade": "A",
    "target_class": "kubernetes",
    "categories_measured": 5,
    "categories_deferred": ["Error Rate - no APM session"],
    "routes_checked": 17,
    "routes_failed": 0,
    "p50_ms": 340,
    "p95_ms": 980,
    "trigger": "post-deploy after PR #92"
  }],
  "baselines": {
    "/": {"p50_ms": 170, "p95_ms": 420, "established": "MON-20260624-2140"}
  }
}
```

`baselines` is what makes response-time scoring meaningful. Establish it on the first run; update it
only on a run that scored A or better, so a degraded run cannot quietly become the new normal.

## Resume state

`.monitor-reports/state-<run-id>.json` holds progress while a run is in flight: stages completed,
routes checked so far, findings accumulated. A run interrupted mid-flight resumes from the last
completed stage rather than restarting, provided the state file is under an hour old. Delete it on
successful completion.

## SITREP

```
===============================================================
/monitor - <project> - <N>/100 (<grade>)
===============================================================

Target      <class>, <surfaces>
Capabilities<what was reachable; what was skipped and why>
Scope       <categories measured>/6  <renormalised if applicable>

Categories
  Route Health      <n>/100   <m>/<t> routes healthy
  Response Time     <n>/100   P50 <x>s, P95 <y>s <vs baseline>
  Function/Service  <n>/100
  Environment       <n>/100
  Infrastructure    <n>/100   SSL <d>d
  Error Rate        <n>/100   <or DEFERRED - reason>

Findings (by severity)
  CRITICAL  <...>
  WARNING   <...>
  INFO      <...>

Deferred
  <check> - <reason>

Trend
  <prev score> -> <now> since <prior run id>

Report  .monitor-reports/MON-<id>.md
===============================================================
```

### Suggested next

| Outcome | Recommend | Why |
|---|---|---|
| A+ / A | none | healthy; nothing to chase |
| B+ / B | none, but watch the flagged items | degradation without urgency |
| C | `/investigate` the worst category | it will not fix itself |
| D | `/investigate` now | unhealthy |
| F | `/incident` | treat as an outage until proven otherwise |
| Deploy-triggered and any route failed | `/gh-ship` rollback path, or `/incident` | the deploy is the suspect |
| Capabilities were missing | re-run after restoring the session | the score is partial |

## Design notes

**Content marker, not just status.** A 200 proves the edge answered, not that the application is
correct. Stale builds, blank shells and branded error pages all return 200. The marker is what makes
"verified" mean the same thing here as in `/gh-ship`.

**Renormalising rather than zero-filling.** Scoring an unmeasured category as 0 would make a missing
cloud session look like an outage; scoring it as 100 would hide a real gap. Renormalising over what
was measured, and naming what was not, is the only honest option.

**Baselines only advance on healthy runs.** Otherwise a slow week silently becomes the standard and
the response-time category stops detecting anything.

**Read-only, always.** A monitor that can change production is not a monitor. Diagnosis here,
remediation in `/investigate` or `/incident`.

## Related skills

**Feeds from:** `/gh-ship` (runs after a deploy completes).
**Feeds into:** `/incident` (F grade or an active outage), `/investigate` (persistent D or a single
bad category), `/perf` (response-time regressions specifically).
**Pairs with:** `/sec-ship` - headers and SSL findings here overlap its Agent 7 and Agent 13.
