"""Regression checks for release rejection and install archive integrity."""

import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest
from zipfile import ZipFile


SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("skill_validator", SOURCE / "scripts/test_skill.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "distributed-system-audit"
        for source in validator.package_files(SOURCE):
            target = self.root / source.relative_to(SOURCE)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)

    def test_valid_package(self):
        self.assertEqual([], validator.validate(self.root))

    def test_invalid_yaml_escape_is_rejected(self):
        manifest = self.root / "agents/openai.yaml"
        content = manifest.read_text(encoding="utf-8").replace("$distributed-system-audit", r"\$distributed-system-audit")
        manifest.write_text(content, encoding="utf-8")
        self.assertTrue(any("invalid YAML" in item for item in validator.validate(self.root)))

    def test_missing_runtime_reference_blocks_packaging(self):
        (self.root / "references/audit-sop.md").unlink()
        with self.assertRaises(ValueError):
            validator.create_package(self.root, Path(self.temp.name) / "broken.zip")

    def test_broken_local_link_is_rejected(self):
        readme = self.root / "README.md"
        with readme.open("a", encoding="utf-8") as stream:
            stream.write("\n[Missing](docs/missing.md)\n")
        self.assertTrue(any("Broken/escaping local link" in item for item in validator.validate(self.root)))

    def test_link_outside_package_is_rejected(self):
        (self.root.parent / "private.md").write_text("private", encoding="utf-8")
        with (self.root / "README.md").open("a", encoding="utf-8") as stream:
            stream.write("\n[Outside](../private.md)\n")
        self.assertTrue(any("Broken/escaping local link" in item for item in validator.validate(self.root)))

    def test_invalid_utf8_is_rejected(self):
        (self.root / "references/audit-sop.md").write_bytes(b"\xff\xfe\x00")
        self.assertTrue(any("Unreadable UTF-8" in item for item in validator.validate(self.root)))

    def test_install_archive_is_complete_and_clean(self):
        for relative in (".git/config", ".idea/workspace.xml", "dist/stale.zip", ".eval-runs/private.log", "scripts/__pycache__/old.pyc"):
            generated = self.root / relative
            generated.parent.mkdir(parents=True, exist_ok=True)
            generated.write_text("must not ship", encoding="utf-8")
        output = validator.create_package(self.root, Path(self.temp.name) / "release.zip")
        with ZipFile(output) as archive:
            names = set(archive.namelist())
            expected = {f"distributed-system-audit/{p.relative_to(self.root).as_posix()}" for p in validator.package_files(self.root)}
            self.assertEqual(expected, names)
            self.assertIn("distributed-system-audit/references/audit-sop.md", names)
            self.assertFalse(any("private" in name or "__pycache__" in name or "/.git/" in name or "/dist/" in name or "/.idea/" in name for name in names))
            installed = Path(self.temp.name) / "installed"
            archive.extractall(installed)
        self.assertEqual([], validator.validate(installed / "distributed-system-audit"))
        for source in validator.package_files(self.root):
            self.assertEqual(source.read_bytes(), (installed / "distributed-system-audit" / source.relative_to(self.root)).read_bytes())

    def test_archive_does_not_overwrite_existing_output(self):
        output = Path(self.temp.name) / "existing.zip"
        output.write_bytes(b"existing release")
        with self.assertRaises(FileExistsError):
            validator.create_package(self.root, output)
        self.assertEqual(b"existing release", output.read_bytes())

    def test_archive_output_cannot_enter_source_tree(self):
        destinations = [self.root, self.root / "release.zip"] + [
            self.root / folder / "nested/release.zip" for folder in validator.RESOURCE_DIRS
        ]
        for output in destinations:
            with self.subTest(output=output.relative_to(self.root)):
                with self.assertRaisesRegex(ValueError, "under dist/"):
                    validator.create_package(self.root, output)
                if output != self.root:
                    self.assertFalse(output.exists())
        self.assertEqual([], validator.validate(self.root))

    def test_archive_under_dist_preserves_valid_source_and_install(self):
        output = validator.create_package(self.root, self.root / "dist/nested/release.zip")
        self.assertEqual([], validator.validate(self.root))
        with ZipFile(output) as archive:
            self.assertIsNone(archive.testzip())
            self.assertFalse(any(name.endswith(".zip") for name in archive.namelist()))
            installed = Path(self.temp.name) / "dist-installed"
            archive.extractall(installed)
        self.assertEqual([], validator.validate(installed / validator.SKILL_NAME))


if __name__ == "__main__":
    unittest.main()
