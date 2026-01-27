"""Open Finder command."""

import subprocess

import click


@click.command()
@click.option("--path", required=True, type=click.Path(exists=True), help="Project path.")
def open_finder(path):
    """Open project in Finder."""
    subprocess.run(["open", path])
