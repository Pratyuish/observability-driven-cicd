# INC-005 — Image Pull Failure Recovery

## Original failure
The Kubernetes Deployment referenced:
registry.invalid/ai-lab/missing-app:v1

The registry hostname could not be resolved, resulting
in ImagePullBackOff and an unavailable Deployment.

## Remediation
Replaced the invalid image reference with nginx:1.27
for the isolated Kind demonstration.

## Verified result
- HTTP response through port-forward: 200 OK

## Final Kubernetes verification
- Deployment availability: 1/1
- Pod readiness: 1/1 Running
- Container restarts: 0
- Running image: nginx:1.27
- HTTP port-forward response: 200 OK

## Limitations
- The replacement image is a demonstration substitute.
- Original application functionality was not validated.
- Recovery duration was not precisely measured.
- This was a local Kind test, not production recovery.

## Approval
Human review required before merging.
