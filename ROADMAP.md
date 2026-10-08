# Roadmap

## v0.1 — Observable deployment foundation

- [ ] Sample microservice
- [ ] kind-based local Kubernetes environment
- [ ] OpenTelemetry Collector
- [ ] Prometheus
- [ ] Grafana
- [x] Initial SLO configuration
- [x] Pre/post deployment gate skeleton
- [ ] Synthetic transaction

## v0.2 — SLO deployment gates

- [ ] PromQL-backed availability gate
- [ ] Error-rate gate
- [ ] p95 latency gate
- [ ] Pod restart gate
- [ ] Baseline-vs-candidate comparison
- [ ] GitHub Actions gate report

## v0.3 — Progressive delivery

- [ ] Argo CD
- [ ] Argo Rollouts
- [ ] Canary 10% -> 50% -> 100%
- [ ] Automated analysis
- [ ] Automated rollback

## v0.4 — AI-assisted RCA

- [ ] Deployment-change context
- [ ] Metrics correlation
- [ ] Log correlation
- [ ] Trace correlation
- [ ] Kubernetes event correlation
- [ ] Deterministic mock agent
- [ ] Optional LLM provider interface

## v0.5 — Agentic delivery

- [ ] PreDeployAgent
- [ ] ChangeRiskAgent
- [ ] DeploymentObserverAgent
- [ ] RCAAgent
- [ ] RemediationAgent
- [ ] Human approval workflow
- [ ] Agent action audit trail

## v1.0 — Portable platform

- [ ] EKS reference
- [ ] GKE reference
- [ ] AKS reference
- [ ] RKE2 reference
- [ ] Pluggable observability backends
- [ ] Policy-as-code integration
- [ ] Stable contributor API and documentation
