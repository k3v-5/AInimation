# Telemetry Bus & Emitters Specification (`backend/core/telemetry.py`)

**Document Version**: 1.0.0  
**Target Module**: `backend/core/telemetry.py`  
**Milestone**: Milestone 1 (Core Models & Telemetry)  
**Author**: Milestone 1 Explorer 2 (Telemetry Bus & Emitters)  
**Compliance**: GEMINI.md Zero-Any Policy (100% Strict Typing) & Clean Architecture / SOLID  

---

## 1. Executive Summary

This specification establishes the architectural contracts, event schema definitions, and production code design for `backend/core/telemetry.py`. Telemetry in the **IANIMATION** system is the critical real-time communication backbone that bridges:
1. **Long-running background tasks** (AI audio separation, Image-to-3D synthesis, MediaPipe mocap extraction, UE5 Movie Render Queue rendering).
2. **FastMCP Server execution** (reporting progress to standard MCP clients like Claude Desktop or Cursor).
3. **Desktop Native UI (Tauri v2 + React 18)** (live progress percentages, waveform/timeline markers, plan approval cards, and terminal logs).
4. **Synchronous OS worker threads and subprocesses** (Librosa/Demucs audio processing, Scipy filterbanks, procedural mesh generators).

A drop-in reference implementation has been developed and verified with 14 automated unit tests:
- Reference Implementation: `.agents/teamwork/explorer_m1_2/proposed_telemetry.py`
- Test Suite: `.agents/teamwork/explorer_m1_2/test_telemetry.py` (100% test pass rate)

---

## 2. Event Model Contracts & Schemas

The event data models map 1:1 to the frontend Zod contract specified in `PROJECT.md` (`TelemetryEventSchema`), while enforcing immutable validation via Pydantic v2.

### 2.1 Enums & Primitive Value Unions

To comply with the Zero-Any Policy, all parameters and metadata are strictly typed without using `Any`:

```python
class AssetType(StrEnum):
    AUDIO_STEMS = "audio_stems"
    MESH_3D = "mesh_3d"
    RIGGED_MESH = "rigged_mesh"
    MOCAP = "mocap"
    RENDER_VIDEO = "render_video"

class LogLevel(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

class PlanStatus(StrEnum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

PlanParamPrimitive = Union[str, int, float, bool, None]
PlanParamValue = Union[PlanParamPrimitive, List[str], Dict[str, str]]
```

### 2.2 Event Models

All models inherit from `StrictTelemetryModel`, which configures `frozen=True`, `extra="forbid"`, and `strict=False` (allowing coercion of valid numeric/string representations):

#### 1. `ProgressEvent`
Emitted to report fractional/percentage progress during atomic tool or pipeline execution.
```python
class ProgressEvent(StrictTelemetryModel):
    type: Literal["progress"] = "progress"
    stage: str = Field(..., min_length=1, description="Execution stage identifier")
    percentage: float = Field(..., ge=0.0, le=100.0, description="Completion percentage (0.0 to 100.0)")
    message: str = Field(..., description="Human-readable progress description for the UI")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    plan_id: Optional[str] = Field(default=None, description="Optional associated plan ID")
    step_id: Optional[Union[str, int]] = Field(default=None, description="Optional step index or UUID")
    tool_name: Optional[str] = Field(default=None, description="Optional name of the emitting tool")
```

#### 2. `PlanProposalEvent`
Emitted when the Copilot agent formulates or updates a multi-stage production plan.
```python
class PlanProposalEvent(StrictTelemetryModel):
    type: Literal["plan_proposal"] = "plan_proposal"
    plan_id: str = Field(..., min_length=1, description="Unique production plan identifier")
    steps: List[PlanStepPayload] = Field(default_factory=list, description="Ordered production steps")
    status: PlanStatus = Field(default=PlanStatus.PROPOSED, description="Current lifecycle plan status")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
```

#### 3. `AssetReadyEvent`
Emitted when an intermediate or final pipeline asset (mesh `.glb`, rig, mocap animation, audio stems, rendered video `.mp4`) is finalized.
```python
class AssetReadyEvent(StrictTelemetryModel):
    type: Literal["asset_ready"] = "asset_ready"
    asset_id: str = Field(..., min_length=1, description="Unique asset identifier")
    asset_type: AssetType = Field(..., description="Asset type classification")
    file_path: str = Field(..., min_length=1, description="Absolute file path to the completed asset")
    metadata: Optional[Dict[str, str]] = Field(default=None, description="Key-value asset metadata")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
```

#### 4. `LogEvent`
Emitted for structured real-time logging streamed to the Tauri copilot console.
```python
class LogEvent(StrictTelemetryModel):
    type: Literal["log"] = "log"
    level: LogLevel = Field(default=LogLevel.INFO, description="Log severity level")
    message: str = Field(..., description="Log message text")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source: Optional[str] = Field(default=None, description="Originating subsystem (e.g. 'FastMCP', 'UE5Bridge')")
```

#### 5. Discriminated Union
```python
TelemetryEvent = Annotated[
    Union[ProgressEvent, PlanProposalEvent, AssetReadyEvent, LogEvent],
    Field(discriminator="type"),
]
TelemetryEventAdapter: Final[TypeAdapter[TelemetryEvent]] = TypeAdapter(TelemetryEvent)
```

---

## 3. Asynchronous Broadcast Event Bus (`TelemetryBus`)

### 3.1 Architectural Principles
- **Asynchronous Decoupling**: Producers (`emit`) broadcast without awaiting consumers.
- **Independent Queues**: Each subscriber holds an independent `asyncio.Queue[TelemetryEvent]`.
- **Lossy Backpressure**: In desktop applications, a slow network consumer (e.g. paused WebSocket) must never block AI generation or cause memory leaks. When a subscriber queue is full, `TelemetryBus` drops the oldest item (`queue.get_nowait()`) and enqueues the latest telemetry event.
- **Replay Ring Buffer**: Maintains a configurable ring buffer (`history_size: int = 100`) of recent events plus cached pointers to `latest_progress` and `latest_plan`. New frontend connections optionally receive the replayed state immediately (`replay_history=True`).

### 3.2 Subscription Lifecycle
Subscribers use an async context manager ensuring zero connection leaks:
```python
async with bus.subscribe(replay_history=True) as queue:
    while True:
        event = await queue.get()
        # handle event
        queue.task_done()
```

---

## 4. Thread-Safe Emission for Synchronous Workers

### 4.1 Challenge & Solution
Heavy CPU-bound AI operations (Librosa audio analysis, Demucs stem filtering, procedural mesh generation) execute in dedicated OS threads (e.g. `ThreadPoolExecutor` or `threading.Thread`). These threads cannot call `await bus.emit(event)`.

`TelemetryBus` implements `emit_threadsafe(event)`:
1. Retains a reference to the running main event loop (`bus.set_event_loop(loop)` or detected via `asyncio.get_running_loop()`).
2. Dispatches coroutines across thread boundaries using `asyncio.run_coroutine_threadsafe(self.emit(event), loop)`.
3. If no event loop is currently running, safely appends the event to the history buffer and logs a debug notice.

### 4.2 Synchronous Convenience Functions
```python
emit_progress_sync(stage="audio", percentage=50.0, message="Processing stems", bus=bus)
emit_log_sync(message="Generated GLB preview", level=LogLevel.INFO, bus=bus)
emit_asset_ready_sync(asset_id="asset-1", asset_type=AssetType.MESH_3D, file_path="/out/m.glb", bus=bus)
```

---

## 5. FastMCP Dual-Invocation Integration

### 5.1 Dual-Invocation Context
According to R4 Acceptance Criteria (Line 54), all FastMCP tools must be callable both:
1. **Via MCP Client**: FastMCP automatically injects a `Context` instance (`ctx: Context`).
2. **Programmatically via Python**: When called directly by internal app routines, tests, or scripts, `ctx` is `None`.

### 5.2 Unified Reporter: `report_fastmcp_progress`
```python
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
```
**Behavior**:
1. Emits `ProgressEvent` to `TelemetryBus` (ensuring Tauri UI and WebSocket subscribers receive progress).
2. Clamps `percentage` between `0.0` and `100.0`.
3. If `ctx is not None`, calls `await ctx.report_progress(progress=percentage / 100.0, total=1.0, message=message)` (handling MCP clients expecting `0.0` to `1.0` progress).
4. Handles context reporting failures gracefully so progress errors never interrupt tool computation.

---

## 6. Starlette / FastAPI SSE & WebSocket Emitters

### 6.1 Server-Sent Events (SSE)
- Function: `telemetry_sse_stream(bus, replay_history=True, heartbeat_seconds=15.0)`
- Format:
  ```
  event: progress
  data: {"type":"progress","stage":"audio_analysis","percentage":50.0,"message":"Processing","timestamp":"..."}
  ```
- Keep-Alive: Yields `: keep-alive\n\n` periodically to prevent HTTP proxy timeouts.
- Response Factory: `create_telemetry_sse_response()` returning `StreamingResponse` with headers:
  - `Cache-Control: no-cache`
  - `Connection: keep-alive`
  - `Content-Type: text/event-stream`
  - `X-Accel-Buffering: no`

### 6.2 WebSockets
- Handler: `handle_telemetry_websocket(websocket, bus, replay_history=True)`
- Lifecycle:
  1. Accepts connection: `await websocket.accept()`.
  2. Subscribes to `TelemetryBus`.
  3. Loops sending `await websocket.send_text(event.model_dump_json())`.
  4. Intercepts `WebSocketDisconnect` cleanly and unregisters subscriber queue to prevent memory leaks.

---

## 7. Verification & Test Evidence

The proposed design was verified against the project Python environment:
- **Python**: 3.14.6 (64-bit AMD64)
- **Pydantic**: 2.12.5
- **Starlette**: 1.3.1
- **MCP**: FastMCP SDK installed

### Test Results (`test_telemetry.py`)
```
.agents/teamwork/explorer_m1_2/test_telemetry.py::test_progress_event_validation PASSED
.agents/teamwork/explorer_m1_2/test_telemetry.py::test_progress_event_boundaries PASSED
.agents/teamwork/explorer_m1_2/test_telemetry.py::test_plan_proposal_event_validation PASSED
.agents/teamwork/explorer_m1_2/test_telemetry.py::test_asset_ready_event_validation PASSED
.agents/teamwork/explorer_m1_2/test_telemetry.py::test_log_event_validation PASSED
.agents/teamwork/explorer_m1_2/test_telemetry.py::test_telemetry_bus_broadcast_multiple_subscribers[asyncio] PASSED
.agents/teamwork/explorer_m1_2/test_telemetry.py::test_telemetry_bus_history_and_replay[asyncio] PASSED
.agents/teamwork/explorer_m1_2/test_telemetry.py::test_telemetry_bus_backpressure_slow_subscriber[asyncio] PASSED
.agents/teamwork/explorer_m1_2/test_telemetry.py::test_telemetry_bus_threadsafe_emission[asyncio] PASSED
.agents/teamwork/explorer_m1_2/test_telemetry.py::test_report_fastmcp_progress_with_context[asyncio] PASSED
.agents/teamwork/explorer_m1_2/test_telemetry.py::test_report_fastmcp_progress_without_context_direct_python[asyncio] PASSED
.agents/teamwork/explorer_m1_2/test_telemetry.py::test_fastmcp_telemetry_bridge[asyncio] PASSED
.agents/teamwork/explorer_m1_2/test_telemetry.py::test_sse_stream_format[asyncio] PASSED
.agents/teamwork/explorer_m1_2/test_telemetry.py::test_websocket_telemetry_endpoint PASSED

============================= 14 passed in 1.26s ==============================
```

### Zero-Any Policy Verification
AST parser confirmed **0 occurrences of `Any`** across all type annotations in `proposed_telemetry.py`.
