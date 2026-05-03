# claude-code-skills

A production skill collection and operating methodology for [Claude Code](https://claude.ai/code). 40 skills covering development, security, testing, shipping, marketing, and lead generation - each with explicit verification rules, cross-skill awareness, and intent-based routing so you don't have to memorize command names.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Works%20with-Claude%20Code-8A2BE2)](https://claude.ai/code)

Built and maintained by [Steel Motion LLC](https://steelmotionllc.com), a military veteran-owned AI development agency. These are the skills we actually use in client and product work.

> **Repository renamed 2026-05-03:** `claw-ops` → `steelmotion-ops`. GitHub auto-redirects from the old name; no action needed for existing clones.

> **2026-05-03 architecture upgrade:** /gh-ship rewrote to AI-judgment paradigm (read + reason vs grep error tables) with multi-repo awareness, self-healing, and self-improvement via `.gh-ship-history.json`. 13 other repo-operating skills inherit 4 new shared standards: [AI-Judgment Paradigm](.claude/standards/AI_JUDGMENT_PARADIGM.md), [Self-Improvement Protocol](.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md), [Multi-Repo Awareness](.claude/standards/MULTI_REPO_AWARENESS.md), [Verify Before Destroy](.claude/standards/VERIFY_BEFORE_DESTROY.md). See [PR #10](../../pull/10) and [PR #11](../../pull/11) for details, and [the rewrite plan](.claude/commands/_plans/skills-collection-rewrite-plan.md) for what's next.

---

## Table of Contents

- [What This Is](#what-this-is)
- [How Skills Work](#how-skills-work)
- [Full Skill Catalog](#full-skill-catalog)
- [Shared Standards](#shared-standards)
- [Sample Skill Chains](#sample-skill-chains)
- [Natural Language Routing](#natural-language-routing)
- [Installation](#installation)
- [FAQ](#faq)
- [License](#license)

---

## What This Is

Claude Code is Anthropic's CLI for Claude. Out of the box, it handles general coding tasks well. This repo adds 40 structured skills so specific jobs - security audits, performance tuning, full git pipelines, marketing campaigns, lead generation, database migrations - run with consistent discipline every time.

Each skill is a markdown file that teaches Claude a specific workflow, the rules for that workflow, the verification required before claiming completion, and the cleanup expected after the work is done. The skills share a common foundation (reporting format, status updates, cleanup protocol, sub-agent orchestration) so output is predictable across every skill.

You don't memorize the 40 commands. An intent router reads your natural language and picks the right skill. Say "ship it" and `/gh-ship` runs. Say "this is broken" and `/investigate` runs. Say "find people complaining about this problem" and `/hunt` runs across Hacker News, GitHub Issues, Reddit, and Indie Hackers.

---

## How Skills Work

A skill is a `.md` file in `~/.claude/commands/`. When Claude Code loads, it reads all skills plus your global `CLAUDE.md`. The routing table in `CLAUDE.md` maps common phrases to skills.

When a skill runs, it follows this structure:

1. **Intake** - parse what was requested, classify complexity
2. **Pre-flight checks** - verify prerequisites (build passes, git state is clean, etc.)
3. **Historical awareness** - read the last 2-3 reports from prior runs to avoid re-discovering known issues
4. **Work phases** - the actual work, broken into discrete steps with verification at each
5. **Cleanup** - close servers, delete test data, verify no orphaned processes
6. **SITREP** - structured final report (before/after metrics, what was fixed, what was deferred with reasons, what was blocked, recommended next skills)

Reports save to `.<skill>-reports/` (gitignored by default). The report is the single source of truth and survives context resets - if Claude's session restarts mid-run, it reads the state file and resumes where it left off.

---

## Full Skill Catalog

Each skill includes a one-line description and an explanation of what it actually does.

### Planning

**`/brainstorm`** - Socratic design exploration.
Asks one question at a time to get a vague idea to an approved spec. Presents 2-3 genuinely different approaches with tradeoffs before recommending. Hard gate: no code is written until you approve an approach. Produces a spec document ready for `/subagent-dev` to execute.

**`/mdmp`** - Military Decision-Making Process adapted for software.
Six specialist lenses (Engineering, Product, Security, QA, Design, DevOps) analyze your proposal. Generates 2-3 Courses of Action with decision matrix. One pause point - your selection. Then autonomous execution through completion. For strategic changes where multiple concerns must be weighed.

### Building

**`/subagent-dev`** - Automated plan execution with two-stage review.
Reads a spec from `/brainstorm` or `/mdmp`. For each task, dispatches an implementer sub-agent, then a spec-compliance reviewer (does the code match what was asked?), then a code-quality reviewer (is the code well-built?). Sequential execution prevents merge conflicts; parallel reviews keep throughput up. Each task gets a full audit trail.

**`/dev`** - Clean development server.
Auto-detects framework (Next.js, Remix, Astro, SvelteKit). Detects port conflicts and resolves them. Self-heals if the server fails. Reports the actual URL to use.

**`/browse`** - Unified browser control via Playwright MCP.
Navigate, click, type, take screenshots, run JavaScript in page context. Used standalone for manual inspection or as a sub-tool from `/qatest`, `/a11y`, `/perf`, `/design`.

### Debugging

**`/investigate`** - Systematic root-cause debugging.
Five phases: evidence collection, pattern analysis, hypothesis testing, minimal fix, regression test. Three-strike rule - if three hypotheses fail, escalates automatically rather than guessing. Each hypothesis is tested with specific evidence. Every fix ships with a regression test that would have caught the original bug.

**`/incident`** - Production incident response.
Triage, root cause, fix, verify, postmortem. Runs the 5 Whys even under pressure. Distinguishes between stabilization (rollback) and resolution (root cause fixed). Generates a postmortem document as a required output.

### Testing

**`/test-ship`** - Comprehensive test audit and execution.
Finds coverage gaps, writes missing tests with strict RED-GREEN-REFACTOR (watch the test fail first, then make it pass), runs the full suite, quarantines flaky tests, reports with before/after coverage numbers.

**`/smoketest`** - Quick pre-ship sanity check (~2-3 minutes).
Lint, typecheck, build, basic route probes. Fast, honest, doesn't try to do too much.

**`/qatest`** - Autonomous end-to-end QA.
Crawls every page, tests every interaction, validates every API endpoint, takes screenshots at multiple breakpoints, reports with a ship/no-ship verdict.

**`/redteam`** - Active exploitation testing against localhost.
OWASP attack patterns against your running application. Reports a Fortress/Breached verdict with specific exploits demonstrated. Safety-bounded - only targets localhost.

### Security

**`/sec-ship`** - Full security pipeline.
Audit → fix → validate. Covers OWASP Top 10 (Web + API + LLM), supply chain, config security, business logic flaws. Every finding gets a confidence score 1-10; the daily mode reports only 8+ (zero noise), comprehensive mode reports everything with confidence tagged.

**`/sec-weekly-scan`** - Scheduled security audit across all your repos.
Runs `/sec-ship` against each repo, aggregates findings, surfaces the highest-risk items across the portfolio.

**`/compliance`** - Privacy and data compliance (GDPR, CCPA).
Audits for missing disclosures, incomplete policies, broken links in legal documents, cookie consent gaps.

**`/compliance-docs`** - Enterprise compliance documentation generator.
Produces vendor questionnaires, SOC 2 artifacts, security one-pagers. Synthesizes from your actual codebase, not generic templates.

### Performance and Accessibility

**`/perf`** - Performance audit with Lighthouse + Core Web Vitals.
Runs Lighthouse at 3 viewport sizes. Measures LCP, CLS, INP on real pages. Identifies top 5 bottlenecks with specific fixes. Before/after metrics for every change.

**`/a11y`** - WCAG 2.1 AA compliance audit.
axe-core scanning, keyboard navigation testing, color contrast validation. Auto-fixes what's safe (ARIA labels, heading order), flags what needs human judgment.

### Code Quality

**`/cleancode`** - Dead code elimination.
Unused exports, zombie files, redundant logic, over-complex functions. Distinguishes "truly unused" from "used only in tests" from "used across service boundaries you can't see" before removing.

**`/docs`** - Documentation generator focused on WHY.
Captures design decisions that aren't obvious from reading the code. Not autogenerated API docs - the reasoning that made the code look the way it does.

**`/deps`** - Dependency health check.
Outdated packages, CVEs, license issues, supply chain risk. Groups findings by severity. Auto-updates patch versions; flags major bumps for review.

### Shipping

**`/gh-ship`** - Full git pipeline end to end.
Analyzes changes, writes a commit message reflecting actual changes (not "update files"), creates feature branch, pushes, opens PR, waits for CI, auto-fixes CI failures where possible, merges when green, verifies deployment with a real HTTP request against the preview and production URLs, cleans up the branch. Never force-pushes to main.

**`/launch`** - Launch readiness pipeline.
Orchestrates `/sec-ship`, `/perf`, `/a11y`, `/deps`, `/test-ship`, `/compliance` in audit mode plus five launch-specific checks (SEO, legal pages, error handling, 404 experience, monitoring setup). Scored GO/NO-GO verdict.

**`/monitor`** - Post-deploy health check.
Probes every route, verifies every API endpoint, checks error rates in logs. Doesn't trust the deploy dashboard - probes the actual production URL.

**`/migrate`** - Major version upgrade.
Next.js, React, Node, TypeScript. Analyzes breaking changes from the changelog, applies codemods, updates code patterns, runs the full test suite against the upgraded version, deploys to a preview environment before declaring complete.

### Data

**`/db`** - Database schema, migrations, drift detection.
Compares current schema vs. desired schema, generates migration files, detects drift between environments, manages RLS policies, handles seed data.

### Design

**`/design`** - Frontend design system.
Auto-detects state: no pages exist → generates premium pages from scratch. Pages exist → audits every screen for consistency, responsiveness, and design debt; fixes what's safe. Anti-slop standards are enforced (no generic stock templates, specific visual language per project).

### Marketing and Content

**`/marketing`** - Full campaign pipeline.
Runs ICP definition, messaging framework (Tier 1/2/3 messages), channel plan, asset checklist, production. Produces a reusable strategy doc that `/copy`, `/social`, `/blog`, and `/newsletter` read as their source of truth.

**`/campaign`** - 90-day GTM launch playbook.
Takes a product and produces a week-by-week timeline with owners, KPIs, assets required, and a launch gate checklist. Orchestrates `/social` and `/copy` for asset production during execution.

**`/copy`** - Conversion copywriting.
Landing pages, email sequences, ad copy, onboarding flows, sales pages, CTAs. Includes embedded teardown checklist (Unbounce-style 18-point audit) for validating any asset. Headlines always ship with 5-10 variants.

**`/social`** - Platform-native social content.
LinkedIn, X, Instagram, TikTok, Threads. Adapts tone and length per platform (same message, different execution). Content calendars with 4:1 value-to-promo ratio enforced. Includes embedded 2026 platform intelligence (algorithm signals, best practices per platform).

**`/newsletter`** - Newsletter-first operator skill.
Issue structure, voice development, list-building tactics, repurposing to social. Covers subject-line discipline, body structure (one idea per issue, 200-600 words), cadence rules, and metrics that matter (reply rate and forward rate, not vanity opens).

**`/narrative`** - Storytelling craft.
Scene-setting, aha-moments, dialogue, opening patterns, voice fingerprinting. Called standalone or as a sub-skill from `/copy` and `/social` when storytelling is the primary mechanism (origin stories, customer stories, founder notes).

**`/blog`** - Article publishing pipeline with auto-deploy.
Interactive drafting, auto-detects project (Velite, Contentlayer, MDX), enforces frontmatter schema, previews locally, deploys via `/gh-ship` when approved.

**`/prospect`** - ICP definition, prospect research, lead scoring.
Writes `icp.json` and `scoring.json` that sibling skills (`/marketing`, `/copy`, `/social`) read. Supports batch scoring a list or individual prospect briefs with relationship history and recent news.

**`/icp-from-repo`** - Auto-extract product context from a local code repo.
Reads package manifests, README, landing pages, and feature routes. Cross-checks marketed features against shipped code and flags the delta (aspirational vs. under-marketed). Writes `product-brief.json` that `/prospect` consumes in Phase 0, eliminating cold-interview tedium when you own the product.

**`/hunt`** - Cross-channel pain-signal prospect discovery.
Sweeps Hacker News (Algolia API), GitHub Issues, Reddit (via SearXNG proxy), and Indie Hackers (via SearXNG site: queries) for prospects expressing pain your ICP cares about. One unified scoring rubric across all channels so cross-channel comparisons are valid. Drafts value-first public replies following each channel's etiquette rules; never auto-posts; never DMs. Respects Reddit's `Disallow: /` robots policy by routing through SearXNG or Google site: search instead of direct API hits. Channel backends are pluggable; new sources plug in without touching the core.

**`/outreach`** - Personalized cross-channel outreach drafts. *(DRAFT SPEC - implementation pending user decisions on delivery backends.)*
Takes Tier 1 signals from `/hunt`, the ICP, and product brief to produce hyper-personalized outreach drafts that quote the prospect's exact pain language back to them. Channel-aware: LinkedIn connect requests (200-300 chars max), cold email sequences (90 words touch #1, micro-yes CTAs only), X/Twitter replies (thread-aware). No volume play. Every draft references a specific signal ID; never spray-and-pray. One CTA, low friction, no calendar link until touch #3.

### Meta

**`/write-skill`** - Create new skills using the same methodology.
Pressure-tests a scenario without the new skill first (observe what goes wrong), then writes the skill to close those failure modes, then pressure-tests again with the skill active. Iterate until no new loopholes are found.

---

## Shared Standards

Six files in `~/.claude/standards/` that every skill inherits. These prevent drift between skills and mean you only define each pattern once.

**`STEEL_DISCIPLINE.md`** - The five non-negotiable rules every skill enforces:
1. No completion claims without fresh verification evidence
2. No fixes without root cause investigation first
3. No production code without a failing test first (when TDD applies)
4. No implementation before approved design (when planning applies)
5. No placeholders in plans or specs

Plus a rationalization defense table listing the common shortcuts AI agents try to take with specific counter-arguments.

**`SKILL_ROUTER.md`** - The intent-to-skill mapping table. How natural language gets routed to the right skill.

**`STATUS_UPDATES.md`** - Standard emoji-prefixed progress format used by every skill. No skill reinvents the way it reports progress.

**`SITREP_FORMAT.md`** - Unified final report structure. Every skill ends with a SITREP in the same format: scope, before/after metrics, what was fixed, what was deferred with reasons, what was blocked with reasons, recommended next skills.

**`CLEANUP_PROTOCOL.md`** - Resource cleanup rules. Every skill closes its browsers, stops servers it started, deletes test data, verifies no orphaned processes before exiting.

**`CONTEXT_MANAGEMENT.md`** - Sub-agent protocol. Sub-agents write details to disk and return summaries under 500 tokens. Prevents the orchestrator's context from filling up mid-run.

**`AGENT_ORCHESTRATION.md`** - Model selection per task type (haiku for pattern matching, sonnet for reasoning, opus for architecture), agent batching rules, failure handling, cross-skill awareness.

---

## Sample Skill Chains

Skills work well in sequence. These are combinations we use regularly.

### Chain 1: Ship a new feature end-to-end

```
/brainstorm → /subagent-dev → /test-ship → /sec-ship --diff → /gh-ship → /monitor
```

- `/brainstorm` produces an approved spec
- `/subagent-dev` implements each task with two-stage review
- `/test-ship` adds missing test coverage
- `/sec-ship --diff` scans only the changed files for security issues
- `/gh-ship` commits, opens PR, waits for CI, merges, deploys
- `/monitor` verifies production is actually working post-deploy

### Chain 2: Fix a production bug

```
/incident → /investigate → /test-ship → /gh-ship → /monitor
```

- `/incident` stabilizes and opens a postmortem
- `/investigate` finds the root cause and applies a minimal fix
- `/test-ship` adds a regression test so the bug can't recur unnoticed
- `/gh-ship` ships the fix
- `/monitor` confirms production is healthy

### Chain 3: Pre-launch readiness

```
/cleancode → /deps → /test-ship → /sec-ship → /perf → /a11y → /launch
```

Remove dead code first so subsequent audits aren't wasting time on code that's about to be deleted. Update dependencies. Run tests. Security audit. Performance baseline. Accessibility compliance. Then `/launch` for the final GO/NO-GO verdict.

### Chain 4: Product launch campaign

```
/icp-from-repo → /brainstorm → /marketing → /campaign → /prospect → /hunt → /outreach → /copy → /social → /newsletter → /blog
```

- `/icp-from-repo` - read the product repo, extract features, pricing, stack, audience hints
- `/brainstorm` - refine the positioning before building anything
- `/marketing` - produce the messaging framework (ICP, positioning, Tier 1/2/3 messages)
- `/campaign` - 90-day GTM timeline with specific weekly deliverables
- `/prospect` - identify and score target accounts (pre-filled from product-brief.json)
- `/hunt` - sweep HN, GitHub Issues, Reddit (via SearXNG), Indie Hackers for prospects describing the pain in their own words; score on one rubric; draft value-first replies per channel etiquette
- `/outreach` (when built) - hyper-personalized DM/email drafts quoting each prospect's exact pain language
- `/copy` - landing page and email sequences using the messaging framework
- `/social` - content calendar with posts per platform
- `/newsletter` - long-form issues for the owned audience
- `/blog` - SEO articles supporting the campaign

Each downstream skill reads the upstream skill's output - no re-entering the same ICP five times.

### Chain 5: Major framework upgrade

```
/deps → /migrate → /test-ship → /sec-ship --diff → /gh-ship → /monitor
```

Check dependencies first (some issues are fixed by the upgrade itself). Run the migration. Full test suite against the new version. Security scan on the changes. Ship. Monitor.

### Chain 6: Maintenance sweep (weekly)

```
/sec-weekly-scan → /deps → /cleancode → /docs
```

Runs on a cron. Security scan of all repos. Dependency check. Clean up anything obvious. Update documentation where code has drifted.

---

## Natural Language Routing

An intent router (`~/CLAUDE.md` + `~/.claude/standards/SKILL_ROUTER.md`) maps natural phrases to skills. Partial table:

| You say (or similar) | Routes to | Mode |
|----------------------|-----------|------|
| "not working", "broken", "can't figure out this bug" | `/investigate` | Auto |
| "production is down", "users are reporting" | `/incident` | Auto |
| "ship it", "commit and push", "open a PR" | `/gh-ship` | Auto |
| "is this secure?", "OWASP", "vulnerabilities" | `/sec-ship` | Auto |
| "slow", "Lighthouse", "Core Web Vitals" | `/perf` | Auto |
| "add tests", "test coverage", "TDD" | `/test-ship` | Auto |
| "clean up code", "dead code", "refactor" | `/cleancode` | Auto |
| "update deps", "CVE scan" | `/deps` | Auto |
| "accessibility", "WCAG", "screen reader" | `/a11y` | Auto |
| "post-deploy check", "is prod healthy" | `/monitor` | Auto |
| "QA everything", "test the whole app" | `/qatest` | Auto |
| "marketing campaign", "GTM strategy", "ICP" | `/marketing` | Auto |
| "write a landing page", "email sequence", "ad copy" | `/copy` | Auto |
| "LinkedIn post", "social calendar" | `/social` | Auto |
| "newsletter issue", "email to the list" | `/newsletter` | Auto |
| "define ICP from this repo", "extract product brief", "scan my product code" | `/icp-from-repo` | Auto |
| "find people complaining about X", "who's talking about this problem", "hunt for pain signals", "find prospects across HN/Reddit/GitHub" | `/hunt` | Auto |
| "write personalized outreach", "draft a LinkedIn note to this prospect", "quote their pain back to them" | `/outreach` | Auto |
| "I'm thinking about...", "should I..." | `/brainstorm` | Suggest |
| "big feature", "architecture change" | `/mdmp` | Suggest |
| "try to hack this", "red team" | `/redteam` | Suggest (high risk) |

Full table in `standards/SKILL_ROUTER.md`.

---

## Installation

### Prerequisites
- [Claude Code](https://claude.ai/code) installed
- Git

### Install

```bash
# Clone the repo
git clone https://github.com/VetSecItPro/claw-ops.git ~/.claude-code-skills

# Copy skills and standards to Claude Code's config locations
mkdir -p ~/.claude/commands ~/.claude/standards
cp ~/.claude-code-skills/commands/*.md ~/.claude/commands/
cp ~/.claude-code-skills/standards/*.md ~/.claude/standards/

# Install the routing block in your global CLAUDE.md
# If ~/CLAUDE.md does not exist:
cp ~/.claude-code-skills/CLAUDE.md.template ~/CLAUDE.md
# If ~/CLAUDE.md exists, append the routing block:
cat ~/.claude-code-skills/CLAUDE.md.routing-block >> ~/CLAUDE.md
```

### Verify

Open Claude Code in any project and type:

```
this is broken
```

Claude should respond:

```
Bug investigation detected. Running /investigate.
```

### Per-project customization

If you want a skill to behave differently in a specific project, add the override in that project's `CLAUDE.md`. Per-project instructions win over global skill defaults.

### Removing a skill

Delete the file or rename with `.disabled`:
```bash
mv ~/.claude/commands/redteam.md ~/.claude/commands/redteam.md.disabled
```

---

## FAQ

**Why skills instead of prompt engineering in the moment?**
Prompts are conversation-scoped and get lost. Skills are persistent. You write the discipline once and it applies every time.

**Can I use this with Cursor, Gemini CLI, Codex, Copilot, other agents?**
This is a **Claude Code skill collection**. It is not drop-in compatible with other agents.

- **Portable:** The markdown content, methodology (Steel Principles, rationalization defense, verification protocol, two-stage review), shared standards (SITREP format, cleanup protocol, status format), and skill chaining patterns.
- **Not portable without rework:** Slash command dispatch (Claude Code's command parser), the `~/.claude/commands/` + `~/.claude/standards/` directory convention, global `CLAUDE.md` auto-loading (Claude Code's session hooks), the `allowed-tools` frontmatter permission model, the `Task` and `Skill` tool invocations inside skills (Claude Code APIs).

Porting to another agent is feasible with moderate effort - Gemini CLI has a similar `GEMINI.md` + extension system, Cursor has a `.cursor-plugin` system, Codex has `.codex/`. Each requires adapting the invocation glue. The writing transfers; the execution glue has to be rebuilt per platform.

Short version: use this with Claude Code. Fork it and port if you want it elsewhere.

**What happens if a skill is wrong for my specific project?**
Skills respect overrides from `CLAUDE.md`. Add project-specific rules there and they override skill defaults.

**Can I add my own skills?**
Yes. Use `/write-skill` - it walks you through pressure-testing, writing, and iterating a new skill.

**Team setup?**
Commit skills to `.claude/commands/` inside your repo for team-wide use. Commit standards to `.claude/standards/`. Personal skills go to `~/.claude/commands/` (global).

**Does this upload my code anywhere?**
No additional network calls. Claude Code sends your code to Anthropic's API during normal operation (required for the AI to respond); no skill in this repo changes that behavior.

**What if I don't like the rationalization defense tables?**
Edit them. They're in each skill's `DISCIPLINE` section. Or delete the whole section if you want less opinionated skills.

**How is this different from [g-stack / other skill collections]?**
Each skill collection has different design choices. This one emphasizes: (1) explicit verification rules per skill, (2) cross-skill awareness via shared state files on disk, (3) intent routing so you don't memorize commands, (4) a shared standards foundation so skills don't reinvent reporting/cleanup/status patterns, (5) marketing skills alongside the dev skills because we use both daily in agency work.

**Pricing?**
MIT-licensed. Free. No SaaS component. You pay for Claude Code usage per Anthropic's pricing.

**Contributing?**
PRs welcome if they follow the existing structure (Steel Principles, rationalization defense, shared standards inheritance). Open an issue first if it's a non-trivial change.

---

## Related Projects

- **[claw-nolan](https://github.com/VetSecItPro/claw-nolan)** - The same methodology applied to a Chief of Staff AI agent running on OpenClaw with Telegram. Different surface, same discipline.

---

## License

MIT. See [LICENSE](LICENSE).

Maintained by [Steel Motion LLC](https://steelmotionllc.com) - military veteran-owned AI development agency (Dallas-Fort Worth).
