"""
Configuration Handling

This module manages persistent configuration stored in `config.json`.

Responsibilities:
- load configuration from disk
- save configuration back to disk
- provide normalized access to include/exclude extension lists
- merge user configuration with built-in defaults
- centralize configuration-related logic

The goal is to keep configuration concerns isolated from
business logic and user interaction.
"""

import json
import os

CONFIG_FILENAME = "config.json"
DEFAULT_EXCLUDE_DIRS = {".venv", ".vscode"}


def script_dir(entry_file: str) -> str:
    return os.path.dirname(os.path.abspath(entry_file))


def config_path(entry_file: str) -> str:
    return os.path.join(script_dir(entry_file), CONFIG_FILENAME)


def load_config(entry_file: str) -> dict:
    path = config_path(entry_file)
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(entry_file: str, cfg: dict) -> None:
    path = config_path(entry_file)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def normalize_ext_list(values) -> list:
    cleaned = {v.strip().lower().lstrip(".") for v in values if v and v.strip()}
    return sorted(cleaned)


def merged_excluded_dirs(cfg: dict) -> set:
    dirs = cfg.get("excluded_dirs", None)
    if isinstance(dirs, list):
        return set(dirs)
    return set(DEFAULT_EXCLUDE_DIRS)


def excluded_extensions(cfg: dict) -> set:
    ex = cfg.get("excluded_extensions", [])
    return set(ex) if isinstance(ex, list) else set()


def included_extensions(cfg: dict) -> set:
    inc = cfg.get("included_extensions", [])
    return set(inc) if isinstance(inc, list) else set()