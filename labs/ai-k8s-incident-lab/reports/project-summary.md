# AI-Assisted Kubernetes Incident-to-PR Lab

**A reproducible SRE/AIOps demonstration: from Kubernetes failure evidence to explainable RCA, human-reviewed remediation, and recovery verification.**

Repository: https://github.com/Pratyuish/observability-driven-cicd

## What this project demonstrates

This lab uses a **local Kind Kubernetes cluster**, controlled failure scenarios, structured evidence collection, AI-assisted read-only investigation, draft GitHub pull requests, and validation gates. The focus is **explainability and deployment safety**, not unsupervised auto-remediation.

### Workflow

```text
Controlled fault in local Kind
         |
         v
kubectl status + events + manifests + logs
         |
         v
Sanitized evidence bundle / ai-input.txt
         |
         v
AI-assisted read-only RCA (symptoms, cause, confidence, evidence, uncertainty)
         |
         v
Human review / draft pull request
         |
         v
Static checks + Kubernetes API dry-run
         |
         v
Manual Kind deployment + pod/service/HTTP validation
         |
         v
Evidence-backed report and scorecard
```

## Five incident scenarios

| Incident | Failure mode | Local lab validation |
|---|---|---|
| INC-001 | Invalid readiness probe | Deployment recovered; 20/20 post-fix HTTP checks succeeded |
| INC-002 | OOMKilled from under-sized memory limit | 1/1 ready; next reported termination completed normally, exit 0 |
| INC-003 | Missing required ConfigMap | 1/1 ready; 0 restarts after ConfigMap creation |
| INC-004 | Unresolvable internal dependency hostname | 1/1 ready; 0 restarts; 15 HTTP 200 dependency check logs |
| INC-005 | Registry hostname cannot resolve / ImagePullBackOff | 1/1 ready; 0 restarts; substitute NGINX returned HTTP 200 |

**Result:** 5/5 scenarios have reported lab recovery validation. Four cases (INC-002–INC-005) were re-reviewed against uploaded diagnostic evidence. These are demonstration results, not blinded AI accuracy scores or production reliability metrics.

## Key engineering practices

- **Evidence-first:** every diagnosis is traced to observable YAML, JSON, events, or container logs where available.
- **Explicit uncertainty:** distinguishes a confirmed DNS failure from an unverified reason why a Service/registry was absent.
- **No autonomous writes:** AI analysis never executes `kubectl` or approves its own remediation.
- **Guardrails:** draft PR + human review + schema/server dry-run + actual post-fix verification.
- **Reproducibility:** preserve original failing manifests and corrected manifests separately.
- **Honest measurement:** investigation timing, model tokens, AI cost, and production MTTR gains are not yet instrumented.

## Published artifacts

- `labs/ai-k8s-incident-lab/reports/final-ai-rca-evaluation.md` — detailed methodology, case review, limitations, and next steps.
- `labs/ai-k8s-incident-lab/reports/incident-scorecard.csv` — machine-readable case-by-case scorecard.
- `labs/ai-k8s-incident-lab/reports/project-summary.md` — this README-ready overview.

> Security: do not commit raw evidence packages or secrets without reviewing/sanitizing them. The bundled scorecard is curated and does not include raw cluster dumps.

## Next iteration

A future controlled evaluation will benchmark blind diagnosis against a locked ground-truth key, compare AI-assisted vs manual SRE time, record token and cost metrics, and introduce repeatable rollout gates, canary checks, and rollback criteria.

**License:** Follow the repository's existing license; do not assume a license is in place without verifying it.
