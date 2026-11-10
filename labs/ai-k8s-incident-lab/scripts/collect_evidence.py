
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

NS = "ai-incidents"
EXPECTED_CONTEXT = "kind-ai-incident-lab"

def run(*args):
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=90
    )
    return result.stdout + (
        "\nSTDERR:\n" + result.stderr
        if result.stderr else ""
    )

def save(folder, filename, *command):
    output = run(*command)
    (folder / filename).write_text(output)
    print("Saved:", folder / filename)

def main(incident):
    if incident not in [f"inc-{n:03d}" for n in range(1, 6)]:
        sys.exit("Invalid incident ID")

    context = subprocess.check_output(
        ["kubectl", "config", "current-context"],
        text=True
    ).strip()

    if context != EXPECTED_CONTEXT:
        sys.exit(f"Unsafe context: {context}")

    folder = Path("evidence") / incident
    folder.mkdir(parents=True, exist_ok=True)

    (folder / "collected-at.txt").write_text(
        datetime.now(timezone.utc).isoformat()
    )

    base = ["kubectl", "-n", NS]

    save(folder, "pods.json",
         *base, "get", "pods",
         "-l", f"app={incident}", "-o", "json")

    save(folder, "deployment.yaml",
         *base, "get", "deployment",
         incident, "-o", "yaml")

    save(folder, "pod-description.txt",
         *base, "describe", "pods",
         "-l", f"app={incident}")

    save(folder, "events.json",
         *base, "get", "events", "-o", "json")

    save(folder, "logs.txt",
         *base, "logs", "-l", f"app={incident}",
         "--all-containers=true",
         "--prefix=true", "--tail=200")

    save(folder, "previous-logs.txt",
         *base, "logs", "-l", f"app={incident}",
         "--all-containers=true",
         "--prefix=true", "--previous=true",
         "--tail=200")

    save(folder, "git-history.txt",
         "git", "log", "-5",
         "--format=%h %aI %s")

    source = Path("manifests/incidents") / f"{incident}.json"
    if source.exists():
        (folder / "submitted-manifest.json").write_bytes(
            source.read_bytes()
        )

    print(f"\nEvidence ready: {folder}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python3 scripts/collect_evidence.py inc-001")
    main(sys.argv[1])
