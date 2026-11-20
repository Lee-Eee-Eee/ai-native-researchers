"""Refresh Markdown reading notes for a Zotero collection and all its subcollections."""

import argparse
from collections import Counter
from http.client import HTTPException
from pathlib import Path
import re
from urllib.parse import quote

import zotero_note as note


def collect_keys(collection, group):
    api = (f"groups/{group}" if group else "users/0") + "/collections"
    pending, visited, keys = [collection], set(), set()
    while pending:
        current = pending.pop()
        if current in visited:
            continue
        visited.add(current)
        for item in note.read_json(f"{api}/{current}/items/top"):
            data = item["data"]
            if data["itemType"] in {"note", "attachment", "annotation"}:
                continue
            if any(str(data.get(f) or "").strip() for f in ("title", "caseName", "nameOfAct")):
                keys.add(item["key"])
        pending.extend(child["key"] for child in note.read_json(f"{api}/{current}/collections"))
    return sorted(keys), len(visited)


def index_notes(directory, scope, keys):
    """Locate notes even after the reader renames or moves them within the directory."""
    owned = {}
    begin = re.compile(re.escape(note.START + scope + "/items/") + r"([A-Z0-9]{8}) -->")
    for path in directory.rglob("*.md"):
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(directory):
            continue
        try:
            text = path.read_bytes().decode("utf-8-sig")
        except UnicodeDecodeError:
            continue  # An unrelated file may use another encoding.
        for match in begin.finditer(text):
            key = match[1]
            if key not in keys:
                continue
            end = text.find(note.END, match.end())
            if text.count(note.START) != 1 or text.count(note.END) != 1 or end < 0:
                raise ValueError(f"Ambiguous managed block in {path}")
            if key in owned:
                raise ValueError(f"Multiple notes for {key}: {owned[key][0]} and {path}")
            block = text[match.start():end + len(note.END)].replace("\r\n", "\n")
            owned[key] = (path, block)
    return owned


def index_page(scope, collection, directory, plan):
    papers = sorted(
        ((block.splitlines()[1].removeprefix("# "), path) for path, block, _ in plan),
        key=lambda pair: (pair[0].casefold(), pair[1].as_posix()),
    )
    lines = [f"{note.START}{scope}/collections/{collection} -->", "# 文献目录", "",
             f"[在 Zotero 中打开分类](zotero://select/{scope}/collections/{collection}) · {len(papers)} 篇", ""]
    for title, path in papers:
        target = quote(path.relative_to(directory).as_posix(), safe="/")
        lines.append(f"- [{title}]({target})")
    lines.append(note.END)
    return "\n".join(lines)


def index_status(path, block):
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValueError(f"Index filename is occupied: {path}")
    if not path.exists():
        return "Created"
    text = path.read_bytes().decode("utf-8-sig").replace("\r\n", "\n")
    begin = block.split("\n", 1)[0]
    if text.count(note.START) != 1 or text.count(note.END) != 1 or begin not in text:
        raise ValueError(f"Index filename is occupied by a different note: {path}")
    if text.index(note.END) < text.index(begin):
        raise ValueError(f"Index markers out of order in {path}")
    return "Unchanged" if block in text else "Updated"


def sync(collection, group, directory, counts, dry_run, index=None):
    # Compare resolved paths on both sides of the vault containment check.
    # Windows temp directories and vault junctions can have several spellings.
    directory = directory.resolve()
    keys, collection_count = collect_keys(collection, group)
    scope = f"groups/{group}" if group else "library"
    owned = index_notes(directory, scope, set(keys))
    plan = []
    for key in keys:
        path, previous = owned.get(key, (directory / f"{key}.md", None))
        if previous is None and (path.exists() or path.is_symlink()):
            raise ValueError(f"{key} needs a new note, but the filename is occupied: {path}")
        block = note.block_for(key, group, counts)
        status = "Created" if previous is None else ("Unchanged" if previous == block else "Updated")
        plan.append((path, block, status))

    index_result = None
    if index is not None:
        if (Path(index).name != index or "/" in index or "\\" in index
                or Path(index).suffix.lower() != ".md"):
            raise ValueError("Use a Markdown filename inside --out-dir for --index")
        index_path = directory / index
        if any(path == index_path for path, _, _ in plan):
            raise ValueError(f"The index and a reading note need different filenames: {index}")
        index_text = index_page(scope, collection, directory, plan)
        index_result = index_status(index_path, index_text)

    totals = Counter()
    for path, block, status in plan:
        if not dry_run:
            status = note.refresh(path, block)
        totals[status] += 1
    if index_result is not None and not dry_run:
        index_result = note.refresh(index_path, index_text)
    action = "Preview" if dry_run else "Synced"
    print(f"{action}: collections={collection_count}, items={len(keys)}, "
          f"created={totals['Created']}, updated={totals['Updated']}, unchanged={totals['Unchanged']}"
          + (f", index={index_result}" if index_result else ""))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("collection_key", help="Eight-character Zotero collection key")
    parser.add_argument("--group", type=int, help="Numeric group ID (default: personal library)")
    parser.add_argument("--counts", action="store_true", help="Include note and PDF annotation counts")
    parser.add_argument("--out-dir", type=Path, required=True, help="Directory for project reading notes")
    parser.add_argument("--index", help="Markdown index filename in --out-dir (optional)")
    parser.add_argument("--dry-run", action="store_true", help="Show counts without changing any files")
    args = parser.parse_args()
    collection = args.collection_key.upper()
    if not note.KEY.fullmatch(collection) or (args.group is not None and args.group < 1):
        parser.error("Expected an eight-character collection key and a positive group ID")
    try:
        directory = args.out_dir
        if directory.exists() and not directory.is_dir():
            raise ValueError(f"Expected a note directory: {directory}")
        sync(collection, args.group, directory, args.counts, args.dry_run, args.index)
    except (ConnectionError, TimeoutError, HTTPException) as exc:
        parser.exit(1, f"Cannot read Zotero at 127.0.0.1:23119. Open Zotero and enable its local API. {exc}\n")
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
