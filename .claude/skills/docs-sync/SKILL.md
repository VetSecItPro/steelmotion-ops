---
name: docs-sync
description: "Keep a repo's documentation true to its code using a per-repo document register: each doc records the ANCHORS its claims depend on (resolved paths, symbols, commands, config keys, counts), so staleness becomes a mechanical check that can sit in a merge gate. Runs in ANY repo - a repo with no register gets a provisional one on first contact. Discovers which documents the work in hand actually invalidated, repairs only those, SUPERSEDES a live claim rather than appending to it, stamps every document it writes with the date and time, and reports a SITREP. Distinct from /docs, which generates documentation; this one reconciles what exists against reality."
when_to_use: 'Trigger phrases: "update the docs", "update docs", "update whatever documents this touched", "update the applicable documents", "record what we did", "reflect the work in the docs", "are my docs current", "sync the docs", "update the documentation for what we just did", "what docs did this change affect", "doc register", "stale references", "which documents need updating". Run after work lands, in any repo, with or without a register. THIS IS THE UPDATE-DOCS SKILL - there is no separate /update-docs, and a second one must not be created. It reconciles LIVE documents against the code and never rewrites records; appending a new record (changelog entry, backlog DONE row, lessons entry, ADR) belongs to /gh-ship Stage 2.5, or to /worklog for the session journal. For generating missing documentation use /docs.'
---

# /docs-sync - reconcile documentation against reality

**Spine. Survives compaction.** Detail beside it:

| File | Read at | Holds |
|---|---|---|
| `curation.md` | Phase 1 and Phase 3 | what may become an anchor, how to classify a document, and the six ways this has gone wrong |
| `reference.md` | Phase 0 and Phase 6 | register schema v2, finding kinds, exit codes, stamp format, SITREP format |

**Standards inherited:** [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) ·
[Steel Discipline](~/.claude/standards/STEEL_DISCIPLINE.md) ·
[Status Updates](~/.claude/standards/STATUS_UPDATES.md) ·
[Sitrep Format](~/.claude/standards/SITREP_FORMAT.md) ·
[Context Management](~/.claude/standards/CONTEXT_MANAGEMENT.md) ·
[Skill Auto-Suggest](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md)

## The one idea

**Prose cannot be checked. Claims that point at the repo can.** The register records, per document,
the anchors its claims depend on. Reading a doc to extract those anchors happens ONCE. After that,
staleness is arithmetic: does this path still exist, is this symbol still exported, does this npm
script still exist, does this count still hold. That is what lets a merge gate enforce it, because
you cannot put a model in a merge gate.

## The second idea: how a document absorbs new work

**Every document is one of four things, and the register says which.** Get this wrong and the
document rots in one of two opposite directions, both of which look like diligence at the time.

| `update_mode` | What it is | What you do to it |
|---|---|---|
| `supersede` | a LIVE claim: a README, an architecture overview, a status doc, a runbook | **Replace the old text in place.** The new truth occupies the same lines the old one did. |
| `hybrid` | a live doc with named append-only sections: a backlog (Open rows flip status in place, Done only ever gains rows) | Supersede everywhere EXCEPT the headings named in `append_sections`. |
| `append` | a RECORD: a changelog, a dated audit, a worklog | **New entries only.** Never edit an existing one. |
| `frozen` | an ADR, a decision log, prose that is the product | **Never written by this skill.** Findings go to the SITREP as proposals. |

**A live document must never become a pile of appends.** Operator directive 2026-09-10: if the new
work supersedes what the document already claims, the old claim is REPLACED, not annotated beneath.
A 20,000-word file that nobody reads to the bottom of is not a record of diligence, it is a document
that stopped being true at paragraph four and kept going. `max_lines` on a `supersede` document
reports SUSPECT `bloat` precisely so this is caught while it is still fixable, and the repair is
always to replace superseded claims, never to raise the ceiling.

**And the opposite failure is worse.** A record states what was true on its date; correcting one to
match today destroys the only thing it is for. That is why `append` and `frozen` exist, and why the
checker refuses to ask a record for a stamp or hold it to a line ceiling.

## The third idea: every write is dated

**Any document this skill writes to carries a stamp, in Central time.** Two levels, both required:

1. **Document level**, machine-checkable, one per document, at the foot of the file:
   `<!-- docs-sync: reconciled YYYY-MM-DD HH:MM CT | mode: <update_mode> | against: <sha> -->`
   An HTML comment on purpose: invisible in rendered markdown, so nobody deletes it as clutter.
2. **Line level**, human-visible, on the thing that actually changed:
   - a superseded claim gains a trailing ` (updated YYYY-MM-DD HH:MM CT)`
   - an appended entry LEADS with `YYYY-MM-DD HH:MM CT`
   - a status flip in a backlog row records the completion time, per the global pairing rule

The stamp and the register are two independent records of the same event. **When they disagree, one
is wrong and the run says so** rather than the register asserting a reconciliation nothing in the
document corroborates.

## Critical rules

1. **CURATED, NEVER HARVESTED.** An anchor is what a document instructs you to RUN or READ. It is
   never what the document merely mentions. Regex extraction from prose reproduces every false
   positive a naive grep makes and then launders them into a register that claims arithmetic
   certainty. **A harvested anchor is a guess wearing a schema.** See `curation.md`.
2. **RECORDS ARE NEVER FRESHENED.** An ADR, a changelog entry, a dated audit, a worklog entry and an
   append-only history section each state what was true on their date. **A stale number in a LIVE
   document is a defect; the same number in a DATED record is evidence.**
3. **REPAIR ONLY WHAT THE CHANGE INVALIDATED.** Never rewrite a document wholesale because one anchor
   moved. The blast radius of this skill is the diff that made a doc suspect, and nothing else. **A
   document the work did not touch is left alone and reported as left alone** - that is a result, not
   an omission.
4. **NEVER EDIT A DOCUMENT TO MAKE THE GATE GREEN.** If a finding cannot be repaired without
   deleting meaning, the finding is wrong. Fix the register, not the document. This rule exists
   because a draft register once turned a naming rule's own counter-examples into build failures,
   and the proposed remedy would have deleted the rule's worked examples.
5. **VERIFY BY RE-RUNNING, NOT BY REASONING.** Done means the checker exits 0 on a fresh run. A
   repair you believe is correct and have not re-checked is not done (Steel Principle 1).
6. **THE GATE ANNOUNCES WHAT IT CANNOT DO.** A register with no curated docs, a provisional register,
   a declared field nothing enforces, a count that does not say what it counts, a vendored checker
   whose version has drifted: each reports itself on every run. A documented trap is not a control,
   and an advisory gate that looks like a real one is worse than no gate because the badge stays green.

## Modes

```
/docs-sync                 check, then repair what recent work invalidated, then SITREP
/docs-sync --audit         report only, change nothing
/docs-sync --bootstrap     curate a register properly (expensive, once per repo)
/docs-sync --since <ref>   scope the suspect set to work since a sha, tag or date
/docs-sync --doc <path>    one document only
/docs-sync --consolidate   PROPOSE a docs layout change; never moves a file without approval
```

The checker underneath takes `--root`, `--register`, `--json`, `--strict`, `--allow-empty`,
`--emit-stub` and `--no-auto-bootstrap`. Run `check-docs.py --version` before trusting any output
from a vendored copy.

## Phases

**Phase 0 - Detect.** Find the register: `--register` if given, else `docs/doc-register.json`, else
a single root-level `*DOC-REGISTER*.json`. **Two candidates is a STOP, not a pick.** Read the repo's
own conventions first - file naming, where docs live, whether a `docs/` tree exists. **Adopt the
layout, never impose one.**

**No register? Do not stop.** Run `check-docs.py --emit-stub`. That writes a provisional register
covering every discovered document, all `provenance: harvested` and anchorless, so it cannot fail a
build and says so on every run. Then carry on into Phase 2 and curate anchors ONLY for the documents
the work in hand touched. **Incremental curation is the design.** A full bootstrap is why this skill,
written 2026-08-31, had never been run against a register in any repo on this machine as of
2026-09-10: the cheapest path to value was too expensive to take.

**Phase 1 - Curate** (with `--bootstrap`, or incrementally on any run). Classify each document as
`supersede` / `hybrid` / `append` / `frozen` per `curation.md`, write `owns` in one line, then curate
anchors. Expensive and resumable: commit the register incrementally so a context death costs one
document, not the pass. Every anchor stays `provenance: harvested` until confirmed, and harvested
anchors cannot fail a build.

**Phase 2 - Check.** Run the checker. It is mechanical and costs no model tokens. Broken anchors are
proof; suspect anchors are a question; INFO is neither. **The suspect set includes uncommitted work**,
because the normal way to use this skill is: do the work, reconcile the docs, then commit.

**Phase 3 - Repair.** For each broken or suspect document: read it, read the diff of its anchors
since `verified_sha` and in the working tree, and change only what that diff invalidated, in the way
`update_mode` dictates. Verify each repaired claim against the repo - a path is resolved, a command
is found in the manifest, a count is recounted. Stamp the document. If repair would require deleting
meaning, stop and report it as a register defect instead (rule 4).

**Phase 4 - Re-verify.** Re-run the checker. Exit 0 or the work is not done.

**Phase 5 - Register update.** Anchors follow the code: a renamed script, symbol or key updates the
anchor as well as the prose, or the next run reports the repair as a new break. Bump `verified_at` and
`verified_sha` for repaired documents ONLY - never bulk-stamp, because a doc nobody looked at must keep
reporting as unverified.

**Stamping takes two commits, and the order is not optional.** Commit the doc repair and the anchor
changes first, then read the resulting sha, write it into the register, and commit that. Stamping
before committing writes a sha that is not in history, which the checker correctly reports as
`unverified` - so the repair looks unfinished even though it is done.

**Phase 6 - SITREP.** Documents updated and what drove each, documents deliberately left alone with
the reason, findings that are register defects rather than doc defects, and anything still broken.
Format in `reference.md`.

## Definition of done

Checker exits 0 on a fresh run; every repaired claim was verified against the repo rather than
reasoned about; every written document carries a current stamp; no record was freshened; no live
document was appended to where it should have been superseded; no document was edited to silence a
gate; the register carries new shas only for documents actually reviewed; SITREP delivered.

<!-- docs-sync: reconciled 2026-09-10 08:50 CT | mode: supersede | against: 7a8c6b6 -->
