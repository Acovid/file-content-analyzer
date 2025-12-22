"""
Reporting and Output Generation

This module is responsible for generating human-readable
text reports for all operation modes.

Responsibilities:
- create the analysis-results directory when needed
- generate timestamped report filenames
- format and write string-search reports
- format and write file-statistics reports
- include program name and version metadata

No analysis logic is implemented here — this module
only consumes already-prepared data.
"""

import os
import datetime


PROGRAM_NAME = "File Content Analyzer"
PROGRAM_VERSION = "3.0.0"

RESULTS_DIRNAME = "analysis-results"


def make_output_file(entry_file: str, prefix: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(entry_file))
    out_dir = os.path.join(base_dir, RESULTS_DIRNAME)
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    return os.path.join(out_dir, f"{prefix}_{ts}.txt")


def write_search_report(entry_file: str, directory: str, case_sensitive: bool, strings: list, results: dict) -> str:
    out = make_output_file(entry_file, "string_search")
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"{PROGRAM_NAME} v{PROGRAM_VERSION}\n")
        f.write("String Search Report\n\n")
        f.write(f"Directory: {os.path.abspath(directory)}\n")
        f.write(f"Case-sensitive: {case_sensitive}\n")
        f.write("Search strings:\n")
        for s in strings:
            f.write(f"  - {s}\n")
        f.write("\n")

        if not results:
            f.write("No matches found.\n")
            return out

        total_files = len(results)
        total_occ = sum(sum(d.values()) for d in results.values())
        f.write(f"Total files with matches: {total_files}\n")
        f.write(f"Total occurrences: {total_occ}\n\n")

        for path, counts in results.items():
            f.write(path + "\n")
            for term, count in counts.items():
                f.write(f"  {term}: {count}\n")
            f.write("\n")

    return out


def write_stats_report(entry_file: str, directory: str, per_file: dict, per_ext: dict) -> str:
    out = make_output_file(entry_file, "file_stats")
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"{PROGRAM_NAME} v{PROGRAM_VERSION}\n")
        f.write("File Statistics Report\n\n")
        f.write(f"Directory: {os.path.abspath(directory)}\n\n")

        total_files = len(per_file)
        total_lines = sum(v["lines"] for v in per_file.values())
        total_words = sum(v["words"] for v in per_file.values())
        total_chars = sum(v["chars"] for v in per_file.values())

        f.write("Summary:\n")
        f.write(f"  Total files: {total_files}\n")
        f.write(f"  Total lines: {total_lines}\n")
        f.write(f"  Total words: {total_words}\n")
        f.write(f"  Total characters: {total_chars}\n\n")

        f.write("Per-extension totals:\n")
        for ext in sorted(per_ext.keys()):
            d = per_ext[ext]
            f.write(f"  .{ext}  files={d['files']} lines={d['lines']} words={d['words']} chars={d['chars']}\n")
        f.write("\n")

        f.write("Per-file details:\n")
        for path in sorted(per_file.keys()):
            s = per_file[path]
            f.write(path + "\n")
            f.write(f"  Lines: {s['lines']}\n")
            f.write(f"  Words: {s['words']}\n")
            f.write(f"  Characters: {s['chars']}\n\n")

    return out
  
def write_name_search_report(entry_file: str, directory: str, case_sensitive: bool, patterns: list, hits_by_pattern: dict) -> str:
    out = make_output_file(entry_file, "name_search")
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"{PROGRAM_NAME} v{PROGRAM_VERSION}\n")
        f.write("Filename Search Report\n\n")
        f.write(f"Directory: {os.path.abspath(directory)}\n")
        f.write(f"Case-sensitive: {case_sensitive}\n\n")

        f.write("Patterns searched:\n")
        for p in patterns:
            f.write(f"  - {p}\n")
        f.write("\n")

        total_matches = sum(len(paths) for paths in hits_by_pattern.values())
        total_patterns_with_hits = sum(1 for p in patterns if hits_by_pattern.get(p))

        f.write(f"Patterns with matches: {total_patterns_with_hits} / {len(patterns)}\n")
        f.write(f"Total matching files: {total_matches}\n\n")

        for p in patterns:
            paths = hits_by_pattern.get(p, [])
            f.write(f"Pattern: {p}\n")
            if not paths:
                f.write("  (no matches)\n\n")
                continue

            for path in sorted(paths):
                f.write(f"  {path}\n")
            f.write("\n")

    return out