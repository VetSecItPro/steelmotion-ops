# /perf - how to measure, per stack

Read at Phase 1 and again at Phase 4. **Phase 4 must use the identical method** or the comparison is
worthless. Record the method in the report.

## Lab vs field - say which, every time

| | What it is | Use for | Never use for |
|---|---|---|---|
| **Lab** | synthetic run on known hardware (Lighthouse, WebPageTest, a local profiler) | diagnosis, A/B of a change, CI gates | claiming the Core Web Vitals grade |
| **Field** | real users, p75, 28-day window (CrUX, RUM, `web-vitals` beacons) | the actual grade | fast iteration - it lags weeks |

A lab improvement is evidence a field improvement will follow. It is not the field improvement. Say
"lab LCP 4.1s -> 2.2s; field p75 will confirm over the next 28 days."

## Frontend

```bash
npx lighthouse <url> --output=json --quiet --chrome-flags="--headless"   # lab, one page
npx unlighthouse --site <url>                                            # lab, whole site
```

Run **three times and take the median** - a single Lighthouse run varies enough to invent or hide a
regression. Throttle consistently (Lighthouse's default 4x CPU / Slow 4G) and say so.

Field data: CrUX via the PageSpeed Insights API for any public URL; or the `web-vitals` library
reporting to your own endpoint for pre-launch and authenticated pages, which CrUX cannot see.

**Bundle:** the bundler's own analyzer is authoritative - `next build` output, `vite build`
`rollup-plugin-visualizer`, `webpack-bundle-analyzer`, `esbuild --analyze`. Measure **gzipped or
brotli**, per route, not raw total.

## Backend and API

Measure from the server's own timing, not the browser's - the browser number includes network you do
not control.

- p50/p95/p99 per endpoint from the APM (`/monitor` detects which one), or add timing middleware
- **Database is the usual answer.** Log slow queries; `EXPLAIN ANALYZE` the worst; look for N+1
  (a query count that scales with result count), missing indexes, and sequential scans on large
  tables
- Cold start vs warm for serverless; state which you measured
- Payload size - an endpoint returning fields nobody reads is latency you can delete

## Runtime and infrastructure

Container CPU throttling, memory pressure and GC pauses show up as latency with no slow code. Check
the runtime's own metrics before profiling the application. For Kubernetes, CPU limits set too low
cause throttling that looks exactly like slow code.

## Recording the baseline

```
Method   : lighthouse 12.x, headless, 4x CPU / Slow 4G, median of 3
Field    : CrUX p75 28-day, fetched <date>
Routes   : 12 measured, 3 auth-gated (DEFERRED)
Baseline : lab LCP 4.1s | INP 310ms | CLS 0.04 | JS 612 KB gz
           field LCP 3.8s | INP 240ms | CLS 0.03  (p75)
```

Without the method line, the numbers are not reproducible and Phase 4 cannot honestly compare.
