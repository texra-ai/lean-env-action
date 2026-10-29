"""Regressions for refreshing immutable apt caches while reusing older archives."""

from pathlib import Path
import tempfile
import unittest

from cache_fingerprint import fingerprint


class CacheFingerprintTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.indexes = self.root / "lists"
        self.indexes.mkdir()
        self.package_index = self.indexes / "repo_Packages"
        self.package_index.write_bytes(b"Package: graphviz\nVersion: 1\n")
        self.action = self.root / "action.yml"
        self.action.write_text("packages=(graphviz latexmk)\n")

    def key(self, extra=""):
        return fingerprint(self.indexes, self.action, extra)

    def test_unchanged_inputs_reuse_the_key(self):
        first = self.key()
        self.assertEqual(self.key(), first)
        self.assertEqual(len(first), 64)

    def test_new_package_versions_get_a_new_save_key(self):
        first = self.key()
        self.package_index.write_bytes(b"Package: graphviz\nVersion: 2\n")
        self.assertNotEqual(self.key(), first)

    def test_package_definition_and_extra_packages_affect_the_key(self):
        first = self.key()
        self.assertNotEqual(self.key("texlive-fonts-extra"), first)
        self.action.write_text("packages=(graphviz latexmk dvisvgm)\n")
        self.assertNotEqual(self.key(), first)

    def test_locks_and_partial_downloads_do_not_change_the_key(self):
        first = self.key()
        (self.indexes / "lock").write_bytes(b"locked")
        partial = self.indexes / "partial"
        partial.mkdir()
        (partial / "repo_Packages").write_bytes(b"incomplete")
        self.assertEqual(self.key(), first)

    def test_absolute_runner_path_does_not_affect_the_key(self):
        other = self.root / "other-lists"
        other.mkdir()
        (other / self.package_index.name).write_bytes(self.package_index.read_bytes())
        self.assertEqual(fingerprint(other, self.action, ""), self.key())

    def test_missing_indexes_are_not_a_valid_cache_generation(self):
        self.package_index.unlink()
        with self.assertRaisesRegex(ValueError, "No apt package indexes"):
            self.key()


if __name__ == "__main__":
    unittest.main()
