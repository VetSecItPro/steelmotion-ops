# Tests Ship With Code - reference

> Extracted from `~/.claude/CLAUDE.md` on 2026-07-28. The RULE stays in CLAUDE.md so it applies on
> every session; this file holds the reference detail, which is only needed when you are
> actually doing the thing. CLAUDE.md is loaded in full on every session in every project,
> so reference material there is paid for permanently.

---

## Tests Ship With Code (GLOBAL - ALL PROJECTS)

**Every PR that adds business logic adds the tests for that logic in the same PR.** No exceptions like "smoke test only" or "I'll write tests later." Tests aren't a follow-up - they're part of the same change.

This codifies Steel Principle #3 (`~/.claude/standards/STEEL_DISCIPLINE.md`) into a default behavior, not just a skill-invocation discipline.

### What needs tests, in priority order

1. **Auth + middleware seams** - every change to a request-validation gate (cookie auth, service token, role check, signature verification) ships with unit tests that cover the new path AND the previously-working paths. Edge middleware bugs surface as silent 401/302 storms in production; the only cheap insurance is automated coverage.
2. **API route handlers** - every new POST/PUT/DELETE handler ships with at least: missing-auth → 4xx, invalid-body → 400 (Zod path), happy path → 200 with expected response shape, downstream-failure → 5xx. Mock the third-party SDK (Resend, Polar, etc.) at the boundary, not the framework.
3. **Pure business logic in `lib/`** - schemas, validators, parsers, decision functions. Easy targets, high ROI. Aim for ~80% line coverage on these files.
4. **Templates and fixtures count as code.** Email/PDF/markdown templates need tests that prove the rendered output contains the expected fields (don't trust mustache to fail loudly).
5. **Critical-path E2E** - login → dashboard → primary action. ~3-5 specs maximum at first; grow only when a real regression escapes.

### What doesn't need a test (yet)

- Pure UI / React component layout (covered by E2E + manual review)
- Generated code, codegen output
- Pages that just compose components and have no logic
- Migrations + one-shot scripts (write defensive code instead)

### Framework conventions

| Codebase | Unit + Integration | E2E | Infra/Bash |
|---|---|---|---|
| Next.js + TS | `vitest` (`tests/*.test.ts`) | `playwright` (`e2e/*.spec.ts`) | bats if scripts |
| Backend Python | `pytest` (`tests/python/`) | optional integration suite | bats |
| Bash/infra | bats (`tests/bash/*.bats`) | n/a | bats |

When you start a session in a codebase that doesn't have tests yet, the FIRST PR adds:
- The test framework (vitest/pytest/bats - match the language)
- A `package.json`/`pyproject.toml` script alias (`npm test` / `pytest`)
- A CI job that runs the suite and gates merges (no manual "did you run tests?" reviews)
- ONE test that proves the framework works end-to-end (smoke test)

After that scaffolding, every subsequent PR adds real tests as part of the work.

### How to apply this rule when working

- **Before writing code:** identify which test file the new code's tests will live in. If the file doesn't exist, create it FIRST as an empty skeleton with the imports and one failing test.
- **While writing code:** make the failing test pass. Add edge-case tests as you discover them.
- **Before opening the PR:** run the suite locally (`npm test` / `pytest` / `bats tests/`) AND `npm run build` (frontend) - typecheck/lint don't catch all integration breakage; build does.
- **In the PR description:** state how many tests this PR adds + the test count delta (e.g., "+22 tests, suite now 1110/1110").

### When the rule is hard to follow

If a piece of code feels untestable, that's a design signal - the code is probably too coupled. Refactor for testability before shipping. Tightly-coupled code without tests is the cheapest way to ship bugs to prod.

If you genuinely can't test something today (waiting on infra access, third-party sandbox, etc.), open the PR with a "tests deferred - blocked on X" note in the description AND a follow-up task in the project's backlog/TaskList. Don't drop the requirement silently.

### Skills that help

- `/test-ship` - full audit + fix + verify pipeline. Run after a coverage gap is discovered, NOT as a substitute for writing tests-with-code.
- `/qatest` - full QA sweep including E2E + a11y + perf. Run before launches, not as default per-PR motion.
- `/smoketest` - quick sanity check after a deploy. Useful but not a stand-in for unit tests.
