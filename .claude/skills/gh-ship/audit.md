# /gh-ship - proactive audit (Stage 11.7) and CI improvement (Stage 12.5)

The point of these stages is to find what nobody specified. A fixed checklist is never complete;
scan the categories below, and surface anything else that looks wrong even if no row covers it.

## Stage 11.7 - proactive audit

### A. Workflow health (`.github/workflows/*.yml` or the engine's equivalent)

- Actions pinned to a **SHA**, not a moving tag - a mutable tag is a supply-chain vector
- `permissions:` present and minimal - the default token is usually over-scoped
- `timeout-minutes:` on every job - prevents a hung job billing indefinitely
- `concurrency:` group on deploy workflows. **`cancel-in-progress` must be `false` for any workflow
  that holds a lock** (helm upgrade, terraform apply, kubectl apply). Cancelling mid-lock strands the
  release and every later deploy fails. Only pure-check workflows may cancel.
- `paths:` filters so unrelated changes do not trigger the whole matrix - **except** where the
  workflow is a required status check. A path-filtered required check never reports on a PR that
  misses its paths, and the PR becomes unmergeable forever. Required and path-filtered are mutually
  exclusive; verify against `branches/<default>/protection` rather than assuming.
- OIDC instead of long-lived `secrets.*` where the provider supports it

### B. Branch protection (`gh api repos/:owner/:repo/branches/<default>/protection`)

Required checks present? Linear history? Force-push disabled? For a solo maintainer, a required
approval count ≥ 1 blocks every PR, since GitHub forbids self-approval - flag it as a config error
rather than a hardening win.

### C. Repository settings

`delete_branch_on_merge` true (Stage 12 sets it: remote-only, restorable), squash the only merge
type for repos shipped through `/gh-ship`, issues enabled where the repo is public.

### D. Container registry (where an image is published)

Package ACL grants the building repo access; untagged versions accumulating and worth pruning.

### E. Repo file health

`.gitignore` covers `.env*`, logs, `dist/`, `node_modules/`; a LICENSE exists; the README is not
stale relative to recent commits; the lockfile is committed.

### F. Open PRs and issues

PRs untouched > 30 days → flag for triage, never close. Branches with no PR > 7 days → flag. Bugs
open > 90 days → flag.

### G. CI trend (`gh run list`)

Failure rate over the last 20 runs > 30% → surface the pattern. Run time creeping up → surface.

### Fix or surface

**Fix autonomously** when the change is uncontroversial and reversible: a missing `timeout-minutes`,
an unpinned action, an over-broad default `permissions` block, a `.gitignore` gap.

**Surface for the operator** when there is a real trade-off: enabling branch protection, changing
required checks, altering merge strategy, anything that changes who can do what.

Autonomous fixes go in their own `chore/audit-improvements-<date>` branch and PR. Never fold them
into the PR being shipped - a ship PR that also rewrites CI is unreviewable.

## Stage 12.5 - CI workflow improvement

If 11.7 found fixable workflow anti-patterns, open a separate PR with a WHY comment in the YAML for
each change, naming the class of issue it closes:

- action pinning → mutable-tag supply-chain vector
- concurrency group → deploy races on rapid pushes
- `timeout-minutes` → runaway billing on a stuck job
- `permissions` → least privilege for the default token
- path filters → wasted runs on unrelated changes (subject to the required-check caveat above)

**Do not auto-merge this PR.** It is an improvement proposal, not part of the shipped change. Say in
the SITREP that it is open and waiting.

## Repeat-finding suppression

Before reporting anything from this audit, read prior `.gh-ship-history.json` entries and any
`.gh-ship-reports/` output. Classify each finding:

- **new** - report normally
- **regression** - previously fixed, now back. Report with the prior run id.
- **deferred** - the operator declined it before. One line reminder at most; do not re-argue.
- **known false positive** - suppress.

A finding the operator has already triaged is noise the second time. Re-surface only on regression,
a changed threat model, or an explicit request.
