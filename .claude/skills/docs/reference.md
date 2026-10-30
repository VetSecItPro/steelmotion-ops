# /docs - generation targets, report, SITREP

## Generation, by target

| Target | Contains | Verify by |
|---|---|---|
| README | what/why, quick start, setup, run, test, structure, conventions | running the setup + quick start |
| API reference | per export/endpoint: purpose (why), signature, auth, errors, example | validating each example against the code |
| Architecture | modules, data flow, key decisions + rationale, diagrams | comparing to the actual current structure |
| WHY comments | the reasoning behind non-obvious code | reading: does it explain something the code cannot say? |
| CHANGELOG | if the repo ships a versioned artefact and lacks one, scaffold it | the Keep-a-Changelog format |

Generate in the project's existing format and location. Never introduce a second documentation system
alongside one that exists.

## Report

`.docs-reports/DOCS-<YYYYMMDD-HHMM>.md`.

```markdown
# Documentation Report: <project>
**Mode:** <full | audit | readme | api | architecture | why>

## Coverage
| Dimension | Before | After | Note |
| README | stale (90d behind) | current | setup verified working |
| API | 4/12 endpoints | 12/12 | examples validated |
| Inline WHY | - | +14 added, 22 signature-echo removed | net -8 lines, +clarity |
| Architecture | absent | generated | matches current structure |

## Generated / updated
- <path> - <what> - verified by <how>

## Flagged for removal
- <path:line> - signature-echo comment adding no value

## Gaps remaining
- <what> - <why deferred>
```

## SITREP

Coverage delta first - what surface went from undocumented/stale to current. The single best line is
"README setup steps verified working", because that is the doc failure that costs a new contributor an
afternoon. Then generated, then removed (yes, removing noise counts), then remaining.

### Suggested next

| Outcome | Recommend |
|---|---|
| Docs current | `/gh-ship` |
| API spec drift found | `/sec-ship` Agent 16 for the security-relevant drift |
| Architecture doc revealed a design smell | `/mdmp` if it is a real decision |
| A decision worth recording | write an ADR in the project's catalogue |

## Design notes

**WHY over WHAT is the whole skill.** Most documentation effort is wasted restating code, producing
comments that echo signatures and rot on the next change. The discipline of documenting only what the
code cannot say for itself is what makes generated docs worth reading and worth maintaining.

**Removing docs is documentation work.** A signature-echo comment or a stale note is net-negative;
deleting it improves the codebase. Coverage is the right docs, not the most docs.

**Verify or it is fiction.** A generated setup guide that was never run, an API example never validated
- these are confident and wrong, the worst kind of documentation. Phase 3 exists because unverified
docs mislead with authority.

**Update the source of truth.** Where a project keeps living docs (an ADR catalogue, phase tech docs),
generating a parallel set creates two truths that immediately diverge. Update in place.
