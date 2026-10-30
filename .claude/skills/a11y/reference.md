# /a11y - report, conformance statement, SITREP

## Report

`.a11y-reports/A11Y-<YYYYMMDD-HHMM>.md`.

```markdown
# Accessibility Report: <project>
**Standard:** WCAG 2.2 Level AA
**Tools:** axe-core <ver>, Lighthouse <ver>, VoiceOver/NVDA <ver>
**Scope:** <routes, components, states covered>  |  **Not covered:** <and why>

## Summary
| Severity | Found | Fixed | Remaining |
|---|---|---|---|
| Blocker / Serious / Moderate / Minor | | | |

## Findings
### <id> - <title>  [<severity>]  SC <criterion> (<A|AA>) <[2.2] if new in 2.2>
**Where:** <route / component / state>
**Impact:** <who cannot do what>
**Evidence:** <announcement heard, contrast ratio measured, keystroke that failed>
**Fix:** <root-cause change>
**Verified by:** <the specific re-check performed>
```

## Conformance statement

Only ever claim what was tested, and name the exceptions.

```
Conformance: WCAG 2.2 Level AA, partial.
Scope tested: <routes/components>. Not tested: <what, why>.
Known exceptions:
  - SC 1.4.3 on <surface> - <reason> - remediation by <date>
Evaluated <date> using <tools> plus manual keyboard and screen-reader testing.
```

Never write "fully accessible" or "WCAG compliant" unqualified. **"Accessible" is a claim about
users, not about a scan.**

For an EU-facing product also record: EN 301 549 conformance basis (v3.2.1 = WCAG 2.1 AA today,
v4.1.1 = WCAG 2.2 when it publishes), and note that EAA enforcement has applied since 28 June 2025.

## SITREP

Findings by severity, blockers first with the flow each one breaks. State plainly what was manually
tested versus scanned - a reader must be able to tell how much of the result is automated.

### Suggested next

| Outcome | Recommend |
|---|---|
| Blockers remain | fix before launch; re-run `/a11y --quick` on those flows |
| Clean automated, no manual done | `/a11y --deep` - the automated pass proved a third of the picture |
| Contrast/design-system issues dominate | `/design` - fix the tokens, not the instances |
| Ready to ship | `/gh-ship`, then `/monitor` |

## Design notes

**A third, not all.** The single most important thing this skill knows is that a clean axe run is
not a clean product. Reporting one as the other is the failure mode that makes accessibility work
look done when it is not.

**Root cause in the component.** One `<button>` fixed in a design system beats fifty ARIA patches at
call sites, and cannot regress the same way.

**Exceptions with dates.** A named exception with a remediation date is honest and manageable. A
silent gap is neither.
