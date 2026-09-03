"""
User Interaction Prompts
File: prompts.py

This module contains reusable input and prompt helpers
for interactive terminal usage.

Responsibilities:
- standardized yes/no prompts with defaults
- menu selection prompts
- directory selection prompts with remembered default paths
- extension list input parsing
- validated non-negative integer input

Keeping prompts here avoids duplicating input logic
across different modes and keeps the CLI flow readable.
"""

import os


def ask_yes_no(prompt: str, default=None) -> bool:
    """
    Ask a yes/no question and return True for yes, False for no.

    If default is True or False, pressing ENTER accepts that default.
    """
    suffix = " (y/n): "

    if default is True:
        suffix = " (y/n) [y]: "
    elif default is False:
        suffix = " (y/n) [n]: "

    while True:
        ans = input(prompt + suffix).strip().lower()

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


def ask_non_negative_int(
    prompt: str,
    default: int | None = None,
) -> int:
    """
    Ask for a non-negative integer.

    Examples of valid values:
    - 0
    - 1
    - 5
    - 10

    If ``default`` is provided, pressing ENTER returns that value.
    """
    if default is not None and default < 0:
        raise ValueError(
            "default must be 0 or greater"
        )

    while True:
        if default is None:
            raw = input(
                f"{prompt}: "
            ).strip()
        else:
            raw = input(
                f"{prompt} [{default}]: "
            ).strip()

        if raw == "":
            if default is not None:
                return default

            print(
                "Please enter a whole number of 0 or greater."
            )
            continue

        try:
            value = int(raw)

        except ValueError:
            print(
                "Please enter a whole number of 0 or greater."
            )
            continue

        if value < 0:
            print(
                "Please enter a whole number of 0 or greater."
            )
            continue

        return value


def ask_menu_choice() -> int:
    """
    Ask user to choose operation.

    Returns:
    - 1: String Search
    - 2: File Statistics
    - 3: Filename Search
    """
    print("\nChoose an operation:")
    print("  1) Search for strings in files")
    print("  2) Count lines, words, and characters in files")
    print("  3) Search for files by name (patterns)")

    while True:
        choice = input(
            "\nEnter choice [1]: "
        ).strip()

        if choice == "":
            return 1

        if choice in {
            "1",
            "2",
            "3",
        }:
            return int(choice)

        print(
            "Please enter 1, 2, or 3."
        )


def choose_directory(
    action_word: str,
    default_path: str | None = None,
) -> str:
    """
    Ask which directory should be processed.

    Behavior:
    - asks whether to use the current directory, default NO
    - if a remembered default path exists, ENTER accepts it
    """
    use_current = ask_yes_no(
        f"{action_word} in the current directory where the program is?",
        default=False,
    )

    if use_current:
        return "."

    while True:
        if default_path:
            path = input(
                f"Enter full directory path to "
                f"{action_word.lower()} "
                f"[{default_path}]: "
            ).strip()

            if path == "":
                path = default_path

        else:
            path = input(
                f"Enter full directory path to "
                f"{action_word.lower()}: "
            ).strip()

        if os.path.isdir(path):
            return path

        print(
            "Invalid directory. Try again.\n"
        )


def ask_extensions_list(
    label: str,
) -> set:
    """
    Parse a comma-separated extension list.

    Leading dots are tolerated and values are normalized to lowercase.
    """
    raw = input(
        label + " "
    ).strip()

    parts = [
        p.strip().lower().lstrip(".")
        for p in raw.split(",")
        if p.strip()
    ]

    return set(parts)

# End of file prompts.py