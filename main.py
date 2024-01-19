#!/usr/bin/python3
# encoding: utf-8

import json
import os
import glob
import sys
from shutil import which

sys.path.insert(1, os.path.abspath("./lib"))

from lib import click

response = {
    "items": [],
    "variables": {}
}

editors = {
    "code": {"name": "VS Code", "available": bool(which("code")), "icon": {"path": "images/vscode.svg"}},
    "idea": {"name": "IntelliJ IDEA", "available": bool(which("idea")), "icon": {"path": "images/idea.svg"}},
    "phpstorm": {"name": "PHPStorm", "available": bool(which("phpstorm")), "icon": {"path": "images/phpstorm.svg"}},
    "webstorm": {"name": "WebStorm", "available": bool(which("webstorm")), "icon": {"path": "images/webstorm.svg"}},
    "pycharm": {"name": "PyCharm", "available": bool(which("pycharm")), "icon": {"path": "images/pycharm.svg"}},
}

class ResponseItem:
    def __init__(self, title, subtitle, arg, icon, score=0):
        self.title = title
        self.subtitle = subtitle
        self.arg = arg
        self.match = title.lower() + " " + subtitle.lower()
        self.icon = icon
        self.score = score

@click.group()
def cli():
    pass

@cli.command()
@click.option('--paths', required=True, type=str, help='Project paths.')
def list(paths):
    projectPaths = paths.split(",");
    for projectPath in projectPaths:
        abspath = os.path.abspath(os.path.expanduser(projectPath))
        for folder in os.listdir(abspath):
            folderPath = os.path.join(abspath, folder);
            if os.path.isdir(folderPath):
                editor_code = determine_editor(folderPath)
                editor_info = editors[editor_code]
                response["items"].append(
                    ResponseItem(
                        folder,
                        "Open " + folderPath + " in " + editor_info["name"],
                        folderPath,
                        editor_info["icon"]
                    )
                )
    print(json.dumps(response, default=lambda o: o.__dict__))


@cli.command()
@click.option('--path', required=True, type=click.Path(), help='Project path.')
def ide(path):
    click.echo(determine_editor(path))

def get_first_available_editor(editor_codes):
    for editor_code in editor_codes:
        if editors[editor_code]["available"]:
            return editor_code
    return "code"

def determine_editor(path):
    if not os.path.isdir(os.path.join(path, '.idea')) and os.path.isdir(os.path.join(path, '.vscode')):
        return get_first_available_editor(['code'])
    if os.path.isfile(f"{path}/pom.xml"):
        # it has maven file, so it's java
        return get_first_available_editor(['idea'])
    elif os.path.isfile(f"{path}/composer.json") or len(glob.glob(f"{path}/*.php")) > 0:
        return get_first_available_editor(['phpstorm'])
    elif os.path.isfile(f"{path}/requirements.txt") or len(glob.glob(f"{path}/*.py")) > 0:
        return get_first_available_editor(['pycharm', 'code'])
    elif os.path.isfile(f"{path}/package.json") or len(glob.glob(f"{path}/*.js")) > 0:
        return get_first_available_editor(['webstorm', 'phpstorm', 'idea'])
    return "code"
    
if __name__ == '__main__':
    cli()
