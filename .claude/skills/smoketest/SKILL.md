---
name: smoketest
description: "Fast pre-ship sanity check: run every cheap mechanical layer (types, build, lint, unit tests, page probes, headers, stray logs, env vars, dep advisories), collect all findings without stopping on the first failure, auto-fix the safe ones, and report. ~2-3 minutes. The quick gate, not a deep audit."
when_to_use: 'Trigger phrases: "smoke test", "quick sanity check", "does it still work", "quick check before I ship", "sanity check". Run after a change and before /gh-ship. For depth use /sec-ship, /test-ship, /qatest instead.'
---

# /smoketest - fast pre-ship sanity check

**Spine. Survives compaction. This skill is small enough to fit almost entirely here** - only the
per-layer detail lives beside it.

| File | Read at | Holds |
|---|---|---|
| `layers.md` | Phase 2 | the nine scan layers, what each runs, per stack |

**Standards inherited:** [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) ·
[Steel Discipline](~/.claude/standards/STEEL_DISCIPLINE.md) ·
[Status Updates](~/.claude/standards/STATUS_UPDATES.md) ·
[Skill Auto-Suggest](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) ·
[Sitrep Format](~/.claude/standards/SITREP_FORMAT.md) ·
[Context Management](~/.claude/standards/CONTEXT_MANAGEMENT.md)

## What it is

The cheap, fast gate: mechanical checks that catch the obvious breakage before you ship. ~2-3 minutes.
It is deliberately shallow - it is not a substitute for `/sec-ship` (real security), `/test-ship`
(coverage), or `/qatest` (full QA). It is what you run every time, so the deep skills are needed less.

## Rules

1. **Run every layer; do not stop on the first failure.** The point is a complete picture of what is
   broken, not the first thing that breaks. Collect all findings, then report.
2. **Auto-fix only the unambiguously safe.** A missing import, a lint-fixable style issue, an unused
   variable - yes. Anything requiring judgment - no; report it for a human.
3. **Detect the stack; run the real commands.** Read `package.json` scripts (or the language
   equivalent); do not assume `npm run build` exists.
4. **Checkpoint after each layer.** Write findings to the report file as each layer completes, so a
   compaction or interruption loses at most one layer.
5. **Fast means fast.** If a layer would take more than ~30s (a full E2E suite, a deep scan), it does
   not belong here - defer it to the deep skill and note it.

## Modes

```
/smoketest              all nine layers, auto-fix safe, report
/smoketest --no-fix     scan and report only
/smoketest --changed    only layers relevant to what changed since the last commit
```

## The nine layers (detail in `layers.md`)

1. Type check · 2. Build · 3. Lint · 4. Unit tests · 5. Page probes · 6. Security headers ·
7. Stray server-side logs · 8. Env var validation · 9. Dependency advisories.

Each layer: run it, collect findings with a severity, mark whether each is safely auto-fixable. HIGH =
blocks the build or the deploy (type error, build fail, failing test). MEDIUM = should fix (missing
header, dep advisory). LOW = hygiene (a stray log, an unused var).

## Definition of done

- All nine applicable layers run (or marked N/A for the stack), none skipped on an earlier failure
- Safe findings auto-fixed and re-verified; the rest reported with severity
- Report written, checkpointed per layer
- A clear pass/fail: any HIGH unresolved = fail. SITREP ends with "Suggested next"

## SITREP

```
/smoketest - <PASS | FAIL> - <n> findings (<h> high, <m> med, <l> low), <k> auto-fixed

Layer results
  1 Types    PASS      6 Headers   2 findings (med)
  2 Build    PASS      7 Logs      1 auto-fixed
  3 Lint     3 fixed   8 Env       PASS
  4 Tests    PASS      9 Deps      1 advisory (high) - <pkg>
  5 Probes   PASS

Unresolved (blocks ship): <the HIGH findings, or "none">
Report: .smoketest-reports/SMOKE-<id>.md
```

### Suggested next

| Outcome | Recommend |
|---|---|
| PASS | `/gh-ship` |
| FAIL on types/build/tests | fix the HIGHs; re-run `/smoketest --changed` |
| Dep advisory | `/deps --security` |
| Header/security findings | `/sec-ship --diff` for the real check |
| Wanting more than a smoke test | `/qatest` (QA) or `/test-ship` (coverage) |
