# /repo-bootstrap - report, SITREP

## Report

`.bootstrap-reports/BOOT-<YYYYMMDD-HHMM>.md`.

```markdown
# Bootstrap Report: <repo>
**Stack:** <detected>  |  **Mode:** <full | audit | ci | tests | hooks>

## Baseline status
| Element | Before | Action | Verified |
| test framework | absent | added Vitest + smoke test | `vitest run` passes |
| CI gate | absent | added, required-check configured | would trigger + pass |
| .gitignore | partial | added .env*, report dirs | |
| CHANGELOG | absent | scaffolded (Keep a Changelog) | |
| pre-commit hooks | absent | husky + lint-staged | fires on commit |
| cost config | absent | path filters + ignoredBuildStep | |

## Operator actions required
- Enable branch protection on `main` with the `gate` check required (plan-gated; skill cannot set it)

## Applied in commits
- <sha> chore: add test framework + smoke test
- <sha> ci: add merge-gating workflow
- ...
```

## SITREP

The before/after baseline table - what the repo had, what it has now. Then, prominently, the
**operator actions required** - branch protection is the one thing the skill configures the check for
but cannot itself enable, and a repo that thinks it is protected but is not is a real gap. Then the
commit list.

### Suggested next

| Outcome | Recommend |
|---|---|
| Baseline applied | enable branch protection, then `/gh-ship` the setup commits |
| Repo has code but no tests | `/test-ship --setup` filled the framework; now add real coverage |
| Monorepo | confirm the cost config with a test PR that touches one package |
| CLAUDE.md missing | `/init` to generate one (this skill installs machinery, not docs) |

## Design notes

**Detect and diff, never clobber.** The rule that makes this safe to run on an existing repo, not just
a fresh one. It adds the gap and leaves what works alone.

**A gate that gates.** A CI workflow that runs but does not block a merge is theatre. The baseline is
a required check - and the skill is honest that enabling branch protection is the operator's step, so
the repo is not left thinking it is protected when it is not.

**Verify each piece.** Files present is not configured working. A workflow referencing a missing
script, a hook that never fires, a test framework with no runnable test - each looks done and is not.
Stage 3 runs each.

**Distinct from /init.** `/init` writes a CLAUDE.md from analysis; this installs CI, tests, hooks and
cost config. Run both on a new repo - they do not overlap.
