# /deps - report, history, SITREP

## Report

`.deps-reports/DEPS-<YYYYMMDD-HHMM>.md`, written progressively.

```markdown
# Dependency Report: <project>
**Ecosystems:** <detected>  |  **Automation:** <renovate/dependabot + open PR count | none>
**Mode:** <full | audit | security | majors | unused | dedupe>

## Security advisories
| Package | Severity | Reachable? | Fix | Status |
|---|---|---|---|---|
| <pkg@ver> | high | yes (request path) | -> <ver> | FIXED |

## Updates applied
| Package | From | To | Kind | Tests | Commit |
|---|---|---|---|---|---|
| <pkg> | 4.2 | 5.0 | major | pass (unit+integ) | <sha> |

## Flagged for decision
- <pkg> - unmaintained (last release <date>) - candidates: <alternatives>
- <pkg> - held by <ADR/comment>; not touched

## Removed / deduped
- unused: <pkg> (nothing imports it)
- duplicate: <pkg> collapsed 4.1 + 4.3 -> 4.3
```

## History

`.deps-reports/history.json`: per-run counts, and `patterns_observed` for updates that broke and how
they were fixed - so a known-bad major upgrade is approached with the fix in hand next time
(e.g. "zod 3->4 needs the .parse signature change; unit passed, integration caught it").

## SITREP

Security advisories first, by severity, with reachability. Then majors applied with their test
result. Then what was flagged for a human decision - an unmaintained core dependency is a real
finding, not a footnote. Then removals.

### Suggested next

| Outcome | Recommend |
|---|---|
| Security fixes applied | `/gh-ship` to ship them |
| A dependency flagged unmaintained | `/mdmp` if replacing it is a real decision |
| Supply-chain signal (typosquat/compromise) | `/sec-ship --supply-chain` for the full picture |
| Majors changed behaviour | `/test-ship` to close the coverage gap that let it through |
| Bundle grew | `/perf --bundle` |

## Design notes

**One major at a time.** The single most important rule. A batch of majors that breaks something is
un-attributable; serialised, each break points at its cause.

**Same map as sec-ship.** `/deps` and `/sec-ship` Agent 1 must not disagree about how to audit a
Go or PHP repo. The shared ecosystem map is what keeps "run a security scan" and "update the deps"
consistent.

**Reachability over score.** A CVSS number is presence, not exploitability. Where the tooling can say
whether the vulnerable code is actually called, that answer ranks the work better than the score.

**Work with the bot.** Renovate and Dependabot already do most of tier 1-2. Fighting them duplicates
CI and dirties the lockfile; the value this skill adds is majors, unmaintained-dependency judgement,
and supply-chain signal the bots do not surface.
