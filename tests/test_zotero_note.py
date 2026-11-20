"""Exercise the reading-note CLI against synthetic responses with no network access."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "ai-native-researchers" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import zotero_note


class ZoteroNoteTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.note = Path(directory.name) / "reading" / "paper.md"
        self.record = {
            "key": "TEST0001",
            "data": {
                "itemType": "journalArticle", "title": "Synthetic sensor study",
                "creators": [{"creatorType": "author", "firstName": "Sample", "lastName": "Author"}],
                "date": "2020", "DOI": "10.0000/example",
            },
        }
        self.responses = {
            "users/0/items/TEST0001": self.record,
            "users/0/items/TEST0001/children": [
                {"key": "TEST0002", "data": {"itemType": "attachment", "contentType": "application/pdf",
                                             "linkMode": "imported_file"}},
                {"key": "TEST0003", "data": {"itemType": "attachment", "contentType": "application/pdf",
                                             "linkMode": "linked_url"}},
                {"key": "TEST0004", "data": {"itemType": "note"}},
            ],
            "users/0/items/TEST0002/children?itemType=annotation": [{"key": "TEST0005"}],
        }
        reader = patch.object(zotero_note, "read_json", side_effect=self.responses.__getitem__)
        reader.start()
        self.addCleanup(reader.stop)

    def run_cli(self, *args):
        stdout = StringIO()
        argv = ["zotero_note.py", "test0001", "--out", str(self.note), *args]
        with patch.object(sys, "argv", argv), redirect_stdout(stdout):
            zotero_note.main()
        return stdout.getvalue().strip()

    def test_creates_metadata_and_links_to_the_attached_pdf(self):
        self.assertEqual(self.run_cli("--counts"), "Created")
        text = self.note.read_text(encoding="utf-8")
        for value in ["# Synthetic sensor study", "Sample Author", "2020", "https://doi.org/10.0000/example",
                      "zotero://select/library/items/TEST0001", "zotero://open-pdf/library/items/TEST0002",
                      "条目子笔记 1 篇，PDF 批注 1 条", "## 我的阅读笔记"]:
            with self.subTest(value=value):
                self.assertIn(value, text)
        self.assertNotIn("TEST0003", text)

    def test_refresh_preserves_handwritten_bytes_around_the_managed_block(self):
        self.run_cli()
        original = self.note.read_bytes().replace(b"\n", b"\r\n")
        before = b"\xef\xbb\xbf" + "写在条目前面的判断。\r\n".encode()
        after = "\n  手写的比较条件  \r\n".encode()
        self.note.write_bytes(before + original + after)
        self.record["data"]["title"] = "Revised synthetic sensor study"
        self.assertEqual(self.run_cli(), "Updated")
        expected = original.replace(b"# Synthetic sensor study", b"# Revised synthetic sensor study")
        self.assertEqual(self.note.read_bytes(), before + expected + after)

    def test_unchanged_metadata_never_rewrites_the_file(self):
        self.run_cli()
        original = self.note.read_bytes()
        with patch.object(zotero_note, "atomic_publish", side_effect=AssertionError("Unexpected write")):
            self.assertEqual(self.run_cli(), "Unchanged")
        self.assertEqual(self.note.read_bytes(), original)

    def test_refuses_to_refresh_a_personal_note_with_the_same_key_in_a_group(self):
        self.run_cli()
        original = self.note.read_bytes()
        self.responses.update({"groups/42/items/TEST0001": self.record, "groups/42/items/TEST0001/children": []})
        error = StringIO()
        with redirect_stderr(error), self.assertRaises(SystemExit) as exit_code:
            self.run_cli("--group", "42")
        self.assertEqual(exit_code.exception.code, 1)
        self.assertIn("No unique managed block", error.getvalue())
        self.assertEqual(self.note.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
