---
name: brainstorm
description: "Socratic design exploration: look up what the repo can answer, then interview the operator in numbered rounds (each question with a recommended answer) until every open decision is settled, present 2-3 genuinely different approaches with tradeoffs, and write a spec. HARD-GATE: no implementation before the spec is approved."
when_to_use: 'Trigger phrases: "help me think through", "explore approaches", "what are the options", "design this with me", "I am not sure how to build this", "grill me", "stress-test this plan". Use BEFORE implementation, when the shape of the solution is still open. Hard-gates on an approved spec.'
allowed-tools: Bash(git *), Bash(mkdir *), Bash(date *), Bash(ls *), Read, Write, Edit, Glob, Grep, WebSearch, Agent
---

# /brainstorm - design exploration with a hard gate

**Spine. Survives compaction.** Detail beside it:

| File | Read at | Holds |
|---|---|---|
| `questions.md` | Phase 2 | the round format, what to look up instead of asking, the language duty, the stop rule |
| `spec-template.md` | Phases 3-4 | approach format, recommendation, spec skeleton, self-review |
| `reference.md` | Phases 5-6 and the end | approval and handoff messages, status lines, SITREP, cleanup, related skills |

**Standards inherited:** [Domain Language](~/.claude/standards/DOMAIN_LANGUAGE.md) ·
[Steel Discipline](~/.claude/standards/STEEL_DISCIPLINE.md) ·
[Status Updates](~/.claude/standards/STATUS_UPDATES.md) ·
[Context Management](~/.claude/standards/CONTEXT_MANAGEMENT.md) ·
[Sitrep Format](~/.claude/standards/SITREP_FORMAT.md) ·
[Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md)

Brainstorming discipline from obra/superpowers (MIT); the round format from the `grilling` skill
in mattpocock/skills (MIT), adopted 2026-10-30.

## Steel Principle: no implementation until the spec is approved

This skill produces an approved design, never code. Lighter than `/mdmp` (no seven-lens war-game),
but the gate is the same: the operator approves the written spec, explicitly, before anything is
built. "It is simple", "just to be helpful" and "a quick prototype" do not open the gate.

## Critical rules

1. **Facts are looked up; decisions are asked.** Anything the repo, its docs, its history or a web
   search can answer is found before the operator sees a question. Only decisions (goals, scope,
   tradeoffs, taste) go to the operator.
2. **Ask in rounds, not one at a time and not all at once.** Each round asks every question whose
   prerequisites are already settled, numbered, each with a recommended answer phrased so "yes"
   accepts it (`questions.md`). A question that depends on an answer still open waits for a later
   round.
3. **Stop when nothing is left open,** not at a fixed count: every decision the approaches depend on
   is settled or explicitly parked. If that takes more than about four rounds, the topic is
   `/mdmp`-sized; say so.
4. **Approaches are genuinely different,** not variants of one idea: 2-3, each with pros, cons,
   effort and risk, and ONE recommendation tied to what the operator said they care about.
5. **No placeholders in the spec.** "TBD", "similar to", "etc." are filled in or become a named open
   question.
6. **If it mostly exists already, say that first.** When the lookup shows the idea is largely
   built (a flag, a skip rule, a deliberate refusal), lead with that and what is actually missing;
   "you already have this, the gap is X" is a complete and valuable outcome. The verdict line goes
   before "Round 1" (CLAUDE.md 1.1: the flaw leads).
7. **Use the project's words** (`standards/DOMAIN_LANGUAGE.md`): read `GLOSSARY.md` first if it
   exists; challenge a conflicting term at once; write a settled term in right away.

## Rationalizations

| The thought | Why it is wrong | Do instead |
|---|---|---|
| "This is simple, skip the spec" | Simple ideas on wrong assumptions build the wrong thing faster | Write the spec; ten lines beats a hundred lines of wrong code |
| "I already know what they want" | You know what they said, not what they meant | Put it to them as a question with your answer as the recommendation |
| "I will ask how it works today" | The repo knows; asking spends the operator on a lookup | Read it, state it, ask only what follows from it |
| "One question at a time is more polite" | Five round trips for five independent questions wastes the operator's attention | Ask the whole open frontier in one round |
| "Ask everything up front" | Questions whose answers depend on earlier answers get guessed | Only the questions whose prerequisites are settled |
| "They seem impatient, skip ahead" | Rework is slower than one good round | A round with recommended answers; "yes to all" is one word |

## Phases

| # | Phase | Must not be skipped |
|---|---|---|
| 0 | Intake | topic, how settled it is, the affected area. Nothing is written to the repo before the first settled glossary term or the spec |
| 1 | Context | read the affected code, recent commits there, `CLAUDE.md`, existing specs, `GLOSSARY.md` and decision records; list what is known and what is a decision |
| 2 | Rounds | `questions.md`; each round waits for answers; stop when the frontier is empty |
| 3 | Approaches | 2-3 distinct approaches and one recommendation (`spec-template.md`); wait for the pick |
| 4 | Spec | in the repo's existing spec or plan folder if it has one, else `docs/brainstorm/specs/YYYY-MM-DD-<topic>-design.md`; self-reviewed |
| 5 | HARD-GATE | explicit approval of the written spec |
| 6 | Handoff | `/subagent-dev <spec>`, inline execution for a small spec, or the operator builds it |

**Phase 5 is what a long session loses first.** Hold it here: no implementation code, no "starter"
files, no proposed diff until the operator approves the spec in words.

## Definition of done

- Every fact the questions depended on was looked up, and the operator was asked only decisions
- Each round numbered, each question with a recommended answer; no question asked before its
  prerequisites were settled
- 2-3 genuinely different approaches, one recommendation, the operator's pick recorded
- Spec written with no placeholders, self-review done, glossary terms used
- Approval explicit and recorded; nothing implemented before it
- SITREP leads with the status: INTERVIEWING (waiting on a round), AWAITING_APPROVAL, SPEC_APPROVED
  or ABANDONED
