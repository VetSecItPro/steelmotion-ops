# /migrate - the migration method

## Phase 0: assess (the phase that prevents disasters)

**Read the official migration guide.** Next.js, React, Tailwind, Vue, Angular, Rails - every major
ships one, and it is authoritative. Extract:

- the full breaking-change list
- which of those breaking changes touch THIS codebase (grep for the removed/changed APIs)
- the codemods the maintainers provide
- the recommended ordering and any "do this first" prerequisites
- default/behaviour changes (caching, rendering, strict mode) that are not compile errors but change
  runtime behaviour - these are the ones that bite silently

Produce an effort/risk estimate. If `--assess`, stop here with the report. A migration whose breaking
changes were never mapped to the actual code is not planned; it is hoped.

## Phase 1: plan and branch

Break the migration into stages that can each build and pass tests. For a framework major, that is
often: config/build changes, then the mechanical codemod pass, then the manual API fixes, then the
behaviour-change handling. Create the branch. Never migrate in place on main.

For a tool swap (CRA -> Vite, Express -> Fastify), the stages are different - stand up the new tool
alongside, migrate surface by surface, cut over, remove the old. Plan the cutover point explicitly.

## Phase 2: baseline

Confirm the suite is green and the build works **before** touching anything. A migration debugged
against a suite that was already red cannot tell migration breakage from pre-existing breakage.

## Phase 3: codemods

Run the official codemods. Then **review every change they made** - codemods are mechanical and
occasionally wrong on edge cases, and reviewing them teaches you what the migration is actually doing.
Commit the codemod pass as its own stage so it is separable from the manual work.

## Phase 4: manual fixes

The breaking changes the codemods do not cover, handled by the guide - not by guessing from
compiler errors. The guide tells you the intended replacement; the compiler only tells you something
broke. Work through them by area, keeping the build closer to green as you go.

## Phase 5: per-stage verify

Build and test green at each stage boundary, not only at the end. A migration that is only tested once
at the finish is a single enormous debugging session when it fails; staged verification localises each
break to the stage that caused it.

## Phase 6: runtime verify

Build-green is necessary, not sufficient. Framework majors change runtime behaviour - a caching
default, a rendering mode, a hydration change - that compiles fine and breaks in the browser. Drive
the app (`/qatest`, or at least the critical flows manually) and confirm the deliberate behaviour
changes landed as intended and nothing else shifted.

## Rollback

The branch IS the rollback for a failed migration - abandon it, main is untouched. Within the
migration, each staged commit is a checkpoint to return to. `--resume` continues from the last green
stage rather than restarting. Document, in the report, the one-way changes (a data migration, a config
that other systems now depend on) that a branch abandon would NOT undo.
