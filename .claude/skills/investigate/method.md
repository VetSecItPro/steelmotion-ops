# /investigate - the evidence-first method

## Phase 1: intake and reproduce

Get the **exact** failure, not the report of it. "It's broken" is a starting point, not evidence.
Establish: what was expected, what happened, the precise steps, the environment, when it started.

**Reproduce it.** A bug you cannot trigger on demand cannot be verified fixed - you would be guessing
that a change helped. If it is intermittent, the first job is to find the trigger: a specific input, a
race under load, a particular data shape, a time-of-day dependency. Do not proceed to fixing until you
can make it happen.

## Phase 2: evidence, before any theory

Gather what is actually happening:

- the full stack trace, read top to bottom - the real cause is often several frames from the crash
- logs around the failure, not just the error line
- the actual state (variable values, DB rows, request payload) at the point of failure - not the
  assumed state
- timing and ordering for anything concurrent or async
- **what changed** - recent commits, deploys, dependency updates, config changes, data migrations.
  "It worked yesterday" plus `git log` since yesterday is often the whole investigation

Resist forming the theory here. The point of this phase is to collect, not to conclude.

## Phase 3: pattern analysis

What does the evidence have in common? Does it fail for all inputs or a class? All users or some?
Since a specific change? Only in one environment? The pattern narrows the cause far more reliably than
intuition - "fails only for users created before the migration" points somewhere specific.

## Phase 4: hypothesis

State a **testable** theory of the mechanism, with a prediction: "the value is null because the
migration did not backfill existing rows; therefore users created before <date> will fail and users
created after will succeed." A hypothesis you cannot test is a guess dressed up.

## Phase 5: test the hypothesis

Prove or disprove it against reality - a targeted query, a log line, a minimal repro isolating the
suspected mechanism, a bisection (`git bisect`, or manually reverting the suspected change). **Confirm
the mechanism actually produces the failure.** A hypothesis that merely fits the symptoms is not
confirmed; many wrong theories fit the symptoms.

If disproven: record it (it narrows the space) and return to Phase 4 with what you learned. Do not
patch a hypothesis you just disproved into a fix.

## Phase 6: fix at root cause

The minimal correct change that addresses the confirmed mechanism. Trace the cause to its origin - if
the value was null, why? Fix *that*, not the place it crashed. Resist scope: a bug fix is not the
moment to refactor the surrounding code; that introduces new variables and new risk.

One change. If the fix requires several, make and verify them one at a time.

## Phase 7: verify and immunise

Re-run the **exact** reproduction from Phase 1 and confirm it now passes. Then write a regression
test that fails against the old code and passes against the fix - this is what stops the bug returning
silently in six months when someone refactors. A fix without a regression test is a fix with a
half-life.

## Deep-tier additions

When Standard stalls (intermittent, systemic, or three failed attempts):

- **Instrument.** Add logging or tracing at the suspected boundary; let the next occurrence produce
  evidence instead of guessing between occurrences.
- **Bisect.** `git bisect` between a known-good and known-bad commit finds the introducing change
  mechanically.
- **Audit the assumptions.** List what you believe to be true about the system and test each. Bugs
  that resist investigation usually hide behind a false assumption held so firmly it was never
  checked - "that function is pure", "that value is always set", "that only runs once".
- **State and timing.** For concurrency: what happens under interleaving, replay, or 10x load. For
  async: what the ordering actually is versus what it is assumed to be.
