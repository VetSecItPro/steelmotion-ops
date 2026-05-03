# /gtm - Full Go-to-Market

**ICP. Prospect. Campaign. Copy. Distribution. One command to launch.**

Chains `/icp-from-repo`, `/prospect`, `/campaign`, `/marketing`, `/copy`, `/social`, `/hunt`, and `/outreach` into a full go-to-market machine. Uses Socratic intake because GTM needs to know what you're selling and to whom.

## INTAKE (Socratic - 3 questions max)

**Question 1: "What product or feature are we taking to market?"**
> Auto-detect from repo if possible (reads package.json, README, landing page). If unclear, ask.

**Question 2: "Who's the buyer?"**
> If `icp.json` exists, use it. If not: "Describe your ideal customer in one sentence."

**Question 3: "What stage are we at?"**
> - **Pre-launch** (no customers yet) -> full pipeline from ICP through campaign
> - **Soft launch** (some beta users) -> focus on outreach + content
> - **Growth** (product-market fit) -> focus on scaling channels

## PIPELINE

```
STAGE 1: Intelligence (who are we selling to?)
   /icp-from-repo (extract product context)
   /prospect (define ICP, score leads)
   /hunt (find pain signals in the wild)
         
STAGE 2: Strategy (how do we reach them?)
   /marketing (strategy, messaging framework, channel plan)
   /campaign (90-day timeline, KPIs, week-by-week plan)
         
STAGE 3: Assets (what do we put in front of them?)
   /copy (landing pages, emails, ad copy)
   /social (platform-specific posts, content calendar)
   /outreach (personalized DMs/emails for top prospects)
```

## BEHAVIOR

- Stage 1 feeds Stage 2: ICP and prospect data inform the marketing strategy.
- Stage 2 feeds Stage 3: the campaign brief tells copy/social what to produce.
- Each stage produces artifacts that persist (icp.json, scoring.json, campaign brief).
- If `/outreach` is still in DRAFT SPEC status, skip it and note "outreach drafts available when /outreach ships."
- For "pre-launch" stage, run all three stages in order.
- For "soft launch", skip Stage 1 if ICP exists, focus on Stages 2-3.
- For "growth", skip strategy (assume it exists), focus on asset production.


## INTRO (displayed at start of every run)

When this plugin is invoked, announce what's about to happen:

```
/gtm Starting
   Skills to run: /icp-from-repo, /prospect, /campaign, /marketing, /copy, /social, /hunt, /outreach
   Report output: .gtm-reports/

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

Every plugin run ends with a structured situation report saved to `.gtm-reports/sitrep-YYYYMMDD-HHMMSS.md` AND displayed to the user.

```
===============================================================
SITREP - /gtm
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
- `.icp-from-repo-reports/` - /icp-from-repo detailed findings
- `.prospect-reports/` - /prospect detailed findings
- `.campaign-reports/` - /campaign detailed findings
- `.marketing-reports/` - /marketing detailed findings
- `.copy-reports/` - /copy detailed findings
- `.social-reports/` - /social detailed findings
- `.hunt-reports/` - /hunt detailed findings
- `.outreach-reports/` - /outreach detailed findings

===============================================================
                      END SITREP
===============================================================
```

**SITREP is NOT optional.** Every plugin run produces one, even if it fails mid-run (report what completed and what didn't).

## AUDIT OUTPUT

**Report directory:** `.gtm-reports/`

Each run produces:
- `.gtm-reports/sitrep-YYYYMMDD-HHMMSS.md` - the unified SITREP above
- Individual sub-skill reports in their own directories (e.g., `.security-reports/`, `.qatest-reports/`)

**Gitignore enforcement:**
```bash
# Ensure report dir is gitignored (run at start of every plugin invocation)
grep -q ".gtm-reports" .gitignore 2>/dev/null || echo ".gtm-reports/" >> .gitignore
```

**Report retention:** Keep last 5 SITREPs. Delete older ones at start of each run.

**Cross-run trend tracking:** If a previous SITREP exists, compare before/after metrics against the previous run's after metrics to show directional progress over time.

---

## NATURAL LANGUAGE TRIGGERS

- "go to market"
- "GTM strategy"
- "launch marketing"
- "how do we sell this?"
- "find customers"
- "marketing campaign"
- "who should we target?"
- "build the funnel"
- "sales pipeline"
- "launch strategy"

## RELATED

- `/marketing` - just strategy/messaging (no ICP research or asset production)
- `/campaign` - just the 90-day plan
- `/content` - just content creation (no ICP/prospect/strategy)
- `/prospect` - just ICP/lead scoring
