"""
Unit test suite for backend.core.cache.

Tests Content-Addressable Storage (CAS), SHA-256 keying, atomic disk writes,
metadata sidecars, TTL invalidation, and LRU pruning.
"""

from __future__ import annotations

from pathlib import Path
import time
import pytest

from backend.core.cache import (
    CASCache,
    ContentAddressableCache,
    ContentAddressableStorage,
    canonical_params_hash,
    compute_composite_cache_key,
    get_cache,
    hash_bytes,
    hash_file,
)


def test_canonical_params_hash_order_independence() -> None:
    params_a = {"resolution": 1024, "provider": "fal", "turbo": True, "seed": 42}
    params_b = {"seed": 42, "turbo": True, "provider": "fal", "resolution": 1024}
    assert canonical_params_hash(params_a) == canonical_params_hash(params_b)


def test_hash_bytes_and_file(tmp_path: Path) -> None:
    sample_data = b"Hello IANIMATION CAS Cache"
    expected_hash = hash_bytes(sample_data)

    test_file = tmp_path / "sample.bin"
    test_file.write_bytes(sample_data)

    assert hash_file(test_file) == expected_hash


def test_put_and_get_file(tmp_path: Path) -> None:
    cache = ContentAddressableStorage(base_dir=tmp_path / "cas")
    sample_mesh = tmp_path / "character.glb"
    sample_mesh.write_bytes(b"GLB_BINARY_STUB_DATA")

    cached = cache.put_file(
        source_path=sample_mesh,
        namespace="image_to_3d",
        params={"resolution": 1024, "provider": "tripo"},
        tags={"source": "test_runner"},
    )

    assert cached.file_path.is_file()
    assert cached.metadata.namespace == "image_to_3d"
    assert cached.metadata.tags["source"] == "test_runner"
    assert cached.metadata.params["resolution"] == 1024

    # Direct retrieval by cache_key
    retrieved = cache.get("image_to_3d", cached.cache_key)
    assert retrieved is not None
    assert retrieved.file_path.read_bytes() == b"GLB_BINARY_STUB_DATA"
    assert retrieved.metadata.file_size_bytes == len(b"GLB_BINARY_STUB_DATA")


def test_put_and_get_bytes(tmp_path: Path) -> None:
    cache = ContentAddressableStorage(base_dir=tmp_path / "cas")

    cached = cache.put_bytes(
        data=b"STEM_VOCALS_AUDIO_WAV",
        extension=".wav",
        namespace="audio_stems",
        original_filename="vocals.wav",
        params={"model": "htdemucs"},
    )

    assert cached.file_path.suffix == ".wav"
    assert cached.file_path.read_bytes() == b"STEM_VOCALS_AUDIO_WAV"

    retrieved = cache.get("audio_stems", cached.cache_key)
    assert retrieved is not None
    assert retrieved.metadata.original_filename == "vocals.wav"


def test_get_by_inputs(tmp_path: Path) -> None:
    cache = ContentAddressableStorage(base_dir=tmp_path / "cas")
    img = tmp_path / "concept.png"
    img.write_bytes(b"PNG_IMAGE_BYTES_12345")

    cached = cache.put_file(
        source_path=img,
        namespace="image_to_3d",
        params={"texture_res": 512},
    )

    hit = cache.get_by_inputs(
        namespace="image_to_3d",
        input_file_paths=[img],
        params={"texture_res": 512},
    )
    assert hit is not None
    assert hit.cache_key == cached.cache_key

    # Miss with different parameters
    miss = cache.get_by_inputs(
        namespace="image_to_3d",
        input_file_paths=[img],
        params={"texture_res": 1024},
    )
    assert miss is None


def test_cache_miss_returns_none(tmp_path: Path) -> None:
    cache = ContentAddressableStorage(base_dir=tmp_path / "cas")
    assert cache.get("nonexistent", "0000000000000000000000000000000000000000000000000000000000000000") is None


def test_ttl_expiration(tmp_path: Path) -> None:
    cache = ContentAddressableStorage(base_dir=tmp_path / "cas")

    cached = cache.put_bytes(
        data=b"EXPIRE_QUICKLY",
        extension=".bin",
        namespace="ephemeral",
        ttl_seconds=1,
    )

    # Immediately available
    assert cache.get("ephemeral", cached.cache_key) is not None

    # Wait for TTL to pass
    time.sleep(1.1)

    # Now expired and purged
    assert cache.get("ephemeral", cached.cache_key) is None


def test_invalidate_and_namespace(tmp_path: Path) -> None:
    cache = ContentAddressableStorage(base_dir=tmp_path / "cas")

    c1 = cache.put_bytes(b"DATA1", ".bin", "ns1")
    c2 = cache.put_bytes(b"DATA2", ".bin", "ns1")
    c3 = cache.put_bytes(b"DATA3", ".bin", "ns2")

    # Invalidate single key
    assert cache.invalidate("ns1", c1.cache_key) is True
    assert cache.get("ns1", c1.cache_key) is None
    assert cache.get("ns1", c2.cache_key) is not None

    # Invalidate whole namespace
    count = cache.invalidate_namespace("ns1")
    assert count >= 1
    assert cache.get("ns1", c2.cache_key) is None
    # Other namespace unaffected
    assert cache.get("ns2", c3.cache_key) is not None


def test_prune_lru(tmp_path: Path) -> None:
    # 50-byte quota
    cache = ContentAddressableStorage(base_dir=tmp_path / "cas", max_size_bytes=50)

    c1 = cache.put_bytes(b"A" * 25, ".bin", "lru_ns")
    time.sleep(0.02)
    c2 = cache.put_bytes(b"B" * 25, ".bin", "lru_ns")
    time.sleep(0.02)
    c3 = cache.put_bytes(b"C" * 25, ".bin", "lru_ns")

    # Total size is 75 bytes > 50 bytes quota
    assert cache.get_total_size_bytes() == 75

    pruned, freed = cache.prune_lru(target_max_bytes=50)
    assert pruned >= 1
    assert freed >= 25

    # Oldest asset (c1) should have been evicted
    assert cache.get("lru_ns", c1.cache_key) is None
    # Newest asset (c3) must still exist
    assert cache.get("lru_ns", c3.cache_key) is not None


def test_unified_put_method(tmp_path: Path) -> None:
    cache = ContentAddressableStorage(base_dir=tmp_path / "cas")

    # Put bytes
    asset_b = cache.put(b"BYTE_DATA", namespace="unified", extension=".txt")
    assert asset_b.file_path.is_file()

    # Put file
    src = tmp_path / "test.glb"
    src.write_bytes(b"FILE_DATA")
    asset_f = cache.put(src, namespace="unified")
    assert asset_f.file_path.is_file()


def test_aliases_and_global_instance(tmp_path: Path) -> None:
    assert CASCache is ContentAddressableStorage
    assert ContentAddressableCache is ContentAddressableStorage

    c = get_cache(base_dir=tmp_path / "global_cas")
    assert isinstance(c, ContentAddressableStorage)
