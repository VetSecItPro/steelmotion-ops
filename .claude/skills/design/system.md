# /design - the system: colour, type, spacing, dark mode

## Three-layer tokens

```css
/* Layer 1 - primitives. Raw scale. Never referenced by a component. */
--color-blue-50:  oklch(0.978 0.011 240);
--color-blue-500: oklch(0.623 0.188 240);
--color-blue-900: oklch(0.312 0.098 240);

/* Layer 2 - semantic. Meaning, not appearance. This is what themes swap. */
--color-surface:        var(--color-neutral-50);
--color-surface-raised: var(--color-neutral-0);
--color-text:           var(--color-neutral-900);
--color-text-muted:     var(--color-neutral-600);
--color-accent:         var(--color-blue-500);
--color-border:         var(--color-neutral-200);
--color-danger:         var(--color-red-600);

/* Layer 3 - component. Only where a component genuinely needs its own knob. */
--button-primary-bg:    var(--color-accent);
--button-primary-text:  var(--color-neutral-0);
```

**A component may only reference layer 2 or 3.** Reaching into layer 1 hard-codes appearance and
makes rethemeing impossible - it is the single most common way a token system rots.

## Platform facts, verified 2026-09-02

Re-verify before trusting; this list is the kind of claim that rots quietly.

| Feature | Status | Use it? |
|---|---|---|
| OKLCH colour | Widely available | yes, no fallback needed for current browsers |
| `contrast-color()` | **Baseline Newly available, April 2026** | yes with a fallback |
| `@scope` | Baseline Newly available, 2026 | yes with care |
| `field-sizing: content` | Baseline Newly available, 2026 | yes with a fallback |
| `sibling-index()` / `sibling-count()` | Baseline Newly available, 2026 | yes with a fallback |
| Container queries, subgrid | Baseline, and still an Interop 2026 focus area | yes; test the edges |
| Anchor positioning | **Interop 2026 focus area, not settled** | only with a fallback path |
| Cross-document view transitions | **Interop 2026 focus area, not settled** | progressive enhancement only |

**Newly available means it works in current browsers, not in the browsers a visitor actually has.**
Widely available means roughly 30 months of support behind it. Choose on the project's audience, not
on the label.

## DTCG token format

First stable version **2025.10**, published October 2025 by the Design Tokens Community Group, with
editors from Adobe, Google, Figma, Microsoft, Salesforce and others. It is the interchange format
between design tools and code, and it maps onto the three layers above without changing them.

```json
{
  "color": {
    "$type": "color",
    "brand": { "500": { "$value": "oklch(0.62 0.19 264)" } }
  },
  "semantic": {
    "$type": "color",
    "surface-accent": { "$value": "{color.brand.500}" }
  }
}
```

`$value`, `$type` and alias references in braces are the parts that matter. **Emit this only where
something downstream reads it.** A DTCG file nobody consumes is a second source of truth to keep in
step with the CSS, which is a cost, not a deliverable.

## Colour scales in OKLCH

`oklch(L C H)` - lightness 0-1, chroma 0-0.4ish, hue 0-360.

Build a scale by holding hue, stepping lightness evenly, and tapering chroma at the extremes (very
light and very dark colours cannot carry high chroma without looking artificial). Eleven steps
(50-950) covers most needs.

Because OKLCH lightness is perceptual, **contrast becomes predictable**: a step-500 accent on a
step-50 surface lands in a known range rather than needing trial and error. Still measure - predictable
is not the same as verified.

Provide an sRGB fallback where the browser matrix requires it; `@supports (color: oklch(0 0 0))` is
the gate.

## Dark mode as its own surface

Not an inversion. What changes:

| Aspect | Light | Dark |
|---|---|---|
| Surface | white-ish, elevation via shadow | dark grey, elevation via **lighter** surface |
| Pure black | fine as text | avoid as background - halation on OLED, harsh contrast; prefer ~oklch(0.15) |
| Pure white | fine as background | avoid as text - too harsh; prefer ~oklch(0.95) |
| Saturation | full chroma reads fine | reduce chroma ~10-20%, saturated colours vibrate on dark |
| Shadow | conveys elevation | barely visible - use surface lightness and border instead |
| Images | as authored | may need a slight brightness reduction |

Both directions must be contrast-verified independently. A pair passing in light frequently fails in
dark, because the eye's contrast sensitivity is not symmetric.

## Typography

One scale, derived by ratio (1.2 minor third for dense UI, 1.25 for general, 1.333 for editorial).
Cap it - most products need 6-8 sizes; more indicates the scale is being worked around.

- Line height: tighter as size increases (1.6 body, ~1.2 display)
- Measure: 45-75 characters for body text; long lines are a readability failure regardless of contrast
- Weight: two or three, not five. Weight carries hierarchy more cheaply than size
- Never rely on weight alone for meaning (WCAG 1.4.1)
- `font-display: swap`, and subset - fonts are a top LCP and CLS cause (see `/perf`)

## Spacing, radii, motion

**Spacing:** one base unit (4 or 8 px), a geometric-ish scale (4 8 12 16 24 32 48 64 96). Every gap,
padding and margin comes from it. A value outside the scale is a bug or a missing step.

**Radii:** three or four values - none, sm, md, lg, full. Consistency here does more for coherence
than almost anything else.

**Motion:** durations 150/250/400 ms for micro/standard/large. Ease-out for entering, ease-in for
exiting. Every transition wrapped in `prefers-reduced-motion`. Animate `transform` and `opacity`
only - anything else costs a layout or paint (see `/perf`).

## Interactive states - all of them, every time

Every interactive element defines: default, hover, focus-visible, active, disabled, loading, and
error where applicable. The two most often missed:

- **focus-visible** - must be designed, must meet 3:1 against its background, and must not be
  removed by `outline: none` without a replacement
- **disabled** - still needs enough contrast to be readable; "disabled" does not mean "invisible"
