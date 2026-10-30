# Resource Cleanup Protocol for All Skills

**Version:** 1.0
**Applies to:** All skills in `~/.claude/commands/`
**Companion to:** [Context Management Protocol](./CONTEXT_MANAGEMENT.md), [Status Update Protocol](./STATUS_UPDATES.md), [Agent Orchestration Protocol](./AGENT_ORCHESTRATION.md)

---

## The Problem

Skills create resources during execution: browser instances, dev servers, test data, temporary files, git stashes, and dependency changes. When a skill finishes - or crashes mid-run - these resources persist. Over time, orphaned Chromium processes consume memory, held ports block other work, test data pollutes databases, and stale git artifacts clutter the repository.

**A skill that doesn't clean up after itself is not production-grade.**

---

## The Principle

**Leave no trace.** When a skill finishes, the system should be in the same state as before the skill ran - plus the intended outputs (report files, code fixes, generated content). Everything else is a leak and must be cleaned up.

Intended outputs:
- Report files in `.[skill]-reports/` directories
- Code changes (fixes, migrations, generated content)
- Git commits on appropriate branches

Everything else - dev servers, browser instances, test data, temp files, background processes - must be cleaned up before the skill exits.

---

## Core Rules

### Rule 1: Track Every Resource You Create

Every resource created during a skill run must be registered in a cleanup manifest. The manifest lives in memory (or in the state file for crash recovery).

**Resource categories and their tracking:**

| Resource Type | How to Track | Cleanup Action |
|--------------|-------------|----------------|
| Dev server | PID stored in variable | `kill $PID` |
| Browser instance | Playwright session | `browser_close` |
| Background process | PID stored in variable | `kill $PID` |
| Git stash | Stash name/ref stored | `git stash drop` |
| Git branch | Branch name stored | Delete if temp; keep if intentional |
| Temp files | File paths stored | `rm -f $paths` |
| Test database records | Record IDs or prefix stored | DELETE query |
| Installed dependencies | Package names stored | Revert if unintentional |
| Port bindings | Port number stored | Verify port released |

### Rule 2: Cleanup Runs ALWAYS - Success or Failure

Cleanup is not optional. It runs:
- On successful completion (final stage)
- On failure/abort (error recovery)
- On context reset (resume protocol checks for orphans)

Structure your skill like a try/finally:
```
try:
  Stage 0: Initialize (track resources)
  Stage 1-N: Do work
  Final Stage: Report + Cleanup
finally:
  Cleanup (runs even if stages fail)
```

### Rule 3: Cleanup Order Matters

Clean up in reverse order of creation (LIFO - last in, first out):

```
1. Close browser instances (they hold the most memory)
2. Stop dev servers and background processes
3. Delete test data from databases
4. Remove temp files outside report directories
5. Drop git stashes (if created by this skill)
6. Verify ports are released
7. Verify no orphaned child processes remain
```

### Rule 4: Verify Cleanup Succeeded

Don't just run the cleanup command - verify it worked:

```bash
# Bad: Fire and forget
kill $DEV_SERVER_PID

# Good: Verify the process is gone
kill $DEV_SERVER_PID 2>/dev/null
sleep 1
if kill -0 $DEV_SERVER_PID 2>/dev/null; then
  kill -9 $DEV_SERVER_PID  # Force kill
  echo "⚠️ Dev server required force kill"
fi
```

```bash
# Bad: Assume port is free
# Good: Verify port is free
if lsof -ti:3000 >/dev/null 2>&1; then
  echo "⚠️ Port 3000 still in use after cleanup"
  kill $(lsof -ti:3000) 2>/dev/null
fi
```

### Rule 5: Never Swallow Cleanup Errors

If cleanup fails, log it prominently in the report and warn the user:

```markdown
## ⚠️ Cleanup Warnings
- Dev server on port 3000 could not be stopped (PID 12345 - kill manually)
- 3 test records in `sm_test_data` could not be deleted (permission denied)
```

The skill should still complete (don't fail the entire run because cleanup failed), but the user must know about orphaned resources.

### Rule 6: Ephemeral Artifacts Must Be Purged

Skills generate artifacts that are useful DURING the run but become waste AFTER. These must be cleaned up at the end of each run unless explicitly retained.

**Ephemeral artifacts and their lifecycle:**

| Artifact | Created By | Useful During | Delete When |
|----------|-----------|---------------|-------------|
| Screenshots (page health, responsive) | `/qatest`, `/design`, `/browse`, `/a11y` | Audit analysis, evidence linking | End of run - UNLESS linked to a finding in the report |
| Before/after evidence screenshots | `/qatest`, `/design`, `/investigate` | Report evidence | **KEEP** - these are finding-linked evidence. Delete only if finding was FALSE POSITIVE |
| CSS inspection dumps | `/browse` | Debugging | End of run |
| Live metric JSON files | `/perf` | Before/after comparison | **KEEP `baseline.json` and `current.json`** only. Delete intermediate measurement files. |
| Route manifests | `/qatest` | Phase 1 discovery | End of run |
| State/checkpoint files | All skills | Crash recovery | End of SUCCESSFUL run. Keep on failure (enables resume). |
| Test user accounts | `/qatest`, `/redteam` | Testing authenticated flows | **MUST delete** at end of run (see Rule 6a) |
| Test form submissions | `/qatest` | Form testing | **MUST delete** at end of run (see Rule 6a) |
| Git bisect state | `/investigate` | Bisect operation | End of run (`git bisect reset`) |
| Temporary logs (`[INV]` markers) | `/investigate` | Hypothesis testing | End of run (grep + remove) |

**Screenshot retention policy:**

```
Per-run screenshot budget:
  - Page screenshots (responsive batch): DELETE at end of run
  - Finding-linked evidence (before/after): KEEP (referenced in report)
  - Audit screenshots: KEEP only the LATEST run's screenshots
  
Cross-run retention:
  - DELETE all screenshots from runs older than 7 days
  - DELETE all state files from runs older than 24 hours
  - KEEP all report .md files (they're the permanent record)
  - KEEP baseline.json and history.json (trend tracking)
```

**Report directory cleanup (prevents bloat across multiple runs):**

At the START of every skill run, before creating new artifacts:
```bash
REPORT_DIR=".[skill]-reports"

# Delete screenshots from previous runs (keep evidence/)
find "$REPORT_DIR/screenshots" -type f -mtime +7 -delete 2>/dev/null

# Delete state files older than 24 hours (no longer useful for resume)
find "$REPORT_DIR" -name "state-*.json" -mtime +1 -delete 2>/dev/null

# Delete intermediate metric files (keep baseline.json, current.json, history.json)
find "$REPORT_DIR" -name "live-metrics-*.json" -mtime +7 -delete 2>/dev/null

# Log what was cleaned
echo "Cleaned $(find "$REPORT_DIR" -name "*.png" -mtime +7 | wc -l) old screenshots"
```

### Rule 6a: Test Data MUST Be Deleted - No Exceptions

Any data created in a database during skill execution MUST be deleted before the skill exits. This is not optional. Test data left in databases causes:
- Confusion when users see test records in their app
- Data integrity issues when test records have fake relationships
- Storage bloat over repeated runs
- Security risk if test data contains predictable patterns

**Test data lifecycle:**

```
1. CREATE: Use a recognizable prefix (e.g., `qatest_`, `redteam_`, `inv_`)
2. TRACK: Record every created record ID in the state file
3. USE: Run tests against the created data
4. DELETE: Remove ALL created records by ID or prefix
5. VERIFY: SELECT count with prefix - must be 0
6. LOG: Report how many records were created and deleted
```

**If deletion fails:**
- Retry once
- If still fails: log the EXACT records that remain (table, IDs, prefix)
- Include manual cleanup command in the report:
  ```sql
  -- Manual cleanup for failed test data deletion
  DELETE FROM sm_contact_inquiries WHERE email LIKE 'qatest_%';
  DELETE FROM users WHERE email LIKE 'redteam_%';
  ```
- **NEVER silently leave test data.** The user MUST be told.

**Test accounts specifically:**
- If the skill created a test user account (for auth flow testing), that account MUST be deleted
- If the account cannot be deleted (e.g., no admin API): document it prominently in SITREP with deletion instructions
- Use unique, timestamped identifiers: `qatest_1711900800@example.com` (not `test@test.com`)

### Rule 7: Gitignore Enforcement is Mandatory

Every skill that creates a report or artifact directory MUST ensure it is gitignored:

```bash
# Standard pattern - use in every skill's Stage 0
REPORT_DIR=".[skill]-reports"
if [ ! -d "$REPORT_DIR" ]; then
  mkdir -p "$REPORT_DIR"
fi
grep -q "$REPORT_DIR" .gitignore 2>/dev/null || echo "$REPORT_DIR/" >> .gitignore
```

**No exceptions.** Report files contain machine-specific paths, timestamps, and potentially sensitive findings. They must never be committed.

### Rule 7: Dependency Installs Require Disclosure

If a skill installs packages (devDependencies or otherwise), it MUST:

1. **Disclose before installing:** Log what will be installed and why
2. **Track what was installed:** Record package names in the state file
3. **Note in the report:** List all dependency changes in the SITREP
4. **Mark as intentional vs temporary:**
   - **Intentional** (e.g., `/a11y` installs `axe-core`): Document in report, user keeps them
   - **Temporary** (e.g., one-time scan tool): Uninstall after use

```markdown
## Dependencies Modified
| Package | Action | Reason | Permanent? |
|---------|--------|--------|------------|
| axe-core | Installed (devDep) | Required for accessibility scanning | Yes - needed for future /a11y runs |
| @playwright/test | Installed (devDep) | Required for E2E testing | Yes - needed for future /test-ship runs |
```

### Rule 8: Sub-Agent Cleanup is the Orchestrator's Responsibility

If a skill spawns sub-agents that create resources (e.g., `/launch` spawning `/test-ship`), the orchestrator must:

1. Instruct each sub-agent to clean up after itself
2. Verify cleanup after each sub-agent completes
3. Run a final sweep for any orphaned resources

Sub-agent prompts MUST include:
> "After completing your work, clean up all resources you created: close browser instances, stop any dev servers you started, delete test data, and remove temp files. Report cleanup status in your return summary."

The orchestrator verifies by checking:
```bash
# After sub-agents complete:
# 1. Check for orphaned processes
pgrep -f "next dev|playwright|chromium" | head -5
# 2. Check for held ports
lsof -ti:3000,3001,4000 2>/dev/null
# 3. Check for temp files
ls /tmp/*-test-* /tmp/evil.* 2>/dev/null
```

### Rule 9: Dev Server Policy

Skills that start dev servers must follow one of these policies:

| Policy | When to Use | Cleanup |
|--------|------------|---------|
| **Start + Stop** | Skill needs server temporarily for testing | Kill PID when done |
| **Start + Leave (Explicit)** | User will need the server after skill finishes | Warn in SITREP: "Dev server left running on port 3000" |
| **Use Existing** | Skill detects a running server | Don't start, don't stop |

**Default is Start + Stop.** Only use Start + Leave if the skill's purpose involves ongoing development (e.g., `/dev`).

If a skill uses Start + Leave, it MUST:
1. Note the PID in the report
2. Note the port in the report
3. Add a SITREP line: "Dev server left running on port [PORT] (PID [PID]). Stop with: `kill [PID]`"

### Rule 10: Crash Recovery Must Check for Orphans

When a skill resumes from a crash/context reset, the first thing it does is check for orphaned resources from the previous run:

```bash
# Resume protocol - orphan detection
STATE_FILE=".${SKILL}-reports/state-*.json"
if [ -f $STATE_FILE ]; then
  # Check if previous run's dev server is still running
  PREV_PID=$(jq -r '.resources.devServerPid // empty' $STATE_FILE)
  if [ -n "$PREV_PID" ] && kill -0 $PREV_PID 2>/dev/null; then
    echo "⚠️ Previous run's dev server still running (PID $PREV_PID)"
    # Decide: reuse or kill
  fi

  # Check for orphaned browser processes
  PREV_BROWSER=$(jq -r '.resources.browserPid // empty' $STATE_FILE)
  if [ -n "$PREV_BROWSER" ] && kill -0 $PREV_BROWSER 2>/dev/null; then
    echo "⚠️ Previous run's browser still running - killing"
    kill $PREV_BROWSER 2>/dev/null
  fi
fi
```

---

## State File Resource Tracking

Add a `resources` field to the state file (alongside existing `skill`, `status`, `stagesCompleted`, etc.):

```json
{
  "skill": "qatest",
  "status": "in_progress",
  "resources": {
    "devServer": {
      "pid": 12345,
      "port": 3000,
      "startedBySkill": true,
      "policy": "start_stop"
    },
    "browser": {
      "active": true,
      "type": "playwright"
    },
    "testData": {
      "database": "supabase",
      "table": "sm_contact_inquiries",
      "prefix": "qatest_",
      "recordIds": ["uuid-1", "uuid-2"]
    },
    "tempFiles": [
      "/tmp/evil.php.jpg",
      ".deps-audit.json"
    ],
    "gitStash": "cleancode-backup-1708819200",
    "installedDeps": ["axe-core", "@axe-core/cli"],
    "backgroundProcesses": [
      { "pid": 12346, "name": "health-monitor" }
    ]
  }
}
```

This enables crash recovery to find and clean up orphaned resources.

---

## Cleanup Phase Template

Add this as the **second-to-last stage** of every skill (before the final Report/SITREP stage):

```markdown
## STAGE [N-1]: CLEANUP

**No agent needed - orchestrator handles cleanup directly.**

### Actions (in order)

1. **Close browser instances:**
   - Call `browser_close` for any open Playwright sessions
   - Verify: `pgrep -f "chromium|chrome|playwright" | wc -l` should match pre-skill count

2. **Stop dev server (if started by this skill):**
   - `kill $DEV_SERVER_PID`
   - Verify: `kill -0 $DEV_SERVER_PID` should fail (process gone)
   - Verify: `lsof -ti:$PORT` should be empty
   - If using Start + Leave policy: skip kill, log in SITREP

3. **Delete test data:**
   - Query database for records with skill prefix (e.g., `qatest_`)
   - DELETE matching records
   - Verify: SELECT count should be 0
   - If deletion fails: log in report, warn user

4. **Remove temp files:**
   - Delete any files tracked in `resources.tempFiles`
   - Delete any files in `/tmp/` matching skill patterns
   - Verify: `ls` should not find them

5. **Clean git artifacts:**
   - Drop stashes created by this skill: `git stash drop [ref]`
   - Delete temp branches (if any): `git branch -d [name]`
   - Verify: `git stash list` and `git branch` are clean

6. **Kill background processes:**
   - Kill any PIDs in `resources.backgroundProcesses`
   - Verify: processes are gone

7. **Verify ports released:**
   - Check all ports used during the run
   - Force-kill any lingering port holders

8. **Final orphan sweep:**
   - `pgrep -f "next dev|next-server|playwright|chromium"` - compare against pre-skill baseline
   - Kill any new processes that the skill created
   - Log any processes that couldn't be killed

9. **Update state file:**
   - Set `resources` to `{}` (empty - all cleaned)
   - Or log remaining orphans with warnings

10. **Log cleanup results in report:**
    ```markdown
    ## Cleanup
    - [x] Browser instances closed
    - [x] Dev server stopped (PID 12345, port 3000)
    - [x] Test data deleted (3 records from sm_contact_inquiries)
    - [x] Temp files removed (2 files)
    - [x] Git stash dropped
    - [x] All ports released
    - [x] No orphaned processes
    ```
```

---

## Skill-Specific Cleanup Reference

Based on the resource audit, here are the cleanup requirements per skill:

### Skills That MUST Have Full Cleanup

| Skill | Browser | Dev Server | Test Data | Temp Files | Git Artifacts | Deps |
|-------|:-------:|:----------:|:---------:|:----------:|:-------------:|:----:|
| `/qatest` | Close | Stop | Delete `qatest_*` records | -- | -- | -- |
| `/test-ship` | Kill Playwright | Stop (has this) | Delete test users (has this) | Root JSON files | Snapshot commit | Disclose installs |
| `/design` | **Close** | -- | -- | Screenshots | -- | -- |
| `/landing-page` | Close if opened | -- | -- | -- | -- | Disclose installs |
| `/redteam` | -- | Stop or disclose | Delete test users (has this) | Delete `/tmp/evil.*` (has this) | -- | -- |
| `/launch` | Verify sub-agents cleaned | Verify sub-agents cleaned | Verify sub-agents cleaned | Stale scorecards | -- | -- |
| `/dev` | -- | Disclose (Start+Leave) | -- | -- | -- | Disclose lockfile changes |
| `/db` | -- | -- | Document seed data | `.db/*.sql` | -- | -- |
| `/browse` | Close | -- | -- | Screenshots, CSS dumps | -- | -- |
| `/investigate` | Close if opened | -- | -- | Temp logs (`[INV]`), bisect state | Bisect reset | -- |

### Skills That Need Only Gitignore Enforcement

| Skill | Report Dir | Needs Gitignore Fix |
|-------|-----------|:-------------------:|
| `/compliance` | `.compliance/` | YES - add enforcement |
| `/sec-ship` | `.security-reports/` | Verify existing |
| `/a11y` | `.a11y/` | YES - add enforcement |
| `/browse` | `.browse/` | YES - add enforcement |
| `/investigate` | `.investigate/` | YES - add enforcement |

### Skills That Are Already Clean (No Cleanup Needed)

| Skill | Why |
|-------|-----|
| `/monitor` | Read-only, HTTP checks only, gitignore enforced |
| `/incident` | Code changes are intentional, failed fixes reverted, gitignore enforced |
| `/migrate` | Branch is intentional, gitignore enforced |
| `/perf` | Live browser measurement added - now needs browser cleanup (see full cleanup table) |
| `/docs` | Minor: `/tmp/example.ts` orphan (fix this) |
| `/mdmp` | Planning tool, minimal side effects |
| `/smoketest` | Minimal side effects |
| `/gh-ship` | Already has best-in-class cleanup (Stage 12) |
| `/deps` | Has cleanup phase, minor `.deps-audit.json` orphan |
| `/cleancode` | Minor: git stash not dropped on success |
| `/sec-ship` | Code changes are intentional, exclusions.json is permanent |

---

## Process Baseline Capture

At the start of every skill run, capture a baseline of running processes and ports. This enables the final orphan sweep to detect exactly what the skill created:

```bash
# Capture at Stage 0
BASELINE_PROCESSES=$(pgrep -f "next|playwright|chromium|node" 2>/dev/null | sort)
BASELINE_PORTS=$(lsof -ti:3000,3001,4000,5432,8080 2>/dev/null | sort)

# Compare at Cleanup Stage
CURRENT_PROCESSES=$(pgrep -f "next|playwright|chromium|node" 2>/dev/null | sort)
CURRENT_PORTS=$(lsof -ti:3000,3001,4000,5432,8080 2>/dev/null | sort)

NEW_PROCESSES=$(comm -13 <(echo "$BASELINE_PROCESSES") <(echo "$CURRENT_PROCESSES"))
NEW_PORTS=$(comm -13 <(echo "$BASELINE_PORTS") <(echo "$CURRENT_PORTS"))

if [ -n "$NEW_PROCESSES" ]; then
  echo "⚠️ New processes detected since skill start:"
  echo "$NEW_PROCESSES" | xargs ps -p 2>/dev/null
fi
```

---

## Implementation Checklist

When adding this protocol to a skill:

- [ ] Add `CLEANUP PROTOCOL` section referencing this standard
- [ ] Add `resources` field to state file template
- [ ] Capture process baseline at Stage 0
- [ ] Track every resource as it's created
- [ ] Add cleanup stage (second-to-last, before Report/SITREP)
- [ ] Cleanup runs on both success AND failure paths
- [ ] Verify each cleanup action succeeded
- [ ] Log cleanup results in the report
- [ ] Enforce gitignore for report directory
- [ ] Disclose any permanent dependency installs
- [ ] If orchestrator skill: verify sub-agent cleanup
- [ ] If crash recovery: check for orphaned resources from previous run

---

## Reference in Skills

Add this section to your skill file:

```markdown
## CLEANUP PROTOCOL

> Reference: [Resource Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md)

### [Skill]-Specific Cleanup

Resources this skill may create:
- [List each resource type]

Cleanup actions (run after final work stage, before report):
1. [Specific action for this skill]
2. [Specific action for this skill]
...

Cleanup verification:
- [How to verify each cleanup succeeded]
```

---

## Anti-Patterns

### 1. "The user can clean it up"
```
❌ BAD:  "Dev server left running. User can kill it."
✅ GOOD: Kill the dev server. If Start+Leave policy, explicitly disclose PID and port.
```

### 2. "It's just a small file"
```
❌ BAD:  Leave .deps-audit.json in project root
✅ GOOD: Write to .[skill]-reports/ directory, or delete after use
```

### 3. "The process will die eventually"
```
❌ BAD:  Assume Chromium will close when idle
✅ GOOD: Explicitly call browser_close and verify the process is gone
```

### 4. "Cleanup failed, oh well"
```
❌ BAD:  Silently ignore cleanup errors
✅ GOOD: Log cleanup failures prominently, warn user with manual cleanup commands
```

### 5. "Sub-agents handle their own cleanup"
```
❌ BAD:  Trust sub-agents cleaned up without verification
✅ GOOD: Verify cleanup after each sub-agent, run final orphan sweep
```

---

## Why This Matters

- **Without cleanup:** Skills leak memory (Chromium), hold ports (dev servers), pollute databases (test data), and leave orphan files that confuse `git status`. Over a day of skill usage, the system degrades.
- **With cleanup:** Every skill run is hermetic. The system is in a clean state before, during recovery, and after every run. Users never encounter mysterious orphaned processes or unexplained test data.

A production-grade skill cleans up after itself. Always.

---

*Last Updated: 2026-03-31*
