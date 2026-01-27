"""Tests for open-github command."""

import pytest
from unittest.mock import patch
from click.testing import CliRunner

from alfred_pj.commands.open_github import open_github


class TestOpenGithubCommand:
    """Tests for the open-github command."""

    def test_calls_gh_browse(self, temp_project):
        """Should call 'gh browse' command."""
        with patch("subprocess.run") as mock_run:
            runner = CliRunner()
            result = runner.invoke(open_github, ["--path", str(temp_project)])

            assert result.exit_code == 0
            mock_run.assert_called_once_with(
                ["gh", "browse"],
                cwd=str(temp_project)
            )

    def test_uses_cwd_parameter(self, temp_project):
        """Should use cwd parameter with the project path."""
        with patch("subprocess.run") as mock_run:
            runner = CliRunner()
            result = runner.invoke(open_github, ["--path", str(temp_project)])

            assert result.exit_code == 0
            call_kwargs = mock_run.call_args[1]
            assert call_kwargs["cwd"] == str(temp_project)

    def test_requires_existing_path(self, tmp_path):
        """Should require path to exist."""
        runner = CliRunner()
        result = runner.invoke(open_github, ["--path", str(tmp_path / "nonexistent")])

        assert result.exit_code != 0

    def test_requires_path_option(self):
        """Should require --path option."""
        runner = CliRunner()
        result = runner.invoke(open_github)

        assert result.exit_code != 0
        assert "Missing option '--path'" in result.output
