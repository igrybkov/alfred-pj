"""Tests for editor command."""

from click.testing import CliRunner

from alfred_pj.commands.editor import editor


class TestEditorCommand:
    """Tests for the editor command."""

    def test_outputs_editor_code(self, python_project):
        """Should output the editor code for a path."""
        runner = CliRunner()
        result = runner.invoke(editor, ["--path", str(python_project)])

        assert result.exit_code == 0
        # Should output an editor code (e.g., 'code', 'pycharm', etc.)
        assert result.output.strip() in [
            "code",
            "pycharm",
            "idea",
            "obsidian",
            "phpstorm",
            "webstorm",
            "goland",
            "rustrover",
            "rubymine",
            "clion",
        ]

    def test_detects_python_project(self, python_project):
        """Should detect Python project correctly."""
        runner = CliRunner()
        result = runner.invoke(editor, ["--path", str(python_project)])

        assert result.exit_code == 0
        # Python projects should use pycharm, idea, or code
        assert result.output.strip() in ["pycharm", "idea", "code"]

    def test_detects_javascript_project(self, javascript_project):
        """Should detect JavaScript project correctly."""
        runner = CliRunner()
        result = runner.invoke(editor, ["--path", str(javascript_project)])

        assert result.exit_code == 0
        # JS projects should use webstorm, phpstorm, idea, or code
        assert result.output.strip() in ["webstorm", "phpstorm", "idea", "code"]

    def test_detects_go_project(self, go_project):
        """Should detect Go project correctly."""
        runner = CliRunner()
        result = runner.invoke(editor, ["--path", str(go_project)])

        assert result.exit_code == 0
        # Go projects should use goland, idea, or code
        assert result.output.strip() in ["goland", "idea", "code"]

    def test_detects_rust_project(self, rust_project):
        """Should detect Rust project correctly."""
        runner = CliRunner()
        result = runner.invoke(editor, ["--path", str(rust_project)])

        assert result.exit_code == 0
        # Rust projects should use rustrover, idea, or code
        assert result.output.strip() in ["rustrover", "idea", "code"]

    def test_detects_obsidian_vault(self, obsidian_vault):
        """Should detect Obsidian vault correctly."""
        runner = CliRunner()
        result = runner.invoke(editor, ["--path", str(obsidian_vault)])

        assert result.exit_code == 0
        # Obsidian vaults should use obsidian (or fallback to default)
        assert result.output.strip() in ["obsidian", "code"]

    def test_fallback_for_unknown_project(self, temp_project):
        """Should fallback to default editor for unknown project type."""
        runner = CliRunner()
        result = runner.invoke(editor, ["--path", str(temp_project)])

        assert result.exit_code == 0
        # Should output default editor (typically 'code')
        assert result.output.strip() == "code"

    def test_requires_path_option(self):
        """Should require --path option."""
        runner = CliRunner()
        result = runner.invoke(editor)

        assert result.exit_code != 0
        assert "Missing option '--path'" in result.output
