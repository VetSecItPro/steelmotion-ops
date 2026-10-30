# /sec-ship - reference

History schema, report format, SITREP template, and the reasoning behind the design. Read when
initializing the report (Stage 0.6), writing the SITREP (Stage 6), or resuming an interrupted run.

## Report persistence

`.sec-ship-reports/<YYYYMMDD-HHMMSS>.md` is the source of truth. Updated continuously so it survives
compaction and session loss. Append-only: re-runs ADD under a new run-id header, never overwrite.

Initialize at Stage 0.6:

```markdown
# Sec-Ship Report - <repo>
**Run started:** <ISO>
**Mode:** <daily|comprehensive|audit|diff|infra|code|supply-chain|owasp|ai>  (auto-selected if no flag given - say why)
**Confidence gate:** <8|2>
**Ecosystems detected:** <from stacks.md>
**Scanners available / missing:** <from stacks.md>

## Findings (rolling - appended as agents complete)
## Fix log (rolling - appended as fixes verified)
## Deferred (with reasons)
## SITREP (populated at end)
```

### Status transitions

```
FOUND -> FIXING -> VERIFIED-FIXED   success
FOUND -> FIXING -> BLOCKED          3-strike
FOUND -> DEFERRED                   judgment, with reason
FOUND -> FALSE-POSITIVE             after triage; logged to history
```

### Finding identity across runs

`SEC-XXX` ids are assigned once and never reused or renumbered. A finding carries its id from FOUND
through to VERIFIED-FIXED and beyond, so that a deferral, a suppression or a regression can all
refer to the same thing months apart. Store alongside each id the file path and the commit sha at
which it was last verified - that pair is what Stage 0.5 uses to decide whether a fixed finding needs
re-checking or can be carried forward untouched.

```json
"findings": {
  "SEC-014": {
    "status": "VERIFIED-FIXED",
    "path": "services/api/routes/session.ts",
    "verified_at_sha": "a1b2c3d",
    "verified_on": "2026-07-14",
    "regression_test": "tests/security/session-fixation.test.ts"
  }
}
```

If `git diff --name-only <verified_at_sha>..HEAD` does not contain `path`, the finding is still
fixed by construction and needs no scanner run. That single comparison is what stops every run
re-litigating settled work.

### Resume protocol

On invocation: read the newest `.sec-ship-reports/*.md` for this project. If its status is
`in-progress` and it is under an hour old, resume from the last logged step. Otherwise start fresh.

## Self-improvement: `.sec-ship-history.json`

Read at Stage 0.5 (reconciliation), appended at Stage 5. Auto-gitignored.

```json
{
  "patterns_observed": {
    "<vuln-shape-key>": {
      "first_seen": "2026-05-03",
      "count": 3,
      "fix_known": true,
      "last_successful_fix": "parameterize via prepared statements",
      "false_positive_rate": 0.02,
      "scanner_that_found_it": "semgrep p/owasp-top-ten"
    }
  },
  "deferred_with_reason": {
    "<finding-id>": {
      "deferred_at": "ISO",
      "reason": "...",
      "reviewer": "operator",
      "expires_at": "ISO"
    }
  }
}
```

Known shape whose prior fix worked: try that FIRST. Unexpired `deferred_with_reason`: do not
re-flag, re-affirm it in the report instead.

## SITREP template

```
===============================================================
/sec-ship - <success | partial | blocked>
===============================================================

Run
   Repo:        <name>
   Mode:        <daily | comprehensive | audit | diff>
   Gate:        <8 | 2>
   Duration:    <Xm Ys>
   Run ID:      <timestamp>

Reconciliation (see SKILL.md Stage 0.5)
   Prior run:        <date, sha> | "none - baseline established"
   Carried forward:  <N> fixed, files unchanged
   Re-verified:      <N> fixed whose files changed  -> <regressed: N>
   Skipped:          <N> deferred unexpired, <N> false-positive
   New scope:        <N> files changed since the prior run

Coverage (MANDATORY - see SKILL.md coverage attestation)
   Ecosystems detected: <list>
   Scanners missing:    <list, with what it cost>
   Agents applicable:   <N> of 17
   Agents dispatched:   <M>
   Agents skipped:      <X>
     Agent <K> (<name>): <applicability-matrix precondition that was met>
   Coverage: <M>/<N> applicable agents executed (<pct>%)

Findings
   FOUND / VERIFIED-FIXED / DEFERRED / BLOCKED / FALSE-POSITIVE

Fixes applied (top 5 by impact)
   - <SEC-XXX> - <description> [confidence N/10]
     Fix: <one line>   Verified: scanner re-run clean
     Regression test: <path>

Deferred (with reasons)
   - <SEC-YYY> - <reason> - operator review: <yes|already-acked>

Blocked (3-strike)
   - <SEC-ZZZ> - attempts: <list> - recommendation: <architectural change>

Sibling repos in workspace
   <name>: <last run | never run>

Self-improvement
   patterns_observed total / new this run / known recurred

Reports
   .sec-ship-reports/<run-id>.md, findings/agent-*.json, attack-surface.md
===============================================================
```

### Suggested next

| Outcome | Recommend | Why |
|---|---|---|
| Clean | `/test-ship` if code changed recently | next quality gate |
| Fixed + verified | `/gh-ship` | ship the fixes |
| Deferred | none - operator reviews the list | judgment call |
| Blocked | `/investigate` | architectural |
| Comprehensive, many low-confidence | `/sec-ship --diff` | narrow to recent change |

## Design decisions (why it is built this way)

**AI judgment over fix tables.** Real CVEs do not fit regex rows. Scanner output is data; the
reasoning is the skill. Agent briefs give structure - what to look at - not verdicts.

**Seventeen agents.** Specialisation beats generality; a focused injection reviewer is sharper than
a general pass. The cost is orchestration discipline, which is what the applicability matrix and
coverage attestation buy back.

**Confidence gates.** False-positive fatigue is the top reason teams switch security tooling off.
8/10 daily produces reports worth trusting; 2/10 is the periodic deep dive.

**Per-finding regression tests.** Without them the same vulnerability returns in six months under a
refactor. Agent 15 makes regressions observable.

**Per-project history.** Fix patterns recur. Without a record every run rediscovers from scratch -
and worse, re-litigates findings the operator already settled. Stage 0.5 turns the record into
scope: a fixed finding whose file has not changed since it was verified is still fixed by
construction and costs nothing to confirm; one whose file HAS changed is the regression case and is
the only thing worth re-scanning.

**Hard exclusions.** Without them the report fills with fixture noise and the operator stops reading.

**Multi-repo report-only.** One repo per invocation; siblings surfaced so "scanned one, forgot the
rest" cannot happen quietly.

**Supporting files rather than one document.** Claude Code re-attaches only the first 5,000 tokens of
a skill after compaction, with a 25,000-token budget shared across all invoked skills. The previous
single-file version was 9,419 tokens with its agent briefs starting at ~5,094 - so on long runs the
entire fan-out definition was dropped, which matches the 2026-05-25 incident where 6 of 17 agents
dispatched. The spine now fits inside the budget and the detail is read on demand.

## Related skills

**Feeds from:** `/test-ship` (fixes should not break tests), `/deps` (surfaces advisories).
**Feeds into:** `/gh-ship` (ship verified fixes), `/monitor` (post-deploy).
**Pairs with:** `/redteam` (active exploitation; multi-step chain analysis lives there),
`/compliance` (regulatory frameworks).

## Disclaimer

/sec-ship is a high-quality automated audit. It is NOT a substitute for periodic human security
review by qualified personnel, particularly before releases handling regulated data (HIPAA, PCI-DSS,
GDPR special categories). Use it as the day-to-day gate; supplement with human review quarterly and
pre-launch.
