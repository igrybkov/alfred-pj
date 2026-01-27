"""Tests for clear-usage command."""

from click.testing import CliRunner

from alfred_pj.commands.clear_usage import clear_usage
from alfred_pj.usage import UsageData


class TestClearUsageCommand:
    """Tests for the clear-usage command."""

    def test_clears_all_usage(self, temp_usage_dir):
        """Should clear all usage data."""
        # Pre-populate usage
        usage = UsageData()
        usage.add_usage("/path/1", count=5)
        usage.add_usage("/path/2", count=10)
        usage.write_data()

        runner = CliRunner()
        result = runner.invoke(clear_usage)

        assert result.exit_code == 0

        # Verify data was cleared
        usage2 = UsageData()
        assert usage2.data == {}

    def test_persists_cleared_state(self, temp_usage_dir):
        """Should persist the cleared state to file."""
        # Pre-populate usage
        usage = UsageData()
        usage.add_usage("/path/1", count=5)
        usage.write_data()

        runner = CliRunner()
        runner.invoke(clear_usage)

        # Create new instance to verify file was updated
        usage2 = UsageData()
        assert usage2.get_usage_by_path("/path/1") == 0

    def test_handles_empty_data(self, temp_usage_dir):
        """Should handle clearing already empty data."""
        runner = CliRunner()
        result = runner.invoke(clear_usage)

        assert result.exit_code == 0

        usage = UsageData()
        assert usage.data == {}

    def test_no_arguments_required(self, temp_usage_dir):
        """Should not require any arguments."""
        runner = CliRunner()
        result = runner.invoke(clear_usage)

        assert result.exit_code == 0
