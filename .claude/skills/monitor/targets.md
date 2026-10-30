# /monitor - target class, observability, and capability detection

Read at Stage 0. Everything here is **detected from the repo and the environment**, never assumed
and never keyed to a project name. A project can match several rows; check all of them.

## 1. Deploy target class

| Detect | Class | What "healthy" means here |
|---|---|---|
| `vercel.json`, `.vercel/`, `next.config.*` | PaaS (Vercel) | routes 2xx + content, functions execute, no runtime errors in the platform log |
| `netlify.toml` | PaaS (Netlify) | same shape |
| `wrangler.toml` | PaaS (Cloudflare) | same shape, plus Workers invocation errors |
| `fly.toml` | PaaS (Fly) | machine state running, health checks passing |
| `render.yaml`, `railway.json`, `Procfile` | PaaS (other) | same shape; read the provider's own health surface |
| `Chart.yaml`, `values.yaml`, `k8s/`, `helm/` | **Kubernetes** | see §2 below |
| `docker-compose*.y*ml` without k8s | Compose | container state `running` + healthcheck passing, restart counts flat |
| a `*.service` unit, or a documented systemd deploy | systemd | unit `active (running)`, no recent restarts in `journalctl` |
| cron invoking a `deploy-*.sh` on a known host | poll-cron | deployed sha == origin tip; last run succeeded |
| none of the above | static / library | public URL only, or "no deploy mechanism" and skip runtime stages |

A repo can have **both** a PaaS preview and a self-hosted production target. Check both and score
them separately.

## 2. Kubernetes: what actually needs checking

A green `kubectl rollout status` confirms only that pods started and passed readiness. It is the
first signal, not the last. Check, in this order:

1. **Rollout completed** - `kubectl rollout status deploy/<name> -n <ns> --timeout=60s`
2. **Pods ready** - desired == ready == available
3. **Restart counts** - `kubectl get pods -n <ns> -o wide`. A pod that is Ready *now* but has
   restarted several times since the deploy is failing intermittently; current state hides it.
4. **Probe-failure events** - `kubectl get events -n <ns> --field-selector reason=Unhealthy`.
   Recurring probe noise is itself a finding: a log line that always appears is a log line nobody
   reads, so the first real failure looks like more of the same.
5. **Running image == deployed image** - compare the pod's image digest against the sha that was
   just shipped. A rollout can succeed while serving the previous image.
6. **Ingress / load-balancer target health** - pods can be Ready while the target group has pulled
   them out. This is the gap that turns a database capacity blip into 502s, and pod-level checks
   alone will not see it.
7. **Golden signals** - see §3. A rollout that is green while latency or error rate is degraded is
   not a successful deploy.

## 3. Observability backend

| Detect | Backend | Use for |
|---|---|---|
| `dd-trace`, `DD_API_KEY`, `datadoghq` in deps/charts | Datadog | golden signals: latency, traffic, errors, saturation |
| `@sentry/*` in deps | Sentry | error rate, new-issue detection since the deploy |
| Vercel/Netlify/CF project detected | platform-native | runtime error log for the last hour |
| `/metrics` endpoint, `prometheus` in charts | Prometheus | golden signals by query |
| none | none | fall back to observed request timings from Stage 2, and say the error-rate category is unmeasured |

Where an APM exists, its monitors may be shared with other teams. **Only report on monitors this
project owns** - usually identifiable by a name prefix or tag. Do not raise findings against another
team's alerts.

## 4. Capability gating - check once, degrade as a unit

Cluster access and cloud-hosted APM credentials usually depend on the **same** cloud session. When it
has expired, both are unavailable together. Test once, at Stage 0:

```bash
command -v kubectl && kubectl config current-context      # is there a context at all
timeout 8 kubectl get ns >/dev/null 2>&1                  # is it reachable RIGHT NOW
timeout 8 aws sts get-caller-identity >/dev/null 2>&1     # cloud session alive
```

| Result | Behaviour |
|---|---|
| session alive | full check: cluster + APM + public surface |
| session expired or absent | public surface + deployment API only. **Report it explicitly:** "cluster and APM checks skipped - no active cloud session; run the SSO login for full coverage." Mark those categories DEFERRED and renormalise the score. |
| no cluster context at all | not a Kubernetes project; skip §2 silently, it is not a gap |

An expired session is the normal case, not an error. The run still produces a useful report of
everything publicly reachable; it just says plainly what it could not see.

## 5. Reuse the project's own verification tooling

Before writing any check, look for verification the project already trusts:

```bash
ls scripts/verify/ infra/*/scripts/verify/ 2>/dev/null
ls scripts/smoke* scripts/healthcheck* 2>/dev/null
grep -l 'healthz\|readyz\|/health' charts/*/values.yaml 2>/dev/null
```

If an orchestrator exists (`verify-all.sh` or similar), **run the relevant subset and parse its
results into the scoring categories** rather than reimplementing the checks. A project with dozens of
maintained verify scripts already encodes what "healthy" means for it; a second opinion invented here
would only disagree.

Health endpoints are usually declared in the chart or compose file (`/healthz` for liveness,
`/readyz` for readiness) - read them from config rather than guessing paths.

## 6. Read what sibling skills already found

Before scanning, check whether another skill has recent output for this repo. It changes what is
worth looking at and prevents re-deriving something already known.

| Directory | Skill | Use |
|---|---|---|
| `.gh-ship-history.json`, `.ship-reports/` | `/gh-ship` | what was deployed, which PR, which sha - sets the trigger and the comparison point |
| `.qatest-reports/` | `/qatest` | known-failing routes; do not re-report them as new |
| `.sec-ship-reports/` | `/sec-ship` | header and SSL findings already raised; cross-reference rather than duplicate |
| `.perf-reports/` | `/perf` | prior response-time baselines |

A finding another skill already raised and the operator already triaged is noise here. Reference it;
do not re-open it.

## 7. Recording detection

Stage 0 writes what it found into the report header, so the scope of the run is auditable:

```
Target class : kubernetes (9 services, 8 charts) + poll-cron
Observability: datadog (golden signals), platform log unavailable
Capabilities : kubectl context present, cluster UNREACHABLE (no cloud session)
Reusing      : scripts/verify/verify-all.sh (12 of 57 scripts relevant)
Baseline     : none - this run establishes one
```

The "unreachable" and "none" lines are the important ones. They are what tells the reader why a
category is missing, and they belong in the SITREP next to the score.
