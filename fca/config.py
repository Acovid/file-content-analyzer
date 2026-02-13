"""
Configuration Handling
File: config.py

This module manages persistent configuration stored in `config.json`.

Responsibilities:
- load configuration from disk (and handle missing/invalid files safely)
- save configuration back to disk
- provide normalized access to include/exclude extension lists
- merge user configuration with built-in defaults (e.g., excluded dirs)
- provide accessors for commonly used settings (e.g., default_directory)

The goal is to keep configuration concerns isolated from
business logic and user interaction.
"""

import json
import os
from typing import Any


CONFIG_FILENAME = "config.json"
DEFAULT_EXCLUDE_DIRS = {".venv", ".vscode"}


def script_dir(entry_file: str) -> str:
    """Return the directory where the main entry script resides."""
    return os.path.dirname(os.path.abspath(entry_file))


def config_path(entry_file: str) -> str:
    """Return the full path to config.json stored next to the entry script."""
    return os.path.join(script_dir(entry_file), CONFIG_FILENAME)


def load_config(entry_file: str) -> dict:
    """
    Load config.json if present.

    Returns an empty dict if:
    - the file does not exist
    - the file is unreadable
    - the file contains invalid JSON
    """
    path = config_path(entry_file)
    if not os.path.isfile(path):
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_config(entry_file: str, cfg: dict) -> None:
    """
    Save the configuration to config.json next to the entry script.

    Writes pretty-printed JSON with 2-space indentation.
    """
    path = config_path(entry_file)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def normalize_ext_list(values: Any) -> list:
    """
    Normalize a list of file extensions:
    - strips whitespace
    - lowercases
    - removes a leading dot
    - removes empty entries
    - returns a sorted list of unique extensions

    Example:
        [".Py", " txt ", "JS", "js"] -> ["js", "py", "txt"]
    """
    if not isinstance(values, (list, tuple, set)):
        return []

    cleaned = {str(v).strip().lower().lstrip(".") for v in values if str(v).strip()}
    cleaned.discard("")  # just in case
    return sorted(cleaned)


def merged_excluded_dirs(cfg: dict) -> set:
    """
    Return the directory names to exclude during traversal.
    Uses config.json if present, otherwise falls back to defaults.
    """
    dirs = cfg.get("excluded_dirs")
    if isinstance(dirs, list) and dirs:
        return set(dirs)
    return set(DEFAULT_EXCLUDE_DIRS)


def excluded_extensions(cfg: dict) -> set:
    """
    Return the set of excluded extensions (no dots), normalized.
    """
    ex = cfg.get("excluded_extensions", [])
    return set(normalize_ext_list(ex))


def included_extensions(cfg: dict) -> set:
    """
    Return the set of included extensions (no dots), normalized.
    If non-empty, only these extensions will be processed.
    """
    inc = cfg.get("included_extensions", [])
    return set(normalize_ext_list(inc))


def default_directory(cfg: dict) -> str | None:
    """
    Return the default directory to analyze/search, if configured.

    If present, `default_directory` can be used to avoid re-typing a long path.
    The CLI should still allow overrides via --dir or manual input.

    Returns:
        A non-empty string path, or None if not set/invalid.
    """
    val = cfg.get("default_directory")
    if isinstance(val, str):
        val = val.strip()
        if val:
            return val
    return None
  
# End of file config.py