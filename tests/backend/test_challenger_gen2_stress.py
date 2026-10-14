"""
Empirical Challenger Test Suite for Milestone 1 Iteration 2.
Author: challenger_m1_it2_2_gen2

Adversarially probes:
1. CAS Concurrency & Disk Contention (high-concurrency collisions, atomic overwrites, simultaneous prune & put).
2. CAS Path Traversal, Empty Key/Namespace, and Windows Device Name boundaries.
3. TelemetryBus Thread Safety (50 worker threads into active loop, concurrent subscriber/callback churn, error resilience).
4. Settings Port Validation Boundaries (0, -1, 65536, non-integer) and Case-Insensitive Log Levels.
5. Zero-Any Policy AST Verification.
"""

from __future__ import annotations

import ast
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import inspect
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import threading
import time
from typing import Dict, List, Optional, Set, Tuple

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
    reset_telemetry_bus,
)


@pytest.fixture
def temp_cas_dir() -> Path:
    """Provide a temporary directory for CAS storage."""
    temp_dir = Path(tempfile.mkdtemp(prefix="test_cas_gen2_"))
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


# =============================================================================
# 1. CAS CONCURRENCY & DISK CONTENTION STRESS TESTS
# =============================================================================

class TestCASConcurrencyDiskContention:
    """Stress-test CAS atomic operations under high concurrency and disk contention."""

    def test_concurrent_put_same_key_collision(self, temp_cas_dir: Path) -> None:
        """
        40 concurrent worker threads attempt to write to the EXACT SAME namespace and cache_key.
        Verify:
        - All 40 threads complete successfully without file locking crashes (especially on Windows).
        - The resulting asset on disk is intact, readable, and matches the expected hash.
        - The metadata sidecar is intact and valid JSON.
        """
        cas = ContentAddressableStorage(base_dir=temp_cas_dir)
        namespace = "concurrency_collision"
        cache_key = "collision_key_sha256_deadbeef12345678"
        payload = b"HEAVY_CONTENT_COLLISION_TEST_PAYLOAD_" * 1024  # ~38KB

        errors: List[Exception] = []
        results: List[CachedAsset] = []
        lock = threading.Lock()

        def worker(thread_idx: int) -> None:
            try:
                # Add unique tag to verify atomic overwrite
                asset = cas.put_bytes(
                    data=payload,
                    extension=".bin",
                    namespace=namespace,
                    cache_key=cache_key,
                    tags={"worker": str(thread_idx)},
                )
                with lock:
                    results.append(asset)
            except Exception as e:
                with lock:
                    errors.append(e)

        with ThreadPoolExecutor(max_workers=40) as executor:
            futures = [executor.submit(worker, i) for i in range(40)]
            for f in as_completed(futures):
                f.result()

        assert len(errors) == 0, f"Errors during concurrent put to same key: {errors}"
        assert len(results) == 40

        # Verify on-disk integrity
        retrieved = cas.get(namespace, cache_key)
        assert retrieved is not None
        assert retrieved.file_path.is_file()
        assert retrieved.file_path.read_bytes() == payload
        assert retrieved.metadata.file_size_bytes == len(payload)
        assert retrieved.metadata.sha256_hash == hash_bytes(payload)

    def test_concurrent_put_and_get_race(self, temp_cas_dir: Path) -> None:
        """
        25 threads constantly putting new assets while 25 threads constantly reading them.
        Verify:
        - No unhandled exceptions.
        - Reads for completed puts return valid intact CachedAsset instances.
        """
        cas = ContentAddressableStorage(base_dir=temp_cas_dir)
        namespace = "put_get_race"
        num_keys = 50
        keys = [f"key_{i:04d}_{hash_bytes(str(i).encode('utf-8'))[:16]}" for i in range(num_keys)]

        errors: List[Exception] = []
        lock = threading.Lock()
        stop_event = threading.Event()

        def putter(idx: int) -> None:
            key = keys[idx % num_keys]
            data = f"data_from_putter_{idx}".encode("utf-8")
            try:
                cas.put_bytes(data=data, extension=".txt", namespace=namespace, cache_key=key)
            except Exception as e:
                with lock:
                    errors.append(e)

        def getter(idx: int) -> None:
            key = keys[idx % num_keys]
            try:
                # Could be None (cache miss) or CachedAsset, but must NOT raise
                asset = cas.get(namespace, key)
                if asset is not None:
                    assert asset.file_path.is_file()
            except Exception as e:
                with lock:
                    errors.append(e)

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = []
            for i in range(100):
                futures.append(executor.submit(putter, i))
                futures.append(executor.submit(getter, i))
            for f in as_completed(futures):
                f.result()

        assert len(errors) == 0, f"Errors during put/get race: {errors}"

    def test_concurrent_put_and_lru_pruning(self, temp_cas_dir: Path) -> None:
        """
        Multiple threads putting files while prune_lru is called concurrently under quota pressure.
        Verify:
        - Cache size quota enforcement stays consistent without deadlocks or file corruptions.
        """
        # Quota of 100 KB
        quota_bytes = 100 * 1024
        cas = ContentAddressableStorage(base_dir=temp_cas_dir, max_size_bytes=quota_bytes)
        namespace = "lru_quota"

        errors: List[Exception] = []
        lock = threading.Lock()

        def put_worker(worker_id: int) -> None:
            # 10 KB payload per put
            payload = b"X" * (10 * 1024)
            for i in range(5):
                key = f"w{worker_id:02d}_item_{i:03d}_{hash_bytes(f'{worker_id}_{i}'.encode('utf-8'))[:16]}"
                try:
                    cas.put_bytes(payload, extension=".bin", namespace=namespace, cache_key=key)
                    # Opportunistically prune
                    cas.prune_lru(quota_bytes)
                except Exception as e:
                    with lock:
                        errors.append(e)

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(put_worker, i) for i in range(20)]
            for f in as_completed(futures):
                f.result()

        assert len(errors) == 0, f"Errors during concurrent put and LRU pruning: {errors}"
        total_size = cas.get_total_size_bytes()
        # Final prune
        cas.prune_lru(quota_bytes)
        assert cas.get_total_size_bytes() <= quota_bytes


# =============================================================================
# 2. CAS PATH TRAVERSAL, EMPTY KEY, AND ATTACK VECTORS
# =============================================================================

class TestCASAttackVectors:
    """Stress-test attack vectors against CAS storage boundaries."""

    @pytest.mark.parametrize(
        "invalid_namespace",
        [
            "",
            " ",
            "   ",
            "\t",
            "\n",
            "../",
            "..\\",
            "../../",
            "..\\..\\",
            "..",
            ".",
            "/escaped",
            "\\escaped",
            "C:\\Windows",
            "sub/dir",
            "sub\\dir",
            "ns:stream",
            "ns;rm",
            "ns|pipe",
            "ns?wildcard",
            "ns*asterisk",
            "ns\x00null",
            "ns café",
            "ns🚀",
        ],
    )
    def test_invalid_namespace_rejected(self, temp_cas_dir: Path, invalid_namespace: str) -> None:
        """Verify invalid or malicious namespaces are rejected with ValueError on put and invalidate."""
        cas = ContentAddressableStorage(base_dir=temp_cas_dir)
        payload = b"sample_data"
        key = "valid_key_12345"

        with pytest.raises(ValueError):
            cas.put_bytes(payload, extension=".txt", namespace=invalid_namespace, cache_key=key)

        with pytest.raises(ValueError):
            cas.invalidate(invalid_namespace, key)

        with pytest.raises(ValueError):
            cas.invalidate_namespace(invalid_namespace)

        # get() must gracefully return None on invalid namespace
        assert cas.get(invalid_namespace, key) is None

    @pytest.mark.parametrize(
        "invalid_key",
        [
            "",
            " ",
            "  ",
            "a",
            "ab",
            "1",
            "12",
            "__",
            "--",
            "../123",
            "..\\123",
            "../../",
            "../../12345",
            "..\\..\\12345",
            "abc/def",
            "abc\\def",
            "abc:def",
            "abc\x00def",
            "abc def",
            "abc*def",
        ],
    )
    def test_invalid_cache_key_rejected(self, temp_cas_dir: Path, invalid_key: str) -> None:
        """Verify invalid, too-short (<3 chars), or malicious cache keys are rejected."""
        cas = ContentAddressableStorage(base_dir=temp_cas_dir)
        payload = b"sample_data"
        namespace = "valid_ns"

        with pytest.raises(ValueError):
            cas.put_bytes(payload, extension=".txt", namespace=namespace, cache_key=invalid_key)

        with pytest.raises(ValueError):
            cas.invalidate(namespace, invalid_key)

        # get() must gracefully return None on invalid cache_key
        assert cas.get(namespace, invalid_key) is None

    def test_base_dir_never_deleted_on_invalidation(self, temp_cas_dir: Path) -> None:
        """Verify invalidation operations cannot delete base_dir or root under any circumstance."""
        cas = ContentAddressableStorage(base_dir=temp_cas_dir)
        assert temp_cas_dir.is_dir()

        # Invalidate non-existent namespace
        assert cas.invalidate_namespace("nonexistent_ns") == 0
        assert temp_cas_dir.is_dir()

        # Invalidate non-existent key
        assert not cas.invalidate("valid_ns", "valid_key_123")
        assert temp_cas_dir.is_dir()

    def test_deterministic_param_hashing_with_paths(self) -> None:
        """Verify canonical_params_hash handles Path, nested paths, and primitives deterministically."""
        p1 = Path("/tmp/somewhere/file.glb")
        p2 = Path(r"C:\Users\User\file.glb")

        # Canonical hash should serialize paths using as_posix()
        hash1 = canonical_params_hash({"mesh": p1, "iterations": 10})
        hash2 = canonical_params_hash({"iterations": 10, "mesh": p1})
        assert hash1 == hash2

        # WindowsPath vs PosixPath formatting
        hash3 = canonical_params_hash({"path": p2})
        assert isinstance(hash3, str)
        assert len(hash3) == 64


# =============================================================================
# 3. TELEMETRYBUS THREAD SAFETY & ERROR RESILIENCE
# =============================================================================

class TestTelemetryBusThreadSafetyStress:
    """Stress-test TelemetryBus multi-threaded execution and failure isolation."""

    def test_emit_50_threads_into_running_loop(self) -> None:
        """
        50 worker threads emitting 40 events each (2,000 total events) into an active event loop.
        Verify:
        - Exactly 2,000 events received by subscriber Queue.
        - Exactly 2,000 events recorded in history.
        - Exactly 2,000 callbacks invoked without duplicates or drops.
        """
        loop = asyncio.new_event_loop()
        loop_ready = threading.Event()

        def run_loop() -> None:
            asyncio.set_event_loop(loop)
            loop_ready.set()
            loop.run_forever()

        t = threading.Thread(target=run_loop, daemon=True)
        t.start()
        loop_ready.wait(timeout=2.0)

        total_expected = 2000
        bus = TelemetryBus(max_queue_size=total_expected + 500, history_size=total_expected + 500)
        bus.set_event_loop(loop)

        # Register callback
        received_callbacks: List[TelemetryEvent] = []
        cb_lock = threading.Lock()

        def on_event(ev: TelemetryEvent) -> None:
            with cb_lock:
                received_callbacks.append(ev)

        bus.add_callback(on_event)

        # Register queue subscriber
        async def make_queue() -> asyncio.Queue[TelemetryEvent]:
            q: asyncio.Queue[TelemetryEvent] = asyncio.Queue(maxsize=total_expected + 500)
            bus.add_subscriber(q)
            return q

        sub_queue = asyncio.run_coroutine_threadsafe(make_queue(), loop).result()

        def worker(thread_idx: int) -> None:
            for i in range(40):
                ev = ProgressEvent(
                    stage=f"worker_{thread_idx}",
                    percentage=float(i * 2.5),
                    message=f"event_{thread_idx}_{i}",
                )
                bus.emit_threadsafe(ev)

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(worker, i) for i in range(50)]
            for f in as_completed(futures):
                f.result()

        # Allow loop to process all scheduled events
        time.sleep(1.5)

        # Drain queue
        drain_future = asyncio.run_coroutine_threadsafe(
            asyncio.wait_for(asyncio.sleep(0.1), timeout=2.0), loop
        )
        drain_future.result()

        history = bus.get_history()
        assert len(history) == total_expected, f"Expected {total_expected} in history, got {len(history)}"
        assert len(received_callbacks) == total_expected, f"Expected {total_expected} callbacks, got {len(received_callbacks)}"
        assert sub_queue.qsize() == total_expected, f"Expected {total_expected} in queue, got {sub_queue.qsize()}"

        loop.call_soon_threadsafe(loop.stop)
        t.join(timeout=2.0)

    def test_callback_raising_exception_does_not_halt_bus(self) -> None:
        """
        Verify that a failing callback does not prevent subsequent callbacks or queue delivery.
        """
        bus = TelemetryBus()
        good_results: List[str] = []

        def failing_callback(ev: TelemetryEvent) -> None:
            raise ZeroDivisionError("Intentionally exploded callback")

        def working_callback(ev: TelemetryEvent) -> None:
            good_results.append(ev.type)

        bus.add_callback(failing_callback)
        bus.add_callback(working_callback)

        event = ProgressEvent(stage="test", percentage=50.0, message="resilience test")
        # Should not raise exception
        bus.emit_threadsafe(event)

        assert len(good_results) == 1
        assert good_results[0] == "progress"

    def test_concurrent_add_remove_callbacks_during_emit(self) -> None:
        """
        Verify adding and removing callbacks concurrently with emit_threadsafe does not raise
        RuntimeError (e.g. Set changed size during iteration).
        """
        bus = TelemetryBus()
        errors: List[Exception] = []
        lock = threading.Lock()
        stop_event = threading.Event()

        def churn_worker() -> None:
            while not stop_event.is_set():
                def dummy_cb(ev: TelemetryEvent) -> None:
                    pass
                unsub = bus.add_callback(dummy_cb)
                time.sleep(0.001)
                unsub()

        def emit_worker() -> None:
            for i in range(100):
                try:
                    ev = LogEvent(message=f"msg_{i}", level=LogLevel.INFO)
                    bus.emit_threadsafe(ev)
                except Exception as e:
                    with lock:
                        errors.append(e)

        with ThreadPoolExecutor(max_workers=10) as executor:
            churn_futures = [executor.submit(churn_worker) for _ in range(4)]
            emit_futures = [executor.submit(emit_worker) for _ in range(6)]

            for f in as_completed(emit_futures):
                f.result()

            stop_event.set()
            for f in as_completed(churn_futures):
                f.result()

        assert len(errors) == 0, f"Errors during concurrent callback churn and emit: {errors}"


# =============================================================================
# 4. SETTINGS PORT VALIDATION BOUNDARIES & LOG LEVEL TESTS
# =============================================================================

class TestSettingsBoundaries:
    """Stress-test configuration port validation boundaries and case-insensitive log levels."""

    PORT_FIELDS = [
        "ue5_http_port",
        "ue5_ws_port",
        "mcp_server_port",
        "telemetry_ws_port",
        "comfyui_port",
    ]

    @pytest.mark.parametrize("port_field", PORT_FIELDS)
    @pytest.mark.parametrize("invalid_port", [0, -1, -500, 65536, 70000, 100000])
    def test_port_out_of_bounds_rejected(self, port_field: str, invalid_port: int) -> None:
        """Verify boundary violations for all 5 port settings raise ValidationError."""
        with pytest.raises(ValidationError):
            Settings(**{port_field: invalid_port})

    @pytest.mark.parametrize("port_field", PORT_FIELDS)
    @pytest.mark.parametrize("valid_port", [1, 80, 8080, 30010, 65535])
    def test_port_valid_boundaries_accepted(self, port_field: str, valid_port: int) -> None:
        """Verify valid edge boundary ports (1 and 65535) are accepted."""
        s = Settings(**{port_field: valid_port})
        assert getattr(s, port_field) == valid_port

    @pytest.mark.parametrize("port_field", PORT_FIELDS)
    @pytest.mark.parametrize("invalid_type", ["abc", "30010.5", None, [8000], {"port": 8000}])
    def test_port_non_integer_rejected(self, port_field: str, invalid_type: object) -> None:
        """Verify non-integer inputs raise ValidationError."""
        with pytest.raises(ValidationError):
            Settings(**{port_field: invalid_type})

    @pytest.mark.parametrize(
        "input_level,expected_level",
        [
            ("debug", "DEBUG"),
            ("info", "INFO"),
            ("warning", "WARNING"),
            ("error", "ERROR"),
            ("critical", "CRITICAL"),
            ("Debug", "DEBUG"),
            ("Info", "INFO"),
            ("Warning", "WARNING"),
            ("Error", "ERROR"),
            ("Critical", "CRITICAL"),
            ("dEbUg", "DEBUG"),
            ("iNfO", "INFO"),
            ("WARNING", "WARNING"),
        ],
    )
    def test_log_level_case_insensitivity(self, input_level: str, expected_level: str) -> None:
        """Verify case-insensitive normalization of log levels."""
        s = Settings(log_level=input_level)
        assert s.log_level == expected_level

    @pytest.mark.parametrize("invalid_level", ["VERBOSE", "TRACE", "FATAL", "OFF", "", "123", None])
    def test_invalid_log_levels_rejected(self, invalid_level: object) -> None:
        """Verify unrecognized log levels raise ValidationError."""
        with pytest.raises(ValidationError):
            Settings(log_level=invalid_level)


# =============================================================================
# 5. ZERO-ANY TYPING POLICY AST VERIFICATION
# =============================================================================

class TestZeroAnyTypingPolicy:
    """Empirically inspect AST of backend/core/ modules to guarantee 0% Any usage."""

    CORE_MODULES = [
        Path("backend/core/models.py"),
        Path("backend/core/cache.py"),
        Path("backend/core/telemetry.py"),
        Path("backend/core/config.py"),
        Path("backend/core/__init__.py"),
    ]

    def test_no_typing_any_imported_or_used_in_core(self) -> None:
        """
        Parse AST of each backend/core/*.py file and verify:
        - 'Any' is never imported from typing.
        - 'Any' is never used as an annotation or expression.
        """
        violations: List[str] = []

        for mod_path in self.CORE_MODULES:
            assert mod_path.is_file(), f"Core module missing: {mod_path}"
            source = mod_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(mod_path))

            for node in ast.walk(tree):
                # Check imports: from typing import ... Any
                if isinstance(node, ast.ImportFrom):
                    if node.module == "typing":
                        for alias in node.names:
                            if alias.name == "Any":
                                violations.append(f"{mod_path}:{node.lineno} imported Any from typing")

                # Check import typing: typing.Any
                if isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name) and node.value.id == "typing" and node.attr == "Any":
                        violations.append(f"{mod_path}:{node.lineno} referenced typing.Any")

                # Check Name annotations: x: Any
                if isinstance(node, ast.Name) and node.id == "Any":
                    violations.append(f"{mod_path}:{node.lineno} used Any identifier")

        assert len(violations) == 0, f"Zero-Any policy violated in core modules:\n" + "\n".join(violations)
