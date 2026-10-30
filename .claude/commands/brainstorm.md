---
description: "/brainstorm - Socratic design exploration: one question at a time, 2-3 approaches with tradeoffs, HARD-GATE before implementation, writes approved spec"
when_to_use: 'Trigger phrases: "help me think through", "explore approaches", "what are the options", "design this with me", "I am not sure how to build this". Use BEFORE implementation, when the shape of the solution is still open. Hard-gates on an approved spec.'
allowed-tools: Bash(git *), Bash(mkdir *), Bash(date *), Bash(ls *), Read, Write, Edit, Glob, Grep, WebSearch, Agent
---

# /brainstorm - Socratic Design Exploration

**Steel Principle: NO implementation code until the design is user-approved and the spec is written.**

This skill turns vague ideas into validated, implementable designs BEFORE a single line of code is written. It's lighter than `/mdmp` (no military-style 6-lens analysis) but still enforces the discipline that separates "threw something together" from "designed something properly."

**FIRE AND FORGET** - Describe the idea. The skill asks one question at a time, explores 2-3 approaches, and produces an approved spec ready for `/subagent-dev`.

> **When to use /brainstorm:**
> - "I'm thinking about adding X"
> - "Should we refactor Y?"
> - "I have an idea..."
> - "What if we tried Z?"
> - Exploring a feature that isn't fully formed yet
>
> **When to use /mdmp instead:**
> - Multi-lens analysis needed (security, DevOps, product, QA all matter)
> - Architectural change with organizational impact
> - Multiple stakeholders' concerns must be weighed
>
> **When NOT to use /brainstorm:**
> - Bug fix → `/investigate`
> - Already-designed feature → `/subagent-dev`
> - Quick change you already know the answer to → just do it

---

## DISCIPLINE

> Reference: [Superpowers Discipline Protocol](~/.claude/standards/STEEL_DISCIPLINE.md)

Key enforcements for this skill:

- **Steel Principle #4:** NO implementation before approved design (the HARD-GATE)
- **Steel Principle #5:** NO placeholders in the final spec (specific, actionable, complete)
- **One question at a time** - no bundled questions, no overwhelming the user
- **Explore, don't dictate** - present 2-3 approaches with tradeoffs, let user decide

### Brainstorm-Specific Rationalization Table

| Rationalization | Reality | What to Do |
|----------------|---------|------------|
| "This is simple, we can skip the spec" | Simple ideas with wrong assumptions build the wrong thing faster | Write the spec. Even 10 lines of spec beats 100 lines of wrong code. |
| "I already know what the user wants" | You know what they said. You don't know what they MEANT. | Ask the clarifying question. |
| "Let's just start coding and iterate" | You'll iterate, but on the wrong foundation | The foundation is the spec. Get it right first. |
| "The user is impatient, skip questions" | Impatience leads to rework. Rework is slower than asking. | One focused question, then proceed. |
| "I can infer the edge cases" | You can infer SOME edge cases. Users know edge cases you can't see. | Ask about the tricky ones. |

---

## STATUS UPDATES

> Reference: [Status Update Protocol](~/.claude/standards/STATUS_UPDATES.md)

```
🧠 /brainstorm Started
   Topic: "[user's topic]"

📋 Phase 1: Context Exploration
   ├─ Reading existing code in affected area
   ├─ Checking docs/ and recent commits for prior discussions
   └─ ✅ Context gathered

💡 Phase 2: Clarifying Questions (one at a time)
   ├─ Q1: [question] → [answer]
   ├─ Q2: [question] → [answer]
   └─ ✅ Core requirements clear

🎯 Phase 3: Approach Exploration
   ├─ Approach A: [name] - [one-line description]
   ├─ Approach B: [name] - [one-line description]
   ├─ Approach C: [name] - [one-line description]
   └─ Recommendation: [A/B/C] because [reason]

📝 Phase 4: Spec Writing
   ├─ Writing design doc → docs/brainstorm/specs/YYYY-MM-DD-[topic].md
   ├─ Self-review: placeholder scan, internal consistency
   └─ ✅ Spec ready for user approval

🚧 HARD-GATE: User must approve spec before implementation
   Next step (after approval): /subagent-dev [path to spec]
```

---

## OUTPUT STRUCTURE

```
.brainstorm-reports/
├── BRAIN-YYYYMMDD-HHMMSS.md      # Brainstorm session report
├── state-YYYYMMDD-HHMMSS.json    # State (for resume)
docs/brainstorm/specs/
└── YYYY-MM-DD-[topic]-design.md  # The approved spec (committed to repo)
```

The report lives in `.brainstorm-reports/` (gitignored). The spec lives in `docs/brainstorm/specs/` and is committed - it's the permanent record.

---

## PHASE 0: INTAKE

Parse the user's request:
- **Topic:** What are they thinking about?
- **Signal strength:** Clear goal, rough idea, or just exploring?
- **Affected area:** Which part of the codebase? (may need to ask)

### 0.1 Create Infrastructure

```bash
mkdir -p .brainstorm-reports docs/brainstorm/specs
grep -q ".brainstorm-reports" .gitignore 2>/dev/null || echo ".brainstorm-reports/" >> .gitignore
```

### 0.2 Announce

```
I'm using /brainstorm to explore this properly before we write code.
I'll ask one focused question at a time, then present 2-3 approaches.
No code until you approve the spec.
```

---

## PHASE 1: CONTEXT EXPLORATION

**Before asking the user anything, explore the codebase.** This is silent prep - don't bombard the user with questions you could answer yourself.

### 1.1 Read What Exists

- Relevant directories (`src/components/`, `src/app/api/`, wherever the topic lives)
- Recent commits in the affected area (`git log --oneline -10 -- [paths]`)
- CLAUDE.md for any project-specific rules
- Package.json for framework, dependencies
- Any existing specs in `docs/brainstorm/specs/`

### 1.2 Identify Unknowns

Write a private list of what you DON'T know yet:
- Exact user needs (what "good" looks like from their perspective)
- Constraints (budget, timeline, existing contracts)
- Hidden requirements (mobile? offline? real-time?)
- Integration points (other systems, other features)

The next phase asks about these.

---

## PHASE 2: CLARIFYING QUESTIONS

**Ask ONE question at a time.** Never bundle. Never present 5 questions at once.

### Question Priority Order

1. **Goal question first:** What problem does this solve? What does success look like?
2. **Scope question:** MVP vs. full? What's the minimum viable version?
3. **User question:** Who will use this? How often? What's their context?
4. **Constraint questions:** Deadline? Budget? Existing patterns to follow?
5. **Edge case questions:** What about [specific tricky scenario]?
6. **Integration questions:** How does this interact with [other feature]?

### Question Format

**Multiple choice preferred** when the options are bounded:
```
What should happen when a user deletes their account?

A) Hard delete - remove all data immediately
B) Soft delete - flag as deleted, purge after 30 days
C) Anonymize - keep data but remove PII

(If something else, describe it.)
```

**Open-ended** when options aren't known:
```
Walk me through a typical use case. Who does what, in what order?
```

### Stopping Rule

Stop asking questions when:
- You have enough to propose 2-3 distinct approaches
- Further questions would be about implementation details (save those for the spec)
- The user seems impatient or says "just propose something"

**Maximum 5 clarifying questions** before moving to Phase 3. If you need more, you're exploring something too big for `/brainstorm` - suggest escalating to `/mdmp`.

---

## PHASE 3: APPROACH EXPLORATION

Present 2-3 distinct approaches. Not 2-3 variants of the same approach - genuinely different paths.

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

---

## PHASE 4: SPEC WRITING

Once the approach is approved, write the spec.

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

---

## PHASE 5: HARD-GATE (USER APPROVAL)

**ABSOLUTE RULE:** No implementation code until the user explicitly approves the spec.

```
🚧 HARD-GATE: Waiting for spec approval

Options:
- "Approve" / "Looks good" / "Let's build it" → Proceed to /subagent-dev
- "Change X" → Revise spec, re-present
- "Need more exploration on Y" → Return to Phase 2/3 for that aspect
```

DO NOT:
- Start writing implementation code
- Propose implementation "just to be helpful"
- Bypass the gate for "simple" specs

DO:
- Wait patiently for approval
- Accept revisions gracefully
- Iterate on the spec as needed

---

## PHASE 6: HANDOFF

Once approved:

```
✅ Spec approved.

Handoff options:
1. /subagent-dev docs/brainstorm/specs/YYYY-MM-DD-[topic]-design.md
   → Automated execution with two-stage review per task

2. I can execute inline (I'll follow the spec step by step)
   → Best for small specs, < 5 tasks

3. You want to build it yourself
   → Spec is ready, happy building

Which do you prefer?
```

---

## CLEANUP PROTOCOL

> Reference: [Resource Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md)

### Brainstorm-Specific Cleanup

1. **Preserve the spec** - `docs/brainstorm/specs/*` stays (committed to repo)
2. **State file** - keep for 24h in case user wants to resume, then auto-clean
3. **No test data created** - nothing to delete
4. **No servers/browsers opened** - nothing to close

---

## SITREP

> Reference: [SITREP Standard](~/.claude/standards/SITREP_FORMAT.md)

```markdown
## SITREP - /brainstorm

**Topic:** [user's topic]
**Duration:** [X minutes, Y questions asked]
**Approaches explored:** [count]
**Selected approach:** [name]
**Status:** SPEC_APPROVED / AWAITING_APPROVAL / ABANDONED

### What Was Produced
- Spec: `docs/brainstorm/specs/YYYY-MM-DD-[topic]-design.md`
- Length: [X] sections, [Y] tasks implied

### Clarifying Questions Asked
1. [question] → [answer, 1 line]
2. [question] → [answer, 1 line]

### Approaches Considered
| Letter | Name | Verdict |
|--------|------|---------|
| A | [name] | [chosen/rejected because X] |
| B | [name] | [chosen/rejected because X] |

### Next Steps
- `/subagent-dev [spec path]` to implement with automated review
```

---

## RELATED SKILLS

**Feeds from:**
- (none - /brainstorm is typically the starting point for new ideas)

**Feeds into:**
- `/subagent-dev` - the approved spec from Phase 5 is the direct input; handoff is explicit at Phase 6
- `/mdmp` - if the scope grows beyond brainstorm capacity (multi-team, architectural), escalate here
- `/write-skill` - if the brainstorm subject is a new skill to create, hand off the spec there

**Pairs with:**
- `/design` - pair brainstorm output with a design pass when the feature has significant UI impact
- `/docs` - write ADR entries to capture the design decision after spec is approved

**Auto-suggest after completion:**
When this skill finishes with an approved spec, suggest: `/subagent-dev [spec path]` to execute the plan with automated two-stage review

---

## REMEMBER

- **One question at a time** - never bundle
- **Explore before deciding** - 2-3 genuine alternatives, not variants
- **HARD-GATE is absolute** - no code before approval, no exceptions
- **No placeholders in the spec** - specific, actionable, complete
- **The spec is the contract** - between planning and execution
- **Escalate to /mdmp** if the topic grows beyond brainstorm scope (architectural, multi-team, multi-concern)

<!-- Claude Code Skill - Superpowers methodology adapted for Steel Motion skill architecture -->
<!-- Incorporates brainstorming discipline from obra/superpowers (MIT License) -->
