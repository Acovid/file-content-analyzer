"""
String Search Mode

This module implements the string-search operation.

Responsibilities:
- load search strings (from file and/or user input)
- perform string occurrence counting per file
- apply case-sensitive or case-insensitive matching
- collect exact match positions for detailed/context reporting
- build and merge line-based context excerpts around matches
- optionally prepare detailed search data for the reporting layer
- skip the program file itself

It does not handle:
- configuration persistence
- file traversal logic
- report formatting
"""

import bisect
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

    if ask_yes_no(
        "Add search strings manually?",
        default=not bool(strings),
    ):
        print("Enter search strings (empty line to finish):")

        while True:
            s = input("> ").strip()

            if not s:
                break

            strings.append(s)

    if not strings:
        return None

    # De-duplicate while preserving the user's original order.
    seen = set()
    out = []

    for s in strings:
        if s not in seen:
            seen.add(s)
            out.append(s)

    return out


def _line_start_offsets(text: str) -> list[int]:
    """
    Return the zero-based character offset at which each line starts.

    The first line always starts at offset 0. These offsets allow a match's
    absolute character position to be converted efficiently to a line number
    and column without repeatedly rescanning the whole file.
    """
    starts = [0]

    for index, char in enumerate(text):
        if char == "\n":
            starts.append(index + 1)

    return starts


def collect_match_positions(
    text: str,
    strings: list[str],
    case_sensitive: bool,
) -> tuple[dict, list[dict]]:
    """
    Count occurrences and collect the position of every match in ``text``.

    Search semantics intentionally match the utility's existing use of
    ``str.count()``:

    - case-insensitive mode compares lower-cased text and search strings;
    - matches for a given search string are non-overlapping;
    - each requested search string is evaluated independently.

    Returns:
        counts:
            ``{search_string: occurrence_count}`` for strings with at least
            one match.

        matches:
            A list of dictionaries, one per occurrence, containing:
            - term: original requested search string
            - start: zero-based absolute start offset
            - end: zero-based exclusive absolute end offset
            - line_number: one-based source line number
            - column_start: one-based start column
            - column_end: one-based inclusive end column
    """
    hay = text if case_sensitive else text.lower()
    processed = strings if case_sensitive else [s.lower() for s in strings]
    line_starts = _line_start_offsets(text)

    counts = {}
    matches = []

    for original, term in zip(strings, processed):
        if not term:
            continue

        search_from = 0
        occurrence_count = 0

        while True:
            start = hay.find(term, search_from)

            if start == -1:
                break

            end = start + len(term)
            occurrence_count += 1

            line_index = bisect.bisect_right(
                line_starts,
                start,
            ) - 1

            line_start = line_starts[line_index]

            matches.append(
                {
                    "term": original,
                    "start": start,
                    "end": end,
                    "line_number": line_index + 1,
                    "column_start": start - line_start + 1,
                    "column_end": end - line_start,
                }
            )

            # Match str.count(): occurrences of the same term do not overlap.
            search_from = end

        if occurrence_count:
            counts[original] = occurrence_count

    # Stable source order is useful for detailed reporting. If multiple terms
    # begin at the same position, Python's stable sort preserves term order.
    matches.sort(
        key=lambda match: match["start"]
    )

    return counts, matches


def build_context_excerpts(
    text: str,
    matches: list[dict],
    context_lines: int,
) -> list[dict]:
    """
    Build merged line-based context excerpts around collected matches.

    Each match contributes a window consisting of ``context_lines`` lines
    before and after its matching line. Windows are clipped to file bounds.

    Overlapping or directly adjacent windows are merged so the same source
    lines are not repeated unnecessarily in a detailed report.

    Returns a list of excerpt dictionaries.

    Each excerpt contains:
    - start_line: one-based first line number in the excerpt
    - end_line: one-based last line number in the excerpt
    - lines: ordered line dictionaries containing:
        - line_number: one-based source line number
        - text: complete source line without its newline terminator
        - matches: all match records whose match begins on this line
    """
    if context_lines < 0:
        raise ValueError(
            "context_lines must be 0 or greater"
        )

    if not matches:
        return []

    lines = text.splitlines()

    if not lines:
        return []

    total_lines = len(lines)

    # Multiple occurrences on one source line should contribute only one
    # context window.
    matching_line_numbers = sorted(
        {
            match["line_number"]
            for match in matches
        }
    )

    windows = []

    for line_number in matching_line_numbers:
        start_line = max(
            1,
            line_number - context_lines,
        )

        end_line = min(
            total_lines,
            line_number + context_lines,
        )

        windows.append(
            [start_line, end_line]
        )

    # Merge windows that overlap or are directly adjacent.
    merged_windows = []

    for start_line, end_line in windows:
        if (
            not merged_windows
            or start_line > merged_windows[-1][1] + 1
        ):
            merged_windows.append(
                [start_line, end_line]
            )

        else:
            merged_windows[-1][1] = max(
                merged_windows[-1][1],
                end_line,
            )

    # Group match records by source line.
    matches_by_line = {}

    for match in matches:
        matches_by_line.setdefault(
            match["line_number"],
            [],
        ).append(match)

    excerpts = []

    for start_line, end_line in merged_windows:
        excerpt_lines = []

        for line_number in range(
            start_line,
            end_line + 1,
        ):
            excerpt_lines.append(
                {
                    "line_number": line_number,
                    "text": lines[line_number - 1],
                    "matches": list(
                        matches_by_line.get(
                            line_number,
                            [],
                        )
                    ),
                }
            )

        excerpts.append(
            {
                "start_line": start_line,
                "end_line": end_line,
                "lines": excerpt_lines,
            }
        )

    return excerpts


def run(
    entry_file: str,
    cfg: dict,
    directory: str,
    case_sensitive: bool,
    excluded_dirs: set,
    excluded_exts: set,
    included_exts: set,
    exclude_hidden_dirs: bool = False,
    detailed: bool = False,
    context_lines: int = 5,
) -> str | None:
    """
    Run String Search.

    Summary mode preserves the established behavior.

    When ``detailed`` is True, match positions and merged context excerpts
    are additionally prepared for the reporting layer.
    """
    if context_lines < 0:
        raise ValueError(
            "context_lines must be 0 or greater"
        )

    strings = load_search_strings(entry_file)

    if not strings:
        print("No search strings provided. Exiting.")
        return None

    results = {}
    detailed_results = {} if detailed else None

    script_path = os.path.abspath(entry_file)

    for path in iter_files(
        directory,
        excluded_dirs,
        excluded_exts,
        included_exts,
        exclude_hidden_dirs=exclude_hidden_dirs,
    ):
        if os.path.abspath(path) == script_path:
            continue

        try:
            with open(
                path,
                "r",
                encoding="utf-8",
                errors="ignore",
            ) as f:
                text = f.read()

            counts, matches = collect_match_positions(
                text=text,
                strings=strings,
                case_sensitive=case_sensitive,
            )

            if not counts:
                continue

            results[path] = counts

            if detailed:
                detailed_results[path] = {
                    "matches": matches,
                    "excerpts": build_context_excerpts(
                        text=text,
                        matches=matches,
                        context_lines=context_lines,
                    ),
                }

        except Exception:
            continue

    out = write_search_report(
        entry_file=entry_file,
        directory=directory,
        case_sensitive=case_sensitive,
        strings=strings,
        results=results,
        detailed_results=detailed_results,
        context_lines=context_lines,
    )

    return out
  
  # End of file search_mode.py