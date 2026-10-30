#!/usr/bin/env python3
"""Mechanical staleness detector for a repo's documentation register.

Reads docs/doc-register.json and checks, without any language model, whether the
claims each document depends on still hold. Prose cannot be checked; anchors can.

Exit codes are the contract the CI gate depends on:
    0  clean
    1  BROKEN  - an anchor is proven gone. Fails the build.
    2  SUSPECT - a doc's anchors were touched, or a doc is unregistered.
                 Warns only. A gate that blocks on suspicion trains people to
                 disable it, and then there is no gate at all.

No third-party dependencies on purpose: this runs inside a merge gate, where a
network fetch or a vendored parser is a worse trade than a plainer file format.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

VERSION = "2.0.1"
REGISTER_RELPATH = "docs/doc-register.json"
REGISTER_BASENAME = "doc-register.json"
REGISTER_ROOT_GLOBS = ("*DOC-REGISTER*.json", "*doc-register*.json")

# The stamp is the operator-visible half of every repair: a document this skill
# touched says so, in Central time, in a form a machine can read back. Invisible in
# rendered markdown on purpose - a doc that has to carry tooling exhaust in its own
# prose gets the exhaust deleted by the next person who reads it as clutter.
STAMP_RE = re.compile(
    r"<!--\s*docs-sync:\s*reconciled\s+(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})\s+CT"
    r"\s*(?:\|[^>]*?)?-->")
STAMP_TEMPLATE = ("<!-- docs-sync: reconciled {date} {time} CT | mode: {mode} "
                  "| against: {sha} -->")

# How a document absorbs new work. Recorded once, per document, because the choice
# is a property of what the document IS and cannot be re-derived per edit without
# getting it wrong half the time.
#
#   supersede  live claim. New truth REPLACES the old text in place. Growth is a
#              defect: this is the mode that stops a status document becoming a
#              20,000-word pile of appends nobody reads to the bottom of.
#   hybrid     live, with named append-only sections (a backlog: Open rows flip
#              status in place, the Done section only ever gains rows).
#   append     a record. New entries only. Existing entries are never edited,
#              because their whole value is stating what was true on their date.
#   frozen     checked, never written. Findings go to the SITREP as proposals.
UPDATE_MODES = {"supersede", "hybrid", "append", "frozen"}
WRITABLE_LIVE_MODES = {"supersede", "hybrid"}

BROKEN, SUSPECT, INFO = "broken", "suspect", "info"

# Anchors extracted from prose by pattern reproduce every false positive a naive grep
# makes, then inherit them into a register whose selling point is arithmetic certainty.
# A harvested anchor is a guess wearing a schema. Documents quote counter-examples
# ("not `audit-pages.py` but `canvas-audit-pages.py`") and record old names in rename
# histories; both are SUPPOSED not to exist. So harvested anchors can never fail a
# build - the cost asymmetry is brutal, because a false BROKEN in a merge gate invites
# somebody to edit a governing document until CI stops complaining.
CURATED = "curated"

# Fields this checker actually acts on. Anything a register declares outside these
# is inert, and an inert field that reads like a guard is worse than no field at all
# - it gets believed. So every unenforced declaration announces itself on every run.
ENFORCED_DOC_FIELDS = {"path", "owns", "anchors", "verified_at", "verified_sha", "provenance",
                       "update_mode", "append_sections", "max_lines"}
ENFORCED_ANCHOR_KINDS = {"paths", "symbols", "commands", "config", "counts"}
CONSUMED_BY_SKILL = {"review"}   # acted on by /docs-sync repair, not by this gate

# Directories never searched for symbols or config keys. Vendored and generated
# trees would produce matches that prove nothing about this repo's own source.
SKIP_DIRS = {
    ".git", "node_modules", ".next", "dist", "build", "target", "vendor",
    "__pycache__", ".venv", "venv", ".mypy_cache", ".pytest_cache",
    "coverage", ".turbo", ".cache",
}

# Records describe the past on purpose. Freshening them destroys the record, so
# they are never registered and never reported as orphans.
DEFAULT_IGNORE = [
    "CHANGELOG.md", "**/CHANGELOG.md",
    "**/adr/**", "**/ADR/**",
    "**/*lessons-learned*.md", "**/*LESSONS*.md",
    "**/worklog/**", "**/*worklog*.md",
    "**/node_modules/**", "**/.git/**",
]


class Finding:
    __slots__ = ("severity", "doc", "kind", "detail")

    def __init__(self, severity: str, doc: str, kind: str, detail: str) -> None:
        self.severity, self.doc, self.kind, self.detail = severity, doc, kind, detail

    def as_dict(self) -> dict:
        return {"severity": self.severity, "doc": self.doc,
                "kind": self.kind, "detail": self.detail}


# --------------------------------------------------------------------------- #
# repo plumbing
# --------------------------------------------------------------------------- #

def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=60)
        return p.returncode, p.stdout
    except (OSError, subprocess.SubprocessError):
        return 127, ""


def has_git(root: Path) -> bool:
    code, _ = run(["git", "rev-parse", "--is-inside-work-tree"], root)
    return code == 0


_TRACKED_CACHE: dict = {}


def tracked_files(root: Path) -> list[Path] | None:
    """Files git knows about. Returns None outside a git repo.

    Untracked scratch is NOT evidence. A checker log, a build artefact or an editor
    backup sitting in the working tree can contain the very symbol or config key an
    anchor names, and satisfy it - measured: a scratch file holding this tool's own
    output made a genuinely stale doc report clean on that anchor. That is a FALSE
    NEGATIVE, the dangerous direction, and it does not reproduce in CI where the
    checkout is clean, so it would only ever mislead locally.
    """
    key = str(root)
    if key in _TRACKED_CACHE:
        return _TRACKED_CACHE[key]
    code, out = run(["git", "ls-files", "-z"], root)
    result = None
    if code == 0:
        result = [root / n for n in out.split("\0") if n]
    _TRACKED_CACHE[key] = result
    return result


def source_files(root: Path, register_path: Path | None = None) -> list[Path]:
    """Every file a symbol or config key could legitimately live in.

    Markdown is excluded deliberately: a symbol that appears only in the docs is
    exactly the stale reference this tool exists to catch, so counting a doc as
    evidence for itself would make the check circular.
    """
    tracked = tracked_files(root)
    if tracked is not None:
        return [f for f in tracked
                if not f.name.endswith((".md", ".mdx", ".lock", ".png", ".jpg", ".pdf", ".zip"))
                and (register_path is None or f.resolve() != register_path)]
    out: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".git")]
        for fn in filenames:
            if fn.endswith((".md", ".mdx", ".lock", ".png", ".jpg", ".pdf", ".zip")):
                continue
            # The register names every symbol it tracks, so searching it would make
            # every anchor prove itself. Excluded by resolved PATH rather than by a
            # fixed name: a repo is free to call it anything, and hardcoding the name
            # reopened this hole the moment one did.
            fp = Path(dirpath) / fn
            if register_path is not None and fp.resolve() == register_path:
                continue
            out.append(fp)
    return out


def grep_symbol(root: Path, symbol: str, use_git: bool, cache: dict,
                register_path: Path | None = None) -> bool:
    """True if the symbol appears as a whole word in non-markdown source."""
    if symbol in cache:
        return cache[symbol]
    found = False
    if use_git:
        excl = [":(exclude)*.md", ":(exclude)*.mdx"]
        if register_path is not None:
            try:
                excl.append(f":(exclude){register_path.relative_to(root).as_posix()}")
            except ValueError:
                pass
        code, _ = run(["git", "grep", "-w", "-l", "-e", symbol, "--", *excl], root)
        found = code == 0
    if not found:
        pat = re.compile(r"\b" + re.escape(symbol) + r"\b")
        for f in source_files(root, register_path):
            try:
                if pat.search(f.read_text(encoding="utf-8", errors="ignore")):
                    found = True
                    break
            except OSError:
                continue
    cache[symbol] = found
    return found


def expand(root: Path, pattern: str) -> list[Path]:
    """Resolve an anchor path, which may be a plain path, a glob, or a dir."""
    dirs_only = pattern.endswith("/")
    pat = pattern.rstrip("/")
    if any(ch in pat for ch in "*?["):
        hits = sorted(root.glob(pat))
    else:
        p = root / pat
        hits = [p] if p.exists() else []
    return [h for h in hits if h.is_dir()] if dirs_only else hits


# --------------------------------------------------------------------------- #
# detectors
# --------------------------------------------------------------------------- #

def find_by_basename(root: Path, name: str) -> list[str]:
    """Every place this filename lives. Counted in full, never truncated early:
    stopping at the first few and reporting them as though they were all of them is
    the same defect as reading a count without its denominator."""
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        if name in filenames:
            hits.append((Path(dirpath) / name).relative_to(root).as_posix())
    return sorted(hits)


def check_paths(root: Path, doc: str, anchors: dict, root_ignored: set) -> list[Finding]:
    """No search path, deliberately. A resolver with fallbacks is silent variance: a
    neighbouring checker turned nine live scripts into twelve dead citations by losing
    a `scripts/` fallback in a rewrite, over a corpus that never changed. An anchor
    stores the RESOLVED repo-relative path, and ambiguity is surfaced, never guessed.
    """
    out = []
    for pattern in anchors.get("paths", []):
        if expand(root, pattern):
            continue
        if "/" not in pattern.rstrip("/"):
            elsewhere = find_by_basename(root, pattern.rstrip("/"))
            if len(elsewhere) == 1:
                out.append(Finding(SUSPECT, doc, "unresolved-basename",
                                   f"{pattern} is a bare filename with no file at the repo root. "
                                   f"It resolves to exactly one path: {elsewhere[0]}. Store that "
                                   f"resolved path in the register rather than the string the prose "
                                   f"used - this checker has no search path on purpose."))
                continue
            if len(elsewhere) > 1:
                shown = ", ".join(elsewhere[:8])
                more = f" (+{len(elsewhere) - 8} more)" if len(elsewhere) > 8 else ""
                out.append(Finding(SUSPECT, doc, "ambiguous-basename",
                                   f"{pattern} is a bare filename matching {len(elsewhere)} files: "
                                   f"{shown}{more}. THE CURATOR MUST CHOOSE - this checker will not "
                                   f"pick one. A register carrying a confidently wrong resolved path "
                                   f"is worse than a bare string, because it looks settled and diffs "
                                   f"clean forever."))
                continue
        # A gitignored artifact is absent in every clean checkout on purpose. Failing
        # the build on it would make the gate red on every run for a correct absence.
        if pattern.rstrip("/") in root_ignored:
            out.append(Finding(INFO, doc, "path-generated",
                               f"{pattern} is absent but gitignored - generated artifact, not a defect"))
        else:
            out.append(Finding(BROKEN, doc, "path", f"{pattern} does not exist"))
    return out


def check_symbols(root: Path, doc: str, anchors: dict, use_git: bool, cache: dict,
                  reg: Path | None = None) -> list[Finding]:
    out = []
    for sym in anchors.get("symbols", []):
        if not grep_symbol(root, sym, use_git, cache, reg):
            out.append(Finding(BROKEN, doc, "symbol", f"{sym} is not in any source file"))
    return out


def check_commands(root: Path, doc: str, anchors: dict) -> list[Finding]:
    """Only three forms are resolvable without executing anything.

    Anything else is reported as unresolvable at SUSPECT, never BROKEN: a command
    the checker cannot model is a gap in the checker, not proof of a stale doc,
    and failing a build on that would be a lie.
    """
    out = []
    for cmd in anchors.get("commands", []):
        tokens = cmd.split()
        if not tokens:
            continue
        m = re.match(r"^(?:npm|pnpm|yarn|bun)\s+(?:run\s+)?([\w:.-]+)", cmd)
        if m:
            pkg = root / "package.json"
            script = m.group(1)
            if not pkg.exists():
                out.append(Finding(BROKEN, doc, "command", f"{cmd!r} but there is no package.json"))
            else:
                try:
                    scripts = json.loads(pkg.read_text(encoding="utf-8")).get("scripts", {})
                except (OSError, json.JSONDecodeError):
                    scripts = {}
                if script not in scripts:
                    out.append(Finding(BROKEN, doc, "command",
                                       f"{cmd!r} but package.json has no script {script!r}"))
            continue
        if tokens[0] == "make":
            mk = next((root / n for n in ("Makefile", "makefile", "GNUmakefile")
                       if (root / n).exists()), None)
            target = tokens[1] if len(tokens) > 1 else ""
            if mk is None:
                out.append(Finding(BROKEN, doc, "command", f"{cmd!r} but there is no Makefile"))
            elif target and not re.search(rf"^{re.escape(target)}\s*:", mk.read_text(
                    encoding="utf-8", errors="ignore"), re.M):
                out.append(Finding(BROKEN, doc, "command",
                                   f"{cmd!r} but the Makefile has no target {target!r}"))
            continue
        script_tok = next((t for t in tokens if "/" in t or t.endswith((".py", ".sh", ".ts", ".js", ".mjs"))), None)
        if script_tok:
            if not (root / script_tok).exists():
                out.append(Finding(BROKEN, doc, "command", f"{cmd!r} but {script_tok} does not exist"))
            continue
        out.append(Finding(SUSPECT, doc, "command", f"{cmd!r} is not a form this checker can resolve"))
    return out


def check_config(root: Path, doc: str, anchors: dict, use_git: bool, cache: dict,
                 reg: Path | None = None) -> list[Finding]:
    out = []
    for key in anchors.get("config", []):
        if not grep_symbol(root, key, use_git, cache, reg):
            out.append(Finding(BROKEN, doc, "config", f"{key} is not defined or referenced anywhere"))
    return out


def count_matches(root: Path, c: dict) -> int:
    """Count what the anchor SAYS it counts, never what a glob happens to match.

    A directory count and a module count are different numbers, and a checker that
    conflates them produces a confident wrong verdict inside a merge gate - which
    is the exact failure the count detector exists to catch.
    """
    kind = c.get("kind")
    if kind == "observation":
        kind = c.get("counts_as", "dir")
    hits = expand(root, c["source"])
    if kind == "file":
        return len([h for h in hits if h.is_file()])
    if kind == "dir":
        return len([h for h in hits if h.is_dir()])
    if kind == "dir_with":
        pattern = c.get("contains", "*")
        return len([h for h in hits if h.is_dir() and any(h.glob(pattern))])
    return len(hits)


def check_counts(root: Path, doc: str, anchors: dict) -> list[Finding]:
    """The class nobody builds and the one that has already bitten this estate:
    a doc asserting 25 Terraform modules while the repo holds 35."""
    out = []
    for c in anchors.get("counts", []):
        source, expect = c.get("source"), c.get("expect")
        if source is None or expect is None:
            continue
        if c.get("kind") == "observation":
            actual = count_matches(root, c)
            if actual != expect:
                out.append(Finding(INFO, doc, "observation-drifted",
                                   f"{c.get('claim', source)!r} was a dated measurement; "
                                   f"it now reads {actual}. Not a defect - do not freshen it."))
            continue
        if c.get("kind") not in ("file", "dir", "dir_with"):
            out.append(Finding(SUSPECT, doc, "count-unqualified",
                               f"count on {source!r} does not say what it counts "
                               f"(kind: file | dir | dir_with) - not gated until it does"))
            continue
        actual = count_matches(root, c)
        if actual != expect:
            claim = c.get("claim", f"{expect} of {source}")
            detail = f"claims {claim!r} but {c['kind']} count of {source}"
            if c.get("kind") == "dir_with":
                detail += f" containing {c.get('contains', '*')!r}"
            out.append(Finding(BROKEN, doc, "count", f"{detail} is {actual}"))
    return out


def now_ct() -> datetime:
    return datetime.now(ZoneInfo("America/Chicago"))


def check_update_mode(root: Path, doc: str, entry: dict) -> list[Finding]:
    """The supersede-versus-append boundary, enforced rather than hoped for.

    Operator directive 2026-09-10: a live document gets the new truth written OVER
    the old one, and a record only ever gains entries. Both halves fail silently
    without a declaration - appending to a live doc looks like diligence for about
    six months, and rewriting a record looks like tidying right up until the moment
    somebody needs to know what was true in March.
    """
    out: list[Finding] = []
    mode = entry.get("update_mode")
    curated = entry.get("provenance") == CURATED
    if mode is None:
        if curated:
            out.append(Finding(SUSPECT, doc, "update-mode-undeclared",
                               "no update_mode, so nothing says whether new work REPLACES this "
                               "document's claims or is APPENDED to them. Declare one of: "
                               + " | ".join(sorted(UPDATE_MODES))))
        return out
    if mode not in UPDATE_MODES:
        out.append(Finding(BROKEN, doc, "update-mode-invalid",
                           f"update_mode {mode!r} is not a mode this gate knows "
                           f"({' | '.join(sorted(UPDATE_MODES))}). A mode nothing enforces reads "
                           f"as a protection and is not one."))
        return out

    sections = entry.get("append_sections")
    if mode == "hybrid":
        if not sections:
            out.append(Finding(BROKEN, doc, "append-sections-missing",
                               "update_mode: hybrid with no append_sections. Hybrid means SOME "
                               "sections are append-only; unnamed, it is an unbounded licence to "
                               "append to a live document, which is the failure the mode exists "
                               "to prevent."))
        else:
            try:
                text = (root / doc).read_text(encoding="utf-8", errors="ignore")
            except OSError:
                text = ""
            headings = {ln.lstrip("#").strip().lower()
                        for ln in text.splitlines() if ln.startswith("#")}
            for want in sections:
                if want.lstrip("#").strip().lower() not in headings:
                    out.append(Finding(BROKEN, doc, "append-section-missing",
                                       f"append_sections names {want!r} but the document has no "
                                       f"such heading. A section guard pointed at a heading that "
                                       f"moved protects nothing and reports green."))
    elif sections:
        out.append(Finding(INFO, doc, "declared-not-enforced",
                           f"append_sections is set but update_mode is {mode!r}, and this gate "
                           f"acts on append_sections only for hybrid. It is inert here."))
    return out


def check_stamp(root: Path, doc: str, entry: dict) -> list[Finding]:
    """A document this skill reconciled says so, with the date and time.

    The stamp and the register are two independent records of the same event, which
    is the point: when they disagree, one of them is wrong and the run says so,
    rather than the register asserting a reconciliation nothing in the document
    corroborates.
    """
    out: list[Finding] = []
    mode = entry.get("update_mode")
    if mode not in WRITABLE_LIVE_MODES:
        return out
    try:
        text = (root / doc).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return out
    matches = STAMP_RE.findall(text)
    sha = entry.get("verified_sha")
    reconciled = bool(sha) and sha != "none"
    if not matches:
        if reconciled:
            out.append(Finding(BROKEN, doc, "stamp-missing",
                               f"the register claims this was reconciled at {str(sha)[:7]} but the "
                               f"document carries no docs-sync stamp. Register and document "
                               f"disagree about whether the work happened."))
        else:
            out.append(Finding(SUSPECT, doc, "stamp-missing",
                               "no docs-sync stamp yet - never reconciled. It gains one the first "
                               "time this skill writes to it."))
        return out
    if len(matches) > 1:
        out.append(Finding(SUSPECT, doc, "stamp-duplicated",
                           f"{len(matches)} docs-sync stamps in one document. The newest is the "
                           f"only one anybody reads; the rest are stale claims wearing the same "
                           f"format. Keep one."))
    date_s, time_s = matches[-1]
    try:
        stamped = datetime.strptime(f"{date_s} {time_s}", "%Y-%m-%d %H:%M").replace(
            tzinfo=ZoneInfo("America/Chicago"))
    except ValueError:
        out.append(Finding(BROKEN, doc, "stamp-malformed",
                           f"stamp reads {date_s!r} {time_s!r}, which is not a real date and time"))
        return out
    if stamped > now_ct():
        out.append(Finding(BROKEN, doc, "stamp-future",
                           f"stamp is dated {date_s} {time_s} CT, which is in the future. A stamp "
                           f"nobody can have written is worse than none: it dates the document "
                           f"ahead of every record that describes it."))
    verified_at = entry.get("verified_at")
    if verified_at:
        try:
            va = datetime.strptime(verified_at, "%Y-%m-%d").replace(
                tzinfo=ZoneInfo("America/Chicago"))
            if stamped.date() < va.date():
                out.append(Finding(SUSPECT, doc, "stamp-behind",
                                   f"register says verified {verified_at}, document stamp says "
                                   f"{date_s}. The register was stamped without the document "
                                   f"being written, or the stamp was lost in an edit."))
        except ValueError:
            out.append(Finding(BROKEN, doc, "verified-at-malformed",
                               f"verified_at {verified_at!r} is not YYYY-MM-DD"))
    return out


def check_bloat(root: Path, doc: str, entry: dict) -> list[Finding]:
    """A live document that only ever grows has become an append pile.

    SUSPECT and never BROKEN, deliberately. Length is a judgment call, and a gate
    that fails a build because a document got long is a gate somebody deletes -
    at which point the genuinely broken anchors stop being reported too.
    """
    cap = entry.get("max_lines")
    if cap is None:
        return []
    mode = entry.get("update_mode")
    if mode is not None and mode not in WRITABLE_LIVE_MODES:
        return [Finding(INFO, doc, "declared-not-enforced",
                        f"max_lines is set but update_mode is {mode!r}; a record is SUPPOSED to "
                        f"grow, so this gate does not act on it here.")]
    if not isinstance(cap, int) or cap <= 0:
        return [Finding(BROKEN, doc, "max-lines-invalid",
                        f"max_lines {cap!r} is not a positive integer")]
    try:
        lines = (root / doc).read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return []
    actual, scope = live_line_count(lines, entry.get("append_sections") or [])
    if actual > cap:
        return [Finding(SUSPECT, doc, "bloat",
                        f"{actual} {scope} against a declared ceiling of {cap} "
                        f"({actual - cap} over). A live document at this length is usually one that "
                        f"got appended to instead. Replace superseded claims rather than raising "
                        f"the ceiling.")]
    return []


def live_line_count(lines: list[str], append_sections: list[str]) -> tuple[int, str]:
    """Lines in the LIVE half of a document.

    A hybrid document's append-only sections grow by design, so a whole-file ceiling
    on one is a guard guaranteed to fire for a correct reason and then be raised
    reflexively until it means nothing. The ceiling asks a narrower question: is the
    half that is supposed to be REPLACED still readable in one sitting.
    """
    if not append_sections:
        return len(lines), "lines"
    wanted = {s.lstrip("#").strip().lower() for s in append_sections}
    live, skipping, skip_depth = 0, False, 0
    for ln in lines:
        if ln.startswith("#"):
            depth = len(ln) - len(ln.lstrip("#"))
            title = ln.lstrip("#").strip().lower()
            if skipping and depth <= skip_depth:
                skipping = False
            if title in wanted:
                skipping, skip_depth = True, depth
                continue
        if not skipping:
            live += 1
    return live, "live lines (append-only sections excluded)"


# --------------------------------------------------------------------------- #
# whole-register checks
# --------------------------------------------------------------------------- #

def discover_register(root: Path, explicit: str | None) -> tuple[Path | None, str | None]:
    """Find the register. Two candidates is an ERROR, never a pick.

    `REGISTER_BASENAME` sat declared and unreferenced through v1 while
    `reference.md` promised a two-step search order, so a repo following the
    documented root-level naming had to pass --register on every invocation. That
    is the `declared-not-enforced` defect this tool exists to report, living inside
    the tool. Fixed here, and deliberately WITHOUT a search path for anchors: this
    resolves the register's own location, which the reference documents, and
    nothing else.
    """
    if explicit:
        return Path(explicit), None
    primary = root / REGISTER_RELPATH
    if primary.exists():
        return primary, None
    seen: list[Path] = []
    for pat in REGISTER_ROOT_GLOBS:
        for hit in sorted(root.glob(pat)):
            if hit.is_file() and hit not in seen:
                seen.append(hit)
    if len(seen) == 1:
        return seen[0], None
    if len(seen) > 1:
        names = ", ".join(h.name for h in seen)
        return None, (f"{len(seen)} candidate registers at the repo root: {names}. "
                      f"THE OPERATOR MUST CHOOSE - pass --register. Picking one would be "
                      f"a confident guess about which document set governs this repo.")
    return primary, None


def working_tree_changes(root: Path) -> set[str]:
    """Files changed but not committed.

    Load-bearing for the way this skill is actually used: the operator does the
    work, then asks for the docs to be reconciled, THEN commits. A touched-anchor
    detector that only reads `verified_sha..HEAD` is blind at exactly that moment
    and reports a clean run over a working tree full of changes.
    """
    code, out = run(["git", "status", "--porcelain", "-z"], root)
    if code != 0:
        return set()
    changed: set[str] = set()
    fields = [f for f in out.split("\0") if f]
    i = 0
    while i < len(fields):
        entry = fields[i]
        if len(entry) < 4:
            i += 1
            continue
        status, name = entry[:2], entry[3:]
        changed.add(name)
        # A rename emits the ORIGINAL path as the next field. Consuming it as a
        # status entry would parse a bare filename as though its first three
        # characters were a status code, silently dropping a real change.
        if "R" in status or "C" in status:
            if i + 1 < len(fields):
                changed.add(fields[i + 1])
                i += 1
        i += 1
    return changed


def changed_since(root: Path, sha: str, doc: str | None = None) -> set[str] | None:
    """Anchor-relevant changes since `sha`, EXCLUDING commits that also changed `doc`.

    Walks commit by commit rather than diffing two endpoints, and that is the whole
    point. A commit that changed an anchor AND the document together is a
    reconciliation: the document was written with knowledge of that change, so it is
    not evidence of staleness. Only an anchor moving in a commit that left the
    document alone means the document has been left behind.

    WHY THIS IS NOT A LOOSENING. A two-endpoint `git diff sha..HEAD` cannot tell the
    two cases apart, and the difference is not cosmetic: a stamp written on a feature
    branch can never name the squash-merge sha, because that sha does not exist when
    the stamp is written. The squash then lands the document and its anchors in ONE
    commit, so the endpoint diff reports every squash-merged documentation change as
    stale against its own reconciliation. Permanently, with no sequence of commits
    that clears it, because the commit that would clear it recreates the condition.

    That was measured in 17.scratchpad on 2026-09-12 and filed as backlog #144. The
    danger was never a false failure - the finding is SUSPECT and does not gate - it
    is that a checker which is always yellow is a checker people stop reading, which
    costs the real findings sitting next to it.

    `--name-only` prints nothing for a merge commit, which is correct here: a true
    merge introduces no changes of its own, and the commits it brings in are already
    in the range and are judged individually.
    """
    code, out = run(["git", "log", "--format=%x01%H", "--name-only", f"{sha}..HEAD"], root)
    if code != 0:
        return None
    changed: set[str] = set()
    for block in out.split("\x01"):
        lines = [ln.strip() for ln in block.splitlines()]
        files = {ln for ln in lines[1:] if ln}
        if doc is not None and doc in files:
            continue
        changed |= files
    return changed


def _matching(changed: set[str], patterns: list[str]) -> set[str]:
    return {f for f in changed
            for p in patterns
            if f == p.rstrip("/") or f.startswith(p.rstrip("/") + "/")
            or fnmatch.fnmatch(f, p)}


def check_suspect(root: Path, entry: dict, use_git: bool) -> list[Finding]:
    doc = entry["path"]
    sha = entry.get("verified_sha")
    patterns = entry.get("anchors", {}).get("paths", [])

    # "No verified_sha recorded" is a fact about the REGISTER and holds outside a git
    # repo too. An earlier draft of this function tested use_git first and swallowed
    # it; the suite caught that, which is the entire argument for the suite.
    if not sha or sha == "none":
        out = [Finding(SUSPECT, doc, "unverified", "no verified_sha recorded")]
        if use_git:
            uncommitted = sorted(_matching(working_tree_changes(root), patterns))
            if uncommitted:
                out.append(Finding(SUSPECT, doc, "touched",
                                   f"anchors changed in the WORKING TREE (uncommitted): "
                                   f"{_shown(uncommitted)}"))
        return out
    if not use_git:
        return []
    uncommitted = sorted(_matching(working_tree_changes(root), patterns))
    changed = changed_since(root, sha, doc)
    if changed is None:
        return [Finding(SUSPECT, doc, "unverified", f"verified_sha {sha} is not in this history")]
    committed = sorted(_matching(changed, patterns))
    out = []
    if committed:
        out.append(Finding(SUSPECT, doc, "touched",
                           f"anchors changed since {sha[:7]}: {_shown(committed)}"))
    # Reported separately rather than merged into one set. "Changed since a sha" and
    # "changed and not yet committed" call for different repairs, and a combined list
    # hides which of the two a given path came from.
    if uncommitted:
        out.append(Finding(SUSPECT, doc, "touched",
                           f"anchors changed in the WORKING TREE (uncommitted): "
                           f"{_shown(uncommitted)}"))
    return out


def _shown(hits: list[str]) -> str:
    return ", ".join(hits[:3]) + (f" (+{len(hits) - 3} more)" if len(hits) > 3 else "")


def gitignored(root: Path, rels: list[str], use_git: bool) -> set[str]:
    """Ask git, rather than guess. Skill output lives in gitignored .*-reports/
    directories by house rule; demanding those be registered is pure noise, and a
    checker that emits noise is a checker somebody switches off."""
    if not use_git or not rels:
        return set()
    try:
        p = subprocess.run(["git", "check-ignore", "--stdin"], cwd=str(root),
                           input="\n".join(rels), capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return set()
    return {ln.strip() for ln in p.stdout.splitlines() if ln.strip()}


def discover_docs(root: Path, registered: set[str], ignore: list[str],
                  doc_roots: list[str], use_git: bool) -> list[str]:
    """Every markdown file that is a candidate for the register.

    Shared by orphan detection and the stub emitter on purpose. Two walkers with
    slightly different exclusion rules is how a document ends up reported as an
    orphan by one and skipped by the other, forever.
    """
    candidates: list[str] = []
    for droot in doc_roots:
        base = root / droot if droot != "." else root
        if not base.exists():
            continue
        walker = base.rglob("*.md") if droot != "." else base.glob("*.md")
        for f in sorted(walker):
            rel = f.relative_to(root).as_posix()
            if rel in registered:
                continue
            # A dot-directory is machine territory: caches, skill output, tooling.
            if any(part.startswith(".") for part in Path(rel).parts[:-1]):
                continue
            if any(fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch("/" + rel, pat) for pat in ignore):
                continue
            candidates.append(rel)
    skip = gitignored(root, candidates, use_git)
    return [rel for rel in candidates if rel not in skip]


def find_orphans(root: Path, registered: set[str], ignore: list[str],
                 doc_roots: list[str], use_git: bool) -> list[Finding]:
    return [Finding(SUSPECT, rel, "orphan", "not in the register")
            for rel in discover_docs(root, registered, ignore, doc_roots, use_git)]


# Names that give away what a document IS. A guess, and labelled as one everywhere
# it surfaces: the stub writes provenance "harvested", which cannot fail a build.
_HYBRID_HINTS = ("backlog", "roadmap", "todo", "tasks")


def guess_update_mode(rel: str) -> str:
    stem = Path(rel).name.lower()
    return "hybrid" if any(h in stem for h in _HYBRID_HINTS) else "supersede"


def emit_stub(root: Path, ignore: list[str], doc_roots: list[str],
              use_git: bool) -> dict:
    """A provisional register for a repo that has none.

    Every entry lands harvested and anchorless, so the register it produces CANNOT
    fail a build and says so on every run. That is the whole trade: the skill
    becomes runnable in a repo on first contact, and buys none of the certainty
    that only curation can supply. Anchors get added for the documents the work in
    hand actually touched, not for all of them at once - a full bootstrap is what
    made this skill too expensive to have ever been run in any repo on this machine.
    """
    docs = discover_docs(root, set(), ignore, doc_roots, use_git)
    return {
        "version": 2,
        "checker_version": VERSION,
        "repo": root.name,
        "doc_roots": doc_roots,
        "provisional": True,
        "docs": [{"path": rel,
                  "owns": "TODO - one line, and it doubles as the duplication check",
                  "provenance": "harvested",
                  "update_mode": guess_update_mode(rel),
                  "verified_at": None,
                  "verified_sha": "none",
                  "anchors": {}} for rel in docs],
    }


def check_unenforced(doc: str, entry: dict) -> list[Finding]:
    """Name every declaration this gate does not enforce, on every run.

    A register that says frozen_sections and a checker that ignores it reads as a
    live protection to the next session. Documented traps are not controls.
    """
    out = []
    for field in entry:
        if field in ENFORCED_DOC_FIELDS or field in CONSUMED_BY_SKILL:
            continue
        out.append(Finding(INFO, doc, "declared-not-enforced",
                           f"{field!r} is recorded in the register and this gate does NOT act on it. "
                           f"Do not rely on it as a guard."))
    for kind in entry.get("anchors", {}):
        if kind not in ENFORCED_ANCHOR_KINDS:
            out.append(Finding(INFO, doc, "declared-not-enforced",
                               f"anchor kind {kind!r} is unknown to this gate and is not checked."))
    return out


def run_checks(root: Path, register: dict, reg_path: Path | None = None,
               allow_empty: bool = False) -> list[Finding]:
    use_git = has_git(root)
    cache: dict[str, bool] = {}
    findings: list[Finding] = []
    entries = register.get("docs", [])
    ignore = DEFAULT_IGNORE + register.get("ignore", [])
    doc_roots = register.get("doc_roots", ["docs", "."])

    seen_owns: dict[str, str] = {}
    for entry in entries:
        doc = entry.get("path")
        if not doc:
            continue
        if not (root / doc).exists():
            findings.append(Finding(BROKEN, doc, "missing-doc", "registered but the file is gone"))
            continue
        anchors = entry.get("anchors", {})
        missing = [p.rstrip("/") for p in anchors.get("paths", []) if not expand(root, p)]
        root_ignored = gitignored(root, missing, use_git)
        per_doc: list[Finding] = []
        per_doc += check_paths(root, doc, anchors, root_ignored)
        per_doc += check_symbols(root, doc, anchors, use_git, cache, reg_path)
        per_doc += check_commands(root, doc, anchors)
        per_doc += check_config(root, doc, anchors, use_git, cache, reg_path)
        per_doc += check_counts(root, doc, anchors)
        per_doc += check_suspect(root, entry, use_git)
        per_doc += check_update_mode(root, doc, entry)
        per_doc += check_stamp(root, doc, entry)
        per_doc += check_bloat(root, doc, entry)
        if entry.get("provenance") != CURATED:
            for f in per_doc:
                if f.severity == BROKEN:
                    f.severity = SUSPECT
                    f.detail += (" [harvested anchor, not gated: nobody has confirmed this doc "
                                 "depends on it. Counter-examples and rename records are SUPPOSED "
                                 "to be absent. Set provenance: curated to gate on it.]")
        findings += per_doc
        findings += check_unenforced(doc, entry)
        owns = (entry.get("owns") or "").strip().lower()
        if owns:
            if owns in seen_owns:
                findings.append(Finding(SUSPECT, doc, "overlap",
                                        f"claims the same scope as {seen_owns[owns]}"))
            else:
                seen_owns[owns] = doc

    declared_cv = register.get("checker_version")
    if declared_cv is None:
        findings.append(Finding(
            INFO, str(reg_path or REGISTER_RELPATH), "checker-version-undeclared",
            f"register does not say which checker version it was written against; this is "
            f"check-docs {VERSION}. Add checker_version to make a vendored copy's drift visible."))
    elif declared_cv != VERSION:
        findings.append(Finding(
            SUSPECT, str(reg_path or REGISTER_RELPATH), "checker-version-drift",
            f"register was written against checker {declared_cv} and this is {VERSION}. CI runs a "
            f"copy vendored into the repo, which cannot see ~/.claude and therefore drifts "
            f"silently; a green run from a stale checker is a green run of the wrong checks."))

    curated = [e for e in entries if e.get("provenance") == CURATED]
    if entries and not curated:
        findings.append(Finding(
            SUSPECT, str(reg_path or REGISTER_RELPATH), "no-curated-docs",
            f"0 of {len(entries)} docs are provenance: curated, so this register CANNOT fail a "
            f"build. It is advisory until someone confirms anchors. Do not read a green run as a "
            f"clean bill of health."))

    checkable = sum(
        len(e.get("anchors", {}).get(k, []))
        for e in entries
        for k in ("paths", "symbols", "commands", "config", "counts")
    )
    if checkable == 0 and not allow_empty:
        findings.append(Finding(
            BROKEN, str(reg_path or REGISTER_RELPATH), "vacuous-register",
            f"{len(entries)} entries but ZERO checkable anchors. A gate that cannot "
            f"fail is worse than no gate, because it is believed. Pass --allow-empty "
            f"only while bootstrapping."))

    findings += find_orphans(root, {e.get("path") for e in entries}, ignore, doc_roots, use_git)
    return findings


# --------------------------------------------------------------------------- #
# reporting
# --------------------------------------------------------------------------- #

def report_human(findings: list[Finding], root: Path) -> None:
    broken = [f for f in findings if f.severity == BROKEN]
    suspect = [f for f in findings if f.severity == SUSPECT]
    info = [f for f in findings if f.severity == INFO]
    print(f"check-docs {VERSION}  ({root})")
    if not findings:
        print("\nCLEAN - every registered anchor resolves.")
        return
    for label, group in (("BROKEN", broken), ("SUSPECT", suspect),
                         ("INFO (never gates)", info)):
        if not group:
            continue
        print(f"\n{label} ({len(group)})")
        for f in group:
            print(f"  {f.doc}\n      [{f.kind}] {f.detail}")
    print(f"\n{len(broken)} broken, {len(suspect)} suspect, {len(info)} info")
    if broken:
        print("Broken anchors are proof of staleness. Fix the doc or the register.")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Mechanical doc staleness detector.")
    ap.add_argument("--root", default=".", help="repo root (default: cwd)")
    ap.add_argument("--register", default=None,
                    help=f"register path (default: {REGISTER_RELPATH}, then a root-level "
                         f"*DOC-REGISTER*.json)")
    ap.add_argument("--emit-stub", action="store_true",
                    help="write a provisional register for a repo that has none, then exit")
    ap.add_argument("--no-auto-bootstrap", action="store_true",
                    help="a missing register is a hard exit 3 (use in CI)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--strict", action="store_true", help="exit 1 on suspect findings too")
    ap.add_argument("--allow-empty", action="store_true",
                    help="permit a register with zero checkable anchors (bootstrap only)")
    ap.add_argument("--version", action="version", version=f"check-docs {VERSION}")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    reg_path, disc_err = discover_register(root, args.register)
    if disc_err:
        print(json.dumps({"error": disc_err}) if args.json else disc_err, file=sys.stderr)
        return 3

    if args.emit_stub:
        target = reg_path if reg_path else root / REGISTER_RELPATH
        if target.exists():
            msg = (f"{target} already exists. --emit-stub will not overwrite a register: "
                   f"the curated anchors in it are the expensive part.")
            print(json.dumps({"error": msg}) if args.json else msg, file=sys.stderr)
            return 3
        stub = emit_stub(root, DEFAULT_IGNORE, ["docs", "."], has_git(root))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(stub, indent=2) + "\n", encoding="utf-8")
        n = len(stub["docs"])
        print(f"wrote provisional register {target} covering {n} document(s).\n"
              f"Every entry is provenance: harvested with no anchors, so this register CANNOT "
              f"fail a build and will say so on every run. Curate anchors for the documents the "
              f"work in hand touches - not for all {n} at once.")
        return 0

    if reg_path is None or not reg_path.exists():
        where = reg_path or (root / REGISTER_RELPATH)
        msg = (f"no register at {where}. Run: check-docs.py --emit-stub to create a provisional "
               f"one, or /docs-sync --bootstrap to curate properly.")
        if args.no_auto_bootstrap:
            print(json.dumps({"error": msg}) if args.json else msg, file=sys.stderr)
            return 3
        print(json.dumps({"error": msg}) if args.json else msg, file=sys.stderr)
        return 3
    try:
        register = json.loads(reg_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        msg = f"register is not valid JSON: {e}"
        print(json.dumps({"error": msg}) if args.json else msg, file=sys.stderr)
        return 3

    findings = run_checks(root, register, reg_path.resolve(), args.allow_empty)
    if args.json:
        print(json.dumps({"version": VERSION, "root": str(root),
                          "findings": [f.as_dict() for f in findings]}, indent=2))
    else:
        report_human(findings, root)

    if any(f.severity == BROKEN for f in findings):
        return 1
    if any(f.severity == SUSPECT for f in findings):
        return 1 if args.strict else 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
