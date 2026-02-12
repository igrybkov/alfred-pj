"""Usage data tracking for project selection frequency."""

import json
import os
import tempfile


class UsageData:
    def __init__(self):
        # alfred_workflow_data is set by Alfred in lowercase
        alfred_data_dir = os.getenv("alfred_workflow_data")
        if not alfred_data_dir:
            # Fallback for running outside Alfred
            alfred_data_dir = os.path.join(tempfile.gettempdir(), "alfred-pj")
        if not os.path.isdir(alfred_data_dir):
            os.makedirs(alfred_data_dir, exist_ok=True)
        usage_file = os.path.join(alfred_data_dir, "usage.json")
        self.file = usage_file
        self.data = self.read_data()

    def read_data(self):
        if os.path.isfile(self.file):
            with open(self.file) as f:
                return json.load(f)
        return {}

    def write_data(self):
        with open(self.file, "w+") as f:
            json.dump(self.data, f)

    def add_usage(self, path, count=1):
        self.data[path] = self.data[path] + count if path in self.data else count

    def clear(self):
        self.data = {}

    def get_usage_by_path(self, path):
        return self.data.get(path, 0)
