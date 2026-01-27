"""Tests for open-terminal command."""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from alfred_pj.commands.open_terminal import open_terminal


class TestOpenTerminalCommand:
    """Tests for the open-terminal command."""

    def test_calls_terminal_open(self, temp_project):
        """Should call the terminal's open function."""
        mock_terminal = {
            "name": "MockTerminal",
            "check": lambda: True,
            "open": MagicMock(),
        }

        with patch("alfred_pj.terminals.Terminals.get_available_terminal", return_value=mock_terminal):
            runner = CliRunner()
            result = runner.invoke(open_terminal, ["--path", str(temp_project)])

            assert result.exit_code == 0
            mock_terminal["open"].assert_called_once_with(str(temp_project))

    def test_uses_detected_terminal(self, temp_project):
        """Should use the terminal returned by get_available_terminal."""
        call_log = []

        mock_terminal = {
            "name": "TestTerminal",
            "check": lambda: True,
            "open": lambda p: call_log.append(("TestTerminal", p)),
        }

        with patch("alfred_pj.terminals.Terminals.get_available_terminal", return_value=mock_terminal):
            runner = CliRunner()
            result = runner.invoke(open_terminal, ["--path", str(temp_project)])

            assert result.exit_code == 0
            assert len(call_log) == 1
            assert call_log[0] == ("TestTerminal", str(temp_project))

    def test_requires_existing_path(self, tmp_path):
        """Should require path to exist."""
        runner = CliRunner()
        result = runner.invoke(open_terminal, ["--path", str(tmp_path / "nonexistent")])

        assert result.exit_code != 0

    def test_requires_path_option(self):
        """Should require --path option."""
        runner = CliRunner()
        result = runner.invoke(open_terminal)

        assert result.exit_code != 0
        assert "Missing option '--path'" in result.output
