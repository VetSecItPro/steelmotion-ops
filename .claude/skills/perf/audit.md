# /perf - what to look for, by layer

Read at Phase 2. Rank every finding by **estimated cost on the critical path**, not by how
interesting the fix is. A finding without a cost estimate cannot be prioritised.

## The cost model

Estimate for each finding: how much time, on which metric, for what share of requests.
"Blocks LCP by ~600 ms on every cold load" is actionable. "Unoptimized images" is not.

## Layer 1 - network and delivery

Uncompressed responses (brotli/gzip absent); no HTTP/2 or /3; missing `Cache-Control` on immutable
assets; render-blocking CSS/JS in `<head>`; no preconnect to a critical third-party origin; fonts
without `font-display: swap` (a direct CLS and LCP cause); no CDN in front of static assets.

## Layer 2 - assets

**Images are usually the largest single win.** Wrong format (not AVIF/WebP), no responsive `srcset`,
no dimensions set (CLS), eager loading below the fold, an oversized LCP image. Then: unsubsetted
fonts, unused CSS, SVGs that should be sprites.

## Layer 3 - JavaScript

Bundle over budget; a heavy dependency used for one function (date libraries, lodash whole-package
imports, moment); no code splitting at the route boundary; client components that could be server
components; polyfills for browsers the project does not support; duplicate dependencies at different
versions in the lockfile.

**INP specifically:** long tasks over 50 ms on the main thread; event handlers doing layout-thrashing
work; large synchronous state updates; hydration cost on interaction-heavy pages.

## Layer 4 - rendering

Layout thrash (read-then-write in a loop); unnecessary re-renders (missing memo where profiling shows
it matters - not everywhere); large lists without virtualisation; animation on non-composited
properties (anything but `transform`/`opacity`); expensive CSS selectors on large DOMs.

## Layer 5 - backend

N+1 queries; missing indexes; `SELECT *` where three columns are used; work done per-request that
could be cached or precomputed; synchronous third-party calls in the request path; no connection
pooling; serverless cold starts on a hot path.

## Layer 6 - build and CI

Build time regressions; no incremental build or cache; test suite duration; a CI pipeline that
rebuilds unchanged packages. Slow builds tax every future change, so they belong in the audit even
though users never see them.

## Anti-findings - do not report these

- A micro-optimisation with no measured effect on the critical path
- "Use a faster framework" - not a finding, a rewrite
- Bundle size on a route nobody visits
- A theoretical improvement you did not measure
- Anything the project's own budget explicitly accepts
