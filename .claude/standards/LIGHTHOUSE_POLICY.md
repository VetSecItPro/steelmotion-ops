# Lighthouse Policy (Org-Wide CI)

## TL;DR for everyone

**Lighthouse is OFF in CI across all VetSecItPro repos. Don't add it back.**

If you need a perf check:
- **`/perf`** — investigate a specific concern (deeper than Lighthouse, examines bundle, traces hot paths)
- **`/quality`** — pre-launch full sweep (perf + a11y + tests)
- **`/qatest`** — full QA validation (everything `/quality` does + crawl + interaction tests)

These are run on demand, not on every PR. Zero CI minutes when not in use.

---

**Decision (2026-05-03): Lighthouse stays OFF in CI across all VetSecItPro repos.** Run `/perf` on demand for specific perf concerns; `/quality` before launches.

---

## Why off entirely

1. **Per-PR Lighthouse is high-noise:** runner load + network variance produce flaky scores. Most PRs in our repos touch backend/security/infra where Lighthouse score change ≈ 0. Failures get ignored or worked around.
2. **CI minutes cost real money on private repos:** GitHub Free gives 2000 min/mo; over that = $0.008/min Linux. Steel-motion (private since 2026-05-01) and the Nolan stack (mission-control, nolan-infra, atlas-openclaw, claw-hq-infra, commandpost-customer-vaults) are all billed surfaces.
3. **Even weekly cron costs minutes:** ~20 min/month per repo. Across our private repos that compounds. And we don't act on the report on a per-week basis.
4. **`/perf` is deeper anyway:** it goes beyond a single Lighthouse run, examines bundle size, traces hot paths, recommends fixes. Per-PR Lighthouse can't do that.

## What we do instead

| Need | Tool | When to invoke |
|---|---|---|
| Investigate a specific perf regression | `/perf` | When you suspect or have a report of slowness |
| Pre-launch perf sweep | `/quality` | Before public launch / major release |
| Full QA-style validation including perf | `/qatest` | Pre-launch + post-major-release |
| Trend monitoring over time | (optional, manual) | Run `/perf` quarterly and compare to prior reports in `.perf-reports/` |

## Decision matrix per repo

Updated 2026-05-03.

| Repo | Lighthouse in CI | Status |
|---|---|---|
| **steel-motion** | OFF | PR #138 (open) |
| **clarus-app** | OFF | PR #147 (open) |
| **rowan-app** | OFF | PR #347 (open) — reverses 2026-04-27 gate decision in light of cost |
| **kaulby-app** | OFF | PR #367 (open) |
| **actnow-education** | n/a (all CI disabled) | 2026-05-03 — repo is being abandoned; all 4 workflows disabled via `gh api -X PUT .../disable` to stop burning Actions minutes. No PR needed. |
| **styrby-app** | OFF | PR #246 (open) — bundled with screenshot-runner relocation cleanup. Removed elaborate FCP-budget gate too; defer FCP enforcement to post-deploy Vercel Speed Insights. |
| All other repos | n/a (already clean) | Confirmed by API scan 2026-05-03 |

**Total: 6 repos had Lighthouse in CI; 5 PR'd (#138 #147 #347 #367 #246), 1 disabled-via-API (actnow being abandoned).**

## When to add Lighthouse back to CI

Only when ALL of these hold:
- Repo is a public marketing site (GitHub Free has unlimited Linux minutes for public repos)
- Perf has a tight SLO that's customer-visible
- Lighthouserc.js assertions are tuned against historical flake (i.e., you've measured the flake floor)
- Team has agreed to act on the score (not just receive it)

Until those four hold, the answer is on-demand `/perf`.

## Anti-patterns

- **"Lighthouse is on by default in our template"** — start templates without it. Add only when justified.
- **"We'll add Lighthouse but make it `continue-on-error: true`"** — that's still ~3-5 min CI minutes per PR for nothing. Just don't run it.
- **"We need a perf gate of some kind"** — bundle-size check is faster, more deterministic, and catches the most common regression class (deps bloat). Use that instead.

## Migration notes

When removing Lighthouse from a workflow file, also clean up:
- `needs: [..., lighthouse, ...]` references in dependent jobs
- `check_job "Lighthouse" "${{ needs.lighthouse.result }}"` in CI summary jobs
- Comments mentioning Lighthouse in build-job comments
- Any `actions/upload-artifact` for Lighthouse reports

If left, the workflow will fail to parse or will produce stale summary entries.

## For new repos created via /repo-bootstrap

The `/repo-bootstrap` skill scaffolds CI without Lighthouse by default. Don't add it back during the bootstrap. If you genuinely need a perf gate, add bundle-size check (cheaper, more deterministic) instead.

## Cross-references

- Memory: `feedback_lighthouse_off_in_ci.md` (auto-loads in every Steel Motion session, will load on relevant cross-project work too)
- Standard: `~/.claude/standards/CI_VERCEL_COST_OPTIMIZATION.md` (broader CI cost framework — Lighthouse policy is one application)
- Skills that replace Lighthouse-on-CI: `/perf`, `/quality`, `/qatest`
