---
name: cleancode
description: "Technical-debt reduction and dead-code elimination: find genuinely unused code, duplication, and complexity, remove or refactor it safely with tests as the safety net, and prove nothing broke. Conservative by design - it deletes only what it can prove is dead, and never trades a passing test for a smaller diff."
when_to_use: 'Trigger phrases: "clean up code", "dead code", "technical debt", "refactor", "remove unused", "simplify this", "code smell", "tidy up". Run when a codebase has accumulated cruft, not as a reflex on working code.'
---

# /cleancode - technical-debt reduction

**Spine. Survives compaction.** Detail beside it:

| File | Read at | Holds |
|---|---|---|
| `targets.md` | Phase 1 | what to look for, per category, and how to prove it is safe to touch |
| `reference.md` | Phase 4 | report, SITREP, before/after metrics |

**Standards inherited:** [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) ·
[Steel Discipline](~/.claude/standards/STEEL_DISCIPLINE.md) ·
[Self-Improvement](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) ·
[Status Updates](~/.claude/standards/STATUS_UPDATES.md) ·
[Skill Auto-Suggest](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) ·
[Context Management](~/.claude/standards/CONTEXT_MANAGEMENT.md) ·
[Sitrep Format](~/.claude/standards/SITREP_FORMAT.md) ·
[Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md)

## The governing bias: conservative

Cleanup that breaks something is worse than the debt it removed. This skill deletes only what it can
**prove** is dead, refactors only behind a test net, and reverts anything that cannot be shown safe.
A smaller, riskier diff loses to a larger, provable one every time.

## Critical rules

1. **Prove dead before deleting.** "Looks unused" is not proof. A symbol can be referenced by a
   string, a dynamic import, a framework convention, a config, a test, or another package. Verify
   with the tooling AND a grep for dynamic uses before removing anything.
2. **Tests are the safety net; run them after every change.** A refactor with no test coverage on the
   touched code gets tests FIRST (hand to `/test-ship`), or it is reported, not done. Refactoring
   untested code blind is how cleanup ships bugs.
3. **One category at a time, committable in slices.** Dead code, then duplication, then complexity -
   separate passes, separate commits. A single giant cleanup diff is unreviewable and un-revertable.
4. **Behaviour must not change.** Cleanup is a refactor: same inputs, same outputs, smaller/clearer
   code. If behaviour changes, it is a feature change wearing a cleanup label - stop and flag it.
5. **Do not "improve" what is not debt.** Working, tested, readable code is not a target because it
   could be written differently. Churn for taste introduces risk for no benefit.
6. **Respect deliberate patterns.** A duplication that exists because two things are coincidentally
   similar but will diverge is not debt. An "ugly" bit with a WHY comment is a decision. Read before
   deleting.
7. **Measure the result.** Report the actual reduction (lines, files, dependencies, complexity), not
   "cleaner".

## Modes

```
/cleancode              audit + safe removal/refactor + verify
/cleancode --audit      report the debt, change nothing
/cleancode --dead       dead code and unused exports/deps only
/cleancode --dupe       duplication only
/cleancode --complexity high-complexity functions only
/cleancode --file <p>   one file, thoroughly
```

## Phases

| # | Phase | Must not be skipped |
|---|---|---|
| 0 | Baseline | current metrics; the test suite must be green before touching anything |
| 1 | Find | dead code, duplication, complexity, unused deps (`targets.md`), ranked by safety |
| 2 | Prove | each candidate confirmed dead/safe before it is touched |
| 3 | Remove/refactor | one category, one slice at a time; tests after each |
| 4 | Verify | full suite green, build green, behaviour unchanged; report the delta |

Phases 2-4 are what a long run loses to compaction if not held here. **Phase 2 - proving safety
before touching - is the whole discipline; skip it and cleanup becomes a bug generator.**

## Definition of done

- Baseline suite was green before, and is green after
- Everything removed was proven dead (tooling + dynamic-use grep), not assumed
- Refactors preserved behaviour; touched-but-untested code got tests first or was left alone
- Changes committed in reviewable slices by category
- Deliberate patterns respected, not "cleaned"
- Report with the measured reduction; SITREP ends with "Suggested next"
