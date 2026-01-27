"""Tests for usage data tracking."""

import json
import pytest

from alfred_pj.usage import UsageData


class TestUsageData:
    """Tests for UsageData class."""

    def test_read_empty_data(self, temp_usage_dir):
        """Should return empty dict when no file exists."""
        usage = UsageData()
        assert usage.data == {}

    def test_write_and_read_data(self, temp_usage_dir):
        """Should persist and read data correctly."""
        usage = UsageData()
        usage.data = {"/path/to/project": 5}
        usage.write_data()

        # Create new instance to verify persistence
        usage2 = UsageData()
        assert usage2.data == {"/path/to/project": 5}

    def test_add_usage_new_path(self, temp_usage_dir):
        """Adding usage for new path should set count to 1."""
        usage = UsageData()
        usage.add_usage("/path/to/new/project")
        assert usage.data["/path/to/new/project"] == 1

    def test_add_usage_existing_path(self, temp_usage_dir):
        """Adding usage for existing path should increment count."""
        usage = UsageData()
        usage.add_usage("/path/to/project")
        usage.add_usage("/path/to/project")
        usage.add_usage("/path/to/project")
        assert usage.data["/path/to/project"] == 3

    def test_add_usage_custom_count(self, temp_usage_dir):
        """Should be able to add custom count."""
        usage = UsageData()
        usage.add_usage("/path/to/project", count=10)
        assert usage.data["/path/to/project"] == 10

    def test_add_usage_accumulates_custom_count(self, temp_usage_dir):
        """Custom count should accumulate with existing."""
        usage = UsageData()
        usage.add_usage("/path/to/project", count=5)
        usage.add_usage("/path/to/project", count=3)
        assert usage.data["/path/to/project"] == 8

    def test_clear_usage(self, temp_usage_dir):
        """Clear should remove all data."""
        usage = UsageData()
        usage.add_usage("/path/to/project1")
        usage.add_usage("/path/to/project2")
        usage.clear()
        assert usage.data == {}

    def test_get_usage_by_path_existing(self, temp_usage_dir):
        """Should return count for existing path."""
        usage = UsageData()
        usage.add_usage("/path/to/project", count=7)
        assert usage.get_usage_by_path("/path/to/project") == 7

    def test_get_usage_by_path_unknown(self, temp_usage_dir):
        """Should return 0 for unknown path."""
        usage = UsageData()
        assert usage.get_usage_by_path("/path/to/unknown") == 0

    def test_uses_alfred_data_dir_env(self, temp_usage_dir):
        """Should use alfred_workflow_data env when set."""
        usage = UsageData()
        assert str(temp_usage_dir) in usage.file

    def test_creates_data_dir_if_missing(self, tmp_path, monkeypatch):
        """Should create data directory if it doesn't exist."""
        data_dir = tmp_path / "new_alfred_data"
        monkeypatch.setenv("alfred_workflow_data", str(data_dir))

        usage = UsageData()
        assert data_dir.exists()

    def test_file_contains_valid_json(self, temp_usage_dir):
        """Written file should contain valid JSON."""
        usage = UsageData()
        usage.add_usage("/path/to/project", count=5)
        usage.write_data()

        with open(usage.file) as f:
            data = json.load(f)

        assert data == {"/path/to/project": 5}
