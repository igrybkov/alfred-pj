"""Clear usage command."""

import click

from alfred_pj.usage import UsageData


@click.command()
def clear_usage():
    """Clear all usage statistics."""
    usage = UsageData()
    usage.clear()
    usage.write_data()
