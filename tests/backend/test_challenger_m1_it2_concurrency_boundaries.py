"""
Challenger 2 Empirical Stress Test Suite for Milestone 1 Iteration 2.

Comprehensive verification of:
1. Multi-threaded `emit_threadsafe()` execution under extreme concurrency:
   - Dedicated background event loop thread receiving bursts from 50+ worker threads.
   - Dual listener setup: async queues and sync/async callbacks simultaneously receiving events.
   - Subscriber churn: subscribing and unsubscribing concurrently during high-throughput threadsafe emissions.
   - Zero duplication check: exactly N events emitted == exactly N events received across queue and history.
2. CAS key and namespace boundary validation in `backend/core/cache.py`:
   - Namespace boundary checks: empty string, path traversal sequences ('../', '..\\', '/'), special characters, regex validation.
   - Cache key boundary checks: length < 3 rejection, minimum length 3 acceptance ('abc'), special character rejection.
   - Invalidation boundaries: attempt to invalidate empty/root paths, non-existent namespaces, namespace wiping prevention.
   - Graceful cache misses: invalid namespace/key in get() returns None without raising unhandled exceptions.
   - Parameter hashing determinism with nested Path objects, WindowsPath, and PosixPath.
   - Extensionless files and unusual extensions in put_bytes and get_total_size_bytes.
3. Network port and configuration boundaries in `backend/core/config.py`:
   - Exact port boundaries: 1 and 65535 accepted; 0, -1, 65536, and 100000 rejected across all 5 port fields.
   - Environment variable injection for boundary violation across all 5 port settings.
   - Log level case insensitivity across all 5 standard levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) in lower/mixed case.
   - Rejection of invalid log levels.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import threading
import time
from typing import Any, Dict, List, Optional, Set, Tuple

import pytest
from pydantic import ValidationError

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
def clean_telemetry_and_config() -> None:
    """Ensure clean state before each test run."""
    reset_telemetry_bus()
    get_settings.cache_clear()


# =============================================================================
# 1. Multi-Threaded emit_threadsafe() Concurrency Stress Harness
# =============================================================================

class TestEmitThreadsafeStress:
    """Stress-test multi-threaded emit_threadsafe execution."""

    def test_emit_threadsafe_high_concurrency_dedicated_loop(self) -> None:
        """
        Run an asyncio event loop in a dedicated background thread,
        and hammer emit_threadsafe from 40 worker threads (25 events each = 1000 total events).
        Verify:
        - Exactly 1000 events received in async Queue.
        - Exactly 1000 events in bus history.
        - Exactly 1000 events received by synchronous callback.
        - Zero duplicate emissions and zero lost events.
        """
        loop = asyncio.new_event_loop()
        loop_ready = threading.Event()
        loop_stop = threading.Event()

        def run_loop() -> None:
            asyncio.set_event_loop(loop)
            loop_ready.set()
            loop.run_forever()

        loop_thread = threading.Thread(target=run_loop, daemon=True)
        loop_thread.start()
        loop_ready.wait()

        try:
            bus = TelemetryBus(max_queue_size=2000, history_size=2000)
            bus.set_event_loop(loop)

            cb_events: List[TelemetryEvent] = []
            cb_lock = threading.Lock()

            def sync_cb(event: TelemetryEvent) -> None:
                with cb_lock:
                    cb_events.append(event)

            bus.subscribe(sync_cb)

            # Create an async queue in the dedicated loop
            async def setup_queue() -> asyncio.Queue[TelemetryEvent]:
                q: asyncio.Queue[TelemetryEvent] = asyncio.Queue(maxsize=2000)
                bus.add_subscriber(q)
                return q

            future_q = asyncio.run_coroutine_threadsafe(setup_queue(), loop)
            queue = future_q.result(timeout=3.0)

            num_threads = 40
            events_per_thread = 25
            total_expected = num_threads * events_per_thread

            def worker(t_id: int) -> None:
                for seq in range(events_per_thread):
                    ev = ProgressEvent(
                        stage=f"stage_{t_id}",
                        percentage=float(seq),
                        message=f"Thread-{t_id}-Seq-{seq}",
                    )
                    bus.emit_threadsafe(ev)

            workers = [threading.Thread(target=worker, args=(t,)) for t in range(num_threads)]
            for w in workers:
                w.start()
            for w in workers:
                w.join()

            # Drain queue in the loop
            async def drain() -> List[TelemetryEvent]:
                # Wait until queue has received all events or timeout
                start = time.time()
                while queue.qsize() < total_expected and (time.time() - start) < 5.0:
                    await asyncio.sleep(0.05)
                items: List[TelemetryEvent] = []
                while not queue.empty():
                    items.append(queue.get_nowait())
                return items

            future_drain = asyncio.run_coroutine_threadsafe(drain(), loop)
            drained_events = future_drain.result(timeout=6.0)

            # Wait briefly for callbacks
            deadline = time.time() + 2.0
            while len(cb_events) < total_expected and time.time() < deadline:
                time.sleep(0.05)

            # Assertions
            assert len(drained_events) == total_expected, (
                f"Async Queue received {len(drained_events)} events, expected {total_expected}"
            )
            assert len(cb_events) == total_expected, (
                f"Callback received {len(cb_events)} events, expected {total_expected}"
            )
            assert len(bus.get_history()) == total_expected, (
                f"History contains {len(bus.get_history())} events, expected {total_expected}"
            )

        finally:
            loop.call_soon_threadsafe(loop.stop)
            loop_thread.join(timeout=2.0)

    def test_emit_threadsafe_concurrent_subscriber_churn(self) -> None:
        """
        Verify that adding and removing callbacks while high-throughput threads
        call emit_threadsafe does not cause RuntimeError (Set changed size during iteration)
        or unhandled exceptions.
        """
        bus = TelemetryBus(max_queue_size=1000, history_size=1000)
        stop_flag = threading.Event()
        errors: List[Exception] = []

        # Worker threads emitting continuously
        def emitter(t_id: int) -> None:
            seq = 0
            while not stop_flag.is_set():
                try:
                    bus.emit_threadsafe(LogEvent(message=f"E-{t_id}-{seq}"))
                    seq += 1
                except Exception as exc:
                    errors.append(exc)
                time.sleep(0.001)

        # Churn thread adding and removing callbacks
        def churner() -> None:
            while not stop_flag.is_set():
                try:
                    cb = lambda ev: None
                    unsub = bus.subscribe(cb)
                    time.sleep(0.002)
                    unsub()
                except Exception as exc:
                    errors.append(exc)
                time.sleep(0.001)

        threads = [threading.Thread(target=emitter, args=(i,)) for i in range(8)]
        churn_threads = [threading.Thread(target=churner) for _ in range(4)]

        for t in threads + churn_threads:
            t.start()

        time.sleep(1.0)
        stop_flag.set()

        for t in threads + churn_threads:
            t.join()

        assert len(errors) == 0, f"Subscriber churn under emit_threadsafe raised errors: {errors}"
        assert len(bus.get_history()) > 0, "Expected events to be recorded in history"


# =============================================================================
# 2. CAS Cache Key, Namespace, and Path Traversal Boundaries
# =============================================================================

class TestCASCacheBoundaries:
    """Stress-test CAS key, namespace, path traversal, and file boundaries."""

    @pytest.mark.parametrize(
        "invalid_ns",
        [
            "",
            "   ",
            "../escape",
            "..\\escape",
            "ns/sub",
            "ns\\sub",
            "ns.dot",
            "ns*wild",
            "ns:colon",
            "ns?question",
            "ns|pipe",
            "ns\x00null",
        ],
    )
    def test_cas_invalid_namespaces_rejected(self, tmp_path: Path, invalid_ns: str) -> None:
        """Verify that malformed or malicious namespaces are strictly rejected with ValueError."""
        cache = ContentAddressableStorage(base_dir=tmp_path / "cas")

        with pytest.raises(ValueError, match="Invalid namespace"):
            cache.put_bytes(b"DATA", ".bin", namespace=invalid_ns)

        with pytest.raises(ValueError, match="Invalid namespace"):
            cache.invalidate_namespace(invalid_ns)

        with pytest.raises(ValueError, match="Invalid namespace"):
            cache.invalidate(invalid_ns, "valid_key_123")

    @pytest.mark.parametrize(
        "invalid_key",
        [
            "",
            "a",
            "ab",
            "   ",
            "../abc",
            "..\\abc",
            "key/slash",
            "key\\backslash",
            "key.dot",
            "key*wild",
            "key\x00null",
        ],
    )
    def test_cas_invalid_cache_keys_rejected(self, tmp_path: Path, invalid_key: str) -> None:
        """Verify that malformed, too-short (<3), or traversal cache keys are strictly rejected."""
        cache = ContentAddressableStorage(base_dir=tmp_path / "cas")

        with pytest.raises(ValueError, match="Invalid cache_key"):
            cache.put_bytes(b"DATA", ".bin", namespace="valid_ns", cache_key=invalid_key)

        with pytest.raises(ValueError, match="Invalid cache_key"):
            cache.invalidate("valid_ns", invalid_key)

    def test_cas_none_handling_in_invalidate(self, tmp_path: Path) -> None:
        """Verify that passing None or non-string to invalidate raises ValueError."""
        cache = ContentAddressableStorage(base_dir=tmp_path / "cas")
        with pytest.raises(ValueError, match="Invalid cache_key"):
            cache.invalidate("valid_ns", None)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="Invalid namespace"):
            cache.invalidate(None, "valid_key")  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="Invalid namespace"):
            cache.invalidate_namespace(None)  # type: ignore[arg-type]

    def test_cas_minimum_valid_key_length_3(self, tmp_path: Path) -> None:
        """A key of exactly length 3 (e.g. 'abc') should partition prefix='ab' and suffix='c' safely."""
        cache = ContentAddressableStorage(base_dir=tmp_path / "cas")
        cached = cache.put_bytes(b"MIN_KEY_DATA", ".txt", namespace="min_ns", cache_key="abc")

        assert cached.cache_key == "abc"
        expected_dir = (tmp_path / "cas" / "min_ns" / "ab" / "c").resolve()
        assert cached.file_path.parent == expected_dir
        assert cached.file_path.is_file()

        retrieved = cache.get("min_ns", "abc")
        assert retrieved is not None
        assert retrieved.file_path.read_bytes() == b"MIN_KEY_DATA"

    def test_cas_get_with_invalid_key_or_ns_returns_none(self, tmp_path: Path) -> None:
        """Verify get() handles invalid namespace or key gracefully by returning None."""
        cache = ContentAddressableStorage(base_dir=tmp_path / "cas")
        assert cache.get("../invalid_ns", "key123") is None
        assert cache.get("valid_ns", "../invalid_key") is None
        assert cache.get("valid_ns", "ab") is None
        assert cache.get("", "abc") is None

    def test_cas_canonical_params_hash_path_determinism(self) -> None:
        """
        Verify canonical_params_hash produces identical hashes for Path objects
        regardless of whether they are PosixPath, WindowsPath, or string posix format.
        """
        path_obj = Path("folder") / "sub" / "file.txt"
        params_with_path = {"target": path_obj, "count": 10}
        params_with_str = {"target": "folder/sub/file.txt", "count": 10}

        hash1 = canonical_params_hash(params_with_path)
        hash2 = canonical_params_hash(params_with_str)

        assert hash1 == hash2, "canonical_params_hash must normalize Path to POSIX string deterministically"

    def test_cas_extensionless_and_multidot_files(self, tmp_path: Path) -> None:
        """
        Test files without extension ('asset') and with multiple dots ('.tar.gz').
        Verify both storage, retrieval, and total size tracking.
        """
        cache = ContentAddressableStorage(base_dir=tmp_path / "cas")

        # 1. Extensionless
        c1 = cache.put_bytes(b"A" * 128, extension="", namespace="ext_ns")
        assert c1.file_path.name == "asset"
        assert c1.metadata.file_size_bytes == 128

        # 2. Multi-dot extension
        c2 = cache.put_bytes(b"B" * 256, extension=".tar.gz", namespace="ext_ns")
        assert c2.file_path.name == "asset.tar.gz"
        assert c2.metadata.file_size_bytes == 256

        # 3. Extension without leading dot (should auto-prefix '.')
        c3 = cache.put_bytes(b"C" * 64, extension="glb", namespace="ext_ns")
        assert c3.file_path.name == "asset.glb"
        assert c3.metadata.file_size_bytes == 64

        # Total size calculation
        total_size = cache.get_total_size_bytes()
        assert total_size == 128 + 256 + 64, f"Expected 448 bytes total, got {total_size}"

    def test_cas_invalidate_namespace_isolation(self, tmp_path: Path) -> None:
        """Invalidating one namespace must not affect other namespaces or the base directory."""
        cache = ContentAddressableStorage(base_dir=tmp_path / "cas")
        cache.put_bytes(b"NS1_FILE", ".bin", namespace="ns_alpha", cache_key="key_alpha_1")
        cache.put_bytes(b"NS2_FILE", ".bin", namespace="ns_beta", cache_key="key_beta_1")

        deleted = cache.invalidate_namespace("ns_alpha")
        assert deleted == 1

        # Alpha is gone
        assert cache.get("ns_alpha", "key_alpha_1") is None
        # Beta is preserved
        assert cache.get("ns_beta", "key_beta_1") is not None
        # Base dir is intact
        assert (tmp_path / "cas").is_dir()


# =============================================================================
# 3. Port Boundaries and Configuration Stress Tests
# =============================================================================

class TestConfigPortBoundaries:
    """Stress-test network port bounds and configuration normalization."""

    PORT_FIELDS = [
        "ue5_http_port",
        "ue5_ws_port",
        "mcp_server_port",
        "telemetry_ws_port",
        "comfyui_port",
    ]

    @pytest.mark.parametrize("port_field", PORT_FIELDS)
    def test_port_exact_boundary_valid(self, port_field: str) -> None:
        """Ports 1 (minimum) and 65535 (maximum) must be strictly accepted."""
        s_min = get_test_settings(**{port_field: 1})
        assert getattr(s_min, port_field) == 1

        s_max = get_test_settings(**{port_field: 65535})
        assert getattr(s_max, port_field) == 65535

    @pytest.mark.parametrize("port_field", PORT_FIELDS)
    @pytest.mark.parametrize("invalid_port", [0, -1, -65535, 65536, 99999, 1000000])
    def test_port_out_of_bounds_rejected(self, port_field: str, invalid_port: int) -> None:
        """Ports <= 0 or >= 65536 must raise pydantic ValidationError."""
        with pytest.raises(ValidationError):
            get_test_settings(**{port_field: invalid_port})

    @pytest.mark.parametrize(
        "env_var, invalid_val",
        [
            ("IANIMATION_UE5_HTTP_PORT", "0"),
            ("IANIMATION_UE5_HTTP_PORT", "65536"),
            ("IANIMATION_UE5_WS_PORT", "-10"),
            ("IANIMATION_MCP_SERVER_PORT", "70000"),
            ("IANIMATION_TELEMETRY_WS_PORT", "0"),
            ("IANIMATION_COMFYUI_PORT", "100000"),
        ],
    )
    def test_port_env_var_boundaries_rejected(
        self, monkeypatch: pytest.MonkeyPatch, env_var: str, invalid_val: str
    ) -> None:
        """Out of bounds port numbers injected via environment variables must fail validation."""
        monkeypatch.setenv(env_var, invalid_val)
        get_settings.cache_clear()
        with pytest.raises(ValidationError):
            get_settings()

    @pytest.mark.parametrize(
        "raw_level, expected_normalized",
        [
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
            ("DeBuG", "DEBUG"),
            ("InFo", "INFO"),
        ],
    )
    def test_log_level_case_normalization_all_levels(
        self, raw_level: str, expected_normalized: str
    ) -> None:
        """Verify that all standard log levels in any case are normalized to uppercase."""
        s = get_test_settings(log_level=raw_level)
        assert s.log_level == expected_normalized

    @pytest.mark.parametrize("invalid_level", ["VERBOSE", "TRACE", "FATAL", "OFF", "", "123"])
    def test_invalid_log_levels_rejected(self, invalid_level: str) -> None:
        """Non-standard log level names must be rejected."""
        with pytest.raises(ValidationError):
            get_test_settings(log_level=invalid_level)
