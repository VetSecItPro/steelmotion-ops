---
name: incident
description: "Structured production incident response: classify severity, mitigate user impact FIRST, find root cause with evidence, fix and verify, then write the postmortem and the regression test. Timestamped throughout. Never deploys to production without explicit approval. Optimised for a live emergency, not a leisurely debug."
when_to_use: 'Trigger phrases: "production is down", "users are reporting", "urgent prod issue", "site is down", "outage", "incident", "emergency". Use the moment real users are affected. For a non-urgent bug with no user impact, use /investigate.'
---

# /incident - production incident response

**Spine. Survives compaction. In an incident the model WILL compact - severity, the approval gate,
and the mitigate-first rule must never be the part that drops.** That is the entire reason this file
is structured this way.

| File | Read at | Holds |
|---|---|---|
| `stages.md` | throughout | the response stages: detect, mitigate, diagnose, fix, verify, postmortem |
| `reference.md` | Stage 6 | postmortem template, timeline format, SITREP |

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

## The rule that comes before all others

**Mitigate user impact first; find the perfect root cause second.** In an outage, a fast rollback
that restores service beats a slow correct fix that keeps users down for an hour. Stop the bleeding,
then diagnose at leisure. This is what separates incident response from debugging - `/investigate`
optimises for the right answer, `/incident` optimises for users being back.

## Severity - classify first, it sets everything

| Severity | Criteria | Response |
|---|---|---|
| **SEV-1** | full outage, data loss risk, security breach, auth/login/payment 500s | immediate; mitigate-first; page a human |
| **SEV-2** | major feature broken, significant user impact | fast triage, structured fix |
| **SEV-3** | degraded performance, minor feature broken, elevated errors without outage | standard workflow |
| **SEV-4** | cosmetic, edge case, non-blocking | can queue; still gets a postmortem |

Fast-classification signals: "site is down" from a user = **SEV-1 until proven otherwise**. 500s on
auth/login/payment = SEV-1. 500s elsewhere = SEV-2. Elevated error rate, no outage = SEV-3.

## Non-negotiable rules

1. **Never deploy to production without explicit approval.** Fix and prove it locally or on a branch;
   the operator decides when it ships. This holds even at SEV-1 - especially at SEV-1, where a panicked
   bad deploy makes an outage worse.
2. **Mitigate before diagnose.** Rollback, feature-flag-off, scale-up, or failover to restore service.
   The clean root-cause fix comes after users are back.
3. **Evidence before hypotheses.** Collect logs, metrics and state before theorising - a wrong theory
   under time pressure burns the minutes that matter.
4. **Timestamp everything, ISO-8601.** The timeline is the incident's spine and the postmortem's data.
5. **3 attempts max per approach; revert each failed fix immediately.** A failed fix left in place
   compounds the incident. Undo, then try a different approach. After 3, mark BLOCKED and escalate.
6. **Postmortem is mandatory, even at SEV-4.** An incident with no postmortem will recur.
7. **A regression test ships with the fix.** The same incident must not happen twice silently.
8. **The report is the single source of truth**, updated after every stage and every fix attempt, so
   a handoff or a compaction loses nothing.

## Run modes

```
/incident                 full response, severity auto-classified
/incident --sev1          skip triage, straight to mitigate-first (declared critical)
/incident --mitigate      restore service only; diagnose later
/incident --postmortem    write the postmortem for an already-resolved incident
```

## Stages

| # | Stage | Must not be skipped |
|---|---|---|
| 0 | Detect and classify | severity, blast radius, who/what is affected, start the timeline |
| 1 | **Mitigate** | restore service by the fastest safe means; users first |
| 2 | Diagnose | evidence-first root cause (deep reasoning here is non-negotiable) |
| 3 | Fix | the correct fix, locally/branch, one change at a time |
| 4 | Verify | reproduce the original failure, confirm the fix resolves it |
| 5 | Deploy | ONLY on explicit approval; verify in production after |
| 6 | Postmortem | timeline, root cause, contributing factors, action items, the regression test |

Every stage after 1 lives past the compaction line unless held here. **Stage 1 - mitigate - is the
one that must survive above everything, because it is what an incident is for.**

## Human decision triggers

Always stop and ask: any production deploy; a mitigation that itself risks data (a rollback across a
migration); anything touching customer data; declaring the incident resolved; a fix that is a guess
rather than a confirmed cause. In an incident the temptation to act unilaterally is highest and the
cost of a wrong unilateral action is worst.

## Definition of done

- Service restored (mitigation) and the time-to-mitigate recorded
- Root cause confirmed with evidence, not assumed
- Permanent fix verified against the original failure and deployed on approval
- Regression test added
- Postmortem written: timeline, cause, contributing factors, dated action items
- SITREP ends with "Suggested next"
