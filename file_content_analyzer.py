"""
File Content Analyzer — Main Entry Point

This file is the minimal entrypoint for the File Content Analyzer application.

Its sole responsibility is to delegate execution to the CLI layer
implemented in the `fca` package.

Keeping this file small allows:
- clean separation between entrypoint and logic
- easier testing
- easier reuse as a module or future packaging as a CLI tool

All real functionality lives in:
    fca/cli.py
"""

from fca.cli import main

if __name__ == "__main__":
    main()