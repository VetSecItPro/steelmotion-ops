---
name: architecture-survey
description: "Module-level architecture survey: find where a codebase is hard to change by reading git hot spots and judging module depth (small interface, much behavior behind it), apply the deletion test, and return ranked candidates with evidence, a visual report and a top pick. Read-only: it proposes where the seams should move and hands the chosen candidate to /brainstorm or /mdmp; it never edits code."
when_to_use: 'Trigger phrases: "hard to change", "ball of mud", "architecture review", "where should the boundaries be", "improve the architecture", "deep modules", "shallow modules", "module design", "this codebase is a mess structurally", "what should we restructure". Run every few weeks on an active repo, or when changes keep touching the same files. For dead code, duplication or long functions use /cleancode; for a decision already framed use /mdmp.'
---

# /architecture-survey - where the seams should be

**Spine. Survives compaction.** Detail beside it:

| File | Read at | Holds |
|---|---|---|
| `vocabulary.md` | Phase 1 | module, interface, depth, seam, adapter, leverage, locality; deletion test; adapter rule |
| `report.md` | Phase 3 | HTML report template, candidate card, diagram guidance |
| `reference.md` | Phase 4 | backlog rows, hand-off, SITREP, suggested next |

**Standards inherited:** [Domain Language](~/.claude/standards/DOMAIN_LANGUAGE.md) ·
[AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) ·
[Steel Discipline](~/.claude/standards/STEEL_DISCIPLINE.md) ·
[Agent Orchestration](~/.claude/standards/AGENT_ORCHESTRATION.md) ·
[Status Updates](~/.claude/standards/STATUS_UPDATES.md) ·
[Context Management](~/.claude/standards/CONTEXT_MANAGEMENT.md) ·
[Sitrep Format](~/.claude/standards/SITREP_FORMAT.md) ·
[Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md)

Adapted from `improve-codebase-architecture` and `codebase-design` in
[mattpocock/skills](https://github.com/mattpocock/skills) (MIT).

## Steel Principle: candidates, not designs

This skill finds and ranks; the operator picks; the design happens in the hand-off. **No new
interface, class split or file layout is proposed in the report.** A candidate says what hurts, why,
and roughly which direction deepening goes. The moment a survey sketches the new modules, the
operator is reviewing a design they never asked for, and the grilling that would have caught a bad
seam is skipped.

## Critical rules

1. **Read the record before the code.** In full: `GLOSSARY.md`, earlier
   `.reports/architecture-survey/`, and the decision records (`docs/adr/` or `docs/decisions/`)
   that concern structure (an unrelated record: title and decision line only, and say so). By
   search: the backlog and lessons file, for each candidate's file names and the words
   architecture, refactor and restructure; read every matching row and print the search terms and
   match count. A candidate the backlog already tracks is marked KNOWN with its row number; one a
   decision record rejected is dropped unless the friction since is real, and then it cites the
   record.
2. **Scope from history, and print the denominator.** Rank CURRENT files by commits touching them
   over a stated window. Plain `git log --format= --name-only` counts dead paths after a move, so
   count with `git log --follow --format=%h -- <file>` per current file, and credit a file split out
   of another with its parent's count; say which method. Print the window, the commit count, the
   number of distinct days and the top files with their counts. Under about 30 commits, or most of
   them on one or two days, say the churn signal is weak and lean on size and fan-in instead.
3. **A coverage table before any ranking.** Read and skimmed modules by name with line counts;
   unread modules grouped by directory with a count, except any in the churn or fan-in top ten,
   which are named. **Read** means every line of the region a claim rests on, with the function or
   line range named; a file that is mostly data is read for its code and sampled for its data, and
   the table says so. **Skimmed** means exports and imports only. A candidate may rest only on
   read regions; a sub-agent's reading counts only if it returns its line ranges.
4. **Every candidate carries evidence:** files, churn count, fan-in, and the specific code fact
   behind the claim (shared mutable state, a re-checked condition, a test that can only run end to
   end). "Feels tangled" is not evidence. Fan-in is required for candidates, not for every module:
   importers of the symbol as well as the path, following barrel `index` re-exports; for a
   scattered rule or a missing module, the count of files that restate it. **Each count states the
   command that took it**, and a grep count is checked against a named file known to match and one
   known not to (CLAUDE.md 6.3). Use POSIX classes (`[[:space:]]`) in `git grep`, not `\s`.
5. **Judge depth at the interface, not by line count.** A 390-line pure function behind one call is
   deep; a 40-line file that only forwards is shallow. Apply the deletion test to every suspect
   (`vocabulary.md`). Long-but-deep code is reported as "leave alone", which is a finding too.
6. **Rate each candidate** `Strong`, `Worth exploring` or `Speculative`, and end on one top pick with
   the reason. Say plainly when the codebase does not need restructuring.
7. **Read-only.** No edits, commits, installs or test runs that write. The report goes in a
   gitignored `.reports/architecture-survey/` in the repo (CLAUDE.md 7.6).
8. **Use the project's words.** Name candidates in `GLOSSARY.md` terms and the architecture in
   `vocabulary.md` terms; never a word the glossary lists under `_Avoid_`. No glossary: use the
   words the repo's `CLAUDE.md`, decision records and code already use, and say so in the record
   check; do not create one during the survey.

## Rationalizations (observed in the no-skill baseline, 2026-10-30)

| The thought | Why it is wrong | Do instead |
|---|---|---|
| "I read the hot files; the rest probably does not change the ranking" | The baseline ranked a second pick with four modules unread and said so only in a footnote | Coverage table first; an unread module that could matter is named in the verdict, or read |
| "A concrete decomposition makes the recommendation actionable" | It is a design nobody grilled; the operator now reviews modules instead of choosing a problem | Direction in two sentences; the design belongs to the hand-off |
| "The lessons file tail is enough context" | Known work (a tracked flake) and settled decisions were not checked, so a KNOWN item reads as NEW | Phase 0 reads backlog, decision records and prior reports |
| "The answer is in chat, that is the deliverable" | Nothing survives the session; the next survey starts from zero | Report file plus backlog rows |

## Modes

```
/architecture-survey               full survey, report, top pick, then offer the hand-off
/architecture-survey <path|area>   survey one area (skips the hot-spot inference)
/architecture-survey --report-only survey and report; no hand-off offered
```

## Phases

| # | Phase | Must not be skipped |
|---|---|---|
| 0 | Record | glossary, decision records, backlog, lessons, prior survey reports read; KNOWN items listed |
| 1 | Scope | churn ranking with its window and denominator; size and fan-in for the top files |
| 2 | Explore | read the hot spots with `vocabulary.md`. Optional above about 150 source files or with a large main context: delegate breadth to a sub-agent (`sonnet`, `medium`, named `#<n> architecture explore`) that returns line ranges; the main agent keeps the coverage table and reads every region a candidate rests on |
| 3 | Report | HTML report (`report.md`): coverage, candidates with evidence and rating, leave-alone list, top pick |
| 4 | Record and hand off | one backlog row per Strong or Worth-exploring candidate; ask which to explore; hand the pick to `/brainstorm` (or `/mdmp` if expensive to reverse) |

**Phase 3's "no new interfaces" and Phase 0's record check are what a long run loses first.** Hold
them here.

## Definition of done

- Record read first; KNOWN and previously rejected candidates marked, not re-proposed as new
- Churn window, commit count and per-file counts printed; weak-signal warning given when it applies
- Coverage table present; no candidate rests on an unread module
- Every candidate has files, churn, fan-in, the code fact, and a rating; no new interface sketched
- Leave-alone list present (deep or deliberate code that looks suspicious)
- Report written to `.reports/architecture-survey/` and its absolute path given; backlog rows written
- SITREP leads with the verdict: top pick, or "no restructuring needed", with the count of candidates
