# Skill Audit Rubric

Apply this rubric to every skill in `~/.claude/commands/*.md` to identify rewrite opportunities. Same lessons that drove `/gh-ship` rewrite (2026-05-03) generalize here.

## When to apply

- Before rewriting a skill: score it against this rubric to identify which dimensions to fix
- After rewriting: score it again to confirm improvements
- Periodically (quarterly): score the whole collection to spot drift

## Rubric: 10 dimensions, 0-3 each (max 30)

For each skill, score 0 (absent), 1 (partial), 2 (mostly there), 3 (well-done). Total ≥ 24 means well-architected; ≤ 12 means rewrite candidate.

### 1. AI-judgment over pattern-match (3)

**Question:** When the skill encounters errors or unexpected situations, does it READ + REASON, or grep for keywords?

- 0: long regex tables of "if X then Y"
- 3: bash blocks are illustrative; the actual decision is "Claude reads the situation and chooses"

### 2. Tool-agnostic detection (3)

**Question:** Does the skill assume specific tools (jest, Vercel, npm) or detect what's actually present?

- 0: hardcoded assumptions (e.g., "always run npm test")
- 3: filesystem-based detection (`package.json` → Node; `pyproject.toml` → Python; etc.) with graceful fallback when nothing matches

### 3. Multi-repo / multi-target awareness (3)

**Question:** When invoked from a workspace with siblings, does the skill scan + report on them?

- 0: operates on cwd only with no acknowledgment of the rest
- 3: Stage 0.5-style scan, sibling state in SITREP, but doesn't cross-traverse without operator opt-in

### 4. Verify before destroy (3)

**Question:** Are destructive actions (delete, force-push, drop, etc.) preceded by content-verification, not just metadata?

- 0: trusts API state alone (e.g., "PR shows merged → delete branch")
- 3: content-grep, ancestry triangulation, AND session-ownership tracking

### 5. WIP protection (3)

**Question:** Does the skill protect operator work-in-progress that wasn't created in this run?

- 0: blanket "auto-cleanup" can destroy pre-existing WIP
- 3: only auto-acts on what THIS run created; pre-existing is reported but inspected-only

### 6. Self-healing recovery (3)

**Question:** When the skill makes a mistake, can it recover in-session?

- 0: failure means manual intervention required
- 3: every destructive action has a documented recovery path (reflog for deletes, force-push-with-lease for rebases, etc.)

### 7. Self-improvement log (3)

**Question:** Does the skill learn from its own past runs?

- 0: every run starts from scratch
- 3: appends to `.X-history.json` with patterns observed; future runs read it to prefer known-good fixes

### 8. Proactive audit (3)

**Question:** Does the skill find issues NOT explicitly listed in its spec?

- 0: only checks the documented checklist
- 3: dedicated audit stage that scans for known anti-patterns AND surfaces unknowns

### 9. Honest scope (3)

**Question:** Does the skill refuse work outside its competence?

- 0: tries to do everything; produces low-quality output for things outside core
- 3: knows when to delegate to a sibling skill OR surface to operator vs. forging ahead

### 10. Documentation discipline (3)

**Question:** Does the skill explain WHY of each major design decision?

- 0: no rationale; reader has to reverse-engineer intent
- 3: dedicated "DESIGN DECISIONS" section + WHY comments inline at every non-obvious choice

## Scoring template

```
Skill: /<name>
Date: <YYYY-MM-DD>

| Dim | Score | Notes |
|---|---|---|
| 1. AI-judgment | _ | |
| 2. Tool-agnostic | _ | |
| 3. Multi-target | _ | |
| 4. Verify-destroy | _ | |
| 5. WIP protection | _ | |
| 6. Self-healing | _ | |
| 7. Self-improvement | _ | |
| 8. Proactive audit | _ | |
| 9. Honest scope | _ | |
| 10. Doc discipline | _ | |
| **Total** | _/30 | |

Rewrite priority: [HIGH (≤12) / MEDIUM (13-23) / LOW (≥24)]
```

## Common anti-patterns to watch for

Beyond the dimensional scores, flag any of these:

- **Vercel-tunnel-vision**: assumes deploys go through Vercel even if the project doesn't use it
- **Node-bias**: assumes `npm` or `package.json` even for non-Node projects
- **Pattern-match cascades**: `if grep "eslint" → fix-eslint` chains that miss real-world variants (ruff, golangci-lint)
- **Missing rollback**: destructive ops with no documented reversal
- **Verbose bash boilerplate**: repeated `if [ -f X ]; then ...; fi` blocks that should be one detection stage
- **Hardcoded URLs / hosts**: any reference to `https://app.aicommandpost.com` etc. that should be operator-config
- **Silent overrides**: skill takes destructive action without surfacing what it did

## Application sequence

1. Read the skill's `~/.claude/commands/<name>.md` end-to-end
2. Score on each dimension; capture in `<name>-audit.md` in `_plans/`
3. If total ≤ 12: rewrite from scratch using the gh-ship.md template structure
4. If total 13-23: targeted patches per low-scoring dimensions
5. If total ≥ 24: skip rewrite; note for future re-audit
