# /incident - response stages

Read from Stage 0. Every action gets an ISO-8601 timestamp written to the timeline as it happens -
not reconstructed later.

## Stage 0 - detect and classify

- What is the observed symptom, from whom (user report, alert, monitor)?
- **Classify severity now** (see spine). When unsure, classify UP - a SEV-2 handled as SEV-1 wastes
  some urgency; a SEV-1 handled as SEV-2 leaves users down.
- Blast radius: which users, which surfaces, how many. "Everyone" and "all endpoints" is a different
  incident from "one feature for EU users".
- Start the timeline. First entry: detection time and source.
- Reachability check: is production observability actually reachable (APM, logs, cluster)? If not, say
  so - you are flying with instruments down and mitigation gets more conservative.

## Stage 1 - MITIGATE (the stage that matters most)

**Restore service before understanding it.** Options, fastest-safe first:

- **Rollback** the last deploy - if the incident began at a deploy, this is usually the answer and the
  fastest one. Confirm the rollback target is safe across any intervening migration.
- **Feature-flag off** the broken feature, if it is flagged.
- **Scale up / restart** if the symptom is saturation or a wedged process (a wedged pod, an exhausted
  pool).
- **Failover** to a healthy replica or region if one exists.

Record time-to-mitigate. A mitigation that itself risks data (a rollback that would undo a migration
holding new rows) is a human-decision trigger - ask.

If the incident cannot be mitigated without the root-cause fix (rare), say so explicitly and move to
Stage 2 with that noted - the clock is now on the fix, not on a workaround.

## Stage 2 - diagnose

Evidence first, exactly as `/investigate` Phase 2, but under time pressure:

- the error, the stack trace read fully, the logs around it
- what changed - the deploy, the config, the data migration, the dependency, the traffic pattern.
  Most incidents start at a change; `git log` and the deploy history since "last known good" is the
  first place to look
- the golden signals from the APM: did latency, error rate, traffic or saturation move, and when
- the actual state, not the assumed state

**Deep reasoning is non-negotiable here** - a wrong root cause leads to a fix that does not hold and a
recurrence. Confirm the mechanism; do not pattern-match under pressure.

## Stage 3 - fix

The correct fix for the confirmed cause, on a local or branch environment, one change at a time. Not
a refactor, not "while we're here" - the minimal change that addresses the mechanism. 3 attempts per
approach; revert each failure before the next. After 3 failures the model of the cause is wrong -
return to Stage 2.

## Stage 4 - verify

Reproduce the original failure, confirm the fix resolves it. A fix that "should work" but was not
tested against the actual failure is a guess, and guesses in incidents cause the second outage.

## Stage 5 - deploy (approval-gated)

Present the fix, its verification, and the risk. **Ask.** Deploy to production only on explicit
approval, then verify in production - the symptom is actually gone, the golden signals are back to
baseline, no new errors. Mitigation from Stage 1 (a flag, a scaled-up replica) is unwound only after
the permanent fix is confirmed live.

## Stage 6 - postmortem

Blameless. Written even for SEV-4. See `reference.md`. The regression test is part of this stage, not
optional - it is the difference between learning from the incident and repeating it.
