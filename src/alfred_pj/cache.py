"""Cache management for alfred-pj."""

import contextlib
import json
import os
import random
import time

# Per-editor TTL ranges (seconds)
MISSING_TTL_RANGE = (24 * 3600, 48 * 3600)  # 24-48h for missing editors
AVAILABLE_TTL_RANGE = (48 * 3600, 96 * 3600)  # 48-96h for available editors


def _random_expiry(available: bool) -> float:
    """Return a future timestamp with a randomized TTL based on availability."""
    lo, hi = AVAILABLE_TTL_RANGE if available else MISSING_TTL_RANGE
    return time.time() + random.uniform(lo, hi)


class CacheStore:
    """Manages persistent caches for editor availability and project detection."""

    def __init__(self):
        cache_dir = os.getenv("alfred_workflow_cache") or "/tmp/alfred-pj-cache"
        os.makedirs(cache_dir, exist_ok=True)
        self._cache_dir = cache_dir
        self._editors_file = os.path.join(cache_dir, "editors_cache.json")
        self._projects_file = os.path.join(cache_dir, "projects_cache.json")
        self._projects: dict | None = None  # lazy-loaded

    # --- Editor availability cache ---

    def get_editors(self) -> dict | None:
        """Return cached editors dict if file exists, else None.

        Always returns cached data regardless of per-editor expiry —
        stale entries are refreshed one-at-a-time via get_most_expired_editor().
        """
        try:
            with open(self._editors_file) as f:
                data = json.load(f)
            return data["editors"]
        except (OSError, KeyError, json.JSONDecodeError):
            pass
        return None

    def set_editors(self, editors: dict) -> None:
        """Bulk-write all editors with randomized per-editor expiry."""
        stamped = {}
        for code, info in editors.items():
            stamped[code] = {**info, "expires_at": _random_expiry(info.get("available", False))}
        self._atomic_write(self._editors_file, {"editors": stamped})

    def get_most_expired_editor(self) -> str | None:
        """Return the editor code whose expires_at is most overdue, or None if all fresh."""
        try:
            with open(self._editors_file) as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return None

        editors = data.get("editors", {})
        if not editors:
            return None

        code = min(editors, key=lambda c: editors[c].get("expires_at", 0))
        if editors[code].get("expires_at", 0) < time.time():
            return code
        return None

    def update_editor(self, code: str, info: dict) -> None:
        """Read-modify-write a single editor entry with a new random expiry."""
        try:
            with open(self._editors_file) as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            data = {"editors": {}}

        data.setdefault("editors", {})[code] = {
            **info,
            "expires_at": _random_expiry(info.get("available", False)),
        }
        self._atomic_write(self._editors_file, data)

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
