---
description: Start a clean development server (fast, resilient, self-healing)
allowed-tools: Bash(git *), Bash(npm *), Bash(npx *), Bash(pnpm *), Bash(yarn *), Bash(sleep *), Bash(cat *), Bash(node *), Bash(mkdir *), Bash(ls *), Bash(head *), Bash(tail *), Bash(grep *), Bash(find *), Bash(xargs *), Bash(kill *), Bash(pkill *), Bash(pgrep *), Bash(lsof *), Bash(echo *), Bash(source *), Bash(export *), Bash(df *), Bash(du *), Bash(ps *), Bash(wc *), Bash(stat *), Bash(vm_stat *), Bash(PATH=*), Bash(open *), Bash(curl *), Bash(rm *), Read, Write, Edit, Glob, Grep, Agent
when_to_use: Trigger phrases: "start dev server", "run the app"
---

# /dev - Just Works

**One command. No flags to remember. It figures out what's wrong and fixes it.**

```bash
/dev 5888
```

That's it. Server starts on port 5888. If something's broken, it fixes it automatically.

---

## DISCIPLINE

> Reference: [Superpowers Discipline Protocol](~/.claude/standards/STEEL_DISCIPLINE.md)

Key enforcements for this skill:
- **Steel Principle #1:** NO completion claims without fresh verification evidence - curl the port and confirm the app responded with 200
- **Steel Principle #4:** NO declaring "server started" based on log tail alone - hit the URL
- Never kill processes outside this project (other projects' dev servers stay untouched)

### Dev-Specific Rationalization Table

| Rationalization | Reality | What to Do |
|----------------|---------|------------|
| "The dev server usually starts" | Usually != always. Port collisions, stale caches, corrupt `.next` all cause silent failures | Verify with curl against the actual port |
| "Logs say 'ready' so it must be up" | Log line 'ready' can fire before the HTTP server binds, or while routes 500 | Hit a real route, check for 200 |
| "I'll just kill all node processes" | Kills other projects' servers, IDE helpers, language servers | Kill only PIDs bound to this project's port |
| "The process is running, skip the health check" | Running != serving; ghost processes bind the port without responding | Run the health ping, not just ps |

---

## Usage

```bash
/dev 5888        # Start on port 5888 - handles everything
/dev             # Start on port 3000 (default)
/dev 5888 -v     # Verbose: show all monitoring/healing output
/dev 5888 -m     # Minimal: just start, skip smart features
```

---

## What It Does Automatically

You don't need to think about any of this. It just happens:

| Situation | Auto-Fix |
|-----------|----------|
| Port already in use | Kills the listening process, starts fresh |
| Stale dependencies (package.json newer than node_modules) | Runs install |
| Corrupted .next cache | Detects corruption signals, clears only when needed |
| Low system memory (<1GB free) | Kills stale Node processes, clears cache |
| Server crashes | Auto-restarts with graduated recovery (4 levels) |
| Repeated crashes | Escalates: cache clear → dep reinstall → nuclear clean |
| Other projects' dev servers | Left alone - only kills processes from current project |

**You only see output when something needed fixing.** Otherwise, it just starts.

---

## Execution Rules

- **NO permission requests** - just execute
- **NO flags to remember** - smart by default
- **Turbopack enabled** - faster rebuilds, stable HMR
- **Silent unless needed** - only shows output when fixing something

---

## STATUS UPDATES

This skill follows the [Status Update Protocol](~/.claude/standards/STATUS_UPDATES.md). See standard for emoji format and cadence rules.

---

## Phase 1: Parse Arguments

```bash
PORT=3000
VERBOSE=false
MINIMAL=false

for arg in $ARGUMENTS; do
  if [[ "$arg" =~ ^[0-9]{4,5}$ ]]; then
    PORT="$arg"
  elif [[ "$arg" == "-v" || "$arg" == "--verbose" ]]; then
    VERBOSE=true
  elif [[ "$arg" == "-m" || "$arg" == "--minimal" ]]; then
    MINIMAL=true
  fi
done
```

---

## Phase 2: Setup Environment

### 2.1 Detect Package Manager

```bash
if [ -f "pnpm-lock.yaml" ]; then
  PKG="pnpm"
elif [ -f "yarn.lock" ]; then
  PKG="yarn"
else
  PKG="npm"
fi
```

### 2.2 Set Node Path

```bash
export PATH="$HOME/.nvm/versions/node/v22.18.0/bin:$PATH"
```

---

## Phase 3: Smart Preparation (skip if -m flag)

**All checks run quickly (<2s total). Only act if issues found.**

### 3.1 Kill Port Conflicts

```bash
# Kill anything LISTENING on target port (more precise than bare lsof)
PORT_PIDS=$(lsof -ti:$PORT -sTCP:LISTEN 2>/dev/null || true)
if [ -n "$PORT_PIDS" ]; then
  echo "$PORT_PIDS" | xargs kill -9 2>/dev/null || true
  echo "Fixed: Cleared port $PORT"
fi

# Kill orphaned Next.js processes from THIS project only
PROJECT_DIR=$(pwd)
for PID in $(pgrep -f "next dev" 2>/dev/null || true); do
  PID_CWD=$(lsof -p "$PID" 2>/dev/null | awk '/cwd/ {print $NF}')
  if [ "$PID_CWD" = "$PROJECT_DIR" ]; then
    kill -9 "$PID" 2>/dev/null || true
    echo "Fixed: Killed orphaned Next.js process (PID $PID)"
  fi
done
```

This avoids killing other projects' dev servers - only targets processes on the requested port or belonging to the current project directory.

### 3.2 Check Dependencies Freshness

```bash
if [ -f "package.json" ] && [ -d "node_modules" ]; then
  if [ "package.json" -nt "node_modules" ]; then
    # package.json is newer - deps may be stale
    echo "📦 Installing dependencies..."
    $PKG install
  fi
elif [ ! -d "node_modules" ]; then
  echo "📦 Installing dependencies..."
  $PKG install
fi
```

### 3.3 Smart Cache Detection

Only clear `.next` if it's actually corrupted or stale (preserves warm cache for faster startup):

```bash
if [ -d ".next" ]; then
  CORRUPTED=false
  # Missing BUILD_ID = incomplete or corrupted build
  [ ! -f ".next/BUILD_ID" ] && CORRUPTED=true
  # Trace directory older than 24 hours = stale
  [ -d ".next/trace" ] && find .next/trace -maxdepth 0 -mmin +1440 -print -quit 2>/dev/null | grep -q . && CORRUPTED=true
  # Cache dir exists but is empty = broken state
  [ -d ".next/cache" ] && [ -z "$(ls -A .next/cache 2>/dev/null)" ] && CORRUPTED=true

  if [ "$CORRUPTED" = true ]; then
    rm -rf .next
    echo "Fixed: Cleared corrupted .next cache"
  fi
fi
```

### 3.4 Memory Pressure Check

```bash
# macOS: check if system memory is critically low (< 1GB free)
FREE_MEM_MB=$(vm_stat 2>/dev/null | awk '/Pages free/ {free=$3} /Pages speculative/ {spec=$3} END {printf "%.0f", (free+spec)*4096/1048576}')
if [ -n "$FREE_MEM_MB" ] && [ "$FREE_MEM_MB" -lt 1024 ] 2>/dev/null; then
  echo "⚠️  Low memory (${FREE_MEM_MB}MB free) - killing stale Node processes"
  pkill -f "next-server" 2>/dev/null || true
  # Also clear .next to reduce memory footprint on startup
  rm -rf .next
fi
```

---

## Phase 4: Start Server with Auto-Recovery Loop

The server runs inside a restart loop that catches crashes and escalates recovery automatically. Intentional stops (Ctrl+C, exit 0) break out cleanly.

```bash
MAX_RESTARTS=4
RESTART_COUNT=0

while [ $RESTART_COUNT -lt $MAX_RESTARTS ]; do
  START_TS=$(date +%s)

  if [ $RESTART_COUNT -eq 0 ]; then
    # Level 1: Normal start
    PORT=$PORT $PKG run dev --turbo
    EXIT_CODE=$?
  elif [ $RESTART_COUNT -eq 1 ]; then
    # Level 2: Clear caches + restart
    rm -rf .next node_modules/.cache .swc
    find . -maxdepth 1 -name '*.tsbuildinfo' -delete 2>/dev/null || true
    PORT=$PORT $PKG run dev --turbo
    EXIT_CODE=$?
  elif [ $RESTART_COUNT -eq 2 ]; then
    # Level 3: Reinstall deps + restart
    rm -rf node_modules
    $PKG install
    PORT=$PORT $PKG run dev --turbo
    EXIT_CODE=$?
  else
    # Level 4: Nuclear - full clean
    pkill -f "next-server" 2>/dev/null || true
    rm -rf .next node_modules .swc
    find . -maxdepth 1 -name '*.tsbuildinfo' -delete 2>/dev/null || true
    $PKG install
    PORT=$PORT $PKG run dev --turbo
    EXIT_CODE=$?
  fi

  # Exit 0 = clean stop, 130 = Ctrl+C (SIGINT) - user stopped intentionally
  if [ $EXIT_CODE -eq 0 ] || [ $EXIT_CODE -eq 130 ]; then
    break
  fi

  RESTART_COUNT=$((RESTART_COUNT + 1))

  if [ $RESTART_COUNT -lt $MAX_RESTARTS ]; then
    echo "⚠️  Server crashed (exit $EXIT_CODE) - auto-recovering (level $((RESTART_COUNT + 1))/4)..."
    sleep 2
  fi
done

if [ $RESTART_COUNT -ge $MAX_RESTARTS ]; then
  echo "❌ Server failed after $MAX_RESTARTS recovery attempts."
  echo "   Last exit code: $EXIT_CODE"
  echo "   Try: Check for syntax errors or missing env vars."
fi
```

**Note:** `--turbo` enables Turbopack (Next.js 15+). Falls back automatically if not supported.

---

## Output Format

### Normal Start (nothing broken):

```
🚀 http://localhost:5888
```

That's it. One line. Server is running.

### Start After Fixing Something:

```
🚀 http://localhost:5888
   └─ Fixed: Cleared stale cache
```

### Start After Multiple Fixes:

```
🚀 http://localhost:5888
   ├─ Fixed: Killed process on port 5888
   ├─ Fixed: Installed dependencies
   └─ Fixed: Cleared corrupted .next cache
```

### Verbose Mode (-v):

```
═══════════════════════════════════════════════════════════════
🚀 DEV SERVER
═══════════════════════════════════════════════════════════════
   URL:        http://localhost:5888
   Package:    pnpm
   Turbopack:  Enabled

   Checks:
   ├─ Port 5888:     ✓ Clear
   ├─ Dependencies:  ✓ Up to date
   ├─ Cache:         ✓ Cleared
   └─ Disk space:    ✓ 42GB free

   Recovery:         Auto (4-level graduated restart loop)
═══════════════════════════════════════════════════════════════
```

### Minimal Mode (-m):

```
http://localhost:5888
```

No emoji, no fixes, just starts. Use when you know everything is fine.

---

## Flag Reference

| Flag | What It Does |
|------|--------------|
| (none) | Smart mode - auto-fixes everything silently |
| `-v` | Verbose - show all checks and monitoring |
| `-m` | Minimal - skip smart features, just start fast |

---

## Examples

```bash
/dev 5888           # 99% of the time, this is all you need
/dev 3000           # Different port
/dev                # Default port 3000
/dev 5888 -v        # "Show me what you're doing"
/dev 5888 -m        # "I know it's fine, just start"
```

---

## Why This Design

1. **No flags to memorize** - Smart behavior is the default
2. **Silent success** - Only shows output when there's something to report
3. **Graduated recovery** - Tries simple fixes first, escalates if needed
4. **Fast path preserved** - If nothing's wrong, startup is ~3-5s
5. **Escape hatches exist** - `-m` for minimal, `-v` for verbose

The goal: You type `/dev 5888` and forget about it. It either works, or it tells you why it can't.

---

## RELATED SKILLS

**Feeds from:**
- (none - /dev is typically the first command in a development session)

**Feeds into:**
- `/browse` - once the dev server is running, browse to visually inspect
- `/qatest` - dev server is the target for QA testing; start dev, then qatest
- `/redteam` - dev server is the attack surface; start dev, then redteam

**Pairs with:**
- `/smoketest` - run smoketest while dev server is running to catch obvious issues early
- `/browse` - dev + browse is the standard interactive development loop

**Auto-suggest after completion:**
When dev server is confirmed healthy (200 OK on the port), suggest: `/browse` for visual inspection, or `/qatest` for functional validation

---

## SITREP

> Reference: [SITREP Standard](~/.claude/standards/SITREP_FORMAT.md)

At the end of every /dev run, output:

**Skill:** /dev
**Status:** COMPLETE / PARTIAL / BLOCKED
**Server:** [running/failed]
**URL:** [http://localhost:PORT]
**PID:** [process ID]
**Build status:** [clean/warnings/errors]
**Errors fixed:** [count or "none"]
**Time to ready:** [duration]

---

## CLEANUP PROTOCOL

> Reference: [Resource Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md)

### Dev-Specific Cleanup

This skill uses **Start + Leave** dev server policy - the dev server is its primary output and should remain running.

Cleanup disclosure (in output when skill finishes):
1. **Dev server disclosure:** Always display: "Dev server running on port [PORT] (PID [PID]). Stop with: `kill [PID]` or Ctrl+C"
2. **Lockfile changes:** If Level 3/4 recovery deleted and regenerated the lockfile, warn: "Lockfile was regenerated - review `git diff` on lockfile before committing"
3. **Recovery disclosure:** If the restart loop triggered recovery, report which level was reached and what was cleaned

Note: `/dev` is exempt from the "Stop dev server" cleanup rule because its entire purpose is to START a dev server. The disclosure requirement still applies.

<!-- Claude Code Skill by Steel Motion LLC - https://steelmotion.dev -->
<!-- Part of the Claude Code Skills Collection -->
<!-- Powered by Claude models: Haiku (fast extraction), Sonnet (balanced reasoning), Opus (deep analysis) -->
<!-- License: MIT -->
