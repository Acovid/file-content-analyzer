# File Content Analyzer

A Python utility for analyzing files across a directory tree.

It supports three operation modes:

1) **String Search**  
   Search for one or more strings in files, count occurrences, and generate a report.

2) **File Statistics**  
   Count lines, words, and characters across files, including per-extension totals.

3) **Filename Search**  
   Search for files by name or glob-style patterns and report where they are located.

The tool is interactive by default, but also supports non-interactive usage via command-line arguments.

---

## Features

- Recursively scans a chosen directory and its subdirectories
- Three modes:
  - String search with per-string occurrence counts per file
  - File statistics (lines / words / characters) with per-extension totals
  - Filename search using exact names or glob patterns
- Accepts batch input files and/or manual input
- Supports case-sensitive and case-insensitive matching
- Excludes directories such as `.venv` and `.vscode`
- Supports file type filtering (include / exclude extensions)
- Skips unreadable or binary files gracefully
- Skips analyzing the program file itself
- Produces timestamped reports saved under `analysis-results/`
- Uses persistent settings stored in `config.json`
- Can edit configuration interactively
- Includes unit tests (built-in `unittest`)

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
    │   └── test_core.py
    ├── CHANGELOG.md
    ├── README.md
    └── .gitignore

---

## Running the Program

### Option A: Run with Python

From the project folder:

    python file_content_analyzer.py

You will be guided through interactive prompts:

- choose mode (string search, statistics, or filename search)
- choose directory (default is NO → you enter a path)
- configure include/exclude file types (optional)
- mode-specific options (case sensitivity, patterns, etc.)

### Option B: macOS Launcher

The repository includes:

    run-file-content-analyzer.command

Make it executable once:

    chmod +x run-file-content-analyzer.command

Then double-click it in Finder (or create a Desktop alias).

---

## Output Reports

Reports are written to:

    analysis-results/

Examples:

    analysis-results/string_search_20251214-112233.txt
    analysis-results/file_stats_20251214-113015.txt
    analysis-results/name_search_20251214-114502.txt

Reports include:

- operation type
- directory analyzed
- summary totals
- per-file details
- (statistics mode) per-extension totals
- (filename search) list of matching paths per pattern

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

When the tool starts, it will detect this file and ask whether to use it.

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

When filename search mode is selected, the tool will detect this file and ask whether to use it.

---

## File Type Filtering (Include / Exclude Extensions)

You can filter by file extension (without dots). Examples: `py`, `txt`, `jpg`.

### Include-only list

If `included_extensions` is not empty, ONLY those extensions are processed.

Example:

    included_extensions = ["py", "txt"]

Processes only `.py` and `.txt` files.

### Exclude list

`excluded_extensions` is always applied (even after include-only).

Example:

    excluded_extensions = ["log", "map", "jpg"]

### Important note for Filename Search Mode

Filename search operates on **file names**, not file contents.

If certain file types (e.g. images) are excluded via configuration,
they will not be discovered during filename search.

If you want to search for files such as `.jpg`, `.png`, or `.pdf`,
ensure those extensions are **not excluded** in `config.json`.

---

## Configuration (config.json)

The tool reads `config.json` next to the main script.  
You can edit it manually at any time.

Example `config.json`:

    {
      "excluded_extensions": ["js", "map", "log"],
      "included_extensions": [],
      "excluded_dirs": [".venv", ".vscode", ".git", "__pycache__"]
    }

Rules:

- If `included_extensions` is empty: all extensions are allowed
- If `included_extensions` is not empty: only those are allowed
- Then `excluded_extensions` are removed
- `excluded_dirs` are skipped during traversal

The program also offers an interactive editor:

    Edit configuration? (y/n) [n]:

If you answer yes, it will update and save `config.json`.

---

## Command-line Usage (Non-interactive)

You can run without prompts (or fewer prompts) using CLI flags:

String search mode:

    python file_content_analyzer.py --search --dir /path/to/scan

Statistics mode:

    python file_content_analyzer.py --stats --dir /path/to/scan

Filename search mode:

    python file_content_analyzer.py --names --dir /path/to/scan

Case-sensitive search:

    python file_content_analyzer.py --search --case-sensitive --dir /path/to/scan

Include-only extensions:

    python file_content_analyzer.py --stats --dir /path --include py,txt

Exclude extensions:

    python file_content_analyzer.py --search --dir /path --exclude js,map,log

Ignore config.json entirely:

    python file_content_analyzer.py --stats --dir /path --no-config

Edit config and exit:

    python file_content_analyzer.py --edit-config

---

## Unit Tests

Tests are located in:

    tests/

Run all tests:

    python3 -m unittest -v

These tests cover:

- extension normalization
- traversal include/exclude behavior
- excluded directory behavior

---

## Troubleshooting

### “Can’t open file ... file_content_analyzer.py”

This typically happens if you ran the launcher from a copied folder missing the script, or you created a copy instead of an alias.
Make sure the launcher resides in the same project folder and points to the correct script.

### The output folder is not where I expect

Reports are always written next to the main script under:

    analysis-results/

If you see it elsewhere, you likely ran a different copy of the tool.

### Some files are skipped

The tool ignores files it cannot decode as text (or that error on read).
Files may also be skipped due to extension filters in `config.json`.

---

## License

Personal and educational use.  
Feel free to adapt it to your needs.