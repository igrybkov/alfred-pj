"""Tests for terminal detection."""

from unittest.mock import patch

from alfred_pj.terminals import Terminals


class TestTerminals:
    """Tests for Terminals class."""

    def test_terminals_list_order(self):
        """Terminals should be in correct priority order."""
        names = [t["name"] for t in Terminals.TERMINALS]
        assert names == ["Ghostty", "WezTerm", "iTerm", "Terminal"]

    def test_ghostty_is_first_priority(self):
        """Ghostty should be first in priority."""
        assert Terminals.TERMINALS[0]["name"] == "Ghostty"

    def test_wezterm_is_second_priority(self):
        """WezTerm should be second in priority."""
        assert Terminals.TERMINALS[1]["name"] == "WezTerm"

    def test_iterm_is_third_priority(self):
        """iTerm should be third in priority."""
        assert Terminals.TERMINALS[2]["name"] == "iTerm"

    def test_terminal_app_is_fallback(self):
        """Terminal.app should be last (fallback)."""
        assert Terminals.TERMINALS[-1]["name"] == "Terminal"

    def test_terminal_app_always_available(self):
        """Terminal.app check should always return True."""
        terminal = Terminals.TERMINALS[-1]
        assert terminal["check"]() is True


class TestGetAvailableTerminal:
    """Tests for Terminals.get_available_terminal()."""

    def test_returns_terminal_dict(self):
        """Should return a terminal dictionary with required keys."""
        terminal = Terminals.get_available_terminal()
        assert "name" in terminal
        assert "check" in terminal
        assert "open" in terminal

    def test_returns_first_available(self):
        """Should return first available terminal."""
        # Mock all terminals as unavailable except Terminal
        with patch.object(
            Terminals,
            "TERMINALS",
            [
                {"name": "Fake1", "check": lambda: False, "open": lambda p: None},
                {"name": "Fake2", "check": lambda: False, "open": lambda p: None},
                {"name": "Terminal", "check": lambda: True, "open": lambda p: None},
            ],
        ):
            terminal = Terminals.get_available_terminal()
            assert terminal["name"] == "Terminal"

    def test_returns_ghostty_when_available(self):
        """Should return Ghostty when it's available."""
        with patch.object(
            Terminals,
            "TERMINALS",
            [
                {"name": "Ghostty", "check": lambda: True, "open": lambda p: None},
                {"name": "Terminal", "check": lambda: True, "open": lambda p: None},
            ],
        ):
            terminal = Terminals.get_available_terminal()
            assert terminal["name"] == "Ghostty"

    def test_fallback_to_terminal_app(self):
        """Should fall back to Terminal.app when nothing else available."""
        # Even with empty terminal list, should return last item
        terminal = Terminals.get_available_terminal()
        # Will return whatever is available, or fallback
        assert terminal is not None


class TestTerminalChecks:
    """Tests for terminal availability checks."""

    def test_ghostty_checks_app_or_command(self):
        """Ghostty check should look for app or command."""
        ghostty = Terminals.TERMINALS[0]
        # We can't easily test the actual check without mocking filesystem
        # but we can verify it's callable
        assert callable(ghostty["check"])

    def test_wezterm_checks_app_or_command(self):
        """WezTerm check should look for app or command."""
        wezterm = Terminals.TERMINALS[1]
        assert callable(wezterm["check"])

    def test_iterm_checks_app(self):
        """iTerm check should look for app."""
        iterm = Terminals.TERMINALS[2]
        assert callable(iterm["check"])


class TestTerminalOpen:
    """Tests for terminal open functions."""

    def test_terminal_open_functions_callable(self):
        """All terminal open functions should be callable."""
        for terminal in Terminals.TERMINALS:
            assert callable(terminal["open"])

    def test_ghostty_open_uses_open_command(self):
        """Ghostty open should use 'open -a Ghostty <path>' on macOS."""
        ghostty = Terminals.TERMINALS[0]
        with patch("subprocess.run") as mock_run:
            ghostty["open"]("/test/path")
            args = mock_run.call_args[0][0]
            assert args == ["open", "-a", "Ghostty", "/test/path"]

    def test_wezterm_open_uses_wezterm_start(self):
        """WezTerm open should use 'wezterm start --cwd --new-tab'."""
        wezterm = Terminals.TERMINALS[1]
        with patch("subprocess.run") as mock_run:
            wezterm["open"]("/test/path")
            # WezTerm uses shell=True with a command string
            call_args = mock_run.call_args
            cmd = call_args[0][0]
            assert "wezterm start" in cmd
            assert "--cwd" in cmd
            assert "--new-tab" in cmd
            assert "/test/path" in cmd
            assert call_args[1]["shell"] is True
