# /monitor - stage procedures

Read at Stage 0 and as each stage begins. Every stage is **read-only**: GET and HEAD only, never a
method that mutates state.

## Stage 0 - detection and pre-flight

Read `targets.md`. Determine, and record in the report header: the deploy target class(es), the
observability backend, the live capability state (cloud session alive or not), any project-owned
verification tooling to reuse, and whether a baseline exists in `.monitor-reports/`.

Resolve the URL to check: an explicit argument, else `$PROD_URL`, else `package.json` `homepage`,
else the repo's `homepage` field, else the platform's project domain. If none resolves and the target
class is not a runtime one, report "no deployment surface detected" and stop - that is a clean
result, not a failure.

Determine the **content marker** now, before checking anything: a string that must appear in a
healthy response. In order of preference - a `<title>` from the built output, a known nav element, a
version string, or a `/health` endpoint's expected JSON key. Record it. Without a marker, Stage 2
cannot distinguish "up" from "correct".

## Stage 1 - route discovery

Enumerate from the project, never from memory.

- **Filesystem routers:** Next.js `app/**/page.tsx` and `pages/**/*.tsx`; Remix `app/routes/**`;
  SvelteKit `src/routes/**/+page.svelte`; Astro `src/pages/**/*.astro`; Nuxt `pages/**`
- **API routes:** `app/api/**/route.ts`, `pages/api/**`, framework equivalents, or the service's
  router file for a backend
- **Declared surfaces:** `sitemap.xml`, `robots.txt`, an OpenAPI spec, ingress rules, a Helm chart's
  declared paths
- **Dynamic segments:** substitute real values from the sitemap, a seed file, or known slugs. If no
  value is obtainable, mark the route DEFERRED rather than guessing an id
- **Exclusions:** auth-gated routes are DEFERRED, not failures. Never attempt to authenticate.

Classify each route as critical or ordinary - a 5xx on a critical route zeroes the route-health
category.

## Stage 2 - endpoint health

Per route: GET (or HEAD for non-idempotent API paths), recording status, response time,
content-type, content-length, and **whether the content marker is present**.

- 3xx: follow, record the final destination, flag chains over 3 hops and any loop
- 4xx/5xx: a finding, with severity by route criticality
- **200 without the content marker: a finding, scored as a 5xx.** This is the stale-build,
  blank-shell and branded-error-page case, and it is the whole reason the marker exists
- Timings: record P50 and P95; compare to baseline if one exists. No baseline → say "no baseline;
  this run establishes one" and do not score response time against an invented number
- Rate limiting: space requests ≥100 ms; on 429 back off exponentially and note it

## Stage 3 - function and service verification

**PaaS:** identify serverless/edge functions, SSR pages, middleware and scheduled functions. Verify
each returns valid JSON/HTML rather than a framework error page. A function that 200s with an error
payload is failing.

**Kubernetes:** per §2 of `targets.md` - rollout completed, pods ready, **restart counts since the
deploy**, probe-failure events, running image digest matches what shipped, and ingress/target-group
membership. Where the project has its own verify scripts, run the relevant ones and parse their
output rather than duplicating the logic.

**Compose / systemd:** container or unit state, healthcheck status, restart counts, recent journal
entries at error level.

**Poll-cron:** deployed sha equals origin tip, and the last scheduled run exited zero.

## Stage 4 - environment validation

Enumerate what the running system requires: `process.env.X` / `os.environ[...]` references in source,
`.env.example` and friends, framework config, chart `env:` blocks and referenced secrets.

Categorise: **critical** (database URL, auth secret, keys for core features) vs **non-critical**
(analytics, feature flags). Verify presence in the deployed environment by observable behaviour -
a route that fails only when a variable is missing, or the platform's own config listing. **Never
print a value.** Report presence and absence only.

## Stage 5 - infrastructure

- **DNS:** hostname resolves; records correct; note propagation differences across resolvers
- **SSL:** validity dates, chain complete, expiry ≥30 days (under 30 is a −50 finding, expired is 0)
- **Headers:** HSTS, CSP, X-Frame-Options or frame-ancestors, Referrer-Policy, X-Content-Type-Options
- **CDN/cache:** cache hit behaviour, correct `Cache-Control` on static versus dynamic
- **Protocol:** HTTP/2 or /3 negotiated
- **Runtime ingress:** for k8s, the ALB/ingress target group's healthy count versus pod count. Pods
  can be Ready while the target group has dropped them; that discrepancy is the finding

## Stage 6 - error tracking

From the backend detected in Stage 0:

- **Datadog:** the four golden signals over the window since the deploy - latency, traffic, errors,
  saturation. A green rollout alongside degraded signals is a failed deploy and must be reported as
  such, not as a pass
- **Sentry:** error count and, specifically, issues first seen after the deploy timestamp
- **Platform-native:** the provider's runtime log for the last hour at error level
- **Prometheus:** the same golden signals by query
- **None:** the category is unmeasured. Say so, mark it DEFERRED, and renormalise

Count unique versus recurring errors; a recurring error weighs more than a one-off. Look for a spike
relative to the pre-deploy window rather than an absolute count.

## Stage 7 - score and report

Compute each category per the table in `SKILL.md`. **Renormalise across only the categories that were
actually measured** and show the arithmetic, so a 95 from four categories is not mistaken for a 95
from six. DEFERRED categories are listed with the capability that was missing.

Write `.monitor-reports/MON-<YYYYMMDD-HHMM>.md` per `reference.md`, append to `history.json`, and
emit the SITREP with the grade, the findings ordered by severity, and "Suggested next".

Compare against the previous report where one exists: score delta, routes that changed state, and
response times that regressed beyond baseline×1.5. A trend is more actionable than a snapshot.
