# /gh-ship — AI-Judgment Git Pipeline

**Commit → Push → PR → CI → Fix → Merge → Deploy → Verify → Cleanup → Audit → Improve.**

Comprehensive shipping pipeline for ANY repo type. Adapts to the language/tools/CI/deploy mechanism it finds. Self-healing on partial failures. Self-improving via per-repo history. Multi-repo aware. Treats unknown situations as reasoning problems, not pattern-match misses.

Spec: `~/.claude/commands/_plans/skills-collection-rewrite-plan.md` (Phase 1 acceptance criteria there).

---

## PARADIGM: AI-judgment, not pattern-match

This skill is **a planning document for Claude to execute**, not a bash script Claude runs verbatim. Bash blocks below are illustrative examples. The real decision tree is Claude reading the actual situation each step.

Concretely:
- "If `eslint` in CI log → run linter" is ANTI-PATTERN. Read the log. Reason about the failure. Pick the fix.
- "Assume Vercel" is ANTI-PATTERN. Detect deploy mechanism (Vercel/Netlify/Fly/CF/poll-cron/none) from filesystem evidence + repo metadata.
- "Auto-delete branches that look merged" is ANTI-PATTERN. Verify content equivalence. Verify session-ownership. Then delete.

The skill should also FIND issues we didn't think to specify (proactive audit) and IMPROVE the CI workflow when patterns are suboptimal — not just execute the documented steps.

---

## DISCIPLINE

> Reference: [Superpowers Discipline Protocol](~/.claude/standards/STEEL_DISCIPLINE.md)

Steel principles applied to /gh-ship:

- **#1 (verification before claim):** "deploy succeeded" requires curl on the actual production URL with HTTP 200 + expected content. Not "Vercel dashboard says success." Not "merge command exited 0." Not "CI says green."
- **#1 (CI passes):** read the actual CI status; don't assume.
- **#3 (RED-GREEN-REFACTOR):** never skip a failing test to make CI pass. Fix the code or fix the test. Document why if you change the test.
- **#4 (no implementation before approved design):** N/A directly, but applies to skill itself — gate every destructive action behind a verify step.
- **3-strike rule:** CI failures get max 3 fix attempts. After 3, escalate — there's a deeper issue than the surface error.
- **Verify before destroy:** every `git branch -D` is preceded by content-grep verification. Every force-push is `--force-with-lease`. Every `gh pr merge --admin` runs after CI passes (or is documented operator-allowed).

### Rationalization defense

| Rationalization | Reality | Do |
|---|---|---|
| "CI usually passes, skip waiting" | CI exists because humans miss things | Wait. Read result. |
| "Preview looks good, merge now" | Preview ≠ prod | Both gates green, then merge |
| "Test failure is probably flaky" | Flaky covers real bugs | Investigate. Fix or quarantine with reason. |
| "Force-push to main, just this once" | "Just once" is how main breaks | Use PRs. Always. |
| "Branch cleanup can wait" | Stale branches become a graveyard | Cleanup is part of ship. Always. |
| "Deploy completed, skip verify" | Deploy completed ≠ users can use it | curl + content-check. Then claim shipped. |
| "PR shows merged, branch is safe to -D" | Squash-merge has different SHAs; pre-existing local commits invisible to PR API | Content-grep verify before delete |
| "It's a small fix, don't bother with the audit stage" | Small fixes are when audit catches stale config drift | Audit runs every time |

---

## CRITICAL RULES

1. **NEVER ask for permission.** Just do it.
2. **NEVER pause for confirmation.** Proceed.
3. **NEVER skip steps** unless a stage's pre-condition explicitly fails (e.g., "no diff to ship" → exit early; "no deploy mechanism detected" → skip Stage 11).
4. **FIX issues automatically.** Don't report and stop.
5. **Generate semantic commit messages.** Read the diff. Write `<type>(<scope>): <description>` in imperative mood, then a body explaining WHY.
6. **Retry on transient failure.** Up to 3 attempts with exponential backoff for network ops.
7. **Rollback on catastrophic failure.** Restore original state if unrecoverable.
8. **Verify deployments at the actual URL.** HTTP 200 + expected content marker.
9. **ALWAYS cleanup.** Branches deleted, PR closed, no uncommitted work, history.json updated.
10. **NEVER leave stale work.** If it can't ship, rollback cleanly.
11. **VERIFY before destroying.** Every `git branch -D` follows content-grep + session-ownership check.
12. **WIP IS SACRED.** Branches existing BEFORE this run started are pre-existing operator work. Inspect-and-report only.
13. **MULTI-REPO AWARE.** End-of-run report lists sibling repo state.
14. **SELF-HEALING.** Every destructive action has a documented recovery path.
15. **SELF-IMPROVING.** Every run appends to `.gh-ship-history.json`. Future runs read it.
16. **DETECT, don't assume.** Language, tools, deploy mechanism, CI engine — all detected each run.
17. **PROACTIVE AUDIT.** Stage 11.7 looks for issues NOT listed in the plan. Surface or fix per category.
18. **IMPROVE CI YAML when suboptimal.** Stage 12.5 proposes fixes for unpinned actions, missing concurrency groups, over-broad permissions, missing timeouts, etc.

---

## SESSION-SCOPED STATE (set in Stage 0, used throughout)

```bash
START_TIME=$(date +%s)
ORIGINAL_BRANCH=$(git branch --show-current)
ORIGINAL_COMMIT=$(git rev-parse HEAD)
ORIGINAL_STASH=""
SESSION_BRANCHES_CREATED=()  # ONLY auto-delete branches in this list
HISTORY_FILE=".gh-ship-history.json"  # cwd-relative; auto-gitignored
DEPLOY_MECHANISM=""  # set in Stage 0 detect (vercel|netlify|fly|cf|poll-cron|self-hosted-other|none)
CI_ENGINE=""  # set in Stage 0 detect (github-actions|gitlab-ci|circleci|none)
PROJECT_TYPE=""  # set in Stage 0 detect (node|python|go|rust|bash|docs|mixed|unknown)
```

---

## STAGE 0: PRE-FLIGHT + HISTORY READ + DETECTION

### 0.1 Save rollback state

Capture above state vars. Stash unstaged changes if any (`git stash push -m "gh-ship-auto-stash-$(date +%s)"`).

### 0.2 Directory exclusion check

Read `CLAUDE.md` (project, parent, ~). If it says "NO GIT" or "NEVER initialize a git repo here" for this dir, ABORT with explanation. Examples:
- `~/vibecode-projects/n8n-workflows/` — managed via n8n UI, not git

### 0.3 Environment sanity

- Must be in a git repo (`git rev-parse --git-dir`)
- Must have a remote (`git remote get-url origin`)
- `gh` must be authenticated (`gh auth status`)
- If any check fails, fix or abort with actionable message

### 0.4 Detect language / tools / deploy mechanism / CI

**Adapt to repo type. Don't assume.**

| Signal | Tells you |
|---|---|
| `package.json` exists | Node project. Read its `scripts:` to find `lint`, `test`, `build` commands. |
| `pyproject.toml` / `setup.py` | Python. Look for `pytest`, `ruff`, `black`. |
| `Cargo.toml` | Rust. `cargo check` / `cargo test`. |
| `go.mod` | Go. `go build` / `go test`. |
| `bats` test files in `tests/bash/` | Bash project. Run bats. |
| `.github/workflows/*.yml` | GitHub Actions CI. Inspect jobs to learn what runs. |
| `.gitlab-ci.yml` | GitLab CI. |
| `vercel.json` or `next.config.*` + `.vercel/` | Vercel deploy. |
| `netlify.toml` | Netlify. |
| `fly.toml` | Fly.io. |
| `wrangler.toml` | Cloudflare Workers. |
| Cron entry referencing a `deploy-*.sh` on a known host | Self-hosted poll-cron deploy (per ADR-041 pattern). |
| None of the above | Pure-source repo, no deploy stage to verify. Skip Stage 11. |

**Multi-mechanism caveats**: a repo can have BOTH Vercel preview AND a self-hosted prod deploy. Both must be verified.

### 0.5 Read `.gh-ship-history.json` (self-improvement)

If the file exists at repo root, read it. Extract:
- `patterns_observed` (known CI failure shapes + the fixes that worked)
- Last run's `outcome`. If `failed`, prepare for elevated caution.
- `wip_branches_protected` from any prior run — sticky protection. Add to a NEVER-DELETE list.

If the file doesn't exist, will be created in Stage 13.

Add `.gh-ship-history.json` to `.gitignore` if not already there:
```bash
grep -q '\.gh-ship-history\.json' .gitignore 2>/dev/null || echo '.gh-ship-history.json' >> .gitignore
```

### 0.6 Stale-branch detection (informational; don't act yet)

```bash
STALE_LOCAL=$(git branch --merged main | grep -v "main\|master\|\*" | xargs)
```

Note in run state. If any are present and clearly merged, they'll be reported in Stage 12 cleanup but NOT auto-deleted unless they're in `SESSION_BRANCHES_CREATED`.

### 0.7 Comprehensive secrets + bad-content scan

Use the conventional regex set (sk-*, ghp_*, AKIA*, AIza*, etc.) but ALSO reason about file content. If a file looks suspicious (large blob in `.env`, `credentials.json`, etc.) and is in the staged set, unstage and add to `.gitignore` even if no regex matched.

```bash
# Conventional patterns (extend as needed; AI judgment fills gaps)
SECRETS_REGEX='(API_KEY|SECRET_KEY|PRIVATE_KEY|sk-[a-zA-Z0-9]{32,}|ghp_[a-zA-Z0-9]{36}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|-----BEGIN (RSA|DSA|EC|OPENSSH|PGP) PRIVATE KEY-----)'
```

If found, unstage + add the path glob to `.gitignore` + create `.env.example` with placeholders if relevant.

### 0.8 Large-file + build-artifact + .env detection

`find . -path ./.git -prune -o -type f -size +50M -print` → add to `.gitignore` and unstage.
`git diff --cached --name-only | grep -E '^\.env'` → unstage; ensure `.env*` in `.gitignore`.
`git diff --cached --name-only | grep -qE 'node_modules/|\.next/|dist/|build/|\.turbo/|\.vercel/'` → unstage; ensure in `.gitignore`.

---

## STAGE 0.5: MULTI-REPO WORKSPACE SCAN

If parent dir of cwd's repo contains other directories that are themselves git repos, this is a multi-repo workspace.

```bash
WORKSPACE_PARENT=$(git rev-parse --show-toplevel | xargs dirname)
SIBLING_STATES=()
for sibling in "$WORKSPACE_PARENT"/*/; do
  if [ -d "$sibling/.git" ] && [ "$(realpath $sibling)" != "$(git rev-parse --show-toplevel)" ]; then
    pushd "$sibling" >/dev/null
    name=$(basename "$sibling")
    uncommitted=$(git status --porcelain | wc -l | tr -d ' ')
    unpushed=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo 0)
    SIBLING_STATES+=("$name:uncommitted=$uncommitted:unpushed=$unpushed")
    popd >/dev/null
  fi
done
```

`SIBLING_STATES` is included in the final SITREP. /gh-ship does NOT cross-traverse to ship sibling work — operator runs /gh-ship from each repo separately. But surfacing the state prevents the "I shipped one repo and forgot the others" class of bug.

---

## STAGE 1: PRE-PUSH LOCAL VALIDATION

Run language-appropriate checks. AI-judgment: pick the right tool for the project.

For Node: `npm run typecheck`, `npm run lint`, `npm run build` — but only if those scripts exist. If they don't, run the underlying tools directly (`npx tsc --noEmit`, etc.) AND consider whether a missing script is itself an issue worth flagging in Stage 11.7 audit.

For Python: `pytest tests/`, `ruff check`, `mypy` — same logic.

For other languages: detect canonical equivalents.

If validation fails:
1. **Auto-fix what's auto-fixable** (formatter, lint --fix). Re-run.
2. **For non-trivial errors** (typecheck, build): read the error, fix the underlying code, NEVER suppress with `--no-verify` or `as any`.
3. **If genuinely stuck** after the diff is small: surface the error and ABORT — don't push broken code.

---

## STAGE 2: ANALYZE CHANGES

```bash
git status --short
git diff --staged --stat
git diff --stat
```

Categorize the diff:
- File count, total lines added/removed
- Categories: source / config / docs / tests / assets / CI
- Intent: feat / fix / refactor / docs / chore / test / style / perf / build / ci / sec
- Scope: which subsystem? (e.g., `auth`, `api`, `ui`, `ci`)

This drives the commit message in Stage 3.

If after safety scans (Stage 0.7-0.8) there's nothing left to commit: report "Nothing to ship after safety filtering" and exit.

---

## STAGE 3: GENERATE COMMIT MESSAGE

Format: `<type>(<scope>): <description>`

- Max 72 chars on title
- Imperative mood ("Add feature" not "Added feature")
- No trailing period
- Specific about WHAT changed
- Body explains WHY (why this approach, what alternative was rejected, what risk this closes)

If the diff has multiple distinct concerns (rare in /gh-ship since usually one PR = one purpose), suggest splitting — but don't auto-split without operator confirmation.

Examples:
- `feat(reddit): Add monitoring keywords for new pain signals`
- `fix(approvals): Collision-proof apr- ids by appending random suffix`
- `chore(ci): Pin actions/checkout to SHA, add concurrency group`

---

## STAGE 4: STAGE & COMMIT

```bash
git add -A
git commit -m "$(cat <<'EOF'
<type>(<scope>): <description>

<body explaining WHY>

Co-Authored-By: Claude <model@anthropic.com>
EOF
)"
```

If pre-commit hooks fail:
- Linter/formatter errors → run auto-fix, re-stage, re-commit
- TypeScript / type errors → fix in code, re-stage, re-commit
- Other → diagnose, fix if possible, otherwise NEVER use `--no-verify` (Steel Principle: don't bypass safety hooks)

---

## STAGE 5: BRANCH MANAGEMENT

```bash
CURRENT_BRANCH=$(git branch --show-current)
```

If on `main` / `master`:
- Generate branch name from commit type + scope + short description
- `feature/...`, `fix/...`, `refactor/...`, `chore/...`, `sec/...`, `docs/...`
- `git checkout -b "$BRANCH_NAME"`
- **Add to `SESSION_BRANCHES_CREATED`** (used in Stage 12 cleanup)

If already on a feature branch: continue, but note we did NOT create it (don't add to SESSION_BRANCHES_CREATED — it's pre-existing).

---

## STAGE 6: PUSH TO REMOTE

```bash
git push -u origin HEAD
```

If push rejected (branch diverged):
- `git fetch origin && git rebase origin/main`
- For lockfile conflicts (`package-lock.json`, `pnpm-lock.yaml`, `Cargo.lock`, `go.sum`): regenerate via `<pm> install`, re-stage, continue rebase
- For generated files (`*.generated.ts`, `*.d.ts`): prefer theirs (origin's version)
- For source files: prefer ours (our changes are intentional)
- Resume: `git push --force-with-lease` (NEVER plain `--force`)

If network failure: retry with exponential backoff (2s, 5s, 10s).

---

## STAGE 7: CREATE PULL REQUEST

```bash
EXISTING_PR=$(gh pr list --head "$(git branch --show-current)" --json number --jq '.[0].number')
```

If PR exists, reuse. Otherwise:

```bash
gh pr create --title "<commit-title>" --body "$(cat <<'EOF'
## Summary
<2-3 bullets — the WHY in compressed form>

## Changes
<key files; high-level not granular diff>

## Test Plan
- [ ] CI passes
- [ ] Preview deployment verified (if applicable)
- [ ] [project-specific verification]

🤖 Shipped via /gh-ship
EOF
)"
```

If `gh pr create` fails on GraphQL rate limit (common during heavy sessions), fall back to REST:
```bash
gh api repos/:owner/:repo/pulls -X POST -f title="..." -f head=<branch> -f base=main -f body="..."
```

---

## STAGE 8: WAIT FOR CI + DEPLOY PREVIEW

Adaptive based on detected `CI_ENGINE` and `DEPLOY_MECHANISM`.

### 8.1 CI checks (max 10 min)

```bash
# poll gh pr checks every 15s
# success: all "SUCCESS" → continue to merge gate
# failure: jump to Stage 9 (fix loop)
# pending: keep polling
```

For `CI_ENGINE=github-actions`: `gh pr checks $PR_NUMBER --json state`
For others: adapt the equivalent.

### 8.2 Preview deployment verification (if applicable)

For `DEPLOY_MECHANISM=vercel|netlify|cf-pages`:
- Wait for deploy bot's checks to complete
- Extract preview URL from PR comments OR `gh pr checks --json targetUrl`
- `curl` the preview URL → expect HTTP 200
- If responds with the expected content marker (page title, version string, etc.), continue
- If 5xx or wrong content: investigate. Don't merge bad deploys.

For `DEPLOY_MECHANISM=poll-cron|self-hosted-other`: skip preview (no preview URLs); rely on Stage 11 production verification.

For `DEPLOY_MECHANISM=none`: skip Stage 8.2 entirely.

---

## STAGE 9: AI-JUDGMENT CI FIX LOOP

**Max 3 attempts.** This is where most pattern-match-skill rewrites get the most improvement.

### 9.1 Get failure detail

```bash
FAILED_RUN=$(gh run list --limit 5 --json databaseId,status,conclusion --jq '.[] | select(.conclusion=="failure") | .databaseId' | head -1)
gh run view "$FAILED_RUN" --log-failed | tail -200
```

### 9.2 Reason about the failure

Read the actual log. Don't grep for keywords; understand what failed. Then:

1. **Check `.gh-ship-history.json` `patterns_observed`** for a known shape. If found and the prior fix worked: try it FIRST. If the prior fix didn't work last time: try a different approach.

2. **Match by meaning, not by string.** "linter complains about formatting" maps to "run formatter" regardless of whether the linter is biome / eslint / ruff / golangci-lint.

3. **Apply the fix-strategy hint table below as starting points, not rules:**

| Failure family | Strategy hint |
|---|---|
| Linter | Run project's linter --fix. Detect tool from project files. |
| Formatter | Run project's formatter (prettier, gofmt, black, dprint, ruff format). |
| Typechecker | Read error, inspect file:line, propose smallest correct change. NEVER suppress with `// @ts-ignore`, `# type: ignore`, etc. |
| Test failure | Read assertion. Decide: code wrong (usual) vs test wrong (rare, only if test was written ahead of code). Fix the right side. NEVER skip the test. |
| Build error | Read error, fix root cause. If due to missing CI env var: surface to operator with exact var name. |
| Dependency / lockfile | Regenerate lockfile OR `<pm> audit fix` for advisories OR pin conflicting peer. Check history for what worked on this project before. |
| Network / rate-limit / 5xx / timeout | Retry up to 3x with backoff. For CI rate-limit specifically, prefer `gh run rerun` over re-pushing. |
| Pre-existing flaky test | Match against history. If flaky: retry once. If still flaky: report — DO NOT mask with quarantine unless operator-allowed. |
| Disk space / runner exhaustion | Not auto-fixable. Report and abort. |
| Auth / credential rotation | Operator-action required. Surface exactly which secret rotated + where to update. |
| Container registry permission (e.g., GHCR 403) | Diagnose: workflow `permissions:` correct? Package-ACL missing repo? PAT expired? Provide fix instructions. |
| **Unknown shape** | State the hypothesis. Try smallest correct fix. Append to `.gh-ship-history.json` regardless of outcome — negative knowledge is valuable. |

### 9.3 Apply fix

Make the change. Stage. Commit (`fix(ci): ...` scope). Push.

### 9.4 Loop

Return to Stage 8. Decrement attempt counter.

### 9.5 After 3 attempts

If unfixed:
- Detailed error report (which fix attempts were tried, why each failed)
- Append to `.gh-ship-history.json` with `outcome=ci-unfixable`
- Do NOT merge broken code
- Keep PR open for manual review
- Exit with error status; SITREP shows BLOCKED

---

## STAGE 10: MERGE PR

Pre-condition: CI green AND (preview verified OR no preview deploy).

```bash
# --admin bypasses GH branch protection's "required reviewers" gate.
# Solo workflow assumption. For team workflows, remove --admin and add review check.
gh pr merge "$PR_NUMBER" --squash --delete-branch --admin
```

Note: `--delete-branch` works inconsistently with `--admin` per observation 2026-05-03. After merge, verify the remote branch was actually deleted; if not, explicit `git push origin --delete <branch>`.

If merge fails:
- **Conflict** → rebase on origin/main, force-with-lease, retry
- **Branch protection** → log requirements + exit (operator-action)
- **GraphQL rate limit** → fall back to REST: `gh api repos/:owner/:repo/pulls/$PR_NUMBER/merge -X PUT -f merge_method=squash`
- **Network** → retry with backoff

---

## STAGE 11: VERIFY PRODUCTION DEPLOYMENT

Adaptive per `DEPLOY_MECHANISM`.

### 11.1 Wait for post-merge CI on main

CI typically runs again on push to main. Poll until completed.

If main-CI fails after merge: this is **bad** — broken code is on main. Stage 11 reports it loudly. Subsequent verification skipped.

### 11.2 Wait for production deploy

| Mechanism | How to wait |
|---|---|
| `vercel` | Poll `gh api repos/:owner/:repo/deployments` for `state=success` from `vercel[bot]` on `ref=main` |
| `netlify` | Same pattern (different bot) |
| `fly` | If Fly's GH workflow integration: poll. Else: `flyctl status`. |
| `cf` | Cloudflare Pages: poll deployments API. |
| `poll-cron` | Cron interval is known (typically 2-5 min). Poll deployed SHA on the host vs origin/main SHA until match. |
| `self-hosted-other` | Operator-defined. Read project docs; if unclear, surface to operator. |
| `none` | Skip. |

### 11.3 Verify production at the actual URL

```bash
# Detect production URL from package.json `homepage`, repo `homepage`, or operator config
PROD_URL=$(jq -r '.homepage // empty' package.json 2>/dev/null || \
           gh api repos/:owner/:repo --jq '.homepage')

# Verify
HTTP_STATUS=$(curl -s -o /tmp/prod-resp -w "%{http_code}" "$PROD_URL" --max-time 30)

# HTTP 200 alone isn't enough — content check
if [ "$HTTP_STATUS" = "200" ] && grep -q "<expected-marker>" /tmp/prod-resp; then
  PROD_VERIFIED="yes"
else
  PROD_VERIFIED="warning"  # surface manual-check note in SITREP
fi
```

**Expected marker** is project-specific. For a Next.js app, could be the page title or a known UI element. Skill should detect it from the repo's recent commit history or fall back to "page returns HTML > 1KB" as a weak default.

### 11.4 Verify squash-merged content actually landed

This is the lesson from 2026-05-03. After merging a PR, before assuming Stage 11 is "done":

```bash
git fetch origin
# the PR's merge_commit_sha
MERGE_SHA=$(gh pr view "$PR_NUMBER" --json mergeCommit --jq '.mergeCommit.oid')

# verify it's on origin/main
if git merge-base --is-ancestor "$MERGE_SHA" origin/main 2>/dev/null; then
  echo "✅ PR merge commit is on origin/main"
else
  echo "❌ PR merge commit NOT on origin/main — propagation lag or merge anomaly"
  # do NOT proceed to cleanup; surface for review
fi
```

---

## STAGE 11.5: VERIFIED-MERGE DETECTION (squash-safe, content-grep)

This is THE check that prevents the "I deleted unmerged work because PR-state said merged" class of bug observed 2026-05-03.

### Helper: `verify_branch_merged()`

```bash
verify_branch_merged() {
  local branch="$1"
  local source_sha=$(git rev-parse "$branch")

  # Method 1: ancestor check (catches merge-commit merges)
  if git merge-base --is-ancestor "$source_sha" main 2>/dev/null; then
    echo "ancestor"; return 0
  fi

  # Method 2: PR-state lookup (catches squash-merge if PR exists)
  local pr_info=$(gh pr list --head "$branch" --state all --json merged --jq '.[0]' 2>/dev/null)
  if echo "$pr_info" | grep -q '"merged":true'; then
    echo "squash-merged-via-pr"; return 0
  fi

  # Method 3: content equivalence (catches squash-merged + branch deleted)
  if [ -z "$(git diff main..."$branch")" ]; then
    echo "content-identical-to-main"; return 0
  fi

  # Genuinely unmerged
  echo "UNMERGED"; return 1
}
```

### Helper: `post_merge_verify()`

```bash
post_merge_verify() {
  local branch="$1"
  local merge_sha=$(gh pr view "$PR_NUMBER" --json mergeCommit --jq '.mergeCommit.oid' 2>/dev/null)
  if [ -n "$merge_sha" ] && git merge-base --is-ancestor "$merge_sha" origin/main 2>/dev/null; then
    return 0
  fi
  git fetch origin main
  if [ -z "$(git diff origin/main..."$branch")" ]; then
    return 0
  fi
  return 1  # divergent — DO NOT delete
}
```

Used by Stage 12 cleanup before any `git branch -D`.

---

## STAGE 11.7: PROACTIVE AUDIT (NEW — find what we didn't specify)

This is the "scan for stuff we didn't think to look for" stage. Surface findings; fix some categories autonomously, queue others for operator review.

### Categories to scan

**A. `.github/workflows/*.yml` health**
- Action versions pinned to SHA (not just tag) — important for supply-chain security
- `permissions:` block present and minimal (most workflows over-permission with default token)
- `timeout-minutes:` set on each job (prevent runaway)
- `concurrency:` group on deploy workflows (prevent races)
- `paths:` filter on push triggers (skip irrelevant runs)
- Direct `secrets.X` use vs OIDC (where supported)

**B. Branch protection on main** (`gh api repos/:owner/:repo/branches/main/protection`)
- Required status checks?
- Linear history enforced?
- Force-push allowed? (should be off)
- Allow auto-merge? (should be off for safety)

**C. Repo settings** (`gh api repos/:owner/:repo`)
- `delete_branch_on_merge`: should be `true` (prevents stale-remote class of bug)
- Allowed merge types sensible?
- Issues enabled if public? Discussions if community-facing?

**D. Container registry health** (if image build present)
- GHCR package's "Manage Actions Access" includes the workflow's repo? (the 2026-05-03 lesson)
- Untagged versions accumulating? (cleanup candidate)

**E. Repo file health**
- `.gitignore` covers common bad things (`.env*`, `*.log`, `dist/`, `node_modules/`)
- `LICENSE` present?
- `README` not stale (last updated > 6 months ago + recent code commits)
- Lockfile committed?

**F. Open PRs / issues**
- PRs with no activity > 30 days → flag for triage (don't close)
- Branches with no PR > 7 days old → flag for cleanup
- Issues labeled `bug` open > 90 days → flag

**G. CI runs trend** (`gh run list`)
- Failure rate over last 20 runs > 30%? Flag the pattern.
- Average run time creeping up? Surface.

### Fix-vs-surface decision

For each finding, decide:
- **Fix autonomously** if: change is uncontroversial (e.g., add missing `timeout-minutes: 15` to a job that doesn't have one)
- **Surface for operator review** if: change has tradeoffs (e.g., enabling branch protection blocks the operator's own admin-merge workflow)

Autonomous fixes go in a separate `chore/audit-improvements-<date>` branch and PR. Operator-review items go in the SITREP.

---

## STAGE 12: CLEANUP & FINAL VERIFICATION

**Pre-condition:** Stage 11.5's `post_merge_verify` passed for the session's branch. If not, ABORT cleanup.

### 12.1 Switch to main + pull

```bash
git checkout main
git pull origin main
```

### 12.2 Delete the session's feature branch

```bash
# Try -d first (safe; refuses if not merged-via-merge-commit)
if git branch -d "$BRANCH_NAME" 2>/dev/null; then
  echo "🗑️  Deleted (safe): $BRANCH_NAME"
else
  # -d refused. Likely squash-merge differing SHAs. Stage 11.5 already
  # verified content is on main, so force-delete is OK.
  git branch -D "$BRANCH_NAME"
  echo "🗑️  Force-deleted (post-verify): $BRANCH_NAME"
fi
```

### 12.3 Remote branch deletion (`gh pr merge --delete-branch` is unreliable)

```bash
REMOTE_BRANCH_EXISTS=$(git ls-remote --heads origin "$BRANCH_NAME" 2>/dev/null)
if [ -n "$REMOTE_BRANCH_EXISTS" ]; then
  git push origin --delete "$BRANCH_NAME"
fi
```

### 12.4 Audit pre-existing branches (inspect-only — never delete)

For every branch NOT in `SESSION_BRANCHES_CREATED`:
- Run `verify_branch_merged $b` → categorize
- If merged: report "can be deleted manually with: `git branch -D <b>`"
- If unmerged + has open PR: "WIP, leaving alone"
- If unmerged + no PR: "ORPHAN? Manual review needed"

This is INFORMATIONAL only. /gh-ship never deletes pre-existing operator work.

### 12.5 Stale remote branches

`git fetch --prune` to drop remote-tracking branches whose origin counterparts are gone. Don't push-delete unless the operator has opted in.

### 12.6 Verify clean repo state

```bash
UNCOMMITTED=$(git status --porcelain | grep -v '^??' || true)
[ -n "$UNCOMMITTED" ] && echo "⚠️  Tracked files modified — review"

# Restore stash if we made one in Stage 0.1
[ "$ORIGINAL_STASH" = "yes" ] && git stash pop
```

---

## STAGE 12.5: CI WORKFLOW IMPROVEMENT (NEW)

If Stage 11.7 audit found fixable workflow anti-patterns:

### Auto-fix categories (low controversy)

- Pin unpinned actions: `actions/checkout@v4` → `actions/checkout@<SHA> # v4.2.x`
- Add missing `permissions: { contents: read }` to workflows missing it
- Add `concurrency: { group: ${{ github.workflow }}-${{ github.ref }}, cancel-in-progress: true }` to long-running CI
- Add `timeout-minutes: 15` to jobs missing it
- Add path filters to deploy workflows to skip pure-doc PRs

### Approach

```bash
git checkout -b chore/ci-improvements-$(date +%Y%m%d)
# apply YAML edits with WHY comments
git add -A
git commit -m "chore(ci): pin action SHAs + add concurrency/timeout/permissions

Per /gh-ship Stage 12.5 audit findings. Each change has a WHY comment in the
YAML noting which class of issue it closes:
- Action pinning: supply-chain attack vector (mutable tags)
- Concurrency: prevent deploy races on rapid-fire pushes
- timeout-minutes: prevent runaway billing on stuck jobs
- permissions: principle of least privilege for default token

Co-Authored-By: Claude /gh-ship <noreply@anthropic.com>"

git push -u origin HEAD
gh pr create --title "chore(ci): /gh-ship audit improvements" \
             --body "Auto-generated by /gh-ship Stage 12.5..."
```

**Do NOT auto-merge this PR.** It's a separate improvement, surfaced for operator review.

---

## STAGE 13: APPEND TO SELF-IMPROVEMENT HISTORY

```bash
RUN_ENTRY=$(cat <<JSONEOF
{
  "run_id": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "repo": "$(gh api repos/:owner/:repo --jq '.full_name')",
  "duration_seconds": $((  $(date +%s) - START_TIME )),
  "session_branches_created": ["${SESSION_BRANCHES_CREATED[@]}"],
  "stages_reached": [...],
  "ci_failures_encountered": [...],
  "anomalies": [...],
  "outcome": "$OUTCOME",
  "deploy_verified": "$PROD_VERIFIED"
}
JSONEOF
)

# Append to .gh-ship-history.json
if [ ! -f "$HISTORY_FILE" ]; then
  echo '{"schema_version":1,"runs":[],"patterns_observed":{}}' > "$HISTORY_FILE"
fi
jq ".runs += [$RUN_ENTRY]" "$HISTORY_FILE" > "$HISTORY_FILE.tmp" && mv "$HISTORY_FILE.tmp" "$HISTORY_FILE"
```

For every CI failure encountered in Stage 9, also update `patterns_observed`:
```bash
# pseudo-code
patterns_observed[shape] = {
  first_seen: existing_or_now,
  count: existing_count + 1,
  fix_known: <bool>,
  last_successful_fix: <description>
}
```

This is the source of truth Stage 0.5 reads on the NEXT run.

---

## STAGE 14: SITREP

```
═══════════════════════════════════════════════════════════════
🎉 /gh-ship — <success | partial | blocked>
═══════════════════════════════════════════════════════════════

📋 Run
   Repo:        VetSecItPro/<repo>
   Branch:      <branch> → main
   Commit(s):   <short SHAs>
   PR:          #<num> (merged | open | closed)
   Duration:    <Xm Ys>

🔗 Deploys
   Preview:     <URL> ✅ HTTP 200
   Production:  <URL> ✅ HTTP 200 + content marker found

🔧 Auto-fixes applied
   • Linter: <files fixed>
   • Formatter: <files formatted>
   • [details]

🔍 Stage 11.7 Audit findings
   Auto-fixed:
   • <thing-1> — committed in chore/ci-improvements-<date>
   Surfaced (operator review):
   • <thing-2> — see PR #<num> or note: <text>

🧹 Cleanup
   Session branch: ✅ deleted (local + remote)
   Pre-existing branches inspected: <N>
     KEEP <branch>: WIP (no PR)
     KEEP <branch>: open PR #<N>
   Stale remote branches: <N pruned>

🌐 Sibling repos in workspace
   <name>: uncommitted=N unpushed=M
   [run /gh-ship from inside if changes pending]

📊 Self-improvement log
   .gh-ship-history.json updated
   Patterns observed total: <N>
   New pattern this run: <shape>

═══════════════════════════════════════════════════════════════
```

---

## ROLLBACK PROCEDURE

If catastrophic failure at any stage:

```bash
# Restore original branch
git checkout "$ORIGINAL_BRANCH" 2>/dev/null || git checkout -

# Reset to original commit
git reset --hard "$ORIGINAL_COMMIT"

# Delete any session-created branches (local + remote)
for b in "${SESSION_BRANCHES_CREATED[@]}"; do
  if [ "$b" != "$ORIGINAL_BRANCH" ]; then
    git branch -D "$b" 2>/dev/null || true
    git push origin --delete "$b" 2>/dev/null || true
  fi
done

# Close PR if created
[ -n "$PR_NUMBER" ] && gh pr close "$PR_NUMBER" --comment "Rolled back due to error" 2>/dev/null

# Restore stash
[ "$ORIGINAL_STASH" = "yes" ] && git stash pop

# Append failure entry to history
echo "Rolled back to: $ORIGINAL_COMMIT on $ORIGINAL_BRANCH"
```

---

## SELF-HEALING RECOVERY PATTERNS

### Accidentally `git branch -D`'d a branch with unmerged work

```bash
# reflog has the SHA
git reflog | grep <branch-name>
# restore
git branch <branch-name> <SHA-from-reflog>
```

### Force-pushed wrong content

```bash
# reflog of remote-tracking ref
git reflog show origin/<branch>
# revert origin via push --force-with-lease to the correct SHA
git push origin <correct-SHA>:<branch> --force-with-lease
```

### Merged a bad PR

```bash
# revert the merge commit
git checkout main
git revert -m 1 <merge-SHA>
git push
```

### Stash got lost

```bash
git fsck --lost-found
# look in .git/lost-found/ for orphan stashes
```

---

## NETWORK RESILIENCE

For any network operation:

```bash
retry_with_backoff() {
  local max_attempts=3 delay=2 attempt=1
  while [ $attempt -le $max_attempts ]; do
    if "$@"; then return 0; fi
    sleep $delay
    delay=$((delay * 2))
    attempt=$((attempt + 1))
  done
  return 1
}
```

For GitHub specifically:
- GraphQL rate limit (5000/hr separate from REST 5000/hr): if exhausted, fall back to REST endpoint for the same operation
- Watch loops should use REST polling (`gh api repos/.../actions/runs/<id>`) not GraphQL `gh pr checks --watch` to preserve quota

---

## RELATED SKILLS

**Feeds from:**
- `/test-ship` — run before /gh-ship to ensure tests pass
- `/sec-ship` — run before /gh-ship to ensure no vulns
- `/smoketest` — quick pre-ship sanity
- `/subagent-dev` — produces code; /gh-ship ships it
- `/blog`, `/investigate` — both call /gh-ship for the publish/fix-ship handoff

**Feeds into:**
- `/monitor` — after /gh-ship completes, run /monitor to verify production health
- `/qatest` — run on preview deployment before merge

**Auto-suggest after success:** `/monitor` for full post-deploy health check.

---

## STATUS UPDATES

Provide brief status every 30-60s during execution. Format per [Status Update Protocol](~/.claude/standards/STATUS_UPDATES.md).

---

## CLEANUP PROTOCOL

> Reference: [Resource Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md)

Stage 12 + 12.5 cover all cleanup. No additional protocol needed.

---

## DESIGN DECISIONS (WHY this structure)

### Why AI-judgment over regex tables

The previous version had ~15 rows of "if grep X then run Y." Real CI failures don't fit those rows. ruff E401 doesn't say "linter" — it says "Multiple imports on one line." A skill that pattern-matches misses this; a skill that reads + reasons handles it.

### Why session-scoped branch tracking

The 2026-05-03 incident: cleanup loop saw `feature/whatsapp-pair-ui-scaffold` (no PR) and could have deleted it as "unmerged garbage." It was actually operator's WIP. Solution: only auto-delete branches that THIS run created. Pre-existing is sacred.

### Why content-grep verification before delete

Squash-merge produces a NEW commit on main with different SHA. Ancestor checks fail. PR-state lookup helps but breaks when the PR was deleted. Content equivalence is the most robust signal: "is the diff between this branch and main empty?" → safe to delete.

### Why proactive audit (Stage 11.7)

The user's ask: "we can tell it to also check for other stuff that it might find but we didn't think to specify." Static fix tables can never be exhaustive. An audit stage that scans for known anti-patterns AND surfaces unknowns covers the long tail.

### Why CI workflow improvement (Stage 12.5)

Most repos accumulate workflow drift: unpinned actions, missing concurrency groups, over-permissioned tokens. /gh-ship sees these patterns across many runs. Surfacing fixes (auto-applied for safe categories, surfaced for review for tradeoffs) is high-leverage maintenance.

### Why self-improvement history

Same patterns of failure recur. ruff E401 on Python projects, GHCR 403 after a rename, idempotency-key collisions on millisecond-resolution ids. Without a log, every run rediscovers from scratch. With a log, future runs try the known-good fix first.

### Why multi-repo report only (no cross-traverse)

A workspace with 3 sibling repos shouldn't make /gh-ship 3x as complex. One repo per invocation. But the SITREP must surface sibling state — otherwise the operator forgets to ship the others.

---

## IMPORTANT REMINDERS

- This skill runs FULLY AUTONOMOUSLY — no permission asking, no confirmation pausing
- READ the diff for commit messages — don't generate generic ones
- FIX everything that's fixable; don't just report
- VERIFY before destroying (content-grep, session-ownership)
- PROTECT pre-existing WIP (only delete what THIS run created)
- AUDIT proactively (Stage 11.7) — find what we didn't specify
- IMPROVE CI workflows (Stage 12.5) — propose safe upgrades for review
- LEARN from history (`.gh-ship-history.json`)
- SCAN siblings in multi-repo workspaces
- ROLLBACK cleanly on catastrophic failure
- The user trusts /gh-ship to ship code SAFELY, CORRECTLY, COMPLETELY, and to GET BETTER over time

<!-- /gh-ship by Steel Motion LLC — https://steelmotion.dev -->
<!-- Part of steelmotion-ops (renamed from claw-ops 2026-05-03) -->
<!-- Lessons learned from 2026-05-03 incident: ~/.claude/commands/_plans/skills-collection-rewrite-plan.md -->
<!-- License: MIT -->
