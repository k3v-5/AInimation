# Architectural Blueprint & Handoff Report: Milestone 2 (UE5 Bridge & Mock Server)

**Author**: `explorer_m2_1`  
**Date**: 2026-10-14  
**Target Milestone**: Milestone 2: UE5 Bridge & Mock Server (`backend/ue5/`)  
**Parent Conversation ID**: `7287cd58-777e-4099-99af-79aab795ba88`  
**Integrity Mode**: Demo / High-Fidelity Mock & Engine Bridge  

---

## 1. Observation

A comprehensive code and requirements audit was conducted across the IANIMATION codebase. Direct observations include:

### 1.1 Requirements & Standards
- **`ORIGINAL_REQUEST.md` (lines 12–18, 41–45, 61–66)**:
  - R1 mandates bidirectional HTTP/WebSocket communication with UE5 Remote Control API: runtime asset loading (`.glb`/`.fbx`), PBR materials, Lumen lighting, CineCamera choreography, and Movie Render Queue (MRQ) triggers.
  - Acceptance criteria mandate a high-fidelity offline mock server emulating ports `30010` (REST) and `30020` (WebSocket) to validate all RPCs without requiring an active Unreal Editor instance.
  - GEMINI.md enforces a **Zero-Any Policy** (100% strict typing with Pydantic v2 and Python typing) and SOLID architecture.
- **`PROJECT.md` (lines 137–144, 182, 217–225)**:
  - Features F-UE5-01 through F-UE5-08 define the scope for M2.
  - Interface contracts specify:
    - REST: `PUT http://localhost:30010/remote/object/call` with payload `{"objectPath": str, "functionName": str, "parameters": dict, "generateTransaction": bool}`.
    - WebSocket: `ws://localhost:30020/remote/protocol` with payload `{"MessageName": "http", "Parameters": {"Url": "/remote/object/call", "Verb": "PUT", "Body": {...}}}` and subscription payload `{"MessageName": "subscribe", "Parameters": {"Path": "/remote/object/property", ...}}`.

### 1.2 Existing Files in `backend/ue5/`
1. **`backend/ue5/client.py`**:
   - Lines 14, 39, 58, 81, 100, 171, 198: Uses `from typing import Any` and `Any` across all core signatures (`Dict[str, Any]`, `value: Any`, `callback: Any`). This violates GEMINI.md Zero-Any policy.
   - Lines 39–53: Uses synchronous standard library `urllib.request.urlopen` with blocking execution and hardcoded 5.0s timeout.
   - Lines 158–181: `UE5WebSocketClient` does not connect to any network socket. It only stores callbacks in a local dictionary `self._subscriptions = {}` without opening `ws://127.0.0.1:30020/remote/protocol`.
   - Lacks retry policies, exponential backoff, connection pooling, and connection lifecycle (`__aenter__` / `__aexit__`).
2. **`backend/ue5/mock_server.py`**:
   - Lines 15, 106–164, 166–218: Implements a synchronous `http.server.HTTPServer` on a background thread.
   - Completely lacks a WebSocket server on port `30020`. Any WebSocket connection to port 30020 fails with `ConnectionRefusedError`.
   - Lines 27–46, 55–89: `UE5MockState` only handles `ImportAsset`, `SpawnActor`, and `SetMaterial`. It does not support camera lens/aperture tracking, Lumen light rigs, sequence keyframing, console command execution, or Movie Render Queue execution.
   - Lines 17, 27–30: Uses `Any` throughout state dictionaries.
3. **`backend/ue5/camera.py`**:
   - Lines 24–134: `CineCameraChoreographer` generates camera positions via simple trigonometric circular orbit or aerial pan.
   - Lacks: Look-At target tracking (calculating pitch/yaw toward a focal actor or 3D point), dynamic lens/focal length transitions (e.g. 24mm to 85mm), aperture/depth-of-field control, beat-aligned camera cuts vs smooth interpolation, and Remote Control synchronization with UE5 Level Sequence.
4. **`backend/ue5/lighting.py`**:
   - Lines 42–132: Provides `studio_3point`, `cyberpunk`/`neon`, and `dramatic`.
   - Lacks: `night` (cool moonlight / ambient sky) and `directional` (outdoor sun daylight at 75,000 lux) presets, comprehensive Lumen post-process settings (Bloom, Auto-Exposure EV100, Tone Curve, Ray Tracing quality), and Remote Control deployment methods.
5. **`backend/ue5/materials.py`**:
   - Lines 29–64: `MaterialManager` is an in-memory dictionary.
   - Lacks: Dynamic Material Instance (MID) parameter binding for scalars (`Roughness`, `Metallic`), vectors (`BaseColor`), and textures (`AlbedoMap`, `NormalMap`). Lacks UE5 Remote Control RPC methods to import textures, create instances, and bind them to actor mesh slots.
6. **`backend/ue5/mrq.py`**:
   - Lines 17–60: `MRQManager` creates a 3-second dummy video if missing.
   - Lacks: Validation of `MovieRenderQueueJobConfig`, simulated engine warmup frames, real-time progress reporting to `TelemetryBus` (`stage="mrq_render"`), cancellation handling, and UE5 Movie Pipeline Subsystem integration.

### 1.3 Environment & Tests
- Verified via `run_command`:
  - Python version: `3.14.6`
  - Packages available: `aiohttp 3.13.3`, `websockets 15.0.1`, `pytest 9.1.1`, `pydantic 2.12.5`.
  - Pytest runs cleanly via `python -m pytest tests/backend/test_models.py` (16 passed in 1.33s).
  - No `tests/backend/test_ue5_bridge.py` exists yet.

---

## 2. Logic Chain

1. **Premise 1 (Zero-Any Compliance)**: Under GEMINI.md, no code may use `Any`. All parameters, returns, and dictionary structures must use explicit Pydantic v2 schemas or strict typing (`Union[str, int, float, bool, Dict[str, float]]`).
2. **Premise 2 (SOLID & Decoupling)**: Client and mock server must be decoupled. The client interacts with the server purely through HTTP REST and WebSocket wire protocols. Downstream modules (`camera.py`, `lighting.py`, `materials.py`, `mrq.py`) must interact with UE5 solely through client abstractions (`IUE5Client`).
3. **Premise 3 (High-Fidelity Mock Server)**: To fulfill Acceptance Criteria R1 without requiring a 50GB Unreal Editor installation during automated testing and CI, `backend/ue5/mock_server.py` must run both an HTTP server on port 30010 (`aiohttp.web`) and a WebSocket server on port 30020 (`websockets` / `aiohttp.web`). The state store must track actors, properties, materials, cameras, and MRQ renders with high fidelity.
4. **Premise 4 (Async-First with Sync Facades)**: The modern FastAPI / FastMCP / Tauri architecture operates asynchronously with event loops, while existing tests and scripts (like `verify_pipeline.py`) may call synchronous facades. All modules should implement asynchronous core methods (`call_async`, `set_property_async`, `render_async`) alongside convenient synchronous wrappers (`call`, `set_property`, `render`).
5. **Conclusion**: We formulate a unified architecture and complete class design across all 6 files in `backend/ue5/`, accompanied by a dedicated test specification for `tests/backend/test_ue5_bridge.py`.

---

## 3. Concrete Architectural Blueprints & Class Designs

### 3.1 `backend/ue5/client.py`: Async REST & WebSocket Client

#### Responsibilities
- Provide asynchronous and synchronous communication with UE5 Remote Control API.
- Strict typing with Zero-Any policy using Pydantic v2 models.
- Resilience: Retry policy with exponential backoff and jitter for transient connection failures.
- Connection lifecycle: Proper session management (`aiohttp.ClientSession`), connection pooling, and WebSocket keepalive/reconnection.

#### Type Definitions & Models (Zero-Any)
```python
UE5Scalar = Union[str, int, float, bool]
UE5ParamValue = Union[UE5Scalar, Dict[str, float], List[float], List[str]]
UE5ParamDict = Dict[str, UE5ParamValue]

class RemoteCallRequest(StrictBaseModel):
    object_path: str = Field(..., alias="objectPath")
    function_name: str = Field(..., alias="functionName")
    parameters: UE5ParamDict = Field(default_factory=dict)
    generate_transaction: bool = Field(default=False, alias="generateTransaction")

class RemoteCallResponse(StrictBaseModel):
    success: bool = Field(default=True, alias="Success")
    object_path: Optional[str] = Field(default=None, alias="Object")
    function_name: Optional[str] = Field(default=None, alias="Function")
    output: UE5ParamDict = Field(default_factory=dict, alias="Output")
    error: Optional[str] = Field(default=None, alias="Error")

class RemotePropertyRequest(StrictBaseModel):
    object_path: str = Field(..., alias="objectPath")
    property_name: str = Field(..., alias="propertyName")
    access: Literal["READ", "WRITE"] = Field(default="READ")
    property_value: Optional[UE5ParamValue] = Field(default=None, alias="propertyValue")
    generate_transaction: bool = Field(default=False, alias="generateTransaction")

class RemotePropertyResponse(StrictBaseModel):
    success: bool = Field(default=True, alias="Success")
    object_path: Optional[str] = Field(default=None, alias="Object")
    property_name: Optional[str] = Field(default=None, alias="Property")
    value: Optional[UE5ParamValue] = Field(default=None, alias="Value")
    error: Optional[str] = Field(default=None, alias="Error")

class RetryConfig(StrictBaseModel):
    max_retries: int = Field(default=3, ge=0)
    base_delay_seconds: float = Field(default=0.2, ge=0.0)
    max_delay_seconds: float = Field(default=2.0, ge=0.0)
    jitter: bool = Field(default=True)
```

#### Class Design: `AsyncUE5RestClient` & `UE5RestClient`
- **`AsyncUE5RestClient`**:
  - `__init__(host: Optional[str], port: Optional[int], timeout: float, retry_config: Optional[RetryConfig])`
  - `async def open() -> None`: Initializes `aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout))`.
  - `async def close() -> None`: Closes active session.
  - `async def __aenter__()` / `async def __aexit__()`
  - `async def call(object_path: str, function_name: str, parameters: Optional[UE5ParamDict] = None, generate_transaction: bool = False) -> RemoteCallResponse`:
    PUT to `/remote/object/call` with retry loop and backoff.
  - `async def set_property(object_path: str, property_name: str, value: UE5ParamValue, generate_transaction: bool = False) -> RemotePropertyResponse`:
    PUT to `/remote/object/property` with `access="WRITE"`.
  - `async def get_property(object_path: str, property_name: str) -> Optional[UE5ParamValue]`:
    PUT to `/remote/object/property` with `access="READ"`.
  - `async def import_asset(source_path: str, destination_path: str = "/Game/Imported") -> RemoteCallResponse`:
    Validates file exists on disk, then calls `/Script/UnrealEd.Default__EditorAssetLibrary:ImportAsset`.
  - `async def spawn_actor(actor_class: str, location: Optional[Union[Vector3D, Dict[str, float]]], rotation: Optional[Union[Rotator3D, Dict[str, float]]]) -> str`:
    Calls `/Script/UnrealEd.Default__EditorActorSubsystem:SpawnActor` and returns the actor path.
- **`UE5RestClient`** (Synchronous facade):
  - Wraps `AsyncUE5RestClient` using an internal event loop or thread-safe runner (`asyncio.run`), maintaining identical method signatures for synchronous consumption.

#### Class Design: `AsyncUE5WebSocketClient` & `UE5WebSocketClient`
- **`AsyncUE5WebSocketClient`**:
  - `__init__(host: Optional[str], port: Optional[int], timeout: float)`
  - `async def connect() -> None`: Establishes `websockets.connect(url)` and spawns background listener task `_receive_loop`.
  - `async def disconnect() -> None`: Cancels listener task and cleanly closes socket.
  - `async def send_rpc(verb: str, url: str, body: UE5ParamDict) -> RemoteCallResponse`:
    Constructs `{"MessageName": "http", "Parameters": {"Url": url, "Verb": verb, "Body": body}, "Id": next_id}`.
    Registers a pending `asyncio.Future` for `next_id` and awaits response.
  - `async def subscribe(object_path: str, property_name: str, callback: Callable[[RemotePropertyResponse], None]) -> None`:
    Sends `{"MessageName": "subscribe", "Parameters": {"ObjectPath": object_path, "PropertyName": property_name}}`.
    Registers callback in `self._subscriptions[(object_path, property_name)]`.
  - `async def unsubscribe(object_path: str, property_name: str, callback: Optional[Callable[[RemotePropertyResponse], None]] = None) -> None`:
    Sends unsubscribe message and removes callback.
  - `async def _receive_loop() -> None`:
    Parses incoming messages. If matching `Id`, resolves pending Future. If `Type == "Event"`, dispatches to subscribed callbacks.
- **`AsyncUE5RemoteClient` & `UE5RemoteClient`**:
  - Unified composite combining REST and WebSocket clients with unified context management.

---

### 3.2 `backend/ue5/mock_server.py`: Async Mock Server (Port 30010 REST & Port 30020 WS)

#### Responsibilities
- Run a high-fidelity asynchronous HTTP server on port 30010 (`aiohttp.web`) simulating UE5 Remote Control REST endpoints.
- Run a high-fidelity WebSocket server on port 30020 simulating UE5 `/remote/protocol`.
- Maintain a thread-safe and coroutine-safe in-memory simulation state (`UE5MockState`).
- Support dual lifecycle: Async (`async with UE5MockServer():`) and Sync (`with UE5MockServer():`).

#### State Model: `UE5MockState`
```python
class UE5ActorRecord(StrictBaseModel):
    actor_id: str
    actor_class: str
    location: Dict[str, float] = Field(default_factory=lambda: {"X": 0.0, "Y": 0.0, "Z": 0.0})
    rotation: Dict[str, float] = Field(default_factory=lambda: {"Pitch": 0.0, "Yaw": 0.0, "Roll": 0.0})
    properties: Dict[str, UE5ParamValue] = Field(default_factory=dict)
    materials: Dict[int, str] = Field(default_factory=dict)  # slot_idx -> material_path
    tags: List[str] = Field(default_factory=list)

class UE5AssetRecord(StrictBaseModel):
    source_path: str
    destination_path: str
    asset_name: str
    asset_type: str = "StaticMesh"

class UE5RenderJobRecord(StrictBaseModel):
    job_id: str
    scene_path: str
    output_path: str
    fps: int
    resolution: str
    warmup_frames: int
    total_frames: int
    status: str = "Completed"
    elapsed_seconds: float = 0.5
```

- **`UE5MockState` Capabilities**:
  - `actors: Dict[str, UE5ActorRecord]`
  - `assets: List[UE5AssetRecord]`
  - `properties: Dict[str, Dict[str, UE5ParamValue]]`
  - `render_jobs: List[UE5RenderJobRecord]`
  - `ws_subscriptions: Dict[Tuple[str, str], Set[websockets.WebSocketServerProtocol]]`
  - Pre-populated actors:
    - `/Game/Stage_Main.Stage_Main:PersistentLevel.CineCameraActor_1` (focal_length=35.0, aperture=2.8, location=(0, -400, 120))
    - `/Game/Stage_Main.Stage_Main:PersistentLevel.DirectionalLight_1` (intensity=10.0, lux=75000.0)
    - `/Game/Stage_Main.Stage_Main:PersistentLevel.SkyLight_1` (intensity=1.0)
    - `/Game/Stage_Main.Stage_Main:PersistentLevel.PostProcessVolume_1` (lumen_gi=True, lumen_reflections=True)
  - Method `call_function(object_path, function_name, parameters) -> Dict[str, UE5ParamValue]`:
    - Handles `SpawnActor`: Adds `UE5ActorRecord`, returns `{"Success": True, "ActorId": actor_id}`.
    - Handles `ImportAsset`: Verifies existence if source path is provided, records asset, returns `{"Success": True, "AssetPath": destination_path}`.
    - Handles `SetMaterial`: Updates actor material slot, returns `{"Success": True, "ActorId": actor_id, "Material": mat_path}`.
    - Handles `SetActorLocationAndRotation`: Updates location and rotation in actor record.
    - Handles `RenderQueueWithExecutor` (MRQ): Records render job, creates synthetic video output file on disk if path provided.
  - Method `set_property(object_path, property_name, value) -> Dict[str, UE5ParamValue]`:
    - Updates property in `properties` and `actor.properties`.
    - Triggers WebSocket broadcast to active subscribers!

#### Mock Server Architecture (`aiohttp` + `websockets`)
- REST routes (`port 30010`):
  - `GET /remote/info`: Returns `{"Version": "5.4.0", "Engine": "UnrealEngine", "Mock": True}`.
  - `PUT /remote/object/call`: Dispatches to `state.call_function`.
  - `PUT /remote/object/property`: Handles `access="READ"` and `access="WRITE"`.
  - `GET /remote/object/property`: Returns property tree.
  - `PUT /remote/preset`: Applies preset.
- WebSocket route (`port 30020` on `/remote/protocol`):
  - Handles message `MessageName == "http"`: Executes internal REST handler and sends reply with same `Id`.
  - Handles message `MessageName == "subscribe"`: Registers connection for property change events.
  - Handles message `MessageName == "unsubscribe"`: Removes subscription.
  - Emits real-time property change events when properties change.

---

### 3.3 `backend/ue5/camera.py`: CineCamera Choreography & Beat Sync

#### Responsibilities
- Choreograph CineCameraActor motion aligned to musical beat timestamps.
- Support 5 cinematic presets: `smooth_orbit`, `dramatic_orbit`, `aerial_pan`, `front_close`, `spiral_ascent`.
- Dynamic lens and depth-of-field control: focal length (18mm to 135mm), aperture (f/1.4 to f/8.0), and manual focus distance.
- Target tracking (Look-At computation): Dynamically computes camera Pitch and Yaw to keep a target point or character chest/head in frame.
- Remote Control sequence deployment: Push generated keyframes into UE5 Level Sequence CineCamera track.

#### Models & Presets
```python
class CameraLensPreset(StrEnum):
    ULTRA_WIDE_18MM = "ultra_wide_18mm"  # f/4.0, landscape/establishing
    WIDE_24MM = "wide_24mm"              # f/2.8, dynamic orbit
    STANDARD_35MM = "standard_35mm"      # f/2.0, standard action
    PORTRAIT_50MM = "portrait_50mm"      # f/1.8, close-up performance
    TELEPHOTO_85MM = "telephoto_85mm"    # f/1.4, extreme shallow DOF portrait

class LookAtTarget(StrictBaseModel):
    target_position: Vector3D = Field(default_factory=lambda: Vector3D(x=0.0, y=0.0, z=120.0))
    look_at_height_offset: float = Field(default=0.0)
```

#### Class Design: `CineCameraChoreographer`
- `calculate_look_at(cam_pos: Vector3D, target_pos: Vector3D) -> Tuple[float, float]`:
  - `yaw = math.degrees(math.atan2(target_pos.y - cam_pos.y, target_pos.x - cam_pos.x))`
  - `pitch = math.degrees(math.atan2(target_pos.z - cam_pos.z, math.hypot(target_pos.x - cam_pos.x, target_pos.y - cam_pos.y)))`
  - Returns `(pitch, yaw)` aligned to UE5 coordinates.
- `generate_track(beat_timestamps, total_duration, preset, target, lens_preset, center_z) -> List[CameraKeyframe]`:
  - Enforces start timestamp `0.0` and end timestamp `total_duration`.
  - For each beat: computes 3D coordinates based on preset math, computes Look-At rotation, calculates distance to target, sets `focus_distance = distance`, assigns focal length and aperture according to lens preset and shot proximity.
  - Adds subtle audio-reactive Dutch tilt (`roll`) on alternating beats.
- `async apply_to_ue5(client: AsyncUE5RemoteClient, actor_path: str, keyframes: List[CameraKeyframe]) -> bool`:
  - Bakes initial transform to CineCameraActor via `client.set_property` or sequence RPC.

---

### 3.4 `backend/ue5/lighting.py`: Lumen Lighting Rig & Post-Process Presets

#### Responsibilities
- Configure dynamic real-time global illumination presets adhering to Lumen standards.
- Provide 5 lighting rig presets:
  1. `studio_3point`: Key light (Spot, 8,000 lm, 45°), Fill light (Spot, 3,500 lm, -45°), Rim light (Point, 5,000 lm, backlight), SkyLight ambient.
  2. `cyberpunk_neon`: Key neon cyan (Spot, 8,000 lm), Fill neon magenta (Spot, 6,000 lm), Rim amber/orange (Point, 12,000 lm).
  3. `dramatic_chiaroscuro`: High contrast Key (Spot, 15,000 lm), Rim hair light (Spot, 10,000 lm), minimal ambient fill.
  4. `outdoor_sunlight`: Directional Sunlight (75,000 lux, warm 5500K), SkyLight (2.0 intensity), Atmospheric Fog.
  5. `night_moonlight`: Directional Moonlight (0.5 lux, cool blue 8500K), Deep ambient sky (0.2 intensity), cool specular highlights.
- Post-process volume settings:
  - Lumen Global Illumination toggle and quality.
  - Lumen Raytraced Reflections toggle.
  - Auto-exposure EV100 bounds (`min_ev100`, `max_ev100`).
  - Bloom intensity and threshold.
  - Color grading (saturation, contrast).
- Remote Control deployment method:
  - `apply_to_ue5(client: UE5RemoteClient, setup: LumenLightingSetup) -> Dict[str, str]` to spawn or update lights in the active UE5 level.

---

### 3.5 `backend/ue5/materials.py`: PBR Dynamic Material Instances

#### Responsibilities
- Manage PBR material definitions, Dynamic Material Instances (MIDs), and texture maps.
- Support scalar parameters (`Roughness`, `Metallic`, `Specular`, `EmissiveIntensity`), vector parameters (`BaseColor`, `EmissiveColor`), and texture parameter links (`AlbedoMap`, `NormalMap`, `RoughnessMap`, `MetallicMap`, `AOMap`).
- Deploy materials to UE5:
  - Import external PBR texture files (`.png`, `.jpg`) into `/Game/Materials/Textures/` via `client.import_asset()`.
  - Create Material Instance Constant or DMI via Remote Control RPC.
  - Set parameter overrides via `/remote/object/call`.
  - Assign material to actor mesh slot 0 via `/remote/object/call` (`SetMaterial`).

#### Models
```python
class DynamicMaterialInstance(StrictBaseModel):
    instance_name: str
    parent_material_path: str = "/Game/Materials/M_MasterPBR"
    base_color: ColorRGB = Field(default_factory=lambda: ColorRGB(r=0.8, g=0.8, b=0.8))
    roughness: float = Field(default=0.5, ge=0.0, le=1.0)
    metallic: float = Field(default=0.0, ge=0.0, le=1.0)
    specular: float = Field(default=0.5, ge=0.0, le=1.0)
    emissive_color: ColorRGB = Field(default_factory=lambda: ColorRGB(r=0.0, g=0.0, b=0.0))
    emissive_intensity: float = Field(default=0.0, ge=0.0)
    textures: Optional[PBRTextureSet] = None

    def to_ue5_parameters(self) -> Dict[str, UE5ParamValue]:
        params: Dict[str, UE5ParamValue] = {
            "Roughness": self.roughness,
            "Metallic": self.metallic,
            "Specular": self.specular,
            "EmissiveIntensity": self.emissive_intensity,
            "BaseColor": self.base_color.to_ue5_dict(),
            "EmissiveColor": self.emissive_color.to_ue5_dict(),
        }
        return params
```

---

### 3.6 `backend/ue5/mrq.py`: Movie Render Queue Executor & Telemetry Progress

#### Responsibilities
- Orchestrate Movie Render Queue (MRQ) execution adhering to `MovieRenderQueueJobConfig`.
- Simulate engine warmup frames (e.g. 15–30 frames for Lumen GI and motion blur stabilization).
- Non-blocking asynchronous progress streaming: emits `ProgressEvent(stage="mrq_render", percentage=...)` to `TelemetryBus` from 0.0% to 100.0%.
- Generates valid output video container (using synthetic fixture or real encoder) matching duration and fps.
- Emits `AssetReadyEvent(AssetType.RENDER_VIDEO, file_path=output_path)` upon completion.
- Support cooperative cancellation via `asyncio.Event` cancellation token.
- Seamless integration with UE5 Remote Control API: invokes `/Script/MovieRenderPipelineCore.Default__MoviePipelineQueueEngineSubsystem:RenderQueueWithExecutor` when live.

#### Class Design: `MRQManager`
```python
class MRQManager:
    def __init__(self, output_dir: Optional[Union[str, Path]] = None, telemetry_bus: Optional[TelemetryBus] = None) -> None:
        self.output_dir: Path = Path(output_dir) if output_dir else Path("./renders")
        self.bus: TelemetryBus = telemetry_bus if telemetry_bus is not None else get_telemetry_bus()

    async def render_async(
        self,
        job_config: MovieRenderQueueJobConfig,
        cancellation_token: Optional[asyncio.Event] = None,
        duration_seconds: float = 3.0,
    ) -> RenderResult:
        # Phase 1: Warmup frames simulation (0% -> 10%)
        # Phase 2: Render frame loop with telemetry emission (10% -> 95%)
        # Phase 3: Video file generation and validation (95% -> 100%)
        # Phase 4: Emit AssetReadyEvent and return RenderResult

    def render(
        self,
        scene_path: str,
        output_path: str,
        fps: int = 30,
        resolution: str = "1280x720",
        warmup_frames: int = 15,
        anti_aliasing_samples: int = 8,
    ) -> RenderResult:
        # Synchronous facade executing render_async
```

---

## 4. Comprehensive Test Suite Design: `tests/backend/test_ue5_bridge.py`

To validate Milestone 2 with 100% test coverage, a dedicated pytest suite `tests/backend/test_ue5_bridge.py` will be created with the following test cases:

| Test Case | Target Feature | Validation Scope |
|---|---|---|
| `test_ue5_rest_client_lifecycle_and_call` | F-UE5-01 | Async/sync REST `call()` with parameter serialization, headers, and response parsing |
| `test_ue5_rest_client_property_read_write` | F-UE5-01 | REST `get_property()` and `set_property()` on actor components |
| `test_ue5_rest_client_retries_and_resilience` | F-UE5-01 | Exponential backoff retry logic on network timeout / HTTP 503 |
| `test_ue5_ws_client_lifecycle_and_rpc` | F-UE5-02 | WebSocket connection to port 30020, `/remote/protocol` message formatting, ID matching |
| `test_ue5_ws_client_property_subscription` | F-UE5-02 | Subscribing to property changes and receiving pushed event callbacks |
| `test_ue5_mock_server_dual_port_binding` | F-UE5-03 | Mock server listening on port 30010 (REST) and port 30020 (WS) concurrently |
| `test_ue5_mock_server_stateful_actor_tracking` | F-UE5-03 | SpawnActor, SetActorLocation, SetMaterial, and property mutation persistence |
| `test_ue5_dynamic_asset_import_glb_fbx` | F-UE5-04 | Asset importing with path validation and Content Browser destination registration |
| `test_ue5_pbr_material_parameter_assignment` | F-UE5-05 | PBR material creation, scalar/vector/texture parameters, and actor slot binding |
| `test_ue5_lumen_lighting_presets_all_5` | F-UE5-06 | Presets for studio, neon, dramatic, sunlight, and moonlight with post-process settings |
| `test_ue5_cinecamera_choreography_and_beat_sync` | F-UE5-07 | Keyframe generation for all presets, Look-At calculations, and focal length interpolation |
| `test_ue5_mrq_render_execution_and_telemetry` | F-UE5-08 | MRQ execution, warmup frames, telemetry progress emission, and output MP4 generation |
| `test_ue5_mrq_cancellation_token` | F-UE5-08 | Cooperative cancellation of ongoing render job midway through execution |
| `test_ue5_end_to_end_mock_pipeline` | F-UE5-01–08 | Integrated flow: Mock server -> Client -> Spawn Camera & Lights -> Choreograph -> Render Video |

---

## 5. Caveats & Assumptions

1. **Hardware Dependencies**: In CI / offline environments, Unreal Engine 5 is not installed. All network calls default to `ue5_mock_mode: bool = True` (or fallback simulation). The mock server provides full binary protocol parity with UE5 Remote Control API 5.4.
2. **Video Encoding Fallback**: When FFmpeg / GPU encoders are unavailable on CPU environments, `MRQManager` utilizes the pure-binary ISO Base Media File Format (MP4) container generator developed in `tests/e2e/fixtures/synthetic_video.py` to ensure valid playable video artifacts without external dependencies.
3. **No Code Implementation in this Turn**: Adhering strictly to the explorer agent role, no production source files have been modified. All architecture blueprints are preserved in this handoff for the executor agent.

---

## 6. Conclusion

Milestone 2 bridges the application to Unreal Engine 5 via a dual-engine architecture:
1. An **Async-First REST and WebSocket Remote Control Client** (`backend/ue5/client.py`) adhering 100% to SOLID and the Zero-Any policy, with retry resilience and connection pooling.
2. An **Async High-Fidelity Mock Server** (`backend/ue5/mock_server.py`) binding ports 30010 and 30020 simultaneously (`aiohttp` + `websockets`), tracking actors, properties, materials, cameras, and MRQ renders statefully.
3. Rhythmic **CineCamera Choreography** (`backend/ue5/camera.py`) with mathematical Look-At tracking and beat synchronization.
4. Comprehensive **Lumen Lighting Rigs** (`backend/ue5/lighting.py`) covering all 5 core presets and post-process parameters.
5. **Dynamic PBR Material Management** (`backend/ue5/materials.py`) linking texture sets and parameters to actors.
6. **Movie Render Queue Executor** (`backend/ue5/mrq.py`) with warmup frame simulation, cooperative cancellation, and real-time telemetry streaming to `TelemetryBus`.

All designs conform strictly to `GEMINI.md`, `PROJECT.md`, and Pydantic v2.

---

## 7. Verification Method

Once the executor implements the blueprint, the system can be independently verified via:

1. **Unit Test Suite**:
   ```powershell
   python -m pytest tests/backend/test_ue5_bridge.py -v
   ```
2. **E2E Feature Coverage (Tier 1 Features F-UE5-01 through F-UE5-08)**:
   ```powershell
   python -m pytest tests/e2e/test_tier1_features.py -k "ue5" -v
   ```
3. **E2E Cross-Feature Interactions (Tier 3)**:
   ```powershell
   python -m pytest tests/e2e/test_tier3_interactions.py -k "camera or mrq" -v
   ```
4. **Zero-Any Lint / Static Typing Check**:
   ```powershell
   python -m pytest tests/backend/test_models.py -v
   ```
5. **Invalidation Conditions**:
   - Any use of `from typing import Any` in `backend/ue5/`.
   - Failure of mock server to bind port 30020 or handle WebSocket `/remote/protocol`.
   - MRQ render failing to emit progress events to `TelemetryBus`.
   - Camera keyframes failing to align with input beat timestamps.
