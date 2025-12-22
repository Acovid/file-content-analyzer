# Changelog

All notable changes to this project will be documented in this file.

The project follows a simplified semantic versioning scheme:
- MAJOR version for new capabilities or structural changes
- MINOR version for enhancements
- PATCH version for fixes

---

## [3.1.0] - 2025-12-15

### Added

- New **Filename Search** mode:
  - Search for files by exact name or glob-style patterns
  - Supports batch input via `file-names.txt`
  - Supports interactive manual input
  - Case-sensitive or case-insensitive matching
  - Generates dedicated name-search reports under `analysis-results/`
- New CLI flag `--names` to run filename search mode non-interactively
- New module `fca/name_search_mode.py`
- Updated README to document filename search functionality
- Clarified interaction between filename search and extension filters

---

## [3.0.0] - 2025-12-14

### Changed

- Renamed entry script to `file_content_analyzer.py`
- Renamed output folder from `search-results` to `analysis-results`
- Refactored codebase into modular architecture under `fca/`
- Renamed macOS launcher to `run-file-content-analyzer.command`

### Added

- Per-extension totals in file statistics reports
- Unit test scaffold using built-in `unittest`
- Persistent configuration via `config.json`
- Interactive configuration editor
- Updated README to reflect new structure and naming

---

## [2.x] - Earlier

### Added

- File statistics mode (lines, words, characters)
- Include-only and exclude file extension filtering
- Persistent configuration file (`config.json`)
- Interactive prompts and CLI flags
- Case-sensitive and case-insensitive string search
- Excluded directory handling (`.venv`, `.vscode`, etc.)

---

## [1.x] - Initial versions

- Recursive string search across directory trees
- Single search string support
- Basic console output