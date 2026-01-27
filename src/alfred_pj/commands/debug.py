"""Debug command to troubleshoot editor detection."""

import os

import click

from alfred_pj.editors import DETECTORS, EDITOR_DEFS, Editors
from alfred_pj.utils import which


@click.command()
@click.option("--path", help="Path to test detection for")
def debug(path: str | None):
    """Debug editor detection and environment."""
    click.echo("=== Environment ===")
    click.echo(f"PATH: {os.environ.get('PATH', 'not set')[:100]}...")
    click.echo(f"HOME: {os.environ.get('HOME', 'not set')}")
    click.echo()

    click.echo("=== Predefined Editor Availability ===")
    editors = Editors()
    for name, info in editors.editors.items():
        location = which(name) or "not found"
        click.echo(f"  {name}: available={info['available']} ({location})")
    click.echo()

    if path:
        click.echo(f"=== Detection for {path} ===")
        for detector in DETECTORS:
            if editors._matches_detector(path, detector):
                click.echo(f"Matched detector: {detector['name']}")
                click.echo(f"  Env var: {detector.get('env')}")
                click.echo(f"  Default editors: {detector.get('editors')}")
                env_editors = editors.get_editors_from_environment(
                    detector.get("env"), detector["editors"]
                )
                click.echo(f"  Resolved editors: {env_editors}")
                result = editors.determine_editor(path)
                click.echo(f"  Final editor: {result}")
                # Show if any dynamic editors were registered
                dynamic = {k: v for k, v in editors.editors.items() if k not in EDITOR_DEFS}
                if dynamic:
                    click.echo()
                    click.echo("=== Dynamic Editors Registered ===")
                    for name, info in dynamic.items():
                        location = which(name) or "not found"
                        click.echo(f"  {name}: available={info['available']} ({location})")
                break
        else:
            click.echo("No detector matched, using default")
            click.echo(f"  Final editor: {editors.default_editor}")
