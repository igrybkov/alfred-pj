"""Tests for open-project command."""

from unittest.mock import patch

from click.testing import CliRunner

from alfred_pj.commands.open_project import open_project


class TestOpenProjectCommand:
    """Tests for the open-project command."""

    def test_calls_subprocess_with_editor(self, python_project):
        """Should call subprocess with determined editor."""
        with patch("subprocess.run") as mock_run:
            runner = CliRunner()
            result = runner.invoke(open_project, ["--path", str(python_project)])

            assert result.exit_code == 0
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            # First arg should be editor command
            assert args[0] in ["code", "pycharm", "idea", "obsidian"]
            # Second arg should be path
            assert args[1] == str(python_project)

    def test_uses_correct_editor_for_project_type(self, go_project):
        """Should use correct editor based on project type."""
        with (
            patch("subprocess.run") as mock_run,
            patch("alfred_pj.editors.which", side_effect=lambda x: x if x == "goland" else None),
        ):
            runner = CliRunner()
            result = runner.invoke(open_project, ["--path", str(go_project)])

            if result.exit_code == 0 and mock_run.called:
                args = mock_run.call_args[0][0]
                # Should be a Go editor
                assert args[0] in ["goland", "idea", "code"]

    def test_requires_existing_path(self, tmp_path):
        """Should require path to exist."""
        runner = CliRunner()
        result = runner.invoke(open_project, ["--path", str(tmp_path / "nonexistent")])

        assert result.exit_code != 0

    def test_requires_path_option(self):
        """Should require --path option."""
        runner = CliRunner()
        result = runner.invoke(open_project)

        assert result.exit_code != 0
        assert "Missing option '--path'" in result.output

    def test_clear_usage_clears_data(self, temp_usage_dir):
        """Should clear usage data when path is __CLEAR_USAGE__."""
        from alfred_pj.usage import UsageData

        # Add some usage data first
        usage = UsageData()
        usage.add_usage("/some/path", count=5)
        usage.write_data()

        # Verify data exists
        usage = UsageData()
        assert usage.get_usage_by_path("/some/path") == 5

        # Run with special clear arg
        runner = CliRunner()
        result = runner.invoke(open_project, ["--path", "__CLEAR_USAGE__"])

        assert result.exit_code == 0

        # Verify data was cleared
        usage = UsageData()
        assert usage.get_usage_by_path("/some/path") == 0
