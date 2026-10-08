#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="${CLUSTER_NAME:-odc-demo}"
NAMESPACE="odc-demo"
IMAGE="observability-demo-api:local"
PID_DIR=".demo-pids"

need() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "ERROR: '$1' is required but was not found in PATH."
    exit 1
  }
}

need docker
need kind
need kubectl
need curl

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker is not running."
  exit 1
fi

echo "==> Building demo API image"
docker build -t "$IMAGE" apps/demo-api

if kind get clusters 2>/dev/null | grep -qx "$CLUSTER_NAME"; then
  echo "==> Reusing kind cluster: $CLUSTER_NAME"
else
  echo "==> Creating kind cluster: $CLUSTER_NAME"
  kind create cluster --name "$CLUSTER_NAME" --wait 120s
fi

echo "==> Loading local image into kind"
kind load docker-image "$IMAGE" --name "$CLUSTER_NAME"

echo "==> Applying demo stack"
kubectl apply -f kubernetes/demo-stack.yaml

echo "==> Waiting for deployments"
for d in demo-api otel-collector prometheus grafana; do
  kubectl -n "$NAMESPACE" rollout status "deployment/$d" --timeout=180s
done

echo "==> Starting local port-forwards"
mkdir -p "$PID_DIR"

start_pf() {
  local name="$1"
  local target="$2"
  local ports="$3"
  local pidfile="$PID_DIR/$name.pid"

  if [[ -f "$pidfile" ]] && kill -0 "$(cat "$pidfile")" 2>/dev/null; then
    echo "    $name port-forward already running"
    return
  fi

  kubectl -n "$NAMESPACE" port-forward "$target" "$ports" >"$PID_DIR/$name.log" 2>&1 &
  echo $! > "$pidfile"
}

start_pf demo-api svc/demo-api 8080:8080
start_pf prometheus svc/prometheus 9090:9090
start_pf grafana svc/grafana 3000:3000

sleep 3

echo "==> Generating starter traffic"
for _ in $(seq 1 25); do
  curl -fsS http://127.0.0.1:8080/work >/dev/null || true
done

echo "==> Verifying endpoints"
curl -fsS http://127.0.0.1:8080/health
curl -fsS http://127.0.0.1:9090/-/ready >/dev/null
curl -fsS http://127.0.0.1:3000/api/health >/dev/null

cat <<'EOF'

✅ observability-driven-cicd demo is running.

Demo API:
  http://localhost:8080
  http://localhost:8080/health
  http://localhost:8080/metrics

Prometheus:
  http://localhost:9090

Grafana:
  http://localhost:3000
  user: admin
  password: admin

Try these PromQL queries:
  demo_http_requests_total
  rate(demo_http_requests_total[1m])
  histogram_quantile(0.95, sum by (le) (rate(demo_http_request_duration_seconds_bucket[1m])))

Generate healthy traffic:
  make traffic

Inject intentional latency + HTTP 500s:
  make bad-traffic

Run the pre-deployment cluster health check:
  make precheck

Clean everything:
  make demo-down

EOF
