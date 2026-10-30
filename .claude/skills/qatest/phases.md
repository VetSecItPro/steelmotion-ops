# /qatest - phases in detail

Every phase drives the running application. If the app is not started, Phase 0 starts it; a QA sweep
against a dead server is not QA.

## Phase 0-1: pre-flight and discovery

Start the app (or accept a `--url`). Confirm reachable. Detect the stack. Enumerate routes from the
**app**: the filesystem router, the sitemap, the API route files, the navigation as rendered. Do not
work from a remembered list - a route added last week must be found.

Classify each route: public vs auth-gated, critical (checkout, login, the primary action) vs ordinary.
Auth-gated routes are driven with a test account, never skipped.

## Phase 2: page health

Each route: loads with 2xx, the content marker is present (not a blank shell or an error page),
`browser_console_messages` shows no errors, `browser_network_requests` shows no failed requests,
security headers present. A 200 that logs a React error to the console is a finding.

## Phase 3: interactive elements

`browser_snapshot` the page, then drive **every** interactive element:

- **buttons:** click each; capture what happened (navigation, a request, a state change, a console
  error, or nothing - "nothing" is a bug)
- **forms:** `browser_fill_form` with valid then invalid data; submit; verify validation fires and
  the success/error path works
- **links:** each resolves (no 404), internal ones stay in-app
- **menus/dropdowns/modals:** open, interact, close; verify focus behaviour (ties to `/a11y`)

Capture console and network for each interaction. A finding is what you observed, not what the code
suggests.

## Phase 3.5: user journeys (the core)

Walk the critical flows as a real user, end to end:

- **signup -> onboarding -> first value:** does it complete without a dead end?
- **the primary conversion action:** start to finish
- **auth lifecycle:** login, logout, password reset, session expiry
- **error recovery:** make a step fail; is there a way forward?

A journey that dead-ends is a high-severity finding regardless of how clean the individual pages are.
This is the phase that justifies a full QA sweep over a page-by-page check.

## Phase 4-4.5: API and integrations

Each endpoint, non-destructively: missing-auth -> 4xx, invalid-body -> 400, happy path -> expected
shape, downstream-failure handled. Use test accounts for anything mutating; clean up. For integrations
(payment, email), verify the app's handling in the provider's test mode - never a real charge, never
a live email blast.

## Phase 5-6.5: accessibility, responsive, performance

Run the existing skills' logic rather than a second implementation:
- **Accessibility:** `/a11y`'s automated scan + a keyboard pass on the critical flows
- **Responsive:** `browser_resize` to key breakpoints, 320px, and 200% zoom; check for overflow,
  clipping, overlap
- **Performance:** `/perf`'s lab measurement on the key routes; note against budget

## Phase 7-9: score, fix, verify

Score across dimensions (`reference.md`). Auto-fix only the unambiguously safe - a missing header, a
lint issue, a broken internal link with an obvious target. A broken journey or a failing interaction
is reported for judgment, not auto-fixed. For every fix and every confirmed flow bug, generate a
regression test (a Playwright spec for a flow, a unit test for a handler). Then re-run the failed
checks and confirm green.
