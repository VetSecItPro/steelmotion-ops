#!/usr/bin/env python3
"""Fold /gh-ship's pending history rows into the repo's history file. Stage 2.5, item 6.

    python3 ~/.claude/skills/gh-ship/history-fold.py [repo]          # fold, before the commit
    python3 ~/.claude/skills/gh-ship/history-fold.py --done [repo]   # after the commit succeeds

Stage 13 never commits: when `.gh-ship-history.json` is tracked, it appends its row to
`.git/gh-ship-history.pending.json` instead, and the NEXT run must fold those rows into its own
commit. That fold was prose until 2026-10-18 and was skipped on 04.novels PR #261 (scratchpad
#205), so it is a script with known-answer tests (`history-fold-test.py`) and a printed count.

Fold: appends pending rows in order, skips any already present, keeps the file's indentation,
writes atomically, and leaves the pending file in place. --done: removes the pending file only
when every pending row is in the history file as committed at HEAD.

Exit codes: 0 ok, 2 refused (damaged JSON: nothing changed), 3 --done refused (not committed yet).
"""
import json, os, subprocess, sys, tempfile

args = [a for a in sys.argv[1:] if not a.startswith("--")]
done = "--done" in sys.argv[1:]
repo = os.path.abspath(args[0] if args else ".")


def git(*a):
    r = subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True)
    return r.returncode, r.stdout


rc, gitdir = git("rev-parse", "--absolute-git-dir")
if rc != 0:
    print(f"gh-ship history fold: REFUSING, {repo} is not a git repo")
    sys.exit(2)
gitdir = gitdir.strip()
hist_path = os.path.join(repo, ".gh-ship-history.json")
pend_path = os.path.join(gitdir, "gh-ship-history.pending.json")


def load(path, what):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (ValueError, OSError) as e:
        print(f"gh-ship history fold: REFUSING, {what} is not valid JSON ({e}); nothing changed")
        sys.exit(2)


def runs_of(doc):
    return doc if isinstance(doc, list) else doc.setdefault("runs", [])


def key(row):
    return json.dumps(row, sort_keys=True, ensure_ascii=False)


if not os.path.exists(pend_path):
    print("gh-ship history fold: waiting rows: 0")
    sys.exit(0)

pending = load(pend_path, "the pending file")
pending = pending if isinstance(pending, list) else pending.get("runs", [])

if done:
    rc, committed = git("show", "HEAD:.gh-ship-history.json")
    try:
        have = {key(r) for r in runs_of(json.loads(committed))} if rc == 0 else set()
    except ValueError:
        have = set()
    missing = [r for r in pending if key(r) not in have]
    if missing:
        print(f"gh-ship history fold: REFUSING --done, {len(missing)} pending row(s) not committed at HEAD; pending kept")
        sys.exit(3)
    os.remove(pend_path)
    print(f"gh-ship history fold: done, {len(pending)} row(s) committed, pending file removed")
    sys.exit(0)

if os.path.exists(hist_path):
    with open(hist_path, encoding="utf-8") as f:
        raw = f.read()
    hist = load(hist_path, ".gh-ship-history.json")
else:
    raw, hist = "", {"schema_version": 2, "runs": []}

runs = runs_of(hist)
have = {key(r) for r in runs}
added = skipped = 0
for row in pending:
    if key(row) in have:
        skipped += 1
        continue
    runs.append(row)
    have.add(key(row))
    added += 1

indent = 2
for line in raw.splitlines()[1:]:
    stripped = line.lstrip(" ")
    if stripped and stripped != line:
        indent = len(line) - len(stripped)
        break
if raw and "\n" not in raw.strip():
    indent = None  # the file was compact; keep it compact

fd, tmp = tempfile.mkstemp(dir=repo, prefix=".gh-ship-history.", suffix=".tmp")
with os.fdopen(fd, "w", encoding="utf-8") as f:
    json.dump(hist, f, indent=indent, ensure_ascii=False)
    f.write("\n")
os.replace(tmp, hist_path)

rc, _ = git("ls-files", "--error-unmatch", ".gh-ship-history.json")
tracked = "tracked: stage .gh-ship-history.json in this commit" if rc == 0 else "untracked (history file is not in git)"
print(f"gh-ship history fold: waiting rows: {len(pending)}, folded: {added}, already present: {skipped}; {tracked}; "
      f"after the commit run with --done")
