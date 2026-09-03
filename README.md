# File Content Analyzer

A Python utility for analyzing files across a directory tree.

It supports three operation modes:

1) **String Search**  
   Search for one or more strings in files, count occurrences, and generate either a compact summary report or a detailed source-context report.

2) **File Statistics**  
   Count lines, words, and characters across files, including per-extension totals.

3) **Filename Search**  
   Search for files by name or glob-style patterns and report where they are located.

The tool is interactive by default, but also supports command-line arguments for faster or partially non-interactive operation.

---

## Features

- Recursively scans a chosen directory and its subdirectories
- Three modes:
  - String Search with per-string occurrence counts per file
  - File Statistics (lines / words / characters) with per-extension totals
  - Filename Search using exact names or glob patterns
- String Search supports two report levels:
  - Summary report
  - Detailed Match Context report
- Detailed Match Context reports include:
  - complete file paths
  - exact source line numbers
  - configurable context lines before and after matches
  - explicit `MATCH:` annotations
  - match column positions
  - merged overlapping or adjacent context windows
  - protection against extremely long or minified source lines
- Accepts batch input files and/or manual input
- Supports case-sensitive and case-insensitive matching
- Supports exact directory exclusions
- Can optionally exclude all hidden directories
- Supports file type filtering (include / exclude extensions)
- Skips unreadable files gracefully
- Skips analyzing the program file itself during String Search
- Produces timestamped reports saved under `analysis-results/`
- Uses persistent settings stored in `config.json`
- Can edit configuration interactively
- Includes unit tests using Python's built-in `unittest`

---

## Requirements

- Python 3.8+
- macOS / Linux / Windows
- Recommended: a virtual environment

---

## Installation

Create and activate a virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Windows:

    .venv\Scripts\activate

Install dependencies:

- None required (standard library only)

---

## Project Structure

Typical layout:

    file-content-analyzer/
    ├── file_content_analyzer.py
    ├── run-file-content-analyzer.command
    ├── config.json                  (optional; auto-created)
    ├── search-strings.txt           (optional)
    ├── file-names.txt               (optional)
    ├── analysis-results/            (auto-created; gitignored)
    ├── fca/
    │   ├── __init__.py
    │   ├── cli.py
    │   ├── config.py
    │   ├── prompts.py
    │   ├── traversal.py
    │   ├── search_mode.py
    │   ├── stats_mode.py
    │   ├── name_search_mode.py
    │   └── reporting.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_core.py
    │   └── test_search_mode.py
    ├── CHANGELOG.md
    ├── README.md
    └── .gitignore

---

## Running the Program

### Option A: Run with Python

From the project folder:

    python file_content_analyzer.py

You will be guided through interactive prompts:

- choose mode (String Search, File Statistics, or Filename Search)
- choose the directory to process
- optionally edit configuration
- choose mode-specific options

For String Search, the interactive workflow can also ask:

    Case-sensitive search? (y/n) [n]:
    Include detailed match context? (y/n) [n]:

If detailed context is selected:

    Context lines before/after [5]:

Press ENTER to use the default of 5 context lines before and after each match.

Any non-negative integer is accepted, including `0`.

---

### Option B: macOS Launcher

The repository includes:

    run-file-content-analyzer.command

Make it executable once:

    chmod +x run-file-content-analyzer.command

Then double-click it in Finder or create a Desktop alias.

---

## Output Reports

Reports are written to:

    analysis-results/

Examples:

    analysis-results/string_search_20260903-150813.txt
    analysis-results/file_stats_20260903-151015.txt
    analysis-results/name_search_20260903-151502.txt

Reports include:

- program name and version
- operation type
- directory analyzed
- summary totals
- per-file details
- statistics-mode per-extension totals
- filename-search matching paths per pattern

String Search reports can additionally contain a **Detailed Match Context** section.

---

## String Search Reports

### Summary Report

The standard String Search report contains:

- directory searched
- case-sensitivity setting
- search strings
- number of files containing matches
- total occurrence count
- occurrence count for each search string in each matching file

Example:

    Total files with matches: 2
    Total occurrences: 7
    
    /path/to/style.css
      primary-button: 4
      secondary-button: 3

---

### Detailed Match Context Report

Detailed mode retains the normal summary and appends source excerpts for every match.

Example:

    FILE: /path/to/style.css
    ------------------------
    
    Excerpt 1: lines 246-256
    ------------------------
      246 | /* ======= */
      247 | /* BUTTONS */
      248 | /* ======= */
      249 |
      250 | /* PRIMARY BUTTON */
    > 251 | .elementor-button.bering-btn-primary,
             MATCH: bering-btn-primary (columns 19-36)
      252 | .another-selector {
      253 |   background-color: var(--accent);
      254 | }

The `>` marker identifies a source line containing one or more matches.

Each `MATCH:` annotation identifies:

- the exact requested search string
- the starting column
- the ending column

This is useful for code audits where the surrounding implementation matters as much as the occurrence count.

---

## Context Window Behavior

Detailed String Search uses line-based context.

For example, a context value of:

    5

means that the report attempts to show:

- 5 lines before the matching line
- the matching line
- 5 lines after the matching line

Context windows are automatically clipped at the beginning and end of files.

If multiple matches have overlapping or directly adjacent context windows, those windows are merged into a single excerpt. This prevents the same source lines from being repeated unnecessarily.

A context value of:

    0

shows only matching lines.

---

## Long and Minified Lines

Detailed reports protect against extremely long source lines, such as minified CSS or JavaScript.

Normal source lines are displayed in full up to the configured internal display limit.

If a matching line exceeds that limit:

- the report creates a focused character excerpt around the match
- the complete matched search string remains visible
- omitted text is indicated with an ellipsis
- the original line length is reported

If matches occur far apart on the same very long line, multiple focused excerpts may be generated rather than printing the entire line.

Long non-matching context lines are also truncated to prevent generated reports from becoming unnecessarily large.

---

## Using search-strings.txt (String Search Mode)

You can place an optional file:

    search-strings.txt

in the same folder as `file_content_analyzer.py`.

Rules:

- One string per line
- Empty lines ignored
- Lines starting with `//` are comments

Example:

    // One search string per line
    // Lines starting with // are comments
    
    error
    timeout
    TODO

When the tool starts String Search, it detects this file and asks whether to use it.

You can also add search strings manually.

Duplicate search strings are removed while preserving their original order.

---

## String Search Semantics

Each requested search string is evaluated independently.

Matches for the same search string are non-overlapping, consistent with Python's `str.count()` behavior.

For example:

    Text: aaa
    Search string: aa

produces:

    1 occurrence

Case-insensitive searching uses lowercase comparison while preserving the original requested search string in reports.

---

## Using file-names.txt (Filename Search Mode)

You can place an optional file:

    file-names.txt

in the same folder as `file_content_analyzer.py`.

Rules:

- One filename or glob pattern per line
- Empty lines ignored
- Lines starting with `//` are comments

Supported patterns use standard glob syntax:

- `*.php`
- `config.json`
- `style*.css`
- `*checkout*`

Example:

    // One filename or pattern per line
    // Lines starting with // are comments
    
    wp-config.php
    *.md
    style*.css

When Filename Search mode is selected, the tool detects this file and asks whether to use it.

---

## File Type Filtering (Include / Exclude Extensions)

You can filter by file extension without dots.

Examples:

    py
    txt
    css
    jpg

### Include-only list

If `included_extensions` is not empty, only those extensions are processed.

Example:

    "included_extensions": ["py", "txt"]

This processes only `.py` and `.txt` files.

### Exclude list

`excluded_extensions` is always applied.

Example:

    "excluded_extensions": ["log", "map", "jpg"]

### Important note for Filename Search Mode

Filename Search operates on file names, not file contents.

If certain file types such as images are excluded through configuration, they will not be discovered during Filename Search.

If you want to search for files such as `.jpg`, `.png`, or `.pdf`, ensure those extensions are not excluded in `config.json`.

---

## Directory Filtering

The Analyzer supports two complementary directory-filtering mechanisms.

### Exact excluded directories

Directories listed in:

    excluded_dirs

are skipped by name.

Typical examples:

    .venv
    .vscode
    .git
    __pycache__

### Exclude all hidden directories

The configuration option:

    "exclude_hidden_dirs": true

causes every directory whose name starts with `.` to be skipped.

For example:

    .git
    .vscode
    .idea
    .cache

This traversal rule is applied consistently to:

- String Search
- File Statistics
- Filename Search

Set it to:

    false

if hidden directories should be traversed unless they are individually listed in `excluded_dirs`.

---

## Configuration (config.json)

The tool reads `config.json` next to the main script.

You can edit it manually at any time.

Example:

    {
      "default_directory": "/path/to/project",
      "excluded_dirs": [
        ".venv",
        ".vscode",
        ".git",
        "__pycache__"
      ],
      "exclude_hidden_dirs": true,
      "excluded_extensions": [],
      "included_extensions": []
    }

Rules:

- `default_directory` remembers the most recently used directory
- if `included_extensions` is empty, all extensions are allowed
- if `included_extensions` is not empty, only those extensions are allowed
- `excluded_extensions` are then removed
- names in `excluded_dirs` are skipped during traversal
- if `exclude_hidden_dirs` is `true`, all hidden directories are skipped

The program also offers an interactive editor:

    Edit configuration? (y/n) [n]:

If you answer yes, supported configuration values can be updated and saved to `config.json`.

---

## Command-line Usage

CLI flags can reduce the number of interactive prompts.

### String Search

    python file_content_analyzer.py --search --dir /path/to/scan

### File Statistics

    python file_content_analyzer.py --stats --dir /path/to/scan

### Filename Search

    python file_content_analyzer.py --names --dir /path/to/scan

### Case-sensitive String Search

    python file_content_analyzer.py --search --case-sensitive --dir /path/to/scan

### Detailed String Search

    python file_content_analyzer.py --search --detailed --dir /path/to/scan

### Detailed String Search with custom context

    python file_content_analyzer.py --search --detailed --context-lines 10 --dir /path/to/scan

A context value of zero is valid:

    python file_content_analyzer.py --search --detailed --context-lines 0 --dir /path/to/scan

### Include-only extensions

    python file_content_analyzer.py --stats --dir /path --include py,txt

### Exclude extensions

    python file_content_analyzer.py --search --dir /path --exclude js,map,log

### Ignore config.json

    python file_content_analyzer.py --stats --dir /path --no-config

### Edit config and exit

    python file_content_analyzer.py --edit-config

`--context-lines` must be zero or greater.

---

## Unit Tests

Tests are located in:

    tests/

Run all tests:

    python3 -m unittest -v

The current test suite covers:

- extension normalization
- traversal include/exclude behavior
- hidden-directory exclusion
- non-negative integer prompt handling
- String Search occurrence-count semantics
- non-overlapping match behavior
- case-sensitive and case-insensitive matching
- match line and column positions
- multiple search terms on the same source line
- context-window construction
- file-boundary clipping
- overlapping context-window merging
- adjacent context-window merging
- separate context excerpts
- Detailed Match Context report generation
- preservation of Summary reporting
- long/minified matching-line truncation

---

## Troubleshooting

### “Can’t open file ... file_content_analyzer.py”

This typically happens if the launcher was run from a copied folder that is missing the script, or if a copy was created instead of an alias.

Make sure the launcher resides in the same project folder and points to the correct script.

### The output folder is not where I expect

Reports are always written next to the main script under:

    analysis-results/

If you see them elsewhere, you may be running a different copy of the tool.

### Some files are skipped

Files may be skipped because of:

- directory exclusions
- hidden-directory exclusion
- include-only extension filtering
- excluded extensions
- file read/decode errors

Review `config.json` if expected files are missing from a report.

### Detailed report does not appear

During interactive String Search, answer:

    Include detailed match context? (y/n) [n]: y

For command-line usage, use:

    --detailed

### Too much context is shown

Choose a smaller value when prompted:

    Context lines before/after [5]:

For example:

    1

or:

    0

For command-line usage:

    --context-lines 1

---

## License

Personal and educational use.  
Feel free to adapt it to your needs.