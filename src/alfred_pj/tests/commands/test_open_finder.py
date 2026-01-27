"""Tests for open-finder command."""

from unittest.mock import patch

from click.testing import CliRunner

from alfred_pj.commands.open_finder import open_finder


class TestOpenFinderCommand:
    """Tests for the open-finder command."""

    def test_calls_open_command(self, temp_project):
        """Should call 'open' command with path."""
        with patch("subprocess.run") as mock_run:
            runner = CliRunner()
            result = runner.invoke(open_finder, ["--path", str(temp_project)])

            assert result.exit_code == 0
            mock_run.assert_called_once_with(["open", str(temp_project)])

    def test_passes_path_to_open(self, temp_project):
        """Should pass the exact path to open command."""
        with patch("subprocess.run") as mock_run:
            runner = CliRunner()
            result = runner.invoke(open_finder, ["--path", str(temp_project)])

            assert result.exit_code == 0
            args = mock_run.call_args[0][0]
            assert args == ["open", str(temp_project)]

    def test_requires_existing_path(self, tmp_path):
        """Should require path to exist."""
        runner = CliRunner()
        result = runner.invoke(open_finder, ["--path", str(tmp_path / "nonexistent")])

        assert result.exit_code != 0

    def test_requires_path_option(self):
        """Should require --path option."""
        runner = CliRunner()
        result = runner.invoke(open_finder)

        assert result.exit_code != 0
        assert "Missing option '--path'" in result.output
