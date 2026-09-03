# Changelog

All notable changes to this project will be documented in this file.

The project follows a simplified semantic versioning scheme:
- MAJOR version for new capabilities or structural changes
- MINOR version for enhancements
- PATCH version for fixes

---

## [3.2.0] - 2026-09-03

### Added

- New **Detailed Match Context** option for String Search
- Detailed reports now show:
  - full matching file paths
  - exact source line numbers
  - complete matching source lines
  - configurable numbers of context lines before and after matches
  - explicit `MATCH:` annotations for every occurrence
  - one-based match column ranges
- Configurable context size with a default of 5 lines before and after each match
- Support for zero context lines to display matching lines only
- Automatic merging of overlapping context windows
- Automatic merging of directly adjacent context windows
- Long/minified-line protection:
  - oversized matching lines are reduced to focused character excerpts
  - the complete matched search string remains visible
  - truncation is explicitly indicated
  - distant matches on the same oversized line can produce separate focused excerpts
- New interactive prompt:
  - `Include detailed match context?`
- New validated non-negative integer prompt for context-line selection
- New CLI flag `--detailed`
- New CLI option `--context-lines`
- Match-position collection including:
  - absolute character offsets
  - source line number
  - starting column
  - ending column
- New String Search unit tests covering match positions, context construction, context merging, detailed report generation, and long-line handling

### Changed

- String Search can now generate either:
  - the existing compact Summary report
  - a Summary report followed by Detailed Match Context
- Existing String Search occurrence-count semantics are preserved
- Nearby matching lines are grouped into consolidated source excerpts to reduce duplicated context
- Hidden-directory exclusion is now applied consistently across:
  - String Search
  - File Statistics
  - Filename Search
- README expanded to document Detailed Match Context reporting, context behavior, long-line handling, CLI options, directory filtering, and the expanded test suite

### Fixed

- Fixed inconsistent handling of `exclude_hidden_dirs`, which previously affected File Statistics but was not propagated to String Search and Filename Search
- Resolved program-version metadata mismatch by advancing the application version to 3.2.0

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