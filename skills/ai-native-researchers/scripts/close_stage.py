"""Close a research stage from an existing result and a small JSON description."""

import argparse
from contextlib import contextmanager, nullcontext
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from tempfile import NamedTemporaryFile
from urllib.parse import quote

import evidence


def require_text(value, key):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Expected non-empty text for {key}")
    return value.strip()


def validate(spec):
    if not isinstance(spec, dict):
        raise ValueError("Expected a JSON object")
    fields = ("id", "question", "finding", "comparison", "command", "next")
    for key in fields:
        spec[key] = require_text(spec.get(key), key)
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", spec["id"]):
        raise ValueError("Use a stable id of 1–64 lowercase letters, digits or hyphens")
    if "\n" in spec["question"] or "\r" in spec["question"]:
        raise ValueError("Use one line for question")
    for key in ("inputs", "outputs"):
        if not isinstance(spec.get(key), list) or not spec[key]:
            raise ValueError(f"Provide at least one file in {key}")
        spec[key] = [require_text(name, key) for name in spec[key]]
    refs = spec.get("literature", [])
    if not isinstance(refs, list):
        raise ValueError("literature must be a list")
    for ref in refs:
        if not isinstance(ref, dict):
            raise ValueError("Expected a literature object")
        require_text(ref.get("title"), "literature.title")
        if "doi" in ref and not re.fullmatch(r"10\.\d{4,9}/\S+", require_text(ref["doi"], "doi")):
            raise ValueError("Use the bare DOI, beginning with 10.")
        if "zotero" in ref and not re.fullmatch(r"zotero://select/(library|groups/\d+)/items/[A-Z0-9]{8}", require_text(ref["zotero"], "zotero")):
            raise ValueError("Expected a Zotero item link")
    number = spec.get("number")
    if number is not None and (type(number) is not int or number < 1):
        raise ValueError("number must be a positive integer")


def label(value):
    return value.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def link(title, target, source):
    relative = Path(os.path.relpath(target, source.parent)).as_posix()
    return f"[{label(title)}]({quote(relative, safe='/.-_~')})"


def add_files(root, spec):
    entries = []
    for role, names in (("input", spec["inputs"]), ("output", spec["outputs"])):
        for name in names:
            if Path(name).is_absolute():
                raise ValueError(f"Expected a project-relative path: {name}")
            path = evidence.project_path(root, name)
            if not path.is_file():
                raise ValueError(f"Missing {role} file: {name}")
            entries.append({"role": role, "path": path.relative_to(root).as_posix(),
                            "sha256": evidence.fingerprint(path)})
    return entries


def atomic_publish(path, data, previous=None):
    with NamedTemporaryFile(dir=path.parent, prefix=".stage-", delete=False) as stream:
        temp = Path(stream.name)
        try:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        except BaseException:
            stream.close()
            temp.unlink(missing_ok=True)
            raise
    try:
        if previous is None:
            os.link(temp, path)  # Fail exclusively even if another writer created it.
        else:
            os.chmod(temp, stat.S_IMODE(path.stat().st_mode))
            if path.read_bytes() != previous:
                raise ValueError(f"Homepage changed during closeout: {path}")
            os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


@contextmanager
def lock(root):
    path = root / ".ai-native-stage.lock"
    with path.open("x", encoding="ascii") as stream:
        stream.write(str(os.getpid()))
    try:
        yield
    finally:
        path.unlink()


def close(root, notes, home, spec, dry_run, git):
    if not home.is_file() or home.suffix.lower() != ".md":
        raise ValueError(f"Expected an existing Markdown homepage: {home}")
    home_bytes = home.read_bytes()
    home_text = home_bytes.decode("utf-8-sig")
    marker = f"<!-- ai-native-researchers:stage {spec['id']} -->"
    digest = hashlib.sha256(json.dumps(spec, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    existing = list(notes.iterdir()) if notes.exists() else []
    prior = [p for p in existing if re.fullmatch(r"\d+_" + re.escape(spec["id"]) + r"\.evidence\.json", p.name)]
    owned = None
    if prior:
        if len(prior) != 1:
            raise ValueError("Multiple manifests use this stage id")
        owned = json.loads(prior[0].read_text(encoding="utf-8")).get("stage", {})
        if owned.get("spec_sha256") != digest:
            raise ValueError("This id already has a different description")
        number = int(prior[0].name.split("_")[0])
    else:
        used = [int(m[1]) for p in existing if (m := re.match(r"^(\d+)(?=[a-zA-Z_.-])", p.name))]
        number = spec.get("number") or max(used, default=0) + 1
    prefix = f"{number:03}"
    stem = spec["id"]
    decision = notes / f"{prefix}_{stem}.md"
    detail = notes / f"{prefix}a_{stem}.md"
    manifest = notes / f"{prefix}_{stem}.evidence.json"
    targets = {decision, detail, manifest}
    target_names = [p for p in existing if re.match(rf"^0*{number}(?=[a-zA-Z_.-])", p.name)
                    or re.fullmatch(r"\d+[a-zA-Z]*_" + re.escape(stem) + r"\.md", p.name)]
    if owned is not None:
        if set(target_names) != targets or not all(p.is_file() and not p.is_symlink() for p in targets):
            raise ValueError("The recorded stage has incomplete or conflicting files")
        if home_text.count(marker) != 1:
            raise ValueError("The homepage entry was moved, removed or duplicated")
        evidence.verify(root, manifest)
        print(f"Already recorded stage {prefix}. Kept both notes and the homepage.")
        return
    if target_names or marker in home_text or home in targets:
        raise ValueError("Stage number, id or homepage entry is already in use")

    entries = add_files(root, spec)
    if any(root / entry["path"] == home for entry in entries):
        raise ValueError("The homepage would change during fingerprinting")
    report = {"schema": 1, "git": git, "files": entries, "stage": {"id": stem, "spec_sha256": digest}}
    decision_text = (f"# {prefix} {spec['question']}\n\n{spec['finding']}\n\n"
                     f"## 对照条件\n\n{spec['comparison']}\n\n## 下一步\n\n{spec['next']}\n\n"
                     f"{link('逐项证据与复算', detail, decision)}\n")
    lines = [f"# {prefix}a {spec['question']} · 证据", "", link("阶段结论", decision, detail),
             "", "## 输入与产物", ""]
    for entry in entries:
        role = "输入" if entry["role"] == "input" else "产物"
        lines.append(f"- {role} · {link(entry['path'], root / entry['path'], detail)}")
    fence = max((len(m) for m in re.findall(r"`+", spec["command"])), default=0)
    fence = "`" * max(3, fence + 1)
    lines += ["", "## 在项目根目录运行", "", fence, spec["command"], fence, "",
              link("输入与输出的 SHA-256 清单", manifest, detail)]
    if spec.get("literature"):
        lines += ["", "## 文献依据", ""]
        for ref in spec["literature"]:
            parts = [f"- {ref['title']}"]
            if ref.get("doi"):
                parts.append(f"[DOI](https://doi.org/{quote(ref['doi'], safe='/')})")
            if ref.get("zotero"):
                parts.append(f"[Zotero]({ref['zotero']})")
            lines.append(" · ".join(parts))
    new_files = {decision: decision_text.encode(), detail: ("\n".join(lines) + "\n").encode(),
                 manifest: (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode()}
    entry = f"{marker}\n- {link(prefix + ' ' + spec['question'], decision, home)} · {link('证据与复算', detail, home)}\n"
    newline = b"\r\n" if b"\r\n" in home_bytes else b"\n"
    separator = newline if home_bytes.endswith(b"\n") else newline * 2
    revised_home = home_bytes + separator + entry.encode().replace(b"\n", newline)
    for path in [*new_files, home]:
        print(("Preview " if dry_run else "Stage ") + path.relative_to(root).as_posix())
    if dry_run:
        return
    notes.mkdir(parents=True, exist_ok=True)
    created = []
    try:
        for path, data in new_files.items():
            atomic_publish(path, data)
            created.append(path)
        atomic_publish(home, revised_home, home_bytes)
    except BaseException:
        for path in reversed(created):
            if path.is_file() and path.read_bytes() == new_files[path]:
                path.unlink()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--notes", default="docs", help="Stage directory, relative to root")
    parser.add_argument("--index", default="README.md", help="Existing Markdown homepage")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        root = args.root.resolve(strict=True)
        spec = json.loads(args.spec.read_text(encoding="utf-8-sig"))
        validate(spec)
        notes = evidence.project_path(root, args.notes)
        home = evidence.project_path(root, args.index)
        git = evidence.git_state(root)  # Before creating the temporary lock.
        with nullcontext() if args.dry_run else lock(root):
            close(root, notes, home, spec, args.dry_run, git)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
