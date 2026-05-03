# /fortress - Complete Security Posture

**Audit. Fix. Pen-test. Comply. Document. Everything security, one command.**

This plugin chains `/sec-ship`, `/compliance`, `/redteam`, `/compliance-docs`, and `/sec-weekly-scan` into a full security posture assessment. No flags - it runs the works.

## INTAKE

No Socratic intake. If you called `/fortress`, you want the full treatment.

**Context-aware scoping:**
- If there are uncommitted changes on the branch: focus the audit on those changes first, then expand to full codebase
- If no uncommitted changes: full codebase audit from the start

## PIPELINE

```
STEP 1: /sec-ship (audit + fix + validate)
   Scope: full codebase - OWASP Top 10, auth, data exposure, input validation
   Output: vulnerabilities found, fixed, remaining
   Gate: no critical vulnerabilities remaining
         
STEP 2: /compliance (privacy + data compliance)
   Scope: GDPR, CCPA, data handling, consent, retention
   Output: compliance gaps, recommendations
   Gate: informational (does not block)
         
STEP 3: /redteam (active exploitation testing)
   Scope: localhost only - injection, auth bypass, privilege escalation
   Output: exploits found, proof of concept
   Gate: no exploitable critical vulnerabilities
   NOTE: only runs if user confirms ("This runs active attacks against localhost. Proceed?")
         
STEP 4: /compliance-docs (generate documentation)
   Scope: security policy, incident response plan, data handling docs
   Output: generated compliance documents
   Gate: informational (does not block)
         
STEP 5: /sec-weekly-scan (dependency + supply chain)
   Scope: all dependencies, known CVEs, license issues
   Output: vulnerable packages, upgrade paths
   Gate: no critical CVEs in production dependencies
```

## BEHAVIOR

- Steps 1-2 always run. Step 3 requires explicit confirmation (active exploitation). Steps 4-5 always run.
- If Step 1 finds and fixes vulnerabilities, re-run the validation to confirm fixes hold.
- Aggregate all findings into a single Fortress Report with severity ratings.
- If the codebase is clean across all steps, say so clearly: "Fortress audit complete. No critical findings."



## INTRO (displayed at start of every run)

When this plugin is invoked, announce what's about to happen:

```
/fortress Starting
   Skills to run: /sec-ship, /compliance, /redteam, /compliance-docs, /sec-weekly-scan
   Report output: .fortress-reports/

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

Every plugin run ends with a structured situation report saved to `.fortress-reports/sitrep-YYYYMMDD-HHMMSS.md` AND displayed to the user.

```
===============================================================
SITREP - /fortress
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
- `.sec-ship-reports/` - /sec-ship detailed findings
- `.compliance-reports/` - /compliance detailed findings
- `.redteam-reports/` - /redteam detailed findings
- `.compliance-docs-reports/` - /compliance-docs detailed findings
- `.sec-weekly-scan-reports/` - /sec-weekly-scan detailed findings

===============================================================
                      END SITREP
===============================================================
```

**SITREP is NOT optional.** Every plugin run produces one, even if it fails mid-run (report what completed and what didn't).

## AUDIT OUTPUT

**Report directory:** `.fortress-reports/`

Each run produces:
- `.fortress-reports/sitrep-YYYYMMDD-HHMMSS.md` - the unified SITREP above
- Individual sub-skill reports in their own directories (e.g., `.security-reports/`, `.qatest-reports/`)

**Gitignore enforcement:**
```bash
# Ensure report dir is gitignored (run at start of every plugin invocation)
grep -q ".fortress-reports" .gitignore 2>/dev/null || echo ".fortress-reports/" >> .gitignore
```

**Report retention:** Keep last 5 SITREPs. Delete older ones at start of each run.

**Cross-run trend tracking:** If a previous SITREP exists, compare before/after metrics against the previous run's after metrics to show directional progress over time.

---

## NATURAL LANGUAGE TRIGGERS

- "full security review"
- "security audit everything"
- "lock this down"
- "is this secure?"
- "OWASP check"
- "pen test this"
- "security posture"
- "vulnerability scan"
- "how secure are we?"

## RELATED

- `/sec-ship` - just the audit/fix cycle (fastest)
- `/redteam` - just active exploitation
- `/compliance` - just privacy/data compliance
- `/compliance-docs` - just documentation generation
