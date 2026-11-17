# Domain Language: GLOSSARY.md and decision records

**One source for a project's own vocabulary, so the operator and every agent use the same word for
the same thing.** Adopted 2026-10-30 from the `domain-modeling` skill in
[mattpocock/skills](https://github.com/mattpocock/skills) (MIT). The claim behind it is his and
unmeasured here: a shared language makes agents less verbose, names consistent, and code easier to
navigate. Treat it as a bet to be checked against real sessions, not a proven result.

## What goes in it

`GLOSSARY.md` at the repo root holds the terms that are specific to THIS project, one or two
sentences each, saying what the thing IS. Nothing else: no implementation detail, no spec, no rules,
no scratch notes. Rules belong in `CLAUDE.md`; decisions belong in the decision records.

```md
# {Project name}

{One or two sentences: what this project is and why it exists.}

## Language

**Freeze**:
The guard's refusal state after a policy trip: every later command is refused until restart.
_Avoid_: lockdown, kill, halt

## Relationships

- A **Freeze** ends a **Session**; it never ends the **Profile**

## Flagged ambiguities

- "session" meant both the browser session and the agent session. Resolved: **Session** is the
  browser one; the other is the **Agent run**.
```

**Rules for terms.**
1. **Be opinionated.** Where several words name one concept, pick one and list the rest under
   `_Avoid_`. The `_Avoid_` line is what does the work.
2. **Project terms only.** General programming words (timeout, retry, cache) never go in, however
   often the project uses them.
3. **Group under subheadings** once natural clusters appear; a flat list is fine until then.
4. **A repo with several distinct areas** may keep one `GLOSSARY.md` per area with a root
   `GLOSSARY-MAP.md` listing them and how they relate. Start with one file; split only when terms
   genuinely collide between areas.

## Who writes it, and when

**Created lazily, and only in a session the operator is part of.** No file exists until the first
term is actually resolved with the operator. No audit, sweep, background agent or
`/repo-bootstrap` run creates one, and no session seeds a glossary across repos.

| Skill | Role |
|---|---|
| `/brainstorm`, `/architecture-survey` (its hand-off), `/mdmp` | **Writers.** Challenge a term that conflicts with the glossary the moment it is used; propose one precise word for a fuzzy one; write the resolved term in right away, not batched at the end |
| `/test-ship`, `/docs`, `/docs-sync`, `/cleancode` and any skill naming things in a repo | **Readers.** If `GLOSSARY.md` exists, read it first and use its words in names, test titles, docs and reports. Never use a word it lists under `_Avoid_` |

**Cross-check against the code.** When the operator states how something works and the code
disagrees, say so before writing the term: the glossary records the real domain, not a wish.

## Decision records (ADRs)

Repos here keep decisions in `docs/adr/` or `docs/decisions/`. Use whichever the repo has, with its
numbering and template. **A repo with neither: say so and do not start one** (same rule as
`/gh-ship` Stage 2.5); record the decision in the backlog row instead.

Offer a record only when all three hold:
1. **Hard to reverse:** changing course later costs something real.
2. **Surprising without context:** a future reader would wonder why it was done this way.
3. **A real trade-off:** there were genuine alternatives and one was chosen for stated reasons.

A record can be one paragraph: the context, what was decided, why. Rejected alternatives only when
the rejection is not obvious. Records are never freshened later (CLAUDE.md 6.5); a changed decision
gets a new record that supersedes the old one.

## Tracking

`GLOSSARY.md` is tracked in git: the repo is its subject (CLAUDE.md 11.3). It is a live document, so
`/docs-sync` registers it, and a term naming a code symbol carries that symbol as an anchor.
