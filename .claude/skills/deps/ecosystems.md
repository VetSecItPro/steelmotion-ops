# /deps - per-ecosystem audit and update commands

Detect every ecosystem present (recursively, excluding vendored trees), then use that ecosystem's
own tooling. This mirrors `/sec-ship`'s `stacks.md` so the two skills agree on what "audit
dependencies" means. If a native auditor is absent, fall back to `osv-scanner` and say so.

| Detect | Ecosystem | Audit | Update | Lockfile |
|---|---|---|---|---|
| `package-lock.json` | npm | `npm audit` | `npm update`, `npm i pkg@latest` | `package-lock.json` |
| `pnpm-lock.yaml` | pnpm | `pnpm audit` | `pnpm update`, `pnpm up pkg@latest` | `pnpm-lock.yaml` |
| `yarn.lock` | yarn | `yarn npm audit` (berry) / `yarn audit` (v1) | `yarn up pkg` | `yarn.lock` |
| `bun.lockb` | bun | `bun audit` else `osv-scanner` | `bun update` | `bun.lockb` |
| `requirements.txt` | pip | `pip-audit` | `pip install -U`, or edit + reinstall | pin file |
| `poetry.lock` | poetry | `pip-audit` on export | `poetry update`, `poetry add pkg@latest` | `poetry.lock` |
| `uv.lock` | uv | `uv pip audit` else `osv-scanner` | `uv lock --upgrade` | `uv.lock` |
| `go.mod` | Go | `govulncheck ./...` | `go get -u`, `go get pkg@latest` | `go.sum` |
| `Cargo.toml` | Rust | `cargo audit` | `cargo update`, `cargo upgrade` (edit) | `Cargo.lock` |
| `composer.json` | PHP | `composer audit` | `composer update pkg` | `composer.lock` |
| `Gemfile.lock` | Ruby | `bundler-audit check --update` | `bundle update pkg` | `Gemfile.lock` |
| `pom.xml` | Maven | `mvn ...dependency-check` | `mvn versions:use-latest-releases` | n/a (declared) |
| `build.gradle` | Gradle | `gradle dependencyCheckAnalyze` | version catalog / `gradle` | n/a |
| `*.csproj` | .NET | `dotnet list package --vulnerable` | `dotnet add package` | n/a |
| `mix.exs` | Elixir | `mix deps.audit` | `mix deps.update pkg` | `mix.lock` |

## Cross-ecosystem, always available

- `osv-scanner -r .` - advisories across every ecosystem above; the fallback when a native auditor is
  missing
- `syft` then `grype` - SBOM, then vulnerabilities against it; the strongest evidence for A03 and the
  right tool when the question is "what is actually in the built artifact"
- `socket.dev` - behavioural signal (unexpected install scripts, network access, obfuscation) that a
  CVE database will not show; the way typosquats and compromised releases surface before a CVE exists

## Severity and reachability

A CVE score is not the whole story - **reachability is.** A critical in a code path the app never
calls is lower real risk than a high in the request path. Where the tooling supports it
(`govulncheck`, `osv-scanner` with call analysis), prefer the reachability-aware result. Where it does
not, note that the score is presence-based, not reachability-based.

Dev-only dependencies still run in CI, which holds secrets - do not dismiss a dev-dep advisory as
harmless without checking what CI exposes.

## Reading a major's changelog

Before a major upgrade, find the breaking-change list: the package's `CHANGELOG.md`, its GitHub
releases, or a migration guide. Extract what applies to how the repo uses the package - most breaking
changes touch APIs a given project does not call. Fix those, then let the test suite catch the rest.
Guessing the changes from red tests is slower and misses behaviour changes that do not throw.

## Unused and duplicate dependencies

- **Unused:** `depcheck` (Node), or grep the import surface. A dependency nothing imports is
  attack surface and weight with no benefit - remove it, run tests, commit.
- **Duplicates:** the same package at two versions in one lockfile bloats the bundle and can cause
  subtle bugs (two React instances, two date libraries). `npm dedupe` / `pnpm dedupe`, or resolve the
  conflicting peer requirement.
