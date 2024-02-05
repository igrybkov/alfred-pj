#!/usr/bin/python3
# encoding: utf-8

import os
import glob
import sys
import json
from shutil import which
import logging

sys.path.insert(1, os.path.abspath("./lib"))

from lib import click


class Logger(logging.Logger):
    def __init__(self, name):
        super().__init__(name)
        self.addHandler(logging.StreamHandler(sys.stderr))
        self.setLevel(logging.DEBUG)
        self.log(logging.INFO, f"logger initiated")

logger = Logger(__name__)

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
        "goland": {"name": "GoLand", "available": bool(which("goland")), "icon": {"path": "images/goland.svg"}},
        "rustrover": {"name": "RustRover", "available": bool(which("rustrover")), "icon": {"path": "images/rustrover.svg"}},
    }

    def __init__(self):
        self.default_editor = os.environ['DEFAULT_EDITOR'] or "code"

    def get_editor(self, editor_code):
        return self.editors[editor_code]

    def get_first_available_editor(self, editor_codes):
        for editor_code in editor_codes:
            if self.editors[editor_code]["available"]:
                return editor_code
        return self.default_editor

    def get_editors_from_environment(self, env_var_name, defaults):
        editors = os.environ[env_var_name]
        if not editors:
            return defaults
        return map(lambda editor: editor.strip(), editors.lower().split(","))

    def determine_editor(self, path):
        # this project has existing vscode configuration
        # and no idea configuration, so we assume vscode is the default
        if not os.path.isdir(os.path.join(path, '.idea')) and os.path.isdir(os.path.join(path, '.vscode')):
            return self.get_first_available_editor(['code'])

        # it has maven file, so it's java
        if os.path.isfile(f"{path}/pom.xml"):
            return self.get_first_available_editor(self.get_editors_from_environment('EDITORS_JAVA', ['idea']))

        # it has composer file, so it's php
        if os.path.isfile(f"{path}/composer.json") or len(glob.glob(f"{path}/*.php")) > 0:
            return self.get_first_available_editor(self.get_editors_from_environment('EDITORS_PHP', ['phpstorm', 'idea', 'code']))

        # it has requirements file, so it's python
        if os.path.isfile(f"{path}/requirements.txt") or os.path.isdir(f"{path}/.venv") or len(glob.glob(f"{path}/*.py")) > 0:
            return self.get_first_available_editor(self.get_editors_from_environment('EDITORS_PYTHON', ['pycharm', 'idea', 'code']))

        # it has package.json file, so it's node/javascript
        if os.path.isfile(f"{path}/package.json") or len(glob.glob(f"{path}/*.js")) > 0:
            return self.get_first_available_editor(self.get_editors_from_environment('EDITORS_JAVASCRIPT', ['webstorm', 'phpstorm', 'idea', 'code']))

        # it has go.mod file, so it's golang
        if os.path.isfile(f"{path}/go.mod") or len(glob.glob(f"{path}/*.go")) > 0:
            return self.get_first_available_editor(self.get_editors_from_environment('EDITORS_GO', ['goland', 'idea', 'code']))

        # it has Cargo.toml file, so it's rust
        if os.path.isfile(f"{path}/Cargo.toml") or len(glob.glob(f"{path}/*.rs")) > 0:
            return self.get_first_available_editor(self.get_editors_from_environment('EDITORS_RUST', ['rustrover', 'idea', 'code']))

        # We don't know what it is, so we use the default editor
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
