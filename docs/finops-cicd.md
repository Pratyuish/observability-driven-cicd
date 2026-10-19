# FinOps-driven CI/CD

## Objective

Move infrastructure cost management left into the delivery lifecycle so that a
pull request can answer:

- What does the current infrastructure cost?
- What will the proposed infrastructure cost?
- What changed?
- Which resource caused the increase?
- Is the increase inside the approved budget envelope?
- Does the change require additional approval?

## Pipeline model

```text
Pull Request
    |
    v
Build / Test / Security
    |
    v
Infrastructure Cost Estimate
    |
    +--> baseline monthly run rate
    +--> candidate monthly run rate
    +--> absolute delta
    +--> percentage delta
    +--> resource-level breakdown
    |
    v
Budget Policy Gate
    |
    +---- PASS ----> reliability checks ----> deploy
    |
    +---- BLOCK ---> optimization / approval
```

## What the MVP estimates

The API-key-free estimator currently understands:

- Deployment / StatefulSet / ReplicaSet CPU and memory requests
- DaemonSet requests using a configurable assumed node count
- Pod and Job requests
- PersistentVolumeClaim requested storage
- Service type `LoadBalancer`

The model deliberately uses **requests rather than limits** because requests
drive Kubernetes scheduling and reserved capacity. Production environments may
replace the simple rates with provider-specific node, storage, networking,
commitment, and support pricing.

## Policy

`finops/budget-policy.yaml` defines governance thresholds:

- maximum candidate monthly cost,
- maximum percentage increase,
- maximum absolute increase,
- mandatory CPU/memory requests,
- approval threshold and owning team.

A failing rule returns exit code `2`, which causes a CI/CD job to fail before
deployment.

## Local demonstration

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run:

```bash
make cost-demo
```

The supplied candidate intentionally scales replicas, increases CPU/memory,
adds a LoadBalancer, and adds a PVC. It should be **BLOCKED** by policy.

Generate a report without failing the shell:

```bash
make cost-report
```

Reports are written to:

- `reports/cost-gate.json`
- `reports/cost-gate.md`

## Real-world evolution

### Kubernetes

Replace illustrative unit rates with:

- actual node-pool cost,
- Spot/On-Demand mix,
- Savings Plans / commitments,
- namespace/team allocation,
- OpenCost runtime data.

### Terraform

Add an IaC adapter that consumes:

- Terraform plan JSON,
- Infracost output,
- cloud pricing APIs,
- negotiated enterprise rate cards.

The same policy engine can remain unchanged.

### Optimization recommendations

The next stage can add a deterministic or AI-assisted optimization agent that
explains alternatives such as:

- reduce excessive requests,
- use autoscaling instead of fixed replicas,
- use a shared ingress instead of another LoadBalancer,
- move suitable workloads to Spot capacity,
- apply storage lifecycle/tiering,
- use committed-use discounts for stable baseline demand.

AI should recommend; policy should decide. Cost-changing production actions
should remain approval-controlled.
