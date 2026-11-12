# INC-001 — Readiness Probe Remediation

## Incident
Controlled Kubernetes readiness-probe failure.

## Proposed correction
Change the NGINX readiness-probe HTTP path to `/`.

## Validation results

| Check | Result |
|---|---|
| Kubernetes server-side dry run | PASS |
| Deployment available replicas | 1/1 |
| Recovered pod status | Running |
| Container restarts at verification | 0 |
| HTTP Service test | 20/20 successful |
| HTTP success rate | 100% |
| Exact recovery time | Not measured |
| Production impact | Not applicable — local Kind lab |

## Evidence
- Before-fix pod descriptions
- Corrected Deployment manifest
- After-fix Kubernetes pod status
- Service and EndpointSlice configuration
- HTTP test results
- Kubernetes events and application logs

## Limitations
The HTTP result covers 20 sampled requests after remediation.
It does not establish uninterrupted availability during the fault.
No production DR or RPO testing was performed.

## Approval
Human review is required before merging the draft pull request.
