"""Build or refresh a Markdown reading note from Zotero's read-only local API."""

import argparse
import json
import re
from html import unescape
from http.client import HTTPConnection, HTTPException
from pathlib import Path
from urllib.parse import quote

from close_stage import atomic_publish


KEY = re.compile(r"[A-Z0-9]{8}")
START = "<!-- ai-native-researchers:zotero "
END = "<!-- /ai-native-researchers:zotero -->"


def read_json(path):
    # A direct loopback connection ignores HTTP proxy settings and redirects.
    connection = HTTPConnection("127.0.0.1", 23119, timeout=10)
    try:
        connection.request("GET", "/api/" + path, headers={"Accept": "application/json"})
        response = connection.getresponse()
        if response.status != 200:
            raise ValueError(f"Zotero GET /api/{path}: HTTP {response.status}")
        return json.loads(response.read())
    finally:
        connection.close()


def plain(value):
    text = re.sub(r"</?(?:i|b|sub|sup|em|strong|span|sc)(?:\s[^>]*)?>", "", str(value or ""), flags=re.I)
    text = " ".join(unescape(text).split())
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return re.sub(r"([\\\[\]*_\x60|])", r"\\\1", text)


def render(scope, key, item, pdfs, counts=None):
    data = item["data"]
    if item["key"] != key or data["itemType"] in {"note", "attachment", "annotation"}:
        raise ValueError("Use the item key of a bibliographic record")
    title = plain(data.get("title") or data.get("caseName") or data.get("nameOfAct"))
    if not title:
        raise ValueError("The Zotero item has no title")
    creators = data.get("creators", [])
    authors = [c for c in creators if c.get("creatorType") == "author"]
    names = []
    for person in authors or creators:
        name = person.get("name") or " ".join(filter(None, [person.get("firstName"), person.get("lastName")]))
        if name:
            names.append(plain(name))
    date = item.get("meta", {}).get("parsedDate") or data.get("date", "")
    year = re.search(r"(?<!\d)[12][0-9]{3}(?!\d)", date)
    lines = [f"{START}{scope}/items/{key} -->", f"# {title}", ""]
    if names:
        who = "作者" if authors else "相关署名"
        lines.append(f"- {who} · " + "、".join(names))
    if year or date:
        lines.append("- 出版时间 · " + (year.group() if year else plain(date)))
    doi = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", data.get("DOI", "").strip(), flags=re.I)
    if doi:
        lines.append(f"- DOI · [{plain(doi)}](https://doi.org/{quote(doi, safe='/')})")
    lines.append(f"- 来源 · [Zotero 本地 API 条目](zotero://select/{scope}/items/{key})")
    for index, pdf in enumerate(pdfs, start=1):
        child_key = pdf["key"]
        if not KEY.fullmatch(child_key):
            raise ValueError("Unexpected PDF attachment key from Zotero")
        label = f"PDF {index}" if len(pdfs) > 1 else "PDF"
        lines.append(f"- [{label} · 在 Zotero 打开](zotero://open-pdf/{scope}/items/{child_key})")
    if counts is not None:
        notes, annotations = counts
        lines.append(f"- 条目子笔记 {notes} 篇，PDF 批注 {annotations} 条")
    lines.append(END)
    return "\n".join(lines)


def block_for(key, group, include_counts):
    api = (f"groups/{group}" if group else "users/0") + "/items"
    item = read_json(f"{api}/{key}")
    children = read_json(f"{api}/{key}/children")
    pdfs = sorted(
        (child for child in children if child["data"]["itemType"] == "attachment"
         and child["data"].get("contentType", "").lower() == "application/pdf"
         and child["data"].get("linkMode") != "linked_url"),
        key=lambda child: child["key"],
    )
    counts = None
    if include_counts:
        notes = sum(child["data"]["itemType"] == "note" for child in children)
        annotations = sum(
            len(read_json(f"{api}/{pdf['key']}/children?itemType=annotation")) for pdf in pdfs
        )
        counts = (notes, annotations)
    scope = f"groups/{group}" if group else "library"
    return render(scope, key, item, pdfs, counts)


def refresh(path, block):
    if path.suffix.lower() != ".md":
        raise ValueError("Use a Markdown (.md) output path")
    path.parent.mkdir(parents=True, exist_ok=True)
    previous = path.read_bytes() if path.exists() else None
    if previous is None:
        updated = (block + "\n\n## 我的阅读笔记\n\n").encode("utf-8")
    else:
        # Keep the BOM, handwritten passages and their exact line endings.
        text = previous.decode("utf-8")
        begin = block.split("\n", 1)[0]
        if text.count(START) != 1 or text.count(END) != 1 or begin not in text:
            raise ValueError(f"No unique managed block for this item in {path}; choose a new output file")
        start = text.index(begin)
        end = text.index(END)
        if end < start:
            raise ValueError(f"Managed block markers out of order in {path}")
        newline = "\r\n" if "\r\n" in text[start:end] else "\n"
        updated = (text[:start] + block.replace("\n", newline) + text[end + len(END):]).encode("utf-8")
    if previous == updated:
        return "Unchanged"
    atomic_publish(path, updated, previous)
    return "Created" if previous is None else "Updated"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("item_key", help="Eight-character Zotero bibliographic item key")
    parser.add_argument("--group", type=int, help="Numeric group library ID (default: personal library)")
    parser.add_argument("--counts", action="store_true", help="Include child note and PDF annotation counts")
    parser.add_argument("--out", type=Path, required=True, help="Markdown note to create or update")
    args = parser.parse_args()
    key = args.item_key.upper()
    if not KEY.fullmatch(key) or (args.group is not None and args.group < 1):
        parser.error("Expected an eight-character item key and a positive group ID")
    try:
        print(refresh(args.out, block_for(key, args.group, args.counts)))
    except (ConnectionError, TimeoutError, HTTPException) as exc:
        parser.exit(1, f"Cannot read Zotero at 127.0.0.1:23119. Open Zotero and enable its local API. {exc}\n")
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
