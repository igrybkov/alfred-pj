"""Open VS Code command."""

import subprocess

import click


@click.command()
@click.option("--path", required=True, type=click.Path(exists=True), help="Project path.")
def open_vscode(path):
    """Open project in VS Code."""
    subprocess.run(["code", path])
