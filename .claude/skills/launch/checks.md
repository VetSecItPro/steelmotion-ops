# /launch - the five checks this skill owns

The orchestrated skills cover security, tests, performance, a11y, deps and health. These five are the
launch domains none of them own, and each is a common real blocker.

## 1. Content readiness

- No placeholder copy shipping (`lorem ipsum`, "TODO", "coming soon" on a live surface)
- No broken internal links; no 404s from the nav or footer
- Images have real content, correct aspect, and load (ties to `/perf` and `/a11y`)
- Empty, loading and error states have real content, not a blank or a raw error
- Meta copy present: titles, descriptions, OG/Twitter cards for anything shareable
- Legal/marketing copy is the approved version, not a draft

## 2. SEO & meta

- Unique `<title>` and meta description per route
- `robots.txt` and `sitemap.xml` present and correct (not blocking the whole site by accident)
- Canonical URLs set; no accidental `noindex` on production
- OG and Twitter card tags for shareable pages, with a real image
- Structured data where it applies (Article, Product, Organization)
- No staging/preview URL leaking into canonical or sitemap

## 3. User-flow completeness

Walk the critical paths end to end, as a real user:

- Signup -> onboarding -> first value: does it complete without a dead end?
- The primary conversion action: does it work start to finish?
- Auth: login, logout, password reset, session expiry all functional
- Error recovery: what happens when a step fails - is there a way forward?
- Email flows fire and their links resolve (verification, reset, receipts)
- The path works on mobile width, not just desktop

A broken critical flow is a hard blocker regardless of how polished everything else is.

## 4. Payment & subscription (if the product charges)

- Checkout completes in the provider's test mode
- Webhook signature validation present (verify in code - do not send unsigned live)
- Subscription lifecycle: create, upgrade, downgrade, cancel, and the entitlement each grants
- Failed-payment handling and dunning behaviour exist
- Prices and plans match what the marketing says
- No real charge is ever made during the check

If the product charges money and payment is broken, that is NO-GO - there is no launching a paid
product that cannot take payment.

## 5. Legal & privacy

- Privacy policy present, accurate to what is actually collected, and linked
- Terms of service present and linked
- Cookie consent where required (EU/UK), and it actually gates non-essential cookies
- Data-handling matches the policy - if the policy says "we don't share", verify nothing does
- Accessibility statement where the EAA applies (EU-facing), given WCAG 2.2 AA obligations
- Required compliance for the domain (HIPAA, PCI, GDPR, SOC2) at least assessed, gaps named
- Age gating / content warnings where applicable

A legal requirement unmet is a hard blocker - the cost is not a bad launch, it is liability.

## Applicability

Not every check applies to every product. A free internal tool has no payment domain and thin legal;
a consumer EU SaaS has all five at full weight. Assess applicability first (spine's N/A rule) so the
verdict is not distorted by scoring an irrelevant domain.
