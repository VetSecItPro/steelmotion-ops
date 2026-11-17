# /architecture-survey - record, hand-off, SITREP

## Backlog rows

One row per `Strong` or `Worth exploring` candidate in the backlog the project's `CLAUDE.md` names
(usually `*-backlog.md` or `backlog.md`; if it lives in another repo, say which), written before the SITREP, numbered from the highest row of ANY status (an
IN PROGRESS row can be higher than the last DONE one; `grep -oE '^\| [0-9]+ ' <backlog> | sort -n |
tail -1`): title in glossary terms, rating, report path. A KNOWN
candidate gets a dated note on its existing row instead of a new one. `Speculative` candidates stay
in the report only.

## Hand-off

Order: the report (Phase 3), then the backlog rows, then each row number added to its card's
Status field, then the SITREP. After the report is open, ask one question: which candidate to explore. If the operator is not
present (a background or scheduled run), write the question and the recommended pick into the
report and the SITREP, and stop. Then:

| The pick | Hand to |
|---|---|
| Reversible, local to one area | `/brainstorm`, seeded with the card (files, evidence, direction) and `vocabulary.md` |
| Expensive to reverse, crosses areas, or several real options | `/mdmp` |
| None, or "later" | stop; the rows are the record |

In the hand-off, the writer duties in `standards/DOMAIN_LANGUAGE.md` apply: a new module named after
a concept not in `GLOSSARY.md` adds the term; a fuzzy term sharpened in conversation is written in
right away. **A candidate the operator rejects for a load-bearing reason** gets a decision record
offered where the repo keeps them (the three tests in `DOMAIN_LANGUAGE.md`), so the next survey does
not propose it again. A repo with no records: put the reason on the backlog row.

Implementation is never part of this skill. A designed change goes through the normal path: tests
first at the agreed seam (`/test-ship`), then `/gh-ship`.

## SITREP

Lead with the verdict on what was asked: "Top pick: <candidate>. <N> candidates, <S> Strong." or
"No restructuring needed. <N> modules surveyed." Then the scope line (window, commits), the coverage
line (read / total modules), the candidate list one line each with rating and status, the leave-alone
count, the report path and the backlog rows written. Close on status: surveyed-awaiting-pick,
handed-off-to-<skill>, or no-action.

### Suggested next

| Outcome | Recommend |
|---|---|
| Operator picked a candidate | `/brainstorm` or `/mdmp` per the table above |
| Top pick blocked by missing tests at the seam | `/test-ship` on that area first |
| Findings are dead code or long functions, not module shape | `/cleancode` |
| Glossary absent and naming caused confusion during the survey | offer to start one in the hand-off (operator present), never seed it alone |

## Cleanup

Read-only skill: nothing to stop except the explore sub-agent (`TaskStop` once its report is
handled). Reports stay in `.reports/architecture-survey/` as the record for the next run's Phase 0.
