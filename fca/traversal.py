"""
File System Traversal

This module provides a single, centralized generator for walking
directory trees while applying filtering rules.

Responsibilities:
- recursive directory traversal
- directory exclusion (e.g. .venv, .vscode)
- include-only extension filtering
- exclude extension filtering

All file iteration in the application flows through this module,
ensuring consistent behavior across modes.
"""

import os

def iter_files(start_dir: str, excluded_dirs: set, excluded_exts: set, included_exts: set):
    for root, dirs, files in os.walk(start_dir):
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        for name in files:
            ext = os.path.splitext(name)[1].lower().lstrip(".")
            if included_exts and ext not in included_exts:
                continue
            if ext in excluded_exts:
                continue
            yield os.path.join(root, name)