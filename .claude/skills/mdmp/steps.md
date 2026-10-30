# /mdmp - the seven steps in detail

## Step 1 - receipt of mission

State the ask in one paragraph, in your own words, and get it confirmed if ambiguous. Separate what
was asked from what was assumed. Name what is explicitly **out of scope** - an unbounded problem
cannot be decided.

## Step 2 - mission analysis

- **Constraints:** what cannot change (budget, deadline, existing contracts, regulatory floor,
  team size, tech the org has standardised on)
- **Assumptions:** what is believed but unverified. Each gets a validation method and a
  what-if-false. **An assumption without a test is a hope.**
- **Unknowns:** what must be discovered before deciding. If a critical unknown blocks the decision,
  say so and recommend spiking it rather than guessing through it
- **Decision criteria and weights:** set them NOW, before any COA exists. This is the single most
  important ordering rule in the process
- **Restated mission:** one sentence, testable

## Step 3 - COA development

Generate at least three genuinely distinct approaches (see the spine's rule). For each, state at
**equal depth** - an underdeveloped COA is a straw man and corrupts the comparison:

- the approach in two sentences
- what it requires (people, time, money, dependencies)
- what it explicitly does not do
- rough effort and time-to-value

Include "do nothing" whenever the status quo survives. Include one option the team would instinctively
reject.

## Step 4 - COA analysis (war-game)

Each COA through all seven lenses (`lenses.md`). Then war-game it: walk the COA forward through a
realistic sequence of events and ask what breaks. Specifically:

- What happens under 10x the expected load?
- What happens when the third party is down?
- What happens when the person who built it has left?
- What happens if the core assumption is false?
- What is the first thing that will go wrong in production?

Record failure modes as they surface. **A COA that survives war-gaming unchanged was war-gamed
too gently.**

## Step 5 - COA comparison

Score against the Step 2 criteria on the fixed weights. Every cell gets a one-sentence reason.
Compute weighted totals, then sanity-check: does the winner match intuition? If not, either the
weights are wrong or the intuition is - resolve it explicitly rather than quietly adjusting numbers.

Show the matrix. A hidden calculation is not a decision anyone can audit.

## Step 6 - COA approval

Recommend one, with:

- **confidence** (high / medium / low) and why
- **the trigger that would change it** - the specific fact that would flip the recommendation
- **what is given up** by not choosing the runner-up
- risks accepted, and their mitigations

Present for approval. Do not proceed to Step 7 on a decision the operator has not made.

## Step 7 - orders production

An executable plan: phases with entry and exit criteria, the first three concrete tasks, who or what
does each, verification per phase, and the rollback path. No placeholders.

Then write the decision record (`reference.md`) including rejected COAs and why. Hand off execution
to `/subagent-dev`.

## Step 8 - lens satisfaction check

Before closing: confirm every lens produced a verdict for every COA, every assumption has a test,
every score has a reason, and the rejected options are recorded. A gap here means the process ran but
did not do its job.
