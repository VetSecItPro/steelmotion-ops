# SITREP (Situation Report) Standard for All Skills

**Version:** 1.0
**Applies to:** All skills in `~/.claude/commands/`
**Companion to:** [Status Update Protocol](./STATUS_UPDATES.md), [Cleanup Protocol](./CLEANUP_PROTOCOL.md)

---

## Purpose

Every skill MUST conclude with a SITREP - a structured situation report that tells the user exactly what happened, what changed, and what to do next. The SITREP is the **single source of truth** for a skill run. A user who reads only the SITREP should know everything they need to know.

**The SITREP is NOT optional.** Even if the skill found nothing, even if everything passed, the SITREP confirms that the skill ran completely and what it covered.

---

## Unified SITREP Template

Every skill uses this exact structure, adapted for its domain. Sections marked `[if applicable]` are included only when relevant.

```markdown
## SITREP

### Mission

**Skill:** /[skill-name]
**Project:** [project-name]
**Branch:** [current git branch]
**Mode:** [mode/flags used, e.g., "full", "--quick", "--comprehensive"]
**Started:** [YYYY-MM-DD HH:MM:SS]
**Completed:** [YYYY-MM-DD HH:MM:SS]
**Duration:** [Xm Ys]
**Status:** [COMPLETE / PARTIAL / BLOCKED]

---

### Scope

**What was examined:**
- [X] pages / [Y] API routes / [Z] components / etc.
- [Specific scope description - what was IN scope]

**What was excluded:**
- [Anything skipped and why - e.g., "--changed mode: 5 pages out of 19 tested"]

---

### Findings Summary

| Severity | Found | Fixed | Deferred | Blocked |
|----------|-------|-------|----------|---------|
| CRITICAL | 0     | 0     | 0        | 0       |
| HIGH     | 0     | 0     | 0        | 0       |
| MEDIUM   | 0     | 0     | 0        | 0       |
| LOW      | 0     | 0     | 0        | 0       |
| INFO     | 0     | - | - | - |
| **Total**| **0** | **0** | **0**    | **0**   |

---

### Before / After [if applicable - when the skill modifies code]

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| [Primary metric] | [value] | [value] | [+/-X% or absolute] |
| [Secondary metric] | [value] | [value] | [+/-X%] |
| [Score/Grade] | [value] | [value] | [improvement] |

---

### What Was Fixed [if applicable]

| # | ID | Finding | File(s) | Fix Applied |
|---|-----|---------|---------|-------------|
| 1 | [ID] | [one-line description] | [file:line] | [what was done] |
| 2 | [ID] | [one-line description] | [file:line] | [what was done] |

**Files modified:** [count]
**Files created:** [count]
**Tests added:** [count]

---

### What Was Deferred [if applicable - with WHY]

| # | ID | Finding | Why Deferred | What Needs to Happen |
|---|-----|---------|-------------|----------------------|
| 1 | [ID] | [description] | [specific reason] | [specific action to resolve] |

---

### What Was Blocked [if applicable - with all attempts documented]

| # | ID | Finding | Attempts | Why Blocked |
|---|-----|---------|----------|-------------|
| 1 | [ID] | [description] | [N attempts: what was tried] | [why it can't be fixed now] |

---

### Cleanup

| Resource | Action | Status |
|----------|--------|--------|
| Browser instances | Closed | [done/warning] |
| Test data | [N] records deleted | [done/warning] |
| Dev server | [Stopped / Pre-existing, left running] | [done/n/a] |
| Screenshots | [N] ephemeral deleted, [M] evidence kept | [done] |
| State files | [N] old files cleaned | [done] |

---

### Recommendations

1. **[Next immediate action]** - [why and how]
2. **[Follow-up action]** - [why and how]
3. **[Longer-term suggestion]** - [why]

### Suggested Next Skills

| Condition | Run |
|-----------|-----|
| Ready to ship | `/gh-ship` |
| [condition specific to this skill] | `/[relevant skill]` |
| [condition specific to this skill] | `/[relevant skill]` |

---

### Historical Context [if previous runs exist]

| Run | Date | Score/Result | Trend |
|-----|------|-------------|-------|
| #1 | [date] | [result] | - |
| #2 | [date] | [result] | [improving/stable/declining] |
| **#3 (this run)** | [today] | [result] | [trend] |
```

---

## Adaptation Rules Per Skill Category

The template above is the **skeleton**. Each skill fills in the sections relevant to its domain and can add domain-specific sections. Here's what each skill type emphasizes:

### Audit Skills (/sec-ship, /a11y, /perf, /design, /compliance, /deps)

**Emphasis:** Findings Summary, Before/After scores, What Was Fixed/Deferred/Blocked
**Domain-specific additions:**
- `/sec-ship`: OWASP coverage table, confidence distribution, trend (NEW/PERSISTENT/RESOLVED/REGRESSED)
- `/design`: Design Score + AI Slop Score (dual), litmus test results, first impression verdict
- `/perf`: Budget dashboard (pass/fail per metric), CWV before/after, slowest resources
- `/a11y`: WCAG level compliance (A/AA/AAA), axe-core violation counts
- `/deps`: CVE counts by severity, outdated package list, supply chain risk
- `/compliance`: Regulation coverage (GDPR/CCPA), policy link status

### Testing Skills (/qatest, /redteam, /test-ship, /smoketest)

**Emphasis:** Scope (pages/endpoints tested), Findings Summary, Ship Decision
**Domain-specific additions:**
- `/qatest`: QA Score with per-dimension health dashboard, ship decision (SHIP/REVIEW/NO SHIP)
- `/redteam`: Campaigns run, endpoints attacked, attack success rate, FORTRESS/BREACHED verdict
- `/test-ship`: Coverage percentages, test counts by type
- `/smoketest`: Pass/fail per check, quick verdict

### Planning Skills (/mdmp)

**Emphasis:** Scope (complexity classification), COA selected, execution summary
**Domain-specific additions:**
- Selected COA and rationale
- Tasks completed vs total
- Lenses satisfied
- Risk register outcomes

### Fix & Ship Skills (/gh-ship, /incident, /investigate, /cleancode)

**Emphasis:** What changed, verification results, next steps
**Domain-specific additions:**
- `/gh-ship`: PR URL, CI status, deploy status
- `/incident`: Severity, timeline, root cause, postmortem link
- `/investigate`: Root cause, hypothesis log, confidence level, pattern learned
- `/cleancode`: Lines removed, complexity reduction, dead code eliminated

### Infrastructure Skills (/dev, /monitor, /migrate, /db)

**Emphasis:** Status (healthy/degraded/broken), what was done
**Domain-specific additions:**
- `/dev`: Server URL, port, PID
- `/monitor`: Health score, endpoint status, error rates
- `/migrate`: Breaking changes resolved, manual steps remaining
- `/db`: Migrations applied, drift detected, schema changes

---

## Display Format (On-Screen)

The SITREP is written to the report file AND displayed on screen. The on-screen version uses the bordered format:

```
═══════════════════════════════════════════════════════════════
SITREP - /[skill-name]
═══════════════════════════════════════════════════════════════
Project: [name]  |  Branch: [branch]  |  Duration: [Xm Ys]
Mode: [mode]     |  Status: [COMPLETE/PARTIAL/BLOCKED]
───────────────────────────────────────────────────────────────

SCOPE
  Examined: [X pages, Y endpoints, Z components]
  Excluded: [what and why]

FINDINGS
  CRITICAL: 0  |  HIGH: 2  |  MEDIUM: 5  |  LOW: 3
  Fixed: 8/10  |  Deferred: 1  |  Blocked: 1

BEFORE → AFTER
  [Primary metric]:  [before] → [after] ([delta])
  [Score/Grade]:     [before] → [after] ([delta])

FIXED (8)
  [ID] [one-line] → [file:line]
  [ID] [one-line] → [file:line]
  ...

DEFERRED (1)
  [ID] [one-line] - [why]

BLOCKED (1)
  [ID] [one-line] - [why] ([N attempts])

CLEANUP
  Browser: closed | Test data: 3 records deleted | Screenshots: 12 purged

NEXT STEPS
  1. [immediate action]
  2. [follow-up]

HISTORY
  Run #1 (2026-03-01): [result]
  Run #2 (2026-03-15): [result]
  Run #3 (today):      [result] - Trend: [improving/stable/declining]

───────────────────────────────────────────────────────────────
Report: .[skill]-reports/[filename].md
═══════════════════════════════════════════════════════════════
```

---

## Rules

1. **SITREP is ALWAYS the last thing displayed** - after cleanup, after report finalization
2. **SITREP is written to the report file AND displayed on screen** - both are mandatory
3. **Every section that has data must be included** - don't skip Deferred if there are deferred items
4. **Empty sections are omitted** - if nothing was deferred, don't show the Deferred section
5. **Findings table is ALWAYS shown** - even if all zeros (proves the skill ran and checked)
6. **Before/After is required for any skill that modifies code** - show the improvement
7. **Cleanup section is ALWAYS shown** - proves resources were handled
8. **Next Steps must be actionable** - specific skill commands, not vague advice
9. **Historical Context shown when previous runs exist** - helps track progress over time
10. **Skill name is ALWAYS in the header** - user must know which skill produced this SITREP

---

## Anti-Patterns

### "The Mystery SITREP"
```
❌ Status: Complete. 5 issues found and fixed.
```
Missing: what skill, what project, what was examined, what the issues were, before/after, next steps.

### "The Novel SITREP"
```
❌ [3 pages of prose explaining every decision made during the run]
```
Tables, not paragraphs. Scannable, not readable.

### "The Orphan SITREP"
```
❌ SITREP displayed on screen but not in the report file
```
Both or nothing. The report is the permanent record.

### "The Silent Cleanup"
```
❌ SITREP says "Complete" but doesn't mention whether test data was deleted
```
Always show cleanup status. Always.

---

## Reference in Skills

Add this to every skill file, replacing any existing SITREP section:

```markdown
## SITREP

> Reference: [SITREP Standard](~/.claude/standards/SITREP_FORMAT.md)

[Use the unified template. Include all sections with data. Omit empty sections.
Add domain-specific sections per the adaptation rules.]
```

---

**Last Updated:** 2026-03-31
