# Skill Router Protocol - Intent to Skill Mapping

**Version:** 1.0
**Applies to:** Every Claude Code session globally
**Companion to:** [Superpowers Discipline](./STEEL_DISCIPLINE.md)

---

## Purpose

The user should never have to memorize skill commands. When the user expresses intent in natural language, Claude should automatically recognize the intent and either:

1. **Auto-invoke** the matching skill (when the match is clear and the user is asking for the outcome the skill delivers)
2. **Suggest** the skill with a one-line explanation and wait for confirmation (when the match is plausible but ambiguous)

This document is the **intent-to-skill mapping table**. Reference it on every user message.

---

## The Core Rule

**Before responding to any user message, check:** does this request match a skill in the table below?

- If YES and the match is obvious (confidence ≥ 80%) → announce the skill and run it
- If YES but ambiguous (confidence 50-80%) → suggest the skill, ask to confirm
- If NO → respond normally

**Do not** list every possible skill the user could run. Match the intent, suggest ONE skill (or at most two alternatives if genuinely comparable).

---

<!-- BEGIN GENERATED INVENTORY - do not edit by hand, run generate-skill-router.py -->

## Intent to Skill Map

**33 skills, generated from the filesystem 2026-10-29 21:46.** 24 in `~/.claude/skills/`, 9 in `~/.claude/commands/`. The two directories are disjoint; both are live. Regenerate with `python3 ~/.claude/generate-skill-router.py` after any skill is added, renamed or removed.

| Skill | Where | What it does | Route to it when the user says |
|---|---|---|---|
| `/a11y` | skills/ | Accessibility audit and remediation to WCAG 2.2 Level AA: automated scan, then the manual checks tooling cannot do (keyboard, screen reader, focus ord... | `accessibility`, `a11y`, `WCAG`, `screen reader`, `keyboard navigation`, `contrast`, `ARIA` |
| `/cleancode` | skills/ | Technical-debt reduction and dead-code elimination: find genuinely unused code, duplication, and complexity, remove or refactor it safely with tests a... | `clean up code`, `dead code`, `technical debt`, `refactor`, `remove unused`, `simplify this`, `code smell` |
| `/compliance` | skills/ | Privacy, data-protection and security-compliance work in one skill: audit against GDPR/CCPA/HIPAA/SOC2 as applicable, generate the policy and readines... | `compliance audit`, `GDPR`, `CCPA`, `HIPAA`, `SOC2`, `privacy audit`, `data compliance` |
| `/db` | skills/ | Database schema, migrations, drift detection and data management, safely. | `DB migration`, `schema change`, `RLS policy`, `database drift`, `add a column`, `migrate the database`, `generate migration` |
| `/deps` | skills/ | Dependency health and supply-chain safety: audit for vulnerable, outdated, abandoned and malicious packages across whatever ecosystems the repo actual... | `update deps`, `outdated packages`, `CVEs in dependencies`, `npm audit`, `upgrade dependencies`, `supply chain`, `is this package safe` |
| `/design` | skills/ | Frontend design system work: auto-detects whether to generate a system from scratch or audit and improve an existing one. | `design system`, `make this look better`, `design audit`, `make it consistent`, `colour palette`, `dark mode`, `spacing` |
| `/docs` | skills/ | Documentation audit and generation: find where docs are missing, stale or signature-echoing, then generate real ones - README, API reference, architec... | `generate docs`, `document this`, `write documentation`, `update the README`, `API docs`, `the docs are stale`, `document why` |
| `/docs-sync` | skills/ | Keep a repo's documentation true to its code using a per-repo document register: each doc records the ANCHORS its claims depend on (resolved paths, sy... | `update the docs`, `update docs`, `update whatever documents this touched`, `update the applicable documents`, `record what we did`, `reflect the work in the docs`, `are my docs current` |
| `/gh-ship` | skills/ | Disciplined git pipeline: validate, commit with a generated semantic message, push, open a PR, watch CI, fix failures at root cause, merge, verify the... | `ship it`, `commit and push`, `create PR`, `deploy`, `get this live`, `push this` |
| `/incident` | skills/ | Structured production incident response: classify severity, mitigate user impact FIRST, find root cause with evidence, fix and verify, then write the ... | `production is down`, `users are reporting`, `urgent prod issue`, `site is down`, `outage`, `incident`, `emergency` |
| `/investigate` | skills/ | Systematic root-cause debugging: gather evidence before forming a theory, test hypotheses against reality rather than guessing, find the actual cause ... | `not working`, `broken`, `cannot figure out`, `why is this happening`, `deep dive`, `debug this`, `keeps failing` |
| `/launch` | skills/ | Launch-readiness gate: orchestrates the audit skills (sec-ship, test-ship, perf, a11y, deps, monitor) in audit-only mode, adds the five checks none of... | `ready to launch?`, `pre-launch check`, `launch readiness`, `are we ready to ship this`, `go/no-go`, `before we go live` |
| `/mdmp` | skills/ | Military Decision-Making Process adapted for software: frame the problem, generate genuinely distinct courses of action, war-game each against seven s... | `big feature`, `new architecture`, `overhaul`, `re-architect`, `should we build or buy`, `plan this properly`, `multi-lens analysis` |
| `/migrate` | skills/ | Major framework and library version migrations: Next 14->15, React 18->19, Tailwind 3->4, CRA->Vite, Express->Fastify and the like. | `migrate [framework]`, `major version upgrade`, `upgrade to [X]`, `Next 15`, `React 19`, `Tailwind 4`, `move from X to Y` |
| `/monitor` | skills/ | Post-deploy health verification: discover what a project actually deploys to, check it at the real URL and in the runtime itself, score six weighted c... | `post-deploy check`, `is prod healthy?`, `health check`, `did the deploy work`, `check production`, `monitor` |
| `/perf` | skills/ | Performance audit and optimization: measure a real baseline, find what actually costs time, fix at root cause, then re-measure and prove the delta. | `slow`, `performance`, `Lighthouse`, `bundle size`, `Core Web Vitals`, `LCP`, `INP` |
| `/qatest` | skills/ | Autonomous QA and UAT: discover every route, drive every interactive element and user flow in a real browser, test the API surface, check accessibilit... | `full QA`, `test all pages`, `UAT`, `user acceptance testing`, `QA sweep`, `test everything`, `quality check before shipping` |
| `/redteam` | skills/ | Active exploitation and multi-step attack-chain analysis against a LOCAL development instance only. | `red team`, `try to hack`, `attack this`, `exploit`, `chain analysis`, `prove the vuln` |
| `/repo-bootstrap` | skills/ | Apply the standard project baseline to a fresh or under-configured repo: test framework + a CI gate that blocks merges, .gitignore, CHANGELOG, pre-com... | `new repo setup`, `bootstrap this repo`, `apply project standards`, `set up CI here`, `scaffold this repo`, `get this repo to baseline` |
| `/sec-ship` | skills/ | AI-judgment security pipeline: discover the attack surface, fan out 17 specialist agents mapped to OWASP Top 10:2025, triage by exploitability, fix at... | `is this secure?`, `security audit`, `OWASP`, `vulnerabilities`, `check for CVEs`, `pentest this`, `before we launch` |
| `/session-conventions` | skills/ | The operator's working formats and procedures, relocated out of ~/.claude/CLAUDE.md on 2026-08-27 so they load on demand instead of on every turn: the... | `recap`, `snapshot`, `status?`, `where are we`, `lessons learned`, `log this`, `what git commands can I run` |
| `/smoketest` | skills/ | Fast pre-ship sanity check: run every cheap mechanical layer (types, build, lint, unit tests, page probes, headers, stray logs, env vars, dep advisori... | `smoke test`, `quick sanity check`, `does it still work`, `quick check before I ship`, `sanity check` |
| `/test-ship` | skills/ | Test coverage audit, gap-fill and verification: find what business logic is untested, write real tests for it (not smoke tests), run the full suite, a... | `test coverage`, `add tests`, `TDD`, `missing tests`, `write tests`, `is this tested`, `coverage gap` |
| `/worklog` | skills/ | End-of-session and end-of-day work journal. | `worklog`, `log the session`, `journal this`, `write up what we did`, `daily log`, `end of day`, `close out the session` |
| `/backup-verify` | commands/ | Restic / Cloud-Backup Restore-Test | `test the restore`, `is my backup actually working`, `verify backups`, `restore-test`, `have we ever restored` |
| `/brainstorm` | commands/ | /brainstorm - Socratic design exploration: one question at a time, 2-3 approaches with tradeoffs, HARD-GATE before implementation, writes approved spe... | `help me think through`, `explore approaches`, `what are the options`, `design this with me`, `I am not sure how to build this` |
| `/browse` | commands/ | /browse - Unified Browser Control: navigate, inspect, screenshot, test, audit - combines Playwright MCP + higher-level operations | `open the site`, `click through`, `screenshot this page`, `check it in a browser`, `does the page work`, `inspect the DOM` |
| `/critique-adversarial` | commands/ | /critique-adversarial - Hostile cut-editor for articles. | `cut this down`, `it is too long`, `tighten this article`, `hostile edit`, `what can I remove`, `make it sharper` |
| `/cron-audit` | commands/ | Cron + Scheduled-Job Health Audit | `are crons working`, `audit my crons`, `check scheduled jobs`, `silent cron failures`, `deploy webhook stuck` |
| `/dev` | commands/ | Start a clean development server (fast, resilient, self-healing) allowed-tools: Bash(git *), Bash(npm *), Bash(npx *), Bash(pnpm *), Bash(yarn *), Bas... | `start dev server` |
| `/secrets-audit` | commands/ | Env Files, Backup Coverage, Key Rotation Health | `audit my secrets`, `are env files backed up`, `rotate API keys`, `key rotation`, `stale env vars`, `stale secrets` |
| `/subagent-dev` | commands/ | /subagent-dev - Automated plan execution with two-stage review per task: dispatch implementer, then spec compliance reviewer, then code quality review... | `execute the plan` |
| `/write-skill` | commands/ | /write-skill - TDD for skill creation: pressure-test a scenario WITHOUT the skill (RED), write the skill (GREEN), close loopholes via rationalization ... | `build a new skill` |

<!-- END GENERATED INVENTORY -->

---

## Pipeline Triggers (Skill Chains)

Some intents trigger a chain. Announce the chain upfront rather than running it silently.
**Every skill named below was verified to exist on 2026-08-27.** Consolidated here from the former
`SKILL_CHAINS.md`, which was a 269-line duplicate of this section naming 8 skills that do not exist.

### "Build this feature end-to-end"
```
/brainstorm (or /mdmp for an expensive-to-reverse call) -> /subagent-dev -> /test-ship -> /gh-ship -> /monitor
```

### "Ship this safely"
```
/smoketest (2 min gate) -> /test-ship -> /sec-ship -> /gh-ship -> /monitor
```

### "Full audit"
```
/sec-ship -> /perf -> /a11y -> /deps -> /cleancode
```

### "Fix production issue"
```
/incident (mitigate first) -> /investigate (root cause) -> /gh-ship -> /monitor
```

### "Make it look better / feel better"
```
/design -> /a11y -> /perf
```
Contrast failures and focus indicators are fixed in the tokens by `/design`, not instance by instance.

### "Are we ready to launch?"
```
/launch (audit-only orchestration, returns GO / CONDITIONAL / NO-GO) -> fix named blockers -> /gh-ship
```
`/launch` already runs the audit skills in audit-only mode. Do not run them separately first.

### "Security, properly"
```
/sec-ship -> /redteam (only once sec-ship is clean, local instance only) -> /compliance
```
Multi-step exploit-chain analysis lives in `/redteam`, not `/sec-ship` (Steel Motion decision 2026-05-03).

### "Schema or data change"
```
/db -> /test-ship -> /gh-ship -> /monitor
```

### "Build or change a skill"
```
/write-skill -> run it on a real task -> /worklog
```

### Content and research
```
/browse (research) -> /critique-adversarial (hostile cut of the draft)
```
The old "Marketing Suite" chain routed to three skills that were planned and never built (marketing,
social, blog - written as bare names on purpose, because the slash-and-backtick form means "a real
route target" and `--check` enforces it). This is the working equivalent.

---

> **Convention, enforced by `python3 ~/.claude/generate-skill-router.py --check`:** writing a skill in
> any hand-written section as a slash-prefixed name inside backticks is a claim that the skill exists
> and is routable. The check fails the run if it does not. To mention a skill that does not exist,
> write its bare name as plain text. A comment saying a section is preserved is a claim; this is the
> check. (This note originally used a literal slash-name placeholder and the check failed on it - the
> doc explaining the rule broke the rule, which is the most honest possible self-test.)

## Flag Reference (hand-written, preserved across regeneration)

Moved here from `~/.claude/CLAUDE.md` on 2026-08-27. The generated inventory above lists every skill and its
trigger phrases; it does NOT carry flags, because flags are not in skill frontmatter. This section is
the only copy - do not delete it when regenerating.

Always include the relevant flags when suggesting: `/sec-ship --comprehensive` is a different job
from `/sec-ship --diff`, and the user should not have to remember which. The flags that actually
differ:

- `/sec-ship` - `--comprehensive` (deep; monthly + pre-launch), `--audit` (read-only), `--diff`
  (pre-PR), `--infra` / `--code` / `--supply-chain` / `--owasp` (scope), `--fix SEC-XXX` (one
  finding). Default daily mode unless the user signals otherwise.
- `/redteam` - active exploitation; multi-step chain analysis lives here, not in `/sec-ship`
  (Steel Motion decision 2026-05-03). Run after `/sec-ship` is clean, or pre-launch.
- `/test-ship`, `/qatest`, `/perf` pick their own mode; no flag needed.

---

## Disambiguation Rules

When multiple skills could match, use these tiebreakers:

### "It's not working"
- Dev server issue? → `/dev`
- Production issue? → `/incident`
- Bug in logic? → `/investigate`
- Test failing? → `/investigate` (tests are bugs until proven otherwise)
- Default: `/investigate`

### "Make this better"
- Better code quality? → `/cleancode`
- Better performance? → `/perf`
- Better security? → `/sec-ship`
- Better UX/design? → `/design`
- Better accessibility? → `/a11y`
- Default: ask which dimension matters

### "Review this"
- Security review? → `/sec-ship --audit`
- Code quality review? → `/cleancode --audit` (or inline review)
- Design review? → `/design --audit`
- Performance review? → `/perf --audit`
- Default: inline code review, no skill invoked

### "Documentation" - three skills claim this space, they are not interchangeable
- Docs are MISSING or thin, and need writing? -> `/docs` (the generate-and-audit engine)
- Docs EXIST and may no longer be true? -> `/docs-sync` (reconciles them against the code)
- Recording what THIS SESSION did and why? -> `/worklog` (the journal, not reference docs)
- "Which documents did this change affect?" -> `/docs-sync`
- **"Update the docs" / "update whatever documents this touched" -> `/docs-sync`.** There is no
  `/update-docs` and one must not be created; a second skill on the same trigger surface splits the
  routing and you get a different half of the job depending on which one matches first.
- **APPENDING a record is a different act from reconciling a live document.** A new changelog entry,
  a backlog row flipped to DONE, a lessons entry, an ADR: those belong to `/gh-ship` **Stage 2.5**,
  which runs before the commit so they ship in the same PR. `/docs-sync` refuses to touch records by
  design (its rule 2), because rewriting one destroys the only thing it is for. If the work is being
  shipped, the records are already handled and `/docs-sync` runs as part of that stage.
- "The docs are stale" -> `/docs-sync` if the repo has a register, `/docs` if it does not
- Default: `/docs-sync --audit` when a register exists, otherwise `/docs`

**Never run `/docs` to fix a `/docs-sync` finding.** One generates prose, the other repairs a
specific claim a specific change invalidated. Regenerating a document to clear a broken anchor
destroys everything in it that was still true.

### "I need to plan something"
- Small idea / "thinking about" → `/brainstorm`
- Feature with multiple approaches → `/mdmp` (TACTICAL or OPERATIONAL)
- Architectural change → `/mdmp` (STRATEGIC)
- Default: `/brainstorm` (user can escalate to `/mdmp` if needed)

---

## Announcement Format

When auto-invoking:
```
[Intent detected]
→ Running /[skill] [with flags]
→ [One-line why]
```

Example:
```
Detected: bug investigation request
→ Running /investigate
→ Evidence-first debugging, regression test mandatory
```

When suggesting:
```
This sounds like a [description] task.
→ Want me to run /[skill]?
→ [What the skill will do]

Or I can handle it inline if you prefer.
```

---

## When NOT to Invoke a Skill

Don't auto-invoke when:

1. **User explicitly asks a question** (not a task) - "How does X work?" is a question, not a skill request
2. **User wants a quick answer** - "What's the syntax for..." doesn't need a skill
3. **User is mid-conversation on an unrelated topic** - continuity matters
4. **The task is trivially small** - "Rename this variable" doesn't need `/cleancode`
5. **User has opted out** - if user says "don't use skills" or "just answer me," respect that

---

## User Override Commands

The user can override the router:

| User Says | Meaning |
|-----------|---------|
| "Don't use a skill" | Skip routing, respond directly |
| "Just answer me" | Skip routing, respond directly |
| "Run /[skill] instead" | User picks the skill explicitly |
| "I know you suggested X, but run Y" | User overrides suggestion |
| "Skip the brainstorm, just build it" | Skip planning phase |

---

## Cascading Suggestions

After a skill completes, suggest the logical next skill based on the outcome:

| Skill Finished | Common Next Steps | Suggest |
|----------------|-------------------|--------|
| `/brainstorm` approved | Implementation | "Ready to build? Run `/subagent-dev` with the spec." |
| `/mdmp` COA selected | Implementation | "Plan approved. Run `/subagent-dev` to execute tasks." |
| `/investigate` fix applied | Ship the fix | "Fix verified. Want to run `/gh-ship` to commit and deploy?" |
| `/test-ship` tests added | Ship or security check | "Tests added. Run `/gh-ship`? Or `/sec-ship` first?" |
| `/sec-ship` vulnerabilities fixed | Ship | "Security clean. Run `/gh-ship`?" |
| `/gh-ship` deploy complete | Monitor | "Shipped. Running `/monitor` to verify production health." |
| `/incident` resolved | Review & learn | "Postmortem written. Consider `/test-ship` to add regression tests." |

---

## Confidence Calibration

Examples of high vs. low confidence matches:

**HIGH CONFIDENCE (auto-invoke):**
- "the login form is broken, can't submit" → `/investigate` (specific bug, actionable)
- "ship this to prod" → `/gh-ship` (explicit ship intent)
- "scan for CVEs in our dependencies" → `/deps` (explicit request)

**MEDIUM CONFIDENCE (suggest):**
- "I want to make this faster" → `/perf` (could mean many things)
- "let's clean this up" → `/cleancode` (ambiguous scope)
- "I'm thinking about adding notifications" → `/brainstorm` or `/mdmp`

**LOW CONFIDENCE (don't invoke, just help):**
- "what does this code do?" → explain, don't run skills
- "is this a good approach?" → discuss, don't run `/mdmp`
- "how do I..." → answer, don't invoke

---

## Reference in CLAUDE.md

The user's global `~/.claude/CLAUDE.md` should include a pointer:

```markdown
## Skill Routing

On every user message, check for skill intent using the [Skill Router Protocol](~/.claude/standards/SKILL_ROUTER.md).

Key pattern:
- "I'm thinking about X" → suggest /brainstorm
- "This is broken / not working" → auto /investigate
- "Ship it" → auto /gh-ship
- "Production is down" → auto /incident
- "Is this secure?" → auto /sec-ship

See SKILL_ROUTER.md for the full intent→skill map.
```

---

**Last Updated:** 2026-04-13
