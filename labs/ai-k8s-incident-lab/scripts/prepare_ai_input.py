from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

def prepare(incident):
    folder = ROOT / "evidence" / incident

    if not folder.exists():
        raise SystemExit(f"No evidence: {folder}")

    names = [
        "collection-time.txt",
        "pods.json",
        "deployment.yaml",
        "pod-description.txt",
        "replicasets.json",
        "events.json",
        "git-history.txt"
    ]

    names += [
        p.name for p in sorted(folder.glob("*.log"))
    ]

    output = folder / "ai-input.txt"

    with output.open("w") as f:
        for name in names:
            file = folder / name

            if not file.exists():
                continue

            f.write(f"\n===== {name} =====\n")
            f.write(file.read_text(errors="replace"))
            f.write("\n")

    print("Created:", output)

for incident in sys.argv[1:]:
    prepare(incident)
