"""
Adversarial Stress Test Suite for Milestone 1: Core Models, TelemetryBus, and CAS Cache.

Executed by EMPIRICAL CHALLENGER to stress-test assumptions, edge cases,
race conditions, high concurrency, and failure modes across:
1. Pydantic Domain Models (extreme values, type mismatches, forbidden fields)
2. TelemetryBus (high-concurrency emission, slow consumer drop policies, thread-safe bridges)
3. CAS Asset Cache (multi-threaded concurrent atomic writes, key collisions, LRU pruning races)
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import tempfile
import threading
import time
from typing import Dict, List, Optional

from pydantic import ValidationError
import pytest

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
    AudioAnalysisRequest,
    AudioAnalysisResult,
    AudioStemType,
    AutoRigRequest,
    AutoRigResult,
    BoneDescriptor,
    CameraKeyframe,
    ColorRGB,
    ImageTo3DRequest,
    ImageTo3DResult,
    LogEvent,
    LogLevel,
    LumenLightConfig,
    MeshFormat,
    MocapExtractionRequest,
    MocapResult,
    MovieRenderQueueJobConfig,
    PBRTextureSet,
    PlanConfirmationRequest,
    PlanConfirmationResponse,
    PlanProposalEvent,
    PlanRiskLevel,
    PlanStatus,
    PlanStep,
    ProductionPlan,
    ProgressEvent,
    RenderResult,
    Rotator3D,
    SceneBuildResult,
    SceneConfig,
    SkeletalHierarchy,
    StemSeparationResult,
    TelemetryEvent,
    Vector3D,
)
from backend.core.telemetry import (
    FastMCPTelemetryBridge,
    TelemetryBus,
    emit_asset_ready,
    emit_asset_ready_sync,
    emit_log,
    emit_log_sync,
    emit_progress,
    emit_progress_sync,
)


# =============================================================================
# PART 1: ADVERSARIAL MODEL STRESS TESTS
# =============================================================================

class TestModelAdversarial:
    """Stress tests and boundary condition probing for domain models."""

    def test_strict_model_extra_field_injection_fails(self) -> None:
        """StrictBaseModel must reject unexpected extra attributes (Zero-Any enforcement)."""
        with pytest.raises(ValidationError):
            Vector3D.model_validate({"x": 1.0, "y": 2.0, "z": 3.0, "malicious_injected_field": "hack"})

        with pytest.raises(ValidationError):
            ColorRGB.model_validate({"r": 0.5, "g": 0.5, "b": 0.5, "alpha": 1.0})

        with pytest.raises(ValidationError):
            ImageTo3DRequest.model_validate({"image_path": "valid.png", "unknown_knob": 123})

    def test_color_rgb_extreme_boundaries(self) -> None:
        """ColorRGB must strictly clamp/validate [0.0, 1.0]."""
        # Valid boundary
        c_low = ColorRGB(r=0.0, g=0.0, b=0.0)
        c_high = ColorRGB(r=1.0, g=1.0, b=1.0)
        assert c_low.to_tuple() == (0.0, 0.0, 0.0)
        assert c_high.to_tuple() == (1.0, 1.0, 1.0)

        # Negative boundary
        with pytest.raises(ValidationError):
            ColorRGB(r=-0.000001, g=0.5, b=0.5)

        # Overflow boundary
        with pytest.raises(ValidationError):
            ColorRGB(r=1.000001, g=0.5, b=0.5)

        # Huge values (e.g. 255 int instead of float normalized)
        with pytest.raises(ValidationError):
            ColorRGB(r=255.0, g=128.0, b=0.0)

    def test_audio_request_adversarial_inputs(self) -> None:
        """AudioAnalysisRequest boundary constraints on sample rate, path, and bpm."""
        # Empty path
        with pytest.raises(ValidationError):
            AudioAnalysisRequest(audio_path="")

        # Sample rate below 8000 Hz
        with pytest.raises(ValidationError):
            AudioAnalysisRequest(audio_path="test.wav", sample_rate=7999)

        # Sample rate above 192000 Hz
        with pytest.raises(ValidationError):
            AudioAnalysisRequest(audio_path="test.wav", sample_rate=192001)

        # BPM hint out of human musical range
        with pytest.raises(ValidationError):
            AudioAnalysisRequest(audio_path="test.wav", bpm_hint=10.0)

        with pytest.raises(ValidationError):
            AudioAnalysisRequest(audio_path="test.wav", bpm_hint=600.0)

    def test_audio_analysis_result_large_payload(self) -> None:
        """AudioAnalysisResult handling large timestamp arrays (e.g. 50,000 beats)."""
        large_beats = [i * 0.5 for i in range(50000)]
        large_envelope = [0.1 * (i % 10) for i in range(50000)]
        res = AudioAnalysisResult(
            bpm=120.0,
            duration_seconds=25000.0,
            beat_timestamps=large_beats,
            onset_envelope=large_envelope,
            danceability=0.85,
        )
        assert len(res.beat_timestamps) == 50000
        assert len(res.onset_envelope) == 50000
        assert res.danceability == 0.85

        # Danceability bounds
        with pytest.raises(ValidationError):
            AudioAnalysisResult(bpm=120.0, duration_seconds=10.0, danceability=-0.1)
        with pytest.raises(ValidationError):
            AudioAnalysisResult(bpm=120.0, duration_seconds=10.0, danceability=1.05)

    def test_mrq_job_config_resolution_regex_adversarial(self) -> None:
        """MovieRenderQueueJobConfig must only accept valid WIDTHxHEIGHT format."""
        valid_resolutions = ["1920x1080", "3840x2160", "1280x720", "512x512", "7680x4320"]
        for res in valid_resolutions:
            cfg = MovieRenderQueueJobConfig(scene_path="/Game/Seq", output_path="out.mp4", resolution=res)
            w, h = cfg.get_resolution_dimensions()
            assert f"{w}x{h}" == res

        invalid_resolutions = [
            "1920",
            "1920x",
            "x1080",
            "1920_1080",
            "1920*1080",
            "1920x1080x720",
            "FHD",
            "1920x1080\n",
            "1920 x 1080",
            "-1920x1080",
        ]
        for inv in invalid_resolutions:
            with pytest.raises(ValidationError, match="resolution"):
                MovieRenderQueueJobConfig(scene_path="/Game/Seq", output_path="out.mp4", resolution=inv)

    def test_camera_keyframe_normalization_adversarial(self) -> None:
        """CameraKeyframe handles tuple inputs, flat inputs, and rejects invalid bounds."""
        # Flat format
        kf1 = CameraKeyframe(time=2.5, x=100.0, y=200.0, z=50.0, pitch=-15.0, yaw=90.0, roll=0.0, fov=45.0)
        assert kf1.timestamp == 2.5
        assert kf1.position == (100.0, 200.0, 50.0)
        assert kf1.rotation == (-15.0, 90.0, 0.0)

        # Tuple format normalization via model_validate
        kf2 = CameraKeyframe.model_validate({
            "timestamp": 4.0,
            "position": [300.0, -100.0, 150.0],
            "rotation": [0.0, 180.0, 0.0],
            "fov": 75.0,
        })
        assert kf2.time == 4.0
        assert kf2.timestamp == 4.0
        assert kf2.x == 300.0
        assert kf2.y == -100.0
        assert kf2.z == 150.0
        assert kf2.yaw == 180.0

        # Out-of-bounds fov (gt 0, lt 180)
        with pytest.raises(ValidationError):
            CameraKeyframe(fov=0.0)
        with pytest.raises(ValidationError):
            CameraKeyframe(fov=180.0)
        with pytest.raises(ValidationError):
            CameraKeyframe(fov=-10.0)

        # Out-of-bounds focal length (ge 1.0, le 500.0)
        with pytest.raises(ValidationError):
            CameraKeyframe(focal_length=0.5)
        with pytest.raises(ValidationError):
            CameraKeyframe(focal_length=501.0)

        # Out-of-bounds aperture (ge 0.7, le 22.0)
        with pytest.raises(ValidationError):
            CameraKeyframe(aperture=0.5)
        with pytest.raises(ValidationError):
            CameraKeyframe(aperture=32.0)

    def test_plan_step_strictly_typed_parameters(self) -> None:
        """PlanStep parameters dictionary must conform strictly to typed JSON values."""
        # Valid primitive types
        step = PlanStep(
            step_id="step_01",
            tool_name="analyze_audio",
            description="Extract audio features",
            parameters={
                "audio_path": "track.mp3",
                "sample_rate": 44100,
                "confidence": 0.95,
                "separate_stems": True,
                "stem_list": ["vocals", "drums", "bass"],
                "options": {"mode": "fast", "device": "cuda"},
            },
        )
        assert step.parameters["sample_rate"] == 44100
        assert step.parameters["separate_stems"] is True

        # Invalid parameter value (e.g. arbitrary object, tuple of tuples)
        with pytest.raises(ValidationError):
            PlanStep(
                step_id="step_bad",
                tool_name="foo",
                description="bar",
                parameters={"bad_obj": object()},  # type: ignore[dict-item]
            )

    def test_telemetry_event_polymorphic_adversarial(self) -> None:
        """TelemetryEvent.model_validate handles missing, invalid, and extreme event payloads."""
        # Valid polymorphic types
        p_event = TelemetryEvent.model_validate({
            "type": "progress",
            "stage": "rendering",
            "percentage": 50.0,
            "message": "Halfway done",
        })
        assert isinstance(p_event, ProgressEvent)
        assert p_event.percentage == 50.0

        # Percentage bounds (0.0 to 100.0)
        with pytest.raises(ValidationError):
            TelemetryEvent.model_validate({
                "type": "progress",
                "stage": "rendering",
                "percentage": -0.1,
                "message": "Underflow",
            })

        with pytest.raises(ValidationError):
            TelemetryEvent.model_validate({
                "type": "progress",
                "stage": "rendering",
                "percentage": 100.1,
                "message": "Overflow",
            })

        # Missing type field
        with pytest.raises(ValidationError):
            TelemetryEvent.model_validate({"stage": "rendering", "percentage": 50.0})

        # Unknown type string fallback: creates raw TelemetryEvent without crashing
        raw_event = TelemetryEvent.model_validate({"type": "custom_extension_event", "foo": "bar"})
        assert type(raw_event) is TelemetryEvent
        assert raw_event.type == "custom_extension_event"


# =============================================================================
# PART 2: CONCURRENCY & STRESS ON TelemetryBus
# =============================================================================

class TestTelemetryBusAdversarial:
    """Stress tests on TelemetryBus for saturation, slow consumers, and thread races."""

    def test_rapid_emission_high_concurrency(self) -> None:
        """10 concurrent async producers emitting 500 events each to 5 concurrent subscribers with cooperative yielding."""
        async def run_stress() -> None:
            bus = TelemetryBus(max_queue_size=2000, history_size=500)
            num_producers = 10
            events_per_producer = 500
            total_expected_events = num_producers * events_per_producer

            consumer_counts: List[int] = [0] * 5
            queues: List[asyncio.Queue[TelemetryEvent]] = []

            for i in range(5):
                q: asyncio.Queue[TelemetryEvent] = asyncio.Queue(maxsize=10000)
                bus.add_subscriber(q)
                queues.append(q)

            stop_event = asyncio.Event()

            async def consumer(idx: int, q: asyncio.Queue[TelemetryEvent]) -> None:
                while not stop_event.is_set() or not q.empty():
                    try:
                        event = await asyncio.wait_for(q.get(), timeout=0.05)
                        consumer_counts[idx] += 1
                        q.task_done()
                    except asyncio.TimeoutError:
                        if stop_event.is_set():
                            break

            async def producer(p_id: int) -> None:
                for seq in range(events_per_producer):
                    ev = ProgressEvent(
                        stage=f"producer_{p_id}",
                        percentage=float(seq % 100),
                        message=f"Event {seq} from producer {p_id}",
                    )
                    await bus.emit(ev)
                    if seq % 10 == 0:
                        await asyncio.sleep(0)  # Cooperative yield to event loop

            consumer_tasks = [asyncio.create_task(consumer(i, queues[i])) for i in range(5)]
            producer_tasks = [asyncio.create_task(producer(p)) for p in range(num_producers)]

            # Wait for all producers to finish emitting
            await asyncio.gather(*producer_tasks)

            # Allow consumers to drain remaining queue completely
            drain_deadline = time.time() + 5.0
            while any(not q.empty() for q in queues) and time.time() < drain_deadline:
                await asyncio.sleep(0.02)
            stop_event.set()
            await asyncio.gather(*consumer_tasks)

            # Cleanup
            for q in queues:
                bus.remove_subscriber(q)

            # Verify every consumer received all 5,000 events
            for i, count in enumerate(consumer_counts):
                assert count == total_expected_events, f"Consumer {i} received {count}/{total_expected_events}"

            # History capped at configured max
            assert len(bus.get_history()) == 500

        asyncio.run(run_stress())


    def test_slow_consumer_drop_policy(self) -> None:
        """
        Verify lossy backpressure drop policy:
        When a subscriber queue is saturated, oldest events are dropped and newest preserved.
        """
        async def run_drop_test() -> None:
            # Create bus and queue with small capacity (e.g. 5)
            bus = TelemetryBus(max_queue_size=5, history_size=50)
            slow_queue: asyncio.Queue[TelemetryEvent] = asyncio.Queue(maxsize=5)
            bus.add_subscriber(slow_queue)

            # Emit 50 events rapidly without consuming
            for i in range(50):
                await bus.emit(ProgressEvent(
                    stage="drop_test",
                    percentage=float(i),
                    message=f"Event {i}",
                ))

            # Queue must not be over capacity
            assert slow_queue.qsize() == 5

            # Drain and inspect items
            drained_events: List[ProgressEvent] = []
            while not slow_queue.empty():
                item = slow_queue.get_nowait()
                assert isinstance(item, ProgressEvent)
                drained_events.append(item)

            # Must contain the newest events (45 through 49), NOT the oldest (0 through 4)
            expected_percentages = [45.0, 46.0, 47.0, 48.0, 49.0]
            actual_percentages = [e.percentage for e in drained_events]
            assert actual_percentages == expected_percentages, f"Expected {expected_percentages}, got {actual_percentages}"

            bus.remove_subscriber(slow_queue)

        asyncio.run(run_drop_test())

    def test_faulty_and_slow_callbacks_do_not_crash_bus(self) -> None:
        """Exceptions in synchronous/asynchronous callbacks must not crash or halt the bus."""
        async def run_callback_test() -> None:
            bus = TelemetryBus()
            received_by_healthy: List[TelemetryEvent] = []

            def bad_callback(ev: TelemetryEvent) -> None:
                raise RuntimeError("Simulated callback explosion!")

            def healthy_callback(ev: TelemetryEvent) -> None:
                received_by_healthy.append(ev)

            bus.add_callback(bad_callback)
            bus.add_callback(healthy_callback)

            # Emit an event
            event = LogEvent(message="Testing resilient callbacks", level=LogLevel.INFO)
            await bus.emit(event)

            # Healthy callback must still have received the event
            assert len(received_by_healthy) == 1
            assert received_by_healthy[0].type == "log"

        asyncio.run(run_callback_test())

    def test_concurrent_subscribe_unsubscribe_churn(self) -> None:
        """Producers emitting while subscribers dynamically subscribe and unsubscribe continuously."""
        async def run_churn() -> None:
            bus = TelemetryBus(max_queue_size=100)
            churn_active = True

            async def churner() -> None:
                while churn_active:
                    q: asyncio.Queue[TelemetryEvent] = asyncio.Queue(maxsize=10)
                    bus.add_subscriber(q)
                    await asyncio.sleep(0.001)
                    bus.remove_subscriber(q)

            async def producer() -> None:
                for i in range(500):
                    await bus.emit(ProgressEvent(stage="churn", percentage=float(i % 100), message=f"Churn {i}"))
                    if i % 50 == 0:
                        await asyncio.sleep(0.001)

            churners = [asyncio.create_task(churner()) for _ in range(5)]
            producers = [asyncio.create_task(producer()) for _ in range(3)]

            await asyncio.gather(*producers)
            churn_active = False
            await asyncio.gather(*churners)

        asyncio.run(run_churn())

    def test_multithreaded_emit_threadsafe(self) -> None:
        """20 OS threads emitting events concurrently via emit_threadsafe to an active asyncio event loop."""
        async def run_multithread() -> None:
            loop = asyncio.get_running_loop()
            bus = TelemetryBus(max_queue_size=5000, history_size=2000)
            bus.set_event_loop(loop)

            received_events: List[TelemetryEvent] = []
            queue: asyncio.Queue[TelemetryEvent] = asyncio.Queue(maxsize=5000)
            bus.add_subscriber(queue)

            num_threads = 10
            events_per_thread = 50
            total_expected = num_threads * events_per_thread

            def worker_thread(thread_id: int) -> None:
                for i in range(events_per_thread):
                    emit_progress_sync(
                        stage=f"thread_{thread_id}",
                        percentage=float(i),
                        message=f"T{thread_id}-E{i}",
                        bus=bus,
                    )

            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = [executor.submit(worker_thread, t) for t in range(num_threads)]
                for f in futures:
                    f.result()

            # Drain queue in asyncio loop
            stop_time = loop.time() + 3.0
            while len(received_events) < total_expected and loop.time() < stop_time:
                try:
                    ev = await asyncio.wait_for(queue.get(), timeout=0.1)
                    received_events.append(ev)
                    queue.task_done()
                except asyncio.TimeoutError:
                    break

            assert len(received_events) == total_expected, f"Expected {total_expected}, received {len(received_events)}"
            bus.remove_subscriber(queue)

        asyncio.run(run_multithread())

    def test_emit_threadsafe_double_invocation_and_history_duplication(self) -> None:
        """
        Verify that emit_threadsafe does NOT duplicate events or callback invocations
        when scheduled on a running event loop.
        """
        async def run_test() -> None:
            loop = asyncio.get_running_loop()
            bus = TelemetryBus()
            bus.set_event_loop(loop)
            call_count = 0
            calling_threads: List[str] = []

            def sync_cb(ev: TelemetryEvent) -> None:
                nonlocal call_count
                call_count += 1
                calling_threads.append(threading.current_thread().name)

            bus.add_callback(sync_cb)

            def worker() -> None:
                bus.emit_threadsafe(LogEvent(message="single_event", level=LogLevel.INFO))

            t = threading.Thread(target=worker, name="WorkerThread")
            t.start()
            t.join()

            await asyncio.sleep(0.05)

            # Verified: Callback is invoked exactly once
            assert call_count == 1, f"Expected 1 invocation, got {call_count}"
            assert "MainThread" in calling_threads

            # Verified: History contains exactly 1 event
            history = bus.get_history()
            assert len(history) == 1, f"History should contain 1 item, got {len(history)}"
            assert history[0].message == "single_event"

        asyncio.run(run_test())




# =============================================================================
# PART 3: CONCURRENCY & STRESS ON CAS ASSET CACHE
# =============================================================================

class TestCASCacheAdversarial:
    """Stress tests on Content-Addressable Storage for race conditions and data integrity."""

    @pytest.fixture
    def temp_cas(self) -> ContentAddressableStorage:
        """Create an isolated temporary CAS instance."""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_cas_adversarial_"))
        cas = ContentAddressableStorage(base_dir=temp_dir, max_size_bytes=10 * 1024 * 1024)
        yield cas
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_concurrent_atomic_writes_identical_key(self, temp_cas: ContentAddressableStorage) -> None:
        """
        10 threads writing to the EXACT same cache key simultaneously.
        Must execute without PermissionError, unhandled race exceptions, or corrupted sidecars.
        """
        num_threads = 10
        cache_key = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
        namespace = "race_test"
        payload = b"IDENTICAL_PAYLOAD_CONTENT" * 1024  # 25 KB
        results: List[CachedAsset] = []
        errors: List[Exception] = []

        def writer_thread(idx: int) -> None:
            try:
                asset = temp_cas.put_bytes(
                    data=payload,
                    extension=".bin",
                    namespace=namespace,
                    cache_key=cache_key,
                    params={"worker": idx},
                )
                results.append(asset)
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=writer_thread, args=(i,)) for i in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Encountered write errors: {errors}"
        assert len(results) == num_threads

        # Verify final state on disk
        asset = temp_cas.get(namespace, cache_key)
        assert asset is not None
        assert asset.file_path.is_file()
        assert asset.file_path.read_bytes() == payload
        assert asset.metadata.sha256_hash == hash_bytes(payload)

    def test_concurrent_writes_high_volume(self, temp_cas: ContentAddressableStorage) -> None:
        """
        10 threads concurrently writing 20 distinct files each (200 total assets).
        Verify zero file corruption, zero collisions, and 100% retrieval success.
        """
        num_threads = 10
        files_per_thread = 20
        total_files = num_threads * files_per_thread
        namespace = "volume_test"

        def worker(thread_idx: int) -> None:
            for f_idx in range(files_per_thread):
                content = f"Payload from thread {thread_idx} file {f_idx}".encode("utf-8")
                temp_cas.put_bytes(
                    data=content,
                    extension=".txt",
                    namespace=namespace,
                    params={"t": thread_idx, "f": f_idx},
                )

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker, t) for t in range(num_threads)]
            for f in futures:
                f.result()

        # Verify all assets can be read without error
        retrieved_count = 0
        for t in range(num_threads):
            for f in range(files_per_thread):
                content = f"Payload from thread {t} file {f}".encode("utf-8")
                key = compute_composite_cache_key(namespace, [hash_bytes(content)], {"t": t, "f": f})
                cached = temp_cas.get(namespace, key)
                assert cached is not None, f"Failed to retrieve key for t={t}, f={f}"
                assert cached.file_path.read_bytes() == content
                retrieved_count += 1

        assert retrieved_count == total_files

    def test_corrupted_metadata_graceful_recovery(self, temp_cas: ContentAddressableStorage) -> None:
        """
        If metadata.json on disk is corrupted, get() must safely invalidate it
        and return None instead of raising JSONDecodeError.
        """
        namespace = "corrupt_test"
        asset = temp_cas.put_bytes(
            data=b"valid asset data",
            extension=".dat",
            namespace=namespace,
        )

        entry_dir = temp_cas._get_entry_dir(namespace, asset.cache_key)
        meta_file = entry_dir / "metadata.json"
        assert meta_file.is_file()

        # Intentionally write corrupted raw non-JSON garbage into metadata.json
        meta_file.write_text("CORRUPTED_NON_JSON_GARBAGE {{{<<<>>>", encoding="utf-8")

        # Ingestion lookup must safely handle the corruption
        recovered = temp_cas.get(namespace, asset.cache_key)
        assert recovered is None, "Corrupted metadata should yield None"

        # The corrupted entry directory should have been purged
        assert not entry_dir.is_dir(), "Corrupted entry directory should be deleted"

    def test_missing_asset_file_graceful_recovery(self, temp_cas: ContentAddressableStorage) -> None:
        """
        If metadata exists but the asset file on disk was manually removed,
        get() must detect the inconsistency, invalidate, and return None.
        """
        namespace = "missing_asset_test"
        asset = temp_cas.put_bytes(
            data=b"temporary asset",
            extension=".bin",
            namespace=namespace,
        )

        # Delete the asset file directly
        asset.file_path.unlink()

        # Lookup must return None and clean up orphaned metadata
        result = temp_cas.get(namespace, asset.cache_key)
        assert result is None
        assert not asset.file_path.parent.is_dir()

    def test_concurrent_lru_prune_race(self, temp_cas: ContentAddressableStorage) -> None:
        """
        Race test: Writers adding files while another thread continuously triggers prune_lru.
        Must not produce unhandled file-not-found or lock crash.
        """
        namespace = "lru_race"
        stop_event = threading.Event()
        errors: List[Exception] = []

        def writer(w_id: int) -> None:
            count = 0
            while not stop_event.is_set() and count < 40:
                try:
                    data = os.urandom(1024 * 10)  # 10 KB
                    temp_cas.put_bytes(
                        data=data,
                        extension=".bin",
                        namespace=namespace,
                        params={"w": w_id, "c": count},
                    )
                    count += 1
                    time.sleep(0.002)
                except Exception as exc:
                    errors.append(exc)

        def pruner() -> None:
            while not stop_event.is_set():
                try:
                    # Target small quota (e.g. 50 KB) to trigger frequent evictions
                    temp_cas.prune_lru(target_max_bytes=50 * 1024)
                    time.sleep(0.005)
                except Exception as exc:
                    errors.append(exc)

        writers = [threading.Thread(target=writer, args=(i,)) for i in range(4)]
        pruning_thread = threading.Thread(target=pruner)

        for w in writers:
            w.start()
        pruning_thread.start()

        for w in writers:
            w.join()

        stop_event.set()
        pruning_thread.join()

        assert len(errors) == 0, f"Errors encountered during concurrent LRU pruning: {errors}"

    def test_vulnerability_invalidate_empty_key_wipes_entire_namespace(self, temp_cas: ContentAddressableStorage) -> None:
        """
        Verify that calling cas.invalidate(namespace, "") raises ValueError
        and does NOT wipe the namespace directory.
        """
        namespace = "critical_ns"
        temp_cas.put_bytes(b"asset_1", ".txt", namespace, cache_key="1111111111111111111111111111111111111111111111111111111111111111")
        temp_cas.put_bytes(b"asset_2", ".txt", namespace, cache_key="2222222222222222222222222222222222222222222222222222222222222222")

        ns_dir = temp_cas.base_dir / namespace
        assert ns_dir.is_dir()

        # Invalidate with empty key must raise ValueError
        with pytest.raises(ValueError, match="Invalid cache_key"):
            temp_cas.invalidate(namespace, "")

        # Entire namespace folder remains intact!
        assert ns_dir.is_dir(), "Namespace directory must not be wiped!"

    def test_vulnerability_invalidate_empty_namespace_wipes_base_dir(self, temp_cas: ContentAddressableStorage) -> None:
        """
        Verify that calling cas.invalidate("", "") raises ValueError
        and does NOT delete self.base_dir.
        """
        temp_cas.put_bytes(b"data", ".txt", "some_ns", cache_key="3333333333333333333333333333333333333333333333333333333333333333")
        assert temp_cas.base_dir.is_dir()

        # Invalidate with empty namespace must raise ValueError
        with pytest.raises(ValueError, match="Invalid namespace"):
            temp_cas.invalidate("", "")

        # Base directory remains intact!
        assert temp_cas.base_dir.is_dir(), "Base cache directory must not be wiped!"

    def test_vulnerability_path_traversal_escapes_base_dir(self, temp_cas: ContentAddressableStorage) -> None:
        """
        Verify that passing a namespace containing '../' raises ValueError
        and does not resolve outside base_dir.
        """
        with pytest.raises(ValueError, match="Invalid namespace"):
            temp_cas._get_entry_dir("../../escaped_sandbox", "4444444444444444444444444444444444444444444444444444444444444444")

    def test_params_hash_type_error_on_path_object(self) -> None:
        """
        Verify that canonical_params_hash cleanly supports Path objects.
        """
        digest = canonical_params_hash({"source_file": Path("test/model.glb")})
        assert isinstance(digest, str) and len(digest) == 64
        assert digest == canonical_params_hash({"source_file": "test/model.glb"})
