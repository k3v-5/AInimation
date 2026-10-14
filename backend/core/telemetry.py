"""
Telemetry Event Bus, Data Contracts, and Streaming Emitters for IANIMATION.

This module provides the central asynchronous telemetry infrastructure for:
1. Pydantic v2 typed event contracts (ProgressEvent, PlanProposalEvent, AssetReadyEvent, LogEvent).
2. Broadcast subscriber event bus (`TelemetryBus`) backed by `asyncio.Queue` and synchronous callbacks.
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
import inspect
import logging
from typing import (
    AsyncContextManager,
    AsyncIterator,
    Awaitable,
    Callable,
    Coroutine,
    Deque,
    Dict,
    List,
    Optional,
    Set,
    Union,
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

# Import FastMCP Context conditionally or directly
try:
    from mcp.server.fastmcp import Context as FastMCPContext
except ImportError:
    FastMCPContext = None  # type: ignore[assignment, misc]

# Import Starlette primitives conditionally or directly
try:
    from starlette.responses import StreamingResponse
    from starlette.websockets import WebSocket, WebSocketDisconnect
except ImportError:
    StreamingResponse = None  # type: ignore[assignment, misc]
    WebSocket = None  # type: ignore[assignment, misc]
    WebSocketDisconnect = Exception  # type: ignore[assignment, misc]

logger = logging.getLogger("ianimation.telemetry")


# Type definition for telemetry event callbacks
TelemetryEventCallback = Callable[[TelemetryEvent], object]


# -----------------------------------------------------------------------------
# 1. TelemetryBus (Asynchronous Broadcast & Replay Queue)
# -----------------------------------------------------------------------------

class TelemetryBus:
    """
    Central Asynchronous Telemetry Bus.

    Provides pub-sub event distribution using `asyncio.Queue` subscribers and callbacks,
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
        self._callbacks: Set[TelemetryEventCallback] = set()
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
        """Return the total number of active queue and callback subscribers."""
        return len(self._subscribers) + len(self._callbacks)

    def add_subscriber(self, queue: asyncio.Queue[TelemetryEvent]) -> None:
        """Register an active subscriber queue."""
        self._subscribers.add(queue)

    def remove_subscriber(self, queue: asyncio.Queue[TelemetryEvent]) -> None:
        """Unregister a subscriber queue."""
        self._subscribers.discard(queue)

    def add_callback(self, callback: TelemetryEventCallback) -> Callable[[], None]:
        """Register a synchronous or asynchronous callback subscriber."""
        self._callbacks.add(callback)

        def unsubscribe() -> None:
            self._callbacks.discard(callback)

        return unsubscribe

    def remove_callback(self, callback: TelemetryEventCallback) -> None:
        """Unregister a callback subscriber."""
        self._callbacks.discard(callback)

    def subscribe_progress(self, callback: Callable[[ProgressEvent], None]) -> Callable[[], None]:
        """Subscribe specifically to progress events."""
        def _filter(ev: TelemetryEvent) -> None:
            if isinstance(ev, ProgressEvent):
                callback(ev)
            elif isinstance(ev, dict) and ev.get("type") == "progress":
                try:
                    callback(ProgressEvent.model_validate(ev))
                except Exception:
                    pass
        return self.add_callback(_filter)

    def subscribe(
        self,
        callback_or_replay: Union[TelemetryEventCallback, bool] = True,
        replay_history: bool = True,
        max_queue_size: Optional[int] = None,
    ) -> Union[AsyncContextManager[asyncio.Queue[TelemetryEvent]], Callable[[], None]]:
        """
        Flexible subscriber method supporting both callback functions and async context managers.

        - If called with a callable argument (e.g. `bus.subscribe(on_event)`), registers the
          callback and returns an unsubscription function.
        - If called without a callable argument, acts as an async context manager yielding an
          `asyncio.Queue[TelemetryEvent]`.
        """
        if callable(callback_or_replay):
            callback = callback_or_replay
            return self.add_callback(callback)

        # Context manager mode
        effective_replay = bool(callback_or_replay) if isinstance(callback_or_replay, bool) else replay_history
        return self._subscribe_context_manager(replay_history=effective_replay, max_queue_size=max_queue_size)

    @asynccontextmanager
    async def _subscribe_context_manager(
        self,
        replay_history: bool = True,
        max_queue_size: Optional[int] = None,
    ) -> AsyncIterator[asyncio.Queue[TelemetryEvent]]:
        """Async context manager yielding a subscriber queue."""
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
        async with self._subscribe_context_manager(replay_history=replay_history, max_queue_size=max_queue_size) as queue:
            while True:
                event = await queue.get()
                try:
                    yield event
                finally:
                    queue.task_done()

    @staticmethod
    async def _wrap_awaitable(awaitable: Awaitable[object]) -> None:
        """Wrap an awaitable in a coroutine with exception logging."""
        try:
            await awaitable
        except Exception as exc:
            logger.warning("Error executing async telemetry callback subscriber: %s", exc)

    def _invoke_callbacks(self, event: TelemetryEvent) -> None:
        """Execute all registered callback subscribers."""
        for callback in list(self._callbacks):
            try:
                result = callback(event)
                if inspect.isawaitable(result):
                    loop = self.get_event_loop()
                    if loop is not None and loop.is_running():
                        coro: Coroutine[object, object, None] = self._wrap_awaitable(result)
                        try:
                            current_loop = asyncio.get_running_loop()
                        except RuntimeError:
                            current_loop = None

                        if current_loop is loop:
                            loop.create_task(coro)
                        else:
                            asyncio.run_coroutine_threadsafe(coro, loop)
                    else:
                        logger.warning(
                            "TelemetryBus._invoke_callbacks: async callback dropped; no running event loop available."
                        )
                        if inspect.iscoroutine(result):
                            result.close()
            except Exception as exc:
                logger.warning("Error executing telemetry callback subscriber: %s", exc)

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

        # Distribute to callback subscribers
        self._invoke_callbacks(event)

        # Distribute to all queue subscribers
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
        Schedules `emit` on the registered asyncio event loop or invokes callbacks immediately
        if no event loop is active.
        """
        loop = self.get_event_loop()
        if loop is not None and loop.is_running():
            asyncio.run_coroutine_threadsafe(self.emit(event), loop)
            return

        # Fallback when running without an active event loop (e.g. standalone CLI or unit test)
        self._history.append(event)
        if isinstance(event, ProgressEvent):
            self._latest_progress = event
        elif isinstance(event, PlanProposalEvent):
            self._latest_plan = event

        self._invoke_callbacks(event)
        logger.debug("TelemetryBus.emit_threadsafe running without active event loop; queue broadcast deferred.")

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
        while self.subscriber_count < count:
            if asyncio.get_running_loop().time() - start_time > timeout_seconds:
                return False
            await asyncio.sleep(0.01)
        return True


# -----------------------------------------------------------------------------
# 2. Global Singleton & Service Management
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


# Module-level convenience reference
telemetry_bus = get_telemetry_bus


# -----------------------------------------------------------------------------
# 3. Asynchronous & Synchronous Emission Helpers
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
    steps: List[PlanStep],
    status: PlanStatus = PlanStatus.PROPOSED,
    bus: Optional[TelemetryBus] = None,
) -> PlanProposalEvent:
    """Construct and emit a PlanProposalEvent asynchronously."""
    target_bus = bus if bus is not None else get_telemetry_bus()
    event = PlanProposalEvent(plan_id=plan_id, steps=steps, status=status)
    await target_bus.emit(event)
    return event


# -----------------------------------------------------------------------------
# 4. FastMCP Dual-Invocation Integration Adapter
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
# 5. Starlette / FastAPI SSE & WebSocket Emitters
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

    # Use the context manager method directly for streaming
    async with target_bus._subscribe_context_manager(replay_history=replay_history) as queue:
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

    async with target_bus._subscribe_context_manager(replay_history=replay_history) as queue:
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
