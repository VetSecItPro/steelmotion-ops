# /cron-audit — Cron + Scheduled-Job Health Audit

> **Standards inherited** (apply throughout this skill):
> - [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) — read + reason, don't pattern-match
> - [Self-Improvement Protocol](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) — log to `.cron-audit-history.json`, learn across runs
> - [Multi-Repo Awareness](~/.claude/standards/MULTI_REPO_AWARENESS.md) — scan siblings, surface in SITREP, never cross-traverse
> - [Verify Before Destroy](~/.claude/standards/VERIFY_BEFORE_DESTROY.md) — content-verify before destructive action
> - [Skill Auto-Suggest Protocol](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) — every SITREP ends with "Suggested next"

**Audit every scheduled job — cron, systemd timer, GitHub Actions schedule — across the operator's hosts. Verify each fires AND succeeds. Surface the silent-failure class of bug.**

## PARADIGM

A scheduled job that's **running** is not a job that's **doing its job**. The 2026-05-03 silent-deploy-gap proved it: `deploy-webhook.service` was active for 4+ days while MC sat 80+ commits behind main, because no GitHub webhook was wired to fire it. Process was healthy. Outcome was not.

Cron-audit's job is to find that gap **proactively**, before the operator discovers it via stale dashboards or angry users.

This skill is a planning document for Claude to execute — bash blocks are illustrative, not literal. The decision tree is Claude reading the actual journal output / log files / cron syntax and reasoning about whether the schedule is healthy.

Anti-patterns:
- "Process is running → healthy" — measure outcomes, not process state
- "Exit 0 → success" — the script may have `exec`'d before its failure-handler trap could fire
- "Last log entry exists → it ran" — scripts may be re-running with the same output every time and producing no actual work

---

## DISCIPLINE

> Reference: [Superpowers Discipline Protocol](~/.claude/standards/STEEL_DISCIPLINE.md)

Steel principles applied:

- **#1 (verification before claim):** "the deploy-webhook is firing" requires evidence in the log within the expected window — not just "the service is active"
- **#2 (root cause first):** silent-failure is a *symptom*; the cause is the wiring (webhook URL not configured, env var missing, alert channel collapsed). Fix the cause; document why the symptom existed
- **#7 (no tech debt):** when an audited script lacks failure-alert wiring (`notify_fix_bot` helper or equivalent), patching it is part of the audit, not a follow-up

### Rationalization defense

| Rationalization | Reality | Do |
|---|---|---|
| "The service is active, the cron must be working" | active ≠ producing output | Read the journal/log; verify a fresh outcome within the schedule window |
| "Last fire was X minutes ago, that's recent enough" | If the schedule is `* * * * *` and last fire was 30 minutes ago, that's 29 missed fires | Compare last-fire timestamp against schedule period |
| "It exited 0 last time, it's fine" | `exec` masks subsequent failure-handlers | Inspect the script for `exec foo` patterns; verify failure paths |
| "These crons are old, no one touches them, they must work" | Old crons drift silently as deps/paths/permissions change | Re-audit on every run regardless of age |
| "The alert channel will tell us if something's wrong" | Alert channels go stale (token expired, bot deleted, channel collapsed via fallback) | Test the alert channel as part of audit |

---

## CRITICAL RULES

1. **READ-ONLY by default.** Audit-mode never modifies a cron entry, env file, or alert config. `--fix` flag explicitly required for any patches.
2. **Multi-host aware.** Operator works across multiple hosts (claw-hq, nolan-prod). Skill takes `--host <ssh-alias>` or operates on local. Never cross-traverse silently.
3. **Verify outcome, not process.** "Service is active" is necessary but never sufficient evidence.
4. **Alert-channel sanity-test.** If a script claims to alert on failure, verify the channel is reachable and the credentials are fresh. Stale tokens are silent failure compounded.
5. **Detect `exec` masking.** Any script using `exec <cmd>` after defining EXIT/ERR traps has the trap silently disabled. Flag it.
6. **Log with timestamps.** Every finding includes when the schedule last fired (or didn't), not just whether the service is running.
7. **Log freshness window per schedule.** A `*/5 * * * *` cron should have a journal entry within the last 5 minutes; a `0 3 * * *` cron should have one within the last 24 hours.
8. **History-driven.** Read `.cron-audit-history.json` first; surface regressions vs last run.
9. **SITREP ends with Suggested next** per autosuggest protocol.

---

## MODES

```
/cron-audit                       # Local host, all schedule sources, audit-only
/cron-audit --host claw-hq        # Remote host via SSH
/cron-audit --host nolan-prod     # Remote host via SSH
/cron-audit --all-hosts           # Iterate over operator's known hosts (CLAUDE.md-listed aliases)
/cron-audit --source cron         # Restrict to user/system cron only
/cron-audit --source systemd      # Restrict to systemd timers only
/cron-audit --source github       # Restrict to GitHub Actions `schedule:` triggers
/cron-audit --fix                 # Apply known-good patches (notify_fix_bot helper, capture-then-act)
/cron-audit --since=24h           # Override the lookback window for "did it fire?"
```

`--fix` is the only mode that writes anything. Audit-only modes are read-and-reason.

---

## DETECTION

### Schedule sources, in priority order

| Source | How to discover | Where logs live |
|---|---|---|
| User cron (`crontab -l`) | per-user, on the host | `journalctl --user -u cron` or `/var/log/syslog` (system cron writes there too) |
| System cron (`/etc/cron.d/*`, `/etc/cron.daily/*`, etc.) | host-wide | `/var/log/syslog` or `journalctl -u cron` |
| systemd user timers (`~/.config/systemd/user/*.timer`) | per-user, linger-enabled | `journalctl --user -u <service>` |
| systemd system timers (`/etc/systemd/system/*.timer`) | host-wide | `journalctl -u <service>` |
| GitHub Actions `schedule:` triggers | repo's `.github/workflows/*.yml` | GitHub Actions run history (gh api) |

### Multi-user host gotcha

On claw-hq, the operator runs as `ops` but the gateway runs as `openclaw`. Their crons are separate. Always sudo into each documented user OR use `loginctl list-users` to discover all linger-enabled accounts and audit each. The `ops`-user `crontab -l` will not show `openclaw`'s crons.

---

## STAGES

### Stage 0: Pre-flight + history read

Capture `START_TIME`, `TARGET_HOST`, `TARGET_USERS[]` (default: current user + any linger-enabled users on host).

Read `.cron-audit-history.json` (cwd-relative if local, else fetch from `~/.cron-audit-history-<host>.json`):
- Last run's findings
- `patterns_observed` for known regression shapes
- `wip_alerts_protected` — alert channels the operator has marked "leave alone" (e.g., temporarily disabled bot)

Auto-gitignore the history file at every run.

### Stage 1: Schedule discovery

For the target host + each target user:

1. **`crontab -l`** for each user
2. **`ls /etc/cron.d/ /etc/cron.daily/ /etc/cron.hourly/ /etc/cron.weekly/ /etc/cron.monthly/`** for system cron
3. **`systemctl list-timers --all`** (system) and **`systemctl --user list-timers --all`** (per-linger-user)
4. **`find . -name "*.yml" -path "*/.github/workflows/*"`** in each git repo cwd; grep for `schedule:` blocks

Build `SCHEDULE_INVENTORY[]`: for each entry, capture:
- `id` (unique key — user+source+name)
- `schedule_expr` (cron syntax or systemd `OnCalendar=`)
- `command` (what runs)
- `expected_window` (max gap between fires, derived from the expression)
- `last_fire_log_pattern` (how to grep the corresponding log)

### Stage 2: Per-schedule outcome check

For each entry in `SCHEDULE_INVENTORY[]`, dispatch a sub-agent (haiku model — pure log-grep, no judgment) to:

1. Pull the corresponding log (last 7d)
2. Extract last-fire timestamp
3. Compare against `expected_window`
4. Classify outcome:
   - `OK` — fired within window, last exit non-error
   - `STALE` — service is enabled but last fire is older than expected window × 2
   - `SILENT` — service is enabled but no log entry ever found (the smoking-gun case)
   - `ERROR` — last fire exited non-zero
   - `BACKOFF` — repeated failures detected; service may be in retry loop
   - `MISSING` — service file referenced by a timer/cron entry doesn't exist

Sub-agent returns < 500 tokens to the orchestrator (per CONTEXT_MANAGEMENT.md).

### Stage 3: Anti-pattern detection (orchestrator-driven, sonnet)

For each schedule's `command` field, read the script (if local file) and reason about:

1. **`exec` masks failures:**
   - Pattern: `^exec \S+` somewhere in the script
   - Why bad: replaces shell process; EXIT/ERR traps don't fire after
   - Decision: read the script. If trap is *defined but unused* due to `exec`, flag as ANTIPATTERN-EXEC.

2. **Missing failure-alert wiring:**
   - Pattern: script has no source of `notify_*` helper, no `curl` to a known alert channel, no email-send
   - Decision: if the cron fires daily-or-more, missing alerts = silent failures. Flag as ANTIPATTERN-NO-ALERTS.

3. **Stale alert channel reference:**
   - Pattern: script references `TELEGRAM_BOT_TOKEN` (the Hermes bot) but the documented infra-failure pattern routes to `TELEGRAM_FIX_BOT_TOKEN` (per `~/CLAUDE.md` § Telegram channel routing rule)
   - Decision: surface the cross-channel collapse. This is the same class of bug that got patched 2026-05-03.

4. **Token expiry / credential rot:**
   - Pattern: script reads `$XXX_API_KEY` but the env file's last-mtime is > 90 days
   - Decision: rotation may be overdue. Flag as ROTATION-OVERDUE.

5. **Webhook target unreachable:**
   - Pattern: script POSTs to a URL; HEAD-request the URL, see if it responds
   - Decision: webhook receiver may be down/wrong. Flag as TARGET-UNREACHABLE.

6. **Schedule expression mismatch:**
   - Pattern: comment says "every 5 minutes" but expression is `*/30 * * * *`
   - Decision: doc drift. Flag as DOC-DRIFT.

### Stage 4: Alert-channel sanity test (orchestrator)

For every alert channel referenced by audited scripts:

1. Read the env vars they reference
2. For each token, do a non-destructive ping:
   - Telegram: `getMe` API call (requires only the token; tells you if it's valid + which bot)
   - Email (SMTP): just verify the credential file is readable and parseable; don't send a message
   - Slack/Discord: similar — call a non-message endpoint to verify token
3. Classify:
   - `OK` — channel is reachable, token is valid
   - `EXPIRED` — token returns 401/403
   - `WRONG_BOT` — token is valid but resolves to a different bot than the script expects
   - `MISSING` — env var referenced by script but not set in any env file

### Stage 5: Fix loop (only if `--fix`)

For each finding type with a known-good fix:

| Finding | Fix | Source-of-truth template |
|---|---|---|
| ANTIPATTERN-EXEC | Convert `exec foo` → `foo; rc=$?; trap_handler $rc` capture-then-act | per `nolan-infra/scripts/lib/notify-fix-bot.sh` style |
| ANTIPATTERN-NO-ALERTS | Source `notify-fix-bot.sh`, add EXIT trap to call `notify_fix_bot` on non-zero | template lives in operator's `nolan-infra` repo |
| TELEGRAM-CHANNEL-COLLAPSE (`${FIX_TOKEN:-${BOT_TOKEN}}`) | Replace fallback with explicit per-script bot choice | per `~/CLAUDE.md` § Telegram channel routing |

Each fix:
1. Backs up the original (`script.sh.bak-<timestamp>`)
2. Applies the patch
3. Runs `bash -n script.sh` syntax-check
4. If `--dry-run`: shows diff, doesn't write
5. Logs the fix application to `.cron-audit-history.json` so future runs see it as a known-good fix

`--fix` NEVER:
- Modifies an entry the operator has marked `wip_alerts_protected`
- Touches GitHub Actions YAML (those go through PRs, not direct edits)
- Disables a cron entry (only patches scripts; if a cron itself should be removed, that's a manual operator decision)

### Stage 6: SITREP + history append

Generate report at `.cron-audit-reports/CA-YYYYMMDD-HHMMSS.md` with:

1. **Inventory summary** — N schedules across M sources, K hosts
2. **Findings table** — per finding: ID, severity, type, where, evidence
3. **Sibling-host state** (per MULTI_REPO_AWARENESS) — if other hosts in operator's known set were not audited this run, list them with last-audit timestamp
4. **Auto-fixes applied** (if `--fix`) — what was patched, with backup paths
5. **Manual recommendations** — items the skill won't auto-fix
6. **Suggested next** block (per autosuggest protocol)

Append to `.cron-audit-history.json`:
```json
{
  "run_id": "...",
  "host": "...",
  "schedules_audited": N,
  "findings": [...],
  "patterns_observed": { ... }
}
```

---

## SITREP TEMPLATE

```
═══════════════════════════════════════════════════════════════════════════════
                        SITREP — /cron-audit
═══════════════════════════════════════════════════════════════════════════════
Run ID:     CA-20260503-143022
Host:       claw-hq
Duration:   2m 14s
Schedules:  18 (5 user-cron, 11 systemd-user-timer, 2 github-actions-schedule)

────────────────────────────────────────────────────────────────────────────────
 OUTCOME CLASSIFICATION
────────────────────────────────────────────────────────────────────────────────
✅ OK        14 schedules firing within expected window
⚠️ STALE      2 schedules — last fire >2× expected window
❌ SILENT     1 schedule — service active, no log entries (deploy-webhook.service)
❌ ERROR      1 schedule — last fire exit-code non-zero (kernel-patch-watcher)

────────────────────────────────────────────────────────────────────────────────
 ANTI-PATTERN FINDINGS
────────────────────────────────────────────────────────────────────────────────
[CA-1] HIGH   ANTIPATTERN-EXEC         /home/openclaw/restic-backup-wrapper.sh
              `exec` on line 47 masks failure-alert trap on line 12
              REGRESSION: matches pattern fixed 2026-05-03 (per history)

[CA-2] MED    ANTIPATTERN-NO-ALERTS    /home/openclaw/some-old-cron.sh
              No alert channel wired; failures will be silent

[CA-3] HIGH   TELEGRAM-CHANNEL-COLLAPSE /home/openclaw/legacy-monitor.sh
              `${TELEGRAM_FIX_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN}}` collapses both
              bots into fix-bot. Per nolan-channel-routing.md anti-pattern.

────────────────────────────────────────────────────────────────────────────────
 ALERT-CHANNEL SANITY
────────────────────────────────────────────────────────────────────────────────
✅ Hermes-bot (TELEGRAM_BOT_TOKEN)        valid, resolves to @NolanChiefOfStaff_bot
✅ Fix-bot    (TELEGRAM_FIX_BOT_TOKEN)    valid, resolves to @NolanFixWorker_bot

────────────────────────────────────────────────────────────────────────────────
 SIBLING HOSTS NOT AUDITED THIS RUN
────────────────────────────────────────────────────────────────────────────────
nolan-prod   last audit 6d ago — re-run /cron-audit --host nolan-prod

────────────────────────────────────────────────────────────────────────────────
 AUTO-FIXES APPLIED  (only if --fix)
────────────────────────────────────────────────────────────────────────────────
(none — audit-only mode)

═══════════════════════════════════════════════════════════════════════════════
```

---

## Suggested next

Per [Skill Auto-Suggest Protocol](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md):

| Outcome | Recommended | Why |
|---|---|---|
| All OK | none — re-audit weekly | clean state, monitoring loop is fine |
| STALE / SILENT findings | /investigate the silent schedule | symptom-vs-cause work needed |
| Anti-patterns found, fixable | /cron-audit --fix | apply known-good patches |
| Anti-patterns found, ambiguous | /sec-ship --infra | escalate to deeper infra review |
| Sibling host not audited | /cron-audit --host \<sibling\> | extend coverage |
| Alert-channel expired token | /sec-ship --secrets-rotation or manual rotation | credential refresh |

**Skip if:** the operator just ran `/cron-audit --fix` and is verifying the SITREP is clean.

---

## DESIGN DECISIONS (WHY)

### Why a separate skill vs extending `/monitor`
`/monitor` is HTTP-route-and-deploy-focused — its mental model is "is the website up?" Cron-audit's mental model is "are the silent processes producing the work I expect?" The two domains share little. A merged skill would be 2x complexity for 2x users; better to keep them separate and chain.

### Why audit-only by default
The 2026-05-03 fixes (notify_fix_bot wrapper, EXIT-trap pattern, channel-routing fix) were operator-driven choices made after reviewing each script. A skill that auto-rewrites scripts without operator review would generate inconsistent fixes; the operator's judgment about which scripts route to which bot is contextual.

### Why `exec` detection is its own check
`exec` is the silent-failure smoking gun documented in the operator's memory (`feedback_exec_masks_failures.md`). Catching it specifically — rather than as part of generic "audit script" — means the SITREP can call out the exact pattern with the exact recovery procedure (capture-then-act).

### Why alert-channel sanity is in-scope
Half the silent-failure incidents this quarter weren't "the cron didn't fire" but "the cron fired, failed, and the alert it tried to send went into a dead channel." Auditing the cron without auditing its alert path is half a check.

### Why per-host history files
Cron state is per-host. Comparing `claw-hq`'s schedule inventory against `nolan-prod`'s would produce noise (different services, different schedules). Each host gets its own history file; the orchestrator surfaces cross-host coverage in the SITREP, not in the diff logic.

---

## DEFINITION OF DONE

- All schedules in `SCHEDULE_INVENTORY[]` classified
- Anti-pattern findings have file:line references
- Alert channels sanity-tested
- Sibling hosts surfaced (not auto-traversed)
- `.cron-audit-history-<host>.json` updated
- `.cron-audit-reports/CA-*.md` written
- SITREP ends with "Suggested next"
- If `--fix`: every patch has a backup file and a syntax-check pass
