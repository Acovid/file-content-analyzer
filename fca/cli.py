"""
CLI Orchestration for File Content Analyzer

This module coordinates the overall program flow:
- parses command-line arguments
- loads and optionally edits persistent configuration
- prompts the user for missing inputs
- selects the operation mode (search or statistics)
- dispatches execution to the appropriate mode module

This is the central "controller" of the application.
It does not implement file traversal or analysis itself.
"""

import argparse
from fca.prompts import ask_yes_no, ask_menu_choice, choose_directory, ask_extensions_list
from fca.config import (
    load_config, save_config, normalize_ext_list,
    merged_excluded_dirs, excluded_extensions, included_extensions
)
from fca.search_mode import run as run_search
from fca.stats_mode import run as run_stats
from fca.reporting import PROGRAM_NAME, PROGRAM_VERSION


def edit_config_interactive(cfg: dict):
    print("\nEditing configuration\n")

    ex = cfg.get("excluded_extensions", [])
    inc = cfg.get("included_extensions", [])

    print("Current excluded extensions:", ", ".join(ex) or "(none)")
    if ask_yes_no("Edit excluded extensions?", default=False):
        new_ex = ask_extensions_list("Enter extensions to EXCLUDE (comma-separated):")
        cfg["excluded_extensions"] = normalize_ext_list(list(new_ex))

    print("\nCurrent included extensions:", ", ".join(inc) or "(all)")
    if ask_yes_no("Edit included extensions?", default=False):
        new_inc = ask_extensions_list("Enter extensions to INCLUDE ONLY (comma-separated, empty = all):")
        cfg["included_extensions"] = normalize_ext_list(list(new_inc))

    if "excluded_dirs" not in cfg:
        cfg["excluded_dirs"] = sorted(list(merged_excluded_dirs(cfg)))

    print("\nConfiguration saved.\n")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--search", action="store_true", help="Run string search mode")
    p.add_argument("--stats", action="store_true", help="Run file statistics mode")
    p.add_argument("--dir", help="Directory to analyze/search")
    p.add_argument("--case-sensitive", action="store_true", help="Case-sensitive string search")
    p.add_argument("--include", help="Include only these extensions (comma-separated, no dots)")
    p.add_argument("--exclude", help="Exclude these extensions (comma-separated, no dots)")
    p.add_argument("--no-config", action="store_true", help="Ignore config.json and do not write it")
    p.add_argument("--edit-config", action="store_true", help="Edit config interactively and exit")
    return p.parse_args()


def main():
    entry_file = __file__.replace("fca/cli.py", "file_content_analyzer.py")
    # The line above works when run via entrypoint. If it ever fails, we’ll still have config fallback.
    # More robust path:
    import os
    entry_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "file_content_analyzer.py")

    print(f"\n{PROGRAM_NAME} v{PROGRAM_VERSION}")
    print("=" * (len(PROGRAM_NAME) + len(PROGRAM_VERSION) + 3))

    args = parse_args()

    cfg = {} if args.no_config else load_config(entry_file)

    # Ensure excluded_dirs exists in cfg
    if "excluded_dirs" not in cfg:
        cfg["excluded_dirs"] = sorted(list(merged_excluded_dirs(cfg)))

    if args.edit_config:
        edit_config_interactive(cfg)
        if not args.no_config:
            save_config(entry_file, cfg)
        return

    if ask_yes_no("Edit configuration?", default=False):
        edit_config_interactive(cfg)
        if not args.no_config:
            save_config(entry_file, cfg)

    # CLI overrides (one-run; we also persist unless --no-config)
    if args.include is not None:
        cfg["included_extensions"] = normalize_ext_list(args.include.split(","))
    if args.exclude is not None:
        cfg["excluded_extensions"] = normalize_ext_list(args.exclude.split(","))

    if not args.no_config:
        save_config(entry_file, cfg)

    excluded_dirs = set(cfg.get("excluded_dirs", []))
    excluded_exts = excluded_extensions(cfg)
    included_exts = included_extensions(cfg)

    # Determine mode
    if args.search:
        mode = 1
    elif args.stats:
        mode = 2
    else:
        mode = ask_menu_choice()

    # Directory
    directory = args.dir or choose_directory("Search" if mode == 1 else "Analyze")

    if mode == 1:
        case_sensitive = args.case_sensitive or ask_yes_no("Case-sensitive search?", default=False)
        out = run_search(
            entry_file=entry_file,
            cfg=cfg,
            directory=directory,
            case_sensitive=case_sensitive,
            excluded_dirs=excluded_dirs,
            excluded_exts=excluded_exts,
            included_exts=included_exts
        )
    else:
        out = run_stats(
            entry_file=entry_file,
            directory=directory,
            excluded_dirs=excluded_dirs,
            excluded_exts=excluded_exts,
            included_exts=included_exts
        )

    if out:
        print("\nResults saved to:")
        print(out)
    print("\nDone.")