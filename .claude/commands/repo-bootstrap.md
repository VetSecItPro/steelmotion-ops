# /repo-bootstrap — Apply Project Standards to a Fresh Repo

> **Standards inherited** (apply throughout this skill):
> - [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) — read + reason, don't pattern-match
> - [Self-Improvement Protocol](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) — log to `.repo-bootstrap-history.json`, learn across runs
> - [Multi-Repo Awareness](~/.claude/standards/MULTI_REPO_AWARENESS.md) — never modify siblings; this skill operates on cwd only
> - [Verify Before Destroy](~/.claude/standards/VERIFY_BEFORE_DESTROY.md) — content-verify before destructive action
> - [Skill Auto-Suggest Protocol](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) — every SITREP ends with "Suggested next"

**Take a fresh git repo and apply the operator's project-standard baseline. Tests-with-code, CHANGELOG, CI, branch protection, gitignore patterns, conventional commit hooks — set up once, automatically.**

## PARADIGM

Every new repo Anouar creates needs the same baseline: vitest/pytest framework + smoke test, CI workflow that gates merges, CHANGELOG.md, branch protection, conventional commit + co-authored-by trailer, project-specific `.gitignore` patterns from `~/CLAUDE.md` § Live Document Protocol, optional Vercel `vercel.json` if it's a deploy target.

Doing this manually drifts: one repo gets `bats` but no CI, another gets CI but no CHANGELOG, a third has a `vercel.json` with the wrong team scope. `/repo-bootstrap` enforces the baseline so the operator stops re-deciding the same setup details every time.

This skill is read-and-reason: detect what's already there, don't clobber, only add what's missing.

---

## DISCIPLINE

> Reference: [Superpowers Discipline Protocol](~/.claude/standards/STEEL_DISCIPLINE.md)

Steel principles applied:

- **#1 (verification before claim):** "CI is configured" requires the workflow YAML actually triggers (push to feature branches at minimum) — verify by reading the trigger block
- **#3 (TDD scaffolding):** the smoke test added by bootstrap exists to fail when the framework is broken; verify it FAILS as expected on a stripped framework, not just passes on the happy path
- **#5 (no placeholders):** every config file written is complete and valid — no `# TODO: fill in deploy URL` lines

### Rationalization defense

| Rationalization | Reality | Do |
|---|---|---|
| "Repo already has package.json, must be set up" | A package.json is the START of bootstrap, not the end | Run the full audit; only skip what's verifiably correct |
| "User can add CI later" | "Later" is "never"; coverage gaps compound from day 1 | Add CI at bootstrap; the cost is 30 seconds |
| "Skip CHANGELOG, this repo is internal-only" | Internal repos pin to versions too (per MC-vs-OpenClaw model) | Always create CHANGELOG.md; mark internal-only in the body |
| "Branch protection is overkill for a side-project" | Operator force-pushes happen in the early-momentum phase | Configure light protection (require PR, no required reviews) |

---

## CRITICAL RULES

1. **NEVER overwrite existing files.** If `.gitignore` exists, AUGMENT it (only append patterns not already present). Same for CI YAML, CHANGELOG, vercel.json.
2. **DETECT framework, don't assume.** package.json + Next signals one stack; pyproject.toml + FastAPI signals another; bats in `tests/bash/` signals an infra repo. Behavior changes per detected stack.
3. **Apply the operator's `~/CLAUDE.md` defaults.** All scaffolding aligns to the global CLAUDE.md (Tests Ship With Code table, Co-Authored-By trailer, VetSecItPro namespace).
4. **Operator-confirm only for the irreversible.** Branch protection requires GitHub API calls; ask before applying. File scaffolding is reversible (one git revert) — just do it.
5. **Idempotent.** Running this twice in a row produces zero diffs the second time. If something changed between runs, surface why.
6. **Multi-language aware.** A polyglot repo (TypeScript frontend + Python backend) gets BOTH test setups, not one.
7. **History-driven.** Read `.repo-bootstrap-history.json` for prior runs; surface any drift since last run.
8. **SITREP ends with Suggested next.**

---

## MODES

```
/repo-bootstrap                       # Full audit + apply missing baseline
/repo-bootstrap --audit               # Read-only — what would be added/modified
/repo-bootstrap --apply               # Apply changes (default behavior)
/repo-bootstrap --branch-protection   # Configure GitHub branch protection (requires confirmation)
/repo-bootstrap --vercel              # Add vercel.json with VetSecItPro team scope
/repo-bootstrap --skip-ci             # Skip CI workflow generation
/repo-bootstrap --polyglot            # Force polyglot detection (multi-language scaffolding)
```

---

## DETECTION

### Stack detection (read filesystem signals)

| Signal | Stack |
|---|---|
| `package.json` + Next.js dep | Next.js + TypeScript |
| `package.json` + no framework | Node CLI/library |
| `pyproject.toml` / `setup.py` | Python |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `tests/bash/` or `*.bats` | Bash/infra |
| Polyglot (multiple of above) | flag for double-bootstrap |
| None of the above | empty repo — interactive: ask what's coming |

### Existing-asset detection

For each baseline component, check whether it already exists:

| Component | Detection | Action if exists |
|---|---|---|
| `.gitignore` | file present | augment with missing patterns |
| Test framework | `vitest` / `pytest` / `bats` in deps | confirm config + smoke test |
| CI workflow | `.github/workflows/ci.yml` | inspect for completeness; flag gaps |
| CHANGELOG | `CHANGELOG.md` or `<PREFIX>-CHANGELOG.md` | leave; verify Keep-A-Changelog format |
| README | `README.md` | leave |
| LICENSE | `LICENSE` / `LICENSE.md` | leave |
| Vercel config | `vercel.json` | verify VetSecItPro team scope |
| Branch protection | `gh api repos/<owner>/<repo>/branches/main/protection` | leave or recommend |

---

## STAGES

### Stage 0: Pre-flight

Read `.repo-bootstrap-history.json`. Capture:
- Last run's stack detection
- Components added vs deferred
- Any operator overrides (e.g. "don't add Vercel config")

Detect:
- `STACK[]` (could be multiple for polyglot)
- `EXISTING_ASSETS[]`
- `MISSING_COMPONENTS[]`

### Stage 1: gitignore augmentation

Required patterns from operator's `~/CLAUDE.md` § Live Document Protocol:
```
*-plan.md
*-research.md
*-enhance*.md
*-todo.md
*-strategy.md
*-backlog.md
LESSONS-LEARNED.md
.test-reports/
.security-reports/
.monitor-reports/
.cron-audit-reports/
.secrets-audit-reports/
.gh-ship-history.json
.sec-ship-history.json
.test-ship-history.json
node_modules/
.next/
.vercel/
.DS_Store
.env
.env.*
!.env.example
```

Plus stack-specific:
- Python: `__pycache__/`, `*.pyc`, `.venv/`, `*.egg-info/`
- Rust: `target/`
- Go: `vendor/` (if vendoring), `*.test`
- Bash: nothing additional

Read existing `.gitignore`; only append patterns not already matched.

### Stage 2: Test framework + smoke test

Per `~/CLAUDE.md` § Tests Ship With Code, the framework chosen is:

| Stack | Framework | Smoke test |
|---|---|---|
| Next.js + TS | vitest + Playwright | `tests/smoke.test.ts` asserts `1+1===2` AND `import { foo } from '@/lib/foo'` resolves |
| Python | pytest | `tests/python/test_smoke.py` asserts framework loads + a fixture works |
| Rust | built-in `#[test]` | smoke in `tests/smoke.rs` |
| Go | built-in `go test` | smoke in `internal/smoke_test.go` |
| Bash/infra | bats | `tests/bash/smoke.bats` asserts bats itself works |

Add scripts:
- `npm test` / `pytest` / `cargo test` / `go test ./...` / `bats tests/bash/`

If framework already present, verify the smoke test exists; create if missing.

### Stage 3: CI workflow

`.github/workflows/ci.yml` template (operator's standard chain):

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4  # pinned by major; bot updates patch version
      - <stack-specific setup>
      - run: <stack-specific install>
      - run: <stack-specific test>
      - run: <stack-specific build, if applicable>
```

Stack-specific blocks plug in. Ensure: timeout, concurrency cancel, least permissions, pinned actions per CI_VERCEL_COST_OPTIMIZATION standard.

### Stage 4: CHANGELOG.md

Bootstrap a Keep-A-Changelog skeleton:

```markdown
# Changelog

All notable changes to this repo are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

(Pending changes go here. Move to a versioned section on release.)
```

If repo is part of a multi-CHANGELOG family (e.g. Command Post style), use `<PREFIX>-CHANGELOG.md` and ask the operator for the prefix.

### Stage 5: README scaffold (only if absent)

Minimal README:
- Project name + one-line purpose
- Quick start (install, test, run)
- Link to CHANGELOG
- License section

Do not over-write an existing README.

### Stage 6: Vercel config (only if `--vercel` or detected)

`vercel.json` with VetSecItPro team scope and minimal-correct config. Includes `ignoredBuildStep` per CI_VERCEL_COST_OPTIMIZATION standard if monorepo.

### Stage 7: Branch protection (only if `--branch-protection`)

Use `gh api -X PUT repos/<owner>/<repo>/branches/main/protection` with conservative settings:
- Require PR before merge: yes
- Required reviews: 0 (operator solo, but PR gate stays)
- Required status checks: CI workflow (if present)
- Allow force-push: no
- Allow deletion: no

Confirm with operator before applying — branch protection changes are repo-visible to collaborators.

### Stage 8: Conventional commit hook (optional)

If `~/.gitconfig` doesn't already have a global hooks dir, skip. If it does, add a commit-msg hook that:
- Validates conventional commit prefix (feat/fix/chore/refactor/docs/test/style/perf)
- Auto-adds Co-Authored-By trailer when triggered by Claude Code

### Stage 9: SITREP + history append

Write report to `.repo-bootstrap-reports/RB-YYYYMMDD-HHMMSS.md`. Append run to `.repo-bootstrap-history.json`.

---

## SITREP TEMPLATE

```
═══════════════════════════════════════════════════════════════════════════════
                       SITREP — /repo-bootstrap
═══════════════════════════════════════════════════════════════════════════════
Run ID:     RB-20260503-180522
Repo:       /Users/airborneshellback/vibecode-projects/new-thing
Stack:      Next.js + TypeScript
Duration:   38s

────────────────────────────────────────────────────────────────────────────────
 BASELINE STATE
────────────────────────────────────────────────────────────────────────────────
✅ git remote     origin → VetSecItPro/new-thing
✅ .gitignore     present, 8 patterns added
✅ test framework vitest + Playwright (added 22 deps, 1 smoke test)
✅ CI workflow    .github/workflows/ci.yml created
✅ CHANGELOG      created (Keep-A-Changelog format)
⚠️ README        already present, left untouched
⚠️ vercel.json   not added (use --vercel to enable)
⚠️ branch protect not configured (use --branch-protection to enable)

────────────────────────────────────────────────────────────────────────────────
 NEXT MOVES (operator-driven)
────────────────────────────────────────────────────────────────────────────────
- Write your first feature, then run /test-ship to verify framework
- Configure branch protection: /repo-bootstrap --branch-protection
- If deploying to Vercel: /repo-bootstrap --vercel

═══════════════════════════════════════════════════════════════════════════════
```

---

## Suggested next

Per [Skill Auto-Suggest Protocol](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md):

| Outcome | Recommended | Why |
|---|---|---|
| Bootstrap complete, smoke test green | /test-ship | verify the framework actually catches issues |
| Bootstrap complete, ready to commit | /gh-ship | first commit through the standard flow |
| Branch protection still pending | /repo-bootstrap --branch-protection | finish the lockdown |
| Vercel deployment intended | /repo-bootstrap --vercel | scoped to VetSecItPro team |
| Existing CI looked broken | /investigate the workflow | root-cause before bootstrap-fix |

**Skip if:** the repo was already fully bootstrapped (zero diff this run).

---

## DESIGN DECISIONS (WHY)

### Why a separate skill, not a stage of /gh-ship
Bootstrap is a **first-time** action. /gh-ship runs N+1 times per repo. Coupling them would make the first run weirdly different and the next 100 runs need a "skip bootstrap" branch. Cleaner to separate.

### Why never overwrite existing files
The operator may have made deliberate deviations (e.g. Python repo with custom test runner). Overwriting destroys those decisions. Augment-only ensures bootstrap is purely additive.

### Why branch protection is gated behind a flag
It's the only stage that has external visibility (collaborators see the protection). Auto-applying it could surprise someone working on the same repo. Manual flag = explicit operator choice.

### Why polyglot detection
Real-world repos go polyglot (Next.js frontend + Python data backend). Single-stack assumption produces incomplete bootstrap. Detection scans all signals; flag controls whether to scaffold both.

### Why no .env.example auto-generation
Operator's secrets vary per repo; auto-generating placeholders creates drift between the example and what's actually needed. Better to leave .env.example for the operator to write as part of writing the first feature that needs an env var.

---

## DEFINITION OF DONE

- Stack(s) detected
- Each baseline component is either: VERIFIED-CORRECT, ADDED, or DEFERRED-WITH-FLAG
- Smoke test runs locally and passes
- CI workflow has a trigger block that fires on PR
- `.repo-bootstrap-history.json` updated
- SITREP ends with "Suggested next"
- Idempotency: re-run produces zero file diffs
