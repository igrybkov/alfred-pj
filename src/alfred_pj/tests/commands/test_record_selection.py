"""Tests for record-selection command."""

import pytest
from click.testing import CliRunner

from alfred_pj.commands.record_selection import record_selection
from alfred_pj.usage import UsageData


class TestRecordSelectionCommand:
    """Tests for the record-selection command."""

    def test_records_usage(self, temp_usage_dir):
        """Should record usage for the path."""
        runner = CliRunner()
        result = runner.invoke(record_selection, ["--path", "/test/project/path"])

        assert result.exit_code == 0

        # Verify usage was recorded
        usage = UsageData()
        assert usage.get_usage_by_path("/test/project/path") == 1

    def test_increments_existing_usage(self, temp_usage_dir):
        """Should increment usage count for existing path."""
        # Pre-populate usage
        usage = UsageData()
        usage.add_usage("/test/project/path", count=5)
        usage.write_data()

        runner = CliRunner()
        result = runner.invoke(record_selection, ["--path", "/test/project/path"])

        assert result.exit_code == 0

        # Verify usage was incremented
        usage2 = UsageData()
        assert usage2.get_usage_by_path("/test/project/path") == 6

    def test_persists_data(self, temp_usage_dir):
        """Should persist data to file."""
        runner = CliRunner()
        runner.invoke(record_selection, ["--path", "/test/path"])

        # Create new UsageData instance to verify persistence
        usage = UsageData()
        assert usage.get_usage_by_path("/test/path") == 1

    def test_requires_path_option(self):
        """Should require --path option."""
        runner = CliRunner()
        result = runner.invoke(record_selection)

        assert result.exit_code != 0
        assert "Missing option '--path'" in result.output

    def test_accepts_nonexistent_path(self, temp_usage_dir):
        """Should accept paths that don't exist (for recording future projects)."""
        runner = CliRunner()
        result = runner.invoke(
            record_selection,
            ["--path", "/nonexistent/project/path"]
        )

        # Should succeed - we're just recording a string
        assert result.exit_code == 0

    def test_multiple_recordings(self, temp_usage_dir):
        """Should handle multiple recordings correctly."""
        runner = CliRunner()

        # Record same path multiple times
        for _ in range(3):
            result = runner.invoke(record_selection, ["--path", "/path/a"])
            assert result.exit_code == 0

        # Record different path
        runner.invoke(record_selection, ["--path", "/path/b"])

        usage = UsageData()
        assert usage.get_usage_by_path("/path/a") == 3
        assert usage.get_usage_by_path("/path/b") == 1
