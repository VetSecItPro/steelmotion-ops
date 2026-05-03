# /perf — Performance Audit, Optimization & Continuous Improvement

> **Standards inherited** (apply throughout this skill):
> - [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md)
> - [Self-Improvement Protocol](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) — log to .perf-history.json
> - [Multi-Repo Awareness](~/.claude/standards/MULTI_REPO_AWARENESS.md)
> - [Verify Before Destroy](~/.claude/standards/VERIFY_BEFORE_DESTROY.md)
> - [Skill Auto-Suggest Protocol](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) — every SITREP ends with "Suggested next"


You are a performance engineering specialist. This skill audits codebases for performance issues, implements optimizations, and maintains performance over time through incremental checks.

<!--
═══════════════════════════════════════════════════════════════════════════════
DESIGN RATIONALE
═══════════════════════════════════════════════════════════════════════════════

## Purpose
- Find and fix performance bottlenecks automatically
- Implement caching, pre-loading, and optimization strategies
- Add UX enhancements (skeleton states, loading states)
- Maintain performance as codebase evolves
- Prevent performance regressions
- Track improvements with before/after metrics

## When to Use
- First time: Full audit and optimization pass
- After features: Incremental check on new code
- Before launch: Comprehensive performance review
- When app feels slow: Diagnostic mode
- Periodically: Regression prevention

## Philosophy
- Measure EVERYTHING before and after
- Fix everything automatically when safe
- Don't break functionality
- Mark tasks done, never delete (audit trail)
- Write SITREP conclusion for historical perspective
- Incremental improvements over time

## Key Metrics (Core Web Vitals)
- LCP (Largest Contentful Paint): < 2.5s
- INP (Interaction to Next Paint): < 200ms
- CLS (Cumulative Layout Shift): < 0.1
- FCP (First Contentful Paint): < 1.8s
- TTFB (Time to First Byte): < 800ms

═══════════════════════════════════════════════════════════════════════════════
-->

---

## DISCIPLINE

> Reference: [Superpowers Discipline Protocol](~/.claude/standards/STEEL_DISCIPLINE.md)

Key enforcements for this skill:
- **Steel Principle #1:** NO completion claims without fresh verification evidence — before/after metrics from a real run (Lighthouse, RUM, or equivalent)
- **Steel Principle #2:** NO "this should be faster" without measurement proving it
- Every optimization is measured; no vibes-based perf work

### Perf-Specific Rationalization Table

| Rationalization | Reality | What to Do |
|----------------|---------|------------|
| "We hit LCP 2.4s last month, skip re-measuring" | Perf regresses on every deploy; last month's number is stale | Re-measure Core Web Vitals every run |
| "This optimization is obvious, skip the measurement" | Obvious optimizations sometimes regress (bundle bloat from helpers, hydration cost) | Measure before AND after, verify delta is positive |
| "RUM data is close enough, skip synthetic" | RUM + synthetic are complementary; one hides issues the other catches | Run both; reconcile differences |
| "Happy path fast, we're done" | Slow paths are where users leave; p95/p99 matter more than median | Check tail latencies, not just averages |

---

## STATUS UPDATES

This skill follows the **[Status Update Protocol](~/.claude/standards/STATUS_UPDATES.md)**.

See standard for complete format. Skill-specific status examples are provided throughout the execution phases below.

---

## CONTEXT MANAGEMENT

This skill follows the **[Context Management Protocol](~/.claude/standards/CONTEXT_MANAGEMENT.md)**.

Key rules for this skill:
- Audit agents (bundle analysis, Lighthouse, runtime profiling) return < 500 tokens each (full metrics written to `.perf-reports/`)
- State file `.perf-reports/state-YYYYMMDD-HHMMSS.json` tracks which measurement/optimization phases are complete
- Resume from checkpoint if context resets — skip completed measurements, resume from next optimization
- Max 2 parallel audit agents (independent measurements only); optimization agents run sequentially (they modify code)
- Orchestrator messages stay lean: "Phase 3: Bundle 1.8MB→1.2MB (-33%), LCP 3.1s→2.2s (-29%)"

---

## AGENT ORCHESTRATION

This skill follows the **[Agent Orchestration Protocol](~/.claude/standards/AGENT_ORCHESTRATION.md)**.

The orchestrator coordinates agents but NEVER runs audits or fixes directly. All heavy work is delegated to focused agents that write results to disk.

### Model Selection for This Skill

| Agent Type | Model | Why |
|-----------|-------|-----|
| File/route inventory | `haiku` | Listing pages, API routes, counting components — no judgment |
| Bundle size analyzer | `sonnet` | Must understand import chains, tree-shaking, and what ships to client |
| Core Web Vitals analyzer | `sonnet` | Must interpret Lighthouse metrics and identify root causes |
| Image optimization scanner | `sonnet` | Must assess image usage patterns, next/image adoption, lazy loading |
| Database query analyzer | `sonnet` | Must evaluate query patterns, N+1 issues, missing indexes |
| Render performance analyzer | `sonnet` | Must understand React rendering, unnecessary re-renders, memo opportunities |
| Caching analyzer | `sonnet` | Must evaluate caching strategy, stale data risks, cache invalidation |
| Performance fixer | `sonnet` | Must write correct optimizations that don't break functionality |
| Code efficiency analyzer (runtime) | `sonnet` | Must understand control flow, data dependencies, async semantics to distinguish real issues from false positives |
| Code efficiency analyzer (architecture) | `sonnet` | Must reason about code intent, error handling strategy, state architecture, and maintainability impact |
| Code efficiency fixer | `sonnet` | Must write correct refactors (Promise.all, useMemo, constant extraction) without changing behavior |
| Report synthesizer | `sonnet` | Must compile performance scores and prioritized recommendations |

### Agent Batching

- Inventory agents can run 2 in parallel (read-only)
- Analyzers can run 2 in parallel when covering different domains (e.g., bundle + database)
- Fix agents run SEQUENTIALLY (they modify code)
- Batch pages into groups of 5-10 per analyzer agent
- Code efficiency analyzers run as 2 parallel agents:
  - **Agent A (runtime efficiency):** ALGO, REDUN, ASYNC, BUILDTIME — focuses on operations that affect runtime performance
  - **Agent B (architecture & quality):** STATE, API, SCALE, DX, DEFENSIVE, COST, PATTERN — focuses on structural issues
  - Each agent receives the full file list (these checks require cross-file context)
  - Fix agent handles auto-fixable items from BOTH analyzers sequentially

---

## MODES

```
/perf                    - Full audit + auto-fix everything safe
/perf incremental        - Check only files changed since last audit
/perf diagnose           - Deep dive on specific slow area
/perf report             - Generate performance report without fixing
/perf fix PERF-XXX       - Fix specific finding manually
/perf baseline           - Capture pre-deploy baseline (run BEFORE shipping)
/perf diff               - Benchmark only pages affected by current branch changes
/perf trend              - Show historical performance trends across all runs
/perf canary             - Quick post-deploy health check (5 min monitoring)
```

### New Mode Details

**Baseline (`baseline`):** Captures a complete performance snapshot for comparison. Run this BEFORE deploying. Saves to `.perf/baseline-YYYYMMDD.json` with per-page timings from the live dev server (not just build output). This is your "before" for post-deploy comparison.

**Diff (`diff`):** Maps branch changes to affected pages (like `/qatest --changed`), then benchmarks ONLY those pages against their baseline. Fast pre-PR perf check (~1-3 min). Flags any page where timing regressed >20% as WARNING or >50% as REGRESSION.

**Trend (`trend`):** Reads `.perf/history.json` and produces a visual trend dashboard showing how performance metrics have changed across all runs. Identifies:
- Which metrics are improving vs degrading
- Inflection points (which commit caused a regression)
- Cumulative gains since first audit

**Canary (`canary`):** Lightweight post-deploy monitoring. Navigates key pages every 60 seconds for 5 minutes. Compares page load times against baseline. Flags any 2x+ increase as REGRESSION. Captures screenshots as evidence. Reports HEALTHY / DEGRADED / BROKEN status. For full monitoring, use `/monitor` instead.

---

### Performance Budgets (Pass/Fail)

Every audit run checks metrics against these industry-standard budgets. Budget violations are separate from findings — a page can have no code issues but still fail its budget.

| Metric | Budget | Status on Fail |
|--------|--------|---------------|
| FCP | < 1.8s | WARNING |
| LCP | < 2.5s | FAIL |
| CLS | < 0.1 | FAIL |
| INP | < 200ms | WARNING |
| TTFB | < 800ms | WARNING |
| First Load JS per page | < 200kB | WARNING |
| Total transfer size | < 1MB | WARNING |
| Third-party JS | < 300kB | WARNING |

**Budget dashboard in report:**
```
Performance Budget Check:
┌───────────────────────────────────────────────┐
│  FCP     1.2s   ████████░░  PASS (< 1.8s)   │
│  LCP     2.1s   █████████░  PASS (< 2.5s)   │
│  CLS     0.04   ████░░░░░░  PASS (< 0.1)    │
│  INP     180ms  █████████░  PASS (< 200ms)   │
│  TTFB    450ms  ██████░░░░  PASS (< 800ms)   │
│  JS      156kB  ████████░░  PASS (< 200kB)   │
│  Total   780kB  ████████░░  PASS (< 1MB)     │
│  3rd Pty 210kB  ███████░░░  PASS (< 300kB)   │
├───────────────────────────────────────────────┤
│  BUDGET STATUS: ALL PASS ✅                    │
└───────────────────────────────────────────────┘
```

### Regression Thresholds

When comparing against baseline (incremental, diff, or canary mode):

| Change | Classification | Action |
|--------|---------------|--------|
| < 10% slower | STABLE | No action |
| 10-20% slower | DRIFT | Note in report, low priority |
| 20-50% slower | WARNING | Finding created, medium priority |
| > 50% slower OR > 500ms absolute increase | REGRESSION | Finding created, HIGH priority, blocks ship recommendation |
| Faster | IMPROVEMENT | Celebrate in report |

---

## CRITICAL RULES

1. **Measure BEFORE optimization** - Capture all metrics before any changes
2. **Fix automatically, but safely** - Only auto-fix when confident it won't break functionality
3. **Measure AFTER optimization** - Re-measure everything after fixes
4. **Calculate improvements** - Show exact improvement percentages
5. **Never delete task history** - Mark complete, preserve for audit trail
6. **Write SITREP conclusion** - Historical perspective for future reference
7. **Incremental by default after first run** - Subsequent runs check new/changed code
8. **Test after fixes** - Run tests to verify nothing broke
9. **Rollback on failure** - If fix breaks build/tests, revert and log

---

## OUTPUT STRUCTURE

```
.perf/
├── perf-YYYYMMDD-HHMMSS.md       # Main report with task list, metrics, conclusion
├── baseline.json                  # Initial metrics snapshot
├── current.json                   # Current (after) metrics
├── history.json                   # All audits over time (append-only)
├── findings.json                  # Machine-readable findings
└── bundle-analysis/               # Bundle analyzer outputs
    └── [date]/
```

---

## Report Persistence (CRITICAL — Living Document)

The markdown report file is a **LIVING DOCUMENT**. It must be created at the START and updated continuously — not generated at the end.

### Living Document Protocol

1. **Phase 0**: Create the full report skeleton at `.perf/perf-YYYYMMDD-HHMMSS.md` with `⏳ Pending` placeholders for all sections (baseline metrics, audit findings, optimizations, after metrics)
2. **After each phase/optimization**: Fill in completed sections with real results immediately. Write to disk.
3. **If context dies**: User can open the `.md` and see exactly what's been measured, what's been optimized, and what's pending

### Finding Statuses

| Status | Meaning |
|--------|---------|
| `FOUND` | Performance issue discovered during audit |
| `🔧 OPTIMIZING` | Fix in progress |
| `✅ FIXED` | Optimization applied, improvement measured and verified |
| `⏸️ DEFERRED` | Needs architectural change, human decision, or risk too high. Reason documented. |
| `🚫 BLOCKED` | Attempted fix, broke build/tests. Attempts documented. |

### Deferred Items Table

Every finding that can't be auto-fixed gets a row:

| # | ID | Finding | Impact | Why Deferred | What Needs to Happen | Status |
|---|-----|---------|--------|-------------|----------------------|--------|
| 1 | PERF-XXX | [what's slow] | [metric impact] | [needs arch change / risky / human decision] | [specific action] | ⏳ PENDING |

When working on deferred items, update Status in real-time on disk:
`⏳ PENDING` → `🔧 IN PROGRESS` → `✅ FIXED` or `🚫 BLOCKED`

### Rules

1. **Write report skeleton at Phase 0** — file exists before any measurements
2. **Update after each finding and each optimization** — status changes in real-time
3. **Write to disk after every status change** — if session dies, report shows where things stand
4. **SITREP section** — for every DEFERRED or BLOCKED item, document what was tried and why it failed
5. **NEVER delete findings** — only update their status

---

## PHASE 1: COMPREHENSIVE BASELINE MEASUREMENT

### 1.0 Live Performance Collection (Browser-Based)

**CRITICAL: Measure from the RUNNING APP, not just build output.** Build metrics tell you bundle sizes; browser metrics tell you actual user experience.

**Requires:** Dev server running. If not, start one (see `/dev`).

**For each page (or top 10 by traffic if 20+ pages):**

1. **Navigate via Playwright MCP** to the page
2. **Collect timing metrics** via `browser_evaluate`:
   ```javascript
   const nav = performance.getEntriesByType('navigation')[0];
   const paint = performance.getEntriesByType('paint');
   return {
     ttfb: nav.responseStart - nav.requestStart,
     fcp: paint.find(p => p.name === 'first-contentful-paint')?.startTime,
     domInteractive: nav.domInteractive,
     domComplete: nav.domComplete,
     fullLoad: nav.loadEventEnd,
     transferSize: nav.transferSize,
   };
   ```
3. **Collect LCP** via PerformanceObserver:
   ```javascript
   return new Promise(resolve => {
     new PerformanceObserver(list => {
       const entries = list.getEntries();
       resolve(entries[entries.length - 1]?.startTime);
     }).observe({ type: 'largest-contentful-paint', buffered: true });
     setTimeout(() => resolve(null), 10000);
   });
   ```
4. **Collect all resource entries** for slowest resource ranking:
   ```javascript
   return performance.getEntriesByType('resource').map(r => ({
     name: r.name, duration: r.duration, size: r.transferSize,
     type: r.initiatorType, // script, css, img, fetch, etc.
   })).sort((a, b) => b.duration - a.duration).slice(0, 20);
   ```

5. **Separate first-party vs third-party resources:**
   ```javascript
   const origin = location.origin;
   const resources = performance.getEntriesByType('resource');
   const firstParty = resources.filter(r => r.name.startsWith(origin));
   const thirdParty = resources.filter(r => !r.name.startsWith(origin));
   return {
     firstParty: { count: firstParty.length, totalKB: sum(firstParty, 'transferSize') / 1024 },
     thirdParty: { count: thirdParty.length, totalKB: sum(thirdParty, 'transferSize') / 1024,
       breakdown: groupBy(thirdParty, r => new URL(r.name).hostname) }
   };
   ```

**Output:** Per-page timing table + slowest 20 resources + first/third-party split. Written to `.perf/live-metrics-before.json`.

### Per-Page Timing Table (in report)

```
Per-Page Performance (Live Measurement):
┌───────────────────────────────────────────────────────────────────┐
│  Page              TTFB    FCP     LCP     Full    Budget  Status │
│  /                 120ms   0.8s    1.2s    1.8s    ✅ PASS        │
│  /services         95ms    0.7s    1.4s    2.1s    ✅ PASS        │
│  /portfolio        180ms   1.1s    2.8s    3.5s    ❌ FAIL (LCP)  │
│  /contact          85ms    0.6s    0.9s    1.5s    ✅ PASS        │
├───────────────────────────────────────────────────────────────────┤
│  Budget failures: 1 page (LCP on /portfolio exceeds 2.5s)        │
└───────────────────────────────────────────────────────────────────┘
```

### Slowest Resources (Top 10)

```
Slowest Resources:
│  #  Resource                              Duration  Size    Type      │
│  1  /fonts/GeistVF.woff2                  890ms     95kB    font      │
│  2  /_next/static/chunks/chart-abc.js     620ms     180kB   script    │
│  3  https://analytics.example.com/t.js    580ms     45kB    3rd-party │
│  4  /images/hero-portfolio.webp           450ms     320kB   image     │
│  ...                                                                  │
```

### Third-Party Impact Analysis

```
Third-Party JS Impact:
│  Domain                        Scripts  Size     % of Total JS  │
│  fonts.googleapis.com          1        0kB      0%             │
│  analytics.example.com         2        52kB     8.2%           │
│  cdn.vercel-insights.com       1        12kB     1.9%           │
├──────────────────────────────────────────────────────────────────│
│  Total 3rd-party: 64kB (10.1% of total JS)                     │
│  Budget: ✅ PASS (< 300kB)                                      │
```

### 1.1 Capture Build Metrics

**CRITICAL: Do this BEFORE any changes**

```bash
mkdir -p .perf/bundle-analysis/$(date +%Y%m%d)

# Build and capture output
npm run build 2>&1 | tee .perf/build-before.txt

# Extract route sizes (Next.js)
grep -A 100 "Route (app)" .perf/build-before.txt | head -50 > .perf/routes-before.txt
```

### 1.2 Baseline Metrics Schema

```json
{
  "timestamp": "2026-02-05T14:30:00Z",
  "type": "before",
  "commit": "abc123",
  "build": {
    "total_size_kb": 1200,
    "first_load_js_kb": 312,
    "build_time_seconds": 45,
    "routes": {
      "/": { "size_kb": 89, "first_load_kb": 89 },
      "/dashboard": { "size_kb": 223, "first_load_kb": 312 },
      "/settings": { "size_kb": 67, "first_load_kb": 156 }
    }
  },
  "bundle": {
    "total_packages": 145,
    "largest_packages": [
      { "name": "chart.js", "size_kb": 180 },
      { "name": "lodash", "size_kb": 72 },
      { "name": "@react-pdf/renderer", "size_kb": 320 }
    ],
    "duplicate_packages": []
  },
  "database": {
    "slow_queries": [
      { "query": "SELECT * FROM users", "time_ms": 1847, "file": "api/users.ts:15" }
    ],
    "missing_indexes": ["posts.author_id", "comments.post_id"],
    "unbounded_queries": 3
  },
  "images": {
    "total_images": 45,
    "unoptimized": 12,
    "missing_dimensions": 8,
    "using_img_tag": 15
  },
  "caching": {
    "routes_without_cache": 12,
    "api_without_cache_headers": 8,
    "missing_isr": 5
  },
  "rendering": {
    "missing_suspense": 4,
    "missing_skeletons": 8,
    "unnecessary_client_components": 6
  },
  "memory": {
    "potential_leaks": 3,
    "unbounded_caches": 2,
    "missing_cleanup": 5
  },
  "code_patterns": {
    "missing_debounce": 4,
    "large_lists_no_virtual": 2,
    "heavy_effects": 3
  },
  "code_efficiency": {
    "algorithmic": { "quadratic_patterns": 0, "linear_search_in_loops": 0, "array_as_lookup": 0 },
    "redundant_operations": { "repeated_derivations": 0, "client_side_filtering": 0, "json_clone_usage": 0 },
    "async_issues": { "sequential_parallelizable_awaits": 0, "await_in_loops": 0, "missing_abort_controllers": 0 },
    "state_waste": { "derived_state_in_usestate": 0, "overly_broad_context": 0, "missing_usememo": 0 },
    "scalability_flags": { "unbounded_collections": 0, "client_side_aggregation": 0, "missing_rate_limits": 0 },
    "dx_issues": { "god_functions": 0, "magic_numbers": 0, "deep_nesting": 0, "inconsistent_error_handling": 0 },
    "cost_issues": { "cold_start_heavy_imports": 0, "excessive_logging": 0, "polling_instead_of_events": 0 },
    "total_findings": 0,
    "auto_fixable": 0,
    "needs_review": 0
  }
}
```

---

## PHASE 2: COMPREHENSIVE AUDIT

### 2.1 Bundle & Loading Analysis

| Check | What to Find | Finding ID |
|-------|--------------|------------|
| **Large routes** | First Load JS > 200kB | PERF-BUNDLE-001 |
| **Heavy imports** | Large libraries in client components | PERF-BUNDLE-002 |
| **Missing code splitting** | No dynamic imports for heavy components | PERF-BUNDLE-003 |
| **Missing barrel optimization** | Importing entire barrel files | PERF-BUNDLE-004 |
| **Duplicate dependencies** | Same lib in multiple versions | PERF-BUNDLE-005 |

### 2.2 Database & API Performance

| Check | What to Find | Finding ID |
|-------|--------------|------------|
| **Unbounded queries** | SELECT without LIMIT | PERF-DB-001 |
| **N+1 queries** | Queries in loops | PERF-DB-002 |
| **Missing indexes** | Slow queries on unindexed columns | PERF-DB-003 |
| **SELECT *** | Fetching unnecessary columns | PERF-DB-004 |
| **No pagination** | Loading all records at once | PERF-DB-005 |

### 2.3 Caching Strategies

| Check | What to Find | Finding ID |
|-------|--------------|------------|
| **No HTTP caching** | API routes without Cache-Control | PERF-CACHE-001 |
| **Missing ISR** | Static pages without revalidate | PERF-CACHE-002 |
| **No client caching** | Fetches without SWR/React Query | PERF-CACHE-003 |
| **Missing memoization** | Expensive computations not cached | PERF-CACHE-004 |

### 2.4 Rendering Optimization

| Check | What to Find | Finding ID |
|-------|--------------|------------|
| **Missing Suspense** | No streaming for slow data | PERF-RENDER-001 |
| **No skeleton states** | Spinners instead of skeletons | PERF-RENDER-002 |
| **Layout shift** | Elements causing CLS | PERF-RENDER-003 |
| **Unnecessary 'use client'** | Server components marked client | PERF-RENDER-004 |
| **Missing memo** | Expensive components not memoized | PERF-RENDER-005 |

### 2.5 Pre-loading & Pre-fetching

| Check | What to Find | Finding ID |
|-------|--------------|------------|
| **Missing preconnect** | Third-party origins without preconnect | PERF-PREFETCH-001 |
| **No preload** | Critical resources not preloaded | PERF-PREFETCH-002 |
| **No route prefetch** | Navigation targets not prefetched | PERF-PREFETCH-003 |

### 2.6 Image Optimization

| Check | What to Find | Finding ID |
|-------|--------------|------------|
| **Not using next/image** | Raw <img> tags | PERF-IMAGE-001 |
| **Missing dimensions** | Images without width/height | PERF-IMAGE-002 |
| **Missing priority** | Hero images without priority | PERF-IMAGE-003 |
| **No lazy loading** | Below-fold images eager-loaded | PERF-IMAGE-004 |

### 2.7 Memory Management

| Check | What to Find | Finding ID |
|-------|--------------|------------|
| **Unbounded cache** | Map/Set without size limit | PERF-MEM-001 |
| **No cleanup** | useEffect without cleanup | PERF-MEM-002 |
| **Interval leak** | setInterval without clear | PERF-MEM-003 |
| **Subscription leak** | Subscriptions not unsubscribed | PERF-MEM-004 |

### 2.8 JavaScript Patterns

| Check | What to Find | Finding ID |
|-------|--------------|------------|
| **No debounce** | Expensive handlers on frequent events | PERF-JS-001 |
| **Missing virtual scroll** | Rendering 1000+ list items | PERF-JS-002 |
| **Main thread blocking** | Heavy computation in render | PERF-JS-003 |

### 2.9 UX Performance

| Check | What to Find | Finding ID |
|-------|--------------|------------|
| **No optimistic updates** | Waiting for server on mutations | PERF-UX-001 |
| **Missing loading states** | No feedback during operations | PERF-UX-002 |
| **No error boundaries** | Errors crash entire app | PERF-UX-003 |

### 2.10 Code Efficiency Audit

> **Purpose:** Captures everything a senior engineer or engineering manager would flag in a code review — algorithmic waste, redundant operations, concurrency mistakes, state architecture problems, scalability red flags, and maintainability patterns that compound into real performance and cost issues over time.
>
> **Agent model:** `sonnet` — every check requires reasoning about code semantics, not literal string matching.

#### 2.10.1 Algorithmic Inefficiency

| Check | What to Find | Finding ID |
|-------|--------------|------------|
| **O(n^2) nested lookups** | `.find()`/`.includes()`/`.indexOf()` inside `.map()`/`.filter()`/`.forEach()`/`for` loops | PERF-ALGO-001 |
| **Linear search in loops** | `array.find()` or `array.filter()` called repeatedly where a `Set` or `Map` lookup suffices | PERF-ALGO-002 |
| **Repeated sorting** | `.sort()` called on the same array multiple times without mutation between calls | PERF-ALGO-003 |
| **Array as lookup table** | Using arrays with `.find(x => x.id === id)` when an object/Map keyed by ID is appropriate | PERF-ALGO-004 |
| **Unnecessary full scans** | `.find()` or `.filter()` on entire collection when index/position is known or could be cached | PERF-ALGO-005 |
| **String concatenation in loops** | Building strings with `+=` in a loop instead of `.join()` or template literals | PERF-ALGO-006 |

#### 2.10.2 Redundant Operations

| Check | What to Find | Finding ID |
|-------|--------------|------------|
| **Repeated derived values** | Same computation (e.g., `items.filter(...).length`, date formatting) done multiple times in one component/function | PERF-REDUN-001 |
| **Multiple API calls instead of batch** | Sequential or parallel calls to the same table/endpoint that could be a single query with `.in()` or a join | PERF-REDUN-002 |
| **Client-side filtering of full dataset** | Fetching all rows then `.filter()` client-side when the filter could be a `.eq()`/`.ilike()` in the DB query | PERF-REDUN-003 |
| **Re-parsing at multiple layers** | Data transformed in the service layer, then re-transformed in the component, then re-transformed in a child | PERF-REDUN-004 |
| **Duplicate work across siblings** | Two sibling components independently fetching or computing the same data (should lift to parent or shared hook) | PERF-REDUN-005 |
| **JSON.parse(JSON.stringify()) for clone** | Deep clone via JSON round-trip when `structuredClone()` or spread operator is sufficient | PERF-REDUN-006 |
| **Re-creating objects/arrays in render** | Inline object/array literals in JSX props that create new references every render (triggers unnecessary child re-renders) | PERF-REDUN-007 |

#### 2.10.3 Code Conciseness & Patterns

| Check | What to Find | Finding ID |
|-------|--------------|------------|
| **Long if/else chains** | > 3 chained if/else blocks that could be a lookup table or object map | PERF-PATTERN-001 |
| **Verbose switch dispatch** | Switch statements with > 5 cases doing similar work that could be an object dispatch pattern | PERF-PATTERN-002 |
| **Manual array manipulation** | Hand-written loops for operations that `.reduce()`, `.flatMap()`, or `Object.fromEntries()` handles cleanly | PERF-PATTERN-003 |
| **Repeated inline logic** | Same 3+ line logic block copy-pasted across 2+ locations (should be a utility function) | PERF-PATTERN-004 |
| **Verbose boolean evaluation** | Manual boolean accumulation in a loop where `.every()` or `.some()` is cleaner and short-circuits | PERF-PATTERN-005 |
| **Deep ternary nesting** | Nested ternaries (> 2 levels) that should be early returns or a lookup | PERF-PATTERN-006 |

#### 2.10.4 Async & Concurrency

| Check | What to Find | Finding ID |
|-------|--------------|------------|
| **Sequential awaits (parallelizable)** | Multiple `await` statements in sequence where the calls are independent and could use `Promise.all()` | PERF-ASYNC-001 |
| **Missing Promise.allSettled()** | Independent operations where one failure shouldn't abort the others, but `Promise.all()` or sequential awaits are used | PERF-ASYNC-002 |
| **Blocking ops in hot paths** | Synchronous heavy computation, `JSON.parse` of large payloads, or complex regex in request handlers / render functions | PERF-ASYNC-003 |
| **Missing request deduplication** | Same API endpoint called simultaneously from multiple components without dedup (no SWR/React Query, no shared promise) | PERF-ASYNC-004 |
| **Thundering herd on cache miss** | Multiple concurrent requests trigger the same expensive operation when cache is empty — no lock/singleflight pattern | PERF-ASYNC-005 |
| **Missing AbortController** | Fetch calls in useEffect or event handlers that don't cancel on unmount or superseding call | PERF-ASYNC-006 |
| **Await in loop body** | `for` loop with `await` inside that could be `Promise.all(items.map(...))` | PERF-ASYNC-007 |

#### 2.10.5 State Architecture Waste

| Check | What to Find | Finding ID |
|-------|--------------|------------|
| **Overly broad parent state** | Parent component holds state that only one child uses, causing all children to re-render on change | PERF-STATE-001 |
| **Prop drilling causing re-renders** | State passed through 3+ intermediate components that don't use it (should colocate or use context selectively) | PERF-STATE-002 |
| **Duplicate state** | Same data stored in two places (e.g., local state and context, or two sibling states) that can get out of sync | PERF-STATE-003 |
| **Derived state in useState** | Value that could be computed from existing state/props stored in its own `useState` with a sync `useEffect` | PERF-STATE-004 |
| **Context provider wrapping too much** | Context provider wraps the entire app or large subtree when only a small section consumes the value | PERF-STATE-005 |
| **State too far from usage** | State defined in a distant ancestor when it's only used by a leaf component (should colocate) | PERF-STATE-006 |
| **Missing useMemo for expensive derivation** | Expensive computation (sort, filter, aggregate over large array) runs on every render without `useMemo` | PERF-STATE-007 |

#### 2.10.6 API & Network Efficiency

| Check | What to Find | Finding ID |
|-------|--------------|------------|
| **Waterfall requests** | Component fetches A, waits, then fetches B using A's result — when B could be fetched via a join or parallel with A | PERF-API-001 |
| **Multiple round trips for joinable data** | Separate queries to related tables that could be a single Supabase query with foreign key joins | PERF-API-002 |
| **Missing batch endpoints** | N individual mutations (create/update/delete) where a single `.upsert()` or bulk operation works | PERF-API-003 |
| **Over-fetching fields** | Selecting columns never rendered (checks component usage, complements PERF-DB-004) | PERF-API-004 |
| **Missing pagination on large datasets** | Endpoint returns unbounded results to client without offset/limit (checks client handling, complements PERF-DB-005) | PERF-API-005 |
| **No request deduplication layer** | Same data fetched by multiple routes/components with no shared caching layer (SWR, React Query, or manual cache) | PERF-API-006 |
| **Chatty API pattern** | Page makes > 5 separate API calls on mount that could be consolidated into 1-2 aggregated calls | PERF-API-007 |

#### 2.10.7 Build-Time vs Runtime

| Check | What to Find | Finding ID |
|-------|--------------|------------|
| **Constants computed at runtime** | Values derived from static data (e.g., `Object.keys(STATIC_CONFIG)`) computed on every render/request instead of at module level | PERF-BUILDTIME-001 |
| **RegExp in render/loop** | `new RegExp(...)` or regex literal inside a function called frequently — should be module-level constant | PERF-BUILDTIME-002 |
| **Config loaded per request** | Environment variables parsed or config objects assembled on every request instead of once at module load | PERF-BUILDTIME-003 |
| **Static data fetched from API** | Data that never changes (feature flags, category lists, plan tiers) fetched at runtime instead of generated at build time or defined as constants | PERF-BUILDTIME-004 |
| **Date/formatter objects recreated** | `new Intl.DateTimeFormat()`, `new Intl.NumberFormat()` created on every render instead of cached at module level | PERF-BUILDTIME-005 |

#### 2.10.8 Defensive Coding Overhead

| Check | What to Find | Finding ID |
|-------|--------------|------------|
| **Excessive null checks on typed internals** | Null/undefined checks on values that TypeScript already guarantees are defined at that point | PERF-DEFENSIVE-001 |
| **Try/catch wrapping non-throwing code** | Try/catch around pure synchronous logic that cannot throw (math, string operations, object access on known shapes) | PERF-DEFENSIVE-002 |
| **Redundant type guards** | Type narrowing checks on internal function boundaries where the caller already ensures the type | PERF-DEFENSIVE-003 |
| **Catch-and-swallow** | `catch (e) { /* empty or just logs */ }` that silently hides errors instead of propagating or handling meaningfully | PERF-DEFENSIVE-004 |
| **Defensive deep clone when immutable** | `structuredClone()` or spread-clone of data that's never mutated downstream | PERF-DEFENSIVE-005 |
| **Upstream-checked conditions re-checked** | Condition already validated by caller, middleware, or Zod schema is re-validated in the callee | PERF-DEFENSIVE-006 |

#### 2.10.9 Scalability Red Flags

| Check | What to Find | Finding ID |
|-------|--------------|------------|
| **Hidden O(n^2) growth** | Loops that are O(n) today but nest over a second dimension that will grow (e.g., users x items, spaces x members) | PERF-SCALE-001 |
| **Unbounded in-memory collections** | `Map`, `Set`, or plain object used as cache without eviction policy or max size | PERF-SCALE-002 |
| **Full table scans on growing tables** | Queries without index-backed WHERE clauses on tables expected to grow > 10k rows | PERF-SCALE-003 |
| **Client-side aggregation** | `.reduce()` / manual aggregation of server data that should be a DB `SUM()`, `COUNT()`, `AVG()` | PERF-SCALE-004 |
| **New connection per request** | Creating Supabase client or other connection inside request handlers without pooling/reuse | PERF-SCALE-005 |
| **Missing rate limiting on expensive ops** | Expensive operations (AI calls, PDF generation, bulk exports) without rate limiting | PERF-SCALE-006 |
| **Unbounded subscription fan-out** | Real-time subscriptions that listen to entire tables instead of filtered channels | PERF-SCALE-007 |

#### 2.10.10 Developer Experience & Maintainability Efficiency

| Check | What to Find | Finding ID |
|-------|--------------|------------|
| **God functions** | Functions > 50 lines with multiple responsibilities (fetch + transform + render logic mixed) | PERF-DX-001 |
| **Deep callback nesting** | > 3 levels of nested callbacks, `.then()` chains, or conditional blocks (should flatten with early returns or async/await) | PERF-DX-002 |
| **Magic numbers/strings** | Unexplained numeric or string literals (e.g., `if (items.length > 50)`, `role === 'admin'`) without named constants | PERF-DX-003 |
| **Inconsistent error handling** | Similar service functions handling errors differently (some throw, some return null, some log and swallow) | PERF-DX-004 |
| **Complex conditionals** | Boolean expressions with > 3 clauses that could be early returns, guard clauses, or named boolean variables | PERF-DX-005 |
| **Functions with > 5 parameters** | Functions accepting > 5 positional parameters instead of an options object | PERF-DX-006 |
| **Dead code paths** | Unreachable branches, always-true/false conditions, or feature flag code for flags that no longer toggle | PERF-DX-007 |

#### 2.10.11 Infrastructure Cost Awareness

| Check | What to Find | Finding ID |
|-------|--------------|------------|
| **Cold start heavy imports** | Top-level imports of large modules (`pdf-lib`, `chart.js`, heavy AI SDKs) in serverless/edge functions that inflate cold start | PERF-COST-001 |
| **Unnecessary middleware on every request** | Middleware that runs expensive logic (DB queries, auth checks, rate limit lookups) on routes that don't need it | PERF-COST-002 |
| **Polling instead of event-driven** | `setInterval` or cron polling for data that could use webhooks, real-time subscriptions, or DB triggers | PERF-COST-003 |
| **Excessive production logging** | `JSON.stringify` of large objects in production logs, verbose logging in hot paths, or logging inside loops | PERF-COST-004 |
| **Missing CDN/edge caching** | API responses for stable data (plan info, feature lists, public content) not cached at CDN/edge layer | PERF-COST-005 |
| **Expensive ops without result caching** | Expensive computations (AI inference, PDF generation, complex aggregations) repeated for same inputs without memoization | PERF-COST-006 |
| **Oversized serverless payloads** | API responses returning significantly more data than the client uses, inflating bandwidth costs | PERF-COST-007 |

#### Auto-Fix vs Flagged Classification

| Category | Auto-Fixable (safe without human review) | Flagged for Review (needs human decision) |
|----------|------------------------------------------|------------------------------------------|
| **ALGO** | ALGO-002 (Set/Map conversion), ALGO-006 (string join) | ALGO-001 (nested loop refactor), ALGO-003/004/005 (data structure changes) |
| **REDUN** | REDUN-001 (extract to const), REDUN-006 (structuredClone), REDUN-007 (extract to useMemo/const) | REDUN-002 (batch API), REDUN-003 (push filter to DB), REDUN-004/005 (architecture) |
| **PATTERN** | PATTERN-005 (.every/.some), PATTERN-006 (early returns) | PATTERN-001 (lookup table), PATTERN-002 (dispatch), PATTERN-003/004 (new abstractions) |
| **ASYNC** | ASYNC-001 (Promise.all), ASYNC-006 (AbortController), ASYNC-007 (map + Promise.all) | ASYNC-002 (allSettled changes error semantics), ASYNC-005 (singleflight is architectural) |
| **STATE** | STATE-004 (remove useState+useEffect, compute inline), STATE-007 (add useMemo) | STATE-001/002/003/005/006 (component restructuring) |
| **API** | None (all involve contract/architecture changes) | All PERF-API-* findings |
| **BUILDTIME** | BUILDTIME-001 (hoist to module level), BUILDTIME-002 (hoist regex), BUILDTIME-005 (hoist formatter) | BUILDTIME-003 (config caching), BUILDTIME-004 (SSG/ISR is architectural) |
| **DEFENSIVE** | DEFENSIVE-001 (remove redundant null checks), DEFENSIVE-005 (remove unnecessary clones) | DEFENSIVE-003/004/006 (error strategy decisions) |
| **SCALE** | None (all require design decisions) | All PERF-SCALE-* findings |
| **DX** | DX-003 (extract magic numbers to constants), DX-005 (early return refactor) | DX-001/002/004/006/007 (design work) |
| **COST** | COST-004 (reduce logging verbosity) | All others (infrastructure decisions) |

---

## PHASE 3: EXECUTE OPTIMIZATIONS

### 3.1 Execution Order (Dependencies Respected)

1. **Bundle optimizations** - Dynamic imports, code splitting
2. **Database fixes** - Add limits, pagination, indexes
3. **Code efficiency auto-fixes** - Promise.all, constant extraction, useMemo, lookup tables (from 2.10 findings marked auto-fixable)
4. **Caching** - Add headers, ISR, client caching
5. **Rendering** - Add skeletons, Suspense, memo
6. **Images** - Convert to next/image, add dimensions
7. **Pre-fetching** - Add preconnect, preload
8. **Memory** - Add cleanup, limits
9. **UX** - Add optimistic updates, loading states
10. **Code efficiency flagged items** - Document in deferred table with refactor suggestions (from 2.10 findings marked flagged-only)

### 3.2 Auto-Generated Assets

**Skeleton Components:**
```typescript
// Generated: src/components/skeletons/UserCardSkeleton.tsx
export function UserCardSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="w-12 h-12 rounded-full bg-gray-200" />
      <div className="h-4 w-32 bg-gray-200 rounded mt-2" />
    </div>
  );
}
```

**Database Migrations:**
```sql
-- Generated: supabase/migrations/20260205_perf_indexes.sql
CREATE INDEX CONCURRENTLY idx_posts_author_id ON posts(author_id);
CREATE INDEX CONCURRENTLY idx_comments_post_id ON comments(post_id);
```

### 3.3 Verification After Each Fix

```bash
# After each optimization
npm run build > /dev/null 2>&1 || { git checkout -- .; echo "Build failed, reverted"; }
npm test > /dev/null 2>&1 || { git checkout -- .; echo "Tests failed, reverted"; }
```

---

## PHASE 4: AFTER METRICS MEASUREMENT

### 4.1 Re-Measure Everything

**CRITICAL: Do this AFTER all optimizations**

```bash
# Rebuild and capture
npm run build 2>&1 | tee .perf/build-after.txt

# Extract route sizes
grep -A 100 "Route (app)" .perf/build-after.txt | head -50 > .perf/routes-after.txt
```

### 4.2 After Metrics Schema

Same structure as baseline, but with `"type": "after"`

---

## PHASE 5: REPORT WITH BEFORE/AFTER COMPARISON

### 5.1 Main Report File

**Filename:** `.perf/perf-YYYYMMDD-HHMMSS.md`

```markdown
# Performance Optimization Report: [PROJECT_NAME]

**Created:** [YYYY-MM-DD HH:MM:SS]
**Commit Before:** [commit_hash]
**Commit After:** [commit_hash]
**Status:** 🟢 COMPLETE

---

## Executive Summary

### Bundle Size Improvements

| Route | Before | After | Saved | Improvement |
|-------|--------|-------|-------|-------------|
| / | 89 kB | 72 kB | 17 kB | **19.1%** ✅ |
| /dashboard | 312 kB | 89 kB | 223 kB | **71.5%** ✅ |
| /settings | 156 kB | 78 kB | 78 kB | **50.0%** ✅ |
| **Total First Load** | **312 kB** | **89 kB** | **223 kB** | **71.5%** ✅ |

### Build Performance

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Build Time | 67s | 45s | **32.8%** faster |
| Total Bundle | 1.2 MB | 480 kB | **60.0%** smaller |
| Package Count | 145 | 142 | 3 removed |

### Core Web Vitals (Live Measured)

| Metric | Before | After | Target | Status |
|--------|--------|-------|--------|--------|
| LCP | 3.2s | 1.8s | < 2.5s | ✅ Good |
| FCP | 2.1s | 1.2s | < 1.8s | ✅ Good |
| CLS | 0.15 | 0.05 | < 0.1 | ✅ Good |
| INP | 280ms | 150ms | < 200ms | ✅ Good |
| TTFB | 450ms | 120ms | < 800ms | ✅ Good |

### Performance Budget Status

[Budget dashboard — all metrics vs industry budgets, PASS/FAIL per metric]

### Third-Party Impact

| Domain | Scripts | Size | % of Total |
|--------|---------|------|-----------|
| [domain] | [count] | [size] | [%] |

### Slowest Resources (Top 10)

| # | Resource | Duration | Size | Type |
|---|----------|----------|------|------|
| 1 | [resource] | [ms] | [kB] | [type] |

### Database Performance

| Query | Before | After | Improvement |
|-------|--------|-------|-------------|
| Get all users | 1,847ms | 45ms | **97.6%** faster |
| Get comments | 340ms | 8ms | **97.6%** faster |
| Dashboard load | 2,100ms | 180ms | **91.4%** faster |

### Caching Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Routes with cache | 0 | 12 | +12 routes |
| API cache headers | 0 | 8 | +8 endpoints |
| ISR enabled | 0 | 5 | +5 pages |

### Memory Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Potential leaks | 3 | 0 | -3 fixed |
| Unbounded caches | 2 | 0 | -2 fixed |
| Missing cleanup | 5 | 0 | -5 fixed |

### UX Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Skeleton states | 0 | 8 | +8 components |
| Suspense boundaries | 0 | 4 | +4 boundaries |
| Optimistic updates | 0 | 3 | +3 mutations |
| Loading states | 2 | 12 | +10 states |

### Code Efficiency Improvements

| Category | Findings | Auto-Fixed | Flagged | Impact |
|----------|----------|------------|---------|--------|
| Algorithmic (PERF-ALGO) | 0 | 0 | 0 | Reduced O(n²) to O(n) in N places |
| Redundant Ops (PERF-REDUN) | 0 | 0 | 0 | Eliminated N redundant computations |
| Patterns (PERF-PATTERN) | 0 | 0 | 0 | Replaced N verbose patterns with idiomatic code |
| Async (PERF-ASYNC) | 0 | 0 | 0 | Parallelized N sequential awaits |
| State Architecture (PERF-STATE) | 0 | 0 | 0 | Reduced N unnecessary re-renders |
| API/Network (PERF-API) | 0 | 0 | 0 | Eliminated N waterfall requests |
| Build-Time vs Runtime (PERF-BUILDTIME) | 0 | 0 | 0 | Moved N computations out of hot paths |
| Defensive Overhead (PERF-DEFENSIVE) | 0 | 0 | 0 | Removed N redundant checks |
| Scalability (PERF-SCALE) | 0 | 0 | 0 | Fixed N hidden scaling issues |
| DX/Maintainability (PERF-DX) | 0 | 0 | 0 | Simplified N complex functions |
| Infrastructure Cost (PERF-COST) | 0 | 0 | 0 | Reduced N cost-inefficient patterns |
| **Total** | **0** | **0** | **0** | |

---

## Task List

### Bundle Optimizations

- [x] **PERF-BUNDLE-001**: Dynamic import chart.js on /dashboard
  - Before: 312 kB First Load JS
  - After: 89 kB First Load JS
  - Saved: 223 kB (71.5%)
  - Status: ✅ DONE

- [x] **PERF-BUNDLE-002**: Dynamic import pdf-lib on /export
  - Before: 420 kB
  - After: 95 kB
  - Saved: 325 kB (77.4%)
  - Status: ✅ DONE

- [x] **PERF-BUNDLE-003**: Replace lodash with lodash-es
  - Before: 72 kB
  - After: 12 kB (tree-shaken)
  - Saved: 60 kB (83.3%)
  - Status: ✅ DONE

### Database Optimizations

- [x] **PERF-DB-001**: Add pagination to users query
  - Before: 1,847ms (50k rows)
  - After: 45ms (50 rows + pagination)
  - Improvement: 97.6%
  - Status: ✅ DONE

- [x] **PERF-DB-002**: Add index on posts.author_id
  - Before: 340ms
  - After: 8ms
  - Improvement: 97.6%
  - Migration: `20260205_perf_indexes.sql`
  - Status: ✅ DONE

- [x] **PERF-DB-003**: Fix N+1 query in comments
  - Before: 50 queries (1 per post)
  - After: 1 query (with join)
  - Improvement: 98%
  - Status: ✅ DONE

### Caching Optimizations

- [x] **PERF-CACHE-001**: Add cache headers to 8 API routes
  - Added: `Cache-Control: public, s-maxage=60, stale-while-revalidate=300`
  - Status: ✅ DONE

- [x] **PERF-CACHE-002**: Enable ISR on 5 static pages
  - Added: `export const revalidate = 3600`
  - Status: ✅ DONE

### Rendering Optimizations

- [x] **PERF-RENDER-001**: Add Suspense boundaries (4)
  - Files: dashboard, settings, profile, analytics
  - Status: ✅ DONE

- [x] **PERF-RENDER-002**: Create skeleton components (8)
  - Created: UserCardSkeleton, StatsCardSkeleton, TableSkeleton, etc.
  - Status: ✅ DONE

- [x] **PERF-RENDER-003**: Convert 6 components to server components
  - Removed unnecessary 'use client' directives
  - Status: ✅ DONE

### Image Optimizations

- [x] **PERF-IMAGE-001**: Convert 15 <img> to next/image
  - Added: width, height, alt, lazy loading
  - Status: ✅ DONE

- [x] **PERF-IMAGE-002**: Add priority to 3 hero images
  - Files: landing, about, pricing pages
  - Status: ✅ DONE

### Pre-fetching Optimizations

- [x] **PERF-PREFETCH-001**: Add preconnect tags
  - Added: fonts.googleapis.com, supabase, analytics
  - Status: ✅ DONE

- [x] **PERF-PREFETCH-002**: Preload critical fonts
  - Added: Inter font preload
  - Status: ✅ DONE

### Memory Optimizations

- [x] **PERF-MEM-001**: Add LRU cache with eviction
  - Before: Unbounded Map
  - After: LRUCache { max: 500, ttl: 5min }
  - Status: ✅ DONE

- [x] **PERF-MEM-002**: Fix 5 useEffect cleanup issues
  - Added: cleanup functions for subscriptions
  - Status: ✅ DONE

### UX Optimizations

- [x] **PERF-UX-001**: Add optimistic updates to 3 mutations
  - Like, bookmark, follow actions
  - Status: ✅ DONE

- [x] **PERF-UX-002**: Add loading states to 10 components
  - Status: ✅ DONE

### Code Efficiency — Auto-Fixed

- [x] **PERF-ASYNC-001**: Convert 3 sequential awaits to Promise.all in dashboard loader
  - Before: 3 serial DB queries (~450ms total)
  - After: 3 parallel queries (~160ms total)
  - Improvement: 64.4%
  - Status: ✅ DONE

- [x] **PERF-REDUN-001**: Extract repeated date formatting into cached formatter
  - Before: `new Intl.DateTimeFormat()` created 47 times per render
  - After: Single shared formatter instance
  - Status: ✅ DONE

- [x] **PERF-BUILDTIME-001**: Move 4 constant arrays/objects out of render functions
  - Eliminated per-render object allocation
  - Status: ✅ DONE

- [x] **PERF-PATTERN-001**: Replace 3 if/else chains with lookup tables
  - Before: 15-25 line switch/if blocks
  - After: 5-8 line object lookups
  - Status: ✅ DONE

### Code Efficiency — Flagged for Review

- [ ] **PERF-ALGO-001**: Nested array.find() inside loop in chores-service.ts
  - Complexity: O(n×m) — should be O(n) with a Map
  - Status: ⚠️ FLAGGED — needs careful testing of edge cases

- [ ] **PERF-STATE-001**: Broad parent re-renders from context in DashboardLayout
  - 12 children re-render on unrelated state changes
  - Status: ⚠️ FLAGGED — needs architecture review

- [ ] **PERF-SCALE-001**: Client-side filtering of 500+ items in shopping list
  - Should filter server-side with query params
  - Status: ⚠️ FLAGGED — API change needed

### Flagged for Future (Infrastructure)

- [ ] **PERF-BUILD-001**: Consider edge runtime for /api/public/*
  - Status: ⚠️ FLAGGED
  - Reason: Requires review of dependencies

- [ ] **PERF-JS-001**: Add virtual scroll to user list (1000+ items)
  - Status: ⚠️ FLAGGED
  - Reason: Requires UX review

---

## Files Modified

| File | Changes | Lines |
|------|---------|-------|
| `src/app/dashboard/page.tsx` | Dynamic import, Suspense | +15, -8 |
| `src/app/api/users/route.ts` | Pagination, cache headers | +12, -3 |
| `src/components/UserCard.tsx` | next/image, skeleton | +25, -10 |
| `next.config.js` | optimizePackageImports | +5 |
| ... | ... | ... |

**Total Files Modified:** 34
**Total Files Created:** 12 (skeletons, migrations)
**Net Lines:** +245, -380 = **-135 lines**

---

## Generated Assets

### Skeleton Components Created

| Component | Location |
|-----------|----------|
| UserCardSkeleton | `src/components/skeletons/UserCardSkeleton.tsx` |
| StatsCardSkeleton | `src/components/skeletons/StatsCardSkeleton.tsx` |
| TableSkeleton | `src/components/skeletons/TableSkeleton.tsx` |
| DashboardSkeleton | `src/components/skeletons/DashboardSkeleton.tsx` |

### Database Migrations Created

| Migration | Purpose |
|-----------|---------|
| `20260205_perf_indexes.sql` | Add indexes for author_id, post_id |

---

## Verification Results

| Check | Status | Details |
|-------|--------|---------|
| TypeScript | ✅ Pass | No errors |
| Build | ✅ Pass | 45s (was 67s) |
| Tests | ✅ Pass | 156/156 passing |
| Bundle Size | ✅ Pass | < 100kB first load |

---

## SITREP (Conclusion)

> Reference: [SITREP Standard](~/.claude/standards/SITREP_FORMAT.md) — use the unified template with domain-specific additions below.

### Mission Status: 🟢 COMPLETE

**Optimization Duration:** 18 minutes 42 seconds

### What Was Accomplished

1. **Bundle Size Reduced by 71.5%**
   - Before: 312 kB First Load JS
   - After: 89 kB First Load JS
   - Method: Dynamic imports for chart.js, pdf-lib; replaced lodash with lodash-es

2. **Database Performance Improved by 97%**
   - Slowest query: 1,847ms → 45ms
   - Added pagination to 3 unbounded queries
   - Created 2 indexes for frequently filtered columns
   - Fixed 1 N+1 query pattern

3. **Caching Implemented Across Stack**
   - 8 API routes now have cache headers
   - 5 pages now use ISR (revalidate every hour)
   - Client-side caching with SWR on 4 data fetches

4. **UX Dramatically Improved**
   - Created 8 skeleton components (perceived performance)
   - Added 4 Suspense boundaries (streaming)
   - Implemented optimistic updates on 3 mutations
   - Added loading states to 10 components

5. **Memory Leaks Eliminated**
   - Fixed 3 potential memory leaks
   - Converted 2 unbounded caches to LRU
   - Added cleanup to 5 useEffect hooks

6. **Code Efficiency Improved**
   - Parallelized N sequential await chains (PERF-ASYNC)
   - Eliminated N redundant computations per render cycle (PERF-REDUN)
   - Moved N constant allocations out of hot paths (PERF-BUILDTIME)
   - Replaced N verbose control flow patterns with lookup tables (PERF-PATTERN)
   - Flagged N architectural issues for review (PERF-STATE, PERF-SCALE, PERF-ALGO)

### Performance Gains Summary

| Category | Improvement |
|----------|-------------|
| Bundle Size | **-71.5%** |
| Build Time | **-32.8%** |
| Database Queries | **-97.6%** (avg) |
| Estimated LCP | **-43.8%** |
| Estimated FCP | **-42.9%** |
| Memory Leaks | **-100%** (all fixed) |
| Code Efficiency | **N findings fixed, M flagged** |

### Remaining Items

2 items flagged for future optimization:
- Edge runtime consideration for public APIs
- Virtual scroll for large lists

### Recommendations

1. Run `/perf incremental` after next major feature
2. Monitor Core Web Vitals in production with Vercel Analytics
3. Consider implementing service worker for offline support
4. Schedule review of flagged items in 2 weeks

### Historical Context

This is performance audit #3 for this project:
- Audit #1 (2025-12-01): Initial audit, 45% bundle reduction
- Audit #2 (2026-01-15): Post-feature audit, 20% improvement
- **Audit #3 (today):** Pre-launch optimization, 71.5% improvement

**Cumulative improvement since first audit:**
- Bundle: 580 kB → 89 kB (**84.7% reduction**)
- Build time: 120s → 45s (**62.5% faster**)
- Avg query time: 2.5s → 45ms (**98.2% faster**)

---

*Report generated by /perf*
*Full history available in .perf/history.json*
*Before metrics: .perf/baseline.json*
*After metrics: .perf/current.json*
```

### 5.2 Update History

Append to `.perf/history.json`:

```json
{
  "audits": [
    {
      "id": 3,
      "timestamp": "2026-02-05T15:00:00Z",
      "commit_before": "abc123",
      "commit_after": "def456",
      "duration_seconds": 1122,
      "improvements": {
        "bundle_reduction_percent": 71.5,
        "build_time_reduction_percent": 32.8,
        "database_improvement_percent": 97.6,
        "memory_leaks_fixed": 3,
        "skeletons_created": 8,
        "cache_routes_added": 8
      },
      "metrics_before": {
        "first_load_js_kb": 312,
        "build_time_seconds": 67,
        "slowest_query_ms": 1847
      },
      "metrics_after": {
        "first_load_js_kb": 89,
        "build_time_seconds": 45,
        "slowest_query_ms": 45
      },
      "tasks_completed": 18,
      "tasks_flagged": 2,
      "report_file": ".perf/perf-20260205-150000.md"
    }
  ]
}
```

---

## INCREMENTAL MODE

For subsequent runs (`/perf incremental`):

### Detect Changes Since Last Audit

```bash
LAST_COMMIT=$(jq -r '.audits[-1].commit_after' .perf/history.json)
CHANGED_FILES=$(git diff --name-only $LAST_COMMIT HEAD -- "*.ts" "*.tsx")
```

### Focused Analysis

Only analyze:
- Files changed since last audit
- New routes added
- New dependencies in package.json
- New API endpoints

### Regression Detection

Compare current metrics against last audit:

```
⚠️ REGRESSION DETECTED

Route /dashboard increased from 89kB to 145kB
Cause: New import of 'pdf-lib' (56kB)
Recommendation: Dynamic import for PDF generation
```

---

## Rollback Procedure

```bash
echo "🔄 Rolling back performance changes..."
git reset --hard $PERF_BASE
echo "✅ Rolled back to: $PERF_BASE"
```

---

## REMEMBER

- **Measure BEFORE and AFTER** - Always capture metrics for comparison
- **Live measurement > build estimates** - Use actual `performance.getEntries()` from the running app, not just build output sizes
- **Calculate improvements** - Show exact percentages
- **Mark DONE, never delete** - Preserve task history for audit trail
- **Write SITREP conclusion** - Historical perspective for future reference
- **Incremental is default** - After first run, only check changes
- **Test after every fix** - Catch breakage immediately
- **Track cumulative gains** - Show improvement over time
- **Budget check is pass/fail** - Industry budgets are non-negotiable thresholds
- **Regression thresholds are tiered** - 20% = WARNING, 50% = REGRESSION. Don't alarm on normal variance.
- **Third-party JS is your hidden tax** - Always separate 1st vs 3rd party impact. You can't fix their code, but you can defer/async it.
- **Slowest resource wins** - The single slowest resource often matters more than total bundle size
- **Code efficiency is performance** - Algorithmic waste, redundant ops, and async misuse are as impactful as bundle size
- **Auto-fix safe patterns only** - Promise.all, constant extraction, useMemo additions are safe; architecture changes get flagged
- **Think like a senior reviewer** - Flag what a 20-year eng manager would catch in code review: hidden O(n²), scalability red flags, DX pain points
- **Baseline before deploy** - Run `/perf baseline` before shipping. Without it, post-deploy comparisons have no teeth.

---

## CLEANUP PROTOCOL

> Reference: [Resource Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md)

### Perf-Specific Cleanup

---

## RELATED SKILLS

**Feeds from:**
- `/design` - new UI components and layout changes directly impact Core Web Vitals
- `/monitor` - production performance regressions trigger a targeted perf run
- `/launch` - perf is a required gate in the launch pipeline

**Feeds into:**
- `/gh-ship` - perf fixes are committed and shipped via gh-ship
- `/launch` - perf score contributes to the GO/NO-GO verdict

**Pairs with:**
- `/a11y` - performance and accessibility audits are both quality gates; run together before launch
- `/cleancode` - dead code removal and perf optimization overlap on bundle size

**Auto-suggest after completion:**
- `/gh-ship` - "Perf fixes staged. Ship them? Run /gh-ship."
- `/launch` - "All quality gates passing? Run /launch for the full pre-ship verdict."

> Reference: [Resource Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md) — Ephemeral Artifact Policy

Cleanup actions:
1. **Close browser instances** — live CWV measurement uses Playwright MCP. Call `browser_close` and verify no orphaned Chromium.
2. **DELETE intermediate measurement files** — `live-metrics-before.json`, `live-metrics-after.json` are ephemeral. Only KEEP `baseline.json`, `current.json`, and `history.json`.
3. **DELETE old bundle analysis** — `bundle-analysis/` directories older than 30 days.
4. **DELETE old build output captures** — `build-before.txt`, `build-after.txt`, `routes-before.txt`, `routes-after.txt` from previous runs.
5. **KEEP report .md files** — these are the permanent record.
6. **KEEP history.json** — trend tracking across runs.
7. **Gitignore enforcement:** Ensure `.perf/` is in `.gitignore`
8. **Dev server cleanup:** If started for live measurement, kill PID and verify port released.

<!-- Claude Code Skill by Steel Motion LLC — https://steelmotion.dev -->
<!-- Part of the Claude Code Skills Collection -->
<!-- Powered by Claude models: Haiku (fast extraction), Sonnet (balanced reasoning), Opus (deep analysis) -->
<!-- License: MIT -->

---

## Suggested next

Per [Skill Auto-Suggest Protocol](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md), every SITREP MUST end with a "Suggested next" block. Use this decision matrix to pick:

| Outcome | Recommended | Why |
|---|---|---|
| Regressions detected | /investigate | find what changed |
| Optimizations applied | /test-ship | regression check |
| Lighthouse green, no regressions | /a11y | next quality dimension |
| Bundle bloated | /cleancode | dead-code elimination |

**Skip if:** the operator has already directed the next step, or this run was a no-op.
