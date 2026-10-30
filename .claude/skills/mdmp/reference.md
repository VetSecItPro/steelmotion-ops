# /mdmp - decision record, matrix, SITREP

## Decision record

`docs/decisions/` or `.mdmp-reports/MDMP-<YYYYMMDD>-<slug>.md`. This outlives the decision and is
the artifact people read in a year.

```markdown
# Decision: <one line>
**Date / Status:** <proposed | accepted | superseded by X>
**Decision criteria and weights:** <fixed at Step 2>

## Context
<the situation, the constraints, what forced a decision now>

## Options considered
### COA-1 <name>  [CHOSEN]
<approach, requirements, effort>
### COA-2 <name>  [rejected]
<approach> - **rejected because:** <reason>
### COA-3 <name>  [rejected]

## Lens findings
| Lens | COA-1 | COA-2 | COA-3 |
|---|---|---|---|
| Engineering / Product / Security / QA / Design / DevOps / Risk | <verdict + key concern> | | |

## Comparison
| Criterion | Weight | COA-1 | COA-2 | COA-3 |
|---|---|---|---|---|
| ... | 30% | 4 - <reason> | 2 - <reason> | 3 - <reason> |
| **Weighted total** | | **3.8** | 2.4 | 3.1 |

## Decision
<what, confidence, the trigger that would change it, what is given up>

## Assumptions
| Assumption | How validated | If false |
|---|---|---|

## Consequences
<what this makes easy, what it makes hard, what it locks in>
```

Where the project keeps ADRs, write it as an ADR in that catalogue and follow its numbering rather
than inventing a parallel store.

## SITREP

The recommendation and its confidence first - the reader wants the answer before the reasoning. Then
the matrix, then the rejected options with one-line reasons, then assumptions with their tests.

### Suggested next

| Outcome | Recommend |
|---|---|
| Decision approved | `/subagent-dev` to execute |
| A critical unknown blocked the decision | spike it first; re-run `/mdmp` with the answer |
| Scores within 10% | say the decision is close; choose the reversible one |
| Security lens rejected all COAs | `/sec-ship --audit` on the current state; the constraint may be elsewhere |

## Design notes

**Weights before options.** Choosing weights after seeing the COAs turns the matrix into a
justification for a decision already made. This ordering is the process's main defence against
motivated reasoning.

**The uncomfortable COA.** Requiring one option the team instinctively rejects is how the process
reaches beyond the first plausible answer. It is usually rejected - but it is rejected with a reason,
and occasionally it wins.

**Rejected options are the durable value.** In a year nobody asks why the chosen option was chosen;
they ask why the obvious alternative was not. That answer only exists if it was written down.
