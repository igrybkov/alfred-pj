"""List projects command."""

import json
import os
from concurrent.futures import ThreadPoolExecutor

import click

from alfred_pj.cache import CacheStore
from alfred_pj.editors import Editors
from alfred_pj.response import ResponseItem
from alfred_pj.usage import UsageData
from alfred_pj.utils import logger


@click.command()
@click.option("--paths", required=True, type=str, help="Project paths.")
def list(paths):
    """List all projects from the specified paths."""
    usage = UsageData()
    cache = CacheStore()
    editors = Editors(cache=cache)  # created once, outside loop
    response = {"items": [], "variables": {}}
    home = os.path.expanduser("~")

    all_entries = []
    for projectPath in paths.split(","):
        try:
            abspath = os.path.abspath(os.path.expanduser(projectPath))
        except (OSError, ValueError) as e:
            logger.error(f"error expanding {projectPath}: {e}")
            continue
        if not os.path.isdir(abspath):
            logger.error(f"{abspath} is not a directory")
            continue
        with os.scandir(abspath) as it:  # single syscall per entry (vs listdir + isdir)
            for entry in it:
                if entry.name.startswith("."):
                    continue
                if entry.is_dir(follow_symlinks=True):
                    all_entries.append(entry)

    def process(entry):
        path = entry.path
        try:
            mtime = entry.stat().st_mtime
        except OSError:
            mtime = 0.0
        editor_code = cache.get_project(path, mtime)
        if editor_code is None:
            editor_code = editors.determine_editor(path)
            cache.set_project(path, editor_code, mtime)
        editor_info = editors.editors[editor_code]
        logger.debug(f"editor for {path} is {editor_info['name'] if editor_info else editor_code}")
        displayPath = path.replace(home, "~", 1)
        return ResponseItem(
            title=entry.name,
            subtitle="Open " + displayPath + " in " + editor_info["name"],
            arg=path,
            icon=editor_info["icon"],
            calls=usage.get_usage_by_path(path),
        )

    with ThreadPoolExecutor() as pool:  # parallel project detection
        items = [*pool.map(process, all_entries)]

    cache.save_projects()  # write cache once at the end

    items.sort(key=lambda x: x.calls, reverse=True)
    items.append(
        ResponseItem(
            title="> Clear usage data",
            subtitle="Reset project selection statistics",
            arg="__CLEAR_USAGE__",
            icon={"path": "icon.png"},
        )
    )
    items.append(
        ResponseItem(
            title="> Clear cache",
            subtitle="Clear project detection and editor availability caches",
            arg="__CLEAR_CACHE__",
            icon={"path": "icon.png"},
        )
    )
    response["items"] = items
    print(json.dumps(response, default=lambda o: o.__dict__))
