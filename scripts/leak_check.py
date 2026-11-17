#!/usr/bin/env python3
"""Refuse to publish private detail: run over the tree before every commit and in CI.

Two lists of patterns:
- PUBLIC_PATTERNS, below: shapes that are never right in a public skill (a home folder path, a personal
  email, an internal ticket number, a cloud project id). These run everywhere, CI included.
- A local file, `.sync-rules.local.json` (gitignored, kept only on the maintainer's machine), whose
  "leak_terms" list names the private words themselves: people, client and product names, hosts. A
  list of private names cannot be committed without publishing them, so CI cannot run it; the sync
  script and the maintainer run it before every push.

Usage: python3 scripts/leak_check.py [root]     exit 0 clean, 1 on any hit (each printed as path:line).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PUBLIC_PATTERNS: dict[str, str] = {
    "home folder path": r"/Users/[A-Za-z0-9._-]+|/home/(?!runner\b|user\b|app\b|<)[a-z][a-z0-9_-]+/",
    "personal email": r"[A-Za-z0-9._%+-]+@(?:gmail|googlemail|icloud|me|yahoo|outlook|hotmail|proton(?:mail)?)\.[a-z.]+",
    "internal ticket number": r"\b(?:env|hub) #\d+",
    "Vercel project or team id": r"\b(?:prj|team)_[A-Za-z0-9]{16,}",
    "Supabase project ref": r"\b[a-z]{20}\.supabase\.co\b",
    "private network address": r"\b(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b",
    "Tailscale address": r"\b100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.\d{1,3}\.\d{1,3}\b",
}

SKIP_DIRS = {".git", "__pycache__", "node_modules"}
SKIP_FILES = {".sync-rules.local.json", "leak_check.py", "test_publishing.py"}  # the last two hold the patterns and planted cases
TEXT_SUFFIXES = {".md", ".py", ".sh", ".json", ".yml", ".yaml", ".txt", ""}
LOCAL_RULES = ".sync-rules.local.json"


def load_local_terms(root: Path) -> list[str]:
    path = root / LOCAL_RULES
    if not path.exists():
        return []
    return [t for t in json.loads(path.read_text()).get("leak_terms", []) if t.strip()]


def compile_patterns(local_terms: list[str]) -> list[tuple[str, re.Pattern[str]]]:
    out = [(name, re.compile(rx)) for name, rx in PUBLIC_PATTERNS.items()]
    out += [("private term", re.compile(r"(?<![A-Za-z0-9])" + re.escape(t) + r"(?![A-Za-z0-9])", re.IGNORECASE))
            for t in local_terms]
    return out


def files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name in SKIP_FILES or path.name == ".DS_Store":
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if path.suffix in TEXT_SUFFIXES:
            yield path


def scan(root: Path, patterns: list[tuple[str, re.Pattern[str]]]) -> list[str]:
    hits = []
    for path in files(root):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(lines, 1):
            for name, rx in patterns:
                if rx.search(line):
                    # Never print the matched text: for a private term that would print the secret word.
                    hits.append(f"{path.relative_to(root)}:{number}: {name}")
    return hits


def main(argv: list[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else ".").resolve()
    terms = load_local_terms(root)
    hits = scan(root, compile_patterns(terms))
    scanned = sum(1 for _ in files(root))
    source = f"{len(PUBLIC_PATTERNS)} public patterns + {len(terms)} local terms"
    if scanned == 0:
        print(f"leak check: no files under {root}; refusing to call that clean", file=sys.stderr)
        return 1
    for hit in hits:
        print(hit)
    print(f"leak check: {len(hits)} hits in {scanned} files ({source})")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
