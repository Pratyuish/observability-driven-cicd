# Agent Architecture

The project separates agent responsibilities so that permissions can be scoped
independently.

## Planned agents

### PreDeployAgent

Inputs:
- cluster health,
- active alerts,
- error-budget state,
- dependency health.

Output:
- PROCEED or BLOCK,
- supporting evidence.

### ChangeRiskAgent

Inputs:
- Git diff,
- Kubernetes/Helm changes,
- infrastructure changes.

Output:
- LOW / MEDIUM / HIGH risk,
- recommended rollout strategy.

### DeploymentObserverAgent

Inputs:
- metrics,
- logs,
- traces,
- Kubernetes events.

Output:
- current rollout-health assessment.

### RCAAgent

Triggered after an SLO failure.

Inputs:
- deployment metadata,
- before/after metrics,
- logs,
- traces,
- events.

Output:
- ranked hypotheses,
- evidence,
- confidence,
- recommended next investigation.

### RemediationAgent

Initially advisory only.

Potential suggestions:
- rollback,
- scale replicas,
- revert configuration,
- restart a failed workload,
- open a remediation PR.

## Execution modes

`mock`
: deterministic and API-key-free.

`local`
: planned local-model integration.

`hosted`
: planned provider interface for hosted LLMs.

## Guardrail

No agent should receive unrestricted production write access.
