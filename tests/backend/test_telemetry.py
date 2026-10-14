"""
Unit test suite for backend.core.telemetry.

Tests TelemetryBus event broadcast, callback subscribers, history replay,
FastMCP telemetry bridge, threadsafe emitters, and SSE streaming.
Uses asyncio.run for portable async execution without external pytest plugin dependencies.
"""

from __future__ import annotations

import asyncio
from typing import Callable, Coroutine, List, TypeVar
import pytest

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
    emit_asset_ready,
    emit_asset_ready_sync,
    emit_log,
    emit_log_sync,
    emit_plan_proposal,
    emit_progress,
    emit_progress_sync,
    get_telemetry_bus,
    reset_telemetry_bus,
    telemetry_sse_stream,
)

T = TypeVar("T")


def run_async(coro: Coroutine[object, object, T]) -> T:
    """Helper running an async coroutine synchronously using standard asyncio.run."""
    return asyncio.run(coro)


@pytest.fixture(autouse=True)
def clean_bus() -> None:
    reset_telemetry_bus()


def test_telemetry_bus_publish_subscribe() -> None:
    async def _test() -> None:
        bus = TelemetryBus(max_queue_size=10)

        async with bus._subscribe_context_manager(replay_history=False) as queue:
            assert bus.subscriber_count == 1

            ev = ProgressEvent(stage="audio", percentage=25.0, message="Analyzing beats")
            await bus.emit(ev)

            received = await asyncio.wait_for(queue.get(), timeout=1.0)
            assert isinstance(received, ProgressEvent)
            assert received.percentage == 25.0
            assert received.stage == "audio"

        assert bus.subscriber_count == 0

    run_async(_test())


def test_telemetry_bus_callback_subscriber() -> None:
    bus = TelemetryBus()
    received_events: List[TelemetryEvent] = []

    def on_event(ev: TelemetryEvent) -> None:
        received_events.append(ev)

    unsub = bus.subscribe(on_event)
    assert bus.subscriber_count == 1

    ev = LogEvent(level=LogLevel.INFO, message="Pipeline booted")
    bus.emit_threadsafe(ev)

    assert len(received_events) == 1
    assert isinstance(received_events[0], LogEvent)
    assert received_events[0].message == "Pipeline booted"

    # Unsubscribe
    unsub()
    assert bus.subscriber_count == 0

    bus.emit_threadsafe(LogEvent(level=LogLevel.INFO, message="Second log"))
    assert len(received_events) == 1


def test_telemetry_bus_history_and_latest() -> None:
    async def _test() -> None:
        bus = TelemetryBus(history_size=5)

        ev_prog = ProgressEvent(stage="mesh", percentage=80.0, message="Baking textures")
        ev_plan = PlanProposalEvent(plan_id="p1", steps=[], status=PlanStatus.PROPOSED)
        ev_log = LogEvent(message="Baking done")

        await bus.emit(ev_prog)
        await bus.emit(ev_plan)
        await bus.emit(ev_log)

        history = bus.get_history()
        assert len(history) == 3

        assert bus.get_latest_progress() is not None
        assert bus.get_latest_progress().percentage == 80.0

        assert bus.get_latest_plan() is not None
        assert bus.get_latest_plan().plan_id == "p1"

        # History replay on new subscriber
        async with bus._subscribe_context_manager(replay_history=True) as queue:
            assert queue.qsize() == 3

        bus.clear_history()
        assert len(bus.get_history()) == 0
        assert bus.get_latest_progress() is None

    run_async(_test())


def test_async_emission_helpers() -> None:
    async def _test() -> None:
        bus = TelemetryBus()

        prog = await emit_progress(
            stage="mocap",
            percentage=150.0,  # Should clamp to 100.0
            message="Extracting poses",
            bus=bus,
        )
        assert prog.percentage == 100.0

        log = await emit_log(message="Pose tracked", level=LogLevel.INFO, bus=bus)
        assert log.message == "Pose tracked"

        asset = await emit_asset_ready(
            asset_id="asset_42",
            asset_type=AssetType.MOCAP,
            file_path="/data/dance.glb",
            bus=bus,
        )
        assert asset.asset_id == "asset_42"

        step = PlanStep(step_id="s1", index=0, tool_name="auto_rig", description="Rig character")
        plan = await emit_plan_proposal(plan_id="p99", steps=[step], bus=bus)
        assert plan.plan_id == "p99"

    run_async(_test())


def test_sync_emission_helpers() -> None:
    bus = TelemetryBus()

    prog = emit_progress_sync(stage="render", percentage=-10.0, message="Starting", bus=bus)
    assert prog.percentage == 0.0

    log = emit_log_sync(message="Render started", level=LogLevel.INFO, bus=bus)
    assert log.message == "Render started"

    asset = emit_asset_ready_sync(
        asset_id="vid_1",
        asset_type=AssetType.RENDER_VIDEO,
        file_path="render.mp4",
        bus=bus,
    )
    assert asset.file_path == "render.mp4"


def test_fastmcp_telemetry_bridge() -> None:
    async def _test() -> None:
        bus = TelemetryBus()

        class MockFastMCPContext:
            def __init__(self) -> None:
                self.progress_calls: List[float] = []
                self.info_calls: List[str] = []

            async def report_progress(self, progress: float, total: float, message: str) -> None:
                self.progress_calls.append(progress)

            async def info(self, msg: str) -> None:
                self.info_calls.append(msg)

            async def warning(self, msg: str) -> None:
                pass

            async def error(self, msg: str) -> None:
                pass

        mock_ctx = MockFastMCPContext()
        bridge = FastMCPTelemetryBridge(ctx=mock_ctx, bus=bus)  # type: ignore[arg-type]

        ev = await bridge.report_progress(
            stage="stem_separation",
            percentage=50.0,
            message="Separating drums",
        )
        assert ev.percentage == 50.0
        assert len(mock_ctx.progress_calls) == 1
        assert mock_ctx.progress_calls[0] == 0.5  # Normalized 0.0 - 1.0

        await bridge.info("Demucs completed")
        assert len(mock_ctx.info_calls) == 1

    run_async(_test())


def test_sse_stream() -> None:
    async def _test() -> None:
        bus = TelemetryBus()

        async def emit_later() -> None:
            await asyncio.sleep(0.05)
            await bus.emit(ProgressEvent(stage="sse_test", percentage=10.0, message="Streaming"))

        task = asyncio.create_task(emit_later())

        stream = telemetry_sse_stream(bus=bus, replay_history=False, heartbeat_seconds=1.0)
        chunk = await anext(stream)

        assert "event: progress" in chunk
        assert "data: " in chunk
        assert "sse_test" in chunk

        await task

    run_async(_test())


def test_backpressure_slow_subscriber() -> None:
    async def _test() -> None:
        bus = TelemetryBus(max_queue_size=2)

        async with bus._subscribe_context_manager(replay_history=False, max_queue_size=2) as queue:
            # Emit 4 events into a queue of size 2
            for i in range(4):
                await bus.emit(ProgressEvent(stage="fast", percentage=float(i), message=f"Step {i}"))

            assert queue.qsize() == 2
            ev1 = await queue.get()
            ev2 = await queue.get()
            # Older items (0, 1) should have been dropped; only fresh items (2, 3) remain
            assert ev1.percentage == 2.0
            assert ev2.percentage == 3.0

    run_async(_test())
