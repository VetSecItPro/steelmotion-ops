# /harden - Codebase Health

> **Standards inherited** (apply throughout this skill):
> - [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md)
> - [Self-Improvement Protocol](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) — log to .harden-history.json
> - [Multi-Repo Awareness](~/.claude/standards/MULTI_REPO_AWARENESS.md)
> - [Verify Before Destroy](~/.claude/standards/VERIFY_BEFORE_DESTROY.md)
> - [Skill Auto-Suggest Protocol](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) — every SITREP ends with "Suggested next"


**Clean dead code. Update deps. Optimize. Align design. One command.**

Chains `/cleancode`, `/deps`, `/perf`, and `/design` into a codebase health sweep. No Socratic intake - if you're hardening, you want all of it.

## PIPELINE

```
STEP 1: /cleancode (dead code, unused imports, tech debt)
   Purpose: remove cruft before optimizing
   Gate: build passes after cleanup
         
STEP 2: /deps (dependency health, CVEs, updates)
   Purpose: update vulnerable/outdated packages
   Gate: no critical CVEs, build passes after updates
         
STEP 3: /perf (performance audit + optimization)
   Purpose: bundle size, load times, API response times
   Gate: no critical regressions
         
STEP 4: /design (design system alignment)
   Purpose: consistent tokens, components, spacing
   Gate: informational (recommendations, not blockers)
   Skip: if no UI components detected
```

## BEHAVIOR

- Step 1 runs first deliberately: cleaning dead code before updating deps avoids updating packages you don't even use.
- If `/deps` finds major version upgrades that need migration work, it reports them but does NOT auto-upgrade. It only auto-upgrades patches and compatible minors.
- The `/design` step is advisory on `/harden` - it reports inconsistencies but doesn't auto-fix UI unless explicitly told to.


## INTRO (displayed at start of every run)

When this plugin is invoked, announce what's about to happen:

```
/harden Starting
   Skills to run: /cleancode, /deps, /perf, /design
   Report output: .harden-reports/

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

Every plugin run ends with a structured situation report saved to `.harden-reports/sitrep-YYYYMMDD-HHMMSS.md` AND displayed to the user.

```
===============================================================
SITREP - /harden
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
- `.cleancode-reports/` - /cleancode detailed findings
- `.deps-reports/` - /deps detailed findings
- `.perf-reports/` - /perf detailed findings
- `.design-reports/` - /design detailed findings

===============================================================
                      END SITREP
===============================================================
```

**SITREP is NOT optional.** Every plugin run produces one, even if it fails mid-run (report what completed and what didn't).

## AUDIT OUTPUT

**Report directory:** `.harden-reports/`

Each run produces:
- `.harden-reports/sitrep-YYYYMMDD-HHMMSS.md` - the unified SITREP above
- Individual sub-skill reports in their own directories (e.g., `.security-reports/`, `.qatest-reports/`)

**Gitignore enforcement:**
```bash
# Ensure report dir is gitignored (run at start of every plugin invocation)
grep -q ".harden-reports" .gitignore 2>/dev/null || echo ".harden-reports/" >> .gitignore
```

**Report retention:** Keep last 5 SITREPs. Delete older ones at start of each run.

**Cross-run trend tracking:** If a previous SITREP exists, compare before/after metrics against the previous run's after metrics to show directional progress over time.

---

## NATURAL LANGUAGE TRIGGERS

- "clean up this codebase"
- "technical debt"
- "dead code"
- "update dependencies"
- "harden this"
- "codebase health check"
- "tighten things up"
- "make this cleaner"
- "maintenance pass"

## RELATED

- `/cleancode` - just dead code removal
- `/deps` - just dependency updates
- `/perf` - just performance
- `/ship` - harden + test + secure + deploy (use when you want to ship after hardening)

---

## Suggested next

Per [Skill Auto-Suggest Protocol](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md), every SITREP MUST end with a "Suggested next" block. Use this decision matrix to pick:

| Outcome | Recommended | Why |
|---|---|---|
| Full sweep clean | /gh-ship | ship the hardening |
| Issues found in sub-skills | /investigate the worst | root-cause priority items |
| Comprehensive cleanup done | /quality | full quality follow-up |
| Pre-launch hardening | /launch | run launch readiness |

**Skip if:** the operator has already directed the next step, or this run was a no-op.
