# Architecture

## Design objective

A deployment is considered successful only when the candidate release is
healthy from the cluster, application, and business perspectives.

## Target flow

```text
Developer
   |
   v
GitHub PR
   |
   v
CI validation
   |
   v
Change-risk analysis
   |
   v
Pre-deployment gate
   |
   v
Argo CD / Argo Rollouts
   |
   v
Canary
   |
   +--> OpenTelemetry Collector
   |       |--> Prometheus
   |       |--> Tempo
   |       +--> Loki
   |
   v
Post-deployment SLO analysis
   |
   +--> pass --> promote
   |
   +--> fail --> pause / rollback
                  |
                  v
             RCA agent
                  |
                  v
         human-approved remediation
```

## Safety principles

1. Observability data is evidence; AI output is advisory by default.
2. A deterministic gate is preferred when a clear threshold exists.
3. Agents receive least-privilege tools.
4. Production-changing actions require explicit approval by default.
5. Every automated decision should produce an auditable report.
6. The local demo must work without paid APIs.
