# Backlog Standard

One format and one meaning for every project. The Task List page reads
these files, so a row that breaks this standard shows as a warning there.

## Status words

Every live row uses exactly one word.

| Word | Only meaning | Note must say |
|---|---|---|
| `OPEN` | Not started | Nothing required |
| `IN PROGRESS` | A session is working on it | Nothing required |
| `WAITING ON OPERATOR` | Only the operator can move it | Exactly what the operator must do |
| `BLOCKED` | Stuck on someone or something other than the operator | Who or what |
| `DONE` | Finished | Central date and time, and what shipped |
| `DROPPED` | Will not be done | The reason or the replacing row |

Retired on live rows: `PENDING`, `TODO`, `PARKED`, `DEFERRED` and `PARTIAL` become `OPEN`.
`NEEDS OPERATOR` and `WAITING` become `WAITING ON OPERATOR`. `CANCELLED`, `REJECTED`, `WONTFIX` and
`SUPERSEDED` become `DROPPED`. Finished rows are dated records: they keep the words they were written
with and are never rewritten.

## Row format

```
| # | Task | Status |
| --- | --- | --- |
| 12 | Add receipts | WAITING ON OPERATOR 2026-11-01 11:20 CT: paste the live key |
```

The last cell leads with the status word, then the Central stamp, then the note. Live rows sit under
`## Open` and finished rows under `## Done`. One row per line, with as many cells as its header: a bare `|`
inside a note splits the cell, so write it as `\|` (GitHub shows a pipe) or in words.

Older tables that keep the status in a middle column are still read. The checker and the sync hook use the
same rule: the status is the last cell, or else the last cell after the title that leads with a status word.

The status stamp is when the status last changed, not when the task began. The opening date goes in a column
headed `Opened`, or, in a table without one, as `Opened 2026-10-24 16:20 CT` in the note (capital O).
The Task List ages an ask by it. Take a lost opening date from the earliest match across all history
(`git log --all --reflog -S '| 12 |'`); main alone gives the squash-merge date, which is later.

Steps too long for a row go in `## Task notes` at the end of the file, under a `### #12` heading.

## Rules

1. **A question for the operator is a row.** If a session stops because it needs an answer, approval
   or action from the operator, it records a `WAITING ON OPERATOR` row before ending its turn. A
   question that exists only in chat is invisible to the Task List.
2. **Blocked on the operator is never `BLOCKED`.** That is `WAITING ON OPERATOR`.
3. **A project may keep several backlogs.** List each extra file, one per line, in `.backlog-paths` at
   the repo root.
4. **Old tables stay as written.** A log, ledger or dated table that is not live work gets a
   `<!-- backlog:history -->` line above it, and `<!-- backlog:live -->` where live rows resume. Nothing
   between the two lines is read, so no row has to be rewritten.
5. **New repos start from `~/.claude/templates/backlog.md`.** `/repo-bootstrap` copies it.

## Tooling

`python3 ~/.claude/check-backlog.py FILE...` checks a backlog. Exit 0 is clean and 1 lists findings.
With `--json` it returns the parsed rows that the Task List page uses, so there is one reader.
