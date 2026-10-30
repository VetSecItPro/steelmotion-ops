# Reference - schema, finding kinds, exit codes, stamps, SITREP

## Where the register lives

Search order, implemented in `discover_register()`:

1. `--register <path>` if given.
2. `<repo>/docs/doc-register.json`.
3. A single root-level `*DOC-REGISTER*.json` or `*doc-register*.json`.
4. **Two or more root-level candidates is exit 3 naming both.** Never a pick. Which document set
   governs a repo is not a thing to guess at.

**Adopt the repo's file-naming convention.** A repo whose house rule is domain-prefixed names gets
`ACME-DOC-REGISTER.json` at root, not a new `docs/` tree invented for one file - a half-populated
`docs/` invites someone to consolidate into it later.

## Schema, version 2

```json
{
  "version": 2,
  "checker_version": "2.0.0",
  "repo": "17.scratchpad",
  "doc_roots": ["."],
  "ignore": ["CHANGELOG.md", "**/adr/**", "*-lessons-learned.md"],
  "docs": [
    {
      "path": "project-backlog.md",
      "owns": "the durable half of the todo list",
      "provenance": "curated",
      "update_mode": "hybrid",
      "append_sections": ["Done"],
      "max_lines": 400,
      "verified_at": "2026-09-10",
      "verified_sha": "0de14f6",
      "anchors": {
        "paths":    ["scripts/check-completeness.py"],
        "symbols":  ["ingestLesson"],
        "commands": ["npm run ingest", "make deploy", "python3 scripts/x.py"],
        "config":   ["INGEST_BATCH_SIZE"],
        "counts":   [{"claim": "35 modules", "kind": "dir_with", "contains": "*.tf",
                      "source": "infra/modules/*/", "expect": 35}]
      }
    }
  ]
}
```

`owns` is one line and doubles as a duplication check: two documents claiming the same scope is how
contradictions get in. **Any field the checker does not act on reports itself as
`declared-not-enforced` on every run**, so a schema addition nobody wires up cannot rot into a
believed guard.

### `update_mode`, required on every curated document

| Value | Written how | Stamp required | `max_lines` enforced |
|---|---|---|---|
| `supersede` | old text replaced in place | yes | yes |
| `hybrid` | superseded except under `append_sections` | yes | yes |
| `append` | new entries only, existing never edited | no | no - a record is supposed to grow |
| `frozen` | never written; findings become SITREP proposals | no | no |

`hybrid` **requires** `append_sections`, and every heading it names must exist in the document.
Unnamed, hybrid is an unbounded licence to append to a live document, which is the failure the mode
exists to prevent; naming a heading that has since moved protects nothing and reports green.

`checker_version` is compared against the running checker's own `VERSION`. CI runs a copy vendored
into the repo, which cannot see `~/.claude` and therefore drifts silently, and a green run from a
stale checker is a green run of the wrong checks.

## The stamp

```
<!-- docs-sync: reconciled YYYY-MM-DD HH:MM CT | mode: supersede | against: 0de14f6 -->
```

One per document, at the foot, on every `supersede` and `hybrid` doc. Central time always, per the
global time-zone rule. Checked for: presence, parseability, not being in the future, not predating
the register's own `verified_at`, and not being duplicated.

Line-level stamps are prose, not machine-checked: a superseded claim gains a trailing
`(updated YYYY-MM-DD HH:MM CT)`, an appended entry leads with the timestamp.

## Exit codes - the CI contract

| Code | Meaning | Gate |
|---|---|---|
| 0 | clean | pass |
| 1 | BROKEN anchor, or a register that cannot fail | **FAIL** |
| 2 | SUSPECT only | pass, write findings to the job summary |
| 3 | register missing, malformed, or ambiguous | **FAIL** |

Suspect must not block. A gate that fails every pull request touching a documented file trains people
to disable it, and a disabled gate is worse than none because the badge stays green.

`fetch-depth: 0` is load-bearing in CI: the touched-anchor detector diffs `verified_sha..HEAD`, and
under a depth-1 clone every doc degrades to unverified without saying why.

CI should pass `--no-auto-bootstrap`, so a missing register fails loudly instead of being papered
over by a provisional one.

## Finding kinds

**BROKEN** (proof, gates the build)
`path` · `symbol` · `command` · `config` · `count` · `missing-doc` · `update-mode-invalid` ·
`append-sections-missing` · `append-section-missing` · `stamp-missing` (on a doc the register claims
was reconciled) · `stamp-malformed` · `stamp-future` · `verified-at-malformed` ·
`max-lines-invalid` · `vacuous-register`

**SUSPECT** (a question, never gates)
`touched` · `unverified` · `orphan` · `overlap` · `count-unqualified` · `unresolved-basename` ·
`ambiguous-basename` · `no-curated-docs` · `update-mode-undeclared` · `stamp-missing` (on a doc never
reconciled) · `stamp-behind` · `stamp-duplicated` · `bloat` · `checker-version-drift`

**INFO** (never gates, always printed)
`path-generated` · `observation-drifted` · `declared-not-enforced` · `checker-version-undeclared`

## First contact with a repo that has no register

```
python3 check-docs.py --emit-stub
```

Writes a provisional register covering every discovered document, all `provenance: harvested`, no
anchors, `provisional: true`. It cannot fail a build and announces that on every run. Records
(changelogs, lessons files, ADRs, worklogs) are never registered. A backlog-shaped filename is
guessed as `hybrid`; every other guess is `supersede`. **Curate anchors for the documents the work in
hand touches, not for all of them at once** - a full bootstrap is why this skill was never once run
against a real register between 2026-08-31 and 2026-09-10.

## SITREP

```
DOCS-SYNC - <repo> - <date time CT>

UPDATED       <doc> - <what changed, which anchor drove it, superseded or appended>
LEFT ALONE    <doc> - <why: record, frozen, generated, untouched by this work>
REGISTER      <anchors added / removed / re-stamped, and for which docs>
NOT FIXED     <finding> - <why, and what it needs>
VERIFIED      checker exit <n> on a fresh run at <sha>
```

Report the denominator, never a bare count: "3 of 28 anchors" rather than "3 findings". A count
without its denominator is the failure the global rule in `~/.claude/CLAUDE.md` names, and this skill is
made of counts.

<!-- docs-sync: reconciled 2026-09-10 08:50 CT | mode: supersede | against: 7a8c6b6 -->
