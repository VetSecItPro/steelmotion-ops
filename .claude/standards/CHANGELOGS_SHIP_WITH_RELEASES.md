# Changelogs Ship With Releases - reference

> Extracted from `~/.claude/CLAUDE.md` on 2026-07-28. The RULE stays in CLAUDE.md so it applies on
> every session; this file holds the reference detail, which is only needed when you are
> actually doing the thing. CLAUDE.md is loaded in full on every session in every project,
> so reference material there is paid for permanently.

---

## Changelogs Ship With Releases (GLOBAL - ALL PROJECTS)

**Every repo that ships a versioned artifact maintains a changelog at its root.** Default filename is `CHANGELOG.md`. When working across multiple sibling repos that all have changelogs, prefix the filename with a 2-3 letter repo identifier so they're disambiguated in editor tabs / IDE search (e.g. `MC-CHANGELOG.md` for mission-control, `COS-CHANGELOG.md` for infra-repo/customer-pod-suite). Single-repo projects: just `CHANGELOG.md`.

The shipped artifact is whatever's pinned by consumers - Docker image tag, npm version, git SHA referenced in another repo's lockfile, anything that someone else depends on by version.

### What counts as "shipping a versioned artifact"

- Docker images published to a registry (GHCR, Docker Hub, ECR)
- npm packages published to a registry
- Tag-based releases used as deploy targets (`v1.2.3`)
- SHA-pinned references from other repos (e.g. `customer-template/image-versions.conf` pinning a specific MC SHA)

### Format

[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) - Added/Changed/Deprecated/Removed/Fixed/Security sections per version. Latest at top. Each version section starts with the **identifier consumers actually pin** (image tag, SHA prefix, version number), followed by the date.

### Update protocol

- **Same PR, same change.** A PR that bumps a version, modifies customer-visible behavior, or fixes a customer-visible regression updates `CHANGELOG.md` in the same PR. Like the "Tests Ship With Code" rule but for release notes.
- **Use an "Unreleased" section** to accumulate changes between publishes. When the artifact publishes, rename "Unreleased" to the new version and reset.
- **Internal refactors, doc fixes, test-only changes:** optional. One-line entry is fine if you want the trail; skip otherwise.
- **Backfill once, maintain forever.** When bootstrapping a CHANGELOG on an existing repo, mine `git log` for the prior 30 days. Don't try to backfill years.

### What CHANGELOG is NOT

- It's not the git log. The git log is per-commit; CHANGELOG is per-release.
- It's not the daily-log session journal. That's `*-backlog.md` (gitignored) - a working memory for you. CHANGELOG is for consumers (anyone reading the repo cold, including future-you).
- It's not the ADR file. ADRs answer "why we made this decision." CHANGELOG answers "what's in this version." Cross-link from CHANGELOG entries to ADRs by reference.

### Where the info actually lives

The single source of truth depends on the question being asked:

| Question | Look at |
|---|---|
| "What changed between sm4 and sm5?" | Repo's changelog (`COS-CHANGELOG.md` / `MC-CHANGELOG.md` / `CHANGELOG.md`) |
| "Why did we choose 3-container architecture?" | ADRs (`docs/decisions.md`) |
| "How do I re-apply Patch 5 after an upgrade?" | Per-patch playbook (e.g. `docs/vendor-patches.md`) |
| "What broke in production last week?" | `LESSONS-LEARNED.md` (gitignored, project-root) |
| "What did I work on yesterday?" | `*-backlog.md` § Daily log (gitignored) |
| "What does this commit do?" | `git log` / PR description |
| "What's pinned in production right now?" | `customer-template/image-versions.conf` (or equivalent lockfile) |
