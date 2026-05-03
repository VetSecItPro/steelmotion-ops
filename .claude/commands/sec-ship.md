# /sec-ship — AI-Judgment Security Pipeline

**Audit → Fix → Validate → Report.** Find vulnerabilities, fix what's safely fixable, iterate until clean, report what's left.

> **Standards inherited** (apply throughout this skill):
> - [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) — read scanner output + reason about fixes; don't pattern-match error strings
> - [Self-Improvement Protocol](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) — log to `.sec-ship-history.json`; recurring vulnerability shapes get faster fixes
> - [Multi-Repo Awareness](~/.claude/standards/MULTI_REPO_AWARENESS.md) — scan siblings, surface in SITREP, never cross-traverse for fixes
> - [Verify Before Destroy](~/.claude/standards/VERIFY_BEFORE_DESTROY.md) — re-run the specific scanner that found the issue to confirm fix; metadata can lie
> - [Skill Auto-Suggest Protocol](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) — every SITREP ends with "Suggested next"

> **⚡ CONTEXT WARNING:** This skill is ~14K tokens (down from 18K via 2026-05-03 rewrite). Best invoked at start of fresh conversation. Mid-conversation: orchestrator delegates ALL scanning to sub-agents (clean context) and keeps own footprint minimal — never read source files directly, only dispatch agents and collect their lean summaries.

---

## PARADIGM

Security work is judgment-heavy. A scanner finding is data; whether it's real, false-positive, or context-dependent is reasoning. /sec-ship is **a planning document for Claude**, not a flowchart.

- **Don't grep error logs for keywords + look up fixes in tables.** Read the scanner output. Understand what's at risk. Choose the fix.
- **Don't assume a fixed set of tools.** Detect what the project uses (npm audit, pip-audit, cargo audit, gosec, semgrep, trufflehog, etc.) and run canonical equivalents.
- **Don't pretend false-positive triage is rule-based.** It's reasoning. Use the confidence-scoring rubric below; commit to a confidence level + justify.
- **Use history to skip re-discovering known fixes.** `.sec-ship-history.json` records what's worked on this project before.

---

## DISCIPLINE

> Reference: [Superpowers Discipline Protocol](~/.claude/standards/STEEL_DISCIPLINE.md)

- **Steel Principle #1 (verify):** "Vulnerability fixed" requires re-running the specific scanner. Not "I applied the patch."
- **Steel Principle #2 (root cause):** Parameterize the query, don't escape the scanned input. execFile with allowlist, don't sanitize shell input.
- **3-strike rule:** 3 failed fix attempts = architectural; flag for human, don't keep iterating.
- **Confidence-gate honesty:** never lower confidence to ship a fix.

### Rationalization defense

| Rationalization | Reality | Do |
|---|---|---|
| "Internal-only, no one will exploit" | Internal apps get breached | Treat every endpoint as public |
| "Low severity, skip it" | Low compounds into high via chains | Document every finding; fix or defer with reason |
| "Looks like a false positive" | Assume exploitable until proven otherwise | Test the exploit |
| "Clean for 3 runs, skip the deep scan" | Past clean ≠ current clean | Run the full scan |
| "Functional test passed" | Did the SECURITY test pass? | Re-run the scanner that flagged |
| "Never exploited in the wild" | Yet | Fix before exploited |
| "Scanner agrees, ship it" | Scanners have FPs + miss novel attacks | Read the code path; don't trust the verdict alone |
| "Quarantine the test" | = shipping a known vuln | Fix or honestly defer with operator awareness |

---

## CRITICAL RULES

1. NEVER ask permission. Just do it.
2. NEVER skip verification. Re-run the scanner.
3. FIX ROOT CAUSES. Not symptoms.
4. ITERATE until clean OR every above-gate finding triaged.
5. DOCUMENT every finding. Status transitions, never delete.
6. CONFIDENCE GATES: 8/10 daily, 2/10 comprehensive. Below gate? Exclude OR escalate to comprehensive — don't lower the gate.
7. VERIFY BEFORE DESTROYING any code. Add regression test (Agent 15) before claiming done.
8. READ SCANNER OUTPUT. Don't grep its summary line.
9. ADAPT to project. Detect language/scanners/frameworks. Don't assume Node/jest/Vercel.
10. EVERY SITREP ends with "Suggested next" per autosuggest protocol.

---

## MODES

```
/sec-ship                      # Default: full audit + auto-fix, 8/10 confidence gate
/sec-ship --comprehensive      # Deep scan, 2/10 gate — monthly or pre-launch
/sec-ship --audit              # Scan only, no fixes (read-only)
/sec-ship --diff               # Scope to current branch diff (fast pre-PR check)
/sec-ship --infra              # Infrastructure & CI/CD only (Agents 13, 17)
/sec-ship --code               # Code vulns only (Agents 3-6, 10-11, 14)
/sec-ship --supply-chain       # Deps & artifacts only (Agents 1, 17)
/sec-ship --owasp              # OWASP Top 10 Web + API + LLM (Agents 3, 6, 8)
/sec-ship --fix SEC-XXX        # Fix one specific finding manually
/sec-ship --key-rotation       # Walk operator through key rotation for a provider
```

### `--key-rotation` mode (added 2026-05-03)

Closes the loop between `/secrets-audit` (which finds OVERDUE rotations) and the operator actually rotating the key. Interactive walkthrough — each destructive step requires explicit confirmation.

Flow:
1. Run `/secrets-audit --check rotation` first to enumerate OVERDUE keys (or accept a `--provider <name>` arg)
2. For each provider:
   - Generate new key via the provider's CLI/dashboard (operator-driven; skill provides exact link/command)
   - Update every `.env*` file that referenced the old key (after grep-find — never blind-replace)
   - Restart consuming services and verify traffic flows on the new key
   - Revoke the old key only after verification
3. Append rotation event to `~/.openclaw/rotation-log.json` for audit trail (date, provider, old-key-fingerprint, new-key-fingerprint, who-restarted-what)

This mode delegates the discovery half to `/secrets-audit` and adds the action half. It does NOT replace `/secrets-audit` — you can still run that standalone for audit-only work.

### Confidence gates

**8/10 (default daily):** zero-noise. Every reported finding is verified, real, exploitable. FP rate ≤ 5% target.

**2/10 (comprehensive):** surfaces tentative findings + theoretical risks + defense-in-depth. Expect more findings; each includes confidence score.

### Confidence calibration (1-10)

| Score | Meaning |
|---|---|
| 1-2 | Theoretical pattern; no demonstrable exploit |
| 3-4 | Pattern present; exploitability depends on deployment assumptions |
| 5-6 | Likely exploitable; could be exercised by motivated attacker |
| 7-8 | Demonstrably exploitable in current configuration |
| 9-10 | Trivially exploitable; PoC included |

Score reflects **exploitability in this codebase right now**, not generic CVSS. Justify with two-sentence rationale per finding.

### Hard-exclusion rules (never findings)

- Test fixtures with deliberately bad inputs
- `.env.example` placeholders
- Documentation showing exploit examples
- Localhost-only debug endpoints with auth gate intact
- Dev-mode console logs that strip at build (verify the strip)
- Already-quarantined findings explicitly marked WONT-FIX with operator-approved reason
- npm audit advisories with score < 7 in dev-only deps (transitive devDeps)
- Findings in archived/disabled code paths
- Generated code (build artifacts, `*.generated.*`)
- Mock public test keys (`pk_test_*`, `sk_test_*` in `__tests__/`)
- `process.env.NODE_ENV === 'development'`-gated debug code
- Operator-allowlisted commands in admin-gated routes (verify the allowlist + admin check)
- Pinned-by-decision deprecation warnings (e.g., a lib version held back with ADR)
- localhost SSRF where the request lands on intentionally-exposed service (e.g., searxng:8888)

When in doubt: surface for review (low confidence) rather than auto-fix.

---

## STATUS UPDATES

> Reference: [Status Update Protocol](~/.claude/standards/STATUS_UPDATES.md)

```
🔍 Phase 1: Discovery + history read
   ├─ Read .sec-ship-history.json (patterns_observed = N)
   ├─ Detect project: <type, scanners, deploy>
   └─ Sibling repos: <count> reported

🤖 Phase 2: Parallel scanning (17 agents)
   ├─ ✅ Agent 1 (deps): N findings
   ├─ ✅ Agent 2 (secrets): N findings
   └─ Total: <N> raw findings

📊 Phase 3: Triage (gate=8/10)
   ├─ Auto-fixable: N
   ├─ Manual review: N
   └─ Deferred: N

🔧 Phase 4: Fix loop
   └─ Re-scan to verify

✅ Phase 5: SITREP + history append
```

---

## CONTEXT MANAGEMENT

> Reference: [Context Management Protocol](~/.claude/standards/CONTEXT_MANAGEMENT.md)

The 17-agent scan is heavy. Orchestrator NEVER reads source directly — only dispatches agents + collects ≤ 200-token summaries. Full findings persist to `.sec-ship-reports/findings/agent-<N>.json`.

---

## AGENT ORCHESTRATION

> Reference: [Agent Orchestration Protocol](~/.claude/standards/AGENT_ORCHESTRATION.md)

### Model selection

- Reasoning agents (Server-Side, AuthN/AuthZ, Logic Correctness): Opus or Sonnet
- Pattern-detection agents (Deps, Secrets, Build Artifacts): Haiku — fast bulk
- Domain agents (LLM, Mobile, Crypto): Sonnet — specialized but bounded

### Batching

Run agents in parallel where they don't share file conflicts:
- Wave A: 1, 2, 17 (read-only file scans)
- Wave B: 3, 4, 6 (server-side patterns)
- Wave C: 5, 7, 13 (client + config)
- Wave D: 8, 9, 12 (specialized: AI, mobile, crypto)
- Wave E: 10, 11, 14 (logic + data flow)
- Wave F: 15, 16 (regression tests + spec drift — depend on prior findings)

Within wave: parallel. Across waves: sequential.

---

## SELF-IMPROVEMENT VIA `.sec-ship-history.json`

Per [Self-Improvement Protocol](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md), every run reads + appends.

### Schema additions specific to /sec-ship

```json
{
  "patterns_observed": {
    "<vuln-shape-key>": {
      "first_seen": "2026-05-03",
      "count": 3,
      "fix_known": true,
      "last_successful_fix": "parameterize via prepared statements",
      "false_positive_rate": 0.02,
      "scanner_that_found_it": "semgrep p/owasp-top-ten"
    }
  },
  "deferred_with_reason": {
    "<finding-id>": {
      "deferred_at": "ISO",
      "reason": "...",
      "reviewer": "operator",
      "expires_at": "ISO"
    }
  }
}
```

Future runs: known shape + prior fix worked → try it FIRST. `deferred_with_reason` not expired → skip auto-fix; re-affirm in report.

---

## DEFINITION OF DONE

A run is COMPLETE when ONE is true:

1. **Clean state**: scanner re-runs return zero findings above gate. SITREP "no findings."
2. **Triaged state**: every above-gate finding either FIXED+VERIFIED or DEFERRED with operator-acknowledged reason. SITREP shows deferred list.
3. **Blocked state**: ≥ 3 fix-attempt failures = architectural. Flag human, document attempts, exit BLOCKED.

NEVER: silently drop findings, lower confidence to dismiss, mask via test changes.

---

## REPORT PERSISTENCE

`.sec-ship-reports/<YYYYMMDD-HHMMSS>.md` is source of truth. Updated continuously; survives compaction.

### Status transitions

```
FOUND → FIXING → VERIFIED-FIXED   (success)
FOUND → FIXING → BLOCKED          (3-strike)
FOUND → DEFERRED                   (judgment, with reason)
FOUND → FALSE-POSITIVE             (after triage; logged to history)
```

Append-only. Never delete. Re-runs ADD to report (with run-id headers); don't overwrite.

### Resume protocol

If interrupted, next /sec-ship invocation:
1. Reads last `.sec-ship-reports/*.md` from same project
2. If status="in-progress" and < 1 hour old: resume from last logged step
3. Otherwise: start fresh

---

## STAGE 0: INITIALIZATION

### 0.1 Pre-flight

In a git repo. `gh` authenticated (advisories API + workflow audit). `.sec-ship-history.json` exists OR will be created (auto-gitignored). `.sec-ship-reports/` exists OR will be created.

### 0.2 Detect project context (don't assume)

| Signal | Tells you |
|---|---|
| `package.json` | Node. Read deps for stack hint (Next.js, Express, etc.) |
| `pyproject.toml` / `requirements.txt` | Python |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `Dockerfile` / `docker-compose.yml` | Container deploy. Run Trivy/Grype. |
| `.github/workflows/*.yml` | GitHub Actions. Audit yml for security anti-patterns. |
| Mobile signals (`Info.plist`, `AndroidManifest.xml`) | Run Agent 9 |
| LLM signals (`anthropic`, `openai`, `langchain` in deps) | Run Agent 8 |

### 0.3 Read history

Per [SELF_IMPROVEMENT_PROTOCOL](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md):
- Load `patterns_observed` → known shapes + fixes
- Load `deferred_with_reason` → don't re-flag operator-acknowledged
- Last run's outcome → if BLOCKED, elevated caution

### 0.4 Multi-repo scan

Per [MULTI_REPO_AWARENESS](~/.claude/standards/MULTI_REPO_AWARENESS.md), capture sibling state for SITREP. /sec-ship operates only on cwd's repo; siblings reported, not scanned.

### 0.5 Sibling skill check

Did /test-ship or /gh-ship run recently in same repo? Read their reports for context (e.g., recent dep updates often introduce new advisories).

### 0.6 Initialize report file

Create `.sec-ship-reports/<YYYYMMDD-HHMMSS>.md` with template:

```markdown
# Sec-Ship Report — <repo>
**Run started:** <ISO>
**Mode:** <daily|comprehensive|audit|diff|...>
**Confidence gate:** <8|2>

## Findings (rolling — appended as agents complete)
## Fix log (rolling — appended as fixes verified)
## Deferred (with reasons)
## SITREP (populated at end)
```

---

## STAGE 1: DISCOVERY & ATTACK SURFACE MAPPING

Map what's exposed BEFORE scanning. Saves work — focus scan on actual attack surface.

For each detected stack:
- HTTP entry points (`/api/*` routes, framework annotations)
- Auth boundaries (middleware, decorators, route guards)
- Data flows (untrusted input → DB query / command exec / response body / file write)
- Trust boundaries (operator vs customer vs anonymous)
- External integrations (third-party APIs, webhook receivers, OAuth)

Output: `.sec-ship-reports/attack-surface.md` — informs Agents 3-6, 10, 11, 14.

---

## STAGE 2: PARALLEL SECURITY SCANNING (17 AGENTS)

Each agent below has: **Mission** (what to find), **Scanners** (illustrative; skill detects + runs equivalent), **Confidence guidance**, **Anti-patterns**.

Agents return ≤ 200-token summaries. Full findings → `.sec-ship-reports/findings/agent-<N>.json`.

### Agent 1 — Dependencies & Supply Chain

**Mission:** vulnerable, abandoned, malicious dependencies.

**Scanners:** `npm audit`, `pip-audit`, `cargo audit`, `gosec`. `osv-scanner` cross-language. `socket.dev` for unusual install patterns. For Node: also typosquat checks (`reactt`, `lodahs`).

**Confidence:** 9-10 known CVE score ≥ 7 in reachable code path; 5-7 CVE in dev-only or unreached transitive; < 5 unmaintained without CVE.

**Anti-patterns:** advisories < 7 in dev-only deps; unmaintained-without-CVE.

**Auto-fix:** `<pm> audit fix` for in-range. Breaking-change required: report only.

### Agent 2 — Dynamic Secret Detection

**Mission:** secrets/credentials/private keys committed (current state + git history).

**Scanners:** `trufflehog filesystem . --include-paths=src,lib,scripts`. History: `trufflehog git file://. --since=<lookback>`. Comprehensive: also `gitleaks detect`.

**Confidence:** 9-10 high-entropy token matching known provider format AND in tracked file; 5-7 token-shaped but in test fixture/`.env.example`; < 5 false positive (e.g., base64-encoded test image).

**Anti-patterns:** see Hard-Exclusion — fixtures, env.example, mocks all skipped.

**Auto-fix:** unstage + .gitignore + create `.env.example` if relevant. Already-pushed: surface for IMMEDIATE rotation; do not auto-rotate.

### Agent 3 — Server-Side Security (OWASP Top 10 Web)

**Mission:** SQLi, command injection, SSRF, deserialization, path traversal, broken access control, server-side template injection.

**Scanners:** `semgrep --config p/owasp-top-ten`, `semgrep --config p/javascript`, `eslint-plugin-security` for Node. Python: `bandit`. Go: `gosec`.

**Confidence:** 9-10 untrusted-source → dangerous-sink with no validation between; 5-7 pattern present but validated upstream OR sink from constants; < 5 looks like pattern but actually safe.

**Anti-patterns:** test fixtures with deliberately-bad inputs; allowlist-validated routes.

**Reasoning:** READ THE CODE PATH. Scanners flag patterns; you decide if exploitable. SQL string concat with constant input = fine. Same with user input = critical.

**Auto-fix:** parameterize queries, use safe APIs (execFile not exec), add validation. NEVER suppress with `// security-disable-line`.

### Agent 4 — Authentication & Authorization

**Mission:** auth bypass, privilege escalation, broken session management, missing role checks.

Read every route's auth gate. Cross-reference against expected access tier. Look for:
- Routes with no auth gate that should have one
- Routes with weaker auth than peers
- Token validation regex-only without HMAC verification
- Session storage in localStorage instead of httpOnly cookies
- Missing CSRF protection on state-changing routes

**Confidence:** 9-10 "operator can access admin route"; 5-7 "anonymous can read endpoint that should be auth'd, returns benign data"; < 5 "auth gate is in middleware not handler" (defense-in-depth, not vuln).

### Agent 5 — Client-Side Security

**Mission:** XSS, DOM clobbering, prototype pollution, IDOR in client code.

For React/Vue/Svelte: `dangerouslySetInnerHTML`, `v-html`, `{@html}` with non-trusted input. For all: localStorage / sessionStorage for sensitive data.

**Confidence:** 9-10 unescaped user input rendered as HTML; 5-7 `dangerouslySetInnerHTML` with constant content; < 5 sanitizer-wrapped (DOMPurify) input.

### Agent 6 — API Security (OWASP API Top 10)

**Mission:** broken object-level authorization (BOLA), excessive data exposure, mass assignment, missing rate limiting, unsafe API consumption.

For each /api/* route:
- Filter by ownership before returning data? (BOLA)
- Returns more fields than caller needs? (excessive exposure)
- Accepts user-controlled `is_admin` / `role`? (mass assignment)
- Has rate limiting?

**Confidence:** 9-10 "anonymous fetches any user's data by ID"; 5-7 "missing rate limit on heavy endpoint"; < 5 "API returns extra non-sensitive fields."

### Agent 7 — Configuration & Headers

**Mission:** missing/incorrect security headers, CORS too permissive, cookie flags wrong, transport-layer issues.

Check (Next.js: `next.config.mjs` → `headers()`; Express: middleware; static: edge config):
- CSP present + non-trivial?
- HSTS `max-age` ≥ 31536000?
- X-Frame-Options or CSP `frame-ancestors`?
- Referrer-Policy set?
- CORS origin not `*` for credentialed routes?
- Cookies with `Secure`, `HttpOnly`, `SameSite=Strict|Lax`?

**Confidence:** 9-10 "no CSP + DOM-XSS sink confirmed"; 5-7 "CSP allows `unsafe-inline`"; < 5 "X-Powered-By leaks framework version."

### Agent 8 — AI/LLM Security (OWASP LLM Top 10)

**Mission:** prompt injection, insecure plugin design, model DoS, sensitive info disclosure, insecure output handling, excessive agency.

For LLM apps:
- User-controlled text → LLM prompt without sanitization (prompt injection)
- LLM output → eval/shell/SQL without validation (insecure output handling)
- LLM has tool/plugin access with broad permissions (excessive agency)
- System prompts contain credentials/PII (system prompt leakage)
- No rate limiting (cost-DoS)
- No content filter on outputs

**Confidence:** 9-10 "user input → LLM → eval()"; 5-7 "LLM has shell access via MCP with no command allowlist"; < 5 "system prompt mentions company name."

### Agent 9 — Mobile Security (if detected)

**Mission:** OWASP MASVS — insecure data storage, insecure communication, insecure auth, code tampering.

Run only if `Info.plist`, `AndroidManifest.xml`, `*.xcodeproj`, `app/build.gradle` detected. Use `mobsfscan` or equivalent.

### Agent 10 — Business Logic & Advanced

**Mission:** logic flaws scanners can't catch — race conditions, broken state machines, missing transaction boundaries, TOCTOU.

Reasoning-heavy. Read code; look for:
- Multi-step state transitions that aren't atomic
- Concurrent-safe operations missing locks (counter increments without DB FOR UPDATE)
- Time-of-check-time-of-use gaps
- Idempotency key storage that doesn't prevent duplicate-effect (apr- id collision class)
- Replay-attack possibilities on state-changing actions

**Confidence:** 9-10 "race condition exploitable in test"; 5-7 "no obvious lock but DB constraint catches"; < 5 "in-process state without obvious concurrent caller."

### Agent 11 — Logic Correctness, Integration Contracts & Admin Verification

**Mission:** logic errors that aren't security per se but become security via downstream effects. Audit admin gates specifically.

For every operator/admin-only route:
- Gate present at handler level (not just middleware)?
- Role check correct?
- Fallback (e.g., single-admin mode) permissive enough to be a problem in multi-user mode?
- Non-GET verbs gated where appropriate? (per ADV-002 lesson 2026-05-03)

**Confidence:** 9-10 "operator-cookie-holder can hit /api/terminal" (host-RCE primitive); 5-7 "admin gate present but uses string-compare on role"; < 5 "missing gate but route is read-only and exposes no PII."

### Agent 12 — Cryptographic & Randomness Analysis

**Mission:** weak crypto, hardcoded keys, predictable randomness, insecure key derivation.

Look for:
- `Math.random()` for security-relevant values
- MD5/SHA1 for password hashing (should be bcrypt/argon2/scrypt)
- AES-ECB mode (should be GCM or CBC with IV+MAC)
- Hardcoded crypto keys
- Weak password hashing iterations (< 10k for bcrypt)
- IV reuse with stream ciphers / counter modes

**Confidence:** 9-10 "session ID via Math.random()"; 5-7 "bcrypt low iterations"; < 5 "MD5 used for non-security cache key."

### Agent 13 — Infrastructure & Configuration Security

**Mission:** Dockerfile security, IaC misconfig, GitHub Actions workflow security.

Run:
- `hadolint Dockerfile`
- `tfsec` / `checkov` for Terraform
- For GitHub Actions:
  - Action versions pinned to SHA?
  - `permissions:` block minimal?
  - Secrets in `env:` at workflow level (broad) vs step level (narrow)?
  - `pull_request_target` triggers (privileged context for fork PRs)?
  - Self-hosted runners on public repos?
- For Dockerfile: USER root; missing healthcheck; package versions unpinned; secrets in build args.

**Confidence:** 9-10 "USER root + sudo + exposed network port"; 5-7 "actions/checkout@v4 unpinned"; < 5 "missing HEALTHCHECK."

### Agent 14 — Data Flow & Taint Tracking

**Mission:** end-to-end taint analysis from untrusted source to dangerous sink.

For each entry point identified in Stage 1:
- Trace input through codebase
- Mark every transformation (validate, sanitize, escape, allowlist)
- Flag flows that reach dangerous sink without crossing trust-establishing transformation

Most reasoning-heavy agent. Use semgrep's taint mode (`semgrep --taint`); supplement with Claude code reading.

### Agent 15 — Security Regression Test Generation

**Mission:** for every fix applied, generate a regression test that would catch the vuln if it returns.

For each VERIFIED-FIXED finding:
- Write test reproducing original vuln pattern
- Assert fix's behavior (403 instead of 200, sanitized output, etc.)
- Add to project's test suite at appropriate location

This prevents the "fix forgets, ships again" regression class. NEVER skip this agent.

### Agent 16 — API Specification Drift Detection

**Mission:** if project has OpenAPI/Swagger spec, find places where implementation drifted in security-relevant ways.

- Spec says "auth required" but route handler doesn't check?
- Spec says "200 returns user_id only" but handler returns whole user object?
- Spec lists allowed origins; CORS config differs?

### Agent 17 — Build Artifact & Secrets in Output

**Mission:** secrets that leak into built bundles, source maps, container images.

- Inspect `dist/`/`build/`/`.next/` output for tokens
- Inspect Docker image layers for `.env` or unredacted secrets
- For source maps: do they include backend code that should never be on client?

Run after a build OR scan latest CI artifact.

---

## STAGE 3: TRIAGE

After 17 agents return:

1. **Confidence-gate filter:** drop below gate (8 default; 2 comprehensive)
2. **Hard-exclusion filter:** drop matching exclusion rules
3. **History match:** for each survivor, check `patterns_observed` for prior fix
4. **Severity sort:** group by category (RCE/auth-bypass/SSRF/SQLi → top), then confidence
5. **Auto-vs-manual decision:**
   - Auto-fix: well-known pattern + mechanical fix
   - Manual review: judgment call ("should this route be admin-only?")
   - Defer: with operator-readable reason

---

## STAGE 4: FIX LOOP

For each auto-fix candidate:

1. Read surrounding code context (not just scanner's file:line)
2. Apply smallest correct fix at root cause
3. Re-run the specific scanner that found the issue
4. If still flagged: try different approach. Max 3 attempts.
5. After 3: mark BLOCKED, document attempts, escalate
6. After fix verified: dispatch Agent 15 to write regression test
7. Update report status: FOUND → FIXING → VERIFIED-FIXED

For manual-review items: add to deferred list with explicit "needs operator review: <reason>". Surface in SITREP.

---

## STAGE 5: VALIDATE & SHIP

After all fixes:

1. **Re-run full scan suite.** Confirm no new findings.
2. **Run regression tests** (Agent 15 + existing).
3. **Build verification.** If build artifacts referenced (Agent 17), regenerate + re-scan.
4. **Sibling-skill awareness:** if /test-ship recently ran, confirm tests still pass.
5. **Append to history** per SELF_IMPROVEMENT_PROTOCOL.

---

## STAGE 6: SITREP + REPORT FINALIZATION

Final report:

```
═══════════════════════════════════════════════════════════════
🛡  /sec-ship — <success | partial | blocked>
═══════════════════════════════════════════════════════════════

📋 Run
   Repo:        <name>
   Mode:        <daily | comprehensive | audit | diff>
   Confidence gate: <8 | 2>
   Duration:    <Xm Ys>
   Run ID:      <timestamp>

📊 Findings
   FOUND:           <N>
   VERIFIED-FIXED:  <N>
   DEFERRED:        <N>
   BLOCKED:         <N>
   FALSE-POSITIVE:  <N>

🔧 Fixes applied (top 5 by impact)
   • <SEC-XXX> — <description> [confidence: <N/10>]
     Fix: <one-line>
     Verified: ✅ scanner re-run shows clean
     Regression test: <path>

⚠️  Deferred (with reasons)
   • <SEC-YYY> — <description>
     Reason: <text>
     Operator review: <yes|already-acked>

❌ Blocked (3-strike)
   • <SEC-ZZZ> — <description>
     Attempts: <list>
     Recommendation: <architectural change needed>

🌐 Sibling repos in workspace
   <name>: <last sec-ship run | "never run"> | recent vuln count: <N>
   [run /sec-ship from inside if not scanned recently]

📈 Self-improvement
   patterns_observed total: <N>
   New patterns this run: <list>
   Known recurred: <list with prior fix worked / didn't>

📁 Reports
   .sec-ship-reports/<run-id>.md
   .sec-ship-reports/findings/agent-*.json
   .sec-ship-reports/attack-surface.md
   .sec-ship-history.json (updated)

═══════════════════════════════════════════════════════════════

## Suggested next

Per [Skill Auto-Suggest Protocol](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md), based on outcome:

| Outcome | Recommended | Why |
|---|---|---|
| Clean (no findings) | /test-ship if recent code changed | next quality gate |
| Findings auto-fixed + verified | /gh-ship | ship the security fixes |
| Findings deferred | none — operator review the deferred list | judgment call |
| Findings BLOCKED (3-strike) | /investigate the architectural issue | need deeper look |
| Comprehensive scan, lots of low-confidence findings | /sec-ship --diff | re-scan only what's recently changed |
```

---

## DESIGN DECISIONS (WHY)

### Why AI-judgment over fix tables
Real CVEs/zero-days don't fit regex rows. 2026-05-03 rewrite shifted decisions to "scanner output is data; Claude reasons." Agent definitions provide structure (what to scan); fix decisions are reasoning.

### Why 17 agents
Specialization beats generality. SQL-injection-detector is sharper than general scanner. Orchestrator dispatches the right agents.

### Why confidence gates
False-positive fatigue is the #1 reason ops teams turn off security tools. 8/10 daily produces zero-noise reports operators trust. Comprehensive (2/10) is periodic deep-dive.

### Why per-finding regression tests
Without them, same vuln re-introduced in 6 months when someone refactors. Agent 15 makes regressions observable.

### Why per-project history
Same fix patterns recur. Without history, every run rediscovers. With it, future runs try known-good fixes first.

### Why hard-exclusion list
Without it, report fills with false positives; operator stops trusting it.

### Why multi-repo report-only (no cross-traverse)
Workspace with 3 sibling repos shouldn't make /sec-ship 3x complex. One repo per invocation. SITREP surfaces sibling state to prevent "scanned one, forgot the others."

### Why auto-suggest
Workflow chaining is high-value. /sec-ship → /gh-ship → /monitor. SITREP pre-computes the next move so operator + Claude don't have to remember.

---

## DEFINITION OF DONE — recap

- All confidence-gated findings either VERIFIED-FIXED or DEFERRED-with-reason
- Every fix: scanner re-run confirms clean + regression test added
- BLOCKED findings have full attempt log
- `.sec-ship-history.json` updated
- Sibling state surfaced in SITREP (no cross-traverse)
- Report file is single source of truth, persists across sessions
- SITREP ends with "Suggested next"

---

## DISCLAIMER

/sec-ship is high-quality automated audit. It is NOT a substitute for periodic human security review by qualified personnel, especially before releases handling regulated data (HIPAA, PCI-DSS, GDPR sensitive categories). Use as day-to-day security gate; supplement with quarterly or pre-launch human reviews.

---

## RELATED SKILLS

**Feeds from:**
- /test-ship — should run before /sec-ship to ensure fixes don't break tests
- /deps — surfaces dep advisories that /sec-ship can fix

**Feeds into:**
- /gh-ship — runs after /sec-ship completes to ship verified-fixed code
- /monitor — runs after deploy to verify production isn't breached

**Pairs with:**
- /redteam — for active exploitation testing on localhost (deeper than passive)
- /compliance — for regulatory framework checks (HIPAA, PCI, GDPR)

---

## IMPORTANT REMINDERS

- Run scanner ON the actual code; REASON about findings; FIX root causes
- ITERATE until clean OR every finding triaged
- DOCUMENT every finding (status transitions, never delete)
- VERIFY every fix by re-running scanner that found it
- ADD regression tests for every fix
- LEARN from history (`.sec-ship-history.json`)
- SCAN siblings in multi-repo workspaces (report only)
- TRIAGE honestly — don't lower confidence to ship more findings; don't quarantine to dismiss real ones
- END SITREP with "Suggested next" per autosuggest protocol
- The user trusts /sec-ship to find real vulns, fix them safely, and improve at security over time

<!-- /sec-ship by Steel Motion LLC — https://steelmotion.dev -->
<!-- Part of steelmotion-ops (renamed from claw-ops 2026-05-03) -->
<!-- License: MIT -->
