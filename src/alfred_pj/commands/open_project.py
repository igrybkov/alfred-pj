"""Open project command."""

import subprocess

import click

from alfred_pj.editors import Editors


@click.command()
@click.option("--path", required=True, type=click.Path(exists=True), help="Project path.")
def open_project(path):
    """Open project in the detected editor."""
    editor_cmd = Editors().determine_editor(path)
    subprocess.run([editor_cmd, path])
