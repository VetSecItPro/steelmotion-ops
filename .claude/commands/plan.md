# /plan - Full Planning Cycle

**Explore. Analyze. Decide. Execute. One command from idea to implementation.**

Chains `/brainstorm`, `/mdmp`, and `/subagent-dev` into a complete plan-to-execution cycle. Socratic at the start (brainstorm phase), then autonomous through planning and execution.

## INTAKE (Socratic via /brainstorm)

The `/brainstorm` skill IS the Socratic intake. It asks one question at a time, explores 2-3 approaches with tradeoffs, and only proceeds when the user approves a direction.

**The flow:**
1. User describes what they want to build
2. `/brainstorm` explores the idea with Socratic questions
3. Once direction is approved, `/mdmp` takes over with 7-lens analysis
4. User approves a COA (Course of Action) at MDMP's single pause point
5. `/subagent-dev` executes the plan with two-stage review per task

## PIPELINE

```
PHASE 1: /brainstorm (Socratic exploration)
   Purpose: clarify requirements, explore approaches, validate assumptions
   Gate: user approves a direction ("yes, do that" or similar)
   Output: approved spec document
         
PHASE 2: /mdmp (7-lens military decision-making process)
   Purpose: full analysis through SWE, PM, Security, QA, UX, DevOps, Risk lenses
   Gate: user selects a COA from the decision matrix
   Output: comprehensive plan with task list
         
PHASE 3: /subagent-dev (automated execution with review)
   Purpose: implement each task with two-stage review (spec compliance + code quality)
   Gate: all tasks complete and reviewed
   Output: working implementation
```

## BEHAVIOR

- Phase 1 is interactive (Socratic). Phases 2-3 are autonomous except for MDMP's single COA selection pause.
- If the task is clearly TACTICAL (small, obvious), suggest skipping brainstorm: "This seems straightforward. Skip brainstorm and go straight to planning?"
- If the user already has a clear spec, skip to Phase 2 directly.
- The MDMP's Risk Management lens (new) evaluates reversibility and blast radius of each COA.


## INTRO (displayed at start of every run)

When this plugin is invoked, announce what's about to happen:

```
/plan Starting
   Skills to run: /brainstorm, /mdmp, /subagent-dev
   Report output: .plan-reports/

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

Every plugin run ends with a structured situation report saved to `.plan-reports/sitrep-YYYYMMDD-HHMMSS.md` AND displayed to the user.

```
===============================================================
SITREP - /plan
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
- `.brainstorm-reports/` - /brainstorm detailed findings
- `.mdmp-reports/` - /mdmp detailed findings
- `.subagent-dev-reports/` - /subagent-dev detailed findings

===============================================================
                      END SITREP
===============================================================
```

**SITREP is NOT optional.** Every plugin run produces one, even if it fails mid-run (report what completed and what didn't).

## AUDIT OUTPUT

**Report directory:** `.plan-reports/`

Each run produces:
- `.plan-reports/sitrep-YYYYMMDD-HHMMSS.md` - the unified SITREP above
- Individual sub-skill reports in their own directories (e.g., `.security-reports/`, `.qatest-reports/`)

**Gitignore enforcement:**
```bash
# Ensure report dir is gitignored (run at start of every plugin invocation)
grep -q ".plan-reports" .gitignore 2>/dev/null || echo ".plan-reports/" >> .gitignore
```

**Report retention:** Keep last 5 SITREPs. Delete older ones at start of each run.

**Cross-run trend tracking:** If a previous SITREP exists, compare before/after metrics against the previous run's after metrics to show directional progress over time.

---

## NATURAL LANGUAGE TRIGGERS

- "let's plan this"
- "plan and build"
- "design and implement"
- "I need to build X"
- "big feature"
- "new architecture"
- "let's think through this"
- "plan it out then build it"

## RELATED

- `/brainstorm` - just the exploration phase
- `/mdmp` - just the planning/analysis phase
- `/subagent-dev` - just the execution phase
