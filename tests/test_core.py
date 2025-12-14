"""
Core Unit Tests for File Content Analyzer

This module contains unit tests for core, low-level functionality.

Currently covered:
- extension list normalization
- file traversal include/exclude behavior
- excluded directory handling

Tests rely only on the Python standard library and use
temporary directories to avoid touching real user files.
"""

import os
import tempfile
import unittest

from fca.config import normalize_ext_list
from fca.traversal import iter_files


class TestCore(unittest.TestCase):
    def test_normalize_ext_list(self):
        self.assertEqual(normalize_ext_list([".Py", " txt ", "JS", "", "js"]), ["js", "py", "txt"])

    def test_iter_files_include_exclude(self):
        with tempfile.TemporaryDirectory() as td:
            # Create dirs
            os.makedirs(os.path.join(td, ".vscode"), exist_ok=True)
            os.makedirs(os.path.join(td, "src"), exist_ok=True)

            # Create files
            with open(os.path.join(td, "a.py"), "w", encoding="utf-8") as f:
                f.write("print('hi')\n")
            with open(os.path.join(td, "b.js"), "w", encoding="utf-8") as f:
                f.write("console.log('hi');\n")
            with open(os.path.join(td, "src", "c.txt"), "w", encoding="utf-8") as f:
                f.write("hello world\n")
            with open(os.path.join(td, ".vscode", "ignored.txt"), "w", encoding="utf-8") as f:
                f.write("should not be seen\n")

            excluded_dirs = {".vscode"}
            excluded_exts = {"js"}
            included_exts = set()  # include all

            found = sorted(os.path.relpath(p, td) for p in iter_files(td, excluded_dirs, excluded_exts, included_exts))
            self.assertIn("a.py", found)
            self.assertIn(os.path.join("src", "c.txt"), found)
            self.assertNotIn("b.js", found)
            self.assertNotIn(os.path.join(".vscode", "ignored.txt"), found)

            # Now include-only py
            included_exts = {"py"}
            found2 = sorted(os.path.relpath(p, td) for p in iter_files(td, excluded_dirs, set(), included_exts))
            self.assertEqual(found2, ["a.py"])


if __name__ == "__main__":
    unittest.main()