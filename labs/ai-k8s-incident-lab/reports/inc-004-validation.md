# INC-004 — Dependency Recovery Validation

## Original failure
The Python application could not resolve:
missing-api.ai-incidents.svc.cluster.local

The application exited with code 1 and entered
CrashLoopBackOff.

## Root cause
DNS resolution failed for the required service dependency.
The unhandled application error caused repeated restarts.

## Remediation
- Added a mock missing-api dependency Service.
- Added a backing HTTP application on port 8080.
- Updated the synthetic Python client for repeated checks.
- Added a readiness check for dependency connectivity.

## Observed results
| Check | Result |
|---|---|
| Deployment availability | 1/1 |
| Pod readiness | 1/1 Running |
| Container restarts | 0 |
| Observed HTTP responses | 15/15 returned 200 |
| New pod age at inspection | 3m 59s |

## Assessment
The application successfully communicates with the
required dependency and remains running during the
observed validation period.

## Limitations
- Long-term resilience was not measured.
- Recovery duration was not independently measured.
- Dependency failure retry behavior was not tested.
- Test performed in local Kind, not production.

## Approval
Human review required before merging changes.
