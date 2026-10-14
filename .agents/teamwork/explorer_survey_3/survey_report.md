# Architectural Survey & Specification Report: R3 (Tauri Desktop App) & Verification Suites

**Project**: IANIMATION — 3D & AI Animation Orchestrator  
**Author**: Survey Agent 3 (Explorer - Desktop UI & Verification Architecture)  
**Date**: 2026-10-14  
**Target Milestone**: Survey & Architectural Specification (R3 Desktop UI & Verification Suites)  
**Status**: Comprehensive & Authoritative Survey Report  

---

## 1. Executive Summary & Architectural Scope

The IANIMATION desktop application delivers a unified, production-grade workstation for orchestrating generative 3D pipelines (Image-to-3D, Rigging, Mocap, Audio Reactivity, Neural Enhancements) and directing Unreal Engine 5 via FastMCP (Model Context Protocol). 

This report delivers the authoritative design, component contracts, testing architecture, and verification specifications for:
1. **R3: Native Desktop Workstation in Tauri (Rust + React 18+ / TypeScript)**.
2. **Verification Suites & Testing Architecture**: Automated backend `pytest` suite, frontend Vitest / React Testing Library suite, end-to-end simulation CLI (`verify_pipeline.py`), and rigorous visual verification protocols according to `GEMINI.md`.

### System Toolchain Verification (Host Environment)
The host development environment was probed directly and confirmed operational:
- **Node.js**: `v24.16.0` (LTS/Current runtime)
- **npm**: `12.0.2`
- **Rust / Cargo**: `rustc 1.96.0` / `cargo 1.96.0`
- **Tauri CLI**: `@tauri-apps/cli 2.12.2` (Tauri v2 ready via npx)
- **Python**: `3.14.6` with `pip 26.2.1`
- **Installed Key Packages**: `pydantic 2.12.5`, `pytest 9.1.1`, `mcp 1.30.0`, `torch 2.14.0`, `torchaudio 2.11.0`, `demucs 4.1.0`, `diffusers 0.41.0`, `scipy 1.18.1`, `numpy 2.5.1`, `websockets 15.0.1`, `uvicorn 0.51.0`, `starlette 1.3.1`.

---

## 2. R3: Tauri Desktop Application Architecture

```
+-----------------------------------------------------------------------------------+
|                           IANIMATION TAURI DESKTOP APP                             |
+-----------------------------------------------------------------------------------+
|  [Header / Project Titlebar] [Backend Status: FastMCP OK | UE5 Remote Control OK] |
+------------------------------------+----------------------------------------------+
|             LEFT PANE              |                  RIGHT PANE                  |
|                                    |                                              |
|  +------------------------------+  |  +----------------------------------------+  |
|  |     Media Dropzone & Tray    |  |  |           Copilot Chat Console         |  |
|  |  [Drop Image / Audio / Video]|  |  | - Step-by-Step Production Plan         |  |
|  |  [Asset Cards: .png/.wav/.mp4]  | - Human Confirmation (Proceed/Mod/Cancel)|  |
|  +------------------------------+  |  | - Live Execution Log Stream (SSE/WS)   |  |
|                                    |  | - Intermediate Asset Cards (3D/Stems)  |  |
|  +------------------------------+  |  +----------------------------------------+  |
|  |     3D Preview Viewport      |  |                                              |
|  |  - Three.js WebGL / Babylon  |  |                                              |
|  |  - WebRTC Pixel Stream Embed |  |                                              |
|  |  - Orbit / Lighting / Gizmo  |  |                                              |
|  +------------------------------+  |                                              |
+------------------------------------+----------------------------------------------+
|                                    BOTTOM PANE                                    |
|  +-----------------------------------------------------------------------------+  |
|  |                      Multi-Track Audiovisual Timeline                       |  |
|  |  [Transport Controls: Play/Pause/Scrub] [Timecode: 00:01:24:12] [Zoom +/-]   |  |
|  |  Track 1: Audio Waveform (Librosa peaks, Beat markers, Onset transients)     |  |
|  |  Track 2: CineCamera Shot Cuts & Keyframe markers                           |  |
|  |  Track 3: 3D Character Mocap Clips (GVHMR motion blocks)                    |  |
|  |  Track 4: Neural VFX Pass Keyframes (ComfyUI render triggers)                |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

### 2.1 Rust Core & Tauri v2 Architecture
The desktop shell utilizes **Tauri v2** (`src-tauri/`) for optimal binary size, zero-overhead memory footprint, and native OS integration:
- **`src-tauri/Cargo.toml` Core Dependencies**:
  - `tauri = { version = "2.0", features = ["tray-icon"] }`
  - `tauri-plugin-fs = "2.0"` (secure file access for intermediate assets)
  - `tauri-plugin-dialog = "2.0"` (native file picker dialog)
  - `tauri-plugin-shell = "2.0"` (subprocess management for Python FastMCP server if launched as sidecar)
  - `serde = { version = "1.0", features = ["derive"] }`
  - `serde_json = "1.0"`
  - `tokio = { version = "1.0", features = ["full"] }`
- **`tauri.conf.json` Key Configuration**:
  - App ID: `com.ianimation.orchestrator`
  - Window defaults: `1440x900` minimum resolution, dark window titlebar, native decorations enabled.
  - CSP: Configured to permit local WebSockets (`ws://localhost:*`), FastMCP SSE streams (`http://localhost:*`), and WebRTC ICE servers for Pixel Streaming.
  - Multi-Window Architecture: Support for detaching the 3D Preview Viewport into a synchronized secondary slave window for multi-monitor production setups.
- **Tauri IPC Command Contracts**:
  - `cmd_pick_media_files(allowed_extensions: Vec<String>) -> Result<Vec<MediaFileMetadata>, String>`
  - `cmd_get_workspace_path() -> Result<String, String>`
  - `cmd_open_output_folder(path: String) -> Result<(), String>`
  - `cmd_check_backend_health() -> Result<BackendHealthStatus, String>`
  - `cmd_compute_file_checksum(file_path: String) -> Result<String, String>`

### 2.2 Frontend Stack & Zero-Any Policy
In strict compliance with `GEMINI.md`:
- **TypeScript Configuration (`tsconfig.json`)**:
  ```json
  {
    "compilerOptions": {
      "target": "ES2022",
      "lib": ["DOM", "DOM.Iterable", "ES2022"],
      "module": "ESNext",
      "moduleResolution": "bundler",
      "strict": true,
      "noImplicitAny": true,
      "strictNullChecks": true,
      "strictFunctionTypes": true,
      "strictBindCallApply": true,
      "strictPropertyInitialization": true,
      "noImplicitThis": true,
      "alwaysStrict": true,
      "noUnusedLocals": true,
      "noUnusedParameters": true,
      "noImplicitReturns": true,
      "noFallthroughCasesInSwitch": true,
      "noUncheckedIndexedAccess": true,
      "exactOptionalPropertyTypes": true,
      "skipLibCheck": true
    }
  }
  ```
- **Runtime Validation via Zod v3**: Every incoming IPC message, WebSocket event, and MCP tool response is parsed through a strict Zod schema before state mutation.
- **Discriminated Unions**: All state transitions, message types, timeline tracks, and tool statuses use discriminated string literals (e.g. `type: "audio" | "image" | "video"`, `status: "idle" | "running" | "waiting_confirmation" | "completed" | "error"`).

---

## 3. UI Component Specifications

### 3.1 Drag-and-Drop Media Dropzone (`MediaDropzone.tsx`)
A versatile, intuitive media staging component supporting drag-and-drop or manual file picking for reference assets.

#### 1. Supported File Formats & MIME Validation
- **Images**: `.png`, `.jpg`, `.jpeg`, `.webp` (Image-to-3D reference, character concept art).
- **Audio**: `.wav`, `.mp3` (Master track for Librosa BPM analysis, beat grid, Demucs stem separation).
- **Video**: `.mp4`, `.mov` (Dance / motion reference for GVHMR/4DHumans mocap extraction).

#### 2. Visual States & Interactivity
- **Idle State**: Dashed high-contrast border (`border-zinc-700`), centered iconography (upload cloud, musical note, cube, film roll), clear prompt text ("Drag & drop media files or click to browse").
- **Drag-Over State**: Glowing animated neon border (`border-indigo-500 bg-indigo-950/20`), pulsing drop icon, active format badges highlighting matching file types.
- **Drag-Reject State**: Red border (`border-rose-500 bg-rose-950/20`), warning message ("Unsupported format. Allowed: .png, .jpg, .wav, .mp3, .mp4").
- **Processing / Staged State**: Progress indicators during metadata extraction, transitioning to Asset Registry Cards.

#### 3. Metadata Extraction & Preview Cards
Upon drop:
- Image: Thumbnail rendering, resolution (`width x height`), aspect ratio calculation, color palette preview.
- Audio: Duration in seconds/frames, sample rate (e.g., `44.1kHz`), channel count, client-side mini-waveform preview using Web Audio API `AudioContext.decodeAudioData`.
- Video: First-frame thumbnail extraction via offscreen `<video>` + `<canvas>`, duration, framerate, video dimensions.
- Asset Card Actions: Quick preview modal, "Send to Copilot Context", remove/replace asset button.

### 3.2 Multi-Track Audiovisual Timeline (`Timeline.tsx`)
A responsive, high-performance timeline editor with sub-frame precision, designed for synchronization between audio transients, camera shots, mocap clips, and neural effects.

#### 1. Multi-Track Layout
- **Track 1: Master Audio Track (`AudioTrack.tsx`)**:
  - Waveform canvas rendering using high-density peak arrays (precomputed by Librosa backend or generated on client).
  - Beat markers: Vertical dashed neon lines (cyan for onsets, gold/yellow for downbeats based on analyzed BPM).
  - Audio sections: Color-coded timeline spans (Intro, Verse, Build-up, Drop, Outro).
- **Track 2: CineCamera Track (`CameraTrack.tsx`)**:
  - Shot boundary cut markers indicating camera switches.
  - Camera keyframes (focal length, camera target, FOV, aperture).
- **Track 3: 3D Character & Mocap Track (`MocapTrack.tsx`)**:
  - Draggable, resizable animation clip blocks representing extracted GVHMR mocap clips.
  - Clip trimming handles, speed multiplier badges (1.0x, 0.5x), root motion offset controls.
- **Track 4: Neural VFX Pass Track (`VfxTrack.tsx`)**:
  - Keyframe triggers for ComfyUI post-processing passes (AnimateDiff style transitions, Wan 2.1 upscale).

#### 2. Interactive Navigation & Transport Controls
- **Playhead**: Scrubbable vertical red bar with timestamp pill showing `HH:MM:SS:FF` (at 24/30/60 fps).
- **Scrubbing Engine**: Sub-frame scrub support powered by `requestAnimationFrame`, smoothly synchronizing the 3D viewport preview and audio playback.
- **Zoom & Pan Engine**:
  - Mouse wheel zoom (`Ctrl + Wheel` or trackpad pinch) scaling from micro-view (single frames) to macro-view (entire track duration).
  - Horizontal panning via middle mouse drag or horizontal scrollbar.
  - Snapping system: Magnetic snapping to audio beat markers, shot cuts, or grid frames (toggleable with `S` key).
- **Transport Bar**: Play/Pause (`Space`), Return to Zero (`Home` / `0`), Loop In/Out markers (`I` / `O`), Framerate selector (24, 30, 60 fps).

### 3.3 3D Preview Viewport (`PreviewViewport.tsx`)
A flexible, dual-mode 3D viewport rendering generated assets immediately or streaming from Unreal Engine 5.

#### 1. Dual-Mode Architecture
- **Mode A: Embedded WebGL/WebGPU Canvas (Three.js / Babylon.js)**:
  - Instant standalone rendering of generated `.glb` meshes without requiring Unreal Engine to be open.
  - Bone & Skeleton visualizer: Overlay bone joints and hierarchy for auto-rigged meshes.
  - Animation Mixer: Direct playback of extracted mocap animation clips applied to the rigged mesh, locked to the Timeline playhead!
  - PBR Shader Material preview: Albedo, Metallic, Roughness, Normal maps.
  - Studio Environment: HDRI ambient lighting, ground grid, directional key/fill lights, shadow maps.
  - Camera OrbitControls: Smooth orbit, pan, zoom, frame-selected (`F` key).
- **Mode B: WebRTC Pixel Streaming Receiver**:
  - Connects to Unreal Engine 5's Pixel Streaming signaling server via WebRTC.
  - Receives high-fidelity Lumen & Nanite rendered stream directly in the viewport canvas.
  - Bidirectional input forwarding: Mouse drag and keyboard commands sent to UE5 Remote Control / Pixel Streaming input channel.
  - Offline Fallback / Mock Stream: Displays simulated UE5 viewport raster or test pattern with server health indicators when UE5 is offline.
- **Mode C: Synchronized Slave Window**:
  - Supports spawning a detached Tauri window for full-screen secondary monitor preview.

#### 2. Viewport Toolbar
- Camera Selection: Free Perspective, Front, Side, Top, CineCamera_01 (locked to UE5 camera).
- Display Mode: Lit (PBR), Unlit, Wireframe, Normal Map, Bone Skeleton.
- Transform Gizmo: Translate, Rotate, Scale widgets.

### 3.4 Copilot Chat Console & Human-in-the-Loop Workflow (`CopilotConsole.tsx`)
An interactive, intelligent control center that turns natural language directions into verifiable FastMCP execution plans.

#### 1. Step-by-Step Guided Workflow
- Conversational chat interface connected to the FastMCP backend.
- Displays structured Production Execution Plans (`ExecutionPlan`) generated by the Copilot agent:
  ```json
  {
    "plan_id": "plan_98241",
    "title": "Audiovisual Cinematic Dance Animation",
    "steps": [
      { "id": 1, "tool": "analyze_audio", "title": "Audio BPM & Beat Analysis", "status": "completed" },
      { "id": 2, "tool": "image_to_3d", "title": "Generate 3D Character Mesh (.glb)", "status": "waiting_confirmation" },
      { "id": 3, "tool": "auto_rig", "title": "Biped Auto-Rigging & Skinning", "status": "pending" },
      { "id": 4, "tool": "extract_mocap", "title": "Video Motion Capture Extraction", "status": "pending" },
      { "id": 5, "tool": "build_ue5_scene", "title": "UE5 Scene Assembly & Lighting", "status": "pending" },
      { "id": 6, "tool": "render_video", "title": "Movie Render Queue High-Res Export", "status": "pending" }
    ]
  }
  ```

#### 2. Human Confirmation Interceptor Card (`ConfirmationCard.tsx`)
Before executing any heavy, costly, or irreversible operation (e.g., Cloud GPU inference, Auto-rigging, UE5 4K MRQ render), execution pauses and displays an interactive Human Confirmation Card:
- **Visual Alert**: Amber / Cyan illuminated card with tool name, execution context, and resource impact estimation (estimated runtime, API token/GPU cost).
- **Parameter Summary**: Collapsible view of tool arguments (e.g., target mesh resolution, skeleton type, camera focal length).
- **Action Buttons**:
  - `[ Proceed / Confirm ]` (Primary Green): Approves execution; triggers FastMCP tool RPC.
  - `[ Modify Parameters ]` (Secondary Blue): Opens quick parameter adjustment sheet (e.g. changing render resolution from 4K to 1080p, selecting local vs cloud backend).
  - `[ Cancel / Skip ]` (Destructive Red): Cancels the step or aborts the production plan safely.

#### 3. Real-Time Execution Log Stream (`ExecutionLogs.tsx`)
- Terminal-style collapsible log panel streaming FastMCP tool stdout, stderr, and telemetry events via WebSocket / SSE.
- Real-time progress bar (`0% -> 100%`) with task milestone notifications (e.g. `Downloading weights 45%`, `Solving inverse kinematics frame 120/300`).
- Filtering controls: All, Info, Warnings, Errors, Tool Calls. Auto-scroll with toggle.

#### 4. Rich Intermediate Asset Cards (`AssetCard.tsx`)
Rendered directly within the chat message stream:
- **Audio Stems Card**: Individual track playback for separated vocals, drums, bass, and instrumental stems with solo/mute buttons.
- **3D Mesh Card**: Interactive 3D thumbnail of generated `.glb` mesh with polycount (vertex/triangle count), PBR texture preview, "Load in Viewport" button, and "Send to UE5" action.
- **Mocap Clip Card**: 3D skeleton animation mini-player showing extracted motion loop, frame count, and FPS.
- **Cinematic Render Card**: Final MP4 preview player with seekbar, download button, and "Open in Explorer" shortcut.

---

## 4. Strict TypeScript Data Contracts & Zod Schemas

To satisfy the **Zero-Any Policy** and ensure end-to-end type safety between frontend, Tauri Rust IPC, and the Python FastMCP backend, the following schemas are formally specified:

```typescript
import { z } from "zod";

// --- 1. Media Assets ---
export const AssetTypeSchema = z.enum(["image", "audio", "video", "mesh_3d", "mocap"]);
export type AssetType = z.infer<typeof AssetTypeSchema>;

export const MediaAssetSchema = z.z.object({
  id: z.string().uuid(),
  name: z.string().min(1),
  filePath: z.string(),
  fileSize: z.number().int().nonnegative(),
  mimeType: z.string(),
  type: AssetTypeSchema,
  metadata: z.discriminatedUnion("type", [
    z.object({
      type: z.literal("image"),
      width: z.number().int().positive(),
      height: z.number().int().positive(),
      aspectRatio: z.number().positive(),
      thumbnailDataUrl: z.string().optional(),
    }),
    z.object({
      type: z.literal("audio"),
      durationSeconds: z.number().positive(),
      sampleRate: z.number().int().positive(),
      channels: z.number().int().positive(),
      bpm: z.number().positive().optional(),
      waveformPeaks: z.array(z.number()).optional(),
    }),
    z.object({
      type: z.literal("video"),
      durationSeconds: z.number().positive(),
      fps: z.number().positive(),
      width: z.number().int().positive(),
      height: z.number().int().positive(),
      thumbnailDataUrl: z.string().optional(),
    }),
    z.object({
      type: z.literal("mesh_3d"),
      vertexCount: z.number().int().nonnegative(),
      triangleCount: z.number().int().nonnegative(),
      hasRig: z.boolean(),
      format: z.enum(["glb", "fbx", "obj"]),
    }),
    z.object({
      type: z.literal("mocap"),
      frameCount: z.number().int().positive(),
      fps: z.number().positive(),
      boneCount: z.number().int().positive(),
    }),
  ]),
  createdAt: z.string().datetime(),
});
export type MediaAsset = z.infer<typeof MediaAssetSchema>;

// --- 2. Multi-Track Timeline ---
export const KeyframeSchema = z.object({
  id: z.string().uuid(),
  timeSeconds: z.number().nonnegative(),
  frameNumber: z.number().int().nonnegative(),
  property: z.string(),
  value: z.union([z.number(), z.string(), z.record(z.unknown())]),
  interpolation: z.enum(["linear", "bezier", "step"]),
});
export type Keyframe = z.infer<typeof KeyframeSchema>;

export const BeatMarkerSchema = z.object({
  id: z.string().uuid(),
  timeSeconds: z.number().nonnegative(),
  beatNumber: z.number().int().positive(),
  isDownbeat: z.boolean(),
  strength: z.number().min(0).max(1),
});
export type BeatMarker = z.infer<typeof BeatMarkerSchema>;

export const TrackTypeSchema = z.enum(["audio", "camera", "mocap", "vfx"]);
export type TrackType = z.infer<typeof TrackTypeSchema>;

export const TimelineTrackSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  type: TrackTypeSchema,
  isMuted: z.boolean(),
  isLocked: z.boolean(),
  colorHex: z.string().regex(/^#[0-9A-Fa-f]{6}$/),
  keyframes: z.array(KeyframeSchema),
  clips: z.array(
    z.object({
      id: z.string().uuid(),
      assetId: z.string().uuid(),
      startTimeSeconds: z.number().nonnegative(),
      durationSeconds: z.number().positive(),
      offsetSeconds: z.number().nonnegative(),
      speedMultiplier: z.number().positive(),
    })
  ),
});
export type TimelineTrack = z.infer<typeof TimelineTrackSchema>;

// --- 3. Copilot & Human-in-the-Loop ---
export const PlanStepStatusSchema = z.enum([
  "pending",
  "waiting_confirmation",
  "running",
  "completed",
  "failed",
  "skipped",
]);
export type PlanStepStatus = z.infer<typeof PlanStepStatusSchema>;

export const PlanStepSchema = z.object({
  stepIndex: z.number().int().nonnegative(),
  toolName: z.enum([
    "analyze_audio",
    "image_to_3d",
    "auto_rig",
    "extract_mocap",
    "build_ue5_scene",
    "render_video",
  ]),
  title: z.string(),
  description: z.string(),
  status: PlanStepStatusSchema,
  parameters: z.record(z.unknown()),
  estimatedDurationSeconds: z.number().positive().optional(),
  requiresHumanConfirmation: z.boolean(),
  resultAssetId: z.string().uuid().optional(),
  error: z.string().optional(),
});
export type PlanStep = z.infer<typeof PlanStepSchema>;

export const ExecutionPlanSchema = z.object({
  planId: z.string().uuid(),
  prompt: z.string(),
  steps: z.array(PlanStepSchema),
  createdAt: z.string().datetime(),
  totalEstimatedSeconds: z.number().positive().optional(),
});
export type ExecutionPlan = z.infer<typeof ExecutionPlanSchema>;

export const HumanConfirmationDecisionSchema = z.discriminatedUnion("decision", [
  z.object({
    decision: z.literal("proceed"),
    planId: z.string().uuid(),
    stepIndex: z.number().int().nonnegative(),
  }),
  z.object({
    decision: z.literal("modify"),
    planId: z.string().uuid(),
    stepIndex: z.number().int().nonnegative(),
    modifiedParameters: z.record(z.unknown()),
  }),
  z.object({
    decision: z.literal("cancel"),
    planId: z.string().uuid(),
    stepIndex: z.number().int().nonnegative(),
    reason: z.string(),
  }),
]);
export type HumanConfirmationDecision = z.infer<typeof HumanConfirmationDecisionSchema>;

export const LogLevelSchema = z.enum(["debug", "info", "warn", "error"]);
export type LogLevel = z.infer<typeof LogLevelSchema>;

export const LogEntrySchema = z.object({
  id: z.string().uuid(),
  timestamp: z.string().datetime(),
  level: LogLevelSchema,
  source: z.enum(["fastmcp", "ue5_remote", "ai_pipeline", "frontend"]),
  message: z.string(),
  progressPercent: z.number().min(0).max(100).optional(),
});
export type LogEntry = z.infer<typeof LogEntrySchema>;
```

---

## 5. Verification Suites & Testing Architecture

To satisfy acceptance criteria, tests must be automated across backend, frontend, and full system integration.

```
+-----------------------------------------------------------------------------------+
|                        IANIMATION VERIFICATION PYRAMID                            |
+-----------------------------------------------------------------------------------+
|               [Tier 4: verify_pipeline.py E2E Simulation CLI]                    |
|               (Full 9-Phase Audio -> 3D -> Mocap -> UE5 -> Render)                |
+-----------------------------------------------------------------------------------+
|            [Tier 3: Visual Verification & Layout Integrity Tests]                 |
|            (Component alignment, contrast, waveform sharp rendering)             |
+-----------------------------------------------------------------------------------+
|         [Tier 2: Frontend Vitest + React Testing Library Tests]                   |
|         (Dropzone validation, Timeline scrub, Copilot confirm buttons)            |
+-----------------------------------------------------------------------------------+
|           [Tier 1: Backend pytest Unit & Integration Suites]                      |
|           (FastMCP tool schemas, Mock UE5 REST/WS, AI pipeline fallbacks)         |
+-----------------------------------------------------------------------------------+
```

### 5.1 Automated Backend Unit & Integration Tests (`pytest`)
- **Location**: `tests/backend/`
- **Execution Command**: `pytest -v tests/backend`
- **Structure**:
  - `tests/backend/test_fastmcp_tools.py`:
    - Validates FastMCP tool registration and JSON Schema conformity.
    - Validates atomic tools: `analyze_audio`, `image_to_3d`, `auto_rig`, `extract_mocap`, `build_ue5_scene`, `render_video`.
    - Verifies Pydantic v2 validation errors on malformed inputs.
  - `tests/backend/test_mock_ue5_server.py`:
    - Tests the REST mock server (`/remote/object/call`, `/remote/object/property`, `/remote/batch`).
    - Tests WebSocket `/remote/protocol` connection, handshake, subscription, and event broadcasts.
    - Verifies GLB/FBX runtime asset loading mock RPC response format.
    - Verifies CineCamera transform updates and Movie Render Queue (MRQ) job execution mock.
  - `tests/backend/test_ai_pipeline_adapters.py`:
    - Audio analyzer: Processes synthetic WAV fixture, verifies BPM, beat timestamps, and onset strength array.
    - Cloud vs. Local fallback: Tests graceful fallback when cloud API credentials are dummy or unreachable.
  - `tests/backend/test_copilot_orchestrator.py`:
    - Validates execution plan generation.
    - Tests Human-in-the-Loop gate: ensures execution suspends until confirmation signal (`Proceed`) is received.

### 5.2 Frontend Component Unit Tests (Vitest + React Testing Library)
- **Location**: `tests/frontend/`
- **Execution Command**: `npm run test` (or `npx vitest run`)
- **Key Test Suites**:
  1. `tests/frontend/MediaDropzone.test.tsx`:
     - Renders idle state with correct format badges.
     - Simulates drag-enter and verifies active visual classes.
     - Simulates drop of valid `.png`, `.wav`, and `.mp4` files; verifies metadata extraction callback fires with validated `MediaAsset` objects.
     - Simulates drop of invalid `.exe` or `.txt` file; verifies visual error alert and rejection.
  2. `tests/frontend/Timeline.test.tsx`:
     - Mounts timeline canvas and renders waveform without DOM exceptions.
     - Verifies beat markers align with time ruler markers.
     - Simulates playhead scrub drag; verifies `useTimelineStore` updates `currentTimeSeconds`.
     - Tests zoom in / zoom out controls and clamps minimum/maximum scale bounds.
     - Tests keyboard shortcut handling (`Space` toggles play/pause, `Home` resets playhead).
  3. `tests/frontend/CopilotConsole.test.tsx`:
     - Renders chat message history and structured `ExecutionPlan` steps.
     - Validates Human Confirmation Card display when step is `waiting_confirmation`.
     - Clicks `Proceed` button; verifies RPC dispatch payload.
     - Clicks `Modify` button; verifies parameter edit drawer triggers.
     - Clicks `Cancel` button; verifies cancellation event dispatch.
     - Simulates incoming WebSocket log stream; verifies progress bar update and auto-scroll behavior.
  4. `tests/frontend/PreviewViewport.test.tsx`:
     - Mounts 3D canvas and handles ResizeObserver cleanly.
     - Verifies mode switching between Three.js WebGL mode and Pixel Streaming WebRTC mode.
     - Verifies camera view preset toolbar buttons (Perspective, Top, CineCamera).

### 5.3 End-to-End Simulation CLI (`verify_pipeline.py`)
A comprehensive, standalone verification script designed to simulate the complete production workflow from input files to final cinematic render without manual human interaction, validating the full system contract.

#### Execution Interface
```bash
python verify_pipeline.py --mode=autonomous --mock-ue5 --output-dir=./artifacts/e2e_output --report=e2e_report.json
```

#### 9-Phase Lifecycle Execution:
1. **Phase 1: Environment & Dependency Sanity Check**:
   - Verifies Python environment, Pydantic v2, pytest, FastMCP server, and mock UE5 server availability.
2. **Phase 2: Synthetic Fixture Staging**:
   - Synthesizes a valid test WAV file (`test_beat_120bpm.wav`, 440Hz pulse at 120 BPM).
   - Generates a valid test character image (`test_character.png`, 512x512 RGBA).
   - Synthesizes a valid test reference video (`test_motion.mp4`).
3. **Phase 3: FastMCP Audio Analysis (`analyze_audio`)**:
   - Calls tool with `test_beat_120bpm.wav`.
   - Asserts: BPM extracted within `120.0 +/- 2.0`, onsets count > 0, duration matches file.
4. **Phase 4: FastMCP Image-to-3D (`image_to_3d`)**:
   - Calls tool with `test_character.png`.
   - Asserts: Outputs valid `.glb` file, binary header matches `glTF` magic bytes (`0x46546C67`), non-zero byte size.
5. **Phase 5: FastMCP Auto-Rigging (`auto_rig`)**:
   - Calls tool with generated `.glb`.
   - Asserts: Outputs rigged `.glb` with standardized bipedal skeleton hierarchy (Hips, Spine, Head, Arms, Legs).
6. **Phase 6: FastMCP Mocap Extraction (`extract_mocap`)**:
   - Calls tool with `test_motion.mp4`.
   - Asserts: Outputs animation track (`.bvh` or `.fbx`) with frame count matching video duration.
7. **Phase 7: FastMCP UE5 Scene Assembly (`build_ue5_scene`)**:
   - Sends scene construction RPCs to UE5 Mock Server:
     - Imports mesh asset.
     - Sets PBR material parameters (BaseColor, Metallic, Roughness).
     - Configures Lumen directional light and sky atmosphere.
     - Creates CineCameraActor with focal length keyframes synchronized with audio beats.
   - Asserts: UE5 Mock server returns HTTP 200 / WebSocket success ACK for all object calls.
8. **Phase 8: Human-in-the-Loop Confirmation Gate**:
   - Emulates Copilot confirmation request: verifies tool pauses with `waiting_confirmation` status, simulates programmatic `Proceed` approval decision, and verifies pipeline resumes seamlessly.
9. **Phase 9: High-Resolution Render Queue (`render_video`)**:
   - Triggers Movie Render Queue export with resolution `1920x1080` at 30 fps.
   - Asserts: Final output video file (`rendered_cinematic.mp4`) is produced, header matches MP4 `ftyp` box, size > 100KB.
   - Generates summary JSON report (`e2e_report.json`) with execution timestamps, tool latencies, and pass/fail assertion breakdown.

### 5.4 Strict Visual Verification Architecture & Compliance Criteria
In accordance with `GEMINI.md` Section 5 ("Verificación Visual Rigurosa"):
1. **Layout & Alignment Compliance**:
   - Workstation split panes must respect flexible grid constraints without overflow or clipping.
   - Media Dropzone must maintain center alignment with responsive padding.
   - 3D Preview Viewport must preserve 16:9 canvas aspect ratio with letterboxing or adaptive camera frustum adjustment upon window resize.
   - Multi-track timeline must anchor cleanly at the bottom pane with fixed transport header and scrollable track body.
2. **Visual Contrast & Design System**:
   - Dark theme base (`bg-zinc-950`, `text-zinc-100`, borders `border-zinc-800`).
   - High contrast status badges:
     - Completed / Success: Emerald (`bg-emerald-500/20 text-emerald-400 border-emerald-500/40`)
     - Running / Active: Blue (`bg-blue-500/20 text-blue-400 border-blue-500/40 animate-pulse`)
     - Human Confirmation: Amber (`bg-amber-500/20 text-amber-300 border-amber-500/50`)
     - Error / Aborted: Rose (`bg-rose-500/20 text-rose-400 border-rose-500/40`)
3. **Timeline Waveform Rendering Fidelity**:
   - Waveform peaks must render sharply on HiDPI/Retina displays (applying devicePixelRatio scaling to canvas).
   - Beat marker lines must align accurately with audio transients without visual drift over extended durations.
   - Playhead red indicator line must scrub smoothly at 60 FPS without DOM jitter.
4. **Visual Testing Protocol**:
   - Test suites must render UI elements to DOM and verify layout classes and visibility attributes.
   - Visual regression snapshot capture strategy: component snapshots saved to `artifacts/visual_snapshots/` during automated UI test runs.

---

## 6. Implementation Breakdown & Milestone Allocation

Based on this survey, the implementation work for R3 and Verification Suites decomposes into five modular work packages:

| Work Package | Deliverable | Key Files | Dependency |
|---|---|---|---|
| **WP 3.1: Tauri & React Scaffold** | Project initialization, strict tsconfig, Tailwind, Tauri v2 configs, state stores | `src-tauri/tauri.conf.json`, `package.json`, `tsconfig.json`, `src/stores/*` | Node, Cargo |
| **WP 3.2: Media Dropzone & Tray** | Drag-and-drop dropzone, MIME validation, metadata parser, asset cards | `src/components/dropzone/MediaDropzone.tsx`, `src/components/dropzone/AssetCard.tsx` | WP 3.1 |
| **WP 3.3: Audiovisual Timeline** | Multi-track timeline, waveform canvas, beat markers, playhead scrubber, zoom/pan | `src/components/timeline/Timeline.tsx`, `src/components/timeline/AudioTrack.tsx` | WP 3.1, WP 3.2 |
| **WP 3.4: 3D Preview Viewport** | Three.js WebGL canvas, GLB loader, skeleton viewer, WebRTC pixel stream embed | `src/components/viewport/PreviewViewport.tsx`, `src/components/viewport/ThreeCanvas.tsx` | WP 3.1 |
| **WP 3.5: Copilot Console & Confirm** | Chat stream, execution plan cards, human confirmation dialog, log stream | `src/components/copilot/CopilotConsole.tsx`, `src/components/copilot/ConfirmationCard.tsx` | WP 3.1 |
| **WP 3.6: Verification Suites** | Pytest suites, Vitest UI suites, and `verify_pipeline.py` E2E simulation script | `tests/backend/*`, `tests/frontend/*`, `verify_pipeline.py` | FastMCP & UI |

---

## 7. Architectural Decisions & Rationale

1. **Why Tauri v2 over Electron?**
   - Tauri v2 delivers sub-50MB binary sizes, sub-100MB RAM consumption (critical when running alongside Unreal Engine 5 and local AI inference), and secure native Rust IPC.
2. **Why Three.js canvas in addition to UE5 Pixel Streaming?**
   - Offline & lightweight mode: Users generating 3D meshes and rigging do not need Unreal Engine 5 launched continuously. The embedded Three.js viewer provides instantaneous, zero-latency 3D mesh inspection and mocap playback, while Pixel Streaming handles the final high-fidelity Lumen/Nanite cinematic rendering.
3. **Why Zod schemas for all IPC & MCP events?**
   - Enforces the **Zero-Any Policy** at the system boundary. Any unexpected payload from FastMCP or UE5 Remote Control is caught and typed at runtime, preventing silent UI failures.
4. **Why an autonomous mode for `verify_pipeline.py`?**
   - Enables continuous integration and automated gate verification where human confirmation steps are programmatically satisfied, while preserving full human-in-the-loop interaction in production desktop mode.

---
*Report completed by Survey Agent 3 (Explorer - Desktop UI & Verification Architecture).*
