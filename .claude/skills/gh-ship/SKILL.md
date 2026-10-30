---
name: gh-ship
description: "Disciplined git pipeline: validate, commit with a generated semantic message, push, open a PR, watch CI, fix failures at root cause, merge, verify the deploy, clean up, and learn from the run. Adapts to the repo's language, CI engine and deploy mechanism rather than assuming a stack."
when_to_use: 'Trigger phrases: "ship it", "commit and push", "create PR", "deploy", "get this live", "push this". This is the ONLY sanctioned path for git push / gh pr create / gh pr merge - the gh-push-guard hook blocks those commands elsewhere.'
disable-model-invocation: false
---

# /gh-ship - disciplined git pipeline

**This file is the spine and stays in context through compaction.** Detail lives beside it:

| File | Read it at | Holds |
|---|---|---|
| `stages.md` | Stage 0, then as each stage begins | per-stage procedure, detection tables, CI fix strategies |
| `recovery.md` | any failure, or before a destructive action | rollback, verify-before-destroy helpers, history schema |
| `audit.md` | Stage 11.7 and 12.5, when they run | proactive repo audit, CI workflow improvement |
| `provenance-archive.md` | never during a run | the incidents and measurements behind each rule |

**Related skills.** Feeds from `/test-ship`, `/sec-ship`, `/smoketest`, `/subagent-dev`. Feeds into
`/monitor` (post-deploy) and `/qatest` (QA the preview). Stage 2.5 calls `/docs-sync`. `/worklog` is
the session journal and deliberately not part of this pipeline.

## Paradigm

A plan Claude executes, not a script to replay. Detect the repo's language, CI engine and deploy
mechanism each run; never assume Node, Vercel or GitHub Actions. Read a failure and reason about it;
never keyword-match a log to a canned fix.

## Non-negotiables

1. **Stage by path, never `git add -A` blind.** Another session's work stays out of your commit.
2. **Never stash, check out, restore or reset work you did not create.**
3. **No `Co-Authored-By` trailer and no Claude attribution** in commits or PR bodies.
   (`attribution` is off in `~/.claude/settings.json`; if the harness asks for a trailer anyway,
   this rule wins and the SITREP says so.)
4. **Never bypass a safety hook.** No `--no-verify`. A failing pre-commit hook gets its cause fixed.
5. **Verify before destroying.** Every branch delete follows the Stage 11.5 gate. Every force push
   is `--force-with-lease`; the only bare `--force` is the Stage 12.6 mirror push.
6. **Deploy verified = HTTP 200 at the real URL plus an expected content marker.**
7. **3-strike rule.** After three failed fix attempts (CI and review share the count), stop and
   escalate.
8. **Leave the repo no dirtier than you found it:** branches cleaned, no stray stash, history
   recorded, foreign paths untouched.
9. **The push-guard bypass is per command.** Prefix every `git push`, `gh pr create` and
   `gh pr merge` with the literal `GH_SHIP_ACTIVE=1`. `export` does nothing: shell state does not
   persist between tool calls, and the guard matches the command text. Never prefix a push whose
   target is the default branch (the Stage 12.6 mirror push is the one exception); the bypass is for
   the pipeline's own branch. **Enforced since 2026-10-18:** the guard refuses a prefixed push that
   resolves to the default branch (`HEAD` while on it, an explicit name, a delete, `--all`).
10. **No quiet-failure shell idioms in a gate.** Never `$(cmd || echo 0)`, `grep ... | head || echo
    clean`, or `>` onto a file that may exist under zsh `noclobber`. Each has produced a plausible
    wrong answer in this pipeline. Capture the exit status separately, force numbers numeric, and
    write files with `>|` or to a fresh path.

## Working tree safety (before Stage 0 does anything)

`/gh-ship` often runs while another session edits the same repo. Run `git status --porcelain` first
and classify every dirty path:

| Path | Rule |
|---|---|
| Created or edited by this session | yours: stage it explicitly by path |
| Anything else | **foreign: do not stage, stash, check out, restore or reset it** |

A broad add, when genuinely right, excludes each foreign path by name:
`git add -A -- ':!<foreign-1>' ':!<foreign-2>'`. Stash only your own paths
(`git stash push -- <paths>`). Name the foreign paths in the SITREP: "left untouched: N files".
A worktree, or a `.claude/worktrees/` directory, means assume concurrency.

## Stages

| # | Stage | Must not be skipped |
|---|---|---|
| 0 | Pre-flight: tree classification, exclusion check, `gh` auth, detection, history read | all of it |
| 0.5 | Sibling-repo scan | report siblings; never ship them |
| 1 | Local validation | the repo's real lint/typecheck/test/build; fix, never suppress |
| 2 | Analyze changes | categorize; nothing left after safety filtering = exit early |
| 2.5 | **Record what this ships** | changelog, backlog rows, lessons, ADR, `/docs-sync`, `history-fold.py` (prints waiting rows); **before the commit**; every check states an outcome |
| 3 | Commit message | `<type>(<scope>): <description>`, body says WHY |
| 4 | Stage and commit | explicit paths, including every Stage 2.5 file |
| 5 | Branch | on the default branch: create one and record it as session-created |
| 6 | Push | read the current branch, push it BY NAME; conflicts: merge the base in, never rebase a pushed branch |
| 7 | Open PR | reuse an existing PR; after a 5xx or timeout on ANY write, check whether it landed before retrying |
| 8 | CI + preview | **`.mergeable` BEFORE waiting**; expected check count before any verdict |
| 8.5 | **Review decision** | read `reviewDecision`; `CHANGES_REQUESTED` = fix loop; a human-only review = exit BLOCKED-ON-HUMAN |
| 9 | CI fix loop | root cause only, max 3 attempts shared with the review loop |
| 10 | **Merge** | CI green AND review approved or not required AND preview verified or none; **`--squash`, never `--delete-branch`** |
| 11 | **Verify production** | HTTP 200 + content marker; merge sha on the default branch |
| 11.5 | **Verified-merge gate** | before any branch delete |
| 11.7 | Proactive audit | when due (see `stages.md`); otherwise record "skipped, last ran <date>" |
| 12 | **Cleanup** | delete this run's branch; then sweep only what is provably redundant (dead worktrees, branches identical to a merged PR head); ensure `delete_branch_on_merge` |
| 12.5 | CI improvement PR | only when 11.7 found workflow fixes; separate PR, never auto-merged |
| 12.6 | Mirror sync | only when `.gh-ship-mirrors` declares one; never infer a mirror |
| 13 | History | one schema row (`recovery.md`), success OR failure; **never commits** |
| 14 | SITREP | verdict first; ends with "Suggested next" |

**Stages 10-13 are what a long run loses to compaction.** Stage 11.5 gates the only destructive
action in the pipeline. Deletion happens in Stage 12 or not at all.

## Branch deletion rule

Delete branches in `SESSION_BRANCHES_CREATED`, plus whatever `sweep_merged_local` proves redundant
(name and tip identical to a merged PR head, not checked out). Any other pre-existing branch is
someone's possible work in progress: report it, never remove it. Before deleting this run's branch:

1. its PR is in state `MERGED` (does not decay; use this for any later cleanup), or
2. `git diff <default>..<branch>` is empty, **two dots**, and only immediately after the merge
   (once the default branch moves on the same files, a merged branch shows a diff again), or
3. the branch is an ancestor of the default branch (rare after a squash merge).

## History file

`.gh-ship-history.json` is read at Stage 0 and written at Stage 13 using the schema in
`recovery.md`. **Tracked or ignored is the repo's choice:** if `git ls-files --error-unmatch` says
tracked, Stage 13 appends to `.git/gh-ship-history.pending.json` and the next run's Stage 2.5 folds
it in; a `.gitignore` comment stating a policy is obeyed; neither means gitignore it and say so.
**Failed and blocked runs get a row too.** A history of only successes measures nothing.

## Rationalization defense

| Rationalization | Do |
|---|---|
| "CI usually passes, skip the wait" | Wait. Read the result. |
| "No checks reported, GitHub must be down" | `.mergeable` first: a conflicted PR runs NO workflows and says so nowhere |
| "It's a platform bug my probes cannot see" | Ask what state YOUR branch is in before blaming the infrastructure |
| "All checks passed" (over a partial list) | Count expected checks first; a verdict over the first few to register is not one |
| "Checks are green, so it is mergeable" | Stage 8.5: the review verdict is on the PR, not in the check list |
| "The bot is wrong, dismiss it" | Reply with evidence, push the commit that makes it checkable, let the re-run decide |
| "The write 502'd, retry it" | Check whether it landed; "already exists" is success |
| "This test is probably flaky" | Investigate; quarantine only with an explicit operator decision |
| "PR says merged, safe to `-D`" | Was it created by this run? Then the 11.5 gate, then delete |
| "`--delete-branch` saves a step" | It skips both gates and does not ask whose branch it is |
| "Deploy finished, skip verification" | curl the URL, check the marker |
| "I will update the docs after the merge" | Stage 2.5, before the commit, or they ship in the wrong PR |
| "Nothing to record, skip 2.5 quietly" | State the outcome for every check |
| "That old record is stale, fix it" | Append a dated correction; never edit a record |
| "This repo probably has a mirror" | Only `.gh-ship-mirrors` counts |
| "Same branch count on both sides" | Compare per branch by SHA |

## Definition of done

- Stage 2.5 stated an outcome for every check, and every file it wrote is in the PR diff
- CI green, PR merged, merge sha confirmed on the default branch
- Deploy verified at the real URL, or recorded as "no deploy mechanism"
- Session-created branches deleted local and remote; pre-existing ones reported, untouched
- Declared mirrors synced with per-branch SHA parity, or "no mirror declared"
- No stray stash; foreign changes still present and untouched
- History row written per the repo's policy, with the schema's `outcome` vocabulary
- SITREP emitted, verdict first, ending with "Suggested next"

If it cannot ship, roll back per `recovery.md`, write the history row, and say so. A half-shipped
state is worse than a refusal.
