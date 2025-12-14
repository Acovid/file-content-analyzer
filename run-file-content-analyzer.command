#!/bin/bash

# Resolve alias/symlink to find the real script folder
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

# Prefer the venv Python if available, fallback to system python3
if [ -x "$PROJECT_DIR/.venv/bin/python" ]; then
  PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"
else
  PYTHON_BIN="python3"
fi

# 1) Set a custom Terminal window title (tab title)
printf '\033]0;Python Search Tool\007'

# 2) Welcome banner
echo
echo "-------------------------------------------"
echo "  Python Multi-String Search Tool"
echo "-------------------------------------------"
echo " Project directory:"
echo "   $PROJECT_DIR"
echo
echo " This tool will:"
echo "   - Load search strings from 'search-strings.txt' (if present)"
echo "   - Optionally let you add more search strings"
echo "   - Search recursively in the directory you choose"
echo "   - Save a detailed report into 'search-results/'"
echo "-------------------------------------------"
echo

# Ensure the Python process runs with the project directory as CWD
cd "$PROJECT_DIR" || exit 1

# 3) Run the main Python script
"$PYTHON_BIN" "$PROJECT_DIR/file_content_analyzer.py"
STATUS=$?

# 4) Closing summary
echo
echo "-------------------------------------------"
if [ $STATUS -eq 0 ]; then
  echo " Search finished."
else
  echo " Search finished with exit status: $STATUS"
fi
echo " You can scroll up to review the details above."
echo " The last line from the Python tool shows"
echo " where the results file was saved in 'search-results/'."
echo "-------------------------------------------"
echo

# 5) Keep window open and let user close it explicitly
read -r -p "Press ENTER to close this window..." _