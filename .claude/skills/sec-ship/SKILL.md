---
name: sec-ship
description: "AI-judgment security pipeline: discover the attack surface, fan out 17 specialist agents mapped to OWASP Top 10:2025, triage by exploitability, fix at root cause, verify by re-scan, add regression tests. Stack-agnostic - detects the ecosystem and uses that ecosystem's scanners."
when_to_use: 'Trigger phrases: "is this secure?", "security audit", "OWASP", "vulnerabilities", "check for CVEs", "pentest this", "before we launch". Also whenever dependencies change materially, an auth or admin surface is added, or a repo is being prepared for release.'
---

# /sec-ship - AI-judgment security pipeline

**This file is the spine and always stays in context.** The detail lives beside it and is read when
needed:

| File | Read it | Holds |
|---|---|---|
| `stacks.md` | Stage 0.2 | ecosystem detection to scanner map, ~20 stacks, fallback rules |
| `agents.md` | Stage 2, before dispatch | the 17 agent briefs, OWASP 2025 map, waves, model choice |
| `reference.md` | Stage 0.6, Stage 6, on resume | report format, history schema, SITREP, design notes |

Read them with the Read tool at the stage named. Do not work from memory of a previous run - the
briefs changed when OWASP 2025 landed.

**Standards inherited** (apply throughout; read when the stage calls for the detail):
[AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) ·
[Steel Discipline](~/.claude/standards/STEEL_DISCIPLINE.md) ·
[Agent Orchestration](~/.claude/standards/AGENT_ORCHESTRATION.md) ·
[Context Management](~/.claude/standards/CONTEXT_MANAGEMENT.md) ·
[Self-Improvement](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) ·
[Multi-Repo Awareness](~/.claude/standards/MULTI_REPO_AWARENESS.md) ·
[Verify Before Destroy](~/.claude/standards/VERIFY_BEFORE_DESTROY.md) ·
[Status Updates](~/.claude/standards/STATUS_UPDATES.md) ·
[Skill Auto-Suggest](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md)

## Progress display

```
Phase 1: Discovery      history read, ecosystems detected, siblings noted
Phase 2: Scanning       agent N (name): M findings ... running total
Phase 3: Triage         gate=<8|2>, auto-fixable / manual / deferred
Phase 4: Fix loop       per finding, with the verifying re-scan
Phase 5: SITREP         coverage attestation + history append
```

## Paradigm

This is a planning document Claude executes, not a script. Scanner output is **data**; the security
judgment is the skill. "If grep says X, report X" is the anti-pattern - read the code path, decide
whether it is reachable and exploitable **in this codebase, in its current configuration**, then act.

Find things nobody specified. A scanner rule set is never complete; the agents give structure to
look under, not a closed list of what can be wrong.

## Discipline

Steel principles as they apply here:

1. **No completion claims without evidence.** "Fixed" means the scanner that found it was re-run and
   is clean, plus a regression test exists. Not "the edit looks right."
2. **Root cause only.** Never `// security-disable-line`, never `as any`, never widen a type to
   silence a finding.
3. **3-strike rule.** Three failed fix attempts on one finding means it is architectural. Stop,
   document the attempts, mark BLOCKED, escalate.
4. **Triage honestly.** Do not lower a confidence score to dismiss a real finding, and do not raise
   one to pad the report.

### Rationalization defense

| Rationalization | Reality | Do |
|---|---|---|
| "Probably a false positive" | Probably is not a verdict | Read the path. Score it. Justify in two sentences. |
| "Skip that agent to save context" | That is a coverage hole with a nice name | Tighten the agent prompt instead. Skips are only legal per the matrix. |
| "No scanner installed for this language" | Absence of a tool is not absence of vulns | Fall back to semgrep + reading; record the gap in the SITREP. |
| "The framework handles that" | Sometimes. Verify which version, which config | Check the actual setting. |
| "It's behind auth" | Auth can be bypassed; that is why Agent 4 exists | Still score it. |
| "Dev-only dependency" | Dev deps run in CI, which has secrets | Check reachability before excluding. |

## Critical rules

1. Never ask permission mid-run. Report outcomes, not intentions.
2. Never silently drop a finding. Every one ends FIXED, DEFERRED, BLOCKED or FALSE-POSITIVE.
3. Never skip an applicable agent for budget reasons - see the applicability matrix.
4. The orchestrator never reads source directly. It dispatches and collects ≤200-token summaries.
5. Fix at root cause, verify by re-running the scanner that found it.
6. Every verified fix gets a regression test (Agent 15).
7. Read `.sec-ship-history.json` first; try known-good fixes before inventing one.
8. Coverage attestation is mandatory in every SITREP.

## Modes

```
/sec-ship                  full audit + auto-fix, 8/10 gate
/sec-ship --comprehensive  deep scan, 2/10 gate - monthly or pre-launch
/sec-ship --audit          scan only, no fixes
/sec-ship --diff           scope to the current branch diff (fast pre-PR)
/sec-ship --infra          infrastructure and CI/CD only (13, 17)
/sec-ship --code           application code only (3, 4, 5, 6, 10, 11, 12, 14)
/sec-ship --supply-chain   deps and build artifacts only (1, 17) - A03
/sec-ship --owasp          every agent owning a 2025 category (1, 3-7, 10-14, 17)
/sec-ship --ai             LLM and agentic surface only (8)
/sec-ship --fix SEC-XXX    fix one finding
/sec-ship --key-rotation   walk through rotating a provider key
```

### Bare `/sec-ship` picks its own mode

**Never make the operator remember a flag.** With no argument, decide from repo state and say which
mode you chose and why in one line before starting. If the signals conflict, state the top two and
proceed with the safer (wider) one rather than asking.

| Repo state | Mode | Why |
|---|---|---|
| On a feature branch with commits ahead of the default branch | `--diff` | pre-PR check; scope to what changed |
| No prior run in `.sec-ship-reports/`, or none within 30 days | `--comprehensive` | no baseline exists; establish one |
| Last run < 7 days old and the diff since is dependency files only | `--supply-chain` | only the supply surface moved |
| The diff since the last run touches only CI, Dockerfile, IaC | `--infra` | only the infra surface moved |
| The diff touches prompts, tool definitions, agent loops or LLM SDK calls | `--ai` | agent 8 is the surface that changed |
| Release branch, tag, or the operator said "before we launch" | `--comprehensive` | pre-launch gate |
| Anything else | default | full audit at the 8/10 gate |

An explicit flag always wins. `--audit` composes with any of the above when fixes are unwanted.

**The scoped modes are derived from the OWASP owner map in `agents.md`, not hand-maintained.**
Before dispatching a scoped mode, read that map and take the agents it names. `--owasp` used to mean
agents 3, 6 and 8 - "web + API + LLM" under the 2021 shape. Under 2025 that set covers three of ten
categories and silently skips A02 misconfiguration, A03 supply chain, A04 crypto, A08 integrity,
A09 logging and A10 exceptional conditions. If the map changes again, these lists change with it;
a scoped mode that no longer matches its name is a defect, not a shorthand.

`--ai` is split out because agent 8 is the only one that is expensive-and-conditional: it now covers
both the LLM Top 10 and the Agentic Applications Top 10, and it is the mode to reach for when the
change under review is a prompt, a tool definition or an agent loop.

**`--key-rotation`** closes the loop with `/secrets-audit`, which finds OVERDUE keys. Per provider:
generate the new key, update every `.env*` that referenced the old one (grep-find first, never blind
replace), restart consumers and verify traffic on the new key, then revoke the old one. Append the
event to `~/.agent/rotation-log.json`. Each destructive step needs explicit confirmation.

## Confidence

**8/10 default.** Zero-noise: every reported finding is verified and exploitable. Target FP ≤ 5%.
**2/10 comprehensive.** Surfaces tentative and theoretical risk; every finding carries its score.

| Score | Meaning |
|---|---|
| 1-2 | Theoretical pattern, no demonstrable exploit |
| 3-4 | Pattern present; exploitability depends on deployment assumptions |
| 5-6 | Likely exploitable by a motivated attacker |
| 7-8 | Demonstrably exploitable in the current configuration |
| 9-10 | Trivially exploitable; PoC included |

Score **exploitability here and now**, not generic CVSS. Two-sentence justification per finding.

### Hard exclusions (never findings)

Test fixtures with deliberately bad input; `.env.example` placeholders; docs showing exploits;
localhost-only debug endpoints with the auth gate intact; dev-mode logging that strips at build
(verify the strip); findings already marked WONT-FIX with an operator reason; advisories scoring < 7
in dev-only transitive deps; archived or disabled code paths; generated build artifacts; public test
keys (`pk_test_*`, `sk_test_*`) in test directories; `NODE_ENV === 'development'`-gated code; operator-allowlisted
commands behind a verified admin check; versions pinned by a documented decision; localhost SSRF
reaching an intentionally exposed service.

When in doubt, surface at low confidence rather than auto-fixing.

## Orchestration

**Applicability matrix.** `--comprehensive` is uncompromising: an applicable agent that did not run
is a coverage hole. Never skip to save budget - tighten the prompt instead. Legal skips only:

| Agent | Skip only iff |
|---|---|
| 1 Deps, 2 Secrets, 7 Config, 10 Logic, 17 Artifacts | never |
| 3 Server-side | no backend code at all |
| 4 Auth | no auth surface detected in Stage 1 |
| 5 Client-side | API-only repo, no client rendering surface |
| 6 API | no HTTP route surface |
| 8 AI/agentic | no LLM dep AND no MCP/tool-call/agent-loop signal AND no user text reaching a prompt (see `stacks.md`) |
| 9 Mobile | no `Info.plist`, `AndroidManifest.xml`, `*.xcodeproj/`, `app/build.gradle` |
| 11 Failure paths | never - every codebase has error paths |
| 12 Crypto | consumes vetted-library crypto end to end and ships none of its own |
| 13 Infra | no CI config, Dockerfile, IaC or k8s manifests |
| 14 Taint | never on a backend |
| 15 Regression tests | no fix landed this run |
| 16 Spec drift | no OpenAPI/Swagger spec and no spec-generating dep |

This matrix exists because a run on 2026-05-25 dispatched 6 of 17 agents on orchestrator judgment,
rationalized as "not applicable", without testing applicability. Judgment became spec.

**Coverage attestation.** Every SITREP states ecosystems detected, scanners missing, agents
applicable, dispatched and skipped with the precondition met per skip, and the resulting percentage.
"Skipped to save context" is not a legal entry - that is a defect in the agent prompt.

**Per-agent budget.** Prompt ≤ 600 tokens. Returned summary ≤ 200 tokens. Full findings ≤ 5,000
tokens written to `.sec-ship-reports/findings/agent-<N>.json`, never read by the orchestrator. After
each wave the orchestrator writes a ~50-token rolling counter and does not re-read prior summaries.
If a prompt approaches 600 tokens, tighten it before dispatching - padding at the prompt layer
becomes verbose returns becomes orchestrator bloat.

## Stages

**0 Initialize.** In a git repo, `gh` authenticated. Detect every ecosystem present - **read
`stacks.md`** and record detected stacks plus missing scanners. Capture sibling-repo state (report
only, never scan them). Check whether `/test-ship` or `/gh-ship` ran recently. Create the report file
per `reference.md`.

**0.5 Reconcile with prior audits - before any scanner runs.**

Read the newest reports in `.sec-ship-reports/` and `.sec-ship-history.json` FIRST. A finding the
operator has already seen and settled is noise the second time, and re-deriving it costs a full
scan. Classify every known finding before deciding what to scan:

| Prior state | Do now |
|---|---|
| VERIFIED-FIXED, and **no commit since has touched its file** | Do not re-scan it. Carry it forward as `still-fixed (unchanged since <sha>)`. |
| VERIFIED-FIXED, and **its file HAS changed since** | **Re-verify this one specifically.** This is the regression case and it is the entire reason to keep the record. |
| DEFERRED with an unexpired reason | Skip. Restate it in the SITREP as a one-liner; do not re-argue it. |
| DEFERRED, reason expired | Back in scope. Say that the deferral lapsed. |
| FALSE-POSITIVE | Suppress silently. If the same shape re-appears, raise the pattern's `false_positive_rate` rather than the finding. |
| BLOCKED | Re-check only if the architecture around it changed; otherwise carry forward. |
| Still-open | Carry forward with its original id, do not renumber. |

Establish the delta once: `git diff --name-only <sha-of-last-run>..HEAD`. That set is what actually
needs scanning plus the re-verify list above. **Findings keep their original `SEC-XXX` id across
runs** - a finding that changes id every run cannot be tracked or deferred.

Report the reconciliation up front so the run's scope is visible before it starts:

```
Reconciled with 2026-07-14 run (sha a1b2c3d)
  carried forward : 4 fixed (files unchanged)
  re-verifying    : 2 fixed (files changed since)
  skipping        : 3 deferred (unexpired), 5 false-positive
  new scope       : 37 files changed
```

If no prior report exists, say so - "no baseline, establishing one" - and scan in full.

**1 Attack surface.** Map what is exposed before scanning: HTTP entry points, auth boundaries,
untrusted-input flows, trust boundaries, external integrations and webhook receivers. Write
`.sec-ship-reports/attack-surface.md`. This is what makes Agents 3-6, 10, 11 and 14 targeted rather
than generic.

**2 Scan.** **Read `agents.md`**, then dispatch by wave. Parallel within a wave, sequential across.

**3 Triage.** Confidence-gate filter, then hard exclusions, then match against `patterns_observed`
for a known fix, then sort by category severity (RCE, auth bypass, injection first) and confidence.
Decide auto-fix (mechanical, well-understood) vs manual review (judgment) vs defer (with a reason a
human can act on).

**4 Fix.** Per candidate: read the surrounding code, apply the smallest correct fix at root cause,
re-run the specific scanner that found it, retry differently up to 3 times, then BLOCKED. On
verification dispatch Agent 15 for the regression test and advance the status.

**5 Validate.** Re-run the full suite and confirm no new findings. Run the regression tests. Rebuild
and re-scan artifacts if Agent 17 applies. Confirm the existing test suite still passes. Append to
history.

**6 SITREP.** Per the template in `reference.md`, including coverage attestation and "Suggested next".

## Definition of done

Complete when one holds: **clean** (re-scan returns nothing above gate); **triaged** (every
above-gate finding FIXED+VERIFIED or DEFERRED with an acknowledged reason); or **blocked** (≥3 failed
attempts, documented, escalated).

Never: silently drop a finding, lower confidence to dismiss one, or mask one by changing a test.

/sec-ship is an automated audit, not a substitute for human review before regulated-data releases.
