# /test-ship - report, SITREP

## Report

`.test-reports/TEST-<YYYYMMDD-HHMM>.md`.

```markdown
# Test Coverage Report: <project>
**Runner:** <vitest/pytest/...>  |  **Suite before:** <N passing>  |  **After:** <M passing>
**Mode:** <full | audit | setup | unit | e2e | file>

## Coverage by risk seam
| Seam | Before | After | Note |
|---|---|---|---|
| Auth / middleware | uncovered | 8 tests | the highest-risk gap, closed first |
| API handlers | 3/11 | 11/11 | missing-auth, bad-body, happy, downstream-fail each |
| lib/ pure logic | 40% | 88% | |

## Tests added
- <file> - <what behaviour> - proven-fails: yes

## Gaps remaining
- <target> - <why deferred: blocked on X / low risk / needs refactor>

## Flagged for refactor
- <file> - untestable without <heroics>; recommend <change>
```

## SITREP

Lead with the delta: "+N tests, suite X -> Y, auth seam now covered." Then the seam table, then what
remains. The single most useful line is which silent-failure seams are now covered - that is the
risk this skill exists to reduce.

### Suggested next

| Outcome | Recommend |
|---|---|
| Coverage filled, suite green | `/gh-ship` |
| A gap was a real bug the test caught | fix it, keep the test as the regression |
| Untestable code found | `/cleancode` or a targeted refactor, then re-run |
| E2E gaps on critical flows | `/qatest` for the full UAT sweep |

## Design notes

**Prove-it-can-fail is the core discipline.** The most common way test suites lie is tests that pass
against broken code. Watching each new test go red first is cheap insurance against a green suite that
verifies nothing.

**Risk order, not ease order.** Auth seams are harder to test than getters, and matter a hundred times
more. A suite built by ease covers the wrong things thoroughly.

**Count, don't percentage.** "+22 tests, 1088 -> 1110" is a claim that can be checked and that maps to
work done. A coverage percentage can rise while the risky code stays uncovered.

**Remediation, not replacement.** This skill closes gaps after the fact. It does not license shipping
logic without tests and cleaning up later - that is how the gaps appear.
