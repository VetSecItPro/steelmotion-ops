#!/usr/bin/env python3
"""Known-answer tests for history-fold.py. Run: python3 ~/.claude/skills/gh-ship/history-fold-test.py

Added 2026-10-18 (scratchpad #205): the fold-in of pending history rows was prose in Stage 2.5 and
was skipped on 04.novels PR #261, leaving two rows waiting. The fold is now a script; these cases
pin its behavior.
"""
import json, os, subprocess, sys, tempfile

FOLD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history-fold.py")


def sh(*a, cwd):
    return subprocess.run(a, cwd=cwd, capture_output=True, text=True)


def repo(history, pending=None, indent=2, track=True):
    d = tempfile.mkdtemp(prefix="foldtest-")
    sh("git", "init", "-q", "-b", "main", cwd=d)
    for k, v in (("user.email", "t@t"), ("user.name", "t"), ("core.hooksPath", "/dev/null")):
        sh("git", "config", k, v, cwd=d)
    if history is not None:
        with open(os.path.join(d, ".gh-ship-history.json"), "w") as f:
            f.write(history if isinstance(history, str) else json.dumps(history, indent=indent) + "\n")
        if track:
            sh("git", "add", ".gh-ship-history.json", cwd=d)
    sh("git", "commit", "-q", "--allow-empty", "-m", "init", cwd=d)
    if pending is not None:
        with open(os.path.join(d, ".git", "gh-ship-history.pending.json"), "w") as f:
            json.dump(pending, f)
    return d


def fold(d, *args):
    p = subprocess.run([sys.executable, FOLD, *args, d], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def rows(d):
    h = json.load(open(os.path.join(d, ".gh-ship-history.json")))
    return h["runs"] if isinstance(h, dict) else h


def pending_exists(d):
    return os.path.exists(os.path.join(d, ".git", "gh-ship-history.pending.json"))


R1 = {"run_id": "2026-10-17T15:54:40-0500", "pr": 260, "outcome": "success"}
R2 = {"run_id": "2026-10-17T17:10:03-0500", "pr": 261, "outcome": "success"}
OLD = {"date": "2026-10-16T21:11:48-0500", "pr": 259, "outcome": "success"}

results = []


def check(name, ok):
    results.append(ok)
    print("PASS" if ok else "FAIL", name)


# 1. nothing waiting
d = repo({"runs": [OLD]})
rc, out = fold(d)
check("no pending file: exit 0, reports 0 waiting", rc == 0 and "gh-ship history fold" in out and "waiting rows: 0" in out and len(rows(d)) == 1)

# 2. two rows waiting, dict format: both appended, order kept, pending kept until --done
d = repo({"schema_version": 1, "runs": [OLD]}, [R1, R2])
rc, out = fold(d)
r = rows(d)
check("2 pending into dict file: folded 2, order kept", rc == 0 and "folded: 2" in out and [x.get("pr") for x in r] == [259, 260, 261])
check("pending kept until the commit (--done)", pending_exists(d))

# 3. bare-list history format
d = repo([OLD], [R1])
rc, out = fold(d)
check("bare-list file: folded 1", rc == 0 and "folded: 1" in out and [x.get("pr") for x in rows(d)] == [259, 260])

# 4. a row already present is not duplicated
d = repo({"runs": [OLD, R1]}, [R1, R2])
rc, out = fold(d)
check("duplicate row skipped", rc == 0 and "folded: 1" in out and "already present: 1" in out and len(rows(d)) == 3)

# 5. damaged history file: refuse, change nothing
d = repo('{"runs": [ broken', [R1])
before = open(os.path.join(d, ".gh-ship-history.json")).read()
rc, out = fold(d)
check("damaged history: non-zero exit, file and pending untouched",
      rc == 2 and "REFUSING" in out and open(os.path.join(d, ".gh-ship-history.json")).read() == before and pending_exists(d))

# 6. damaged pending file: refuse, change nothing
d = repo({"runs": [OLD]}, None)
with open(os.path.join(d, ".git", "gh-ship-history.pending.json"), "w") as f:
    f.write("[{oops")
rc, out = fold(d)
check("damaged pending: non-zero exit, history untouched", rc == 2 and "REFUSING" in out and len(rows(d)) == 1)

# 7. --done before the folded rows are committed: refuse, keep pending
d = repo({"runs": [OLD]}, [R1])
fold(d)
rc, out = fold(d, "--done")
check("--done before commit: refuses, pending kept", rc == 3 and "not committed" in out and pending_exists(d))

# 8. --done after the commit: removes pending
sh("git", "add", ".gh-ship-history.json", cwd=d)
sh("git", "commit", "-q", "-m", "fold", cwd=d)
rc, out = fold(d, "--done")
check("--done after commit: pending removed", rc == 0 and not pending_exists(d))

# 9. formatting kept: a 4-space-indented file stays 4-space-indented
d = repo({"runs": [OLD]}, [R1], indent=4)
fold(d)
txt = open(os.path.join(d, ".gh-ship-history.json")).read()
check("indent preserved (4 spaces)", '\n    "runs"' in txt and txt.endswith("\n") and len(rows(d)) == 2)

# 10. untracked history file: still folds, says so (Stage 13 normally appends in place there)
d = repo({"runs": [OLD]}, [R1], track=False)
rc, out = fold(d)
check("untracked history: folds and reports untracked", rc == 0 and "folded: 1" in out and "untracked" in out)

print(f"{sum(results)} of {len(results)} passed")
sys.exit(0 if all(results) else 1)
