# /brainstorm - gate, handoff, status, SITREP

## Phase 5: HARD-GATE

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

## Phase 6: handoff

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

## Status lines

```
🧠 /brainstorm Started
   Topic: "[user's topic]"

📋 Phase 1: Context Exploration
   ├─ Reading existing code in affected area
   ├─ Checking docs/ and recent commits for prior discussions
   └─ ✅ Context gathered

💡 Phase 2: Rounds
   ├─ Round 1: [n] questions → [answers, one line]
   ├─ Round 2: [n] questions → [answers, one line]
   └─ ✅ Frontier empty, summary confirmed

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

## Output

```
.reports/brainstorm/
└── BRAIN-YYYYMMDD-HHMMSS.md      # Brainstorm session report
docs/brainstorm/specs/
└── YYYY-MM-DD-[topic]-design.md  # The approved spec (committed to repo)
```

The report lives in `.reports/brainstorm/` (gitignored; add it to `.gitignore` when the first report is written). The spec lives in `docs/brainstorm/specs/` and is committed - it's the permanent record.

## CLEANUP PROTOCOL

> Reference: [Resource Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md)

### Brainstorm-Specific Cleanup

1. **Preserve the spec** - it stays where Phase 4 wrote it (committed to repo)
2. **No test data created** - nothing to delete
3. **No servers/browsers opened** - nothing to close; stop any lookup sub-agent once its report is used

---

## SITREP

> Reference: [SITREP Standard](~/.claude/standards/SITREP_FORMAT.md)

```markdown
## SITREP - /brainstorm

**Topic:** [user's topic]
**Duration:** [X minutes, R rounds, Y questions asked]
**Approaches explored:** [count]
**Selected approach:** [name]
**Status:** INTERVIEWING / AWAITING_APPROVAL / SPEC_APPROVED / ABANDONED

### What Was Produced
- Spec: `docs/brainstorm/specs/YYYY-MM-DD-[topic]-design.md`
- Length: [X] sections, [Y] tasks implied

### Decisions Settled
1. [question] → [answer, 1 line] (round N)
2. [question] → [answer, 1 line] (round N)

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
- `/docs` - record the design decision where the repo keeps decision records (`standards/DOMAIN_LANGUAGE.md`; no records kept: do not start them)

**Auto-suggest after completion:**
When this skill finishes with an approved spec, suggest: `/subagent-dev [spec path]` to execute the plan with automated two-stage review

