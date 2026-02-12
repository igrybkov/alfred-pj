"""Tests for CacheStore."""

import json
import time

import pytest

from alfred_pj.cache import CacheStore


@pytest.fixture
def cache(tmp_path, monkeypatch):
    """Provide a CacheStore backed by a temporary directory."""
    monkeypatch.setenv("alfred_workflow_cache", str(tmp_path))
    return CacheStore()


class TestEditorCache:
    def test_get_editors_returns_none_when_missing(self, cache):
        """No cache file → None."""
        assert cache.get_editors() is None

    def test_get_editors_returns_cached_when_fresh(self, cache):
        """Fresh timestamp → returns stored dict."""
        editors = {"code": {"name": "VS Code", "available": True}}
        cache.set_editors(editors)
        result = cache.get_editors()
        assert result == editors

    def test_get_editors_returns_none_when_stale(self, cache):
        """Expired timestamp → None."""
        editors = {"code": {"name": "VS Code", "available": True}}
        # Write with a timestamp that is older than TTL
        stale_data = {"timestamp": time.time() - CacheStore.EDITORS_TTL - 1, "editors": editors}
        with open(cache._editors_file, "w") as f:
            json.dump(stale_data, f)
        assert cache.get_editors() is None

    def test_set_and_get_editors_roundtrip(self, cache):
        """set_editors followed by get_editors returns the same data."""
        editors = {
            "code": {"name": "VS Code", "available": True},
            "pycharm": {"name": "PyCharm", "available": False},
        }
        cache.set_editors(editors)
        assert cache.get_editors() == editors


class TestProjectCache:
    def test_get_project_miss_on_different_mtime(self, cache):
        """Cached entry with different mtime → None."""
        cache.set_project("/some/path", "code", 1000.0)
        assert cache.get_project("/some/path", 9999.0) is None

    def test_get_project_hit_on_same_mtime(self, cache):
        """Cached entry with matching mtime → editor code."""
        cache.set_project("/some/path", "pycharm", 1234.5)
        assert cache.get_project("/some/path", 1234.5) == "pycharm"

    def test_get_project_miss_on_unknown_path(self, cache):
        """Unknown path → None."""
        assert cache.get_project("/unknown/path", 0.0) is None

    def test_save_projects_persists_to_disk(self, cache, tmp_path, monkeypatch):
        """save_projects writes data; a new CacheStore instance reads it back."""
        cache.set_project("/my/project", "code", 42.0)
        cache.save_projects()

        # New instance reads the same data
        monkeypatch.setenv("alfred_workflow_cache", str(tmp_path))
        cache2 = CacheStore()
        assert cache2.get_project("/my/project", 42.0) == "code"

    def test_save_projects_is_atomic(self, cache, tmp_path):
        """Verify that .tmp file is not left behind after save."""
        cache.set_project("/proj", "code", 1.0)
        cache.save_projects()
        tmp_file = cache._projects_file + ".tmp"
        assert not __import__("os").path.exists(tmp_file)


class TestCacheClear:
    def test_clear_removes_cache_files(self, cache):
        """clear() deletes both cache files."""
        import os

        cache.set_editors({"code": {"available": True}})
        cache.set_project("/p", "code", 1.0)
        cache.save_projects()

        assert os.path.exists(cache._editors_file)
        assert os.path.exists(cache._projects_file)

        cache.clear()

        assert not os.path.exists(cache._editors_file)
        assert not os.path.exists(cache._projects_file)

    def test_clear_resets_in_memory_projects(self, cache):
        """clear() resets the in-memory projects dict."""
        cache.set_project("/p", "code", 1.0)
        cache.clear()
        assert cache.get_project("/p", 1.0) is None


class TestCacheEnvVar:
    def test_cache_uses_alfred_workflow_cache_env(self, tmp_path, monkeypatch):
        """CacheStore respects the alfred_workflow_cache env var."""
        custom_dir = tmp_path / "custom_cache"
        custom_dir.mkdir()
        monkeypatch.setenv("alfred_workflow_cache", str(custom_dir))

        store = CacheStore()
        assert store._cache_dir == str(custom_dir)

    def test_cache_falls_back_to_tmp_when_no_env(self, monkeypatch):
        """CacheStore falls back to /tmp/alfred-pj-cache when env var absent."""
        monkeypatch.delenv("alfred_workflow_cache", raising=False)
        store = CacheStore()
        assert store._cache_dir == "/tmp/alfred-pj-cache"
