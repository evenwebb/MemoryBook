"""Tests for the caching system."""
import time
import pytest
from app.core.cache import SimpleCache


@pytest.fixture
def cache():
    return SimpleCache()


class TestSimpleCache:
    def test_set_and_get(self, cache):
        cache.set("key", "value", ttl_seconds=60)
        assert cache.get("key") == "value"

    def test_get_missing_key(self, cache):
        assert cache.get("nonexistent") is None

    def test_expiry(self, cache):
        cache.set("key", "value", ttl_seconds=1)
        assert cache.get("key") == "value"
        time.sleep(1.1)
        assert cache.get("key") is None

    def test_delete(self, cache):
        cache.set("key", "value")
        cache.delete("key")
        assert cache.get("key") is None

    def test_delete_nonexistent(self, cache):
        # Should not raise
        cache.delete("nonexistent")

    def test_clear(self, cache):
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_overwrite(self, cache):
        cache.set("key", "old")
        cache.set("key", "new")
        assert cache.get("key") == "new"

    def test_different_types(self, cache):
        cache.set("int", 42)
        cache.set("list", [1, 2, 3])
        cache.set("dict", {"a": 1})
        assert cache.get("int") == 42
        assert cache.get("list") == [1, 2, 3]
        assert cache.get("dict") == {"a": 1}
