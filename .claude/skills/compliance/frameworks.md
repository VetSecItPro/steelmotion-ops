# /compliance - framework requirements and how to check each

Audit only the frameworks that actually apply (detect from the data the app handles). Each finding
cites the specific requirement it fails.

## GDPR (EU personal data)

| Requirement | Check |
|---|---|
| Legal basis (Art. 6) | every processing activity has a recorded basis: consent, contract, legal obligation, legitimate interests. Undocumented processing is a finding |
| Consent (Art. 7) | where consent is the basis: freely given, specific, unbundled, as easy to withdraw as to give. A pre-ticked box or cookie-wall fails |
| Data subject rights (Art. 15-22) | access, rectification, erasure, portability, objection - is there a mechanism, and does it work? |
| Data minimisation (Art. 5) | only data actually needed is collected. A signup asking for a phone number never used is a finding |
| Breach notification (Art. 33) | a process exists to notify within 72 hours |
| DPA with processors (Art. 28) | a data-processing agreement with every third party that touches personal data |
| Privacy by design (Art. 25) | defaults are privacy-protective, not privacy-exposing |
| International transfers (Ch. V) | data leaving the EU has a valid mechanism (adequacy, SCCs) |

## CCPA / CPRA (California)

Notice at collection; the right to know, delete, correct, and opt out of sale/sharing; a
"Do Not Sell or Share My Personal Information" link where applicable; no discrimination for exercising
rights; sensitive-personal-information limits. Check each against the actual site and code.

## HIPAA (US health data)

Applies only to covered entities and business associates handling PHI. Administrative, physical and
technical safeguards; a BAA with every subcontractor touching PHI; access controls and audit logging;
encryption in transit and at rest; a breach-notification process. **This is high-stakes - findings
here get a qualified reviewer, and the report says so explicitly.** Where the project already keeps
HIPAA deliverables (a controls matrix, transmission-controls doc), audit against and update THOSE.

## SOC 2 (Trust Services Criteria)

Not a checklist of code but of controls and evidence: security, availability, processing integrity,
confidentiality, privacy. The audit here is a **readiness** assessment - which of the common criteria
have a control and evidence, which are gaps. Access control, change management, vulnerability
management, incident response, data retention, monitoring. The output feeds the readiness doc.

## The audit method

1. **Detect applicability** - what data, what users, what jurisdiction, what customers. Only then pick
   frameworks.
2. **Map the data** - what personal/sensitive data the app collects, where it flows, where it rests,
   who it is shared with. Most findings come from the data map, not the policy.
3. **Check behaviour against requirement** - and against the app's own stated policy. Contradictions
   between code and policy are the highest-value findings.
4. **List gaps with citations and remediations** - each tied to its article/control, each with a
   concrete fix.
