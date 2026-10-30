---
name: launch
description: "Launch-readiness gate: orchestrates the audit skills (sec-ship, test-ship, perf, a11y, deps, monitor) in audit-only mode, adds the five checks none of them cover (content, SEO, user-flow, payment, legal), scores every domain, and returns a single GO / CONDITIONAL / NO-GO verdict with the blockers named."
when_to_use: 'Trigger phrases: "ready to launch?", "pre-launch check", "launch readiness", "are we ready to ship this", "go/no-go", "before we go live". Run before a real launch or a major release, not for a routine deploy.'
---

# /launch - launch-readiness gate

**Spine. Survives compaction. The verdict logic and the blocker rules must never drop** - a launch
gate that loses its own GO/NO-GO criteria is worse than none.

| File | Read at | Holds |
|---|---|---|
| `checks.md` | Phase 2 | the five unique domain checks this skill owns, in detail |
| `reference.md` | Phase 3 | scorecard, verdict rules, report, SITREP |

**Standards inherited:** [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) ·
[Steel Discipline](~/.claude/standards/STEEL_DISCIPLINE.md) ·
[Self-Improvement](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) ·
[Agent Orchestration](~/.claude/standards/AGENT_ORCHESTRATION.md) ·
[Status Updates](~/.claude/standards/STATUS_UPDATES.md) ·
[Skill Auto-Suggest](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) ·
[Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md) ·
[Context Management](~/.claude/standards/CONTEXT_MANAGEMENT.md) ·
[Multi Repo Awareness](~/.claude/standards/MULTI_REPO_AWARENESS.md) ·
[Sitrep Format](~/.claude/standards/SITREP_FORMAT.md)

## What it does

Two things, in one pass:

1. **Orchestrate the audit skills** (audit-only - it never mutates during a readiness check), each
   producing a domain score.
2. **Run the five checks no other skill owns** - content, SEO, user-flow, payment, legal/privacy.

Then it scores every domain, weights them, and returns **one verdict**: GO, CONDITIONAL, or NO-GO,
with the specific blockers. The value is the single answer - a launch decision fragmented across six
separate reports is not a decision.

## Orchestrated skills (audit-only)

| Domain | Skill | Mode |
|---|---|---|
| Security | `/sec-ship --audit` | never fix during a gate |
| Test coverage | `/test-ship --audit` | |
| Performance | `/perf --audit` | Core Web Vitals + budgets |
| Accessibility | `/a11y --audit` | WCAG 2.2 AA |
| Dependencies | `/deps --audit` | supply-chain + advisories |
| Production health | `/monitor` | if already deployed to a staging/preview surface |

Each runs in **audit mode** - a readiness gate reports, it does not change the thing being assessed.
If the operator wants fixes, that is a separate pass after the verdict. Spawn them as sub-agents where
the orchestration standard allows, sequentially where they would conflict.

## The five checks this skill owns (detail in `checks.md`)

Content readiness · SEO & meta · User-flow completeness · Payment & subscription · Legal & privacy.
These are the domains the code-level audit skills do not cover, and they are frequent launch blockers.

## Verdict rules - the load-bearing logic

| Verdict | Condition |
|---|---|
| **NO-GO** | any hard blocker: a security finding that exposes data, a legal requirement unmet, payment broken on a paid product, a SEV-1-class failure in any domain |
| **CONDITIONAL** | no hard blocker, but one or more domains below threshold with a named, dated remediation the operator accepts |
| **GO** | every domain at or above threshold, no hard blocker, no unaccepted risk |

**A single hard blocker is NO-GO regardless of a high average.** A 95/100 overall with a data-exposing
security hole is NO-GO, not "GO with a note" - averaging a blocker away is the failure this gate exists
to prevent.

## Not-applicable domains

A domain that does not apply (payment on a free product, mobile on a web-only app) is marked N/A and
its weight redistributed proportionally across the rest - never scored 0 (which would tank the verdict)
and never 100 (which would hide that it was not checked).

## Modes

```
/launch                full gate: all skills + 5 checks, scored verdict
/launch --quick        the hard-blocker checks only - fast "any showstoppers?"
/launch --domain <n>   one domain (security | content | seo | flow | payment | legal | perf | a11y)
/launch --recheck      re-run only the domains that were below threshold last time
```

## Definition of done

- Every applicable domain scored, from a real audit not an assumption
- N/A domains marked and their weight redistributed
- A single verdict: GO / CONDITIONAL / NO-GO
- Every hard blocker named, with what it would take to clear it
- CONDITIONAL items carry an operator-accepted, dated remediation
- Report written linking each domain's underlying skill report; SITREP ends with the verdict and
  "Suggested next"
