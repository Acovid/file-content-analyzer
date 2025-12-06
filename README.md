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
- [What the Program Does](#-what-the-program-does)  
- [Output Report](#-output-report)  
- [Excluded Directories](#-excluded-directories)  
- [Demo / Example Runs](#-demo--example-runs)  
- [Continuous Integration (optional)](#-continuous-integration-optional)  
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
search-strings.txt    # optional input file for search terms
search-results/       # auto-created folder for output reports
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

From the project folder:

```bash
python search_string.py
```

The tool will prompt you for:

1. **Search strings**

   - From `search-strings.txt` (if available)  
   - Optional manual input (one per line, empty line to finish)

2. **Case sensitivity**

   ```text
   Should the search be case-sensitive? (y/n) [n]:
   ```

   - Press **ENTER** to accept the default (**no**, case-insensitive)

3. **Directory to search**

   ```text
   Search in the current directory where the program is? (y/n) [n]:
   Enter full directory path to search:
   ```

   - Default is **no** → pressing ENTER will ask you for a full directory path  
   - macOS tip: in Finder, right-click the folder → hold **⌥ Option** → _Copy as Pathname_ → paste into the terminal

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
$ python search_string.py
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

### Example 2: Only manual search strings

```text
$ python search_string.py
Found search strings file '.../search-strings.txt'. Use it? (y/n) [y]:
Do you want to add search strings manually? (y/n) [y]:

Enter search strings (one per line).
Press ENTER on an empty line when you are done.

Search string: TODO
Search string: FIXME
Search string:

Should the search be case-sensitive? (y/n) [n]:
Search in the current directory where the program is? (y/n) [n]:
Enter full directory path to search: /Users/aco/Projects/notes
...
```

---

## 🤖 Continuous Integration (optional)

If you want to add a tiny CI setup using GitHub Actions (for example, to make sure the script runs and passes basic checks), you can create:

**File:** `.github/workflows/python-check.yml`

```yaml
name: Python checks

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  run-checks:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Run basic syntax check
        run: python -m py_compile search_string.py
```

This is minimal, but it will:

- Check out your code
- Install Python
- Ensure `search_string.py` at least compiles

You can extend this later with unit tests if you add them.

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