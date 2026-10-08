# Observability-Driven CI/CD

An open-source reference implementation for **health-aware Kubernetes delivery**.

Instead of declaring a deployment successful only because Kubernetes reports a completed rollout, this project uses **pre-deployment and post-deployment observability gates** to decide whether a release should proceed, pause, or roll back.

## Quick demo

The repository now includes a working local model using:

- **kind** for Kubernetes
- a small observable Python API
- **OpenTelemetry Collector**
- **Prometheus**
- **Grafana**

### Prerequisites

Install and start:

- Docker
- kind
- kubectl
- curl
- make

### Start everything

```bash
git clone https://github.com/Pratyuish/observability-driven-cicd.git
cd observability-driven-cicd
make demo
```

`make demo` will:

1. build the local demo API image,
2. create or reuse the `odc-demo` kind cluster,
3. load the image into kind,
4. deploy the API, OpenTelemetry Collector, Prometheus, and Grafana,
5. wait for all deployments,
6. start local port-forwards,
7. generate starter traffic,
8. verify the main endpoints.

After startup:

| Component | URL |
| --- | --- |
| Demo API | http://localhost:8080 |
| API health | http://localhost:8080/health |
| API metrics | http://localhost:8080/metrics |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

Grafana local credentials:

```text
username: admin
password: admin
```

### Generate healthy traffic

```bash
make traffic
```

### Inject an intentional regression

```bash
make bad-traffic
```

The bad-traffic target introduces slow requests and HTTP 500 responses so you can see the observability signals change immediately.

Useful PromQL examples:

```promql
demo_http_requests_total
```

```promql
rate(demo_http_requests_total[1m])
```

```promql
histogram_quantile(
  0.95,
  sum by (le) (
    rate(demo_http_request_duration_seconds_bucket[1m])
  )
)
```

### Run the pre-deployment health check

```bash
make precheck
```

This checks Kubernetes API connectivity and node health and writes a JSON report under `reports/`.

### Stop the demo

```bash
make demo-down
```

## Goals

- Validate cluster and application health before deployment.
- Deploy progressively with measurable health gates.
- Evaluate SLOs using Prometheus-compatible metrics.
- Correlate metrics, logs, traces, Kubernetes events, and deployment metadata.
- Add optional agentic AI for risk analysis and root-cause analysis.
- Keep remediation human-approved by default.
- Be runnable locally with free/open-source tooling.
- Provide a contributor-friendly Apache-2.0 licensed project.

## Reference flow

```text
GitHub Pull Request
        |
        v
CI: test -> lint -> security checks
        |
        v
Pre-deployment health gate
        |
        v
Progressive deployment
        |
        v
Post-deployment health gate
        |
        +---- healthy ----> promote
        |
        +---- unhealthy --> stop / rollback
                              |
                              v
                         RCA agent
                              |
                              v
                     GitHub issue/report
```

## Stack

| Area | Technology |
| --- | --- |
| Source control / CI | GitHub + GitHub Actions |
| Local Kubernetes | kind |
| Continuous delivery | Argo CD planned |
| Progressive delivery | Argo Rollouts planned |
| Telemetry | OpenTelemetry Collector |
| Metrics | Prometheus |
| Visualization | Grafana |
| Traces | Tempo planned |
| Logs | Loki planned |
| SLO gates | PromQL + Python |
| Agents | Python; LangGraph planned |
| Policy | OPA/Rego planned |
| License | Apache-2.0 |

## Health model

The project separates deployment health into three layers:

1. **Cluster health** — Kubernetes API, nodes, DNS, scheduling, critical workloads.
2. **Application health** — availability, latency, errors, saturation, pod restarts.
3. **Business health** — synthetic end-to-end transactions representing customer journeys.

A release should be promoted only when all required gates pass.

## Initial SLO examples

- Availability >= 99%
- HTTP 5xx rate < 1%
- p95 latency < 500 ms
- Pod restart delta <= 2
- Synthetic transaction success >= 99%

See [`slo/slo.yaml`](slo/slo.yaml).

## Agentic AI principles

AI is **optional** and must not be required to run the base project.

Initial modes:

- `mock` — deterministic/rule-based logic; no API key.
- `local` — future local-model integration.
- `hosted` — future pluggable hosted LLM integration.

Agents may analyze and recommend. Production-changing remediation remains **approval-required by default**.

## Roadmap

See [ROADMAP.md](ROADMAP.md).

## Contributing

Contributions are welcome. Start with [CONTRIBUTING.md](CONTRIBUTING.md), then look for issues labeled `good first issue` or `help wanted`.

## Security

Please do not report vulnerabilities in public issues. See [SECURITY.md](SECURITY.md).

## License

Licensed under the [Apache License 2.0](LICENSE).
