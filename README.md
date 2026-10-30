# steelmotion-ops

The Claude Code skills and shared standards used day to day at [Steel Motion LLC](https://steelmotionllc.com), a veteran-owned AI development company: 22 skills, 9 commands and 17 shared standards. Each one states how its work is verified and ends with a report that leads with its status.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Works%20with-Claude%20Code-8A2BE2)](https://claude.ai/code)

> **Synced 2026-10-29.** The core skills moved from single files in `.claude/commands/` to folders in `.claude/skills/<name>/`: a short `SKILL.md` plus detail files loaded only when a step needs them. Retired since the May release, all unused: the chain wrappers (`/ship`, `/plan`, `/quality`, `/harden`, `/fortress`, `/ops`, `/intel`), the content and marketing set (`/blog`, `/content`, `/copy`, `/marketing`, `/campaign`, `/social`, `/newsletter`, `/narrative`, `/gtm`), the lead-generation set (`/hunt`, `/prospect`, `/icp-from-repo`, `/outreach`), `/scrape`, and `/sec-weekly-scan` and `/compliance-docs` (both now modes of `/compliance`). New: `/docs-sync`.

## Install

```bash
bash <(curl -s https://raw.githubusercontent.com/VetSecItPro/steelmotion-ops/main/install.sh)
```

Skills go to `~/.claude/skills/`, commands to `~/.claude/commands/`, standards to `~/.claude/standards/`. A file or skill folder with the same name is replaced, so back up anything you changed first.

## Skills (`.claude/skills/`)

| Skill | What it does |
|---|---|
| `/a11y` | Accessibility audit and remediation to WCAG 2.2 Level AA |
| `/cleancode` | Technical-debt reduction and dead-code elimination |
| `/compliance` | Privacy, data-protection and security-compliance work in one skill |
| `/db` | Database schema, migrations, drift detection and data management, safely |
| `/deps` | Dependency health and supply-chain safety |
| `/design` | Frontend design system work |
| `/docs-sync` | Keep a repo's documentation true to its code using a per-repo document register |
| `/docs` | Documentation audit and generation |
| `/gh-ship` | Disciplined git pipeline: validate, commit with a generated semantic message, push, open a PR, watch CI, fix failures at root cause, merge, verify the deploy, clean up, and learn from the run |
| `/incident` | Structured production incident response |
| `/investigate` | Systematic root-cause debugging |
| `/launch` | Launch-readiness gate: orchestrates the audit skills (sec-ship, test-ship, perf, a11y, deps, monitor) in audit-only mode, adds the five checks none of them cover (content, SEO, user-flow, payment, legal), scores every domain, and returns a single GO / CONDITIONAL / NO-GO verdict with the blockers named |
| `/mdmp` | Military Decision-Making Process adapted for software |
| `/migrate` | Major framework and library version migrations |
| `/monitor` | Post-deploy health verification |
| `/perf` | Performance audit and optimization |
| `/qatest` | Autonomous QA and UAT: discover every route, drive every interactive element and user flow in a real browser, test the API surface, check accessibility and responsive behaviour, score the result, auto-fix the safe findings and generate regression tests |
| `/redteam` | Active exploitation and multi-step attack-chain analysis against a LOCAL development instance only |
| `/repo-bootstrap` | Apply the standard project baseline to a fresh or under-configured repo |
| `/sec-ship` | AI-judgment security pipeline |
| `/smoketest` | Fast pre-ship sanity check |
| `/test-ship` | Test coverage audit, gap-fill and verification |

## Commands (`.claude/commands/`)

| Command | What it does |
|---|---|
| `/backup-verify` | Restic / Cloud-Backup Restore-Test |
| `/brainstorm` | Socratic design exploration |
| `/browse` | Unified Browser Control: navigate, inspect, screenshot, test, audit - combines Playwright MCP + higher-level operations |
| `/critique-adversarial` | Hostile cut-editor for articles |
| `/cron-audit` | Cron + Scheduled-Job Health Audit |
| `/dev` | Start a clean development server (fast, resilient, self-healing) |
| `/secrets-audit` | Env Files, Backup Coverage, Key Rotation Health |
| `/subagent-dev` | Automated plan execution with two-stage review per task |
| `/write-skill` | TDD for skill creation: pressure-test a scenario WITHOUT the skill (RED), write the skill (GREEN), close loopholes via rationalization tables (REFACTOR) |

## Shared standards (`.claude/standards/`)

Skills point at these instead of repeating them: [AGENT_ORCHESTRATION](.claude/standards/AGENT_ORCHESTRATION.md), [AI_JUDGMENT_PARADIGM](.claude/standards/AI_JUDGMENT_PARADIGM.md), [AUTH_GATE_PROTOCOL](.claude/standards/AUTH_GATE_PROTOCOL.md), [CHANGELOGS_SHIP_WITH_RELEASES](.claude/standards/CHANGELOGS_SHIP_WITH_RELEASES.md), [CI_VERCEL_COST_OPTIMIZATION](.claude/standards/CI_VERCEL_COST_OPTIMIZATION.md), [CLEANUP_PROTOCOL](.claude/standards/CLEANUP_PROTOCOL.md), [CONTEXT_MANAGEMENT](.claude/standards/CONTEXT_MANAGEMENT.md), [MULTI_REPO_AWARENESS](.claude/standards/MULTI_REPO_AWARENESS.md), [SELF_IMPROVEMENT_PROTOCOL](.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md), [SITREP_FORMAT](.claude/standards/SITREP_FORMAT.md), [SKILL_AUTOSUGGEST_PROTOCOL](.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md), [SKILL_PATTERN](.claude/standards/SKILL_PATTERN.md), [SKILL_ROUTER](.claude/standards/SKILL_ROUTER.md), [STATUS_UPDATES](.claude/standards/STATUS_UPDATES.md), [STEEL_DISCIPLINE](.claude/standards/STEEL_DISCIPLINE.md), [TESTS_SHIP_WITH_CODE](.claude/standards/TESTS_SHIP_WITH_CODE.md), [VERIFY_BEFORE_DESTROY](.claude/standards/VERIFY_BEFORE_DESTROY.md).

## How a skill runs

A skill detects the stack it is pointed at rather than assuming one, works in phases with a verification step at each, cleans up after itself, and ends with a report that leads with its status (fixed, pending, blocked) and a suggested next step. Reports go to a gitignored `.<skill>-reports/` folder in the project.

## License

MIT. See [LICENSE](LICENSE).
