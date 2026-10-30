# /cleancode - report, SITREP

## Report

`.cleancode-reports/CLEAN-<YYYYMMDD-HHMM>.md`.

```markdown
# Cleanup Report: <project>
**Suite:** green before (<N> passing) / green after (<N> passing)
**Mode:** <full | dead | dupe | complexity | file>

## Reduction
| Metric | Before | After | Delta |
| lines of code | 42,100 | 40,830 | -1,270 |
| files | 312 | 305 | -7 |
| dependencies | 84 | 81 | -3 |
| avg complexity (touched) | 14 | 8 | -43% |

## Removed (proven dead)
- <symbol/file> - proof: <tool + no dynamic refs>

## Refactored (behaviour unchanged)
- <what> - <before -> after> - covered by <test>

## Reported, not changed
- <candidate> - <why left: untested and coverage not cheap / deliberate pattern / uncertain>
```

## SITREP

The reduction delta first - the point of the skill is measurable debt removed. Then what was removed
(with its proof), then what was deliberately left and why. A cleanup SITREP that says "cleaner" with
no numbers has not shown its work.

### Suggested next

| Outcome | Recommend |
|---|---|
| Cleanup done, suite green | `/gh-ship` |
| Found untested code blocking a refactor | `/test-ship` on it, then re-run `/cleancode` |
| Removed dependencies | `/deps` to confirm the lockfile is clean |
| Complexity remains but is untestable | flag for a design discussion, not a blind refactor |

## Design notes

**Prove, don't assume.** The single rule that keeps cleanup from being a bug source. Static analysers
miss dynamic references; the grep-for-dynamic-use step is what catches the route file, the
string-keyed handler, the config reference that the tool called dead.

**Conservative beats thorough.** A cleanup that removes 80% of the debt with zero regressions is a
success; one that removes 100% and breaks a flow is a failure. When unsure, report rather than remove.

**Not-debt is not a target.** The urge to rewrite working code to taste is where cleanup does harm -
risk with no payoff. Debt is duplication that will diverge, code that is provably dead, complexity
that genuinely obscures. Style preference is not debt.

**De-duplication can be debt.** Coupling two things that look alike but model different concepts is
worse than the duplication. Only extract what must change together.
