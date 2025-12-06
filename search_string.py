import os
import datetime

# Folders to skip during search
EXCLUDE_DIRS = {".venv", ".vscode"}


def ask_yes_no(prompt, default=None):
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
            else:
                print("Please answer with 'y' or 'n'.")
                continue

        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False

        print("Please answer with 'y' or 'n'.")


def choose_directory():
    """
    Ask whether to use current directory or a custom one.
    Default: NO (i.e., user must enter a directory).
    """
    use_current = ask_yes_no(
        "Search in the current directory where the program is?",
        default=False   # default changed to NO
    )

    if use_current:
        return "."

    # Ask for a custom directory path
    while True:
        path = input("Enter full directory path to search: ").strip()

        if os.path.isdir(path):
            return path
        else:
            print("That is not a valid directory. Please try again.\n")


def load_search_strings_from_file(file_path):
    """
    Load search strings from a file, one per line.
    Empty lines and comment lines (starting with //) are ignored.
    """
    strings = []
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


def prompt_for_search_strings():
    """
    Let the user enter search strings manually (one per line).
    Returns a list. Empty line finishes input.
    """
    print("\nEnter search strings (one per line).")
    print("Press ENTER on an empty line when you are done.\n")

    strings = []
    while True:
        line = input("Search string: ").strip()
        if line == "":
            break
        strings.append(line)
    return strings


def get_search_strings():
    """
    Combine optional file-based search strings and manual input.
    - Looks for 'search-strings.txt' in the script's directory.
    - Asks whether to use it if found.
    - Then optionally allows adding more strings manually.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_file = os.path.join(script_dir, "search-strings.txt")

    search_strings = []

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
    unique_strings = []
    for s in search_strings:
        if s not in seen:
            seen.add(s)
            unique_strings.append(s)

    return unique_strings


def find_strings_in_files(search_strings, start_dir=".", case_sensitive=True):
    """
    Return a dict: {file_path: {search_string: occurrence_count}}
    Only includes files where at least one string occurs.
    """
    results = {}

    # Prepare processed version for searching (for case-insensitive mode)
    if case_sensitive:
        processed_terms = list(search_strings)
    else:
        processed_terms = [s.lower() for s in search_strings]

    script_path = os.path.abspath(__file__)

    for root, dirs, files in os.walk(start_dir):
        # Remove excluded directories from the walk
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for filename in files:
            file_path = os.path.join(root, filename)

            # Skip this program itself
            if os.path.abspath(file_path) == script_path:
                continue

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    content_to_search = content if case_sensitive else content.lower()

                    file_counts = {}
                    # Count occurrences of each term
                    for original, term in zip(search_strings, processed_terms):
                        count = content_to_search.count(term)
                        if count > 0:
                            file_counts[original] = count

                    if file_counts:
                        results[file_path] = file_counts

            except Exception as e:
                print(f"Skipping {file_path} (cannot read): {e}")

    return results


def make_output_filename(search_for_description):
    """
    Create the search-results directory if missing, then
    return a full path for the output file.
    search_for_description is used just to make name a bit meaningful.
    """
    # Ensure output directory exists
    output_dir = "search-results"
    os.makedirs(output_dir, exist_ok=True)

    # Sanitize description for filename
    safe_term = "".join(c if c.isalnum() else "_" for c in search_for_description)
    if not safe_term:
        safe_term = "search"
    safe_term = safe_term[:30]

    # Timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    # Full path: search-results/search_results_term_timestamp.txt
    filename = f"search_results_{safe_term}_{timestamp}.txt"
    return os.path.join(output_dir, filename)


def write_results_to_file(
    filename,
    search_strings,
    case_sensitive,
    search_directory,
    results_dict
):
    total_files = len(results_dict)
    total_occurrences = sum(
        sum(counts.values()) for counts in results_dict.values()
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write("Search results\n")
        f.write("==============\n\n")
        f.write("Search strings:\n")
        for s in search_strings:
            f.write(f"  - {repr(s)}\n")
        f.write(f"\nCase-sensitive: {case_sensitive}\n")
        f.write(f"Directory: {os.path.abspath(search_directory)}\n")
        f.write(f"Total files with matches: {total_files}\n")
        f.write(f"Total occurrences across all files: {total_occurrences}\n\n")

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


if __name__ == "__main__":
    # 1) Get all search strings (file + manual)
    search_strings = get_search_strings()
    if not search_strings:
        # Message already printed in get_search_strings()
        exit(0)

    # 2) Ask for case sensitivity (default: NO → case-insensitive)
    case_sensitive = ask_yes_no(
        "Should the search be case-sensitive?",
        default=False
    )

    # 3) Ask for directory (default: NO → user must enter one)
    search_directory = choose_directory()

    print("\nSearching for the following strings:")
    for s in search_strings:
        print(f"  - {repr(s)}")
    print(f"\nCase-sensitive: {case_sensitive}")
    print(f"In directory:   {os.path.abspath(search_directory)}\n")

    # 4) Run search
    results = find_strings_in_files(
        search_strings,
        start_dir=search_directory,
        case_sensitive=case_sensitive
    )

    # 5) Show results on screen
    if results:
        print("Files containing one or more search strings:\n")
        for file_path, counts in results.items():
            print(file_path)
            for term, count in counts.items():
                print(f"    {repr(term)} : {count} occurrence(s)")
            print()
        total_files = len(results)
        total_occurrences = sum(
            sum(counts.values()) for counts in results.values()
        )
        print(f"Total files with matches: {total_files}")
        print(f"Total occurrences across all files: {total_occurrences}")
    else:
        print("No files containing the search strings were found.")

    # 6) Write results to file in search-results/
    # Use a short description based on first search string
    description = search_strings[0] if search_strings else "search"
    output_filename = make_output_filename(description)
    write_results_to_file(
        output_filename,
        search_strings,
        case_sensitive,
        search_directory,
        results
    )

    print(f"\nResults have been saved to: {output_filename}")