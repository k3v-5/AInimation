"""
Challenger 2 Empirical Stress Test Suite for Milestone 1 (backend/core).

Empirically tests:
1. Thread safety of TelemetryBus.emit_threadsafe() under heavy concurrent thread calls.
2. Callback behavior and duplicate event detection under emit_threadsafe().
3. Async callback invocation from background threads.
4. CAS cache TTL eviction, prune logic (prune_expired, prune_lru), zero-byte files, and boundary conditions.
5. CAS cache concurrent put/get across multiple threads.
6. Settings and configuration edge cases, environment variable validation, and error handling.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import threading
import time
from typing import Dict, List, Optional
import pytest

from backend.core.cache import (
    CASCache,
    ContentAddressableStorage,
    canonical_params_hash,
    compute_composite_cache_key,
    hash_bytes,
    hash_file,
)
from backend.core.config import (
    AppConfig,
    Settings,
    get_config,
    get_settings,
    get_test_settings,
)
from backend.core.models import (
    AssetReadyEvent,
    AssetType,
    LogEvent,
    LogLevel,
    PlanProposalEvent,
    PlanStatus,
    PlanStep,
    ProgressEvent,
    TelemetryEvent,
)
from backend.core.telemetry import (
    TelemetryBus,
    reset_telemetry_bus,
)


@pytest.fixture(autouse=True)
def clean_environment() -> None:
    reset_telemetry_bus()
    get_settings.cache_clear()


# =============================================================================
# 1. TelemetryBus emit_threadsafe Stress & Concurrency Tests
# =============================================================================

def test_emit_threadsafe_heavy_concurrency_no_loop() -> None:
    """Verify emit_threadsafe across 50 concurrent threads without a running event loop."""
    bus = TelemetryBus(max_queue_size=1000, history_size=1000)
    received: List[TelemetryEvent] = []
    lock = threading.Lock()

    def cb(event: TelemetryEvent) -> None:
        with lock:
            received.append(event)

    bus.subscribe(cb)

    num_threads = 50
    events_per_thread = 20
    total_expected = num_threads * events_per_thread

    def worker(thread_idx: int) -> None:
        for i in range(events_per_thread):
            ev = LogEvent(
                level=LogLevel.INFO,
                message=f"T{thread_idx}-E{i}",
            )
            bus.emit_threadsafe(ev)

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Verify no events dropped in callbacks
    assert len(received) == total_expected, f"Expected {total_expected} callback events, got {len(received)}"
    # Verify history contains all events
    history = bus.get_history()
    assert len(history) == total_expected, f"Expected {total_expected} history events, got {len(history)}"


def test_emit_threadsafe_duplicate_emission_with_running_loop() -> None:
    """
    Empirically test whether emit_threadsafe duplicates events when an event loop is running.
    
    When an event loop is running on the main thread, emit_threadsafe:
    1. appends to _history
    2. invokes sync callbacks
    3. calls asyncio.run_coroutine_threadsafe(self.emit(event), loop)
    Inside emit(event):
    1. appends to _history AGAIN
    2. invokes sync callbacks AGAIN
    """
    async def _test() -> None:
        loop = asyncio.get_running_loop()
        bus = TelemetryBus(max_queue_size=500, history_size=500)
        bus.set_event_loop(loop)

        callback_received: List[TelemetryEvent] = []

        def cb(event: TelemetryEvent) -> None:
            callback_received.append(event)

        bus.subscribe(cb)

        async with bus._subscribe_context_manager(replay_history=False) as queue:
            # Emit from a background thread
            def bg_worker() -> None:
                ev = ProgressEvent(stage="bg_test", percentage=50.0, message="From thread")
                bus.emit_threadsafe(ev)

            bg_thread = threading.Thread(target=bg_worker)
            bg_thread.start()
            bg_thread.join()

            # Wait a moment for loop to process the threadsafe scheduled emit
            await asyncio.sleep(0.1)

            # Check queue received exactly 1 event
            assert queue.qsize() == 1, f"Queue expected 1 event, got {queue.qsize()}"

            # Check callback received count
            # CRITICAL CHECK: did callback receive event ONCE or TWICE?
            cb_count = len(callback_received)
            hist_count = len(bus.get_history())
            
            print(f"\n[DIAGNOSTIC] callback_count: {cb_count}, history_count: {hist_count}")
            assert cb_count == 1, f"BUG CONFIRMED: callback called {cb_count} times for a single emit_threadsafe call!"
            assert hist_count == 1, f"BUG CONFIRMED: history recorded {hist_count} events for a single emit_threadsafe call!"

def test_emit_threadsafe_heavy_concurrency_with_running_loop() -> None:
    """
    Stress-test 20 concurrent threads calling emit_threadsafe with an active event loop
    and an active async queue subscriber.
    """
    async def _test() -> None:
        loop = asyncio.get_running_loop()
        bus = TelemetryBus(max_queue_size=1000, history_size=1000)
        bus.set_event_loop(loop)

        callback_received: List[TelemetryEvent] = []
        lock = threading.Lock()

        def cb(event: TelemetryEvent) -> None:
            with lock:
                callback_received.append(event)

        bus.subscribe(cb)

        num_threads = 20
        events_per_thread = 10
        total_events = num_threads * events_per_thread

        async with bus._subscribe_context_manager(replay_history=False, max_queue_size=1000) as queue:
            def worker(t_idx: int) -> None:
                for i in range(events_per_thread):
                    ev = LogEvent(level=LogLevel.INFO, message=f"Concurrent-T{t_idx}-E{i}")
                    bus.emit_threadsafe(ev)

            threads = [threading.Thread(target=worker, args=(t,)) for t in range(num_threads)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            # Wait for event loop to flush all scheduled emit calls
            await asyncio.sleep(0.3)

            queue_count = queue.qsize()
            cb_count = len(callback_received)
            hist_count = len(bus.get_history())

            print(f"\n[DIAGNOSTIC] Concurrency loop test: emitted={total_events}, queue={queue_count}, cb={cb_count}, history={hist_count}")
            # The queue receives each scheduled emit once:
            assert queue_count == total_events, f"Queue received {queue_count}, expected {total_events}"
            # But history and callbacks were duplicated:
            assert cb_count == total_events, f"Callbacks duplicated: got {cb_count}, expected {total_events}"
            assert hist_count == total_events, f"History duplicated: got {hist_count}, expected {total_events}"

    asyncio.run(_test())


def test_emit_threadsafe_async_callback_from_thread() -> None:
    """
    Empirically test what happens if a callback is an async function
    and emit_threadsafe is called from a background thread.
    """
    async def _test() -> None:
        loop = asyncio.get_running_loop()
        bus = TelemetryBus()
        bus.set_event_loop(loop)

        async_received: List[str] = []

        async def async_cb(event: TelemetryEvent) -> None:
            async_received.append(str(event))

        bus.subscribe(async_cb)

        def bg_worker() -> None:
            ev = LogEvent(message="Async callback test")
            # This calls _invoke_callbacks(event) from the bg thread
            bus.emit_threadsafe(ev)

        bg_thread = threading.Thread(target=bg_worker)
        bg_thread.start()
        bg_thread.join()

        await asyncio.sleep(0.1)
        # Verify whether async_cb was executed without crashing
        print(f"\n[DIAGNOSTIC] async_received count: {len(async_received)}")

    asyncio.run(_test())


# =============================================================================
# 2. CAS Cache TTL, LRU, and File System Boundaries
# =============================================================================

def test_cas_cache_zero_byte_file(tmp_path: Path) -> None:
    """Verify CAS cache handles zero-byte files correctly."""
    cache = ContentAddressableStorage(base_dir=tmp_path / "cas")
    zero_file = tmp_path / "empty.bin"
    zero_file.write_bytes(b"")

    cached = cache.put_file(zero_file, namespace="empty_test")
    assert cached.metadata.file_size_bytes == 0
    assert cached.metadata.sha256_hash == hash_bytes(b"")

    retrieved = cache.get("empty_test", cached.cache_key)
    assert retrieved is not None
    assert retrieved.file_path.read_bytes() == b""


def test_cas_cache_concurrent_put_and_get(tmp_path: Path) -> None:
    """Stress-test concurrent read and write access across 20 threads."""
    cache = ContentAddressableStorage(base_dir=tmp_path / "cas")
    num_threads = 20
    keys: List[str] = []
    lock = threading.Lock()
    errors: List[Exception] = []

    def writer(t_idx: int) -> None:
        try:
            for i in range(10):
                data = f"thread_{t_idx}_data_{i}".encode("utf-8")
                res = cache.put_bytes(
                    data=data,
                    extension=".txt",
                    namespace="concurrent_ns",
                    params={"t": t_idx, "i": i},
                )
                with lock:
                    keys.append(res.cache_key)
        except Exception as e:
            with lock:
                errors.append(e)

    threads = [threading.Thread(target=writer, args=(t,)) for t in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, f"Concurrent put encountered errors: {errors}"
    assert len(keys) == num_threads * 10

    # Concurrent readers
    def reader(k: str) -> None:
        try:
            asset = cache.get("concurrent_ns", k)
            assert asset is not None
        except Exception as e:
            with lock:
                errors.append(e)

    with ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(reader, keys))

    assert len(errors) == 0, f"Concurrent get encountered errors: {errors}"


def test_cas_cache_prune_expired_corrupted_metadata(tmp_path: Path) -> None:
    """Verify prune_expired handles corrupted metadata JSON files cleanly."""
    cache = ContentAddressableStorage(base_dir=tmp_path / "cas")
    cached = cache.put_bytes(b"CORRUPT_TEST", ".bin", "corrupt_ns")

    # Corrupt the metadata file
    meta_path = cache._get_metadata_path(cache._get_entry_dir("corrupt_ns", cached.cache_key))
    assert meta_path.is_file()
    meta_path.write_text("{invalid json", encoding="utf-8")

    # prune_expired should catch Exception and prune it
    pruned = cache.prune_expired()
    assert pruned == 1
    assert not meta_path.exists()


def test_cas_cache_prune_lru_quota_zero(tmp_path: Path) -> None:
    """Verify prune_lru with target_max_bytes=0 clears all assets."""
    cache = ContentAddressableStorage(base_dir=tmp_path / "cas")
    cache.put_bytes(b"A" * 100, ".bin", "quota_ns")
    cache.put_bytes(b"B" * 200, ".bin", "quota_ns")

    assert cache.get_total_size_bytes() == 300
    pruned, freed = cache.prune_lru(target_max_bytes=0)
    assert pruned == 2
    assert freed == 300
    assert cache.get_total_size_bytes() == 0


def test_cas_cache_get_total_size_bytes_without_extension(tmp_path: Path) -> None:
    """
    Test whether get_total_size_bytes() counts assets without extensions.
    
    If put_file is used on a file named 'raw_artifact' (no extension),
    does get_total_size_bytes() correctly track its size?
    """
    cache = ContentAddressableStorage(base_dir=tmp_path / "cas")
    src = tmp_path / "raw_artifact"
    src.write_bytes(b"NO_EXTENSION_CONTENT_50_BYTES" + b"X" * 21)

    cached = cache.put_file(src, namespace="no_ext_ns")
    assert cached.file_path.name == "asset"

    total = cache.get_total_size_bytes()
    print(f"\n[DIAGNOSTIC] get_total_size_bytes for file without extension: {total}")
    assert total == 50, f"get_total_size_bytes() returned {total}, expected 50! rglob('asset.*') skips extensionless files."


# =============================================================================
# 3. Security, Boundaries & Path Traversal Tests
# =============================================================================

def test_cas_cache_path_traversal_boundaries(tmp_path: Path) -> None:
    """Test that namespaces with directory traversal are rejected with ValueError."""
    base_dir = tmp_path / "cas_sandbox"
    cache = ContentAddressableStorage(base_dir=base_dir)

    # Malicious namespace attempting to traverse up
    evil_ns = "../../escaped_dir"
    with pytest.raises(ValueError, match="Invalid namespace"):
        cache.put_bytes(b"MALICIOUS_PAYLOAD", ".txt", namespace=evil_ns)


def test_cas_cache_negative_ttl_behavior(tmp_path: Path) -> None:
    """
    Test how negative ttl_seconds is handled.
    If ttl_seconds=-10 is passed, does it expire immediately or treat as indefinite?
    """
    cache = ContentAddressableStorage(base_dir=tmp_path / "cas")
    cached = cache.put_bytes(b"DATA", ".bin", "ttl_ns", ttl_seconds=-10)

    # If ttl_seconds <= 0 returns False in is_expired, it will NEVER expire!
    retrieved = cache.get("ttl_ns", cached.cache_key)
    print(f"\n[DIAGNOSTIC] Negative TTL is_expired: {cached.metadata.is_expired}")
    assert retrieved is not None, "Negative TTL treated as indefinite"


# =============================================================================
# 4. Configuration & Environment Variable Edge Cases
# =============================================================================

def test_config_case_sensitivity_log_level(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that lowercase log_level is normalized to uppercase without errors."""
    monkeypatch.setenv("IANIMATION_LOG_LEVEL", "debug")
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.log_level == "DEBUG"


def test_config_invalid_port_types(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that non-numeric port strings raise ValidationError cleanly."""
    monkeypatch.setenv("IANIMATION_UE5_HTTP_PORT", "not_a_port")
    get_settings.cache_clear()

    with pytest.raises(Exception):
        get_settings()


def test_config_port_range_boundaries(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that negative or out-of-range port numbers raise ValidationError."""
    from pydantic import ValidationError

    monkeypatch.setenv("IANIMATION_UE5_HTTP_PORT", "-1")
    get_settings.cache_clear()
    with pytest.raises(ValidationError):
        get_settings()


def test_config_fallback_precedence(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify precedence: IANIMATION_FAL_KEY vs FAL_KEY.
    """
    monkeypatch.setenv("IANIMATION_FAL_KEY", "prefixed-key")
    monkeypatch.setenv("FAL_KEY", "unprefixed-key")
    get_settings.cache_clear()

    settings = get_settings()
    assert settings.fal_key == "prefixed-key"

