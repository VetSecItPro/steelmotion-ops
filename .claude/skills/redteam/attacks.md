# /redteam - attack classes, chains, PoC standards

Read from Phase 2. Every payload targets localhost (see the spine's safety boundary). The point is
not to run a scanner - `/sec-ship` did that - but to actively confirm exploitability and chain
findings.

## Attack classes

### Authorization (usually the highest-value class)
- **IDOR / BOLA:** request another user's object by id. Create two test users; as user A, try to
  read/modify B's records. This is the most common real, high-impact finding.
- **Privilege escalation:** can a normal user reach an admin route? Mass-assign a `role`/`is_admin`
  field? Reach an operator-only action?
- **Auth bypass:** does the gate live in middleware only (bypassable) or at the handler? Does token
  validation actually verify a signature, or just shape?
- **Tenant isolation:** in multi-tenant apps, cross-tenant read/write.

### Injection (send live to localhost, read the real effect)
SQLi, NoSQL injection, command injection, template injection, header injection. A 500 is a clue, not
proof - confirm the actual effect (data returned, command run, template evaluated).

### SSRF and access-control-at-a-distance
Can a URL parameter make the server fetch an internal address, a cloud metadata endpoint, or a
localhost-only service? Under OWASP 2025 this is an access-control failure - the question is where the
server can be made to reach.

### Client-side
Stored and reflected XSS (does the payload actually execute, or is it escaped?), DOM XSS, prototype
pollution, sensitive data in localStorage.

### Business logic
Race conditions (fire concurrent requests at a counter/balance/idempotency key), replay, workflow
step-skipping, negative quantities, TOCTOU. These never show in a scanner and are frequently the
worst findings.

### Session and crypto
Predictable tokens, session fixation, missing rotation on privilege change, JWT alg confusion,
weak randomness in anything security-relevant.

### AI/LLM surface (respect the 3-request cap)
Prompt injection reaching a tool call or `eval`; model output used unsafely; system-prompt leakage;
excessive tool agency. Verify the rest by code review rather than burning requests.

## Chain construction - the Phase 3 core

A chain turns low findings into a high one. Method:

1. List every finding, including the ones `/sec-ship` rated low.
2. For each, ask what it *grants* - an id, a token, a redirect, a foothold, an information leak.
3. Look for a finding whose precondition is another finding's grant.
4. Walk the chain end to end against localhost and confirm each hop actually enables the next.

Canonical shapes to look for:
- info leak (verbose error / IDOR-readable id) → targeted attack using the leaked value
- open redirect → credential/token theft → session takeover
- weak reset flow → account takeover → privilege escalation
- SSRF → cloud metadata → credential → lateral movement (confirm only what is reachable from localhost)

**A chain is only CONFIRMED when every hop is demonstrated.** A plausible chain with an unproven hop
is reported as a chain hypothesis with the missing link named.

## PoC standard

A confirmed finding carries a reproduction another person can run:

```
Finding: IDOR on GET /api/documents/:id
Setup:   two test users (A id=..., B id=...) created via admin API
Steps:   1. auth as A   2. GET /api/documents/<B's doc id>
Result:  200, B's document body returned  (expected: 403)
Impact:  any authenticated user reads any document by id
Cleanup: both test users deleted
```

No PoC and no code-review basis → the finding is a **hypothesis**, ranked below anything proven, and
labelled so. Downgrading an unproven finding is not weakness; over-claiming is what makes a red-team
report untrustworthy.

## The attacker mindset

Assume the developer's assumptions are wrong. The endpoint that "only the frontend calls" is callable
directly. The id that is "always the current user's" is attacker-controlled. The value that is
"validated on the client" is not validated at all. Test the assumption, not the happy path.
