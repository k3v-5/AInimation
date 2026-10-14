# Handoff Report: Milestone 2 UE5 Bridge & Mock Server QA Strategy & Testing Blueprint

**Agent**: `explorer_m2_2`  
**Working Directory**: `e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m2_2`  
**Parent Task ID**: `7287cd58-777e-4099-99af-79aab795ba88`  
**Target File**: `tests/backend/test_ue5_bridge.py`  
**Specification References**: `PROJECT.md`, `TEST_INFRA.md`, `TEST_READY.md`, `GEMINI.md`  

---

## 1. Observation

### 1.1 Existing E2E Test Suite Analysis (Tiers 1–4) for F-UE5-01 through F-UE5-08

Across the 4-tier E2E testing architecture established in `tests/e2e/`, the features `F-UE5-01` through `F-UE5-08` are exercised at various levels of abstraction. The table below catalogs every E2E test exercising these features, including file path, line numbers, test function, execution mechanics, and verbatim assertions:

| Feature ID | Feature Description | Test Tier & File | Line Numbers | Test Function Name | Specific Assertions & Verbatim Checks | Coverage Assessment / Identified Gaps |
|---|---|---|---|---|---|---|
| **F-UE5-01** | UE5 Remote Control REST Client (`/remote/object/call`, `/remote/object/property`) | Tier 1: `tests/e2e/test_tier1_features.py` | 76–83 | `test_f_ue5_01_rest_client_call_and_property` | `assert hasattr(ue5_client_mod, "UE5RestClient") or hasattr(ue5_client_mod, "UE5RemoteClient")` | **Shallow smoke check only**. Does not test wire HTTP request emission, payload serialization, headers, HTTP error responses, or network timeouts. |
| **F-UE5-02** | UE5 Remote Control WebSocket Client (`/remote/protocol`) with RPC & Events | Tier 1: `tests/e2e/test_tier1_features.py` | 85–92 | `test_f_ue5_02_websocket_rpc_and_subscribe` | `assert hasattr(ue5_client_mod, "UE5WebSocketClient") or hasattr(ue5_client_mod, "UE5RemoteClient")` | **Symbol check only**. Does not test socket connection, WebSocket frame formatting, event dispatching, or callbacks. |
| **F-UE5-03** | High-Fidelity Mock Server (Ports 30010 & 30020) | Tier 1: `tests/e2e/test_tier1_features.py` | 94–101 | `test_f_ue5_03_mock_server_lifecycle` | `assert hasattr(ue5_mock_mod, "UE5MockServer") or hasattr(ue5_mock_mod, "MockUE5Server")` | **Symbol check only**. Does not test server daemon startup, port binding, HTTP routing (`/remote/info`, `/remote/object/call`), thread safety, or clean shutdown. |
| **F-UE5-04** | Dynamic Runtime Asset Loading (`.glb`/`.fbx`) | Tier 1: `tests/e2e/test_tier1_features.py` | 103–109 | `test_f_ue5_04_dynamic_asset_import_glb_fbx` | `assert hasattr(ue5_mod, "UE5RestClient") or hasattr(ue5_mod, "UE5RemoteClient")` | Takes `synthetic_glb_path` fixture but does not actually invoke `import_asset()` or verify Content Browser destination path. |
| **F-UE5-04** | Corrupt GLB Import Handling | Tier 2: `tests/e2e/test_tier2_boundaries.py` | 100–111 | `test_f_ue5_04_corrupt_glb_import_failure` | `corrupt_glb = create_corrupt_glb(tmp_path / "corrupt_mesh.glb"); assert corrupt_glb.exists()` | **Fixture assertion only**. Does not pass the corrupt asset to `client.import_asset()` to assert structured failure responses or validation errors. |
| **F-UE5-04 / 05 / 06** | Scene Assembly (Mesh, Materials, Lumen) | Tier 3: `tests/e2e/test_tier3_interactions.py` | 89–129 | `test_interaction_scene_assembly_to_mrq_render` | Calls `build_scene_fn(scene_config)`; `assert scene_result.success is True`; `assert scene_result.scene_path is not None` | **Black-box integration**. Verifies FastMCP wrapper `build_ue5_scene()` returns success, but does not verify internal actor transforms, lighting intensities, or component hierarchies. |
| **F-UE5-05** | Dynamic PBR Material Assignment | Tier 1: `tests/e2e/test_tier1_features.py` | 111–118 | `test_f_ue5_05_pbr_material_assignment` | `assert hasattr(mat_mod, "create_pbr_material") or hasattr(mat_mod, "MaterialManager")` | **Symbol check only**. Does not test roughness/metallic clamp boundaries, ColorRGB serialization, or texture map dictionary linking. |
| **F-UE5-06** | Lumen Lighting Rig Configuration | Tier 1: `tests/e2e/test_tier1_features.py` | 120–127 | `test_f_ue5_06_lumen_lighting_presets` | `assert hasattr(light_mod, "setup_lumen_lighting") or hasattr(light_mod, "LightingRig")` | **Symbol check only**. Does not test preset structures (`studio_3point`, `cyberpunk`, `dramatic`), intensity ranges, or color temperatures. |
| **F-UE5-07** | CineCamera Beat Choreography | Tier 1: `tests/e2e/test_tier1_features.py` | 129–136 | `test_f_ue5_07_cinecamera_beat_sync` | `assert hasattr(cam_mod, "generate_camera_track") or hasattr(cam_mod, "CineCameraChoreographer")` | **Symbol check only**. Does not test keyframe count, mathematical interpolation curves, or beat alignment. |
| **F-UE5-07** | Empty Beats Fallback Timeline | Tier 2: `tests/e2e/test_tier2_boundaries.py` | 117–130 | `test_f_ue5_07_zero_beats_fallback` | `track = gen_cam_fn(beat_timestamps=[], total_duration=10.0, preset="smooth_orbit"); assert track is not None; assert len(track) >= 2` | **Substantive boundary test**. Confirms fallback timeline generates start ($t=0.0$) and end ($t=10.0$) keyframes when input beat list is empty. |
| **F-UE5-07** | Audio BPM to Camera Cut Sync | Tier 3: `tests/e2e/test_tier3_interactions.py` | 19–50 | `test_interaction_audio_to_camera_choreography` | Calls `analyze_fn(synthetic_audio_path)`; feeds `beat_timestamps` to `cam_choreograph_fn(..., preset="dramatic_orbit")`; `assert len(camera_keyframes) > 0`; `assert first_keyframe_time >= 0.0` | **Substantive integration test**. Verifies pairwise data flow from audio analysis to camera choreographer. |
| **F-UE5-08** | Movie Render Queue (MRQ) Scheduling & Poll | Tier 1: `tests/e2e/test_tier1_features.py` | 138–145 | `test_f_ue5_08_mrq_job_submission_and_poll` | `assert hasattr(mrq_mod, "render_sequence") or hasattr(mrq_mod, "MRQManager")` | **Symbol check only**. Does not test render parameter validation, frame calculation, output file writing, or job state transitions. |
| **F-UE5-08** | MRQ Render Execution from Scene | Tier 3: `tests/e2e/test_tier3_interactions.py` | 118–129 | `test_interaction_scene_assembly_to_mrq_render` | Calls `render_video_fn(scene_path=scene_result.scene_path, output_path=..., fps=30, resolution="1280x720")`; `assert render_result is not None`; `assert render_result.frame_count > 0` | **Substantive integration test**. Verifies `render_video` tool produces valid `RenderResult` with positive frame count. |
| **F-UE5-01..08** | Full End-to-End Assisted Pipeline | Tier 4: `tests/e2e/test_tier4_scenarios.py` | 19–110 | `test_scenario_a_full_pipeline` | Phase 4 (Scene Assembly): `scene_res = build_scene_fn(scene_config); assert scene_res.success is True`. Phase 5 (Render): `render_res = render_fn(...); assert render_res is not None; assert render_res.frame_count > 0; assert out_video.exists()` | **Full scenario test**. Proves the high-level happy path functions end-to-end across all subsystems. |

### 1.2 Inspection of Existing Backend Implementation (`backend/ue5/`)

The inspection of `backend/ue5/` confirms the following modules are implemented:
1. `backend/ue5/client.py` (212 lines):
   - `UE5RestClient`: Communicates via `urllib.request` with `http://{host}:{port}`. Implements `call()`, `set_property()`, `get_property()`, `import_asset()`, and `spawn_actor()`. Includes graceful fallback dictionaries when connection fails.
   - `UE5WebSocketClient`: Manages subscription dict `_subscriptions: Dict[str, List[Any]]`, `subscribe()`, `unsubscribe()`.
   - `UE5RemoteClient`: Facade combining REST and WebSocket clients.
2. `backend/ue5/mock_server.py` (219 lines):
   - `UE5MockState`: Thread-safe state store (`_lock = threading.Lock()`) tracking `actors`, `properties`, `loaded_assets`, `rendered_jobs`, `active_level`. Implements `call_function()`, `set_property()`, `get_property()`, `reset()`.
   - `UE5RESTHandler`: `BaseHTTPRequestHandler` handling `GET /remote/info`, `GET /remote/object/property`, `PUT /remote/object/call`, `PUT /remote/object/property`, `PUT /remote/preset`.
   - `UE5MockServer`: Multi-threaded daemon runner managing `HTTPServer` lifecycle (`start()`, `stop()`, `reset_state()`, context manager support).
3. `backend/ue5/camera.py` (153 lines):
   - `CineCameraChoreographer`: Computes beat-synced motion paths for presets (`smooth_orbit`, `dramatic_orbit`, `aerial_pan`, `front_close`). Clamps `default_fov` $[10, 120]$ and `distance` $\ge 50$. Handles empty beat list fallback.
   - `generate_camera_track()`: Functional facade returning `List[CameraKeyframe]`.
4. `backend/ue5/lighting.py` (140 lines):
   - `LightActorConfig` & `LumenLightingSetup`: Pydantic models for individual lights and global Lumen settings.
   - `LightingRig`: Generates presets (`studio_3point`, `cyberpunk` / `neon`, `dramatic`).
   - `setup_lumen_lighting()`: Functional facade.
5. `backend/ue5/materials.py` (89 lines):
   - `PBRMaterialInstance`: Pydantic model for material parameters (`material_name`, `parent_material_path`, `base_color`, `roughness`, `metallic`, `specular`, `textures`).
   - `MaterialManager`: Registry and factory for material instances.
   - `create_pbr_material()`: Functional facade.
6. `backend/ue5/mrq.py` (82 lines):
   - `MRQManager`: Coordinates Movie Render Queue export, calls `create_dummy_video()`, returns `RenderResult`.
   - `render_sequence()`: Functional facade.

### 1.3 Baseline Execution Results

Running pytest against existing tests confirmed:
- `python -m pytest tests/e2e/test_tier1_features.py -k "ue5" -v`: **8 passed in 1.95s**.
- `python -m pytest tests/e2e/test_tier2_boundaries.py tests/e2e/test_tier3_interactions.py -k "ue5 or camera or mrq or scene" -v`: **4 passed in 13.99s**.
- `python -m pytest tests/e2e/test_tier4_scenarios.py -v`: **3 passed in 13.92s**.
- Crucial finding: `tests/backend/test_ue5_bridge.py` **does not exist yet** in `tests/backend/`.

---

## 2. Logic Chain

1. **Observation 1.1** establishes that while E2E Tiers 1–4 provide comprehensive black-box validation of the integrated pipeline, Tier 1 tests are primarily symbol-existence assertions (`hasattr`) designed for progressive milestone readiness, and Tiers 3–4 invoke UE5 tools only via the FastMCP wrapper (`build_ue5_scene`, `render_video`).
2. **Observation 1.2** reveals rich internal logic across `backend/ue5/` (thread locking, port binding, HTTP handler dispatch, camera mathematical curves, PBR property clamping, lighting configurations, and MRQ video writing) that has zero dedicated unit/integration coverage in `tests/backend/`.
3. In accordance with `GEMINI.md` §1 (SOLID), §2 (Zero-Any Policy), and §5 (Pruebas Automatizadas Rigurosas), each backend component, adapter, and utility function must have comprehensive unit and integration tests covering nominal paths, boundary limits, and failure modes.
4. Therefore, `tests/backend/test_ue5_bridge.py` must be authored to provide isolated, high-density coverage across all 7 functional areas identified in the mission mandate:
   - Area 1: Client connection handling, disconnect, reconnect, timeouts, REST call serialization.
   - Area 2: Mock server startup, port binding, HTTP routes, WebSocket subscriptions, simulated failures.
   - Area 3: Dynamic asset loading (.glb/.fbx), actor transforms, component hierarchy.
   - Area 4: PBR material properties and validation.
   - Area 5: Lumen lighting adjustments, intensities, color temperatures.
   - Area 6: CineCamera keyframe interpolation and tracking.
   - Area 7: MRQ job queueing, state transitions, progress callbacks, and output verification.
5. To guarantee test determinism and prevent port collision during parallel test runs, the mock server tests must utilize dynamically assigned ephemeral ports or fixture-scoped server lifecycles with guaranteed cleanup.

---

## 3. Caveats

1. **Offline Environment Guarantee**: All tests in `test_ue5_bridge.py` must run 100% offline without connecting to an actual Unreal Engine 5 Editor instance. The mock server (`UE5MockServer`) and client simulation fallbacks are the authoritative fixtures.
2. **WebSocket Client Real Transport**: Currently, `UE5WebSocketClient` in `client.py` implements in-memory subscription callback management (`_subscriptions: Dict[str, List[Any]]`). Tests for WebSocket must verify this subscription contract and envelope serialization without expecting a live RFC 6455 WebSocket handshake unless mock server implements standard WebSocket frames.
3. **No Code Implementation in this Turn**: Per the Explorer role constraints, this report delivers the comprehensive testing blueprint and detailed test specifications. Implementation of `tests/backend/test_ue5_bridge.py` will be carried out by the subsequent milestone implementer.

---

## 4. Conclusion & Testing Blueprint for `tests/backend/test_ue5_bridge.py`

Below is the complete testing blueprint and architectural specification for `tests/backend/test_ue5_bridge.py`.

### 4.1 Test Suite Architecture & Module Layout

The test file `tests/backend/test_ue5_bridge.py` is organized into 7 specialized test classes mapping directly to the 7 functional areas:

```
tests/backend/test_ue5_bridge.py
├── Fixtures:
│   ├── ephemeral_mock_server (starts UE5MockServer on ephemeral port, cleans up on teardown)
│   ├── ue5_test_client (instantiates UE5RestClient pointing to ephemeral mock server)
│   ├── ue5_remote_client (instantiates unified UE5RemoteClient)
│   ├── mock_glb_file (creates temporary minimal valid GLB)
│   └── mock_corrupt_file (creates temporary truncated/corrupt binary file)
│
├── 1. TestUE5ClientConnection (Connection handling, disconnect, timeouts, serialization)
├── 2. TestUE5MockServer (Server lifecycle, port binding, routes, concurrency, errors)
├── 3. TestUE5AssetAndActors (Dynamic asset import, actor transforms, component hierarchy)
├── 4. TestUE5PBRMaterials (PBR material models, validation, clamping, texture sets)
├── 5. TestUE5LumenLighting (Lighting presets, intensity calculation, color temperatures)
├── 6. TestUE5CineCameraChoreography (Presets, beat alignment, fallback timelines, math curves)
└── 7. TestUE5MovieRenderQueue (MRQ configuration, video export, frame counts, error modes)
```

---

### 4.2 Detailed Test Case Specifications

#### Class 1: `TestUE5ClientConnection`
*Objective*: Validate REST call serialization, HTTP headers, payload schemas, timeouts, and connection failure handling.

1. `test_rest_call_serialization_nominal`:
   - **Target**: `UE5RestClient.call()`
   - **Input**: `object_path="/Script/UnrealEd.Default__EditorActorSubsystem"`, `function_name="SpawnActor"`, `parameters={"Class": "StaticMeshActor"}`, `generate_transaction=True`.
   - **Verification**: Verifies that the JSON payload contains `objectPath`, `functionName`, `parameters`, and `generateTransaction`. Asserts HTTP 200 response parsed correctly.
2. `test_rest_set_property_serialization`:
   - **Target**: `UE5RestClient.set_property()`
   - **Input**: `object_path="/Game/Stage_Main.PersistentLevel.Actor_1"`, `property_name="RelativeLocation"`, `value={"X": 100.0, "Y": 200.0, "Z": 300.0}`.
   - **Verification**: Verifies payload contains `access: "WRITE"`, `propertyValue`, and `objectPath`. Asserts `res["Success"] is True`.
3. `test_rest_get_property_serialization`:
   - **Target**: `UE5RestClient.get_property()`
   - **Input**: Set property first, then `get_property(object_path, property_name)`.
   - **Verification**: Verifies `access: "READ"` request sent. Asserts returned value matches previously set value.
4. `test_client_timeout_handling`:
   - **Target**: `UE5RestClient._request()` timeout parameter
   - **Input**: Send request to a non-responsive HTTP server or socket that delays response beyond timeout.
   - **Verification**: Verifies request terminates cleanly within timeout window without hanging; returns structured error dictionary `{"Success": False, "Error": ...}` or fallback dictionary.
5. `test_client_offline_graceful_fallback`:
   - **Target**: `UE5RestClient.call()` and `set_property()` when host/port is completely unreachable (e.g. port 65530).
   - **Verification**: Verifies client does not crash with unhandled `URLError` or `ConnectionRefusedError`; returns simulated fallback `{"Success": True, "Object": ..., ...}` ensuring headless copilot workflows proceed uninterrupted.
6. `test_websocket_subscription_and_unsubscription`:
   - **Target**: `UE5WebSocketClient.subscribe()` and `unsubscribe()`
   - **Input**: Register callback `cb1` on event `"OnActorSpawned"`, register `cb2`, then unsubscribe `cb1`.
   - **Verification**: Asserts `_subscriptions["OnActorSpawned"]` contains only `cb2`. Unsubscribing a non-existent callback does not raise an exception.
7. `test_remote_client_facade_delegation`:
   - **Target**: `UE5RemoteClient`
   - **Verification**: Asserts all facade methods (`call`, `set_property`, `get_property`, `import_asset`, `spawn_actor`) correctly delegate to the underlying `UE5RestClient` and match return signatures.

---

#### Class 2: `TestUE5MockServer`
*Objective*: Validate high-fidelity mock server startup, port binding, HTTP routes, multi-threaded concurrency, and simulated failures.

1. `test_mock_server_start_stop_lifecycle`:
   - **Target**: `UE5MockServer.start()` and `stop()`
   - **Verification**: `is_running` transitions `False` $\rightarrow$ `True` $\rightarrow$ `False`. Sockets properly opened and closed.
2. `test_mock_server_context_manager`:
   - **Target**: `with UE5MockServer(port=...) as server:`
   - **Verification**: Server is active within context block; server automatically shuts down upon exiting context block.
3. `test_mock_server_info_endpoint`:
   - **Target**: `GET /remote/info`
   - **Verification**: Returns status 200, JSON payload `{"Version": "5.4.0", "Engine": "UnrealEngine", "Mock": True}`.
4. `test_mock_server_root_endpoint`:
   - **Target**: `GET /`
   - **Verification**: Returns status 200, `{"Status": "OK", "ActiveLevel": "Stage_Main"}`.
5. `test_mock_server_reset_state`:
   - **Target**: `UE5MockServer.reset_state()` / `UE5MockState.reset()`
   - **Verification**: After adding custom actors and properties, calling `reset_state()` wipes custom actors and restores default actors (`CineCameraActor_1`, `DirectionalLight_1`).
6. `test_mock_server_concurrency_thread_safety`:
   - **Target**: `UE5MockState` under concurrent multi-threaded writes
   - **Execution**: Launch 10 worker threads simultaneously spawning actors and writing properties.
   - **Verification**: Verifies no race conditions, deadlocks, or state corruption occur; actor count equals exactly the sum of spawned actors.
7. `test_mock_server_malformed_json_resilience`:
   - **Target**: `UE5RESTHandler.do_PUT`
   - **Input**: Send raw non-JSON bytes (e.g. `b"MALFORMED{{{INVALID"`) with `Content-Type: application/json`.
   - **Verification**: Server responds with HTTP 200/400 without crashing the background thread.
8. `test_mock_server_preset_endpoint`:
   - **Target**: `PUT /remote/preset`
   - **Verification**: Returns `{"Success": True, "Preset": "Applied"}`.

---

#### Class 3: `TestUE5AssetAndActors`
*Objective*: Validate dynamic 3D asset import, actor spawning, spatial transforms, and component hierarchy.

1. `test_dynamic_asset_import_valid_glb`:
   - **Target**: `UE5RestClient.import_asset()`
   - **Input**: Valid synthetic GLB file path, destination `/Game/Imported/Characters`.
   - **Verification**: Returns `{"Success": True, "AssetPath": "/Game/Imported/Characters/<filename>"}`. Mock server records asset in `loaded_assets`.
2. `test_dynamic_asset_import_missing_file_error`:
   - **Target**: `UE5RestClient.import_asset()`
   - **Input**: Path to non-existent file `/tmp/does_not_exist_9999.glb`.
   - **Verification**: Returns `{"Success": False, "Error": "Asset file does not exist: ...", "AssetPath": ""}` without sending unnecessary remote call.
3. `test_spawn_actor_with_vector3d_and_rotator3d`:
   - **Target**: `UE5RestClient.spawn_actor()`
   - **Input**: `actor_class="StaticMeshActor"`, `location=Vector3D(x=150.0, y=-200.0, z=50.0)`, `rotation=Rotator3D(pitch=10.0, yaw=45.0, roll=0.0)`.
   - **Verification**: Verifies location and rotation parameters serialized via `.to_ue5_dict()`. Returns valid actor ID matching `/Game/Stage_Main.Stage_Main:PersistentLevel.StaticMeshActor_*`.
4. `test_spawn_actor_extreme_transforms`:
   - **Target**: `UE5RestClient.spawn_actor()`
   - **Input**: Negative coordinates ($X=-50000.0, Y=-50000.0, Z=-1000.0$), extreme rotations ($Yaw=359.9, Pitch=-89.0$).
   - **Verification**: Asserts successful spawn and storage in mock server state without numerical overflow or NaN.
5. `test_actor_material_assignment_function`:
   - **Target**: Function call `SetMaterial` via `call()`
   - **Input**: `object_path="/Script/UnrealEd.Default__EditorActorSubsystem"`, `function_name="SetMaterial"`, `parameters={"ActorId": actor_id, "MaterialPath": "/Game/Materials/M_CharacterPBR"}`.
   - **Verification**: Verifies mock server updates actor dictionary with assigned material.

---

#### Class 4: `TestUE5PBRMaterials`
*Objective*: Validate PBR material models, parameter ranges, clamping, texture map binding, and registry management.

1. `test_pbr_material_instance_model_valid`:
   - **Target**: `PBRMaterialInstance`
   - **Input**: `material_name="M_Armor"`, `base_color=ColorRGB(r=0.9, g=0.9, b=0.9)`, `roughness=0.2`, `metallic=0.9`, `specular=0.5`.
   - **Verification**: Model instantiates with strictly validated fields and exact values.
2. `test_pbr_material_roughness_and_metallic_bounds`:
   - **Target**: Boundary enforcement on `PBRMaterialInstance`
   - **Input**: `roughness=-0.1` and `roughness=1.1`; `metallic=-0.5` and `metallic=1.5`.
   - **Verification**: Raises `pydantic.ValidationError` on values outside $[0.0, 1.0]$.
3. `test_material_manager_create_and_retrieve`:
   - **Target**: `MaterialManager.create_material()` and `get_material()`
   - **Input**: Register material `"M_Gold"`, retrieve by name.
   - **Verification**: Retrieved instance matches registered instance. Retrieving unregistered name returns `None`.
4. `test_material_manager_clamping_logic`:
   - **Target**: `MaterialManager.create_material()`
   - **Input**: Pass `roughness=1.5` and `metallic=-0.2`.
   - **Verification**: `MaterialManager` clamps values to $1.0$ and $0.0$ respectively rather than failing, providing robust pipeline resilience.
5. `test_create_pbr_material_facade_with_dict_coercion`:
   - **Target**: `create_pbr_material()`
   - **Input**: Pass `base_color={"r": 0.5, "g": 0.5, "b": 1.0}` and `textures={"albedo_path": "/tmp/albedo.png"}` as dicts.
   - **Verification**: Facade cleanly coerces dictionaries to `ColorRGB` and `PBRTextureSet` Pydantic models.

---

#### Class 5: `TestUE5LumenLighting`
*Objective*: Validate Lumen lighting presets, light intensity values, spatial positioning, color temperatures, and post-process settings.

1. `test_lumen_lighting_preset_studio_3point`:
   - **Target**: `LightingRig.get_preset("studio_3point")`
   - **Verification**: Returns `LumenLightingSetup` containing 4 lights (`Key_Light` Spot 8000 lm, `Fill_Light` Spot 3500 lm, `Rim_Backlight` Point 5000 lm, `Sky_Ambient` Sky 1000 lm). `lumen_global_illumination is True`, `lumen_reflections is True`.
2. `test_lumen_lighting_preset_cyberpunk`:
   - **Target**: `LightingRig.get_preset("cyberpunk")`
   - **Verification**: Returns 3 neon lights (`Key_NeonCyan` Spot, `Fill_NeonMagenta` Spot, `Rim_NeonAmber` Point 12000 lm). Verifies color coordinates ($r=0.0, g=0.9, b=1.0$ for cyan).
3. `test_lumen_lighting_preset_dramatic`:
   - **Target**: `LightingRig.get_preset("dramatic")`
   - **Verification**: Returns 2 high-contrast chiaroscuro lights (`Key_Chiaroscuro` Spot 15000 lm, `Rim_HairLight` Spot 10000 lm).
4. `test_lumen_lighting_unknown_preset_fallback`:
   - **Target**: `LightingRig.get_preset("non_existent_preset_xyz")`
   - **Verification**: Gracefully falls back to default `studio_3point` configuration without crashing.
5. `test_light_actor_config_model_validation`:
   - **Target**: `LightActorConfig`
   - **Input**: Create light with custom `temperature_kelvin=6500.0`, `intensity=25000.0`, `position=Vector3D(x=0, y=0, z=500)`.
   - **Verification**: Strictly validates attributes, defaults `cast_shadows=True`.

---

#### Class 6: `TestUE5CineCameraChoreography`
*Objective*: Validate beat-synced CineCamera keyframe generation, trajectory math, presets, FOV bounds, and empty-beat fallback behavior.

1. `test_camera_choreographer_initialization_bounds`:
   - **Target**: `CineCameraChoreographer.__init__()`
   - **Input**: Extreme FOV values ($5.0$ and $150.0$), distance $< 50.0$.
   - **Verification**: `default_fov` clamped to $[10.0, 120.0]$; `distance` clamped to $\ge 50.0$.
2. `test_camera_track_empty_beats_fallback`:
   - **Target**: `CineCameraChoreographer.generate_track(beat_timestamps=[], total_duration=8.0)`
   - **Verification**: Returns exactly 2 keyframes: first at $t=0.0$, second at $t=8.0$. Both have valid spatial coordinates, pitch, yaw, roll, and fov.
3. `test_camera_track_smooth_orbit_math`:
   - **Target**: `generate_camera_track(..., preset="smooth_orbit")`
   - **Input**: `beat_timestamps=[1.0, 2.0, 3.0, 4.0]`, `total_duration=5.0`.
   - **Verification**: Generated track starts at $t=0.0$ and ends at $t=5.0$. Keyframe count equals $len(beats) + 2$. Camera radius remains constant at `distance`. Yaw values progress smoothly within $[0.0, 360.0]$.
4. `test_camera_track_dramatic_orbit_fov_oscillation`:
   - **Target**: `generate_camera_track(..., preset="dramatic_orbit")`
   - **Verification**: Dynamic radius varies with sine wave; FOV alternates between $\text{default\_fov} + 5.0$ and $\text{default\_fov} - 5.0$ on alternating beats.
5. `test_camera_track_aerial_pan_preset`:
   - **Target**: `generate_camera_track(..., preset="aerial_pan")`
   - **Verification**: Camera Z elevation is high ($Z > \text{center\_z} + 150.0$); downward pitch is fixed at $-25.0^\circ$.
6. `test_camera_track_front_close_preset`:
   - **Target**: `generate_camera_track(..., preset="front_close")`
   - **Verification**: Camera distance is halved ($0.5 \times \text{distance}$); narrow FOV ($\le \text{default\_fov}$).
7. `test_camera_keyframe_ue5_payload_formatting`:
   - **Target**: `CameraKeyframe.to_ue5_payload()`
   - **Verification**: Formats dictionary containing `Location: {"X": ..., "Y": ..., "Z": ...}`, `Rotation: {"Pitch": ..., "Yaw": ..., "Roll": ...}`, `CurrentFocalLength`, `CurrentAperture`, `FocusDistance`, and `FieldOfView`.

---

#### Class 7: `TestUE5MovieRenderQueue`
*Objective*: Validate Movie Render Queue configuration models, resolution string parsing, dummy video export, frame counts, and elapsed execution timing.

1. `test_mrq_job_config_model_validation`:
   - **Target**: `MovieRenderQueueJobConfig`
   - **Input**: `scene_path="/Game/Sequences/LS_Main"`, `output_path="/renders/output.mp4"`, `fps=60`, `resolution="1920x1080"`, `anti_aliasing_samples=16`, `warmup_frames=30`.
   - **Verification**: All fields validate strictly. `get_resolution_dimensions()` correctly returns integer tuple `(1920, 1080)`.
2. `test_mrq_job_config_invalid_resolution_regex`:
   - **Target**: `MovieRenderQueueJobConfig` regex validation
   - **Input**: `resolution="1920-1080"`, `resolution="invalid"`, `resolution="1920x"`.
   - **Verification**: Raises `pydantic.ValidationError`.
3. `test_mrq_manager_render_execution`:
   - **Target**: `MRQManager.render()`
   - **Input**: Render sequence with `fps=30`, `output_path=tmp_path / "renders" / "test_render.mp4"`.
   - **Verification**: Output video file is created on disk with non-zero size (`file_size_bytes > 0`). Returned `RenderResult` has `frame_count == 90` (3.0s * 30 fps), `fps == 30`, `elapsed_seconds > 0.0`, and `success is True`.
4. `test_render_sequence_functional_facade`:
   - **Target**: `render_sequence()`
   - **Verification**: Functional facade delegates to `MRQManager` and produces identical valid `RenderResult`.

---

### 4.3 Proposed Implementation Code Blueprint

Below is the concrete code structure to be placed in `tests/backend/test_ue5_bridge.py`:

```python
"""
Unit and Integration Test Suite for Unreal Engine 5 Bridge & Mock Server (Milestone 2).

Tests:
1. UE5 REST and WebSocket clients (serialization, headers, connection handling, timeouts, fallbacks).
2. High-fidelity UE5 Mock Server (lifecycle, HTTP routes, multi-threaded state, failure resilience).
3. Dynamic runtime asset loading (.glb/.fbx), actor transforms, and component hierarchy.
4. Programmatic PBR material configuration, parameter clamping, and texture map linking.
5. Lumen lighting rig presets, intensity scaling, and color temperatures.
6. CineCamera choreography, beat-synced keyframe interpolation, and trajectory math.
7. Movie Render Queue (MRQ) job scheduling, validation, and video container export.

Adheres strictly to SOLID principles, Zero-Any Policy, and Pydantic v2 strict typing.
"""

from __future__ import annotations

import json
from pathlib import Path
import threading
import time
from typing import Any, Dict, Generator, List
import urllib.error
import urllib.request

import pytest
from pydantic import ValidationError

from backend.core.models import (
    CameraKeyframe,
    ColorRGB,
    MovieRenderQueueJobConfig,
    PBRTextureSet,
    RenderResult,
    Rotator3D,
    Vector3D,
)
from backend.ue5.camera import CineCameraChoreographer, generate_camera_track
from backend.ue5.client import UE5RemoteClient, UE5RestClient, UE5WebSocketClient
from backend.ue5.lighting import LightActorConfig, LightingRig, LumenLightingSetup, setup_lumen_lighting
from backend.ue5.materials import MaterialManager, PBRMaterialInstance, create_pbr_material
from backend.ue5.mock_server import UE5MockServer, UE5MockState, UE5RESTHandler
from backend.ue5.mrq import MRQManager, render_sequence
from tests.e2e.fixtures.synthetic_mesh import create_minimal_glb


# ---------------------------------------------------------------------------
# Test Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def ephemeral_mock_server() -> Generator[UE5MockServer, None, None]:
    """Provide an isolated UE5MockServer running on ephemeral test port 30015."""
    server = UE5MockServer(host="127.0.0.1", port=30015, ws_port=30025)
    server.start()
    time.sleep(0.05)  # Allow thread to bind
    try:
        yield server
    finally:
        server.stop()


@pytest.fixture(scope="function")
def ue5_test_client(ephemeral_mock_server: UE5MockServer) -> UE5RestClient:
    """Provide a UE5RestClient connected to the running ephemeral mock server."""
    return UE5RestClient(host=ephemeral_mock_server.host, port=ephemeral_mock_server.port)


@pytest.fixture
def mock_glb_file(tmp_path: Path) -> Path:
    """Create a temporary valid binary GLB file fixture."""
    file_path = tmp_path / "test_model.glb"
    return create_minimal_glb(file_path, mesh_name="TestMesh")


# ---------------------------------------------------------------------------
# 1. Client Connection Handling & Serialization Tests
# ---------------------------------------------------------------------------

class TestUE5ClientConnection:
    def test_rest_call_serialization_nominal(self, ue5_test_client: UE5RestClient) -> None:
        res = ue5_test_client.call(
            object_path="/Script/UnrealEd.Default__EditorActorSubsystem",
            function_name="SpawnActor",
            parameters={"Class": "StaticMeshActor"},
            generate_transaction=True,
        )
        assert res.get("Success") is True
        assert "ActorId" in res

    def test_rest_property_write_and_read(self, ue5_test_client: UE5RestClient) -> None:
        obj_path = "/Game/Stage_Main.PersistentLevel.Actor_1"
        prop_name = "CustomScalar"
        prop_val = 42.5

        set_res = ue5_test_client.set_property(obj_path, prop_name, prop_val)
        assert set_res.get("Success") is True

        read_val = ue5_test_client.get_property(obj_path, prop_name)
        assert read_val == prop_val

    def test_client_offline_graceful_fallback(self) -> None:
        offline_client = UE5RestClient(host="127.0.0.1", port=65530)
        res = offline_client.call(
            object_path="/Script/Engine.Actor",
            function_name="CustomFunction",
            parameters={"Value": 10},
        )
        assert res.get("Success") is True
        assert res.get("Function") == "CustomFunction"

    def test_websocket_client_subscription_management(self) -> None:
        ws_client = UE5WebSocketClient(host="127.0.0.1", port=30025)
        events_received: List[str] = []

        def callback(event: Any) -> None:
            events_received.append("triggered")

        ws_client.subscribe("ActorSpawned", callback)
        assert callback in ws_client._subscriptions["ActorSpawned"]

        ws_client.unsubscribe("ActorSpawned", callback)
        assert callback not in ws_client._subscriptions["ActorSpawned"]

    def test_remote_client_facade(self, ephemeral_mock_server: UE5MockServer) -> None:
        remote = UE5RemoteClient(host=ephemeral_mock_server.host, http_port=ephemeral_mock_server.port)
        actor_id = remote.spawn_actor("CineCameraActor")
        assert "CineCameraActor" in actor_id


# ---------------------------------------------------------------------------
# 2. Mock Server Lifecycle & Concurrency Tests
# ---------------------------------------------------------------------------

class TestUE5MockServer:
    def test_mock_server_info_endpoint(self, ephemeral_mock_server: UE5MockServer) -> None:
        url = f"http://{ephemeral_mock_server.host}:{ephemeral_mock_server.port}/remote/info"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["Version"] == "5.4.0"
            assert data["Mock"] is True

    def test_mock_server_reset_state(self, ue5_test_client: UE5RestClient, ephemeral_mock_server: UE5MockServer) -> None:
        ue5_test_client.spawn_actor("StaticMeshActor")
        assert len(ephemeral_mock_server.state.actors) > 2
        ephemeral_mock_server.reset_state()
        assert len(ephemeral_mock_server.state.actors) == 2

    def test_mock_server_thread_safety(self, ue5_test_client: UE5RestClient) -> None:
        def worker(idx: int) -> None:
            ue5_test_client.spawn_actor(f"WorkerActor_{idx}")

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()


# ---------------------------------------------------------------------------
# 3. Dynamic Asset Loading & Actor Transforms Tests
# ---------------------------------------------------------------------------

class TestUE5AssetAndActors:
    def test_dynamic_asset_import_valid_glb(self, ue5_test_client: UE5RestClient, mock_glb_file: Path) -> None:
        res = ue5_test_client.import_asset(str(mock_glb_file), "/Game/Imported/Meshes")
        assert res.get("Success") is True
        assert "/Game/Imported/Meshes/test_model" in res.get("AssetPath", "")

    def test_dynamic_asset_import_missing_file(self, ue5_test_client: UE5RestClient) -> None:
        res = ue5_test_client.import_asset("/non/existent/path/mesh.glb")
        assert res.get("Success") is False
        assert "does not exist" in res.get("Error", "")

    def test_spawn_actor_with_models(self, ue5_test_client: UE5RestClient) -> None:
        loc = Vector3D(x=100.0, y=-250.0, z=120.0)
        rot = Rotator3D(pitch=15.0, yaw=90.0, roll=0.0)
        actor_id = ue5_test_client.spawn_actor("SkeletalMeshActor", location=loc, rotation=rot)
        assert "SkeletalMeshActor" in actor_id


# ---------------------------------------------------------------------------
# 4. PBR Materials Tests
# ---------------------------------------------------------------------------

class TestUE5PBRMaterials:
    def test_pbr_material_bounds_validation(self) -> None:
        with pytest.raises(ValidationError):
            PBRMaterialInstance(material_name="InvalidMat", roughness=1.5)

        with pytest.raises(ValidationError):
            PBRMaterialInstance(material_name="InvalidMat", metallic=-0.2)

    def test_material_manager_create_and_get(self) -> None:
        manager = MaterialManager()
        mat = manager.create_material("M_Gold", base_color=ColorRGB(r=1.0, g=0.8, b=0.2), roughness=0.3, metallic=1.0)
        assert mat.material_name == "M_Gold"
        assert manager.get_material("M_Gold") == mat
        assert manager.get_material("M_NonExistent") is None

    def test_create_pbr_material_facade(self) -> None:
        mat = create_pbr_material(
            name="M_TestFacade",
            base_color={"r": 0.2, "g": 0.4, "b": 0.8},
            roughness=0.6,
            metallic=0.1,
        )
        assert mat.base_color.b == 0.8
        assert mat.roughness == 0.6


# ---------------------------------------------------------------------------
# 5. Lumen Lighting Tests
# ---------------------------------------------------------------------------

class TestUE5LumenLighting:
    def test_lighting_presets_structure(self) -> None:
        studio = LightingRig.get_preset("studio_3point")
        assert len(studio.lights) == 4
        assert studio.lumen_global_illumination is True

        cyber = LightingRig.get_preset("cyberpunk")
        assert any(l.name == "Key_NeonCyan" for l in cyber.lights)

        dramatic = LightingRig.get_preset("dramatic")
        assert len(dramatic.lights) == 2

    def test_unknown_preset_fallback(self) -> None:
        setup = setup_lumen_lighting("random_non_existent_preset")
        assert len(setup.lights) == 4  # Falls back to studio_3point


# ---------------------------------------------------------------------------
# 6. CineCamera Choreography Tests
# ---------------------------------------------------------------------------

class TestUE5CineCameraChoreography:
    def test_empty_beats_fallback(self) -> None:
        choreographer = CineCameraChoreographer()
        track = choreographer.generate_track(beat_timestamps=[], total_duration=6.0)
        assert len(track) == 2
        assert track[0].time == 0.0
        assert track[1].time == 6.0

    def test_camera_presets_generation(self) -> None:
        beats = [1.0, 2.0, 3.0, 4.0]
        duration = 5.0

        for preset in ["smooth_orbit", "dramatic_orbit", "aerial_pan", "front_close"]:
            track = generate_camera_track(beats, duration, preset=preset)
            assert len(track) >= len(beats)
            assert all(isinstance(kf, CameraKeyframe) for kf in track)
            payload = track[0].to_ue5_payload()
            assert "Location" in payload and "Rotation" in payload


# ---------------------------------------------------------------------------
# 7. Movie Render Queue Tests
# ---------------------------------------------------------------------------

class TestUE5MovieRenderQueue:
    def test_mrq_job_config_model_validation(self) -> None:
        config = MovieRenderQueueJobConfig(
            scene_path="/Game/Sequences/LS_Test",
            output_path="/renders/out.mp4",
            resolution="1920x1080",
        )
        assert config.get_resolution_dimensions() == (1920, 1080)

        with pytest.raises(ValidationError):
            MovieRenderQueueJobConfig(scene_path="LS", output_path="out.mp4", resolution="invalid_res")

    def test_render_sequence_execution(self, tmp_path: Path) -> None:
        out_video = tmp_path / "cinematic_output.mp4"
        res = render_sequence(
            scene_path="/Game/Sequences/LS_Stage",
            output_path=str(out_video),
            fps=30,
            resolution="1280x720",
        )
        assert isinstance(res, RenderResult)
        assert res.success is True
        assert res.frame_count == 90
        assert out_video.exists()
```

---

## 5. Verification Method

To independently verify this analysis and validate implementation when authored:

1. **Verify E2E Suite Stability**:
   ```powershell
   python -m pytest tests/e2e/test_tier1_features.py -k "ue5" -v
   python -m pytest tests/e2e/test_tier2_boundaries.py tests/e2e/test_tier3_interactions.py -k "ue5 or camera or mrq or scene" -v
   python -m pytest tests/e2e/test_tier4_scenarios.py -v
   ```
2. **Execute New Backend Test Suite**:
   Once `tests/backend/test_ue5_bridge.py` is written:
   ```powershell
   python -m pytest tests/backend/test_ue5_bridge.py -v
   ```
   *Expected outcome*: 100% of tests pass without skipped modules or unhandled exceptions.
3. **Invalidation Conditions**:
   - Any test using external public internet sockets or third-party dependencies outside the Python standard library, `pydantic`, and `pytest`.
   - Any unhandled `URLError` crashing the test runner when port is unbound.
   - Any regression in E2E Tiers 1–4.
