---
name: mdmp
description: "Military Decision-Making Process adapted for software: frame the problem, generate genuinely distinct courses of action, war-game each against seven specialist lenses, score on a weighted matrix, and produce an executable plan with the rejected options and their reasons recorded."
when_to_use: 'Trigger phrases: "big feature", "new architecture", "overhaul", "re-architect", "should we build or buy", "plan this properly", "multi-lens analysis", "which approach". Use when a decision is expensive to reverse and several approaches are plausible.'
---

# /mdmp - multi-lens decision process

**Spine. Survives compaction.** Detail beside it:

| File | Read at | Holds |
|---|---|---|
| `lenses.md` | Step 3 | the seven specialist lenses and what each must produce |
| `steps.md` | throughout | the seven-step procedure in detail |
| `reference.md` | Step 7 | decision record format, matrix, SITREP |

**Standards inherited:** [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) ·
[Steel Discipline](~/.claude/standards/STEEL_DISCIPLINE.md) ·
[Agent Orchestration](~/.claude/standards/AGENT_ORCHESTRATION.md) ·
[Context Management](~/.claude/standards/CONTEXT_MANAGEMENT.md) ·
[Status Updates](~/.claude/standards/STATUS_UPDATES.md) ·
[Skill Auto-Suggest](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) ·
[Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md) ·
[SITREP Format](~/.claude/standards/SITREP_FORMAT.md)

## When to use, and when not

**Use** when reversal is expensive: architecture, data model, build-vs-buy, a migration, a security
posture change, anything that sets a constraint others will inherit.

**Do not use** for work with one obvious approach, a reversible change, or a decision already made.
MDMP on a small decision is theatre and burns the operator's patience for the times it matters.
Say so and recommend `/brainstorm` (exploration) or `/subagent-dev` (already decided, needs execution).

## The non-negotiable: courses of action must be genuinely different

The failure mode of this process is generating three variations of the same idea and calling it
analysis. Each COA must differ in **approach**, not in parameters.

A valid set: build in-house / adopt an existing library / buy a managed service.
An invalid set: build it with Postgres / build it with MySQL / build it with SQLite.

**Minimum three. At least one must be genuinely uncomfortable** - the option the team's instinct
rejects. If every COA is palatable, the option space was not explored. "Do nothing" is a legitimate
COA and must be considered whenever the status quo is survivable.

## Seven steps

| # | Step | Produces |
|---|---|---|
| 1 | Receipt of mission | what is actually being asked, and what is out of scope |
| 2 | Mission analysis | constraints, assumptions, unknowns, the real decision criteria |
| 3 | COA development | ≥3 genuinely distinct approaches, each stated at equal depth |
| 4 | COA analysis (war-game) | each COA through all seven lenses; failure modes surfaced |
| 5 | COA comparison | weighted matrix, scored with reasons, not vibes |
| 6 | COA approval | a recommendation with its confidence and what would change it |
| 7 | Orders production | an executable plan, plus the decision record |

Steps 4-7 are what a long run loses to compaction if not held here. **Step 4 is where the value is** -
a COA that has not been war-gamed is a guess with a heading.

## The seven lenses (detail in `lenses.md`)

Engineering · Product · Security · QA/Testing · Design/UX · DevOps · Risk.

Every COA goes through **all seven**. A lens that finds nothing must say so explicitly - silence is
indistinguishable from a lens that was skipped, and Step 8's satisfaction check will catch it.

## Scoring

Weighted matrix. **Weights are set by the operator before scoring, never after seeing the results** -
weights chosen afterwards are a justification, not a decision.

Default weights when the operator has not specified: correctness/risk 30%, effort 20%,
maintainability 20%, time-to-value 15%, cost 15%. Score each COA 1-5 per criterion with a
one-sentence reason. **A score without a reason is not a score.**

Ties are information: if two COAs score within 10%, say the decision is close, name what would break
the tie, and recommend the reversible one.

## Critical rules

1. **No placeholders.** "TBD", "we'll figure this out later" and "some kind of caching layer" are
   forbidden in a plan. If it is unknown, it is an assumption to be recorded and tested.
2. **Assumptions are labelled and testable.** Each carries how it would be validated and what
   happens if it is false.
3. **Rejected COAs are recorded with reasons.** The most valuable part of the record six months
   later is why the obvious option was not taken.
4. **The recommendation carries a confidence and a trigger.** "High confidence unless the vendor's
   rate limits turn out lower than published, which would move this to COA-2."
5. **No implementation before approval.** This skill produces a decision, not code.

## Definition of done

- ≥3 genuinely distinct COAs, at equal depth, including an uncomfortable one
- All seven lenses applied to each, with explicit silence where a lens found nothing
- Weights fixed before scoring; every score justified in a sentence
- Recommendation with confidence and its change-trigger
- Decision record written, including rejected options and assumptions
- Executable plan produced; hand off to `/subagent-dev` for execution
