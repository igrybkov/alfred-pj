"""Tests for list command."""

import json

from click.testing import CliRunner

from alfred_pj.commands.list import list as list_cmd


class TestListCommand:
    """Tests for the list command."""

    def test_lists_projects_from_path(self, projects_dir, temp_usage_dir):
        """Should list all project directories."""
        runner = CliRunner()
        result = runner.invoke(list_cmd, ["--paths", str(projects_dir)])

        assert result.exit_code == 0
        output = json.loads(result.output)

        assert "items" in output
        titles = [item["title"] for item in output["items"]]
        assert "my-python-app" in titles
        assert "my-js-app" in titles
        assert "my-go-app" in titles

    def test_items_have_required_fields(self, projects_dir, temp_usage_dir):
        """Each item should have title, subtitle, arg, icon."""
        runner = CliRunner()
        result = runner.invoke(list_cmd, ["--paths", str(projects_dir)])

        output = json.loads(result.output)
        for item in output["items"]:
            assert "title" in item
            assert "subtitle" in item
            assert "arg" in item
            assert "icon" in item

    def test_sorted_by_usage(self, projects_dir, temp_usage_dir):
        """Items should be sorted by usage count (descending)."""
        # Set up usage data
        from alfred_pj.usage import UsageData

        usage = UsageData()
        # Add more usage to go project
        usage.add_usage(str(projects_dir / "my-go-app"), count=10)
        usage.add_usage(str(projects_dir / "my-python-app"), count=5)
        usage.write_data()

        runner = CliRunner()
        result = runner.invoke(list_cmd, ["--paths", str(projects_dir)])

        output = json.loads(result.output)
        items = output["items"]

        # Find go and python projects
        go_idx = next(i for i, item in enumerate(items) if item["title"] == "my-go-app")
        python_idx = next(i for i, item in enumerate(items) if item["title"] == "my-python-app")

        # Go should come before Python (higher usage)
        assert go_idx < python_idx

    def test_handles_multiple_paths(self, tmp_path, temp_usage_dir):
        """Should handle comma-separated paths."""
        # Create two separate project directories
        path1 = tmp_path / "projects1"
        path1.mkdir()
        proj1 = path1 / "proj-a"
        proj1.mkdir()
        (proj1 / "package.json").touch()

        path2 = tmp_path / "projects2"
        path2.mkdir()
        proj2 = path2 / "proj-b"
        proj2.mkdir()
        (proj2 / "go.mod").touch()

        runner = CliRunner()
        result = runner.invoke(list_cmd, ["--paths", f"{path1},{path2}"])

        assert result.exit_code == 0
        output = json.loads(result.output)
        titles = [item["title"] for item in output["items"]]
        assert "proj-a" in titles
        assert "proj-b" in titles

    def test_skips_invalid_paths(self, projects_dir, temp_usage_dir):
        """Should skip paths that don't exist."""
        runner = CliRunner()
        result = runner.invoke(list_cmd, ["--paths", f"{projects_dir},/nonexistent/path/12345"])

        assert result.exit_code == 0
        output = json.loads(result.output)
        # Should still have items from valid path
        assert len(output["items"]) > 0

    def test_skips_non_directory_paths(self, tmp_path, temp_usage_dir):
        """Should skip paths that are files, not directories."""
        # Create a file instead of directory
        file_path = tmp_path / "not_a_directory"
        file_path.touch()

        runner = CliRunner()
        result = runner.invoke(list_cmd, ["--paths", str(file_path)])

        assert result.exit_code == 0
        output = json.loads(result.output)
        # Only the "Clear usage data" item should be present
        assert len(output["items"]) == 1
        assert output["items"][0]["arg"] == "__CLEAR_USAGE__"

    def test_only_lists_directories(self, tmp_path, temp_usage_dir):
        """Should only list directories, not files in the path."""
        projects = tmp_path / "projects"
        projects.mkdir()

        # Create a directory project
        proj_dir = projects / "my-project"
        proj_dir.mkdir()
        (proj_dir / "pyproject.toml").touch()

        # Create a file (should be ignored)
        (projects / "some-file.txt").touch()

        runner = CliRunner()
        result = runner.invoke(list_cmd, ["--paths", str(projects)])

        output = json.loads(result.output)
        titles = [item["title"] for item in output["items"]]
        assert "my-project" in titles
        assert "some-file.txt" not in titles

    def test_arg_is_full_path(self, projects_dir, temp_usage_dir):
        """Item arg should be the full path to the project."""
        runner = CliRunner()
        result = runner.invoke(list_cmd, ["--paths", str(projects_dir)])

        output = json.loads(result.output)
        for item in output["items"]:
            # Skip the "Clear usage data" item
            if item["arg"] == "__CLEAR_USAGE__":
                continue
            assert item["arg"].startswith(str(projects_dir))

    def test_empty_directory(self, tmp_path, temp_usage_dir):
        """Should handle empty project directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        runner = CliRunner()
        result = runner.invoke(list_cmd, ["--paths", str(empty_dir)])

        assert result.exit_code == 0
        output = json.loads(result.output)
        # Only the "Clear usage data" item should be present
        assert len(output["items"]) == 1
        assert output["items"][0]["arg"] == "__CLEAR_USAGE__"

    def test_requires_paths_option(self, temp_usage_dir):
        """Should require --paths option."""
        runner = CliRunner()
        result = runner.invoke(list_cmd)

        assert result.exit_code != 0
        assert "Missing option '--paths'" in result.output

    def test_clear_usage_item_at_end(self, projects_dir, temp_usage_dir):
        """Should include 'Clear usage data' item at the end of the list."""
        runner = CliRunner()
        result = runner.invoke(list_cmd, ["--paths", str(projects_dir)])

        output = json.loads(result.output)
        items = output["items"]

        # Last item should be "Clear usage data"
        assert items[-1]["title"] == "> Clear usage data"
        assert items[-1]["arg"] == "__CLEAR_USAGE__"
        assert items[-1]["subtitle"] == "Reset project selection statistics"

    def test_skips_hidden_directories(self, tmp_path, temp_usage_dir):
        """Should skip directories starting with a dot."""
        projects = tmp_path / "projects"
        projects.mkdir()

        # Create a visible project
        visible_proj = projects / "visible-project"
        visible_proj.mkdir()
        (visible_proj / "package.json").touch()

        # Create hidden directories (should be skipped)
        hidden_proj = projects / ".hidden-project"
        hidden_proj.mkdir()
        (hidden_proj / "package.json").touch()

        git_dir = projects / ".git"
        git_dir.mkdir()

        runner = CliRunner()
        result = runner.invoke(list_cmd, ["--paths", str(projects)])

        output = json.loads(result.output)
        titles = [item["title"] for item in output["items"]]

        assert "visible-project" in titles
        assert ".hidden-project" not in titles
        assert ".git" not in titles

    def test_handles_tilde_path_expansion(self, tmp_path, temp_usage_dir, monkeypatch):
        """Should expand ~ in paths."""
        # Create projects in a fake home directory
        fake_home = tmp_path / "fakehome"
        fake_home.mkdir()
        projects = fake_home / "projects"
        projects.mkdir()

        proj = projects / "home-project"
        proj.mkdir()
        (proj / "pyproject.toml").touch()

        monkeypatch.setenv("HOME", str(fake_home))

        runner = CliRunner()
        result = runner.invoke(list_cmd, ["--paths", "~/projects"])

        assert result.exit_code == 0
        output = json.loads(result.output)
        titles = [item["title"] for item in output["items"]]
        assert "home-project" in titles

    def test_handles_path_with_special_chars(self, tmp_path, temp_usage_dir):
        """Should handle paths with spaces and special characters."""
        projects = tmp_path / "my projects"
        projects.mkdir()

        proj = projects / "project-name"
        proj.mkdir()
        (proj / "package.json").touch()

        runner = CliRunner()
        result = runner.invoke(list_cmd, ["--paths", str(projects)])

        assert result.exit_code == 0
        output = json.loads(result.output)
        titles = [item["title"] for item in output["items"]]
        assert "project-name" in titles
