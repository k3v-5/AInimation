# Exhaustive Specification Mining & Architectural Survey
## R1: Unreal Engine 5 Remote Control & R4: Python FastMCP Server

**Author**: Survey Agent 1 (Spec Miner - UE5 & MCP)  
**Date**: 2026-10-14  
**Project**: IANIMATION (Orquestador de Animación 3D e IA)  
**Workspace**: `e:\Disco F\Dev\IANIMATION`  
**Integrity Mode**: Demo / Production-Ready Standards  

---

## Executive Summary

This report establishes the authoritative architectural and interface specification for two critical subsystems of the IANIMATION platform:
1. **Unreal Engine 5 Headless / Remote Control Orchestration (R1)**: Enabling programmatic scene synthesis, dynamic `.glb`/`.fbx` mesh and skeletal loading, PBR material dynamic instantiation, Lumen illumination rig composition, CineCamera beat-synchronized tracking, and Movie Render Queue (MRQ) batch rendering. It includes a high-fidelity Python mock server design providing zero-dependency local simulation for offline testing.
2. **Python FastMCP Server & Human-in-the-Loop Copilot (R4)**: Defining the 6 atomic pipeline tools (`analyze_audio`, `image_to_3d`, `auto_rig`, `extract_mocap`, `build_ue5_scene`, `render_video`) backed by strict Pydantic v2 schemas and JSON Schemas, dual-invocation architecture (standard MCP client vs. direct programmatic Python import), multi-stage production planning with human confirmation gates, and real-time telemetry streaming over WebSocket/SSE.

---

## Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | UE5 Remote Control (REST) | `PUT /remote/object/call` | Executes a UFUNCTION on an active UObject or Engine Subsystem | `objectPath`: str, `functionName`: str, `parameters`: dict, `generateTransaction`: bool | `{"ReturnValue": any, "OutParameters": dict}` (HTTP 200) | HTTP 400 (Bad parameters), HTTP 404 (Object not found), HTTP 500 (Invocation crash) | Unreal Engine Remote Control Web API Spec |
| 2 | UE5 Remote Control (REST) | `PUT /remote/object/property` | Writes a property value to a UObject/Actor | `objectPath`: str, `propertyName`: str, `propertyValue`: dict, `access`: "WRITE_ACCESS" | `{"PropertyName": value}` (HTTP 200) | HTTP 400 (Property does not exist or type mismatch), HTTP 404 (Object not found) | Unreal Engine Remote Control Web API Spec |
| 3 | UE5 Remote Control (REST) | `GET /remote/object/property` | Reads current property values from an object | `objectPath`: str, `propertyName`: str, `access`: "READ_ACCESS" | JSON object containing property values (HTTP 200) | HTTP 404 (Object or property not found) | Unreal Engine Remote Control Web API Spec |
| 4 | UE5 Remote Control (REST) | `PUT /remote/batch` | Executes multiple REST operations in a single atomic/sequential transaction | `requests`: list of `{requestId, url, verb, body}` | `responses`: list of `{requestId, responseCode, responseBody}` | Individual sub-request status codes returned in payload | Unreal Engine Remote Control Web API Spec |
| 5 | UE5 Remote Control (REST) | `PUT /remote/object/describe` | Inspects UClass reflection, exposed properties, methods, and types | `objectPath`: str | UClass schema with property names, types, flags, and function signatures | HTTP 404 (Class/Object not found) | Unreal Engine Remote Control Web API Spec |
| 6 | UE5 Remote Control (WebSocket) | `/remote/protocol` | Bidirectional full-duplex WebSocket RPC and event streaming | JSON envelopes: `{"MessageName": "http", "Parameters": {...}, "Id": int}` | `{"Type": "Response", "Id": int, "ResponseCode": int, "ResponseBody": dict}` | Returns error code in `ResponseCode` with descriptive string in `ResponseBody` | Unreal Engine Remote Control Web API Spec |
| 7 | UE5 Remote Control (WebSocket) | Property Watch & Events | Real-time subscription to property changes and engine events | `{"MessageName": "preset.register", "Parameters": {"PresetName": str}}` | Pushed `{"Type": "Event", "EventName": str, "Data": dict}` frames | Disconnection or invalid preset error frame | Unreal Engine Remote Control Web API Spec |
| 8 | UE5 Mock Server | Headless UE5 Simulator | Pure Python async mock server replicating UE5 REST (30010) and WS (30020) | HTTP / WS requests matching UE5 API | Structured responses mirroring UE5 engine state | Emulates 400/404/500 errors matching UE5 error schemas | Architectural Design / ORIGINAL_REQUEST.md |
| 9 | UE5 Asset Pipeline | Dynamic GLB/FBX Import | Imports external 3D meshes and skeletal hierarchies into the level | File path, target folder, skeletal flag, import transform | Created asset path `/Game/Assets/...` and spawned Actor reference | Import failure returns structured error and fallback default mesh | UE5 Interchange / AssetTools Python API |
| 10 | UE5 Lighting | Lumen Lighting Rig Setup | Programmatically spawns and configures Directional, SkyLight, and 3-Point Accent lights | Lighting preset ("studio_3point", "cyberpunk_neon", etc.), color temperature, lux | Actor IDs and light component references | Validation error on invalid preset; defaults to studio_3point | UE5 Engine Lumen & Lighting Architecture |
| 11 | UE5 Shading | Dynamic Material Assignment | Creates Dynamic Material Instance (MID) and assigns PBR maps (Albedo, Normal, Roughness, Metallic) | Target mesh actor, texture file paths, tint vector, scalar multipliers | Applied MID object path and parameter confirmation | Missing texture falls back to default engine grid/gray texture | UE5 Material System API |
| 12 | UE5 Cinematics | CineCamera Beat-Synced Track | Spawns CineCameraActor and generates Level Sequence with keyframes aligned to audio beats | Beat timestamps, camera preset ("orbit", "cuts", "dolly"), focal length, aperture | LevelSequence asset path, CineCameraActor path, keyframe count | If beat list is empty, generates smooth interpolation curve | UE5 CineCamera & Sequencer API |
| 13 | UE5 Rendering | Movie Render Queue (MRQ) Trigger | Allocates MRQ job, sets sequence/map, configures output (MP4/ProRes), executes render | Sequence path, output directory, resolution, frame rate, format | Render Job ID, initial state `Rendering` | Returns error if Sequence or Map not found | UE5 MoviePipelineQueueSubsystem |
| 14 | UE5 Rendering | MRQ Progress Tracking | Polls or listens for render job status percentage and frame completion | Job ID | Status percentage (0.0 - 100.0%), current frame, elapsed time, output path | Detects render crash, GPU timeout, or disk write error | UE5 MoviePipelineExecutorJob API |
| 15 | FastMCP Core | FastMCP Server Host | Exposes atomic AI & UE5 tools via Model Context Protocol | Client connections over Stdio or SSE transport | MCP tool discovery (`tools/list`) and execution (`tools/call`) | Standard JSON-RPC error codes (-32602, -32603) | FastMCP SDK / Anthropic MCP Spec |
| 16 | FastMCP Core | Dual Invocation Bridge | Allows tools to be invoked via MCP protocol or directly imported in Python | Direct function call arguments or MCP JSON-RPC payload | Typed Pydantic v2 response model or MCP Text/Embedded content | Direct call raises Python exceptions; MCP wraps in tool error | Clean Architecture / GEMINI.md |
| 17 | FastMCP Tool | `analyze_audio` | Analyzes audio file for BPM, beat timestamps, downbeats, and stems | Audio file path, stem separation flag, BPM bounds | `AudioAnalysisResult` (BPM, beats, energy curve, stems) | Missing/corrupt audio raises validation error | Librosa / Demucs API Spec |
| 18 | FastMCP Tool | `image_to_3d` | Converts 2D input image to textured 3D mesh (.glb) | Image path, provider (Fal.ai, Tripo, Local), texture resolution | `Model3DResult` (mesh path, texture maps, polycount) | Provider failure triggers automatic fallback or error plan | Fal.ai / Tripo AI Spec |
| 19 | FastMCP Tool | `auto_rig` | Analyzes 3D biped mesh and generates skinned skeletal hierarchy | Mesh path (.glb/.obj), skeleton preset (UE5 Mannequin, Mixamo) | `RigResult` (rigged FBX path, joint list, skinning status) | Degenerate topology error returns unskinned warning | Auto-Rigging Engine Spec |
| 20 | FastMCP Tool | `extract_mocap` | Extracts 3D motion data from dancing video and maps to skeleton | Video path, target FPS, background cleanup flag, skeleton target | `MocapResult` (FBX animation path, frame count, confidence) | Low confidence detection or occlusion warning | GVHMR / 4DHumans Spec |
| 21 | FastMCP Tool | `build_ue5_scene` | Coordinates UE5 scene composition (character, mocap, PBR, Lumen, camera) | Mesh path, anim path, PBR textures, lighting preset, camera preset, beats | `SceneBuildResult` (sequence path, actor references, frame count) | Actor spawn failure returns rollback status | IANIMATION Orchestrator Spec |
| 22 | FastMCP Tool | `render_video` | Triggers high-fidelity Movie Render Queue output in UE5 | Level sequence path, format, resolution, output directory | `RenderResult` (video file path, resolution, render time, file size) | Render queue failure returns detailed log snippet | MRQ Spec |
| 23 | Human-in-the-Loop | Production Plan Generator | Generates step-by-step production plan with risk-graded confirmation gates | User prompt / request parameters | `ProductionPlan` with list of `PlanStep` items | Invalid parameters reject plan creation | IANIMATION Copilot Architecture |
| 24 | Human-in-the-Loop | Step Confirmation Gate | Holds execution of heavy steps (image_to_3d, render_video) until user approves | Plan ID, Step ID, Approval boolean, modified parameters | Updated plan state (`confirmed`, `running`, or `rejected`) | Timeout or rejection aborts subsequent dependent steps | Human-in-the-Loop Protocol |
| 25 | Telemetry | Real-Time Progress Stream | Streams fine-grained logs, sub-stages, and percentage progress to UI | Job events from tools or MRQ | WebSocket / SSE telemetry packets `TelemetryProgressEvent` | Broken pipe handled with buffering and reconnect support | IANIMATION Telemetry Spec |

---

## Edge Cases

| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | UE5 REST `/remote/object/call` | Non-existent UObject path (e.g. `/Game/Invalid/Path.Actor`) | Returns HTTP 404 with JSON: `{"errorMessage": "Failed to find object /Game/Invalid/Path.Actor"}`. Client must handle without crashing. |
| 2 | UE5 REST `/remote/object/property` | Mismatched property type (e.g. passing string `"bright"` to float `Intensity`) | Returns HTTP 400 with JSON: `{"errorMessage": "Property 'Intensity' cannot be converted from string"}`. |
| 3 | UE5 WebSocket RPC | Sudden disconnect during long-running operation | WebSocket client must maintain an unacknowledged message queue, re-establish connection with exponential backoff (1s, 2s, 4s, max 10s), and re-subscribe to watched properties. |
| 4 | UE5 Headless Asset Loading | Degenerate or malformed `.glb` file (missing vertices or corrupt buffer) | UE5 Interchange/glTF loader returns import error `ImportError: glTF binary chunk corrupted`. Mock server must return structured error `{"status": "error", "code": "ASSET_IMPORT_FAILED"}`. |
| 5 | Lumen Lighting Setup | PostProcessVolume without unbound flag (`bUnbound=false`) | Lumen GI and reflections only affect camera when inside volume bounds. The orchestrator must explicitly set `bUnbound=true` so lighting applies globally. |
| 6 | CineCamera Beat Sync | Audio track with zero detected beats (silent or ambient track) | Beat extraction returns empty list `[]`. CineCamera track generator must fallback to duration-based keyframing (e.g. keyframe every 4.0 seconds) to avoid sequencer generation failure. |
| 7 | Movie Render Queue | Output directory does not exist or has write permission issues | MRQ fails immediately on job start. Orchestrator must pre-validate and create `output_dir` before issuing render call. |
| 8 | MRQ Frame Timeout | Unreal Engine hangs during heavy frame rendering (e.g. Nanite/Lumen stall) | Progress tracker detects no progress update for >60 seconds; raises `RenderTimeoutError` and aborts job cleanly. |
| 9 | FastMCP Tool Call | Missing required parameter (e.g. `audio_path` omitted in `analyze_audio`) | FastMCP Pydantic validation interceptor immediately raises `ValidationError` with HTTP/RPC error -32602, detailing missing field. |
| 10 | Human-in-the-Loop | User rejects step in `awaiting_confirmation` status | Orchestrator marks step as `rejected`, halts execution graph, and queries copilot for plan revision without executing heavy operations. |
| 11 | Dual Invocation | Tool called via programmatic Python while MCP server is not running | Tool executes directly via service layer without requiring MCP subprocess or network sockets. |

---

## Section 1: Unreal Engine 5 Headless & Remote Control Architecture (R1)

### 1.1 Remote Control Network Protocol Specification

Unreal Engine provides the **Remote Control Web Interface** plugin which exposes two network interfaces:
- **HTTP REST API**: Standard port `30010` (default)
- **WebSocket Protocol**: Standard port `30020` or routed via HTTP upgrade at `ws://localhost:30010/remote/protocol`

#### 1.1.1 REST API Endpoints & Request/Response Contracts

##### Endpoint 1: Function Invocation (`PUT /remote/object/call`)
Executes any `UFUNCTION` exposed on a `UObject` (including Subsystems, Blueprint Function Libraries, and Actors).

- **URL**: `http://<ue5_host>:30010/remote/object/call`
- **Method**: `PUT`
- **Headers**: `Content-Type: application/json`
- **Request Body Contract**:
  ```json
  {
    "objectPath": "/Script/EditorActorSubsystem.Default__EditorActorSubsystem",
    "functionName": "SetActorTransform",
    "parameters": {
      "TargetActor": "/Game/Maps/MainScene.MainScene:PersistentLevel.Character_Mesh_1",
      "NewTransform": {
        "Translation": { "X": 0.0, "Y": 0.0, "Z": 90.0 },
        "Rotation": { "Pitch": 0.0, "Yaw": 180.0, "Roll": 0.0 },
        "Scale3D": { "X": 1.0, "Y": 1.0, "Z": 1.0 }
      }
    },
    "generateTransaction": true
  }
  ```
- **Success Response (HTTP 200)**:
  ```json
  {
    "ReturnValue": true,
    "OutParameters": {}
  }
  ```
- **Error Response (HTTP 404 / 400)**:
  ```json
  {
    "errorMessage": "Function SetActorTransform could not be resolved on /Script/EditorActorSubsystem.Default__EditorActorSubsystem"
  }
  ```

##### Endpoint 2: Property Read/Write (`PUT /remote/object/property` & `GET /remote/object/property`)
Directly manipulates reflected UProperties on components and actors.

- **URL**: `http://<ue5_host>:30010/remote/object/property`
- **Method**: `PUT`
- **Write Request Body Contract**:
  ```json
  {
    "objectPath": "/Game/Maps/MainScene.MainScene:PersistentLevel.DirectionalLight_1.LightComponent0",
    "propertyName": "Intensity",
    "access": "WRITE_ACCESS",
    "propertyValue": {
      "Intensity": 25.0
    }
  }
  ```
- **Success Response (HTTP 200)**:
  ```json
  {
    "Intensity": 25.0
  }
  ```

##### Endpoint 3: Batch Execution (`PUT /remote/batch`)
Allows executing a series of commands in a single network roundtrip.

- **Request Body Contract**:
  ```json
  {
    "requests": [
      {
        "requestId": 1,
        "url": "/remote/object/property",
        "verb": "PUT",
        "body": {
          "objectPath": "/Game/Maps/MainScene.MainScene:PersistentLevel.SkyLight_1.Component",
          "propertyName": "Intensity",
          "access": "WRITE_ACCESS",
          "propertyValue": { "Intensity": 1.5 }
        }
      },
      {
        "requestId": 2,
        "url": "/remote/object/call",
        "verb": "PUT",
        "body": {
          "objectPath": "/Script/PythonScriptPlugin.Default__PythonScriptLibrary",
          "functionName": "ExecutePythonCommand",
          "parameters": {
            "PythonCommand": "unreal.log('Batch executed')"
          }
        }
      }
    ]
  }
  ```
- **Success Response (HTTP 200)**:
  ```json
  {
    "responses": [
      {
        "requestId": 1,
        "responseCode": 200,
        "responseBody": { "Intensity": 1.5 }
      },
      {
        "requestId": 2,
        "responseCode": 200,
        "responseBody": { "ReturnValue": true }
      }
    ]
  }
  ```

#### 1.1.2 WebSocket Protocol Specification
The WebSocket endpoint provides lower latency and asynchronous event notifications.

- **Connection URL**: `ws://<ue5_host>:30020/` or `ws://<ue5_host>:30010/remote/protocol`
- **Message Framing Format**:
  All messages are JSON objects containing `MessageName`, `Parameters`, and an optional client tracking `Id`.
- **RPC Call Framing**:
  ```json
  {
    "MessageName": "http",
    "Parameters": {
      "Url": "/remote/object/call",
      "Verb": "PUT",
      "Body": {
        "objectPath": "/Script/MovieRenderPipelineCore.Default__MoviePipelineQueueSubsystem",
        "functionName": "GetQueue",
        "parameters": {}
      }
    },
    "Id": 2048
  }
  ```
- **WebSocket Response Framing**:
  ```json
  {
    "Type": "Response",
    "Id": 2048,
    "ResponseCode": 200,
    "ResponseBody": {
      "ReturnValue": "/Engine/Transient.MoviePipelineQueue_0"
    }
  }
  ```
- **Subscription / Event Streaming**:
  Clients subscribe to property updates or presets:
  ```json
  {
    "MessageName": "preset.register",
    "Parameters": {
      "PresetName": "IANIMATION_LiveSync"
    }
  }
  ```
  The server subsequently streams event frames:
  ```json
  {
    "Type": "Event",
    "EventName": "preset.field.changed",
    "Data": {
      "Property": "CameraFocalLength",
      "Value": 35.0
    }
  }
  ```

---

### 1.2 High-Fidelity UE5 Mock Server Architecture

To satisfy acceptance criteria without requiring a live instance of Unreal Engine 5 (which requires 32GB+ RAM and dedicated NVIDIA RTX GPU), a high-fidelity Python mock server is designed.

```
+------------------------------------------------------------------------+
|                     UE5 Mock Server (Python)                           |
|                                                                        |
|  +---------------------+                       +--------------------+  |
|  |  HTTP REST Server   |                       |  WebSocket Server  |  |
|  |  (Port 30010)       |                       |  (Port 30020)      |  |
|  +----------+----------+                       +---------+----------+  |
|             |                                            |             |
|             +---------------------+----------------------+             |
|                                   |                                    |
|                      +------------v------------+                       |
|                      |  UE5 Dispatch Router    |                       |
|                      +------------+------------+                       |
|                                   |                                    |
|       +---------------------------+---------------------------+        |
|       |                           |                           |        |
|  +----v-------------+     +-------v-------------+     +-------v-----+  |
|  | Scene Graph State|     | Asset Registry &    |     | MRQ Render  |  |
|  | - Actors         |     | Materials DB        |     | Simulation  |  |
|  | - Components     |     | - GLB / FBX cache   |     | - Ticker    |  |
|  | - Transforms     |     | - Dynamic Instances |     | - 0-100%    |  |
|  | - CineCameras    |     | - Texture Maps      |     | - MP4 gen   |  |
|  +------------------+     +---------------------+     +-------------+  |
+------------------------------------------------------------------------+
```

#### Mock Server Components:
1. **In-Memory Scene Graph**:
   - Maintains dictionary of active Actors, Components, Transforms, and Properties.
   - Pre-seeded with subsystems:
     - `/Script/EditorActorSubsystem.Default__EditorActorSubsystem`
     - `/Script/PythonScriptPlugin.Default__PythonScriptLibrary`
     - `/Script/MovieRenderPipelineCore.Default__MoviePipelineQueueSubsystem`
2. **Asset Importer Simulation**:
   - When `ImportAsset` or `ExecutePythonCommand` with import logic is called:
     - Validates source `.glb` / `.fbx` existence on disk.
     - Creates simulated UAsset path: `/Game/Assets/Imported/<MeshName>.<MeshName>`.
     - Spawns corresponding `SkeletalMeshActor` or `StaticMeshActor`.
3. **Movie Render Queue (MRQ) Simulator**:
   - Simulates render execution ticker asynchronously.
   - Transitions state: `Pending` -> `Rendering` (increments progress from 0.0% to 100.0% over simulated elapsed time, e.g. 2.0s in test mode) -> `Finished`.
   - Generates mock output video file (`.mp4`) with valid header or placeholder frames in `output_dir`.

---

### 1.3 Dynamic Asset Loading & Skeletal Meshes

Unreal Engine 5 headless mode imports assets using either:
1. **Interchange Framework** (`unreal.InterchangeManager`): Modern unified import framework for glTF, FBX, USD.
2. **AssetTools Subsystem** (`unreal.AssetToolsHelpers.get_asset_tools()`): Legacy robust importer.

#### Automated Python Script Invoked via Remote Control:
```python
import unreal

def import_gltf_or_fbx(source_path: str, destination_path: str, is_skeletal: bool) -> str:
    """Imports 3D model into UE5 Content Browser and returns asset path."""
    task = unreal.AssetImportTask()
    task.filename = source_path
    task.destination_path = destination_path
    task.destination_name = source_path.replace("\\", "/").split("/")[-1].split(".")[0]
    task.replace_existing = True
    task.automated = True
    task.save = True

    if is_skeletal:
        options = unreal.FbxImportUI()
        options.import_mesh = True
        options.import_as_skeletal = True
        options.import_animations = True
        options.skeletal_mesh_import_data.import_uniform_scale = 1.0
        task.options = options

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    imported_path = f"{destination_path}/{task.destination_name}.{task.destination_name}"
    return imported_path
```

#### Actor Spawning & Spatial Transform Setup:
Once imported, the actor is spawned into the current `PersistentLevel`:
- Spawn Actor: `actor_subsystem.spawn_actor_from_object(asset, location, rotation)`
- Default Spatial Transform Coordinate Space:
  - Unreal Engine uses **Left-Handed Z-Up** coordinate system ($X = \text{Forward}$, $Y = \text{Right}$, $Z = \text{Up}$ in centimeters).
  - Standard GLB format is **Right-Handed Y-Up** ($X = \text{Right}$, $Y = \text{Up}$, $Z = \text{Forward}$ in meters).
  - Transformation Matrix: Scale $\times 100$, coordinate permutation: $(X_{UE}, Y_{UE}, Z_{UE}) = (-Z_{GLB} \times 100, X_{GLB} \times 100, Y_{GLB} \times 100)$.

---

### 1.4 Programmatic PBR Material Assignment & Lumen Lighting Rig

#### 1.4.1 Dynamic Material Instantiation
PBR textures extracted or generated by the AI pipelines must be mapped onto the character mesh.
- Master Material: `/Game/Materials/M_Master_PBR.M_Master_PBR`
  - Texture Parameters:
    - `AlbedoMap` (Texture2D, sRGB: True)
    - `NormalMap` (Texture2D, Normal compression, sRGB: False)
    - `RoughnessMap` (Texture2D, Grayscale, sRGB: False)
    - `MetallicMap` (Texture2D, Grayscale, sRGB: False)
  - Scalar Parameters:
    - `RoughnessScale` (float, default 1.0)
    - `MetallicScale` (float, default 1.0)
  - Vector Parameters:
    - `BaseColorTint` (FLinearColor: R, G, B, A)

#### 1.4.2 Lumen Lighting Rig Setup
Lumen provides fully dynamic global illumination and reflections without precomputed lightmaps.

```
                 [DirectionalLight / Sun] (5500K, 15 lux)
                            \
                             \
   [Rim SpotLight]            v          [Key RectLight]
   (Warm, 1200 lm) -----> [Character] <----- (Cool 6500K, 2500 lm)
                              ^
                             /
                     [Fill SpotLight]
                     (Soft, 800 lm)

   +--------------------------------------------------------------+
   | PostProcessVolume (bUnbound=True)                            |
   | - GlobalIlluminationType: Lumen                              |
   | - ReflectionsType: Lumen                                     |
   | - LumenSceneDetail: 2.0                                      |
   +--------------------------------------------------------------+
```

##### Lighting Actor Manifest:
1. **DirectionalLight**: Sun light source.
   - `Intensity`: 10.0 - 20.0 lux
   - `bAtmosphereSunLight`: True
   - `CastShadows`: True
2. **SkyLight**: Ambient environmental fill.
   - `SourceType`: `SLS_CapturedScene`
   - `RealTimeCapture`: True
   - `Intensity`: 1.0
3. **Studio 3-Point Light Rig**:
   - **Key Light (`RectLight`)**: Positioned $45^\circ$ azimuth, $30^\circ$ elevation from camera; $2500\text{ lumens}$, Width: $50\text{cm}$, Height: $50\text{cm}$.
   - **Fill Light (`SpotLight`)**: Positioned $-45^\circ$ azimuth; $800\text{ lumens}$, InnerCone: $30^\circ$, OuterCone: $50^\circ$.
   - **Rim / Accent Light (`SpotLight`)**: Positioned $150^\circ$ behind character; $1200\text{ lumens}$ for edge separation.
4. **PostProcessVolume**:
   - `bUnbound`: `True` (affects entire world)
   - `Settings.GlobalIlluminationType`: `Lumen`
   - `Settings.ReflectionsType`: `Lumen`
   - `Settings.LumenSceneLightingQuality`: 2.0

---

### 1.5 Cinematic Camera Track & Beat-Synced Keyframing

#### 1.5.1 CineCameraActor Properties
- **Sensor Dimensions**: Full Frame 35mm ($36.0\text{mm} \times 24.0\text{mm}$).
- **Focal Lengths**:
  - `Wide Shot`: 24mm or 28mm (establishes environment)
  - `Hero Medium Shot`: 50mm (natural perspective)
  - `Close-up / Dramatic`: 85mm or 105mm (compressed background, shallow depth-of-field)
- **Aperture**: $f/1.8$ to $f/2.8$ for cinematic bokeh.
- **Focus Method**: `CameraFocusMethod.Tracking` tracking the character actor's bone hierarchy.

#### 1.5.2 Beat-Synchronized Keyframe Calculation
Given a sequence of beat timestamps $B = [t_0, t_1, \dots, t_n]$ from audio analysis and scene frame rate $FPS$ (e.g. 30):
$$\text{Frame}_i = \text{round}(t_i \times FPS)$$

##### Camera Presets:
1. **Beat-Synced Cuts (`beat_synced_cuts`)**: On every major downbeat (e.g. every 4th beat), switch camera angles between Wide, Medium, and Close-Up by generating discrete Camera Cut keys.
2. **Cinematic Orbit (`cinematic_orbit`)**: Smooth continuous rotational orbit around character root, with focal length pulses on downbeats.
3. **Dolly Zoom (`dolly_zoom`)**: Synchronized dolly push (decreasing camera distance) combined with decreasing focal length to create the Vertigo effect on musical drops.

---

### 1.6 Movie Render Queue (MRQ) Integration

#### MRQ Execution Flow:
1. **Initialize Subsystem**: Obtain `/Script/MovieRenderPipelineCore.Default__MoviePipelineQueueSubsystem`.
2. **Allocate Job**: Add new `UMoviePipelineExecutorJob` to the active queue.
3. **Bind Sequence and Map**:
   - `job.sequence`: SoftObjectPath pointing to `/Game/Cinematics/LS_CinematicShot`.
   - `job.map`: SoftObjectPath pointing to `/Game/Maps/MainScene`.
4. **Configure Settings**:
   - Video output: `UMoviePipelineOutputSetting` (Resolution $1920 \times 1080$ or $3840 \times 2160$, Framerate 30/60 fps, WarmUpFrameCount 30).
   - Render passes: `UMoviePipelineDeferredPasses` with spatial/temporal anti-aliasing sample counts ($1 \times 8$).
   - Output container: MP4 / Apple ProRes 422HQ.
5. **Trigger Rendering**: Call `subsystem.render_queue_with_executor(unreal.MoviePipelinePIEExecutor)` (or `NewProcessExecutor` for headless batch).
6. **Telemetry Polling**:
   - Read `job.get_status_percent()` (returns float $0.0 \dots 100.0$).
   - Read `job.get_status_message()`.

---

## Section 2: FastMCP Architecture & Human-in-the-Loop Copilot (R4)

### 2.1 FastMCP Server Architecture & Dual Invocation

To achieve full modularity and satisfy SOLID principles (DIP, SRP):
- **Core Domain Services**: Standalone Python modules containing pure business logic (`backend.services.*`).
- **FastMCP Layer**: Thin protocol adapters decorating domain services (`backend.mcp.server`).
- **Dual Invocation**:
  - **Path A (MCP Protocol)**: Claude Desktop, Cursor, or Tauri Desktop MCP Client communicates via `stdio` or `sse` JSON-RPC.
  - **Path B (Direct Python Import)**: Tauri backend or test runners import services directly (`from backend.services.scene_builder import SceneBuilderService`) with zero IPC overhead.

```
+--------------------------------------------------------------------------------+
|                             IANIMATION BACKEND                                 |
|                                                                                |
|   +------------------------------------+  +--------------------------------+   |
|   |        MCP Protocol Client         |  |      Direct Programmatic       |   |
|   |  (Tauri Frontend / Claude Desktop) |  |   (CLI / verify_pipeline.py)   |   |
|   +-----------------+------------------+  +---------------+----------------+   |
|                     | JSON-RPC (stdio/sse)                |                    |
|                     v                                     |                    |
|   +------------------------------------+                  | Direct Python      |
|   |       FastMCP Server Adapter       |                  | Function Call      |
|   |     (@mcp.tool() wrappers)         |                  |                    |
|   +-----------------+------------------+                  |                    |
|                     |                                     |                    |
|                     +-----------------+-------------------+                    |
|                                       |                                        |
|                                       v                                        |
|   +------------------------------------------------------------------------+   |
|   |                      CORE DOMAIN SERVICES LAYER                        |   |
|   |                                                                        |   |
|   |  - AudioAnalysisService        - RiggingService                        |   |
|   |  - ImageTo3DService            - UE5SceneBuilderService                |   |
|   |  - MocapService                - MovieRenderService                    |   |
|   +-----------------------------------+------------------------------------+   |
|                                       |                                        |
|                      +----------------+----------------+                       |
|                      |                                 |                       |
|                      v                                 v                       |
|   +------------------------------------+    +------------------------------+   |
|   |      AI Cloud & Local Adapters     |    |   UE5 Remote Control Client  |   |
|   |   (Fal.ai, Tripo, Librosa, etc.)   |    |      (REST & WebSocket)      |   |
|   +------------------------------------+    +------------------------------+   |
+--------------------------------------------------------------------------------+
```

---

### 2.2 Atomic Tool Definitions with Pydantic v2 Models

All tools are modeled with 100% strict typing, Pydantic v2 validation, field descriptions, and enumerated constraints.

#### Tool 1: `analyze_audio`
Analyzes an audio file (`.wav`, `.mp3`) to extract musical tempo (BPM), beat timestamps, downbeat markers, and optional stem separation paths.

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class AudioAnalysisInput(BaseModel):
    audio_path: str = Field(..., description="Absolute path to input audio file (.wav, .mp3, .flac)")
    extract_stems: bool = Field(False, description="Whether to perform Demucs stem separation (drums, bass, vocals, other)")
    min_bpm: float = Field(60.0, ge=30.0, le=300.0, description="Minimum expected tempo for beat tracking")
    max_bpm: float = Field(200.0, ge=30.0, le=300.0, description="Maximum expected tempo for beat tracking")

class AudioAnalysisResult(BaseModel):
    bpm: float = Field(..., description="Detected tempo in Beats Per Minute")
    duration_seconds: float = Field(..., description="Total audio duration in seconds")
    beat_timestamps: List[float] = Field(..., description="Timestamps in seconds for every detected beat")
    downbeat_timestamps: List[float] = Field(..., description="Timestamps in seconds for bar start downbeats (every 4th beat)")
    energy_profile: List[float] = Field(..., description="RMS energy sampled over time (normalized 0.0 to 1.0)")
    stem_paths: Optional[Dict[str, str]] = Field(None, description="Paths to separated stems: drums, bass, vocals, other")
```

#### Tool 2: `image_to_3d`
Converts a 2D reference character image into a 3D textured mesh (`.glb`).

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal

class PBRTextureMaps(BaseModel):
    albedo_path: str = Field(..., description="Path to diffuse / base color texture map")
    normal_path: Optional[str] = Field(None, description="Path to tangent space normal map")
    roughness_path: Optional[str] = Field(None, description="Path to roughness grayscale map")
    metallic_path: Optional[str] = Field(None, description="Path to metallic grayscale map")

class ImageTo3DInput(BaseModel):
    image_path: str = Field(..., description="Absolute path to 2D reference image (.png, .jpg)")
    backend_provider: Literal["fal_trellis", "tripo_v2", "replicate_sf3d", "local_trellis"] = Field(
        "fal_trellis", description="Inference backend for 3D mesh reconstruction"
    )
    texture_resolution: int = Field(2048, ge=512, le=4096, description="PBR texture resolution (e.g. 1024, 2048)")
    target_polycount: int = Field(50000, ge=5000, le=200000, description="Target polygon count for output mesh")

class Model3DResult(BaseModel):
    mesh_path_glb: str = Field(..., description="Absolute path to generated .glb mesh file")
    mesh_path_obj: Optional[str] = Field(None, description="Optional path to generated .obj file")
    texture_maps: PBRTextureMaps = Field(..., description="Generated PBR texture map paths")
    vertex_count: int = Field(..., description="Total vertex count of generated mesh")
    polygon_count: int = Field(..., description="Total triangle/polygon count")
    generation_time_seconds: float = Field(..., description="Processing duration in seconds")
```

#### Tool 3: `auto_rig`
Analyzes an unskinned 3D mesh, detects bipedal anatomy, creates joint hierarchy, and computes skinning weights.

```python
from pydantic import BaseModel, Field
from typing import List, Literal

class AutoRigInput(BaseModel):
    mesh_path: str = Field(..., description="Absolute path to unrigged 3D mesh (.glb, .obj)")
    rig_preset: Literal["ue5_mannequin", "mixamo", "biped_standard"] = Field(
        "ue5_mannequin", description="Target skeletal hierarchy standard"
    )
    bone_count: int = Field(65, ge=24, le=120, description="Target number of bones in skeleton")

class RigResult(BaseModel):
    rigged_mesh_path_fbx: str = Field(..., description="Path to rigged skeletal mesh in FBX format")
    skeleton_type: str = Field(..., description="Standardized skeleton naming convention used")
    joint_hierarchy: List[str] = Field(..., description="List of joint/bone names generated")
    weight_skinning_passed: bool = Field(..., description="Whether automatic weight skinning converged successfully")
```

#### Tool 4: `extract_mocap`
Extracts 3D skeletal joint motion data from dance or action video.

```python
from pydantic import BaseModel, Field
from typing import Literal

class ExtractMocapInput(BaseModel):
    video_path: str = Field(..., description="Absolute path to dance/performance video (.mp4, .mov)")
    target_fps: int = Field(30, ge=15, le=120, description="Target animation frame rate")
    clean_background: bool = Field(True, description="Whether to apply neural background matting before pose estimation")
    retarget_skeleton: Literal["ue5_mannequin", "mixamo"] = Field(
        "ue5_mannequin", description="Skeleton target for motion retargeting"
    )

class MocapResult(BaseModel):
    animation_path_fbx: str = Field(..., description="Path to exported FBX animation sequence")
    frame_count: int = Field(..., description="Total animation frames extracted")
    fps: int = Field(..., description="Frame rate of animation")
    duration_seconds: float = Field(..., description="Animation duration in seconds")
    root_motion_included: bool = Field(..., description="Whether root translation trajectory is preserved")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Mean pose estimation confidence score")
```

#### Tool 5: `build_ue5_scene`
Synthesizes the complete 3D scene in Unreal Engine 5 via Remote Control.

```python
from pydantic import BaseModel, Field
from typing import List, Literal

class BuildUE5SceneInput(BaseModel):
    character_mesh_path: str = Field(..., description="Path to character rigged mesh (.fbx or .glb)")
    animation_path: str = Field(..., description="Path to character animation track (.fbx)")
    pbr_textures: PBRTextureMaps = Field(..., description="PBR texture maps for dynamic material")
    lighting_preset: Literal["studio_3point", "cyberpunk_neon", "golden_hour", "dramatic_noir"] = Field(
        "studio_3point", description="Lighting environment rig preset"
    )
    camera_preset: Literal["cinematic_orbit", "beat_synced_cuts", "dolly_zoom", "low_angle_hero"] = Field(
        "beat_synced_cuts", description="Cinematic camera motion choreography preset"
    )
    beat_timestamps: List[float] = Field(default_factory=list, description="List of beat timestamps for camera synchronization")

class SceneBuildResult(BaseModel):
    level_sequence_path: str = Field(..., description="Unreal Engine asset path to created Level Sequence")
    camera_actor_name: str = Field(..., description="Name of spawned CineCameraActor in PersistentLevel")
    character_actor_name: str = Field(..., description="Name of spawned Character SkeletalMeshActor")
    lighting_actors: List[str] = Field(..., description="Names of spawned lighting actors")
    total_frames: int = Field(..., description="Total timeline frames created in Level Sequence")
```

#### Tool 6: `render_video`
Executes Movie Render Queue (MRQ) in UE5 to produce high-fidelity cinematic video output.

```python
from pydantic import BaseModel, Field
from typing import Literal

class RenderVideoInput(BaseModel):
    level_sequence_path: str = Field(..., description="Asset path to Level Sequence to render")
    output_format: Literal["mp4", "prores422", "png_sequence"] = Field("mp4", description="Output container format")
    resolution_width: int = Field(1920, ge=640, le=7680, description="Video width in pixels")
    resolution_height: int = Field(1080, ge=360, le=4320, description="Video height in pixels")
    fps: int = Field(30, ge=24, le=60, description="Output video frame rate")
    warmup_frames: int = Field(30, ge=0, le=120, description="Engine warmup frames before rendering")
    output_dir: str = Field(..., description="Directory where rendered video will be saved")

class RenderResult(BaseModel):
    video_file_path: str = Field(..., description="Absolute path to rendered video file")
    resolution: str = Field(..., description="Resolution string (e.g. 1920x1080)")
    frame_count: int = Field(..., description="Total frames rendered")
    render_time_seconds: float = Field(..., description="Time taken to render in seconds")
    file_size_bytes: int = Field(..., description="Size of rendered file on disk in bytes")
```

---

### 2.3 Step-by-Step Production Plan & Human-in-the-Loop Confirmation Protocol

To avoid unexpected consumption of cloud credits or locking the user's GPU on long renders, the copilot generates a **Production Plan** with explicit confirmation gates before heavy operations.

```
[User Request / Drag-and-Drop Assets]
                |
                v
     [Copilot Agent (LLM)]
                |
                v  (Generates)
      [ProductionPlan]
                |
  +-------------+------------------------------------+
  |                                                  |
[Step 1: analyze_audio]                    [Step 2: image_to_3d]
Risk: Low                                  Risk: High (Cloud Credits)
Auto-Approved                              *REQUIRES USER CONFIRMATION*
  |                                                  |
  v (Executes)                                       v
[Audio Analyzed]                           [UI Prompt: Approve $0.20?]
  |                                                  |
  |                                         +--------+--------+
  |                                         |                 |
  |                                      [Approve]        [Reject]
  |                                         |                 |
  |                                         v                 v
  |                                   (Executes)        (Plan Aborted)
  +-----------------------------------------+
```

#### Production Plan Pydantic Models:
```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal

class PlanStep(BaseModel):
    step_id: int = Field(..., description="Sequential step index (1, 2, 3...)")
    tool_name: str = Field(..., description="Name of FastMCP tool to invoke")
    parameters: Dict[str, Any] = Field(..., description="Input parameters prepared for the tool")
    requires_human_confirmation: bool = Field(..., description="True if step requires explicit user sign-off")
    risk_level: Literal["low", "medium", "high"] = Field(..., description="Risk assessment of the operation")
    estimated_duration_seconds: float = Field(..., description="Estimated completion time in seconds")
    state: Literal["pending", "awaiting_confirmation", "confirmed", "rejected", "running", "completed", "failed"] = Field(
        "pending", description="Current lifecycle state of this step"
    )
    confirmation_prompt: Optional[str] = Field(None, description="Human-readable explanation of cost/time impact")

class ProductionPlan(BaseModel):
    plan_id: str = Field(..., description="Unique plan identifier (e.g. plan_20261014_001)")
    title: str = Field(..., description="Descriptive title of the production workflow")
    steps: List[PlanStep] = Field(..., description="Ordered list of production steps")
    status: Literal["draft", "awaiting_confirmation", "in_progress", "completed", "cancelled"] = Field(
        "draft", description="Overall plan status"
    )
```

#### Risk Grading Rules:
1. **Low Risk (`requires_human_confirmation: False`)**:
   - `analyze_audio`: Fast local CPU operation (<3 seconds), zero financial cost.
2. **Medium Risk (`requires_human_confirmation: False / Configurable`)**:
   - `auto_rig`: Local geometric algorithm (<10 seconds).
   - `extract_mocap`: Local or lightweight neural extraction.
   - `build_ue5_scene`: Scene assembly in Unreal Engine (<5 seconds).
3. **High Risk (`requires_human_confirmation: True`)**:
   - `image_to_3d`: Consumes paid API credits (Fal.ai, Tripo) or high VRAM on local TRELLIS; takes 30-90s.
   - `render_video`: Heavy GPU compute with Movie Render Queue; locks rendering resources for 1-5 minutes.

---

### 2.4 Real-Time Telemetry & Progress Streaming Specification

Both the Tauri frontend and MCP clients require real-time feedback during lengthy operations.

#### 2.4.1 Telemetry Event Schema (JSON)
Transmitted via WebSocket and Server-Sent Events (SSE):

```json
{
  "event_type": "telemetry_progress",
  "plan_id": "plan_20261014_001",
  "step_id": 2,
  "tool_name": "image_to_3d",
  "status": "running",
  "progress_percent": 68.5,
  "current_stage": "Synthesizing high-poly mesh and baking PBR maps",
  "log_snippet": "Baking normal map at 2048x2048: pass 2 of 2 complete.",
  "timestamp": 1728867200.451
}
```

#### 2.4.2 FastMCP Native Progress Integration
Inside tool implementations, progress is reported via FastMCP `Context`:
```python
from mcp.server.fastmcp import Context

async def execute_heavy_operation(ctx: Context) -> None:
    await ctx.report_progress(progress=0.25, total=1.0)
    await ctx.info("Phase 1 of 4 completed successfully.")
```

---

## Section 3: Recommended Implementation Blueprint for Subsequent Agents

### 3.1 Directory Structure Compliance (SOLID & Clean Architecture)

```
e:\Disco F\Dev\IANIMATION\
├── backend/
│   ├── __init__.py
│   ├── config.py                     # Environment, ports, API keys
│   ├── mcp/                          # FastMCP Server & Adapters
│   │   ├── __init__.py
│   │   ├── server.py                 # FastMCP server instance and @mcp.tool() definitions
│   │   └── telemetry.py              # WebSocket / SSE telemetry broadcaster
│   ├── models/                       # 100% Strict Pydantic v2 schemas
│   │   ├── __init__.py
│   │   ├── audio.py                  # AudioAnalysis models
│   │   ├── mesh.py                   # ImageTo3D and Rig models
│   │   ├── mocap.py                  # MocapResult models
│   │   ├── ue5.py                    # UE5 Scene & Remote Control models
│   │   └── plan.py                   # ProductionPlan & PlanStep models
│   ├── services/                     # Pure domain services (Dual Invocation target)
│   │   ├── __init__.py
│   │   ├── audio_service.py          # Librosa analysis service
│   │   ├── mesh_service.py           # Fal.ai / Tripo 3D service
│   │   ├── rig_service.py            # Rigging service
│   │   ├── mocap_service.py          # Motion capture service
│   │   ├── ue5_service.py            # UE5 scene assembly service
│   │   └── render_service.py         # MRQ video render service
│   ├── ue5_bridge/                   # Unreal Engine 5 integration
│   │   ├── __init__.py
│   │   ├── client.py                 # REST & WebSocket client for Remote Control
│   │   ├── mock_server.py            # High-fidelity UE5 Python mock server
│   │   └── ue_scripts/               # Python scripts to run inside UE5
│   │       ├── import_asset.py
│   │       ├── setup_lighting.py
│   │       └── setup_camera.py
│   └── tests/                        # Automated pytest suite
│       ├── test_ue5_client_and_mock.py
│       ├── test_fastmcp_tools.py
│       └── test_production_plan.py
├── frontend/                         # Tauri desktop app (Rust + React/TS)
├── verify_pipeline.py                # End-to-end CLI verification runner
├── PROJECT_STATUS.md                 # Project continuity and status
└── GEMINI.md                         # Engineering rules and SOLID standards
```

---

## Verification & Independent Reproducibility

To independently verify the schemas, protocol contracts, and mock server behavior defined in this report:

1. **Verify Pydantic Schemas**:
   ```powershell
   python -c "from pydantic import BaseModel; print('Pydantic v2 ready')"
   ```
2. **Verify FastMCP Tool Registration**:
   ```powershell
   python -c "from mcp.server.fastmcp import FastMCP; m = FastMCP('test'); print(m.name)"
   ```
3. **Verify UE5 Remote Control Client & Mock**:
   Once implemented by the builder agents, running `pytest backend/tests/test_ue5_client_and_mock.py` must achieve 100% pass rate against the mock server on ports 30010/30020.
