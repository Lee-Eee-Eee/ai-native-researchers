"""Generate a file inventory for the public example's paired milestone notes."""

import csv
import json
import re
import sys
from pathlib import Path


settings_path, output_path, *filenames = sys.argv[1:]
settings = json.loads(Path(settings_path).read_text(encoding="utf-8"))
first_stage, last_stage = settings["first_stage"], settings["last_stage"]
if not 1 <= first_stage <= last_stage <= 999:
    raise ValueError("Stage bounds must be ascending and within 1–999.")

notes = {}
for filename in filenames:
    note = Path(filename)
    match = re.fullmatch(r"([0-9]{3})(a?)_.+\.md", note.name)
    if match is None:
        continue
    stage, suffix = match.groups()
    key = (int(stage), suffix)
    if key in notes:
        raise ValueError(f"Multiple notes found for {stage}{suffix}.")
    notes[key] = note

rows = []
for stage in range(first_stage, last_stage + 1):
    decision = notes.get((stage, ""))
    evidence = notes.get((stage, "a"))
    if decision is None or evidence is None:
        raise ValueError(f"Stage {stage:03d} needs a decision note and an evidence note.")
    for source, target in ((decision, evidence), (evidence, decision)):
        if f"]({target.name})" not in source.read_text(encoding="utf-8"):
            raise ValueError(f"{source.name} needs a link to {target.name}.")
    rows.append((f"{stage:03d}", decision.as_posix(), evidence.as_posix()))

with Path(output_path).open("w", encoding="utf-8", newline="") as stream:
    writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
    writer.writerow(("stage", "decision_note", "evidence_note"))
    writer.writerows(rows)
