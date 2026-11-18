"""
Tests for World Cache System (UAF-81.56 Section 205).
"""

import pytest
from uaf.universal_world import (
    WorldCache,
    WorldCacheKey,
)


def test_world_cache():
    cache = WorldCache()
    assert cache.size() == 0


def test_cell_cache():
    cache = WorldCache()
    key = WorldCacheKey("HASH_01", "CELL_0_0")
    cache.put(key, {"data": 123})
    assert cache.get(key) == {"data": 123}


def test_profile_cache():
    cache = WorldCache()
    k1 = WorldCacheKey("HASH_01", "CELL_0_0", profile_hash="PROF_A")
    k2 = WorldCacheKey("HASH_01", "CELL_0_0", profile_hash="PROF_B")
    cache.put(k1, "VAL_A")
    cache.put(k2, "VAL_B")
    assert cache.get(k1) != cache.get(k2)


def test_asset_cache_dependency():
    cache = WorldCache()
    key = WorldCacheKey("HASH_01", "CELL_1_1", asset_library_hash="LIB_HASH_99")
    cache.put(key, "CACHED_PAYLOAD")
    assert cache.get(key) == "CACHED_PAYLOAD"


def test_cache_invalidation():
    cache = WorldCache()
    key = WorldCacheKey("HASH_01", "CELL_0_0")
    cache.put(key, "VALUE")
    invalidated = cache.invalidate_cell("CELL_0_0")
    assert invalidated == 1
    assert cache.get(key) is None


def test_cache_reuse():
    cache = WorldCache()
    key = WorldCacheKey("HASH_SHARED", "CELL_2_2")
    cache.put(key, "REUSABLE_DATA")
    # Repeated get calls
    for _ in range(5):
        assert cache.get(key) == "REUSABLE_DATA"
