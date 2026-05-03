# /backup-verify — Restic / Cloud-Backup Restore-Test

> **Standards inherited** (apply throughout this skill):
> - [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) — read + reason, don't pattern-match
> - [Self-Improvement Protocol](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) — log to `.backup-verify-history.json`, learn across runs
> - [Multi-Repo Awareness](~/.claude/standards/MULTI_REPO_AWARENESS.md) — scan siblings, surface in SITREP, never cross-traverse
> - [Verify Before Destroy](~/.claude/standards/VERIFY_BEFORE_DESTROY.md) — content-verify before destructive action
> - [Skill Auto-Suggest Protocol](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) — every SITREP ends with "Suggested next"

**A backup that has never been restored is not a backup. Test the restore path. Hash-compare. Drop the temp restore. Repeat monthly.**

## PARADIGM

The 2026-05-03 `~/.hermes/.env` clobber proved both halves of the backup-rot pattern:
1. **Coverage gap** — the file wasn't in `BACKUP_PATHS` (a `/secrets-audit` problem)
2. **Restore was never tested** — even if it HAD been backed up, no one had ever attempted a restore from R2 to verify the credentials still worked, the bucket policy still allowed the operator's IP, and the restic password file was actually readable

This skill closes the second half. It assumes coverage exists (use `/secrets-audit` for the first half) and exercises the restore path on representative data.

Anti-patterns:
- "restic snapshots succeeded → backup is fine" — backup write succeeding doesn't mean restore will
- "We tested restore once at install → still works" — credentials rotate, bucket policies drift, restic versions change
- "The most recent snapshot is what matters" — operator may need to restore from a snapshot 3 weeks back; verify older snapshots are reachable too

---

## DISCIPLINE

> Reference: [Superpowers Discipline Protocol](~/.claude/standards/STEEL_DISCIPLINE.md)

Steel principles applied:

- **#1 (verification before claim):** "the backup is healthy" requires a successful restore-and-hash-compare, not "restic snapshots succeeded"
- **#7 (no tech debt):** if the restore-test reveals stale credentials or a wrong bucket policy, fix the root cause; don't just file a TODO

### Rationalization defense

| Rationalization | Reality | Do |
|---|---|---|
| "Restic listed snapshots, that's good enough" | listing != restoring | Pull at least one file out and verify content match |
| "Disk space is tight, skip the restore-test" | Disk space at restore-time will also be tight; rehearse | Do a small targeted restore (10-100 MB), not full |
| "Daily backup ran last night, no need to verify monthly" | Backups can succeed for years and fail to restore on first try | Monthly restore-test cadence regardless of backup-write health |
| "I'll write a restore-test script later" | "Later" is when you actually need a restore; bad time to find bugs | Test now, in a known-good state |

---

## CRITICAL RULES

1. **NEVER restore over live data.** Restore goes to a temp dir. Hash-compare. Then delete the temp dir.
2. **NEVER expose secrets during the test.** Restored content stays in temp dir at 0700; never `cat` it to console; only hash compare.
3. **Read-only against the backup target.** This skill never deletes snapshots, never forgets, never re-init's the repo.
4. **Multi-target aware.** Operator may have multiple backup targets (R2 for `claw-hq`, B2 archive for old data, GitHub for sanitized infra). Audit each target separately.
5. **Verify credentials work BEFORE the restore attempt.** A 401 on auth means the backup config is stale; surface that as the finding instead of a confused restore-failed message.
6. **History-driven.** `.backup-verify-history.json` per host tracks last successful restore-test date.
7. **Sample, don't full-restore.** Pull a small representative subset (100MB cap or 10 files cap, whichever first). Full-restore tests are operator-driven, not automated.
8. **SITREP ends with Suggested next.**

---

## MODES

```
/backup-verify                       # Default: latest snapshot, sample 10 files
/backup-verify --host claw-hq        # Verify backup target for a remote host
/backup-verify --target r2           # Restrict to a single named target
/backup-verify --snapshot <id>       # Verify a specific snapshot, not latest
/backup-verify --depth full          # Pull every path in BACKUP_PATHS (operator-driven, expensive)
/backup-verify --since=30d           # Verify all snapshots in last 30 days are reachable (lightweight metadata-only)
```

---

## DETECTION

### Backup-target discovery

| Indicator | Target | How to inspect |
|---|---|---|
| `restic-backup.sh` + `BACKUP_PATHS` | restic to S3-compatible (R2/B2/AWS) | `restic snapshots` |
| `~/.config/restic/repo` | restic local | restic CLI |
| `borgmatic` config | borg repo | `borg list` |
| `pg_dump` cron + S3 upload | DB backup separate from filesystem | inspect cron + check S3 LATEST timestamp |
| GitHub Actions cron with backup workflow | repo-level backup | `gh run list` |

For each detected target, capture:
- `target_id` (target name + host)
- `repo_url` (e.g. `s3:s3.us-east-1.amazonaws.com/bucket`)
- `credentials_source` (env var names, key file paths)
- `last_known_good_restore` (from history)
- `paths_covered[]` (`BACKUP_PATHS` or equivalent)

### Pre-flight credential check

Before any restore attempt:
1. Verify env vars are set (not the values, just existence)
2. Verify password file is readable
3. Run `restic snapshots --no-cache --quiet --json | head -1` (cheap, surfaces auth failure fast)
4. If 401/403: classify as `CREDS-EXPIRED`; do NOT attempt restore

---

## STAGES

### Stage 0: Pre-flight + history read

Read `.backup-verify-history-<host>.json`. Extract:
- Last successful restore-test date per target
- `flagged_targets[]` — operator-marked "leave alone" (e.g. mid-migration)
- Known-good sample-files used for hash comparison

Auto-gitignore the history file.

### Stage 1: Target discovery

Run detection above; populate `BACKUP_TARGETS[]`.

### Stage 2: Per-target credential probe

For each target, sub-agent (haiku) attempts:
- env var existence check
- credential file readability
- repo metadata fetch (`restic snapshots` or equivalent)

Classifications:
- `OK` — credentials valid, repo reachable
- `CREDS-EXPIRED` — auth fails (401/403)
- `REPO-UNREACHABLE` — network/DNS issue (5xx, timeout)
- `MISCONFIG` — env vars missing, password file unreadable
- `UNKNOWN` — fall through to operator review

### Stage 3: Snapshot freshness check

For each `OK` target:

1. List all snapshots, get most recent timestamp
2. Compare against expected schedule (daily backup → most recent should be < 25h old)
3. Classify:
   - `FRESH` — within window
   - `STALE` — last snapshot > 2× expected window
   - `EMPTY` — no snapshots ever (new repo, or backup never ran)

### Stage 4: Restore-test (the actual restore)

For each `OK` + `FRESH` target:

1. Pick a representative sample:
   - From the latest snapshot, pick small files (< 10 MB each) up to 10 files / 100 MB total
   - Prefer text files (env files, configs) over binary blobs (better signal-to-noise on hash compare)
   - Skip secrets — restore everything else first; secrets get a separate verify if needed

2. Restore to a temp dir (`mktemp -d`):
   ```
   restic restore <snapshot> --target $TMPDIR --include <selected-paths>
   ```

3. For each restored file:
   - Compute hash of restored content
   - Compute hash of source content (live file)
   - Compare

4. Classifications:
   - `RESTORED-MATCH` — restore worked, content matches live
   - `RESTORED-DIFF` — restore worked but content differs from live (file changed since backup; this is EXPECTED for active files; not a failure)
   - `RESTORE-FAILED` — restic command exited non-zero
   - `MISSING-IN-SNAPSHOT` — file is in `BACKUP_PATHS` but not in the snapshot (coverage gap, restic exclusion bug, etc.)

5. **Cleanup:** `rm -rf $TMPDIR` — verify it's gone before moving on (per VERIFY_BEFORE_DESTROY)

### Stage 5: Snapshot retention check

For each target, list snapshots over the configured retention window. Verify count matches expectation (e.g. restic policy `--keep-daily 7 --keep-weekly 4 --keep-monthly 12` → expect 7 daily + 4 weekly + 12 monthly = ~23 snapshots).

If snapshot count is way under expected: surface as `RETENTION-DRIFT`.

### Stage 6: SITREP + history

Write report to `.backup-verify-reports/BV-YYYYMMDD-HHMMSS.md`. Append to `.backup-verify-history-<host>.json`.

If all targets are `OK + FRESH + RESTORED-MATCH`: SITREP says CLEAN.
If any target has issues: SITREP categorizes and recommends remediation.

---

## SITREP TEMPLATE

```
═══════════════════════════════════════════════════════════════════════════════
                       SITREP — /backup-verify
═══════════════════════════════════════════════════════════════════════════════
Run ID:     BV-20260503-190044
Host:       claw-hq
Targets:    1 (restic → R2 bucket claw-hq)
Duration:   2m 51s

────────────────────────────────────────────────────────────────────────────────
 PER-TARGET STATUS
────────────────────────────────────────────────────────────────────────────────
restic → R2 bucket claw-hq
  ✅ Credentials      OK
  ✅ Snapshot freshness  FRESH (last fire 2026-05-03 03:00 CDT, 16h ago)
  ✅ Restore test     RESTORED-MATCH (8 sample files, 1 RESTORED-DIFF as expected for active log)
  ✅ Retention        23 snapshots within policy (7 daily + 4 weekly + 12 monthly)
  ✅ Coverage         all BACKUP_PATHS resolved in snapshot

────────────────────────────────────────────────────────────────────────────────
 LAST KNOWN GOOD
────────────────────────────────────────────────────────────────────────────────
Previous successful restore-test: 2026-04-03 (30 days ago — within monthly cadence)

────────────────────────────────────────────────────────────────────────────────
 TEMP CLEANUP
────────────────────────────────────────────────────────────────────────────────
✅ Restore temp dir removed (/tmp/tmp.XXXXXX)
✅ No residual restored content on disk

────────────────────────────────────────────────────────────────────────────────
 SIBLING HOSTS NOT VERIFIED THIS RUN
────────────────────────────────────────────────────────────────────────────────
nolan-prod   never verified — re-run /backup-verify --host nolan-prod

═══════════════════════════════════════════════════════════════════════════════
```

---

## Suggested next

Per [Skill Auto-Suggest Protocol](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md):

| Outcome | Recommended | Why |
|---|---|---|
| All targets clean | none — re-verify monthly | clean state |
| CREDS-EXPIRED | /secrets-audit --rotate <provider> | rotate then re-verify |
| MISSING-IN-SNAPSHOT (coverage gap) | /secrets-audit --check coverage | diagnose backup-path config |
| RETENTION-DRIFT | /investigate the restic forget policy | retention misconfig needs root-cause |
| RESTORE-FAILED | /investigate | could be repo corruption — needs deep look |
| Sibling host never verified | /backup-verify --host <sibling> | extend coverage |

**Skip if:** the operator just did a manual restore-test outside the skill (rare, but they may have).

---

## DESIGN DECISIONS (WHY)

### Why sample-restore vs full-restore
Full restores are expensive (R2 bandwidth + disk + time) and infrequent. Sample restores catch the same failure modes (creds, network, repo integrity) at a fraction of the cost. Operator can run `--depth full` when they want a real disaster-recovery rehearsal.

### Why hash-compare vs cat
The point is to verify content arrived intact. Comparing hashes proves that without ever displaying restored content. Critical for env files — restored content stays out of stdout/logs.

### Why the temp dir is enforced at 0700
Restored content is sensitive (operator's env files, config). Setting the temp dir permissions tightly prevents another process on the host from reading the restored files during the test window.

### Why the `RESTORED-DIFF` classification exists
Active log files / databases have different content between the snapshot moment and "now." Without this classification, every active file would falsely register as a restore failure. Diff-from-live is expected for live-changing files; the test is whether restore *worked*, not whether content matches a moving target.

### Why per-host history files
Same reason as `/cron-audit` and `/secrets-audit` — each host has its own backup config, schedule, and restore-test cadence. Cross-host comparisons would produce noise.

### Why this is its own skill, not part of `/secrets-audit`
`/secrets-audit` operates on the env-file ecosystem layer. `/backup-verify` operates on the backup-target layer (which covers more than secrets — includes data, configs, logs, the whole filesystem subset). Different domains, different mental models.

---

## DEFINITION OF DONE

- Every detected backup target probed for credentials
- Every `OK` target's freshness classified
- At least one restore-test run on each `OK + FRESH` target
- Hash-compare results recorded
- Temp restore dir verified DELETED
- `.backup-verify-history-<host>.json` updated
- `.backup-verify-reports/BV-*.md` written
- SITREP ends with "Suggested next"
