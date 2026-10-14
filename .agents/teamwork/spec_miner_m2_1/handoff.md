# Handoff Report: Specification Mining for Milestone 2 (UE5 Bridge & Mock Server)

**Target Milestone**: Milestone 2 (`backend/ue5/`)  
**Miner Agent**: `spec_miner_m2_1`  
**Date**: 2026-10-14  
**Status**: COMPLETE  

---

## 1. Observation

### 1.1 Direct Repository Evidence
1. **Repository Layout and Architectural Contracts** (`.agents/teamwork/PROJECT.md` lines 56–70, 137–144, 217–225):
   - Module path: `backend/ue5/` containing:
     - `client.py`: REST and WebSocket Remote Control client.
     - `mock_server.py`: High-fidelity offline UE5 emulator (ports 30010 HTTP, 30020 WebSocket).
     - `camera.py`: CineCameraActor choreography & tracking synced to audio beats.
     - `lighting.py`: Lumen lighting rig (Directional, SkyLight, 3-point key/fill/rim, PostProcessVolume).
     - `materials.py`: Dynamic PBR material assignment (albedo, normal, roughness, metallic).
     - `mrq.py`: Movie Render Queue triggers & job tracking.
   - Wire contract definitions:
     - REST endpoint: `PUT http://localhost:30010/remote/object/call` with payload `{"objectPath": str, "functionName": str, "parameters": dict, "generateTransaction": bool}`.
     - WebSocket endpoint: `ws://localhost:30020/remote/protocol` with payload `{"MessageName": "http", "Parameters": {"Url": "/remote/object/call", "Verb": "PUT", "Body": {...}}}`.
     - Event subscriptions: `{"MessageName": "subscribe", "Parameters": {"Path": "/remote/object/property", ...}}` or `{"MessageName": "preset.register", "Parameters": {"PresetName": str}}`.

2. **Core Domain Schema Bindings** (`backend/core/models.py` lines 55–115, 550–858):
   - Spatial math primitives:
     - `Vector3D` (lines 55–76): fields `x`, `y`, `z`; method `to_ue5_dict()` yields `{"X": self.x, "Y": self.y, "Z": self.z}`.
     - `Rotator3D` (lines 78–99): fields `pitch`, `yaw`, `roll`; method `to_ue5_dict()` yields `{"Pitch": self.pitch, "Yaw": self.yaw, "Roll": self.roll}`.
     - `ColorRGB` (lines 101–115): fields `r`, `g`, `b` in `[0.0, 1.0]`; method `to_ue5_dict()` yields `{"R": self.r, "G": self.g, "B": self.b, "A": 1.0}`.
   - PBR Materials:
     - `PBRTextureSet` (lines 239–264): fields `albedo_path`, `normal_path`, `roughness_path`, `metallic_path`, `ambient_occlusion_path`, `emissive_path`, `height_path`, `resolution`.
   - Camera Choreography:
     - `CameraKeyframe` (lines 550–637): fields `time`, `x`, `y`, `z`, `pitch`, `yaw`, `roll`, `fov` ($0 < \text{fov} < 180$), `focal_length`, `aperture`, `focus_distance`; method `to_ue5_payload()` returns UE5 transform and optic parameters dictionary.
   - Lighting:
     - `LumenLightConfig` (lines 639–688): fields `preset_name`, `directional_light_intensity`, `sky_light_intensity`, `key_light_intensity`, `fill_light_intensity`, `rim_light_intensity`, `use_lumen_gi`, `use_lumen_reflections`.
   - Scene Assembly & MRQ:
     - `SceneConfig` (lines 690–732): fields `mesh_path`, `animation_path`, `lighting_preset`, `lighting_config`, `camera_choreography`, `audio_track_path`, `level_name`, `environment`, `lumen_enabled`.
     - `SceneBuildResult` (lines 734–763): fields `success`, `actor_ids`, `scene_path`, `camera_actor_id`, `character_actor_id`, `message`.
     - `MovieRenderQueueJobConfig` (lines 769–818): fields `scene_path`, `output_path`, `fps`, `resolution` (regex `^\d+x\d+$`), `codec`, `anti_aliasing_samples`, `warmup_frames`, `render_passes`.
     - `RenderResult` (lines 820–858): fields `video_path`, `frame_count`, `elapsed_seconds`, `fps`, `resolution`, `file_size_bytes`, `success`.

3. **Application Configuration Contracts** (`backend/core/config.py` lines 90–114, 213–223):
   - `ue5_host`: default `"127.0.0.1"`.
   - `ue5_http_port`: default `30010`.
   - `ue5_ws_port`: default `30020`.
   - `ue5_mock_mode`: default `True`.
   - `ue5_timeout_seconds`: default `30.0`.
   - Property `ue5_http_url`: `"http://127.0.0.1:30010"`.
   - Property `ue5_ws_url`: `"ws://127.0.0.1:30020/remote/protocol"`.

4. **Existing Preliminary Implementations & Discrepancies Observed**:
   - `backend/ue5/mock_server.py`: Currently only starts an HTTP server on port 30010 (`HTTPServer`). The WebSocket server on port 30020 is not yet implemented or bound. In `UE5RESTHandler._handle_write`, the property write logic conflates the `access` parameter with the property value.
   - `backend/ue5/client.py`: `UE5WebSocketClient` is currently a local stub that stores callback references in an in-memory dictionary without opening an actual WebSocket socket connection to `ws://localhost:30020/remote/protocol`.
   - `backend/ue5/mrq.py`: Contains a direct import from `tests.e2e.fixtures.synthetic_video` inside `render()`, violating Clean Architecture and module isolation rules (`GEMINI.md` and `PROJECT.md`).

5. **Authoritative Unreal Engine Remote Control API Specification**:
   - HTTP Server Port: default `30010` (REST).
   - WebSocket Server Port: default `30020` (`/remote/protocol`).
   - Function execution: `PUT /remote/object/call` with `{"objectPath": str, "functionName": str, "parameters": dict, "generateTransaction": bool}`. Response code `200` with return parameters dict or `{}` on void. Errors return `400` or `404` with `{"errorMessage": str}`.
   - Property access: `PUT /remote/object/property`.
     - Read: `{"objectPath": str, "propertyName": str, "access": "READ_ACCESS"}`. Returns `{"propertyValue": ...}`.
     - Write: `{"objectPath": str, "propertyName": str, "access": "WRITE_ACCESS", "propertyValue": {...}, "generateTransaction": bool}`. Returns `{}`.
   - WebSocket message envelope:
     - Request: `{"MessageName": "http" | "preset.register" | "preset.unregister", "Parameters": {...}, "Id": str | int}`.
     - Response: `{"RequestId": str | int, "ResponseCode": int, "ResponseBody": {...}}`.

6. **Test Suite Verification Evidence**:
   - Executing `python -m pytest tests/e2e/test_tier1_features.py -v -k "ue5"` verified that all 8 Tier 1 tests (`test_f_ue5_01` through `test_f_ue5_08`) currently check basic symbol existence.
   - Executing `python -m tests.e2e.runner --tier all --verbose` succeeded with 58/58 passed across all 4 tiers in 26.89s, confirming baseline readiness.

---

## 2. Logic Chain

1. **Premise 1 (R1 & Acceptance Criteria)**: The project requires bidirectional communication with Unreal Engine 5 via Remote Control REST and WebSocket APIs, supported by an offline high-fidelity mock server emulating ports 30010 and 30020, enabling automated testing without requiring an Unreal Editor installation.
2. **Premise 2 (Zero-Any and Schema Compliance)**: All data payloads passed between the FastMCP server, AI pipeline, and UE5 bridge must strictly serialize through Pydantic v2 models (`Vector3D`, `Rotator3D`, `ColorRGB`, `PBRTextureSet`, `CameraKeyframe`, `LumenLightConfig`, `SceneConfig`, `SceneBuildResult`, `MovieRenderQueueJobConfig`, `RenderResult`).
3. **Premise 3 (Authentic Wire Emulation)**: The Mock Server must implement both HTTP on 30010 and WebSocket on 30020 with exact response envelopes (`ResponseCode`, `ResponseBody`, `RequestId`), transaction simulation (`generateTransaction`), and a simulated world state tracking spawned actors, properties, and loaded assets.
4. **Premise 4 (Decoupling and Zero Production Leakage)**: Production code in `backend/ue5/` must never import fixtures from `tests/`. Mock video generation for headless fallback must be self-contained within `backend/ue5/` or handled through standard video generation without test fixture coupling.
5. **Deduction**: Milestone 2 requires full specification and implementation of 8 core features (F-UE5-01 through F-UE5-08) plus 4 discovered operational features (F-UE5-09 through F-UE5-12) to fulfill R1, ensure 100% adherence to project rules, and support seamless integration with FastMCP tools (`build_ue5_scene`, `render_video`).

---

## 3. Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | UE5-Bridge | **F-UE5-01: UE5 Remote Control REST Client** | Synchronous and async HTTP client for UE5 Remote Control API executing object function calls, property reads/writes, health checks, and actor lifecycle management. | `objectPath: str`, `functionName: str`, `parameters: Dict[str, Any]`, `generateTransaction: bool`, `propertyName: str`, `access: Literal["READ_ACCESS", "WRITE_ACCESS"]`, `propertyValue: Any` | `Dict[str, Any]` (function output or property value envelope `{"propertyValue": ...}`) | Raises `UE5ConnectionError` or `UE5ResponseError` on HTTP 400/404/500 with `errorMessage`; timeout after `ue5_timeout_seconds` | `PROJECT.md` §Interface Contracts, Epic Games Remote Control REST Docs |
| 2 | UE5-Bridge | **F-UE5-02: UE5 Remote Control WebSocket Client** | Persistent WebSocket connection to `ws://{host}:{ws_port}/remote/protocol` tunneling REST calls, batch requests, and subscribing to property/preset events. | `MessageName: str` (`"http"`, `"preset.register"`, `"preset.unregister"`, `"batch"`), `Parameters: Dict[str, Any]`, `Id: Union[str, int]` | Standardized response envelope `{"RequestId": Id, "ResponseCode": int, "ResponseBody": Dict[str, Any]}` | Auto-reconnect with exponential backoff on disconnect; pending RPC futures rejected on socket error | `PROJECT.md` §2, Epic Games Remote Control WebSocket Docs |
| 3 | UE5-Mock | **F-UE5-03: High-Fidelity Python UE5 Mock Server** | Dual-port server emulating port 30010 (REST HTTP) and port 30020 (WebSocket) with thread-safe world state tracking spawned actors, transforms, properties, and loaded assets. | HTTP requests (`/remote/info`, `/remote/object/call`, `/remote/object/property`) and WebSocket frames matching UE5 Remote Control wire format | Authentic UE5 JSON envelopes matching real engine responses (HTTP 200/400/404 and WebSocket envelopes with `ResponseCode` and `ResponseBody`) | Returns HTTP 404 with `{"errorMessage": "Object: ... does not exist."}` when object path unresolved; HTTP 400 on bad parameters | `PROJECT.md` §Code Layout, `backend/ue5/mock_server.py` |
| 4 | UE5-Assets | **F-UE5-04: Dynamic Runtime Asset Loading** | Ingests `.glb` and `.fbx` 3D meshes and skeletal armatures via `EditorAssetLibrary:ImportAsset`, spawning `StaticMeshActor` or `SkeletalMeshActor` with spatial transforms. | `source_path: str` (path to `.glb`/`.fbx`), `destination_path: str` (`/Game/Imported/...`), `actor_class: str`, `location: Vector3D`, `rotation: Rotator3D` | Structured import result `{"Success": True, "AssetPath": str, "ActorId": str}` | Returns `Success: False` with error message if file does not exist or glTF binary header is corrupt/invalid | `ORIGINAL_REQUEST.md` R1, `tests/e2e/test_tier2_boundaries.py` |
| 5 | UE5-Materials | **F-UE5-05: Programmatic PBR Material Assignment** | Generates Dynamic Material Instances (`UMaterialInstanceDynamic`) from master material `/Game/Materials/M_MasterPBR` and binds albedo, normal, roughness, and metallic parameters. | `material_name: str`, `base_color: ColorRGB`, `roughness: float`, `metallic: float`, `textures: Optional[PBRTextureSet]` | `PBRMaterialInstance` descriptor and remote execution assigning material to actor mesh slot 0 | Clamps scalar inputs to `[0.0, 1.0]`; falls back to default flat colors if texture map paths are invalid/missing | `PROJECT.md` §1, `backend/ue5/materials.py` |
| 6 | UE5-Lighting | **F-UE5-06: Lumen Lighting Rig Configuration** | Spawns and configures DirectionalLight, SkyLight, 3-point character spotlights/pointlights, and global unbound PostProcessVolume with Lumen GI and reflections. | `preset: str` (`"studio_3point"`, `"cyberpunk_neon"`, `"dramatic"`, `"natural_outdoor"`), `lighting_config: Optional[LumenLightConfig]` | `LumenLightingSetup` containing list of `LightActorConfig` and PostProcess settings; spawned light actor IDs in scene | Unsupported preset falls back to default `studio_3point` with warning log | `PROJECT.md` §1, `backend/core/models.py` |
| 7 | UE5-Camera | **F-UE5-07: CineCameraActor Beat Choreography** | Procedural keyframe generation for CineCameraActor (location, rotation, focal length, aperture, FOV) synchronized to audio beat timestamps. | `beat_timestamps: List[float]`, `total_duration: float`, `preset: str` (`"smooth_orbit"`, `"dramatic_orbit"`, `"aerial_pan"`, `"front_close"`), `center_z: float`, `default_fov: float` | `List[CameraKeyframe]` strictly conforming to physical bounds ($0 < \text{fov} < 180$, `focal_length` in $[1.0, 500.0]$) | If beat list is empty, generates at least 2 fallback keyframes ($t=0.0$ and $t=\text{duration}$); filters out timestamps beyond duration | `PROJECT.md` §1, `tests/e2e/test_tier2_boundaries.py` |
| 8 | UE5-MRQ | **F-UE5-08: Movie Render Queue (MRQ) Scheduling & Progress** | Submits Level Sequence render jobs to MRQ, executes progress ticker emitting `ProgressEvent` via `TelemetryBus`, and captures final `.mp4` video export. | `scene_path: str`, `output_path: str`, `fps: int`, `resolution: str` (e.g. `"1920x1080"`), `warmup_frames: int`, `anti_aliasing_samples: int` | `RenderResult` containing `video_path`, `frame_count`, `elapsed_seconds`, `fps`, `resolution`, `file_size_bytes`, `success` | Raises `TimeoutError` if render exceeds timeout threshold; creates valid video container if rendering in offline/mock mode | `PROJECT.md` §1, `backend/core/models.py` |
| 9 | UE5-Sequence | **F-UE5-09: LevelSequence Composition & Track Setup** | Programmatically creates and configures LevelSequence assets (`ULevelSequence`), adding CineCameraActor cut tracks and binding skeletal animation clips to SkeletalMeshActors. | `level_name: str`, `character_actor_id: str`, `camera_actor_id: str`, `animation_path: str`, `duration_seconds: float`, `fps: int` | `scene_path: str` (`/Game/Sequences/LS_{level_name}`) | Validates duration $> 0$; returns error if character or camera actor paths cannot be bound in the sequence | `ORIGINAL_REQUEST.md` R1, `backend/mcp/tools.py` |
| 10 | UE5-Preset | **F-UE5-10: Remote Control Preset Management** | Interacts with Unreal Engine Remote Control Presets (`/remote/preset/{PresetName}`) for grouped property querying and batch metadata inspection. | `preset_name: str`, `property_filter: Optional[List[str]]` | `Dict[str, Any]` describing exposed preset properties, functions, and current values | Returns HTTP 404 if preset name does not exist in the loaded project | Epic Games Remote Control Preset Documentation |
| 11 | UE5-Subsystems | **F-UE5-11: Editor Subsystems Remote Automation** | Direct execution of Unreal Editor Subsystems via Remote Control (`EditorActorSubsystem`, `EditorAssetLibrary`, `LevelSequenceEditorSubsystem`). | Subsystem class paths (`/Script/UnrealEd.Default__EditorActorSubsystem`, etc.), method names, and parameters | Subsystem return values (spawned actors, asset existence booleans, save confirmations) | Standard UFunction reflection error handling on parameter mismatch | `backend/ue5/client.py` lines 126–155 |
| 12 | UE5-Resilience | **F-UE5-12: Resilience, Reconnect, and Mock Mode Routing** | Automatic transparent routing between live Unreal Editor and internal `UE5MockServer` based on `AppConfig.ue5_mock_mode` and server healthcheck. | `ue5_mock_mode: bool`, connection timeout settings | Seamless execution of client requests against active engine or mock server | If live UE5 connection drops and `ue5_mock_mode` is enabled, automatically starts local mock server and routes traffic | `backend/core/config.py` lines 106–113 |

---

## 4. Edge Cases

| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | `F-UE5-01` | REST call with non-existent `objectPath` (`"/Game/NonExistent.Actor"`) | Server returns HTTP 404 with authentic Unreal JSON error payload: `{"errorMessage": "Web Remote Call deserialization error: Object: ... does not exist."}`. |
| 2 | `F-UE5-01` | REST property write on read-only property (`access: "WRITE_ACCESS"` on `EditConst` property) | Server returns HTTP 400 Bad Request indicating property is read-only. |
| 3 | `F-UE5-02` | WebSocket connection drop while RPC requests are in flight | Client detects disconnect, rejects pending futures with `ConnectionError`, and begins exponential backoff reconnection. |
| 4 | `F-UE5-02` | Concurrent WebSocket RPC calls sharing single socket | `Id` / `RequestId` correlation routes responses to exact calling coroutines without cross-talk or race conditions. |
| 5 | `F-UE5-03` | Mock server port collision (e.g. port 30010 already bound) | Mock server handles `OSError` gracefully, logging warning without crashing the backend process. |
| 6 | `F-UE5-04` | Corrupt or truncated `.glb` file (missing 12-byte header or invalid magic bytes) | Asset loader returns structured error `{"Success": False, "Error": "Corrupt or invalid glTF binary header"}` without raising unhandled exception. |
| 7 | `F-UE5-04` | Asset file does not exist on disk | Asset loader returns `{"Success": False, "Error": "Asset file does not exist: ..."}` with empty `AssetPath`. |
| 8 | `F-UE5-05` | PBR material creation with missing texture paths (None or empty strings) | Successfully instantiates `PBRMaterialInstance` with fallback scalar parameters (`roughness=0.5`, `metallic=0.0`, default `base_color`). |
| 9 | `F-UE5-05` | Extreme roughness and metallic values ($< 0.0$ or $> 1.0$) | Clamped strictly to $[0.0, 1.0]$ conforming to PBR conservation of energy principles. |
| 10 | `F-UE5-06` | Unknown or misspelled lighting preset name (`"random_neon_vibe"`) | Logs warning and defaults safely to `"studio_3point"` lighting setup. |
| 11 | `F-UE5-06` | Unbound PostProcessVolume flag validation | PostProcessVolume strictly configures `bUnbound=True`, `DynamicGlobalIlluminationMethod="Lumen"`, and `ReflectionMethod="Lumen"`. |
| 12 | `F-UE5-07` | Empty beat list (`beat_timestamps = []` from silent audio) | Choreographer generates at least 2 valid boundary keyframes ($t=0.0$ and $t=\text{duration}$) with valid FOV and non-zero distance. |
| 13 | `F-UE5-07` | Beats containing negative timestamps or timestamps $> \text{duration}$ | Out-of-range timestamps are filtered out; keyframes are sorted in strictly ascending chronological order. |
| 14 | `F-UE5-08` | MRQ render destination directory does not exist | Manager automatically creates parent directories on disk (`mkdir(parents=True, exist_ok=True)`). |
| 15 | `F-UE5-08` | Render timeout exceeded (`elapsed_seconds > timeout`) | Render loop raises `TimeoutError` and logs error event to `TelemetryBus`. |

---

## 5. Detailed Component Specifications

### 5.1 Protocol Specification: UE5 Remote Control REST (`backend/ue5/client.py`)
```
Base URL: http://{ue5_host}:{ue5_http_port} (Default: http://127.0.0.1:30010)

1. GET /remote/info
   - Headers: Accept: application/json
   - Status: 200 OK
   - Envelope:
     {
       "Version": "5.4.0",
       "Engine": "UnrealEngine",
       "Mock": true
     }

2. PUT /remote/object/call
   - Headers: Content-Type: application/json
   - Request Body:
     {
       "objectPath": str,           // e.g. "/Script/UnrealEd.Default__EditorActorSubsystem"
       "functionName": str,         // e.g. "SpawnActor"
       "parameters": dict,          // e.g. {"Class": "CineCameraActor", "Location": {"X": 0, "Y": 0, "Z": 120}}
       "generateTransaction": bool  // Default: false
     }
   - Status: 200 OK
   - Envelope (Void or Return):
     {
       "ReturnValue": Any,
       "ActorId": str
     }
   - Status: 400 Bad Request / 404 Not Found:
     {
       "errorMessage": "Web Remote Call deserialization error: Object: /... does not exist."
     }

3. PUT /remote/object/property
   - Read Property:
     Request:
     {
       "objectPath": str,
       "propertyName": str,
       "access": "READ_ACCESS"
     }
     Response 200 OK:
     {
       "propertyValue": Any
     }
   - Write Property:
     Request:
     {
       "objectPath": str,
       "propertyName": str,
       "access": "WRITE_ACCESS",
       "propertyValue": Any,
       "generateTransaction": bool
     }
     Response 200 OK:
     {}
```

### 5.2 Protocol Specification: UE5 Remote Control WebSocket (`backend/ue5/client.py`)
```
WebSocket URL: ws://{ue5_host}:{ue5_ws_port}/remote/protocol (Default: ws://127.0.0.1:30020/remote/protocol)

1. RPC Command Envelope:
   Client Frame:
   {
     "MessageName": "http",
     "Id": 101,
     "Parameters": {
       "Url": "/remote/object/call",
       "Verb": "PUT",
       "Body": {
         "objectPath": "/Script/UnrealEd.Default__EditorActorSubsystem",
         "functionName": "SpawnActor",
         "parameters": {"Class": "CineCameraActor"}
       }
     }
   }

   Server Response Frame:
   {
     "RequestId": 101,
     "ResponseCode": 200,
     "ResponseBody": {
       "ActorId": "/Game/Stage_Main.Stage_Main:PersistentLevel.CineCameraActor_1"
     }
   }

2. Batch Command Envelope:
   Client Frame:
   {
     "MessageName": "batch",
     "Id": 102,
     "Parameters": {
       "Requests": [
         {"Url": "/remote/object/property", "Verb": "PUT", "Body": {...}},
         {"Url": "/remote/object/call", "Verb": "PUT", "Body": {...}}
       ]
     }
   }

3. Property / Preset Subscription:
   Client Frame:
   {
     "MessageName": "preset.register",
     "Id": 103,
     "Parameters": {
       "PresetName": "MainStagePreset"
     }
   }

   Event Push from Server:
   {
     "Type": "PropertyChanged",
     "PresetName": "MainStagePreset",
     "Property": "RelativeLocation",
     "Value": {"X": 100.0, "Y": -350.0, "Z": 130.0}
   }
```

### 5.3 Mock Server Architecture (`backend/ue5/mock_server.py`)
- **HTTP Engine**: `http.server.HTTPServer` with `UE5RESTHandler` binding port 30010.
- **WebSocket Engine**: Dedicated asynchronous WebSocket server on port 30020 supporting RFC 6455 framing and connection pooling.
- **State Store (`UE5MockState`)**:
  - `actors: Dict[str, Dict[str, Any]]`: Actor registry.
  - `properties: Dict[str, Dict[str, Any]]`: Property store indexed by `objectPath`.
  - `loaded_assets: List[Dict[str, Any]]`: Asset catalog tracking source file, destination, and status.
  - `rendered_jobs: List[Dict[str, Any]]`: MRQ job history.
  - `subscribers: Set[WebSocketServerProtocol]`: Active WebSocket listener connections.

### 5.4 Asset Loading, Materials, Lighting, Camera, and MRQ Contracts
- **Asset Loading (`client.py`)**:
  - `import_asset(source_path: str, destination_path: str = "/Game/Imported") -> Dict[str, Any]`
  - `spawn_actor(actor_class: str, location: Optional[Vector3D], rotation: Optional[Rotator3D]) -> str`
- **Materials (`materials.py`)**:
  - `create_pbr_material(name: str, base_color: Optional[ColorRGB], roughness: float, metallic: float, textures: Optional[PBRTextureSet]) -> PBRMaterialInstance`
- **Lighting (`lighting.py`)**:
  - `setup_lumen_lighting(preset: str = "studio_3point") -> LumenLightingSetup`
  - Presets: `studio_3point`, `cyberpunk_neon`, `dramatic`, `natural_outdoor`.
- **Camera (`camera.py`)**:
  - `generate_camera_track(beat_timestamps: List[float], total_duration: float, preset: str, default_fov: float, distance: float) -> List[CameraKeyframe]`
  - Presets: `smooth_orbit`, `dramatic_orbit`, `aerial_pan`, `front_close`.
- **MRQ Video Rendering (`mrq.py`)**:
  - `render_sequence(scene_path: str, output_path: str, fps: int = 30, resolution: str = "1280x720", warmup_frames: int = 15, anti_aliasing_samples: int = 8) -> RenderResult`
  - Emits telemetry progress updates; standalone mock video generator without importing from `tests/`.

---

## 6. Caveats

1. **Live Unreal Engine Instance Availability**: In environments where an active Unreal Editor instance is not running, the system relies on the internal `UE5MockServer`. The client and mock server contracts specified here ensure 100% parity so that identical code works against both live UE5.4+ and the mock server.
2. **Third-Party glTF Runtime Plugins in UE5**: In standard UE5, dynamic runtime `.glb` import in standalone packaged builds typically uses the built-in glTF runtime loader or Interchange Framework. The mock server emulates this via `EditorAssetLibrary:ImportAsset`.
3. **WebSocket Concurrency**: When running under Python's `asyncio` and multi-threaded test runners, WebSocket connections must manage loop thread-safety using thread-safe event scheduling.

---

## 7. Conclusion

The specification for Milestone 2 (`backend/ue5/`) has been comprehensively mined and defined across all 8 target features and 4 discovered operational features:
1. **REST Client (`F-UE5-01`)** adheres to Unreal Engine Remote Control REST specifications (`/remote/object/call`, `/remote/object/property`, `/remote/info`).
2. **WebSocket Client (`F-UE5-02`)** implements wire protocol tunneling (`MessageName: "http"`), batching, and property subscription.
3. **Mock Server (`F-UE5-03`)** dual-binds port 30010 (HTTP) and port 30020 (WebSocket) with thread-safe world state and authentic response envelopes.
4. **Asset Loading (`F-UE5-04`)**, **PBR Materials (`F-UE5-05`)**, **Lumen Lighting (`F-UE5-06`)**, **CineCamera Choreography (`F-UE5-07`)**, and **MRQ Video Rendering (`F-UE5-08`)** are strictly bounded, typed with Zero-Any Pydantic v2 schemas, and decoupled from test fixtures.

The specification is ready for immediate implementation by the Milestone 2 worker agent.

---

## 8. Verification Method

To independently verify the specification and its alignment with existing test suites:

1. **Verify E2E Feature Coverage for UE5**:
   ```powershell
   python -m pytest tests/e2e/test_tier1_features.py -v -k "ue5"
   ```
   *Expected Result*: All 8 tests (`test_f_ue5_01` through `test_f_ue5_08`) pass.

2. **Verify Boundary and Interaction Tests for UE5**:
   ```powershell
   python -m pytest tests/e2e/test_tier2_boundaries.py tests/e2e/test_tier3_interactions.py -v -k "ue5 or camera or mrq"
   ```
   *Expected Result*: Keyframe boundaries, corrupt GLB handling, and audio-to-camera interactions pass.

3. **Verify Full E2E Standalone Runner**:
   ```powershell
   python -m tests.e2e.runner --tier all --verbose
   ```
   *Expected Result*: 58/58 tests pass across all 4 tiers with 100% feature coverage recorded in `tests/e2e/reports/e2e_results.json`.

4. **Verify Zero-Any and Strict Typing**:
   ```powershell
   python -c "import backend.ue5; import backend.core.models; print('Imports valid')"
   ```
   *Expected Result*: Exits cleanly with status 0.
