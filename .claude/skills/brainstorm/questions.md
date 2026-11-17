# /brainstorm - the interview

## Map it as a decision tree

Every decision branches into the decisions that hang off it. The **frontier** is every decision
whose prerequisites are already settled: the questions that can be asked now without guessing at an
answer not yet heard. Each round asks the whole frontier, then waits.

Typical order of what settles first (a guide, not a script): the goal and what success looks like,
then scope (smallest useful version), then who uses it and how often, then constraints, then the
tricky cases, then how it meets other features.

## Look up before asking

Before a round goes out, everything a question would need that is a FACT is found: how the code
does it today, what the docs or decision records already settled, what a library supports, what the
backlog says was tried. Put the finding in the round as context ("Today `build_render` re-renders
every track because ..."), not as a question.

A lookup that is still running does not hold up the whole round: ask the questions that do not
depend on it now, and the dependent ones next round. A lookup that would touch more than about ten
files, or after two greps that missed, goes to a sub-agent (`sonnet`, `medium`, named `#<n> brainstorm lookup`) so the main context stays on the
conversation.

## Round format

```
Round 1. What I found: <one to three lines of facts from the repo, with file paths>

❓ **Q1 - <short title>**: <the question, with options A/B/C when they are bounded>

➡️ <recommended answer, and why in one line>

---

❓ **Q2 - <short title>**: <question>

➡️ <recommended answer>

Reply "yes" to take every recommendation, or answer by number.
```

- Word each question so "yes" accepts the recommendation.
- Multiple choice when the options are bounded; open-ended ("walk me through a typical run") only
  when they are not.
- Typically two to five questions a round. More than about seven means some of them depend on
  others: move those to the next round.
- If one question's answer could void the others (it challenges the premise), ask it alone this
  round and hold the rest.
- After each round, recompute the frontier: settled answers unblock the questions that hung off
  them. Never re-ask a settled decision.

## Language duty (`standards/DOMAIN_LANGUAGE.md`)

- A term that conflicts with `GLOSSARY.md`: say so in the next round ("the glossary defines X as
  ...; you seem to mean ...; which is it?").
- A fuzzy or overloaded word: propose one precise term, as a question with a recommendation.
- A term settled: write it into `GLOSSARY.md` right away, creating the file if this is the first
  one. The spec then uses the settled word.
- When the operator states how something works and the code disagrees, say so before writing it down.

## Stop rule

Stop when the frontier is empty: every decision the approaches depend on is settled or explicitly
parked ("decide during implementation" is a valid answer for a genuinely low-stakes choice). Then
state the shared understanding in a few lines and move to approaches. Do not act on it before the
operator confirms the summary.

More than about four rounds and still branching: the topic is bigger than `/brainstorm`; offer
`/mdmp`.
