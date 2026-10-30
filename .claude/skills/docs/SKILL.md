---
name: docs
description: "Documentation audit and generation: find where docs are missing, stale or signature-echoing, then generate real ones - README, API reference, architecture overview, and WHY comments where the reasoning is non-obvious. Explains why, never restates what. This is the generate-and-audit engine; keeping docs current in the same PR is a separate standing discipline."
when_to_use: 'Trigger phrases: "generate docs", "document this", "write documentation", "update the README", "API docs", "the docs are stale", "document why". Run when documentation coverage has gaps or drifted, not to restate code that speaks for itself.'
---

# /docs - documentation audit and generation

**Spine. Survives compaction.** Detail beside it:

| File | Read at | Holds |
|---|---|---|
| `audit.md` | Phase 1 | the five audit dimensions and what each looks for |
| `reference.md` | Phase 2 | generation targets, formats, SITREP |

**Standards inherited:** [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) ·
[Steel Discipline](~/.claude/standards/STEEL_DISCIPLINE.md) ·
[Self-Improvement](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) ·
[Agent Orchestration](~/.claude/standards/AGENT_ORCHESTRATION.md) ·
[Status Updates](~/.claude/standards/STATUS_UPDATES.md) ·
[Skill Auto-Suggest](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) ·
[Context Management](~/.claude/standards/CONTEXT_MANAGEMENT.md) ·
[Sitrep Format](~/.claude/standards/SITREP_FORMAT.md) ·
[Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md)

## The one rule: document WHY, never WHAT

The failure mode of documentation is restating the code. A JSDoc that says `@param name - the name`
above `function greet(name)` adds nothing and rots the moment the signature changes. Good
documentation explains what the code cannot say for itself: **why** this approach, **why** this
constraint, what alternative was rejected, what will bite the next reader. If a doc only echoes the
signature or the obvious, it is noise - do not write it, and flag existing ones for removal.

## What this is vs the same-PR discipline

Keeping docs current alongside the code that changes them is a standing rule (it lives in CLAUDE.md
and applies on every PR). **This skill is different** - it is the audit-and-generation engine you run
when coverage has gaps or drifted: it finds what is missing or stale and generates real
documentation. The rule prevents drift; the skill fixes drift that already happened.

## Critical rules

1. **WHY over WHAT.** Every generated doc earns its place by explaining something the code does not.
   Signature-echo, restated-logic, and obvious-comment docs are net-negative - they are maintenance
   burden with no reader value.
2. **Verify against the code, generate from reality.** A README claiming a setup step that does not
   work, an API doc for a removed endpoint, an architecture diagram of last year's structure - each is
   worse than nothing. Generate from what the code actually does, now.
3. **Match the project's existing doc conventions.** If it uses TSDoc, use TSDoc; if it keeps
   architecture in `docs/adr/`, put it there. Do not impose a parallel system.
4. **Accuracy is checkable, so check it.** A generated setup guide is run. A generated API example is
   validated against the actual endpoint. "Should work" is not documentation.
5. **Stale is worse than absent.** A wrong doc actively misleads; a missing one at least does not.
   When auditing, flag stale docs as higher priority than gaps.
6. **Where the project has living deliverables** (an ADR catalogue, a per-phase tech doc), update
   THOSE rather than generating a competing set.

## Modes

```
/docs                 audit coverage, generate the missing/stale docs, verify
/docs --audit         report doc gaps and staleness only, generate nothing
/docs --readme        the README specifically
/docs --api           API/endpoint reference
/docs --architecture  architecture overview + diagrams
/docs --why <path>    add WHY comments where a file's reasoning is non-obvious
```

## Phases

| # | Phase | Must not be skipped |
|---|---|---|
| 0 | Detect | doc conventions in use, existing docs, what the project already keeps |
| 1 | Audit | five dimensions (`audit.md`): README, API, components, inline, architecture |
| 2 | Generate | the missing/stale docs, from the real code, in the project's format |
| 3 | Verify | run the setup steps, validate the API examples, confirm diagrams match |

Phases 1-3 are what a long run loses to compaction if not held here. **Phase 3 - verifying the
generated docs against reality - is what keeps them from becoming the confident-but-wrong docs that
are worse than none.**

## Definition of done

- Doc coverage audited across the five dimensions; stale flagged above missing
- Generated docs explain WHY, not WHAT; no signature-echo added
- Every generated doc verified against the code (setup steps run, API examples validated)
- Project conventions matched; living deliverables updated in place, not forked
- Report written; SITREP ends with "Suggested next"
