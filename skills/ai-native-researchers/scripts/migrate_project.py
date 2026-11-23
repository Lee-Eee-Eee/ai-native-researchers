"""Index notes already present in a research project."""

import argparse
from codecs import BOM_UTF8
from collections import defaultdict
from html import escape
from pathlib import Path
import re
import stat

from close_stage import atomic_publish, label, link


MARKER = b"<!-- ai-native-researchers:project-index"
START = MARKER + b":start -->"
END = MARKER + b":end -->"
STAGE = re.compile(r"^([0-9]+)(a?)(?=[\s_.·-]|$)", re.IGNORECASE)
DATED_NAME = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}(?:\D|$)")
HEADING = re.compile(r"^ {0,3}#[ \t]+(.+)")
UNDERLINE = re.compile(r"^ {0,3}=+[ \t]*$")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)")


def redirected(metadata):
    return (stat.S_ISLNK(metadata.st_mode)
            or bool(getattr(metadata, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT))


def note_directory(root, name):
    relative = Path(name)
    if relative.anchor or ".." in relative.parts:
        raise ValueError("--notes must be relative to the project root")
    directory = root
    for component in relative.parts:
        directory /= component
        metadata = directory.lstat()
        if redirected(metadata) or not stat.S_ISDIR(metadata.st_mode):
            raise ValueError(f"Expected a directory inside the project: {directory}")
    return directory


def markdown_files(directory, index):
    for path in directory.iterdir():
        if path == index or path.name.startswith("."):
            continue
        metadata = path.lstat()
        if redirected(metadata):
            continue
        if stat.S_ISDIR(metadata.st_mode):
            yield from markdown_files(path, index)
        elif stat.S_ISREG(metadata.st_mode) and path.suffix.lower() == ".md":
            yield path


def note_title(path):
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except UnicodeDecodeError:
        return path.stem
    if lines and lines[0] == "---":
        end = next((i for i, line in enumerate(lines[1:], 1) if line.strip() in ("---", "...")), len(lines))
        lines = lines[end + 1:]
    opened = previous = ""
    for line in lines:
        fence = FENCE.match(line)
        if fence:
            marker, info = fence.groups()
            if not opened:
                opened = marker
            elif marker[0] == opened[0] and len(marker) >= len(opened) and not info.strip():
                opened = ""
            previous = ""
            continue
        if opened:
            continue
        heading = HEADING.match(line)
        if heading:
            title = re.sub(r"[ \t]+#+[ \t]*$", "", heading[1]).strip()
            if title:
                return title
        if previous and UNDERLINE.fullmatch(line):
            return previous
        previous = line.strip() if not line.startswith(("    ", "\t")) else ""
    return path.stem


def render_block(index, paths):
    directory = index.parent
    stages = defaultdict(lambda: defaultdict(list))
    other = defaultdict(list)
    for path in paths:
        group = path.parent.relative_to(directory).as_posix()
        title = escape(" ".join(note_title(path).split()) or path.stem, quote=False)
        reference = link(title, path, index)
        stage = STAGE.match(path.stem)
        if stage and not DATED_NAME.match(path.stem):
            stages[group][int(stage[1])].append((bool(stage[2]), reference))
        else:
            other[group].append(reference)

    lines = [START.decode()]
    if stages:
        lines.extend(("", "## 编号进展"))
        for group, numbers in sorted(stages.items()):
            if len(stages) > 1 or group != ".":
                lines.extend(("", group_heading(group)))
            lines.append("")
            for number, references in sorted(numbers.items()):
                titles = " · ".join(reference for _, reference in sorted(references))
                lines.append(f"- **{number:03}** · {titles}")
    if other:
        lines.extend(("", "## 其他记录"))
        for group, references in sorted(other.items()):
            if len(other) > 1 or group != ".":
                lines.extend(("", group_heading(group)))
            lines.append("")
            lines.extend(f"- {reference}" for reference in references)
    if not paths:
        lines.extend(("", "所选目录中暂无可索引的 Markdown 笔记。"))
    lines.extend(("", END.decode()))
    return "\n".join(lines).encode("utf-8")


def group_heading(group):
    title = "根目录" if group == "." else " ".join(group.split())
    return "### " + label(escape(title, quote=False))


def index_content(before, block):
    if before in (None, b"", BOM_UTF8):
        return (before or b"") + "# 项目记录索引\n\n".encode("utf-8") + block + b"\n"
    before.decode("utf-8-sig")
    newline = b"\r\n" if b"\r\n" in before else b"\n"
    count = before.count(MARKER)
    if count == 0:
        separator = newline if before.endswith(b"\n") else newline * 2
        return before + separator + block.replace(b"\n", newline) + newline
    pattern = rb"(?m)^(?:\xef\xbb\xbf)?(%s)(?=\r?$)"
    start = re.search(pattern % re.escape(START), before)
    end = re.search(pattern % re.escape(END), before)
    if count != 2 or not start or not end or start.start(1) >= end.start(1):
        raise ValueError("Invalid project-index markers in init.md")
    current = before[start.start(1):end.end(1)]
    if current.replace(b"\r\n", b"\n") == block:
        return before
    return before[:start.start(1)] + block.replace(b"\n", newline) + before[end.end(1):]


def migrate(root, notes, dry_run):
    if not root.is_dir():
        raise ValueError(f"Expected a project directory: {root}")
    directory = note_directory(root, notes)
    index = directory / "init.md"
    try:
        metadata = index.lstat()
    except FileNotFoundError:
        before = None
    else:
        if redirected(metadata) or not stat.S_ISREG(metadata.st_mode):
            raise ValueError(f"Index filename is occupied: {index}")
        before = index.read_bytes()
    paths = sorted(markdown_files(directory, index),
                   key=lambda path: (path.as_posix().casefold(), path.as_posix()))
    block = render_block(index, paths)
    after = index_content(before, block)
    action = "Created" if before is None else "Unchanged" if after == before else "Updated"
    if dry_run:
        print(f"Preview: {action} {index.relative_to(root).as_posix()} ({len(paths)} notes)")
        print(block.decode("utf-8"))
    else:
        if after != before:
            atomic_publish(index, after, before)
        print(f"{action} {index.relative_to(root).as_posix()} ({len(paths)} notes)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--notes", default="docs", help="Existing note directory, relative to root")
    parser.add_argument("--dry-run", action="store_true", help="Print the generated index block without writing")
    args = parser.parse_args()
    try:
        migrate(args.root.resolve(strict=True), args.notes, args.dry_run)
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
