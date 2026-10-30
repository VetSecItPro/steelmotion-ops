# /design - direction: dials and archetypes

Read when setting or extracting design direction. In audit mode, infer the current position on each
dial from what exists before proposing a change - a system being *consistently* something is worth
more than moving it toward a preference.

## The three dials

| Dial | Range | Effect |
|---|---|---|
| **Density** | airy ←→ compact | spacing scale multiplier, line height, control heights. Data tools go compact; marketing goes airy |
| **Contrast** | soft ←→ stark | lightness distance between surface and text, border prominence, shadow depth |
| **Expression** | restrained ←→ characterful | accent saturation, radius, motion amount, typographic personality |

Defaults when nothing is specified: density mid, contrast stark enough to clear WCAG AA with margin,
expression restrained. **Restrained is the safer default** - it fails gracefully, whereas
characterful applied inconsistently reads as broken rather than bold.

## Archetypes

A starting position on all three dials plus a palette temperament. Pick by name, describe a custom
one, or extract from an existing product.

| Archetype | Dials | Character |
|---|---|---|
| **Technical/tool** | compact, stark, restrained | monospace accents, tight grid, minimal motion, function-first. Dashboards, consoles, developer tools |
| **Editorial** | airy, soft-to-mid, characterful | serif display, generous measure, strong hierarchy, image-forward. Publishing, long-form |
| **Premium dark** | mid, stark, characterful | deep surfaces (~oklch 0.15), a single warm accent, restrained motion, tabular numerals. Finance, security, high-trust |
| **Clinical** | mid, mid, restrained | high legibility, unambiguous states, no decoration, strong error affordances. Healthcare, legal, regulated |
| **Consumer-friendly** | airy, soft, characterful | rounded radii, warmer palette, playful motion within reduced-motion limits |
| **Brutalist/utility** | compact, stark, restrained | system fonts, hard edges, near-zero radius, no shadow. Fast to build, fast to load, polarising |

## Choosing

Match the archetype to the **task**, not to taste. A clinical archetype on a consumer app feels cold;
a consumer archetype on a medical record feels untrustworthy. When the operator's stated preference
conflicts with the task, say so once, then follow their preference - it is their product.

Record the choice and the dial positions in the report, so later work extends the system rather than
drifting from it.

## Component libraries

If one is already in use (shadcn/ui, Radix, Headless UI, Mantine, MUI, Chakra), **theme it rather
than replace it**. Map its theming surface onto the layer-2 semantic tokens; do not fork components
to hard-code colours. A library swap is an architecture decision - route it to `/mdmp`, not here.

Where no library exists and one is warranted, prefer an unstyled/accessible primitive set (Radix,
Headless UI, Ark) over a styled kit - it gives correct keyboard and ARIA behaviour without fighting
its aesthetics.
