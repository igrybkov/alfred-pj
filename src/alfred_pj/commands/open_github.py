"""Open GitHub command."""

import subprocess

import click


@click.command()
@click.option("--path", required=True, type=click.Path(exists=True), help="Project path.")
def open_github(path):
    """Open GitHub page for the project."""
    subprocess.run(["gh", "browse"], cwd=path)
