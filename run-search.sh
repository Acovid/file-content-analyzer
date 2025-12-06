#!/bin/bash

# Absolute path to your project
PROJECT_DIR="/Users/aco/Development/myPrograms/Python/python-search-tool"

# Go to project directory
cd "$PROJECT_DIR" || exit 1

# Ensure the script is executable (harmless if run repeatedly)
chmod +x search_string.py 2>/dev/null || true

# Run the script using the virtualenv Python
"$PROJECT_DIR/.venv/bin/python" search_string.py