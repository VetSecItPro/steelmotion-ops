# /ops - Operations: Debug, Respond, Monitor

**Something's wrong? This figures out what and runs the right skill.**

Auto-routes between `/investigate`, `/incident`, `/monitor`, and `/dev` based on severity. No Socratic intake - it reads the situation and acts.

## AUTO-ROUTING

```
Is production down or users affected?
  YES -> /incident (triage, fix, verify, postmortem)
  NO  -> Is something broken locally?
           YES -> /investigate (evidence-first root cause debugging)
           NO  -> Is a service unhealthy or degraded?
                    YES -> /monitor (health check, identify degradation)
                    NO  -> /dev (start/restart dev server)
```

## DETECTION SIGNALS

| Signal | Routes To | Why |
|--------|-----------|-----|
| "production is down", "users are reporting", "urgent" | `/incident` | Production impact requires incident protocol |
| "not working", "broken", "can't figure out", "bug" | `/investigate` | Local bug needs evidence-first debugging |
| "is it healthy?", "check the deploy", "anything wrong?" | `/monitor` | Health verification |
| "start it up", "run the app", "dev server" | `/dev` | Development server management |
| "something's off but I'm not sure what" | `/monitor` first, then `/investigate` if issues found | Triage before deep dive |

## BEHAVIOR

- Always start with a 10-second situation assessment: git status, running processes, recent logs
- Route to the right sub-skill without asking
- If the initial routing was wrong (e.g., started `/investigate` but it's actually a production issue), escalate automatically to `/incident`
- After resolution, suggest `/monitor` to verify the fix in production


## INTRO (displayed at start of every run)

When this plugin is invoked, announce what's about to happen:

```
/ops Starting
   Skills to run: /investigate, /incident, /monitor, /dev
   Report output: .ops-reports/

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

Every plugin run ends with a structured situation report saved to `.ops-reports/sitrep-YYYYMMDD-HHMMSS.md` AND displayed to the user.

```
===============================================================
SITREP - /ops
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
- `.investigate-reports/` - /investigate detailed findings
- `.incident-reports/` - /incident detailed findings
- `.monitor-reports/` - /monitor detailed findings
- `.dev-reports/` - /dev detailed findings

===============================================================
                      END SITREP
===============================================================
```

**SITREP is NOT optional.** Every plugin run produces one, even if it fails mid-run (report what completed and what didn't).

## AUDIT OUTPUT

**Report directory:** `.ops-reports/`

Each run produces:
- `.ops-reports/sitrep-YYYYMMDD-HHMMSS.md` - the unified SITREP above
- Individual sub-skill reports in their own directories (e.g., `.security-reports/`, `.qatest-reports/`)

**Gitignore enforcement:**
```bash
# Ensure report dir is gitignored (run at start of every plugin invocation)
grep -q ".ops-reports" .gitignore 2>/dev/null || echo ".ops-reports/" >> .gitignore
```

**Report retention:** Keep last 5 SITREPs. Delete older ones at start of each run.

**Cross-run trend tracking:** If a previous SITREP exists, compare before/after metrics against the previous run's after metrics to show directional progress over time.

---

## NATURAL LANGUAGE TRIGGERS

- "something's broken"
- "it's not working"
- "production is down"
- "can you check on things?"
- "what's the status?"
- "is everything healthy?"
- "start the server"
- "fix this"
- "why is this happening?"
- "debug this"

## RELATED

- `/investigate` - just root-cause debugging
- `/incident` - just production incident response
- `/monitor` - just health check
- `/dev` - just dev server
