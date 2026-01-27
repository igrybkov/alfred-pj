"""Record selection command."""

import click

from alfred_pj.usage import UsageData


@click.command()
@click.option("--path", required=True, type=click.Path(), help="Project path.")
def record_selection(path):
    """Record a project selection for usage tracking."""
    if path == "__CLEAR_USAGE__":
        return
    usage = UsageData()
    usage.add_usage(path)
    usage.write_data()
