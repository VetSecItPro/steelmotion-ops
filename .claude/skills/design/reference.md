# /design - audit rubric, output, SITREP

## Audit rubric

Score each dimension 1-5 with evidence. This is what makes "make it look better" a measurable request.

| Dimension | 1 | 5 |
|---|---|---|
| **Token architecture** | hard-coded values throughout | three clean layers, no layer skipping |
| **Colour consistency** | many near-identical greys and accents | one scale, semantic names, no strays |
| **Contrast/a11y** | failures on body text | every pair measured and passing, focus states designed |
| **Type scale** | arbitrary sizes | one ratio-derived scale, capped, consistently applied |
| **Spacing** | magic numbers everywhere | every value from the scale |
| **State coverage** | hover only | all seven states on every interactive element |
| **Dark mode** | absent or inverted | designed as its own surface, independently verified |
| **Responsive** | breaks under 400px | fluid to 320px, verified at 200% zoom |
| **Motion** | none, or unconstrained | small consistent set, reduced-motion honoured |

Count **stray values** as a hard metric: distinct colours not in the scale, distinct spacing values
not in the scale, distinct font sizes not in the scale. The count moving down over time is the
clearest single measure that a system is taking hold.

## Output

```
.design-reports/DESIGN-<YYYYMMDD-HHMM>.md
<or the project's existing design docs location, if one exists>
```

```markdown
# Design Report: <project>
**Mode:** generate | extract | audit | component
**Direction:** <archetype>, density <x>, contrast <y>, expression <z>

## Rubric
| Dimension | Before | After | Evidence |

## Stray values
| Kind | Before | After |
| colours not in scale | 34 | 0 |
| spacing values not in scale | 21 | 0 |
| font sizes not in scale | 11 | 7 |

## Contrast verification
| Pair | Ratio | Required | Theme | Status |
| text on surface | 12.6:1 | 4.5:1 | light | PASS |
| text on surface | 11.9:1 | 4.5:1 | dark | PASS |
| accent on surface | 3.2:1 | 4.5:1 | dark | **FAIL - accent lightened to 600** |

## Changed / Remaining
```

## SITREP

Lead with the rubric delta and the stray-value counts - those are the numbers that show whether
anything actually improved. Then contrast verification, then what remains.

### Suggested next

| Outcome | Recommend |
|---|---|
| System applied, surfaces user-facing | `/a11y` - independent verification, keyboard and screen reader |
| Fonts or images changed | `/perf` - typography and images are top LCP/CLS causes |
| Library swap being considered | `/mdmp` - that is an architecture decision, not a design one |
| Tokens in place, components pending | continue in component mode, one component at a time |

## Design notes

**OKLCH over HSL** because HSL's lightness is a lie - equal L values across hues are visibly
different brightnesses, which is why HSL-derived scales need per-hue hand-correction and still
produce unpredictable contrast.

**Stray-value counts, not adjectives.** "More consistent" is unfalsifiable. "34 off-scale colours
reduced to 0" is a claim that can be checked, and it is the same claim.

**Dark mode is designed, not derived.** Inversion produces halation on OLED, vibrating saturated
colours and shadows that convey nothing. It is a second surface with its own rules.

**Theme the library, never fork it.** A forked component drifts from upstream and loses its
accessibility fixes silently.
