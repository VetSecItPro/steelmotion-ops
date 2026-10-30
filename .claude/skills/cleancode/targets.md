# /cleancode - what to look for, and how to prove it safe

Every candidate must be **proven** safe before it is touched. The proof method is in each section.

## Dead code

- **Unused exports / functions / variables:** the language's own tool first (`ts-prune`,
  `knip`, `eslint no-unused-vars`, `vulture` for Python, `deadcode` for Go). THEN grep for dynamic
  references the tool cannot see: string-based lookups, dynamic imports, framework conventions
  (a Next.js `page.tsx` is "unused" to a static analyser but is a route), config references, test-only
  uses. Only what survives both checks is dead.
- **Unreachable branches:** code after a return, conditions that cannot be true, feature flags
  permanently off. Confirm the condition genuinely cannot occur.
- **Commented-out code:** delete it - git is the archive. Exception: a commented block with a WHY that
  explains a non-obvious decision stays.
- **Unused dependencies:** `depcheck`/`knip`, then confirm nothing imports it dynamically or via a
  config. An unused dep is weight and attack surface (ties to `/deps`).

## Duplication

- Genuine copy-paste that will change together -> extract a shared function/component.
- **NOT** two things that merely look similar today but model different concepts and will diverge -
  premature de-duplication couples things that should stay separate, which is worse debt than the
  duplication. The test: would a change to one always require the same change to the other? Only then
  is it real duplication.

## Complexity

- Functions doing too much (high cyclomatic complexity, deep nesting, many parameters). Split by
  responsibility, behind tests.
- Deeply nested conditionals -> early returns, guard clauses.
- **Only where it genuinely reduces the burden of understanding.** A complex function that is complex
  because the problem is complex, and is well-tested and commented, is not a target.

## Proving safety before touching

1. The touched code has test coverage. If not, get it (`/test-ship`) before refactoring, or leave it.
2. Run the full suite - green baseline.
3. Make the change.
4. Run the full suite - still green, and the touched behaviour is exercised by a test that would have
   caught a regression.
5. Build - green.

If any step cannot be satisfied, the candidate is reported, not changed. "I am fairly sure this is
safe" is not the bar.

## Anti-targets - do not touch

- Working, tested, readable code that is merely not how you would write it
- A pattern with a WHY comment explaining a deliberate choice
- Generated code
- Vendored code
- Anything where the test coverage is too thin to catch a regression and cannot cheaply be added
