#!/usr/bin/env python3
"""Alfred workflow CLI for opening projects in appropriate editors."""

import click

from alfred_pj.commands import (
    clear_cache,
    clear_usage,
    debug,
    editor,
    list,
    open_finder,
    open_github,
    open_project,
    open_terminal,
    open_vscode,
    record_selection,
)


@click.group()
def cli():
    pass


cli.add_command(list)
cli.add_command(editor)
cli.add_command(record_selection)
cli.add_command(clear_cache)
cli.add_command(clear_usage)
cli.add_command(debug)
cli.add_command(open_project)
cli.add_command(open_vscode)
cli.add_command(open_terminal)
cli.add_command(open_github)
cli.add_command(open_finder)


if __name__ == "__main__":
    cli()
