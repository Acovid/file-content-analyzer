#!/bin/bash
#
# File Content Analyzer Launcher (macOS)
#
# This script serves as a clickable launcher for macOS.
#
# Responsibilities:
# - resolve its own real location (handles aliases/symlinks)
# - determine the project directory
# - prefer Python from the local virtual environment if present
# - fall back to system python otherwise
# - open a visible Terminal window
# - execute file_content_analyzer.py
# - keep the Terminal open until the user closes it
#
# This allows the tool to be used like a lightweight desktop app.

SCRIPT_PATH="$0"
while [ -L "$SCRIPT_PATH" ]; do
  TARGET="$(readlink "$SCRIPT_PATH")"
  if [[ "$TARGET" == /* ]]; then
    SCRIPT_PATH="$TARGET"
  else
    SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
    SCRIPT_PATH="$SCRIPT_DIR/$TARGET"
  fi
done

PROJECT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"

if [ -x "$PROJECT_DIR/.venv/bin/python" ]; then
  PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"
else
  PYTHON_BIN="python3"
fi

printf '\033]0;File Content Analyzer\007'

echo
echo "-------------------------------------------"
echo "  File Content Analyzer"
echo "-------------------------------------------"
echo " Project directory:"
echo "   $PROJECT_DIR"
echo
echo " Reports folder:"
echo "   $PROJECT_DIR/analysis-results"
echo "-------------------------------------------"
echo

"$PYTHON_BIN" "$PROJECT_DIR/file_content_analyzer.py"
STATUS=$?

echo
echo "-------------------------------------------"
if [ $STATUS -eq 0 ]; then
  echo " Finished successfully."
else
  echo " Finished with exit status: $STATUS"
fi
echo "-------------------------------------------"
echo
read -r -p "Press ENTER to close this window..." _