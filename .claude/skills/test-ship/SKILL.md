---
name: test-ship
description: "Test coverage audit, gap-fill and verification: find what business logic is untested, write real tests for it (not smoke tests), run the full suite, and ship coverage that catches regressions. Detects the test framework in use; sets one up if none exists. Enacts the Tests-Ship-With-Code rule after the fact."
when_to_use: 'Trigger phrases: "test coverage", "add tests", "TDD", "missing tests", "write tests", "is this tested", "coverage gap". Run after a coverage gap is discovered - not as a substitute for writing tests alongside the code they cover.'
---

# /test-ship - test coverage audit and gap-fill

**Spine. Survives compaction.** Detail beside it:

| File | Read at | Holds |
|---|---|---|
| `frameworks.md` | Phase 0 | test-runner detection per stack; scaffolding a suite where none exists |
| `phases.md` | throughout | audit, prioritise, write, verify, self-heal |
| `reference.md` | report | report format, SITREP, coverage-delta reporting |

**Standards inherited:** [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) ·
[Steel Discipline](~/.claude/standards/STEEL_DISCIPLINE.md) ·
[Self-Improvement](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) ·
[Agent Orchestration](~/.claude/standards/AGENT_ORCHESTRATION.md) ·
[Status Updates](~/.claude/standards/STATUS_UPDATES.md) ·
[Skill Auto-Suggest](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) ·
[Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md) ·
[Context Management](~/.claude/standards/CONTEXT_MANAGEMENT.md) ·
[Multi-Repo Awareness](~/.claude/standards/MULTI_REPO_AWARENESS.md) ·
[SITREP Format](~/.claude/standards/SITREP_FORMAT.md) ·
[Verify Before Destroy](~/.claude/standards/VERIFY_BEFORE_DESTROY.md)

## What this skill is and is not

The standing rule is **Tests Ship With Code** - a PR that adds business logic adds its tests in the
same PR. This skill is the *remediation* when that did not happen: it finds and closes an existing
gap. It is **not** a substitute for writing tests alongside the code, and running it must never become
the reason to skip tests during development.

## Critical rules

1. **A smoke test is not a test.** A test that only asserts "it renders" or "returns 200" catches
   almost nothing. Test behaviour: the happy path, the error path, the boundary, the edge case.
2. **Test the seam that fails silently first.** Auth and middleware gates, then API handlers, then
   pure logic in `lib/`, then templates, then a few critical-path E2E. That order is by
   silent-failure risk, not by ease.
3. **A test that cannot fail is worthless.** Every test must be able to go red. Write it, watch it
   fail against the un-fixed code or a deliberately broken assertion, then make it pass. A test that
   passes against broken code is testing nothing.
4. **Mock at the boundary, not the framework.** Mock the third-party SDK (Resend, Stripe, the AI
   client), not your own router. Mocking your own code tests the mock.
5. **The full suite must stay green.** A new test that passes while breaking three others is a net
   loss. Run everything after each addition.
6. **Coverage percentage is a guide, not a goal.** 100% line coverage of trivial getters is worth
   less than 60% that covers every auth path. Report what is covered, not just how much.
7. **Untestable code is a design signal.** If something cannot be tested without heroics, it is too
   coupled. Note it; recommend the refactor; do not contort a test around bad structure.

## Modes

```
/test-ship               audit coverage, fill the highest-risk gaps, verify
/test-ship --audit       report the gaps only, write nothing
/test-ship --setup       scaffold a test framework + CI gate + one smoke test (no suite exists)
/test-ship --unit        unit + integration gaps only
/test-ship --e2e         critical-path end-to-end only
/test-ship --file <path> cover one file thoroughly
```

## Phases

| # | Phase | Must not be skipped |
|---|---|---|
| 0 | Detect | test runner, existing coverage, CI gate. If no framework: `--setup` first |
| 1 | Audit | what business logic is untested, ranked by silent-failure risk |
| 2 | Prioritise | the seam order above; the operator's critical paths first |
| 3 | Write | real tests - happy, error, boundary. Each proven able to fail |
| 4 | Verify | full suite green; the new tests actually exercise the target |
| 5 | Report | coverage delta, what was covered, what remains and why |

Phases 3-5 are what a long run loses to compaction if not held here. **Phase 3's "proven able to
fail" step is what separates real tests from green decoration.**

## Setting up a suite where none exists

The first PR in a test-less codebase adds: the framework (vitest/pytest/bats matched to the language),
a `test` script alias, a CI job that gates merges, and one smoke test proving the pipeline runs. Every
subsequent PR adds real tests. Do not attempt to cover the whole codebase in the setup PR - establish
the machinery, then fill gaps by risk.

## Definition of done

- Every gap found is either covered or listed with why it was deferred
- New tests cover behaviour (happy + error + boundary), not just existence
- Each new test proven able to fail
- Full suite green; coverage delta reported (e.g. "+22 tests, suite 1088 -> 1110")
- Untestable code flagged with a refactor recommendation, not worked around
- Report written; SITREP ends with "Suggested next"
