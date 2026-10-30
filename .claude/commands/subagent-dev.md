---
description: "/subagent-dev - Automated plan execution with two-stage review per task: dispatch implementer, then spec compliance reviewer, then code quality reviewer. Model selection per task. No task complete without review."
allowed-tools: Bash(git *), Bash(npx *), Bash(npm *), Bash(pnpm *), Bash(yarn *), Bash(node *), Bash(cat *), Bash(ls *), Bash(find *), Bash(grep *), Bash(mkdir *), Bash(date *), Read, Write, Edit, Glob, Grep, Agent
when_to_use: Trigger phrases: "execute the plan", "implement all these tasks with review"
---

# /subagent-dev - Automated Plan Execution with Two-Stage Review

**Steel Principle: No task complete without spec compliance review AND code quality review.**

This skill is the execution engine for plans produced by `/brainstorm` or `/mdmp`. It dispatches a fresh sub-agent for each task, then runs TWO separate reviews before marking the task done. The implementer never marks their own work complete - review is mandatory.

**FIRE AND FORGET** - Point at a spec/plan. The skill executes every task with full review cycle.

> **When to use /subagent-dev:**
> - After `/brainstorm` produces an approved spec
> - After `/mdmp` produces a selected COA with task list
> - When you have a written plan with discrete tasks
> - Multi-file/multi-task features where quality matters
>
> **When NOT to use /subagent-dev:**
> - No plan/spec exists → run `/brainstorm` or `/mdmp` first
> - Single trivial change → just do it inline
> - Debugging → `/investigate`
> - Emergency fix → `/incident`

---

## DISCIPLINE

> Reference: [Superpowers Discipline Protocol](~/.claude/standards/STEEL_DISCIPLINE.md)

Key enforcements for this skill:

- **Steel Principle #1:** NO completion claims without fresh verification evidence (both reviewers verify independently)
- **Steel Principle #3:** NO production code without a failing test first (TDD enforced per task)
- **Steel Principle #4:** Spec exists before execution begins
- **Steel Principle #5:** Plan is specific and complete before tasks are dispatched

### Subagent-Dev Rationalization Table

| Rationalization | Reality | What to Do |
|----------------|---------|------------|
| "The implementer says DONE, we can trust it" | Implementers mark DONE when they think they're done. Not when they ARE done. | Run both reviews. Always. |
| "This task is too simple for review" | Simple tasks fail review for subtle reasons more often than complex ones | Review every task. No exceptions. |
| "I can combine spec + quality review" | Combined reviews miss BOTH "does it match spec" AND "is it well-built" | Two separate stages. In order. |
| "The implementer will fix issues found" | Only if you TELL them. And only if you VERIFY the fix. | Re-dispatch with specific issues. Re-review after fix. |
| "We're behind, skip the review to catch up" | Skipping review creates bugs that take longer than review would | Review is faster than debugging in production |
| "Parallel implementers would be faster" | Parallel implementers on same codebase cause merge conflicts and contradictory changes | Sequential implementation. Parallel reviews only. |

---

## STATUS UPDATES

> Reference: [Status Update Protocol](~/.claude/standards/STATUS_UPDATES.md)

```
🤖 /subagent-dev Started
   Spec: [path to spec]
   Tasks identified: [N]
   Worktree: [path] (isolated)

📋 Task 1/N: [task name]
   🔧 Implementer (sonnet) dispatched
   └─ Status: DONE | Modified: 3 files | Tests: 2 added

   🔍 Spec Compliance Review (sonnet)
   └─ Verdict: PASS | All requirements met

   🔍 Code Quality Review (sonnet)
   └─ Verdict: PASS | Clean, tested, maintainable

   ✅ Task 1 complete

📋 Task 2/N: [task name]
   🔧 Implementer (sonnet) dispatched
   └─ Status: DONE_WITH_CONCERNS

   🔍 Spec Compliance Review (sonnet)
   └─ Verdict: FAIL - missing edge case from spec
   🔧 Implementer fix dispatched
   └─ Status: DONE
   🔍 Re-review: PASS

   🔍 Code Quality Review (sonnet)
   └─ Verdict: PASS

   ✅ Task 2 complete

📋 ...

🔍 Final Code Review (opus) - entire implementation
   └─ Verdict: PASS | Integration coherent, no scope drift

✅ /subagent-dev Complete
   Tasks: N/N complete
   Review cycles: X (Y required re-work)
   Handoff: /test-ship then /gh-ship
```

---

## CONTEXT MANAGEMENT

> Reference: [Context Management Protocol](~/.claude/standards/CONTEXT_MANAGEMENT.md)

Key rules for this skill:
- Orchestrator NEVER writes implementation code - only dispatches agents
- Each agent returns < 500 tokens summary; full work is on disk
- State file tracks task progress, review cycles, model selections
- Sequential task execution (parallel implementers conflict); parallel reviews OK

---

## AGENT ORCHESTRATION

> Reference: [Agent Orchestration Protocol](~/.claude/standards/AGENT_ORCHESTRATION.md)

### Model Selection for This Skill

| Agent Role | Model | Why |
|-----------|-------|-----|
| Implementer (mechanical, 1-2 files, clear spec) | `sonnet` | Must write correct code, handle edge cases |
| Implementer (integration, multi-file, judgment) | `sonnet` | Same - quality matters |
| Implementer (architectural, cross-cutting) | `opus` | Complex reasoning about system-wide implications |
| Spec Compliance Reviewer | `sonnet` | Reads code and compares to spec line-by-line |
| Code Quality Reviewer | `sonnet` | Evaluates maintainability, tests, clean code |
| Final Integration Reviewer | `opus` | Reviews entire implementation holistically |

**Auto-selection:** Before dispatching an implementer, assess task complexity:
- 1-2 files, pattern from spec is clear → sonnet
- 3+ files or novel pattern → sonnet (not opus - saves for integration review)
- Architectural decision affecting multiple subsystems → opus

---

## OUTPUT STRUCTURE

```
.subagent-dev-reports/
├── SUBDEV-YYYYMMDD-HHMMSS.md     # Living execution report
├── state-YYYYMMDD-HHMMSS.json    # Resumable state
├── tasks/
│   ├── task-01-implementer.md     # Implementer output per task
│   ├── task-01-spec-review.md     # Spec compliance review
│   ├── task-01-quality-review.md  # Code quality review
│   └── ...
└── final-review.md                # Final integration review
```

---

## PHASE 0: INTAKE & SETUP

### 0.1 Parse the Spec/Plan

The user passes a path to a spec (from `/brainstorm`) or a plan (from `/mdmp`). Extract:
- **Title/Topic:** What's being built
- **Tasks:** Discrete units of work (numbered, 2-5 minutes each)
- **Dependencies:** Which tasks block others
- **Success criteria:** What "done" looks like for each task

### 0.2 Validate the Plan

Check for placeholder violations (Steel Principle #5):

```bash
# Grep for forbidden phrases
grep -iE "(TBD|TODO|implement later|similar to Task|as needed|figure out)" [spec path]
```

If found: STOP. Report the placeholders. Request user fix the spec (or return to `/brainstorm` / `/mdmp`).

### 0.3 Create Worktree (Isolation)

```bash
# Check for worktree convention in project
if [ -d ".worktrees" ] || grep -q "worktree" CLAUDE.md; then
  WORKTREE_DIR=".worktrees"
else
  WORKTREE_DIR=".worktrees"  # Default
fi

mkdir -p "$WORKTREE_DIR"
grep -q "$WORKTREE_DIR" .gitignore || echo "$WORKTREE_DIR/" >> .gitignore

# Create branch + worktree
BRANCH="feature/$(basename [spec path] .md)"
git worktree add "$WORKTREE_DIR/$BRANCH" -b "$BRANCH"
cd "$WORKTREE_DIR/$BRANCH"

# Install deps + verify baseline
[pnpm/npm] install
[pnpm/npm] test  # Baseline must be clean
[pnpm/npm] build  # Baseline must build
```

If baseline fails: STOP. Report the broken baseline. User must fix main before subagent-dev runs.

### 0.4 Create Infrastructure

```bash
mkdir -p .subagent-dev-reports/tasks
grep -q ".subagent-dev-reports" .gitignore || echo ".subagent-dev-reports/" >> .gitignore
```

---

## PHASE 1: TASK DECOMPOSITION

Read the spec. Extract all tasks. For each task, record:

```json
{
  "id": "task-01",
  "title": "Create UserProfile component",
  "full_text": "[entire task description from the plan]",
  "files_expected": ["src/components/UserProfile.tsx", "src/components/UserProfile.test.tsx"],
  "dependencies": [],
  "estimated_complexity": "simple",
  "model": "sonnet"
}
```

Save to state file. This is the orchestrator's checklist.

---

## PHASE 2: TASK EXECUTION LOOP

For each task in order (respecting dependencies):

### 2.1 Dispatch Implementer

```
Task tool with model=[selected model]:

You are implementing task [N] of [total] from the spec at [path].

## Your Task

[Full task text from the plan - not a reference, the entire text]

## Context

[Scene-setting: what this code does, how it fits, why it matters]

## Success Criteria

[Specific, verifiable checklist from the spec]

## Constraints

- TDD: Write the failing test first. Watch it fail. Write the code. Watch it pass.
- Scope lock: Only touch files listed in the spec for this task
- No placeholders: Every line of code is real, working code
- Verification required: Run `pnpm build` and `pnpm test` before claiming DONE

## Context Management

- Write all detailed output (full diffs, test output, reasoning) to:
  `.subagent-dev-reports/tasks/task-[N]-implementer.md`
- Return ONLY a summary under 500 tokens

## Return Format

---
AGENT: implementer
TASK: task-[N]
STATUS: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED
FILES_MODIFIED: [count]
FILES_CREATED: [count]
TESTS_ADDED: [count]
BUILD: PASS | FAIL
TESTS: [X/Y passing]
CONCERNS: [if any, brief]
OUTPUT: .subagent-dev-reports/tasks/task-[N]-implementer.md
---
```

### 2.2 Handle Implementer Status

| Status | Controller Action |
|--------|-------------------|
| `DONE` | Proceed to Spec Compliance Review |
| `DONE_WITH_CONCERNS` | Read concerns, decide: dispatch reviewer anyway OR address concerns first |
| `NEEDS_CONTEXT` | Provide the missing context, re-dispatch |
| `BLOCKED` | Evaluate: can we re-scope? Is it architectural? Ask user if truly blocked. |

### 2.3 Spec Compliance Review (Stage 1)

```
Task tool with model=sonnet:

You are reviewing task [N] for SPEC COMPLIANCE. Your job: does the implementation build WHAT was requested?

## The Spec

[Full task text from the plan]

## The Implementer's Claim

[Status: DONE, files modified: X, tests added: Y]

## CRITICAL INSTRUCTION

The implementer finished suspiciously quickly. Their report may be incomplete or inaccurate. DO NOT trust the implementer's report. Read the ACTUAL CODE and compare it to the spec line-by-line.

## What to Check

1. Every requirement in the spec is actually implemented
2. No missing edge cases the spec mentioned
3. No extra work beyond the spec (scope creep)
4. Files modified match files expected

## What NOT to Check (That's Stage 2)

- Code quality
- Test quality
- Naming conventions
- SOLID principles
- Maintainability

## Return Format

---
AGENT: spec-reviewer
TASK: task-[N]
VERDICT: PASS | FAIL
MISSING: [list of spec items not implemented]
EXTRA_SCOPE: [list of work beyond spec]
FILE_MISMATCHES: [files changed that shouldn't have been, or missing]
EVIDENCE: [specific file:line references proving findings]
OUTPUT: .subagent-dev-reports/tasks/task-[N]-spec-review.md
---
```

### 2.4 Spec Review Handling

- **PASS** → proceed to Code Quality Review
- **FAIL** → re-dispatch implementer with specific issues, loop until PASS

```
Re-dispatch implementer with:
"Spec compliance review failed. Fix these issues:
- [specific issue 1 from reviewer]
- [specific issue 2 from reviewer]

Do NOT make any other changes. Only address these findings.
Then re-run verification and report."
```

### 2.5 Code Quality Review (Stage 2)

ONLY runs after Spec Compliance passes.

```
Task tool with model=sonnet:

You are reviewing task [N] for CODE QUALITY. Your job: is what they built WELL-CONSTRUCTED?

## Context

Spec compliance already verified. Now evaluate HOW the code was built.

## What to Check

- **Naming:** Clear, consistent, follows project conventions
- **Tests:** Present, meaningful, cover edge cases (not just happy path)
- **Structure:** Separation of concerns, file responsibilities clear
- **Error handling:** Appropriate for the context, not over/under
- **Anti-patterns:** No mock-what-you-test, no mysterious guards, no dead code
- **Complexity:** Functions have single responsibility, logic is readable
- **Tight coupling:** Components could be tested in isolation
- **Security:** No obvious vulnerabilities introduced (XSS, SQLi, etc.)

## Severity Levels

- **CRITICAL:** Must fix before merge (security, correctness, or breaks existing behavior)
- **IMPORTANT:** Should fix (maintainability, clarity, test coverage)
- **MINOR:** Note for later (polish, style, micro-optimizations)

## Return Format

---
AGENT: quality-reviewer
TASK: task-[N]
VERDICT: PASS | FAIL (FAIL = any CRITICAL or blocking IMPORTANT issues)
STRENGTHS: [what was done well]
CRITICAL: [issues that must be fixed]
IMPORTANT: [issues that should be fixed]
MINOR: [notes for later]
OUTPUT: .subagent-dev-reports/tasks/task-[N]-quality-review.md
---
```

### 2.6 Quality Review Handling

- **PASS** → task complete, proceed to next task
- **FAIL on CRITICAL** → re-dispatch implementer with specific issues, loop until PASS
- **FAIL on IMPORTANT only** → decide: block (re-dispatch) or note and proceed (if truly non-blocking)

### 2.7 Mark Task Complete

Update state file:
```json
{
  "task": "task-01",
  "status": "complete",
  "implementer_cycles": 2,
  "spec_review_verdict": "PASS",
  "quality_review_verdict": "PASS",
  "commit_sha": "[sha of completion commit]"
}
```

Move to next task.

---

## PHASE 3: INTEGRATION (After All Tasks Complete)

### 3.1 Run Full Verification

```bash
pnpm build          # Must pass
pnpm test           # Must pass (full suite)
pnpm typecheck      # Must pass
pnpm lint           # Must pass
```

If any fail: identify which task introduced the issue (likely last one). Dispatch implementer for that task with failure details. Re-review.

### 3.2 Final Integration Review

```
Task tool with model=opus:

You are doing a FINAL INTEGRATION REVIEW of the entire implementation.

## Implementation Summary

Spec: [path]
Tasks completed: [N]
Files modified: [list]
Files created: [list]

## What to Check

- **Coherence:** Does the whole implementation tell a consistent story?
- **Scope drift:** Is anything outside the original spec?
- **Integration seams:** Do the pieces from different tasks actually work together?
- **Overall quality:** Is this something you'd approve as a PR reviewer?
- **Regression risk:** Anything in the broader codebase likely affected?

## Review Output

---
AGENT: integration-reviewer
VERDICT: SHIP | REVISE | MAJOR_CONCERNS
SCOPE_DRIFT: [any work beyond spec]
INTEGRATION_ISSUES: [cross-task problems]
REGRESSION_RISK: [areas likely affected]
OVERALL: [summary paragraph]
OUTPUT: .subagent-dev-reports/final-review.md
---
```

### 3.3 Handle Final Verdict

- **SHIP** → proceed to handoff
- **REVISE** → address specific issues, re-run final review
- **MAJOR_CONCERNS** → escalate to user with full context

---

## PHASE 4: HANDOFF

```
✅ All tasks complete with two-stage review
   Spec: [path]
   Tasks: N/N
   Review cycles: X (Y required rework)
   Worktree: [path]
   Branch: [name]

Recommended handoff:
1. /test-ship - Verify test coverage is comprehensive
2. /sec-ship --diff - Security check on the changes
3. /gh-ship - Commit, push, PR, deploy

Or you can review the worktree manually before proceeding.
```

---

## CLEANUP PROTOCOL

> Reference: [Resource Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md)

### Subagent-Dev-Specific Cleanup

1. **Worktree preservation** - Do NOT delete worktree. User will use it for `/test-ship`, `/gh-ship`, or merge.
2. **Agent output files** - Keep in `.subagent-dev-reports/tasks/` for audit trail. Auto-clean after 30 days.
3. **State file** - Keep for resume capability. Auto-clean after 7 days of completion.
4. **No test data** - should not have been created outside tests
5. **Build/test artifacts** - node_modules, .next/, etc. belong to worktree, not a cleanup issue

---

## SITREP

> Reference: [SITREP Standard](~/.claude/standards/SITREP_FORMAT.md)

```markdown
## SITREP - /subagent-dev

**Spec:** [path]
**Worktree:** [path]
**Branch:** [name]
**Duration:** [X minutes]
**Status:** SHIP / REVISE / BLOCKED

### Execution Summary

| Task | Status | Implementer Cycles | Spec Review | Quality Review |
|------|--------|-------------------|-------------|----------------|
| 1 | Complete | 1 | PASS | PASS |
| 2 | Complete | 2 | FAIL→PASS | PASS |
| ... | ... | ... | ... | ... |

### Metrics
- Total tasks: [N]
- First-pass success rate: [X/N]
- Total re-work cycles: [Y]
- Files created: [count]
- Files modified: [count]
- Tests added: [count]
- Lines added: [count]

### Final Integration Review
- Verdict: [SHIP/REVISE]
- Overall: [one paragraph]

### Handoff
- Next: `/test-ship` → `/gh-ship`
- Worktree: [path] (preserved)
- Reports: `.subagent-dev-reports/`
```

---

## RELATED SKILLS

**Feeds from:**
- `/brainstorm` - the approved spec from brainstorm's Phase 5 is the primary input
- `/mdmp` - the selected COA with task list from MDMP is the primary input for larger plans

**Feeds into:**
- `/test-ship` - after all tasks are complete, run test-ship to verify coverage before shipping
- `/sec-ship` - run sec-ship on the diff to catch any security issues introduced during implementation
- `/gh-ship` - the standard next step after subagent-dev: commit, push, PR, deploy

**Pairs with:**
- `/smoketest` - quick sanity check during development to catch obvious build breaks early
- `/qatest` - functional validation of the completed feature before shipping

**Auto-suggest after completion:**
When all tasks pass both review stages (SHIP verdict), suggest in order: `/test-ship` then `/gh-ship` to ship the completed work

---

## REMEMBER

- **Two-stage review is non-negotiable** - spec compliance THEN code quality, in order
- **Don't trust the implementer** - reviewers read actual code, not reports
- **Sequential implementation, parallel reviews** - parallel implementers cause conflicts
- **Model selection matters** - sonnet for most, opus only for architectural/integration
- **Worktree isolates the work** - main branch stays clean during execution
- **Every task has a complete trail** - implementer output + both reviews + commit

<!-- Claude Code Skill - Superpowers methodology adapted for Steel Motion skill architecture -->
<!-- Incorporates subagent-driven-development from obra/superpowers (MIT License) -->
