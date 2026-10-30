#!/usr/bin/env python3
"""Proof that every detector in check-docs.py can FAIL.

A guard nobody has watched fail is not a guard. Each test builds a throwaway repo
that is broken in exactly one way and asserts the checker names that one way.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
CHECKER = HERE / "check-docs.py"

# Read from the checker rather than restated here. A test file carrying its own copy
# of the version is a second source of truth that goes stale silently and then proves
# the wrong thing about drift detection.
CHECKER_VERSION = re.search(r'^VERSION = "([^"]+)"',
                            CHECKER.read_text(encoding="utf-8"), re.M).group(1)


class RepoBuilder:
    def __init__(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="docs-sync-fixture-"))

    def write(self, rel: str, body: str = "x") -> Path:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
        return p

    def register(self, docs: list, **extra) -> None:
        # Fixtures that say nothing about update_mode get `frozen`, the mode that adds
        # no obligations: no stamp is required and no ceiling applies. A test written
        # to prove the count detector fails must not also start failing because a
        # field it never cared about became required. Tests that DO exercise
        # update_mode declare it explicitly and this default never applies to them.
        docs = [{"update_mode": "frozen", **d} for d in docs]
        payload = {"version": 2, "checker_version": CHECKER_VERSION, "docs": docs}
        payload.update(extra)
        self.write("docs/doc-register.json", json.dumps(payload, indent=2))

    def git_init(self) -> str:
        env = ["-c", "user.email=t@t", "-c", "user.name=t", "-c", "commit.gpgsign=false"]
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", *env, "add", "-A"], cwd=self.root, check=True)
        subprocess.run(["git", *env, "commit", "-q", "-m", "init"], cwd=self.root, check=True)
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.root,
                              capture_output=True, text=True).stdout.strip()

    def git_commit_all(self) -> None:
        env = ["-c", "user.email=t@t", "-c", "user.name=t", "-c", "commit.gpgsign=false"]
        subprocess.run(["git", *env, "add", "-A"], cwd=self.root, check=True)
        subprocess.run(["git", *env, "commit", "-q", "-m", "change"], cwd=self.root, check=True)

    def run(self, *args: str, allow_empty: bool = True):
        base = [sys.executable, str(CHECKER), "--root", str(self.root), "--json"]
        if allow_empty:
            base.append("--allow-empty")
        p = subprocess.run([*base, *args],
                           capture_output=True, text=True)
        try:
            payload = json.loads(p.stdout) if p.stdout.strip() else {}
        except json.JSONDecodeError:
            payload = {}
        return p.returncode, payload

    def kinds(self, payload) -> set:
        return {f["kind"] for f in payload.get("findings", [])}

    def destroy(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)


class DetectorTests(unittest.TestCase):
    def setUp(self):
        self.r = RepoBuilder()

    def tearDown(self):
        self.r.destroy()

    # ---- the clean control. If this ever fails, every other test is meaningless.
    def test_clean_repo_exits_zero(self):
        self.r.write("src/ingest.ts", "export function ingestLesson() {}")
        self.r.write("docs/ingest.md", "# Ingest")
        self.r.write("package.json", json.dumps({"scripts": {"ingest": "node ."}}))
        self.r.write(".env.example", "INGEST_BATCH_SIZE=10")
        sha = "0" * 40
        self.r.register([{
            "path": "docs/ingest.md", "owns": "ingest pipeline",
            "provenance": "curated", "verified_sha": sha,
            "anchors": {"paths": ["src/ingest.ts"], "symbols": ["ingestLesson"],
                        "commands": ["npm run ingest"], "config": ["INGEST_BATCH_SIZE"]},
        }])
        code, payload = self.r.run()
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload["findings"], [])

    def test_broken_path(self):
        self.r.write("docs/a.md", "# A")
        self.r.register([{"path": "docs/a.md", "provenance": "curated", "verified_sha": "0" * 40,
                          "anchors": {"paths": ["src/gone.ts"]}}])
        code, payload = self.r.run()
        self.assertEqual(code, 1)
        self.assertIn("path", self.r.kinds(payload))

    def test_broken_symbol(self):
        self.r.write("src/a.ts", "export function stillHere() {}")
        self.r.write("docs/a.md", "# A")
        self.r.register([{"path": "docs/a.md", "provenance": "curated", "verified_sha": "0" * 40,
                          "anchors": {"symbols": ["renamedAway"]}}])
        code, payload = self.r.run()
        self.assertEqual(code, 1)
        self.assertIn("symbol", self.r.kinds(payload))

    def test_symbol_present_only_in_markdown_is_still_broken(self):
        """The circularity guard: a doc may not be evidence for its own claim."""
        self.r.write("src/a.ts", "export function stillHere() {}")
        self.r.write("docs/a.md", "# A\n\nCall `ghostSymbol()` to start.")
        self.r.register([{"path": "docs/a.md", "provenance": "curated", "verified_sha": "0" * 40,
                          "anchors": {"symbols": ["ghostSymbol"]}}])
        code, payload = self.r.run()
        self.assertEqual(code, 1, payload)
        self.assertIn("symbol", self.r.kinds(payload))

    def test_broken_npm_script(self):
        self.r.write("docs/a.md", "# A")
        self.r.write("package.json", json.dumps({"scripts": {"build": "tsc"}}))
        self.r.register([{"path": "docs/a.md", "provenance": "curated", "verified_sha": "0" * 40,
                          "anchors": {"commands": ["npm run ingest"]}}])
        code, payload = self.r.run()
        self.assertEqual(code, 1)
        self.assertIn("command", self.r.kinds(payload))

    def test_broken_make_target(self):
        self.r.write("docs/a.md", "# A")
        self.r.write("Makefile", "build:\n\techo hi\n")
        self.r.register([{"path": "docs/a.md", "provenance": "curated", "verified_sha": "0" * 40,
                          "anchors": {"commands": ["make deploy"]}}])
        code, payload = self.r.run()
        self.assertEqual(code, 1)
        self.assertIn("command", self.r.kinds(payload))

    def test_broken_script_path_in_command(self):
        self.r.write("docs/a.md", "# A")
        self.r.register([{"path": "docs/a.md", "provenance": "curated", "verified_sha": "0" * 40,
                          "anchors": {"commands": ["python3 tools/gone.py --all"]}}])
        code, payload = self.r.run()
        self.assertEqual(code, 1)
        self.assertIn("command", self.r.kinds(payload))

    def test_unresolvable_command_is_suspect_not_broken(self):
        """A command the checker cannot model is a gap in the checker, not proof
        of a stale doc. Failing a build on that would be a lie."""
        self.r.write("docs/a.md", "# A")
        self.r.register([{"path": "docs/a.md", "provenance": "curated", "verified_sha": "0" * 40,
                          "anchors": {"commands": ["kubectl apply"]}}])
        code, payload = self.r.run()
        self.assertEqual(code, 2, payload)
        self.assertIn("command", self.r.kinds(payload))

    def test_broken_config_key(self):
        self.r.write("src/a.ts", "const x = process.env.REAL_KEY")
        self.r.write("docs/a.md", "# A")
        self.r.register([{"path": "docs/a.md", "provenance": "curated", "verified_sha": "0" * 40,
                          "anchors": {"config": ["REMOVED_KEY"]}}])
        code, payload = self.r.run()
        self.assertEqual(code, 1)
        self.assertIn("config", self.r.kinds(payload))

    def test_count_mismatch(self):
        """The count-drift class: a doc asserting 25 modules against a repo holding 35."""
        for i in range(3):
            self.r.write(f"infra/modules/m{i}/main.tf", "resource {}")
        self.r.write("docs/infra.md", "# Infra\n\nThere are 5 modules.")
        self.r.register([{"path": "docs/infra.md", "provenance": "curated", "verified_sha": "0" * 40,
                          "anchors": {"counts": [{"claim": "5 modules", "kind": "dir",
                                                  "source": "infra/modules/*/",
                                                  "expect": 5}]}}])
        code, payload = self.r.run()
        self.assertEqual(code, 1, payload)
        self.assertIn("count", self.r.kinds(payload))
        self.assertIn("is 3", json.dumps(payload))

    def test_count_match_is_clean(self):
        for i in range(3):
            self.r.write(f"infra/modules/m{i}/main.tf", "resource {}")
        self.r.write("docs/infra.md", "# Infra")
        self.r.register([{"path": "docs/infra.md", "provenance": "curated", "verified_sha": "0" * 40,
                          "anchors": {"counts": [{"claim": "3 modules", "kind": "dir",
                                                  "source": "infra/modules/*/",
                                                  "expect": 3}]}}])
        code, payload = self.r.run()
        self.assertEqual(code, 0, payload)

    def test_registered_doc_deleted(self):
        self.r.register([{"path": "docs/gone.md", "provenance": "curated", "verified_sha": "0" * 40, "anchors": {}}])
        code, payload = self.r.run()
        self.assertEqual(code, 1)
        self.assertIn("missing-doc", self.r.kinds(payload))

    def test_orphan_doc(self):
        self.r.write("docs/tracked.md", "# T")
        self.r.write("docs/untracked.md", "# U")
        self.r.register([{"path": "docs/tracked.md", "provenance": "curated", "verified_sha": "0" * 40, "anchors": {}}])
        code, payload = self.r.run()
        self.assertEqual(code, 2, payload)
        self.assertIn("orphan", self.r.kinds(payload))

    def test_records_are_never_orphans(self):
        """ADRs, changelogs and lessons-learned describe the past on purpose."""
        self.r.write("docs/tracked.md", "# T")
        self.r.write("CHANGELOG.md", "# Changelog")
        self.r.write("docs/adr/0001-choose-x.md", "# ADR 1")
        self.r.write("docs/project-lessons-learned.md", "# Lessons")
        self.r.register([{"path": "docs/tracked.md", "provenance": "curated", "verified_sha": "0" * 40, "anchors": {}}])
        code, payload = self.r.run()
        self.assertEqual(code, 0, payload)

    def test_two_docs_claiming_the_same_scope(self):
        self.r.write("docs/a.md", "# A")
        self.r.write("docs/b.md", "# B")
        self.r.register([
            {"path": "docs/a.md", "owns": "the ingest pipeline", "provenance": "curated", "verified_sha": "0" * 40, "anchors": {}},
            {"path": "docs/b.md", "owns": "The Ingest Pipeline", "provenance": "curated", "verified_sha": "0" * 40, "anchors": {}},
        ])
        code, payload = self.r.run()
        self.assertEqual(code, 2, payload)
        self.assertIn("overlap", self.r.kinds(payload))

    def test_missing_verified_sha_is_suspect(self):
        self.r.write("docs/a.md", "# A")
        self.r.register([{"path": "docs/a.md", "anchors": {}}])
        code, payload = self.r.run()
        self.assertEqual(code, 2)
        self.assertIn("unverified", self.r.kinds(payload))

    def test_strict_promotes_suspect_to_failure(self):
        self.r.write("docs/a.md", "# A")
        self.r.write("docs/orphan.md", "# O")
        self.r.register([{"path": "docs/a.md", "provenance": "curated", "verified_sha": "0" * 40, "anchors": {}}])
        self.assertEqual(self.r.run()[0], 2)
        self.assertEqual(self.r.run("--strict")[0], 1)

    def test_no_register_exits_three(self):
        self.r.write("docs/a.md", "# A")
        code, payload = self.r.run()
        self.assertEqual(code, 3)

    def test_malformed_register_exits_three(self):
        self.r.write("docs/doc-register.json", "{not json")
        code, _ = self.r.run()
        self.assertEqual(code, 3)

    def test_count_without_kind_is_suspect_not_gated(self):
        """A count anchor that does not say what it counts cannot fail a build.
        Directory count and module count are different numbers; gating on the
        ambiguity would be the very failure the count detector exists to catch."""
        for i in range(3):
            self.r.write(f"infra/modules/m{i}/main.tf", "resource {}")
        self.r.write("docs/infra.md", "# Infra")
        self.r.register([{"path": "docs/infra.md", "provenance": "curated", "verified_sha": "0" * 40,
                          "anchors": {"counts": [{"claim": "5 modules",
                                                  "source": "infra/modules/*/",
                                                  "expect": 5}]}}])
        code, payload = self.r.run()
        self.assertEqual(code, 2, payload)
        self.assertIn("count-unqualified", self.r.kinds(payload))

    def test_count_dir_with_ignores_directories_lacking_the_file(self):
        """The flaw found in my own 36-module claim: two of those directories
        might hold no .tf at all, making the number right about directories and
        wrong about modules."""
        for i in range(3):
            self.r.write(f"infra/modules/m{i}/main.tf", "resource {}")
        self.r.write("infra/modules/notamodule/README.txt", "scratch")
        self.r.write("docs/infra.md", "# Infra")
        self.r.register([{"path": "docs/infra.md", "provenance": "curated", "verified_sha": "0" * 40,
                          "anchors": {"counts": [{"claim": "3 modules", "kind": "dir_with",
                                                  "contains": "*.tf",
                                                  "source": "infra/modules/*/",
                                                  "expect": 3}]}}])
        self.assertEqual(self.r.run()[0], 0)
        # the same repo counted as bare directories is 4, not 3
        self.r.register([{"path": "docs/infra.md", "provenance": "curated", "verified_sha": "0" * 40,
                          "anchors": {"counts": [{"claim": "3 modules", "kind": "dir",
                                                  "source": "infra/modules/*/",
                                                  "expect": 3}]}}])
        code, payload = self.r.run()
        self.assertEqual(code, 1, payload)
        self.assertIn("is 4", json.dumps(payload))

    def test_docs_in_dot_directories_are_not_orphans(self):
        """Skill output lives in gitignored dot-directories by house rule.
        Demanding those be registered is noise, and noise gets gates disabled."""
        self.r.write("docs/tracked.md", "# T")
        self.r.write(".canvas-audit/verdicts-batch1.md", "# audit output")
        self.r.write(".docs-reports/run-01.md", "# report")
        self.r.register([{"path": "docs/tracked.md", "provenance": "curated", "verified_sha": "0" * 40, "anchors": {}}],
                        doc_roots=["docs", ".", ".canvas-audit"])
        code, payload = self.r.run()
        self.assertEqual(code, 0, payload)

    def test_vacuous_register_fails_loudly(self):
        """A register with nothing checkable must not report CLEAN. Same doctrine as
        the global count-is-not-a-verdict rule: zero findings from an empty source is
        evidence about the source."""
        self.r.write("docs/a.md", "# A")
        self.r.register([{"path": "docs/a.md", "provenance": "curated", "verified_sha": "0" * 40, "anchors": {}}])
        code, payload = self.r.run(allow_empty=False)
        self.assertEqual(code, 1, payload)
        self.assertIn("vacuous-register", self.r.kinds(payload))

    def test_observation_count_never_gates(self):
        """A dated measurement kept on purpose is not rot. Firing on it is how a
        checker earns deletion rather than tuning."""
        for i in range(4):
            self.r.write(f"pages/p{i}/index.html", "<html>")
        self.r.write("docs/baseline.md", "# Verified baseline, 343 pages (2026-08-12)")
        self.r.register([{"path": "docs/baseline.md", "provenance": "curated", "verified_sha": "0" * 40,
                          "anchors": {"counts": [{"claim": "343 pages", "kind": "observation",
                                                  "counts_as": "dir",
                                                  "source": "pages/*/", "expect": 343}]}}])
        code, payload = self.r.run()
        self.assertEqual(code, 0, payload)
        self.assertIn("observation-drifted", self.r.kinds(payload))

    def test_register_named_by_house_convention_still_excluded(self):
        """A repo may name the register anything. Excluding a hardcoded basename let
        it become evidence for its own anchors the moment one did."""
        self.r.write("src/a.ts", "export function stillHere() {}")
        self.r.write("CANVAS-DOC-REGISTER.json", json.dumps({"version": 1, "docs": [
            {"path": "GUIDE.md", "provenance": "curated", "verified_sha": "0" * 40,
             "anchors": {"symbols": ["ghostSymbol"]}}]}, indent=2))
        self.r.write("GUIDE.md", "# Guide")
        code, payload = self.r.run("--register", str(self.r.root / "CANVAS-DOC-REGISTER.json"))
        self.assertEqual(code, 1, payload)
        self.assertIn("symbol", self.r.kinds(payload))

    def test_gitignored_missing_path_is_info_not_broken(self):
        """A generated artifact is absent in every clean checkout by design. Failing
        the build on it would make the gate red on every run for a correct absence."""
        self.r.write("docs/a.md", "# A")
        self.r.write("src/real.ts", "x")
        self.r.write(".gitignore", "canvas-380-audit-baseline.json\n")
        self.r.register([{"path": "docs/a.md", "provenance": "curated", "verified_sha": "PLACEHOLDER",
                          "anchors": {"paths": ["src/real.ts", "canvas-380-audit-baseline.json"]}}])
        sha = self.r.git_init()
        reg = self.r.root / "docs/doc-register.json"
        reg.write_text(reg.read_text().replace("PLACEHOLDER", sha), encoding="utf-8")
        code, payload = self.r.run(allow_empty=False)
        self.assertEqual(code, 0, payload)
        self.assertIn("path-generated", self.r.kinds(payload))

    def test_untracked_missing_path_is_still_broken(self):
        """The control for the test above: absence without a gitignore entry is a defect."""
        self.r.write("docs/a.md", "# A")
        self.r.write("src/real.ts", "x")
        self.r.register([{"path": "docs/a.md", "provenance": "curated", "verified_sha": "PLACEHOLDER",
                          "anchors": {"paths": ["src/real.ts", "scripts/audit-pages.py"]}}])
        sha = self.r.git_init()
        reg = self.r.root / "docs/doc-register.json"
        reg.write_text(reg.read_text().replace("PLACEHOLDER", sha), encoding="utf-8")
        code, payload = self.r.run(allow_empty=False)
        self.assertEqual(code, 1, payload)
        self.assertIn("path", self.r.kinds(payload))

    def test_unenforced_field_announces_itself_every_run(self):
        """A register declaring frozen_sections while the gate ignores it reads as a
        live protection. Documented traps are not controls."""
        self.r.write("docs/a.md", "# A")
        self.r.write("src/real.ts", "x")
        self.r.register([{"path": "docs/a.md", "provenance": "curated", "verified_sha": "0" * 40,
                          "frozen_sections": ["History"],
                          "anchors": {"paths": ["src/real.ts"], "screenshots": ["x.png"]}}])
        code, payload = self.r.run(allow_empty=False)
        self.assertEqual(code, 0, payload)
        details = json.dumps(payload)
        self.assertIn("declared-not-enforced", self.r.kinds(payload))
        self.assertIn("frozen_sections", details)
        self.assertIn("screenshots", details)

    def test_review_field_is_not_flagged(self):
        """review is consumed by the repair skill, so it is enforced, just not here."""
        self.r.write("docs/a.md", "# A")
        self.r.write("src/real.ts", "x")
        self.r.register([{"path": "docs/a.md", "provenance": "curated", "verified_sha": "0" * 40, "review": "manual",
                          "anchors": {"paths": ["src/real.ts"]}}])
        code, payload = self.r.run(allow_empty=False)
        self.assertEqual(code, 0, payload)
        self.assertNotIn("declared-not-enforced", self.r.kinds(payload))

    def test_harvested_anchor_cannot_fail_a_build(self):
        """The counter-example case: CLAUDE.md quotes `audit-pages.py` as a COUNTER-EXAMPLE
        inside its own naming rule, and names it again in a rename record. It is supposed
        not to exist. A regex harvest turns that into a BROKEN anchor, and 'fix the doc
        until CI is green' would delete the rule's own worked examples."""
        self.r.write("docs/naming.md",
                     "Not `audit-pages.py` but `canvas-audit-pages.py`.")
        self.r.write("scripts/canvas-audit-pages.py", "print(1)")
        self.r.register([{"path": "docs/naming.md", "verified_sha": "0" * 40,
                          "anchors": {"paths": ["audit-pages.py",
                                                "scripts/canvas-audit-pages.py"]}}])
        code, payload = self.r.run(allow_empty=False)
        self.assertEqual(code, 2, payload)
        self.assertNotIn("broken", {f["severity"] for f in payload["findings"]})
        self.assertIn("harvested anchor, not gated", json.dumps(payload))

    def test_curated_anchor_does_fail_a_build(self):
        """The control: once someone confirms the doc really depends on it, it gates."""
        self.r.write("docs/naming.md", "Run `scripts/gone.py` first.")
        self.r.register([{"path": "docs/naming.md", "provenance": "curated",
                          "verified_sha": "0" * 40,
                          "anchors": {"paths": ["scripts/gone.py"]}}])
        code, payload = self.r.run(allow_empty=False)
        self.assertEqual(code, 1, payload)

    def test_register_with_no_curated_docs_says_it_cannot_fail(self):
        self.r.write("docs/a.md", "# A")
        self.r.write("src/real.ts", "x")
        self.r.register([{"path": "docs/a.md", "verified_sha": "0" * 40,
                          "anchors": {"paths": ["src/real.ts"]}}])
        code, payload = self.r.run(allow_empty=False)
        self.assertIn("no-curated-docs", self.r.kinds(payload))

    def test_bare_basename_that_lives_elsewhere_is_surfaced_not_guessed(self):
        """Docs cite `canvas-audit-pages.py` bare while the file is scripts/canvas-audit-pages.py.
        Adding a search path would hide resolver gaps; a neighbouring checker lost its
        scripts/ fallback in a rewrite and turned nine live scripts into twelve dead
        citations. So the ambiguity is reported and the curator stores the resolved path."""
        self.r.write("scripts/canvas-audit-pages.py", "print(1)")
        self.r.write("docs/a.md", "# A")
        self.r.register([{"path": "docs/a.md", "provenance": "curated", "verified_sha": "0" * 40,
                          "anchors": {"paths": ["canvas-audit-pages.py"]}}])
        code, payload = self.r.run(allow_empty=False)
        self.assertEqual(code, 2, payload)
        self.assertIn("unresolved-basename", self.r.kinds(payload))
        self.assertIn("scripts/canvas-audit-pages.py", json.dumps(payload))

    def test_resolved_path_is_clean(self):
        self.r.write("scripts/canvas-audit-pages.py", "print(1)")
        self.r.write("docs/a.md", "# A")
        self.r.register([{"path": "docs/a.md", "provenance": "curated", "verified_sha": "0" * 40,
                          "anchors": {"paths": ["scripts/canvas-audit-pages.py"]}}])
        self.assertEqual(self.r.run(allow_empty=False)[0], 0)

    def test_bare_basename_that_exists_nowhere_still_breaks(self):
        self.r.write("docs/a.md", "# A")
        self.r.write("src/x.ts", "x")
        self.r.register([{"path": "docs/a.md", "provenance": "curated", "verified_sha": "0" * 40,
                          "anchors": {"paths": ["src/x.ts", "totally-gone.py"]}}])
        code, payload = self.r.run(allow_empty=False)
        self.assertEqual(code, 1, payload)
        self.assertIn("path", self.r.kinds(payload))

    def test_ambiguous_basename_lists_all_and_refuses_to_choose(self):
        """README.md resolves three ways in a real repo here. Naming the first match
        would have the curator freeze a path that may be the wrong one, and a wrong
        RESOLVED path is worse than a bare string: it looks settled and diffs clean."""
        for d in ("guides", "CANVAS-RESEARCH", "canvas-380-ig-grading"):
            self.r.write(f"{d}/README.md", "# readme")
        self.r.write("docs/a.md", "# A")
        self.r.register([{"path": "docs/a.md", "provenance": "curated", "verified_sha": "0" * 40,
                          "anchors": {"paths": ["README.md"]}}])
        code, payload = self.r.run(allow_empty=False)
        self.assertEqual(code, 2, payload)
        self.assertIn("ambiguous-basename", self.r.kinds(payload))
        blob = json.dumps(payload)
        self.assertIn("matching 3 files", blob)
        self.assertIn("CANVAS-RESEARCH/README.md", blob)
        self.assertIn("canvas-380-ig-grading/README.md", blob)
        self.assertIn("guides/README.md", blob)
        self.assertNotIn("unresolved-basename", self.r.kinds(payload))

    def test_many_matches_are_counted_not_truncated(self):
        """Seven copies must be reported as seven, not as the first few."""
        for i in range(9):
            self.r.write(f"infographics/set{i}/NOTE-recovered.txt", "note")
        self.r.write("docs/a.md", "# A")
        self.r.register([{"path": "docs/a.md", "provenance": "curated", "verified_sha": "0" * 40,
                          "anchors": {"paths": ["NOTE-recovered.txt"]}}])
        code, payload = self.r.run(allow_empty=False)
        blob = json.dumps(payload)
        self.assertIn("matching 9 files", blob)
        self.assertIn("+1 more", blob)


class GitBackedTests(unittest.TestCase):
    def setUp(self):
        self.r = RepoBuilder()

    def tearDown(self):
        self.r.destroy()

    def test_touched_anchor_becomes_suspect(self):
        self.r.write("src/ingest.ts", "export function ingestLesson() {}")
        self.r.write("docs/ingest.md", "# Ingest")
        self.r.register([{"path": "docs/ingest.md", "provenance": "curated", "verified_sha": "PLACEHOLDER",
                          "anchors": {"paths": ["src/ingest.ts"]}}])
        sha = self.r.git_init()
        reg = self.r.root / "docs/doc-register.json"
        reg.write_text(reg.read_text().replace("PLACEHOLDER", sha), encoding="utf-8")
        self.r.write("src/ingest.ts", "export function ingestLesson() { /* rewritten */ }")
        self.r.git_commit_all()
        code, payload = self.r.run()
        self.assertEqual(code, 2, payload)
        self.assertIn("touched", self.r.kinds(payload))

    def test_doc_reconciled_in_the_same_commit_as_its_anchor_is_not_suspect(self):
        """Backlog #144. A stamp written on a feature branch can never name the
        squash-merge sha, because that sha does not exist yet. The squash then
        carries the doc AND its anchors in one commit, so a naive sha..HEAD diff
        reports the doc stale against its own reconciliation - permanently, and
        for every squash-merged documentation change. A doc updated in the same
        commit as its anchor was written WITH knowledge of that change."""
        self.r.write("src/ingest.ts", "export function ingestLesson() {}")
        self.r.write("docs/ingest.md", "# Ingest")
        self.r.register([{"path": "docs/ingest.md", "provenance": "curated", "verified_sha": "PLACEHOLDER",
                          "anchors": {"paths": ["src/ingest.ts"]}}])
        sha = self.r.git_init()
        reg = self.r.root / "docs/doc-register.json"
        reg.write_text(reg.read_text().replace("PLACEHOLDER", sha), encoding="utf-8")
        # one commit changing BOTH the anchor and the doc, the shape a squash merge makes
        self.r.write("src/ingest.ts", "export function ingestLesson() { /* rewritten */ }")
        self.r.write("docs/ingest.md", "# Ingest\n\nNow describes the rewrite.")
        self.r.git_commit_all()
        code, payload = self.r.run()
        self.assertEqual(code, 0, payload)

    def test_anchor_changed_without_the_doc_is_still_suspect(self):
        """The other half, and the one that matters: the fix above must not become
        a way for real staleness to pass. An anchor that moves in a commit which
        leaves the doc alone is exactly what this checker exists to catch."""
        self.r.write("src/ingest.ts", "export function ingestLesson() {}")
        self.r.write("docs/ingest.md", "# Ingest")
        self.r.register([{"path": "docs/ingest.md", "provenance": "curated", "verified_sha": "PLACEHOLDER",
                          "anchors": {"paths": ["src/ingest.ts"]}}])
        sha = self.r.git_init()
        reg = self.r.root / "docs/doc-register.json"
        reg.write_text(reg.read_text().replace("PLACEHOLDER", sha), encoding="utf-8")
        self.r.write("src/ingest.ts", "export function ingestLesson() { /* a */ }")
        self.r.write("docs/ingest.md", "# Ingest\n\nreconciled")
        self.r.git_commit_all()
        # a LATER commit moves the anchor and does not touch the doc
        self.r.write("src/ingest.ts", "export function ingestLesson() { /* b */ }")
        self.r.git_commit_all()
        code, payload = self.r.run()
        self.assertEqual(code, 2, payload)
        self.assertIn("touched", self.r.kinds(payload))

    def test_mixed_history_reports_only_the_unreconciled_commit(self):
        """A doc reconciled once, then left behind by a second anchor change. The
        reconciled commit must not contribute and the orphaned one must."""
        self.r.write("src/a.ts", "export function a() {}")
        self.r.write("src/b.ts", "export function b() {}")
        self.r.write("docs/ingest.md", "# Ingest")
        self.r.register([{"path": "docs/ingest.md", "provenance": "curated", "verified_sha": "PLACEHOLDER",
                          "anchors": {"paths": ["src/a.ts", "src/b.ts"]}}])
        sha = self.r.git_init()
        reg = self.r.root / "docs/doc-register.json"
        reg.write_text(reg.read_text().replace("PLACEHOLDER", sha), encoding="utf-8")
        self.r.write("src/a.ts", "export function a() { /* reconciled with the doc */ }")
        self.r.write("docs/ingest.md", "# Ingest\n\nmentions a")
        self.r.git_commit_all()
        self.r.write("src/b.ts", "export function b() { /* doc never updated */ }")
        self.r.git_commit_all()
        code, payload = self.r.run()
        self.assertEqual(code, 2, payload)
        blob = json.dumps(payload)
        self.assertIn("src/b.ts", blob)
        self.assertNotIn("src/a.ts", blob)

    def test_untouched_anchor_stays_clean(self):
        self.r.write("src/ingest.ts", "export function ingestLesson() {}")
        self.r.write("src/other.ts", "export function other() {}")
        self.r.write("docs/ingest.md", "# Ingest")
        self.r.register([{"path": "docs/ingest.md", "provenance": "curated", "verified_sha": "PLACEHOLDER",
                          "anchors": {"paths": ["src/ingest.ts"]}}])
        sha = self.r.git_init()
        reg = self.r.root / "docs/doc-register.json"
        reg.write_text(reg.read_text().replace("PLACEHOLDER", sha), encoding="utf-8")
        self.r.write("src/other.ts", "export function other() { /* unrelated */ }")
        self.r.git_commit_all()
        code, payload = self.r.run()
        self.assertEqual(code, 0, payload)

    def test_gitignored_docs_are_not_orphans(self):
        self.r.write("docs/tracked.md", "# T")
        self.r.write("build-notes/generated.md", "# generated")
        self.r.write(".gitignore", "build-notes/\n")
        self.r.register([{"path": "docs/tracked.md", "provenance": "curated", "verified_sha": "PLACEHOLDER", "anchors": {}}],
                        doc_roots=["docs", ".", "build-notes"])
        sha = self.r.git_init()
        reg = self.r.root / "docs/doc-register.json"
        reg.write_text(reg.read_text().replace("PLACEHOLDER", sha), encoding="utf-8")
        code, payload = self.r.run()
        self.assertEqual(code, 0, payload)

    def test_untracked_scratch_is_not_evidence(self):
        """A checker log, build artefact or editor backup in the working tree can
        contain the symbol an anchor names and silently satisfy it - a false negative,
        which is the dangerous direction and does not reproduce in clean CI."""
        self.r.write("src/a.ts", "export function stillHere() {}")
        self.r.write("docs/a.md", "# A")
        self.r.register([{"path": "docs/a.md", "provenance": "curated",
                          "verified_sha": "PLACEHOLDER",
                          "anchors": {"symbols": ["renamedAway"]}}])
        sha = self.r.git_init()
        reg = self.r.root / "docs/doc-register.json"
        reg.write_text(reg.read_text().replace("PLACEHOLDER", sha), encoding="utf-8")
        # untracked scratch that happens to name the missing symbol
        self.r.write("checker-output.txt", "renamedAway is not in any source file")
        code, payload = self.r.run(allow_empty=False)
        self.assertEqual(code, 1, payload)
        self.assertIn("symbol", self.r.kinds(payload))




# Derived, never hardcoded. A fixed date in a fixture that is compared against
# "now" passes until it does not, and then fails as a mystery months later:
# the first draft of this file stamped 14:32 on a day the suite ran at 08:26
# and every stamp test reported stamp-future.
_YESTERDAY = datetime.now(ZoneInfo("America/Chicago")) - timedelta(days=1)
STAMP = ("<!-- docs-sync: reconciled " + _YESTERDAY.strftime("%Y-%m-%d")
         + " 09:00 CT | mode: supersede | against: abc1234 -->")
STAMP_DATE = _YESTERDAY.strftime("%Y-%m-%d")


class RegisterDiscoveryTests(unittest.TestCase):
    """v1 declared REGISTER_BASENAME and never used it while reference.md promised a
    two-step search order. The promise is the thing under test."""

    def setUp(self):
        self.r = RepoBuilder()

    def tearDown(self):
        self.r.destroy()

    def _root_register(self, name: str, docs: list) -> None:
        payload = {"version": 2, "checker_version": CHECKER_VERSION,
                   "docs": [{"update_mode": "frozen", **d} for d in docs]}
        self.r.write(name, json.dumps(payload, indent=2))

    def test_root_level_register_is_found_without_a_flag(self):
        self.r.write("GUIDE.md", "# Guide")
        self._root_register("ACME-DOC-REGISTER.json",
                            [{"path": "GUIDE.md", "provenance": "curated",
                              "verified_sha": "0" * 40, "anchors": {}}])
        code, payload = self.r.run()
        self.assertNotEqual(code, 3, payload)
        self.assertNotIn("orphan", self.r.kinds(payload), payload)

    def test_two_root_registers_is_an_error_not_a_pick(self):
        self.r.write("GUIDE.md", "# Guide")
        self._root_register("ACME-DOC-REGISTER.json", [])
        self._root_register("OLD-DOC-REGISTER.json", [])
        code, _ = self.r.run()
        self.assertEqual(code, 3)

    def test_missing_register_still_exits_three(self):
        self.r.write("GUIDE.md", "# Guide")
        code, _ = self.r.run()
        self.assertEqual(code, 3)


class UpdateModeTests(unittest.TestCase):
    def setUp(self):
        self.r = RepoBuilder()
        self.r.write("docs/a.md", "# A\n" + STAMP + "\n")

    def tearDown(self):
        self.r.destroy()

    def _reg(self, **doc):
        base = {"path": "docs/a.md", "provenance": "curated", "verified_sha": "0" * 40,
                "anchors": {}}
        base.update(doc)
        payload = {"version": 2, "checker_version": CHECKER_VERSION, "docs": [base]}
        self.r.write("docs/doc-register.json", json.dumps(payload, indent=2))

    def test_undeclared_update_mode_is_suspect(self):
        self._reg()
        code, payload = self.r.run()
        self.assertIn("update-mode-undeclared", self.r.kinds(payload), payload)
        self.assertEqual(code, 2, payload)

    def test_harvested_doc_is_not_nagged_for_update_mode(self):
        self._reg(provenance="harvested")
        _, payload = self.r.run()
        self.assertNotIn("update-mode-undeclared", self.r.kinds(payload), payload)

    def test_unknown_update_mode_is_broken(self):
        self._reg(update_mode="freshen")
        code, payload = self.r.run()
        self.assertIn("update-mode-invalid", self.r.kinds(payload), payload)
        self.assertEqual(code, 1, payload)

    def test_hybrid_without_append_sections_is_broken(self):
        self._reg(update_mode="hybrid")
        code, payload = self.r.run()
        self.assertIn("append-sections-missing", self.r.kinds(payload), payload)
        self.assertEqual(code, 1, payload)

    def test_hybrid_naming_a_heading_that_is_not_there_is_broken(self):
        self._reg(update_mode="hybrid", append_sections=["Done"])
        code, payload = self.r.run()
        self.assertIn("append-section-missing", self.r.kinds(payload), payload)
        self.assertEqual(code, 1, payload)

    def test_hybrid_with_a_real_heading_is_clean(self):
        self.r.write("docs/a.md", "# A\n\n## Open\n\n## Done\n\n" + STAMP + "\n")
        self._reg(update_mode="hybrid", append_sections=["Done"])
        code, payload = self.r.run()
        self.assertEqual(code, 0, payload)

    def test_append_sections_on_a_supersede_doc_announces_itself_as_inert(self):
        self._reg(update_mode="supersede", append_sections=["Done"])
        _, payload = self.r.run()
        inert = [f for f in payload["findings"]
                 if f["kind"] == "declared-not-enforced" and "append_sections" in f["detail"]]
        self.assertTrue(inert, payload)


class StampTests(unittest.TestCase):
    def setUp(self):
        self.r = RepoBuilder()

    def tearDown(self):
        self.r.destroy()

    def _reg(self, **doc):
        base = {"path": "docs/a.md", "provenance": "curated", "update_mode": "supersede",
                "verified_sha": "0" * 40, "anchors": {}}
        base.update(doc)
        payload = {"version": 2, "checker_version": CHECKER_VERSION, "docs": [base]}
        self.r.write("docs/doc-register.json", json.dumps(payload, indent=2))

    def test_reconciled_doc_with_no_stamp_is_broken(self):
        self.r.write("docs/a.md", "# A\n")
        self._reg()
        code, payload = self.r.run()
        self.assertIn("stamp-missing", self.r.kinds(payload), payload)
        self.assertEqual(code, 1, payload)

    def test_never_reconciled_doc_with_no_stamp_is_only_suspect(self):
        self.r.write("docs/a.md", "# A\n")
        self._reg(verified_sha="none")
        code, payload = self.r.run()
        self.assertIn("stamp-missing", self.r.kinds(payload), payload)
        self.assertEqual(code, 2, payload)

    def test_valid_stamp_is_clean(self):
        self.r.write("docs/a.md", "# A\n" + STAMP + "\n")
        self._reg()
        code, payload = self.r.run()
        self.assertEqual(code, 0, payload)

    def test_malformed_stamp_is_broken(self):
        self.r.write("docs/a.md",
                     "# A\n<!-- docs-sync: reconciled 2026-13-45 99:99 CT -->\n")
        self._reg()
        code, payload = self.r.run()
        self.assertIn("stamp-malformed", self.r.kinds(payload), payload)
        self.assertEqual(code, 1, payload)

    def test_future_stamp_is_broken(self):
        self.r.write("docs/a.md",
                     "# A\n<!-- docs-sync: reconciled 2099-01-01 09:00 CT -->\n")
        self._reg()
        code, payload = self.r.run()
        self.assertIn("stamp-future", self.r.kinds(payload), payload)
        self.assertEqual(code, 1, payload)

    def test_stamp_older_than_the_register_claim_is_suspect(self):
        self.r.write("docs/a.md",
                     "# A\n<!-- docs-sync: reconciled 2026-09-01 09:00 CT -->\n")
        self._reg(verified_at="2026-09-10")
        code, payload = self.r.run()
        self.assertIn("stamp-behind", self.r.kinds(payload), payload)
        self.assertEqual(code, 2, payload)

    def test_two_stamps_in_one_document_is_suspect(self):
        self.r.write("docs/a.md",
                     "# A\n<!-- docs-sync: reconciled 2026-09-01 09:00 CT -->\n"
                     "more\n" + STAMP + "\n")
        self._reg(verified_at="2026-09-10")
        code, payload = self.r.run()
        self.assertIn("stamp-duplicated", self.r.kinds(payload), payload)
        self.assertEqual(code, 2, payload)

    def test_a_record_is_never_asked_for_a_stamp(self):
        self.r.write("docs/a.md", "# A\n")
        self._reg(update_mode="append")
        code, payload = self.r.run()
        self.assertNotIn("stamp-missing", self.r.kinds(payload), payload)
        self.assertEqual(code, 0, payload)


class BloatTests(unittest.TestCase):
    def setUp(self):
        self.r = RepoBuilder()

    def tearDown(self):
        self.r.destroy()

    def _reg(self, **doc):
        base = {"path": "docs/a.md", "provenance": "curated", "update_mode": "supersede",
                "verified_sha": "0" * 40, "anchors": {}}
        base.update(doc)
        payload = {"version": 2, "checker_version": CHECKER_VERSION, "docs": [base]}
        self.r.write("docs/doc-register.json", json.dumps(payload, indent=2))

    def test_a_live_doc_past_its_ceiling_is_suspect(self):
        self.r.write("docs/a.md", "\n".join(["line"] * 50) + "\n" + STAMP + "\n")
        self._reg(max_lines=10)
        code, payload = self.r.run()
        self.assertIn("bloat", self.r.kinds(payload), payload)
        self.assertEqual(code, 2, payload)

    def test_the_bloat_finding_carries_its_denominator(self):
        self.r.write("docs/a.md", "\n".join(["line"] * 50) + "\n" + STAMP + "\n")
        self._reg(max_lines=10)
        _, payload = self.r.run()
        detail = next(f["detail"] for f in payload["findings"] if f["kind"] == "bloat")
        self.assertIn("of 10", detail)
        self.assertIn("51 lines", detail)

    def test_a_hybrid_ceiling_measures_only_the_live_half(self):
        # The append-only section grows by design. A whole-file ceiling on a hybrid
        # doc is a guard guaranteed to fire for a correct reason, and then be raised
        # until it means nothing.
        body = ("# B\n\n## Open\n" + "row\n" * 5
                + "\n## Done\n" + "closed\n" * 500 + "\n" + STAMP + "\n")
        self.r.write("docs/a.md", body)
        self._reg(update_mode="hybrid", append_sections=["Done"], max_lines=20)
        code, payload = self.r.run()
        self.assertNotIn("bloat", self.r.kinds(payload), payload)
        self.assertEqual(code, 0, payload)

    def test_a_hybrid_whose_live_half_bloats_is_still_caught(self):
        body = ("# B\n\n## Open\n" + "row\n" * 500
                + "\n## Done\n" + "closed\n" * 5 + "\n" + STAMP + "\n")
        self.r.write("docs/a.md", body)
        self._reg(update_mode="hybrid", append_sections=["Done"], max_lines=20)
        code, payload = self.r.run()
        self.assertIn("bloat", self.r.kinds(payload), payload)
        detail = next(f["detail"] for f in payload["findings"] if f["kind"] == "bloat")
        self.assertIn("append-only sections excluded", detail)
        self.assertEqual(code, 2, payload)

    def test_a_record_is_allowed_to_grow(self):
        self.r.write("docs/a.md", "\n".join(["line"] * 50) + "\n")
        self._reg(update_mode="append", max_lines=10)
        code, payload = self.r.run()
        self.assertNotIn("bloat", self.r.kinds(payload), payload)
        self.assertEqual(code, 0, payload)

    def test_a_nonsense_ceiling_is_broken(self):
        self.r.write("docs/a.md", "# A\n" + STAMP + "\n")
        self._reg(max_lines=0)
        code, payload = self.r.run()
        self.assertIn("max-lines-invalid", self.r.kinds(payload), payload)
        self.assertEqual(code, 1, payload)


class WorkingTreeTests(unittest.TestCase):
    """The operator does the work, asks for the docs to be reconciled, THEN commits.
    A detector that only reads verified_sha..HEAD is blind at exactly that moment."""

    def setUp(self):
        self.r = RepoBuilder()

    def tearDown(self):
        self.r.destroy()

    def test_uncommitted_anchor_change_is_reported_as_touched(self):
        self.r.write("src/ingest.ts", "export function ingestLesson() {}")
        self.r.write("docs/a.md", "# A\n" + STAMP + "\n")
        self.r.register([{"path": "docs/a.md", "provenance": "curated",
                          "update_mode": "supersede", "verified_sha": "PLACEHOLDER",
                          "anchors": {"paths": ["src/ingest.ts"]}}])
        sha = self.r.git_init()
        reg = self.r.root / "docs/doc-register.json"
        reg.write_text(reg.read_text().replace("PLACEHOLDER", sha), encoding="utf-8")
        code, payload = self.r.run()
        self.assertEqual(code, 0, payload)

        (self.r.root / "src/ingest.ts").write_text("export function ingestLesson2() {}")
        code, payload = self.r.run()
        touched = [f for f in payload["findings"] if f["kind"] == "touched"]
        self.assertTrue(touched, payload)
        self.assertIn("WORKING TREE", touched[0]["detail"])
        self.assertEqual(code, 2, payload)

    def test_an_uncommitted_rename_reports_both_paths(self):
        self.r.write("src/ingest.ts", "export function ingestLesson() {}")
        self.r.write("docs/a.md", "# A\n" + STAMP + "\n")
        self.r.register([{"path": "docs/a.md", "provenance": "curated",
                          "update_mode": "supersede", "verified_sha": "PLACEHOLDER",
                          "anchors": {"paths": ["src/ingest.ts", "src/renamed.ts"]}}])
        sha = self.r.git_init()
        reg = self.r.root / "docs/doc-register.json"
        reg.write_text(reg.read_text().replace("PLACEHOLDER", sha), encoding="utf-8")
        subprocess.run(["git", "mv", "src/ingest.ts", "src/renamed.ts"],
                       cwd=self.r.root, check=True)
        _, payload = self.r.run()
        detail = " ".join(f["detail"] for f in payload["findings"] if f["kind"] == "touched")
        self.assertIn("src/renamed.ts", detail)
        self.assertIn("src/ingest.ts", detail)


class CheckerVersionTests(unittest.TestCase):
    def setUp(self):
        self.r = RepoBuilder()
        self.r.write("docs/a.md", "# A\n")

    def tearDown(self):
        self.r.destroy()

    def test_drift_from_the_canonical_checker_is_suspect(self):
        payload = {"version": 2, "checker_version": "0.0.1",
                   "docs": [{"path": "docs/a.md", "provenance": "curated",
                             "update_mode": "frozen", "verified_sha": "0" * 40,
                             "anchors": {}}]}
        self.r.write("docs/doc-register.json", json.dumps(payload, indent=2))
        code, out = self.r.run()
        self.assertIn("checker-version-drift", self.r.kinds(out), out)
        self.assertEqual(code, 2, out)

    def test_an_undeclared_version_never_gates(self):
        payload = {"version": 2,
                   "docs": [{"path": "docs/a.md", "provenance": "curated",
                             "update_mode": "frozen", "verified_sha": "0" * 40,
                             "anchors": {}}]}
        self.r.write("docs/doc-register.json", json.dumps(payload, indent=2))
        code, out = self.r.run()
        self.assertIn("checker-version-undeclared", self.r.kinds(out), out)
        self.assertEqual(code, 0, out)


class StubTests(unittest.TestCase):
    """A full bootstrap is what made this skill too expensive to have ever been run
    in any repo on this machine. The stub is the cheap first contact."""

    def setUp(self):
        self.r = RepoBuilder()

    def tearDown(self):
        self.r.destroy()

    def test_stub_covers_discovered_docs_and_cannot_gate(self):
        self.r.write("README.md", "# R")
        self.r.write("docs/guide.md", "# G")
        code, _ = self.r.run("--emit-stub")
        self.assertEqual(code, 0)
        reg = json.loads((self.r.root / "docs/doc-register.json").read_text())
        paths = {d["path"] for d in reg["docs"]}
        self.assertEqual(paths, {"README.md", "docs/guide.md"}, reg)
        self.assertTrue(all(d["provenance"] == "harvested" for d in reg["docs"]), reg)
        self.assertTrue(reg["provisional"])

    def test_stub_never_registers_a_record(self):
        self.r.write("README.md", "# R")
        self.r.write("CHANGELOG.md", "# C")
        self.r.write("project-lessons-learned.md", "# L")
        self.r.run("--emit-stub")
        reg = json.loads((self.r.root / "docs/doc-register.json").read_text())
        self.assertEqual({d["path"] for d in reg["docs"]}, {"README.md"}, reg)

    def test_stub_guesses_hybrid_for_a_backlog(self):
        self.r.write("project-backlog.md", "# B")
        self.r.run("--emit-stub")
        reg = json.loads((self.r.root / "docs/doc-register.json").read_text())
        mode = next(d["update_mode"] for d in reg["docs"] if d["path"] == "project-backlog.md")
        self.assertEqual(mode, "hybrid")

    def test_stub_refuses_to_overwrite_curated_work(self):
        self.r.write("README.md", "# R")
        self.r.register([{"path": "README.md", "provenance": "curated",
                          "verified_sha": "0" * 40, "anchors": {"paths": ["README.md"]}}])
        code, _ = self.r.run("--emit-stub")
        self.assertEqual(code, 3)


if __name__ == "__main__":
    unittest.main()
