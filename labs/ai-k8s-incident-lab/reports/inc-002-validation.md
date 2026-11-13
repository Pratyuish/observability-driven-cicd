# INC-002 — Kubernetes OOM Remediation Validation

## Incident
Synthetic container memory exhaustion causing OOMKilled
and CrashLoopBackOff.

## Root cause
The application attempted a 128 MiB allocation while
the container was limited to 32 MiB.

## Remediation
Memory request increased from 16Mi to 64Mi.
Memory limit increased from 32Mi to 256Mi.

## Observed post-remediation results

| Check | Result |
|---|---|
| Deployment availability | 1/1 |
| Pod readiness | 1/1 Running |
| Restart count | 1 |
| Previous exit code | 0 |
| Previous termination reason | Completed |
| Current state | Running |
| OOMKilled in latest termination | No |

## Assessment
The previous process execution completed successfully.
The observed restart is consistent with the Deployment's
Always restart policy.

The reported execution no longer exhibits the original
OOMKilled termination.

## Limitations
Actual peak memory usage was not measured.
Long-term memory stability was not established.
Recovery time was not independently measured.
This is a local Kind test, not production DR.

## Approval
Human review required before merging the remediation PR.
