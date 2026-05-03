# Skill Auto-Suggest Protocol

**Reference standard for skill workflow chaining.** Every skill ends its SITREP with "Suggested next" so operator + Claude know what move comes after.

## Why this exists

The skill collection works best as **chains, not islands.** /sec-ship before /gh-ship before /monitor. /investigate before /incident. /test-ship before /sec-ship. Without explicit suggestions, operator has to remember which skill to fire next.

Auto-suggest pre-computes the next move based on:
- The skill's outcome (success/partial/blocked)
- Findings (e.g., /sec-ship found vulns → suggest fix workflow)
- Cross-skill awareness (e.g., /gh-ship just merged → suggest /monitor)

## The pattern

Every skill's SITREP ends with a `## Suggested next` block:

```markdown
## Suggested next

**Recommended:** /<skill-name> — <reason in one sentence>

**Alternatives:**
- /<other> — <when to pick this instead>
- /<other> — <when to pick this instead>

**Skip if:** <condition under which the operator should NOT chain into another skill>
```

### Examples

After successful /gh-ship:
```markdown
## Suggested next

**Recommended:** /monitor — verify the production deployment is healthy

**Alternatives:**
- /sec-ship — run a security audit on the just-shipped code
- /test-ship — coverage check on what just shipped

**Skip if:** the change was docs-only or this was a chore commit
```

After /sec-ship with findings deferred:
```markdown
## Suggested next

**Recommended:** none — review the deferred list with the operator before proceeding

**Alternatives:**
- /sec-ship --comprehensive — escalate to deep scan if more findings expected
- /redteam — active exploitation testing for the deferred findings to confirm severity

**Skip if:** all findings auto-fixed and SITREP shows clean state
```

After /investigate finishes:
```markdown
## Suggested next

**Recommended:** /gh-ship — ship the verified fix

**Alternatives:**
- /test-ship — write regression test before shipping (recommended for high-blast-radius fixes)
- /incident — promote to formal incident if user-facing impact confirmed

**Skip if:** the investigation was a no-op (couldn't reproduce, no fix needed)
```

## Decision matrix per skill

Each skill's documentation should include a "Suggested next" decision table:

| Skill outcome | Default suggestion | Why |
|---|---|---|
| /gh-ship: success + deploy verified | /monitor | confirm prod health |
| /gh-ship: partial (deploy unverified) | /monitor (manual) | investigate why deploy didn't verify |
| /gh-ship: blocked (CI fix loop failed) | /investigate | root-cause the unfixable failure |
| /sec-ship: clean | /test-ship if recent code changes | next gate in pipeline |
| /sec-ship: findings fixed | /gh-ship | ship the security fixes |
| /sec-ship: findings deferred | none — operator review | judgment call |
| /test-ship: passes | /sec-ship | next quality gate |
| /test-ship: failures fixed | /sec-ship | confirmed-clean → security check |
| /test-ship: BLOCKED | /investigate | unfixable failure needs deeper look |
| /investigate: fix found | /test-ship + /gh-ship | regression test then ship |
| /qatest: bug found | /investigate | root-cause |
| /monitor: anomaly | /investigate or /incident depending on severity | escalation ladder |
| /perf: regression | /investigate | find what changed |
| /deps: vulnerable patches available | /sec-ship | confirm fix landed |

## How Claude reads "Suggested next"

When a skill completes and its SITREP is in the conversation context, Claude SHOULD:

1. Note the suggested-next block exists
2. Surface to the operator: "I see /sec-ship recommended /monitor — should I run that?"
3. If operator confirms: invoke
4. If operator gives different direction: follow that, but mention the original suggestion was overridden so context is preserved

This is a soft chain, not a hard one. The recommendation is a HINT to the operator + Claude. Either can override.

## When NOT to auto-suggest

- Skill is operator-action-only (e.g., /smoketest is a quick check, not part of a chain)
- Skill failed catastrophically and rolled back (suggest manual review, not chaining)
- Skill explicitly delivered a "stop and think" outcome (e.g., /brainstorm asking for design choice)

## Application checklist

For any skill being audited or rewritten:

- [ ] Add a "Suggested next" subsection to the SITREP template
- [ ] Define the decision matrix (table above) for that skill's specific outcomes
- [ ] Document in DESIGN DECISIONS: WHY auto-suggest vs. silent completion
- [ ] Note in CRITICAL RULES: every SITREP ends with "Suggested next"

## Cross-skill chain visualization

The most common chains:

```
Coding cycle:
  /investigate → /test-ship → /sec-ship → /gh-ship → /monitor
                       ↓                                  ↓
                   /qatest                          /incident (if anomaly)

Maintenance:
  /deps → /sec-ship → /gh-ship → /monitor

Pre-launch:
  /test-ship → /qatest → /sec-ship → /perf → /a11y → /gh-ship → /monitor

Security incident:
  /incident → /investigate → /sec-ship → /test-ship → /gh-ship → /monitor

Content:
  /icp-from-repo → /prospect → /campaign → /copy → /gh-ship (publishes site)

Operations:
  /ops → /investigate → /incident → /gh-ship (rollback) → /monitor
```

These are guides, not gates. Operator can pick any starting point.

## Future: predictive suggestion based on history

Per the [Self-Improvement Protocol](./SELF_IMPROVEMENT_PROTOCOL.md), each skill's `.X-history.json` captures patterns. Future enhancement: suggested-next can read history to recommend based on what worked LAST time on this project. E.g., if last time /sec-ship ran on this project, the operator chained into /test-ship — suggest the same chain.

For now, the decision matrix above is static. Predictive enhancement is Phase-2.
