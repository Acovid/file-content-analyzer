"""
CLI Orchestration for File Content Analyzer
File: cli.py

This module coordinates the overall program flow:

- Parses command-line arguments (optional non-interactive usage)
- Loads and optionally edits persistent configuration (config.json)
- Prompts the user for any missing inputs (interactive usage)
- Selects the operation mode:
    1) String search
    2) File statistics
    3) Filename/pattern search
- Dispatches execution to the appropriate mode module

Design notes:
- This module is the "controller" / orchestrator.
- It does not implement traversal, searching, or report formatting itself.
- It remembers the last-used directory by writing it into config.json
  as `default_directory` (unless --no-config is used).
- String Search can optionally generate Detailed/Context reports.
"""

import argparse
import os

from fca.prompts import (
    ask_yes_no,
    ask_menu_choice,
    choose_directory,
    ask_extensions_list,
    ask_non_negative_int,
)
from fca.config import (
    load_config,
    save_config,
    normalize_ext_list,
    merged_excluded_dirs,
    excluded_extensions,
    included_extensions,
    default_directory,
)
from fca.search_mode import run as run_search
from fca.stats_mode import run as run_stats
from fca.name_search_mode import run as run_name_search
from fca.reporting import PROGRAM_NAME, PROGRAM_VERSION


def edit_config_interactive(cfg: dict) -> None:
    """
    Interactive editor for config.json values that are safe and common to edit.

    Currently supports:
    - excluded_extensions
    - included_extensions

    Note:
    - excluded_dirs is ensured to exist (defaults are applied if missing).
    - default_directory is auto-managed by the program (last-used directory),
      so we do not prompt for it here by default.
    """
    print("\nEditing configuration\n")

    ex = cfg.get("excluded_extensions", [])
    inc = cfg.get("included_extensions", [])

    print("Current excluded extensions:", ", ".join(ex) or "(none)")
    if ask_yes_no("Edit excluded extensions?", default=False):
        new_ex = ask_extensions_list(
            "Enter extensions to EXCLUDE (comma-separated):"
        )
        cfg["excluded_extensions"] = normalize_ext_list(
            list(new_ex)
        )

    print(
        "\nCurrent included extensions:",
        ", ".join(inc) or "(all)",
    )

    if ask_yes_no(
        "Edit included extensions?",
        default=False,
    ):
        new_inc = ask_extensions_list(
            "Enter extensions to INCLUDE ONLY "
            "(comma-separated, empty = all):"
        )
        cfg["included_extensions"] = normalize_ext_list(
            list(new_inc)
        )

    # Ensure excluded_dirs exists (use defaults if missing)
    if "excluded_dirs" not in cfg:
        cfg["excluded_dirs"] = sorted(
            list(
                merged_excluded_dirs(cfg)
            )
        )

    print("\nConfiguration saved.\n")


def parse_args():
    """
    Parse optional command-line arguments.

    If a mode flag is provided, the tool can run with fewer prompts.
    If flags are not provided, the tool uses interactive prompts.
    """
    p = argparse.ArgumentParser()

    p.add_argument(
        "--search",
        action="store_true",
        help="Run string search mode",
    )

    p.add_argument(
        "--stats",
        action="store_true",
        help="Run file statistics mode",
    )

    p.add_argument(
        "--names",
        action="store_true",
        help="Run filename search mode",
    )

    p.add_argument(
        "--dir",
        help="Directory to analyze/search",
    )

    p.add_argument(
        "--case-sensitive",
        action="store_true",
        help="Case-sensitive string search",
    )

    p.add_argument(
        "--detailed",
        action="store_true",
        help="Include detailed match context in String Search report",
    )

    p.add_argument(
        "--context-lines",
        type=int,
        help=(
            "Number of context lines before and after each "
            "String Search match (default: 5)"
        ),
    )

    p.add_argument(
        "--include",
        help=(
            "Include only these extensions "
            "(comma-separated, no dots)"
        ),
    )

    p.add_argument(
        "--exclude",
        help=(
            "Exclude these extensions "
            "(comma-separated, no dots)"
        ),
    )

    p.add_argument(
        "--no-config",
        action="store_true",
        help="Ignore config.json and do not write it",
    )

    p.add_argument(
        "--edit-config",
        action="store_true",
        help="Edit config interactively and exit",
    )

    return p.parse_args()


def main() -> None:
    """
    Main program entry for CLI orchestration.

    Responsibilities:
    - Resolve entry_file path
    - Load config and apply defaults
    - Optionally edit config interactively
    - Determine mode and directory
    - Determine String Search report detail when applicable
    - Dispatch to the selected mode
    - Remember the last-used directory in config.json
    """
    # Resolve the main entry file path from the package directory.
    entry_file = os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        ),
        "file_content_analyzer.py",
    )

    # Startup banner
    print(
        f"\n{PROGRAM_NAME} v{PROGRAM_VERSION}"
    )

    print(
        "="
        * (
            len(PROGRAM_NAME)
            + len(PROGRAM_VERSION)
            + 3
        )
    )

    args = parse_args()

    # Validate --context-lines early.
    if (
        args.context_lines is not None
        and args.context_lines < 0
    ):
        raise SystemExit(
            "--context-lines must be 0 or greater."
        )

    # Load configuration unless explicitly disabled.
    cfg = (
        {}
        if args.no_config
        else load_config(entry_file)
    )

    # Ensure excluded_dirs exists in cfg.
    if "excluded_dirs" not in cfg:
        cfg["excluded_dirs"] = sorted(
            list(
                merged_excluded_dirs(cfg)
            )
        )

    # Ensure exclude_hidden_dirs exists in cfg.
    if "exclude_hidden_dirs" not in cfg:
        cfg["exclude_hidden_dirs"] = False

    # One-shot mode: edit config and exit.
    if args.edit_config:
        edit_config_interactive(cfg)

        if not args.no_config:
            save_config(
                entry_file,
                cfg,
            )

        return

    # Optional runtime config editing.
    if ask_yes_no(
        "Edit configuration?",
        default=False,
    ):
        edit_config_interactive(cfg)

        if not args.no_config:
            save_config(
                entry_file,
                cfg,
            )

    # CLI extension overrides.
    if args.include is not None:
        cfg["included_extensions"] = normalize_ext_list(
            args.include.split(",")
        )

    if args.exclude is not None:
        cfg["excluded_extensions"] = normalize_ext_list(
            args.exclude.split(",")
        )

    if not args.no_config:
        save_config(
            entry_file,
            cfg,
        )

    # Prepare traversal filters.
    excluded_dirs = set(
        cfg.get(
            "excluded_dirs",
            [],
        )
    )

    excluded_exts = excluded_extensions(
        cfg
    )

    included_exts = included_extensions(
        cfg
    )

    exclude_hidden_dirs = cfg.get(
        "exclude_hidden_dirs",
        False,
    )

    # Determine operation mode.
    if args.search:
        mode = 1
    elif args.stats:
        mode = 2
    elif args.names:
        mode = 3
    else:
        mode = ask_menu_choice()

    # Choose target directory.
    cfg_default_dir = default_directory(
        cfg
    )

    directory = (
        args.dir
        or choose_directory(
            (
                "Search"
                if mode in (1, 3)
                else "Analyze"
            ),
            default_path=cfg_default_dir,
        )
    )

    # Remember last-used directory.
    if not args.no_config:
        abs_dir = os.path.abspath(
            directory
        )

        if os.path.isdir(abs_dir):
            cfg["default_directory"] = abs_dir

            save_config(
                entry_file,
                cfg,
            )

    # Dispatch to selected mode.
    if mode == 1:
        case_sensitive = (
            args.case_sensitive
            or ask_yes_no(
                "Case-sensitive search?",
                default=False,
            )
        )

        # If --detailed was supplied, do not ask again.
        # Otherwise, interactive mode asks whether context should be included.
        if args.detailed:
            detailed = True
        else:
            detailed = ask_yes_no(
                "Include detailed match context?",
                default=False,
            )

        if detailed:
            if args.context_lines is not None:
                context_lines = args.context_lines
            else:
                context_lines = ask_non_negative_int(
                    "Context lines before/after",
                    default=5,
                )
        else:
            # This value is ignored by Summary reporting, but using the
            # normal default keeps the function call explicit and stable.
            context_lines = 5

        out = run_search(
            entry_file=entry_file,
            cfg=cfg,
            directory=directory,
            case_sensitive=case_sensitive,
            excluded_dirs=excluded_dirs,
            excluded_exts=excluded_exts,
            included_exts=included_exts,
            exclude_hidden_dirs=exclude_hidden_dirs,
            detailed=detailed,
            context_lines=context_lines,
        )

    elif mode == 2:
        out = run_stats(
            entry_file=entry_file,
            directory=directory,
            excluded_dirs=excluded_dirs,
            excluded_exts=excluded_exts,
            included_exts=included_exts,
            exclude_hidden_dirs=exclude_hidden_dirs,
        )

    else:
        out = run_name_search(
            entry_file=entry_file,
            directory=directory,
            excluded_dirs=excluded_dirs,
            excluded_exts=excluded_exts,
            included_exts=included_exts,
            exclude_hidden_dirs=exclude_hidden_dirs,
        )

    # Mode functions already create the output report.
    _ = out

# End of file cli.py