"""Record and verify the content of explicitly selected research files."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def project_path(root, name):
    path = (root / name).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Path outside project: {name}")
    return path


def fingerprint(path):
    with path.open("rb") as stream:
        digest = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_state(root):
    def git(*args):
        return subprocess.run(
            ["git", "-C", str(root), *args], capture_output=True, text=True, check=True
        ).stdout.strip()

    try:
        return {"commit": git("rev-parse", "HEAD"), "dirty": bool(git("status", "--porcelain"))}
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def record(args, root, manifest):
    entries = []
    for role, names in (("input", args.input), ("output", args.output)):
        for name in names:
            path = project_path(root, name)
            if path == manifest:
                raise ValueError("The manifest cannot list itself")
            entries.append({
                "role": role,
                "path": path.relative_to(root).as_posix(),
                "sha256": fingerprint(path),
            })
    payload = {"schema": 1, "git": git_state(root), "files": entries}
    manifest.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    # Exclusive creation preserves earlier evidence and concurrent records.
    with manifest.open("x", encoding="utf-8") as stream:
        stream.write(content)
    print(f"Recorded {len(entries)} files in {manifest}")


def verify(root, manifest):
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    if payload.get("schema") != 1 or not payload.get("files"):
        raise ValueError("Unrecognised or empty evidence manifest")
    failures = []
    for entry in payload["files"]:
        path = project_path(root, entry["path"])
        if not path.is_file() or fingerprint(path) != entry["sha256"]:
            failures.append(entry["path"])
    if failures:
        raise ValueError("Missing or modified: " + ", ".join(failures))
    print(f"Verified {len(payload['files'])} files")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("record", "verify"):
        sub = commands.add_parser(command)
        sub.add_argument("--root", default=".")
        sub.add_argument("--manifest", required=True)
        if command == "record":
            sub.add_argument("--input", action="append", required=True)
            sub.add_argument("--output", action="append", required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    try:
        manifest = project_path(root, args.manifest)
        if args.command == "record":
            record(args, root, manifest)
        else:
            verify(root, manifest)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
