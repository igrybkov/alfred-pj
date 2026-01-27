#!/usr/bin/env python3
"""Release management CLI for alfred-pj workflow."""

import json
import plistlib
import re
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

import click

ROOT = Path(__file__).parent.parent
SRC_PATH = ROOT / "src"
PLIST_PATH = ROOT / "info.plist"
PYPROJECT_PATH = ROOT / "pyproject.toml"
WORKFLOW_NAME = "alfred-pj.alfredworkflow"

# Files to include in the workflow package
PACKAGE_FILES = [
    "images",
    "src",
    "app.sh",
    "pyproject.toml",
    "uv.lock",
    "LICENSE",
    "README.md",
    "info.plist",
]
PACKAGE_GLOBS = ["icon.*"]

# Directories and extensions to exclude from the package
EXCLUDE_DIRS = {"tests", "__pycache__", ".pytest_cache"}
EXCLUDE_EXTENSIONS = {".pyc"}


def _should_exclude(path: Path) -> bool:
    """Check if path should be excluded from package."""
    # Check if any parent directory is in exclude list
    if any(part in EXCLUDE_DIRS for part in path.parts):
        return True
    # Check file extension
    return path.suffix in EXCLUDE_EXTENSIONS


def get_plist() -> dict:
    """Read info.plist."""
    with open(PLIST_PATH, "rb") as f:
        return plistlib.load(f)


def write_plist(data: dict) -> None:
    """Write info.plist."""
    with open(PLIST_PATH, "wb") as f:
        plistlib.dump(data, f)


def get_detectors() -> list[dict]:
    """Import and return DETECTORS from cli module."""
    # Add src to path temporarily to import the module
    sys.path.insert(0, str(SRC_PATH))
    try:
        from alfred_pj.editors import DETECTORS

        return DETECTORS
    finally:
        sys.path.pop(0)


def sync_editor_defaults(write: bool = True) -> dict[str, str]:
    """Sync editor defaults from DETECTORS to info.plist.

    Args:
        write: If True, write changes to plist. If False, only report changes.

    Returns dict of variable -> new_value for any changes needed/made.
    """
    detectors = get_detectors()
    plist = get_plist()

    # Build mapping: env_var -> default_editors from DETECTORS
    detector_defaults = {}
    for detector in detectors:
        env = detector.get("env")
        editors = detector.get("editors", [])
        if not env or not editors:
            continue

        # env can be a string or list of strings
        env_vars = [env] if isinstance(env, str) else env
        default_value = ",".join(editors)

        for env_var in env_vars:
            # Only set if not already defined (first detector wins)
            if env_var not in detector_defaults:
                detector_defaults[env_var] = default_value

    # Update plist user configuration
    changes = {}
    config_list = plist.get("userconfigurationconfig", [])

    for config_item in config_list:
        variable = config_item.get("variable", "")
        if variable in detector_defaults:
            current = config_item.get("config", {}).get("default", "")
            new_value = detector_defaults[variable]
            if current != new_value:
                config_item["config"]["default"] = new_value
                changes[variable] = new_value

    if changes and write:
        write_plist(plist)

    return changes


def get_version() -> str:
    """Get current version from info.plist."""
    return get_plist()["version"]


def set_version(version: str) -> None:
    """Set version in info.plist and pyproject.toml."""
    # Update info.plist
    plist = get_plist()
    plist["version"] = version
    write_plist(plist)

    # Update pyproject.toml
    content = PYPROJECT_PATH.read_text()
    content = re.sub(r'^version = ".*"', f'version = "{version}"', content, flags=re.MULTILINE)
    PYPROJECT_PATH.write_text(content)


def bump_version(bump_type: str) -> str:
    """Bump version and return new version string."""
    current = get_version()
    parts = [int(p) for p in current.split(".")]

    # Ensure we have at least 3 parts
    while len(parts) < 3:
        parts.append(0)

    if bump_type == "major":
        parts[0] += 1
        parts[1] = 0
        parts[2] = 0
    elif bump_type == "minor":
        parts[1] += 1
        parts[2] = 0
    elif bump_type == "patch":
        parts[2] += 1
    else:
        raise click.ClickException(f"Invalid bump type: {bump_type}")

    return ".".join(str(p) for p in parts)


def get_alfred_workflows_path() -> Path:
    """Get Alfred workflows directory path."""
    prefs_path = Path.home() / "Library/Application Support/Alfred/prefs.json"
    if not prefs_path.exists():
        raise click.ClickException("Could not find Alfred config. Make sure Alfred is installed.")

    with open(prefs_path) as f:
        prefs = json.load(f)

    return Path(prefs["current"]) / "workflows"


@click.group()
def cli():
    """Release management for alfred-pj workflow."""
    pass


@cli.command()
@click.argument("version", required=False)
@click.option(
    "--bump",
    type=click.Choice(["patch", "minor", "major"]),
    help="Bump version by type instead of setting explicitly.",
)
def version(version: str | None, bump: str | None):
    """Get or set workflow version.

    If no arguments provided, prints current version.
    If VERSION provided, sets that exact version.
    If --bump provided, increments by that amount.
    """
    if version and bump:
        raise click.ClickException("Cannot specify both VERSION and --bump")

    if version is None and bump is None:
        click.echo(get_version())
        return

    current = get_version()

    # Strip leading 'v' if present when version is provided explicitly
    new_version = bump_version(bump) if bump else version.lstrip("vV")

    set_version(new_version)
    click.echo(f"{current} → {new_version}")


@cli.command()
@click.option("--output", "-o", type=click.Path(), help="Output path for the package.")
def package(output: str | None):
    """Create .alfredworkflow package."""
    output_path = Path(output) if output else ROOT / WORKFLOW_NAME

    # Remove existing package
    if output_path.exists():
        output_path.unlink()

    with ZipFile(output_path, "w") as zf:
        for item in PACKAGE_FILES:
            path = ROOT / item
            if path.is_dir():
                for file in path.rglob("*"):
                    if file.is_file() and not _should_exclude(file):
                        zf.write(file, file.relative_to(ROOT))
            elif path.exists():
                zf.write(path, path.relative_to(ROOT))

        for pattern in PACKAGE_GLOBS:
            for path in ROOT.glob(pattern):
                if path.is_file():
                    zf.write(path, path.relative_to(ROOT))

    click.echo(f"Created {output_path}")


@cli.command()
def link():
    """Link workflow to Alfred for development."""
    workflows_path = get_alfred_workflows_path()
    link_path = workflows_path / ROOT.name

    if link_path.exists():
        if link_path.is_symlink():
            click.echo(f"Already linked: {link_path}")
            return
        raise click.ClickException(f"Path exists and is not a symlink: {link_path}")

    link_path.symlink_to(ROOT)
    click.echo(f"Linked {ROOT} → {link_path}")


@cli.command()
def unlink():
    """Unlink workflow from Alfred."""
    workflows_path = get_alfred_workflows_path()
    link_path = workflows_path / ROOT.name

    if not link_path.exists():
        click.echo("Not linked")
        return

    if not link_path.is_symlink():
        raise click.ClickException(f"Path is not a symlink: {link_path}")

    link_path.unlink()
    click.echo(f"Unlinked {link_path}")


@cli.command("sync-defaults")
@click.option(
    "--check",
    is_flag=True,
    help="Check if sync is needed without making changes. Exits 1 if out of sync.",
)
def sync_defaults(check: bool):
    """Sync editor defaults from code to info.plist.

    Reads DETECTORS from cli.py and updates the default editor
    preferences in info.plist to match.
    """
    changes = sync_editor_defaults(write=not check)
    if changes:
        if check:
            click.echo("Defaults out of sync in info.plist:")
            for var, value in sorted(changes.items()):
                click.echo(f"  {var}: should be {value}")
            raise SystemExit(1)
        else:
            click.echo("Updated defaults in info.plist:")
            for var, value in sorted(changes.items()):
                click.echo(f"  {var}: {value}")
    else:
        click.echo("All defaults already in sync")


@cli.command()
def update():
    """Package and open workflow for manual update."""
    ctx = click.get_current_context()
    ctx.invoke(package)
    subprocess.run(["open", str(ROOT / WORKFLOW_NAME)], check=True)


@cli.command()
@click.argument("bump_type", type=click.Choice(["patch", "minor", "major"]))
@click.option("--draft/--no-draft", default=True, help="Create as draft release.")
@click.option("--dry-run", is_flag=True, help="Show what would be done without doing it.")
def release(bump_type: str, draft: bool, dry_run: bool):
    """Create a new release.

    Bumps version, commits, tags, pushes, packages, and creates GitHub release.
    Must be on main branch with clean working tree.
    """
    # Check for clean working tree
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    if result.stdout.strip():
        raise click.ClickException("Working tree is not clean. Commit or stash changes first.")

    # Check branch
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    branch = result.stdout.strip()
    if branch != "main":
        raise click.ClickException(f"Must be on main branch (currently on {branch})")

    # Bump version
    current = get_version()
    new_version = bump_version(bump_type)
    tag = f"v{new_version}"

    click.echo(f"Version: {current} → {new_version}")
    click.echo(f"Tag: {tag}")

    if dry_run:
        click.echo("Dry run - stopping here")
        return

    # Sync editor defaults from code to plist
    click.echo("Syncing editor defaults...")
    default_changes = sync_editor_defaults()
    if default_changes:
        click.echo("Updated defaults:")
        for var, value in sorted(default_changes.items()):
            click.echo(f"  {var}: {value}")
    else:
        click.echo("Defaults already in sync")

    # Update version
    set_version(new_version)

    # Regenerate lock file
    click.echo("Regenerating lock file...")
    subprocess.run(["uv", "lock"], cwd=ROOT, check=True)

    # Git operations
    subprocess.run(["git", "add", "info.plist", "pyproject.toml", "uv.lock"], cwd=ROOT, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"Bump version to {new_version}"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(["git", "tag", "-s", tag, "-m", tag], cwd=ROOT, check=True)
    subprocess.run(["git", "push", "--follow-tags", "origin", "main"], cwd=ROOT, check=True)

    # Package
    ctx = click.get_current_context()
    ctx.invoke(package)

    # Create GitHub release
    gh_args = ["gh", "release", "create", tag, str(ROOT / WORKFLOW_NAME)]
    if draft:
        gh_args.append("--draft")
    gh_args.extend(["--generate-notes", "--latest"])

    subprocess.run(gh_args, cwd=ROOT, check=True)
    click.echo(f"Release {tag} created!")


if __name__ == "__main__":
    cli()
