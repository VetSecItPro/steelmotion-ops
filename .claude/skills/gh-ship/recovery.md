# /gh-ship - recovery, verification helpers, resilience

Read before any destructive action, and on any failure.

## Verify before destroy

### `post_merge_verify <pr>` (Stage 11.4)

Strict: the merge commit must be on the default branch. No fallback; if this fails, stop before
cleanup and surface it.

```bash
post_merge_verify() {
  local pr="$1" base="${2:-main}" sha
  sha=$(gh pr view "$pr" -R "$OWNER_REPO" --json mergeCommit --jq '.mergeCommit.oid' 2>/dev/null)
  [ -n "$sha" ] || { echo "NO MERGE COMMIT"; return 1; }
  git fetch -q origin "$base" && git merge-base --is-ancestor "$sha" "origin/$base" \
    && { echo "merge $sha on origin/$base"; return 0; }
  echo "NOT ON origin/$base: $sha"; return 1
}
```

### `verify_branch_merged <branch>` (Stage 11.5)

Signals in the order of `SKILL.md` "Branch deletion rule". Any one is sufficient. Print which one
fired; read it before the delete, which is a separate command.

```bash
verify_branch_merged() {
  local branch="$1" base="${2:-main}" m
  # 1. PR state MERGED - does not decay, so it is the one to use for any later cleanup
  m=$(gh pr list -R "$OWNER_REPO" --head "$branch" --state all --json state --jq 'map(select(.state=="MERGED")) | length' 2>/dev/null) || m=0
  case "$m" in ''|*[!0-9]*) m=0 ;; esac
  [ "$m" -gt 0 ] && { echo "pr-merged"; return 0; }
  # 2. content equivalence, TWO dots, valid only right after the merge: once the base moves on the
  #    same files, a merged branch shows a diff again (reads as unmerged: safe direction)
  git fetch -q origin "$base"
  [ -z "$(git diff "origin/$base".."$branch")" ] && { echo "content-identical"; return 0; }
  # 3. ancestor - only after a merge-commit merge; a squash rewrites the sha
  git merge-base --is-ancestor "$branch" "origin/$base" 2>/dev/null && { echo "ancestor"; return 0; }
  echo "UNMERGED - DO NOT DELETE"; return 1
}
```

### `sweep_merged_local` (Stage 12, after this run's own cleanup)

Removes local clutter left by ANY session, but only what is provably redundant, so it can never
cost anyone unshipped work:
- `git worktree prune` drops only worktree entries whose directory no longer exists;
- a local branch is deleted only when its name AND tip commit equal the head of a MERGED PR, and no
  worktree has it checked out. One commit added after the merge, by anyone, and it is kept.

Everything else is counted and reported, never deleted. Branches in `wip_branches_protected` are
passed in `WIP_PROTECTED` (one per line) and always kept.

```bash
sweep_merged_local() {
  local base="${1:-main}" merged co b tip del=0 kept=0
  git fetch -q --prune origin
  git worktree prune -v
  merged=$(gh pr list -R "$OWNER_REPO" --state merged -L 1000 --json headRefName,headRefOid \
           --jq '.[] | .headRefName+" "+.headRefOid') || { echo "PR list failed: sweep skipped"; return 1; }
  co=$(git worktree list --porcelain | sed -n 's|^branch refs/heads/||p')
  while read -r b tip; do
    [ "$b" = "$base" ] && continue
    if printf '%s\n' "$co" "${WIP_PROTECTED:-}" | grep -qxF -- "$b"; then kept=$((kept+1)); continue; fi
    if printf '%s\n' "$merged" | grep -qxF -- "$b $tip"; then
      git branch -D -- "$b" >/dev/null && del=$((del+1))
    else kept=$((kept+1)); fi
  done < <(git for-each-ref --format='%(refname:short) %(objectname)' refs/heads)
  echo "sweep: deleted=$del kept=$kept (kept = not identical to a merged PR head, checked out, or protected)"
}
```

**Why this exists.** A cleanup loop once saw a branch with no PR and could have deleted it as
"unmerged garbage" when it was in-progress work. Two rules came out of that: only auto-delete
branches THIS run created, and content-verify before every delete.

## Rollback

On catastrophic failure at any stage:

```bash
git checkout "$ORIGINAL_BRANCH" 2>/dev/null || git checkout -
git reset --hard "$ORIGINAL_COMMIT"

for b in "${SESSION_BRANCHES_CREATED[@]}"; do          # ONLY session-created
  [ "$b" = "$ORIGINAL_BRANCH" ] && continue
  git branch -D "$b" 2>/dev/null
  GH_SHIP_ACTIVE=1 git push origin --delete "$b" 2>/dev/null
done

[ -n "$PR_NUMBER" ] && gh pr close "$PR_NUMBER" -R "$OWNER_REPO" --comment "Rolled back due to error"
```

**`reset --hard` only when the tree holds no foreign paths.** If another session has uncommitted work
here, do NOT reset - undo your own commits with `git reset --soft` or revert specific paths, and say
in the SITREP that a full rollback was withheld to protect concurrent work. Losing someone's
in-flight edits is worse than an untidy rollback.

Restore your own stash only if this run created it.

## Self-healing

| Situation | Recovery |
|---|---|
| Deleted a branch that had unmerged work | `git reflog \| grep <branch>` then `git branch <name> <sha>` |
| Force-pushed the wrong content | `git reflog show origin/<branch>`, then `git push origin <good-sha>:<branch> --force-with-lease` |
| Merged a bad PR | `git revert -m 1 <merge-sha>` on the default branch, then push through a PR |
| Stash lost | `git fsck --lost-found`, look in `.git/lost-found/` |
| Helm/deploy release stuck mid-upgrade | roll back to the last good revision, then re-run the deploy |
| `.git/index.lock` left behind | remove it and retry - a transient from a killed git process |
| Interactive `rm`/`cp` alias hangs the run | call the binary directly (`/bin/rm -f`, `/bin/cp -f`); never answer the prompt blind |

## Network resilience

```bash
retry_with_backoff() {         # 2s, 5s, 10s; on a WRITE, check whether it landed first (stages.md Stage 7)
  local d
  for d in 2 5 10; do "$@" && return 0; sleep "$d"; done
  "$@"
}
```

GitHub has separate GraphQL and REST rate limits. When GraphQL is exhausted, the same operation
usually works over REST - `gh api` hits REST. Prefer REST polling (`gh api repos/.../actions/runs/<id>`)
over `gh pr checks --watch` for long waits, to preserve GraphQL quota.

## Abort conditions

Stop and report rather than pressing on:

- CI unfixable after 3 attempts - leave the PR open
- Branch protection blocks the merge and no legitimate path exists
- A secret was found already pushed - rotation is the priority, not shipping
- The working tree contains foreign changes that a required operation would destroy
- Post-merge CI fails on the default branch - broken code is live; that is an incident, not a cleanup

Every abort still writes the history entry and emits a SITREP. A silent failure teaches nothing.


## History schema (`.gh-ship-history.json`, schema_version 2)

Written at Stage 13, read at Stage 0 (0e). Respect the repo's tracking policy from `SKILL.md`.

**Every key below is written on every row, using these exact names and values.** Anything else goes
in `notes`. Why: free-form rows (about 190 distinct keys across 521 rows, 2026-10-17) and
success-only history left the pipeline unable to measure itself. Older rows stay as they are (dated records); new rows use this shape. A file that is a bare
list or has no `schema_version` gets wrapped as `{"schema_version": 2, "runs": [...]}` on the next
write, with the old rows untouched.

```json
{
  "schema_version": 2,
  "runs": [{
    "run_id": "2026-10-17T13:40:05-05:00",
    "repo": "owner/name",
    "pr": 42,
    "branch": "fix/thing",
    "branch_created_this_run": true,
    "duration_seconds": 412,
    "ci_attempts": 1,
    "review_attempts": 0,
    "ci_failures": [{"shape": "eslint-no-unused", "fix": "lint --fix", "worked": true}],
    "outcome": "success",
    "deploy_verified": "yes",
    "audit": "ran",
    "mirror": "none-declared",
    "foreign_paths_left_untouched": 3,
    "anomalies": [],
    "notes": ""
  }],
  "patterns_observed": {
    "<failure-shape>": {"first_seen": "2026-05-03", "count": 4, "fix_known": true,
                        "last_successful_fix": "regenerate lockfile then re-push"}
  },
  "wip_branches_protected": ["feature/long-running-thing"]
}
```

| Key | Values |
|---|---|
| `run_id` | `TZ=America/Chicago date +%Y-%m-%dT%H:%M:%S%z`, Central, with offset |
| `ci_attempts` | number of CI runs on this PR, first one included; 0 for a repo with no CI |
| `outcome` | `success` \| `blocked-on-human` \| `review-unresolved` \| `ci-unfixable` \| `aborted` \| `rolled-back` |
| `deploy_verified` | `yes` \| `no` \| `n/a` |
| `audit` | `ran` \| `skipped`; the last audit date is the `run_id` of the newest row with `ran` |
| `mirror` | `synced` \| `failed` \| `none-declared` |

`wip_branches_protected` is sticky: once a branch is listed there, no later run may auto-delete it.
`patterns_observed` is what makes the next run try a known-good fix before inventing one. Record
failures too: knowing a fix did NOT work is what stops it being retried.
