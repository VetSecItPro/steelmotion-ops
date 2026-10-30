---
name: repo-bootstrap
description: "Apply the standard project baseline to a fresh or under-configured repo: test framework + a CI gate that blocks merges, .gitignore, CHANGELOG, pre-commit hooks, the cost-optimisation config (path filters, ignored build steps), .claude/agents/ role definitions with restricted tool sets, and the three living project docs (CLAUDE.md, state-backlog, lessons-learned). Detects what is already present and adds only what is missing. Distinct from /init, which only writes a CLAUDE.md."
when_to_use: 'Trigger phrases: "new repo setup", "bootstrap this repo", "apply project standards", "set up CI here", "scaffold this repo", "get this repo to baseline". Run once on a new repo, or on an old one that drifted from the baseline.'
---

# /repo-bootstrap - apply the standard baseline

**Spine. Survives compaction.** Detail beside it:

| File | Read at | Holds |
|---|---|---|
| `baseline.md` | Stage 1 | the full baseline checklist, per stack, with the drop-in templates |
| `reference.md` | report | what was added vs already present, SITREP |

**Standards inherited:** [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) ·
[Steel Discipline](~/.claude/standards/STEEL_DISCIPLINE.md) ·
[Self-Improvement](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) ·
[Multi-Repo Awareness](~/.claude/standards/MULTI_REPO_AWARENESS.md) ·
[Status Updates](~/.claude/standards/STATUS_UPDATES.md) ·
[Skill Auto-Suggest](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) ·
[Context Management](~/.claude/standards/CONTEXT_MANAGEMENT.md) ·
[Sitrep Format](~/.claude/standards/SITREP_FORMAT.md) ·
[Agent Orchestration](~/.claude/standards/AGENT_ORCHESTRATION.md)

## What it does, and why it exists

Every new repo needs the same baseline, and doing it by hand drifts - one repo gets a test framework
but no CI gate, another gets CI but no CHANGELOG, a third gets neither. This applies the baseline
consistently: **test framework + a merge-gating CI job, `.gitignore`, CHANGELOG, pre-commit hooks, and
the CI/deploy cost-optimisation config.**

It is not `/init`. `/init` analyses the codebase and writes a CLAUDE.md - useful, and complementary,
but it configures nothing. This skill installs the working machinery.

## Critical rules

1. **Detect first; add only what is missing.** A repo that already has vitest and a CI gate does not
   get them overwritten. Read the current state, diff against the baseline, apply the gap. Never
   clobber existing config.
2. **Match the stack.** The test framework, CI syntax, and gitignore are stack-specific - detect the
   language and package manager, apply the right versions. Do not install vitest in a Python repo.
3. **The CI gate must actually gate.** A CI workflow that runs tests but does not block a merge is
   decoration. The baseline is a required status check on the default branch - configure the check,
   and note that branch protection is the operator's to enable (it is plan-gated on some accounts).
4. **Verify each piece works, not just exists.** "CI is configured" means the workflow file is present
   AND a trivial push would trigger it AND it would pass on the current code. A YAML that references a
   missing script is not configured.
5. **One baseline element per commit.** Test framework, then CI, then hooks - separate, reviewable
   commits, not one opaque "bootstrap" blob.
6. **Cost-optimisation is part of the baseline** (per the CI/Vercel cost standard): path filters so
   unrelated changes do not trigger the whole matrix, an ignored-build-step short-circuit for
   monorepos, turbo/remote-cache where a monorepo warrants it.

## Modes

```
/repo-bootstrap            detect gaps, apply the full missing baseline, verify
/repo-bootstrap --audit    report what is missing vs baseline, apply nothing
/repo-bootstrap --ci       CI gate + cost config only
/repo-bootstrap --tests    test framework + one smoke test + the test script
/repo-bootstrap --hooks    pre-commit hooks only
/repo-bootstrap --agents   .claude/agents/ role definitions only
/repo-bootstrap --docs     CLAUDE.md + state-backlog + lessons-learned only
/repo-bootstrap --docs-register   install the /docs-sync checker + CI gate (NOT in the default baseline)
```

## Stages

| # | Stage | Must not be skipped |
|---|---|---|
| 0 | Detect | stack, package manager, what baseline elements already exist |
| 1 | Gap analysis | diff current state against the baseline (`baseline.md`) |
| 2 | Apply | each missing element, matched to the stack, one commit each |
| 3 | Verify | each element works - the CI would trigger and pass, hooks fire, tests run |
| 4 | Report | what was added vs already present, and what the operator must do (branch protection) |

Stages 2-4 are what a long run loses to compaction if not held here. **Stage 3 - verifying each piece
actually functions - is what separates a configured repo from one that merely has the files.**

## Definition of done

- Every baseline element present and verified working, or reported as already-present
- `.claude/agents/` seeded; **report it as unverified until the next session** - definitions load at
  session start, so the run that writes them cannot call them
- The CI gate genuinely blocks merges (check configured; branch protection flagged for the operator)
- Cost-optimisation config applied for the repo type
- Applied in per-element commits, not one blob
- Nothing existing was clobbered
- Report written; SITREP ends with "Suggested next"
