# Verify Before Destroy

**Reference standard for skills that perform destructive operations.** Every destructive action is preceded by content-verification, not just metadata.

## When to apply

Apply to any skill that:
- Deletes files, directories, branches, tags, releases
- Force-pushes (git push --force, git reset --hard, etc.)
- Drops database tables / runs DESTRUCTIVE migrations
- Closes / abandons / archives work

Examples: `/gh-ship`, `/cleancode`, `/db`, `/migrate`, `/harden`

## Core principle

**Metadata can lie.** Content cannot. Always verify by content equivalence before destruction.

## Specific patterns

### Branch deletion (git)

`gh pr view` showing "MERGED" is NECESSARY but NOT SUFFICIENT to delete a branch:
- Squash-merge produces a NEW commit on main with different SHA than any commit on the source branch
- Local commits added to the branch AFTER the PR was opened may not have been pushed before the merge
- `git merge-base --is-ancestor <branch-sha> main` returns FALSE for squash-merged work even when fully on main

**Use this triangulation order:**

1. **Method 1 (ancestor)**: `git merge-base --is-ancestor <branch-sha> main` — catches merge-commit merges
2. **Method 2 (PR state)**: `gh pr list --head <branch> --state all` — catches squash-merge if PR exists
3. **Method 3 (content equivalence)**: `[ -z "$(git diff main...<branch>)" ]` — catches squash-merged + branch deleted on remote
4. If any of 1/2/3 returns true: branch IS merged, safe to delete
5. If all return false AND no PR exists: branch has unmerged work — DO NOT delete

### Recovery if you got it wrong

```bash
# reflog has the deleted SHA
git reflog | grep <branch-name>

# restore
git branch <branch-name> <SHA-from-reflog>
```

ALWAYS check reflog before assuming permanent loss.

### File / directory deletion

Before `rm -rf <path>`:
- Verify `<path>` is what you think (`ls -la <path>` + `head` of files)
- Backup if uncertain (`cp -r <path> <path>.bak-<date>`)
- Use `git status` to confirm whether the contents are tracked
- Document in SITREP what was deleted + what's in `.bak-<date>` for recovery

### Database operations

Before any DROP / TRUNCATE / DELETE WHERE:
- Snapshot the table (`pg_dump --table=...`)
- Run `EXPLAIN ANALYZE` on the destructive query first
- For migrations, store the down-migration alongside

## Session-ownership tracking

For skills that create + destroy resources within a single run:

```bash
SESSION_RESOURCES_CREATED=()
# ... in stage that creates things:
SESSION_RESOURCES_CREATED+=("<resource-id>")

# ... in cleanup stage:
# ONLY auto-destroy items in SESSION_RESOURCES_CREATED
# Pre-existing resources are inspect-only, never auto-deleted
```

This prevents the "destroyed pre-existing operator work" class of bug.

## Anti-patterns

- ❌ "PR shows merged → `git branch -D`" without content verification
- ❌ "auto-delete all branches matching `feature/*`" without ownership check
- ❌ `rm -rf node_modules` without checking the path is what you expect
- ❌ Force-push without `--force-with-lease`
- ❌ Database migrations without down-migration

## Application checklist

For any destructive-action-skill being audited:

- [ ] Document the verify-before-destroy pattern for each destructive action type
- [ ] Implement session-ownership tracking for created-then-destroyed resources
- [ ] Document recovery paths (reflog, backups, etc.)
- [ ] Add to CRITICAL RULES: "Verify by content; metadata can lie"
- [ ] Test: induce a near-miss scenario; verify the skill refuses to destroy
