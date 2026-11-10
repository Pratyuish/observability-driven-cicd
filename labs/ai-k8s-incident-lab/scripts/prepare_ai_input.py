
import sys
from pathlib import Path

incident = sys.argv[1]
folder = Path("evidence") / incident

sections = [
    "pods.json",
    "deployment.yaml",
    "pod-description.txt",
    "events.json",
    "logs.txt",
    "previous-logs.txt",
    "git-history.txt"
]

output = folder / "ai-input.txt"

with output.open("w") as f:
    for name in sections:
        file = folder / name
        if file.exists():
            f.write(f"\n===== {name} =====\n")
            f.write(file.read_text(errors="replace"))
            f.write("\n")

print(f"AI evidence package: {output}")
