"""Utility functions and logging configuration."""

import logging
import os
import sys
from pathlib import Path
from shutil import which as system_which

# Fallback paths to search if command not found in system PATH
FALLBACK_SEARCH_PATHS = [
    "/opt/homebrew/bin",
    "/opt/homebrew/sbin",
    "/usr/local/bin",
    Path.home() / ".local/bin",
]


def which(cmd: str) -> str | None:
    """Find command in PATH, falling back to common install locations."""
    # Try system PATH first
    if result := system_which(cmd):
        return result

    # Fall back to common paths (useful when Alfred has limited PATH)
    for directory in FALLBACK_SEARCH_PATHS:
        cmd_path = Path(directory) / cmd
        if cmd_path.is_file() and os.access(cmd_path, os.X_OK):
            return str(cmd_path)

    return None


class Logger(logging.Logger):
    def __init__(self, name):
        super().__init__(name)
        self.addHandler(logging.StreamHandler(sys.stderr))
        # alfred_debug is set by Alfred in lowercase
        self.setLevel(logging.DEBUG if os.environ.get("alfred_debug") == "1" else logging.INFO)
        self.log(logging.INFO, "logger initiated")


logging.basicConfig(level=logging.DEBUG, format="[%(levelname)] %(message)s")
logger = Logger(__name__)
