"""
Telemetry Event Bus, Data Contracts, and Streaming Emitters for IANIMATION.

This module provides the central asynchronous telemetry infrastructure for:
1. Pydantic v2 typed event contracts (ProgressEvent, PlanProposalEvent, AssetReadyEvent, LogEvent).
2. Broadcast subscriber event bus (`TelemetryBus`) backed by `asyncio.Queue`.
3. FastMCP `Context.report_progress` dual-invocation adapter.
4. Starlette / FastAPI Server-Sent Events (SSE) and WebSocket emitters.
5. Thread-safe emission helpers for synchronous AI workers and UE5 thread pools.

Adheres strictly to the Zero-Any Policy (100% strict typing) and SOLID design principles.
"""

from __future__ import annotations

import asyncio
from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from enum import StrEnum
import logging
from typing import (
    Annotated,
    AsyncIterator,
    Deque,
    Dict,
    Final,
    List,
    Literal,
    Optional,
    Set,
    Union,
)

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

# Import FastMCP Context conditionally or directly
try:
    from mcp.server.fastmcp import Context as FastMCPContext
except ImportError:
    FastMCPContext = None  # type: ignore[assignment, misc]

# Import Starlette / FastAPI primitives conditionally or directly
try:
    from starlette.responses import StreamingResponse
    from starlette.websockets import WebSocket, WebSocketDisconnect
except ImportError:
    StreamingResponse = None  # type: ignore[assignment, misc]
    WebSocket = None  # type: ignore[assignment, misc]
    WebSocketDisconnect = Exception  # type: ignore[assignment, misc]

logger = logging.getLogger("ianimation.telemetry")


# -----------------------------------------------------------------------------
# Base Configuration & Enums (Zero-Any Policy)
# -----------------------------------------------------------------------------

class StrictTelemetryModel(BaseModel):
    """Base model enforcing strict typing, immutability, and forbidding unmapped fields."""
    model_config = ConfigDict(
        strict=False,
        frozen=True,
        validate_assignment=True,
        populate_by_name=True,
        extra="forbid",
        arbitrary_types_allowed=False,
    )


class AssetType(StrEnum):
    """Classification of generated intermediate or final pipeline assets."""
    AUDIO_STEMS = "audio_stems"
    MESH_3D = "mesh_3d"
    RIGGED_MESH = "rigged_mesh"
    MOCAP = "mocap"
    RENDER_VIDEO = "render_video"


class LogLevel(StrEnum):
    """Log level severity classification."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class PlanStatus(StrEnum):
    """Lifecycle status of a production plan or step."""
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


PlanParamPrimitive = Union[str, int, float, bool, None]
PlanParamValue = Union[PlanParamPrimitive, List[str], Dict[str, str]]


# -----------------------------------------------------------------------------
# 1. Typed Event Models (Conforming to Frontend TelemetryEventSchema)
# -----------------------------------------------------------------------------

class PlanStepPayload(StrictTelemetryModel):
    """Lightweight immutable representation of a production step in a plan proposal."""
    step_id: Union[str, int] = Field(
        ...,
        description="Unique step identifier (UUID string or sequential integer index)",
    )
    index: int = Field(
        default=0,
        ge=0,
        description="Ordinal execution index in the production sequence",
    )
    tool_name: str = Field(
        ...,
        min_length=1,
        description="Target FastMCP atomic tool name",
    )
    title: Optional[str] = Field(
        default=None,
        description="Short human-readable title for the step",
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of what this step produces",
    )
    parameters: Dict[str, PlanParamValue] = Field(
        default_factory=dict,
        description="Strictly typed parameters for the tool",
    )
    requires_confirmation: bool = Field(
        default=False,
        description="Whether this step requires explicit human approval before execution",
    )
    status: PlanStatus = Field(
        default=PlanStatus.PROPOSED,
        description="Current status of the step",
    )
    output_preview: Optional[str] = Field(
        default=None,
        description="Path or URL to intermediate asset produced by this step for UI preview",
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Failure reason if the step encountered an error",
    )


class ProgressEvent(StrictTelemetryModel):
    """
    Event emitted to report percentage progress and status of ongoing background tasks.
    Conforms to frontend TelemetryEventSchema: type='progress'.
    """
    type: Literal["progress"] = "progress"
    stage: str = Field(
        ...,
        min_length=1,
        description="Execution stage identifier (e.g. 'audio_analysis', 'image_to_3d')",
    )
    percentage: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Completion percentage (0.0 to 100.0)",
    )
    message: str = Field(
        ...,
        description="Human-readable progress description for the UI",
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp",
    )
    plan_id: Optional[str] = Field(
        default=None,
        description="Optional plan ID associated with this operation",
    )
    step_id: Optional[Union[str, int]] = Field(
        default=None,
        description="Optional step index or ID associated with this operation",
    )
    tool_name: Optional[str] = Field(
        default=None,
        description="Optional name of the tool emitting progress",
    )


class PlanProposalEvent(StrictTelemetryModel):
    """
    Event emitted when a new production plan has been formulated by Copilot.
    Conforms to frontend TelemetryEventSchema: type='plan_proposal'.
    """
    type: Literal["plan_proposal"] = "plan_proposal"
    plan_id: str = Field(
        ...,
        min_length=1,
        description="Unique production plan identifier",
    )
    steps: List[PlanStepPayload] = Field(
        default_factory=list,
        description="List of proposed production steps",
    )
    status: PlanStatus = Field(
        default=PlanStatus.PROPOSED,
        description="Current status of the proposed plan",
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp",
    )


class AssetReadyEvent(StrictTelemetryModel):
    """
    Event emitted when a pipeline asset is finalized and ready for consumption.
    Conforms to frontend TelemetryEventSchema: type='asset_ready'.
    """
    type: Literal["asset_ready"] = "asset_ready"
    asset_id: str = Field(
        ...,
        min_length=1,
        description="Unique asset identifier",
    )
    asset_type: AssetType = Field(
        ...,
        description="Asset type classification",
    )
    file_path: str = Field(
        ...,
        min_length=1,
        description="Absolute file path to the completed asset",
    )
    metadata: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional key-value metadata tags",
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp",
    )


class LogEvent(StrictTelemetryModel):
    """
    Event emitted for structured real-time logging streamed to the UI console.
    Conforms to frontend TelemetryEventSchema: type='log'.
    """
    type: Literal["log"] = "log"
    level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Log severity level",
    )
    message: str = Field(
        ...,
        description="Log message text",
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp",
    )
    source: Optional[str] = Field(
        default=None,
        description="Originating subsystem (e.g. 'FastMCP', 'UE5Bridge', 'Librosa')",
    )


TelemetryEvent = Annotated[
    Union[ProgressEvent, PlanProposalEvent, AssetReadyEvent, LogEvent],
    Field(discriminator="type"),
]

TelemetryEventAdapter: Final[TypeAdapter[TelemetryEvent]] = TypeAdapter(TelemetryEvent)


# -----------------------------------------------------------------------------
# 2. TelemetryBus (Asynchronous Broadcast & Replay Queue)
# -----------------------------------------------------------------------------

class TelemetryBus:
    """
    Central Asynchronous Telemetry Bus.

    Provides pub-sub event distribution using `asyncio.Queue` subscribers,
    lossy backpressure handling for slow consumers, in-memory replay buffer,
    and thread-safe scheduling bridges for synchronous execution contexts.
    """

    def __init__(
        self,
        max_queue_size: int = 1000,
        history_size: int = 100,
    ) -> None:
        self._max_queue_size: int = max_queue_size
        self._history_size: int = history_size
        self._subscribers: Set[asyncio.Queue[TelemetryEvent]] = set()
        self._history: Deque[TelemetryEvent] = deque(maxlen=history_size)
        self._latest_progress: Optional[ProgressEvent] = None
        self._latest_plan: Optional[PlanProposalEvent] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._lock: asyncio.Lock = asyncio.Lock()

    def set_event_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Register the primary asyncio event loop for thread-safe cross-thread scheduling."""
        self._loop = loop

    def get_event_loop(self) -> Optional[asyncio.AbstractEventLoop]:
        """Return the registered event loop, or auto-detect if running."""
        if self._loop is not None and not self._loop.is_closed():
            return self._loop
        try:
            loop = asyncio.get_running_loop()
            self._loop = loop
            return loop
        except RuntimeError:
            return None

    @property
    def subscriber_count(self) -> int:
        """Return the number of active subscribers."""
        return len(self._subscribers)

    def add_subscriber(self, queue: asyncio.Queue[TelemetryEvent]) -> None:
        """Register an active subscriber queue."""
        self._subscribers.add(queue)

    def remove_subscriber(self, queue: asyncio.Queue[TelemetryEvent]) -> None:
        """Unregister a subscriber queue."""
        self._subscribers.discard(queue)

    @asynccontextmanager
    async def subscribe(
        self,
        replay_history: bool = True,
        max_queue_size: Optional[int] = None,
    ) -> AsyncIterator[asyncio.Queue[TelemetryEvent]]:
        """
        Async context manager yielding a subscriber queue.
        Automatically handles registration and deregistration on exit.
        """
        queue_size = max_queue_size if max_queue_size is not None else self._max_queue_size
        queue: asyncio.Queue[TelemetryEvent] = asyncio.Queue(maxsize=queue_size)

        # Pre-seed with replay history if requested
        if replay_history:
            for past_event in list(self._history):
                try:
                    queue.put_nowait(past_event)
                except asyncio.QueueFull:
                    break

        self.add_subscriber(queue)
        try:
            yield queue
        finally:
            self.remove_subscriber(queue)

    async def listen(
        self,
        replay_history: bool = True,
        max_queue_size: Optional[int] = None,
    ) -> AsyncIterator[TelemetryEvent]:
        """Async generator yielding events as they arrive on the bus."""
        async with self.subscribe(replay_history=replay_history, max_queue_size=max_queue_size) as queue:
            while True:
                event = await queue.get()
                try:
                    yield event
                finally:
                    queue.task_done()

    async def emit(self, event: TelemetryEvent) -> None:
        """
        Broadcast an event asynchronously to all active subscribers.
        Applies lossy backpressure if a subscriber queue is full (drops oldest).
        """
        # Ensure event loop registration
        if self._loop is None:
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                pass

        # Update in-memory history and latest caches
        self._history.append(event)
        if isinstance(event, ProgressEvent):
            self._latest_progress = event
        elif isinstance(event, PlanProposalEvent):
            self._latest_plan = event

        # Distribute to all subscribers
        subscribers = list(self._subscribers)
        for queue in subscribers:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                # Subscriber is slow; drop the oldest item to prioritize fresh telemetry
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
                try:
                    queue.put_nowait(event)
                except asyncio.QueueFull:
                    logger.warning("Subscriber queue is persistently saturated; dropping event.")

    def emit_threadsafe(self, event: TelemetryEvent) -> None:
        """
        Thread-safe emission helper for synchronous background worker threads.
        Schedules `emit` on the registered asyncio event loop.
        """
        loop = self.get_event_loop()
        if loop is None or not loop.is_running():
            # If no running event loop is registered, buffer into history and log warning
            self._history.append(event)
            if isinstance(event, ProgressEvent):
                self._latest_progress = event
            elif isinstance(event, PlanProposalEvent):
                self._latest_plan = event
            logger.warning(
                "TelemetryBus.emit_threadsafe called without an active running event loop; buffered to history."
            )
            return

        asyncio.run_coroutine_threadsafe(self.emit(event), loop)

    def get_history(self) -> List[TelemetryEvent]:
        """Return a snapshot of recent telemetry events."""
        return list(self._history)

    def get_latest_progress(self) -> Optional[ProgressEvent]:
        """Return the most recent ProgressEvent, if any."""
        return self._latest_progress

    def get_latest_plan(self) -> Optional[PlanProposalEvent]:
        """Return the most recent PlanProposalEvent, if any."""
        return self._latest_plan

    def clear_history(self) -> None:
        """Clear all retained history and cached events."""
        self._history.clear()
        self._latest_progress = None
        self._latest_plan = None

    async def wait_for_subscribers(self, count: int = 1, timeout_seconds: float = 5.0) -> bool:
        """
        Helper for testing and synchronization: await until at least `count` subscribers connect.
        Returns True if condition met, False if timed out.
        """
        start_time = asyncio.get_running_loop().time()
        while len(self._subscribers) < count:
            if asyncio.get_running_loop().time() - start_time > timeout_seconds:
                return False
            await asyncio.sleep(0.01)
        return True


# -----------------------------------------------------------------------------
# 3. Global Singleton & Service Management
# -----------------------------------------------------------------------------

_GLOBAL_TELEMETRY_BUS: Optional[TelemetryBus] = None


def get_telemetry_bus() -> TelemetryBus:
    """Retrieve or create the global TelemetryBus singleton instance."""
    global _GLOBAL_TELEMETRY_BUS
    if _GLOBAL_TELEMETRY_BUS is None:
        _GLOBAL_TELEMETRY_BUS = TelemetryBus()
    return _GLOBAL_TELEMETRY_BUS


def reset_telemetry_bus() -> None:
    """Reset the global TelemetryBus singleton (primarily for test teardown)."""
    global _GLOBAL_TELEMETRY_BUS
    _GLOBAL_TELEMETRY_BUS = None


# -----------------------------------------------------------------------------
# 4. Asynchronous & Synchronous Emission Helpers
# -----------------------------------------------------------------------------

async def emit_progress(
    stage: str,
    percentage: float,
    message: str,
    plan_id: Optional[str] = None,
    step_id: Optional[Union[str, int]] = None,
    tool_name: Optional[str] = None,
    bus: Optional[TelemetryBus] = None,
) -> ProgressEvent:
    """Construct and emit a ProgressEvent asynchronously."""
    target_bus = bus if bus is not None else get_telemetry_bus()
    clamped_percentage = max(0.0, min(100.0, float(percentage)))
    event = ProgressEvent(
        stage=stage,
        percentage=clamped_percentage,
        message=message,
        plan_id=plan_id,
        step_id=step_id,
        tool_name=tool_name,
    )
    await target_bus.emit(event)
    return event


def emit_progress_sync(
    stage: str,
    percentage: float,
    message: str,
    plan_id: Optional[str] = None,
    step_id: Optional[Union[str, int]] = None,
    tool_name: Optional[str] = None,
    bus: Optional[TelemetryBus] = None,
) -> ProgressEvent:
    """Construct and emit a ProgressEvent thread-safely from a synchronous thread."""
    target_bus = bus if bus is not None else get_telemetry_bus()
    clamped_percentage = max(0.0, min(100.0, float(percentage)))
    event = ProgressEvent(
        stage=stage,
        percentage=clamped_percentage,
        message=message,
        plan_id=plan_id,
        step_id=step_id,
        tool_name=tool_name,
    )
    target_bus.emit_threadsafe(event)
    return event


async def emit_log(
    message: str,
    level: LogLevel = LogLevel.INFO,
    source: Optional[str] = None,
    bus: Optional[TelemetryBus] = None,
) -> LogEvent:
    """Construct and emit a LogEvent asynchronously."""
    target_bus = bus if bus is not None else get_telemetry_bus()
    event = LogEvent(message=message, level=level, source=source)
    await target_bus.emit(event)
    return event


def emit_log_sync(
    message: str,
    level: LogLevel = LogLevel.INFO,
    source: Optional[str] = None,
    bus: Optional[TelemetryBus] = None,
) -> LogEvent:
    """Construct and emit a LogEvent thread-safely from a synchronous thread."""
    target_bus = bus if bus is not None else get_telemetry_bus()
    event = LogEvent(message=message, level=level, source=source)
    target_bus.emit_threadsafe(event)
    return event


async def emit_asset_ready(
    asset_id: str,
    asset_type: AssetType,
    file_path: str,
    metadata: Optional[Dict[str, str]] = None,
    bus: Optional[TelemetryBus] = None,
) -> AssetReadyEvent:
    """Construct and emit an AssetReadyEvent asynchronously."""
    target_bus = bus if bus is not None else get_telemetry_bus()
    event = AssetReadyEvent(
        asset_id=asset_id,
        asset_type=asset_type,
        file_path=file_path,
        metadata=metadata,
    )
    await target_bus.emit(event)
    return event


def emit_asset_ready_sync(
    asset_id: str,
    asset_type: AssetType,
    file_path: str,
    metadata: Optional[Dict[str, str]] = None,
    bus: Optional[TelemetryBus] = None,
) -> AssetReadyEvent:
    """Construct and emit an AssetReadyEvent thread-safely from a synchronous thread."""
    target_bus = bus if bus is not None else get_telemetry_bus()
    event = AssetReadyEvent(
        asset_id=asset_id,
        asset_type=asset_type,
        file_path=file_path,
        metadata=metadata,
    )
    target_bus.emit_threadsafe(event)
    return event


async def emit_plan_proposal(
    plan_id: str,
    steps: List[PlanStepPayload],
    status: PlanStatus = PlanStatus.PROPOSED,
    bus: Optional[TelemetryBus] = None,
) -> PlanProposalEvent:
    """Construct and emit a PlanProposalEvent asynchronously."""
    target_bus = bus if bus is not None else get_telemetry_bus()
    event = PlanProposalEvent(plan_id=plan_id, steps=steps, status=status)
    await target_bus.emit(event)
    return event


# -----------------------------------------------------------------------------
# 5. FastMCP Dual-Invocation Integration Adapter
# -----------------------------------------------------------------------------

class FastMCPTelemetryBridge:
    """
    Bridge connecting FastMCP tools to both the local TelemetryBus
    and the native FastMCP `Context.report_progress` channel.
    """

    def __init__(
        self,
        ctx: Optional[FastMCPContext] = None,
        bus: Optional[TelemetryBus] = None,
    ) -> None:
        self.ctx: Optional[FastMCPContext] = ctx
        self.bus: TelemetryBus = bus if bus is not None else get_telemetry_bus()

    async def report_progress(
        self,
        stage: str,
        percentage: float,
        message: str,
        plan_id: Optional[str] = None,
        step_id: Optional[Union[str, int]] = None,
        tool_name: Optional[str] = None,
    ) -> ProgressEvent:
        """Report progress simultaneously to TelemetryBus and FastMCP Context."""
        return await report_fastmcp_progress(
            ctx=self.ctx,
            stage=stage,
            percentage=percentage,
            message=message,
            plan_id=plan_id,
            step_id=step_id,
            tool_name=tool_name,
            bus=self.bus,
        )

    async def info(self, message: str, source: Optional[str] = "FastMCP") -> LogEvent:
        """Log info to TelemetryBus and ctx.info if context is active."""
        if self.ctx is not None:
            try:
                await self.ctx.info(message)
            except Exception:
                pass
        return await emit_log(message=message, level=LogLevel.INFO, source=source, bus=self.bus)

    async def warning(self, message: str, source: Optional[str] = "FastMCP") -> LogEvent:
        """Log warning to TelemetryBus and ctx.warning if context is active."""
        if self.ctx is not None:
            try:
                await self.ctx.warning(message)
            except Exception:
                pass
        return await emit_log(message=message, level=LogLevel.WARNING, source=source, bus=self.bus)

    async def error(self, message: str, source: Optional[str] = "FastMCP") -> LogEvent:
        """Log error to TelemetryBus and ctx.error if context is active."""
        if self.ctx is not None:
            try:
                await self.ctx.error(message)
            except Exception:
                pass
        return await emit_log(message=message, level=LogLevel.ERROR, source=source, bus=self.bus)


async def report_fastmcp_progress(
    ctx: Optional[FastMCPContext],
    stage: str,
    percentage: float,
    message: str,
    plan_id: Optional[str] = None,
    step_id: Optional[Union[str, int]] = None,
    tool_name: Optional[str] = None,
    bus: Optional[TelemetryBus] = None,
) -> ProgressEvent:
    """
    Unified dual-invocation progress reporter.

    If `ctx` is supplied (invoked via FastMCP client), invokes `ctx.report_progress`.
    In all cases (including direct Python programmatic calls where `ctx` is None),
    emits `ProgressEvent` to the local `TelemetryBus` so the frontend UI receives updates.
    """
    event = await emit_progress(
        stage=stage,
        percentage=percentage,
        message=message,
        plan_id=plan_id,
        step_id=step_id,
        tool_name=tool_name,
        bus=bus,
    )

    if ctx is not None:
        try:
            # FastMCP expects progress as a float from 0.0 to 1.0 (or total specified)
            progress_fraction = max(0.0, min(1.0, float(percentage) / 100.0))
            await ctx.report_progress(progress=progress_fraction, total=1.0, message=message)
        except Exception as exc:
            # Context progress reporting is best-effort and must not abort tool execution
            logger.debug("FastMCP ctx.report_progress skipped or failed: %s", exc)

    return event


# -----------------------------------------------------------------------------
# 6. Starlette / FastAPI SSE & WebSocket Emitters
# -----------------------------------------------------------------------------

async def telemetry_sse_stream(
    bus: Optional[TelemetryBus] = None,
    replay_history: bool = True,
    heartbeat_seconds: float = 15.0,
) -> AsyncIterator[str]:
    """
    Async generator yielding formatted Server-Sent Events (SSE).

    Format:
    event: {type}
    data: {json_payload}

    Also yields periodic comments (: keep-alive) to prevent connection timeouts.
    """
    target_bus = bus if bus is not None else get_telemetry_bus()

    async with target_bus.subscribe(replay_history=replay_history) as queue:
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=heartbeat_seconds)
                yield f"event: {event.type}\ndata: {event.model_dump_json()}\n\n"
                queue.task_done()
            except asyncio.TimeoutError:
                # Keep-alive comment
                yield ": keep-alive\n\n"
            except asyncio.CancelledError:
                # Client disconnected
                break


def create_telemetry_sse_response(
    bus: Optional[TelemetryBus] = None,
    replay_history: bool = True,
    heartbeat_seconds: float = 15.0,
) -> StreamingResponse:
    """
    Create a Starlette StreamingResponse delivering the SSE telemetry stream.
    Sets standard HTTP SSE headers preventing proxy caching or buffering.
    """
    if StreamingResponse is None:
        raise RuntimeError("Starlette is required to create an SSE StreamingResponse.")

    headers: Dict[str, str] = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "text/event-stream",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(
        telemetry_sse_stream(
            bus=bus,
            replay_history=replay_history,
            heartbeat_seconds=heartbeat_seconds,
        ),
        media_type="text/event-stream",
        headers=headers,
    )


async def handle_telemetry_websocket(
    websocket: WebSocket,
    bus: Optional[TelemetryBus] = None,
    replay_history: bool = True,
) -> None:
    """
    Handle a persistent Starlette/FastAPI WebSocket telemetry connection.

    Accepts the connection, subscribes to TelemetryBus, forwards all serialized events,
    and cleanly detaches the subscriber upon disconnection or error.
    """
    if WebSocket is None:
        raise RuntimeError("Starlette is required to handle WebSocket connections.")

    target_bus = bus if bus is not None else get_telemetry_bus()
    await websocket.accept()

    async with target_bus.subscribe(replay_history=replay_history) as queue:
        try:
            while True:
                event = await queue.get()
                try:
                    await websocket.send_text(event.model_dump_json())
                finally:
                    queue.task_done()
        except WebSocketDisconnect:
            logger.info("WebSocket telemetry client disconnected normally.")
        except Exception as exc:
            logger.debug("WebSocket connection terminated: %s", exc)
