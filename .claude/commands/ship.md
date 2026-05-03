# /ship - Full Ship Pipeline

> **Standards inherited** (apply throughout this skill + all sub-skills):
> - [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md)
> - [Self-Improvement Protocol](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md)
> - [Multi-Repo Awareness](~/.claude/standards/MULTI_REPO_AWARENESS.md)
> - [Verify Before Destroy](~/.claude/standards/VERIFY_BEFORE_DESTROY.md)
> - [Skill Auto-Suggest Protocol](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) — every SITREP ends with "Suggested next"


**Test. Secure. Commit. Deploy. Verify. One command.**

This plugin chains `/test-ship`, `/sec-ship`, `/gh-ship`, and `/monitor` into a single gated pipeline. Each step must pass before the next runs. No flags, no options - it runs everything.

## INTAKE

No Socratic intake needed. If you called `/ship`, the intent is clear: get this code to production.

**One optional question (only if uncommitted changes span multiple concerns):**
> "I see changes in [areas]. Ship everything, or scope to [specific area]?"

If the user says "everything" or doesn't respond in context, ship everything.

## PIPELINE

```
STEP 1: /test-ship (write missing tests, fix failing ones)
   Gate: all tests pass, build succeeds
   Fail: fix and retry (up to 2 attempts), then stop and report
         
STEP 2: /sec-ship (full audit + fix + validate)
   Gate: no critical or high vulnerabilities remaining
   Fail: fix what's fixable, report what needs manual review, STOP
         
STEP 3: /gh-ship (commit, push, PR, CI, merge)
   Gate: PR created, CI passes, merged to main
   Fail: fix CI failures (up to 2 attempts), then stop with PR link
         
STEP 4: /monitor (verify deploy health)
   Gate: all health checks pass
   Fail: report degradation, suggest rollback if critical
```

## BEHAVIOR

- Run steps sequentially. Never skip a step.
- If Step 1 finds zero test gaps AND all tests pass, report "Tests clean" and move to Step 2 quickly.
- If Step 2 finds zero security issues, report "Security clean" and move to Step 3 quickly.
- Aggregate all reports into a single summary at the end.
- If any step fails after retries, STOP. Report what passed, what failed, and what the user needs to do.



## INTRO (displayed at start of every run)

When this plugin is invoked, announce what's about to happen:

```
/ship Starting
   Skills to run: /test-ship, /sec-ship, /gh-ship, /monitor
   Report output: .ship-reports/

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

Every plugin run ends with a structured situation report saved to `.ship-reports/sitrep-YYYYMMDD-HHMMSS.md` AND displayed to the user.

```
===============================================================
SITREP - /ship
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
- `.test-ship-reports/` - /test-ship detailed findings
- `.sec-ship-reports/` - /sec-ship detailed findings
- `.gh-ship-reports/` - /gh-ship detailed findings
- `.monitor-reports/` - /monitor detailed findings

===============================================================
                      END SITREP
===============================================================
```

**SITREP is NOT optional.** Every plugin run produces one, even if it fails mid-run (report what completed and what didn't).

## AUDIT OUTPUT

**Report directory:** `.ship-reports/`

Each run produces:
- `.ship-reports/sitrep-YYYYMMDD-HHMMSS.md` - the unified SITREP above
- Individual sub-skill reports in their own directories (e.g., `.security-reports/`, `.qatest-reports/`)

**Gitignore enforcement:**
```bash
# Ensure report dir is gitignored (run at start of every plugin invocation)
grep -q ".ship-reports" .gitignore 2>/dev/null || echo ".ship-reports/" >> .gitignore
```

**Report retention:** Keep last 5 SITREPs. Delete older ones at start of each run.

**Cross-run trend tracking:** If a previous SITREP exists, compare before/after metrics against the previous run's after metrics to show directional progress over time.

---

## NATURAL LANGUAGE TRIGGERS

- "ship it"
- "push this to prod"
- "commit, test, and deploy"
- "full pipeline"
- "test and ship"
- "get this live"

## RELATED

- `/gh-ship` - just the git/PR/merge part (no tests, no security)
- `/test-ship` - just testing
- `/sec-ship` - just security
- `/monitor` - just health check
- `/launch-ready` - even more thorough (adds compliance, a11y, perf, QA)

---

## Suggested next

Per [Skill Auto-Suggest Protocol](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md), every SITREP MUST end with a "Suggested next" block. Use this decision matrix to pick:

| Outcome | Recommended | Why |
|---|---|---|
| Pipeline succeeded, deployed | /monitor | confirm prod health |
| Pipeline blocked at security | /sec-ship --comprehensive | resolve before re-running |
| Pipeline blocked at tests | /investigate | root-cause |
| Verified live | none — chain ended cleanly | done |

**Skip if:** the operator has already directed the next step, or this run was a no-op.
