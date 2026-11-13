import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

NAMESPACE = "ai-incidents"
CONTEXT = "kind-ai-incident-lab"
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
INCIDENTS = [f"inc-{i:03d}" for i in range(1, 6)]

def execute(args, timeout=60):
    try:
        p = subprocess.run(
            args, capture_output=True, text=True,
            timeout=timeout
        )
        output = p.stdout
        if p.stderr:
            output += "\nSTDERR:\n" + p.stderr
        return output, p.returncode
    except subprocess.TimeoutExpired:
        return "COMMAND TIMED OUT\n", 124

def capture(folder, filename, args):
    output, code = execute(args)
    (folder / filename).write_text(output)
    print(f"  {filename}: exit={code}")
    return output

def collect(incident):
    folder = ROOT / "evidence" / incident
    folder.mkdir(parents=True, exist_ok=True)

    print(f"\nCollecting {incident}")

    (folder / "collection-time.txt").write_text(
        datetime.now(timezone.utc).isoformat()
    )

    base = ["kubectl", "-n", NAMESPACE]

    pods_text = capture(
        folder, "pods.json",
        base + [
            "get", "pods", "-l", f"app={incident}",
            "-o", "json"
        ]
    )

    capture(
        folder, "deployment.yaml",
        base + ["get", "deployment", incident, "-o", "yaml"]
    )

    capture(
        folder, "pod-description.txt",
        base + ["describe", "pods", "-l", f"app={incident}"]
    )

    capture(
        folder, "replicasets.json",
        base + [
            "get", "replicasets",
            "-l", f"app={incident}", "-o", "json"
        ]
    )

    capture(
        folder, "git-history.txt",
        ["git", "-C", str(REPO), "log", "-5",
         "--format=%h %aI %s"]
    )

    try:
        pods = json.loads(pods_text).get("items", [])
    except json.JSONDecodeError:
        pods = []

    # Collect namespace events, then retain events associated
    # with this workload's pod UIDs or ReplicaSet.
    events_text, code = execute(
        base + ["get", "events", "-o", "json"]
    )

    if code == 0:
        try:
            all_events = json.loads(events_text)
            pod_uids = {
                p["metadata"]["uid"] for p in pods
            }

            relevant = []
            for event in all_events.get("items", []):
                obj = event.get("involvedObject", {})
                name = obj.get("name", "")
                uid = obj.get("uid", "")

                if (
                    uid in pod_uids
                    or name == incident
                    or name.startswith(incident + "-")
                ):
                    relevant.append(event)

            (folder / "events.json").write_text(
                json.dumps(relevant, indent=2)
            )
        except json.JSONDecodeError:
            (folder / "events-error.txt").write_text(
                events_text
            )
    else:
        (folder / "events-error.txt").write_text(
            events_text
        )

    for pod in pods:
        pod_name = pod["metadata"]["name"]
        containers = pod.get("spec", {}).get(
            "containers", []
        )

        for container in containers:
            cname = container["name"]

            for previous, suffix in [
                (False, "current"),
                (True, "previous")
            ]:
                args = base + [
                    "logs", pod_name,
                    "-c", cname,
                    "--timestamps=true",
                    "--tail=200"
                ]

                if previous:
                    args.append("--previous=true")

                safe_name = f"{pod_name}-{cname}-{suffix}.log"
                capture(folder, safe_name, args)

    print(f"Saved evidence to: {folder}")

def main():
    context, code = execute(
        ["kubectl", "config", "current-context"]
    )

    if code != 0 or context.strip() != CONTEXT:
        sys.exit(
            f"Refusing unexpected Kubernetes context: {context}"
        )

    selected = sys.argv[1:] or INCIDENTS

    if any(i not in INCIDENTS for i in selected):
        sys.exit("Invalid incident ID")

    for incident in selected:
        collect(incident)

if __name__ == "__main__":
    main()
