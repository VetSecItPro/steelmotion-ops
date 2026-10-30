# Agent Orchestration Protocol for Multi-Agent Skills

**Version:** 1.0
**Applies to:** All skills in `~/.claude/commands/` **and** `~/.claude/skills/` that spawn subagents.

**Companion to:** [Context Management Protocol](./CONTEXT_MANAGEMENT.md), [Status Update Protocol](./STATUS_UPDATES.md)

> **Currency note, 2026-08-27.** The spawning tool is now **`Agent`**, not `Task` - the `Task*`
> names refer to todo management. 18 skills defer to this document, so the old name was
> propagating. Subagents **cannot nest**: a subagent must not spawn another, and `workflow()`
> inside a child throws. Any design here implying a deep agent tree is wrong.

---

## The Principle

**You are a project manager, not a worker.** The orchestrator (main Claude session running the skill) should NEVER do heavy scanning, analysis, or fixing directly. It delegates to agents, collects their results from disk, coordinates the next step, and reports progress. This keeps the orchestrator's context window clean and prevents context exhaustion.

---

## Persistent Agent Definitions vs Dynamic Spawning

Two different mechanisms, and this document historically covered only the second.

**Dynamic spawning** - a skill calls `Agent` mid-run with a prompt it composes. Right for
work whose shape is only known at runtime. Everything below in this document is about this.

**Persistent agent definitions** - `.md` files in `.claude/agents/` (project) or
`~/.claude/agents/` (global) with frontmatter declaring `name`, `description`, `tools` and
`model`, invoked by `subagent_type`. Right for a role you use repeatedly.

**The tool list is the security boundary, and it is the reason to prefer a definition.**
A dynamically spawned `general-purpose` agent carries `Tools: *` - full write access to the
repo. A definition can withhold `Edit` and `Write`. Two consequences worth designing around:

- A **verifier with no write tools cannot make a failing check pass by editing the check.**
  That is Steel Principle 1 enforced by tool scope rather than by instruction, and
  instructions are the layer that erodes under pressure.
- An **implementer with a declared file scope and no git tools** cannot commit, so the parent
  session stays the only thing that touches git history. This complements `gh-push-guard.py`,
  which only covers push and PR-create.

Definitions load **at session start**. A newly written agent file is not available in the
session that created it. Field-test after a restart, never before.

Reference implementations: `17.scratchpad/.claude/agents/readonly-verifier.md` and
`scoped-implementer.md`.

---

## Model Selection Guide

Choose the right model for each agent based on what the task actually demands. **Do NOT default to inheriting the parent's model, and do not default to the cheapest one either.** Choose the cheapest model that will produce the right result for the task.

### `haiku` - Literal Pattern Extraction Only

Use ONLY when the task is pure text pattern matching with no judgment required:

| Task | Why Haiku Is Sufficient |
|------|------------------------|
| Parse import/export statements | Extracting text from AST-like patterns, no interpretation |
| Find literal strings (`console.log`, `debugger`, `TODO`) | Exact string matching |
| Count files, list directories | Inventory, no analysis |
| Extract env variable names from .env.example | Reading key names, not values |
| Check if a file exists | Existence check |
| Gather package.json dependency names | Reading a JSON file |

**If you're unsure whether haiku is sufficient, use sonnet.** The quality difference matters.

**Cost is NOT negligible on a Max subscription (corrected 2026-10-16).** The weekly limit is the
binding constraint. Measured 2026-10-16: subagents were ~90% of fresh input tokens and 91% of their
calls ran on Opus 5.5, because a subagent with no `model` inherits the parent's. Always pass `model`
and `effort` explicitly, and give every agent a `description` that leads with its task number when
it has one (`#247 CySA+ currency check`). The rule and its table: `~/.claude/CLAUDE.md`
section 8 "Subagents".

### `sonnet` - The Default for Most Agent Work

Use for anything that requires understanding context, making judgments, or writing code:

| Task | Why Sonnet Is Needed |
|------|---------------------|
| Security vulnerability scanning | Must understand if a pattern is actually exploitable vs a false positive |
| RLS policy analysis | Must understand SQL semantics and authorization logic |
| React component analysis | Must understand props flow, rendering, effect dependencies |
| Compliance assessment | Must reason about legal requirements vs actual code behavior |
| Dead code determination | Must trace usage through dependency chains, not just grep |
| Type tightening | Must understand TypeScript type system to suggest correct replacements |
| Unused prop detection | Must understand component logic, not just prop destructuring |
| Pattern enforcement | Must compare code against conventions and understand intent |
| Code fixing / refactoring | Must write correct code that doesn't break anything |
| Complexity analysis | Must understand logic flow to suggest simplifications |
| Duplicate consolidation | Must design shared abstractions |
| Report synthesis | Must create coherent narrative from disparate findings |
| Build verification | Must interpret errors and iterate on fixes |
| Bundle analysis | Must reason about import chains and tree-shaking |
| API route analysis | Must understand auth patterns, error handling consistency |
| CSS/Tailwind analysis | Must understand utility interactions and overrides |
| Document generation | Must produce professional, accurate, well-structured content |

### `opus` - Complex Reasoning, Architecture, and High-Stakes Decisions

Use when the task demands deep reasoning, multi-step logic, or consequences of getting it wrong are significant:

| Task | Why Opus Is Warranted |
|------|----------------------|
| Architecture analysis | Must understand system-wide implications of design decisions |
| Complex refactoring planning | Must reason about cascading effects across many files |
| Security vulnerability triage (critical) | Must assess attack vectors, chain exploitability, determine real vs false positive on complex patterns |
| SOC 2 / compliance gap assessment | Must map code controls to regulatory frameworks with nuanced interpretation |
| Root cause analysis (complex bugs) | Must trace multi-file logic chains and reason about state |
| Vendor questionnaire answers | Must synthesize accurate, defensible answers from multiple data sources |
| Report synthesis (final, high-stakes) | When the report will be shared externally (enterprise prospects, auditors) |

### Decision Rule

**Literal string matching (find this exact text)** → `haiku`
**Reasoning about code, writing fixes, analyzing patterns** → `sonnet`
**Architecture decisions, high-stakes analysis, external-facing output** → `opus`

Choose the cheapest model that produces the right result for the task. Opus needs a one-clause
reason Sonnet would get it wrong; inheriting Opus by omission is not a choice.

---

## Agent Architecture

All multi-agent skills follow a two-tier hierarchy:

```
═══════════════════════════════════════════════════════════════
                    ORCHESTRATOR (you)
              Model: inherited from user session
              Role: coordinate, delegate, report
              NEVER: scan files, fix code, read full reports
═══════════════════════════════════════════════════════════════
                           │
           ┌───────────────┼───────────────┐
           │               │               │
     ┌─────┴─────┐  ┌─────┴─────┐  ┌─────┴─────┐
     │  SCOUT    │  │  SCOUT    │  │  SCOUT    │
     │ haiku or  │  │ haiku or  │  │ haiku or  │
     │ sonnet *  │  │ sonnet *  │  │ sonnet *  │
     │           │  │           │  │           │
     │ Scan      │  │ Scan      │  │ Scan      │
     │ Detect    │  │ Detect    │  │ Detect    │
     │ Write     │  │ Write     │  │ Write     │
     │ to disk   │  │ to disk   │  │ to disk   │
     └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
           │               │               │
           └───────┬───────┘               │
                   │ (results on disk)     │
           ┌───────┴───────┐               │
           │               │               │
     ┌─────┴─────┐  ┌─────┴─────┐  ┌─────┴─────┐
     │  FIX      │  │  FIX      │  │  ANALYSIS │
     │  (sonnet) │  │  (sonnet) │  │  (sonnet) │
     │           │  │           │  │           │
     │ Read      │  │ Read      │  │ Reason    │
     │ findings  │  │ findings  │  │ Analyze   │
     │ Auto-fix  │  │ Auto-fix  │  │ Recommend │
     │ Verify    │  │ Verify    │  │ Write     │
     │ build     │  │ build     │  │ to disk   │
     └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
           │               │               │
           └───────────────┴───────────────┘
                           │
                 [Results on disk]
                           │
               ┌───────────┴───────────┐
               │    ORCHESTRATOR       │
               │    reads summaries    │
               │    updates state      │
               │    updates report     │
               │    launches next      │
               │    batch              │
               └───────────────────────┘

* Scout model depends on task: haiku for literal pattern matching,
  sonnet for anything requiring judgment. See Model Selection Guide.
```

**Key rule:** Agents NEVER spawn sub-agents. Only the orchestrator spawns agents. Two-level hierarchy maximum.

---

## Agent Spawning Rules

### 1. Parallel Limits

- **Max 2 agents running in parallel** - prevents resource contention
- **Scout agents** can run in parallel (they're read-only)
- **Fix agents** run sequentially (they modify code - conflicts possible)
- Process results and checkpoint BEFORE spawning the next batch

### 2. Agents Write to Disk

- Agents write ALL detailed findings, reports, and data to disk
- Agents return ONLY a brief summary (< 500 tokens) to the orchestrator
- The orchestrator NEVER reads full agent report files into its own context

### 3. Agents Are Stateless

Each agent gets a self-contained prompt with everything it needs:
- Exact file list to work on
- What to look for (patterns, rules)
- Where to write output
- Output format (JSON structure)
- Budget (max tool calls)

### 4. Batch Sizing

Prevent any single agent from consuming too much context:

| Codebase Size | Files Per Scout Agent | Findings Per Fix Agent |
|--------------|----------------------|----------------------|
| < 50 files | All files in 1 agent | Up to 10 fixes |
| 50-150 files | 25-30 files per agent | Up to 8 fixes |
| 150-300 files | 15-20 files per agent | Up to 5 fixes |
| 300+ files | 10-15 files per agent | Up to 3 fixes |

---

## Agent Task Prompt Template

Every agent prompt MUST include these sections:

```markdown
## Task
[Clear, specific description of what to do]

## Files to Process
[Exact file paths - never "scan everything"]

## What to Look For
[Specific patterns with examples]

## Output
- Write detailed findings to: [exact file path]
- Use this JSON format: [structure]

## Rules
- [For scouts]: Do NOT fix anything. Do NOT modify files. Only scan and write findings.
- [For fixers]: Fix ONLY the items listed below. Verify build after each fix.
- Complete within [N] tool calls maximum.

## Return Format
Return ONLY a summary under 500 tokens:
---
AGENT: [name]
STATUS: COMPLETE / PARTIAL / FAILED
FINDINGS: [count]
AUTO_FIXABLE: [count]
DEFERRED: [count]
OUTPUT: [path to detailed report on disk]
---
```

---

## Orchestrator Workflow

The orchestrator follows this loop for every skill:

```
1. SETUP
   - Create state file on disk
   - Create living document report skeleton
   - Check for previous incomplete run (resume if found)

2. FOR EACH PHASE:
   a. Determine which agents to spawn (scout or fix)
   b. Prepare agent prompts with file batches
   c. Spawn agents (max 2 parallel)
   d. Collect agent summaries (< 500 tokens each)
   d2. STOP each agent (TaskStop) the moment its report is handled. See "Agent lifecycle" below.
   e. Update state file on disk
   f. Update living document report on disk
   g. Output brief status to user
   h. Proceed to next batch or phase

3. FINALIZE
   - ListAgents: stop anything still listed as completed or idle; only agents still working remain
   - Run final verification (build, type check, lint)
   - Write SITREP conclusion to report
   - Update history file
   - Output final summary to user
```

---

## Agent lifecycle: the orchestrator stops every agent it is done with (operator directive, 2026-10-12)

**The orchestrator owns each agent from dispatch to stop.** When an agent's report has been read and
acted on (committed, routed, or recorded as no action), stop it with `TaskStop` in the same turn. Do not
leave a finished agent registered: some keep background work running after their hand-back, and a list
of finished agents hides the ones still working from the operator.

- After each hand-back: handle it, then `TaskStop <agent id>`.
- **An `isolation: "worktree"` agent that changed files leaves a worktree and a branch behind.** In
  the same turn as its hand-back, merge its branch into yours or discard it, then
  `git worktree remove <path>` and `git branch -D <branch>` once its commits are on your branch (or
  deliberately thrown away). Measured 2026-10-17: one repo held 169 orphaned `wt-*` and
  `worktree-agent-*` branches and 114 dead worktree entries.
- Before any status reply, and at the end of a run: `ListAgents`, and stop every agent listed as
  completed. Only agents still working stay.
- A resumed agent (one you sent new scope to) is stopped only after its NEXT report, never on the strength
  of an older one.
- **Limit, measured 2026-10-12:** `TaskStop` marks the entry "killed" but does not delete it; no tool in
  reach removes an agent entry. Say so plainly if asked to remove one; never claim it was removed.

---

## Recovery from Context Reset

If context is lost mid-skill:

1. **Find the state file:** `.[skill]-reports/state-*.json` (most recent)
2. **Read it** - it tells you exactly what's done and what's pending
3. **Find the living document:** `.[skill]-reports/[report]-*.md`
4. **Resume from the next incomplete item** - NEVER re-run completed agents
5. **Agent results are on disk** - don't re-scan what's already been scanned

### Recovery Prompt

When resuming, the orchestrator should think:

```
"I am resuming [skill-name]. Reading state file to determine progress.
Completed phases: [list]. Next pending: [phase/agent].
Previous agent results are on disk at [paths]. Continuing from here."
```

---

## Skill-Specific Model Selection

Each skill should define its own model table in its AGENT ORCHESTRATION section. Here are common patterns:

### Audit Skills (sec-ship, compliance, a11y, perf, deps)

| Agent Type | Model | Why |
|-----------|-------|-----|
| Inventory scanners | `haiku` | Listing files, counting routes, extracting names - no judgment |
| Security scanners | `sonnet` | Must assess exploitability, understand auth logic, evaluate risk |
| Compliance analyzers | `sonnet` | Must reason about legal requirements vs code behavior |
| Accessibility analyzers | `sonnet` | Must understand ARIA semantics, keyboard nav patterns, screen reader behavior |
| Performance analyzers | `sonnet` | Must understand rendering, bundle impact, runtime performance |
| Fixers | `sonnet` | Must write correct code, handle edge cases, verify build |
| Report synthesizers | `sonnet` | Must create coherent, actionable narrative |

### Code Modification Skills (cleancode, test-ship)

| Agent Type | Model | Why |
|-----------|-------|-----|
| Literal pattern finders | `haiku` | console.log, TODO, debugger - exact string matches |
| Dead code analyzers | `sonnet` | Must trace dependency chains, understand usage context |
| React/framework analyzers | `sonnet` | Must understand component logic, hooks, rendering |
| Type analyzers | `sonnet` | Must understand TypeScript type system |
| Fixers / refactorers | `sonnet` | Must write correct code that doesn't break anything |
| Report synthesizers | `sonnet` | Must create before/after narrative |

### Documentation Skills (docs, compliance-docs)

| Agent Type | Model | Why |
|-----------|-------|-----|
| File inventory | `haiku` | Listing existing docs, counting coverage - no judgment |
| Content generators | `sonnet` | Must write professional, accurate documentation |
| Code analyzers (for docs) | `sonnet` | Must understand code to document the WHY, not just the WHAT |
| Link validators | `haiku` | URL existence checks - no judgment |
| Report synthesizers | `sonnet` | Must create coverage narrative and recommendations |

---

## Pre-Flight Checks

Before any skill begins its main work, the orchestrator MUST verify prerequisites. A failed build at the start wastes an entire run.

### Required Pre-Flight Checks (All Skills)

```
1. Git state: Is the working tree clean? (warn if uncommitted changes - they could interfere with rollback)
2. Build passes: Run `pnpm build` or equivalent - if the build is already broken, stop and tell the user
3. Dependencies installed: Check node_modules exists and is current (run install if needed)
4. Disk space: Ensure the reports directory can be created
5. Previous run check: Look for incomplete state files from the last 2 hours (offer to resume)
```

### Skill-Specific Pre-Flight Checks

Each skill should add checks relevant to its domain:

- **sec-ship**: Verify no active deploy is in progress
- **cleancode**: Record baseline LOC and complexity metrics before changes
- **test-ship**: Verify test framework is configured and at least one test file exists
- **perf**: Verify dev server can start (needed for Lighthouse)
- **deps**: Verify package.json and lock file are in sync
- **a11y**: Verify pages are accessible (dev server or build)

### Pre-Flight Failure

If pre-flight fails:
- Output a clear message explaining what's wrong
- Do NOT proceed with the skill
- Suggest how to fix the issue
- Do NOT attempt to auto-fix pre-flight failures (they're environment issues, not code issues)

---

## Historical Awareness (Read Your Own Past Reports)

Before starting any work, the orchestrator MUST check for previous reports from **its own skill's** past runs. This prevents:
- Rediscovering the same issues and giving the same advice every run
- Hitting the same roadblocks that were already documented
- Overriding decisions that were deliberately made (deferred items with a reason)
- Wasting tokens and time on analysis that's already been done

### How It Works

During pre-flight, after checking prerequisites:

```
1. Find the last 2-3 reports from this skill:
   ls -t .[skill]-reports/*-*.md | head -3

2. For each report, read ONLY the SITREP/conclusion section (last ~50 lines)
   This gives you:
   - What was found last time
   - What was fixed
   - What was DEFERRED and WHY
   - What was BLOCKED and WHY
   - What recommendations were made
   - The before/after metrics

3. Build a "historical context" summary (< 300 tokens):
   - "Run #3 (2026-02-10): Fixed 12 issues, deferred 3 (CC-015: too risky without tests,
     CC-022: needs architectural decision, CC-031: blocked by upstream dep).
     Recommendation: add tests before refactoring pricing module."
   - "Run #2 (2026-01-15): Fixed 8 issues, deferred 2 (same CC-015 and CC-022)."

4. Pass this context to relevant agents so they can:
   - Skip re-analyzing deferred items that haven't changed
   - Note when a previously deferred item can NOW be fixed (conditions changed)
   - Reference the decision history ("this was deferred twice before because X - revisiting because Y has changed")
   - Avoid recommending the same action that was already rejected
```

### What to Do with Historical Context

| Situation | Action |
|-----------|--------|
| Previously DEFERRED, conditions unchanged | Note in report: "Previously deferred (run #3, reason: X). Conditions unchanged. Keeping DEFERRED." Do NOT re-analyze in depth. |
| Previously DEFERRED, conditions changed | Re-analyze. Note: "Previously deferred (run #3, reason: X). Conditions have changed: [what changed]. Re-evaluating." |
| Previously BLOCKED | Check if the blocker is resolved. If not, note: "Still BLOCKED (same reason since run #2)." If resolved, attempt the fix. |
| Previously recommended, not acted on | Note but don't nag. "Recommendation from run #3 still applies: [recommendation]. Not yet implemented." |
| New finding not seen before | Analyze normally. No historical context needed. |

### Historical Context Budget

- Read ONLY the SITREP sections, NOT the full reports (stay under 300 tokens per previous run)
- Check at most 3 previous reports (going back further than that is diminishing returns)
- If no previous reports exist, skip this step entirely (first run)

---

## Agent Failure Handling

Agents can fail. The orchestrator must handle this gracefully, not crash.

### Failure Response Protocol

When an agent returns STATUS: FAILED or PARTIAL:

```
1. READ the failure summary (from the agent's return message)
2. CLASSIFY the failure:
   a. TRANSIENT - timeout, rate limit, temporary error
      → Retry ONCE with the same prompt
      → If retry fails → mark as BLOCKED, continue to next agent
   b. SCOPE - agent ran out of tool calls before finishing
      → Split the batch: re-run with half the files
      → If still fails → mark remaining files as DEFERRED
   c. CODE - agent encountered an error in the code it was analyzing/fixing
      → Record the error in the report
      → Mark the specific finding as BLOCKED with the error details
      → Continue to next agent (don't let one failure stop the pipeline)
   d. BUILD - fix agent's change broke the build
      → Agent should have already rolled back (per its instructions)
      → If not rolled back → orchestrator runs git checkout on the affected files
      → Mark the finding as BLOCKED ("fix broke build - needs manual review")
      → Continue to next agent

3. UPDATE the state file and living document with the failure details
4. CONTINUE - never stop the entire pipeline because one agent failed
```

### Retry Limits

| Failure Type | Max Retries | After Max Retries |
|-------------|-------------|-------------------|
| Transient | 1 | Mark BLOCKED, continue |
| Scope (too many files) | 2 (with smaller batches) | Mark remaining as DEFERRED |
| Code error | 0 (don't retry) | Mark BLOCKED, continue |
| Build failure | 0 (don't retry) | Rollback, mark BLOCKED, continue |

### Never Block the Pipeline

The orchestrator MUST complete all phases even if some agents fail. A skill run with 80% of agents succeeding is far more valuable than a skill run that dies at 20% because one agent failed.

---

## Cross-Skill Awareness

Skills should be aware of recent reports from related skills. This prevents:
- Conflicting changes (cleancode removes code that sec-ship flagged for fixing)
- Duplicate work (perf already identified the same issue cleancode found)
- Missed context (a11y findings that affect how cleancode should refactor a component)

### How It Works

At the start of each skill run (during pre-flight), check for recent reports from related skills:

```
Related skill report directories to check:
- .security-reports/        (sec-ship findings)
- .cleancode-reports/       (cleancode findings)
- .compliance-reports/      (compliance findings)
- .compliance-docs-reports/ (compliance-docs outputs)
- .test-reports/            (test-ship findings)
- .perf-reports/            (perf findings)
- .a11y-reports/            (a11y findings)
- .deps-reports/            (deps findings)
- .docs-reports/            (docs findings)

For each directory that exists:
1. Find the most recent state file (state-*.json)
2. Check if it's from the last 30 days
3. If yes, note the key findings in a one-line summary
4. Pass this context to relevant agents
```

### Cross-Skill Rules

| Running Skill | Check Reports From | Why |
|--------------|-------------------|-----|
| `/cleancode` | sec-ship, perf, a11y | Don't remove code flagged for security fixes. Don't refactor components perf flagged for optimization. Respect a11y-required patterns. |
| `/sec-ship` | cleancode, deps | If cleancode recently ran, unused code is already removed. Check deps report for known CVEs already handled. |
| `/perf` | cleancode, a11y | If cleancode recently simplified components, re-measure. Don't optimize away a11y-required DOM elements. |
| `/a11y` | cleancode, perf | If cleancode removed components, skip them. If perf flagged heavy components, note the a11y cost of optimization. |
| `/test-ship` | cleancode, sec-ship | Don't write tests for code cleancode flagged as dead. Prioritize testing code sec-ship flagged as risky. |
| `/deps` | sec-ship | Check if sec-ship already flagged the same CVEs. |
| `/compliance` | sec-ship, compliance-docs | Check if security controls are already documented. |
| `/docs` | cleancode | Skip documenting code that cleancode flagged as dead. |

### Implementation

The orchestrator does NOT read full reports from other skills. It reads ONLY the state file summary (a few lines of JSON) to get:
- What was the last run date?
- How many findings? How many fixed?
- Any BLOCKED or DEFERRED items that overlap with the current skill's scope?

This adds minimal context overhead (< 200 tokens per related skill) while preventing conflicts.

---

## Reference in Skills

Add this section to any skill that spawns sub-agents:

```markdown
## AGENT ORCHESTRATION

This skill follows the **[Agent Orchestration Protocol](~/.claude/standards/AGENT_ORCHESTRATION.md)**.

### Model Selection for This Skill

| Agent | Model | Task |
|-------|-------|------|
| [agent-1] | `haiku` | [what it does] |
| [agent-2] | `sonnet` | [what it does] |
| ... | ... | ... |

### Agent Batching

[Skill-specific batching rules based on codebase size]
```

---

## SITREP Requirements (Before/After State Documentation)

Every skill run MUST end with a SITREP (Situation Report) that documents the before and after state. This is not optional - it's the historical record that future runs will read for context.

### Required SITREP Sections

Every skill's final report MUST include these sections in the SITREP:

#### 1. Before/After Metrics Table

Quantitative comparison of the codebase state before and after the skill ran:

```markdown
## Before/After State

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| [skill-specific metric 1] | X | Y | +/- Z |
| [skill-specific metric 2] | X | Y | +/- Z |
| ... | ... | ... | ... |
```

Each skill defines its own metrics. Examples:

| Skill | Key Metrics |
|-------|------------|
| `/cleancode` | Lines of code, unused exports, zombie code, complexity score, any types, console.logs, TODOs |
| `/sec-ship` | Critical vulns, high vulns, medium vulns, low vulns, RLS coverage %, rate-limited routes % |
| `/perf` | Lighthouse score, LCP, FID, CLS, bundle size, image optimization % |
| `/a11y` | WCAG violations (A/AA/AAA), keyboard-navigable %, color contrast issues, ARIA errors |
| `/deps` | Outdated deps, critical CVEs, high CVEs, license risks, unmaintained deps |
| `/test-ship` | Test count, pass rate, coverage %, untested critical paths, flaky tests |
| `/compliance` | Compliance gaps, policy completeness %, data collection disclosed %, link validation % |
| `/docs` | Documentation coverage %, undocumented exports, stale docs, missing sections |

#### 2. What Was Accomplished

Narrative summary of the work done. Be specific:

```markdown
### What Was Accomplished

1. **[Category]:** [Specific description with counts]
   - Fixed X issues in Y files
   - Consolidated Z duplicate patterns into shared utility

2. **[Category]:** [Specific description]
   ...
```

#### 3. What Was Deferred and Why

Every DEFERRED item gets documented with the reason. This is critical for historical awareness - future runs will read this.

```markdown
### Deferred Items

| ID | Finding | Why Deferred | Conditions to Revisit |
|----|---------|-------------|----------------------|
| CC-015 | Complex pricing function (complexity 22) | No test coverage - refactoring without tests is too risky | Revisit after test-ship adds tests for this module |
| SEC-008 | Rate limiting on webhook endpoint | Webhooks need to accept high throughput from Stripe | Revisit if abuse is detected in production logs |
```

**"Conditions to Revisit"** is the most important column. It tells future runs WHEN this item should be re-evaluated, not just why it was skipped.

#### 4. What Was Blocked and Why

Every BLOCKED item with the specific blocker:

```markdown
### Blocked Items

| ID | Finding | Blocker | What Needs to Happen |
|----|---------|---------|---------------------|
| CC-031 | Unused dep 'legacy-auth' | Removing it breaks build - hidden transitive dependency | Investigate which module actually needs it, then remove properly |
```

#### 5. Recommendations

Actionable next steps. Reference specific findings and other skills when relevant:

```markdown
### Recommendations

1. Run `/test-ship` to add tests for the pricing module before refactoring (blocked CC-015)
2. Schedule `/deps` run - 3 dependencies have known CVEs that couldn't be auto-updated
3. Consider running `/perf` - removed 2,400 lines of dead code which may improve bundle size
```

#### 6. Historical Context (if previous runs exist)

Reference what changed since the last run:

```markdown
### Historical Context

This is run #4 for this project.
- Run #3 (2026-02-10): 12 issues fixed, 3 deferred. CC-015 still deferred (same reason).
- CC-022 was deferred in runs #2 and #3 - resolved this run because tests were added.
- Overall trend: Codebase health improving. Technical debt reduced 45% since run #1.
```

### SITREP Quality Standards

- **Specific, not vague** - "Removed 23 unused exports from 12 files" not "cleaned up dead code"
- **Quantified** - Numbers, percentages, before/after deltas
- **Decision-aware** - Document WHY things were deferred, not just that they were
- **Forward-looking** - What should happen next, what conditions would change deferred decisions
- **Cross-skill aware** - Reference other skills when recommendations involve them
- **Honest** - If something wasn't fixed because it was too hard or risky, say so. Don't hide it.

---

## Why This Matters

- **Without orchestration protocol:** The orchestrator tries to do everything itself, fills its context window, and the session dies halfway through. User loses progress, wastes time.
- **With orchestration protocol:** The orchestrator stays lean (coordination only), heavy work is delegated to focused agents, state lives on disk, and recovery is instant. Zero wasted effort, consistent execution across all skills.

---

**Last Updated:** 2026-02-17
