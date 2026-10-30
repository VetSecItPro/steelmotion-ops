---
name: compliance
description: "Privacy, data-protection and security-compliance work in one skill: audit against GDPR/CCPA/HIPAA/SOC2 as applicable, generate the policy and readiness documents an assessment needs, and run the recurring cross-repo security sweep. Consolidates the former /compliance, /compliance-docs and /sec-weekly-scan; sec-ship owns the scanning half."
when_to_use: 'Trigger phrases: "compliance audit", "GDPR", "CCPA", "HIPAA", "SOC2", "privacy audit", "data compliance", "generate compliance docs", "privacy policy", "weekly security scan", "audit all repos". Run before handling regulated data, before an assessment, and on a schedule for the cross-repo sweep.'
---

# /compliance - privacy, data protection, and security compliance

**Spine. Survives compaction.** Detail beside it:

| File | Read at | Holds |
|---|---|---|
| `frameworks.md` | audit mode | GDPR / CCPA / HIPAA / SOC2 requirements and how to check each |
| `docs.md` | docs mode | the policy and readiness documents, what each must contain |
| `reference.md` | report | report format, the cross-repo sweep, SITREP |

**Standards inherited:** [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) ·
[Steel Discipline](~/.claude/standards/STEEL_DISCIPLINE.md) ·
[Self-Improvement](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) ·
[Multi-Repo Awareness](~/.claude/standards/MULTI_REPO_AWARENESS.md) ·
[Status Updates](~/.claude/standards/STATUS_UPDATES.md) ·
[Skill Auto-Suggest](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) ·
[Context Management](~/.claude/standards/CONTEXT_MANAGEMENT.md) ·
[Sitrep Format](~/.claude/standards/SITREP_FORMAT.md) ·
[Agent Orchestration](~/.claude/standards/AGENT_ORCHESTRATION.md) ·
[Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md)

## What this consolidates

Three former skills, merged because they overlapped and each was mostly unused:

- **audit** (was `/compliance`) - assess the code and data handling against a framework
- **docs** (was `/compliance-docs`) - generate the policies and readiness artefacts an assessment needs
- **sweep** (was `/sec-weekly-scan`) - the recurring cross-repo security pass

The scanning half now lives in `/sec-ship` (which this calls, not duplicates). This skill is the
compliance layer on top: mapping findings to obligations, producing the paperwork, and running the
periodic sweep.

## The honest scope line

This skill assesses and documents. **It is not legal advice, and a generated policy is a starting
draft a qualified reviewer must check** - especially for HIPAA, PCI and anything with real regulatory
teeth. It gets you to a reviewable draft and a gap list fast; it does not certify compliance. Say so
in every report.

## Modes

```
/compliance --audit <fw>    audit against a framework (gdpr | ccpa | hipaa | soc2)
/compliance --docs <what>   generate a policy or readiness doc (privacy-policy | dpa | soc2-readiness | ...)
/compliance --sweep         cross-repo security sweep (orchestrates /sec-ship + /deps per repo)
/compliance                 detect what applies, audit it, list the doc gaps
```

Bare `/compliance` detects which frameworks apply from the data the app handles (PII -> GDPR/CCPA;
health data -> HIPAA; selling to enterprise -> SOC2) and audits those, then reports which required
documents are missing.

## Critical rules

1. **Map to the actual obligation, cite the article.** "Missing consent" is not a finding; "no
   Art. 6 legal basis recorded for the email-tracking processing" is. Every finding names the
   requirement it fails.
2. **Verify against real behaviour, not the policy's claims.** If the privacy policy says "we do not
   share data", confirm the code does not. A policy that contradicts the code is worse than none.
3. **Detect what applies; do not audit against everything.** A free internal tool is not subject to
   HIPAA. Auditing against an irrelevant framework produces noise that buries the real gaps.
4. **A generated document is a draft.** Marked as such, with the fields that need human/legal input
   flagged, never presented as final or as advice.
5. **The sweep reports, per repo, and never fixes across repos silently.** It surfaces state; fixing
   is a deliberate per-repo `/sec-ship` run.
6. **Where the project keeps compliance deliverables already** (a threat model, an SSP, a controls
   matrix in the repo), update THOSE rather than generating a parallel set. Do not fork the source of
   truth.

## Definition of done

- **audit:** applicable frameworks identified; each requirement checked against real behaviour; gaps
  listed with the article/control they fail and a remediation
- **docs:** the requested document generated as a reviewable draft, human-input fields flagged, placed
  where the project keeps its compliance artefacts
- **sweep:** every repo's security state reported (via `/sec-ship`/`/deps`), nothing changed silently
- Every output states plainly that it is assessment, not legal certification
- Report written; SITREP ends with "Suggested next"
