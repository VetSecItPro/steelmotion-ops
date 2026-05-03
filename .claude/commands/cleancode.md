# /cleancode — Technical Debt Reduction & Dead Code Elimination

> **Standards inherited** (apply throughout this skill):
> - [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md)
> - [Self-Improvement Protocol](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) — log to .cleancode-history.json
> - [Multi-Repo Awareness](~/.claude/standards/MULTI_REPO_AWARENESS.md)
> - [Verify Before Destroy](~/.claude/standards/VERIFY_BEFORE_DESTROY.md)
> - [Skill Auto-Suggest Protocol](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) — every SITREP ends with "Suggested next"


**Strategic codebase cleanup: dependency-graph-aware dead code removal, React/Next.js optimization, bundle reduction, pattern enforcement, and cruft elimination.**

**FIRE AND FORGET** — Execute the entire pipeline without waiting for user input. Status updates every 5 minutes. Clean thoroughly but safely.

<!--
═══════════════════════════════════════════════════════════════════════════════
DESIGN RATIONALE
═══════════════════════════════════════════════════════════════════════════════

## Purpose
- Build a comprehensive understanding of the codebase BEFORE making changes
- Find and eliminate dead/zombie code safely using dependency graph analysis
- Optimize React/Next.js patterns (Server vs Client, memo, effects, props)
- Reduce bundle size by fixing imports and tree-shaking failures
- Enforce project-specific patterns (service layer, select columns, error handling)
- Tighten types, remove unnecessary assertions
- Clean up debug code, stale TODOs, and security cruft
- Preserve history of what was cleaned for audit trail

## Key Principles
- UNDERSTAND FIRST, CUT SECOND — map the entire dependency graph before removing anything
- Fix everything automatically when safe
- Never break functionality, code, or dependencies
- Create persistent .md file with all findings and actions
- Mark tasks as DONE, never delete them (audit trail)
- Write conclusion/SITREP for historical perspective
- Subsequent runs are incremental

## Safety Rules
- Build must pass after every change
- Tests must pass after every change
- If either fails, rollback that specific change
- Never remove code that might be used externally
- Flag uncertain items for review

## What Makes This Different
- Phase 0 builds a full dependency graph and codebase map FIRST
- Every removal decision is informed by the graph, not blind grep
- React/Next.js-specific optimizations (not just generic dead code)
- Bundle-aware: understands what ships to the client
- Pattern enforcement: catches inconsistencies across the codebase
- Type tightening: makes TypeScript stricter where it can be

═══════════════════════════════════════════════════════════════════════════════
-->

---

## DISCIPLINE

> Reference: [Superpowers Discipline Protocol](~/.claude/standards/STEEL_DISCIPLINE.md)

Key enforcements for this skill:
- **Steel Principle #1:** NO completion claims without fresh verification evidence — build + tests must pass after every removal
- **Steel Principle #3:** NO scope creep — clean only what this run identified; new refactors get their own pass
- Every deletion is backed by dependency-graph evidence, not grep guesses

### Cleancode-Specific Rationalization Table

| Rationalization | Reality | What to Do |
|----------------|---------|------------|
| "While I'm here, I'll also refactor X" | Scope creep creates bugs that look like cleanup regressions | One task at a time; new refactor = new run |
| "This change is safe, skip the test" | Safe-looking changes break things; barrel exports, dynamic imports, and framework conventions bite | Run the test suite after every change |
| "No one imports this file, delete it" | External consumers, framework conventions (e.g., `page.tsx`), and runtime imports don't show in static graphs | Verify with the full dep graph + framework-aware rules before deleting |
| "TypeScript says it's unused" | TS unused checks miss JSX-only refs, side-effect imports, and type-only usage | Confirm with build + runtime check, not just ts-unused-exports |

---

## STATUS UPDATES

This skill follows the **[Status Update Protocol](~/.claude/standards/STATUS_UPDATES.md)**.

See standard for complete format. Skill-specific status examples are provided throughout the execution phases below.

---

## CONTEXT MANAGEMENT

This skill follows the **[Context Management Protocol](~/.claude/standards/CONTEXT_MANAGEMENT.md)**.

Key rules for this skill:
- Audit agents return < 500 tokens each to the orchestrator (full findings written to `.cleancode-reports/`)
- State file `.cleancode-reports/state-YYYYMMDD-HHMMSS.json` tracks which phases, agents, and cleanup items are complete
- Resume from checkpoint if context resets — skip completed work, resume from next incomplete item
- Max 2 parallel agents at a time; cleanup agents run sequentially (they modify code — must verify build after each)
- Orchestrator messages stay lean: "Agent 3/8 complete: React audit found 12 issues, 7 auto-fixable"

---

## AGENT ORCHESTRATION STRATEGY (CRITICAL)

The orchestrator (you, running /cleancode) must NEVER do the heavy scanning or fixing itself. You are a **project manager** — you delegate to agents, collect their results from disk, and coordinate the next step. This keeps your context window clean and prevents context exhaustion.

### Model Selection

Choose the best model for each agent. Cost is not a factor — quality of results is.

| Task Type | Model | Why |
|-----------|-------|-----|
| **Import/export parsing** | `haiku` | Extracting text patterns from files, no judgment needed |
| **Console.log / debugger / TODO grep** | `haiku` | Literal string matching |
| **File counting / inventory** | `haiku` | Listing files, no analysis |
| **Dead code analysis** | `sonnet` | Must trace dependency chains, understand usage context |
| **Orphaned file analysis** | `sonnet` | Must verify against dependency graph, understand entry points |
| **Commented code analysis** | `sonnet` | Must distinguish dead commented code from documentation comments |
| **React/Next.js audit** | `sonnet` | Must understand component logic, props flow, effect dependencies |
| **Bundle size audit** | `sonnet` | Must reason about import chains and tree-shaking |
| **Type tightening audit** | `sonnet` | Must understand TypeScript type system to suggest correct replacements |
| **Pattern enforcement audit** | `sonnet` | Must understand project conventions and compare across files |
| **Tailwind/CSS audit** | `sonnet` | Must understand utility interactions, overrides, and design consistency |
| **Security cruft analysis** | `sonnet` | Must assess whether patterns are genuinely risky |
| **Complexity analysis** | `sonnet` | Must understand logic flow to suggest simplifications |
| **Duplicate consolidation** | `sonnet` | Must design shared abstractions that maintain correctness |
| **Auto-fix execution** | `sonnet` | Must write correct code changes and verify they work |
| **API route analysis** | `sonnet` | Must understand auth patterns, error handling, consistency |
| **Final report & SITREP** | `opus` | Synthesizes all findings into a comprehensive, accurate narrative — high-stakes output |

### Agent Architecture

```
═══════════════════════════════════════════════════════════════════════════════
                        ORCHESTRATOR (you)
                    Model: inherited from user session
                    Role: coordinate, never scan/fix directly
═══════════════════════════════════════════════════════════════════════════════
                              │
              ┌───────────────┼───────────────┐
              │               │               │
        ┌─────┴─────┐  ┌─────┴─────┐  ┌─────┴─────┐
        │  SCOUT    │  │  SCOUT    │  │  SCOUT    │
        │  AGENTS   │  │  AGENTS   │  │  AGENTS   │
        │  (haiku)  │  │  (haiku)  │  │  (haiku)  │
        │           │  │           │  │           │
        │ Find      │  │ Find      │  │ Find      │
        │ patterns  │  │ patterns  │  │ patterns  │
        │ Write to  │  │ Write to  │  │ Write to  │
        │ disk      │  │ disk      │  │ disk      │
        └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
              │               │               │
              └───────┬───────┘               │
                      │  (results on disk)    │
              ┌───────┴───────┐               │
              │               │               │
        ┌─────┴─────┐  ┌─────┴─────┐  ┌─────┴─────┐
        │  FIX      │  │  FIX      │  │  ANALYSIS │
        │  AGENTS   │  │  AGENTS   │  │  AGENTS   │
        │  (sonnet) │  │  (sonnet) │  │  (sonnet) │
        │           │  │           │  │           │
        │ Read      │  │ Read      │  │ Read      │
        │ findings  │  │ findings  │  │ findings  │
        │ Auto-fix  │  │ Auto-fix  │  │ Reason    │
        │ Verify    │  │ Verify    │  │ about     │
        │ build     │  │ build     │  │ complex   │
        └─────┬─────┘  └─────┬─────┘  │ issues   │
              │               │        └─────┬─────┘
              └───────────────┴──────────────┘
                              │
                    [Results on disk]
                              │
                    ┌─────────┴─────────┐
                    │   ORCHESTRATOR    │
                    │   reads results   │
                    │   updates report  │
                    │   launches next   │
                    │   batch           │
                    └───────────────────┘
```

### Agent Spawning Rules

1. **Max 2 agents running in parallel** — prevents resource contention and keeps orchestrator responsive
2. **Agents write ALL findings to disk** — never rely on agent return messages for data; the return message is a brief summary only
3. **Agents are stateless** — each agent gets a clear, self-contained task prompt with everything it needs (file list, what to scan for, where to write results)
4. **Agents never spawn sub-agents** — only the orchestrator spawns agents (two-level hierarchy max)
5. **Fix agents run sequentially** — they modify code, so only one fix agent at a time to avoid conflicts

### Agent Task Prompt Template

Every agent prompt MUST include:

```
1. WHAT TO DO: Clear, specific task (e.g., "Scan these 15 files for unused exports")
2. FILE LIST: Exact files to scan (never "scan everything" — batch into groups)
3. WHAT TO LOOK FOR: Specific patterns with examples
4. WHERE TO WRITE: Exact output file path (e.g., ".cleancode-reports/reports/dead-code-batch1.json")
5. OUTPUT FORMAT: JSON structure for findings
6. WHAT NOT TO DO: "Do NOT fix anything. Do NOT modify any files. Only scan and write findings to disk."
   (for scout agents) OR "Fix ONLY the items listed. Verify build after each fix." (for fix agents)
7. BUDGET: "Complete this task within 10 tool calls" (prevents runaway agents)
```

### Agent Batch Sizing

To prevent any single agent from consuming too much context:

| Codebase Size | Files Per Scout Agent | Findings Per Fix Agent |
|--------------|----------------------|----------------------|
| < 50 files | All files in 1 agent | Up to 10 fixes per agent |
| 50-150 files | 25-30 files per agent | Up to 8 fixes per agent |
| 150-300 files | 15-20 files per agent | Up to 5 fixes per agent |
| 300+ files | 10-15 files per agent | Up to 3 fixes per agent |

### Orchestrator Context Budget

The orchestrator MUST stay lean. Follow these rules:

1. **Never read full file contents** — agents do that. Orchestrator reads only agent result summaries from disk.
2. **Never scan code directly** — always delegate to an agent, even for "quick" scans
3. **State lives on disk, not in context** — after each agent completes, update the state file on disk
4. **Summarize, don't accumulate** — when reporting to the user, summarize counts ("45 dead exports found across 12 files") not full lists
5. **Checkpoint after every agent** — write state to disk so recovery is possible

### State File Format

`.cleancode-reports/state-YYYYMMDD-HHMMSS.json`:

```json
{
  "session_id": "cleancode-20260216-143000",
  "started_at": "2026-02-16T14:30:00Z",
  "phase": "2",
  "status": "in_progress",
  "baseline_commit": "abc123",
  "phases": {
    "0_mapping": {
      "status": "complete",
      "dependency_graph": ".cleancode-reports/dependency-graph.json",
      "component_tree": ".cleancode-reports/component-tree.json",
      "entry_points": ".cleancode-reports/entry-points.json",
      "file_count": 187,
      "completed_at": "2026-02-16T14:32:00Z"
    },
    "1_dead_code": {
      "status": "complete",
      "agents_dispatched": 4,
      "agents_complete": 4,
      "findings_file": ".cleancode-reports/reports/dead-code.json",
      "total_findings": 23,
      "auto_fixable": 18,
      "deferred": 5,
      "completed_at": "2026-02-16T14:38:00Z"
    },
    "2_framework_audits": {
      "status": "in_progress",
      "agents": {
        "react_audit": { "status": "complete", "findings": 12 },
        "bundle_audit": { "status": "complete", "findings": 5 },
        "type_audit": { "status": "running", "agent_id": "abc123" },
        "pattern_audit": { "status": "pending" },
        "tailwind_audit": { "status": "pending" },
        "security_cruft": { "status": "pending" }
      }
    },
    "3_additional_audits": { "status": "pending" },
    "4_cleanup": { "status": "pending" },
    "5_format_verify": { "status": "pending" },
    "6_report": { "status": "pending" }
  }
}
```

### Recovery from Context Reset

If context is lost (session ends, context window fills):

1. Read the state file: `.cleancode-reports/state-YYYYMMDD-HHMMSS.json`
2. Read the living document report: `.cleancode-reports/cleanup-YYYYMMDD-HHMMSS.md`
3. Identify the current phase and what's complete vs pending
4. Resume from the next incomplete agent or phase
5. **Do NOT re-run completed agents** — their results are already on disk
6. **Do NOT re-read the full dependency graph** — it's on disk, only read the summary counts

Recovery prompt for the orchestrator:
```
"I am resuming /cleancode. Read .cleancode-reports/state-*.json (most recent)
to determine where I left off. Skip all completed phases. Resume from the next
pending agent or phase. All previous findings are on disk in .cleancode-reports/reports/."
```

---

## Execution Rules (CRITICAL)

- **NO permission requests** — just execute
- **NO "should I proceed?" questions** — just do it
- **NO waiting for user confirmation** — work continuously
- **Status updates every 5 minutes** — output progress without waiting for response
- **Orchestrator never scans or fixes directly** — always delegate to agents
- **Verify after every change** — build and tests must pass
- **Rollback on failure** — no broken state left behind
- **Self-healing** — retry failed operations
- **Mark tasks DONE, never delete** — preserve for audit trail
- **Write conclusion** — SITREP at end for historical perspective

---

## Usage

```bash
/cleancode                    # Full strategic cleanup pipeline
/cleancode incremental        # Only check files changed since last run
/cleancode --audit-only       # Just report, don't modify
/cleancode --dead-code        # Remove dead code only
/cleancode --duplicates       # Fix duplicates only
/cleancode --complexity       # Reduce complexity only
/cleancode --imports          # Organize imports only
/cleancode --console          # Remove console.log only
/cleancode --todos            # Process TODO comments only
/cleancode --react            # React/Next.js optimizations only
/cleancode --bundle           # Bundle size optimizations only
/cleancode --types            # Type tightening only
/cleancode --patterns         # Pattern enforcement only
/cleancode --api              # API route cleanup only
/cleancode --tailwind         # Tailwind/CSS cleanup only
/cleancode --security-cruft   # Security cruft detection only
/cleancode --file=<path>      # Clean specific file
/cleancode --aggressive       # More aggressive cleanup (may change behavior)
```

---

## Output Structure

```
.cleancode-reports/
├── cleanup-YYYYMMDD-HHMMSS.md    # Main report with task list & conclusion
├── baseline.json                  # Metrics before cleanup
├── history.json                   # All cleanups over time (append-only)
├── findings.json                  # Machine-readable current findings
├── dependency-graph.json          # Codebase dependency map
├── component-tree.json            # React component hierarchy
├── entry-points.json              # All entry points (pages, API routes, exports)
└── reports/
    ├── dead-code.json             # Dead code inventory
    ├── duplicates.json            # Duplication report
    ├── complexity.json            # Complexity hotspots
    ├── zombies.json               # Zombie code (referenced but broken)
    ├── react-audit.json           # React/Next.js issues
    ├── bundle-audit.json          # Bundle size issues
    ├── type-audit.json            # Type tightening opportunities
    ├── pattern-audit.json         # Pattern inconsistencies
    ├── api-audit.json             # API route issues
    ├── tailwind-audit.json        # CSS/Tailwind issues
    └── security-cruft.json        # Security cruft findings
```

---

## Report Persistence (CRITICAL — Living Document)

The markdown report file is a **LIVING DOCUMENT**. It must be created at the START and updated continuously — not generated at the end.

### Living Document Protocol

1. **Phase 0**: Create the full report skeleton at `.cleancode-reports/cleanup-YYYYMMDD-HHMMSS.md` with `Pending` placeholders for all sections
2. **After each cleanup action**: Fill in completed sections with real results immediately. Write to disk.
3. **If context dies**: User can open the `.md` and see exactly what was cleaned, what's pending, and what was deferred

### Finding Statuses

| Status | Meaning |
|--------|---------|
| `FOUND` | Dead code, duplication, or tech debt identified |
| `CLEANING` | Removal/refactor in progress |
| `FIXED` | Cleaned up, build + tests verified |
| `DEFERRED` | Uncertain if safe to remove, used externally, or needs refactor that's too large. Reason documented. |
| `BLOCKED` | Attempted removal broke build/tests. Attempts documented. |

### Deferred Items Table

Every finding that can't be auto-fixed gets a row:

| # | ID | Type | Finding | Why Deferred | What Needs to Happen | Status |
|---|-----|------|---------|-------------|----------------------|--------|
| 1 | CC-XXX | [dead-code/duplicate/complexity/react/bundle/type/pattern] | [what + file] | [may be used externally / refactor too large / uncertain / needs testing] | [specific action] | PENDING |

When working on deferred items, update Status in real-time on disk:
`PENDING` -> `IN PROGRESS` -> `FIXED` or `BLOCKED`

### Rules

1. **Write report skeleton at Phase 0** — file exists before any scans
2. **Update after each cleanup action** — status changes in real-time
3. **Write to disk after every status change** — if session dies, report shows where things stand
4. **SITREP section** — for every DEFERRED or BLOCKED item, document what was tried and why
5. **NEVER delete findings** — only update their status

---

**FIRST ACTION:** Ensure gitignored:
```bash
mkdir -p .cleancode-reports/reports
for pattern in ".cleancode/" ".cleancode-reports/" ".cleancode-audit.json"; do
  grep -qxF "$pattern" .gitignore 2>/dev/null || echo "$pattern" >> .gitignore
done
```

---

## Architecture

```
═══════════════════════════════════════════════════════════════════════════════
                            /cleancode PIPELINE
═══════════════════════════════════════════════════════════════════════════════

PHASE 0: STRATEGIC CODEBASE MAPPING (understand before cutting)
├── Build full dependency graph (who imports who)
├── Identify all entry points (pages, API routes, layout, middleware)
├── Map component tree (parent → child relationships)
├── Classify files: entry point / internal / leaf / shared utility
├── Identify data flow: services → components → UI
├── Baseline metrics (LOC, file count, complexity, bundle estimate)
└── Load previous cleanup history

PHASE 1: DEPENDENCY-AWARE DEAD CODE AUDIT (8 detection types)
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│  UNUSED   │ │  ZOMBIE   │ │ ORPHANED  │ │ COMMENTED │
│  EXPORTS  │ │   CODE    │ │   FILES   │ │    OUT    │
└─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
      │             │             │             │
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│UNREACHABLE│ │  UNUSED   │ │ DEPRECATED│ │  STALE    │
│    CODE   │ │   DEPS    │ │    CODE   │ │ FEATURES  │
└─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
      │             │             │             │
      └─────────────┴──────┬──────┴─────────────┘
                           │
                    [MERGE FINDINGS → validate against dependency graph]

PHASE 2: FRAMEWORK & PATTERN AUDITS (6 parallel agents, max 2 at a time)
┌───────────┐ ┌───────────┐ ┌───────────┐
│  REACT /  │ │  BUNDLE   │ │   TYPE    │
│  NEXT.JS  │ │   SIZE    │ │ TIGHTEN   │
└─────┬─────┘ └─────┬─────┘ └─────┬─────┘
      │             │             │
┌───────────┐ ┌───────────┐ ┌───────────┐
│  PATTERN  │ │ TAILWIND  │ │ SECURITY  │
│  ENFORCE  │ │   / CSS   │ │   CRUFT   │
└─────┬─────┘ └─────┬─────┘ └─────┬─────┘
      │             │             │
      └─────────────┴──────┬──────┴─────────────┘
                           │
                    [MERGE ALL FINDINGS]

PHASE 3: ADDITIONAL AUDITS
├── Duplication detection
├── Complexity analysis
├── Import organization
├── Debug code detection
├── TODO/FIXME analysis
└── API route analysis

PHASE 4: EXECUTE CLEANUP (Sequential, safe order)
├── Remove dead/zombie code (safest first)
├── Fix React/Next.js patterns
├── Tighten types
├── Enforce patterns (select columns, error handling)
├── Consolidate duplicates
├── Simplify complex functions
├── Clean Tailwind/CSS
├── Organize imports
├── Remove debug code
├── Process TODOs
├── Remove security cruft
└── Verify after each step

PHASE 5: FORMAT & VERIFY
├── Run formatter (Prettier/Biome)
├── Run linter fix (ESLint/Biome)
├── Type check (tsc --noEmit)
├── Final build verification
└── Final test verification

PHASE 6: REPORT & CONCLUSION
├── Before/after comparison (LOC, complexity, bundle estimate)
├── Update task list (mark DONE)
├── Write SITREP conclusion
├── Append to history.json
└── Save all reports

═══════════════════════════════════════════════════════════════════════════════
```

---

## PHASE 0: STRATEGIC CODEBASE MAPPING

**This is the most important phase.** Before removing a single line of code, build a complete understanding of how the codebase is connected. Every subsequent decision is informed by this map.

### 0.1 Git Snapshot

```bash
git add -A && git stash push -m "cleancode-backup-$(date +%Y%m%d%H%M%S)" 2>/dev/null || true
CLEAN_BASE=$(git rev-parse HEAD)
echo "Rollback point: $CLEAN_BASE"
```

### 0.2 Build Dependency Graph

Map every file's imports and exports. This is the foundation for all dead code detection.

```
For every .ts/.tsx file in the project:
1. Parse all import statements (what it depends on)
2. Parse all export statements (what it provides)
3. Record: file → imports → [list of files/modules]
4. Record: file → exports → [list of named exports]
5. Build reverse map: export → [list of files that import it]
```

Save to `.cleancode-reports/dependency-graph.json`:
```json
{
  "files": {
    "lib/services/chores-service.ts": {
      "imports": ["@supabase/supabase-js", "lib/types.ts", "lib/utils.ts"],
      "exports": ["getChores", "createChore", "updateChore", "deleteChore"],
      "imported_by": ["app/(dashboard)/chores/page.tsx", "components/chores/ChoreList.tsx"],
      "classification": "service",
      "entry_point": false
    }
  }
}
```

### 0.3 Identify All Entry Points

Entry points are files that DON'T need to be imported — they're invoked by the framework:

```
Next.js entry points:
- app/**/page.tsx          — Pages (routed by filesystem)
- app/**/layout.tsx        — Layouts
- app/**/loading.tsx       — Loading states
- app/**/error.tsx         — Error boundaries
- app/**/not-found.tsx     — 404 pages
- app/api/**/route.ts      — API routes
- middleware.ts            — Edge middleware
- next.config.mjs         — Build config
- tailwind.config.ts      — Tailwind config

Other entry points:
- package.json scripts     — Build/dev commands
- Capacitor config         — Mobile entry points
```

### 0.4 Map Component Tree

Build a parent-child component hierarchy:

```
For every React component:
1. What components does it render? (children in JSX)
2. What props does it accept? (interface/type definition)
3. What props does it actually USE in the function body?
4. Is it a Server Component or Client Component? ('use client' directive)
5. Does it use hooks? Which ones?
6. What state does it manage?
```

Save to `.cleancode-reports/component-tree.json`

### 0.5 Classify Every File

Using the dependency graph and entry points, classify each file:

| Classification | Definition | Removal Risk |
|---------------|------------|--------------|
| **Entry point** | Invoked by framework (pages, routes, layouts) | NEVER remove |
| **Shared utility** | Imported by 3+ files | HIGH risk — many dependents |
| **Internal** | Imported by 1-2 files | MEDIUM risk — verify dependents |
| **Leaf** | Imported by 0 files, not an entry point | LOW risk — likely dead |
| **Service** | In lib/services/, provides data operations | MEDIUM — may be used indirectly |
| **Type-only** | Only exports types/interfaces | LOW — build will catch issues |
| **Config** | Configuration files | NEVER remove automatically |

### 0.6 Map Data Flow

Understand how data moves through the application:

```
Supabase tables
  → lib/services/*.ts (queries)
    → hooks or server components (data fetching)
      → components (display)
        → user interaction
          → lib/services/*.ts (mutations)
            → Supabase tables
```

### 0.7 Baseline Metrics

```json
{
  "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
  "commit": "abc123",
  "metrics": {
    "lines_of_code": 0,
    "file_count": 0,
    "component_count": 0,
    "service_count": 0,
    "api_route_count": 0,
    "page_count": 0,
    "unused_exports": 0,
    "zombie_code_instances": 0,
    "orphaned_files": 0,
    "commented_code_blocks": 0,
    "unreachable_code": 0,
    "unused_dependencies": 0,
    "deprecated_usages": 0,
    "duplicate_blocks": 0,
    "complex_functions": 0,
    "console_logs": 0,
    "todos": 0,
    "circular_imports": 0,
    "avg_complexity": 0,
    "client_components": 0,
    "server_components": 0,
    "select_star_queries": 0,
    "type_assertions": 0,
    "any_types": 0,
    "unused_props": 0,
    "unnecessary_effects": 0
  }
}
```

### 0.8 Load History

```bash
if [ -f ".cleancode-reports/history.json" ]; then
  LAST_CLEANUP=$(jq -r '.[-1].timestamp' .cleancode-reports/history.json)
  LAST_COMMIT=$(jq -r '.[-1].commit' .cleancode-reports/history.json)
  echo "Last cleanup: $LAST_CLEANUP"
fi
```

---

## PHASE 1: DEPENDENCY-AWARE DEAD CODE AUDIT

Every finding is validated against the Phase 0 dependency graph. No blind grep — every removal decision is informed.

### 1.1 Unused Exports Detection

**Using the dependency graph (NOT just grep):**

```
For each exported function/type/constant:
1. Check dependency graph: is it imported by any file?
2. If no imports found, check if it's an entry point export
3. If no imports AND not entry point → DEAD
4. Confidence: HIGH if graph is complete, MEDIUM if dynamic imports possible
```

**Patterns to detect:**
```typescript
// DEAD: Exported but never imported (graph confirms)
export function unusedHelper() { ... }
export const UNUSED_CONSTANT = 'value'
export type UnusedType = { ... }
export interface UnusedInterface { ... }
```

**Special cases to NOT flag:**
- Re-exports from index.ts barrel files (may be consumed externally)
- Exports from lib/types.ts (may be used by external tooling)
- Exports that match naming conventions for framework magic (e.g., generateMetadata, generateStaticParams)

### 1.2 Zombie Code Detection

**Find code that exists but doesn't function:**

```typescript
// ZOMBIE: Function exists but throws "not implemented"
export function zombieFunction() {
  throw new Error('Not implemented')
}

// ZOMBIE: Empty implementation
export function emptyFunction() {
  // TODO: implement
}

// ZOMBIE: Always returns placeholder
export function placeholderFunction() {
  return null // placeholder
}

// ZOMBIE: Disabled with early return
export function disabledFunction() {
  return // disabled
  // ... actual code below never runs
}

// ZOMBIE: Feature flagged off permanently
const ENABLE_FEATURE = false
if (ENABLE_FEATURE) {
  // This code never runs and the flag never changes
}
```

### 1.3 Orphaned Files Detection

**Using the dependency graph (not just grep):**

```
For each file in the project:
1. Is it an entry point? → KEEP
2. Is it imported by any other file? (check graph) → KEEP
3. Is it a config file? → KEEP
4. None of the above? → ORPHANED (verify with graph, then flag)
```

**Additional orphan checks:**
- Test files with no corresponding source file
- Story files with no corresponding component
- Type definition files with no corresponding implementation
- Migration files that were superseded

### 1.4 Commented-Out Code Detection

**Find blocks of commented code (not documentation comments):**

```
Detect patterns:
- // followed by code syntax (function, const, export, import, return, if, for)
- /* ... */ blocks containing code syntax
- More than 3 consecutive lines of commented code

Do NOT flag:
- JSDoc comments (/** ... */)
- Explanatory comments (// This does X because Y)
- Single-line disabled features with a clear reason
- License headers
```

### 1.5 Unreachable Code Detection

```
Detect patterns:
- Code after return/throw/break/continue statements
- Code inside if(false) or if(0) blocks
- Code after process.exit()
- Constant conditions that are always true/false
- Switch cases that can never be reached
- Functions that are defined but the only call site is also dead
```

### 1.6 Unused Dependencies Detection

```bash
# Check package.json dependencies against actual imports
npx depcheck --json > .cleancode-reports/reports/unused-deps.json
```

**Categories:**
| Type | Risk | Action |
|------|------|--------|
| Unused dependency | Low | Remove from package.json |
| Missing dependency | High | Add or remove usage |
| DevDependency in dependencies | Low | Move to devDependencies |
| Dependency in devDependencies | Medium | Move to dependencies |

### 1.7 Deprecated Code Detection

```
Find:
- @deprecated JSDoc tags and check if the deprecated item is still used
- Usage of deprecated APIs from dependencies (check library changelogs)
- Internal functions marked deprecated but still called
```

### 1.8 Stale Feature Flags / Dead Branches

```
Detect patterns:
- Boolean constants that are always false, gating code blocks
- Environment variable checks for values that are never set
- if/else branches where one branch is impossible
- A/B test code where the test has been resolved
- Conditional imports that always resolve the same way
```

---

## PHASE 2: FRAMEWORK & PATTERN AUDITS

These are the audits that generic cleancode tools miss. They're specific to React, Next.js, Tailwind, TypeScript, and the project's own patterns.

### 2.1 React / Next.js Audit

**Server vs Client Component Analysis:**

```
For each component:
1. Does it have 'use client'?
2. If YES: Does it actually need client-side features?
   - Uses hooks (useState, useEffect, useContext, etc.) → NEEDS client
   - Uses event handlers (onClick, onChange, etc.) → NEEDS client
   - Uses browser APIs (window, document, localStorage) → NEEDS client
   - None of the above → CANDIDATE for Server Component (flag)
3. If NO ('use client' absent): Does it import any client components?
   - If yes, it's a Server Component rendering client children — OK
```

**Unused Props Detection:**

```
For each component:
1. Parse the Props interface/type
2. Parse the function signature (destructured props)
3. Search the function body for each prop name
4. If a prop is destructured but never used in JSX or logic → DEAD PROP
5. If a prop is in the interface but never destructured → DEAD PROP
```

Example:
```typescript
// FOUND: 'isAdmin' prop is accepted but never used
interface UserCardProps {
  name: string
  email: string
  isAdmin: boolean  // ← never referenced in component body
}
```

**Unnecessary useEffect Detection:**

```
Flag useEffect that:
- Has an empty dependency array AND only sets state from props
  (should be derived state or initial state instead)
- Fetches data that could be done in a Server Component
- Only runs a cleanup with no setup
- Sets state that's immediately derived from other state
  (should use useMemo or derived calculation instead)
- Transforms data from props (should just compute inline)
```

Example:
```typescript
// FLAGGED: Derived state should be computed inline, not in useEffect
const [fullName, setFullName] = useState('')
useEffect(() => {
  setFullName(`${firstName} ${lastName}`)
}, [firstName, lastName])

// BETTER: const fullName = `${firstName} ${lastName}`
```

**Unnecessary useMemo/useCallback:**

```
Flag useMemo/useCallback that:
- Wraps a primitive value (string, number, boolean)
- Has a dependency array that changes every render anyway
- Memoizes something cheap to compute (simple string concat, basic math)
- Is used in a component that doesn't have expensive children or use React.memo
```

**Missing React.memo Analysis:**

```
Flag components that:
- Receive the same props frequently (parent re-renders often)
- Have expensive render logic (large JSX trees, complex calculations)
- Are rendered in lists (map callbacks)
- BUT: Don't flag components that receive object/function props that aren't memoized
  (React.memo would be useless since the props change every render)
```

**Dead Page/Route Detection:**

```
For each page.tsx and route.ts:
1. Is it linked to from any navigation, Link component, or router.push?
2. Is it referenced in any redirect logic?
3. Is it a dynamic route that's generated from data?
4. If none of the above → potentially dead route (flag for review)
```

**Pass-Through Component Detection:**

```
Flag components that:
- Accept props and pass them all directly to a single child
- Add no additional logic, state, or UI
- Could be replaced by using the child component directly
```

### 2.2 Bundle Size Audit

**Barrel File Analysis:**

```
For each index.ts that re-exports:
1. How many things does it export?
2. When other files import from it, do they use all exports or just 1-2?
3. If only 1-2 exports are used → import directly from source file instead
   (barrel imports can defeat tree-shaking)
```

Example:
```typescript
// BAD: Imports everything from barrel, only uses one thing
import { Button } from '@/components/ui'
// BETTER: Import directly
import { Button } from '@/components/ui/Button'
```

**Large Import Detection:**

```
Flag imports of large libraries where a smaller alternative exists or
where only a small part is used:
- import moment from 'moment' → use date-fns (already in project)
- import _ from 'lodash' → use specific lodash functions or native
- import * as Icons from 'lucide-react' → import specific icons
```

**Client Bundle Bloat:**

```
Flag 'use client' components that import server-only libraries:
- Database clients
- Node.js built-in modules
- Heavy server-side libraries
These should never be in client components.
```

**Dynamic Import Opportunities:**

```
Flag large components that:
- Are below the fold (not visible on initial load)
- Are in modals/dialogs (loaded on interaction)
- Are in tabs (only one tab visible at a time)
These are candidates for next/dynamic or React.lazy.
```

### 2.3 Type Tightening Audit

**`any` Type Detection:**

```
Find every instance of:
- : any
- as any
- : any[]
- <any>
- Record<string, any>

For each: suggest the correct specific type based on usage context.
```

**Unnecessary Type Assertions:**

```
Flag:
- 'as' assertions where TypeScript can infer the type
- Non-null assertions (!) where null checks exist
- Type assertions that widen instead of narrow
- Double assertions (as unknown as Type)
```

**Overly Broad Types:**

```
Flag:
- string where a union of literals would be more precise
- number where a specific range or enum would help
- object where an interface should be defined
- Function where a specific signature is known
```

**Unused Type Members:**

```
For each interface/type:
1. Check all properties
2. Search for usage of each property in code that uses the type
3. If a property is defined but never accessed → flag
```

### 2.4 Pattern Enforcement Audit

**Project-specific patterns from CLAUDE.md:**

```
Check and enforce:
1. select('*') → Replace with specific columns on READ queries
2. All DB operations through lib/services/ (not direct Supabase in components)
3. space_id filter on every query
4. Real-time subscription cleanup in useEffect return
5. No 'any' types (use interfaces from lib/types.ts)
6. Consistent naming: camelCase vars, PascalCase components, UPPER_SNAKE_CASE constants
7. Loading states for async operations
8. Empty states for lists
9. Dark mode only (no light mode variants, no dark: prefixes)
10. Rate limiting on API routes
11. Zod validation on inputs
12. DOMPurify on user-generated HTML
```

**Error Handling Consistency:**

```
Check all API routes and service functions for consistent patterns:
- Do all API routes return the same error response shape?
- Do all service functions handle errors the same way?
- Are there try/catch blocks that silently swallow errors?
- Are error types consistent (Error vs string vs unknown)?
```

**Naming Consistency:**

```
Flag inconsistencies:
- Some files use 'get' prefix, others use 'fetch' for the same pattern
- Inconsistent boolean naming (is/has/should prefixes)
- Inconsistent event handler naming (handle vs on prefix)
- File naming inconsistencies (kebab-case vs camelCase vs PascalCase)
```

### 2.5 Tailwind / CSS Audit

**Unused Tailwind Classes:**

```
This is tricky because Tailwind purges unused classes at build time.
Focus on:
- Duplicate utility combinations (e.g., 'p-4 px-6' — px-6 overrides p-4's horizontal padding)
- Conflicting utilities (e.g., 'text-red-500 text-blue-500' — last one wins)
- Responsive prefixes that are never different from base (e.g., 'text-sm md:text-sm')
- Overly specific utilities that could be simplified
```

**Inconsistent Spacing/Sizing:**

```
Flag:
- Components using different spacing for the same pattern (some use p-4, others p-5 for cards)
- Inconsistent border radius (rounded-lg vs rounded-xl for similar components)
- Inconsistent text sizes for the same role (headings vary between files)
```

**Inline Styles:**

```
Flag any style={{ }} attributes — should use Tailwind classes instead.
Exception: Dynamic values that can't be expressed as Tailwind utilities.
```

### 2.6 Security Cruft Audit

```
Detect:
- Debug API endpoints (app/api/debug/*)
- console.log statements that output sensitive data (tokens, passwords, keys)
- Commented-out auth checks
- Disabled rate limiting (commented out or set to very high limits)
- Overly permissive CORS headers
- Hardcoded credentials or API keys (even in comments)
- TODO comments about security fixes that haven't been done
- Test/seed data that shouldn't be in production code
- Exposed error details in API responses (stack traces, internal paths)
```

---

## PHASE 3: ADDITIONAL AUDITS

### 3.1 Duplication Detection (Textual + Semantic)

#### 3.1a Textual Duplication (jscpd)

```bash
npx jscpd --min-lines 5 --min-tokens 50 --reporters json --output .cleancode-reports/reports/
```

**Thresholds:**
| Lines | Similarity | Action |
|-------|------------|--------|
| 5-10 | 100% | Consider extraction |
| 10-20 | 100% | Extract to shared function |
| 20+ | 100% | Must extract |
| 10+ | 80%+ | Review for abstraction |

#### 3.1b Semantic Duplicate Detection (LLM-Powered)

**Beyond textual matching:** jscpd finds code that LOOKS the same. Semantic detection finds code that DOES the same thing but is written differently. Two functions that both "fetch user by ID, check permissions, return profile data" are semantic duplicates even if they use different variable names, different error handling patterns, or different query styles.

**Agent:** `sonnet` — must understand function intent, not just syntax

**Two-phase approach:**

**Phase A: Classical Extraction**
1. Parse all exported functions across the codebase
2. For each function, extract a signature: `(input types) → output type + side effects`
3. Group functions with matching signatures (same input/output shape)
4. Within each group, flag pairs for semantic comparison

**Phase B: LLM-Powered Intent Clustering**
For each group of signature-matched functions:
1. Read both function bodies
2. Determine: do these functions have the **same intent**?
   - Same intent, same implementation → textual duplicate (already caught by jscpd)
   - Same intent, different implementation → **SEMANTIC DUPLICATE** → must consolidate
   - Different intent, same signature → coincidence, not a duplicate
3. For confirmed semantic duplicates, determine the **canonical** version (the better implementation)

**Semantic duplicate finding format:**
```
CC-SEM-001: Semantic duplicate detected
  Function A: getUserProfile() in lib/services/user-service.ts:45
  Function B: fetchUserData() in app/api/users/route.ts:23
  Intent: Both fetch user by ID from Supabase, check auth, return profile
  Difference: A uses .single(), B uses .limit(1). A throws on not-found, B returns null.
  Canonical: A (better error handling)
  Action: Replace B's callers with A, delete B
```

**Common semantic duplicate patterns to check:**

| Pattern | Example |
|---------|---------|
| **Same query, different wrappers** | `getUser()` in service vs inline Supabase query in route handler |
| **Same validation, different locations** | Zod schema defined in both the form component and the API route |
| **Same transformation, different names** | `formatDate()` in utils vs `dateToString()` in helpers |
| **Same error handling, different styles** | try/catch with redirect in one place, try/catch with throw in another |
| **Same data fetch, different caching** | SWR hook and a manual fetch doing the same query |
| **Same component logic, different UI** | Two card components that fetch and display the same data differently |

**Auto-fixable semantic duplicates:**
- Functions with identical intent + one is strictly better → replace callers, delete the weaker one
- Zod schemas duplicated across client/server → extract to shared `lib/validations/`

**Flagged for review:**
- Functions with same intent but different error handling strategies (user must decide which is correct)
- Components with same data but different UI (may be intentional variation)

**Smart consolidation:** When consolidating duplicates, check if the duplicated code belongs in:
- A shared utility (`lib/utils.ts`)
- A custom hook (`hooks/useXxx.ts`)
- A shared component (if it's JSX)
- The service layer (if it's data operations)

### 3.2 Complexity Analysis

```bash
npx eslint --rule 'complexity: [warn, 10]' . 2>&1
```

**Thresholds:**
| Complexity | Rating | Action |
|------------|--------|--------|
| 1-10 | Simple | OK |
| 11-15 | Moderate | Flag for review |
| 16-20 | Complex | Refactor |
| 21+ | Critical | Must refactor |

**Refactoring strategies (informed by component tree):**
- Extract early returns for guard clauses
- Split into sub-functions with clear names
- Replace nested conditionals with lookup objects
- Extract complex conditions into named booleans

### 3.3 Import Analysis

```
Using the dependency graph from Phase 0:
- Circular imports (A imports B imports A)
- Unused imports (imported but never used)
- Duplicate imports (same thing imported in two different ways)
- Import order inconsistency (React first, then external, then internal)
```

### 3.4 Debug Code Detection

```
Console statements in production code:
- console.log → REMOVE (unless clearly intentional with a comment)
- console.warn → REVIEW (may be intentional deprecation warnings)
- console.error → KEEP (usually intentional error logging)
- console.debug → REMOVE
- console.info → REVIEW
- debugger statements → REMOVE
- alert() calls → REMOVE
```

### 3.5 TODO/FIXME Analysis

```
For each TODO/FIXME/HACK/XXX/@ts-ignore/@ts-expect-error:
1. How old is it? (git blame)
2. Is the issue it describes still relevant?
3. Categorize:
   - Stale (> 90 days, likely forgotten) → flag for resolution or removal
   - Active (< 30 days, likely in progress) → keep
   - Blocked (describes a dependency or external blocker) → document
4. @ts-ignore / @ts-expect-error: Can the underlying type issue be fixed properly?
```

### 3.6 API Route Analysis

```
For each API route in app/api/:
1. Does it have rate limiting?
2. Does it validate input with Zod?
3. Does it check authentication?
4. Does it filter by space_id?
5. Does it return consistent error shapes?
6. Does it have proper HTTP status codes?
7. Is the response type defined?
8. Are there duplicate patterns across routes that could be middleware?
```

### 3.7 WHY Comment Audit (LLM-Powered)

**Purpose:** Scan the codebase for non-obvious code decisions that lack inline WHY comments.
This is NOT docstring generation (what a function does) - it's intent documentation (why a
specific implementation choice was made). No existing tool does this; it requires understanding
the surrounding context to identify decisions that would confuse a future reader.

**Agent:** `sonnet` - needs to reason about code intent and non-obvious trade-offs

**What qualifies as "needs a WHY comment":**

| Code Pattern | Why It Needs a Comment | Example Comment |
|---|---|---|
| Magic numbers or thresholds | Reader won't know why that specific value | `// 500ms debounce - faster triggers API rate limits` |
| Security decisions | Reader might "simplify" away the protection | `// Identical error for missing user vs wrong code - prevents enumeration` |
| Workarounds for framework/library bugs | Reader might remove the "unnecessary" code | `// Explicit null check - React 19 strictMode double-renders cause stale ref` |
| Non-obvious ordering | Reader might reorder for "clarity" | `// Clean dead code BEFORE updating deps - avoids updating unused packages` |
| Performance-motivated choices | Reader might refactor into "cleaner" but slower version | `// Inline style instead of className - avoids Tailwind purge miss in dynamic component` |
| Business logic branches | Reader won't know the business rule | `// Premium tier gets 6-hour backup interval, not daily` |
| Intentional omissions | Reader might add the "missing" code | `// No auth check here - this route is public (webhook receiver)` |
| Environment-specific branches | Reader might not know why both paths exist | `// /.dockerenv exists in containers but not bare metal - reliable env detection` |
| Regex patterns | Almost always non-obvious | `// Match scrypt format: "scrypt:<salt>:<hash>" - 3 colon-separated segments` |
| Error handling choices | Reader might wonder why catch is empty or why retry count | `// Retry 3x with backoff - Ollama Cloud occasionally returns 503 under load` |

**What does NOT need a WHY comment (skip these):**

| Pattern | Why Skip |
|---|---|
| Simple CRUD operations | Self-evident from function name and types |
| Standard framework patterns | `useEffect`, `getServerSideProps`, route handlers with obvious purpose |
| Well-named variables and functions | Good naming IS the documentation |
| Import statements | Never comment imports |
| Type definitions | The types document themselves |
| Simple conditionals with clear intent | `if (!user) return unauthorized()` is self-evident |

**Audit process:**

```
For each file modified in the current cleancode run (or all files if first run):

1. SCAN: Read the file and identify candidate locations:
   - Functions longer than 15 lines
   - Conditional branches with non-obvious conditions
   - Try/catch blocks with specific error handling
   - Numeric literals that aren't 0, 1, or common defaults
   - Regex patterns
   - setTimeout/setInterval with specific durations
   - Security-related code (auth checks, sanitization, encryption)
   - Environment-detection branches
   - Code that references external systems (APIs, DBs, services)

2. FILTER: For each candidate, check:
   - Does a WHY comment already exist within 2 lines above? → Skip
   - Is the intent obvious from naming alone? → Skip
   - Is this a standard framework pattern? → Skip
   - Would a competent developer joining the team understand this without context? → Skip

3. GENERATE: For candidates that survive filtering:
   - Read the surrounding function and file for context
   - Determine the non-obvious WHY (not WHAT)
   - Write a single-line comment (max 100 chars) starting with WHY, not WHAT
   - Place it on the line immediately above the code it explains

4. VALIDATE: Before inserting any comment:
   - Does it explain WHY, not WHAT? ("// Escape markdown" is WHAT; "// User answers may contain # that breaks template structure" is WHY)
   - Is it specific to THIS code, not generic? ("// Handle error" is generic; "// Ollama Cloud returns 503 under load, retry with backoff" is specific)
   - Is it under 100 characters?
   - Does it NOT reference the current task, ticket, or PR? (Those rot as context changes)
```

**Comment format rules:**
- Single line only: `// WHY explanation`
- No multi-line comment blocks (`/* */`)
- No JSDoc-style comments on internal functions (only exported API surfaces)
- No trailing comments on the same line as code
- Use sentence fragments, not full sentences: `// Prevents enumeration attacks` not `// This prevents enumeration attacks.`
- Never start with "This", "We", "I", or "Note:"

**Output format in cleancode report:**

```
## WHY Comment Audit

Files scanned: [N]
Candidates identified: [N]
Comments inserted: [N]
Skipped (already documented): [N]
Skipped (self-evident): [N]

### Comments Added

| File | Line | Comment |
|---|---|---|
| src/lib/users.ts:335 | `hashes.push(...)` | // scrypt hash each code individually so DB compromise doesn't reveal all codes |
| src/app/api/operations/route.ts:22 | `existsSync("/.dockerenv")` | // /.dockerenv exists in containers but not bare metal - reliable env detection |
```

**Safety rules:**
- Never modify code logic, only add comments
- Never remove existing comments (even if they seem wrong - flag for review instead)
- Build must still pass after comment insertion (comments can't break syntax)
- If a file has zero candidates, don't add comments just to hit a quota

---

## PHASE 4: EXECUTE CLEANUP

### 4.1 Cleanup Order (Safety-first, Dependencies Respected)

Execute in this exact order — safest changes first, riskiest last:

1. **Unused imports** (safest, no behavior change, no dependents affected)
2. **Unused variables** (safe, no behavior change)
3. **Commented-out code blocks** (safe, just comments)
4. **Unreachable code** (safe, never executes)
5. **Dead console.log/debugger** (safe, debug only)
6. **Stale feature flags** (safe, code never runs)
7. **Unused exports** (verify against dependency graph first)
8. **Zombie code** (verify against dependency graph first)
9. **Unused props** (verify no callers pass the prop)
10. **Type tightening** (change `any` to specific types)
11. **select('*') replacement** (specific columns)
12. **Unnecessary useEffect conversion** (derived state)
13. **Pattern enforcement fixes** (error handling consistency)
14. **Duplicate consolidation** (test thoroughly)
15. **Complexity reduction** (test thoroughly)
16. **Tailwind cleanup** (conflicting/duplicate utilities)
17. **Orphaned file removal** (flag for review, don't auto-delete)
18. **WHY comment insertion** (safest last - adds only comments, never changes logic)
18. **Security cruft** (remove debug endpoints, fix exposed data)
19. **TODO processing** (resolve or create issues for old ones)

### 4.2 Safe Removal Process

For each item:

```bash
# 1. Make the change
CHANGE_FILE="$file"
CHANGE_DESC="$description"

# 2. Verify type check
npx tsc --noEmit > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "Type check failed after: $CHANGE_DESC"
  git checkout -- "$CHANGE_FILE"
  # Record as BLOCKED
  continue
fi

# 3. Verify build
pnpm build > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "Build failed after: $CHANGE_DESC"
  git checkout -- "$CHANGE_FILE"
  # Record as BLOCKED
  continue
fi

# 4. Mark as FIXED
echo "Safely completed: $CHANGE_DESC"
```

**Note:** Run type check first (faster) before full build. Only run full build if type check passes. This saves time on large codebases.

### 4.3 What Gets Auto-Fixed vs Flagged

| Type | Auto-Fix | Flagged |
|------|----------|---------|
| Unused imports | Yes | - |
| Unused variables | Yes | - |
| Unreachable code | Yes | - |
| Commented code (>3 lines) | Yes | - |
| console.log (debug) | Yes | - |
| debugger statements | Yes | - |
| Stale feature flags | Yes | - |
| Unused exports (graph confirms dead) | Yes | - |
| `any` types (clear replacement) | Yes | - |
| select('*') (columns determinable) | Yes | - |
| Conflicting Tailwind classes | Yes | - |
| Duplicate Tailwind classes | Yes | - |
| Unused exports (uncertain) | - | Review |
| Zombie functions | - | Review |
| Orphaned files | - | Review |
| Complex functions | - | Refactor suggestion |
| Duplicates | - | Consolidation plan |
| Old TODOs | - | Resolve or create issue |
| Unnecessary useEffect | - | Refactor suggestion |
| Pass-through components | - | Simplification suggestion |
| Server Component candidates | - | Migration suggestion |
| Unused props | - | Review (may affect API) |
| API route inconsistencies | - | Pattern suggestion |
| Security cruft | - | Review (may be intentional) |

---

## PHASE 5: FORMAT & VERIFY

```bash
# Format
if [ -f "biome.json" ]; then
  npx @biomejs/biome format --write .
  npx @biomejs/biome check --apply .
elif [ -f ".prettierrc" ] || [ -f "prettier.config.*" ]; then
  npx prettier --write .
  npx eslint --fix .
fi

# Type check
npx tsc --noEmit

# Build
pnpm build

# Lint
pnpm lint 2>/dev/null || npx eslint . 2>/dev/null
```

---

## PHASE 6: REPORT & CONCLUSION

### 6.1 Main Report File

**Filename:** `.cleancode-reports/cleanup-YYYYMMDD-HHMMSS.md`

```markdown
# Code Cleanup Report: [PROJECT_NAME]

**Created:** [YYYY-MM-DD HH:MM:SS]
**Commit Before:** [commit_hash]
**Commit After:** [commit_hash]
**Status:** COMPLETE

---

## Executive Summary

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Lines of Code | X | Y | -Z (N%) |
| Files | X | Y | -Z |
| Unused Exports | X | 0 | -X |
| Zombie Code | X | 0 | -X |
| Commented Code Blocks | X | 0 | -X |
| Complex Functions (>15) | X | Y | -Z |
| Console.logs | X | Y | -Z |
| TODOs | X | Y | -Z |
| `any` Types | X | Y | -Z |
| select('*') Queries | X | Y | -Z |
| Unnecessary useEffects | X | Y | -Z |
| Unused Props | X | Y | -Z |

**Code Reduction:** N% fewer lines
**Type Safety Improvement:** N fewer `any` types
**React Optimization:** N patterns improved

---

## Dependency Graph Summary

| Classification | Count | Dead Found |
|---------------|-------|------------|
| Entry Points | X | 0 (never removed) |
| Shared Utilities | X | Y unused |
| Internal Files | X | Y unused |
| Leaf Files | X | Y orphaned |
| Services | X | Y unused functions |
| Type-only Files | X | Y unused types |

---

## [Detailed task list with all findings, actions, and statuses]

---

## Verification Results

| Check | Status | Details |
|-------|--------|---------|
| TypeScript | Pass/Fail | Details |
| Build | Pass/Fail | Details |
| Lint | Pass/Fail | Details |

---

> Reference: [SITREP Standard](~/.claude/standards/SITREP_FORMAT.md) — use the unified template with domain-specific additions below.

## SITREP (Conclusion)

### Mission Status: COMPLETE

[Detailed summary of what was accomplished, what was deferred, why,
and recommendations for future cleanups]

### Historical Context

[Reference to previous cleanup runs and cumulative improvement]
```

### 6.2 Update History

Append to `.cleancode-reports/history.json` with full metrics from this run.

---

## INCREMENTAL MODE

For subsequent runs (`/cleancode incremental`):

### Detect Changes Since Last Cleanup

```bash
LAST_COMMIT=$(jq -r '.cleanups[-1].commit_after' .cleancode-reports/history.json)
CHANGED_FILES=$(git diff --name-only $LAST_COMMIT HEAD -- "*.ts" "*.tsx")
```

### Focused Analysis

Only analyze:
- Files changed since last cleanup
- Files importing changed files (check dependency graph)
- New files added
- New dependencies in package.json
- Files that were DEFERRED in the last run (re-check)

### Incremental Report

Shows only new findings since last full cleanup. References the previous cleanup for context.

---

## Rollback Procedure

```bash
echo "Rolling back code cleanup..."
git reset --hard $CLEAN_BASE
git stash pop 2>/dev/null || true
echo "Rolled back to: $CLEAN_BASE"
```

---

## RELATED SKILLS

**Feeds from:**
- (none - /cleancode is typically run proactively on existing code, or as part of /launch readiness)

**Feeds into:**
- `/gh-ship` - once code is cleaned and build passes, ship the cleanup with gh-ship
- `/perf` - dead code removal and bundle optimization surface the same issues; cleancode may reduce bundle size enough to skip a perf pass

**Pairs with:**
- `/test-ship` - run together before launch to ensure both code quality and test coverage are solid
- `/docs` - clean code paired with good documentation is the full maintenance readiness pass
- `/launch` - cleancode is one of 8 skills orchestrated by launch; run standalone first to address major debt before launch sweep

**Auto-suggest after completion:**
When all FIXED findings are verified and build passes, suggest: `/gh-ship` to commit the cleanup; if large files remain over 400 lines, suggest `/brainstorm` to plan a decomposition

---

## REMEMBER

- **UNDERSTAND FIRST, CUT SECOND** — Phase 0 dependency mapping is not optional
- **Mark DONE, never delete** — Preserve task history for audit trail
- **Verify after every change** — Build and type check must pass
- **Write conclusion** — SITREP provides historical perspective
- **Incremental is faster** — After first run, only check changes
- **Flag uncertain items** — Don't auto-remove if the dependency graph can't confirm it's dead
- **Preserve intentional code** — Not all console.logs are debug, not all TODOs are stale
- **React/Next.js aware** — This isn't generic dead code removal, it understands the framework
- **Bundle conscious** — Every import has a cost, every 'use client' has a cost
- **Type strict** — Every `any` is a bug waiting to happen

---

## CLEANUP PROTOCOL

> Reference: [Resource Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md)

### Cleancode-Specific Cleanup

Cleanup actions:
1. **Git stash:** On successful completion, drop the backup stash: `git stash drop` for the `cleancode-backup-*` entry. Only keep the stash if the skill failed and rollback may be needed
2. **Gitignore enforcement:** Ensure `.cleancode-reports/` is in `.gitignore`

<!-- Claude Code Skill by Steel Motion LLC — https://steelmotion.dev -->
<!-- Part of the Claude Code Skills Collection -->
<!-- Powered by Claude models: Haiku (fast extraction), Sonnet (balanced reasoning), Opus (deep analysis) -->
<!-- License: MIT -->

---

## Suggested next

Per [Skill Auto-Suggest Protocol](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md), every SITREP MUST end with a "Suggested next" block. Use this decision matrix to pick:

| Outcome | Recommended | Why |
|---|---|---|
| Cleanup applied | /test-ship | verify no regressions |
| Heavy refactor done | /test-ship + /sec-ship | full quality gate |
| Tech debt deferred | none — operator review | judgment call |
| Clean (nothing to remove) | /perf or /deps | next health check |

**Skip if:** the operator has already directed the next step, or this run was a no-op.
