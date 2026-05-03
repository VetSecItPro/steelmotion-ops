---

> **Standards inherited** (apply throughout this skill):
> - [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md)
> - [Self-Improvement Protocol](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) — log to .migrate-history.json
> - [Multi-Repo Awareness](~/.claude/standards/MULTI_REPO_AWARENESS.md)
> - [Verify Before Destroy](~/.claude/standards/VERIFY_BEFORE_DESTROY.md)

description: "/migrate -- Major Version Upgrade: analyze breaking changes, update dependencies, migrate code patterns, verify everything works"
allowed-tools: Bash(cat:*), Bash(ls:*), Bash(find:*), Bash(wc:*), Bash(curl:*), Bash(node:*), Bash(npx:*), Bash(npm:*), Bash(bun:*), Bash(pnpm:*), Bash(yarn:*), Bash(git:*), Bash(jq:*), Bash(date:*), Bash(mkdir:*), Bash(touch:*), Bash(head:*), Bash(tail:*), Bash(grep:*), Bash(sort:*), Bash(uniq:*), Bash(gh:*), Bash(sed:*), Read, Write, Edit, Glob, Grep, Task, WebFetch, WebSearch
---

# /migrate — Major Version Upgrade

**Purpose:** Automate major version upgrades with rollback safety. Not just "update the version number" but the full migration: analyze breaking changes, update code patterns, verify everything works, document everything.

**Philosophy:**
1. Safety first — always on a new branch, always with rollback plan
2. Research-driven — fetch official migration guides, don't guess breaking changes
3. Systematic — handle every breaking change, not just the obvious ones
4. Verify relentlessly — build, type-check, test after every change
5. Document everything — future you will want to know what changed and why

<!--
## Design Rationale

### When to use /migrate
- Major version upgrades (Next.js 14→15, React 18→19, Tailwind 3→4, etc.)
- Minor versions with significant breaking changes
- Framework migrations (CRA→Vite, Express→Fastify, etc.)
- Runtime upgrades (Node.js 20→22)
- When /deps flags a major version update as available

### When NOT to use /migrate
- Patch version updates (use /deps)
- Minor version updates without breaking changes (use /deps)
- Adding new dependencies (just install them)
- Dependency security fixes (use /deps or /sec-ship)

### Flow
```
  /migrate next@15
     │
     ▼
  ┌──────────────────────────────────┐
  │  Stage 0: Initialization         │─── Parse target, create branch, create report
  │  Stage 1: Breaking Changes       │─── Fetch migration guide, identify all breaking changes
  │  Stage 2: Impact Assessment      │─── Scan codebase for affected patterns
  │  Stage 3: Migration Plan         │─── Prioritize changes, build execution order
  │  Stage 4: Dependency Updates     │─── Update package versions, resolve conflicts
  │  Stage 5: Code Migration         │─── Apply code changes file by file
  │  Stage 6: Build & Test Loop      │─── Iterative: build → fix → test → fix → repeat
  │  Stage 7: Validation             │─── Full build, lint, type-check, test suite
  │  Stage 8: Report & Rollback Plan │─── Document changes, provide rollback instructions
  └──────────────────────────────────┘
     │
     ▼
  .migrate-reports/MIG-[package]-[version]-YYYYMMDD.md
  Branch: migrate/[package]-[version]-YYYYMMDD
```

### Key Design Decisions
1. Git branch is MANDATORY — never migrate on current branch
2. Web fetch for migration guides — skill knowledge is a starting point, not the source of truth
3. Checkpoint commits after each stage — partial progress is preserved
4. Iterative fix loop (max 10 iterations) — build → fix → build until clean
5. Dry-run mode — full analysis without touching files, essential for effort estimation
6. Rollback is always possible — git branch + checkpoint commits = easy undo
-->

---

## DISCIPLINE

> Reference: [Superpowers Discipline Protocol](~/.claude/standards/STEEL_DISCIPLINE.md)

Key enforcements for this skill:
- **Steel Principle #1:** NO completion claims without fresh verification evidence — build, type-check, full test suite pass on a real run
- **Steel Principle #2:** NO guessing breaking changes; fetch the official migration guide every time
- **Steel Principle #3:** NO scope creep — migrate only the target version; other cleanup waits

### Migrate-Specific Rationalization Table

| Rationalization | Reality | What to Do |
|----------------|---------|------------|
| "While I'm here, I'll also refactor X" | Scope creep makes rollback impossible when the migration fails | One migration at a time; refactors are separate PRs |
| "This change is safe, skip the test" | Safe-looking API updates break runtime behavior silently | Run full tests after every affected file change |
| "I know the breaking changes, skip the guide" | Official guides list edge cases you've forgotten; deprecations become errors across minors | Fetch the migration guide, check every item |
| "Only 10 files touched, no need for a branch" | Mid-migration failure on main blocks the team; branch + checkpoint is free insurance | Always on a fresh branch with checkpoint commits |

---

## STATUS UPDATES

> Reference: [Status Update Protocol](~/.claude/standards/STATUS_UPDATES.md)

Provide status updates every 30-60 seconds during active migration work.

### Migration-Specific Status Examples

```
📋 Stage 0/8 — Initialization
   ├─ Target: next@15 (currently on 14.2.5)
   ├─ Creating branch: migrate/next-15-20260224
   └─ Report: .migrate-reports/MIG-next-15-20260224.md

🔍 Stage 1/8 — Breaking Change Analysis
   ├─ Fetching Next.js 15 migration guide...
   ├─ Identified 12 breaking changes relevant to this codebase
   └─ 3 high-impact, 5 medium-impact, 4 low-impact

📊 Stage 2/8 — Impact Assessment [scanning]
   ├─ 47 files affected by breaking changes
   ├─ Highest impact: async request APIs (23 files)
   ├─ Second: new caching defaults (12 files)
   └─ Building migration plan...

🔧 Stage 5/8 — Code Migration [14/47 files]
   ├─ Migrating async request API patterns...
   ├─ ✅ 14 files updated
   ├─ ⚠️ 2 files need manual review (complex patterns)
   └─ Committing checkpoint...

🔄 Stage 6/8 — Build & Test Loop [iteration 2/10]
   ├─ Build: ❌ 3 type errors remaining
   ├─ Fixing type errors...
   ├─ Previous iteration: 8 errors → 3 errors
   └─ Progress: 62% of errors resolved

✅ Stage 8/8 — Migration Complete
   ├─ Migration Score: 94/100 (A)
   ├─ 47 files migrated, 0 breaking changes remaining
   ├─ Branch: migrate/next-15-20260224
   ├─ All tests passing (48/48)
   └─ Report: .migrate-reports/MIG-next-15-20260224.md
```

---

## CONTEXT MANAGEMENT

> Reference: [Context Management Protocol](~/.claude/standards/CONTEXT_MANAGEMENT.md)

### Migration-Specific Context Rules

1. **Sub-agents return < 500 tokens.** Full analysis writes to `.migrate-reports/` files.
2. **State file:** `.migrate-reports/state-YYYYMMDD-HHMMSS.json` — updated after every stage.
3. **Resume protocol:** Check for incomplete migration from last 2 hours. Also check for existing migration branch.
4. **Max 2 parallel scout agents** for impact assessment. Code migration is ALWAYS sequential.
5. **Checkpoint commits after every stage** — if context resets, `git log` shows progress.
6. **Orchestrator never reads full agent output** — only return summaries.
7. **Migration guide content cached to disk** — `.migrate-reports/migration-guide.md` — never re-fetch.

---

## AGENT ORCHESTRATION

> Reference: [Agent Orchestration Protocol](~/.claude/standards/AGENT_ORCHESTRATION.md)

### Model Selection Table

| Agent | Model | Rationale |
|-------|-------|-----------|
| Breaking Change Research | sonnet | Web research + document parsing |
| Breaking Change Relevance Filter | sonnet | Match breaking changes to codebase patterns |
| Impact Scanner (batch 1) | sonnet | Pattern search across files |
| Impact Scanner (batch 2) | sonnet | Pattern search across files |
| Dependency Resolver | sonnet | Resolve version conflicts, peer deps |
| Code Migrator (per file/batch) | sonnet | Apply code transformations |
| Build Error Fixer | sonnet | Parse build errors + apply fixes |
| Test Error Fixer | sonnet | Parse test failures + apply fixes |
| Validation | sonnet | Comprehensive verification |

### Agent Batching Rules

| Codebase Size | Affected Files | Batch Strategy |
|--------------|---------------|----------------|
| Small (< 20 affected) | < 20 | Single agent for code migration |
| Medium (20-50 affected) | 20-50 | Batch files by change type |
| Large (50+ affected) | 50+ | Batch by feature area, 2 parallel scouts, sequential fixers |

---

## REPORT PERSISTENCE

### Finding Lifecycle

Every migration item follows this lifecycle:

```
IDENTIFIED → PLANNED → MIGRATING → MIGRATED | MANUAL | DEFERRED | BLOCKED
```

- **IDENTIFIED**: Breaking change found in migration guide
- **PLANNED**: Impact assessed, files identified, execution order determined
- **MIGRATING**: Code change in progress
- **MIGRATED**: Change applied and verified (build + type-check pass)
- **MANUAL**: Requires human review (complex pattern, ambiguous transformation)
- **DEFERRED**: Skipped for now (low priority, can address later)
- **BLOCKED**: Cannot migrate (dependency conflict, missing feature in new version)

### Persistence Rules

1. Report file created at Stage 0, updated after every stage
2. State file updated after every stage with machine-readable progress
3. Breaking changes are tracked individually with IDs: `MIG-[seq]` (e.g., `MIG-001`)
4. Checkpoint commits preserve progress on the migration branch
5. Migration guide content is cached to disk (never re-fetched)
6. Every file modification is tracked with before/after context

### Resume Protocol

Before starting a migration:
1. Check for existing `migrate/[package]-*` branch
2. Check for `.migrate-reports/state-*.json` from last 2 hours
3. If found, offer to resume from last checkpoint commit
4. If resuming, `git log` on migration branch reveals completed stages
5. If starting fresh, ensure no conflicting migration branch exists

---

## HUMAN DECISION TRIGGERS

**Pause and ask the user before proceeding if:**

1. **Multiple major versions to skip** (e.g., React 17→19) — migration path may differ
2. **Peer dependency conflict cannot be auto-resolved** — user must choose which dep to keep/update
3. **Breaking change requires architectural decision** (e.g., migration from Pages Router to App Router)
4. **Migration guide mentions data migration** — any data changes need explicit approval
5. **10 build fix iterations exhausted** — something fundamentally wrong, need human guidance
6. **Dry-run reveals >100 affected files** — confirm user wants to proceed with large migration
7. **Deprecated API has no 1:1 replacement** — user must choose migration strategy
8. **Test suite has <50% coverage** — warn that migration verification is limited

---

## RUN MODES

```
/migrate next@15                    # Full migration (default)
/migrate react@19 --dry-run         # Analyze impact without making changes
/migrate tailwind@4 --no-fix        # Update deps only, list required code changes
/migrate next@15 --rollback         # Revert a previous migration (uses git)
/migrate --assess                   # Show what's outdated and migration complexity
```

### Mode Behavior

| Mode | Stages Run | What Happens |
|------|-----------|-------------|
| Full (default) | 0-8 | Complete migration end-to-end |
| `--dry-run` | 0-3 | Full analysis, zero file changes. Outputs impact report |
| `--no-fix` | 0-4 | Update deps, list all code changes needed but don't apply them |
| `--rollback` | Special | Delete migration branch, restore to pre-migration state |
| `--assess` | Special | Quick scan: what's outdated, estimated effort per upgrade |

### Assess Mode

`/migrate --assess` provides a quick overview without targeting a specific package:

```markdown
## Dependency Upgrade Assessment

| Package | Current | Latest | Breaking Changes | Affected Files | Effort |
|---------|---------|--------|-----------------|---------------|--------|
| next | 14.2.5 | 15.1.0 | 12 | ~47 files | High |
| react | 18.3.1 | 19.0.0 | 8 | ~30 files | Medium |
| tailwindcss | 3.4.1 | 4.0.0 | 15 | ~60 files | High |
| typescript | 5.3.3 | 5.7.0 | 3 | ~5 files | Low |

Recommended migration order:
1. typescript@5.7 (low effort, improves tooling)
2. react@19 (medium effort, prerequisite for next@15)
3. next@15 (high effort, depends on react@19)
4. tailwindcss@4 (high effort, independent)
```

---

## CRITICAL RULES

1. **ALWAYS create a new git branch.** Never migrate on main or current branch. Branch name: `migrate/[package]-[version]-YYYYMMDD`.
2. **Fetch the official migration guide.** Do not rely solely on built-in knowledge. WebSearch + WebFetch the official docs.
3. **Checkpoint commit after every stage.** Message: `chore(migrate): stage N — [description]`. Partial progress is preserved.
4. **Build verification after every code change batch.** Don't accumulate errors. Fix as you go.
5. **Type-check is a gate.** Zero TypeScript errors before proceeding to runtime testing.
6. **Max 10 iterations in build-fix loop (Stage 6).** After 10, escalate to human.
7. **Dry-run mode is sacred.** When `--dry-run`, NEVER modify any file. Analysis only.
8. **Rollback plan in every report.** Exact git commands to undo the migration.
9. **Report is the single source of truth.** Updated after every stage.
10. **Sub-agents return < 500 tokens.** Full analysis writes to disk.
11. **Status updates every 30-60 seconds.** Migrations are long-running — keep the user informed.
12. **Handle peer dependency conflicts explicitly.** Don't force-install. Resolve properly.
13. **Respect existing code style.** Migrated code should match the project's conventions.
14. **This is a GLOBAL skill.** Works on any project, any framework, any package manager.
15. **Create `.migrate-reports/` directory and ensure it's gitignored.**

---

## SCORING SYSTEM

### Migration Score (Weighted)

| Category | Weight | What's Measured | Scoring Criteria |
|----------|--------|----------------|-----------------|
| Dependency Resolution | 15% | All deps updated, no conflicts | 100: clean install. -10 per warning. -25 per unresolved conflict. 0 if install fails |
| Breaking Changes Resolved | 30% | All identified changes addressed | 100: all MIGRATED. -5 per MANUAL. -10 per DEFERRED. -20 per BLOCKED |
| Build Health | 20% | Clean build with zero errors | 100: zero errors. -5 per warning. 0 if build fails |
| Type Safety | 15% | Zero TypeScript errors | 100: zero errors. -3 per error. 0 if >20 errors |
| Test Suite | 15% | All existing tests pass | 100: all pass. -5 per failure. 0 if >20% failing |
| Lint Clean | 5% | No new lint violations | 100: clean. -2 per new violation. Score floored at 0 |

### Grade Scale

| Score | Grade | Migration Status |
|-------|-------|-----------------|
| 95-100 | A+ | Complete — ready to merge |
| 90-94 | A | Complete — minor items to review |
| 85-89 | B+ | Mostly complete — some manual items |
| 80-84 | B | Functional — review MANUAL items before merge |
| 70-79 | C | Incomplete — significant manual work remaining |
| 60-69 | D | Problematic — many unresolved breaking changes |
| 0-59 | F | Failed — consider rollback |

---

## KNOWN MIGRATION PATTERNS

Built-in knowledge for common upgrades. Always supplement with WebSearch for the official migration guide.

### Next.js 14 → 15

| Breaking Change | Pattern to Find | Migration |
|----------------|----------------|-----------|
| Async Request APIs | `cookies()`, `headers()`, `params`, `searchParams` used synchronously | Add `await` to all request API calls; update function signatures to `async` |
| `NextRequest` geo/ip | `request.geo`, `request.ip` | Move to `geolocation()` and `ipAddress()` from `@vercel/functions` |
| Caching defaults changed | `fetch()` calls without explicit cache option | Add explicit `cache: 'force-cache'` or `cache: 'no-store'` |
| `next/image` layout changes | `<Image>` with deprecated layout prop | Migrate to `width`/`height` or `fill` prop |
| Turbopack default in dev | `next dev` | Verify dev server works with Turbopack; if issues, use `--no-turbo` |

### React 18 → 19

| Breaking Change | Pattern to Find | Migration |
|----------------|----------------|-----------|
| `useActionState` replaces `useFormState` | `useFormState` imports | Replace with `useActionState` from `react` |
| `ref` as prop (no `forwardRef`) | `React.forwardRef` | Remove `forwardRef` wrapper, accept `ref` as prop |
| Suspense sibling behavior | `<Suspense>` with sibling elements | Review Suspense boundaries for new rendering behavior |
| `use()` hook | Custom promise-based patterns | Consider using `use()` for promise and context consumption |

### Tailwind CSS 3 → 4

| Breaking Change | Pattern to Find | Migration |
|----------------|----------------|-----------|
| CSS-first configuration | `tailwind.config.js/ts` | Migrate config to `@theme` directive in CSS |
| Renamed utilities | `bg-opacity-*`, `text-opacity-*`, `shadow-sm`, etc. | Use new utility names (e.g., `bg-black/50` for opacity) |
| Default style changes | `border-gray-200` (was default) | Explicitly set border colors where defaults changed |
| `@apply` behavior | `@apply` in CSS files | Review `@apply` usage for changed specificity |
| PostCSS plugin change | `require('tailwindcss')` in PostCSS config | Update to `@tailwindcss/postcss` |

### TypeScript 5.x Upgrades

| Breaking Change | Pattern to Find | Migration |
|----------------|----------------|-----------|
| `moduleResolution` changes | `tsconfig.json` module settings | Update to `bundler` or `nodenext` resolution |
| Isolated declarations | Complex type exports | Add explicit return types where needed |
| Deprecated compiler options | Removed `tsconfig` options | Remove deprecated options, use replacements |

### Node.js 20 → 22

| Breaking Change | Pattern to Find | Migration |
|----------------|----------------|-----------|
| ESM changes | `require()` in ESM contexts | Migrate to `import` or use `createRequire` |
| API deprecations | Deprecated Node.js APIs | Replace with recommended alternatives |
| `--experimental-*` flags | Flags in scripts | Remove flags for now-stable features |

---

## PRE-FLIGHT CHECKS (Stage 0 Sub-Steps)

Before any migration work begins:

1. **Parse migration target** — extract package name and target version from user input
2. **Detect current version** — read `package.json` for current installed version
3. **Verify version gap** — confirm this is a major (or significant minor) upgrade
4. **Check git state** — working tree must be clean (no uncommitted changes)
5. **Check for existing migration branch** — if `migrate/[package]-*` exists, offer to resume
6. **Check for previous migration reports** — scan `.migrate-reports/` for related reports
7. **Detect package manager** — npm, yarn, pnpm, or bun
8. **Verify build works** — run build before migration to establish baseline
9. **Run existing tests** — capture test baseline before migration
10. **Create report infrastructure** — mkdir `.migrate-reports/`, initialize report and state files

---

## STAGE 0: INITIALIZATION

### Actions

1. Parse migration target (`/migrate next@15` → package: `next`, version: `15`)
2. Read current version from `package.json`
3. Verify git working tree is clean
4. Create migration branch: `git checkout -b migrate/[package]-[version]-YYYYMMDD`
5. Run baseline build and tests (capture results)
6. Create report and state files
7. Initial commit on branch: `chore(migrate): initialize [package]@[version] migration`

### Report Template (Created at Stage 0)

```markdown
# Migration Report: [PACKAGE]@[VERSION]

**Run ID:** MIG-[package]-[version]-YYYYMMDD
**Date:** YYYY-MM-DD HH:MM:SS
**Branch:** migrate/[package]-[version]-YYYYMMDD
**Package Manager:** [npm|yarn|pnpm|bun]
**Current Version:** [X.Y.Z]
**Target Version:** [A.B.C]
**Mode:** [full | dry-run | no-fix | rollback | assess]

## Pre-Migration Baseline
- **Build:** ✅ | ❌
- **Type-check:** ✅ ([N] errors) | ❌
- **Tests:** [N]/[N] passing
- **Lint:** ✅ | ❌ ([N] warnings)

## Progress
- [ ] Stage 1: Breaking Change Analysis
- [ ] Stage 2: Impact Assessment
- [ ] Stage 3: Migration Plan
- [ ] Stage 4: Dependency Updates
- [ ] Stage 5: Code Migration
- [ ] Stage 6: Build & Test Loop
- [ ] Stage 7: Validation
- [ ] Stage 8: Report & Rollback Plan

## Breaking Changes
> Pending...

## Impact Assessment
> Pending...

## Migration Plan
> Pending...

## Code Changes
> Pending...

## Build & Test Log
> Pending...

## Migration Score
> Pending...

## Rollback Plan
> Pending...

> Reference: [SITREP Standard](~/.claude/standards/SITREP_FORMAT.md) — use the unified template with domain-specific additions below.

## SITREP
> Pending...
```

### State File Template

```json
{
  "skill": "migrate",
  "runId": "MIG-next-15-20260224",
  "project": "project-name",
  "package": "next",
  "currentVersion": "14.2.5",
  "targetVersion": "15.1.0",
  "branch": "migrate/next-15-20260224",
  "packageManager": "bun",
  "mode": "full",
  "started": "ISO-8601",
  "status": "in_progress",
  "stagesCompleted": [],
  "stagesRemaining": [1, 2, 3, 4, 5, 6, 7, 8],
  "breakingChanges": [],
  "affectedFiles": [],
  "buildIterations": 0,
  "lastCheckpoint": "ISO-8601"
}
```

---

## STAGE 1: BREAKING CHANGE ANALYSIS

**Agents:** 1-2 sonnet agents (research + relevance filtering)

### Actions

1. **Fetch official migration guide:**
   - WebSearch: `"[package] [version] migration guide official"`
   - WebFetch the official migration/upgrade page
   - Save content to `.migrate-reports/migration-guide.md`

2. **Fetch CHANGELOG:**
   - WebSearch: `"[package] [version] changelog breaking changes"`
   - Look for `CHANGELOG.md`, `BREAKING_CHANGES.md`, GitHub releases

3. **Extract breaking changes:**
   - Parse migration guide for all breaking changes
   - Categorize by impact level (HIGH / MEDIUM / LOW)
   - Note deprecated features vs removed features vs behavior changes

4. **Supplement with built-in knowledge:**
   - Check Known Migration Patterns section for this package
   - Merge any gaps not covered by the fetched guide

5. **Build breaking changes manifest:**

```markdown
### Breaking Changes Identified

| ID | Change | Impact | Category | Status |
|----|--------|--------|----------|--------|
| MIG-001 | Async request APIs | HIGH | API Change | IDENTIFIED |
| MIG-002 | Caching defaults | MEDIUM | Behavior Change | IDENTIFIED |
| MIG-003 | Image component layout | LOW | Deprecation | IDENTIFIED |
```

6. **Checkpoint commit:** `chore(migrate): stage 1 — breaking changes analyzed`

---

## STAGE 2: IMPACT ASSESSMENT

**Agents:** 2 sonnet agents (parallel scanning)

### Actions

1. **For each breaking change, scan codebase:**
   - Search for the pattern/API that's changing
   - Count affected files and occurrences
   - Note complexity of migration (simple find-replace vs. complex refactor)

2. **Build impact matrix:**

```markdown
### Impact Assessment

| ID | Change | Files Affected | Occurrences | Complexity | Effort |
|----|--------|---------------|-------------|------------|--------|
| MIG-001 | Async request APIs | 23 | 47 | Medium | ~30 min |
| MIG-002 | Caching defaults | 12 | 12 | Low | ~10 min |
| MIG-003 | Image layout prop | 3 | 5 | Low | ~5 min |
```

3. **Identify migration dependencies:**
   - Which changes must be applied before others?
   - Are there circular dependencies?
   - Build dependency graph

4. **Check for patterns NOT in the migration guide:**
   - Scan for usage of internal/undocumented APIs
   - Check for monkey-patching or workarounds that might break
   - Check for version-specific dependencies that need updating

5. **Trigger Human Decision if >100 affected files**

6. **Checkpoint commit:** `chore(migrate): stage 2 — impact assessed`

### Dry-Run Mode Exit Point

If `--dry-run` is active, **STOP HERE**. Output the impact report and migration plan without making any changes. Inform the user:

```
📊 Dry-Run Complete — No files were modified

Impact Summary:
- 12 breaking changes identified
- 47 files affected
- Estimated effort: ~2-3 hours

Full report: .migrate-reports/MIG-next-15-20260224.md
To proceed with migration: /migrate next@15
```

---

## STAGE 3: MIGRATION PLAN

**No agent needed — orchestrator builds the execution plan.**

### Actions

1. **Prioritize breaking changes:**
   - HIGH impact first (most files affected)
   - Respect dependency order (prerequisite changes first)
   - Group by file when possible (minimize file reopening)

2. **Build execution order:**

```markdown
### Migration Execution Plan

**Phase A: Prerequisite Changes (must be first)**
1. MIG-004: Update TypeScript config
2. MIG-006: Update import paths

**Phase B: High-Impact Changes**
3. MIG-001: Async request APIs (23 files)
4. MIG-002: Caching defaults (12 files)

**Phase C: Medium-Impact Changes**
5. MIG-005: Middleware changes (4 files)
6. MIG-007: Router changes (3 files)

**Phase D: Low-Impact Changes**
7. MIG-003: Image layout prop (3 files)
8. MIG-008: CSS module changes (2 files)
```

3. **Identify items requiring manual review:**
   - Complex patterns that can't be safely auto-migrated
   - Business logic that might be affected
   - Mark as MANUAL in the plan

4. **Update report with migration plan**

5. **Checkpoint commit:** `chore(migrate): stage 3 — migration plan created`

---

## STAGE 4: DEPENDENCY UPDATES

**Agent:** 1 sonnet agent

### Actions

1. **Update the target package:**
   ```
   [package-manager] add [package]@[version]
   ```

2. **Resolve peer dependency conflicts:**
   - Check for peer dep warnings
   - Update related packages as needed
   - If conflict cannot be auto-resolved, trigger Human Decision

3. **Update related packages:**
   - Packages that are commonly updated together (e.g., `next` + `eslint-config-next`)
   - Type definition packages (`@types/[package]`)
   - Plugin/extension packages

4. **Verify lockfile integrity:**
   - Run install to regenerate lockfile
   - Check for duplicate packages
   - Verify no security vulnerabilities introduced

5. **Verify install succeeds:**
   - Clean install must complete without errors
   - Warnings are acceptable but logged

6. **Checkpoint commit:** `chore(migrate): stage 4 — dependencies updated`

### No-Fix Mode Exit Point

If `--no-fix` is active, **STOP HERE**. Output the dependency changes and list of required code changes:

```
📦 Dependencies Updated — Code changes listed but not applied

Dependencies changed:
- next: 14.2.5 → 15.1.0
- eslint-config-next: 14.2.5 → 15.1.0

Required code changes: 47 files affected
Full list: .migrate-reports/MIG-next-15-20260224.md
To apply code changes: /migrate next@15
```

---

## STAGE 5: CODE MIGRATION

**Agents:** Sequential sonnet agents (1 per change batch)

### Actions

1. **Follow the migration plan from Stage 3 (Phase A → D)**

2. **For each breaking change:**
   a. Read all affected files
   b. Apply the transformation pattern
   c. Verify the change is correct (syntax check)
   d. Build after each batch to catch errors early

3. **Transformation approach by complexity:**

   **Simple (find-replace):**
   - Direct API renames, import path changes
   - Apply with Edit tool, verify with build

   **Medium (pattern transform):**
   - Adding `async`/`await`, changing function signatures
   - Apply carefully, respecting existing code patterns

   **Complex (restructure):**
   - Component restructuring, config migration
   - Apply one file at a time, build-verify each

4. **Track progress per breaking change:**

```markdown
### Code Migration Progress

| ID | Change | Files | Done | Status |
|----|--------|-------|------|--------|
| MIG-001 | Async request APIs | 23 | 23 | MIGRATED |
| MIG-002 | Caching defaults | 12 | 8 | MIGRATING |
| MIG-003 | Image layout | 3 | 0 | PLANNED |
```

5. **Build verification after each batch:**
   - Run `build` after every 5-10 files changed
   - If build fails, fix immediately before continuing
   - Do not accumulate errors across batches

6. **Mark MANUAL items:**
   - If a pattern is too complex or ambiguous to auto-migrate
   - Add a `// TODO: Manual migration required — [description]` comment
   - Document in report with explanation

7. **Checkpoint commits after each phase:**
   ```
   chore(migrate): stage 5A — prerequisite changes
   chore(migrate): stage 5B — async request APIs (23 files)
   chore(migrate): stage 5C — caching defaults (12 files)
   chore(migrate): stage 5D — remaining changes (8 files)
   ```

---

## STAGE 6: BUILD & TEST LOOP

**Agents:** Sequential sonnet agents (1 per iteration)

### Iterative Fix Loop

```
FOR iteration = 1 to 10:
  1. Run full build
     → IF passes: go to step 3
     → IF fails: collect errors, fix them, go to step 1

  2. Run type-check (if not part of build)
     → IF passes: continue
     → IF fails: fix type errors, go to step 1

  3. Run full test suite
     → IF all pass: EXIT LOOP — success
     → IF failures: analyze failures
       → If related to migration: fix and retry
       → If pre-existing failure: mark as PRE-EXISTING
       → Go to step 1

  4. Log iteration results

IF iteration > 10:
  → STOP
  → Mark remaining errors as BLOCKED
  → Trigger Human Decision
  → Document all 10 attempts
```

### Iteration Tracking

```markdown
### Build & Test Loop

| Iteration | Build | Type-Check | Tests | Errors Fixed | Remaining |
|-----------|-------|------------|-------|-------------|-----------|
| 1 | ❌ (8 errors) | — | — | — | 8 |
| 2 | ❌ (3 errors) | — | — | 5 fixed | 3 |
| 3 | ✅ | ✅ | ❌ (2 failures) | 3 fixed | 2 test failures |
| 4 | ✅ | ✅ | ✅ (48/48) | 2 fixed | 0 |
```

### Error Classification

| Error Type | Action | Example |
|-----------|--------|---------|
| Type error from migration | Fix immediately | Missing `await` causes type mismatch |
| Import error | Fix immediately | Moved/renamed export |
| Runtime error in test | Analyze — might be migration-related or pre-existing | |
| Build config error | Fix config | Webpack/Turbopack config change |
| Pre-existing failure | Mark as PRE-EXISTING, do not block migration | Test was failing before migration |

### Checkpoint Commits

After each successful iteration:
```
chore(migrate): stage 6 — iteration N (M errors remaining)
```

On final success:
```
chore(migrate): stage 6 — build and tests clean
```

---

## STAGE 7: VALIDATION

**Agent:** 1 sonnet agent

### Actions

1. **Full production build:**
   - `[package-manager] run build`
   - Must complete with zero errors
   - Warnings documented but not blocking

2. **Type-check:**
   - `npx tsc --noEmit` (or equivalent)
   - Zero TypeScript errors required

3. **Lint:**
   - `[package-manager] run lint`
   - No new lint violations (compare against baseline)
   - Update lint config if needed for new version

4. **Full test suite:**
   - Run all tests
   - All tests passing (except documented PRE-EXISTING failures)
   - No new test failures

5. **Manual verification checklist:**

```markdown
### Manual Verification Checklist
- [ ] Application starts without errors
- [ ] Key pages render correctly
- [ ] No console errors in browser
- [ ] API endpoints respond correctly
- [ ] Authentication flow works (if applicable)
- [ ] Dynamic routes resolve correctly
- [ ] Static generation works (if applicable)
- [ ] CSS/styling renders correctly
```

6. **Compare against pre-migration baseline:**
   - Same or better build time
   - Same or more tests passing
   - No new lint violations

7. **Checkpoint commit:** `chore(migrate): stage 7 — validation complete`

---

## STAGE 8: REPORT & ROLLBACK PLAN

**No agent needed — orchestrator finalizes the report.**

### Actions

1. **Calculate migration score:**
   - Apply scoring criteria from each category
   - Calculate weighted final score
   - Determine grade

2. **Document all changes:**
   - Files modified (with counts by change type)
   - Dependencies updated (with version changes)
   - Config files modified
   - Tests added or modified

3. **Generate rollback plan:**

```markdown
## Rollback Plan

If issues are discovered after merge, rollback with:

### Option A: Revert the Merge (Preferred)
\`\`\`bash
git revert [merge-commit-hash]
\`\`\`

### Option B: Full Branch Reset
\`\`\`bash
git checkout main
git branch -D migrate/[package]-[version]-YYYYMMDD
\`\`\`

### Option C: Partial Rollback (Checkpoint Commits)
\`\`\`bash
# Revert to specific stage checkpoint:
git log --oneline migrate/[package]-[version]-YYYYMMDD
git revert [checkpoint-commit]..HEAD
\`\`\`

### Dependency Rollback
\`\`\`bash
# Restore original package versions:
git checkout main -- package.json [lockfile]
[package-manager] install
\`\`\`
```

4. **Generate SITREP**

5. **Console summary:**

```
📊 Migration Complete: [package]@[version]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Migration Score: 94/100 (A)

Dependency Resolution:  100/100 (15%) ████████████████████████████
Breaking Changes:        90/100 (30%) ██████████████████████░░░░░░
Build Health:           100/100 (20%) ████████████████████████████
Type Safety:            100/100 (15%) ████████████████████████████
Test Suite:              90/100 (15%) ██████████████████████░░░░░░
Lint Clean:             100/100 (5%)  ████████████████████████████

Changes: 47 files modified, 2 MANUAL items
Branch: migrate/next-15-20260224
Report: .migrate-reports/MIG-next-15-20260224.md

Next steps:
1. Review MANUAL items in report
2. Run the app locally and verify key flows
3. Create PR: /gh-ship
```

6. **Final checkpoint commit:** `chore(migrate): stage 8 — migration complete, score [XX]/100`

---

## SITREP REQUIREMENTS

The SITREP section of the report must include:

### 1. Before/After Metrics Table

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| [Package] Version | 14.2.5 | 15.1.0 | Major upgrade |
| Build Status | ✅ | ✅ | No change |
| Type Errors | 0 | 0 | No change |
| Tests Passing | 48/48 | 48/48 | No change |
| Lint Warnings | 3 | 2 | -1 (removed deprecated rule) |
| Breaking Changes | — | 12 identified | 10 migrated, 2 manual |
| Files Modified | — | 47 | — |

### 2. What Was Accomplished

Summary of all migration work performed.

### 3. MANUAL Items (Require Human Review)

Each item with:
- File and line reference
- What needs to be decided
- Suggested approaches

### 4. Deferred and Why

Items skipped with conditions to revisit.

### 5. Blocked and Why

Items that could not be migrated with explanation.

### 6. Recommendations

- Post-migration testing suggestions
- Performance considerations with new version
- New features unlocked by the upgrade

### 7. Historical Context

- How long since last major upgrade of this package
- Any related upgrades that should follow

---

## DEFINITION OF DONE

A migration is complete when:

- [ ] Migration branch created with all checkpoint commits
- [ ] All identified breaking changes have a status (MIGRATED, MANUAL, DEFERRED, or BLOCKED)
- [ ] Build passes with zero errors
- [ ] Type-check passes with zero errors
- [ ] All tests pass (except documented PRE-EXISTING failures)
- [ ] Lint passes with no new violations
- [ ] Migration score calculated
- [ ] Report complete with all sections
- [ ] Rollback plan documented
- [ ] SITREP written with all required sections
- [ ] Console summary displayed
- [ ] Final checkpoint commit on migration branch

---

## OUTPUT STRUCTURE

```
.migrate-reports/
├── MIG-[package]-[version]-YYYYMMDD.md    # Main migration report
├── state-YYYYMMDD-HHMMSS.json             # Machine-readable state
├── migration-guide.md                      # Cached official migration guide
├── impact-analysis.json                    # Detailed file-by-file impact
└── history.json                            # Migration history
```

### History File Format

```json
{
  "migrations": [
    {
      "runId": "MIG-next-15-20260224",
      "date": "ISO-8601",
      "package": "next",
      "fromVersion": "14.2.5",
      "toVersion": "15.1.0",
      "score": 94,
      "grade": "A",
      "filesModified": 47,
      "breakingChanges": 12,
      "status": "complete",
      "branch": "migrate/next-15-20260224"
    }
  ]
}
```

### Gitignore

```bash
grep -q 'migrate-reports' .gitignore 2>/dev/null || echo '.migrate-reports/' >> .gitignore
```

---

## CROSS-SKILL INTEGRATION

### Skills That Feed Into /migrate
| Skill | What It Provides | Where to Check |
|-------|-----------------|----------------|
| `/deps` | Identifies outdated packages, recommends major upgrades | `.deps-reports/` |
| `/deps --assess` | Quick overview of what's outdated | — |

### Skills That /migrate Feeds Into
| Skill | When to Recommend | Trigger |
|-------|------------------|---------|
| `/gh-ship` | Create PR for the migration branch | After Stage 8 |
| `/qatest` | Full QA after major migration | After merge |
| `/monitor` | Post-deploy verification | After deploy |
| `/test-ship` | Expand test coverage for migrated code | If coverage gaps found |

---

## ERROR RECOVERY

### Git State Issues
1. If working tree is not clean, ask user to commit or stash changes
2. If migration branch already exists, offer to resume or start fresh
3. If branch diverged from main, rebase before continuing

### Build Loop Exhaustion (10 Iterations)
1. Stop the loop
2. Document all remaining errors
3. Mark remaining items as BLOCKED
4. Present to user with full context
5. Suggest: manual fix, rollback, or partial migration

### Peer Dependency Conflict
1. Document the conflict clearly
2. Present options to user (which version to use)
3. If user resolves, continue
4. If unresolvable, mark as BLOCKED, assess partial migration viability

### Context Reset
1. `git log --oneline` on migration branch to see checkpoint commits
2. Read state file for last completed stage
3. Read report for current findings
4. Resume from next stage after last checkpoint

### Package Manager Issues
1. Clear cache and retry: `[pm] cache clean`
2. Delete node_modules and lockfile, fresh install
3. If persists, try alternative install flags
4. Document in report

---

## CLEANUP PROTOCOL

> Reference: [Resource Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md)

### Migrate-Specific Cleanup

Resources this skill creates:
- Git branch (`migrate/[package]-[version]-YYYYMMDD`) — intentional, kept for user review
- Updated `node_modules/` — matches migration branch deps

Cleanup actions:
1. **Gitignore enforcement:** Already handled in Stage 0
2. **node_modules disclosure:** If user abandons migration and switches back to main, remind: "Run `[package-manager] install` on main to restore original dependencies"
3. **Migration branch:** Not auto-deleted — user merges via `/gh-ship` which handles branch cleanup

---

## REMEMBER

1. Always on a new branch. Never touch main. The migration branch is your safety net.
2. Fetch the official migration guide. Your built-in knowledge is a starting point, not the source of truth.
3. Build after every batch of changes. Don't accumulate errors. Fix as you go.
4. Checkpoint commits are your lifeline. If context resets, git log tells you where you were.
5. Type-check is a gate. Zero TypeScript errors before moving to runtime testing.
6. 10 iterations max in the build-fix loop. After that, it's a human problem.
7. Dry-run mode is for estimation. It helps users decide whether to commit to the migration.
8. The rollback plan is mandatory. Every migration report includes exact commands to undo everything.
9. Respect code style. Migrated code should look like it belongs in the project.
10. Major migrations are marathons, not sprints. Checkpoint often, report progress, and don't rush.

---

## RELATED SKILLS

**Feeds from:**
- `/deps` - dependency audit surfaces the packages that need migrating
- `/brainstorm` - migration strategy options are explored in brainstorm first for major upgrades

**Feeds into:**
- `/test-ship` - after migration, run full test suite to verify nothing regressed
- `/docs` - migration changes require updated docs for new APIs and patterns
- `/db` - library migrations sometimes require schema or query updates

**Pairs with:**
- `/deps` - run together: deps identifies the problem, migrate fixes it
- `/test-ship` - migrate and test-ship are always run together on major version upgrades

**Auto-suggest after completion:**
- `/test-ship` - "Migration complete. Run /test-ship to verify no regressions?"
- `/docs` - "Update docs to reflect new API patterns? Run /docs."

---

<!-- Claude Code Skill by Steel Motion LLC — https://steelmotion.dev -->
<!-- Part of the Claude Code Skills Collection -->
<!-- Powered by Claude models: Haiku (fast extraction), Sonnet (balanced reasoning), Opus (deep analysis) -->
<!-- License: MIT -->
