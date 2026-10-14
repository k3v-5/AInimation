"""
Comprehensive Adversarial Stress Test Suite for Milestone 1 Iteration 2.

Authored by Challenger 1 (Iterative Empirical Verification).
Adversarially challenges:
1. TelemetryBus: high-throughput multithreaded / async concurrency, error isolation, slow consumers, SSE.
2. ContentAddressableStorage (CAS): path traversal fuzzing, Windows reserved device names, concurrent race conditions, LRU quota stress.
3. Settings: strict port boundaries, case-insensitive log level validation, path resolution, environment precedence.
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
from typing import Any, Dict, List, Set

import pytest
from pydantic import ValidationError

from backend.core.cache import (
    AssetMetadata,
    CachedAsset,
    ContentAddressableStorage,
    canonical_params_hash,
    compute_composite_cache_key,
    hash_bytes,
    hash_file,
)
from backend.core.config import Settings, get_test_settings
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
    FastMCPTelemetryBridge,
    TelemetryBus,
    emit_log_sync,
    emit_progress_sync,
    telemetry_sse_stream,
)


# =============================================================================
# 1. TELEMETRY BUS ADVERSARIAL STRESS TESTS
# =============================================================================

class TestTelemetryBusStress:
    """Stress-testing TelemetryBus under high concurrency and failure injection."""

    def test_emit_threadsafe_massive_concurrency_with_active_loop(self) -> None:
        """
        Launch 20 threads emitting 50 events each into an active event loop.
        Verify:
        - Exactly 1000 events received by queue subscriber.
        - Exactly 1000 callback invocations (NO duplicate calls).
        - No unhandled exceptions or thread deadlocks.
        """
        loop = asyncio.new_event_loop()
        loop_ready = threading.Event()

        def run_loop() -> None:
            asyncio.set_event_loop(loop)
            loop_ready.set()
            loop.run_forever()

        t_loop = threading.Thread(target=run_loop, daemon=True)
        t_loop.start()
        loop_ready.wait(timeout=2.0)

        bus = TelemetryBus(max_queue_size=2000, history_size=2000)
        bus.set_event_loop(loop)

        callback_counts: List[int] = []
        callback_lock = threading.Lock()

        def on_event(ev: TelemetryEvent) -> None:
            with callback_lock:
                callback_counts.append(1)

        bus.add_callback(on_event)

        # Set up an async subscriber queue inside the running loop
        async def create_subscriber() -> asyncio.Queue[TelemetryEvent]:
            q: asyncio.Queue[TelemetryEvent] = asyncio.Queue(maxsize=2000)
            bus.add_subscriber(q)
            return q

        sub_queue_future = asyncio.run_coroutine_threadsafe(create_subscriber(), loop)
        sub_queue = sub_queue_future.result(timeout=2.0)

        num_threads = 20
        events_per_thread = 50
        total_events = num_threads * events_per_thread

        def worker_emit(thread_id: int) -> None:
            for i in range(events_per_thread):
                event = ProgressEvent(
                    stage=f"worker_{thread_id}",
                    percentage=float(i * 2),
                    message=f"Event {thread_id}-{i}",
                )
                bus.emit_threadsafe(event)

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker_emit, tid) for tid in range(num_threads)]
            for f in futures:
                f.result(timeout=10.0)

        # Allow loop to process all scheduled events
        time.sleep(1.0)

        # Verify callback count
        with callback_lock:
            assert len(callback_counts) == total_events, (
                f"Expected {total_events} callbacks, got {len(callback_counts)}"
            )

        # Verify subscriber queue count
        async def count_queue_items(q: asyncio.Queue[TelemetryEvent]) -> int:
            return q.qsize()

        q_size = asyncio.run_coroutine_threadsafe(count_queue_items(sub_queue), loop).result(timeout=2.0)
        assert q_size == total_events, f"Expected {total_events} queued events, got {q_size}"

        # Cleanup
        loop.call_soon_threadsafe(loop.stop)
        t_loop.join(timeout=2.0)

    def test_callback_failure_isolation(self) -> None:
        """Verify faulty sync and async callbacks do not disrupt the bus or other subscribers."""
        async def _run() -> None:
            bus = TelemetryBus()
            success_events: List[str] = []

            def faulty_sync_callback(ev: TelemetryEvent) -> None:
                raise RuntimeError("Fatal explosion in sync callback")

            async def faulty_async_callback(ev: TelemetryEvent) -> None:
                raise ValueError("Fatal explosion in async callback")

            def good_callback(ev: TelemetryEvent) -> None:
                success_events.append(ev.type)

            bus.add_callback(faulty_sync_callback)
            bus.add_callback(faulty_async_callback)
            bus.add_callback(good_callback)

            event = LogEvent(message="Testing fault isolation", level=LogLevel.INFO)
            await bus.emit(event)

            # Allow scheduled async callbacks to resolve
            await asyncio.sleep(0.05)

            assert len(success_events) == 1
            assert success_events[0] == "log"

        asyncio.run(_run())

    def test_lossy_backpressure_drop_oldest(self) -> None:
        """Verify that when a subscriber queue is full, the oldest event is dropped and new event is accepted."""
        async def _run() -> None:
            bus = TelemetryBus(max_queue_size=3)
            async with bus.subscribe(replay_history=False, max_queue_size=3) as queue:
                # Emit 5 events into queue of capacity 3
                for i in range(5):
                    await bus.emit(ProgressEvent(stage="st", percentage=float(i), message=f"msg_{i}"))

                assert queue.qsize() == 3
                # Items remaining in queue should be the latest 3: 2, 3, 4
                items: List[ProgressEvent] = []
                while not queue.empty():
                    item = queue.get_nowait()
                    assert isinstance(item, ProgressEvent)
                    items.append(item)

                assert [item.message for item in items] == ["msg_2", "msg_3", "msg_4"]

        asyncio.run(_run())

    def test_sse_streaming_format_and_termination(self) -> None:
        """Verify telemetry_sse_stream formats SSE standard frames correctly with history replay."""
        async def _run() -> None:
            bus = TelemetryBus()
            # Emit an event prior to streaming with replay_history=True
            ev = LogEvent(message="SSE Test Message", level=LogLevel.WARNING, source="TestRunner")
            await bus.emit(ev)

            gen = telemetry_sse_stream(bus=bus, replay_history=True, heartbeat_seconds=0.1)

            # First event should be the replayed LogEvent
            sse_chunk = await gen.__anext__()
            assert sse_chunk.startswith("event: log\ndata: {")
            assert "SSE Test Message" in sse_chunk
            assert sse_chunk.endswith("\n\n")

            # Await next chunk which should be a keep-alive comment
            keep_alive_chunk = await gen.__anext__()
            assert keep_alive_chunk == ": keep-alive\n\n"

            await gen.aclose()

        asyncio.run(_run())

    def test_fastmcp_bridge_without_context(self) -> None:
        """Verify FastMCPTelemetryBridge operates cleanly when ctx is None."""
        async def _run() -> None:
            bus = TelemetryBus()
            bridge = FastMCPTelemetryBridge(ctx=None, bus=bus)

            progress = await bridge.report_progress(stage="audio", percentage=50.0, message="Processing")
            assert progress.stage == "audio"
            assert progress.percentage == 50.0

            log_info = await bridge.info("Info log")
            assert log_info.level == LogLevel.INFO

            log_warn = await bridge.warning("Warn log")
            assert log_warn.level == LogLevel.WARNING

            log_err = await bridge.error("Err log")
            assert log_err.level == LogLevel.ERROR

            history = bus.get_history()
            assert len(history) == 4

        asyncio.run(_run())


# =============================================================================
# 2. CAS CACHE ADVERSARIAL STRESS TESTS
# =============================================================================

class TestCASCacheStress:
    """Stress-testing ContentAddressableStorage for security, boundaries, and concurrency."""

    @pytest.mark.parametrize("bad_ns", [
        "",
        " ",
        "../",
        "ns/nested",
        "ns\\nested",
        "ns:colon",
        "ns*wildcard",
        "ns?question",
        "ns\x00null",
    ])
    def test_namespace_fuzzing_rejections(self, tmp_path: Path, bad_ns: str) -> None:
        """Verify malformed or invalid namespaces are rejected or sanitized."""
        cache = ContentAddressableStorage(base_dir=tmp_path / "cache")
        with pytest.raises(ValueError):
            cache.put_bytes(b"data", extension=".bin", namespace=bad_ns)
        with pytest.raises(ValueError):
            cache.invalidate_namespace(bad_ns)
        with pytest.raises(ValueError):
            cache.invalidate(namespace=bad_ns, cache_key="abc12345")
        # get() gracefully returns None
        assert cache.get(namespace=bad_ns, cache_key="abc12345") is None

    @pytest.mark.parametrize("bad_key", [
        "",
        "a",
        "ab",
        " ",
        "../escape",
        "..\\escape",
        "key/sub",
        "key\\sub",
        "key:bad",
        "key*bad",
        "key\x00bad",
    ])
    def test_cache_key_fuzzing_rejections(self, tmp_path: Path, bad_key: str) -> None:
        """Verify malformed or short cache keys (< 3 chars or bad characters) are rejected."""
        cache = ContentAddressableStorage(base_dir=tmp_path / "cache")
        with pytest.raises(ValueError):
            cache.put_bytes(b"data", extension=".bin", namespace="valid_ns", cache_key=bad_key)
        with pytest.raises(ValueError):
            cache.invalidate(namespace="valid_ns", cache_key=bad_key)
        # get() gracefully returns None
        assert cache.get(namespace="valid_ns", cache_key=bad_key) is None

    def test_path_traversal_boundaries_exhaustive(self, tmp_path: Path) -> None:
        """Exhaustive check on path traversal attack payloads."""
        cache = ContentAddressableStorage(base_dir=tmp_path / "cache")
        attack_keys = [
            "../../etc/passwd",
            "..\\..\\windows\\system32",
            "....//....//payload",
            "/absolute/root/escape",
            "C:\\Windows\\System32",
            "key/with/slashes",
            "key\\with\\backslashes",
            "key\x00nullbyte",
        ]
        for key in attack_keys:
            with pytest.raises(ValueError):
                cache.put_bytes(b"attack", extension=".bin", namespace="default", cache_key=key)
            with pytest.raises(ValueError):
                cache.invalidate(namespace="default", cache_key=key)
            assert cache.get(namespace="default", cache_key=key) is None

    def test_concurrent_atomic_put_identical_key(self, tmp_path: Path) -> None:
        """Simultaneously write the exact same asset key from 15 threads."""
        cache = ContentAddressableStorage(base_dir=tmp_path / "cache")
        payload = b"Identical Concurrent Payload Data"
        cache_key = "concurrent_key_identical_12345"

        errors: List[Exception] = []

        def worker() -> None:
            try:
                asset = cache.put_bytes(
                    data=payload,
                    extension=".bin",
                    namespace="concurrent_ns",
                    cache_key=cache_key,
                )
                assert asset.file_path.is_file()
                assert asset.metadata.file_size_bytes == len(payload)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(15)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        cached = cache.get("concurrent_ns", cache_key)
        assert cached is not None
        assert cached.file_path.read_bytes() == payload

    def test_lru_prune_quota_stress(self, tmp_path: Path) -> None:
        """Verify LRU correctly evicts older assets down to quota."""
        cache = ContentAddressableStorage(base_dir=tmp_path / "cache")
        # Put 5 assets of 1000 bytes each = 5000 bytes
        for i in range(5):
            cache.put_bytes(
                data=b"x" * 1000,
                extension=".dat",
                namespace="lru_ns",
                cache_key=f"asset_key_{i:04d}",
            )
            time.sleep(0.01)  # Ensure unique accessed_at timestamps

        assert cache.get_total_size_bytes() == 5000

        # Prune to 2500 bytes (should prune oldest 3 assets: 0, 1, 2)
        pruned_count, freed_bytes = cache.prune_lru(target_max_bytes=2500)
        assert pruned_count == 3
        assert freed_bytes == 3000
        assert cache.get_total_size_bytes() == 2000

        # Assets 0, 1, 2 should be gone; assets 3, 4 remain
        assert cache.get("lru_ns", "asset_key_0000") is None
        assert cache.get("lru_ns", "asset_key_0001") is None
        assert cache.get("lru_ns", "asset_key_0002") is None
        assert cache.get("lru_ns", "asset_key_0003") is not None
        assert cache.get("lru_ns", "asset_key_0004") is not None

    def test_canonical_params_hash_nested_paths_cross_platform(self) -> None:
        """Verify canonical_params_hash normalizes Windows vs Posix paths identically."""
        params_win = {
            "model_path": Path("models\\mesh.glb"),
            "texture": Path("textures\\albedo.png"),
            "steps": 50,
        }
        params_posix = {
            "model_path": Path("models/mesh.glb"),
            "texture": Path("textures/albedo.png"),
            "steps": 50,
        }
        hash_win = canonical_params_hash(params_win)
        hash_posix = canonical_params_hash(params_posix)
        assert hash_win == hash_posix, "Hashes between Windows and Posix paths must match"

    def test_params_serialization_roundtrip_with_pydantic_metadata(self, tmp_path: Path) -> None:
        """Verify AssetMetadata with Path params serializes and deserializes cleanly."""
        cache = ContentAddressableStorage(base_dir=tmp_path / "cache")
        params = {
            "path_param": Path("my/input/model.glb"),
            "num_param": 42,
            "float_param": 3.14,
            "bool_param": True,
            "none_param": None,
        }
        asset = cache.put_bytes(
            data=b"dummy",
            extension=".glb",
            namespace="param_test",
            params=params,
        )
        assert asset.file_path.is_file()

        # Retrieve and verify params are intact and posix-normalized
        retrieved = cache.get("param_test", asset.cache_key)
        assert retrieved is not None
        assert retrieved.metadata.params["path_param"] == "my/input/model.glb"
        assert retrieved.metadata.params["num_param"] == 42


# =============================================================================
# 3. SETTINGS & CONFIG ADVERSARIAL STRESS TESTS
# =============================================================================

class TestSettingsConfigStress:
    """Stress-testing Settings configuration, validation boundaries, and environment overrides."""

    @pytest.mark.parametrize("log_input,expected_enum", [
        ("debug", "DEBUG"),
        ("DEBUG", "DEBUG"),
        ("info", "INFO"),
        ("INFO", "INFO"),
        ("warning", "WARNING"),
        ("WARNING", "WARNING"),
        ("error", "ERROR"),
        ("ERROR", "ERROR"),
        ("critical", "CRITICAL"),
        ("CRITICAL", "CRITICAL"),
        ("dEbUg", "DEBUG"),
        ("wArNiNg", "WARNING"),
    ])
    def test_log_level_case_insensitivity_matrix(self, log_input: str, expected_enum: str) -> None:
        """Verify all valid log levels in any case combination are accepted and normalized."""
        s = get_test_settings(log_level=log_input)
        assert s.log_level == expected_enum

    @pytest.mark.parametrize("invalid_log", ["verbose", "trace", "FATAL", "warn", "123", ""])
    def test_invalid_log_levels_rejected(self, invalid_log: str) -> None:
        """Verify unrecognized log levels are rejected with ValidationError."""
        with pytest.raises(ValidationError):
            get_test_settings(log_level=invalid_log)

    @pytest.mark.parametrize("port_field", [
        "ue5_http_port",
        "ue5_ws_port",
        "mcp_server_port",
        "telemetry_ws_port",
        "comfyui_port",
    ])
    @pytest.mark.parametrize("invalid_port", [-100, -1, 0, 65536, 70000, 99999])
    def test_all_port_fields_boundary_validation(self, port_field: str, invalid_port: int) -> None:
        """Verify strict [1, 65535] boundary enforcement across all network port fields."""
        with pytest.raises(ValidationError):
            get_test_settings(**{port_field: invalid_port})

    @pytest.mark.parametrize("port_field", [
        "ue5_http_port",
        "ue5_ws_port",
        "mcp_server_port",
        "telemetry_ws_port",
        "comfyui_port",
    ])
    @pytest.mark.parametrize("valid_port", [1, 80, 8080, 65535])
    def test_all_port_fields_valid_boundaries(self, port_field: str, valid_port: int) -> None:
        """Verify boundary edges 1 and 65535 are accepted."""
        s = get_test_settings(**{port_field: valid_port})
        assert getattr(s, port_field) == valid_port

    def test_path_attributes_are_absolute_resolved(self) -> None:
        """Verify directory paths in settings are automatically resolved and absolute."""
        s = get_test_settings()
        assert s.project_root.is_absolute()
        assert s.cache_dir.is_absolute()
        assert s.output_dir.is_absolute()
        assert s.temp_dir.is_absolute()
