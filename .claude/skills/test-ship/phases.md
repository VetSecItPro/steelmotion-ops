# /test-ship - phases in detail

## Phase 0-1: detect and audit

Detect the runner and current coverage (`frameworks.md`). Then audit for gaps by reading the code,
not just the coverage report - coverage tools count lines executed, not behaviours verified. A line
can be 100% covered by a test that asserts nothing meaningful about it.

Rank gaps by **silent-failure risk**:

1. **Auth and middleware seams** - a broken auth gate fails as a silent 401/302 storm or, worse, an
   open door. Highest priority, always.
2. **API route handlers** - each mutating handler needs: missing-auth -> 4xx, invalid-body -> 400,
   happy path -> expected shape, downstream-failure -> 5xx.
3. **Pure logic in `lib/`** - schemas, validators, parsers, decision functions. High ROI, easy targets.
4. **Templates and fixtures** - prove the rendered output contains the expected fields; do not trust
   the template engine to fail loudly.
5. **Critical-path E2E** - login -> primary action. A handful, grown only when a real regression escapes.

## Phase 2: prioritise

Take the operator's critical paths first, then the seam order above. A test suite is built by risk,
not alphabetically. If time is bounded, cover the auth seam and the top mutating handlers before
anything else - that is where an escaped bug hurts most.

## Phase 3: write real tests

For each target, cover behaviour:

- **happy path** - the expected input produces the expected output/effect
- **error path** - bad input, missing auth, downstream failure each handled correctly
- **boundary** - empty, null, max, the off-by-one, the concurrent case where it applies

**Prove each test can fail.** Run it against the unmodified code with the assertion inverted, or
against a deliberately broken version, and watch it go red - then correct it. A test written to pass
that was never seen to fail is testing the test, not the code.

Mock third-party SDKs at the boundary. Never mock your own router, handler or logic - that tests the
mock and proves nothing about the code.

## Phase 4: verify

Run the **full** suite, not just the new tests. Confirm: everything green, the new tests actually
exercise the target (flip the code, watch them fail, restore), and coverage moved where intended.
For services, run integration too - unit-green is not enough when a real database is involved.

## Phase 5: report and self-heal

If a new test is flaky, fix the cause (timing, shared state, order dependence) - do not accept a
flaky test into the suite; a flaky test trains people to ignore red. Report the coverage delta as a
count ("+22 tests, 1088 -> 1110 passing"), the seams now covered, and what remains with why.
