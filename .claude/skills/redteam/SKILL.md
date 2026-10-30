---
name: redteam
description: "Active exploitation and multi-step attack-chain analysis against a LOCAL development instance only. Goes beyond passive scanning: actually sends payloads to localhost, chains findings into realistic attacks, and proves or disproves exploitability with a PoC. Never touches production or external targets."
when_to_use: 'Trigger phrases: "red team", "try to hack", "attack this", "exploit", "chain analysis", "prove the vuln". Run after /sec-ship is clean, or pre-launch, on a local instance you own. Multi-step exploit-chain analysis lives here, not in /sec-ship (Steel Motion decision 2026-05-03).'
---

# /redteam - active exploitation against localhost

**Spine. Survives compaction. The safety boundary below is the reason this file is structured this
way** - it must never be the part that gets dropped.

| File | Read at | Holds |
|---|---|---|
| `attacks.md` | Phase 2+ | attack classes, chain construction, PoC standards |
| `reference.md` | reporting | report format, finding schema, SITREP |

**Standards inherited:** [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) ·
[Steel Discipline](~/.claude/standards/STEEL_DISCIPLINE.md) ·
[Agent Orchestration](~/.claude/standards/AGENT_ORCHESTRATION.md) ·
[Context Management](~/.claude/standards/CONTEXT_MANAGEMENT.md) ·
[Self-Improvement](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) ·
[Skill Auto-Suggest](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) ·
[Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md) ·
[SITREP Format](~/.claude/standards/SITREP_FORMAT.md) ·
[Status Updates](~/.claude/standards/STATUS_UPDATES.md)

## SAFETY BOUNDARY - mandatory, no exception, no rationalization

**Every request, every payload targets `http://localhost:<dev-port>` only.** If a URL does not start
with `http://localhost` (or `http://127.0.0.1`), it is not sent. There is no rationalization -
"just to confirm", "it's my own account", "the staging box is basically local" - that overrides this.
A single request to a production or external host is a hard failure of the run.

**Why localhost only:** active exploitation against a live system is an attack on a running service,
possibly a crime, and always a risk to real data and real users. The entire value of red-teaming is
available against a local instance, with none of that risk.

### External services your localhost code calls

Your endpoint may legitimately call a third party as part of normal operation. That is allowed,
within strict caps, because you are testing **what your code does** - never the third party.

| When localhost triggers | Cap during the run | Everything else |
|---|---|---|
| AI/LLM (real tokens = real money) | **3 requests total** across all prompt-injection tests | verify input handling by **code review** |
| Email | **2 total** | verify the rate limiter by code review |
| Payment | **0 real charges** - test mode only | verify webhook signature validation by code review |
| Object storage / DB REST | **0 direct** - always through the localhost API | your RLS is tested by what localhost returns |
| Admin API for test-user setup/teardown | as needed on your own project | standard admin ops, not an attack |

### What you cannot safely send live, you code-review

For any attack that would require hitting an external service to test live: **read the source, verify
the defence exists (validation, sanitization, signature check, rate limit), and report the result
marked `(code review)`** - clearly distinguished from a live-tested finding. A code-reviewed
"not vulnerable" is honest; a live test that would have cost money or risk is not worth the finding.

## Authorization

This runs against a **local instance the operator owns and controls**. Confirm at Phase 0 that the
target is local and operator-owned. If asked to point it at anything else - a client's system, a
production host, a bug-bounty target on the public internet - **decline and explain**: this skill is
scoped to local self-assessment. Point them to a proper engagement with written authorization.

## Modes

```
/redteam                 full: recon -> attack -> chain -> PoC -> report
/redteam --quick         the highest-value attack classes only
/redteam --chains        focus on multi-step chains from existing findings
/redteam --class <name>  one attack class (authz, injection, ssrf, ...)
/redteam --verify <id>   re-test one prior finding after a fix
```

## Phases

| # | Phase | Must not be skipped |
|---|---|---|
| 0 | Pre-flight | confirm target is localhost + operator-owned; start the dev server; read prior findings |
| 1 | Recon | map the real attack surface from the running app, not from the source alone |
| 2 | Attack | send payloads to localhost; observe actual behaviour (`attacks.md`) |
| 3 | Chain | combine findings into realistic multi-step attacks - this is what /sec-ship cannot do |
| 4 | Prove | a working PoC per confirmed finding, or downgrade it to unproven |
| 5 | Report | severity by demonstrated impact, with reproduction steps |

Chain analysis (Phase 3) is the reason this skill exists separately from `/sec-ship`. A collection
of individually-low findings that chain into account takeover is a critical finding, and only active,
stateful testing reveals it.

## Discipline

1. **Prove it or downgrade it.** A finding is CONFIRMED only with a working PoC against localhost. No
   PoC and no code-review confirmation → it is a hypothesis, reported as such, never as a vuln.
2. **Real impact, not theoretical severity.** Rank by what the PoC actually achieved, not by a CVSS
   guess. "Read another user's records via IDOR - PoC attached" outranks "missing header, in theory".
3. **Read the response, do not assume the payload worked.** A 500 is not proof of injection; a 200
   is not proof of bypass. Verify the actual effect.
4. **Never leave the target dirty.** Test users, planted data and modified state are cleaned up in
   Phase 5. Track everything created so nothing is orphaned.
5. **Read-only where possible; destructive tests are last and reversible.** Prove a delete works
   against a throwaway record you created, never against real seed data.

## Definition of done

- Every confirmed finding has a working localhost PoC or an explicit `(code review)` basis
- Chains explored, not just individual findings
- Severity reflects demonstrated impact
- The target is clean: every test user and planted artifact removed
- Report written; hand confirmed findings to `/sec-ship --fix` or the operator
