---
name: migrate
description: "Major framework and library version migrations: Next 14->15, React 18->19, Tailwind 3->4, CRA->Vite, Express->Fastify and the like. Read the breaking-change list, apply codemods where they exist, fix what they cannot, and verify at each step. Distinct from /deps (which does package-level updates) - this handles the architectural moves."
when_to_use: 'Trigger phrases: "migrate [framework]", "major version upgrade", "upgrade to [X]", "Next 15", "React 19", "Tailwind 4", "move from X to Y", "framework migration". Use for a framework/major-version move; for routine dependency bumps use /deps.'
---

# /migrate - major version and framework migration

**Spine. Survives compaction.** Detail beside it:

| File | Read at | Holds |
|---|---|---|
| `method.md` | throughout | the migration method: assess, plan, execute-in-stages, verify |
| `reference.md` | report | report format, rollback, SITREP |

**Standards inherited:** [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) ·
[Steel Discipline](~/.claude/standards/STEEL_DISCIPLINE.md) ·
[Self-Improvement](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) ·
[Multi-Repo Awareness](~/.claude/standards/MULTI_REPO_AWARENESS.md) ·
[Status Updates](~/.claude/standards/STATUS_UPDATES.md) ·
[Skill Auto-Suggest](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) ·
[Context Management](~/.claude/standards/CONTEXT_MANAGEMENT.md) ·
[Sitrep Format](~/.claude/standards/SITREP_FORMAT.md) ·
[Agent Orchestration](~/.claude/standards/AGENT_ORCHESTRATION.md)

## migrate vs deps

`/deps` bumps package versions and handles majors one dependency at a time. `/migrate` handles the
**architectural** moves: a framework major with breaking API changes across the codebase, or a swap
between tools (CRA -> Vite, Express -> Fastify, Pages Router -> App Router). Those need a breaking-change
map, codemods, and per-file work that a version bump does not. If the task is "bump lodash", that is
`/deps`. If it is "move to Next 15", that is here.

## Critical rules

1. **Read the official migration guide first.** Every major framework ships one. It is the
   breaking-change list, the codemod inventory, and the ordering. Migrating without reading it is
   guessing, and framework majors are the worst possible place to guess.
2. **A migration is a branch, never in-place on main.** It is a large, reversible-only-by-branch
   change. Isolate it.
3. **Run the codemods the maintainers provide, then fix what they miss.** Official codemods
   (`npx @next/codemod`, React's, Tailwind's upgrade tool) do the mechanical 80%. The remaining 20% is
   judgment - do that by hand, informed by the guide.
4. **Stage it; keep it green between stages.** A framework migration done as one atomic change is
   un-debuggable when it breaks. Break it into stages that each build and pass tests where possible.
5. **Tests are the migration's proof.** A migration "works" when the suite that passed before passes
   after. Thin coverage on a migrated path is a risk - note it, and prefer adding tests before the
   move on critical paths.
6. **Behaviour is preserved unless the migration deliberately changes it.** A framework major
   sometimes changes defaults (caching, rendering). Those are called out in the guide - handle each
   deliberately, do not let a silent default change ship as a surprise.
7. **Verify the build AND the running app.** A migration can compile and still break at runtime -
   a changed rendering model, a removed API used dynamically. Drive the app after (hand to `/qatest`).

## Modes

```
/migrate <target>        full migration to the named target
/migrate --assess <t>    analyse effort/risk/breaking-changes for a target; do not migrate
/migrate --resume        continue a staged migration from the last green stage
```

## Phases

| # | Phase | Must not be skipped |
|---|---|---|
| 0 | Assess | read the guide; inventory breaking changes that touch THIS codebase; estimate effort/risk |
| 1 | Plan | stage the migration; identify codemods; branch |
| 2 | Baseline | suite green, build green, before touching anything |
| 3 | Codemods | run the official ones; review every change they made |
| 4 | Manual fixes | the breaking changes codemods cannot handle, by the guide |
| 5 | Per-stage verify | build + tests green at each stage, not just at the end |
| 6 | Runtime verify | drive the app; confirm no runtime-only breakage |
| 7 | Report | what changed, what behaviour shifted deliberately, rollback path |

Phases 3-7 are what a long run loses to compaction if not held here. **Phase 0 - reading the guide
and mapping breaking changes to THIS code - is what turns a migration from a gamble into a plan.**

## Definition of done

- The official migration guide was read; breaking changes mapped to this codebase
- On a branch; baseline was green
- Codemods run and reviewed; manual fixes applied per the guide
- Build green, suite green (the same tests that passed before)
- App driven at runtime; no runtime-only regressions
- Deliberate default/behaviour changes documented, not silent
- Report with the rollback path; SITREP ends with "Suggested next"
