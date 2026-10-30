# /mdmp - the seven specialist lenses

Read at Step 4. **Every COA goes through every lens.** A lens with nothing to say writes
"no concerns, because <reason>" - explicit silence, so the record cannot be confused with a skip.

Each lens produces: **concerns** (what could go wrong), **requirements** (what this COA must include
to be viable), and a **verdict** (viable / viable-with-conditions / not viable, with the reason).

## 1. Engineering

Complexity, coupling, and what this constrains later. Does it fit the existing architecture or fight
it? What is the blast radius of getting it wrong? What does it make hard that is currently easy?
Migration path and reversibility. Whether the team can maintain it after the author moves on.
**The question that matters: what does this lock us into?**

## 2. Product

Does it serve the actual user need, or the need as we have described it to ourselves? Time to first
value. What ships in a week versus a quarter. Which users are excluded by this approach. Whether it
can be delivered incrementally or must land whole. **Question: what does the user get, and when?**

## 3. Security

Attack surface added. Trust boundaries crossed. Data classification and where it comes to rest.
AuthN/AuthZ implications. Third-party and supply-chain exposure (OWASP A03). Secrets handling.
Regulatory obligations triggered - HIPAA, PCI, GDPR, EAA. Blast radius of a compromise.
**Question: what does this let an attacker reach that they cannot reach today?**

## 4. QA / Testing

How is this verified? What cannot be tested, and what does that cost? Test data and fixtures needed.
Regression surface. Whether failures will be detectable in production or silent.
**Question: how would we know this is broken?**

## 5. Design / UX

The interaction model and whether it matches how the task is really done. Accessibility implications
(WCAG 2.2 AA - keyboard, announcement, target size, focus). Error and empty states. Consistency with
existing patterns, or a deliberate departure. Whether it adds a concept the user must learn.
**Question: what does the user have to understand for this to work?**

## 6. DevOps

Deploy mechanism and rollback. Observability - can it be monitored, and by what signals?
Infrastructure cost and scaling shape. Operational burden: who gets paged, and for what? Secrets and
config management. CI/CD impact including build time. **Question: what does this cost to operate at
3am?**

## 7. Risk

Failure modes ranked by likelihood x impact. Dependencies outside our control - vendors, teams,
approvals. What happens if a key assumption is wrong. Reversibility and its cost. Compliance and
contractual exposure. **The one-way doors.** **Question: what is the worst realistic outcome, and can
we get back?**

## Anti-patterns in lens application

- **The rubber-stamp lens.** Seven "looks fine" verdicts means the lenses were not applied. At least
  one lens should surface a real constraint on any non-trivial decision.
- **The lens that rejects everything.** Security saying "not viable" to all three COAs is not
  analysis; it means the criteria are wrong or a fourth COA is missing.
- **Copying concerns between COAs.** If a concern is identical across all COAs, it belongs in
  mission analysis as a constraint, not in the war-game.
- **Confusing a requirement with a concern.** "Needs rate limiting" is a requirement that makes the
  COA viable. "Rate limiting may not be sufficient under burst" is a concern.
