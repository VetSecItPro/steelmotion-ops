---
name: monitor
description: "Post-deploy health verification: discover what a project actually deploys to, check it at the real URL and in the runtime itself, score six weighted categories, and report a graded verdict with findings. Covers PaaS, Kubernetes, containers, systemd and poll-cron deploys - detected, not assumed."
when_to_use: 'Trigger phrases: "post-deploy check", "is prod healthy?", "health check", "did the deploy work", "check production", "monitor". Run after /gh-ship completes a deploy, after an incident is resolved, or on a schedule as a drift check.'
---

# /monitor - post-deploy health verification

**Spine. Stays in context through compaction.** Detail lives beside it:

| File | Read at | Holds |
|---|---|---|
| `targets.md` | Stage 0 | target-class + observability detection, capability gating, reuse of existing verify tooling |
| `stages.md` | each stage | the seven stages in detail |
| `reference.md` | Stage 0.6 and Stage 7 | report format, history, SITREP, scoring detail |

**Standards inherited:** [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) ·
[Steel Discipline](~/.claude/standards/STEEL_DISCIPLINE.md) ·
[Self-Improvement](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) ·
[Status Updates](~/.claude/standards/STATUS_UPDATES.md) ·
[Context Management](~/.claude/standards/CONTEXT_MANAGEMENT.md) ·
[Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md) ·
[Skill Auto-Suggest](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) ·
[SITREP Format](~/.claude/standards/SITREP_FORMAT.md) ·
[Agent Orchestration](~/.claude/standards/AGENT_ORCHESTRATION.md) ·
[Multi-Repo Awareness](~/.claude/standards/MULTI_REPO_AWARENESS.md) ·
[Verify Before Destroy](~/.claude/standards/VERIFY_BEFORE_DESTROY.md)

## Critical rules

1. **Read-only against production.** GET and HEAD only. Never POST/PUT/DELETE, never mutate state,
   never run a destructive command against a live system. If a check would change something, it is
   not a monitor check.
2. **200 is not "healthy".** A route passes only when the status is 2xx/3xx **and the body contains
   the expected content marker**. A 200 serving a blank shell, a stale build or a branded error page
   is a failure. `/gh-ship` uses the same rule; both sides of a deploy must mean the same thing by
   "verified".
3. **A green rollout is the first signal, not the last.** `kubectl rollout status` only says pods
   started and passed readiness. It routinely goes green alongside a 500 spike. Check the golden
   signals - latency, traffic, errors, saturation - before calling a deploy good.
4. **A missing capability is a coverage note, never a silent skip.** If the cluster is unreachable or
   the APM is not configured, say so in the report and score only what was actually checked.
5. **Reuse the project's own verification tooling** where it exists rather than reimplementing it.
   Two implementations of "is the cluster healthy" produce two answers.
6. **Never fabricate a metric.** If response time has no baseline, say "no baseline; this run
   establishes one" - do not invent a comparison.
7. **Findings persist.** The report file is the source of truth and survives the session.

## Modes

```
/monitor                  full check, all applicable stages
/monitor --quick          routes + errors only; the fast post-deploy gate
/monitor --deep           full, plus baseline comparison and trend analysis
/monitor --routes         route health only (alias: --routes-only)
/monitor --infra          DNS, SSL, headers, CDN, cluster/runtime only
/monitor --errors         error tracking only
/monitor --env-only       environment config only; after an env var change
/monitor --baseline       establish or refresh baselines without grading
/monitor --changed        only routes touched by the last deploy's diff
/monitor <url>            monitor an explicit URL rather than a detected one
```

**Bare `/monitor` decides its own scope** and says which and why in one line:

| Situation | Scope |
|---|---|
| Invoked right after a deploy (a `/gh-ship` run just completed) | `--quick`, then escalate to full if anything is off |
| No prior report in `.monitor-reports/` | full - establishes the baseline |
| Last report < 24h old and nothing deployed since | `--quick` - nothing has changed |
| An incident is open, or the last run scored < 70 | `--deep` |
| Anything else | full |

## Scoring

Six weighted categories. Only categories that were actually checkable count toward the score;
anything ungradeable is reported as DEFERRED with the reason, and the weights are renormalised over
what was checked. **Never score a category you could not measure.**

| Category | Weight | Scoring |
|---|---|---|
| Route health | 25% | 100 all pass. −10 per 4xx, −25 per 5xx, −25 per 200-with-wrong-content. 0 if a critical route is down |
| Response time | 20% | 100 under baseline×1.2. −5 per route over ×1.5, −15 per route over ×3 |
| Function/service health | 15% | 100 all execute. −20 per failing function or unready service. 0 if >50% failing |
| Environment config | 15% | 100 all present. −10 per missing non-critical, −25 per missing critical |
| Infrastructure | 15% | 100 all pass. −15 per issue, −50 SSL expiry <30d, 0 if SSL expired |
| Error rate | 10% | 100 zero. −5 per unique error, −20 per recurring, 0 if >10 unique |

| Score | Grade | Verdict |
|---|---|---|
| 95-100 | A+ | healthy, no action |
| 90-94 | A | healthy, minor items |
| 85-89 | B+ | mostly healthy, address flagged |
| 80-84 | B | acceptable, some degradation |
| 70-79 | C | degraded, investigate soon |
| 60-69 | D | unhealthy, investigate now |
| 0-59 | F | critical - consider `/incident` |

## Stages

Read `stages.md` for the procedure.

| # | Stage | Must not be skipped |
|---|---|---|
| 0 | Detect target class, observability, capabilities | read `targets.md`; record what is and is not reachable |
| 1 | Route discovery | enumerate from the router/sitemap/manifest, not from memory |
| 2 | Endpoint health | status **and content marker**; timings; redirects |
| 3 | Function / service verification | serverless functions, or pod readiness + restarts + rollout |
| 4 | Environment validation | required config present in the running system |
| 5 | Infrastructure | DNS, SSL, headers, CDN, ingress/target-group health |
| 6 | Error tracking | from the detected APM, or platform-native logs |
| 7 | Score and report | renormalise over checked categories; write the report; SITREP |

Stages 3-7 are the half a long run loses to compaction if it is not held here. **Stage 7 produces
the score the whole skill exists to output** - it must never be the part that gets dropped.

## Human decision triggers

Stop and surface rather than deciding alone: a 5xx on a critical route; SSL expiring inside 7 days;
an error spike that looks like an active incident; a rollout that is green while the golden signals
are degraded; any finding that would require a write to fix. `/monitor` diagnoses; it does not
remediate.

## Definition of done

- Every applicable stage ran, or is listed as DEFERRED with the reason and the capability that was
  missing
- Every route checked for status **and** content
- Score computed only over categories actually measured, with the renormalisation shown
- Report written to `.monitor-reports/MON-<YYYYMMDD-HHMM>.md`, history appended
- SITREP ends with a verdict and "Suggested next" - `/incident` on an F, `/investigate` on a
  persistent D, nothing on an A
