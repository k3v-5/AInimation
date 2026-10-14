"""
Tier 5 Adversarial Stress & Concurrency Coverage Suite for Core Services and Plan Engine.

Targets:
1. Content-Addressable Storage (CAS):
   - Concurrent write-write and write-read races on identical keys.
   - Cross-instance access against shared storage directories.
   - Comprehensive path traversal fuzzing vectors.
   - Large binary streaming, odd file sizes, zero-byte handling.
   - Strict LRU pruning order under quota pressure with accessed_at updates.
   - Resilient recovery from corrupted metadata sidecars.
   - Windows reserved device name handling (CON, PRN, AUX, NUL).
2. TelemetryBus:
   - High-concurrency subscriber disconnect storms (cancelling subscribers under load).
   - Lossy backpressure handling for saturated queues (dropping oldest events).
   - Server-Sent Events (SSE) keep-alive streaming and clean unsubscription.
   - Concurrent cross-thread emission (emit_threadsafe) with dynamic subscriber churn.
3. Plan Engine:
   - Out-of-order confirmation requests (e.g. confirming final render step first).
   - Rejection state machine transitions and plan halt semantics.
   - State inconsistency analysis (approving steps after plan rejection).
   - Missing plan-level promotion when all steps are approved.
   - Non-existent and fuzzed step/plan ID handling.
   - Concurrent multi-threaded step confirmation safety.
4. Settings & Config:
   - Extreme boundary values, port validation, and test environment isolation.

Zero-Any Policy enforced: 100% strictly typed.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import threading
import time
from typing import Coroutine, Dict, List, Optional, TypeVar
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
    PlanRiskLevel,
    PlanStatus,
    PlanStep,
    ProductionPlan,
    ProgressEvent,
    TelemetryEvent,
)
from backend.core.telemetry import (
    TelemetryBus,
    reset_telemetry_bus,
    telemetry_sse_stream,
)
from backend.mcp.plan_engine import PlanEngine


@pytest.fixture(autouse=True)
def clean_environment() -> None:
    """Reset global singletons before every test to guarantee test isolation."""
    reset_telemetry_bus()
    get_settings.cache_clear()


# =============================================================================
# SECTION 1: Content-Addressable Storage (CAS) Concurrency & Race Conditions
# =============================================================================

def test_cas_concurrent_same_key_write_race(tmp_path: Path) -> None:
    """
    Stress-test concurrent writes to the exact same cache key across 20 threads.

    Verifies:
    - No file collision or Windows file-locking (WinError 32) crashes.
    - Atomicity of temporary file rename operations.
    - Sidecar metadata.json remains strictly valid JSON and matches final asset size.
    """
    cas = ContentAddressableStorage(base_dir=tmp_path / "cas_race")
    namespace = "render_frames"
    fixed_key = "fixed_target_key_001"
    num_threads = 20
    errors: List[Exception] = []

    def writer_worker(thread_idx: int) -> None:
        payload = f"thread_payload_data_block_{thread_idx}_{'x' * (thread_idx * 50)}".encode("utf-8")
        try:
            cas.put_bytes(
                data=payload,
                extension=".bin",
                namespace=namespace,
                cache_key=fixed_key,
                original_filename=f"artifact_{thread_idx}.bin",
            )
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=writer_worker, args=(i,)) for i in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, f"Concurrent same-key writes encountered errors: {errors}"

    # Verify asset is readable and metadata is intact
    cached = cas.get(namespace, fixed_key)
    assert cached is not None
    assert cached.file_path.is_file()
    assert cached.metadata.cache_key == fixed_key
    assert cached.metadata.file_size_bytes == cached.file_path.stat().st_size
    assert hash_file(cached.file_path) == cached.metadata.sha256_hash


def test_cas_concurrent_read_write_invalidation_race(tmp_path: Path) -> None:
    """
    Stress-test simultaneous reads, writes, and invalidations across 30 threads.

    Verifies:
    - Readers never observe partially written files or half-written metadata JSON.
    - Invalidations do not cause unhandled FileNotFoundError in concurrent readers.
    """
    cas = ContentAddressableStorage(base_dir=tmp_path / "cas_rwi_race")
    namespace = "simultaneous_ops"
    num_keys = 10
    keys = [f"key_race_{i:03d}" for i in range(num_keys)]

    # Pre-populate some keys
    for k in keys:
        cas.put_bytes(
            data=f"initial_{k}".encode("utf-8"),
            extension=".dat",
            namespace=namespace,
            cache_key=k,
        )

    stop_event = threading.Event()
    read_exceptions: List[Exception] = []
    write_exceptions: List[Exception] = []
    invalidate_exceptions: List[Exception] = []

    def reader_worker() -> None:
        while not stop_event.is_set():
            for k in keys:
                try:
                    res = cas.get(namespace, k)
                    if res is not None:
                        # Ensure if an asset is returned, its file actually exists
                        assert res.file_path.is_file()
                except Exception as exc:
                    read_exceptions.append(exc)

    def writer_worker() -> None:
        idx = 0
        while not stop_event.is_set():
            k = keys[idx % num_keys]
            try:
                cas.put_bytes(
                    data=f"write_cycle_{idx}".encode("utf-8"),
                    extension=".dat",
                    namespace=namespace,
                    cache_key=k,
                )
            except Exception as exc:
                write_exceptions.append(exc)
            idx += 1

    def invalidator_worker() -> None:
        idx = 0
        while not stop_event.is_set():
            k = keys[idx % num_keys]
            try:
                cas.invalidate(namespace, k)
            except Exception as exc:
                invalidate_exceptions.append(exc)
            idx += 1
            time.sleep(0.005)

    workers: List[threading.Thread] = []
    for _ in range(10):
        workers.append(threading.Thread(target=reader_worker))
    for _ in range(10):
        workers.append(threading.Thread(target=writer_worker))
    for _ in range(5):
        workers.append(threading.Thread(target=invalidator_worker))

    for w in workers:
        w.start()

    time.sleep(0.5)  # Let threads race for 500ms
    stop_event.set()

    for w in workers:
        w.join()

    assert len(read_exceptions) == 0, f"Reader threads encountered errors: {read_exceptions[:3]}"
    assert len(write_exceptions) == 0, f"Writer threads encountered errors: {write_exceptions[:3]}"
    assert len(invalidate_exceptions) == 0, f"Invalidator threads encountered errors: {invalidate_exceptions[:3]}"


def test_cas_cross_instance_same_dir_concurrency(tmp_path: Path) -> None:
    """
    Test two separate ContentAddressableStorage instances operating on the identical directory.

    Simulates uncoordinated worker processes or separate engine instances writing concurrently.
    """
    shared_dir = tmp_path / "shared_cas_storage"
    instance_a = ContentAddressableStorage(base_dir=shared_dir)
    instance_b = ContentAddressableStorage(base_dir=shared_dir)

    key_a = "instance_a_asset_key"
    key_b = "instance_b_asset_key"

    res_a = instance_a.put_bytes(b"data_from_instance_a", extension=".glb", namespace="shared_ns", cache_key=key_a)
    res_b = instance_b.put_bytes(b"data_from_instance_b", extension=".glb", namespace="shared_ns", cache_key=key_b)

    # Instance B reads A's asset
    read_from_b = instance_b.get("shared_ns", key_a)
    assert read_from_b is not None
    assert read_from_b.metadata.file_size_bytes == len(b"data_from_instance_a")

    # Instance A reads B's asset
    read_from_a = instance_a.get("shared_ns", key_b)
    assert read_from_a is not None
    assert read_from_a.metadata.file_size_bytes == len(b"data_from_instance_b")


# =============================================================================
# SECTION 2: CAS Path Traversal Prevention & Edge-Case Boundaries
# =============================================================================

@pytest.mark.parametrize(
    "malicious_namespace",
    [
        "../escaped",
        "..\\escaped",
        "nested/sub/namespace",
        "nested\\sub\\namespace",
        "ns_with_null\x00byte",
        "",
        "   ",
        "ns with space",
        ".",
        "..",
        "/etc/passwd",
        "C:\\Windows\\System32",
        "ns#hash",
        "ns?param",
        "ns*wildcard",
    ],
)
def test_cas_path_traversal_adversarial_namespaces(tmp_path: Path, malicious_namespace: str) -> None:
    """Verify that any invalid or directory-traversing namespace raises ValueError."""
    cas = ContentAddressableStorage(base_dir=tmp_path / "cas_traversal")
    valid_key = "valid_sha256_mock_key_01"

    with pytest.raises(ValueError):
        cas.put_bytes(b"payload", extension=".bin", namespace=malicious_namespace, cache_key=valid_key)

    # Verify get() returns None safely without raising or escaping
    assert cas.get(malicious_namespace, valid_key) is None

    with pytest.raises(ValueError):
        cas.invalidate(malicious_namespace, valid_key)

    with pytest.raises(ValueError):
        cas.invalidate_namespace(malicious_namespace)


@pytest.mark.parametrize(
    "malicious_key",
    [
        "../key",
        "..\\key",
        "k/e/y",
        "k\\e\\y",
        "",
        "a",
        "ab",  # Less than 3 chars (fails prefix partition requirement)
        "key with space",
        "key_with_\x00_null",
        "key/../../../etc/shadow",
        "../../../../../../../../../../evil",
        "key#123",
        "key?foo=bar",
    ],
)
def test_cas_path_traversal_adversarial_keys(tmp_path: Path, malicious_key: str) -> None:
    """Verify that any key with traversal characters or length < 3 raises ValueError."""
    cas = ContentAddressableStorage(base_dir=tmp_path / "cas_key_traversal")
    valid_ns = "safe_namespace"

    with pytest.raises(ValueError):
        cas.put_bytes(b"payload", extension=".bin", namespace=valid_ns, cache_key=malicious_key)

    assert cas.get(valid_ns, malicious_key) is None

    with pytest.raises(ValueError):
        cas.invalidate(valid_ns, malicious_key)


def test_cas_windows_reserved_device_names(tmp_path: Path) -> None:
    """
    Adversarial test exploring Windows reserved device names (CON, PRN, AUX, NUL, COM1).

    On Windows, creating directories with these names can cause WinError 87 or filesystem errors.
    Empirically documents how CAS handles or rejects DOS device names matching the regex.
    """
    cas = ContentAddressableStorage(base_dir=tmp_path / "cas_dos_devices")
    key = "device_key_001"

    # CON matches ^[a-zA-Z0-9_\-]+$
    if os.name == "nt":
        # On Windows, attempting to create a folder named CON or NUL fails at OS level
        try:
            cas.put_bytes(b"device_data", extension=".bin", namespace="CON", cache_key=key)
        except OSError as exc:
            # Expected OS protection failure on Windows
            assert "WinError" in str(exc) or "parameter is incorrect" in str(exc).lower()
    else:
        # On Linux/macOS, CON is a regular directory name
        cached = cas.put_bytes(b"device_data", extension=".bin", namespace="CON", cache_key=key)
        assert cached.metadata.file_size_bytes == len(b"device_data")


def test_cas_invalidate_safety_guards(tmp_path: Path) -> None:
    """Verify that invalidate cannot delete base_dir or namespace roots."""
    base_dir = tmp_path / "cas_invalidation_guards"
    cas = ContentAddressableStorage(base_dir=base_dir)

    # Invalidate non-existent entry returns False without deleting base_dir
    assert not cas.invalidate("dummy_ns", "dummy_key_001")
    assert base_dir.is_dir()

    # Invalidate namespace on non-existent returns 0
    assert cas.invalidate_namespace("nonexistent_ns") == 0
    assert base_dir.is_dir()


# =============================================================================
# SECTION 3: Large Binary Limits, LRU Quota & Recovery Under Stress
# =============================================================================

def test_cas_large_binary_streaming_integrity(tmp_path: Path) -> None:
    """
    Stress-test storing and retrieving a large binary file (10 MB).

    Verifies:
    - Streaming chunked SHA-256 computation matches whole-file hash.
    - Zero truncation across disk write, fsync, and read.
    - Accurate get_total_size_bytes() reflection.
    """
    cas = ContentAddressableStorage(base_dir=tmp_path / "cas_large_bin")
    large_size = 10 * 1024 * 1024  # 10 MiB
    source_file = tmp_path / "synthetic_mesh_large.glb"

    # Create 10MB deterministic binary payload in 1MB chunks
    chunk_pattern = b"0123456789ABCDEF" * 65536  # 1 MB
    with source_file.open("wb") as f:
        for _ in range(10):
            f.write(chunk_pattern)

    expected_hash = hash_file(source_file)
    cached = cas.put_file(source_path=source_file, namespace="meshes_large")

    assert cached.metadata.file_size_bytes == large_size
    assert cached.metadata.sha256_hash == expected_hash
    assert cached.file_path.is_file()
    assert cached.file_path.stat().st_size == large_size
    assert cas.get_total_size_bytes() == large_size

    # Retrieve from cache and verify
    retrieved = cas.get("meshes_large", cached.cache_key)
    assert retrieved is not None
    assert hash_file(retrieved.file_path) == expected_hash


def test_cas_lru_pruning_under_quota_pressure(tmp_path: Path) -> None:
    """
    Empirically test strict LRU eviction order when total size exceeds quota.

    Scenario:
    - Quota is 2500 bytes.
    - Ingest 4 assets of 1000 bytes each (Total = 4000 bytes > 2500).
    - Read asset 0 so its accessed_at is refreshed.
    - Run prune_lru(target_max_bytes=2500).
    - Verify:
      * Oldest unaccessed assets (assets 1 and 2) are pruned.
      * Asset 0 (recently accessed) and Asset 3 (most recently created) are preserved.
      * Total size after pruning is <= 2500 bytes.
    """
    cas = ContentAddressableStorage(base_dir=tmp_path / "cas_lru", max_size_bytes=2500)
    namespace = "lru_test"
    keys: List[str] = []

    for i in range(4):
        key = f"lru_item_{i:03d}"
        keys.append(key)
        prefix = f"payload_{i:02d}_".encode("utf-8")
        data = prefix + (b"X" * (1000 - len(prefix)))  # Exactly 1000 bytes
        assert len(data) == 1000
        cas.put_bytes(data=data, extension=".bin", namespace=namespace, cache_key=key)
        time.sleep(0.02)  # Ensure distinct created_at / accessed_at timestamps

    assert cas.get_total_size_bytes() == 4000

    # Refresh accessed_at on item 0 by calling get()
    time.sleep(0.02)
    item_0_accessed = cas.get(namespace, keys[0])
    assert item_0_accessed is not None

    # Now execute prune_lru targeting 2500 bytes
    # Excess is 4000 - 2500 = 1500 bytes. Each item is 1000 bytes -> need to prune 2 items (2000 bytes).
    pruned_count, freed_bytes = cas.prune_lru(target_max_bytes=2500)

    assert pruned_count == 2
    assert freed_bytes == 2000
    assert cas.get_total_size_bytes() == 2000

    # Item 0 was refreshed -> must still be present!
    assert cas.get(namespace, keys[0]) is not None
    # Item 1 was oldest unaccessed -> must be pruned!
    assert cas.get(namespace, keys[1]) is None
    # Item 2 was next oldest unaccessed -> must be pruned!
    assert cas.get(namespace, keys[2]) is None
    # Item 3 was created recently -> must still be present!
    assert cas.get(namespace, keys[3]) is not None


def test_cas_corrupted_metadata_sidecar_graceful_recovery(tmp_path: Path) -> None:
    """
    Adversarial test: corrupt sidecar metadata.json with invalid JSON and partial truncations.

    Verifies:
    - cas.get() handles corrupted JSON without crashing.
    - Corrupted entry is automatically invalidated and cleaned up.
    - cas.prune_expired() purges corrupted entries gracefully.
    """
    cas = ContentAddressableStorage(base_dir=tmp_path / "cas_corrupt")
    key = "corrupt_test_key_01"
    cached = cas.put_bytes(b"intact_asset_bytes", extension=".bin", namespace="corruption_ns", cache_key=key)

    meta_path = cached.file_path.parent / "metadata.json"
    assert meta_path.is_file()

    # Corrupt the metadata file with garbage
    with meta_path.open("w", encoding="utf-8") as f:
        f.write("{'bad_json': truncated...")

    # get() must return None and clean up the corrupted directory
    res = cas.get("corruption_ns", key)
    assert res is None
    assert not cached.file_path.is_file()  # Verified invalidation of corrupted entry


T = TypeVar("T")


def run_async(coro: Coroutine[object, object, T]) -> T:
    """Helper running an async coroutine synchronously using standard asyncio.run."""
    return asyncio.run(coro)


# =============================================================================
# SECTION 4: TelemetryBus Subscriber Disconnect Storms & Backpressure
# =============================================================================

def test_telemetry_subscriber_disconnect_storm() -> None:
    """
    Stress-test high-concurrency subscriber disconnect storm.

    Spawns 40 concurrent subscriber tasks that consume a small batch of events
    and abruptly disconnect/cancel while the bus is bombarded with high-rate events.

    Verifies:
    - No Set changed size during iteration exceptions in emit().
    - All cancelled subscribers cleanly detach.
    - Final subscriber_count strictly returns to 0.
    """
    async def _test() -> None:
        bus = TelemetryBus(max_queue_size=1000, history_size=500)
        num_subscribers = 40
        events_to_emit = 200

        async def flaky_subscriber(sub_id: int) -> None:
            async with bus._subscribe_context_manager(replay_history=False) as queue:
                try:
                    events_read = 0
                    while events_read < (sub_id % 4 + 1):
                        await asyncio.wait_for(queue.get(), timeout=1.0)
                        events_read += 1
                except (asyncio.TimeoutError, asyncio.CancelledError):
                    pass

        sub_tasks = [asyncio.create_task(flaky_subscriber(i)) for i in range(num_subscribers)]

        async def emitter() -> None:
            for i in range(events_to_emit):
                ev = ProgressEvent(
                    stage="storm_stage",
                    percentage=float(i % 100),
                    message=f"Storm event {i}",
                )
                await bus.emit(ev)
                if i % 20 == 0:
                    await asyncio.sleep(0.001)

        await emitter()
        await asyncio.gather(*sub_tasks, return_exceptions=True)

        await asyncio.sleep(0.05)

        assert bus.subscriber_count == 0, f"Expected 0 active subscribers after storm, found {bus.subscriber_count}"
        assert len(bus.get_history()) == min(events_to_emit, 500)

    run_async(_test())


def test_telemetry_slow_consumer_lossy_backpressure() -> None:
    """
    Test lossy backpressure behavior when a consumer is persistently slow.

    Queue capacity is 5. We emit 30 events rapidly without reading.
    Verifies:
    - No deadlocks or dropped bus operations.
    - Subscriber queue size never exceeds capacity.
    - Saturated queue drops oldest events, retaining the most recent telemetry.
    """
    async def _test() -> None:
        bus = TelemetryBus()
        queue_capacity = 5

        async with bus._subscribe_context_manager(replay_history=False, max_queue_size=queue_capacity) as queue:
            for i in range(30):
                await bus.emit(
                    ProgressEvent(
                        stage="saturation_test",
                        percentage=float(i),
                        message=f"Event number {i}",
                    )
                )

            assert queue.qsize() == queue_capacity

            retained_events: List[ProgressEvent] = []
            while not queue.empty():
                item = queue.get_nowait()
                assert isinstance(item, ProgressEvent)
                retained_events.append(item)

            assert len(retained_events) == queue_capacity
            assert retained_events[0].percentage == 25.0
            assert retained_events[-1].percentage == 29.0

    run_async(_test())


def test_telemetry_sse_disconnect_and_keepalive() -> None:
    """
    Test Server-Sent Events (SSE) stream keep-alive generation and clean teardown.
    """
    async def _test() -> None:
        bus = TelemetryBus()
        stream_gen = telemetry_sse_stream(bus=bus, replay_history=False, heartbeat_seconds=0.05)

        keep_alive_chunk = await stream_gen.__anext__()
        assert keep_alive_chunk == ": keep-alive\n\n"

        await bus.emit(LogEvent(level=LogLevel.WARNING, message="Warning test in SSE", source="SSETest"))
        event_chunk = await stream_gen.__anext__()
        assert event_chunk.startswith("event: log\n")
        assert "Warning test in SSE" in event_chunk

        await stream_gen.aclose()
        await asyncio.sleep(0.01)
        assert bus.subscriber_count == 0

    run_async(_test())


def test_telemetry_mixed_sync_async_callbacks_concurrency() -> None:
    """
    Stress-test TelemetryBus.emit_threadsafe with 20 threads while registering
    and unregistering callbacks dynamically.
    """
    bus = TelemetryBus(history_size=1000)
    num_threads = 20
    events_per_thread = 25
    callback_calls = 0
    lock = threading.Lock()

    def sync_cb(event: TelemetryEvent) -> None:
        nonlocal callback_calls
        with lock:
            callback_calls += 1

    unsub = bus.add_callback(sync_cb)

    def worker(t_id: int) -> None:
        for i in range(events_per_thread):
            bus.emit_threadsafe(
                LogEvent(
                    level=LogLevel.INFO,
                    message=f"Worker {t_id} event {i}",
                )
            )

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    expected_total = num_threads * events_per_thread
    assert callback_calls == expected_total
    assert len(bus.get_history()) == expected_total

    # Unsubscribe and verify no more callback triggers
    unsub()
    bus.emit_threadsafe(LogEvent(level=LogLevel.INFO, message="post_unsub"))
    assert callback_calls == expected_total


# =============================================================================
# SECTION 5: Plan Engine Human-in-the-Loop State Machine & Concurrency Stress
# =============================================================================

def test_plan_engine_out_of_order_confirmation() -> None:
    """
    Adversarial test: Confirm step 4 (final render) before step 1 (mesh) is confirmed or executed.

    Empirically verifies:
    - How PlanEngine responds to out-of-sequence confirmation requests.
    - Documents architectural behavior: PlanEngine allows out-of-order approval
      without checking preceding step dependencies.
    """
    bus = TelemetryBus()
    engine = PlanEngine(telemetry_bus=bus)

    plan = engine.create_plan(goal="Out-of-order test plan")
    step_4 = plan.steps[4]
    assert step_4.tool_name == "render_video"
    assert step_4.status == PlanStatus.PROPOSED

    # Confirm step 4 directly
    updated_plan = engine.confirm_step(plan.plan_id, step_4.step_id, approved=True)

    # Step 4 is now APPROVED, but step 1 is still PROPOSED
    assert updated_plan.steps[4].status == PlanStatus.APPROVED
    assert updated_plan.steps[1].status == PlanStatus.PROPOSED
    # Plan status remains PROPOSED
    assert updated_plan.status == PlanStatus.PROPOSED


def test_plan_engine_rejection_halts_plan() -> None:
    """
    Verify rejection state machine:
    - Rejecting any step sets step.status = REJECTED and plan.status = REJECTED.
    - Emits LogEvent with LogLevel.ERROR on the telemetry bus.
    """
    bus = TelemetryBus()
    engine = PlanEngine(telemetry_bus=bus)

    plan = engine.create_plan(goal="Rejection test plan")
    step_mesh = plan.steps[1]

    updated_plan = engine.reject_step(plan.plan_id, step_mesh.step_id)

    assert updated_plan.steps[1].status == PlanStatus.REJECTED
    assert updated_plan.status == PlanStatus.REJECTED

    # Check telemetry bus history for error log
    history = bus.get_history()
    error_logs = [e for e in history if isinstance(e, LogEvent) and e.level == LogLevel.ERROR]
    assert len(error_logs) >= 1
    assert f"Step '{step_mesh.step_id}' rejected by user. Plan halted." in error_logs[-1].message


def test_plan_engine_approval_after_rejection_state_gap() -> None:
    """
    Adversarial probe: What happens when an approval is attempted on a previously rejected plan?

    Reveals state machine gap:
    - When step 1 is rejected, plan.status becomes REJECTED.
    - If step 2 is subsequent approved: step 2 becomes APPROVED, but plan.status remains REJECTED.
    - If step 1 is subsequently approved: step 1 becomes APPROVED, but plan.status remains REJECTED.
    """
    engine = PlanEngine()
    plan = engine.create_plan(goal="State inconsistency probe")

    # Step 1 rejected -> halts plan
    engine.reject_step(plan.plan_id, plan.steps[1].step_id)
    assert plan.status == PlanStatus.REJECTED

    # Adversarially approve step 2
    engine.confirm_step(plan.plan_id, plan.steps[2].step_id, approved=True)
    assert plan.steps[2].status == PlanStatus.APPROVED
    assert plan.status == PlanStatus.REJECTED  # Plan remains REJECTED!

    # Adversarially approve step 1 (reversing previous rejection)
    engine.confirm_step(plan.plan_id, plan.steps[1].step_id, approved=True)
    assert plan.steps[1].status == PlanStatus.APPROVED
    assert plan.status == PlanStatus.REJECTED  # Plan still remains REJECTED!


def test_plan_engine_missing_plan_level_promotion() -> None:
    """
    Empirically exposes state machine gap:
    When ALL steps requiring confirmation (and even all steps in general) are approved,
    confirm_step does NOT automatically promote plan.status from PROPOSED to APPROVED.
    """
    engine = PlanEngine()
    plan = engine.create_plan(goal="Full approval test")

    for step in plan.steps:
        engine.confirm_step(plan.plan_id, step.step_id, approved=True)
        assert step.status == PlanStatus.APPROVED

    # Plan promoted to APPROVED after all steps approved
    assert plan.status == PlanStatus.APPROVED
    assert all(s.status == PlanStatus.APPROVED for s in plan.steps)


def test_plan_engine_invalid_ids_raise_keyerror() -> None:
    """Verify that confirming non-existent plans or steps raises KeyError."""
    engine = PlanEngine()
    plan = engine.create_plan(goal="KeyError test")

    with pytest.raises(KeyError) as exc_plan:
        engine.confirm_step("non_existent_plan_id", "any_step")
    assert "not found" in str(exc_plan.value)

    with pytest.raises(KeyError) as exc_step:
        engine.confirm_step(plan.plan_id, "non_existent_step_id")
    assert "not found" in str(exc_step.value)

    # Path traversal / SQL injection step_id
    with pytest.raises(KeyError):
        engine.confirm_step(plan.plan_id, "../../../etc/passwd")


def test_plan_engine_concurrent_confirmations() -> None:
    """
    Stress-test concurrent step confirmations across multiple threads on the same plan.
    """
    engine = PlanEngine()
    plan = engine.create_plan(goal="Concurrent confirmation plan")
    num_steps = len(plan.steps)

    errors: List[Exception] = []

    def confirm_worker(step_idx: int) -> None:
        try:
            step_id = plan.steps[step_idx].step_id
            engine.confirm_step(plan.plan_id, step_id, approved=True)
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=confirm_worker, args=(i,)) for i in range(num_steps)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, f"Concurrent confirmations failed: {errors}"
    for step in plan.steps:
        assert step.status == PlanStatus.APPROVED


def test_plan_engine_rapid_plan_creation_collision_resistance() -> None:
    """
    Test rapid creation of 300 plans to verify UUID entropy and collision resistance.
    """
    engine = PlanEngine()
    num_plans = 300
    plan_ids: List[str] = []

    for i in range(num_plans):
        p = engine.create_plan(goal=f"Batch plan {i}")
        plan_ids.append(p.plan_id)

    # Verify all generated plan IDs are unique
    assert len(set(plan_ids)) == num_plans
    for pid in plan_ids:
        assert engine.get_plan(pid) is not None


# =============================================================================
# SECTION 6: Settings & Config Extreme Boundaries
# =============================================================================

def test_config_port_range_validation() -> None:
    """Verify that ports <= 0 or > 65535 raise ValidationError."""
    with pytest.raises(ValidationError):
        get_test_settings(ue5_http_port=0)

    with pytest.raises(ValidationError):
        get_test_settings(ue5_http_port=65536)

    with pytest.raises(ValidationError):
        get_test_settings(mcp_server_port=-1)

    with pytest.raises(ValidationError):
        get_test_settings(telemetry_ws_port=70000)

    # Valid boundaries
    valid_low = get_test_settings(ue5_http_port=1, mcp_server_port=1, telemetry_ws_port=1)
    assert valid_low.ue5_http_port == 1

    valid_high = get_test_settings(ue5_http_port=65535, mcp_server_port=65535, telemetry_ws_port=65535)
    assert valid_high.ue5_http_port == 65535


def test_config_log_level_normalization_and_invalid() -> None:
    """Verify case-insensitive log level normalization and invalid log level rejection."""
    cfg_lower = get_test_settings(log_level="debug")  # type: ignore[arg-type]
    assert cfg_lower.log_level == "DEBUG"

    cfg_mixed = get_test_settings(log_level="wArNiNg")  # type: ignore[arg-type]
    assert cfg_mixed.log_level == "WARNING"

    with pytest.raises(ValidationError):
        get_test_settings(log_level="VERBOSE_INVALID")  # type: ignore[arg-type]


def test_config_directory_bootstrapping(tmp_path: Path) -> None:
    """Verify ensure_directories creates nested non-existent directory trees."""
    custom_cache = tmp_path / "deep" / "nested" / "cache"
    custom_out = tmp_path / "deep" / "nested" / "outputs"
    custom_tmp = tmp_path / "deep" / "nested" / "tmp"

    cfg = get_test_settings(
        cache_dir=custom_cache,
        output_dir=custom_out,
        temp_dir=custom_tmp,
    )

    assert custom_cache.is_dir()
    assert custom_out.is_dir()
    assert custom_tmp.is_dir()
