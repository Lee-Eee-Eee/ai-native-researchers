"""Run the synthetic research workflow and close its first stage in an empty directory."""

import argparse
import csv
from decimal import Decimal
from importlib import metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv


SKILL = Path(__file__).resolve().parents[1] / "skills" / "ai-native-researchers"
STARTER = SKILL / "assets" / "snakemake-starter"
VERSION = "9.27.0"
MARKER = "ai-native-researchers/synthetic-observations/v1\n"
MANIFEST = "docs/001_observed-peaks.evidence.json"
INPUTS = ["data/observations.csv", "Snakefile", "scripts/check_observations.py", "scripts/summarize.py"]
OUTPUTS = ["results/accepted.csv", "results/quality.json", "results/summary.csv"]


def prepare(root):
    root.mkdir(parents=True, exist_ok=True)
    marker = root / ".ai-native-demo"
    if marker.exists():
        if marker.read_text(encoding="utf-8") != MARKER:
            raise ValueError(f"Unrecognised demo directory: {root}")
    else:
        if any(root.iterdir()):
            raise ValueError(f"Choose an empty directory. No files were changed in {root}")
        with marker.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(MARKER)
    for name in ["README.md", *INPUTS]:
        path = root / name
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with (STARTER / name).open("rb") as src, path.open("xb") as dst:
                shutil.copyfileobj(src, dst)


def local_runner(root):
    envdir = root / ".venv"
    python = envdir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.is_file():
        if envdir.exists() and any(envdir.iterdir()):
            raise ValueError(f"Incomplete environment at {envdir}. Choose a fresh demo directory.")
        venv.EnvBuilder(with_pip=True).create(envdir)
    version_probe = subprocess.run(
        [str(python), "-c", "from importlib.metadata import version; print(version('snakemake'))"],
        capture_output=True, text=True,
    )
    if version_probe.stdout.strip() != VERSION:
        uv = shutil.which("uv")
        installer = [uv, "pip", "install", "--python", str(python)] if uv else [
            str(python), "-m", "pip", "install", "--disable-pip-version-check",
        ]
        subprocess.run([*installer, f"snakemake=={VERSION}"], check=True)
    return [str(python), "-m", "snakemake"], python.parent


def choose_runner(root):
    try:
        installed = metadata.version("snakemake")
    except metadata.PackageNotFoundError:
        installed = None
    if installed == VERSION:
        return [sys.executable, "-m", "snakemake"], Path(sys.executable).parent
    if not (root / ".venv").exists():
        cli = shutil.which("snakemake")
        if cli:
            probe = subprocess.run([cli, "--version"], capture_output=True, text=True)
            if probe.returncode == 0 and probe.stdout.strip() == VERSION:
                return [cli], Path(cli).parent
    return local_runner(root)


def describe(root):
    with (root / OUTPUTS[2]).open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    quality = json.loads((root / OUTPUTS[1]).read_text(encoding="utf-8"))
    if not rows or len(rows) != quality["series_count"] or sum(int(row["n"]) for row in rows) != quality["rows_accepted"]:
        raise ValueError("Series or observation counts disagree between the quality report and summary")
    earliest = min(Decimal(row["first_peak_h"]) for row in rows)
    leaders = "、".join(row["series"] for row in rows if Decimal(row["first_peak_h"]) == earliest)
    peaks = "；".join(f"{r['series']} 在第 {Decimal(r['first_peak_h']):g} 小时达到 {Decimal(r['peak_reading']):g}" for r in rows)
    return {
        "id": "observed-peaks", "number": 1, "question": "哪组观测最早达到各自的最高读数？",
        "finding": f"{leaders} 最早达到本组最高读数。{peaks}。读数以任意单位计。",
        "comparison": (f"比较 {len(rows)} 组合成观测。{quality['rows_read']} 条记录中有 "
                       f"{quality['rows_accepted']} 条有效，{quality['missing_readings']} 条读数缺失。"
                       "同组读数并列最高时，采用最早观测时刻。"),
        "command": "snakemake --cores 1", "inputs": INPUTS, "outputs": OUTPUTS,
        "next": "在峰值前后加密采样，检查两组峰值的先后顺序是否仍然一致。",
    }


def run_demo(root):
    manifest = root / MANIFEST
    verify = [sys.executable, str(SKILL / "scripts/evidence.py"), "verify",
              "--root", str(root), "--manifest", MANIFEST]
    # Check old evidence before any repair or workflow could rewrite a missing/changed file.
    if manifest.is_file():
        subprocess.run(verify, check=True)
    prepare(root)
    runner, bindir = choose_runner(root)
    env = dict(os.environ, PATH=str(bindir) + os.pathsep + os.environ.get("PATH", ""))
    subprocess.run([*runner, "--cores", "1"], cwd=root, env=env, check=True)
    spec = describe(root)
    specfile = root / "stage.json"
    if specfile.exists():
        if json.loads(specfile.read_text(encoding="utf-8-sig")) != spec:
            raise ValueError(f"Existing description differs from the computed result: {specfile}")
    else:
        with specfile.open("x", encoding="utf-8") as stream:
            json.dump(spec, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    subprocess.run([sys.executable, str(SKILL / "scripts/close_stage.py"), str(specfile),
                    "--root", str(root)], check=True)
    subprocess.run(verify, check=True)
    print(f"Open {root / 'README.md'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="A new/empty directory, or this demo's previous directory")
    args = parser.parse_args()
    try:
        run_demo(args.directory.resolve())
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"{exc}\n")
