"""Clear cache command."""

import os
import shutil

import click

from alfred_pj.usage import UsageData


@click.command()
@click.option("--usage/--no-usage", default=True, help="Clear usage statistics")
@click.option("--alfred/--no-alfred", default=True, help="Clear Alfred cache")
def clear_cache(usage: bool, alfred: bool):
    """Clear workflow cache and usage data."""
    cleared = []

    if usage:
        usage_data = UsageData()
        usage_data.clear()
        usage_data.write_data()
        cleared.append("usage statistics")

    if alfred:
        # Alfred cache directory
        cache_dir = os.getenv("alfred_workflow_cache")
        if cache_dir and os.path.isdir(cache_dir):
            shutil.rmtree(cache_dir)
            os.makedirs(cache_dir, exist_ok=True)
            cleared.append("Alfred cache")

    if cleared:
        click.echo(f"Cleared: {', '.join(cleared)}")
    else:
        click.echo("Nothing to clear")
