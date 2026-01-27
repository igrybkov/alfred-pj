"""Terminal detection and launching."""

import os
import subprocess

from alfred_pj.utils import which


class Terminals:
    """Terminal detection and launching."""

    # Order determines priority
    TERMINALS = [
        {
            "name": "Ghostty",
            "check": lambda: os.path.isdir("/Applications/Ghostty.app") or bool(which("ghostty")),
            "open": lambda path: subprocess.run(
                ["ghostty", f"--working-directory={path}"],
                env={
                    **os.environ,
                    "PATH": f"/Applications/Ghostty.app/Contents/MacOS:{os.environ.get('PATH', '')}",
                },
            ),
        },
        {
            "name": "WezTerm",
            "check": lambda: os.path.isdir("/Applications/WezTerm.app") or bool(which("wezterm")),
            "open": lambda path: subprocess.run(["wezterm", "cli", "spawn", "--cwd", path]),
        },
        {
            "name": "iTerm",
            "check": lambda: os.path.isdir("/Applications/iTerm.app"),
            "open": lambda path: subprocess.run(
                [
                    "osascript",
                    "-e",
                    f"""
                tell application "iTerm"
                    tell current window
                        create tab with default profile
                        tell current session
                            write text "cd {path!r}"
                        end tell
                    end tell
                end tell
            """,
                ]
            ),
        },
        {
            "name": "Terminal",
            "check": lambda: True,  # Always available on macOS
            "open": lambda path: subprocess.run(
                [
                    "osascript",
                    "-e",
                    f"""
                tell application "Terminal"
                    activate
                    do script "cd {path!r}"
                end tell
            """,
                ]
            ),
        },
    ]

    @classmethod
    def get_available_terminal(cls):
        """Return the first available terminal."""
        for terminal in cls.TERMINALS:
            if terminal["check"]():
                return terminal
        return cls.TERMINALS[-1]  # Fallback to Terminal.app
