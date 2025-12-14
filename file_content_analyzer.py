import os
import datetime
from typing import Dict, List, Optional, Tuple

# --------------------------------------------
# File Content Analyzer
# --------------------------------------------

PROGRAM_NAME = "File Content Analyzer"

# Folders to skip during directory traversal
EXCLUDE_DIRS = {".venv", ".vscode"}


# ----------------------------
# Prompt helpers
# ----------------------------

def ask_yes_no(prompt: str, default: Optional[bool] = None) -> bool:
    """
    Ask a yes/no question and return True for yes, False for no.
    - default can be True, False, or None (meaning no default).
    - ENTER selects the default if provided.
    """
    if default is True:
        full_prompt = f"{prompt} (y/n) [y]: "
    elif default is False:
        full_prompt = f"{prompt} (y/n) [n]: "
    else:
        full_prompt = f"{prompt} (y/n): "

    while True:
        answer = input(full_prompt).strip().lower()

        # ENTER pressed → choose default
        if answer == "":
            if default is not None:
                return default
            print("Please answer with 'y' or 'n'.")
            continue

        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False

        print("Please answer with 'y' or 'n'.")


def ask_menu_choice() -> int:
    """
    Ask user to select an operation mode.
    Returns 1 or 2.
    Default is 1.
    """
    print("\nChoose an operation:")
    print("  1) Search for strings in files")
    print("  2) Count lines, words, and characters in files")

    while True:
        choice = input("\nEnter choice [1]: ").strip()
        if choice == "":
            return 1
        if choice in {"1", "2"}:
            return int(choice)
        print("Please enter 1 or 2 (or press ENTER for 1).")


def choose_directory(prompt_prefix: str = "Search") -> str:
    """
    Ask whether to use current directory or a custom one.
    Default: NO (i.e., user must enter a directory).
    """
    use_current = ask_yes_no(
        f"{prompt_prefix} in the current directory where the program is?",
        default=False
    )

    if use_current:
        return "."

    while True:
        path = input(f"Enter full directory path to {prompt_prefix.lower()}: ").strip()
        if os.path.isdir(path):
            return path
        print("That is not a valid directory. Please try again.\n")


# ----------------------------
# Search strings input
# ----------------------------

def load_search_strings_from_file(file_path: str) -> List[str]:
    """
    Load search strings from a file, one per line.
    Empty lines and comment lines (starting with //) are ignored.
    """
    strings: List[str] = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()

                if not s:
                    continue  # skip empty lines
                if s.startswith("//"):
                    continue  # skip comment lines

                strings.append(s)

    except Exception as e:
        print(f"Could not read search strings from file {file_path}: {e}")

    return strings


def prompt_for_search_strings() -> List[str]:
    """
    Let the user enter search strings manually (one per line).
    Returns a list. Empty line finishes input.
    """
    print("\nEnter search strings (one per line).")
    print("Press ENTER on an empty line when you are done.\n")

    strings: List[str] = []
    while True:
        line = input("Search string: ").strip()
        if line == "":
            break
        strings.append(line)
    return strings


def get_search_strings() -> Optional[List[str]]:
    """
    Combine optional file-based search strings and manual input.
    - Looks for 'search-strings.txt' in the script's directory.
    - Asks whether to use it if found.
    - Then optionally allows adding more strings manually.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_file = os.path.join(script_dir, "search-strings.txt")

    search_strings: List[str] = []

    # 1) Optional file input
    if os.path.isfile(default_file):
        use_file = ask_yes_no(
            f"Found search strings file '{default_file}'. Use it?",
            default=True
        )
        if use_file:
            file_strings = load_search_strings_from_file(default_file)
            if file_strings:
                print(f"Loaded {len(file_strings)} search string(s) from file.")
                search_strings.extend(file_strings)
            else:
                print("The search strings file was empty or unreadable.")

    # 2) Optional manual input
    add_manual = ask_yes_no(
        "Do you want to add search strings manually?",
        default=True if not search_strings else False
    )
    if add_manual:
        manual_strings = prompt_for_search_strings()
        if manual_strings:
            search_strings.extend(manual_strings)

    # 3) Final check
    if not search_strings:
        print("No search strings provided. Exiting.")
        return None

    # Remove duplicates while preserving order
    seen = set()
    unique_strings: List[str] = []
    for s in search_strings:
        if s not in seen:
            seen.add(s)
            unique_strings.append(s)

    return unique_strings


# ----------------------------
# Traversal helpers
# ----------------------------

def iter_files(start_dir: str) -> List[str]:
    """
    Return a list of file paths under start_dir, excluding EXCLUDE_DIRS.
    """
    files_found: List[str] = []
    for root, dirs, files in os.walk(start_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for filename in files:
            files_found.append(os.path.join(root, filename))
    return files_found


# ----------------------------
# Mode 1: String Search
# ----------------------------

def find_strings_in_files(
    search_strings: List[str],
    start_dir: str,
    case_sensitive: bool
) -> Dict[str, Dict[str, int]]:
    """
    Return a dict: {file_path: {search_string: occurrence_count}}
    Only includes files where at least one string occurs.
    """
    results: Dict[str, Dict[str, int]] = {}

    processed_terms = list(search_strings) if case_sensitive else [s.lower() for s in search_strings]
    script_path = os.path.abspath(__file__)

    for file_path in iter_files(start_dir):
        if os.path.abspath(file_path) == script_path:
            continue  # skip this program file

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                content_to_search = content if case_sensitive else content.lower()

                file_counts: Dict[str, int] = {}
                for original, term in zip(search_strings, processed_terms):
                    count = content_to_search.count(term)
                    if count > 0:
                        file_counts[original] = count

                if file_counts:
                    results[file_path] = file_counts

        except Exception as e:
            print(f"Skipping {file_path} (cannot read): {e}")

    return results


# ----------------------------
# Mode 2: File Statistics
# ----------------------------

def compute_file_stats(start_dir: str) -> Dict[str, Dict[str, int]]:
    """
    Return a dict: {file_path: {"lines": int, "words": int, "chars": int}}
    Skips unreadable files. Counts are based on decoded text (utf-8, errors ignored).
    """
    results: Dict[str, Dict[str, int]] = {}
    script_path = os.path.abspath(__file__)

    for file_path in iter_files(start_dir):
        if os.path.abspath(file_path) == script_path:
            continue  # skip this program file

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

            # Lines: splitlines() counts lines reliably across \n / \r\n
            lines = len(text.splitlines())

            # Words: split on any whitespace
            words = len(text.split())

            # Characters: includes whitespace
            chars = len(text)

            results[file_path] = {"lines": lines, "words": words, "chars": chars}

        except Exception as e:
            print(f"Skipping {file_path} (cannot read): {e}")

    return results


# ----------------------------
# Reporting (log files)
# ----------------------------

def _script_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def make_output_filename(operation_slug: str, description: str) -> str:
    """
    Always create the results folder in the same directory as the script.
    Returns an absolute path to the output report file.
    """
    output_dir = os.path.join(_script_dir(), "search-results")
    os.makedirs(output_dir, exist_ok=True)

    safe_desc = "".join(c if c.isalnum() else "_" for c in description).strip("_")
    if not safe_desc:
        safe_desc = "report"
    safe_desc = safe_desc[:30]

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{operation_slug}_{safe_desc}_{timestamp}.txt"
    return os.path.join(output_dir, filename)


def write_search_report(
    filename: str,
    search_strings: List[str],
    case_sensitive: bool,
    search_directory: str,
    results_dict: Dict[str, Dict[str, int]]
) -> None:
    total_files = len(results_dict)
    total_occurrences = sum(sum(counts.values()) for counts in results_dict.values())

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"{PROGRAM_NAME} - String Search Report\n")
        f.write("================================\n\n")
        f.write(f"Operation: String search\n")
        f.write(f"Directory: {os.path.abspath(search_directory)}\n")
        f.write(f"Case-sensitive: {case_sensitive}\n")
        f.write("Search strings:\n")
        for s in search_strings:
            f.write(f"  - {repr(s)}\n")

        f.write("\nSummary:\n")
        f.write(f"  Total files with matches: {total_files}\n")
        f.write(f"  Total occurrences: {total_occurrences}\n\n")

        if total_files == 0:
            f.write("No files containing the search strings were found.\n")
            return

        f.write("Files containing one or more search strings:\n")
        f.write("--------------------------------------------\n\n")
        for file_path, counts in results_dict.items():
            f.write(f"{file_path}\n")
            for term, count in counts.items():
                f.write(f"    {repr(term)} : {count} occurrence(s)\n")
            f.write("\n")


def write_stats_report(
    filename: str,
    directory: str,
    stats_dict: Dict[str, Dict[str, int]]
) -> None:
    total_files = len(stats_dict)
    total_lines = sum(v["lines"] for v in stats_dict.values())
    total_words = sum(v["words"] for v in stats_dict.values())
    total_chars = sum(v["chars"] for v in stats_dict.values())

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"{PROGRAM_NAME} - File Statistics Report\n")
        f.write("====================================\n\n")
        f.write("Operation: File statistics (lines, words, characters)\n")
        f.write(f"Directory: {os.path.abspath(directory)}\n\n")

        f.write("Summary:\n")
        f.write(f"  Total files analyzed: {total_files}\n")
        f.write(f"  Total lines: {total_lines}\n")
        f.write(f"  Total words: {total_words}\n")
        f.write(f"  Total characters: {total_chars}\n\n")

        if total_files == 0:
            f.write("No readable files were found.\n")
            return

        f.write("Per-file statistics:\n")
        f.write("--------------------\n\n")
        for file_path, stats in stats_dict.items():
            f.write(f"{file_path}\n")
            f.write(f"    Lines: {stats['lines']}\n")
            f.write(f"    Words: {stats['words']}\n")
            f.write(f"    Characters: {stats['chars']}\n\n")


# ----------------------------
# Runner functions for each mode
# ----------------------------

def run_string_search() -> str:
    search_strings = get_search_strings()
    if not search_strings:
        return "No search strings provided. Exiting."

    case_sensitive = ask_yes_no("Should the search be case-sensitive?", default=False)
    search_directory = choose_directory(prompt_prefix="Search")

    print("\nSearching for the following strings:")
    for s in search_strings:
        print(f"  - {repr(s)}")
    print(f"\nCase-sensitive: {case_sensitive}")
    print(f"In directory:   {os.path.abspath(search_directory)}\n")

    results = find_strings_in_files(
        search_strings=search_strings,
        start_dir=search_directory,
        case_sensitive=case_sensitive
    )

    if results:
        print("Files containing one or more search strings:\n")
        for file_path, counts in results.items():
            print(file_path)
            for term, count in counts.items():
                print(f"    {repr(term)} : {count} occurrence(s)")
            print()

        total_files = len(results)
        total_occurrences = sum(sum(counts.values()) for counts in results.values())
        print(f"Total files with matches: {total_files}")
        print(f"Total occurrences across all files: {total_occurrences}")
    else:
        print("No files containing the search strings were found.")

    description = search_strings[0] if search_strings else "search"
    output_filename = make_output_filename("string_search", description)
    write_search_report(
        filename=output_filename,
        search_strings=search_strings,
        case_sensitive=case_sensitive,
        search_directory=search_directory,
        results_dict=results
    )

    return f"Results have been saved to:\n  {output_filename}"


def run_file_statistics() -> str:
    stats_directory = choose_directory(prompt_prefix="Analyze")

    print(f"\nAnalyzing files in directory: {os.path.abspath(stats_directory)}\n")
    stats = compute_file_stats(stats_directory)

    if stats:
        # Print a short console summary
        total_files = len(stats)
        total_lines = sum(v["lines"] for v in stats.values())
        total_words = sum(v["words"] for v in stats.values())
        total_chars = sum(v["chars"] for v in stats.values())

        print("Summary:")
        print(f"  Total files analyzed: {total_files}")
        print(f"  Total lines: {total_lines}")
        print(f"  Total words: {total_words}")
        print(f"  Total characters: {total_chars}\n")
    else:
        print("No readable files were found.\n")

    output_filename = make_output_filename("file_stats", "lines_words_chars")
    write_stats_report(
        filename=output_filename,
        directory=stats_directory,
        stats_dict=stats
    )

    return f"Results have been saved to:\n  {output_filename}"


# ----------------------------
# Main
# ----------------------------

if __name__ == "__main__":
    print(f"\n{PROGRAM_NAME}")
    print("=" * len(PROGRAM_NAME))

    mode = ask_menu_choice()

    if mode == 1:
        final_message = run_string_search()
    else:
        final_message = run_file_statistics()

    print(f"\n{final_message}")
    print("\nDone.")