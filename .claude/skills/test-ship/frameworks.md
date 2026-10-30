# /test-ship - framework detection and setup

Detect what the repo uses; do not impose a preference. Match new tests to the existing convention.

| Signal | Runner | Unit/integration | E2E |
|---|---|---|---|
| `vitest` in deps, `vitest.config.*` | Vitest | `*.test.ts` next to source or in `tests/` | Playwright |
| `jest` in deps, `jest.config.*` | Jest | `*.test.ts`, `__tests__/` | Playwright/Cypress |
| `@playwright/test` | Playwright | - | `e2e/*.spec.ts` |
| `cypress/` | Cypress | - | `cypress/e2e/` |
| `pytest`, `pyproject.toml [tool.pytest]` | pytest | `tests/test_*.py` | - |
| `go test` (any `*_test.go`) | Go testing | `*_test.go` beside source | - |
| `cargo test` | Rust | `#[cfg(test)]` mods, `tests/` | - |
| `*.bats`, `tests/bash/` | bats | `tests/*.bats` | - |
| `phpunit.xml` | PHPUnit | `tests/` | - |
| `vitest`+`@testing-library` | + component tests | render + interact + assert | - |

**Testcontainers / integration:** where a service talks to a real database or queue, an integration
test against a containerised instance (`testcontainers`) catches what a mocked unit test cannot -
a schema mismatch, a real query failure, a serialization break. A repo with `npm run test:integration`
means unit-only validation is insufficient; run both.

## Detecting the current coverage

```bash
# whatever the runner supports
vitest run --coverage    /  jest --coverage    /  pytest --cov    /  go test -cover ./...
```

Read the coverage report for **which files and branches are uncovered**, not just the headline
percentage. An 80% number with the auth middleware in the uncovered 20% is worse than a 60% number
with auth fully covered.

## Setup, when no framework exists

Add, in one PR:

1. the runner matched to the language (Vitest for Next.js/TS, pytest for Python, bats for shell)
2. a `test` (and `test:integration` where relevant) script in the manifest
3. a CI job that runs the suite and **gates merges** - no "did you run tests?" reviews
4. exactly one smoke test that proves the pipeline executes end to end

State in the PR that this is scaffolding; real tests follow by risk. Do not try to cover the codebase
in the setup PR.

## Framework conventions per language

| Language | Unit + integration | E2E | Infra |
|---|---|---|---|
| Next.js / TS | Vitest (`tests/*.test.ts`) | Playwright (`e2e/*.spec.ts`) | bats for scripts |
| Python | pytest (`tests/`) | optional integration suite | bats |
| Go | `go test` | - | - |
| Bash / infra | bats | - | bats |
