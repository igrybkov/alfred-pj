#!/usr/bin/python3
# encoding: utf-8

import json
import os
import glob
import sys
import json
from shutil import which

sys.path.insert(1, os.path.abspath("./lib"))

from lib import click

usage_data = None

response = {
    "items": [],
    "variables": {}
}


class UsageData:
    def __init__(self):
        alfred_data_dir = os.getenv('alfred_workflow_data')
        if not os.path.isdir(alfred_data_dir):
            os.mkdir(alfred_data_dir)
        usage_file = os.path.join(alfred_data_dir, 'usage.json')
        self.file = usage_file
        self.data = self.read_data()

    def read_data(self):
        if os.path.isfile(self.file):
            with open(self.file, 'r') as f:
                return json.load(f)
        return {}

    def write_data(self):
        with open(self.file, 'w+') as f:
            json.dump(self.data, f)

    def add_usage(self, path, count=1):
        self.data[path] = self.data[path] + count if path in self.data else count

    def clear(self):
        self.data = {}

    def get_usage_by_path(self, path):
        return self.data[path] if path in self.data else 0


class Editors:
    editors = {
        "code": {"name": "VS Code", "available": bool(which("code")), "icon": {"path": "images/vscode.svg"}},
        "idea": {"name": "IntelliJ IDEA", "available": bool(which("idea")), "icon": {"path": "images/idea.svg"}},
        "phpstorm": {"name": "PHPStorm", "available": bool(which("phpstorm")), "icon": {"path": "images/phpstorm.svg"}},
        "webstorm": {"name": "WebStorm", "available": bool(which("webstorm")), "icon": {"path": "images/webstorm.svg"}},
        "pycharm": {"name": "PyCharm", "available": bool(which("pycharm")), "icon": {"path": "images/pycharm.svg"}},
    }

    def __init__(self):
        self.default_editor = "code"

    def get_editor(self, editor_code):
        return self.editors[editor_code]

    def get_first_available_editor(self, editor_codes):
        for editor_code in editor_codes:
            if self.editors[editor_code]["available"]:
                return editor_code
        return self.default_editor

    def determine_editor(self, path):
        if not os.path.isdir(os.path.join(path, '.idea')) and os.path.isdir(os.path.join(path, '.vscode')):
            return self.get_first_available_editor(['code'])
        if os.path.isfile(f"{path}/pom.xml"):
            # it has maven file, so it's java
            return self.get_first_available_editor(['idea'])
        elif os.path.isfile(f"{path}/composer.json") or len(glob.glob(f"{path}/*.php")) > 0:
            return self.get_first_available_editor(['phpstorm'])
        elif os.path.isfile(f"{path}/requirements.txt") or len(glob.glob(f"{path}/*.py")) > 0:
            return self.get_first_available_editor(['pycharm', 'code'])
        elif os.path.isfile(f"{path}/package.json") or len(glob.glob(f"{path}/*.js")) > 0:
            return self.get_first_available_editor(['webstorm', 'phpstorm', 'idea'])
        return self.default_editor


class ResponseItem:
    def __init__(self, title, subtitle, arg, icon, calls=0, score=0):
        self.title = title
        self.subtitle = subtitle
        self.arg = arg
        self.match = title.lower() + " " + subtitle.lower()
        self.icon = icon
        self.calls = calls
        self.score = score


@click.group()
def cli():
    pass


@cli.command()
@click.option('--paths', required=True, type=str, help='Project paths.')
def list(paths):
    usage = UsageData()

    projectPaths = paths.split(",");
    for projectPath in projectPaths:
        abspath = os.path.abspath(os.path.expanduser(projectPath))
        for folder in os.listdir(abspath):
            folderPath = os.path.join(abspath, folder);
            if os.path.isdir(folderPath):
                editors = Editors()
                editor_code = editors.determine_editor(folderPath)
                editor_info = editors.editors[editor_code]
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


@cli.command()
@click.option('--path', required=True, type=click.Path(), help='Project path.')
def editor(path):
    click.echo(Editors().determine_editor(path))

@cli.command()
@click.option('--path', required=True, type=click.Path(), help='Project path.')
def record_selection(path):
    usage = UsageData()
    usage.add_usage(path)
    usage.write_data()

@cli.command()
def clear_usage():
    usage = UsageData()
    usage.clear()
    usage.write_data()

if __name__ == '__main__':
    cli()
