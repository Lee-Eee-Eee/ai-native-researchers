"""Exercise collection sync with a synthetic group library and no network."""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from urllib.parse import unquote
import re


SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "ai-native-researchers" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import zotero_collection as collection


class CollectionTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.directory = Path(temp.name)
        a = {"key": "TEST0001", "data": {"title": "Shared paper", "itemType": "book"}}
        b = {"key": "TEST0002", "data": {"title": "Another paper", "itemType": "book"}}
        routes = {
            "groups/42/collections/ROOT0001/items/top": [a],
            "groups/42/collections/ROOT0001/collections": [{"key": "SUB00001"}],
            "groups/42/collections/SUB00001/items/top": [a, b],
            "groups/42/collections/SUB00001/collections": [],
        }
        for record in (a, b):
            uri = f"groups/42/items/{record['key']}"
            routes[uri] = record
            routes[uri + "/children"] = []
        reader = patch.object(collection.note, "read_json", side_effect=routes.__getitem__)
        reader.start()
        self.addCleanup(reader.stop)

    def sync(self, directory, dry_run=False):
        with redirect_stdout(StringIO()) as output:
            collection.sync("ROOT0001", 42, directory, False, dry_run, "index.md")
        return output.getvalue()

    def test_nested_membership_reuses_renamed_note_and_links_it_by_title(self):
        renamed = self.directory / "Reviews" / "My reading (summer).md"
        block = collection.note.block_for("TEST0001", 42, False)
        collection.note.refresh(renamed, block)
        with renamed.open("ab") as stream:
            stream.write(b"\nMy interpretation.\n")
        original = renamed.read_bytes()
        alias = renamed.parent / ".."
        self.assertIn("created=1, updated=0, unchanged=1", self.sync(alias, dry_run=True))
        self.assertFalse((self.directory / "index.md").exists())
        self.assertIn("items=2", self.sync(self.directory))
        self.assertEqual(renamed.read_bytes(), original)
        self.assertFalse((self.directory / "TEST0001.md").exists())

        index = self.directory / "index.md"
        indices = re.findall(r"^- \[(.+)\]\((.+)\)$", index.read_text(encoding="utf-8"), re.M)
        self.assertEqual([title for title, _ in indices], ["Another paper", "Shared paper"])
        actual = [self.directory / unquote(uri) for _, uri in indices]
        self.assertEqual(actual, [self.directory / "TEST0002.md", renamed])
        self.assertTrue(all(path.is_file() for path in actual))
        stamps = {p: p.stat().st_mtime_ns for p in [index, *actual]}
        self.assertIn("created=0, updated=0, unchanged=2, index=Unchanged", self.sync(self.directory))
        self.assertEqual(stamps, {p: p.stat().st_mtime_ns for p in stamps})

    def test_unmanaged_filename_conflict_prevents_all_writes(self):
        for name in ("index.md", "TEST0002.md"):
            with self.subTest(name=name):
                directory = self.directory / name.split(".")[0]
                directory.mkdir()
                occupied = directory / name
                original = b"# My notes\r\nDo not replace.\r\n"
                occupied.write_bytes(original)
                before = occupied.stat().st_mtime_ns
                for dry_run in (True, False):
                    with self.assertRaisesRegex(ValueError, "occupied"):
                        self.sync(directory, dry_run)
                    self.assertEqual(list(directory.iterdir()), [occupied])
                    self.assertEqual(occupied.read_bytes(), original)
                    self.assertEqual(occupied.stat().st_mtime_ns, before)


if __name__ == "__main__":
    unittest.main()
