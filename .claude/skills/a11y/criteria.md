# /a11y - WCAG 2.2 AA criteria that actually matter in review

Read at Phase 2. Organised by what you check, not by spec numbering. Criterion ids are given so a
finding can cite the requirement. **[2.2]** marks a criterion new in 2.2 - required now under WCAG
2.2 AA, and under EN 301 549 once v4.1.1 publishes.

## Perceivable

| Check | Criteria | What passes |
|---|---|---|
| Text alternatives | 1.1.1 (A) | meaningful images described; decorative images `alt=""`; icon buttons have accessible names; complex images have a long description |
| Captions / audio | 1.2.2, 1.2.4 (A/AA) | prerecorded video captioned; live video captioned |
| Info and relationships | 1.3.1 (A) | headings are real headings, tables have `<th>` and scope, form controls have real labels, lists are lists |
| Meaningful sequence | 1.3.2 (A) | DOM order matches visual order; CSS never reorders content into nonsense for a screen reader |
| Identify input purpose | 1.3.5 (AA) | `autocomplete` on name, email, address, phone fields |
| Use of colour | 1.4.1 (A) | colour is never the only signal - errors, required fields, links in body text |
| Contrast | 1.4.3 (AA) | 4.5:1 body text, 3:1 for ≥18.66px bold or ≥24px |
| Resize / reflow | 1.4.4, 1.4.10 (AA) | usable at 200% zoom, and at 320 CSS px wide with no horizontal scroll |
| Non-text contrast | 1.4.11 (AA) | 3:1 for UI component boundaries, focus indicators, and meaningful graphics |
| Text spacing | 1.4.12 (AA) | no loss of content when line-height 1.5, para spacing 2x, letter 0.12em, word 0.16em |
| Content on hover/focus | 1.4.13 (AA) | dismissable, hoverable, persistent |

## Operable

| Check | Criteria | What passes |
|---|---|---|
| Keyboard | 2.1.1, 2.1.2 (A) | every function reachable and operable by keyboard; **no traps** |
| Timing | 2.2.1 (A) | limits adjustable, extendable or disableable |
| Seizures | 2.3.1 (A) | nothing flashes more than 3x/second |
| Bypass blocks | 2.4.1 (A) | skip link, or correct landmarks |
| Page titled / headings / labels | 2.4.2, 2.4.6 (A/AA) | unique descriptive title per route; headings describe their section |
| Focus order | 2.4.3 (A) | follows meaning; modals trap focus **deliberately** and restore it on close |
| Link purpose | 2.4.4 (A) | clear from the link text or its context - never a bare "click here" |
| Focus visible | 2.4.7 (AA) | a visible indicator, meeting 1.4.11 contrast |
| **Focus not obscured** | **2.4.11 (AA) [2.2]** | the focused element is not hidden behind a sticky header, cookie bar or toast |
| **Dragging movements** | **2.5.7 (AA) [2.2]** | anything draggable has a single-pointer alternative (reorder buttons, not drag-only) |
| **Target size** | **2.5.8 (AA) [2.2]** | interactive targets ≥ 24x24 CSS px, or adequately spaced |
| Pointer gestures / cancellation | 2.5.1, 2.5.2 (A) | multipoint or path gestures have a simple alternative; actions fire on up-event |

## Understandable

| Check | Criteria | What passes |
|---|---|---|
| Language | 3.1.1, 3.1.2 (A/AA) | `lang` on `<html>`; `lang` on foreign-language passages |
| On focus / on input | 3.2.1, 3.2.2 (A) | focus alone changes nothing; changing a value does not auto-submit or navigate |
| Consistent nav / identification | 3.2.3, 3.2.4 (AA) | navigation in the same order across pages; the same component named the same way |
| **Consistent help** | **3.2.6 (A) [2.2]** | help mechanisms appear in the same relative place on every page that has them |
| Error identification / suggestion | 3.3.1, 3.3.3 (A/AA) | errors named in text, tied to their field, with a suggested fix |
| Labels or instructions | 3.3.2 (A) | every control labelled; placeholder is never the only label |
| Error prevention | 3.3.4 (AA) | legal, financial and data-deleting actions are reversible, checked or confirmed |
| **Redundant entry** | **3.3.7 (A) [2.2]** | information already given in a process is not asked for again, or is auto-populated |
| **Accessible authentication** | **3.3.8 (AA) [2.2]** | no cognitive function test (puzzle, memory, transcription) without an alternative; password managers must be able to fill fields |

## Robust

| Check | Criteria | What passes |
|---|---|---|
| Name, role, value | 4.1.2 (A) | every custom control exposes all three correctly to assistive tech |
| Status messages | 4.1.3 (AA) | async results, toasts and validation summaries announced via a live region without moving focus |

**4.1.1 Parsing was removed in WCAG 2.2.** Do not report it. Malformed markup still matters where it
breaks 1.3.1 or 4.1.2 - report it as those.

## Frequent root causes

`div` with a click handler instead of `button` · placeholder used as label · custom select with no
keyboard support · modal that does not trap or restore focus · toast that never announces ·
focus indicator removed by `outline: none` with no replacement · icon-only button with no accessible
name · sticky header covering the focused field (2.4.11) · drag-only reordering (2.5.7) ·
touch target under 24px (2.5.8).
