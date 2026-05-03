# /quality - Full Quality Sweep

> **Standards inherited** (apply throughout this skill):
> - [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md)
> - [Self-Improvement Protocol](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) — log to .quality-history.json
> - [Multi-Repo Awareness](~/.claude/standards/MULTI_REPO_AWARENESS.md)
> - [Verify Before Destroy](~/.claude/standards/VERIFY_BEFORE_DESTROY.md)


**Tests. QA. Smoke. Performance. Accessibility. Everything quality, one command.**

Chains `/test-ship`, `/qatest`, `/smoketest`, `/perf`, and `/a11y` into a comprehensive quality gate.

## INTAKE

No Socratic intake. Quality means everything.

**Smart fast-path:** If the codebase has no UI (pure API/CLI), skip `/a11y` and UI-specific `/qatest` steps automatically.

## PIPELINE

```
STEP 1: /smoketest (quick sanity - 2-3 min)
   Purpose: catch obvious breakage before investing in deep analysis
   Gate: build passes, no runtime crashes
   Fail: fix immediately, then continue
         
STEP 2: /test-ship (comprehensive test audit)
   Purpose: find gaps, write missing tests, fix failing ones
   Gate: all tests pass, coverage acceptable
   Fail: fix and retry (up to 2 attempts)
         
STEP 3: /perf (performance audit)
   Purpose: Lighthouse, bundle size, Core Web Vitals, API response times
   Gate: no critical performance regressions
   Fail: report with specific optimization recommendations
         
STEP 4: /a11y (accessibility audit)
   Purpose: WCAG compliance, keyboard nav, screen readers, contrast
   Gate: no critical a11y violations
   Fail: fix what's auto-fixable, report manual fixes needed
   Skip: if no UI components detected
         
STEP 5: /qatest (full autonomous QA)
   Purpose: crawl all pages, test all interactions, validate all APIs
   Gate: no critical failures
   Fail: auto-fix what's possible, report remaining issues
```

## QUALITY REPORT

```
QUALITY REPORT
Date: [date]
Duration: [X minutes]
Overall: PASS / CONDITIONAL PASS / FAIL

Smoke Test:     PASS/FAIL
Test Coverage:  [X]% ([N] tests, [N] new)
Performance:    [Lighthouse score] / [bundle size] / [LCP]
Accessibility:  [N] violations ([N] critical, [N] fixed)
QA:             [N] pages tested, [N] interactions, [N] failures

Action Items:
   [numbered list of remaining issues by severity]
```


## INTRO (displayed at start of every run)

When this plugin is invoked, announce what's about to happen:

```
/quality Starting
   Skills to run: /smoketest, /test-ship, /perf, /a11y, /qatest
   Report output: .quality-reports/

   Capturing before-state metrics...
```

**Before-state capture (run BEFORE any skill executes):**
- Git status: uncommitted changes count, branch name
- Build status: passes or fails
- Test count: total tests, passing, failing
- Security: known vulnerability count (from last scan if available)
- Performance: bundle size, Lighthouse score (if applicable)
- Dependencies: outdated count, CVE count (if applicable)

Store these in memory for the SITREP before/after comparison.

## SITREP (mandatory at end of every run)

Every plugin run ends with a structured situation report saved to `.quality-reports/sitrep-YYYYMMDD-HHMMSS.md` AND displayed to the user.

```
===============================================================
SITREP - /quality
===============================================================

Date: [YYYY-MM-DD HH:MM CT]
Duration: [X minutes Y seconds]
Branch: [branch-name]

---------------------------------------------------------------
BEFORE / AFTER
---------------------------------------------------------------

| Metric              | Before    | After     | Delta       |
|---------------------|-----------|-----------|-------------|
| Build               | [P/F]     | [P/F]     | [fixed/broke/same] |
| Tests               | [N pass]  | [N pass]  | [+N/-N/same]|
| Test coverage       | [X%]      | [X%]      | [+/-/same]  |
| Security vulns      | [N]       | [N]       | [-N fixed]  |
| Bundle size         | [X KB]    | [X KB]    | [+/-/same]  |
| Outdated deps       | [N]       | [N]       | [-N updated]|
| Files modified      | -         | [N]       | -           |

---------------------------------------------------------------
SKILLS EXECUTED
---------------------------------------------------------------

| # | Skill          | Status    | Duration | Findings     |
|---|----------------|-----------|----------|--------------|
| 1 | [skill name]   | PASS/FAIL | [Xm Ys]  | [summary]   |
| 2 | [skill name]   | PASS/FAIL | [Xm Ys]  | [summary]   |
| 3 | [skill name]   | SKIPPED   | -        | [reason]     |

---------------------------------------------------------------
FINDINGS SUMMARY
---------------------------------------------------------------

Critical: [N]
High:     [N]
Medium:   [N]
Low:      [N]
Info:     [N]

[Top 3 most important findings with file:line references]

---------------------------------------------------------------
DEFERRED ITEMS
---------------------------------------------------------------

Items that were identified but not fixed in this run:
- [ ] [item 1 - why deferred, what to do]
- [ ] [item 2 - why deferred, what to do]

---------------------------------------------------------------
LESSONS LEARNED
---------------------------------------------------------------

Patterns or insights discovered during this run that should
inform future work:
- [lesson 1]
- [lesson 2]

---------------------------------------------------------------
SUB-SKILL REPORTS
---------------------------------------------------------------

Full details in individual skill reports:
- `.smoketest-reports/` - /smoketest detailed findings
- `.test-ship-reports/` - /test-ship detailed findings
- `.perf-reports/` - /perf detailed findings
- `.a11y-reports/` - /a11y detailed findings
- `.qatest-reports/` - /qatest detailed findings

===============================================================
                      END SITREP
===============================================================
```

**SITREP is NOT optional.** Every plugin run produces one, even if it fails mid-run (report what completed and what didn't).

## AUDIT OUTPUT

**Report directory:** `.quality-reports/`

Each run produces:
- `.quality-reports/sitrep-YYYYMMDD-HHMMSS.md` - the unified SITREP above
- Individual sub-skill reports in their own directories (e.g., `.security-reports/`, `.qatest-reports/`)

**Gitignore enforcement:**
```bash
# Ensure report dir is gitignored (run at start of every plugin invocation)
grep -q ".quality-reports" .gitignore 2>/dev/null || echo ".quality-reports/" >> .gitignore
```

**Report retention:** Keep last 5 SITREPs. Delete older ones at start of each run.

**Cross-run trend tracking:** If a previous SITREP exists, compare before/after metrics against the previous run's after metrics to show directional progress over time.

---

## NATURAL LANGUAGE TRIGGERS

- "full QA"
- "test everything"
- "is this ready?"
- "quality check"
- "run all tests"
- "check everything before shipping"
- "QA this"
- "how's the quality?"

## RELATED

- `/ship` - quality + security + deploy (the full pipeline)
- `/smoketest` - just the quick sanity check
- `/launch-ready` - quality + security + compliance (pre-launch)
