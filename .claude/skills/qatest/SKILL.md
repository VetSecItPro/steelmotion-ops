---
name: qatest
description: "Autonomous QA and UAT: discover every route, drive every interactive element and user flow in a real browser, test the API surface, check accessibility and responsive behaviour, score the result, auto-fix the safe findings and generate regression tests. The full pre-launch sweep, deeper than /smoketest, broader than any single audit skill."
when_to_use: 'Trigger phrases: "full QA", "test all pages", "UAT", "user acceptance testing", "QA sweep", "test everything", "quality check before shipping". Run before a launch or a major release. For a 2-minute sanity check use /smoketest; for one dimension use the specific skill.'
---

# /qatest - autonomous QA and UAT engine

**Spine. Survives compaction.** Detail beside it:

| File | Read at | Holds |
|---|---|---|
| `phases.md` | throughout | the discovery, drive, test, score, fix, verify phases in detail |
| `reference.md` | Phase 7+ | scoring, report, SITREP |

**Standards inherited:** [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) ·
[Steel Discipline](~/.claude/standards/STEEL_DISCIPLINE.md) ·
[Self-Improvement](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) ·
[Agent Orchestration](~/.claude/standards/AGENT_ORCHESTRATION.md) ·
[Status Updates](~/.claude/standards/STATUS_UPDATES.md) ·
[Skill Auto-Suggest](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) ·
[Context Management](~/.claude/standards/CONTEXT_MANAGEMENT.md) ·
[Sitrep Format](~/.claude/standards/SITREP_FORMAT.md) ·
[Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md)

## What it is, and what it is not

The **full QA sweep**: it drives the actual application in a real browser and exercises everything a
user would touch, then scores it. It is broader than any single skill and deeper than `/smoketest`.

It composes rather than duplicates. Where a dimension has its own skill, `/qatest` runs that skill's
logic (accessibility -> `/a11y`'s checks, performance -> `/perf`'s measurement, security headers ->
`/sec-ship`'s) rather than inventing a second version. Its unique value is **exercising the running
app end to end** - the interactions and journeys that only a driven browser reveals.

Browser driving uses the Playwright MCP tools (`browser_navigate`, `browser_click`, `browser_type`,
`browser_snapshot`, `browser_evaluate`, `browser_fill_form`, `browser_resize`, `browser_wait_for`,
`browser_console_messages`, `browser_network_requests`).

## Critical rules

1. **Drive the real app, do not read the source and imagine it.** A QA sweep that reasons about the
   code instead of exercising the browser is a code review, not QA. Click the button; watch what
   happens.
2. **Non-destructive against real data.** GET freely; for actions that mutate, use test accounts and
   test data, and clean up after. Never run a destructive flow against production data.
3. **Every interactive element gets driven.** Buttons, forms, links, menus, modals - if a user can
   touch it, QA touches it. A page that "loads fine" can have a dead button.
4. **Collect everything, do not stop on the first failure.** The value is the complete picture.
5. **Auto-fix only the unambiguously safe;** report the rest. A broken user flow is usually a real
   bug needing judgment, not a mechanical fix.
6. **A finding is reproduced, not inferred.** "This button does nothing" means you clicked it and
   nothing happened - with the console and network captured, not "the handler looks unwired".
7. **Regression tests for what was fixed**, so QA-found bugs do not silently return.

## Modes

```
/qatest                 full sweep, all phases, score + auto-fix + regression tests
/qatest --audit         drive and report only, fix nothing
/qatest --flows         user-journey testing only (signup, checkout, the critical paths)
/qatest --pages         page health + interactive elements, no deep journeys
/qatest --api           API surface only
/qatest --url <url>     QA a specific deployed URL rather than local
```

## Phases

| # | Phase | What |
|---|---|---|
| 0 | Pre-flight | start the app; confirm it is reachable; detect stack and routes |
| 1 | Discovery | enumerate every route and API endpoint from the app, not from memory |
| 2 | Page health | each route loads, 2xx + content marker, no console errors, headers present |
| 3 | Interactive elements | drive every button, form, link, menu, modal; capture what each does |
| 3.5 | User journeys | the critical flows end to end: signup -> value, checkout, auth lifecycle |
| 4 | API surface | each endpoint: auth, validation, happy path, error path (non-destructive) |
| 4.5 | Integrations | third-party health as the app sees it (payment test mode, email, etc.) |
| 5 | Accessibility | `/a11y`'s automated + keyboard pass on critical flows |
| 6 | Responsive | key breakpoints incl. 320px and 200% zoom |
| 6.5 | Performance | `/perf`'s baseline measurement on the key routes |
| 7 | Score | weighted across dimensions; the verdict |
| 8 | Auto-fix | safe findings only; re-verify each |
| 8.5 | Regression tests | for every fix and every confirmed flow bug |
| 9 | Validate | re-run the failed checks; confirm green |

Phases 3-9 are what a long run loses to compaction if not held here. **Phase 3.5 - driving the user
journeys - is the heart of QA and the thing no other skill does.**

## Definition of done

- Every route discovered from the app and health-checked (status + content)
- Every interactive element driven; every critical journey walked end to end
- API surface exercised non-destructively
- Accessibility, responsive and performance dimensions covered (via their skills)
- Score computed across dimensions with a clear pass/fail
- Safe findings fixed and re-verified; the rest reported with reproduction
- Regression tests added; report written; SITREP ends with "Suggested next"
