# Curation - what may become an anchor, and how a document absorbs work

Read this before creating or amending any register entry.

## The test

An anchor is something the document **instructs you to run or read**, and that the document would be
**wrong** about if it disappeared. Everything else is a mention.

| In the doc | Anchor? | Why |
|---|---|---|
| ``Run `scripts/build.py` before publishing`` | yes | the instruction fails if it is gone |
| ```scripts/lint.py` enforces this rule`` | yes | the doc asserts a mechanism exists |
| ``not `backlog.md` but `PROJECT-BACKLOG.md``` | **NO** | a counter-example; it is SUPPOSED to be absent |
| ``renamed `old-name.py` to `new-name.py``` | **NO** | a rename record; the absence is the fact |
| ``we used to call this `legacy.py``` | **NO** | history |
| ``never create `utils.py``` | **NO** | a prohibition |
| ``for example, `foo.json``` | **NO** | an illustration |
| ``https://example.com/a/b.html`` | **NO** | a URL, not a path |
| ```config.py` (planned)`` | **NO** | not yet real |

## The six ways this has gone wrong, all measured

1. **Specimens read as defects.** A naming rule reading "not `audit-pages.py` but
   `canvas-audit-pages.py`" produced two broken anchors. The proposed repair - edit the citation
   until CI is green - would have deleted the rule's own worked examples from the file that loads
   into every session in that repo. **A document quotes what is WRONG as often as what is right, and
   any tool that treats a mention as a dependency attacks negations and history first, because that
   is exactly where the absent things live.**
2. **Line-scoped specimen detection leaking.** A rule wrapping across four lines carries its "not X
   but Y" marker only on the first. Scope specimen suppression to the paragraph, never the line.
3. **URLs resolved as filesystem paths.** `169.254.169.254/latest/meta-data/` and any `https://` are
   not files.
4. **A resolver fallback silently changing the answer.** Dropping a `scripts/` search path during a
   rewrite turned nine live scripts into twelve dead citations over a corpus that never changed.
   **Store the RESOLVED repo-relative path in the register. Never add a search path to the checker** -
   a fallback is variance made permanent, and the register is where resolution belongs because it is
   visible and diffable there.
5. **Ambiguity resolved by guessing.** A bare `README.md` may match three files. List them and make
   the curator choose. A register carrying a confidently wrong resolved path is worse than a bare
   string, because it looks settled and diffs clean forever.

6. **A guard reordered into uselessness.** Adding working-tree detection to `check_suspect`
   2026-09-10 moved the `use_git` early-return above the `verified_sha` check, so a register with no
   recorded sha stopped being reported outside a git repo. The finding was still implemented, still
   tested, and unreachable. The suite caught it in the same pass. **"No verified_sha recorded" is a
   fact about the REGISTER and does not depend on git** - and a check placed behind an unrelated
   guard is deleted without anyone deleting it.

**Known blind spot, do not paper over it:** if a doc cites `README.md`, a root `README.md` exists,
and the doc meant `docs/README.md`, this resolves silently and reports clean. No walk fixes it; the
information needed is what the sentence meant. It is an argument for curation, since a curator
reading the line knows and a resolver cannot.

## Documents whose SUBJECT is an absent reference

The sharpest trap, because the whole file is a specimen rather than one line in it. A source register
that records what could NOT be sourced. A watch list tracking twelve external URLs precisely because
they change. An ADR describing a deliberately parked or superseded state. A rename record. In each,
**the broken reference is the content**, and a checker that resolves references will report the
document's entire purpose as decay.

Detect these at bootstrap by what the document is FOR, not by scanning it: if its own title or opening
paragraph says it tracks unavailable, external, volatile, retired, superseded or parked things,
exclude the file and record why in `ignore`. **Never register a document you would have to argue with.**

**The sharpest form: a document that records an unresolved DISAGREEMENT.** One such register holds two
research agents' contradictory positions on whether a claim appears in a primary source, unresolved on
purpose, with the instruction that nothing publishes on either agent's word. A checker that resolved
that to one answer would not be freshening a stale document - it would be deciding an open question,
and doing it silently, in a commit nobody reviewed as a decision.

## Invisible-by-convention paths

Some trees are deliberately unreachable and correct that way: an underscore prefix meaning "not for
consumption" (`_retired/`, `_draft.md`), a directory a non-recursive reader is designed to skip, a
generated tree written between sentinels. **The checker does not guess these** - dot-directories and
gitignored paths are skipped automatically, and everything else belongs in the register's `ignore`
list, captured at bootstrap by reading the repo's own conventions.

Ask the repo, not the filesystem: a load-bearing convention is nearly always written down in a
CLAUDE.md or a README, and a session that owns the repo can tell you in one sentence what a walk
would take an hour to infer wrongly.

**But a session's recollection is not verification, and this is where it bites.** The order of trust
is: (1) a read of the code that ENFORCES the convention, (2) the repo's own written conventions,
(3) what the owning session remembers. The session that told me about a `_retired/` skip knew it was
true because they had written that directory that same day and read the two scripts that skip it -
asked a week earlier they would have given the identical confident sentence and it would have been
wrong, because the path did not exist yet. **A bootstrap conversation captures what the owning
session believes, which is usually better than a filesystem walk and is not the same thing as
checked.** Where a convention will gate a build, read the enforcing code.

## Records versus live documents, and choosing `update_mode`

**This is the second classification decision, and it is made once per document, at curation time.**
Getting it wrong rots the document in one of two opposite directions, both of which look like
diligence while they happen.

Exclude wholesale, and never freshen: ADRs, CHANGELOGs, lessons-learned, worklog entries, dated
audits, per-item verdict files, and anything generated between sentinels by a script.

For everything that IS registered, pick a mode by asking one question: **when new work contradicts
what this document says, is the old text now wrong, or is it still true about its own date?**

| Answer | Mode | Examples |
|---|---|---|
| Now wrong | `supersede` | README, architecture overview, runbook, status doc, a CLAUDE.md |
| Now wrong, except under one or two named headings | `hybrid` | a backlog with a `## Done` section |
| Still true about its date | `append` | a changelog you have deliberately registered to CHECK without freshening |
| Still true, and the prose is the product | `frozen` | an ADR, a decision log, a rule file with worked examples |

**`supersede` is the default and the one that matters.** A live document that only ever gains text
has stopped being a description of the system and become a transcript of edits to it. Replace the
claim where it stands, date the line, move on.

**A file can be half record, and `hybrid` only saves the tidy case.** `hybrid` works when the
append-only material sits under its OWN heading, which the register names and the checker verifies
still exists. It does **not** save the messy case: a backlog whose live rows and dated CLOSED rows
are interleaved in one table has the row, not the heading, as its real unit, and no section scoping
reaches that. There, choose `frozen` and propose changes in the SITREP, or restructure the document
so the record half has a heading of its own - which is worth doing on its own merits.

When the unit is unclear, **exclude the whole file** and say why. A smaller register everyone trusts
beats a larger one that cries wolf.

## Ceilings

`max_lines` is a curation judgment, not a formatting rule. Set it on a `supersede` or `hybrid`
document at roughly where the document stops being readable in one sitting, and treat a `bloat`
finding as the question it is: *did this grow because the system grew, or because somebody appended
where they should have replaced?* **Raising the ceiling is the wrong repair in every case where the
answer is the second one**, which is most of them. Leave it unset rather than guess; an unset ceiling
is honest, and a ceiling nobody chose gets raised reflexively the first time it fires.

## Counts

A count anchor must declare what it counts: `file`, `dir`, or `dir_with` plus `contains`. An
unqualified count is not gated, because a directory count and a module count are different numbers -
a register once claimed 36 modules when it had counted immediate subdirectories, some of which held
no module at all.

**A dated measurement is `kind: observation`.** It reports drift as INFO and can never fail a build.
"Verified baseline, 343 pages (2026-08-12)" is not rot; it is an observation kept on purpose, and a
checker that fires on it earns deletion rather than tuning.

## Provenance

`provenance: curated` is the only value that lets a document's anchors fail a build, and it means a
human or a reading agent confirmed each one against its citing line. Everything else is advisory.

A checker's first answers about a repo are about the checker, not the repo: one such tool read 3
dead citations, then 8, then 12, then 0, over a corpus that never changed once. **Any tool that gates
on run one is gating on its own immaturity.**

<!-- docs-sync: reconciled 2026-09-10 08:50 CT | mode: supersede | against: 7a8c6b6 -->
