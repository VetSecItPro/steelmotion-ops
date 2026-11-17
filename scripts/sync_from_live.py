#!/usr/bin/env python3
"""Rebuild the published skills from the maintainer's live Claude Code setup, cleaned for the public.

The live skills (~/.claude/skills, ~/.claude/commands, ~/.claude/standards) keep changing; a hand-copied
public set drifts within weeks. This script makes the copy repeatable:

1. Copies exactly what `scripts/sync-manifest.json` lists, skipping its `exclude` globs.
2. Cleans every text file: the generic rules below (internal ticket numbers, home paths), then the
   maintainer's private replacements from `.sync-rules.local.json` (gitignored: it names the private
   words, so it can never be committed).
3. Drops router rows for skills that are not published, and regenerates the README catalog.
4. Runs the leak check over the result and exits non-zero on any hit.

Usage: python3 scripts/sync_from_live.py [--source ~/.claude]
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import leak_check  # noqa: E402

DEST = ROOT / ".claude"
MANIFEST = ROOT / "scripts" / "sync-manifest.json"
README = ROOT / "README.md"
TEXT_SUFFIXES = {".md", ".py", ".sh", ".json", ".yml", ".yaml", ".txt"}

# Generic cleaning, safe to publish: internal ticket references and the maintainer's folder layout.
GENERIC_RULES: list[tuple[str, str]] = [
    (r"\s*\((?:env|hub) #\d+[^()]*\)", ""),                                      # a whole "(env #N, date)" aside
    (r"(?:,|;)?\s*(?:env|hub) #\d+(?:\.\d+)?(?:(?:,\s*| and | to )#\d+(?:\.\d+)?)*", ""),  # a trailing ", env #N" mention
    (r"~/vibecode-projects/", "~/projects/"),
    # Pointers into the maintainer's own task tooling, which is not published.
    (r",? and add the\s+project to `~/\.claude/task-list-projects\.json` so the Task List page shows it", ""),
    (r"See `~/\.claude/standards/SKILL_EVOLUTION\.md`[^\n]*\n", ""),
]


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text())


def load_local_rules(root: Path = ROOT) -> list[tuple[str, str]]:
    path = root / leak_check.LOCAL_RULES
    if not path.exists():
        return []
    return [(pattern, repl) for pattern, repl in json.loads(path.read_text()).get("replace", [])]


def clean(text: str, local_rules: list[tuple[str, str]]) -> str:
    for pattern, repl in GENERIC_RULES + local_rules:
        text = re.sub(pattern, repl, text)
    return text


def excluded(rel: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel, p) for p in patterns) or "__pycache__" in rel or rel.endswith(".DS_Store")


def router_rows_for(text: str, published: set[str]) -> str:
    """Keep only router table rows whose skill is published; other lines pass through."""
    out = []
    for line in text.splitlines(keepends=True):
        m = re.match(r"\| `/([a-z0-9-]+)` \|", line)
        if m and m.group(1) not in published:
            continue
        out.append(line)
    return "".join(out)


def description(path: Path, name: str) -> str:
    text = path.read_text(encoding="utf-8")
    m = re.search(r'^description:\s*"?(.*?)"?\s*$', text, re.MULTILINE)
    if not m:
        return ""
    desc = re.sub(rf"^/{re.escape(name)}\s*-\s*", "", m.group(1).strip().strip("'"))
    desc = re.split(r"\s+-\s+Trigger phrases|(?<=[a-z0-9)])\.\s", desc)[0].rstrip(".")
    return desc if len(desc) <= 220 else desc[:217].rsplit(" ", 1)[0] + "..."


def catalog(manifest: dict) -> str:
    rows = ["| Skill | What it does |", "|---|---|"]
    for name in sorted(manifest["skills"]):
        rows.append(f"| `/{name}` | {description(DEST / 'skills' / name / 'SKILL.md', name)} |")
    rows += ["", "**Commands** (`.claude/commands/`, single files):", "", "| Command | What it does |", "|---|---|"]
    for name in sorted(manifest["commands"]):
        rows.append(f"| `/{name}` | {description(DEST / 'commands' / f'{name}.md', name)} |")
    links = ", ".join(f"[{s}](.claude/standards/{s}.md)" for s in sorted(manifest["standards"]))
    rows += ["", f"**Shared standards** (`.claude/standards/`), which the skills point at instead of repeating them: {links}."]
    return "\n".join(rows) + "\n"


def write_readme_catalog(manifest: dict) -> None:
    text = README.read_text(encoding="utf-8")
    start, end = "<!-- catalog:start -->\n", "<!-- catalog:end -->"
    if start not in text or end not in text:
        raise SystemExit("README.md has no catalog markers")
    head, rest = text.split(start, 1)
    _, tail = rest.split(end, 1)
    README.write_text(head + start + catalog(manifest) + end + tail, encoding="utf-8")


def copy_tree(src: Path, dst: Path, rel_base: str, manifest: dict, rules: list[tuple[str, str]], published: set[str]) -> int:
    count = 0
    paths = [src] if src.is_file() else sorted(p for p in src.rglob("*") if p.is_file())
    for path in paths:
        rel = f"{rel_base}/{path.relative_to(src)}" if src.is_dir() else rel_base
        if excluded(rel, manifest.get("exclude", [])):
            continue
        target = DEST / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix in TEXT_SUFFIXES:
            text = clean(path.read_text(encoding="utf-8"), rules)
            if rel == "standards/SKILL_ROUTER.md":
                text = router_rows_for(text, published)
            target.write_text(text, encoding="utf-8")
        else:
            shutil.copy2(path, target)
        if path.stat().st_mode & 0o111:
            target.chmod(target.stat().st_mode | 0o111)
        count += 1
    return count


def sync(source: Path) -> int:
    manifest = load_manifest()
    rules = load_local_rules()
    missing = [f"skills/{s}" for s in manifest["skills"] if not (source / "skills" / s / "SKILL.md").exists()]
    missing += [f"commands/{c}.md" for c in manifest["commands"] if not (source / "commands" / f"{c}.md").exists()]
    missing += [f"standards/{s}.md" for s in manifest["standards"] if not (source / "standards" / f"{s}.md").exists()]
    missing += [t for t in manifest.get("tools", []) if not (source / t).exists()]
    if missing:
        raise SystemExit("not in the live setup: " + ", ".join(missing))
    for sub in ("skills", "commands", "standards", "templates"):
        shutil.rmtree(DEST / sub, ignore_errors=True)
    for tool in manifest.get("tools", []):
        (DEST / tool).unlink(missing_ok=True)
    published = set(manifest["skills"]) | set(manifest["commands"])
    n = sum(copy_tree(source / "skills" / s, DEST / "skills" / s, f"skills/{s}", manifest, rules, published) for s in manifest["skills"])
    n += sum(copy_tree(source / "commands" / f"{c}.md", DEST, f"commands/{c}.md", manifest, rules, published) for c in manifest["commands"])
    n += sum(copy_tree(source / "standards" / f"{s}.md", DEST, f"standards/{s}.md", manifest, rules, published) for s in manifest["standards"])
    n += sum(copy_tree(source / t, DEST, t, manifest, rules, published) for t in manifest.get("tools", []))
    # The generator writes the router beside itself, so this rebuilds the PUBLISHED router from the published
    # skills, with the right counts, instead of filtering the maintainer's.
    if (DEST / "generate-skill-router.py").exists():
        subprocess.run([sys.executable, str(DEST / "generate-skill-router.py")], check=True, capture_output=True)
    write_readme_catalog(manifest)
    print(f"synced {n} files: {len(manifest['skills'])} skills, {len(manifest['commands'])} commands, "
          f"{len(manifest['standards'])} standards ({len(rules)} local rules)")
    return leak_check.main(["leak_check", str(ROOT)])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", type=Path, default=Path.home() / ".claude")
    sys.exit(sync(parser.parse_args().source.expanduser()))
