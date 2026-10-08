#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="${CLUSTER_NAME:-odc-demo}"
PID_DIR=".demo-pids"

if [[ -d "$PID_DIR" ]]; then
  for pidfile in "$PID_DIR"/*.pid; do
    [[ -e "$pidfile" ]] || continue
    pid="$(cat "$pidfile")"
    kill "$pid" 2>/dev/null || true
  done
  rm -rf "$PID_DIR"
fi

if command -v kind >/dev/null 2>&1 && kind get clusters 2>/dev/null | grep -qx "$CLUSTER_NAME"; then
  kind delete cluster --name "$CLUSTER_NAME"
else
  echo "kind cluster '$CLUSTER_NAME' does not exist."
fi
