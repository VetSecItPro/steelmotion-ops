---
name: perf
description: "Performance audit and optimization: measure a real baseline, find what actually costs time, fix at root cause, then re-measure and prove the delta. Core Web Vitals plus bundle, render, network and backend cost. Stack-detected, never assumed."
when_to_use: 'Trigger phrases: "slow", "performance", "Lighthouse", "bundle size", "Core Web Vitals", "LCP", "INP", "CLS", "why is this taking so long", "optimize". Run after a perceived slowdown, before a launch, or when a monitor run flags response-time regression.'
---

# /perf - performance audit and optimization

**Spine. Survives compaction.** Detail beside it:

| File | Read at | Holds |
|---|---|---|
| `measure.md` | Phase 1 and 4 | how to get a trustworthy baseline per stack; lab vs field |
| `audit.md` | Phase 2 | what to look for, by layer, with the cost model |
| `reference.md` | Phase 5 | report format, history, SITREP, design notes |

**Standards inherited:** [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) ·
[Steel Discipline](~/.claude/standards/STEEL_DISCIPLINE.md) ·
[Self-Improvement](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) ·
[Context Management](~/.claude/standards/CONTEXT_MANAGEMENT.md) ·
[Agent Orchestration](~/.claude/standards/AGENT_ORCHESTRATION.md) ·
[Status Updates](~/.claude/standards/STATUS_UPDATES.md) ·
[Skill Auto-Suggest](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) ·
[Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md) ·
[Multi-Repo Awareness](~/.claude/standards/MULTI_REPO_AWARENESS.md) ·
[SITREP Format](~/.claude/standards/SITREP_FORMAT.md) ·
[Verify Before Destroy](~/.claude/standards/VERIFY_BEFORE_DESTROY.md)

## Core Web Vitals - the current three

Verified 2026-07-28. **FID was fully replaced by INP in March 2024 and is no longer a Core Web
Vital** - do not report it.

| Metric | Good | Needs work | Poor | Measures |
|---|---|---|---|---|
| **LCP** Largest Contentful Paint | < 2.5s | 2.5-4.0s | > 4.0s | loading |
| **INP** Interaction to Next Paint | < 200ms | 200-500ms | > 500ms | responsiveness |
| **CLS** Cumulative Layout Shift | < 0.1 | 0.1-0.25 | > 0.25 | visual stability |

**All three are graded at the 75th percentile of real users**, from the Chrome UX Report over a
28-day rolling window. That has two consequences this skill must respect:

1. **A lab number is not a score.** Lighthouse on your machine is a diagnostic, not the grade. Say
   "lab" or "field" every time you quote a number.
2. **A p75 improvement takes up to 28 days to appear** in CrUX. Never claim a field improvement on
   the day of the fix; claim the lab delta and say when the field number will confirm it.

Supporting diagnostics (not Core Web Vitals, useful for finding causes): TTFB, FCP, TBT, total blocking
time, bundle bytes, request count, main-thread work.

## Critical rules

1. **Measure before, measure after, show both.** A performance claim without a before/after pair is
   an opinion. Both from the same method, same conditions, stated.
2. **Never guess the bottleneck.** Profile first. The intuition-obvious cause is wrong often enough
   that guessing costs more than measuring.
3. **Optimize the critical path, not the impressive-looking thing.** A 40% gain on something that
   runs once at build time is worth less than 5% on every request.
4. **No regressions traded for wins.** A faster page that breaks a feature is not faster. Run the
   test suite after every change.
5. **Root cause, not symptom.** Caching over an N+1 query hides it; fixing the query removes it.
   Cache deliberately, never as a bandage.
6. **Report honestly.** If a change made no measurable difference, say so and revert it. A change
   with no measured effect is complexity with no payment.
7. **Read-only until the operator has seen the audit** in `--audit` mode; default mode may fix.

## Modes

```
/perf                  audit + fix + verify, full cycle
/perf --audit          measure and report only, change nothing
/perf --quick          Core Web Vitals + obvious wins, no deep profiling
/perf --deep           full profiling incl. backend, DB, and render path
/perf --bundle         bundle and dependency weight only
/perf --backend        server, query and API latency only
/perf --incremental    re-check only what changed since the last run
/perf <url>            audit a specific URL rather than a detected one
```

**Bare `/perf` picks its scope** and says which and why: a fresh repo with no prior report → full;
a report under 7 days old with only frontend changes since → `--incremental`; an explicit complaint
about a specific page → that page, deeply; a `/monitor` response-time regression → `--backend` first,
since that is where a regression usually originates.

## Phases

| # | Phase | Must not be skipped |
|---|---|---|
| 1 | Baseline measurement | real numbers, stated method, lab vs field labelled |
| 2 | Audit | per-layer, cost-ranked, with evidence per finding |
| 3 | Execute | one change at a time, tests after each |
| 4 | After measurement | same method as Phase 1, or the comparison is meaningless |
| 5 | Report | before/after table, what worked, what did not, what was reverted |

Phases 2-5 are what a long run loses to compaction if not held here. **Phase 4 is the one that makes
the whole exercise honest** - a run that optimizes without re-measuring has proved nothing.

## Budgets

Set or read a budget before optimizing; without one there is no definition of done.

| Thing | Default budget | Note |
|---|---|---|
| LCP / INP / CLS | the table above | field, p75 |
| JS shipped to the client | ≤ 300 KB gzipped initial route | per route, not total |
| Total page weight | ≤ 1 MB initial | images dominate; check formats first |
| Requests on first load | ≤ 50 | |
| API p95 | ≤ 500 ms | per endpoint, from the server's own timing |
| Build time | no regression > 20% | slow builds cost every future change |

A project may declare its own budgets (`lighthouse-budget.json`, a `performance` block in config, a
documented SLO). **Project budgets always win over these defaults.**

## Definition of done

- Before and after measured by the same method, both in the report
- Every applied change has a measured effect, or was reverted
- No test regressions; build still green
- Findings that were not fixed are listed with why and their estimated cost
- Report written; history appended; SITREP ends with "Suggested next"
