"""
Reporting and Output Generation

This module is responsible for generating human-readable
text reports for all operation modes.

Responsibilities:
- create the analysis-results directory when needed
- generate timestamped report filenames
- format and write string-search reports
- optionally render detailed/context String Search excerpts
- safeguard reports against extremely long or minified source lines
- format and write file-statistics reports
- format and write filename-search reports
- include program name and version metadata

No search or analysis logic is implemented here — this module
only consumes already-prepared data.
"""

import datetime
import os


PROGRAM_NAME = "File Content Analyzer"
PROGRAM_VERSION = "3.2.0"

RESULTS_DIRNAME = "analysis-results"

# Detailed reports normally display complete source lines up to this size.
# Longer lines are abbreviated so minified/generated files do not overwhelm
# the report.
DEFAULT_MAX_SOURCE_LINE_LENGTH = 500

# For a very long matching line, retain useful source characters around each
# match. The value may be reduced automatically if necessary to keep the
# resulting excerpt close to DEFAULT_MAX_SOURCE_LINE_LENGTH.
DEFAULT_MATCH_CHARACTER_CONTEXT = 200


def make_output_file(
    entry_file: str,
    prefix: str,
) -> str:
    base_dir = os.path.dirname(
        os.path.abspath(entry_file)
    )

    out_dir = os.path.join(
        base_dir,
        RESULTS_DIRNAME,
    )

    os.makedirs(
        out_dir,
        exist_ok=True,
    )

    ts = datetime.datetime.now().strftime(
        "%Y%m%d-%H%M%S"
    )

    return os.path.join(
        out_dir,
        f"{prefix}_{ts}.txt",
    )


def _merge_character_ranges(
    ranges: list[tuple[int, int]],
    maximum_length: int,
) -> list[tuple[int, int]]:
    """
    Merge overlapping character ranges when the merged result remains
    reasonably bounded.

    This prevents repeated text around nearby matches while avoiding one huge
    excerpt when matches occur far apart on a minified source line.
    """
    if not ranges:
        return []

    ranges = sorted(ranges)
    merged = [ranges[0]]

    for start, end in ranges[1:]:
        previous_start, previous_end = merged[-1]

        proposed_start = previous_start
        proposed_end = max(
            previous_end,
            end,
        )

        overlaps_or_touches = (
            start <= previous_end + 1
        )

        proposed_length = (
            proposed_end - proposed_start
        )

        if (
            overlaps_or_touches
            and proposed_length <= maximum_length
        ):
            merged[-1] = (
                proposed_start,
                proposed_end,
            )

        else:
            merged.append(
                (start, end)
            )

    return merged


def _long_matching_line_segments(
    source_line: str,
    matches: list[dict],
    max_line_length: int,
    match_character_context: int,
) -> list[dict]:
    """
    Build bounded character excerpts around matches on an oversized line.

    Each returned segment contains:
    - display_text
    - start: zero-based original line offset
    - end: zero-based exclusive original line offset
    - matches included in that segment

    The complete requested search string is always preserved.
    """
    ranges = []

    for match in matches:
        match_start = (
            match["column_start"] - 1
        )

        match_end = match["column_end"]

        match_length = (
            match_end - match_start
        )

        # Preserve the whole match even if the search term itself is long.
        available_context = max(
            0,
            (
                max_line_length
                - match_length
            )
            // 2,
        )

        character_context = min(
            match_character_context,
            available_context,
        )

        start = max(
            0,
            match_start - character_context,
        )

        end = min(
            len(source_line),
            match_end + character_context,
        )

        ranges.append(
            (start, end)
        )

    merged_ranges = _merge_character_ranges(
        ranges,
        maximum_length=max_line_length,
    )

    segments = []

    for start, end in merged_ranges:
        segment_matches = []

        for match in matches:
            match_start = (
                match["column_start"] - 1
            )

            match_end = match["column_end"]

            if (
                match_start >= start
                and match_end <= end
            ):
                segment_matches.append(
                    match
                )

        display_text = source_line[
            start:end
        ]

        if start > 0:
            display_text = "…" + display_text

        if end < len(source_line):
            display_text = display_text + "…"

        segments.append(
            {
                "display_text": display_text,
                "start": start,
                "end": end,
                "matches": segment_matches,
            }
        )

    return segments


def _write_match_annotations(
    f,
    matches: list[dict],
    line_number_width: int,
) -> None:
    """
    Write unambiguous MATCH annotations beneath a matching source line.
    """
    annotation_indent = (
        " " * (line_number_width + 6)
    )

    for match in matches:
        f.write(
            f"{annotation_indent}"
            f"MATCH: {match['term']} "
            f"(columns "
            f"{match['column_start']}-"
            f"{match['column_end']})\n"
        )


def _write_detailed_source_line(
    f,
    line_data: dict,
    line_number_width: int,
    max_line_length: int,
    match_character_context: int,
) -> None:
    """
    Write one source line for a detailed String Search report.

    Normal lines are written in full.

    Very long matching lines are represented by character excerpts centered
    around their actual matches.

    Very long non-matching context lines are shortened from the end.
    """
    line_number = line_data["line_number"]
    source_line = line_data["text"]
    matches = line_data["matches"]

    marker = ">" if matches else " "

    if len(source_line) <= max_line_length:
        f.write(
            f"{marker} "
            f"{line_number:>{line_number_width}} | "
            f"{source_line}\n"
        )

        if matches:
            _write_match_annotations(
                f,
                matches,
                line_number_width,
            )

        return

    # Oversized matching line: produce one or more focused excerpts around
    # the actual match locations.
    if matches:
        segments = _long_matching_line_segments(
            source_line=source_line,
            matches=matches,
            max_line_length=max_line_length,
            match_character_context=match_character_context,
        )

        for segment in segments:
            f.write(
                f"> "
                f"{line_number:>{line_number_width}} | "
                f"{segment['display_text']}\n"
            )

            _write_match_annotations(
                f,
                segment["matches"],
                line_number_width,
            )

        f.write(
            " " * (line_number_width + 6)
            + "[line truncated: "
            + f"original length {len(source_line)} characters]\n"
        )

        return

    # Oversized non-matching context line. There is no match around which to
    # center an excerpt, so keep the beginning of the source line.
    display_text = (
        source_line[:max_line_length]
        + "…"
    )

    f.write(
        f"  "
        f"{line_number:>{line_number_width}} | "
        f"{display_text}\n"
    )

    f.write(
        " " * (line_number_width + 6)
        + "[context line truncated: "
        + f"original length {len(source_line)} characters]\n"
    )


def _write_detailed_search_section(
    f,
    detailed_results: dict,
    context_lines: int,
    max_line_length: int,
    match_character_context: int,
) -> None:
    """
    Append the Detailed Match Context section to a String Search report.
    """
    f.write(
        "\n"
        "Detailed Match Context\n"
        "======================\n\n"
    )

    for path, detail in detailed_results.items():
        excerpts = detail.get(
            "excerpts",
            [],
        )

        if not excerpts:
            continue

        f.write(
            f"FILE: {path}\n"
        )

        f.write(
            "-" * (
                len(path) + 6
            )
            + "\n\n"
        )

        for excerpt_index, excerpt in enumerate(
            excerpts,
            start=1,
        ):
            start_line = excerpt["start_line"]
            end_line = excerpt["end_line"]

            if start_line == end_line:
                range_label = (
                    f"line {start_line}"
                )

            else:
                range_label = (
                    f"lines "
                    f"{start_line}-{end_line}"
                )

            f.write(
                f"Excerpt {excerpt_index}: "
                f"{range_label}\n"
            )

            f.write(
                "-" * (
                    len(
                        f"Excerpt {excerpt_index}: "
                        f"{range_label}"
                    )
                )
                + "\n"
            )

            line_number_width = max(
                1,
                len(str(end_line)),
            )

            for line_data in excerpt["lines"]:
                _write_detailed_source_line(
                    f=f,
                    line_data=line_data,
                    line_number_width=line_number_width,
                    max_line_length=max_line_length,
                    match_character_context=match_character_context,
                )

            f.write("\n")

        f.write("\n")


def write_search_report(
    entry_file: str,
    directory: str,
    case_sensitive: bool,
    strings: list,
    results: dict,
    detailed_results: dict | None = None,
    context_lines: int = 5,
    max_line_length: int = DEFAULT_MAX_SOURCE_LINE_LENGTH,
    match_character_context: int = DEFAULT_MATCH_CHARACTER_CONTEXT,
) -> str:
    """
    Write a String Search report.

    When ``detailed_results`` is None, the established compact Summary report
    is produced.

    When detailed data is supplied, the same summary is retained and a
    Detailed Match Context section is appended.
    """
    if context_lines < 0:
        raise ValueError(
            "context_lines must be 0 or greater"
        )

    if max_line_length <= 0:
        raise ValueError(
            "max_line_length must be greater than 0"
        )

    if match_character_context < 0:
        raise ValueError(
            "match_character_context must be 0 or greater"
        )

    out = make_output_file(
        entry_file,
        "string_search",
    )

    with open(
        out,
        "w",
        encoding="utf-8",
    ) as f:
        f.write(
            f"{PROGRAM_NAME} "
            f"v{PROGRAM_VERSION}\n"
        )

        f.write(
            "String Search Report\n\n"
        )

        f.write(
            f"Directory: "
            f"{os.path.abspath(directory)}\n"
        )

        f.write(
            f"Case-sensitive: "
            f"{case_sensitive}\n"
        )

        if detailed_results is not None:
            f.write(
                "Report detail: Detailed\n"
            )

            f.write(
                "Context lines before/after: "
                f"{context_lines}\n"
            )

            f.write(
                "Maximum displayed source line: "
                f"{max_line_length} characters\n"
            )

        f.write(
            "Search strings:\n"
        )

        for s in strings:
            f.write(
                f"  - {s}\n"
            )

        f.write("\n")

        if not results:
            f.write(
                "No matches found.\n"
            )

            return out

        total_files = len(results)

        total_occ = sum(
            sum(d.values())
            for d in results.values()
        )

        f.write(
            f"Total files with matches: "
            f"{total_files}\n"
        )

        f.write(
            f"Total occurrences: "
            f"{total_occ}\n\n"
        )

        for path, counts in results.items():
            f.write(
                path + "\n"
            )

            for term, count in counts.items():
                f.write(
                    f"  {term}: {count}\n"
                )

            f.write("\n")

        if detailed_results is not None:
            _write_detailed_search_section(
                f=f,
                detailed_results=detailed_results,
                context_lines=context_lines,
                max_line_length=max_line_length,
                match_character_context=match_character_context,
            )

    return out


def write_stats_report(
    entry_file: str,
    directory: str,
    per_file: dict,
    per_ext: dict,
) -> str:
    out = make_output_file(
        entry_file,
        "file_stats",
    )

    with open(
        out,
        "w",
        encoding="utf-8",
    ) as f:
        f.write(
            f"{PROGRAM_NAME} "
            f"v{PROGRAM_VERSION}\n"
        )

        f.write(
            "File Statistics Report\n\n"
        )

        f.write(
            f"Directory: "
            f"{os.path.abspath(directory)}\n\n"
        )

        total_files = len(per_file)

        total_lines = sum(
            v["lines"]
            for v in per_file.values()
        )

        total_words = sum(
            v["words"]
            for v in per_file.values()
        )

        total_chars = sum(
            v["chars"]
            for v in per_file.values()
        )

        f.write(
            "Summary:\n"
        )

        f.write(
            f"  Total files: "
            f"{total_files}\n"
        )

        f.write(
            f"  Total lines: "
            f"{total_lines}\n"
        )

        f.write(
            f"  Total words: "
            f"{total_words}\n"
        )

        f.write(
            f"  Total characters: "
            f"{total_chars}\n\n"
        )

        f.write(
            "Per-extension totals:\n"
        )

        for ext in sorted(
            per_ext.keys()
        ):
            d = per_ext[ext]

            f.write(
                f"  .{ext}  "
                f"files={d['files']} "
                f"lines={d['lines']} "
                f"words={d['words']} "
                f"chars={d['chars']}\n"
            )

        f.write("\n")

        f.write(
            "Per-file details:\n"
        )

        for path in sorted(
            per_file.keys()
        ):
            s = per_file[path]

            f.write(
                path + "\n"
            )

            f.write(
                f"  Lines: "
                f"{s['lines']}\n"
            )

            f.write(
                f"  Words: "
                f"{s['words']}\n"
            )

            f.write(
                f"  Characters: "
                f"{s['chars']}\n\n"
            )

    return out


def write_name_search_report(
    entry_file: str,
    directory: str,
    case_sensitive: bool,
    patterns: list,
    hits_by_pattern: dict,
) -> str:
    out = make_output_file(
        entry_file,
        "name_search",
    )

    with open(
        out,
        "w",
        encoding="utf-8",
    ) as f:
        f.write(
            f"{PROGRAM_NAME} "
            f"v{PROGRAM_VERSION}\n"
        )

        f.write(
            "Filename Search Report\n\n"
        )

        f.write(
            f"Directory: "
            f"{os.path.abspath(directory)}\n"
        )

        f.write(
            f"Case-sensitive: "
            f"{case_sensitive}\n\n"
        )

        f.write(
            "Patterns searched:\n"
        )

        for p in patterns:
            f.write(
                f"  - {p}\n"
            )

        f.write("\n")

        total_matches = sum(
            len(paths)
            for paths in hits_by_pattern.values()
        )

        total_patterns_with_hits = sum(
            1
            for p in patterns
            if hits_by_pattern.get(p)
        )

        f.write(
            f"Patterns with matches: "
            f"{total_patterns_with_hits} "
            f"/ {len(patterns)}\n"
        )

        f.write(
            f"Total matching files: "
            f"{total_matches}\n\n"
        )

        for p in patterns:
            paths = hits_by_pattern.get(
                p,
                [],
            )

            f.write(
                f"Pattern: {p}\n"
            )

            if not paths:
                f.write(
                    "  (no matches)\n\n"
                )

                continue

            for path in sorted(
                paths
            ):
                f.write(
                    f"  {path}\n"
                )

            f.write("\n")

    return out
  
#  End of file reporting.py