# steelmotion-ops

The Claude Code skills and shared standards used day to day at [Steel Motion LLC](https://steelmotionllc.com), a veteran-owned AI development company: 24 skills, 8 commands and 19 shared standards, plus the helper scripts they call. Each one says how its work is verified and ends with a report that leads with its status.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Works%20with-Claude%20Code-8A2BE2)](https://claude.ai/code)
[![CI](https://github.com/VetSecItPro/steelmotion-ops/actions/workflows/ci.yml/badge.svg)](https://github.com/VetSecItPro/steelmotion-ops/actions/workflows/ci.yml)

> **Synced 2026-11-17** from the live setup by `scripts/sync_from_live.py`, so this copy now follows the skills in daily use instead of drifting from them. New since October: `/architecture-survey`, `/brainstorm` as a skill folder (it was a command), the `DOMAIN_LANGUAGE` and `BACKLOG_STANDARD` standards, and the helper scripts the skills call (`ci-local.sh`, the skill-router generator and check, a backlog template).

## Install

```bash
bash <(curl -s https://raw.githubusercontent.com/VetSecItPro/steelmotion-ops/main/install.sh)
```

Skills go to `~/.claude/skills/`, commands to `~/.claude/commands/`, standards to `~/.claude/standards/`, and the helper scripts, backlog template and two agent definitions (`readonly-verifier`, `scoped-implementer`) to `~/.claude/`. Anything with the same name is replaced, and the installer copies the old version to `~/.claude/.steelmotion-ops-backup-<timestamp>/` first.

Some skills assume a few conventions: skill reports in a gitignored `.reports/<skill>/` folder, a `.ci-local` file holding the repo's local CI command, and a `<name>-backlog.md` per project. `/repo-bootstrap` sets these up in a repo.

## Catalog

<!-- catalog:start -->
| Skill | What it does |
|---|---|
| `/a11y` | Accessibility audit and remediation to WCAG 2.2 Level AA: automated scan, then the manual checks tooling cannot do (keyboard, screen reader, focus order, contrast in context), fix at root cause, verify, and report... |
| `/architecture-survey` | Module-level architecture survey: find where a codebase is hard to change by reading git hot spots and judging module depth (small interface, much behavior behind it), apply the deletion test, and return ranked... |
| `/brainstorm` | Socratic design exploration: look up what the repo can answer, then interview the operator in numbered rounds (each question with a recommended answer) until every open decision is settled, present 2-3 genuinely... |
| `/cleancode` | Technical-debt reduction and dead-code elimination: find genuinely unused code, duplication, and complexity, remove or refactor it safely with tests as the safety net, and prove nothing broke |
| `/compliance` | Privacy, data-protection and security-compliance work in one skill: audit against GDPR/CCPA/HIPAA/SOC2 as applicable, generate the policy and readiness documents an assessment needs, and run the recurring cross-repo... |
| `/db` | Database schema, migrations, drift detection and data management, safely |
| `/deps` | Dependency health and supply-chain safety: audit for vulnerable, outdated, abandoned and malicious packages across whatever ecosystems the repo actually uses, then update safely - one major at a time, tests after... |
| `/design` | Frontend design system work: auto-detects whether to generate a system from scratch or audit and improve an existing one |
| `/docs` | Documentation audit and generation: find where docs are missing, stale or signature-echoing, then generate real ones - README, API reference, architecture overview, and WHY comments where the reasoning is non-obvious |
| `/docs-sync` | Keep a repo's documentation true to its code using a per-repo document register: each doc records the ANCHORS its claims depend on (resolved paths, symbols, commands, config keys, counts), so staleness becomes a... |
| `/gh-ship` | Disciplined git pipeline: validate, commit with a generated semantic message, push, open a PR, watch CI, fix failures at root cause, merge, verify the deploy, clean up, and learn from the run |
| `/incident` | Structured production incident response: classify severity, mitigate user impact FIRST, find root cause with evidence, fix and verify, then write the postmortem and the regression test |
| `/investigate` | Systematic root-cause debugging: gather evidence before forming a theory, test hypotheses against reality rather than guessing, find the actual cause not a plausible one, apply the minimal correct fix, and add a... |
| `/launch` | Launch-readiness gate: orchestrates the audit skills (sec-ship, test-ship, perf, a11y, deps, monitor) in audit-only mode, adds the five checks none of them cover (content, SEO, user-flow, payment, legal), scores... |
| `/mdmp` | Military Decision-Making Process adapted for software: frame the problem, generate genuinely distinct courses of action, war-game each against seven specialist lenses, score on a weighted matrix, and produce an... |
| `/migrate` | Major framework and library version migrations: Next 14->15, React 18->19, Tailwind 3->4, CRA->Vite, Express->Fastify and the like |
| `/monitor` | Post-deploy health verification: discover what a project actually deploys to, check it at the real URL and in the runtime itself, score six weighted categories, and report a graded verdict with findings |
| `/perf` | Performance audit and optimization: measure a real baseline, find what actually costs time, fix at root cause, then re-measure and prove the delta |
| `/qatest` | Autonomous QA and UAT: discover every route, drive every interactive element and user flow in a real browser, test the API surface, check accessibility and responsive behaviour, score the result, auto-fix the safe... |
| `/redteam` | Active exploitation and multi-step attack-chain analysis against a LOCAL development instance only |
| `/repo-bootstrap` | Apply the standard project baseline to a fresh or under-configured repo: test framework + a CI gate that blocks merges, .gitignore, CHANGELOG, pre-commit hooks, the cost-optimisation config (path filters, ignored... |
| `/sec-ship` | AI-judgment security pipeline: discover the attack surface, fan out 17 specialist agents mapped to OWASP Top 10:2025, triage by exploitability, fix at root cause, verify by re-scan, add regression tests |
| `/smoketest` | Fast pre-ship sanity check: run every cheap mechanical layer (types, build, lint, unit tests, page probes, headers, stray logs, env vars, dep advisories), collect all findings without stopping on the first failure,... |
| `/test-ship` | Test coverage audit, gap-fill and verification: find what business logic is untested, write real tests for it (not smoke tests), run the full suite, and ship coverage that catches regressions |

**Commands** (`.claude/commands/`, single files):

| Command | What it does |
|---|---|
| `/backup-verify` | Restic / Cloud-Backup Restore-Test |
| `/browse` | Unified Browser Control: navigate, inspect, screenshot, test, audit - combines Playwright MCP + higher-level operations |
| `/critique-adversarial` | Hostile cut-editor for articles |
| `/cron-audit` | Cron + Scheduled-Job Health Audit |
| `/dev` | Start a clean development server (fast, resilient, self-healing) |
| `/secrets-audit` | Env Files, Backup Coverage, Key Rotation Health |
| `/subagent-dev` | Automated plan execution with two-stage review per task: dispatch implementer, then spec compliance reviewer, then code quality reviewer |
| `/write-skill` | TDD for skill creation: pressure-test a scenario WITHOUT the skill (RED), write the skill (GREEN), close loopholes via rationalization tables (REFACTOR) |

**Shared standards** (`.claude/standards/`), which the skills point at instead of repeating them: [AGENT_ORCHESTRATION](.claude/standards/AGENT_ORCHESTRATION.md), [AI_JUDGMENT_PARADIGM](.claude/standards/AI_JUDGMENT_PARADIGM.md), [AUTH_GATE_PROTOCOL](.claude/standards/AUTH_GATE_PROTOCOL.md), [BACKLOG_STANDARD](.claude/standards/BACKLOG_STANDARD.md), [CHANGELOGS_SHIP_WITH_RELEASES](.claude/standards/CHANGELOGS_SHIP_WITH_RELEASES.md), [CI_VERCEL_COST_OPTIMIZATION](.claude/standards/CI_VERCEL_COST_OPTIMIZATION.md), [CLEANUP_PROTOCOL](.claude/standards/CLEANUP_PROTOCOL.md), [CONTEXT_MANAGEMENT](.claude/standards/CONTEXT_MANAGEMENT.md), [DOMAIN_LANGUAGE](.claude/standards/DOMAIN_LANGUAGE.md), [MULTI_REPO_AWARENESS](.claude/standards/MULTI_REPO_AWARENESS.md), [SELF_IMPROVEMENT_PROTOCOL](.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md), [SITREP_FORMAT](.claude/standards/SITREP_FORMAT.md), [SKILL_AUTOSUGGEST_PROTOCOL](.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md), [SKILL_PATTERN](.claude/standards/SKILL_PATTERN.md), [SKILL_ROUTER](.claude/standards/SKILL_ROUTER.md), [STATUS_UPDATES](.claude/standards/STATUS_UPDATES.md), [STEEL_DISCIPLINE](.claude/standards/STEEL_DISCIPLINE.md), [TESTS_SHIP_WITH_CODE](.claude/standards/TESTS_SHIP_WITH_CODE.md), [VERIFY_BEFORE_DESTROY](.claude/standards/VERIFY_BEFORE_DESTROY.md).
<!-- catalog:end -->

## How a skill runs

A skill detects the stack it is pointed at rather than assuming one, works in phases with a verification step at each, cleans up after itself, and ends with a report that leads with its status (fixed, pending, blocked) and a suggested next step. Reports go to a gitignored `.reports/<skill>/` folder in the project.

## Not included

The skills come from a setup with a few more pieces around them. They work without these, but some text mentions them:

- **A push guard** that only lets `/gh-ship` push and asks for a reason before re-running CI. Without it, the `GH_SHIP_ACTIVE=1` prefix and `CI_RERUN_REASON` in `/gh-ship` are harmless no-ops.
- **A global gitleaks pre-commit hook.** `/gh-ship` runs gitleaks itself when no such hook is set.
- **A pull-request review bot.** `/gh-ship` reads a review decision when one exists and moves on when none does.
- **Backlog sync tooling** named in `BACKLOG_STANDARD`; the standard and the template stand on their own.
- **A personal `~/.claude/CLAUDE.md`.** A few skills cite numbered sections of one; the rule they rely on is stated where it is used.

Timestamps in `/docs-sync` and `ci-local.sh` use US Central Time; change the zone in those two files if you work elsewhere.

## How this copy is kept current

`scripts/sync_from_live.py` rebuilds `.claude/` from the maintainer's live `~/.claude`: it copies what `scripts/sync-manifest.json` lists, removes internal ticket references and private names (the private word list stays on the maintainer's machine), regenerates the skill router and this README's catalog, then runs `scripts/leak_check.py`. CI runs the leak check's public patterns and the tests in `tests/` on every pull request.

## License

MIT. See [LICENSE](LICENSE).
