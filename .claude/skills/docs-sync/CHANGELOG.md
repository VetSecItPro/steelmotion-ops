# Changelog - check-docs.py

The version consumers pin is the string `check-docs.py --version` reports. A copy of this script is
vendored into each repo that uses it, so a repo can be behind; the version line is how you tell.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Newest first.

## [2.0.1] - 2026-09-12

### Fixed

- **Touched-anchor detection no longer reports a document stale against its own
  reconciliation.** `changed_since` now walks commit by commit and skips any commit
  that changed the document alongside its anchor, because such a commit IS the
  reconciliation. Previously a two-endpoint `git diff sha..HEAD` could not tell the
  two apart, which meant **every squash-merged documentation change landed SUSPECT
  permanently**: a stamp written on a feature branch can never name the squash-merge
  sha, since that sha does not exist yet, and the squash then carries the document
  and its anchors in one commit. No sequence of commits cleared it, because the
  commit that would clear it recreated the condition.

  The finding was non-gating, so nothing ever failed because of it. The cost was
  that the checker was permanently yellow, and a checker that is always yellow is
  one people stop reading, which spends the credibility of the real findings beside
  it. Measured in `17.scratchpad` and filed there as backlog #144.

  Three tests, including one asserting that an anchor moving in a commit that leaves
  the document alone is **still** suspect, so the fix cannot become a way for real
  staleness to pass.

## [Unreleased]

Nothing yet.

## [2.0.0] - 2026-09-10

Made the tool usable. v1 was correct and had never been run against a register in any repo on this
machine: 0 of 42 project directories held one, including the busiest one. The gap was never the
detectors, it was the cost of first contact and a doctrine that said nothing about how a document
absorbs new work.

### Added
- `--emit-stub`: a provisional register for a repo that has none. Every entry `harvested` and
  anchorless, so it cannot fail a build and says so on every run. Curate anchors for the documents
  the work in hand touched, not for all of them at once.
- `update_mode` per document, required on every curated entry: `supersede` (live claim replaced in
  place), `hybrid` (live, with named `append_sections`), `append` (record, new entries only),
  `frozen` (checked, never written). Operator directive 2026-09-10: a live document must never
  become a pile of appends when the new work supersedes the old one.
- Dated stamps. `<!-- docs-sync: reconciled YYYY-MM-DD HH:MM CT | mode | against: sha -->` on every
  `supersede` and `hybrid` document, checked for presence, parse, not-in-future, not predating
  `verified_at`, and not duplicated. The stamp and the register are two independent records of the
  same event, so a disagreement between them is reported rather than silently resolved.
- `max_lines`, reported SUSPECT as `bloat` with its denominator. On a `hybrid` document it measures
  the LIVE half only: an append-only section grows by design, so a whole-file ceiling there is a
  guard guaranteed to fire for a correct reason and then be raised until it means nothing.
- `checker_version` in the register, compared against the running checker. CI cannot read
  `~/.claude`, so the checker is vendored per repo and drifts silently; a green run from a stale
  checker is a green run of the wrong checks.
- Register discovery: `--register`, then `docs/doc-register.json`, then a single root-level
  `*DOC-REGISTER*.json`. **Two candidates is exit 3 naming both, never a pick.**
- `--no-auto-bootstrap` for CI, so a missing register fails loudly.
- 32 tests, 73 total, all passing.

### Changed
- Touched-anchor detection now includes the working tree, reported SEPARATELY from committed
  changes. The skill is used after the work and before the commit, which is exactly where a
  `verified_sha..HEAD` diff is blind. Renames report both paths.
- `docs-check.workflow.yml` is repo-agnostic. It shipped as the generic template while hardcoding
  `scripts/canvas-check-docs.py` and `CANVAS-DOC-REGISTER.json` in four places.
- `review: manual` is retired in favour of `update_mode: frozen`.

### Fixed
- `REGISTER_BASENAME` was declared and never referenced while `reference.md` documented a two-step
  search order, so the documented root-level naming required `--register` on every invocation. The
  `declared-not-enforced` defect this tool exists to report, living inside the tool.
- `reference.md` claimed "3 documents in this skill" against 4. Caught by the tool's own count
  detector running on its own register, which is the first time that has happened.

## [1.0.0] - 2026-08-31

First release. Mechanical documentation-staleness checker with no model in the loop, so it can sit in
a merge gate.

### Added
- Nine detectors: `path`, `symbol`, `command` (npm/pnpm/yarn/bun scripts, make targets, script paths),
  `config`, `count`, `missing-doc`, `touched`, `orphan`, `overlap`.
- Exit-code contract for CI: 0 clean, 1 broken or vacuous, 2 suspect only, 3 register missing or
  malformed.
- `provenance`: only `curated` documents can fail a build. Everything else is advisory.
- `kind: observation` counts, which report drift as INFO and never gate, for dated measurements kept
  on purpose.
- `declared-not-enforced`: any register field this gate does not act on names itself on every run.
- `no-curated-docs` and `vacuous-register`: the gate says out loud when it cannot fail.
- 41 tests, including a control for every detector in both directions.

### Deliberately not included
- **No search path.** An anchor stores the resolved repo-relative path. A resolver fallback is
  variance made permanent: a neighbouring tool lost a `scripts/` fallback in a rewrite and turned nine
  live scripts into twelve dead citations over a corpus that never changed.
- **No prose harvesting.** Anchors are curated from lines a person read. A regex harvest reproduces
  every false positive a naive grep makes: an early draft reported a naming rule's own counter-examples
  as broken paths, and the proposed remedy would have deleted the rule's worked examples.

### Known limitations
- If a document cites `README.md`, a root `README.md` exists, and the document meant
  `docs/README.md`, this resolves silently and reports clean. No walk fixes it; the information needed
  is what the sentence meant.
- `command` anchors resolve only npm-family scripts, make targets and script paths. Anything else
  reports `unresolvable` at SUSPECT rather than guessing.

### Fixed before release (each found by running it, not by reading it)
- The register was evidence for its own anchors; excluded by resolved path, not by a hardcoded name.
- A vacuous register exited 0 and printed CLEAN.
- Gitignored generated artifacts reported BROKEN, which would have made the gate red on every run.
- `find_by_basename` truncated at four matches and phrased many matches as one resolution.
- **The fallback symbol scan walked the filesystem, so an untracked scratch file could satisfy an
  anchor and make a stale document read clean - a false negative that does not reproduce in CI.**
  Now searches tracked files only when git is available.
