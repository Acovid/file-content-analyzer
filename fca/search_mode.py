"""
String Search Mode

This module implements the string-search operation.

Responsibilities:
- load search strings (from file and/or user input)
- perform string occurrence counting per file
- apply case-sensitive or case-insensitive matching
- skip the program file itself
- return structured results for reporting

It does not handle:
- configuration persistence
- file traversal logic
- report formatting
"""

import os
from fca.traversal import iter_files
from fca.reporting import write_search_report


def load_search_strings(entry_file: str) -> list | None:
    base = os.path.dirname(os.path.abspath(entry_file))
    path = os.path.join(base, "search-strings.txt")
    strings = []

    if os.path.isfile(path):
        from fca.prompts import ask_yes_no
        if ask_yes_no("Found search-strings.txt. Use it?", default=True):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if s and not s.startswith("//"):
                        strings.append(s)

    from fca.prompts import ask_yes_no
    if ask_yes_no("Add search strings manually?", default=not bool(strings)):
        print("Enter search strings (empty line to finish):")
        while True:
            s = input("> ").strip()
            if not s:
                break
            strings.append(s)

    if not strings:
        return None

    # de-dupe preserve order
    seen = set()
    out = []
    for s in strings:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def run(entry_file: str, cfg: dict, directory: str, case_sensitive: bool,
        excluded_dirs: set, excluded_exts: set, included_exts: set) -> str | None:
    strings = load_search_strings(entry_file)
    if not strings:
        print("No search strings provided. Exiting.")
        return None

    processed = strings if case_sensitive else [s.lower() for s in strings]
    results = {}

    script_path = os.path.abspath(entry_file)

    for path in iter_files(directory, excluded_dirs, excluded_exts, included_exts):
        if os.path.abspath(path) == script_path:
            continue
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            hay = text if case_sensitive else text.lower()
            counts = {}
            for orig, term in zip(strings, processed):
                c = hay.count(term)
                if c:
                    counts[orig] = c
            if counts:
                results[path] = counts
        except Exception:
            continue

    out = write_search_report(entry_file, directory, case_sensitive, strings, results)
    return out