# /docs - the five audit dimensions

Run as parallel agents. Each produces findings ranked stale-before-missing (a wrong doc misleads; a
missing one merely lacks).

## 1. README

The front door. Check: does it exist; is its last update far behind the last code change (a staleness
signal); does it cover what a new contributor needs - what the project is, quick start, setup, how to
run and test, project structure, key conventions. Does the quick-start actually work if run? A README
whose setup steps fail is a common and costly gap.

## 2. API / endpoints

For a library: are the public exports documented, with WHY not just signatures? For a service: is
every endpoint documented - method, auth, request/response shape, errors? Is there an OpenAPI/Swagger
spec, and does it match the implementation (drift here is a `/sec-ship` Agent 16 concern too)? Are the
examples valid against the real endpoint?

## 3. Components (for a UI project)

Are shared/public components documented with their props, states and usage? A Storybook or equivalent?
The bar is a consumer knowing how to use the component without reading its source - and knowing the
non-obvious constraints (this must be inside a provider, this is controlled-only).

## 4. Inline / WHY comments

The dimension where the WHY-over-WHAT rule bites hardest. Look for:

- **Non-obvious code with no explanation** - a magic constant, a workaround, an ordering that matters,
  a deliberate deviation from the obvious approach. These NEED a WHY comment.
- **Signature-echo comments to REMOVE** - `// increment i` over `i++`, a JSDoc restating the
  parameter names. These are net-negative; flag them for deletion.
- **Stale comments** - a comment describing behaviour the code no longer has. Worse than none.

The output is both additions (WHY where reasoning is hidden) and removals (noise that echoes the
code). Documentation coverage is not "more comments" - it is the right comments.

## 5. Architecture

Is there a document explaining how the pieces fit - the major modules, the data flow, the key
decisions and their rationale? For a non-trivial system this is what lets a new engineer orient
without reverse-engineering. Check it exists and matches the current structure; an architecture doc of
a previous design actively misleads. Diagrams (Mermaid, or the project's tool) where they clarify more
than prose.

## Ranking findings

Stale (misleads) > missing-on-a-critical-surface (README, public API) > missing-on-internal >
signature-echo-to-remove. Fix in that order; a wrong README hurts more than an undocumented internal
helper.
