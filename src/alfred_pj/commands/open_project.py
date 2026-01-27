"""Open project command."""

import os
import subprocess

import click

from alfred_pj.editors import Editors
from alfred_pj.usage import UsageData


@click.command()
@click.option("--path", required=True, type=click.Path(), help="Project path.")
def open_project(path):
    """Open project in the detected editor."""
    if path == "__CLEAR_USAGE__":
        usage = UsageData()
        usage.clear()
        usage.write_data()
        return
    if not os.path.exists(path):
        raise click.BadParameter(f"Path '{path}' does not exist.", param_hint="'--path'")
    editor_cmd = Editors().determine_editor(path)
    subprocess.run([editor_cmd, path])
