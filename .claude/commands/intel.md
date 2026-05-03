# /intel - Research and Intelligence

**Scrape. Browse. Hunt. Score. One command for any research mission.**

Chains `/scrape`, `/browse`, `/hunt`, and `/prospect` into a research pipeline. Uses Socratic intake because "research" could mean competitive intel, prospect hunting, or general web research.

## INTAKE (Socratic - 1 question)

**"What are we researching?"**
Auto-detect from context if possible. Route based on answer:

| Intent | Route |
|--------|-------|
| "competitors", "market", "what's out there" | Competitive intel: `/scrape` + `/browse` on competitor sites |
| "find customers", "prospects", "leads" | Prospect hunting: `/hunt` + `/prospect` |
| "research X topic", "what does Y say about Z" | General research: `/scrape` + `/browse` for information gathering |
| "all of it" or product/market research | Full pipeline: competitors + prospects + general research |

## PIPELINES

### Competitive Intel
```
/scrape (extract competitor sites, pricing pages, feature lists)
  -> /browse (interactive exploration of competitor products)
  -> Structured output: competitor comparison matrix
```

### Prospect Hunting
```
/hunt (scan HN, GitHub, Reddit for pain signals matching ICP)
  -> /prospect (score and rank found signals)
  -> Structured output: scored prospect list with talking points
```

### General Research
```
/scrape (extract content from specified URLs or search results)
  -> /browse (follow interesting leads interactively)
  -> Structured output: research brief with citations
```

### Full Pipeline
```
All three pipelines above, run in order.
Output: comprehensive market intelligence brief.
```

## BEHAVIOR

- Always cite sources. Every claim links to the URL it came from.
- For competitive intel: extract pricing, features, positioning, team size if available.
- For prospect hunting: requires `icp.json` to exist. If it doesn't, run `/prospect` first to define the ICP.
- For general research: respect rate limits, don't hammer sites, use SearXNG for search.
- Output goes to `.intel-reports/` directory (gitignored).


## INTRO (displayed at start of every run)

When this plugin is invoked, announce what's about to happen:

```
/intel Starting
   Skills to run: /scrape, /browse, /hunt, /prospect
   Report output: .intel-reports/

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

Every plugin run ends with a structured situation report saved to `.intel-reports/sitrep-YYYYMMDD-HHMMSS.md` AND displayed to the user.

```
===============================================================
SITREP - /intel
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
- `.scrape-reports/` - /scrape detailed findings
- `.browse-reports/` - /browse detailed findings
- `.hunt-reports/` - /hunt detailed findings
- `.prospect-reports/` - /prospect detailed findings

===============================================================
                      END SITREP
===============================================================
```

**SITREP is NOT optional.** Every plugin run produces one, even if it fails mid-run (report what completed and what didn't).

## AUDIT OUTPUT

**Report directory:** `.intel-reports/`

Each run produces:
- `.intel-reports/sitrep-YYYYMMDD-HHMMSS.md` - the unified SITREP above
- Individual sub-skill reports in their own directories (e.g., `.security-reports/`, `.qatest-reports/`)

**Gitignore enforcement:**
```bash
# Ensure report dir is gitignored (run at start of every plugin invocation)
grep -q ".intel-reports" .gitignore 2>/dev/null || echo ".intel-reports/" >> .gitignore
```

**Report retention:** Keep last 5 SITREPs. Delete older ones at start of each run.

**Cross-run trend tracking:** If a previous SITREP exists, compare before/after metrics against the previous run's after metrics to show directional progress over time.

---

## NATURAL LANGUAGE TRIGGERS

- "research this"
- "competitive analysis"
- "what are competitors doing?"
- "find me prospects"
- "market research"
- "look into X"
- "intel on X"
- "what's the landscape?"
- "who else does this?"
- "dig into this"

## RELATED

- `/scrape` - just web extraction
- `/browse` - just interactive browsing
- `/hunt` - just pain-signal discovery
- `/prospect` - just ICP/lead scoring
- `/gtm` - intel as part of a full go-to-market campaign
