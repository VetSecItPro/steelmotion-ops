# /smoketest - the nine layers

Detect the stack first (read the manifest's scripts); run the real command, not an assumed one. A
layer whose tool the stack does not have is marked N/A, not failed.

| # | Layer | Command (illustrative - use the project's) | Severity | Auto-fix |
|---|---|---|---|---|
| 1 | **Type check** | `tsc --noEmit` / `mypy` / `go vet` | HIGH - blocks build | missing imports, unused vars, obvious type fixes |
| 2 | **Build** | the project's build (`next build`, `vite build`, `go build`, `cargo build`) | HIGH | rarely; usually surfaces a real error to report |
| 3 | **Lint** | `eslint` / `ruff` / `golangci-lint` | LOW-MED | `--fix` the safe rules |
| 4 | **Unit tests** | the fast unit suite only (`vitest run`, `pytest -m 'not slow'`) | HIGH | no - a failing test is reported, never "fixed" by editing the test |
| 5 | **Page probes** | GET the key routes on a local/preview URL; expect 2xx and a content marker | HIGH if a critical route is down | no |
| 6 | **Security headers** | check CSP, HSTS, X-Frame-Options, X-Content-Type-Options on a probe | MEDIUM | add missing headers if the config is obvious |
| 7 | **Stray server logs** | `grep -rn 'console\.log' server code` (not client, not tests) | LOW | remove obvious debug logs |
| 8 | **Env var validation** | referenced `process.env.X` vs what is defined; missing criticals | HIGH if critical, else MED | no - never invent a value |
| 9 | **Dependency advisories** | `npm/pnpm audit`, `pip-audit`, etc. - the quick version | MED-HIGH by score | `audit fix` for in-range only |

## Per-layer notes

- **Layer 4 runs the FAST suite only.** A full integration or E2E suite is not a smoke test - it
  belongs to `/test-ship` or `/qatest`. Run unit; note if integration is deferred.
- **Layer 5 needs a running target.** If no local or preview server is up, start the dev server or
  mark the layer deferred - do not skip it silently.
- **Layer 6-9 overlap `/sec-ship`.** They are the shallow version. A finding here is a signal to run
  `/sec-ship --diff` for the real assessment, not a complete security verdict.
- **Auto-fix then re-verify.** After fixing a layer's safe findings, re-run that layer to confirm the
  fix held and introduced nothing new. An unverified fix is not a fix.

## What does NOT belong here

Full E2E, deep security scanning, accessibility auditing, performance profiling, load testing. Each
has its own skill. Smoketest stays under ~3 minutes by refusing everything that would make it slower;
its value is that it is cheap enough to run every single time.
