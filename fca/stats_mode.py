"""
File Statistics Mode

This module implements file content statistics analysis.

Responsibilities:
- count lines, words, and characters per file
- aggregate totals across all files
- compute per-extension statistics
- skip the program file itself

It focuses purely on data collection and aggregation.
Report formatting is handled by the reporting module.
"""

import os
from fca.traversal import iter_files
from fca.reporting import write_stats_report


def run(entry_file: str, directory: str,
        excluded_dirs: set, excluded_exts: set, included_exts: set) -> str:
    per_file = {}
    per_ext = {}

    script_path = os.path.abspath(entry_file)

    for path in iter_files(directory, excluded_dirs, excluded_exts, included_exts):
        if os.path.abspath(path) == script_path:
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

            ext = os.path.splitext(path)[1].lower().lstrip(".") or "(none)"
            lines = len(text.splitlines())
            words = len(text.split())
            chars = len(text)

            per_file[path] = {"lines": lines, "words": words, "chars": chars}

            if ext not in per_ext:
                per_ext[ext] = {"files": 0, "lines": 0, "words": 0, "chars": 0}
            per_ext[ext]["files"] += 1
            per_ext[ext]["lines"] += lines
            per_ext[ext]["words"] += words
            per_ext[ext]["chars"] += chars
        except Exception:
            continue

    out = write_stats_report(entry_file, directory, per_file, per_ext)
    return out