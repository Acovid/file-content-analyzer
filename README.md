# Python Multi-String File Search Tool

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)]()
[![License](https://img.shields.io/badge/license-personal%20%26%20educational-lightgrey.svg)]()
[![Status](https://img.shields.io/badge/status-active-green.svg)]()

A flexible command-line tool for recursively searching files for one or more strings.

This tool can:

- Search all files in a chosen directory and its subdirectories  
- Accept **multiple search strings**, from a file or manual input  
- Ignore comment lines in the search-strings file  
- Exclude specific directories (e.g., `.venv`, `.vscode`)  
- Count **how many times each string appears** in each file  
- Produce a clean **summary report** saved in `search-results/`  
- Skip binary/unreadable files gracefully  
- Allow case-sensitive or case-insensitive search  
- Skip searching inside the program file itself  

The script is interactive and guides the user step by step.

---

## 📚 Table of Contents

- [Requirements](#-requirements)  
- [Project Structure](#-project-structure)  
- [Using `search-strings.txt`](#-using-search-stringstxt)  
- [Running the Program](#-running-the-program)  
- [Launcher (`run-search.command`)](#-launcher-run-searchcommand)  
- [Custom Icon](#-custom-icon)  
- [What the Program Does](#-what-the-program-does)  
- [Output Report](#-output-report)  
- [Excluded Directories](#-excluded-directories)  
- [Demo / Example Runs](#-demo--example-runs)  
- [Future Enhancements](#-future-enhancements-ideas)  
- [License](#-license)

---

## ✅ Requirements

- **Python 3.8+**  
- A virtual environment is recommended but not required.

To create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

(on Windows, use `.venv\Scripts\activate`)

---

## 📂 Project Structure

A minimal setup looks like this:

```text
search_string.py      # main program
run-search.command    # macOS clickable launcher (opens Terminal and runs the tool)
search-strings.txt    # optional input file for search terms
icon.png              # icon for the launcher (e.g. Python + magnifying glass)
search-results/       # auto-created folder for output reports (ignored by Git)
.gitignore
README.md
```

`search-results/` is created automatically when you run the tool and is ignored by Git.

---

## 📝 Using `search-strings.txt`

You may include a file named **`search-strings.txt`** in the same directory as `search_string.py`.

Format rules:

- One search string per line  
- Empty lines are ignored  
- Comment lines start with `//` and are ignored  

Example:

```text
// Enter one search string per line.
// Blank lines are ignored.
// Lines starting with // are comments.
// Example search strings:
// error
// timeout

error
failed
TODO
```

When the script starts, it will detect this file and ask:

```text
Found search strings file 'search-strings.txt'. Use it? (y/n) [y]:
```

You can then optionally add more search strings manually.

---

## ▶️ Running the Program

From the project folder (using Python directly):

```bash
python search_string.py
```

The tool will prompt you for:

1. **Search strings** (from `search-strings.txt` and/or manual input)  
2. **Case sensitivity**  
3. **Directory to search**

---

## 🚀 Launcher `run-search.command`

On macOS, you can run the tool by simply **double-clicking** a `.command` file.

This repository includes a launcher:

```text
run-search.command
```

It:

- Finds the project directory automatically (relative to its own location)  
- Uses the virtual environment Python if `.venv/bin/python` exists  
- Falls back to `python3` otherwise  
- Runs `search_string.py` in a Terminal window  

### Make sure it is executable:

```bash
chmod +x run-search.command
```

To use it like an app:

- Option 1: Double-click `run-search.command` in Finder  
- Option 2: Create a Desktop alias  
  - Hold `⌥⌘` and drag `run-search.command` to the Desktop  
  - This keeps the real file in the repo but gives you a clickable shortcut

---

## 🎨 Custom Icon

This repo also includes an icon file (e.g. `icon.png`) you can use for your launcher.

To apply it to `run-search.command` or its Desktop alias:

1. Open `icon.png` in **Preview**  
2. Press `⌘A` to select all  
3. Press `⌘C` to copy  
4. Right-click `run-search.command` (or its alias) → **Get Info**  
5. Click the small icon in the top-left of the Info window (it should highlight)  
6. Press `⌘V` to paste the new icon  

Your launcher now looks like a polished app instead of a generic script file.

---

## 🔍 What the Program Does

- Recursively scans the directory you choose  
- Skips:

  - `.venv/`  
  - `.vscode/`  
  - the script file itself

- Attempts to read each file as text using UTF-8 (with errors ignored)  
- For each file, counts **how many times each search string appears**  
- Stores results as:

  ```text
  /path/to/file1.txt
      "error" : 3 occurrence(s)
      "timeout" : 1 occurrence(s)
  ```

---

## 🧾 Output Report

After finishing, the program writes a summary file to:

```text
search-results/
```

Example filename:

```text
search_results_error_20251205-183200.txt
```

Each report contains:

- All search strings used  
- Whether the search was case-sensitive  
- Directory scanned  
- Number of files with matches  
- Total number of occurrences  
- A detailed list of filenames + per-string counts  

Example excerpt:

```text
Search results
==============

Search strings:
  - 'error'
  - 'timeout'

Case-sensitive: False
Directory: /Users/aco/Projects
Total files with matches: 4
Total occurrences across all files: 27

Files containing one or more search strings:
--------------------------------------------

/Users/aco/Projects/app/logs/system.log
    'error' : 12 occurrence(s)
    'timeout' : 3 occurrence(s)

/Users/aco/Projects/app/debug.txt
    'error' : 5 occurrence(s)
```

---

## 🚫 Excluded Directories

By default, the program ignores:

- `.venv/`  
- `.vscode/`

These are controlled by the `EXCLUDE_DIRS` set near the top of `search_string.py`:

```python
EXCLUDE_DIRS = {".venv", ".vscode"}
```

You can add more, e.g.:

```python
EXCLUDE_DIRS = {".venv", ".vscode", ".git", "node_modules", "__pycache__"}
```

---

## 🎬 Demo / Example Runs

### Example 1: Use `search-strings.txt` only

```text
$ ./run-search.command

Found search strings file '.../search-strings.txt'. Use it? (y/n) [y]:
Do you want to add search strings manually? (y/n) [n]:
Should the search be case-sensitive? (y/n) [n]:
Search in the current directory where the program is? (y/n) [n]:
Enter full directory path to search: /Users/aco/Projects

Searching for the following strings:
  - 'error'
  - 'timeout'

Case-sensitive: False
In directory:   /Users/aco/Projects

Files containing one or more search strings:

/Users/aco/Projects/app/logs/system.log
    'error' : 12 occurrence(s)
    'timeout' : 3 occurrence(s)

Total files with matches: 1
Total occurrences across all files: 15

Results have been saved to: search-results/search_results_error_20251205-183200.txt
```

---

## 🛠 Future Enhancements (Ideas)

Some possible directions:

- **Regex search** (e.g., use `re` module for patterns)  
- **File extension filtering** (only `.py`, `.txt`, `.md`, etc.)  
- **Command-line arguments** using `argparse`, so you can run non-interactively:

  ```bash
  python search_string.py --dir /path --case no --strings-file my-strings.txt
  ```

- **CSV or JSON export** for easier tooling  
- Parallel scanning for large codebases  

---

## 📜 License

This project is intended for personal and educational use.  
Feel free to adapt it to your needs.