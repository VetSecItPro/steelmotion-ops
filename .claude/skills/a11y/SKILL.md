---
name: a11y
description: "Accessibility audit and remediation to WCAG 2.2 Level AA: automated scan, then the manual checks tooling cannot do (keyboard, screen reader, focus order, contrast in context), fix at root cause, verify, and report conformance honestly."
when_to_use: 'Trigger phrases: "accessibility", "a11y", "WCAG", "screen reader", "keyboard navigation", "contrast", "ARIA", "EAA compliance", "is this accessible". Run before launch, after a UI change, and on any surface sold into the EU.'
---

# /a11y - accessibility audit and remediation

**Spine. Survives compaction.** Detail beside it:

| File | Read at | Holds |
|---|---|---|
| `criteria.md` | Phase 2 | WCAG 2.2 AA criteria by category, what each actually requires |
| `testing.md` | Phase 1 and 3 | automated tooling per stack, and the manual protocol |
| `reference.md` | Phase 5 | report, conformance statement, SITREP |

**Standards inherited:** [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) ·
[Steel Discipline](~/.claude/standards/STEEL_DISCIPLINE.md) ·
[Self-Improvement](~/.claude/standards/SELF_IMPROVEMENT_PROTOCOL.md) ·
[Status Updates](~/.claude/standards/STATUS_UPDATES.md) ·
[Skill Auto-Suggest](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) ·
[Agent Orchestration](~/.claude/standards/AGENT_ORCHESTRATION.md) ·
[Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md) ·
[Context Management](~/.claude/standards/CONTEXT_MANAGEMENT.md) ·
[Multi-Repo Awareness](~/.claude/standards/MULTI_REPO_AWARENESS.md) ·
[SITREP Format](~/.claude/standards/SITREP_FORMAT.md) ·
[Verify Before Destroy](~/.claude/standards/VERIFY_BEFORE_DESTROY.md)

## The standard to build to

Verified 2026-09-02:

- **WCAG 2.2 Level AA is the current target.** Published October 2023; now also
  **ISO/IEC 40500:2025**. It is a superset of 2.1 - everything in 2.1 AA still applies, plus nine new
  success criteria.
- **WCAG 3.0 is NOT a compliance target.** The March 2026 Working Draft renamed "outcomes" to
  "requirements" and lists 174 of them; **Candidate Recommendation is anticipated Q4 2027 and
  Recommendation no earlier than 2028**. Do not audit against it or cite it as a requirement. WCAG
  2.2 is not deprecated when 3.0 lands: it is embedded in legislation worldwide and stays in force.
- **The WCAG 3 contrast algorithm is still undecided.** Visual contrast was moved OUT of the draft
  in July 2023 and as of April 2026 the draft records it as to-be-determined. **APCA is a candidate,
  not the answer.** Do not re-model contrast on APCA because an article says WCAG 3 uses it; if you
  want APCA, run it as a readability ceiling ABOVE the WCAG 2.2 compliance floor, never instead.
- **European Accessibility Act enforcement has been active since 28 June 2025**, transposed by all
  27 Member States. It requires conformance with **EN 301 549**, whose current version (v3.2.1)
  incorporates **WCAG 2.1 AA**. **v4.1.1 is expected to be cited in the Official Journal in October
  2026**, replacing v3.2.1 as the harmonised standard and moving the floor to WCAG 2.2 AA.
- **Enforcement is no longer theoretical.** First EAA suits filed in France November 2025;
  Netherlands audits from spring 2026. Fines range from roughly EUR 60,000 (Ireland) to EUR 900,000
  (Sweden). A finding labelled "2.2-only" stops being a nice-to-have the month v4.1.1 is cited.

The practical reading: **audit to WCAG 2.2 AA**. It satisfies the current legal floor (2.1 AA) and
the one arriving with EN 301 549 v4.1.1. Where a finding is 2.2-only, label it so the operator can
tell "legally required today" from "required when v4.1.1 lands".

### The nine criteria new in 2.2

`2.4.11` Focus Not Obscured (Minimum, AA) · `2.4.12` Focus Not Obscured (Enhanced, AAA) ·
`2.4.13` Focus Appearance (AAA) · `2.5.7` Dragging Movements (AA) · `2.5.8` Target Size Minimum
(AA, 24x24 CSS px) · `3.2.6` Consistent Help (A) · `3.3.7` Redundant Entry (A) ·
`3.3.8` Accessible Authentication Minimum (AA) · `3.3.9` Accessible Authentication Enhanced (AAA).

`4.1.1 Parsing` was **removed** in 2.2 - do not report it.

## Critical rules

1. **Automated tooling finds a minority of issues.** axe and Lighthouse catch roughly 20 to 40
   percent of real WCAG failures. A clean automated scan is the start of the audit, never the
   conclusion, and must never be reported as "accessible" - that is a coverage figure presented as a
   verdict. **Report the denominator: say what was scanned and what the scan cannot see.**
   **Of the nine criteria new in 2.2, only `2.5.8` Target Size is reliably automatable**, and Deque
   has said it is likely the only 2.2 rule axe-core will ever add, because the rest produce too many
   false positives without human review. So a green axe run on a 2.2 audit has checked, at most, one
   of the nine.
2. **Keyboard and screen reader are mandatory, manual, and not optional.** Every interactive surface
   is operated by keyboard alone, and announced content is verified.
3. **Fix at the root, in the component.** A `role` bolted onto a `div` that should be a `button` is
   a workaround. Native semantics first; ARIA only where no native element exists.
4. **Never suppress.** No `aria-hidden` on focusable content, no `tabindex="-1"` to silence a
   warning, no rule disabled to make a scan pass.
5. **Contrast is measured in context**, against the actual rendered background, including over
   images, gradients and on hover/focus/disabled states.
6. **Report conformance precisely.** "WCAG 2.2 AA with 3 known exceptions, listed" is honest.
   "Accessible" is not a claim this skill may make.

## Modes

```
/a11y                 audit + fix + verify
/a11y --audit         report only, change nothing
/a11y --quick         automated scan + keyboard pass on critical flows
/a11y --deep          full manual protocol across every route and state
/a11y --component <n> one component, all states
/a11y --report        regenerate the conformance report from the last run
```

## Phases

| # | Phase | Must not be skipped |
|---|---|---|
| 1 | Automated scan | every route and key state; record the tool and version |
| 2 | Manual audit | keyboard, screen reader, focus order, contrast in context, zoom/reflow |
| 3 | Remediate | root cause, in the component, one issue at a time |
| 4 | Verify | re-scan **and** re-run the manual checks that failed |
| 5 | Report | conformance statement with exceptions named |

Phase 2 is the phase that finds the real issues and the phase most often skipped under time
pressure. If only one phase runs, it is this one, not Phase 1.

## Severity

| Level | Meaning | Examples |
|---|---|---|
| **Blocker** | a user with this disability cannot complete the task | keyboard trap, unlabelled form control on checkout, focus lost after a modal closes |
| **Serious** | task possible but substantially harder | contrast below 4.5:1 on body text, missing skip link, illogical heading order |
| **Moderate** | friction or confusion | vague link text, missing landmark, redundant alt |
| **Minor** | polish | decorative image with empty-but-present alt, minor label wording |

Blockers gate a launch. Everything else is scheduled, not ignored.

## Definition of done

- Automated scan clean **or** every remaining finding triaged with a reason
- Keyboard-only path through every critical flow, verified
- Screen reader announcement verified on every interactive component changed
- Contrast verified in context, including hover, focus and disabled states
- Conformance statement written with exceptions and their remediation dates
- No suppressions added; no native semantics replaced by ARIA workarounds
