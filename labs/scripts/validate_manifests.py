
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "ai-k8s-incident-lab"

files = [
    BASE / "manifests/fixes/inc-001-fixed.json"
]

def validate(path):
    manifest = json.loads(path.read_text())

    assert manifest["apiVersion"] == "apps/v1"
    assert manifest["kind"] == "Deployment"
    assert manifest["metadata"]["namespace"] == "ai-incidents"

    spec = manifest["spec"]
    selector = spec["selector"]["matchLabels"]
    labels = spec["template"]["metadata"]["labels"]

    assert all(labels.get(k) == v for k, v in selector.items())

    containers = spec["template"]["spec"]["containers"]

    for container in containers:
        image = container["image"]
        assert not image.endswith(":latest")
        assert not container.get(
            "securityContext", {}
        ).get("privileged", False)

    if manifest["metadata"]["name"] == "inc-001":
        probe = containers[0]["readinessProbe"]["httpGet"]
        assert probe["path"] == "/"
        assert probe["port"] == 80

    print("PASS:", path.name)

for file in files:
    if not file.exists():
        sys.exit(f"Missing file: {file}")
    validate(file)

print("Manifest validation successful")
