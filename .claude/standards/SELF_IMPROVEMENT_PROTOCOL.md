# Self-Improvement Protocol

**Reference standard for skills with recurring patterns of failure.** Skills that run repeatedly should learn from their own history.

## When to apply

Apply this protocol to any skill that:
- Runs across multiple invocations on the same project
- Encounters varied real-world failures
- Has a "fix loop" where the same patterns recur

Examples: `/gh-ship`, `/sec-ship`, `/test-ship`, `/qatest`, `/monitor`, `/deps`

## The pattern

### 1. Per-project history file

Each invocation appends to a per-project history file at the repo root:
`.<skill>-history.json` (e.g., `.gh-ship-history.json`, `.sec-ship-history.json`)

The file is gitignored automatically by Stage 0.

Schema:
```json
{
  "schema_version": 1,
  "runs": [
    {
      "run_id": "ISO-8601-timestamp",
      "duration_seconds": 154,
      "stages_reached": ["..."],
      "failures_encountered": [
        {
          "stage": "9",
          "shape": "ruff-E401-multiple-imports",
          "log_excerpt": "...",
          "fix_applied": "split imports into separate lines",
          "succeeded": true
        }
      ],
      "anomalies": [...],
      "outcome": "success | partial | failed"
    }
  ],
  "patterns_observed": {
    "ruff-E401": {
      "first_seen": "2026-05-03",
      "count": 3,
      "fix_known": true,
      "last_successful_fix": "split imports into separate lines"
    }
  }
}
```

### 2. Read at Stage 0 / pre-flight

```
At Stage 0, read .<skill>-history.json if it exists.
Extract patterns_observed → known fix shapes.
Extract last run's outcome → if failed, prepare for elevated caution.
Extract any "wip_branches_protected" or similar sticky-state across runs.
```

### 3. Append at Stage 13 / SITREP

After every run (success OR failure), append a complete entry. Failure entries include log excerpts so future runs can recognize the shape.

### 4. Use during fix loops

Before trying a fix, check `patterns_observed`:
- If the current failure matches a known shape AND the prior fix worked: try it FIRST
- If the prior fix DIDN'T work last time: try a different approach
- If new shape: try smallest-correct-fix from first principles, log the result regardless

## Why this matters

Without history:
- Every run rediscovers the same fixes
- Operator gets the same "I tried X, didn't work, trying Y" loop every time
- No accumulation of project-specific knowledge

With history:
- Recurring patterns get faster (tried-and-true fix used first)
- New patterns get logged for future runs
- Negative knowledge (fixes that didn't work) is as valuable as positive

## Cross-project patterns

If a pattern recurs across MANY projects (e.g., "GHCR 403 from missing package-ACL"), consider promoting it from per-project history to:
- A note in the skill's documentation
- A `~/.claude/standards/` cross-reference
- A `feedback_*` memory entry (per Anouar's memory system)

## Application checklist

For any skill being audited for self-improvement:

- [ ] Define `.<skill>-history.json` schema in skill doc
- [ ] Add Stage 0.5 "read history" step
- [ ] Add final stage "append to history" step
- [ ] Reference `patterns_observed` in fix-loop logic
- [ ] Auto-gitignore the history file
- [ ] Document in skill: WHY history-driven > stateless

## File location

Per-project history files live at the repo root, gitignored. They never get committed. They survive across local sessions and Claude restarts because they're filesystem state.

If the operator clones the repo fresh, history starts empty. That's fine — the skill builds it up over its first few runs in the new clone.
