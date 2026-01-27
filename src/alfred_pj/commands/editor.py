"""Editor detection command."""

import click

from alfred_pj.editors import Editors


@click.command()
@click.option("--path", required=True, type=click.Path(), help="Project path.")
def editor(path):
    """Determine and output the appropriate editor for a project."""
    click.echo(Editors().determine_editor(path))
