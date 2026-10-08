#!/usr/bin/env python3
"""Tiny dependency-free demo API with Prometheus-format metrics."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
import os
import random
import time

REQUESTS = {"200": 0, "500": 0}
LATENCY_BUCKETS = {0.1: 0, 0.25: 0, 0.5: 0, 1.0: 0, 2.5: 0, float("inf"): 0}
LATENCY_SUM = 0.0
LATENCY_COUNT = 0


def observe(seconds: float) -> None:
    global LATENCY_SUM, LATENCY_COUNT
    LATENCY_SUM += seconds
    LATENCY_COUNT += 1
    for bound in LATENCY_BUCKETS:
        if seconds <= bound:
            LATENCY_BUCKETS[bound] += 1


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        started = time.perf_counter()
        path = urlparse(self.path).path
        status = 200
        body = b"observability-driven-cicd demo\n"

        if path == "/health":
            body = b'{"status":"ok"}\n'
        elif path == "/bad":
            time.sleep(0.8)
            status = 500
            body = b'{"status":"error","reason":"intentional demo failure"}\n'
        elif path == "/work":
            time.sleep(random.uniform(0.02, 0.18))
            body = b'{"status":"ok","work":"completed"}\n'
        elif path == "/metrics":
            self._metrics()
            return
        elif path != "/":
            status = 404
            body = b'{"status":"not-found"}\n'

        REQUESTS[str(status)] = REQUESTS.get(str(status), 0) + 1
        observe(time.perf_counter() - started)

        self.send_response(status)
        self.send_header("Content-Type", "application/json" if body.startswith(b"{") else "text/plain")
        self.end_headers()
        self.wfile.write(body)

    def _metrics(self):
        lines = [
            "# HELP demo_http_requests_total Total HTTP requests.",
            "# TYPE demo_http_requests_total counter",
        ]
        for status, value in sorted(REQUESTS.items()):
            lines.append(f'demo_http_requests_total{{status="{status}"}} {value}')

        lines += [
            "# HELP demo_http_request_duration_seconds Request duration.",
            "# TYPE demo_http_request_duration_seconds histogram",
        ]
        for bound, value in LATENCY_BUCKETS.items():
            le = "+Inf" if bound == float("inf") else str(bound)
            lines.append(f'demo_http_request_duration_seconds_bucket{{le="{le}"}} {value}')
        lines.append(f"demo_http_request_duration_seconds_sum {LATENCY_SUM}")
        lines.append(f"demo_http_request_duration_seconds_count {LATENCY_COUNT}")
        lines.append('demo_build_info{version="good"} 1')

        payload = ("\n".join(lines) + "\n").encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4")
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args):
        print(f"[demo-api] {self.address_string()} {fmt % args}")


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    print(f"demo-api listening on :{port}")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
