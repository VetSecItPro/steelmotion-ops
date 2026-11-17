# /brainstorm - approaches and the spec

## Phase 3: approaches

Present 2-3 distinct approaches. Not 2-3 variants of the same approach: genuinely different paths.

### Approach Format

```
═══════════════════════════════════════════════════════════════
APPROACH [LETTER]: [Short Name]
═══════════════════════════════════════════════════════════════

**Core idea:** [One sentence]

**How it works:**
- [Step or component 1]
- [Step or component 2]
- [Step or component 3]

**Pros:**
- [Specific advantage 1]
- [Specific advantage 2]

**Cons:**
- [Specific tradeoff 1]
- [Specific tradeoff 2]

**Best for:** [When this approach wins]
**Effort:** [Low / Medium / High - relative to other approaches]
**Risk:** [Specific risk or "Low"]
```

### Recommendation

After presenting approaches, recommend ONE:

```
**Recommendation:** Approach [X]

**Why:** [2-3 sentences tying recommendation to what the user said they cared about]

**When to pick a different one:**
- Pick A if [condition]
- Pick B if [condition]
```

### User Decision Point

Wait for the user to pick. DON'T proceed to spec writing until they confirm.

If they want to modify an approach (hybrid), capture the modification and proceed.


## Phase 4: the spec

Once the approach is picked, write the spec where the repo already keeps specs or plans (for
example `docs/plans/`); only if it has none, `docs/brainstorm/specs/YYYY-MM-DD-<topic>-design.md`. Use `GLOSSARY.md` terms throughout.

### Spec Template

```markdown
# Design Spec: [Topic Name]

**Date:** YYYY-MM-DD
**Approach:** [Letter and Name]
**Status:** APPROVED / DRAFT / REVISION_NEEDED

---

## Problem

[What problem does this solve? Why now?]

## Goal

[What does success look like? Measurable if possible.]

## Non-Goals

[What this explicitly is NOT trying to solve. Prevents scope creep.]

## Approach

[The approved approach in detail - 2-4 paragraphs]

## Architecture

### Components to Create

| Component | Path | Purpose |
|-----------|------|---------|
| [Name] | `src/.../` | [One-line purpose] |

### Components to Modify

| File | What Changes | Why |
|------|------------|-----|
| `src/.../file.ts` | [Specific change] | [Reason] |

### Data Model

```typescript
// Types/schemas involved
interface [Name] {
  [field]: [type]; // [purpose]
}
```

### API (if applicable)

| Endpoint | Method | Input | Output |
|----------|--------|-------|--------|
| `/api/...` | GET | [schema] | [schema] |

## User Flow

1. User does [action]
2. System responds with [behavior]
3. [Continue step by step]

## Edge Cases

| Case | Behavior |
|------|----------|
| [Tricky scenario 1] | [What happens] |
| [Tricky scenario 2] | [What happens] |

## Constraints

- [Constraint 1 - e.g., "Must work without JS for form submission"]
- [Constraint 2 - e.g., "No new dependencies"]

## Testing Strategy

- Unit tests for [specific modules]
- Integration tests for [specific flows]
- E2E test for [critical path]

## Rollout

- [How to ship safely - feature flag? Phased? All at once?]

## Out of Scope (Revisit Later)

- [Feature/concern deliberately excluded and why]

## Open Questions

[Only if genuinely unresolved. Empty is ideal.]

---

## Implementation Handoff

Ready for `/subagent-dev [path to this spec]` to execute.
```

### Self-Review (before presenting)

Before showing the spec to the user, check:

1. **Placeholder scan:** Grep the spec for "TBD", "TODO", "...", "similar to", "etc." - if any exist, fill them in
2. **Internal consistency:** Are the Architecture, User Flow, and Edge Cases consistent?
3. **Completeness:** Could a developer build this from the spec alone without asking questions?
4. **Scope check:** Does every section trace back to the approved approach? No scope creep.

### Present to User

```
📝 Spec written: docs/brainstorm/specs/YYYY-MM-DD-[topic]-design.md

Quick read:
- Problem: [one line]
- Approach: [one line]
- Scope: [count] components, [count] files modified

**Review the full spec.** When approved, we're ready for /subagent-dev.

Want changes? Describe what to adjust.
```
