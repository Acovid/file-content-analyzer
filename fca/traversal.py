"""
File System Traversal

This module provides a single, centralized generator for walking
directory trees while applying filtering rules.

Responsibilities:
- recursive directory traversal
- exact directory exclusion, e.g. .venv, .vscode, .git
- optional hidden directory exclusion, i.e. folders starting with "."
- include-only extension filtering
- exclude extension filtering

All file iteration in the application flows through this module,
ensuring consistent behavior across modes.
"""

import os


def iter_files(
    start_dir: str,
    excluded_dirs: set,
    excluded_exts: set,
    included_exts: set,
    exclude_hidden_dirs: bool = False,
):
    """
    Yield file paths under start_dir while applying directory and extension filters.

    Args:
        start_dir: Directory tree to scan.
        excluded_dirs: Directory names to skip exactly.
        excluded_exts: File extensions to exclude, without dots.
        included_exts: If non-empty, only these extensions are included.
        exclude_hidden_dirs: If True, skip all folders whose names start with ".".
    """
    for root, dirs, files in os.walk(start_dir):
        dirs[:] = [
            d for d in dirs
            if d not in excluded_dirs
            and not (exclude_hidden_dirs and d.startswith("."))
        ]

        for name in files:
            ext = os.path.splitext(name)[1].lower().lstrip(".")

            if included_exts and ext not in included_exts:
                continue

            if ext in excluded_exts:
                continue

            yield os.path.join(root, name)


# End of file traversal.py