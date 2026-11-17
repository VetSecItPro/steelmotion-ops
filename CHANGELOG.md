# Changelog

All notable changes to this skill collection. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## 2026-11-17

### Added
- `scripts/sync_from_live.py`: rebuilds `.claude/` from the maintainer's live setup, cleaned for the public, so this copy no longer drifts by hand.
- `scripts/leak_check.py` and `tests/`: a leak check that every planted case must trip, run in CI on every pull request.
- `/architecture-survey`; `/brainstorm` as a skill folder (it was a command).
- Standards `DOMAIN_LANGUAGE` and `BACKLOG_STANDARD`; helper scripts `ci-local.sh`, `generate-skill-router.py`, `check-skill-router.sh`; a backlog template; the `readonly-verifier` and `scoped-implementer` agents.
- README section on what is not included.

### Changed
- Every skill, command and standard synced to the version in daily use.
- `install.sh` copies anything it replaces to `~/.claude/.steelmotion-ops-backup-<timestamp>/` first, and installs the helper scripts and agents.
- `/gh-ship` runs gitleaks itself when no global pre-commit hook does.

### Fixed
- Links to `steelmotion.dev`, a domain the company does not own, now point to steelmotionllc.com.

## 2026-10-29

### Changed
- Skills moved to folders under `.claude/skills/`; the content, marketing and lead-generation skills and the chain wrappers were retired.
