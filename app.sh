#!/bin/bash

# Wrapper script to run alfred-pj with uv-managed environment

set -e

# Ensure ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    export PATH="$HOME/.local/bin:$PATH"
fi

# Check if uv is available, install if not
if ! command -v uv &> /dev/null; then
    echo "uv not found, installing to ~/.local/bin..." >&2
    mkdir -p "$HOME/.local/bin"
    curl -LsSf https://astral.sh/uv/install.sh | sh -s -- --no-modify-path
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Sync dependencies
uv sync --project "$SCRIPT_DIR"

# Run the application
uv run --project "$SCRIPT_DIR" alfred-pj "$@"
