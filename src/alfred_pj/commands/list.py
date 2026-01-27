"""List projects command."""

import json
import os

import click

from alfred_pj.editors import Editors
from alfred_pj.response import ResponseItem
from alfred_pj.usage import UsageData
from alfred_pj.utils import logger


@click.command()
@click.option("--paths", required=True, type=str, help="Project paths.")
def list(paths):
    """List all projects from the specified paths."""
    usage = UsageData()
    response = {"items": [], "variables": {}}

    projectPaths = paths.split(",")
    for projectPath in projectPaths:
        try:
            abspath = os.path.abspath(os.path.expanduser(projectPath))
        except (OSError, ValueError) as e:
            logger.error(f"error expanding {projectPath}: {e}")
            continue
        if not os.path.isdir(abspath):
            logger.error(f"{abspath} is not a directory")
            continue
        editors = Editors()
        for folder in os.listdir(abspath):
            if folder.startswith("."):
                continue
            folderPath = os.path.join(abspath, folder)
            if os.path.isdir(folderPath):
                editor_code = editors.determine_editor(folderPath)
                editor_info = editors.editors[editor_code]
                logger.debug(
                    f"editor for {folderPath} is {editor_info['name'] if editor_info else editor_code}"
                )
                response["items"].append(
                    ResponseItem(
                        title=folder,
                        subtitle="Open " + folderPath + " in " + editor_info["name"],
                        arg=folderPath,
                        icon=editor_info["icon"],
                        calls=usage.get_usage_by_path(folderPath),
                    )
                )
    response["items"] = sorted(response["items"], key=lambda item: item.calls, reverse=True)
    print(json.dumps(response, default=lambda o: o.__dict__))
