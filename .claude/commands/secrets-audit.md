# /secrets-audit — Env Files, Backup Coverage, Key Rotation Health

> **Standards inherited** (apply throughout this skill):
> - [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) — read + reason, don't pattern-match
> - [Self-Improvement Protocol](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) — log to `.secrets-audit-history.json`, learn across runs
> - [Multi-Repo Awareness](~/.claude/standards/MULTI_REPO_AWARENESS.md) — scan siblings, surface in SITREP, never cross-traverse
> - [Verify Before Destroy](~/.claude/standards/VERIFY_BEFORE_DESTROY.md) — content-verify before destructive action
> - [Skill Auto-Suggest Protocol](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) — every SITREP ends with "Suggested next"

**Find every secret store across operator's hosts and repos. Verify each is backed up, current, and not silently rotting.**

## PARADIGM

Secrets fail in three modes that no other skill catches:

1. **Backup coverage gap** — the file exists, the env vars are read by code, but the file isn't in any backup target. Lost on disk failure or accidental clobber. (2026-05-03 `~/.hermes/.env` clobber: not in `BACKUP_PATHS`, no recovery possible from R2.)
2. **Stale-key sprawl** — env vars defined in `.env` but never read by any consumer. Side-effect of provider migrations (e.g. Poe → ChatGPT consolidation left `POE_API_KEY` in claw-hq's openclaw.env for weeks). Old keys are attack surface.
3. **Rotation overdue** — keys older than the provider's recommended rotation period. No alerting because providers don't push rotation reminders.

This skill is read-and-reason — `.env` parsing, code consumer detection, backup-config cross-referencing. It is NOT regex-fix-secrets — that's `/sec-ship`. The two skills compose: `/sec-ship` finds secrets in *committed* files; `/secrets-audit` audits the env-file-and-backup-target ecosystem.

---

## DISCIPLINE

> Reference: [Superpowers Discipline Protocol](~/.claude/standards/STEEL_DISCIPLINE.md)

Steel principles applied:

- **#1 (verification before claim):** "the env file is backed up" requires confirming it appears in the running backup config, not just "looks like it should be"
- **#6 (no hallucination):** rotation thresholds are provider-specific (Stripe rotates yearly, OpenAI quarterly per their docs); query the actual provider docs at audit time, don't assume
- **#7 (no tech debt):** stale keys found during audit get flagged loudly; the skill surfaces them so the operator removes them in the same session

### Rationalization defense

| Rationalization | Reality | Do |
|---|---|---|
| "These env vars are old, but the service still works, leave them alone" | Stale env vars are attack surface and create mystery later | Flag them; operator decides remove vs keep |
| "It's in restic, it's backed up" | restic only backs up paths in `BACKUP_PATHS` — being on-disk does not mean covered | Cross-reference each `.env*` file against the live backup config |
| "I'll rotate keys later" | "Later" never comes; key age is a function of operator memory | Surface age + rotation guidance; let the SITREP nag |
| "The provider will tell me if my key is compromised" | Providers don't proactively flag rotation; usage patterns mask abuse | Operator-driven rotation, on a schedule the operator owns |
| "We'll audit secrets before launching to customers" | Stale-key cleanup before launch is a 4-hour scramble; doing it now is 20 minutes | Audit early; audit often |

---

## CRITICAL RULES

1. **NEVER LOG SECRET VALUES.** Only log existence, file path, age, and consumer status.
2. **READ-ONLY by default.** Audit-mode never modifies env files. `--fix` flag does only narrow patches (gitignore additions, backup-config additions). Never auto-rotates keys.
3. **Cross-host aware.** Operator's secrets live across hosts (laptop, claw-hq, nolan-prod) AND across repos. Skill takes `--host <ssh-alias>` or `--repo <path>`.
4. **Don't conflate `/sec-ship` and `/secrets-audit`.** /sec-ship finds secrets in *committed* code (the bug). /secrets-audit audits the *env-file ecosystem* (the lifecycle).
5. **Coverage cross-reference is mandatory.** Every `.env*` found gets cross-checked against `BACKUP_PATHS` (or platform-equivalent). Coverage gaps are the highest-severity finding.
6. **Stale-key detection is consumer-based, not heuristic.** A key is "stale" if no code in the consumer repo grep-finds the env var name. Not "looks unused."
7. **Rotation guidance is provider-specific.** Read provider docs to set the threshold; default to 90 days only when no provider-specific guidance is available.
8. **History-driven.** Same as other audit skills — `.secrets-audit-history.json` per host.
9. **SITREP ends with Suggested next.**

---

## MODES

```
/secrets-audit                        # Local host, all .env* files, audit-only
/secrets-audit --host claw-hq         # Remote host
/secrets-audit --all-hosts            # Iterate over operator's known hosts
/secrets-audit --repo .               # Scan only this repo's env-file ecosystem
/secrets-audit --check coverage       # Restrict to backup-coverage check
/secrets-audit --check staleness      # Restrict to stale-key consumer check
/secrets-audit --check rotation       # Restrict to age-based rotation check
/secrets-audit --fix-coverage         # Add uncovered .env* files to BACKUP_PATHS
/secrets-audit --fix-gitignore        # Ensure .env* matches .gitignore patterns
/secrets-audit --rotate <provider>    # Walk operator through key rotation (manual confirm at each step)
```

`--fix-coverage` and `--fix-gitignore` are narrow auto-patches. `--rotate` is interactive: the skill walks the operator through, but each destructive step (revoke old key, push new key) requires explicit confirmation.

---

## DETECTION

### Discovery: where env-files hide

| Pattern | Where | Example |
|---|---|---|
| `.env*` | Project repos cwd | `.env.local`, `.env.production` |
| `~/.<service>/.env` | Service home dirs | `~/.openclaw/.env`, `~/.hermes/.env` |
| `~/.<service>/<service>.json` | JSON config with embedded secrets | `~/.openclaw/openclaw.json` |
| `/etc/secrets/*` | System-level secrets dirs | rare on operator hosts |
| GitHub Action secrets | repo Settings > Secrets | `gh secret list` |
| Vercel env vars | per-project | `vercel env ls` |
| Cloudflare worker secrets | per-worker | `wrangler secret list` |
| 1Password / vault refs | external | Skip — vault is its own audit |

For each discovered location, capture:
- `path` (or remote system identifier)
- `mtime` (file age)
- `permissions` (must be 0600 or stricter for `.env` files)
- `referenced_vars[]` (the keys defined inside)

### Coverage cross-reference

For each `.env*` file location, check:
1. **restic backups** — read `~/.restic-backup.sh` (or platform equivalent), extract `BACKUP_PATHS`, check whether the file's path is covered by any path or its parent directory
2. **GitHub** — file should NOT be tracked. Run `git ls-files <path>` in the enclosing repo; non-empty result is a critical finding
3. **gitignore** — file should be matched by `.gitignore`. Run `git check-ignore <path>`; if not ignored, flag

Classification:
- `COVERED` — in backup config, gitignored, not tracked
- `UNCOVERED-BACKUP` — exists on disk but not in backup config (data-loss risk)
- `UNCOVERED-GITIGNORE` — not gitignored (commit risk)
- `TRACKED` — already committed to git (DEFCON-1)

### Staleness check (consumer-based)

For each env var defined in each `.env*` file:

1. Identify the consumer scope:
   - For project `.env*`: consumer is the repo
   - For `~/.<service>/.env`: consumer is the service's source code (e.g. openclaw npm package, hermes Python source)
   - For host-level `/etc/secrets/*`: consumer is anything on the host (skip — too broad)

2. `grep -r <VAR_NAME> <consumer_path>` (excluding the env file itself)

3. Classify:
   - `LIVE` — referenced by ≥1 consumer file
   - `STALE` — defined but no consumer grep-find anywhere
   - `LEGACY` — referenced only in commented-out code or `archive/` paths

### Rotation check

For each LIVE env var that matches a known-provider pattern (`OPENAI_*`, `STRIPE_*`, `GITHUB_*`, etc.):

1. Determine the provider's recommended rotation period (read provider docs via WebFetch when uncertain — don't hallucinate)
2. Compare the env file's `mtime` to current date
3. Classify:
   - `FRESH` — rotated within recommended period
   - `DUE` — past recommended period but < 2× threshold
   - `OVERDUE` — past 2× recommended threshold

NOTE: file mtime is a proxy for rotation date — the operator may want to override with explicit annotation in the env file (`# ROTATED: 2026-04-15`). Read those comments and prefer the annotated date over `mtime`.

---

## STAGES

### Stage 0: Pre-flight + history

Read `.secrets-audit-history-<host>.json`. Extract:
- Last run's findings
- `wip_keys_protected` — keys the operator has flagged "leave alone" (e.g. mid-migration, not yet rotated)
- `provider_rotation_thresholds` — cached values to avoid re-fetching provider docs every run

### Stage 1: Discovery

Sub-agent (haiku) lists every `.env*` location and parse each one's `referenced_vars[]`. Returns < 500 tokens to orchestrator.

### Stage 2: Coverage cross-reference

Sub-agent (sonnet) cross-checks each location against backup config, gitignore, git tracking. Returns classification per location.

### Stage 3: Staleness check

Sub-agent (sonnet) runs the consumer-based grep for each var. Returns LIVE/STALE/LEGACY classifications.

### Stage 4: Rotation check

Sub-agent (sonnet) reads file mtimes + annotations, queries provider docs (cached) for thresholds, returns FRESH/DUE/OVERDUE classifications.

### Stage 5: Fix loop (only if `--fix-*` flags)

| Finding | Fix flag | Action |
|---|---|---|
| UNCOVERED-BACKUP | `--fix-coverage` | Add path to `BACKUP_PATHS` in restic-backup.sh; verify the wrapper script reflects it |
| UNCOVERED-GITIGNORE | `--fix-gitignore` | Append `.env*` (or specific path) to repo's `.gitignore` |
| TRACKED | (manual only) | Skill refuses to auto-fix; tracked secrets need `git filter-branch` or BFG which the operator must drive |
| OVERDUE rotation | `--rotate <provider>` | Interactive walkthrough |

### Stage 6: SITREP + history

Same pattern as `/cron-audit`. Report at `.secrets-audit-reports/SA-YYYYMMDD-HHMMSS.md`.

---

## SITREP TEMPLATE

```
═══════════════════════════════════════════════════════════════════════════════
                       SITREP — /secrets-audit
═══════════════════════════════════════════════════════════════════════════════
Run ID:     SA-20260503-150511
Host:       claw-hq
Duration:   1m 47s
Locations:  6 env-file locations, 47 env vars total

────────────────────────────────────────────────────────────────────────────────
 BACKUP COVERAGE
────────────────────────────────────────────────────────────────────────────────
✅ COVERED         5 locations in restic BACKUP_PATHS
❌ UNCOVERED       1 location — /home/openclaw/some-newish-service/.env
                   regression risk: same shape as ~/.hermes/.env clobber

────────────────────────────────────────────────────────────────────────────────
 GIT TRACKING SAFETY
────────────────────────────────────────────────────────────────────────────────
✅ NOT-TRACKED     6/6 locations
✅ GITIGNORED      6/6 locations match a .gitignore pattern

────────────────────────────────────────────────────────────────────────────────
 STALENESS (consumer-based)
────────────────────────────────────────────────────────────────────────────────
✅ LIVE            42 vars referenced by ≥1 consumer file
⚠️ STALE            5 vars defined but no consumer grep-find:
                     • POE_API_KEY      (~/.openclaw/.env, removed 2026-04-26)
                     • OPENROUTER_API_KEY (same)
                     • OLLAMA_API_KEY   (same)
                     • OLLAMA_CLOUD_API_KEY (same)
                     • XAI_API_KEY      (same)
                   Per memory project_llm_provider_split.md — these can be removed.

────────────────────────────────────────────────────────────────────────────────
 ROTATION HEALTH
────────────────────────────────────────────────────────────────────────────────
✅ FRESH            38 keys within recommended rotation window
⚠️ DUE               4 keys past recommended period
                     • TELEGRAM_BOT_TOKEN     mtime 2026-01-12 (115d, threshold 90d)
                     • OPENAI_API_KEY         mtime 2026-02-03 (89d, threshold 90d)
                     • CLOUDFLARE_API_TOKEN   mtime 2026-01-29 (94d, threshold 90d)
                     • RESEND_API_KEY         mtime 2026-02-01 (91d, threshold 90d)
❌ OVERDUE           0 keys
🔒 PROTECTED         5 keys flagged wip_keys_protected (mid-migration)

────────────────────────────────────────────────────────────────────────────────
 SIBLING HOSTS NOT AUDITED THIS RUN
────────────────────────────────────────────────────────────────────────────────
nolan-prod   last audit 14d ago — re-run /secrets-audit --host nolan-prod

═══════════════════════════════════════════════════════════════════════════════
```

---

## Suggested next

Per [Skill Auto-Suggest Protocol](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md):

| Outcome | Recommended | Why |
|---|---|---|
| All COVERED + all FRESH | none — re-audit monthly | clean state |
| UNCOVERED-BACKUP findings | /secrets-audit --fix-coverage | apply patches |
| TRACKED secret found | /sec-ship --comprehensive | tracked-in-git is a critical finding; full security pass |
| STALE keys to remove | manual cleanup, then re-audit | operator removes; skill confirms |
| OVERDUE keys | /secrets-audit --rotate \<provider\> | interactive rotation |
| Cross-host gap | /secrets-audit --host \<sibling\> | extend coverage |

**Skip if:** the operator just ran a fix flag and is verifying the SITREP cleared.

---

## DESIGN DECISIONS (WHY)

### Why a separate skill from `/sec-ship`
Different lifecycle phase. `/sec-ship` audits *committed* code for secrets that shouldn't be there (the prevention layer). `/secrets-audit` assumes secrets are correctly in env files and audits the *operational health* of those files (backup, freshness, consumer-binding). Same domain, different time-axis.

### Why no auto-rotate
Rotation is a multi-step, multi-system operation: generate new key → update every consumer's env → restart services → verify functionality on new key → revoke old key. Each step has rollback implications. The skill walks through it, but auto-rotating without operator confirmation per step is too high-blast-radius for this skill's safety profile.

### Why mtime as proxy for rotation date
Operators don't reliably annotate `# ROTATED:` comments. mtime is the cheapest reliable signal. The skill prefers explicit annotations when present and falls back to mtime when absent. False positives (file touched for unrelated reason) are tolerable because they cause re-audit; false negatives (file edited but mtime didn't update) are rare.

### Why consumer-based staleness, not "looks unused"
"Looks unused" is regex pattern-matching ("if VAR_NAME doesn't appear in the project, it's stale"). Consumer-based grep is reasoning ("did the codebase actually consume this in the last commit?"). The latter survives renames, refactors, and conditional code paths better.

### Why provider-specific rotation thresholds
A 90-day blanket threshold is wrong: Stripe recommends yearly, OpenAI quarterly, Cloudflare on use-case. WebFetch the provider docs at audit time (cached for the session) so the threshold is grounded. Cache invalidates per session — providers update guidance.

### Why TRACKED is refuse-to-fix
git history rewrites are dangerous and operator-specific (force-push policies, branch-protection rules, who else has cloned). The skill's job is to surface — the operator drives the rewrite tooling.

---

## DEFINITION OF DONE

- Every `.env*` location classified for COVERAGE, GIT-TRACKING, GITIGNORE
- Every env var classified for STALENESS (LIVE/STALE/LEGACY)
- Every LIVE provider-keyed var classified for ROTATION (FRESH/DUE/OVERDUE)
- Sibling hosts surfaced
- `.secrets-audit-history-<host>.json` updated
- `.secrets-audit-reports/SA-*.md` written
- SITREP ends with "Suggested next"
- Auto-fixes (if any) have backup files and verification
