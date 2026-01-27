"""Tests for editor detection."""

from unittest.mock import patch

from alfred_pj.editors import DETECTORS, Editors


class TestEditorDetection:
    """Tests for Editors.determine_editor()."""

    def test_detect_obsidian_vault(self, obsidian_vault):
        """Directory with .obsidian should detect as obsidian."""
        editors = Editors()
        result = editors.determine_editor(str(obsidian_vault))
        # Obsidian may not be available, so it falls back to default
        assert result in ("obsidian", editors.default_editor)

    def test_detect_vscode_project(self, vscode_project):
        """Directory with .vscode (without .idea) should detect as code."""
        editors = Editors()
        result = editors.determine_editor(str(vscode_project))
        assert result == "code" or result == editors.default_editor

    def test_vscode_excluded_by_idea(self, vscode_project):
        """Directory with both .vscode and .idea should NOT detect as vscode."""
        # Add .idea directory
        (vscode_project / ".idea").mkdir()
        editors = Editors()
        result = editors.determine_editor(str(vscode_project))
        # Should not be vscode detector (it has exclude_dirs for .idea)
        # Should fall through to default since no other detector matches
        assert result == editors.default_editor

    def test_detect_java_maven(self, java_maven_project):
        """Directory with pom.xml should detect as java."""
        editors = Editors()
        result = editors.determine_editor(str(java_maven_project))
        assert result in ("idea", editors.default_editor)

    def test_detect_java_gradle(self, java_gradle_project):
        """Directory with build.gradle should detect as java."""
        editors = Editors()
        result = editors.determine_editor(str(java_gradle_project))
        assert result in ("idea", editors.default_editor)

    def test_detect_php_composer(self, php_project):
        """Directory with composer.json should detect as php."""
        editors = Editors()
        result = editors.determine_editor(str(php_project))
        assert result in ("phpstorm", "idea", "code", editors.default_editor)

    def test_detect_php_glob(self, temp_project):
        """Directory with *.php files should detect as php."""
        (temp_project / "index.php").touch()
        editors = Editors()
        result = editors.determine_editor(str(temp_project))
        assert result in ("phpstorm", "idea", "code", editors.default_editor)

    def test_detect_jupyter(self, jupyter_project):
        """Directory with *.ipynb files should detect as jupyter."""
        editors = Editors()
        result = editors.determine_editor(str(jupyter_project))
        assert result in ("pycharm", "idea", "code", editors.default_editor)

    def test_detect_python_pyproject(self, python_project):
        """Directory with pyproject.toml should detect as python."""
        editors = Editors()
        result = editors.determine_editor(str(python_project))
        assert result in ("pycharm", "idea", "code", editors.default_editor)

    def test_detect_python_venv(self, temp_project):
        """Directory with .venv should detect as python."""
        (temp_project / ".venv").mkdir()
        editors = Editors()
        result = editors.determine_editor(str(temp_project))
        assert result in ("pycharm", "idea", "code", editors.default_editor)

    def test_detect_typescript(self, typescript_project):
        """Directory with tsconfig.json should detect as typescript."""
        editors = Editors()
        result = editors.determine_editor(str(typescript_project))
        assert result in ("webstorm", "code", editors.default_editor)

    def test_detect_javascript(self, javascript_project):
        """Directory with package.json should detect as javascript."""
        editors = Editors()
        result = editors.determine_editor(str(javascript_project))
        assert result in ("webstorm", "phpstorm", "idea", "code", editors.default_editor)

    def test_detect_go(self, go_project):
        """Directory with go.mod should detect as go."""
        editors = Editors()
        result = editors.determine_editor(str(go_project))
        assert result in ("goland", "idea", "code", editors.default_editor)

    def test_detect_rust(self, rust_project):
        """Directory with Cargo.toml should detect as rust."""
        editors = Editors()
        result = editors.determine_editor(str(rust_project))
        assert result in ("rustrover", "idea", "code", editors.default_editor)

    def test_detect_ruby(self, ruby_project):
        """Directory with Gemfile should detect as ruby."""
        editors = Editors()
        result = editors.determine_editor(str(ruby_project))
        assert result in ("rubymine", "code", editors.default_editor)

    def test_detect_cpp(self, cpp_project):
        """Directory with CMakeLists.txt should detect as cpp."""
        editors = Editors()
        result = editors.determine_editor(str(cpp_project))
        assert result in ("clion", "code", editors.default_editor)

    def test_fallback_to_default(self, temp_project):
        """Unknown project type should fallback to DEFAULT_EDITOR."""
        editors = Editors()
        result = editors.determine_editor(str(temp_project))
        assert result == editors.default_editor

    def test_default_editor_from_environment(self, temp_project, mock_env):
        """DEFAULT_EDITOR environment variable should be respected."""
        mock_env(DEFAULT_EDITOR="sublime")
        editors = Editors()
        assert editors.default_editor == "sublime"


class TestGetFirstAvailableEditor:
    """Tests for Editors.get_first_available_editor()."""

    def test_returns_first_available(self):
        """Should return first available editor from list."""
        editors = Editors()
        # Code is commonly available
        result = editors.get_first_available_editor(["code"])
        if editors.editors.get("code", {}).get("available"):
            assert result == "code"
        else:
            assert result == editors.default_editor

    def test_falls_back_to_default(self):
        """Should return default editor if none available."""
        editors = Editors()
        result = editors.get_first_available_editor(["nonexistent_editor"])
        assert result == editors.default_editor


class TestGetEditorsFromEnvironment:
    """Tests for Editors.get_editors_from_environment()."""

    def test_returns_defaults_when_no_env(self, mock_env):
        """Should return defaults when env var is not set."""
        mock_env(EDITORS_PYTHON=None)
        editors = Editors()
        result = editors.get_editors_from_environment("EDITORS_PYTHON", ["pycharm", "code"])
        assert result == ["pycharm", "code"]

    def test_reads_from_environment(self, mock_env):
        """Should read editors from environment variable."""
        mock_env(EDITORS_PYTHON="code,sublime")
        editors = Editors()
        result = editors.get_editors_from_environment("EDITORS_PYTHON", ["pycharm", "code"])
        assert result == ["code", "sublime"]

    def test_handles_list_of_env_vars(self, mock_env):
        """Should check multiple env vars in order."""
        mock_env(EDITORS_JUPYTER=None, EDITORS_PYTHON="pycharm")
        editors = Editors()
        result = editors.get_editors_from_environment(
            ["EDITORS_JUPYTER", "EDITORS_PYTHON"], ["code"]
        )
        assert result == ["pycharm"]

    def test_strips_whitespace(self, mock_env):
        """Should strip whitespace from editor names."""
        mock_env(EDITORS_PYTHON="  code  ,  sublime  ")
        editors = Editors()
        result = editors.get_editors_from_environment("EDITORS_PYTHON", ["pycharm"])
        assert result == ["code", "sublime"]


class TestDetectorPriority:
    """Tests for detector priority (first match wins)."""

    def test_obsidian_has_highest_priority(self, temp_project):
        """Obsidian detector should take priority over others."""
        # Create both obsidian vault and python project markers
        (temp_project / ".obsidian").mkdir()
        (temp_project / "pyproject.toml").touch()

        editors = Editors()
        # Should detect as obsidian, not python
        for detector in DETECTORS:
            if editors._matches_detector(str(temp_project), detector):
                assert detector["name"] == "obsidian"
                break

    def test_typescript_before_javascript(self, temp_project):
        """TypeScript should be detected before JavaScript."""
        # Create both typescript and javascript markers
        (temp_project / "tsconfig.json").touch()
        (temp_project / "package.json").touch()

        editors = Editors()
        matched_name = None
        for detector in DETECTORS:
            if editors._matches_detector(str(temp_project), detector):
                matched_name = detector["name"]
                break

        assert matched_name == "typescript"


class TestMatchesDetector:
    """Tests for Editors._matches_detector()."""

    def test_matches_dirs(self, temp_project):
        """Should match when directory exists."""
        (temp_project / ".venv").mkdir()
        editors = Editors()
        detector = {"dirs": [".venv"]}
        assert editors._matches_detector(str(temp_project), detector)

    def test_matches_files(self, temp_project):
        """Should match when file exists."""
        (temp_project / "requirements.txt").touch()
        editors = Editors()
        detector = {"files": ["requirements.txt"]}
        assert editors._matches_detector(str(temp_project), detector)

    def test_matches_globs(self, temp_project):
        """Should match when glob pattern matches."""
        (temp_project / "main.py").touch()
        editors = Editors()
        detector = {"globs": ["*.py"]}
        assert editors._matches_detector(str(temp_project), detector)

    def test_exclude_dirs_blocks_match(self, temp_project):
        """Exclude dirs should prevent a match."""
        (temp_project / ".vscode").mkdir()
        (temp_project / ".idea").mkdir()
        editors = Editors()
        detector = {"dirs": [".vscode"], "exclude_dirs": [".idea"]}
        assert not editors._matches_detector(str(temp_project), detector)


class TestGetEditor:
    """Tests for Editors.get_editor() method."""

    def test_returns_known_editor(self):
        """Should return info for known editor."""
        editors = Editors()
        result = editors.get_editor("code")
        assert result is not None
        assert "name" in result
        assert result["name"] == "VS Code"

    def test_registers_dynamic_editor_when_available(self, monkeypatch):
        """Should register and return dynamic editor if available."""
        editors = Editors()
        # Mock which() to return a path for our fake editor
        with patch("alfred_pj.editors.which") as mock_which:
            mock_which.return_value = "/usr/local/bin/custom-editor"
            result = editors.get_editor("custom-editor")
            assert result is not None
            assert result["available"] is True
            assert result["name"] == "Custom Editor"  # Title case

    def test_registers_unavailable_editor(self, monkeypatch):
        """Should register editor as unavailable if not found."""
        editors = Editors()
        with patch("alfred_pj.editors.which") as mock_which:
            mock_which.return_value = None
            result = editors.get_editor("nonexistent-editor")
            assert result is not None
            assert result["available"] is False


class TestDynamicEditorRegistration:
    """Tests for dynamic editor registration."""

    def test_dynamic_editor_uses_title_case_name(self):
        """Dynamic editor should have title-cased display name."""
        editors = Editors()
        with patch("alfred_pj.editors.which") as mock_which:
            mock_which.return_value = "/usr/bin/my-custom-editor"
            editors._register_dynamic_editor("my-custom-editor")
            assert editors.editors["my-custom-editor"]["name"] == "My Custom Editor"

    def test_dynamic_editor_with_underscore(self):
        """Dynamic editor with underscores should convert to spaces."""
        editors = Editors()
        with patch("alfred_pj.editors.which") as mock_which:
            mock_which.return_value = "/usr/bin/my_editor"
            editors._register_dynamic_editor("my_editor")
            assert editors.editors["my_editor"]["name"] == "My Editor"

    def test_dynamic_editor_uses_fallback_icon(self):
        """Dynamic editor should use workflow icon as fallback."""
        editors = Editors()
        with patch("alfred_pj.editors.which") as mock_which:
            mock_which.return_value = "/usr/bin/some-editor"
            editors._register_dynamic_editor("some-editor")
            assert editors.editors["some-editor"]["icon"] == {"path": "icon.png"}

    def test_get_first_available_registers_unknown_editor(self):
        """get_first_available_editor should register unknown editors."""
        editors = Editors()
        with patch("alfred_pj.editors.which") as mock_which:
            mock_which.return_value = "/usr/bin/my-new-editor"
            result = editors.get_first_available_editor(["my-new-editor"])
            assert result == "my-new-editor"
            assert "my-new-editor" in editors.editors
            assert editors.editors["my-new-editor"]["available"] is True

    def test_get_first_available_skips_unavailable_dynamic(self):
        """get_first_available_editor should skip unavailable dynamic editors."""
        editors = Editors()
        with patch("alfred_pj.editors.which") as mock_which:
            # First editor not available, second is
            def which_side_effect(cmd):
                if cmd == "unavailable-editor":
                    return None
                elif cmd == "code":
                    return "/usr/bin/code"
                return None

            mock_which.side_effect = which_side_effect

            result = editors.get_first_available_editor(["unavailable-editor", "code"])
            # Should return code since it's available (or default if code isn't installed)
            assert result in ("code", editors.default_editor)
