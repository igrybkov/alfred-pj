"""Cache management for alfred-pj."""

import contextlib
import json
import os
import time


class CacheStore:
    """Manages persistent caches for editor availability and project detection."""

    EDITORS_TTL = 86400  # 24 hours

    def __init__(self):
        cache_dir = os.getenv("alfred_workflow_cache") or "/tmp/alfred-pj-cache"
        os.makedirs(cache_dir, exist_ok=True)
        self._cache_dir = cache_dir
        self._editors_file = os.path.join(cache_dir, "editors_cache.json")
        self._projects_file = os.path.join(cache_dir, "projects_cache.json")
        self._projects: dict | None = None  # lazy-loaded

    # --- Editor availability cache ---

    def get_editors(self) -> dict | None:
        """Return cached editors dict if fresh, else None."""
        try:
            with open(self._editors_file) as f:
                data = json.load(f)
            if time.time() - data.get("timestamp", 0) < self.EDITORS_TTL:
                return data["editors"]
        except (OSError, KeyError, json.JSONDecodeError):
            pass
        return None

    def set_editors(self, editors: dict) -> None:
        """Atomically write editors cache."""
        self._atomic_write(self._editors_file, {"timestamp": time.time(), "editors": editors})

    # --- Project detection cache ---

    def load_projects(self) -> dict:
        """Return full projects dict, lazy-loaded and memoized."""
        if self._projects is None:
            try:
                with open(self._projects_file) as f:
                    self._projects = json.load(f)
            except (OSError, json.JSONDecodeError):
                self._projects = {}
        return self._projects

    def get_project(self, path: str, mtime: float) -> str | None:
        """Return cached editor_code if path exists in cache with matching mtime."""
        projects = self.load_projects()
        entry = projects.get(path)
        if entry and entry.get("mtime") == mtime:
            return entry.get("editor")
        return None

    def set_project(self, path: str, editor_code: str, mtime: float) -> None:
        """Store entry in in-memory dict (call save_projects to persist)."""
        projects = self.load_projects()
        projects[path] = {"editor": editor_code, "mtime": mtime}

    def save_projects(self) -> None:
        """Atomically write projects cache to disk."""
        if self._projects is not None:
            self._atomic_write(self._projects_file, self._projects)

    # --- Lifecycle ---

    def clear(self) -> None:
        """Delete both cache files."""
        for path in (self._editors_file, self._projects_file):
            with contextlib.suppress(OSError):
                os.remove(path)
        self._projects = None

    # --- Helpers ---

    def _atomic_write(self, path: str, data: dict) -> None:
        """Write data atomically via a temp file + rename."""
        tmp = path + ".tmp"
        try:
            with open(tmp, "w") as f:
                json.dump(data, f)
            os.replace(tmp, path)
        except OSError:
            with contextlib.suppress(OSError):
                os.remove(tmp)
