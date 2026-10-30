# /compliance - report, cross-repo sweep, SITREP

## Audit / docs report

`.compliance-reports/COMP-<YYYYMMDD-HHMM>.md`.

```markdown
# Compliance Report: <project>
**Mode:** audit | docs | sweep
**Frameworks (applicable):** <detected + why>
**DISCLAIMER: assessment, not legal certification. Drafts need qualified review.**

## Data map
| Data | Category | Collected where | Rests where | Shared with |

## Findings
### <id> - <title>  [severity]
**Fails:** <framework Art./control cited>
**Evidence:** <the actual behaviour, vs the policy claim if they conflict>
**Remediation:** <concrete fix>

## Documents
| Doc | Status | Human-input fields flagged |
| privacy policy | draft generated | retention periods, DPO contact |

## Gaps (for an assessment)
- <required doc/control not present> - <what it takes>
```

## The cross-repo sweep (`--sweep`)

The recurring security pass across repos. Per repo, in report-only fashion:

1. Run `/sec-ship --audit` - security findings
2. Run `/deps --security` - advisories
3. Note last `/monitor` and `/gh-ship` state if present

Aggregate into one table: repo, security findings by severity, dep advisories, last audited. **Never
fixes across repos** - it surfaces which repos need a deliberate `/sec-ship` run. This is the
"where do I point my attention this week" report, not an action.

```
Repo             sec  deps  last audited
app-a            0    1H    2026-07-20
app-b            2M   0     never  <- attend here
```

## SITREP

Applicable frameworks and the disclaimer first. Then findings by severity with their citations, then
the document status, then (for a sweep) the per-repo table with the repos needing attention flagged.

### Suggested next

| Outcome | Recommend |
|---|---|
| Findings map to code issues | `/sec-ship` (fix) for the security ones |
| Policy contradicts behaviour | fix the behaviour or the policy - the audit says which is wrong |
| Docs drafted | route to a qualified reviewer; do not treat as final |
| Sweep flagged a repo | `/sec-ship` in that repo specifically |
| HIPAA/PCI in scope | human expert review - this skill does not certify |

## Design notes

**Cite the obligation.** A compliance finding without the article or control it fails is an opinion.
The citation is what makes it actionable and defensible.

**Behaviour over claims.** The highest-value finding is where the code and the stated policy disagree -
that is the gap a regulator or plaintiff finds first. Auditing the policy against the code, not just
reading the policy, is the point.

**Generate from truth.** A templated policy that describes an idealised system the code does not
implement is a liability. Documents are generated from the data map and the real behaviour.

**Not legal advice, stated every time.** The consolidation makes this skill broad; the disclaimer
keeps it honest about where assessment ends and qualified review begins.
