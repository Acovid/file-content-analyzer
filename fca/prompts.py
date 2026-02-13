"""
User Interaction Prompts
File: prompts.py

This module contains reusable input and prompt helpers
for interactive terminal usage.

Responsibilities:
- standardized yes/no prompts with defaults
- menu selection prompts
- directory selection prompts (supports a remembered default path)
- extension list input parsing

Keeping prompts here avoids duplicating input logic
across different modes and keeps the CLI flow readable.
"""

import os


def ask_yes_no(prompt: str, default=None) -> bool:
    """
    Ask a yes/no question and return True for yes, False for no.

    Args:
        prompt: The question to show (without the "(y/n)" suffix).
        default: True/False/None. If True, ENTER means yes. If False, ENTER means no.
                 If None, the user must type y/n.

    Returns:
        bool: True for yes, False for no.
    """
    suffix = " (y/n): "
    if default is True:
        suffix = " (y/n) [y]: "
    elif default is False:
        suffix = " (y/n) [n]: "

    while True:
        ans = input(prompt + suffix).strip().lower()

        # ENTER selects default, if provided
        if ans == "":
            if default is not None:
                return default
            print("Please answer y or n.")
            continue

        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False

        print("Please answer y or n.")


def ask_menu_choice() -> int:
    """
    Ask the user to choose which operation mode to run.

    Returns:
        int: 1 (string search), 2 (file stats), 3 (filename search).
    """
    print("\nChoose an operation:")
    print("  1) Search for strings in files")
    print("  2) Count lines, words, and characters in files")
    print("  3) Search for files by name (patterns)")

    while True:
        choice = input("\nEnter choice [1]: ").strip()
        if choice == "":
            return 1
        if choice in {"1", "2", "3"}:
            return int(choice)
        print("Please enter 1, 2, or 3.")


def choose_directory(action_word: str, default_path: str | None = None) -> str:
    """
    Ask the user which directory should be processed.

    Behavior:
    - First asks if the user wants to use the current directory (default: NO).
    - If not using current directory:
      - If default_path is provided, ENTER accepts it.
      - Otherwise, user must type a valid path.

    Args:
        action_word: Short word used in prompts (e.g., "Search", "Analyze").
        default_path: Optional remembered directory path (from config.json).

    Returns:
        str: "." for current directory or a validated full directory path.
    """
    use_current = ask_yes_no(
        f"{action_word} in the current directory where the program is?",
        default=False
    )
    if use_current:
        return "."

    while True:
        if default_path:
            path = input(
                f"Enter full directory path to {action_word.lower()} [{default_path}]: "
            ).strip()
            if path == "":
                path = default_path
        else:
            path = input(
                f"Enter full directory path to {action_word.lower()}: "
            ).strip()

        if os.path.isdir(path):
            return path

        print("Invalid directory. Try again.\n")


def ask_extensions_list(label: str) -> set:
    """
    Ask the user for a comma-separated list of file extensions.

    Notes:
    - Extensions should be provided without dots (but dots are tolerated).
    - Returns a set of normalized extensions in lowercase.

    Example input:
        "py, txt, .js"

    Returns:
        set[str]: {"py", "txt", "js"}
    """
    raw = input(label + " ").strip()
    parts = [p.strip().lower().lstrip(".") for p in raw.split(",") if p.strip()]
    return set(parts)


# End of file prompts.py