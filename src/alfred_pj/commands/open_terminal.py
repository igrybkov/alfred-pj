"""Open terminal command."""

import click

from alfred_pj.terminals import Terminals
from alfred_pj.utils import logger


@click.command()
@click.option("--path", required=True, type=click.Path(exists=True), help="Project path.")
def open_terminal(path):
    """Open terminal and cd to project directory.

    Supports: Ghostty, WezTerm, iTerm, Terminal (in priority order).
    """
    terminal = Terminals.get_available_terminal()
    logger.debug(f"Using terminal: {terminal['name']}")
    terminal["open"](path)
