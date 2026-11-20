import csv
import json
import math
from pathlib import Path


def finite_number(text, field, line):
    try:
        value = float(text)
    except ValueError as exc:
        raise ValueError(f"line {line}: invalid {field} {text!r}") from exc
    if not math.isfinite(value):
        raise ValueError(f"line {line}: {field} must be finite")
    return value


def check_observations(source, accepted_path, report_path):
    seen = set()
    series_ids = set()
    accepted = []
    fields = ["series", "time_h", "reading"]
    with open(source, newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != fields:
            raise ValueError(f"expected columns: {', '.join(fields)}")
        for row in reader:
            line = reader.line_num
            if None in row or None in row.values():
                raise ValueError(f"line {line}: expected three columns")
            series = row["series"].strip()
            if not series:
                raise ValueError(f"line {line}: missing series ID")
            time_h = finite_number(row["time_h"], "time_h", line)
            key = (series, time_h)
            if key in seen:
                raise ValueError(f"line {line}: duplicate series/time {key}")
            seen.add(key)
            series_ids.add(series)
            if row["reading"].strip():
                reading = finite_number(row["reading"], "reading", line)
                accepted.append((series, time_h, reading))

    if not seen:
        raise ValueError("input table is empty")
    empty_series = series_ids - {series for series, _, _ in accepted}
    if empty_series:
        raise ValueError(f"no readings for series: {', '.join(sorted(empty_series))}")

    with open(accepted_path, "w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(fields)
        writer.writerows(sorted(accepted))

    report = {
        "rows_read": len(seen),
        "rows_accepted": len(accepted),
        "missing_readings": len(seen) - len(accepted),
        "series_count": len(series_ids),
    }
    Path(report_path).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


check_observations(snakemake.input[0], snakemake.output.observations, snakemake.output.report)
