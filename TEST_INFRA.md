# IANIMATION E2E Testing Infrastructure & Methodology Specification

> **Document Version**: 1.0.0  
> **Status**: Official Testing Specification  
> **Target Framework**: Python 3.14+ / pytest / Standalone E2E Test Runner  
> **Standard Compliance**: SOLID, Zero-Any Policy (Pydantic v2 strict typing), Opaque-Box Verification  

---

## 1. Testing Philosophy & Architecture

The IANIMATION test architecture is constructed on **Opaque-Box, Requirements-Driven** principles. The test suites verify system behavior, public interface contracts, invariants, and edge cases solely through observable inputs, return values, file artifacts, and wire protocols—without coupling to private implementation internals.

```
+------------------------------------------------------------------------------------------------+
|                                4-TIER E2E TESTING ARCHITECTURE                                 |
+------------------------------------------------------------------------------------------------+
|  Tier 1: Feature Coverage (F-CORE, F-UE5, F-AI, F-MCP, F-UI, F-TEST, F-DOC)                   |
|  - Verifies each inventoried feature in isolation using synthetic fixtures.                    |
|  - Validates input validation, output schema compliance, and contract invariants.             |
+------------------------------------------------------------------------------------------------+
|  Tier 2: Boundary, Adversarial & Corner Cases                                                  |
|  - Empty / corrupt audio, images, videos, and meshes.                                          |
|  - Extreme BPM values (30 to 300), negative transforms, zero scales, unicode & path injection.|
|  - Network timeout simulation, disconnected sockets, and cancellation tokens.                 |
+------------------------------------------------------------------------------------------------+
|  Tier 3: Cross-Feature Interactions & Subsystem Handshakes                                     |
|  - Pairwise data flows: Audio Analysis -> Beat-Synced CineCamera Keyframing.                   |
|  - Image-to-3D GLB -> Auto-Rigging UE5 Mannequin Skeletal Hierarchy.                           |
|  - Auto-Rigging Mesh -> Video Mocap Motion Retargeting.                                        |
|  - Scene Configuration -> UE5 Remote Control Composition -> Movie Render Queue (MRQ).         |
|  - FastMCP Tool Invocation -> Plan Engine Confirmation Gates -> Telemetry Bus.                |
+------------------------------------------------------------------------------------------------+
|  Tier 4: Real-World Scenarios (End-to-End Orchestration)                                       |
|  - Complete pipeline execution: Reference Image + Audio Track + Dance Video -> Master Render.  |
|  - Human-in-the-Loop decision branch: Proposal -> User Modification/Approval -> Render Pass. |
|  - Offline fallback workflow: Local stubs executing when Cloud APIs or GPUs are unavailable.  |
+------------------------------------------------------------------------------------------------+
```

---

## 2. 4-Tier Testing Methodology

### Tier 1: Feature Coverage (Contract & Isolation Verification)
- **Objective**: Ensure that 100% of the inventoried features (F-CORE-01 through F-E2E-02) have at least one dedicated test exercising their core functionality and verifying output against the authoritative specifications.
- **Methodology**: Uses self-contained synthetic fixtures (in-memory or temporary files) to validate each feature in isolation.
- **Expected Derivation**: Ground-truth assertions based directly on `PROJECT.md` contracts, Pydantic v2 model schemas, and UE5/FastMCP protocol specifications.

### Tier 2: Boundary, Stress & Corner Cases
- **Objective**: Expose failure modes, edge conditions, resource constraints, and adversarial inputs.
- **Scope**:
  - **Zero / Empty Data**: 0-byte audio file, 0x0 pixel image, 0-frame video, empty scene actors.
  - **Malformed & Corrupt Data**: Truncated GLB binary header, random noise audio, invalid JSON-RPC packets.
  - **Domain Extremes**: Extremes in tempo (30 BPM, 300 BPM), zero/negative actor scale, out-of-bounds camera FOV.
  - **Transient Errors & Timeouts**: Simulated UE5 connection drop, socket ping timeout, cancellation token trigger.

### Tier 3: Cross-Feature Interactions (Subsystem Integration)
- **Objective**: Validate pairwise contracts, data serializations, and transitions across module boundaries.
- **Key Pairs**:
  - `F-AI-02` (Audio BPM) $\rightarrow$ `F-UE5-07` (CineCamera keyframe choreography).
  - `F-AI-05` (Image-to-3D GLB) $\rightarrow$ `F-AI-06` (Auto-Rigging armature).
  - `F-AI-06` (Rigged Mesh) $\rightarrow$ `F-AI-08` (Mocap animation sequence).
  - `F-UE5-04/05/06` (Assets, Materials, Lumen) $\rightarrow$ `F-UE5-08` (MRQ Video Render).
  - `F-MCP-01/02` (Atomic Tools) $\rightarrow$ `F-MCP-03/04` (Plan Engine with Human Approval).

### Tier 4: Real-World Scenarios (End-to-End Production)
- **Objective**: Execute multi-stage realistic production workflows replicating real user journeys.
- **Scenarios**:
  - **Scenario A (Standard Assisted Production)**: Ingest audio track + character concept $\rightarrow$ Plan generation $\rightarrow$ Human approval $\rightarrow$ 3D Mesh generation $\rightarrow$ Beat extraction $\rightarrow$ Camera choreography $\rightarrow$ MRQ Rendering $\rightarrow$ Output verification.
  - **Scenario B (Dance Animation with Mocap)**: Ingest video + audio $\rightarrow$ Mocap extraction $\rightarrow$ Auto-rigging $\rightarrow$ Animation retargeting $\rightarrow$ UE5 level sequence composition $\rightarrow$ Telemetry event verification.
  - **Scenario C (Local Fallback & Graceful Degradation)**: Complete run in environment without Cloud API keys or CUDA GPU, verifying procedural GLB and filterbank fallback logic.

---

## 3. Comprehensive Feature Coverage Matrix

Every feature defined in `PROJECT.md` is mapped to its test tier, test case identifier, and expected contract:

| Feature ID | Category | Feature Name | Tier 1 Test Case | Tier 2/3 Test Case | Tier 4 Scenario |
|------------|----------|--------------|-------------------|---------------------|-----------------|
| `F-CORE-01` | Core | Pydantic v2 Domain Models | `test_f_core_01_domain_models_schema` | `test_f_core_01_invalid_payload_validation` | `test_scenario_a_full_pipeline` |
| `F-CORE-02` | Core | Telemetry & Event Bus | `test_f_core_02_telemetry_event_dispatch` | `test_f_core_02_event_bus_backpressure` | `test_scenario_b_telemetry_flow` |
| `F-CORE-03` | Core | SHA-256 CAS Asset Cache | `test_f_core_03_cas_cache_put_get` | `test_f_core_03_cache_corrupt_entry_eviction` | `test_scenario_a_full_pipeline` |
| `F-CORE-04` | Core | Central Configuration | `test_f_core_04_app_config_defaults_and_env`| `test_f_core_04_invalid_env_types` | `test_scenario_c_offline_fallback` |
| `F-UE5-01` | UE5 | Remote Control REST Client | `test_f_ue5_01_rest_client_call_and_property`| `test_f_ue5_01_rest_server_error_responses` | `test_scenario_a_full_pipeline` |
| `F-UE5-02` | UE5 | Remote Control WebSocket | `test_f_ue5_02_websocket_rpc_and_subscribe` | `test_f_ue5_02_ws_reconnect_backoff` | `test_scenario_b_telemetry_flow` |
| `F-UE5-03` | UE5 | High-Fidelity Mock Server | `test_f_ue5_03_mock_server_lifecycle` | `test_f_ue5_03_mock_server_concurrency` | `test_scenario_a_full_pipeline` |
| `F-UE5-04` | UE5 | Dynamic Runtime Asset Loading | `test_f_ue5_04_dynamic_asset_import_glb_fbx`| `test_f_ue5_04_corrupt_glb_import_failure` | `test_scenario_a_full_pipeline` |
| `F-UE5-05` | UE5 | Dynamic PBR Materials | `test_f_ue5_05_pbr_material_assignment` | `test_f_ue5_05_missing_texture_fallback` | `test_scenario_a_full_pipeline` |
| `F-UE5-06` | UE5 | Lumen Lighting Rig Setup | `test_f_ue5_06_lumen_lighting_presets` | `test_f_ue5_06_unbound_postprocess_flag` | `test_scenario_a_full_pipeline` |
| `F-UE5-07` | UE5 | CineCamera Beat Choreography | `test_f_ue5_07_cinecamera_beat_sync` | `test_f_ue5_07_zero_beats_fallback` | `test_scenario_a_full_pipeline` |
| `F-UE5-08` | UE5 | Movie Render Queue (MRQ) | `test_f_ue5_08_mrq_job_submission_and_poll` | `test_f_ue5_08_render_timeout_detection` | `test_scenario_a_full_pipeline` |
| `F-AI-01` | AI | BaseAIProvider LSP & Registry | `test_f_ai_01_base_provider_registry` | `test_f_ai_01_unknown_provider_error` | `test_scenario_c_offline_fallback` |
| `F-AI-02` | AI | Audio BPM & Onset Extraction | `test_f_ai_02_audio_bpm_and_beat_grid` | `test_f_ai_02_silent_and_extreme_bpm` | `test_scenario_a_full_pipeline` |
| `F-AI-03` | AI | Audio 4-Stem Separation | `test_f_ai_03_stem_separation_demucs` | `test_f_ai_03_filterbank_fallback_cpu` | `test_scenario_a_full_pipeline` |
| `F-AI-04` | AI | Image-to-3D Cloud Adapters | `test_f_ai_04_image_to_3d_cloud_adapters` | `test_f_ai_04_api_key_missing_or_rate_limit`| `test_scenario_a_full_pipeline` |
| `F-AI-05` | AI | Procedural GLB Generator Stub | `test_f_ai_05_procedural_glb_cpu_stub` | `test_f_ai_05_1x1_and_monochrome_image` | `test_scenario_c_offline_fallback` |
| `F-AI-06` | AI | Auto-Rigging Engine | `test_f_ai_06_auto_rig_biped_armature` | `test_f_ai_06_non_biped_mesh_handling` | `test_scenario_b_telemetry_flow` |
| `F-AI-07` | AI | Mocap Video Background Removal| `test_f_ai_07_video_rotoscopy_rembg` | `test_f_ai_07_empty_video_handling` | `test_scenario_b_telemetry_flow` |
| `F-AI-08` | AI | 3D Pose Extraction & Dance | `test_f_ai_08_mediapipe_dance_loop` | `test_f_ai_08_zero_detections_procedural` | `test_scenario_b_telemetry_flow` |
| `F-AI-09` | AI | ComfyUI Neural Enhancer | `test_f_ai_09_comfyui_headless_client` | `test_f_ai_09_comfyui_unavailable_bypass` | `test_scenario_a_full_pipeline` |
| `F-AI-10` | AI | Async Supervisor & Cancel | `test_f_ai_10_async_engine_cancellation` | `test_f_ai_10_multiple_concurrent_tasks` | `test_scenario_a_full_pipeline` |
| `F-MCP-01` | FastMCP | 6 Atomic MCP Tools | `test_f_mcp_01_tool_registration_and_schemas`| `test_f_mcp_01_tool_invalid_args_rpc_error` | `test_scenario_a_full_pipeline` |
| `F-MCP-02` | FastMCP | Dual Invocation Architecture | `test_f_mcp_02_dual_invocation_parity` | `test_f_mcp_02_direct_call_exception_types` | `test_scenario_a_full_pipeline` |
| `F-MCP-03` | FastMCP | Production Plan Generation | `test_f_mcp_03_plan_generation_and_steps` | `test_f_mcp_03_invalid_goal_plan_rejection` | `test_scenario_a_full_pipeline` |
| `F-MCP-04` | FastMCP | Human-in-the-Loop Approval | `test_f_mcp_04_confirmation_gate_workflow`| `test_f_mcp_04_rejected_step_halts_pipeline`| `test_scenario_a_full_pipeline` |
| `F-MCP-05` | FastMCP | Real-Time Telemetry Streaming | `test_f_mcp_05_telemetry_streaming_sse_ws` | `test_f_mcp_05_slow_client_backpressure` | `test_scenario_b_telemetry_flow` |
| `F-UI-01` | UI | Tauri v2 Architecture Contract| `test_f_ui_01_tauri_config_and_rust_bridge`| `test_f_ui_01_window_bounds_validation` | `test_scenario_a_full_pipeline` |
| `F-UI-02` | UI | Drag-and-Drop Media Dropzone | `test_f_ui_02_media_dropzone_contract` | `test_f_ui_02_unsupported_file_extensions` | `test_scenario_a_full_pipeline` |
| `F-UI-03` | UI | Multi-Track Timeline Contract | `test_f_ui_03_timeline_tracks_and_markers`| `test_f_ui_03_scrub_boundary_clamps` | `test_scenario_a_full_pipeline` |
| `F-UI-04` | UI | 3D Viewport Three.js Preview | `test_f_ui_04_viewport_threejs_contract` | `test_f_ui_04_corrupt_asset_viewport_error` | `test_scenario_a_full_pipeline` |
| `F-UI-05` | UI | 3D Viewport Pixel Streaming | `test_f_ui_05_pixel_streaming_interface` | `test_f_ui_05_webrtc_signaling_loss` | `test_scenario_a_full_pipeline` |
| `F-UI-06` | UI | Copilot Chat & Approval Cards | `test_f_ui_06_copilot_chat_approval_cards`| `test_f_ui_06_rapid_user_actions` | `test_scenario_a_full_pipeline` |
| `F-UI-07` | UI | Intermediate Asset Cards | `test_f_ui_07_intermediate_asset_cards` | `test_f_ui_07_missing_thumbnail_fallback` | `test_scenario_a_full_pipeline` |
| `F-UI-08` | UI | Zustand Store & Zod Validation| `test_f_ui_08_zustand_store_zod_schema` | `test_f_ui_08_zod_runtime_type_coercion` | `test_scenario_a_full_pipeline` |
| `F-TEST-01` | Testing| Backend pytest Suites | `test_f_test_01_backend_test_suite_status`| `test_f_test_01_flaky_test_resilience` | `test_scenario_a_full_pipeline` |
| `F-TEST-02` | Testing| Frontend Vitest Component Tests| `test_f_test_02_frontend_test_suite_status`| `test_f_test_02_component_render_errors` | `test_scenario_a_full_pipeline` |
| `F-TEST-03` | Testing| verify_pipeline.py CLI Script | `test_f_test_03_verify_pipeline_cli_exec` | `test_f_test_03_verify_pipeline_error_exit`| `test_scenario_a_full_pipeline` |
| `F-DOC-01` | Docs | README & MCP Tool Catalog | `test_f_doc_01_documentation_completeness`| `test_f_doc_01_schema_mismatch_check` | `test_scenario_a_full_pipeline` |
| `F-E2E-01` | E2E | 100% Pass of E2E Tiers 1-4 | `test_f_e2e_01_suite_pass_threshold` | `test_f_e2e_01_zero_unhandled_exceptions` | `test_scenario_a_full_pipeline` |
| `F-E2E-02` | E2E | Adversarial Hardening (Tier 5)| `test_f_e2e_02_adversarial_stress_pass` | `test_f_e2e_02_fuzz_parameter_injection` | `test_scenario_a_full_pipeline` |

---

## 4. Synthetic Fixture Architecture

To ensure 100% offline determinism and eliminate dependencies on external web services or heavy binary assets, all test fixtures are generated programmatically using standard library formats:

1. **Synthetic Audio Generator (`tests/e2e/fixtures/synthetic_audio.py`)**:
   - Generates valid IEEE PCM `.wav` files via Python's standard `wave` and `struct` modules.
   - Configurable sample rate ($44.1\,\text{kHz}$), duration, channels (mono/stereo), and pulse/tone modes.
   - Includes rhythmic transient pulses at exact BPM rates (e.g. 120.0 BPM, 60.0 BPM, 180.0 BPM) for exact beat detection validation.
   - Generates silent tracks, white-noise tracks, and corrupt WAV headers.

2. **Synthetic Image Generator (`tests/e2e/fixtures/synthetic_image.py`)**:
   - Generates valid binary `.png` and `.jpg` image files via standard library / zlib.
   - Standard 512x512 RGBA character silhouette texture.
   - Boundary images: 1x1 pixel image, corrupt PNG chunk, zero-byte file, high-contrast black/white mask.

3. **Synthetic 3D Mesh Generator (`tests/e2e/fixtures/synthetic_mesh.py`)**:
   - Generates strictly compliant binary glTF 2.0 (`.glb`) files without third-party dependencies.
   - Includes JSON chunk, binary buffer chunk, standard vertex positions, normals, UVs, and indices for a standard 3D cube or humanoid biped mesh.
   - Generates corrupt GLB headers, truncated buffers, and missing chunk lengths for boundary testing.

4. **Synthetic Video & Dance Sequence Generator (`tests/e2e/fixtures/synthetic_video.py`)**:
   - Generates lightweight synthetic MP4 video containers or frame sequences for mocap testing.
   - Provides mock pose landmarks (33 body keypoints conforming to MediaPipe Pose specification).

---

## 5. Standalone Test Runner Specification (`tests/e2e/runner.py`)

The standalone test runner is executable independently from `pytest` or alongside it:

```bash
# Execute via standalone runner
python -m tests.e2e.runner --tier all --verbose

# Execute specific tier
python -m tests.e2e.runner --tier 1
python -m tests.e2e.runner --tier 2
python -m tests.e2e.runner --tier 3
python -m tests.e2e.runner --tier 4

# Execute via standard pytest
pytest tests/e2e -v --tb=short
```

### Output Contracts
- Colored ANSI console summary table.
- JSON metrics report output (`tests/e2e/reports/e2e_results.json`).
- Exit codes:
  - `0`: All tests passed or gracefully skipped due to pending milestone implementation.
  - `1`: Contract violation, unexpected assertion error, or regression in implemented features.

---

## 6. Pass/Fail Thresholds & Escalation Protocol

- **Zero-Tolerance Criteria**:
  1. No unhandled crashes or unformatted Python tracebacks.
  2. Any implemented module violating Pydantic v2 schemas or the Zero-Any policy triggers immediate failure.
  3. No network calls to public internet during offline test execution.
- **Progressive Milestone Testing**:
  When a backend milestone has not yet been implemented by the corresponding implementation worker, tests check for the presence of the module. If absent, the runner logs `PENDING_IMPLEMENTATION` and continues, avoiding test suite blocking while maintaining full requirement readiness. When the module lands, the test executes the full opaque-box verification.
