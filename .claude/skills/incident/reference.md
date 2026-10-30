# /incident - postmortem, timeline, SITREP

## Report / postmortem

`.incident-reports/INC-<YYYYMMDD-HHMM>.md`, written live during the incident and finalised at Stage 6.

```markdown
# Incident: <symptom>
**Severity:** SEV-<n>  |  **Status:** mitigated | resolved | monitoring
**Detected:** <ISO>  |  **Mitigated:** <ISO> (TTM <duration>)  |  **Resolved:** <ISO>
**Blast radius:** <who / what / how many>

## Timeline
| Time (ISO) | Action | Result |
|---|---|---|
| 14:02:11 | detected - user report "checkout 500s" | classified SEV-1 |
| 14:04:30 | rolled back deploy <sha> | service restored, TTM 2m19s |
| 14:11:00 | root cause confirmed: <mechanism> | |

## Root cause
<the mechanism, evidence-confirmed, traced to origin>

## Contributing factors
<what made it possible or worse: missing test, no alert, a fragile pattern>

## Fix
<permanent fix, and how it differs from the mitigation>
Regression test: <path> - fails on old, passes on new

## Action items
| Item | Owner | By |
|---|---|---|
| add alert on checkout error rate | | <date> |
| the coverage gap that let this ship | | <date> |
```

## Blameless

The postmortem names systems and mechanisms, never people. "The deploy lacked a smoke test on the
checkout path" - not "X forgot to test". A blameless postmortem gets honest data; a blameful one gets
defensiveness and hidden causes.

## History

`.incident-reports/history.json`: severity, TTM, root-cause class, and `patterns_observed` for
recurring incident shapes - so a repeat symptom starts Stage 2 with the last confirmed cause in hand.

## SITREP

Severity and current status first - mitigated or still bleeding is the only thing anyone wants to
know at a glance. Then TTM, then root cause, then the action items with dates. An incident SITREP that
buries "service is restored" under analysis has the priorities backwards.

### Suggested next

| Outcome | Recommend |
|---|---|
| Mitigated, fix pending approval | get approval, deploy, verify, then `/monitor` |
| Resolved | `/monitor` to confirm the golden signals held; complete the action items |
| Root cause was a coverage gap | `/test-ship` on that seam - it is an action item, do it now |
| Root cause was a dependency | `/deps` for the fixed version |
| Cannot mitigate, still down | escalate to a human; this is beyond autonomous response |

## Design notes

**Mitigate-first is the whole identity of the skill.** Debugging finds the right answer; incident
response gets users back. Conflating the two - insisting on the perfect fix while users are down - is
the most common and most damaging incident-response failure.

**Approval gate even under pressure.** The instinct at SEV-1 is to deploy fast and unilaterally. That
instinct causes the second, worse outage. The gate is most important exactly when it is most tempting
to skip.

**Timeline as you go.** Reconstructing timestamps after the fact produces a fiction. The timeline is
the postmortem's evidence and the handoff's context; it is written live or it is unreliable.

**Blameless or useless.** A postmortem that assigns blame teaches people to hide causes. One that
examines systems gets the honest mechanism, which is the only thing that prevents recurrence.
