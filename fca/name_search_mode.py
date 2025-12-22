"""
Filename Search Mode

This module implements searching for files by name (or glob-style patterns),
and produces a report listing the matching file paths.

Input sources:
- Optional batch file: file-names.txt (one pattern per line, // comments allowed)
- Optional manual input: interactive prompts in terminal

Matching:
- Supports glob patterns via fnmatch: *, ?, [abc]
- Can be case-sensitive or case-insensitive (prompted)

This module focuses on collecting results; report writing is done via fca.reporting.
"""

import os
import fnmatch

from fca.traversal import iter_files
from fca.reporting import write_name_search_report
from fca.prompts import ask_yes_no


def load_name_patterns(entry_file: str) -> list | None:
    """
    Load filename patterns from:
    1) file-names.txt (optional, next to entry_file)
    2) interactive terminal input (optional)

    Returns list of unique patterns (preserving order) or None if empty.
    """
    base = os.path.dirname(os.path.abspath(entry_file))
    batch_path = os.path.join(base, "file-names.txt")

    patterns = []

    if os.path.isfile(batch_path):
        if ask_yes_no(f"Found file-names.txt at '{batch_path}'. Use it?", default=True):
            try:
                with open(batch_path, "r", encoding="utf-8") as f:
                    for line in f:
                        s = line.strip()
                        if not s or s.startswith("//"):
                            continue
                        patterns.append(s)
            except Exception:
                pass

    if ask_yes_no("Add filename patterns manually?", default=not bool(patterns)):
        print("Enter filename patterns (empty line to finish). Examples:")
        print("  - config.json")
        print("  - *.php")
        print("  - style*.css")
        print("  - *checkout*")
        while True:
            s = input("> ").strip()
            if not s:
                break
            patterns.append(s)

    if not patterns:
        return None

    # De-dupe while preserving order
    seen = set()
    unique = []
    for p in patterns:
        if p not in seen:
            seen.add(p)
            unique.append(p)

    return unique


def _matches_any_pattern(filename: str, patterns: list, case_sensitive: bool) -> list:
    """
    Return a list of patterns that match filename (may be multiple).
    """
    if case_sensitive:
        return [p for p in patterns if fnmatch.fnmatchcase(filename, p)]

    lower_name = filename.lower()
    matches = []
    for p in patterns:
        if fnmatch.fnmatchcase(lower_name, p.lower()):
            matches.append(p)
    return matches


def run(entry_file: str, directory: str, excluded_dirs: set, excluded_exts: set, included_exts: set) -> str | None:
    """
    Search for files by name/pattern within directory (recursive).

    Returns output report path or None.
    """
    patterns = load_name_patterns(entry_file)
    if not patterns:
        print("No filename patterns provided. Exiting.")
        return None

    case_sensitive = ask_yes_no("Should filename matching be case-sensitive?", default=False)

    # Map: pattern -> list of full paths
    hits_by_pattern = {p: [] for p in patterns}

    script_path = os.path.abspath(entry_file)

    for path in iter_files(directory, excluded_dirs, excluded_exts, included_exts):
        # Skip the program file itself
        if os.path.abspath(path) == script_path:
            continue

        name = os.path.basename(path)
        matched_patterns = _matches_any_pattern(name, patterns, case_sensitive)
        for p in matched_patterns:
            hits_by_pattern[p].append(path)

    out = write_name_search_report(
        entry_file=entry_file,
        directory=directory,
        case_sensitive=case_sensitive,
        patterns=patterns,
        hits_by_pattern=hits_by_pattern
    )
    return out
