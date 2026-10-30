---
name: deps
description: "Dependency health and supply-chain safety: audit for vulnerable, outdated, abandoned and malicious packages across whatever ecosystems the repo actually uses, then update safely - one major at a time, tests after each, lockfile kept clean. Aligned with sec-ship's Agent 1 (OWASP A03)."
when_to_use: 'Trigger phrases: "update deps", "outdated packages", "CVEs in dependencies", "npm audit", "upgrade dependencies", "supply chain", "is this package safe". Run before a launch, on a schedule, and whenever a lockfile changes materially.'
---

# /deps - dependency health and supply-chain safety

**Spine. Survives compaction.** Detail beside it:

| File | Read at | Holds |
|---|---|---|
| `ecosystems.md` | audit | per-ecosystem auditor + update commands; the same map sec-ship uses |
| `reference.md` | report | report format, history, SITREP |

**Standards inherited:** [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) ·
[Steel Discipline](~/.claude/standards/STEEL_DISCIPLINE.md) ·
[Self-Improvement](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) ·
[Agent Orchestration](~/.claude/standards/AGENT_ORCHESTRATION.md) ·
[Status Updates](~/.claude/standards/STATUS_UPDATES.md) ·
[Skill Auto-Suggest](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) ·
[Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md) ·
[Context Management](~/.claude/standards/CONTEXT_MANAGEMENT.md) ·
[Multi-Repo Awareness](~/.claude/standards/MULTI_REPO_AWARENESS.md) ·
[SITREP Format](~/.claude/standards/SITREP_FORMAT.md) ·
[Verify Before Destroy](~/.claude/standards/VERIFY_BEFORE_DESTROY.md)

## Supply chain is a top-3 risk (OWASP A03, 2025)

Software Supply Chain Failures moved to #3 in the OWASP Top 10:2025. This skill is the update-and-fix
half of that; `/sec-ship` Agent 1 is the find half, and **the two use the same ecosystem-to-scanner
map** (`ecosystems.md` here mirrors sec-ship's `stacks.md`). A finding raised there should be fixable
here without re-discovering it.

A dependency risk is more than a CVE count: an unmaintained package, an install script in a transitive
dep, a package pulled from a non-default registry, a maintainer change, or a typosquat are all A03
even with zero advisories.

## Critical rules

1. **Detect ecosystems, do not assume npm.** A repo can carry Node + Python + Go + a Dockerfile at
   once. Audit each with its own tooling (`ecosystems.md`). Missing a language is a coverage hole.
2. **One major version at a time.** Batching majors makes a breakage impossible to attribute. Update,
   run the full test suite, commit, then the next.
3. **The full test suite, not a smoke test.** A dependency update that passes lint and typecheck can
   still break behaviour. For services, that means unit AND integration
   (a zod-4 break once passed unit and was caught only by testcontainers).
4. **Never bump a pinned-by-decision version without checking why it is pinned.** A version held back
   by an ADR or a comment is a decision, not neglect.
5. **Read the changelog before a major.** The breaking-change list tells you what to fix; guessing
   from test failures is slower and misses silent behaviour changes.
6. **Keep the lockfile clean.** Regenerate through the package manager, never hand-edit. Commit the
   lockfile with the update that produced it.
7. **A malicious-package signal beats an outdated one.** A typosquat or a compromised release is
   urgent; a version two minor behind is not.

## Modes

```
/deps                 audit + safe updates (patch/minor auto, majors one-by-one with tests)
/deps --audit         report only, change nothing
/deps --security      security advisories only - the fast pre-launch check
/deps --majors        walk the major upgrades interactively, one at a time
/deps --unused        find and remove dependencies nothing imports
/deps --dedupe        collapse duplicate versions in the lockfile
```

## Update safety ladder - safest first

| Tier | What | How |
|---|---|---|
| 1 | Security patches in range | apply, run tests, commit. Highest priority |
| 2 | Patch/minor, in range | batch is acceptable; tests; commit |
| 3 | Majors | **one at a time**, changelog first, tests after each, separate commit |
| 4 | Unmaintained / risky | flag for a decision; do not auto-replace a dependency |
| 5 | Malicious signal | stop, surface immediately, do not auto-anything |

Never skip a tier to reach a shinier one. A repo with three security patches pending does not get a
React major first.

## Automation awareness

If the repo runs Renovate or Dependabot, **work with it, not against it.** Check its config and open
PRs before acting; a manual bump that duplicates a bot PR wastes CI and muddies the lockfile. Note
in the report which updates the bot already has in flight.

Where the bot's PRs do not self-run CI (self-hosted Renovate with a `GITHUB_TOKEN`), they must be
validated locally before merge - and local validation must match CI, which for services means
integration tests, not unit-only.

## Definition of done

- Every ecosystem in the repo audited, or the gap named
- Security advisories resolved or explicitly deferred with a reason
- Majors done one at a time, each with a passing full suite and its own commit
- Lockfile regenerated cleanly, committed
- Unmaintained/risky deps flagged for decision, not silently swapped
- Report written; SITREP ends with "Suggested next"
