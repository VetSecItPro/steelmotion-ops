# /sec-ship - ecosystem detection and scanner map

Read this at Stage 0.2. Do not guess a tool for a language; look it up here.

**The rule when a tool is missing.** Detect what is installed (`command -v <tool>`). If the
ecosystem's native auditor is absent, say so explicitly in the SITREP and fall back to
`semgrep` plus reading the code. **Never skip a language silently** - "no scanner installed" is a
coverage note the operator needs, not a reason the language is clean. A missing tool downgrades
confidence; it does not remove the agent.

**Multiple ecosystems in one repo is normal.** A Next.js app with a Python worker, Terraform and a
Dockerfile is four rows below, not one. Detect all of them; run each row's tools.

**Detect recursively, not just at the repo root.** This is the difference between a real audit and a
shallow one, and it was measured: a root-only scan of a monorepo on this machine found
`package.json` and a Dockerfile, and missed **688 Terraform files, 66 nested `package.json`, and 35
of 36 Dockerfiles**. Another repo's entire Python toolchain sits at `tools/requirements.txt` and
would have registered as "no Python".

```bash
# per signature, e.g.
find . -name 'go.mod' -not -path '*/node_modules/*' -not -path '*/.git/*' \
       -not -path '*/vendor/*' -not -path '*/.claude/worktrees/*'
```

Exclude `node_modules/`, `vendor/`, `.git/`, `dist/`, `build/`, and worktree/checkout copies -
scanning a vendored dependency tree produces findings you cannot act on and inflates the run.

**The exclusions are not optional hygiene; without them the ecosystem detection is wrong.** Measured
on two real repos, recursive detection with and without the exclusion list:

| Signal | Raw hits | After exclusions | Verdict |
|---|---|---|---|
| `yarn.lock` | 11 | **0** | phantom - all vendored |
| `AndroidManifest.xml` | 4 | **0** | phantom - would have run Agent 9 on a repo with no mobile |
| `.gitlab-ci.yml` | 8 | **0** | phantom |
| `Package.swift` | 2 | **0** | phantom |
| `Cargo.toml` | 1 | **1** | real |
| `package-lock.json` | 48 | **12** | real, and see below |

Four ecosystems would have been invented out of other people's dependency trees. Every phantom
costs a scanner run, pollutes the coverage attestation, and produces findings in code the operator
does not own.

**When two lockfiles coexist, that is itself an A03 finding.** The repo above carries 12 real
`package-lock.json` alongside a root `pnpm-lock.yaml`. Ask which is authoritative, whether CI
installs from the one that was audited, and whether the other is stale. A lockfile nobody audits is
a supply-chain gap, not a formatting quirk.

**Each detected location is its own unit.** `services/api/package.json` and
`services/worker/pyproject.toml` are two ecosystems with two lockfiles and two audit runs. Report
per-location, not per-repo; "the repo has a CVE" is not actionable, "`services/api` has a reachable
CVE in `lib-x@1.2` " is.

## Detection to scanner map

| Detect | Ecosystem | SCA / advisories | SAST | Notes |
|---|---|---|---|---|
| `package.json` + `package-lock.json` | Node (npm) | `npm audit --json` | `semgrep p/javascript`, `eslint-plugin-security` | read deps for framework hint |
| `pnpm-lock.yaml` | Node (pnpm) | `pnpm audit --json` | same as npm | `pnpm audit` differs from npm's output shape |
| `yarn.lock` | Node (yarn) | `yarn npm audit` (berry) / `yarn audit` (v1) | same as npm | check yarn major first |
| `bun.lockb` | Node (bun) | `bun audit` if present, else `osv-scanner` | same as npm | newest, thinnest tooling |
| `requirements.txt` | Python (pip) | `pip-audit` | `semgrep p/python`, `bandit -r .` | |
| `poetry.lock` | Python (poetry) | `poetry audit` or `pip-audit -r <export>` | same as pip | export first if needed |
| `uv.lock` | Python (uv) | `uv pip audit` if present, else `osv-scanner` | same as pip | |
| `go.mod` | Go | `govulncheck ./...` | `gosec ./...`, `semgrep p/golang` | govulncheck is reachability-aware |
| `Cargo.toml` | Rust | `cargo audit` | `cargo clippy`, `semgrep p/rust` | |
| `composer.json` | PHP | `composer audit` | `psalm --taint-analysis`, `semgrep p/php` | psalm taint mode is the strong one |
| `Gemfile.lock` | Ruby | `bundler-audit check --update` | `brakeman` (Rails), `semgrep p/ruby` | brakeman only for Rails |
| `pom.xml` | Java (Maven) | `mvn org.owasp:dependency-check-maven:check` | `semgrep p/java`, CodeQL if available | dependency-check is slow; budget for it |
| `build.gradle(.kts)` | Java/Kotlin (Gradle) | `gradle dependencyCheckAnalyze` | `semgrep p/java`, `detekt` for Kotlin | |
| `*.csproj` / `*.sln` | .NET | `dotnet list package --vulnerable --include-transitive` | `security-code-scan`, `semgrep p/csharp` | |
| `Package.swift` / `*.xcodeproj` | Swift | `osv-scanner` | `semgrep`, `mobsfscan` for app targets | also triggers Agent 9 |
| `pubspec.yaml` | Dart/Flutter | `osv-scanner` | `semgrep` | also triggers Agent 9 if a mobile target |
| `mix.exs` | Elixir | `mix deps.audit` (mix_audit) | `sobelow` (Phoenix), `semgrep` | |
| `Dockerfile` / `compose.y*ml` | Containers | `trivy image` / `grype` | `hadolint` | scan the built image, not just the file |
| `*.tf` | Terraform | - | `tfsec`, `checkov -d .` | |
| `*.yaml` under `k8s/`, `helm/` | Kubernetes | - | `checkov`, `kube-score` | |
| `template.y*ml`, `*.cfn.y*ml` | CloudFormation | - | `cfn-lint`, `checkov` | |
| `.github/workflows/*.yml` | GitHub Actions | - | `actionlint`, plus Agent 13's manual checks | SHA pinning is A08 |
| `.gitlab-ci.yml` | GitLab CI | - | Agent 13 manual checks | same anti-patterns, different syntax |
| `.circleci/config.yml`, `Jenkinsfile`, `azure-pipelines.yml` | Other CI | - | Agent 13 manual checks | pinning, secret scope, privileged contexts |
| `pulumi/`, `cdk/`, `*.bicep` | Other IaC | - | `checkov` (supports several), else read | do not assume Terraform is the only IaC |
| `Info.plist`, `AndroidManifest.xml` | Mobile | - | `mobsfscan` | triggers Agent 9 |

## Cross-language, always available

| Tool | Use | Note |
|---|---|---|
| `osv-scanner -r .` | SCA across every ecosystem above | the universal fallback when a native auditor is missing |
| `syft` then `grype` | SBOM, then vulns against it | best evidence for A03 supply chain |
| `semgrep --config auto` | SAST across languages | `auto` picks packs by detected language |
| `trufflehog`, `gitleaks` | secrets, tree and history | Agent 2 |
| `codeql` | deep dataflow where a DB can be built | slow; `--comprehensive` only, and only if the CLI is present |

## LLM and agentic signals (routes Agent 8)

Dependency names: `openai`, `anthropic`, `@anthropic-ai/sdk`, `langchain`, `llamaindex`,
`@google/generative-ai`, `cohere-ai`, `replicate`, `ollama`, `vercel ai`.

Agentic signals, which the dependency list alone will miss: an MCP server config
(`.mcp.json`, `mcpServers` in settings), tool/function-call definitions passed to a model, an agent
loop that runs without per-iteration human confirmation, or a skill/agent directory
(`.claude/skills/`, `.claude/agents/`). **If user-controlled text can reach a prompt context, or the
system can act autonomously, Agent 8 runs** - regardless of which SDK is in the manifest.

## Recording the result

Stage 0.2 writes the detected set into the report header, so coverage is auditable:

```
Ecosystems detected: node(pnpm), python(uv), terraform, docker
Scanners available : pnpm audit, pip-audit, osv-scanner, semgrep, tfsec, trivy, trufflehog
Scanners missing   : checkov (IaC depth reduced), grype (no SBOM vuln pass)
```

The "missing" line is not decoration. It is what tells the operator why a category came back thin,
and it belongs in the SITREP's coverage section alongside skipped agents.
