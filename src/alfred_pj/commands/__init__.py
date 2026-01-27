"""CLI commands for alfred-pj."""

from alfred_pj.commands.clear_cache import clear_cache
from alfred_pj.commands.clear_usage import clear_usage
from alfred_pj.commands.debug import debug
from alfred_pj.commands.editor import editor
from alfred_pj.commands.list import list
from alfred_pj.commands.open_finder import open_finder
from alfred_pj.commands.open_github import open_github
from alfred_pj.commands.open_project import open_project
from alfred_pj.commands.open_terminal import open_terminal
from alfred_pj.commands.open_vscode import open_vscode
from alfred_pj.commands.record_selection import record_selection

__all__ = [
    "clear_cache",
    "clear_usage",
    "debug",
    "editor",
    "list",
    "open_finder",
    "open_github",
    "open_project",
    "open_terminal",
    "open_vscode",
    "record_selection",
]
