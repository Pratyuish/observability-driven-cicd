#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-good}"
COUNT="${COUNT:-50}"
BASE_URL="${BASE_URL:-http://127.0.0.1:8080}"

echo "Generating $COUNT requests in '$MODE' mode..."

for i in $(seq 1 "$COUNT"); do
  if [[ "$MODE" == "bad" ]] && (( i % 4 == 0 )); then
    curl -sS -o /dev/null "$BASE_URL/bad" || true
  else
    curl -sS -o /dev/null "$BASE_URL/work" || true
  fi
done

echo "Done. Open Prometheus/Grafana to inspect the signal."
