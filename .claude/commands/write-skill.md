---
description: "/write-skill - TDD for skill creation: pressure-test a scenario WITHOUT the skill (RED), write the skill (GREEN), close loopholes via rationalization tables (REFACTOR). Produces a new skill that inherits all shared standards."
allowed-tools: Bash(git *), Bash(mkdir *), Bash(date *), Bash(ls *), Bash(cat *), Read, Write, Edit, Glob, Grep, Agent
when_to_use: Trigger phrases: "build a new skill", "create custom skill"
---

# /write-skill - Meta-Skill for Creating Skills

**Steel Principle: No skill without a failing test first.**

This is a meta-skill: a skill for building new skills. It applies TDD methodology to skill creation. First, you pressure-test a scenario WITHOUT the skill and observe where Claude fails. Then you write the skill to close those failure modes. Then you pressure-test again to close any remaining loopholes.

**FIRE AND FORGET** - Describe what the skill should do. The skill guides you through RED → GREEN → REFACTOR.

> **When to use /write-skill:**
> - You notice a pattern you wish Claude did automatically
> - An existing skill has a loophole that keeps getting exploited
> - You want to enforce a new discipline across your work
> - You want to extract a personal workflow into a repeatable command
>
> **When NOT to use /write-skill:**
> - The skill already exists - just enhance it inline
> - It's a one-off script, not a repeatable pattern - just write the script
> - You're not sure what the skill should do yet - use `/brainstorm` first

---

## DISCIPLINE

> Reference: [Superpowers Discipline Protocol](~/.claude/standards/STEEL_DISCIPLINE.md)

Key enforcements for this skill:

- **Steel Principle #1:** NO skill is "done" without fresh pressure-testing evidence
- **Steel Principle #3:** RED-GREEN-REFACTOR - write the failing test first
- **Every skill inherits shared standards** - no reinventing SITREP, STATUS_UPDATES, CLEANUP, CONTEXT_MANAGEMENT, AGENT_ORCHESTRATION, STEEL_DISCIPLINE
- **Every skill follows the 5-phase pattern** - see `~/.claude/standards/SKILL_PATTERN.md`. Socratic Interview -> Research + Context -> Written Plan + HARD GATE -> Execute with live plan -> Iterative Verification -> SITREP. Session folders gitignored. Generic with placeholders. No project-specific references.

### Write-Skill Rationalization Table

| Rationalization | Reality | What to Do |
|----------------|---------|------------|
| "I know what agents will do wrong, skip the pressure test" | You know what agents usually do wrong. You don't know what THIS skill's agents will do wrong. | Run the pressure test. Observe the actual failures. |
| "The description says it all" | Descriptions are discovery hooks. The skill body is what enforces behavior. | Write the full skill. Don't leave it at description level. |
| "This skill is small, it doesn't need shared standards" | Small skills drift from project conventions, produce inconsistent output, confuse users | Every skill inherits shared standards. No exceptions. |
| "The rationalization table is overkill" | Rationalization tables are the #1 thing that prevents agents from skipping discipline | Include the table. Fill it with real excuses you've seen agents use. |

---

## STATUS UPDATES

> Reference: [Status Update Protocol](~/.claude/standards/STATUS_UPDATES.md)

```
🔨 /write-skill Started
   Skill name: [name]
   Purpose: [one-line purpose]

🧪 Phase 1: RED - Pressure Test (no skill exists)
   ├─ Scenario constructed
   ├─ Dispatching agent WITHOUT the skill
   └─ Failures observed: [count]

📝 Phase 2: GREEN - Write the Skill
   ├─ Description (CSO-optimized for discovery)
   ├─ Steel Principle(s)
   ├─ Rationalization table (from observed failures)
   ├─ Shared standards references
   └─ ✅ Draft skill written

🧪 Phase 3: REFACTOR - Pressure Test WITH the skill
   ├─ Same scenario, skill active
   ├─ Loopholes found: [count]
   └─ Skill hardened

📋 Phase 4: Router Integration
   ├─ Added intent mapping to SKILL_ROUTER.md
   ├─ Added ~/.claude/CLAUDE.md entry
   └─ ✅ Skill is globally discoverable

✅ Skill Ready
   File: ~/.claude/commands/[name].md
   First test: /[name] [example]
```

---

## OUTPUT STRUCTURE

```
.write-skill-reports/
├── WS-YYYYMMDD-HHMMSS.md          # Session report
├── state-YYYYMMDD-HHMMSS.json     # Resume state
├── red-phase/
│   ├── scenario.md                  # The pressure test scenario
│   ├── agent-output-no-skill.md    # What the agent did without the skill
│   └── failure-analysis.md         # Why it failed
└── refactor-phase/
    ├── agent-output-with-skill.md  # What it did with the skill
    └── remaining-loopholes.md       # What still leaked through
```

---

## PHASE 0: INTAKE

Parse the user's request:
- **Skill name:** Short, memorable (e.g., `/brainstorm`, `/investigate`)
- **Trigger:** When should it activate? What user intent should map to it?
- **Purpose:** What discipline does it enforce? What output does it produce?
- **Scope:** What's in, what's out?

### 0.1 Check for Duplicates

```bash
ls ~/.claude/commands/ | grep -i [keyword]
```

If a similar skill exists: propose enhancing it instead of creating new.

### 0.2 Create Infrastructure

```bash
mkdir -p .write-skill-reports/red-phase .write-skill-reports/refactor-phase
grep -q ".write-skill-reports" .gitignore 2>/dev/null || echo ".write-skill-reports/" >> .gitignore
```

---

## PHASE 1: RED - PRESSURE TEST WITHOUT THE SKILL

**The hypothesis:** Without this skill, Claude will fail in specific, predictable ways. We need to observe the actual failures before we write the skill - otherwise we're guessing at what to enforce.

### 1.1 Construct the Scenario

Design a scenario that would trigger the skill if it existed. Include:

- **The user's request:** Realistic, 1-2 sentences, the kind of thing the user would actually type
- **The context:** Files/state that exist in the scenario (describe, don't create)
- **The desired outcome:** What "good" looks like
- **The likely failure modes:** What you suspect will go wrong

Save to `.write-skill-reports/red-phase/scenario.md`.

### 1.2 Dispatch Fresh Agent (No Skill)

```
Task tool with model=sonnet:

You are a developer working on a project. A user has just sent you this message:

"[scenario user message]"

Context:
[scenario context]

Respond to the user. Do your best work. Handle the request to completion.

After you're done, write to .write-skill-reports/red-phase/agent-output-no-skill.md:
- What you did
- Why you made the choices you made
- Any assumptions
- How confident you are the result is correct
```

The fresh agent has no knowledge of this skill or our discipline standards. It will respond based on its default behavior.

### 1.3 Analyze the Failures

Read the agent's output. Compare against the desired outcome. Identify:

- **Discipline skipped:** Did it verify? Did it investigate before fixing? Did it write tests?
- **Rationalizations used:** What phrases did the agent use that signal skipped discipline?
- **Output issues:** Missing sections, wrong format, false completion claims?
- **Scope drift:** Did it do more/less than asked?

Document each failure in `.write-skill-reports/red-phase/failure-analysis.md`:

```markdown
## Failure 1: [Name]

**What happened:** [specific agent behavior]
**Why it's wrong:** [what the desired behavior was]
**Rationalization used (if any):** "[quoted phrase]"
**Fix in skill:** [what the skill needs to enforce]
```

**Minimum failures to observe:** 3. If fewer, the scenario isn't hard enough - construct a harder one.

---

## PHASE 2: GREEN - WRITE THE SKILL

Now write the skill to close the observed failure modes.

### 2.1 Skill File Template

```markdown
---
description: "/[name] - [CSO-optimized description: specific, triggers on user intent, ~15-25 words]"
allowed-tools: [specific tools only, not "all"]
---

# /[name] - [Short Title]

**Steel Principle: [The non-negotiable rule this skill enforces]**

[2-3 sentence intro: what problem does this solve, what does it produce]

**FIRE AND FORGET** - [How it runs]

> **When to use /[name]:**
> - [Signal 1]
> - [Signal 2]
>
> **When NOT to use /[name]:**
> - [Alternative skill for X]
> - [Alternative skill for Y]

---

## DISCIPLINE

> Reference: [Superpowers Discipline Protocol](~/.claude/standards/STEEL_DISCIPLINE.md)

Key enforcements for this skill:
- [Steel Principle most relevant]
- [Skill-specific discipline]

### [Skill]-Specific Rationalization Table

| Rationalization | Reality | What to Do |
|----------------|---------|------------|
| [From RED phase observation] | [Why it's wrong] | [What to do instead] |
| [From RED phase observation] | [Why it's wrong] | [What to do instead] |
| [From RED phase observation] | [Why it's wrong] | [What to do instead] |

---

## STATUS UPDATES

> Reference: [Status Update Protocol](~/.claude/standards/STATUS_UPDATES.md)

[Skill-specific status flow with emojis]

---

## [CONTEXT MANAGEMENT, AGENT ORCHESTRATION sections if skill spawns sub-agents]

---

## OUTPUT STRUCTURE

```
.[skill]-reports/
├── [SKILL]-YYYYMMDD-HHMMSS.md
├── state-YYYYMMDD-HHMMSS.json
└── [other artifacts]
```

---

## PHASE 0: INTAKE

[What the skill parses from user input, initial setup]

---

## PHASE 1+: [Domain-specific phases]

[The actual work the skill does]

---

## CLEANUP PROTOCOL

> Reference: [Resource Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md)

### [Skill]-Specific Cleanup

1. [Specific cleanup action]
2. [Specific cleanup action]

---

## SITREP

> Reference: [SITREP Standard](~/.claude/standards/SITREP_FORMAT.md)

[Skill-specific SITREP with required fields]

---

## REMEMBER

- [Key rule 1]
- [Key rule 2]
- [Key rule 3]

<!-- Created with /write-skill on YYYY-MM-DD -->
```

### 2.2 Description (CSO) Optimization

The description is the MOST IMPORTANT part for discovery. Rules:

| Rule | Example |
|------|---------|
| Start with skill command | "/investigate - ..." |
| Specific, not generic | "Systematic root-cause debugging" not "Helps with bugs" |
| Include trigger keywords | "investigate", "debug", "not working" |
| Mention the discipline | "evidence-first", "regression test mandatory" |
| 15-25 words | Long enough to be specific, short enough to scan |

**Bad description:**
> "Helps you find and fix bugs"

**Good description:**
> "/investigate - Systematic Root-Cause Debugging: evidence-first investigation, hypothesis testing, minimal fix, regression test"

### 2.3 Write the Skill

Use the template. Fill every section. DO NOT:
- Leave placeholders like "[TBD]" or "similar to /other-skill"
- Skip the rationalization table (it's the most important section)
- Forget to reference the 5 shared standards (SITREP, STATUS, CLEANUP, CONTEXT, ORCHESTRATION, DISCIPLINE)

Save to `~/.claude/commands/[name].md`.

---

## PHASE 3: REFACTOR - PRESSURE TEST WITH THE SKILL

Now test whether the skill actually works.

### 3.1 Dispatch Fresh Agent (WITH the skill)

```
Task tool with model=sonnet:

You are a developer. The user has sent this message:

"[same scenario from RED phase]"

Before responding, load this skill:
[full contents of the new skill file]

Now respond to the user following the skill's discipline.

After you're done, write to .write-skill-reports/refactor-phase/agent-output-with-skill.md:
- What you did
- Which sections of the skill you followed
- Any rationalizations you considered and rejected
- Any parts of the skill you were tempted to skip (but didn't)
```

### 3.2 Analyze Remaining Loopholes

Compare this agent's output to the RED phase output. What's better? What's still not ideal?

For any remaining issues, trace them back to the skill:

- **Missing guidance:** Add a new section
- **Insufficient rationalization defense:** Add to the rationalization table
- **Ambiguous instruction:** Rewrite for specificity
- **Discipline still skipped:** Add a HARD-GATE or stronger Steel Principle

Update the skill file. Re-run Phase 3 with the updated skill. Iterate until agent reliably follows the discipline.

**Stopping criterion:** 3 consecutive pressure tests with no new loopholes found.

---

## PHASE 4: ROUTER INTEGRATION

For the skill to be discoverable, it must be in the routing system.

### 4.1 Add to SKILL_ROUTER.md

Edit `~/.claude/standards/SKILL_ROUTER.md`:

```markdown
| "[trigger phrase 1]", "[trigger phrase 2]" | `/[name]` | [confidence] | [Auto/Suggest] |
```

Add to the appropriate category section (Planning, Debugging, Testing, Security, etc.).

### 4.2 Regenerate the router (do NOT edit ~/.claude/CLAUDE.md)

The router is generated from each skill's frontmatter, so the trigger phrases belong in the new
skill's `description` and `when_to_use`. Then run:

```bash
python3 ~/.claude/generate-skill-router.py && ~/.claude/check-skill-router.sh
```

### 4.3 Verify Discoverability

Test the router:

```
Task tool with model=sonnet:

You are Claude Code. Read ~/.claude/CLAUDE.md for the skill routing rules.

A user just sent: "[trigger phrase for the new skill]"

What would you do? Which skill would you invoke/suggest?
```

The agent should identify the new skill. If not: the description/routing entry needs better keywords.

**Then register it mechanically, because discoverability by agent judgement is not registration:**

```bash
~/.claude/check-skill-router.sh --fix   # regenerate from frontmatter
~/.claude/check-skill-router.sh         # must exit 0
```

The guard fails both when the router content has drifted and when the skill COUNT on disk does not
match the count named in the router, so a new skill cannot pass it without being registered. It
compares content only and ignores the generator's timestamp, so it does not cry wolf on every run.

---

## PHASE 5: FINAL VERIFICATION

Before marking the skill complete:

- [ ] Skill file exists at `~/.claude/commands/[name].md`
- [ ] Description is CSO-optimized
- [ ] Steel Principle(s) are stated explicitly
- [ ] Rationalization table includes at least 3 real rationalizations from RED phase
- [ ] All 6 shared standards are referenced (DISCIPLINE, STATUS, CONTEXT, ORCHESTRATION, CLEANUP, SITREP)
- [ ] Output structure is defined
- [ ] Phases are specific (no placeholder steps)
- [ ] CLEANUP protocol is specified
- [ ] SITREP format follows the standard
- [ ] **`~/.claude/check-skill-router.sh` exits 0.** This is the registration step and it is NOT
      optional. Do NOT hand-edit `SKILL_ROUTER.md`: it is GENERATED from skill frontmatter by
      `generate-skill-router.py`, so a hand-added entry is discarded by the next regeneration and
      a hand-maintained router measurably rots (31 skills named against an estate of 40, 6 routed
      that did not exist, 15 live skills it had never heard of). Run
      `~/.claude/check-skill-router.sh --fix`, then commit the regenerated router with the skill.
- [ ] 3 consecutive pressure tests pass without new loopholes
- [ ] Skill appears in the global skills list (globally available via `~/.claude/commands/`)

---

## CLEANUP PROTOCOL

> Reference: [Resource Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md)

### Write-Skill-Specific Cleanup

1. **Keep the skill file** - it's the whole point of the run
2. **Keep RED/REFACTOR phase outputs** - audit trail for future skill maintenance
3. **State file** - auto-clean after 7 days of completion
4. **No servers/browsers opened** - nothing to close

---

## SITREP

> Reference: [SITREP Standard](~/.claude/standards/SITREP_FORMAT.md)

```markdown
## SITREP - /write-skill

**New Skill:** /[name]
**Duration:** [X minutes]
**Status:** DEPLOYED / IN_PROGRESS / ABANDONED

### Pressure Test Results

| Phase | Failures Observed | Notes |
|-------|-------------------|-------|
| RED (no skill) | [count] | [1-line summary] |
| REFACTOR (with skill) | [count] | [1-line summary] |
| Final iteration | 0 | Skill locked |

### Skill Attributes
- File: `~/.claude/commands/[name].md`
- Lines: [count]
- Rationalizations defended: [count]
- Shared standards referenced: [6/6]
- Sub-agents dispatched in skill: [yes/no + which]

### Router Integration
- `SKILL_ROUTER.md`: entry added under [category]
- `~/.claude/CLAUDE.md`: entry added under [Auto-Invoke/Suggest]
- Discoverability verified: PASS

### Handoff
- First real-world test: try `/[name] [example prompt]`
- Monitor: If agent rationalizes past discipline, add to table and iterate
```

---

## RELATED SKILLS

**Feeds from:**
- `/brainstorm` - new skill ideas emerge from brainstorm sessions; write-skill structures them into executable skills
- `/mdmp` - MDMP may identify a workflow gap that needs a new skill to fill it

**Feeds into:**
- `/gh-ship` - new skill file is committed and shipped via gh-ship
- All skills - every skill created by write-skill inherits shared standards (SITREP, CLEANUP, STATUS)

**Pairs with:**
- `/brainstorm` - brainstorm defines WHAT the skill should do; write-skill defines HOW it enforces it
- `/smoketest` - after a new skill is written, smoketest verifies the project is still healthy

**Auto-suggest after completion:**
- `/gh-ship` - "New skill written. Commit and register it? Run /gh-ship."

---

## REMEMBER

- **RED before GREEN** - observe failure before writing solution
- **Rationalization table is the core** - this is what makes skills actually enforce discipline
- **Every skill inherits shared standards** - don't reinvent SITREP, STATUS, CLEANUP, etc.
- **CSO-optimized description** - this is what makes the skill discoverable
- **Iterate until loopholes close** - a skill that's "mostly right" will be exploited
- **Route integration matters** - a skill users can't find is a skill users don't use

<!-- Claude Code Skill - Superpowers methodology adapted for Steel Motion skill architecture -->
<!-- Incorporates writing-skills methodology from obra/superpowers (MIT License) -->
