# /gh-ship - stage procedures

Read at Stage 0 and as each stage begins. `SKILL.md` holds the rules; this holds the how. The story
behind each rule is in `provenance-archive.md`; do not read it during a run. Carry this state:

```
START_EPOCH (date +%s), ORIGINAL_BRANCH, ORIGINAL_COMMIT, OWNER_REPO, DEFAULT_BRANCH
SESSION_BRANCHES_CREATED[]   # ONLY these may be deleted
FOREIGN_PATHS[]              # dirty paths this session did not create
PROJECT_TYPE, CI_ENGINE, DEPLOY_MECHANISM, CI_ATTEMPTS, REVIEW_ATTEMPTS
```

## Stage 0 - pre-flight

**0a Tree.** `git status --porcelain` FIRST; populate `FOREIGN_PATHS` per `SKILL.md`. Record
`ORIGINAL_BRANCH` and `ORIGINAL_COMMIT` for rollback.

**0b Exclusion.** Read `CLAUDE.md` at project, parent and `~`. If it says this directory must not be
git-managed (for example an n8n workflow store), abort with the reason.

**0c Environment.** Inside a git repo, `origin` exists, `gh auth status` is clean; otherwise fix it or abort with an actionable message. Set
`OWNER_REPO` from `origin` and pass `-R "$OWNER_REPO"` to every `gh` call: in a fork, `gh` defaults
to the upstream repo.

**0d Detection. Adapt, never assume.**

| Signal | Means |
|---|---|
| `package.json` | Node: its `scripts` hold the real lint/test/build commands |
| `pnpm-lock.yaml` / `yarn.lock` / `bun.lockb` | that package manager, not npm |
| `pyproject.toml` / `requirements.txt` | Python: pytest, ruff, mypy |
| `Cargo.toml` / `go.mod` | Rust / Go |
| `*.csproj`, `pom.xml`, `Gemfile`, `composer.json` | .NET / Java / Ruby / PHP |
| `tests/bash/*.bats` | bats |
| `.github/workflows/*.yml` | GitHub Actions: read the jobs to learn what gates |
| `.gitlab-ci.yml`, `.circleci/`, `Jenkinsfile` | that CI engine |
| `vercel.json`, `netlify.toml`, `fly.toml`, `wrangler.toml` | that deploy target |
| cron invoking a `deploy-*.sh` on a known host | self-hosted poll-cron deploy |
| none of the above | source-only repo: Stage 11 records "no deploy mechanism" |

A repo can have both a preview deploy and a self-hosted production deploy. Verify both.

**0e History.** Read `.gh-ship-history.json` and `.git/gh-ship-history.pending.json` if present:
`patterns_observed` (known CI failure shapes and the fix that worked), the last run's `outcome`, the
last `audit` date, and `wip_branches_protected` (sticky: never delete these). Apply the history-file
policy in `SKILL.md`.

**0f Stale branches.** `git branch --merged <default>`: note for the SITREP. Do not act.

**0g Content safety.** The global pre-commit hook (`~/.claude/git-hooks/pre-commit`) runs gitleaks on
every commit, so do not re-run a secrets regex here. **Exception:** a repo-local `core.hooksPath`
(`git config --local core.hooksPath`, which husky sets) replaces the global hooks entirely, so run
`gitleaks protect --staged --redact` yourself after Stage 4's `git add`. Then check what a scanner misses: a `.env*`, `*.pem`, `credentials*` or a file over
50 MB in the intended paths, or build output (`node_modules/`, `.next/`, `dist/`, `build/`,
`.turbo/`, `.vercel/`). Leave those out of the path list and add them to `.gitignore`. If the hook
prints "gitleaks NOT INSTALLED", say so in the SITREP. **Any credential found is compromised:
surface it for rotation**, regardless of apparent blast radius, and add a `.env.example` with placeholders when the value belonged in an env file.

## Stage 0.5 - sibling repos

If the parent directory holds sibling git repos, record each one's uncommitted and unpushed counts
for the SITREP. Ship one repo per invocation; never cross-traverse.

## Stage 1 - local validation

Run the commands found in 0d, including the build when one exists: typecheck and tests can pass on
a build that fails. A missing conventional script: run the underlying tool and note the gap for
11.7. Auto-fix only the mechanical (formatter, `lint --fix`), then re-run. Typecheck and build
errors get a code fix: never `--no-verify`, `@ts-ignore` or a widened type. Stuck: surface the error
and abort rather than push something broken.

## Stage 2 - analyze changes

`git status --short`, `git diff --staged --stat`, `git diff --stat`. Categorize by file count,
lines, kind (source, config, docs, tests, assets, CI), intent (feat, fix, refactor, docs, chore,
test, style, perf, build, ci, sec) and scope. This drives Stage 3. Nothing left after 0g: report
"nothing to ship after safety filtering" and exit.

## Stage 2.5 - record what this ships

**After Stage 2, before Stage 3, so the records are in this commit.** A record written after Stage
4 ships in some later, unrelated PR and leaves the tree dirty. Scope: `git merge-base
origin/<default> HEAD` on a feature branch with commits, else the working diff. Never write a record
about foreign changes.

| Kind | Examples | Action |
|---|---|---|
| **Record**: true on its date | CHANGELOG entry, ADR, lessons entry, backlog row | **Append a new one; never rewrite an old one** (correct with a dated new entry) |
| **Live document**: describes the code now | README, architecture, API reference, runbook | Reconcile: `/docs-sync --since <base>` |

**Each check states an outcome; "nothing to record" is a stated result, never a silent skip.**

1. **Changelog** when the repo ships something others pin (published image, npm version, deploy tag,
   referenced SHA; a root `CHANGELOG*.md` or a release workflow signals it). Append under
   `## [Unreleased]` with Keep a Changelog headings. Write what a consumer needs, not the diff
   summary. Otherwise: "no versioned artifact".
2. **Backlog rows.** The repo's `*-backlog.md` (environment work:
   `17.scratchpad/environment-improvement-backlog.md`). Every row this run completes goes to DONE
   with Central date and time, never deleted. Work with no row gets one now, already DONE.
3. **Lessons.** Append to the repo's lessons file anything this run learned, either direction, in
   two or three sentences, dated Central: what went wrong (especially what Claude got wrong
   unprompted), the correction, the guard. "Nothing learned" is common and legitimate.
4. **ADR** only when an option was chosen over another and the reasoning is not in the diff. Follow
   the repo's numbering and template. No ADR practice: say so; do not start one.
5. **Live documents:** `/docs-sync --since <base>`. No register: name the documents the diff makes
   suspect and `/docs-sync --bootstrap` as the fix; do not edit docs on a guess.
6. **Pending history: run the script, every time, and put its line in the report.**
   `python3 ~/.claude/skills/gh-ship/history-fold.py` folds any rows waiting in
   `.git/gh-ship-history.pending.json` into the history file and prints
   `waiting rows: N, folded: M`. If it says "tracked", add `.gh-ship-history.json` to the Stage 4
   list. After the Stage 4 commit succeeds, run it again with `--done`, which removes the pending
   file only when every row is committed. Exit 2 means damaged JSON (nothing changed: fix the file);
   exit 3 means `--done` ran before the commit. Prose was not enough: this step was skipped on
   04.novels PR #261 (scratchpad #205).

List every file this stage wrote, by name, in the run log; Stage 4 stages all of them. A repo's own
conventions outrank these defaults. Never invent a record to look productive: a fabricated entry is
worse than a missing one. This stage never blocks the ship; an honest gap goes in the SITREP.

## Stage 3 - commit message

`<type>(<scope>): <description>`, imperative, at most 72 characters, no trailing period. The body
says WHY: the reason for the approach, the alternative rejected, the risk closed, with measured
before and after numbers when the change is quantitative. A message that mentions a guarded phrase
(`git push`, `gh pr create`, `gh pr merge`) at the start of a line trips the push guard: write the
message to a file and commit with `-F`. Several unrelated concerns: suggest a split; do not split
unilaterally.

## Stage 4 - stage and commit

```bash
git add <paths>                    # every Stage 2.5 file included
git diff --cached --name-only      # ALWAYS read this before committing: no foreign path
git commit -F <message-file>
```

Hook failure: fix the cause, re-stage, re-commit. Never `--no-verify`.

## Stage 5 - branch

On the default branch: create `<prefix>/<scope>-<slug>` (`feature/`, `fix/`, `chore/`, `docs/`,
`refactor/`, `sec/`) and append it to `SESSION_BRANCHES_CREATED`. Already on a feature branch:
continue, and do NOT add it; it pre-existed this run.

## Stage 6 - push

**Confirm the branch in the same command, then push it by name:**

```bash
b=$(git branch --show-current); echo "on: ${b:-DETACHED}"   # must be this run's feature branch
GH_SHIP_ACTIVE=1 git push -u origin <that-branch-name>
```

Any earlier step can leave the tree on the default branch (a failed command whose cleanup ran
`git checkout main` did exactly that on 2026-10-18 and a commit reached main with no PR). The push
guard now refuses a prefixed push that resolves to the default branch, but read the branch anyway:
the guard is the backstop, not the plan. If you are on the default branch with commits, create the
feature branch there (`git switch -c <name>`), then reset the default branch only if it has not
been pushed. Rejected: `git fetch origin`, then
`git merge origin/<branch>` (or the base), resolve, and push again without force. Lockfiles:
regenerate with the package manager. Generated files: take theirs. Source: resolve by reading both
sides. Merge, not rebase: a rebase re-hits an append-heavy file (changelog, backlog, lockfile) once
per commit and needs a force push. Network failure: Stage 7 rule, then retry 3x (2s, 5s, 10s).

## Stage 7 - pull request

Reuse the PR for this branch if one exists (`--state all`: reopen a closed, unmerged one rather than open a duplicate). Otherwise
`GH_SHIP_ACTIVE=1 gh pr create -R "$OWNER_REPO" --body-file <file>`: WHY in 2-3 bullets, key files,
and a test plan stating the verification actually performed. No Claude attribution.

**A 5xx or timeout on a write is not evidence it failed.** Before ANY retry of a write (push, PR
create, merge, comment), check whether it landed: `gh pr list --head <branch> --state all --json
number,state,url`, `gh pr view <n> --json state,mergeCommit`, or `git ls-remote origin <branch>`
against the local sha. Landed, or "already exists", means success: take the existing object.
GraphQL rate limit: fall back to REST,
`gh api repos/$OWNER_REPO/pulls -X POST -f title=... -f head=... -f base=... -f body=...`.

## Stage 8 - CI and preview

### 8.0 Mergeability first

```bash
gh api "repos/$OWNER_REPO/pulls/<n>" --jq '"mergeable=\(.mergeable) state=\(.mergeable_state)"'
```

| Reading | Meaning | Do |
|---|---|---|
| `mergeable=false`, `state=dirty` | Conflicted. **No workflow will ever run** | Merge the base in, resolve, push. Waiting is wasted |
| `mergeable=null`, `state=unknown` | Not computed yet (GitHub computes it asynchronously) | Re-poll every ~4s, up to 3 times. Never read null as fine |
| `mergeable=true` | Free to wait | 8.1 |
| `blocked` / `unstable` / `behind` | Not a conflict; checks still run | 8.1 |

Null is permanent and meaningless on a closed or merged PR; check it is open first. **"No checks
reported" says nothing on its own about CI or GitHub.** For more than ~90 seconds, check in order:
mergeability (a conflict can appear mid-wait when another PR merges), then whether any workflow's
triggers and `paths:` match this branch and diff, then the platform. Probing with a throwaway
branch cut from the conflicted branch reproduces the conflict; cut it from the base.

### 8.1 Expected checks, then the verdict

Checks register one at a time, so "all passed" over a partial list is not a verdict.

```bash
num(){ case "$1" in ''|*[!0-9]*) echo 0 ;; *) echo "$1" ;; esac; }
req=$(gh api "repos/$OWNER_REPO/branches/<default>/protection/required_status_checks" \
      --jq '.checks | length' 2>/dev/null) || req=0      # a 404 prints JSON to stdout: num() drops it
last=$(gh pr list -R "$OWNER_REPO" --state merged -L 1 --json number --jq '.[0].number' 2>/dev/null) || last=""
prev=0; [ -n "$last" ] && { prev=$(gh pr checks "$last" -R "$OWNER_REPO" --json name --jq 'length' 2>/dev/null) || prev=0; }
got=$(gh pr checks "$PR_NUMBER" -R "$OWNER_REPO" --json name --jq 'length' 2>/dev/null) || got=0
req=$(num "$req"); prev=$(num "$prev"); got=$(num "$got")
exp=$(( req > prev ? req : prev ))
echo "registered=$got expected=$exp (required=$req, last merged PR #${last:-none}=$prev)"
```

Wait until `got` reaches `exp`, then read states. Not reached 5 minutes after the last new check
appeared: **the stage FAILS.** Name each missing check (compare with the last merged PR) and account
for it; a path filter is an answer only after reading that workflow's `paths:` against this diff.
Expected 0 on a repo with no CI is fine; say so.

**Waiting.** Foreground `sleep` is blocked in this harness, so never poll in a sleep loop. Run
`gh pr checks <n> -R "$OWNER_REPO" --watch --interval 20` in the background (or a Monitor until-loop)
and act on the completion notice. For waits over ~10 minutes, poll REST
(`gh api repos/$OWNER_REPO/actions/runs/<id> --jq .status`) to spare GraphQL quota.

All green: 8.5. Any failure: Stage 9.

**Preview deploys** (Vercel, Netlify, CF Pages): wait for the bot's check, take the URL, curl it,
expect 2xx and the content marker. A 5xx or wrong content blocks the merge. Poll-cron and
self-hosted mechanisms have no preview; Stage 11 covers them.

## Stage 8.5 - review decision

`gh pr checks` reports the `review` JOB, which succeeds whether the verdict was approve or
request-changes. The verdict lives on the PR. Read it on every repo: a repo without the gate returns
a harmless answer.

```bash
gh pr view "$PR_NUMBER" -R "$OWNER_REPO" --json reviewDecision,reviews \
  --jq '{decision: .reviewDecision, last: (.reviews | map(select(.author.login=="claude")) | last | {state, body})}'
```

| `reviewDecision` | Do |
|---|---|
| `APPROVED` | Stage 10 |
| `""` / null | No review requirement: Stage 10 |
| `CHANGES_REQUESTED` | Review fix loop, below |
| `REVIEW_REQUIRED` | Decide which of the three cases it is, below |

`REVIEW_REQUIRED` has three causes, and only one of them means waiting:
1. **The `review` job is still running.** Wait as for a check.
2. **The review ran and could not approve.** It posts a comment starting `## Review gate FAILED`
   naming the cause: a dead or out-of-quota token (an operator action; name the secret
   `CLAUDE_CODE_OAUTH_TOKEN`), or the reviewer ran out of turns (push again or split the PR). Read
   it; do not guess.
3. **A human is required.** The PR touches a CODEOWNERS path, edits `pr-review.yml`, or was opened
   by a bot. Report which, name who can approve, exit **BLOCKED-ON-HUMAN**. Do not poll for a review
   no automation will post.

**Review fix loop** (shares the 3-strike count with Stage 9). Findings carry severity `blocking`,
`should_fix` or `nit`; only `blocking` causes the request-changes.
1. Verify each blocking finding against the code before acting.
2. Right: fix at root cause, commit `fix(review): ...`, push, back to Stage 8.
3. Wrong: never dismiss the review yourself. Reply on the PR with evidence, push the test or comment
   that makes the point checkable, and let the re-run decide.
4. `should_fix`: fix in the same push when cheap, else a backlog row. `nit`: your call.

After 3 attempts: report every finding and response, write history `outcome: review-unresolved`,
leave the PR open, exit BLOCKED. Never merge, never dismiss.

## Stage 9 - CI fix loop (max 3 attempts)

```bash
gh run view <failed-run-id> -R "$OWNER_REPO" --log-failed | tail -200
```

Read the log and understand it. Check `patterns_observed` first: a known shape whose fix worked gets
that fix first; one whose fix failed gets something different.

| Failure | Strategy |
|---|---|
| Linter / formatter | the project's own tool with `--fix` / format |
| Typechecker | read the error at file:line, smallest correct change; never `@ts-ignore` or `# type: ignore` |
| Test failure | read the assertion; usually the code is wrong, rarely the test (only if the test predates the code); never skip it |
| Build error | root cause; a missing CI env var: name the exact variable |
| Dependency / lockfile | regenerate, `audit fix`, or pin the conflicting peer; check history for what worked |
| Network, rate limit, 5xx, timeout | on a write, Stage 7 rule first; for CI prefer `gh run rerun` over re-pushing |
| Flaky test | match history; retry once; still flaky: report, never quarantine without an operator decision |
| Disk / runner exhaustion | not auto-fixable: report and abort |
| Auth / rotated credential | operator action: name the secret and where to update it |
| Registry permission (GHCR 403) | workflow `permissions:`, package ACL, expired PAT: give the fix |
| Unknown shape | state the hypothesis, smallest fix, record the outcome in history either way |

Commit `fix(ci): ...`, push, back to Stage 8. After 3 attempts: report each attempt and why it
failed, write history `outcome: ci-unfixable`, leave the PR open, exit BLOCKED.

## Stage 10 - merge

Pre-condition: CI green AND review approved or not required AND preview verified or none.

```bash
GH_SHIP_ACTIVE=1 gh pr merge "$PR_NUMBER" -R "$OWNER_REPO" --squash    # NEVER --delete-branch
```

`--delete-branch` deletes before the Stage 11.5 gate and without asking whose branch it is. Both
branches stay until Stage 12.

`--admin` only as a recorded, deliberate exception; where `enforce_admins=true` it cannot work, so
fix the PR instead. Check the real protection: `gh api repos/$OWNER_REPO/branches/<default>/protection`.

Failures: conflict, Stage 8.0. Branch protection, report the requirement and exit. GraphQL limit,
`gh api repos/$OWNER_REPO/pulls/<n>/merge -X PUT -f merge_method=squash`. Network: Stage 7 rule, then backoff. A "not fast-forward"
error right after a successful squash merge is normal: confirm with `gh pr view --json
state,mergeCommit` (Stage 7 rule).

## Stage 11 - verify production

**11.1** Wait for post-merge CI on the default branch (background, as in 8.1). A failure means broken
code is live: report loudly, skip the rest of 11, never clean up past it.

**11.2** Wait for the deploy found in 0d. Vercel, Netlify, CF: the deployments API for
`state=success` (`?sha=` needs the full 40-character SHA). Fly: the workflow or `flyctl status`.
Poll-cron: compare the deployed sha with origin's tip until they match. None: record "no deploy
mechanism".

**11.3** At the real public URL (`$PROD_URL`, else `package.json` `homepage`, else the repo's
`homepage`): `curl -s -o "$TMPDIR/prod" -w "%{http_code}" --max-time 30 -L "$PROD_URL"`. HTTP 200 and
an expected content marker. An immutable preview URL often 401s and proves nothing about public
reachability.

**11.4** `post_merge_verify` in `recovery.md`: the merge sha is an ancestor of `origin/<default>`.
If not, stop before cleanup and surface it.

Shipping several PRs in a row: finish 11 for each before merging the next.

## Stage 11.5 - verified-merge gate

Apply `verify_branch_merged` (`recovery.md`) to each branch Stage 12 may delete, using the order in
`SKILL.md` "Branch deletion rule". **Run the gate, read its output, then delete in a separate
command.** Never put the check and the delete in one command block.

## Stage 11.7 - proactive audit (when due)

Run `audit.md` when ANY holds: the history has no `audit` date for this repo in the last 14 days;
the diff touches `.github/workflows/`, a deploy config or branch-protection-related files; or the
operator asked. Otherwise record `audit: skipped, last ran <date>`. Fixes go in their own PR (12.5),
never in this one.

## Stage 12 - cleanup

`git checkout <default> && git pull`. For each branch in `SESSION_BRANCHES_CREATED` that cleared
11.5: `git branch -d`, falling back to `-D` only on the 11.5 result; then
`GH_SHIP_ACTIVE=1 git push origin --delete <branch>` and `git fetch --prune`.

**Then sweep, for every session's leftovers:** `sweep_merged_local <default>` (`recovery.md`), with
`WIP_PROTECTED` set from history. It prunes dead worktree entries and deletes only local branches
identical to a merged PR head and not checked out, so no one's unshipped work can be lost. Report its
counts. Everything it keeps is reported as merged-with-later-commits, in progress (open PR) or orphan
(no PR, needs review), never deleted.

**Remote side:** if `gh api repos/$OWNER_REPO --jq .delete_branch_on_merge` is `false`, turn it on
(`gh api -X PATCH repos/$OWNER_REPO -F delete_branch_on_merge=true`) and say so in the SITREP. It
deletes only the GitHub copy of a merged PR's head branch, never anything local, and the PR page can
restore it. This is not `--delete-branch`, which also deletes the LOCAL branch.

Confirm the tree is clean apart from `FOREIGN_PATHS`, which must still be present and unmodified.
Restore your own stash only if you made one.

## Stage 12.6 - mirror sync

**Only when `.gh-ship-mirrors` at the repo root declares one** (one URL per line, `#` comments).
None: record "no mirror declared" and skip. **Never infer a mirror** from a same-named repo or a
remote: this stage force-pushes. Runs only after Stage 11 verified the merge and Stage 12 finished, so `--prune` carries this run's branch
deletion.

```bash
git clone --mirror <origin-url> "$TMPDIR/mirror.git" && cd "$TMPDIR/mirror.git"
GH_SHIP_ACTIVE=1 git push --force --prune <mirror-url> 'refs/heads/*:refs/heads/*' 'refs/tags/*:refs/tags/*'
```

- **Push only from a fresh `--mirror` clone, never from the working repo.** A working repo lacks
  remote-only branches, so `--prune` from it deletes them on the mirror.
- Not `git push --mirror`: GitHub rejects the source's hidden `refs/pull/*`.
- `--force` is required: nothing originates in a mirror, and without it a rewritten branch is
  rejected while `main` succeeds, so the push looks fine and the mirror drifts.
- Verify **per branch by SHA**, never by count: `gh api repos/<repo>/branches --paginate --jq
  '.[] | .name+" "+.commit.sha' | sort` on both sides; same names, same SHAs, nothing extra.
- This is the one sanctioned push that includes the default branch (the mirror's), and the one bare
  `--force`: SKILL.md rules 5 and 9 name it.
- A mirror failure never fails the run: it is a loud SITREP line and a suggested next step.
- Never branch-protect a mirror or enable Actions on it; a compliance flag gets a documented
  exception, since the control is met on the source.

## Stage 13 - history

Write one row in the `recovery.md` schema, for EVERY run including blocked, unfixable and rolled
back. `duration_seconds` is `$(( $(date +%s) - START_EPOCH ))`. Update `patterns_observed` for each
CI failure (shape, count, whether the fix worked). Unknown detail goes in `notes`, never a new key.
**Never commit here:** gitignored file, append in place; tracked file, append to
`.git/gh-ship-history.pending.json` (the next run's Stage 2.5 folds it with `history-fold.py`).

## Stage 14 - SITREP

**Lead with the verdict in the operator's terms:** "Shipped: PR #N merged, deploy verified at <url>"
or "Not merged: blocked on X". Then, briefly:
- PR, branch, duration, CI and review attempts, auto-fixes applied
- preview and production URLs, each with its verified status
- Stage 2.5 outcome per check
- audit: findings split into auto-fixed and surfaced, or "skipped, last ran <date>"
- cleanup: deleted, and pre-existing branches with their disposition
- foreign paths left untouched (count)
- sibling repo state
- mirror: the per-branch SHA comparison, not the push exit code
- history: row written, pattern count, new patterns this run

End with "Suggested next": `/monitor` after a verified deploy, `/investigate` after a 3-strike
failure, nothing after a docs-only change.
