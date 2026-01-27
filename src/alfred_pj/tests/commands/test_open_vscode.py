"""Tests for open-vscode command."""

from unittest.mock import patch

from click.testing import CliRunner

from alfred_pj.commands.open_vscode import open_vscode


class TestOpenVscodeCommand:
    """Tests for the open-vscode command."""

    def test_calls_code_command(self, temp_project):
        """Should call 'code' command with path."""
        with patch("subprocess.run") as mock_run:
            runner = CliRunner()
            result = runner.invoke(open_vscode, ["--path", str(temp_project)])

            assert result.exit_code == 0
            mock_run.assert_called_once_with(["code", str(temp_project)])

    def test_always_uses_code(self, python_project):
        """Should always use 'code' regardless of project type."""
        with patch("subprocess.run") as mock_run:
            runner = CliRunner()
            result = runner.invoke(open_vscode, ["--path", str(python_project)])

            assert result.exit_code == 0
            args = mock_run.call_args[0][0]
            assert args[0] == "code"

    def test_requires_existing_path(self, tmp_path):
        """Should require path to exist."""
        runner = CliRunner()
        result = runner.invoke(open_vscode, ["--path", str(tmp_path / "nonexistent")])

        assert result.exit_code != 0

    def test_requires_path_option(self):
        """Should require --path option."""
        runner = CliRunner()
        result = runner.invoke(open_vscode)

        assert result.exit_code != 0
        assert "Missing option '--path'" in result.output
