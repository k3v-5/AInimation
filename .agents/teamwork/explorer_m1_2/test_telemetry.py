"""
Unit Tests for proposed_telemetry.py in explorer_m1_2.
Verifies event bus, Pydantic v2 schemas, FastMCP bridge, thread safety, and WebSocket/SSE.
"""

import asyncio
import json
import threading
import time
from typing import List, Optional

import pytest
from starlette.applications import Starlette
from starlette.routing import Route, WebSocketRoute
from starlette.testclient import TestClient

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from proposed_telemetry import (
    AssetReadyEvent,
    AssetType,
    FastMCPTelemetryBridge,
    LogEvent,
    LogLevel,
    PlanProposalEvent,
    PlanStatus,
    PlanStepPayload,
    ProgressEvent,
    TelemetryBus,
    TelemetryEvent,
    TelemetryEventAdapter,
    create_telemetry_sse_response,
    emit_asset_ready,
    emit_asset_ready_sync,
    emit_log,
    emit_log_sync,
    emit_plan_proposal,
    emit_progress,
    emit_progress_sync,
    get_telemetry_bus,
    handle_telemetry_websocket,
    report_fastmcp_progress,
    reset_telemetry_bus,
    telemetry_sse_stream,
)


@pytest.fixture(autouse=True)
def cleanup_bus():
    reset_telemetry_bus()
    yield
    reset_telemetry_bus()


# -----------------------------------------------------------------------------
# 1. Pydantic v2 Event Model Tests
# -----------------------------------------------------------------------------

def test_progress_event_validation():
    ev = ProgressEvent(
        stage="audio_analysis",
        percentage=45.5,
        message="Extracting tempo and beat frames",
        plan_id="plan-123",
        step_id=1,
        tool_name="analyze_audio",
    )
    dumped = ev.model_dump_json()
    loaded = TelemetryEventAdapter.validate_json(dumped)
    assert isinstance(loaded, ProgressEvent)
    assert loaded.type == "progress"
    assert loaded.percentage == 45.5
    assert loaded.tool_name == "analyze_audio"


def test_progress_event_boundaries():
    with pytest.raises(Exception):
        # Percentage must be <= 100.0
        ProgressEvent(stage="audio", percentage=105.0, message="Out of bounds")

    with pytest.raises(Exception):
        # Percentage must be >= 0.0
        ProgressEvent(stage="audio", percentage=-1.0, message="Negative")


def test_plan_proposal_event_validation():
    step = PlanStepPayload(
        step_id="step-1",
        index=0,
        tool_name="image_to_3d",
        title="Synthesize 3D Mesh",
        parameters={"provider": "fal_trellis", "texture_res": 1024},
        requires_confirmation=True,
        status=PlanStatus.PROPOSED,
    )
    ev = PlanProposalEvent(
        plan_id="plan-999",
        steps=[step],
        status=PlanStatus.PROPOSED,
    )
    dumped = ev.model_dump_json()
    loaded = TelemetryEventAdapter.validate_json(dumped)
    assert isinstance(loaded, PlanProposalEvent)
    assert loaded.type == "plan_proposal"
    assert len(loaded.steps) == 1
    assert loaded.steps[0].tool_name == "image_to_3d"


def test_asset_ready_event_validation():
    ev = AssetReadyEvent(
        asset_id="asset-777",
        asset_type=AssetType.MESH_3D,
        file_path="/cache/models/character.glb",
        metadata={"vertices": "42100", "cas_hash": "abc123sha"},
    )
    dumped = ev.model_dump_json()
    loaded = TelemetryEventAdapter.validate_json(dumped)
    assert isinstance(loaded, AssetReadyEvent)
    assert loaded.type == "asset_ready"
    assert loaded.asset_type == AssetType.MESH_3D
    assert loaded.file_path == "/cache/models/character.glb"


def test_log_event_validation():
    ev = LogEvent(
        level=LogLevel.WARNING,
        message="Low confidence in onset detection, using fallback",
        source="LibrosaAdapter",
    )
    dumped = ev.model_dump_json()
    loaded = TelemetryEventAdapter.validate_json(dumped)
    assert isinstance(loaded, LogEvent)
    assert loaded.type == "log"
    assert loaded.level == LogLevel.WARNING
    assert loaded.source == "LibrosaAdapter"


# -----------------------------------------------------------------------------
# 2. TelemetryBus Broadcast & Async Subscriber Tests
# -----------------------------------------------------------------------------

@pytest.mark.anyio
async def test_telemetry_bus_broadcast_multiple_subscribers():
    bus = TelemetryBus()
    loop = asyncio.get_running_loop()
    bus.set_event_loop(loop)

    received_1: List[TelemetryEvent] = []
    received_2: List[TelemetryEvent] = []

    async with bus.subscribe(replay_history=False) as q1, bus.subscribe(replay_history=False) as q2:
        assert bus.subscriber_count == 2

        ev1 = ProgressEvent(stage="stage1", percentage=10.0, message="Init")
        ev2 = LogEvent(level=LogLevel.INFO, message="Ready")

        await bus.emit(ev1)
        await bus.emit(ev2)

        received_1.append(await q1.get())
        received_1.append(await q1.get())
        received_2.append(await q2.get())
        received_2.append(await q2.get())

    # Subscribers should be automatically removed upon exiting context manager
    assert bus.subscriber_count == 0

    assert len(received_1) == 2
    assert len(received_2) == 2
    assert received_1[0].type == "progress"
    assert received_1[1].type == "log"
    assert received_2[0].type == "progress"


@pytest.mark.anyio
async def test_telemetry_bus_history_and_replay():
    bus = TelemetryBus(history_size=5)
    ev1 = ProgressEvent(stage="stage1", percentage=20.0, message="First")
    ev2 = ProgressEvent(stage="stage2", percentage=40.0, message="Second")

    await bus.emit(ev1)
    await bus.emit(ev2)

    assert len(bus.get_history()) == 2
    assert bus.get_latest_progress() == ev2

    # New subscriber joining with replay_history=True should get historical events
    async with bus.subscribe(replay_history=True) as q:
        r1 = await q.get()
        r2 = await q.get()
        assert r1.message == "First"
        assert r2.message == "Second"


@pytest.mark.anyio
async def test_telemetry_bus_backpressure_slow_subscriber():
    # Max queue size of 2 for slow consumer
    bus = TelemetryBus(max_queue_size=2)

    async with bus.subscribe(replay_history=False, max_queue_size=2) as q:
        # Emit 3 events; the oldest should be dropped so the queue does not block or error
        await bus.emit(ProgressEvent(stage="s", percentage=10.0, message="Ev1"))
        await bus.emit(ProgressEvent(stage="s", percentage=20.0, message="Ev2"))
        await bus.emit(ProgressEvent(stage="s", percentage=30.0, message="Ev3"))

        assert q.qsize() == 2
        item1 = await q.get()
        item2 = await q.get()
        # Item 1 was dropped, so queue holds Ev2 and Ev3
        assert item1.message == "Ev2"
        assert item2.message == "Ev3"


# -----------------------------------------------------------------------------
# 3. Thread-Safe Emission Tests
# -----------------------------------------------------------------------------

@pytest.mark.anyio
async def test_telemetry_bus_threadsafe_emission():
    bus = TelemetryBus()
    loop = asyncio.get_running_loop()
    bus.set_event_loop(loop)

    async with bus.subscribe(replay_history=False) as q:
        def worker_thread():
            time.sleep(0.02)
            emit_progress_sync(
                stage="audio_demucs",
                percentage=80.0,
                message="Separated drums stem in worker thread",
                bus=bus,
            )
            emit_log_sync(
                message="Worker thread completed",
                level=LogLevel.INFO,
                bus=bus,
            )

        thread = threading.Thread(target=worker_thread)
        thread.start()
        thread.join()

        ev1 = await asyncio.wait_for(q.get(), timeout=2.0)
        ev2 = await asyncio.wait_for(q.get(), timeout=2.0)

        assert isinstance(ev1, ProgressEvent)
        assert ev1.percentage == 80.0
        assert isinstance(ev2, LogEvent)
        assert ev2.message == "Worker thread completed"


# -----------------------------------------------------------------------------
# 4. FastMCP Dual-Invocation Integration Tests
# -----------------------------------------------------------------------------

class MockFastMCPContext:
    def __init__(self):
        self.reported_progress: List[tuple[float, Optional[float], Optional[str]]] = []
        self.logs: List[tuple[str, str]] = []

    async def report_progress(self, progress: float, total: Optional[float] = None, message: Optional[str] = None):
        self.reported_progress.append((progress, total, message))

    async def info(self, msg: str):
        self.logs.append(("info", msg))

    async def warning(self, msg: str):
        self.logs.append(("warning", msg))

    async def error(self, msg: str):
        self.logs.append(("error", msg))


@pytest.mark.anyio
async def test_report_fastmcp_progress_with_context():
    bus = TelemetryBus()
    mock_ctx = MockFastMCPContext()

    async with bus.subscribe(replay_history=False) as q:
        ev = await report_fastmcp_progress(
            ctx=mock_ctx,  # type: ignore[arg-type]
            stage="rigging",
            percentage=75.0,
            message="Auto-rigging bipedal mannequin",
            bus=bus,
        )

        assert ev.percentage == 75.0
        bus_ev = await q.get()
        assert bus_ev.percentage == 75.0

        # Verify Mock context received progress normalized to 0.75
        assert len(mock_ctx.reported_progress) == 1
        assert mock_ctx.reported_progress[0] == (0.75, 1.0, "Auto-rigging bipedal mannequin")


@pytest.mark.anyio
async def test_report_fastmcp_progress_without_context_direct_python():
    bus = TelemetryBus()

    async with bus.subscribe(replay_history=False) as q:
        # ctx is None (direct programmatic invocation)
        ev = await report_fastmcp_progress(
            ctx=None,
            stage="direct_call",
            percentage=100.0,
            message="Direct invocation complete",
            bus=bus,
        )

        assert ev.percentage == 100.0
        bus_ev = await q.get()
        assert bus_ev.message == "Direct invocation complete"


@pytest.mark.anyio
async def test_fastmcp_telemetry_bridge():
    bus = TelemetryBus()
    mock_ctx = MockFastMCPContext()
    bridge = FastMCPTelemetryBridge(ctx=mock_ctx, bus=bus)  # type: ignore[arg-type]

    async with bus.subscribe(replay_history=False) as q:
        await bridge.report_progress(stage="mocap", percentage=50.0, message="Extracting pose keyframes")
        await bridge.info("Model loaded")

        ev_prog = await q.get()
        ev_log = await q.get()

        assert ev_prog.type == "progress"
        assert ev_log.type == "log"
        assert len(mock_ctx.reported_progress) == 1
        assert len(mock_ctx.logs) == 1


# -----------------------------------------------------------------------------
# 5. Starlette WebSocket Telemetry Endpoint Tests
# -----------------------------------------------------------------------------

def test_websocket_telemetry_endpoint():
    bus = TelemetryBus()

    async def ws_endpoint(websocket):
        await handle_telemetry_websocket(websocket, bus=bus, replay_history=False)

    app = Starlette(routes=[WebSocketRoute("/ws/telemetry", ws_endpoint)])
    client = TestClient(app)

    with client.websocket_connect("/ws/telemetry") as ws:
        # Emit an event on the bus
        asyncio.run(
            bus.emit(
                ProgressEvent(
                    stage="render_mrq",
                    percentage=92.5,
                    message="Frame 120 of 130 rendered",
                )
            )
        )
        msg_text = ws.receive_text()
        data = json.loads(msg_text)
        assert data["type"] == "progress"
        assert data["stage"] == "render_mrq"
        assert data["percentage"] == 92.5
        assert data["message"] == "Frame 120 of 130 rendered"


# -----------------------------------------------------------------------------
# 6. Starlette SSE Streaming Format Tests
# -----------------------------------------------------------------------------

@pytest.mark.anyio
async def test_sse_stream_format():
    bus = TelemetryBus()

    # Trigger an event into bus history
    await bus.emit(
        LogEvent(
            level=LogLevel.INFO,
            message="System initialized",
            source="MainApp",
        )
    )

    # Stream with replay_history=True
    stream = telemetry_sse_stream(bus=bus, replay_history=True, heartbeat_seconds=0.05)

    # First chunk from generator should be the replayed event
    chunk = await anext(stream)
    assert chunk.startswith("event: log\n")
    assert "System initialized" in chunk
    assert chunk.endswith("\n\n")

    # Second chunk should be a keep-alive ping when timeout fires
    ping_chunk = await anext(stream)
    assert ping_chunk == ": keep-alive\n\n"
