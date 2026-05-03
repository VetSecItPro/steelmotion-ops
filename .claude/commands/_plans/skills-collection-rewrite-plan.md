# Skills Collection — Rewrite & Optimization Plan

**Created**: 2026-05-03 (end of long /gh-ship session)
**Purpose**: Self-contained spec a fresh session can execute cold to (a) properly rewrite `/gh-ship`, (b) generalize the lessons to audit the rest of the skills collection.
**Repo**: `VetSecItPro/steelmotion-ops` (renamed from `claw-ops` 2026-05-03)
**Local clone**: `~/vibecode-projects/claude-code-skills/`
**Skill files**: `~/.claude/commands/<skill>.md` — these are the actual source-of-truth (the upstream repo packages these).

---

## Why this plan exists

Today's session ran `/gh-ship` repeatedly across 3 repos and found multiple structural issues:

1. **Squash-merge false-negative**: `git merge-base --is-ancestor` returns false on squash-merged work; naive cleanup either left stale branches or force-deleted unmerged work.
2. **Pre-existing WIP destruction**: Skill assumed all branches without PRs were stale; in fact some were the operator's WIP.
3. **Regex-based fix table**: `if grep "eslint" then $LINTER_FIX` patterns missed real-world cases (ruff E401 in nolan-infra, flaky test that was a real bug).
4. **GHCR 403 not in fix table**: Required manual UI step, no skill knew to surface that.
5. **Multi-repo blindness**: Workspace has 3 sibling repos; skill operated on cwd only and gave no signal about the others.
6. **Silent CI mismatches**: Deploy chain broken for 4 days because no end-to-end verification of "does PR-merged content actually reach prod."
7. **No self-improvement**: Same patterns of failure recur across runs because nothing is logged or learned.
8. **Static workflow assumption**: Assumes Vercel; no graceful path for self-hosted poll-cron deploys (which we just built).

User direct asks (verbatim, this session):
- "we're using AI, not dumb regex right? or adapt it to be comprehensive and self-improving and self-healing"
- "make this skill comprehensive for all github work on whatever repo or repos it's targeting"
- "let's not restrict this skill to what's only there. we can tell it to also check for other stuff that it might find but we didn't think to specify"
- "improve the ci workflow or whatever on github as needed if stuff is not optimal"
- "we will audit the other skills too to optimize them too since we're optimizing this one"

---

## Phase 1 — Rewrite `/gh-ship`

### Foundational paradigm shift

Move from **"bash script with regex-based fix tables"** → **"AI judgment engine with bash examples and self-improvement memory."**

Concretely:
- Every "if X happens, do Y" pattern becomes "read the actual situation, reason, decide."
- The skill is a *planning document for Claude to execute*, not a script Claude executes.
- bash blocks are illustrative examples; the actual decision tree is Claude's reasoning.

### Required new capabilities

| # | Capability | Status today |
|---|---|---|
| 1.1 | Detect repo type from filesystem (Node/Python/Go/Rust/bash/docs-only) | Partial (Node-biased) |
| 1.2 | Detect linter/formatter/test-runner/CI-engine, not assume Vercel | Partial |
| 1.3 | Detect deploy mechanism: Vercel/Netlify/Fly/CF/self-hosted-poll-cron/none | Vercel-only assumption |
| 1.4 | Multi-repo workspace awareness — operate on cwd, report siblings | Missing |
| 1.5 | Squash-merge-safe cleanup (content equivalence, not ancestry) | Patched 2026-05-03 (Stage 11.5) |
| 1.6 | WIP-branch protection (only delete what THIS run created) | Patched 2026-05-03 (Stage 11.5) |
| 1.7 | AI-judgment CI fix (read log, reason, fix; not regex-table) | Patched 2026-05-03 (Stage 9.2 table replaced) |
| 1.8 | Proactive audit: scan for issues we DIDN'T tell it to look for | Missing — KEY ADD |
| 1.9 | CI workflow improvement: detect suboptimal `.github/workflows/*.yml` and propose/apply upgrades | Missing — KEY ADD |
| 1.10 | Self-healing recovery patterns (reflog-aware deletes, force-push-with-lease, etc.) | Mentioned, not codified |
| 1.11 | Self-improvement log at `.gh-ship-history.json` per repo | Mentioned, not implemented |
| 1.12 | Cross-run learning: read prior run's history to skip known-bad approaches | Missing |
| 1.13 | Container registry awareness (GHCR ACL gotcha, ECR auth, etc.) | Missing |
| 1.14 | Auth-rotation detection: if token expired, surface exactly which one | Missing |
| 1.15 | Verify deployment AT THE ACTUAL URL with HTTP 200 + content check | Stated, not always enforced |

### Stages structure (target — keeping numbers user already knows)

```
Stage 0: Pre-flight + read .gh-ship-history.json
Stage 0.5: Multi-repo scan (sibling state report)
Stage 1: Local validation (lint, typecheck, build) — language-adaptive
Stage 2: Analyze diff
Stage 3: Generate commit message (semantic, body explaining WHY)
Stage 4: Stage & commit
Stage 5: Branch management (track session-created in SESSION_BRANCHES_CREATED)
Stage 6: Push (with rebase + force-with-lease if diverged)
Stage 7: Open PR (template-aware, links to relevant issues)
Stage 8: Wait for CI + Vercel preview (or self-hosted equivalent)
Stage 9: AI-judgment CI fix loop (max 3, log to history regardless of outcome)
Stage 10: Merge (REST fallback for GraphQL rate limit; never --no-verify; never force-push main)
Stage 11: Verify production deployment (curl actual URL, expect 200 + expected content)
Stage 11.5: Verified-merge detection (squash-safe, content-grep based)  [PATCHED 2026-05-03]
Stage 11.7: Proactive audit (NEW)
   - Scan for stale workflow files (deprecated actions, missing permissions)
   - Scan for missing branch protection
   - Scan for missing CI on critical paths
   - Scan for orphan PRs from prior runs
   - Scan for over-broad ignores or secrets in tracked files
   - Propose fixes; apply IF non-controversial, surface for review IF judgment-call
Stage 12: Cleanup (only branches THIS run created; pre-existing WIP inspected, not deleted)
Stage 12.5: CI workflow improvement (NEW)
   - If detected workflows have known anti-patterns:
     * unpinned action versions
     * missing concurrency groups
     * missing path filters causing wasted runs
     * missing permissions: block (over-permissioned token)
     * missing timeout-minutes
   - Propose update PR (separate from the just-merged work) — DO NOT auto-merge; surface
Stage 13: Append run to .gh-ship-history.json
Stage 14: SITREP with sibling-repo summary
```

### Self-improvement log schema

Path: `.gh-ship-history.json` at repo root, gitignored.

```json
{
  "schema_version": 1,
  "runs": [
    {
      "run_id": "2026-05-03T17:32:00Z",
      "repo": "VetSecItPro/mission-control",
      "duration_seconds": 154,
      "session_branches_created": ["mc/foo"],
      "stages_reached": [...],
      "ci_failures_encountered": [
        {
          "stage": "9",
          "shape": "ruff-E401-multiple-imports-on-one-line",
          "log_excerpt": "...",
          "fix_applied": "split imports into separate lines",
          "succeeded": true
        }
      ],
      "anomalies": [
        {"category": "pre-existing-wip-protected", "branches": ["feature/foo"]},
        {"category": "remote-stale", "remotes": ["origin/fix/bar"], "action": "left-alone-pre-existing"}
      ],
      "outcome": "success",
      "lessons_added_to_skill": false
    }
  ],
  "patterns_observed": {
    "ruff-E401": {"first_seen": "2026-05-03", "count": 3, "fix_known": true},
    "ghcr-403-on-package-acl": {"first_seen": "2026-05-03", "count": 1, "fix_known": true, "manual_step_required": true}
  }
}
```

Stage 0 reads `patterns_observed` to prefer known-good fixes. After every CI failure, Stage 9 appends to both arrays. Periodically (every N runs?) the skill could prompt: "I've seen pattern X 5 times, want me to harden against it?"

### Proactive audit (Stage 11.7) — what to look for

Beyond what the user explicitly asked:

- **`.github/workflows/*.yml` audits**:
  - Action versions pinned to SHA (not just tag)?
  - `permissions:` block present and minimal?
  - `timeout-minutes:` set?
  - `concurrency:` group set for deploy workflows?
  - `paths:` filter on push triggers to skip irrelevant runs?
  - Secrets used directly (`secrets.X`) vs via OIDC?
- **Branch protection** on main (probe via `gh api`):
  - Required status checks?
  - Linear history?
  - Force-push allowed? (should be off)
- **Repo settings**:
  - Auto-delete-head-branches enabled? (prevents the stale-remote class of bug we hit)
  - Allow squash merge / rebase merge / merge commit settings sensible?
- **Package registry health** (if image build present):
  - GHCR package's "Manage Actions Access" includes the workflow's repo?
  - Versions accumulating untagged? (cleanup candidate)
- **Repo file health**:
  - `.gitignore` covers common bad things (`.env*`, `*.log`, `dist/`, `node_modules/`)
  - `LICENSE` present?
  - `README` not stale (last updated > 6 months ago + recent commits)?
  - `package-lock.json` / equivalent committed?
- **Open PRs / issues**:
  - Stale PRs (no activity > 30 days)? Surface for triage.
  - Orphan branches (no PR, > 7 days old)? Surface for cleanup.
- **CI runs trend**:
  - Failure rate over last 20 runs > 30%? Flag the pattern.
  - Average run time creeping up? Surface.

### CI workflow improvement (Stage 12.5)

If the skill identifies a fixable workflow anti-pattern:

1. Create a separate branch `chore/ci-improvement-<short-desc>`
2. Apply the change with WHY comment in the YAML
3. Open PR with explanation
4. Do NOT auto-merge — operator reviews

Examples of changes the skill should be empowered to make:
- Replace unpinned action `actions/checkout@v4` with `actions/checkout@<full-sha> # v4.x`
- Add `permissions: { contents: read }` block to workflows missing it
- Add `concurrency: { group: ${{ github.workflow }}-${{ github.ref }}, cancel-in-progress: true }` to long-running CI
- Add `timeout-minutes: 15` to jobs missing it
- Add path filters to deploy workflows to skip pure-doc PRs

### What NOT to do (anti-patterns to encode)

- Don't pattern-match error strings; READ THE LOG and reason
- Don't assume Node/Vercel/jest; detect
- Don't auto-delete branches without verification AND session-ownership check
- Don't fix CI failures by suppressing tests or `--no-verify`
- Don't open chained PRs without explaining the dependency
- Don't propose CI changes that break the existing pipeline; only propose strict improvements
- Don't write to `.gh-ship-history.json` without verifying the run's classification (success/partial/failed) is actually correct

### Implementation approach

**Recommended**: rewrite `~/.claude/commands/gh-ship.md` from scratch as ~600 lines (current is 1300+).

Structure:
1. **Header**: skill purpose + paradigm + critical rules + AI-driven execution model (~80 lines)
2. **Stage 0**: pre-flight + history read (~50 lines)
3. **Stage 0.5**: multi-repo scan (~30 lines)
4. **Stages 1-12**: core ship pipeline with reasoning prompts (~300 lines)
5. **Stage 11.7**: proactive audit (~50 lines)
6. **Stage 12.5**: CI workflow improvement (~50 lines)
7. **Stage 13**: history append (~20 lines)
8. **Stage 14**: SITREP (~30 lines)
9. **Reusable patterns**: post_merge_verify, verify_branch_merged, etc. (~50 lines)

Drop:
- Vercel-specific verbosity (replace with generic "deploy mechanism" detection)
- Repeated bash code blocks that are now Claude-judgment
- Network-resilience boilerplate (Claude knows to retry network ops)

---

## Phase 2 — Audit framework for other skills

After /gh-ship is rewritten, generalize the patterns and audit each other skill for the same anti-patterns.

### Skills inventory (from system reminder this session)

```
update-config     keybindings-help   simplify         fewer-permission-prompts
loop              schedule           claude-api       newsletter
redteam           qatest             icp-from-repo    ops
campaign          mdmp               harden           launch
content           test-ship          subagent-dev     compliance-docs
investigate       migrate            gtm              scrape
blog              dev                ship             quality
a11y              write-skill        marketing        monitor
social            compliance         critique-adversarial  browse
perf              prospect           sec-ship         sec-weekly-scan
deps              intel              plan             db
copy              fortress           design           docs
outreach          hunt               cleancode        narrative
incident          smoketest          gh-ship          brainstorm
init              review             security-review
```

~58 skills total. Not all need rewrites — only the most-used + the most-bash-heavy.

### Audit checklist (apply to each skill)

For each skill `~/.claude/commands/X.md`:

| Check | Why it matters |
|---|---|
| Uses regex/grep error matching where AI judgment fits better? | The /gh-ship lesson — reasoning beats pattern-matching |
| Assumes specific tooling (Vercel, jest, npm)? | Should detect or graceful fallback |
| Multi-repo aware (when applicable)? | /sec-ship, /test-ship, /quality, /ship probably need this |
| Has self-improvement memory file? | All long-running skills should |
| Self-healing on partial failures? | Especially destructive skills (/cleancode, /db, /migrate) |
| Pre-flight reads operator-level docs (CLAUDE.md)? | Already done in some, missing in others |
| Generates plain-text SITREP? | Most do, but format consistency varies |
| Honest scope (refuses to do things outside its competence)? | Some skills overreach |
| Logs to `.X-reports/` correctly + gitignored? | Most do |
| Idempotent re-run? | /db migrations especially |

### Priority ranking for rewrites (Phase 2)

Tier 1 (used often + high blast radius — highest value to harden):
1. `/sec-ship` — same patterns; adds: vuln-class taxonomy that learns
2. `/test-ship` — same patterns; adds: flaky-test protection
3. `/qatest` — exploration-heavy; adds: smarter coverage of new pages
4. `/ship` — meta-skill that calls /test-ship + /sec-ship + /gh-ship; needs to inherit patterns
5. `/monitor` — reads the world; needs to be smarter about what's actually broken

Tier 2 (used periodically, mid-blast-radius):
- `/cleancode`, `/deps`, `/perf`, `/a11y`, `/migrate`, `/db`, `/incident`, `/investigate`

Tier 3 (content/marketing — different family, separate audit pass):
- `/blog`, `/copy`, `/content`, `/social`, `/marketing`, `/narrative`, `/hunt`, `/prospect`, `/icp-from-repo`, `/campaign`, `/gtm`, `/outreach`

Tier 4 (single-purpose, less likely to need rewrite):
- `/dev`, `/init`, `/review`, `/security-review`, `/loop`, `/schedule`, `/smoketest`, `/keybindings-help`, `/update-config`, `/fewer-permission-prompts`

### Phase 2 deliverables

1. **`SKILL_AUDIT_RUBRIC.md`** at `~/.claude/commands/_plans/` — formalize the audit checklist above into a reusable spec.
2. **One PR per Tier-1 skill** in `steelmotion-ops` repo, each with: rewritten skill + audit-rubric reference + before/after metrics (line count, regex-pattern count, etc.)
3. **A meta-skill `/audit-skill`** that runs the rubric automatically against any skill in the collection.

---

## Phase 3 — Propagate to upstream repo

The local `~/.claude/commands/` is the working copy. Open-source `steelmotion-ops` is the published version. Once Phase 1 + Phase 2 ship, propagate.

### Steps

1. Pull latest steelmotion-ops to `~/vibecode-projects/claude-code-skills/`
2. Identify which skills are in the published repo vs local-only
3. For each rewritten skill, copy `~/.claude/commands/<skill>.md` → repo path
4. Open one PR per skill (or batch if logical) on `steelmotion-ops`
5. Tag a release: `v2.x` reflecting the rewrite
6. Update README to mention the AI-judgment paradigm + self-improvement log

---

## Execution time estimate (honest)

- Phase 1 (gh-ship rewrite): 4-6 hours of focused work, fresh session
- Phase 2 (Tier 1 — 5 skills): 8-12 hours, can be split across sessions
- Phase 2 (Tier 2 — 8 skills): 8-12 hours, lower urgency
- Phase 3 (publish): 2-3 hours

**Total scope: 22-33 hours of focused work.** Best done in dedicated half-day blocks, not end-of-session squeeze.

---

## How a fresh session executes this plan

### Session 1 (gh-ship rewrite, 4-6h)

1. Read this plan top to bottom
2. Read existing `~/.claude/commands/gh-ship.md` end to end
3. Draft new structure (Stages 0-14) in a scratch file
4. Implement stage-by-stage; test each by running `/gh-ship` on a small change
5. Implement `.gh-ship-history.json` schema + Stage 0 read + Stage 13 append
6. Cross-check against the "Required new capabilities" table — every row must be addressed
7. Final pass: read for tone consistency + bash-block pruning
8. Commit to `~/vibecode-projects/claude-code-skills/`, open PR, merge

### Session 2 (audit rubric + 1 Tier-1 skill, 4-6h)

1. Write `SKILL_AUDIT_RUBRIC.md`
2. Run rubric against highest-priority skill (likely `/sec-ship`)
3. Rewrite `/sec-ship` per rubric findings
4. Ship via /gh-ship (now using the rewritten version)

### Subsequent sessions

Continue Tier-1, then Tier-2. Tier-3 (content) is a separate audit pass with different criteria.

---

## Acceptance criteria (Phase 1 done)

- [ ] `~/.claude/commands/gh-ship.md` is < 700 lines (down from 1300+)
- [ ] Zero regex-based error tables; all CI fix logic is AI-judgment with examples
- [ ] Multi-repo workspace scan implemented (Stage 0.5 + Stage 14 SITREP includes siblings)
- [ ] Squash-merge-safe cleanup verified by inducing test case
- [ ] WIP protection verified by inducing test case (pre-existing branch with no PR — should NOT be deleted)
- [ ] Proactive audit (Stage 11.7) implemented with at least 5 distinct check categories
- [ ] CI workflow improvement (Stage 12.5) implemented; produces PR for review (not auto-merge)
- [ ] `.gh-ship-history.json` schema created + read at Stage 0 + appended at Stage 13
- [ ] At least one repo's history shows successful "learn from past run" behavior (Stage 9 used a known-good fix from history)
- [ ] SITREP includes sibling-repo state when in workspace
- [ ] Skill documented at top with WHY of every major design decision

## Acceptance criteria (Phase 2 done)

- [ ] `SKILL_AUDIT_RUBRIC.md` published
- [ ] All 5 Tier-1 skills rewritten + tested
- [ ] Audit reports filed for Tier-2 skills (rewrites optional)
- [ ] `/audit-skill` meta-skill ships

## Acceptance criteria (Phase 3 done)

- [ ] All rewritten skills propagated to `steelmotion-ops` repo
- [ ] README updated
- [ ] Tagged release shipped
