---
name: investigate
description: "Systematic root-cause debugging: gather evidence before forming a theory, test hypotheses against reality rather than guessing, find the actual cause not a plausible one, apply the minimal correct fix, and add a regression test so it cannot return. Evidence-first, not intuition-first."
when_to_use: 'Trigger phrases: "not working", "broken", "cannot figure out", "why is this happening", "deep dive", "debug this", "keeps failing", "bug". Run when something is wrong and the cause is not obvious. For a live production outage use /incident instead.'
---

# /investigate - systematic root-cause debugging

**Spine. Survives compaction.** Detail beside it:

| File | Read at | Holds |
|---|---|---|
| `method.md` | throughout | the evidence-first method, per phase, with the discipline that makes it work |
| `reference.md` | report | root-cause record, regression test, SITREP |

**Standards inherited:** [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) ·
[Steel Discipline](~/.claude/standards/STEEL_DISCIPLINE.md) ·
[Self-Improvement](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) ·
[Status Updates](~/.claude/standards/STATUS_UPDATES.md) ·
[Skill Auto-Suggest](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) ·
[Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md) ·
[Context Management](~/.claude/standards/CONTEXT_MANAGEMENT.md) ·
[SITREP Format](~/.claude/standards/SITREP_FORMAT.md)

## The one rule everything else serves

**Evidence before theory.** The failure mode of debugging is forming a hypothesis in the first ten
seconds and then spending an hour trying to confirm it. This skill inverts that: gather what is
actually happening first, and let the evidence narrow the hypotheses, not the other way round.

If this is a live production outage - users affected right now - this is the wrong skill; use
`/incident`, which triages and mitigates first and investigates after.

## Critical rules

1. **Reproduce it before you fix it.** A bug you cannot reproduce is a bug you cannot verify fixed.
   If it is intermittent, find the condition that triggers it before touching code.
2. **The first plausible cause is usually not the cause.** Plausible and correct are different.
   Confirm the mechanism, do not assume it.
3. **Change one thing at a time.** Multiple simultaneous changes make it impossible to know which
   fixed it - or which introduced a new bug while masking the old.
4. **Fix the root, not the symptom.** A null check that stops the crash without explaining why the
   value was null has moved the bug, not fixed it. Trace to the origin.
5. **The fix is the minimal correct change.** Not a refactor, not "while I'm here" - the smallest
   change that addresses the actual cause. Scope creep during a fix introduces new bugs.
6. **Prove the fix against the reproduction.** Re-run the exact steps that failed; confirm they now
   pass. Then add a regression test so the same bug cannot return silently.
7. **A wrong theory is data.** Record disproven hypotheses - they narrow the space and stop the next
   session re-treading them.

## Modes / tiers

The depth scales to the problem. State which tier and why.

| Tier | When | Depth |
|---|---|---|
| **Quick** | clear error, obvious locus | reproduce, read the trace, fix, test |
| **Standard** | non-obvious, needs evidence | full method: evidence -> pattern -> hypothesis -> test -> fix |
| **Deep** | intermittent, systemic, or several failed attempts | add: instrumentation, bisection, state/timing analysis, the assumption audit |

Escalate a tier when the current one stalls - three failed fix attempts at Standard means the model of
the bug is wrong; go Deep and question the assumptions, do not keep trying variations.

## Phases

| # | Phase | Must not be skipped |
|---|---|---|
| 1 | Intake | reproduce; capture the exact failure, not the reported paraphrase |
| 2 | Evidence | logs, stack traces, state, timing, recent changes - before any theory |
| 3 | Pattern | what the evidence has in common; when it started; what changed |
| 4 | Hypothesis | a testable theory of the mechanism, with a prediction |
| 5 | Test | prove or disprove the hypothesis against reality |
| 6 | Fix | minimal, root-cause, one change |
| 7 | Verify | re-run the reproduction; add the regression test |

Phases 4-7 are what a long run loses to compaction if not held here. **Phase 5 - testing the
hypothesis rather than assuming it - is the whole discipline; skip it and you are guessing.**

## Definition of done

- The bug was reproduced, then confirmed fixed against that same reproduction
- The root cause is identified and stated - the mechanism, not just the location
- The fix is minimal and addresses the cause, not the symptom
- A regression test exists that fails on the old code and passes on the new
- Disproven hypotheses recorded; a pattern worth remembering saved to history
- Report written; SITREP ends with "Suggested next"
