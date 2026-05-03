# /content - End-to-End Content Pipeline

**Write. Edit. Cut. Distribute. One command for any content piece.**

Chains `/blog`, `/newsletter`, `/copy`, `/narrative`, `/critique-adversarial`, and `/social` based on what you need. This is the one plugin that uses Socratic intake because "content" could mean anything.

## INTAKE (Socratic - 2 questions max)

**Question 1: "What are we creating?"**
Auto-detect from context if possible. If ambiguous, ask:
> "What kind of content? (article/newsletter/social posts/landing page copy/email sequence)"

Route based on answer:
- Article/blog post -> `/blog` pipeline
- Newsletter -> `/newsletter` pipeline
- Social posts -> `/social` pipeline
- Landing page/email/ad -> `/copy` pipeline
- "All of it" -> `/blog` first, then repurpose to all channels

**Question 2 (only if creating from scratch): "What's the topic or angle?"**
> "Give me the topic, angle, or just paste the rough idea."

If the user already provided context (e.g., "write a piece about X"), skip this question entirely.

## PIPELINES (by content type)

### Article Pipeline
```
/blog (research, outline, draft, voice pass, anti-slop scrub)
  -> /critique-adversarial (hostile edit - cut what doesn't serve the argument)
  -> /social (repurpose to LinkedIn, X, etc.)
```

### Newsletter Pipeline
```
/newsletter (structure issue, develop voice, build sections)
  -> /critique-adversarial (tighten prose)
  -> /social (teaser posts for distribution)
```

### Social Pipeline
```
/social (platform-specific posts, content calendar)
  -> /narrative (add storytelling where flat)
```

### Copy Pipeline
```
/copy (conversion-optimized output for the asset type)
  -> /narrative (inject story structure where appropriate)
```

### Full Pipeline ("all of it")
```
/blog (the anchor piece)
  -> /critique-adversarial (edit pass)
  -> /newsletter (adapt for newsletter format)
  -> /social (repurpose to all platforms)
  -> /copy (extract CTAs, email snippets, ad hooks)
```

## BEHAVIOR

- The `/critique-adversarial` step is non-optional for articles and newsletters. Every long-form piece gets the hostile editor.
- `/narrative` runs as a sub-skill inside `/copy` and `/social` when storytelling is the mechanism, not as a standalone step.
- Voice consistency: all outputs anchor to `voice-dna.md` if it exists in the workspace.
- No AI slop. The `/blog` pipeline includes an anti-slop scrub. If slop survives, `/critique-adversarial` catches it.


## INTRO (displayed at start of every run)

When this plugin is invoked, announce what's about to happen:

```
/content Starting
   Skills to run: /blog, /newsletter, /social, /copy, /narrative, /critique-adversarial
   Report output: .content-reports/

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

Every plugin run ends with a structured situation report saved to `.content-reports/sitrep-YYYYMMDD-HHMMSS.md` AND displayed to the user.

```
===============================================================
SITREP - /content
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
- `.blog-reports/` - /blog detailed findings
- `.newsletter-reports/` - /newsletter detailed findings
- `.social-reports/` - /social detailed findings
- `.copy-reports/` - /copy detailed findings
- `.narrative-reports/` - /narrative detailed findings
- `.critique-adversarial-reports/` - /critique-adversarial detailed findings

===============================================================
                      END SITREP
===============================================================
```

**SITREP is NOT optional.** Every plugin run produces one, even if it fails mid-run (report what completed and what didn't).

## AUDIT OUTPUT

**Report directory:** `.content-reports/`

Each run produces:
- `.content-reports/sitrep-YYYYMMDD-HHMMSS.md` - the unified SITREP above
- Individual sub-skill reports in their own directories (e.g., `.security-reports/`, `.qatest-reports/`)

**Gitignore enforcement:**
```bash
# Ensure report dir is gitignored (run at start of every plugin invocation)
grep -q ".content-reports" .gitignore 2>/dev/null || echo ".content-reports/" >> .gitignore
```

**Report retention:** Keep last 5 SITREPs. Delete older ones at start of each run.

**Cross-run trend tracking:** If a previous SITREP exists, compare before/after metrics against the previous run's after metrics to show directional progress over time.

---

## NATURAL LANGUAGE TRIGGERS

- "write a piece about X"
- "create content about X"
- "write and publish"
- "blog post about X"
- "newsletter issue"
- "social posts for X"
- "landing page copy"
- "email sequence"
- "content calendar"
- "write this up"

## RELATED

- `/blog` - just the article pipeline
- `/social` - just social posts
- `/copy` - just conversion copy
- `/newsletter` - just newsletter
- `/gtm` - content as part of a full go-to-market campaign
