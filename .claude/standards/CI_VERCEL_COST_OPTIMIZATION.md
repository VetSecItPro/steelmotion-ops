# CI + Vercel Cost Optimization Standard

> Cross-repo standard for minimizing CI compute and Vercel build minutes
> while preserving correctness signal. Apply this to every repo you ship.
>
> **Rewritten in place 2026-11-02.** The old "recommended default" (Pattern B: N PRs
> plus an integration PR) cost N+1 CI runs and contradicted the operator's rule: one work block,
> one branch, one PR. It is replaced below by the single-branch work-block default. The measured
> repo table replaces the old priority table, which rated the main site repo "Low" while it was 83% of
> the October bill.

## Executive principle

**CI cost scales with PR count × workflow scope × per-PR overhead.**
**Vercel cost scales with deploy count × build time.**

The cheap-shipping playbook attacks all four multipliers:
1. Reduce PR count: one work block = one branch = one PR (see "The work-block default")
2. Reduce workflow scope via path filters (don't run web's CI on CLI-only PRs)
3. Reduce per-PR overhead via merge queue + concurrency cancellation
4. Reduce build time via Turbo remote cache + Vercel `ignoredBuildStep`

Big-shipping teams (Vercel, Linear, Stripe, Shopify) all run this stack.
The default GitHub + Vercel config is *uneconomical* on monorepos - it's
on you to opt in to the optimizations.

---

## The 4 default gaps every monorepo has

Without explicit configuration, a monorepo with mixed packages
(e.g. `acme-web` + `acme-cli` + `acme-mobile`) pays for:

| Gap | What it costs |
|---|---|
| **Workflows trigger on every PR** regardless of touched files | Web's lint/typecheck/build runs on a CLI-only PR. ~80% of CI minutes are this overhead. |
| **No `ignoredBuildStep` in `vercel.json`** | Vercel builds the Next.js app on every push to main, even when only CLI/mobile/SQL changed. ~3 min × N PRs. |
| **No `turbo.json` remote cache** | Every CI run re-builds packages whose source didn't change. Adds 1-3 min per workflow. |
| **No merge queue + naive auto-merge** | N stacked PRs → N CI rebases → N Vercel deploys. Compound waste. |

**Rule of thumb**: a properly-configured monorepo CI is ~85% cheaper
than a default one for the same correctness signal.

---

## The 4-layer remediation stack

Apply each layer independently. Each compounds the previous savings.

### Layer 1: The work-block default (one branch, one PR)

**The default, for every session in every repo: one work block = one branch = one PR.**
Operator, 2026-11-02: "I'm tired of having too many damn PRs ... push a lot of work in there,
and then ... one PR ... so we don't have stale branches and work trees ... I'm not an enterprise.
I don't have unlimited funds."

The loop:
1. Cut one branch (and one worktree if another session shares the repo) for the block.
2. Commit each task on it locally. Push the branch freely with `/gh-ship --push-only` for
   backup. Where CI runs only on `pull_request`, a push with no PR open costs nothing.
3. Run the full local suite (lint, typecheck, unit tests, build) before the FIRST push.
4. When the block is done, open the PR once. CI runs once.
5. A CI failure is fixed locally and the fixes are pushed together, not one push per symptom;
   every push to an open PR re-runs billed CI.
6. Records (backlog rows, lessons, changelog) ride the work PR. Never a records-only PR.
7. Never a second PR while one is open; `gh-push-guard.py` refuses it
   (override: `PR_BATCH_OVERRIDE="<reason>"`, for a live security fix or a broken checkout).
8. Squash-merge, then delete the branch and the worktree the same hour. No stale branches.

CI cost for a block of N tasks: **1 run** (plus fix pushes), not N or N+1.

**When work really is independent across agents** (parallel agents on disjoint files), they still
commit to the one block branch (worktrees merge locally), not one PR each. Only genuinely separate
deliverables with different owners or release timing get separate PRs, and then one at a time.

**Merge queue** (section 2.4) is a fallback for repos where several humans open PRs at once. It is
not needed for a solo operator following this default. Stacked PRs are not used.

---

### Layer 2: GitHub Actions selectivity

#### 2.1 Path filters

Every workflow must declare what files trigger it. Default to NO trigger
for paths the workflow doesn't care about.

```yaml
# .github/workflows/web-ci.yml
on:
  pull_request:
    paths:
      - 'packages/acme-web/**'
      - 'packages/acme-shared/**'
      - 'pnpm-lock.yaml'
      - 'package.json'
      - '.github/workflows/web-ci.yml'
  push:
    branches: [main]
    paths:
      - 'packages/acme-web/**'
      - 'packages/acme-shared/**'
```

Repeat per-package: `cli-ci.yml` filters `packages/acme-cli/**` etc.

**Effect**: a CLI-only PR skips web's entire CI chain. Saves ~80% of
the per-PR fixed overhead.

#### 2.2 Concurrency cancellation

Cancel old in-flight runs when a new push lands on the same branch.

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref_name }}
  cancel-in-progress: true
```

**Effect**: rapid-fire pushes (e.g. fixing typos) don't queue 5 redundant
runs. Only the latest push runs.

#### 2.3 Caching (npm/pnpm install + build artifacts)

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.pnpm-store
      ~/.cache
      node_modules/.cache
      .next/cache
      packages/*/.next/cache
      packages/*/.tsbuildinfo
    key: ${{ runner.os }}-build-${{ hashFiles('pnpm-lock.yaml') }}-${{ hashFiles('packages/**/*.ts', 'packages/**/*.tsx') }}
    restore-keys: |
      ${{ runner.os }}-build-${{ hashFiles('pnpm-lock.yaml') }}-
      ${{ runner.os }}-build-
```

**Effect**: `pnpm install` returns in <10s on cache hit; Next.js incremental
build uses `.next/cache`. Saves 30-90s per workflow.

#### 2.4 GitHub Merge Queue (native, free on public repos)

Settings → Branches → Branch protection → main → "Require merge queue".

Once enabled, PRs go into the queue instead of merging directly.
GitHub batches up to N PRs into a single rebased branch and runs CI **once**
on the combined diff. After it passes, all N PRs merge.

**Effect**: N PRs → 1 batch CI run + 1 Vercel deploy. Most expensive single
optimization on this list.

**Setup**: enable in branch protection; add `merge_group:` trigger to your
workflows so CI runs in queue context too.

```yaml
on:
  pull_request:
  merge_group:  # required for merge queue
```

---

### Layer 3: Vercel selectivity

#### 3.1 `vercel.json` `ignoredBuildStep`

The single highest-leverage Vercel config. A shell command that
exits 0 to skip the build, 1 to proceed.

```jsonc
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "ignoredBuildStep": "bash -c 'git diff --quiet HEAD^ HEAD -- packages/acme-web packages/acme-shared package.json pnpm-lock.yaml turbo.json next.config.js && exit 0 || exit 1'"
}
```

**Read as**: if NO file in `packages/acme-web`, `packages/acme-shared`,
or critical root files changed → exit 0 (skip build). Otherwise exit 1
(build).

For monorepos where Vercel ships one package (`packages/acme-web`), this
saves the entire ~3 min build cost on every CLI-only / mobile-only / SQL-only
push.

**Verification**: Vercel logs show "Build skipped via ignoredBuildStep" in <1s.

#### 3.2 Disable preview deploys for irrelevant branches

```jsonc
{
  "git": {
    "deploymentEnabled": {
      "main": true,
      "preview/*": false
    }
  }
}
```

Use sparingly - preview deploys are valuable for QA. Better: rely on
`ignoredBuildStep` to short-circuit cheaply.

#### 3.3 Turbo + Vercel integration

If you use Turbo (recommended for monorepos), Vercel auto-detects it and
caches `turbo build --filter=...` outputs. No extra config needed beyond
having `turbo.json` in the repo root.

---

### Layer 4: Cache reuse across CI + Vercel

#### 4.1 `turbo.json` - even minimal config unlocks remote cache

```jsonc
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"]
    },
    "test": {
      "dependsOn": ["^build"],
      "outputs": []
    },
    "lint": {
      "outputs": []
    },
    "typecheck": {
      "dependsOn": ["^build"],
      "outputs": ["**/*.tsbuildinfo"]
    }
  }
}
```

Plus enable Vercel Remote Cache (free for personal accounts):
```bash
npx turbo login
npx turbo link
```

CI runs then auto-share cache with Vercel and other CI runs.

**Effect**: A CI run on a PR that doesn't touch `acme-web` returns
the web build instantly from Vercel's remote cache.

#### 4.2 GitHub Actions cache (npm/pnpm + `.next` + `.tsbuildinfo`)

See §2.3 above.

---

## Per-repo onboarding checklist

For every new repo OR existing repo missing this stack:

- [ ] **`turbo.json` at repo root** (even minimal - unlocks remote cache)
- [ ] **`vercel.json` with `ignoredBuildStep`** for any monorepo where Vercel
      only ships some packages
- [ ] **Path filters on every `.github/workflows/*.yml`** - declare which
      paths trigger which workflow
- [ ] **`concurrency:` block** on every workflow
- [ ] **`actions/cache`** for `~/.pnpm-store` + `node_modules/.cache` +
      `.next/cache` + `*.tsbuildinfo`
- [ ] **GitHub merge queue enabled** in branch protection (Settings →
      Branches → main → "Require merge queue")
- [ ] **`merge_group:` trigger** on workflows that should run in queue
- [ ] **Turbo remote cache linked** (`npx turbo link`)

Verification: a CLI-only PR should produce:
- ✓ Workflows that filter to web should NOT trigger
- ✓ Vercel deploy should skip with "Build skipped via ignoredBuildStep"
- ✓ Workflows that DO trigger should hit cache for unchanged packages
- ✓ Total billable CI minutes < 30s for the irrelevant workflows combined

---

## Multi-PR session patterns (superseded 2026-11-02)

The old Patterns A to D (sequential, stage-and-batch with an integration PR, stacked, merge queue)
all assumed several PRs per session. Pattern B, the old "recommended default", paid N CI runs for
the per-task PRs plus one for the integration PR. Under the work-block default there is one PR per
block, so there is no DAG to route. If a session finds itself holding several open PRs anyway
(inherited, or a bot opened them), merge them oldest first, one at a time, and do not open another
until they are gone.

---

## Cost worked example

*(Illustrative; written for the old several-PRs-per-session model. Under the work-block default the PR count is 1, which cuts the totals below further.)*

Monorepo with 5 PRs: 3 touch `packages/acme-cli`, 2 touch `packages/acme-web`.

### Without optimizations (default GitHub + Vercel)
- 5 × full CI workflow (lint+test+build for ALL packages) = ~10 min × 5 = **50 min CI**
- 5 × Vercel preview build + 5 × prod build = ~3 min × 10 = **30 min Vercel**
- **Total: ~80 min compute**

### With full optimization stack (this doc)
- 3 × CLI-only CI workflow (skip web) = ~2 min × 3 = 6 min
- 2 × web CI workflow + cached deps = ~5 min × 2 = 10 min
- 5 × Vercel: 3 skipped via `ignoredBuildStep` (~1s each), 2 build (~3 min × 2 = 6 min)
- 1 prod build at merge = 3 min
- **Total: ~25 min compute**

**~70% reduction** for the same correctness signal. Larger savings when
PR count grows or workflows are more expensive.

---

## Industry references

- **Vercel**: [Skip a build step](https://vercel.com/docs/projects/overview#ignored-build-step) - official `ignoredBuildStep` doc
- **GitHub**: [Merge queue](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue) - native batched-merge feature
- **Turbo**: [Remote caching](https://turbo.build/repo/docs/core-concepts/remote-caching) - cross-CI cache sharing
- **Linear blog**: [How Linear builds product](https://linear.app/blog/how-linear-builds-product) - small-PR + merge queue + Vercel ignoredBuildStep workflow
- **Vercel engineering**: [Building Vercel](https://vercel.com/blog/how-vercel-uses-vercel) - internal monorepo patterns
- **Shopify**: [Shopify monorepo CI](https://shopify.engineering/shopify-monorepo) - path-filtered workflows at scale
- **Stripe**: [Sorbet at Stripe](https://stripe.com/blog/sorbet-stripes-type-checker-for-ruby) - incremental typecheck pattern (analog: TypeScript `.tsbuildinfo` caching)

---

## Templates (drop-in)

### `vercel.json` (monorepo where Vercel ships `packages/<web>`)

```jsonc
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "ignoredBuildStep": "bash -c 'git diff --quiet HEAD^ HEAD -- packages/<web> packages/<shared> pnpm-lock.yaml package.json next.config.js turbo.json && exit 0 || exit 1'",
  "git": {
    "deploymentEnabled": {
      "main": true
    }
  }
}
```

Replace `<web>` and `<shared>` with the package names that affect the
deployed bundle.

### `.github/workflows/<package>-ci.yml`

```yaml
name: <package> CI

on:
  pull_request:
    paths:
      - 'packages/<package>/**'
      - 'packages/<shared>/**'
      - 'pnpm-lock.yaml'
      - 'package.json'
      - '.github/workflows/<package>-ci.yml'
  push:
    branches: [main]
    paths:
      - 'packages/<package>/**'
      - 'packages/<shared>/**'
  merge_group:

concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref_name }}
  cancel-in-progress: true

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
      - uses: actions/cache@v4
        with:
          path: |
            ~/.pnpm-store
            node_modules/.cache
            packages/*/.next/cache
            packages/*/*.tsbuildinfo
          key: ${{ runner.os }}-<package>-${{ hashFiles('pnpm-lock.yaml') }}-${{ hashFiles('packages/<package>/**/*.ts', 'packages/<package>/**/*.tsx') }}
          restore-keys: |
            ${{ runner.os }}-<package>-${{ hashFiles('pnpm-lock.yaml') }}-
            ${{ runner.os }}-<package>-
      - run: pnpm install --frozen-lockfile
      - run: pnpm --filter <package> lint
      - run: pnpm --filter <package> typecheck
      - run: pnpm --filter <package> test --run
      - run: pnpm --filter <package> build
```

### `turbo.json` (minimal, unlocks remote cache)

```jsonc
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "!.next/cache/**"]
    },
    "test": {
      "dependsOn": ["^build"],
      "outputs": []
    },
    "lint": {
      "outputs": []
    },
    "typecheck": {
      "dependsOn": ["^build"],
      "outputs": ["**/*.tsbuildinfo"]
    }
  }
}
```

---

## When NOT to apply this

- **Single-package repo with no monorepo overhead**: path filters and
  `ignoredBuildStep` add complexity without savings. Skip Layers 2.1 and 3.
- **Solo dev, low PR volume**: merge queue overhead may exceed savings.
  Skip the merge queue (section 2.4).
- **Team unfamiliar with merge queue / stacked PRs**: introduce one layer
  at a time. Layer 3 (`ignoredBuildStep`) is the safest first step.

---

## Decision: where the money goes (measured, not guessed)

Measured 2026-11-02. A prior version of this table ranked repos by package layout and rated
the main site repo "Low priority, caching only". The bill said otherwise.

| Fact | Value | Source |
|---|---|---|
| GitHub Actions spend, October 2026 | **$129.51** | billing page |
| of which the main site repo | **$106.96** (83%) | billing page, by repository |
| the main site repo, last 200 runs, 2026-10-28 to 11-02: CI | 1,097 wall-minutes | `gh run list` |
| the main site repo, same window: Deploy | 276 wall-minutes | `gh run list` |
| the main site repo, same window: Content CI | 231 wall-minutes | `gh run list` |
| share of those runs that were PR events plus deploys | about 96% | `gh run list` |

What it means: the cost driver is the number of pull_request events times the weight of each
workflow, not the repo's package layout. A single-app repo with heavy PR CI and a frequent deploy
is the expensive one. Rank repos by `gh run list --limit 200` wall-minutes by workflow and event,
and by the billing page, before touching anything. Wall-minutes understate the bill for non-Linux
runners (macOS bills 10x, Windows 2x).

Public repos get free Actions minutes; do not optimize them for cost.

---

## Workflow hygiene checklist (apply to every workflow in every repo)

`project-baseline-check.sh` flags items 1, 2, 4 and 5 at session start (via
`workflow-cost-check.py`). Fix them in the repo's next work PR, never a standalone PR.

- [ ] **1. `concurrency` with `cancel-in-progress: true`** on every pull_request workflow, keyed by
      `${{ github.workflow }}-${{ github.ref }}`, so a new push cancels the superseded run.
- [ ] **2. `paths-ignore` for docs-only changes** (`**.md`, `docs/**`, backlog and lessons files) on
      code CI. Because a required check that never starts blocks the merge, add a cheap `noop`
      job under the same required check name (or a sibling workflow with the inverse `paths:`)
      that reports success on docs-only PRs.
      **Equally valid, and better when a required check must always report:** a changed-paths job
      (`git diff --name-only` or `dorny/paths-filter`) whose output gates the heavy jobs through
      `if: needs.<job>.outputs.<flag> == 'true'`, with an always-run summary job as the required
      check (added 2026-11-02; the main site repo's `ci.yml` is the reference).
- [ ] **3. Expensive jobs need the cheap gate**: `needs: quality` (lint plus typecheck) on test,
      security, build and e2e jobs, so a lint failure does not also pay for the slow jobs.
- [ ] **4. Deploy workflows skip docs-only merges** (`paths-ignore` on the push trigger). Content
      that is rendered from MDX or similar is NOT docs-only and still deploys.
- [ ] **5. Ubuntu runners only** (`ubuntu-latest`). macOS bills 10x and Windows 2x; justify any
      exception in a comment and keep it to one job.
- [ ] **6. `timeout-minutes` on every job.** The default is 360; a hung job bills all of it.
- [ ] **7. Renovate (or Dependabot) grouped and weekly**: one grouped PR a week, not one per
      package. Each bot PR is a full CI run.
- [ ] **8. Publish content through a database, not a deploy**, where the site allows it. A content
      edit that writes to a table costs no build; one that commits MDX costs CI plus a deploy.
- [ ] **9. Public repos get free minutes**: record "public, free" and skip the above for cost.
- [ ] **10. Draft PRs and skip tokens**: `if: github.event.pull_request.draft == false` on heavy
      jobs where drafts are used (see the audit checklist below, Step 4).

Verification for a docs-only PR: the required check reports success from the noop job in seconds,
no Vercel preview builds, and the Actions tab shows no billable test or build minutes.

---

## Per-repo audit checklist (use this on cold sessions)

When starting on a new repo (or returning to one) and asked to cut CI
cost, walk through this list. Each step is independent - apply what
fits, skip what doesn't. ~30 minutes of work yields 50-80% reduction in
CI minutes for a typical Next.js + Playwright repo.

### Step 1: Identify the dominant cost line

Run: `gh run list --limit 50 --json name,conclusion,createdAt`

Group by workflow name; multiply count × typical duration. The workflow
with the highest product is your target. In example-app (2026-05-04) it
was `smart-e2e.yml` at ~40 min × every PR push = >90% of total CI minutes.

### Step 2: Scan that workflow's `on:` block

For each trigger, ask:
- Does `paths` / `paths-ignore` exist? If no → most PRs are wasting it.
- Does `concurrency` with `cancel-in-progress: true` exist? If no →
  force-pushes burn duplicate runs.
- Does the `if:` block skip drafts? If no → draft-and-iterate workflows
  burn N runs before review.

### Step 3: Derive the IGNORE list

Universal ignores (every repo, every workflow):
- `**/*.md`
- `docs/**`
- `LICENSE`
- `CHANGELOG*.md`
- `.github/ISSUE_TEMPLATE/**`
- `.github/PULL_REQUEST_TEMPLATE.md`

Repo-class ignores (apply if present):
- DB-migration repos: `<migrations-dir>/**` (Supabase: `supabase/migrations/**`,
  Drizzle: `drizzle/**`, Prisma: `prisma/migrations/**`) - only IF a
  separate drift-check workflow already gates them.
- Marketing-asset repos: `public/marketing/**`, `public/screenshots/**`,
  any `assets/**` dir not imported by app code.
- Content repos: `content/**`, `posts/**`, blog markdown - assuming
  static content, not MDX with logic.

Repo-specific ignores (audit per-repo):
- Sibling-package paths in monorepos when the workflow only cares about
  one package (e.g. `apps/cli/**` ignored by web's E2E workflow).
- Backend-only API routes if the E2E suite covers UI flows only.
  (Caveat: only if you're confident no UI test exercises that endpoint.)

Do NOT ignore:
- `package.json`, `pnpm-lock.yaml` - version bumps absolutely affect
  test outcomes
- `.github/workflows/<the-workflow-itself>` - workflow changes need
  to validate themselves
- `playwright.config.*`, `vitest.config.*`, equivalent test configs
- `next.config.*`, `middleware.ts`, build-time config
- `scripts/**` if any of those scripts run as service_role or modify
  shared state - security audit must still run

### Step 4: Add the `if:` skip-draft + skip-token guards

```yaml
if: >-
  !contains(github.event.head_commit.message || '', '[skip-e2e]') &&
  !contains(github.event.pull_request.title || '', '[skip-e2e]') &&
  github.event.pull_request.draft != true
```

Replace `skip-e2e` with the workflow's name (`skip-build`, `skip-test`,
etc.). Document the opt-out token in CONTRIBUTING.md or PR template.

### Step 5: Verify branch protection still passes

If `main` requires the workflow's status checks via branch protection,
a skipped workflow leaves the PR un-merge-able. Two options:
- Make the check NOT required (preferred for expensive checks)
- Or add a "neutral skip" job that always passes when the path filter
  excludes the PR (more complex; only worth it if branch protection is
  load-bearing for compliance)

### Step 6: Estimate savings before merging

For each ignored path category, count recent PRs that touched ONLY that
category:

```bash
gh pr list --state merged --limit 50 --json files,number \
  --jq '.[] | select(.files | all(.path | test("^(docs|supabase/migrations|public/marketing)/"))) | .number'
```

If you find ≥3 such PRs in the last 50, the path filter pays for itself
in the next sprint.

### Step 7: Land it in the repo's next work PR (2026-11-02: not a standalone PR)

A standalone CI-config PR pays a full CI run for a one-file change. Put it on the current work
block's branch. Only when the repo has no open work block, make it one block with other pending
chores. Commit message format:

Title format: `chore(ci): skip <workflow> for irrelevant paths and draft PRs`

Body includes:
- The IGNORE list with one-line justification per entry
- Estimated savings ("the merged PR #N would have skipped this")
- Note that branch protection / drift-check still gates correctness

### Worked example (example-app PR #357, 2026-05-04)

Cuts shipped:
1. `paths-ignore` on `smart-e2e.yml`: `**/*.md`, `docs/**`,
   `supabase/migrations/**`, `public/marketing/**`,
   `public/screenshots/**`, `.github/ISSUE_TEMPLATE/**`,
   `.github/PULL_REQUEST_TEMPLATE.md`, `CHANGELOG*.md`, `LICENSE`
2. Draft PR skip via `pull_request.draft != true`
3. Existing `[skip-e2e]` opt-out preserved

Migrations were safe to ignore because `deploy.yml` runs drift-check
on push to main against the prod registry.

PR #348 (the 34-file migration cleanup that motivated this) would have
skipped E2E entirely - saving ~40 min per push × the 3 pushes that PR
took = ~2 hours of CI on one PR alone.

---

*Standard owner: this is a living document. Update as new GitHub /
Vercel features ship. Last revision: 2026-05-04.*
