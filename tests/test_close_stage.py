"""Exercise note properties and reruns through the closeout CLI."""

from datetime import date
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


SCRIPT = (Path(__file__).resolve().parents[1] / "skills" / "ai-native-researchers"
          / "scripts" / "close_stage.py")


class CloseStagePropertiesTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name) / "合成观测"
        self.root.mkdir()
        self.home = self.root / "README.md"
        self.home.write_text("# Project\n", encoding="utf-8")
        (self.root / "input.csv").write_text("value\n1\n", encoding="utf-8")
        (self.root / "result.csv").write_text("value\n2\n", encoding="utf-8")
        self.spec = {
            "id": "test-stage", "question": "Question?", "finding": "Finding.",
            "comparison": "Comparison.", "command": "python run.py", "next": "Next.",
            "inputs": ["input.csv"], "outputs": ["result.csv"],
        }
        self.notes = self.root / "docs"
        self.decision = self.notes / "001_test-stage.md"
        self.detail = self.notes / "001a_test-stage.md"

    def run_cli(self, *args, check=True):
        description = self.root / "stage.json"
        description.write_text(json.dumps(self.spec), encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-X", "utf8", str(SCRIPT), str(description),
             "--root", str(self.root), *args],
            capture_output=True, encoding="utf-8", check=check,
        )

    def test_both_notes_share_text_stage_and_explicit_project_date(self):
        self.spec.update(project='观测: "A" #1', date="2026-11-22")
        self.run_cli()
        for note, kind in ((self.decision, "阶段判断"), (self.detail, "证据与复算")):
            with self.subTest(note=note.name):
                frontmatter, body = note.read_text(encoding="utf-8").split("\n---\n", 1)
                self.assertEqual(frontmatter.splitlines(), [
                    "---", r'project: "观测: \"A\" #1"', 'stage: "001"',
                    "date: 2026-11-22", f'kind: "{kind}"',
                ])
                self.assertTrue(body.startswith("\n# "))

    def test_defaults_are_recorded_and_rerun_preserves_both_note_formats(self):
        before = date.today().isoformat()
        self.run_cli()
        after = date.today().isoformat()
        properties = self.decision.read_text(encoding="utf-8").splitlines()
        self.assertIn('project: "合成观测"', properties)
        self.assertIn(properties[3], {f"date: {before}", f"date: {after}"})

        self.decision.write_bytes(self.decision.read_bytes() + "\n手写判断。\n".encode())
        # A note written before properties were added has only the Markdown body.
        body = self.detail.read_bytes().split(b"\n---\n\n", 1)[1]
        self.detail.write_bytes(body + "\n手写证据。\n".encode())
        saved = {p: p.read_bytes() for p in (self.home, *self.notes.iterdir())}
        self.assertIn("Already recorded stage 001", self.run_cli().stdout)
        self.assertEqual({p: p.read_bytes() for p in saved}, saved)

    def test_invalid_date_and_preview_leave_home_and_notes_unchanged(self):
        original = self.home.read_bytes()
        self.spec["date"] = "2026-02-30"
        failed = self.run_cli(check=False)
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("YYYY-MM-DD", failed.stderr)
        self.spec["date"] = "2026-02-28"
        self.assertIn("Preview docs/001_test-stage.md", self.run_cli("--dry-run").stdout)
        self.assertFalse(self.notes.exists())
        self.assertFalse((self.root / ".ai-native-stage.lock").exists())
        self.assertEqual(self.home.read_bytes(), original)

    def test_new_evidence_rejects_reusing_an_input_as_an_output(self):
        self.spec["outputs"] = ["./input.csv"]
        original = self.home.read_bytes()
        failed = self.run_cli(check=False)
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("both input and output", failed.stderr)
        self.assertFalse(self.notes.exists())
        self.assertEqual(self.home.read_bytes(), original)

        recorded = subprocess.run(
            [sys.executable, "-X", "utf8", str(SCRIPT.with_name("evidence.py")), "record",
             "--root", str(self.root), "--manifest", "test.json", "--input", "input.csv",
             "--output", "./input.csv"],
            capture_output=True, encoding="utf-8", check=False,
        )
        self.assertNotEqual(recorded.returncode, 0)
        self.assertIn("both input and output", recorded.stderr)
        self.assertFalse((self.root / "test.json").exists())
