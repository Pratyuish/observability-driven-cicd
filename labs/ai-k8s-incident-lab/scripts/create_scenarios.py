
import json
from pathlib import Path

OUT = Path("manifests/incidents")
OUT.mkdir(parents=True, exist_ok=True)

NAMESPACE = "ai-incidents"

def deployment(name, image, command=None, **container_options):
    container = {
        "name": "app",
        "image": image,
        **container_options
    }

    if command is not None:
        container["command"] = command

    return {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": name,
            "namespace": NAMESPACE
        },
        "spec": {
            "replicas": 1,
            "selector": {
                "matchLabels": {"app": name}
            },
            "template": {
                "metadata": {
                    "labels": {"app": name}
                },
                "spec": {
                    "containers": [container]
                }
            }
        }
    }

scenarios = {}

# INC-001: Wrong readiness endpoint.
scenarios["inc-001"] = deployment(
    "inc-001", "nginx:1.27",
    readinessProbe={
        "httpGet": {"path": "/does-not-exist", "port": 80},
        "initialDelaySeconds": 2,
        "periodSeconds": 5
    }
)

# INC-002: Process tries to allocate more than its limit.
scenarios["inc-002"] = deployment(
    "inc-002", "python:3.12-alpine",
    command=[
        "python", "-c",
        "import time; a=bytearray(128*1024*1024); time.sleep(300)"
    ],
    resources={
        "requests": {"memory": "16Mi"},
        "limits": {"memory": "32Mi"}
    }
)

# INC-003: Required ConfigMap does not exist.
scenarios["inc-003"] = deployment(
    "inc-003", "nginx:1.27",
    envFrom=[{
        "configMapRef": {
            "name": "missing-app-config",
            "optional": False
        }
    }]
)

# INC-004: Required service does not exist.
scenarios["inc-004"] = deployment(
    "inc-004", "python:3.12-alpine",
    command=[
        "python", "-c",
        (
            "import urllib.request; "
            "urllib.request.urlopen("
            "'http://missing-api.ai-incidents.svc.cluster.local:8080',"
            "timeout=3)"
        )
    ]
)

# INC-005: Deliberately unavailable image.
scenarios["inc-005"] = deployment(
    "inc-005",
    "registry.invalid/ai-lab/missing-app:v1"
)

for name, manifest in scenarios.items():
    path = OUT / f"{name}.json"
    path.write_text(json.dumps(manifest, indent=2))
    print(f"Created: {path}")
