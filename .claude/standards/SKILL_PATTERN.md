# Skill Pattern Standard

**Version:** 2.0
**Applies to:** Both skill locations. Measured 2026-08-27: `~/.claude/commands/` holds 18 live
`.md` command files and `~/.claude/skills/` holds 22 skill directories, **fully disjoint - no
skill exists in both.** This is a half-finished migration, not a duplication. Treat the two as
one estate of 40 until they are consolidated.
**Companion to:** [SITREP Format](./SITREP_FORMAT.md), [Cleanup Protocol](./CLEANUP_PROTOCOL.md), [Status Updates](./STATUS_UPDATES.md)

---

## Core Philosophy

**Skills are NOT cookie-cutter. Each skill is tailored to its specific use case.**

A skill that plans a 90-day marketing campaign has different needs than a skill that runs a quick smoke test. A skill that designs premium websites has different needs than a skill that deploys code.

What every skill MUST have is:
1. **Research-backed depth** - integrate actual best practices from practitioners in the skill's domain
2. **Comprehensive coverage** - be the most thorough treatment of its use case
3. **Shared standards** - inherit SITREP, CLEANUP, CONTEXT_MANAGEMENT, STATUS_UPDATES
4. **Generic** - no project/company-specific references, use placeholders
5. **Globally available** - lives in `~/.claude/commands/`, same folder as all other skills
6. **Composable** - documents how it feeds from/into other skills

What each skill PICKS based on its domain:
- Its own execution pattern (phases, gates, loops, whatever fits)
- Its own input mechanism (Socratic, flags, auto-detection)
- Its own output format (documents, code, configurations, reports)
- Its own approval model (hard gate, opt-in, autonomous)

---

## Optional Patterns (Use What Fits)

Skills may adopt ANY of these patterns based on their use case:

### Pattern A: Socratic + Plan + Gate + Verify + SITREP
**Best for:** Creative/planning skills where direction matters more than execution speed. Marketing, design, brainstorming, content.
- Phase 0: 3-5 open-ended questions
- Phase 1: Research + context load
- Phase 2: Written plan + hard gate approval
- Phase 3: Execute with live plan updates
- Phase 4: Iterative verification
- Phase 5: SITREP
**Examples:** `/design`

### Pattern B: TDD (RED-GREEN-REFACTOR)
**Best for:** Meta-skills, skill creation, new code features. Ensures evidence-based output.
- RED: Define failing state
- GREEN: Implement minimum to pass
- REFACTOR: Close loopholes
**Examples:** `/write-skill`

### Pattern C: MDMP (Military Decision-Making Process)
**Best for:** Strategic analysis requiring multi-lens examination. Major architecture, big decisions.
- Mission receipt -> Mission analysis (6 lenses) -> COA development -> Decision -> Execution -> SITREP
**Examples:** `/mdmp`

### Pattern D: Detection + Action + Verify
**Best for:** Fix/audit skills that need to find things, fix them, confirm. Security, code quality, performance.
- Scan/detect
- Apply fixes
- Verify fixes didn't break anything
**Examples:** `/sec-ship`, `/a11y`, `/perf`, `/cleancode`

### Pattern E: Investigation + Root Cause + Regression Test
**Best for:** Debug/investigation skills. Evidence-first, hypothesis-driven.
- Evidence gathering
- Hypothesis formation
- Testing
- Minimal fix + regression test
**Examples:** `/investigate`, `/incident`

### Pattern F: Orchestration
**Best for:** Skills that coordinate multiple other skills. Launch pipelines, full audits.
- Route to sub-skills
- Aggregate results
- Produce unified report
**Examples:** `/launch`, `/sec-ship`, `/test-ship`

### Pattern G: Rapid Utility
**Best for:** Fast, focused tools. Low-ceremony, high-throughput.
- Direct execution
- Minimal interrogation
- Immediate output
**Examples:** `/smoketest`, `/dev`, `/gh-ship`

### Pattern H: Interactive Loop
**Best for:** Skills that need back-and-forth with user. Brainstorming, exploration.
- One question or action at a time
- Wait for input
- Iterate
**Examples:** `/brainstorm`

---

## What Every Skill Must Have (regardless of pattern)

### 1. Frontmatter
```yaml
---
description: "/[skill] - [one-line description optimized for discovery]"
allowed-tools: [specific tools, principle of least privilege]
---
```

### 2. Shared Standards Inheritance
Every skill references (not duplicates):
- `~/.claude/standards/SITREP_FORMAT.md`
- `~/.claude/standards/STATUS_UPDATES.md`
- `~/.claude/standards/CLEANUP_PROTOCOL.md`
- `~/.claude/standards/CONTEXT_MANAGEMENT.md`
- `~/.claude/standards/AGENT_ORCHESTRATION.md` (if spawning subagents)
- `~/.claude/standards/AUTH_GATE_PROTOCOL.md` (if launching a browser against authenticated apps)
- `~/.claude/standards/STEEL_DISCIPLINE.md`

### 3. Research-Backed Content
The skill must integrate actual industry best practices, not theoretical descriptions:
- Cite real practitioners, companies, frameworks
- Include actual templates, examples, worked cases
- Link to authoritative sources
- NO generic advice - be specific and defensible

### 4. Generic and Placeholder-Based
- NO company-specific references (not IronWorks, Steel Motion, or any)
- Use `{{product_name}}`, `{{company_name}}`, `{{target_audience}}` placeholders
- Worked examples use hypothetical brands

### 5. Related Skills Section
```markdown
## RELATED SKILLS

**Feeds from:** [skills whose output this consumes]
**Feeds into:** [skills that consume this skill's output]
**Pairs with:** [skills commonly run together]
**Auto-suggest after completion:** [what to propose next]
```

### 6. SITREP at the End
Reference `~/.claude/standards/SITREP_FORMAT.md` with domain-specific additions.

### 7. Discipline Section (for complex skills)
Rationalization table documenting common excuses and how to reject them.

### 8. Self-Improvement Hooks (NEW in v2.0)
See `~/.claude/standards/SKILL_EVOLUTION.md` for the autoresearch-inspired self-improvement system. Every skill logs telemetry for future evolution.

---

## Session Folder Convention

Skills that produce deliverables use session folders:

```
.[skill]-reports/YYYYMMDD-HHMMSS-<slug>/
  [artifacts specific to this skill]
```

NOT every skill needs a session folder. Rapid utilities and quick tools often don't.

Rules:
- Session folders are GITIGNORED
- Add to project `.gitignore`: `.[skill]-reports/`
- Persistent context (cross-session) goes in `.[skill]-context/` or `~/.claude/[skill]-global/`

---

## Global vs Project-Local Context

For skills with persistent brand/project context:
- **Local-first:** `./[skill]-context/` in current project
- **Global fallback:** `~/.claude/[skill]-global/` for reusable contexts across projects
- **Lookup order:** local -> global -> prompt user to create

---

## All Skills Live in `~/.claude/commands/`

One global folder. No per-project skills. No split directories.

This ensures:
- Every skill available from every project
- Single source of truth
- Easy inventory via `ls ~/.claude/commands/`

---

## Verification for New Skills

Before a skill is marked complete:

- [ ] Pattern chosen fits the use case (not forced pattern)
- [ ] Research-backed with real practitioners/sources cited
- [ ] Comprehensive coverage of the use case (not shallow)
- [ ] Generic with placeholders (no company refs)
- [ ] Lives in `~/.claude/commands/`
- [ ] SITREP references shared standard
- [ ] RELATED SKILLS section filled in
- [ ] No em dashes
- [ ] No sparkle icons
- [ ] Self-improvement hooks present (telemetry, eval suite stub)

---

## Evolution

This standard is versioned.
- **v1.0:** Mandated same 5-phase pattern for all skills (too rigid, deprecated)
- **v2.0:** Principles-based. Each skill picks patterns that fit. Common requirements separate from execution pattern.
