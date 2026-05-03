# /deps — Dependency Health, Updates & Supply Chain Security

> **Standards inherited** (apply throughout this skill):
> - [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md)
> - [Self-Improvement Protocol](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) — log to .deps-history.json
> - [Multi-Repo Awareness](~/.claude/standards/MULTI_REPO_AWARENESS.md)
> - [Verify Before Destroy](~/.claude/standards/VERIFY_BEFORE_DESTROY.md)


**Comprehensive dependency audit, update, and supply chain security sweep.**

**FIRE AND FORGET** — Execute the entire pipeline without waiting for user input. Status updates every 5 minutes. Human intervention only for breaking changes.

---

## DISCIPLINE

> Reference: [Superpowers Discipline Protocol](~/.claude/standards/STEEL_DISCIPLINE.md)

Key enforcements for this skill:
- **Steel Principle #1:** NO completion claims without fresh verification evidence — build + tests must pass after every update batch
- **Steel Principle #3:** NO silent major upgrades — majors get explicit approval and a migration plan (defer to /migrate)
- Lockfile changes are code — review them; never commit an unreviewed lockfile rewrite

### Deps-Specific Rationalization Table

| Rationalization | Reality | What to Do |
|----------------|---------|------------|
| "We were clean last week, skip the full audit" | CVEs drop daily; last week's clean audit doesn't prove today | Run full audit every time |
| "This CVE is low severity, skip it" | Low severity CVEs chain with others into full exploits | Document and patch; no silent skips |
| "Minor version, should be safe to bump" | Semver is a suggestion; minors break APIs regularly | Run the test suite after every bump |
| "The lockfile diff is too big to read" | Big lockfile diffs hide transitive package swaps (supply chain risk) | Diff tree, not just lockfile; verify no unexpected packages |

---

## STATUS UPDATES

This skill follows the **[Status Update Protocol](~/.claude/standards/STATUS_UPDATES.md)**.

See standard for complete format. Skill-specific status examples are provided throughout the execution phases below.

---

## CONTEXT MANAGEMENT

This skill follows the **[Context Management Protocol](~/.claude/standards/CONTEXT_MANAGEMENT.md)**.

Key rules for this skill:
- Audit agents (outdated, vulnerabilities, licenses, unused) return < 500 tokens each (full findings written to `.deps-reports/`)
- State file `.deps-reports/state-YYYYMMDD-HHMMSS.json` tracks which audit/update phases are complete
- Resume from checkpoint if context resets — skip completed audits and updates
- Max 2 parallel audit agents (Phase 1); update agents run sequentially (they modify package.json/lockfile)
- Orchestrator messages stay lean: "Phase 2: 12/18 packages updated — 3 major deferred, 2 blocked"

---

## AGENT ORCHESTRATION

This skill follows the **[Agent Orchestration Protocol](~/.claude/standards/AGENT_ORCHESTRATION.md)**.

The orchestrator coordinates agents but NEVER runs audits or fixes directly. All heavy work is delegated to focused agents that write results to disk.

### Model Selection for This Skill

| Agent Type | Model | Why |
|-----------|-------|-----|
| Dependency lister | `haiku` | Reading package.json, listing deps — no judgment |
| Outdated dependency scanner | `haiku` | Running npm outdated, collecting version numbers — no judgment |
| Vulnerability scanner | `sonnet` | Must assess CVE severity, determine if vulnerability is exploitable in this project's context |
| License analyzer | `sonnet` | Must understand license compatibility, flag copyleft risks for commercial projects |
| Supply chain analyzer | `sonnet` | Must evaluate dependency trustworthiness, maintenance status, bus factor |
| Dependency updater | `sonnet` | Must determine safe upgrade paths, handle breaking changes, verify build |
| Security fixer | `sonnet` | Must resolve CVEs with correct dependency version changes or patches |
| Report synthesizer | `sonnet` | Must compile dependency health scores and prioritized update plan |

### Agent Batching

- Inventory/listing agents can run 2 in parallel (read-only)
- Vulnerability analysis runs as a single focused agent (needs full dependency context)
- Update agents handle up to 5 dependency updates each
- Update agents run SEQUENTIALLY (each update may affect others)

---

## Execution Rules (CRITICAL)

- **NO permission requests** — just execute
- **NO "should I proceed?" questions** — just do it
- **NO waiting for user confirmation** — work continuously
- **REPORT IS THE SINGLE SOURCE OF TRUTH** — written to disk after every status change
- **UPDATE REPORT AS UPDATES HAPPEN** — each finding's status changes in real-time in the markdown
- **NEVER DELETE findings** — only update their status
- **ATTEMPT FIX UP TO 3 TIMES** before marking BLOCKED — document each attempt
- **SITREP ANNOTATES EVERYTHING** — what was updated, what was deferred and WHY, what was blocked and WHY
- **Status updates every 5 minutes** — output progress without waiting for response
- **Auto-update safe packages** — patch and minor versions (configurable)
- **Flag breaking changes** — major versions require human decision
- **Self-healing** — retry failed operations, work around network issues

---

## Report Persistence (CRITICAL — Survives Compaction/Restart)

The markdown report file is the **living document**. Updated continuously as work happens.

### Finding Statuses

| Status | Meaning |
|--------|---------|
| `FOUND` | Issue discovered during audit, not yet addressed |
| `🔧 UPDATING` | Package update in progress |
| `✅ FIXED` | Update applied, build verified, tests pass |
| `⏸️ DEFERRED` | Major version update — needs human review, or risky change. Reason documented. |
| `🚫 BLOCKED` | Attempted update up to 3 times, all broke build/tests. Each attempt documented. |
| `✅ OK` | No issue found (e.g., license is clean) |
| `🗑️ REMOVED` | Unused dependency removed successfully |

### Rules

1. **Write report at Phase 0** — file exists before any audits, with header and empty sections
2. **Update after each audit agent completes** — findings added as discovered
3. **Update after each package update** — status changes from FOUND → UPDATING → FIXED/BLOCKED/DEFERRED
4. **Write to disk after every status change** — if session dies, report shows exactly where things stand
5. **Progress Log** — timestamped entries after each phase and each update
6. **SITREP section** — for every DEFERRED or BLOCKED item, document:
   - What was tried (all attempts)
   - Why it failed (build error, test failure, etc.)
   - What would be needed to fix it

### Resume Protocol

Before creating a new report, check for a recent incomplete one:

1. Find most recent `.deps-reports/deps-*.md`
2. If < 1 hour old AND Status is not `🟢 COMPLETE` → resume it
3. Read `## Progress Log` to find last completed step
4. Skip completed phases, continue from next incomplete step

---

## Usage

```bash
/deps                         # Full audit + safe updates
/deps --audit-only            # Just report, don't update anything
/deps --update-all            # Update everything including major versions
/deps --update-patch          # Only patch updates (safest)
/deps --update-minor          # Patch + minor updates (default)
/deps --check=<package>       # Check specific package
/deps --licenses              # License compliance report only
/deps --security              # Security vulnerabilities only
/deps --unused                # Find unused dependencies only
```

---

## Output Files (All Gitignored)

| File | Purpose |
|------|---------|
| `.deps-reports/deps-YYYY-MM-DD-HHMMSS.md` | Human-readable report |
| `.deps-audit.json` | Machine-readable findings |
| `.deps-reports/licenses.json` | License inventory |
| `.deps-reports/unused.json` | Unused dependency list |
| `.deps-reports/updates.json` | Available updates |

**FIRST ACTION:** Ensure gitignored:
```bash
for pattern in ".deps-reports/" ".deps-audit.json"; do
  grep -qxF "$pattern" .gitignore 2>/dev/null || echo "$pattern" >> .gitignore
done
```

---

## Architecture

```
═══════════════════════════════════════════════════════════════════════════════
                              /deps PIPELINE
═══════════════════════════════════════════════════════════════════════════════

PHASE 0: SETUP
├── Git snapshot (rollback point)
├── Detect package manager (npm/pnpm/yarn/bun)
├── Baseline metrics (package count, size)
└── Create output directories

PHASE 1: AUDIT (4 parallel agents)
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│    SECURITY     │ │    OUTDATED     │ │    LICENSE      │ │     HEALTH      │
│    Agent 1      │ │    Agent 2      │ │    Agent 3      │ │    Agent 4      │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │                   │
         └───────────────────┴─────────┬─────────┴───────────────────┘
                                       │
                                [MERGE FINDINGS]
                                [STATUS UPDATE]

PHASE 2: UPDATE (Sequential, safe first)
├── Patch updates (automatic)
├── Minor updates (automatic, with test verification)
├── Major updates (flag for human, or auto if --update-all)
├── Verify after each update (build + test)
└── Rollback if verification fails

PHASE 3: CLEANUP
├── Remove unused dependencies
├── Dedupe dependencies
├── Regenerate lockfile
├── Verify build still works
└── Update .env.example if needed

PHASE 4: REPORT
├── Before/after comparison
├── Security fixes applied
├── Updates applied
├── License inventory
├── Recommendations
└── Save reports

═══════════════════════════════════════════════════════════════════════════════
```

---

## PHASE 0: SETUP

### 0.1 Git Snapshot

```bash
git add -A && git commit -m "chore: pre-deps snapshot" --allow-empty 2>/dev/null || true
DEPS_BASE=$(git rev-parse HEAD)
echo "📌 Rollback point: $DEPS_BASE"
```

### 0.2 Detect Package Manager

```bash
if [ -f "bun.lockb" ]; then
  PM="bun"; PM_INSTALL="bun install"; PM_ADD="bun add"; PM_REMOVE="bun remove"
  PM_AUDIT="bun audit"; PM_OUTDATED="bun outdated"; PM_WHY="bun why"
elif [ -f "pnpm-lock.yaml" ]; then
  PM="pnpm"; PM_INSTALL="pnpm install"; PM_ADD="pnpm add"; PM_REMOVE="pnpm remove"
  PM_AUDIT="pnpm audit"; PM_OUTDATED="pnpm outdated"; PM_WHY="pnpm why"
elif [ -f "yarn.lock" ]; then
  PM="yarn"; PM_INSTALL="yarn install"; PM_ADD="yarn add"; PM_REMOVE="yarn remove"
  PM_AUDIT="yarn audit"; PM_OUTDATED="yarn outdated"; PM_WHY="yarn why"
else
  PM="npm"; PM_INSTALL="npm install"; PM_ADD="npm install"; PM_REMOVE="npm uninstall"
  PM_AUDIT="npm audit"; PM_OUTDATED="npm outdated"; PM_WHY="npm why"
fi

echo "📦 Package manager: $PM"
```

### 0.3 Check for Resumable Report

```bash
LATEST=$(ls -t .deps-reports/deps-*.md 2>/dev/null | head -1)
if [ -n "$LATEST" ]; then
  AGE=$(( $(date +%s) - $(stat -f %m "$LATEST") ))
  if [ "$AGE" -lt 3600 ] && ! grep -q "🟢 COMPLETE" "$LATEST"; then
    REPORT_FILE="$LATEST"
    RESUMING=true
  fi
fi
```

If resuming: read the report, find last completed step in Progress Log, skip to next.

### 0.4 Baseline Metrics

```bash
BASELINE_DIRECT=$(jq '.dependencies | length' package.json 2>/dev/null || echo 0)
BASELINE_DEV=$(jq '.devDependencies | length' package.json 2>/dev/null || echo 0)
BASELINE_TOTAL=$((BASELINE_DIRECT + BASELINE_DEV))
BASELINE_SIZE=$(du -sh node_modules 2>/dev/null | cut -f1 || echo "unknown")
```

### 0.5 Initialize Report File (Skip if Resuming)

**Write this to disk IMMEDIATELY:**

```markdown
# Dependency Audit Report — [PROJECT_NAME]

**Date:** YYYY-MM-DD HH:MM
**Status:** 🔴 IN PROGRESS — Phase 0: Setup
**Package Manager:** [pm]
**Packages:** [direct] direct + [dev] dev = [total] total
**node_modules:** [size]

---

## Progress Log

| Time | Phase | Action | Result |
|------|-------|--------|--------|
| [HH:MM] | Phase 0 | Setup | [total] packages, [size] node_modules |

---

## Findings

| ID | Severity | Category | Package | Issue | Status |
|----|----------|----------|---------|-------|--------|

---

## Update Log

| ID | Package | From | To | Type | Attempt | Build | Test | Status |
|----|---------|------|----|------|---------|-------|------|--------|

---

> Reference: [SITREP Standard](~/.claude/standards/SITREP_FORMAT.md) — use the unified template with domain-specific additions below.

## SITREP

_To be populated as updates are applied_

### What Was Fixed
_Updated in real-time_

### What Was Deferred (and Why)
_Each deferred item with full explanation_

### What Was Blocked (and Why)
_Each blocked item with all attempts documented_
```

**IMPORTANT:** This file is written to disk NOW. Every subsequent phase updates this same file.

---

## PHASE 1: AUDIT (4 Parallel Agents)

### AGENT 1: Security Vulnerabilities

**Run security audit:**
```bash
$PM_AUDIT --json > .deps-reports/audit-raw.json 2>&1 || true
```

**Check for:**

| Severity | Description | Action |
|----------|-------------|--------|
| CRITICAL | Known exploit, actively attacked | Auto-fix immediately |
| HIGH | Severe vulnerability, exploit possible | Auto-fix |
| MEDIUM | Vulnerability, exploit difficult | Auto-fix if safe |
| LOW | Minor issue, theoretical risk | Report only |

**Parse vulnerabilities:**
```javascript
// For each vulnerability:
{
  "id": "DEP-SEC-001",
  "severity": "critical",
  "package": "lodash",
  "vulnerability": "Prototype Pollution",
  "cve": "CVE-2021-23337",
  "cvss": 7.4,
  "installedVersion": "4.17.15",
  "fixedVersion": "4.17.21",
  "path": "lodash > express > ...",
  "autoFixable": true
}
```

**Supply chain checks:**

| Check | What It Detects |
|-------|-----------------|
| Postinstall scripts | Suspicious `curl`, `wget`, `eval`, `base64` in package.json scripts |
| Typosquatting | Package names similar to popular packages (lodahs, recat, expres) |
| Malicious packages | Known malicious packages (check against npm advisory database) |
| Unmaintained | No commits in 2+ years + known vulnerabilities |
| Deprecated | Officially deprecated packages |

```bash
# Check for suspicious postinstall scripts
find node_modules -name "package.json" -exec grep -l '"postinstall"\|"preinstall"' {} \; | \
  xargs grep -l 'curl\|wget\|eval\|base64\|nc \|/dev/tcp' 2>/dev/null
```

---

### AGENT 2: Outdated Packages

**Check for updates:**
```bash
$PM_OUTDATED --json > .deps-reports/outdated-raw.json 2>&1 || true
```

**Categorize updates:**

| Type | Example | Risk | Auto-Update |
|------|---------|------|-------------|
| Patch | 1.2.3 → 1.2.4 | Low (bug fixes only) | Yes |
| Minor | 1.2.3 → 1.3.0 | Medium (new features, backwards compatible) | Yes (default) |
| Major | 1.2.3 → 2.0.0 | High (breaking changes) | No (flag) |

**For each outdated package:**
```javascript
{
  "id": "DEP-OUT-001",
  "package": "next",
  "current": "14.0.0",
  "wanted": "14.2.5",
  "latest": "15.0.0",
  "updateType": "minor",  // or "patch" or "major"
  "changelog": "https://github.com/vercel/next.js/releases",
  "breaking": false,
  "autoUpdate": true
}
```

**Check changelogs for breaking changes:**
- Read CHANGELOG.md if available
- Check GitHub releases for "BREAKING" mentions
- Flag packages with migration guides

---

### AGENT 3: License Compliance

**Extract all licenses:**
```bash
npx license-checker --json > .deps-reports/licenses-raw.json 2>&1 || true
```

**License categories:**

| Category | Licenses | Commercial Use | Action |
|----------|----------|----------------|--------|
| Permissive | MIT, Apache-2.0, BSD, ISC | ✅ Safe | OK |
| Weak Copyleft | LGPL, MPL | ⚠️ Conditions | Review |
| Strong Copyleft | GPL, AGPL | ❌ Viral | FLAG |
| Proprietary | Commercial, Custom | ❌ May require license | FLAG |
| Unknown | No license found | ⚠️ Risk | FLAG |

**Check for:**
- GPL "contamination" (GPL dependency makes your code GPL)
- AGPL in server-side code (triggers copyleft)
- Missing licenses (legal risk)
- License incompatibilities

```javascript
{
  "id": "DEP-LIC-001",
  "severity": "high",
  "package": "some-gpl-package",
  "license": "GPL-3.0",
  "category": "strong-copyleft",
  "risk": "May require open-sourcing your code",
  "recommendation": "Find MIT/Apache alternative"
}
```

---

### AGENT 4: Dependency Health

**Check for unused dependencies:**
```bash
npx depcheck --json > .deps-reports/depcheck-raw.json 2>&1 || true
```

**Unused dependencies:**
- Listed in package.json but never imported
- Cost: download time, disk space, audit noise, security surface

**Missing dependencies:**
- Imported in code but not in package.json (relying on transitive)
- Risk: can break when transitive dep updates

**Duplicate dependencies:**
```bash
$PM_INSTALL --check-duplicates 2>&1 || true
# or
npx npm-dedupe --list
```

**Circular dependencies:**
```bash
npx madge --circular --json . > .deps-reports/circular.json 2>&1 || true
```

**Package size analysis:**
```bash
npx package-size-analyzer > .deps-reports/size-analysis.json 2>&1 || true
```

**Health metrics per package:**
```javascript
{
  "id": "DEP-HEALTH-001",
  "package": "moment",
  "issues": [
    "Deprecated (use date-fns or dayjs)",
    "Large bundle size (67kB minified)",
    "No tree-shaking support"
  ],
  "alternative": "date-fns",
  "severity": "medium"
}
```

---

### Status Update: Every 5 Minutes

```
═══════════════════════════════════════════════════════════════
⏳ DEPENDENCY AUDIT IN PROGRESS — 5:00 elapsed
═══════════════════════════════════════════════════════════════
Agent 1 (Security):  ████████████ 100% — 3 vulnerabilities found
Agent 2 (Outdated):  ████████░░░░ 80% — 45 packages checked
Agent 3 (Licenses):  ████████████ 100% — All permissive ✅
Agent 4 (Health):    ██████░░░░░░ 60% — Checking unused...

Findings so far: 8 (2 CRIT, 1 HIGH, 3 MED, 2 LOW)
═══════════════════════════════════════════════════════════════
```

### After All Agents Complete

1. **Add ALL findings to report `## Findings` table** with status `FOUND`
2. **Append to Progress Log:** `| [HH:MM] | Phase 1 | Audit complete | [X] findings across [Y] agents |`
3. **Update Status:** `🔴 IN PROGRESS — Phase 2: Update`
4. **Write report to disk** — checkpoint between audit and update

---

## PHASE 2: UPDATE (Sequential, Safe First)

### Update Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    UPDATE SEQUENCE                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. SECURITY FIXES (Critical/High)                          │
│     └── Always apply, verify build                          │
│                                                             │
│  2. PATCH UPDATES (x.x.PATCH)                               │
│     └── Auto-apply all, verify build                        │
│                                                             │
│  3. MINOR UPDATES (x.MINOR.x)                               │
│     └── Auto-apply, verify build + tests                    │
│                                                             │
│  4. MAJOR UPDATES (MAJOR.x.x)                               │
│     └── Flag for review (or auto if --update-all)           │
│                                                             │
│  After each batch: BUILD → TEST → CONTINUE or ROLLBACK      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Living Update Cycle (Per-Package)

**For EVERY package update in sections 2.1-2.4, follow this cycle:**

1. **Update finding row** in `## Findings` → `🔧 UPDATING`
2. **Add row** to `## Update Log` → `Attempt 1`
3. **Update report header** Status → `🟡 FIXING — [DEP-XXX] [package]@[version]`
4. **Write report to disk**
5. **Apply the update** (`$PM_ADD "$pkg@$version"`)
6. **Verify build** (`$PM_RUN build`)
7. **If build fails:**
   - Revert: `git checkout -- package.json *lock* && $PM_INSTALL`
   - If attempt < 3: try different version (e.g., pin to `^current+1`), go to step 5
   - If attempt 3: mark `🚫 BLOCKED`, add SITREP entry with all 3 attempts, **write to disk**, next package
8. **Verify tests** (if available): `$PM_RUN test`
9. **If tests fail:**
   - Revert and retry (same 3-attempt logic as build failure)
10. **Mark `✅ FIXED`** in both `## Findings` and `## Update Log`
11. **Add Progress Log entry:** `| [HH:MM] | Phase 2 | Updated [package] | [from] → [to] ✅ |`
12. **Write report to disk**
13. **Next package**

### 2.1 Security Fixes

**Priority: CRITICAL → HIGH → MEDIUM** (skip LOW for auto-fix)

```bash
# Try automatic fix first
$PM_AUDIT fix 2>&1 || true
```

If audit fix doesn't resolve everything, manually update each remaining vulnerability using the Living Update Cycle above. For each:
- Record the CVE and fix version in Update Log
- If the only fix is a major version bump, mark `⏸️ DEFERRED` with reason

### 2.2 Patch Updates

Apply all patch updates using the Living Update Cycle. Patches can be batched (all at once) for the first attempt, but if the batch fails, fall back to one-at-a-time to isolate the culprit.

### 2.3 Minor Updates

Apply minor updates **one at a time** using the Living Update Cycle. Each package gets its own build + test verification. More risky than patches — isolate failures.

### 2.4 Major Updates

**Default behavior (flag for human):** Mark each as `⏸️ DEFERRED` in the findings table with reason: "Major version — breaking changes, requires human review." Add SITREP entry listing each deferred major update with changelog link.

**With --update-all flag:** Apply each major update using the Living Update Cycle. These are most likely to fail — the 3-attempt limit is especially important here.

---

## PHASE 3: CLEANUP

**Update report header:** `🔴 IN PROGRESS — Phase 3: Cleanup`
**Write to disk.**

### 3.1 Remove Unused Dependencies

For each unused dependency found by Agent 4:

1. **Update finding row** → `🗑️ REMOVED` (optimistic)
2. **Write report to disk**
3. Remove: `$PM_REMOVE "$pkg"`
4. Verify build: `$PM_RUN build`
5. **If build fails:** revert, mark `🚫 BLOCKED` with reason "Removal broke build — likely used via re-export or dynamic import", **write to disk**
6. **If build passes:** confirm `🗑️ REMOVED`, add Progress Log entry, **write to disk**

### 3.2 Dedupe Dependencies

```bash
if [ "$PM" = "npm" ]; then npm dedupe
elif [ "$PM" = "pnpm" ]; then pnpm dedupe
elif [ "$PM" = "yarn" ]; then yarn dedupe
fi
```

Add Progress Log entry: `| [HH:MM] | Phase 3 | Dedupe | [result] |`
**Write to disk.**

### 3.3 Final Verification

```bash
$PM_RUN build && ($PM_RUN test 2>/dev/null || true) && ($PM_RUN typecheck 2>/dev/null || npx tsc --noEmit)
```

Add Progress Log entry: `| [HH:MM] | Phase 3 | Final verification | Build ✅ / Tests ✅ / Types ✅ |`
**Write to disk.**

---

## PHASE 4: FINALIZE REPORT

The report has been updated incrementally throughout Phases 1-3. Now finalize it.

### 4.1 Compute Before/After Metrics

```bash
FINAL_DIRECT=$(jq '.dependencies | length' package.json 2>/dev/null || echo 0)
FINAL_DEV=$(jq '.devDependencies | length' package.json 2>/dev/null || echo 0)
FINAL_TOTAL=$((FINAL_DIRECT + FINAL_DEV))
FINAL_SIZE=$(du -sh node_modules 2>/dev/null | cut -f1 || echo "unknown")
```

### 4.2 Add Before/After Comparison to Report

Add a `## Before/After` section with baseline vs final metrics (packages, size, vulnerabilities, outdated counts).

### 4.3 Finalize SITREP

Review and finalize the three SITREP subsections:

- **What Was Fixed** — count and list all `✅ FIXED` and `🗑️ REMOVED` items
- **What Was Deferred (and Why)** — each `⏸️ DEFERRED` with full explanation (major version, breaking changes, needs human review, etc.)
- **What Was Blocked (and Why)** — each `🚫 BLOCKED` with all 3 attempts documented (what was tried, what error occurred, what would be needed to resolve)

### 4.4 Update Report Header

```markdown
**Status:** 🟢 COMPLETE
```

Add final Progress Log entry: `| [HH:MM] | Phase 4 | Finalized | [X] fixed, [Y] deferred, [Z] blocked |`
**Write report to disk.**

### 4.5 Console Summary

```
═══════════════════════════════════════════════════════════════════════════════
🎉 /deps COMPLETE
═══════════════════════════════════════════════════════════════════════════════

⏱️ Total Duration: [X] minutes [Y] seconds

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Total Packages | [X] | [Y] | [diff] |
| node_modules | [size] | [size] | [diff] |
| Vulnerabilities | [X] | [Y] | [diff] |

| Status | Count |
|--------|-------|
| ✅ FIXED | [X] |
| 🗑️ REMOVED | [X] |
| ⏸️ DEFERRED | [X] |
| 🚫 BLOCKED | [X] |
| ✅ OK | [X] |

📁 Report: .deps-reports/deps-[timestamp].md

═══════════════════════════════════════════════════════════════════════════════
```

### 4.6 Next Action Table

| Condition | Recommendation |
|-----------|----------------|
| All findings ✅ FIXED or ✅ OK | Ready to ship → `/gh-ship` |
| ⏸️ DEFERRED items exist | Review deferred majors manually, then `/deps --update-all` |
| 🚫 BLOCKED items exist | Investigate blocked items — see SITREP for details |
| License flags remain | Review flagged licenses with legal/team before shipping |

---

## Rollback Procedure

```bash
echo "🔄 Rolling back to pre-deps state..."
git reset --hard $DEPS_BASE
rm -rf node_modules
$PM_INSTALL
echo "✅ Rolled back to: $DEPS_BASE"
```

---

## Human Intervention Triggers

Only ask for human input when:

| Trigger | Reason |
|---------|--------|
| Major version update | Breaking changes require code review |
| GPL/AGPL license found | Legal decision needed |
| Security fix breaks build | Manual resolution needed |
| Package has no alternative | Business decision on risk acceptance |

---

## Important Notes

- **Report IS the single source of truth** — written to disk after every status change, survives session compaction/restart
- **Every finding gets a status** — FOUND → 🔧 UPDATING → ✅ FIXED / ⏸️ DEFERRED / 🚫 BLOCKED / 🗑️ REMOVED / ✅ OK
- **3 attempts max** before marking BLOCKED — each attempt documented in SITREP
- **SITREP annotates everything** — what was updated, deferred (and WHY), blocked (and WHY with all attempts)
- **Fully autonomous** for patch/minor updates and security fixes
- **Verifies after every change** — build and tests must pass
- **Rollback on failure** — no broken state left behind
- **License compliance** built-in — catches legal issues early
- **Supply chain security** — detects malicious packages
- Run weekly to stay ahead of vulnerabilities
- Run before deployments for peace of mind

## RELATED SKILLS

**Feeds from:**
- (none - /deps is typically run proactively or as part of launch readiness)

**Feeds into:**
- `/gh-ship` - once all dependencies are updated and clean, ship with gh-ship
- `/test-ship` - dep updates may break tests; run test-ship after major updates to verify coverage
- `/sec-ship` - security vulnerabilities found by deps feed into sec-ship for full remediation context

**Pairs with:**
- `/sec-ship` - run together when security is the priority; deps handles supply chain, sec-ship handles application code
- `/migrate` - when deps flags a major version upgrade, migrate handles the actual breaking-change migration
- `/launch` - deps is one of 8 skills orchestrated by launch readiness; pre-launch deps sweep is mandatory

**Auto-suggest after completion:**
When all findings are FIXED or OK, suggest: `/gh-ship` to commit the dependency updates; if major versions were deferred, suggest `/migrate` for each one

---

## CLEANUP PROTOCOL

> Reference: [Resource Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md)

### Deps-Specific Cleanup

Cleanup actions:
1. **Orphan file:** Delete `.deps-audit.json` from project root after data is captured in `.deps-reports/`
2. **Gitignore enforcement:** Ensure `.deps-reports/` is in `.gitignore`
3. **Pre-deps snapshot commit:** The `chore: pre-deps snapshot` commit persists in git history (this is intentional for rollback safety)

<!-- Claude Code Skill by Steel Motion LLC — https://steelmotion.dev -->
<!-- Part of the Claude Code Skills Collection -->
<!-- Powered by Claude models: Haiku (fast extraction), Sonnet (balanced reasoning), Opus (deep analysis) -->
<!-- License: MIT -->
