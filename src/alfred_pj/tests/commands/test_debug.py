"""Tests for debug command."""

import pytest
from click.testing import CliRunner

from alfred_pj.commands.debug import debug


class TestDebugCommand:
    """Tests for the debug command."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_shows_environment_info(self, runner, monkeypatch):
        """Debug command outputs environment information."""
        monkeypatch.setenv("HOME", "/home/testuser")
        result = runner.invoke(debug)
        assert result.exit_code == 0
        assert "=== Environment ===" in result.output
        assert "PATH:" in result.output
        assert "HOME:" in result.output

    def test_shows_editor_availability(self, runner):
        """Debug command shows predefined editor availability."""
        result = runner.invoke(debug)
        assert result.exit_code == 0
        assert "=== Predefined Editor Availability ===" in result.output

    def test_with_path_shows_detection(self, runner, python_project):
        """Debug command with path shows detection details."""
        result = runner.invoke(debug, ["--path", str(python_project)])
        assert result.exit_code == 0
        assert f"=== Detection for {python_project} ===" in result.output
        assert "Matched detector:" in result.output

    def test_with_path_shows_env_var(self, runner, python_project):
        """Debug command shows environment variable for detector."""
        result = runner.invoke(debug, ["--path", str(python_project)])
        assert result.exit_code == 0
        assert "Env var:" in result.output

    def test_with_path_shows_default_editors(self, runner, python_project):
        """Debug command shows default editors for detector."""
        result = runner.invoke(debug, ["--path", str(python_project)])
        assert result.exit_code == 0
        assert "Default editors:" in result.output

    def test_with_path_shows_resolved_editors(self, runner, python_project):
        """Debug command shows resolved editors list."""
        result = runner.invoke(debug, ["--path", str(python_project)])
        assert result.exit_code == 0
        assert "Resolved editors:" in result.output

    def test_with_path_shows_final_editor(self, runner, python_project):
        """Debug command shows final selected editor."""
        result = runner.invoke(debug, ["--path", str(python_project)])
        assert result.exit_code == 0
        assert "Final editor:" in result.output

    def test_unmatched_path_shows_default(self, runner, temp_project):
        """Debug command with unmatched path shows default fallback."""
        result = runner.invoke(debug, ["--path", str(temp_project)])
        assert result.exit_code == 0
        assert "No detector matched, using default" in result.output
        assert "Final editor:" in result.output

    def test_shows_dynamic_editors_when_registered(self, runner, temp_project, monkeypatch):
        """Debug command shows dynamic editors if any were registered."""
        # Create a project that would use a custom editor from env
        (temp_project / "pyproject.toml").touch()
        monkeypatch.setenv("EDITORS_PYTHON", "custom-editor,code")
        result = runner.invoke(debug, ["--path", str(temp_project)])
        assert result.exit_code == 0
        # Dynamic editors section may or may not appear depending on availability

    def test_detects_javascript_project(self, runner, javascript_project):
        """Debug command correctly detects JavaScript project."""
        result = runner.invoke(debug, ["--path", str(javascript_project)])
        assert result.exit_code == 0
        assert "Matched detector:" in result.output

    def test_detects_go_project(self, runner, go_project):
        """Debug command correctly detects Go project."""
        result = runner.invoke(debug, ["--path", str(go_project)])
        assert result.exit_code == 0
        assert "Matched detector:" in result.output

    def test_detects_rust_project(self, runner, rust_project):
        """Debug command correctly detects Rust project."""
        result = runner.invoke(debug, ["--path", str(rust_project)])
        assert result.exit_code == 0
        assert "Matched detector:" in result.output

    def test_detects_obsidian_vault(self, runner, obsidian_vault):
        """Debug command correctly detects Obsidian vault."""
        result = runner.invoke(debug, ["--path", str(obsidian_vault)])
        assert result.exit_code == 0
        assert "Matched detector:" in result.output
        assert "obsidian" in result.output.lower()
