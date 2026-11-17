"""Known-answer tests for the leak check and the sync cleaning: every pattern must catch a planted case
and pass a clean one, so a silently broken pattern cannot report a clean tree."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import leak_check  # noqa: E402
import sync_from_live  # noqa: E402

PLANTED = {
    "home folder path": "see /Users/someone/projects/app",
    "personal email": "write to someone@gmail.com",
    "internal ticket number": "fixed in env #578",
    "Vercel project or team id": "team_AbCdEfGhIjKlMnOpQr",
    "Supabase project ref": "https://abcdefghijklmnopqrst.supabase.co",
    "private network address": "ssh to 192.168.1.20",
    "Tailscale address": "host at 100.101.102.103",
    "numbered private repo folder": "the work in 16.canvas-courses",
}
CLEAN = "Saved to 2026-11-05.json and v1.2; Next 15.x is fine. Run `bash ~/.claude/ci-local.sh`; paths like /home/runner/work and /home/app/ are placeholders."


def scan_text(text: str, terms: list[str] | None = None) -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "doc.md").write_text(text)
        return leak_check.scan(Path(tmp), leak_check.compile_patterns(terms or []))


class LeakCheckTests(unittest.TestCase):
    def test_every_public_pattern_catches_its_planted_case(self):
        self.assertEqual(set(PLANTED), set(leak_check.PUBLIC_PATTERNS), "a pattern has no planted case")
        for name, text in PLANTED.items():
            with self.subTest(name):
                self.assertEqual(scan_text(text), [f"doc.md:1: {name}"])

    def test_clean_text_passes(self):
        self.assertEqual(scan_text(CLEAN), [])

    def test_local_terms_match_whole_words_without_printing_the_term(self):
        hits = scan_text("Built for Zorblax.\nzorblaxian is fine", ["Zorblax"])
        self.assertEqual(hits, ["doc.md:1: private term"])
        self.assertNotIn("Zorblax", " ".join(hits))

    def test_an_empty_tree_is_refused_not_called_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(leak_check.main(["leak_check", tmp]), 1)

    def test_the_published_tree_is_clean(self):
        hits = leak_check.scan(ROOT, leak_check.compile_patterns(leak_check.load_local_terms(ROOT)))
        self.assertEqual(hits, [])


class CleaningTests(unittest.TestCase):
    def test_ticket_asides_and_mentions_go_and_dates_stay(self):
        clean = lambda t: sync_from_live.clean(t, [])
        self.assertEqual(clean("**Cost guards (env #578, 2026-11-05).** CI"), "**Cost guards.** CI")
        self.assertEqual(clean("(gitignored, env #573, 2026-11-05)"), "(gitignored, 2026-11-05)")
        self.assertEqual(clean("(MIT), env #415."), "(MIT).")
        self.assertEqual(clean("see ~/vibecode-projects/x"), "see ~/projects/x")
        self.assertEqual(clean("no tickets here, 2026"), "no tickets here, 2026")

    def test_local_rules_apply_after_generic_ones(self):
        self.assertEqual(sync_from_live.clean("the Zorblax repo", [(r"Zorblax", "example")]), "the example repo")

    def test_router_keeps_only_published_rows(self):
        text = "| `/a11y` | skills/ | x |\n| `/private` | skills/ | y |\nprose\n"
        self.assertEqual(sync_from_live.router_rows_for(text, {"a11y"}), "| `/a11y` | skills/ | x |\nprose\n")

    def test_manifest_and_tree_agree(self):
        manifest = json.loads((ROOT / "scripts" / "sync-manifest.json").read_text())
        for skill in manifest["skills"]:
            self.assertTrue((ROOT / ".claude" / "skills" / skill / "SKILL.md").exists(), skill)
        for command in manifest["commands"]:
            self.assertTrue((ROOT / ".claude" / "commands" / f"{command}.md").exists(), command)
        for standard in manifest["standards"]:
            self.assertTrue((ROOT / ".claude" / "standards" / f"{standard}.md").exists(), standard)
        for tool in manifest["tools"]:
            self.assertTrue((ROOT / ".claude" / tool).exists(), tool)
        published = {p.name for p in (ROOT / ".claude" / "skills").iterdir() if p.is_dir()}
        self.assertEqual(published, set(manifest["skills"]), "a skill folder is not in the manifest")


if __name__ == "__main__":
    unittest.main()
