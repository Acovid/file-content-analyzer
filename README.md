# File Content Analyzer

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)]()
[![License](https://img.shields.io/badge/license-personal%20%26%20educational-lightgrey.svg)]()
[![Status](https://img.shields.io/badge/status-active-green.svg)]()

**File Content Analyzer** is a flexible Python-based command-line tool for analyzing text files across directory trees.

It supports multiple analysis modes and produces clean, human-readable reports saved to disk.

---

## ✨ Features

This tool can:

- Recursively scan all files in a chosen directory and subdirectories
- Provide **multiple operation modes**
  - **String search** with occurrence counting
  - **File statistics** (lines, words, characters)
- Accept multiple search strings (from file and/or manual input)
- Ignore comment lines in input files
- Exclude specific **directories**
- Exclude specific **file types**
- Skip binary/unreadable files gracefully
- Allow case-sensitive or case-insensitive search
- Skip analyzing the program file itself
- Generate timestamped **summary reports**
- Save reports automatically to `search-results/`

The program is fully interactive and guides the user step by step.

---

## 📚 Table of Contents

- Requirements
- Installation
- Project Structure
- Operation Modes
- Using search-strings.txt
- File Type Exclusion
- Running the Program
- Launcher (run-search.command)
- Custom Icon
- Output Reports
- Excluded Directories
- Demo / Example Runs
- Future Enhancements
- License

---

## ✅ Requirements

- Python 3.8+
- macOS, Linux, or Windows
- A virtual environment is recommended

---

## 📦 Installation

Create and activate a virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

(Windows: `.venv\Scripts\activate`)

---

## 📂 Project Structure

    file-content-analyzer/
    ├── search_string.py        # main program
    ├── run-search.command      # macOS launcher
    ├── search-strings.txt      # optional search terms file
    ├── icon.png                # optional launcher icon
    ├── search-results/         # auto-created output reports
    ├── .gitignore
    └── README.md

---

## 🔧 Operation Modes

When the program starts, you choose an operation:

    1) Search for strings in files
    2) Count lines, words, and characters in files

### Mode 1 — String Search

- Counts how many times each string appears in each file
- Supports case-sensitive or insensitive search

### Mode 2 — File Statistics

Counts:

- Lines
- Words
- Characters

Also provides totals across all files and per-file breakdown.

---

## 📝 Using search-strings.txt

Optional file placed next to the script.

Rules:

- One string per line
- Empty lines ignored
- Lines starting with `//` are comments

Example:

    // One search string per line
    // Comments start with //
    
    error
    timeout
    TODO

---

## 🧹 File Type Exclusion

You may optionally exclude file types by extension.

Example prompt:

    Do you want to exclude specific file types? (y/n) [n]:
    Enter file extensions to exclude (comma-separated):
    js,map,log,min.css

Notes:

- Extensions are case-insensitive
- Do not include dots
- Files without extensions are included by default

---

## ▶️ Running the Program

Run directly:

    python search_string.py

Or on macOS:

    Double-click run-search.command

---

## 🚀 Launcher run-search.command

The launcher:

- Automatically finds the project directory
- Uses `.venv/bin/python` if available
- Opens Terminal visibly
- Displays a welcome banner
- Keeps the window open after completion

Make executable:

    chmod +x run-search.command

---

## 🎨 Custom Icon

To apply icon.png:

1. Open it in Preview
2. Select all (Cmd+A)
3. Copy (Cmd+C)
4. Right-click run-search.command or its alias → Get Info
5. Click the small icon in the top-left
6. Paste (Cmd+V)

---

## 🧾 Output Reports

Reports are saved to:

    search-results/

Example filenames:

    string_search_error_20251205-183200.txt
    file_stats_lines_words_chars_20251206-101455.txt

Each report includes:

- Operation type
- Directory analyzed
- Summary totals
- Per-file details

---

## 🚫 Excluded Directories

By default:

    EXCLUDE_DIRS = {".venv", ".vscode"}

You may extend this to:

    {".venv", ".vscode", ".git", "node_modules", "__pycache__", ".idea"}

---

## 🎬 Demo / Example Runs

Example startup:

    File Content Analyzer
    ====================
    
    Choose an operation:
      1) Search for strings in files
      2) Count lines, words, and characters in files

---

## 🛠 Future Enhancements

- Regex-based searching
- File extension include filters
- Non-interactive CLI arguments
- CSV / JSON exports
- Persistent configuration file
- Parallel scanning
- Language-aware code metrics

---

## 📜 License

This project is intended for **personal and educational use**.  
Feel free to adapt, extend, and experiment.