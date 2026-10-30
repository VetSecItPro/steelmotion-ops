# /migrate - report, SITREP

## Report

`.migrate-reports/MIG-<YYYYMMDD-HHMM>.md`.

```markdown
# Migration Report: <from> -> <to>
**Status:** assessed | in-progress (stage <n>) | complete
**Branch:** <name>  |  **Guide:** <url read>

## Breaking changes affecting this codebase
| Change | Files affected | Handled by |
| App Router metadata API | 12 | codemod |
| removed `next/image` legacy | 4 | manual, per guide |

## Behaviour changes (deliberate, not silent)
- <default that changed> - <how it was handled> - <verified at runtime how>

## Stages
| Stage | Build | Tests | Commit |
| 1 config | green | green | <sha> |
| 2 codemods | green | green | <sha> |
| 3 manual API | green | green | <sha> |

## Runtime verification
<critical flows driven, result>

## Rollback
- branch abandon restores main fully, EXCEPT: <any one-way change>
```

## SITREP

Status and stage first. Then the breaking-change count and how each was handled (codemod vs manual),
then the deliberate behaviour changes with how they were verified, then the rollback note. The single
most important line for a framework major is which behaviour defaults changed - those are what surprise
people weeks later.

### Suggested next

| Outcome | Recommend |
|---|---|
| Complete, green, runtime-verified | `/qatest` for a full sweep, then `/gh-ship` |
| Assessed only | decide go/no-go; a large one may warrant `/mdmp` |
| Thin coverage on a migrated path | `/test-ship` before merging |
| Runtime behaviour shifted | `/monitor` after deploy to confirm the golden signals |

## Design notes

**Read the guide.** The rule that separates a migration from a gamble. The maintainers wrote down
exactly what breaks and how to fix it; not reading it means rediscovering all of that from red tests,
slower and with silent behaviour changes missed.

**Distinct from /deps.** A version bump and a framework migration are different jobs. Keeping them
separate means `/deps` stays a fast, safe, frequent operation and `/migrate` carries the heavier
staged-and-branched machinery only when it is actually needed.

**Stage and keep green.** A framework migration as one atomic change is the worst debugging experience
in software. Staged, each break points at its cause.

**Runtime, not just build.** The migrations that hurt are the ones that compile. A changed caching or
rendering default ships green and breaks in production; driving the app after is what catches it.
