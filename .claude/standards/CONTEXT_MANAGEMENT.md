# Context Management Protocol for Agent-Spawning Skills

**Version:** 1.0
**Applies to:** All skills in `~/.claude/commands/` that spawn sub-agents via the Task tool

---

## The Problem

When the orchestrator (main Claude session) spawns sub-agents via the Task tool, each agent returns results to the orchestrator's context window. If multiple agents return detailed findings, file contents, or verbose output, the orchestrator's context fills up and the session dies. The user must then `/clear` and restart, losing all progress and wasting time re-reading files and re-running work.

**This is the #1 cause of wasted effort in multi-agent skill runs.**

---

## Core Rules

### Rule 1: Sub-Agent Return Budget - 500 Tokens Maximum

Every sub-agent prompt MUST include this instruction:

> "Return ONLY a structured summary under 500 tokens. Your full output is already on disk. Do NOT echo back file contents, full findings lists, or verbose logs."

Sub-agents write full reports/results to disk. Only a brief structured summary comes back to the orchestrator.

### Rule 2: State Lives on Disk

The orchestrator maintains a machine-readable state file (JSON or JSONL) on disk:

```
.[skill]-reports/state-YYYYMMDD-HHMMSS.json
```

This file tracks:
- Which sub-agents/phases have completed
- Scores or key metrics from each
- Which sub-agents/phases remain
- Paths to detailed report files

Update this file after EVERY sub-agent completes or phase finishes.

### Rule 3: Resume Protocol

At startup, check for an incomplete state file from the last 2 hours:

```bash
find .[skill]-reports/ -name "state-*.json" -mmin -120
```

If found and work remains:
- Read the state file
- Report to user: "Resuming - X/Y steps already complete"
- Skip completed work, resume from the next step
- Never redo completed work

### Rule 4: Sequential by Default

Run sub-agents one at a time unless they are truly independent (different repos, different files, no shared state).

- **Max parallel agents:** 2 (to limit context accumulation)
- Process each agent's result and update disk state BEFORE spawning the next batch
- If running 2 in parallel, process both results and checkpoint before the next pair

### Rule 5: Never Ingest Full Reports

The orchestrator must NEVER use the Read tool to load a sub-agent's full report file into its own context. The summary returned by the sub-agent is sufficient for orchestration. Users read the full reports themselves from disk.

### Rule 6: Checkpoint Every 3 Steps

After every 3 sub-agents or phases, the orchestrator should:
1. Ensure the state file is current on disk
2. Assess whether context is getting heavy
3. If heavy: summarize progress in a brief message and continue
4. Do NOT stop to ask the user - continue working

### Rule 7: Lean Orchestrator Messages

Keep progress messages to the user short:

**Good:**
```
[3/8] Performance audit: 82/100 (B) - 0 critical, 2 warnings
Report: .perf-reports/perf-20260212-103000.md
```

**Bad:**
```
Performance audit complete. Found 2 warnings:
1. Bundle size is 1.8MB, which exceeds the recommended 500KB threshold...
   [15 lines of detail]
2. Images in components/home/ are using raw <img> tags instead of next/image...
   [10 lines of detail]
The full report has been written to...
```

---

## Sub-Agent Prompt Template

When spawning a sub-agent that performs work and returns results, include these constraints in the prompt:

```
CONTEXT MANAGEMENT RULES (MANDATORY):
1. Write all detailed output to disk (report files, logs, findings)
2. Return ONLY a structured summary under 500 tokens
3. DO NOT return full file contents, finding lists, or verbose output
4. Your detailed work is preserved on disk - the orchestrator only needs the summary
5. Use this return format:

---
AGENT: [agent-name]
STATUS: [COMPLETE / PARTIAL / FAILED]
SCORE: [0-100 if applicable]
KEY_METRICS:
- [metric 1]
- [metric 2]
TOP_FINDINGS:
1. [one-line finding]
2. [one-line finding]
3. [one-line finding]
OUTPUT: [path to detailed report on disk]
---
```

---

## State File Format

```json
{
  "skill": "[skill-name]",
  "project": "[project-name]",
  "started": "ISO-8601 timestamp",
  "status": "in_progress | complete | failed",
  "steps_completed": ["step-1", "step-2"],
  "steps_remaining": ["step-3", "step-4"],
  "results": {
    "step-1": {
      "status": "complete",
      "score": 85,
      "critical": 0,
      "warnings": 3,
      "report": ".reports/step-1-report.md"
    }
  },
  "last_checkpoint": "ISO-8601 timestamp"
}
```

---

## Implementation Checklist

For each skill that spawns sub-agents:

- [ ] Sub-agent prompts include 500-token return limit
- [ ] State file created at startup (before work begins)
- [ ] State file updated after each sub-agent/phase completes
- [ ] Resume protocol checks for recent incomplete state
- [ ] Sequential execution by default (max 2 parallel)
- [ ] Full reports written to disk, not returned to orchestrator
- [ ] Checkpoint every 3 steps
- [ ] Lean progress messages to user

---

## Reference in Skills

Add this section to any skill that spawns sub-agents:

```markdown
## CONTEXT MANAGEMENT

This skill follows the **[Context Management Protocol](~/.claude/standards/CONTEXT_MANAGEMENT.md)**.

Key rules:
- Sub-agents return < 500 tokens (full reports on disk)
- State file on disk, updated after each step
- Resume from checkpoint if context resets
- Sequential execution (max 2 parallel)
```

---

## Why This Matters

- **Without this protocol:** A skill spawning 5+ agents will exhaust the orchestrator's context window ~60% of the time, forcing a restart and losing 10-30 minutes of work.
- **With this protocol:** The orchestrator stays lean, state is preserved on disk, and work can resume even after a context reset. Zero wasted effort.

---

**Last Updated:** 2026-02-12
