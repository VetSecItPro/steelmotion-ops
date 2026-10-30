---
name: design
description: "Frontend design system work: auto-detects whether to generate a system from scratch or audit and improve an existing one. OKLCH colour architecture, three-layer tokens, dark mode as a first-class surface, typography and spacing scales, and accessibility built into the tokens rather than retrofitted."
when_to_use: 'Trigger phrases: "design system", "make this look better", "design audit", "make it consistent", "colour palette", "dark mode", "spacing", "typography", "UI overhaul", "it looks generic". Also when a11y findings are contrast or focus-indicator issues - fix the tokens, not the instances.'
---

# /design - design system generation and audit

**Spine. Survives compaction.** Detail beside it:

| File | Read at | Holds |
|---|---|---|
| `system.md` | generation and audit | colour/type/spacing architecture, dark mode, token layers |
| `archetypes.md` | direction-setting | the vibe archetypes and the three dials |
| `reference.md` | reporting | audit rubric, output structure, SITREP |

**Standards inherited:** [AI-Judgment Paradigm](~/.claude/standards/AI_JUDGMENT_PARADIGM.md) ·
[Steel Discipline](~/.claude/standards/STEEL_DISCIPLINE.md) ·
[Status Updates](~/.claude/standards/STATUS_UPDATES.md) ·
[Cleanup Protocol](~/.claude/standards/CLEANUP_PROTOCOL.md) ·
[Skill Auto-Suggest](~/.claude/standards/SKILL_AUTOSUGGEST_PROTOCOL.md) ·
[Context Management](~/.claude/standards/CONTEXT_MANAGEMENT.md) ·
[SITREP Format](~/.claude/standards/SITREP_FORMAT.md)

## Mode is detected, not asked

| State | Mode |
|---|---|
| No pages, or a bare scaffold | **generate** - build the system, then the surfaces |
| Pages exist, no token layer | **extract then systematise** - find the de-facto palette and scale, formalise it, migrate |
| Pages and tokens exist | **audit and improve** - find drift, inconsistency and a11y failures, fix at the token level |
| A single component named | **component pass** - all states, all breakpoints |

Say which mode was chosen and why, in one line, before starting.

## Non-negotiables

1. **Fix at the token, not the instance.** A contrast failure fixed in one component returns in the
   next. Fixed in the token, it cannot.
2. **Accessibility is part of the system, not a later audit.** Every colour pair ships with its
   measured contrast ratio; every interactive token meets 3:1 non-text contrast; every focus state
   is designed, not defaulted. WCAG 2.2 AA is the floor - see `/a11y` for verification.
3. **Dark mode is a designed surface, not an inversion.** Pure-black-on-pure-white inverted is a
   different product with worse readability. Elevation, shadow and saturation all behave differently.
4. **Three layers, never two.** Primitives → semantic → component. A component that references a
   primitive directly is a leak that makes rethemeing impossible.
5. **Check what the component library is before extending it.** Radix UI is no longer actively
   maintained; its authors moved to Base UI. A shadcn/ui project is built on Radix, so "add a
   component in the existing style" may mean building on something with no upstream. Name it rather
   than discovering it later. Verified 2026-09-02.
6. **No magic numbers.** Every spacing, radius, duration and size comes from a scale. A one-off value
   is either a scale gap or a mistake; decide which.
7. **Consistency beats novelty.** A distinctive system applied consistently reads as designed; an
   inventive system applied inconsistently reads as broken.

## OKLCH is the colour space

Use OKLCH rather than HSL or RGB for scale generation. **HSL lies about perceptual brightness** -
`hsl(60 100% 50%)` (yellow) and `hsl(240 100% 50%)` (blue) claim the same lightness and are wildly
different to the eye. That is why HSL-derived scales have muddy mid-tones and unpredictable contrast.

OKLCH is perceptually uniform, so a fixed lightness step produces an even visual step, and contrast
becomes predictable across hues.

## Contrast model, and what not to change it to

**WCAG 2.2 AA is the floor: 4.5:1 body, 3:1 large and non-text. Do not re-model contrast on APCA.**
Visual contrast was moved OUT of the WCAG 3 draft in July 2023, and as of April 2026 the draft still
records the algorithm as to-be-determined. APCA is a candidate, not the standard. If APCA is wanted,
run it as a readability ceiling ABOVE the WCAG floor, never in place of it.

**`contrast-color()` is Baseline Newly available (April 2026)** and returns black or white to meet AA
against a given colour. Useful for a token's on-colour, with two conditions: ship a fallback, because
newly available is not widely available; and **it does not replace measurement.** It reasons about
the colour you hand it, not the gradient, image or stacking context actually behind the text, which
is the case Phase 6 exists to catch.

## Tokens have a standard format now

**Emit the token layer in DTCG format** (Design Tokens Community Group, first stable version
2025.10, October 2025) wherever a build step or a design tool consumes it. The three-layer rule maps
onto it directly: primitives, then semantic aliases, then component tokens.

**This buys portability, not appearance.** If nothing downstream reads the tokens - no Figma sync, no
style-dictionary build, no second platform - CSS custom properties alone are sufficient and DTCG is
ceremony. Say which case applies rather than emitting a format nobody consumes. Detail: `system.md`.

## Pipeline

| # | Phase | Produces |
|---|---|---|
| 1 | Detect and orient | mode, existing tokens, stack, component library in use |
| 2 | Direction | dials and archetype settled (`archetypes.md`) - or extracted from what exists |
| 3 | System | colour scales, semantic tokens, type scale, spacing, radii, motion (`system.md`) |
| 4 | Dark mode | designed as its own surface, both directions verified for contrast |
| 5 | Apply | components migrated to tokens; magic numbers eliminated |
| 6 | Verify | contrast measured, states checked, responsive breakpoints exercised |
| 7 | Report | what changed, what drifted, what remains (`reference.md`) |

Phases 4-7 are what a long run loses to compaction if not held here. **Phase 6 is what separates a
design system from a palette** - unverified tokens are a proposal.

## Visual verification uses the browser

Contrast and state checks are done against **rendered pixels**, not the token values, via the
Playwright MCP tools when available: `browser_navigate`, `browser_snapshot`,
`browser_take_screenshot`, `browser_resize` (for the 320px and 200%-zoom checks), `browser_click` and
`browser_evaluate` (to drive hover/focus/active/disabled states), `browser_wait_for`. A token that
looks right in CSS can still fail once a background image, a gradient or a stacking context is behind
it - only the rendered result is authoritative.

## Verification, before claiming done

- Every text/background pair measured: 4.5:1 body, 3:1 large. **Measured, not assumed from the scale.**
- Every interactive boundary and focus indicator at 3:1 non-text contrast
- Both themes checked, including hover, focus, active, disabled, and error states
- 320 CSS px width with no horizontal scroll; 200% zoom without loss
- `prefers-reduced-motion` respected by every transition
- No component references a primitive token directly

## Definition of done

- Three-layer token architecture in place, with no layer skipping
- Every colour pair's contrast recorded in the report
- Dark mode designed and verified, not derived by inversion
- Magic numbers removed or promoted into the scale with a reason
- Report written; hand to `/a11y` for independent verification if the surface is user-facing
