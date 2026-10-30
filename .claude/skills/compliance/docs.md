# /compliance - document generation

Every generated document is a **reviewable draft**, not a final or legal artefact. Fields needing
human or legal input are flagged inline (e.g. `[LEGAL REVIEW: retention period per jurisdiction]`).
Place documents where the project already keeps compliance artefacts; do not create a parallel store.

## Privacy-facing

- **Privacy policy** - what is collected, why, the legal basis, sharing, retention, rights, contact.
  Generated FROM the data map (frameworks.md step 2), so it matches reality rather than boilerplate.
- **Cookie policy / consent notice** - the actual cookies, categorised, with the consent mechanism.
- **DPA** (data processing agreement) - for the app as processor, or to require of sub-processors.
- **DSAR process doc** - how a data-subject request is received, verified, and fulfilled in time.
- **Data retention & deletion policy** - per data category, with the deletion mechanism.

## SOC 2 / enterprise readiness

- **SOC 2 readiness assessment** - the Trust Services Criteria mapped to existing controls and
  evidence, with the gaps as an action list.
- **Security policies** the audit expects to exist: access control, change management, vulnerability
  management, incident response, data classification, vendor management. Each generated as a draft
  reflecting how the project ACTUALLY operates (read the repo - the CI, the deploy flow, the incident
  history) rather than a generic template that an auditor will see through.

## The rule that keeps generated docs honest

**Generate from what is true, not from a template.** A privacy policy that claims practices the code
does not follow is a liability, not a compliance artefact - a regulator or a plaintiff will compare
the policy to the behaviour. So generation reads the data map and the code first, and the document
describes the real system. Where the real system falls short of what the document should say, that is
a FINDING for the audit, not something to paper over in the doc.

## Where the project already has deliverables

Some projects (regulated ones especially) keep a threat model, a system security plan, a controls
matrix, HIPAA transmission-controls docs, in the repo as living deliverables. **Update those in place**
rather than generating a competing set - a parallel document immediately drifts and the project ends
up with two sources of truth, which is worse than one imperfect one.
