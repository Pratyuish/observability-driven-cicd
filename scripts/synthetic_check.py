#!/usr/bin/env python3
"""Minimal synthetic HTTP transaction checker."""

from __future__ import annotations

import argparse
import json
import time
from urllib import request, error


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--max-latency-ms", type=float, default=500.0)
    args = parser.parse_args()

    started = time.perf_counter()
    status = None
    failure = None

    try:
        with request.urlopen(args.url, timeout=args.timeout) as response:
            status = response.status
    except (error.URLError, TimeoutError) as exc:
        failure = str(exc)

    latency_ms = (time.perf_counter() - started) * 1000
    passed = failure is None and status is not None and 200 <= status < 400 and latency_ms <= args.max_latency_ms

    result = {
        "url": args.url,
        "status": status,
        "latency_ms": round(latency_ms, 2),
        "max_latency_ms": args.max_latency_ms,
        "passed": passed,
        "error": failure,
    }

    print(json.dumps(result, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
