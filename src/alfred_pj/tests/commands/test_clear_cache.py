"""Tests for clear_cache command."""

import pytest
from click.testing import CliRunner

from alfred_pj.commands.clear_cache import clear_cache


class TestClearCacheCommand:
    """Tests for the clear-cache command."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_clears_usage_by_default(self, runner, temp_usage_dir):
        """Clear cache clears usage statistics by default."""
        # Create some usage data first
        usage_file = temp_usage_dir / "usage.json"
        usage_file.write_text('{"test": 5}')

        result = runner.invoke(clear_cache, ["--no-alfred"])
        assert result.exit_code == 0
        assert "usage statistics" in result.output

    def test_clears_alfred_cache_when_exists(self, runner, tmp_path, monkeypatch, temp_usage_dir):
        """Clear cache clears Alfred cache directory when it exists."""
        cache_dir = tmp_path / "alfred_cache"
        cache_dir.mkdir()
        (cache_dir / "some_cache_file.txt").write_text("cached data")

        monkeypatch.setenv("alfred_workflow_cache", str(cache_dir))

        result = runner.invoke(clear_cache)
        assert result.exit_code == 0
        assert "Alfred cache" in result.output
        # Cache dir should be recreated but empty
        assert cache_dir.exists()
        assert len(list(cache_dir.iterdir())) == 0

    def test_skips_alfred_cache_when_no_env(self, runner, temp_usage_dir, monkeypatch):
        """Clear cache skips Alfred cache when env var not set."""
        monkeypatch.delenv("alfred_workflow_cache", raising=False)
        result = runner.invoke(clear_cache)
        assert result.exit_code == 0
        assert "usage statistics" in result.output
        # Alfred cache not mentioned since env var not set

    def test_skips_alfred_cache_when_dir_missing(
        self, runner, tmp_path, monkeypatch, temp_usage_dir
    ):
        """Clear cache skips Alfred cache when directory doesn't exist."""
        nonexistent = tmp_path / "nonexistent_cache"
        monkeypatch.setenv("alfred_workflow_cache", str(nonexistent))

        result = runner.invoke(clear_cache)
        assert result.exit_code == 0
        # Only usage statistics cleared, not Alfred cache
        assert "usage statistics" in result.output

    def test_no_usage_flag_skips_usage(self, runner, temp_usage_dir, monkeypatch):
        """--no-usage flag skips clearing usage statistics."""
        monkeypatch.delenv("alfred_workflow_cache", raising=False)
        result = runner.invoke(clear_cache, ["--no-usage"])
        assert result.exit_code == 0
        assert "Nothing to clear" in result.output

    def test_no_alfred_flag_skips_alfred_cache(self, runner, tmp_path, monkeypatch, temp_usage_dir):
        """--no-alfred flag skips clearing Alfred cache."""
        cache_dir = tmp_path / "alfred_cache"
        cache_dir.mkdir()
        (cache_dir / "keep_me.txt").write_text("important")

        monkeypatch.setenv("alfred_workflow_cache", str(cache_dir))

        result = runner.invoke(clear_cache, ["--no-alfred"])
        assert result.exit_code == 0
        assert "usage statistics" in result.output
        assert "Alfred cache" not in result.output
        # File should still exist
        assert (cache_dir / "keep_me.txt").exists()

    def test_both_flags_disabled_nothing_to_clear(self, runner, monkeypatch):
        """Both --no-usage and --no-alfred results in nothing to clear."""
        monkeypatch.delenv("alfred_workflow_cache", raising=False)
        result = runner.invoke(clear_cache, ["--no-usage", "--no-alfred"])
        assert result.exit_code == 0
        assert "Nothing to clear" in result.output

    def test_clears_both_when_available(self, runner, tmp_path, monkeypatch, temp_usage_dir):
        """Clear cache clears both usage and Alfred cache when available."""
        cache_dir = tmp_path / "alfred_cache"
        cache_dir.mkdir()
        (cache_dir / "cache.txt").write_text("data")

        monkeypatch.setenv("alfred_workflow_cache", str(cache_dir))

        result = runner.invoke(clear_cache)
        assert result.exit_code == 0
        assert "usage statistics" in result.output
        assert "Alfred cache" in result.output
