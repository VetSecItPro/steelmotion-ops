# /a11y - how to test

Read at Phase 1 (automated) and Phase 3/4 (manual). **Automated tooling catches roughly a third of
WCAG failures.** The manual protocol is where the rest are found; it is not optional.

## Automated, by stack

| Stack | Tool |
|---|---|
| any URL | `npx @axe-core/cli <url>`, or Lighthouse accessibility category |
| whole site | `npx unlighthouse --site <url>` for per-route scores |
| React/Vue/Svelte in CI | `jest-axe` / `vitest-axe` per component, all states |
| Playwright/Cypress e2e | `@axe-core/playwright`, `cypress-axe` on each critical flow |
| Storybook | `@storybook/addon-a11y` catches issues per component variant |
| lint-time | `eslint-plugin-jsx-a11y` - cheapest possible feedback |
| HTML | `html-validate`, or the W3C validator for structural errors |

Record the tool **and version** - rule sets change between releases, so a comparison across versions
is not like-for-like.

Scan every route **and every state**: empty, loading, error, populated, modal-open, menu-expanded.
Most real failures live in states an automated crawler never reaches.

## Manual protocol - the part that matters

**1. Keyboard only.** Unplug the mouse. For every critical flow: Tab forward through everything,
Shift+Tab back. Verify - every interactive element is reachable; focus is always visible; focus order
matches visual order; Enter and Space activate as expected; Escape closes overlays; **focus returns
to the trigger** when an overlay closes; no trap; the focused element is never hidden behind sticky
UI (2.4.11).

**2. Screen reader.** VoiceOver (⌘F5) on macOS, NVDA on Windows. Do not read the code and imagine
the output - listen to it. Verify names, roles and states are announced; headings form a sensible
outline; landmarks let you jump; form errors are announced and tied to their field; async status
reaches a live region (4.1.3).

**3. Contrast in context.** Not the palette in isolation - the rendered pixels. Include hover, focus,
active, disabled, text over images and gradients, and focus indicators against their actual
background (1.4.11).

**4. Zoom and reflow.** 200% browser zoom, then 320 CSS px width. No horizontal scrolling, no
clipped content, no overlap. Then the 1.4.12 text-spacing overrides.

**5. Motion and timing.** `prefers-reduced-motion` respected; nothing flashes >3x/second; time limits
adjustable.

**6. Forms end to end.** Submit empty, submit invalid, submit valid. Errors must be perceivable
(text, not colour), programmatically associated, and focus must move somewhere useful.

## Verifying a fix

Re-run the automated scan **and** re-perform the specific manual check that failed. An automated
pass does not verify a keyboard or announcement fix, because automation could not see it in the
first place.
