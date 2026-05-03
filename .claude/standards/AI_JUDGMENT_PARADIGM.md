# AI-Judgment Paradigm

**Reference standard for all skills.** Use AI judgment over pattern-matching tables.

## Core principle

A skill is **a planning document for Claude to execute**, not a bash script Claude runs verbatim.

When the skill encounters errors, missing tools, unexpected situations:
- **DO NOT** grep error logs for keywords and look up a fix in a table
- **DO** read the actual situation, reason about what's wrong, decide on the fix

## Why this matters

Real-world failures don't fit fixed tables. Examples observed in production:
- "ruff E401 (Multiple imports on one line)" — won't match `if grep "linter"`
- "GHCR 403 due to package's Manage-Actions-Access list" — not in any standard fix table
- "apr- id collision under same-millisecond POSTs" — looks like a flaky test, IS a real bug

Pattern-match skills miss these. AI-judgment skills handle them by reading + reasoning.

## What this looks like in practice

### Anti-pattern (DO NOT use)

```
| Error string | Fix |
|---|---|
| "eslint" | Run linter |
| "prettier" | Run formatter |
| "tsc" | Read error, fix type |
```

This works for 80% of cases. The 20% is where bugs live.

### Pattern (DO use)

```
## Fix strategy hints

When CI fails:
1. Read the actual log
2. Identify what's failing (linter complaint? type error? assertion failure? network 5xx?)
3. Match by MEANING, not by string. "Linter complaint" maps to "run formatter" regardless of which linter (biome, eslint, ruff, golangci-lint).
4. If the failure doesn't match any known shape, reason from first principles. Try the smallest correct fix. Document in `.X-history.json` so future runs recognize it.

The strategy hints below are starting points, not rules:
- Linter: run project's linter --fix
- Type error: read error, inspect file:line, propose smallest correct change. NEVER suppress.
- ...
```

## Detection over assumption

Skills must ADAPT to whatever repo type they find. Don't assume:
- Language (Node? Python? Rust? Go? Bash?) — detect from `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `bats` files
- Test runner — read package.json scripts; fall back to canonical commands
- Linter / formatter — same
- Deploy mechanism (Vercel? Netlify? self-hosted? none?) — detect from config files

## Reasoning over rules

When in doubt:
- State the hypothesis (what you think is wrong)
- Try the smallest correct fix
- Verify (re-run the failing thing)
- Log the outcome (success or failure) for future runs to learn from

## Application checklist

For any skill being audited:

- [ ] Replace fix-tables with strategy-hints sections
- [ ] Mark all bash blocks "examples, not patterns to match"
- [ ] Add "Detect, don't assume" section in Stage 0
- [ ] Note in CRITICAL RULES: "READ + REASON, don't grep"
- [ ] Add to DESIGN DECISIONS: WHY AI-judgment over regex
