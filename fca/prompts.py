"""
User Interaction Prompts

This module contains reusable input and prompt helpers
for interactive terminal usage.

Responsibilities:
- standardized yes/no prompts with defaults
- menu selection prompts
- directory selection prompts
- extension list input parsing

Keeping prompts here avoids duplicating input logic
across different modes and keeps the CLI flow readable.
"""

import os


def ask_yes_no(prompt: str, default=None) -> bool:
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


def ask_menu_choice() -> int:
    print("\nChoose an operation:")
    print("  1) Search for strings in files")
    print("  2) Count lines, words, and characters in files")
    while True:
        choice = input("\nEnter choice [1]: ").strip()
        if choice == "":
            return 1
        if choice in {"1", "2"}:
            return int(choice)
        print("Please enter 1 or 2.")


def choose_directory(action_word: str) -> str:
    use_current = ask_yes_no(
        f"{action_word} in the current directory where the program is?",
        default=False
    )
    if use_current:
        return "."

    while True:
        path = input(f"Enter full directory path to {action_word.lower()}: ").strip()
        if os.path.isdir(path):
            return path
        print("Invalid directory. Try again.\n")


def ask_extensions_list(label: str) -> set:
    raw = input(label + " ").strip()
    parts = [p.strip().lower().lstrip(".") for p in raw.split(",") if p.strip()]
    return set(parts)