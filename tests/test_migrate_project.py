"""Check that importing existing work only changes the generated index block."""

from codecs import BOM_UTF8
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


SCRIPT = (Path(__file__).resolve().parents[1] / "skills" / "ai-native-researchers"
          / "scripts" / "migrate_project.py")
START = b"<!-- ai-native-researchers:project-index:start -->"
END = b"<!-- ai-native-researchers:project-index:end -->"


class MigrateProjectTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name).resolve()
        self.project = self.root / "项目"
        self.notes = self.project / "docs"
        self.notes.mkdir(parents=True)
        self.index = self.notes / "init.md"
        self.home = self.project / "README.md"
        self.home.write_bytes(b"# Home\n")

    def note(self, path, text):
        destination = self.notes / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")
        return destination

    def run_cli(self, *args, check=True):
        return subprocess.run(
            [sys.executable, "-X", "utf8", str(SCRIPT), *args], cwd=self.project,
            capture_output=True, encoding="utf-8", check=check,
        )

    def test_fresh_index_groups_existing_notes_and_retains_source_bytes(self):
        decision = self.note("过轨记录/001_判断.md", "\ufeff---\nproject: A\n---\n# 判断 [A] ###\n")
        detail = self.note("过轨记录/001a_取样.md", "~~~\n# 示例代码\n~~~\n# 逐例结果\n")
        self.note("过轨记录/014_次轮.md", "# 下一轮\n")
        self.note("过轨记录/008a_旧资料.MD", "留待补写\n")
        self.note("过轨记录/2026-11-22 记录.md", "组会回顾\n========\n")
        self.note("工作说明.md", "只写了正文。\n")
        self.note(".hidden/忽略.md", "# Hidden\n")
        source_bytes = {note: note.read_bytes() for note in (decision, detail, self.home)}

        self.assertIn("Created docs/init.md (6 notes)", self.run_cli().stdout)
        text = self.index.read_text(encoding="utf-8")
        stage = next(line for line in text.splitlines() if line.startswith("- **001**"))
        self.assertIn(r"[判断 \[A\]](", stage)
        self.assertIn("[逐例结果](", stage)
        self.assertIn("%E8%BF%87%E8%BD%A8%E8%AE%B0%E5%BD%95/", stage)
        self.assertLess(text.index("**008**"), text.index("**014**"))
        self.assertIn("[008a_旧资料](", text)
        self.assertIn("[组会回顾](", text.split("## 其他记录", 1)[1])
        self.assertIn("[工作说明](", text)
        self.assertNotIn("Hidden", text)
        self.assertEqual({note: note.read_bytes() for note in source_bytes}, source_bytes)

    def test_keep_existing_init_prose_and_replace_only_the_generated_block(self):
        prefix = BOM_UTF8 + "# 手写首页\r\n\r\n保留这一段。".encode("utf-8")
        suffix = "\r\n\r\n最后附一条补充说明。".encode("utf-8")
        self.index.write_bytes(prefix)
        self.note("旧记录.md", "# 旧记录\n")
        self.assertIn("Updated", self.run_cli().stdout)
        before = self.index.read_bytes()
        self.assertTrue(before.startswith(prefix + b"\r\n\r\n" + START))
        self.index.write_bytes(before.rstrip(b"\r\n") + suffix)
        self.note("新记录.md", "# 新记录\n")

        self.assertIn("Updated", self.run_cli().stdout)
        updated = self.index.read_bytes()
        self.assertTrue(updated.startswith(prefix + b"\r\n\r\n" + START))
        self.assertTrue(updated.endswith(END + suffix))
        self.assertIn("[新记录](".encode(), updated)
        self.assertEqual(updated.count(START), 1)
        self.assertNotIn("(init.md)", updated.decode("utf-8-sig"))
        stamp = self.index.stat().st_mtime_ns
        self.assertIn("Unchanged", self.run_cli().stdout)
        self.assertEqual(self.index.stat().st_mtime_ns, stamp)
        self.assertEqual(self.index.read_bytes(), updated)

    def test_preview_and_invalid_markers_cause_no_writes(self):
        source = self.note("原始记录.md", "# 原始记录\n")
        preview = self.run_cli("--dry-run").stdout
        self.assertIn("Preview: Created docs/init.md", preview)
        self.assertIn("[原始记录]", preview)
        self.assertEqual(set(self.notes.iterdir()), {source})
        for malformed in (START, END + b"\n" + START, START + b"\n" + START + b"\n" + END,
                          b"existing text " + START + b"\n" + END):
            with self.subTest(malformed=malformed):
                self.index.write_bytes(malformed)
                failed = self.run_cli(check=False)
                self.assertNotEqual(failed.returncode, 0)
                self.assertIn("Invalid project-index markers", failed.stderr)
                self.assertEqual(self.index.read_bytes(), malformed)

    def test_scope_is_relative_to_project(self):
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "external.md").write_text("# Outside", encoding="utf-8")
        for scope in ("../outside", str(outside)):
            with self.subTest(scope=scope):
                self.assertNotEqual(self.run_cli("--notes", scope, check=False).returncode, 0)
        self.assertFalse((outside / "init.md").exists())
        self.assertFalse(self.index.exists())

    def test_skips_redirects_and_refuses_a_redirected_index(self):
        outside = self.root / "outside"
        outside.mkdir()
        external = outside / "external.md"
        external.write_bytes(b"# Outside\n")
        try:
            (self.notes / "linked").symlink_to(outside, target_is_directory=True)
            (self.notes / "linked.md").symlink_to(external)
        except OSError as exc:
            self.skipTest(f"Symlink creation unavailable: {exc}")
        self.assertNotEqual(self.run_cli("--notes", "docs/linked", check=False).returncode, 0)
        self.assertIn("(0 notes)", self.run_cli("--dry-run").stdout)
        self.index.symlink_to(external)
        self.assertNotEqual(self.run_cli(check=False).returncode, 0)
        self.assertEqual(external.read_bytes(), b"# Outside\n")
