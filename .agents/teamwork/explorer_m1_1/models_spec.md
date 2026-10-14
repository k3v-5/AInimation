# Specification: Domain Models & Pydantic v2 Schemas (`backend/core/models.py`)

- **Component**: `backend/core/models.py`
- **Milestone**: Milestone 1 (Core Models & Telemetry)
- **Author**: Explorer M1-1 (Domain Models & Pydantic v2 Schemas)
- **Status**: Formulated, Verified & Ready for Implementation
- **Compliance**: Pydantic v2.12.5, Python 3.14+, Zero-Any Policy (`GEMINI.md`), FastMCP OpenAPI Schema Standard

---

## 1. Architectural Role and System Boundaries

In the IANIMATION Clean Architecture, `backend/core/models.py` defines the canonical data models for all inter-subsystem communication:
1. **FastMCP Server**: Input validation and output serialization for the 6 atomic tools (`analyze_audio`, `image_to_3d`, `auto_rig`, `extract_mocap`, `build_ue5_scene`, `render_video`).
2. **Hybrid AI Pipelines**: Standardized requests and results for Audio (Librosa/Demucs), Image-to-3D (Fal.ai/Tripo/Procedural Stub), Auto-Rigging (UE5 Mannequin), and Mocap (MediaPipe/Rotoscopy).
3. **Unreal Engine 5 Bridge**: Typed coordinate vectors (`Vector3D`), rotators (`Rotator3D`), camera choreographies, Lumen lighting presets, and MRQ render jobs compatible with UE5 Remote Control API.
4. **Copilot Human-in-the-Loop (HITL)**: Step-by-step production plans (`ProductionPlan`, `PlanStep`), risk scoring, and interactive confirmation gates (`PlanConfirmationRequest`/`Response`).
5. **Frontend Tauri Telemetry**: Real-time progress updates, plan proposals, asset readiness notifications, and log streams via WebSocket/SSE conforming directly to frontend Zod schemas.

```
       ┌───────────────────────────────┐
       │   Tauri / React Frontend      │
       │   (Zod / TypeScript strict)   │
       └──────────────┬────────────────┘
                      │ JSON-RPC / SSE
                      ▼
       ┌───────────────────────────────┐
       │     FastMCP Atomic Tools      │
       │   (OpenAPI / JSON Schema)     │
       └──────────────┬────────────────┘
                      │
                      ▼
   ┌──────────────────────────────────────────┐
   │         backend/core/models.py           │
   │  - StrictBaseModel (extra="forbid")      │
   │  - Zero-Any Policy (100% Strict Typing)  │
   └───────┬──────────────┬─────────────┬─────┘
           │              │             │
           ▼              ▼             ▼
   ┌──────────────┐┌──────────────┐┌──────────────┐
   │  AI Pipeline ││  UE5 Bridge  ││   Copilot    │
   │ (Demucs, 3D, ││ (Lumen, MRQ, ││ (Plan, Risk, │
   │  Mocap, Rig) ││  Remote Ctrl)││  HITL Gates) │
   └──────────────┘└──────────────┘└──────────────┘
```

---

## 2. Zero-Any Policy & Strict Typing Architecture

Per `GEMINI.md`:
> *"Zero-Any Policy: Tipado estricto con typing (Optional, Union, Dict, List, Callable) y modelos validados con Pydantic v2. Ninguna función debe carecer de firmas de tipos en parámetros y retornos."*

To enforce this:
1. **StrictBaseModel**: Every model inherits from `StrictBaseModel`, configured with `extra="forbid"` to prevent unauthorized or silent parameter injection, `validate_assignment=True`, and `arbitrary_types_allowed=False`.
2. **Explicit Enums (`StrEnum`)**: All category constants (`AudioStemType`, `MeshFormat`, `PlanRiskLevel`, `PlanStatus`, `AssetType`, `LogLevel`) inherit from standard `enum.StrEnum` (Python 3.11+ / 3.14 native), serializing directly to JSON strings.
3. **No `typing.Any`**: Generic dictionaries are typed with concrete scalar unions:
   ```python
   PlanParamScalar = Union[str, int, float, bool]
   PlanParamValue = Union[PlanParamScalar, List[str], Dict[str, str]]
   ```
4. **Field Validation**: Numerical constraints (`ge`, `le`), string lengths (`min_length`), and regex patterns (`pattern=r"^\d+x\d+$"` for resolutions) guarantee runtime safety before downstream execution.

---

## 3. Comprehensive Domain Model Catalog

### 3.1 Primitives & Spatial Types
| Model | Fields | Methods / Helpers | Purpose |
|---|---|---|---|
| `StrictBaseModel` | `model_config = ConfigDict(strict=False, validate_assignment=True, populate_by_name=True, extra="forbid")` | - | Root configuration for all domain entities. |
| `Vector3D` | `x: float = 0.0`<br>`y: float = 0.0`<br>`z: float = 0.0` | `to_tuple() -> Tuple[float, float, float]`<br>`from_tuple(...)`<br>`to_ue5_dict() -> Dict[str, float]` | 3D Cartesian coordinates (cm for UE5, m for glTF). |
| `Rotator3D` | `pitch: float = 0.0`<br>`yaw: float = 0.0`<br>`roll: float = 0.0` | `to_tuple() -> Tuple[float, float, float]`<br>`from_tuple(...)`<br>`to_ue5_dict() -> Dict[str, float]` | 3D Euler angles in degrees matching UE5 convention. |
| `ColorRGB` | `r: float = 1.0` (0.0-1.0)<br>`g: float = 1.0` (0.0-1.0)<br>`b: float = 1.0` (0.0-1.0) | `to_tuple()`<br>`to_ue5_dict()` | Normalized linear RGB color with UE5 LinearColor formatting. |

### 3.2 Audio Domain (`analyze_audio`)
| Model | Fields | Constraints & Defaults | FastMCP & Pipeline Contract |
|---|---|---|---|
| `AudioStemType` | `VOCALS = "vocals"`<br>`DRUMS = "drums"`<br>`BASS = "bass"`<br>`OTHER = "other"`<br>`GUITAR = "guitar"`<br>`PIANO = "piano"` | `StrEnum` | Demucs 4-stem and extended stem separation channels. |
| `AudioAnalysisRequest` | `audio_path: str`<br>`separate_stems: bool = True`<br>`sample_rate: int = 44100`<br>`bpm_hint: Optional[float] = None` | `min_length=1`<br>`8000 <= sample_rate <= 192000`<br>`30.0 <= bpm_hint <= 300.0` | Input for `analyze_audio` tool. |
| `StemSeparationResult` | `stems: Dict[str, str]`<br>`model_used: str = "demucs"`<br>`sample_rate: int = 44100`<br>`duration_seconds: float` | `duration_seconds >= 0.0` | Output of Demucs/Scipy filterbank stem extraction. |
| `AudioAnalysisResult` | `bpm: float`<br>`duration_seconds: float`<br>`beat_timestamps: List[float]`<br>`onset_envelope: List[float]`<br>`stems: Optional[Dict[str, str]] = None`<br>`time_signature: str = "4/4"`<br>`danceability: float = 0.5` | `bpm >= 0.0`<br>`duration_seconds >= 0.0`<br>`0.0 <= danceability <= 1.0` | FastMCP tool return object with `get_stem_path(...)` accessor. |

### 3.3 3D Asset Domain (`image_to_3d`)
| Model | Fields | Constraints & Defaults | FastMCP & Pipeline Contract |
|---|---|---|---|
| `MeshFormat` | `GLB = "glb"`<br>`GLTF = "gltf"`<br>`FBX = "fbx"`<br>`OBJ = "obj"`<br>`USD = "usd"` | `StrEnum` | Supported 3D formats. Default is `GLB`. |
| `PBRTextureSet` | `albedo_path: Optional[str]`<br>`normal_path: Optional[str]`<br>`roughness_path: Optional[str]`<br>`metallic_path: Optional[str]`<br>`ambient_occlusion_path: Optional[str]`<br>`emissive_path: Optional[str]`<br>`height_path: Optional[str]`<br>`resolution: int = 1024` | `128 <= resolution <= 8192`<br>Helper: `has_textures() -> bool` | Standard metallic-roughness PBR texture channels. |
| `ImageTo3DRequest` | `image_path: str`<br>`provider: str = "auto"`<br>`texture_resolution: int = 1024`<br>`target_format: MeshFormat = GLB`<br>`generate_textures: bool = True`<br>`seed: Optional[int] = None` | `min_length=1`<br>`256 <= texture_resolution <= 4096` | Input payload for `image_to_3d` tool. |
| `ImageTo3DResult` | `mesh_path: str`<br>`textures: PBRTextureSet`<br>`vertex_count: int`<br>`polygon_count: int = 0`<br>`cached: bool = False`<br>`mesh_format: MeshFormat = GLB`<br>`provider_used: str = "procedural_stub"`<br>`generation_time_seconds: float = 0.0` | `min_length=1`<br>`vertex_count >= 0`<br>`polygon_count >= 0` | Output payload for `image_to_3d` tool. |

### 3.4 Rigging Domain (`auto_rig`)
| Model | Fields | Constraints & Defaults | FastMCP & Pipeline Contract |
|---|---|---|---|
| `BoneDescriptor` | `name: str`<br>`parent_name: Optional[str] = None`<br>`head_position: Tuple[float, float, float]`<br>`tail_position: Tuple[float, float, float]`<br>`roll: float = 0.0` | `min_length=1` | Individual bone definition in anatomical hierarchy. |
| `SkeletalHierarchy` | `skeleton_type: str = "ue5_mannequin"`<br>`root_bone: str = "root"`<br>`bones: List[BoneDescriptor]`<br>`is_biped: bool = True` | Standard biped hierarchy | Full armature specification. |
| `AutoRigRequest` | `mesh_path: str`<br>`skeleton_type: str = "ue5_mannequin"`<br>`max_influences: int = 4`<br>`symmetry: bool = True` | `min_length=1`<br>`1 <= max_influences <= 8` | Input payload for `auto_rig` tool. |
| `AutoRigResult` | `rigged_mesh_path: str`<br>`bone_count: int`<br>`hierarchy: List[str]`<br>`skeleton_type: str = "ue5_mannequin"`<br>`success: bool = True` | `min_length=1`<br>`bone_count >= 1` | Output payload for `auto_rig` tool. |

### 3.5 Mocap Domain (`extract_mocap`)
| Model | Fields | Constraints & Defaults | FastMCP & Pipeline Contract |
|---|---|---|---|
| `Pose3DKeyframe` | `timestamp: float`<br>`frame_index: int`<br>`keypoints_3d: Dict[str, Tuple[float, float, float]]`<br>`confidence_scores: Dict[str, float] = {}` | `timestamp >= 0.0`<br>`frame_index >= 0` | Single frame 3D skeletal tracking coordinates. |
| `MocapExtractionRequest` | `video_path: str`<br>`target_fps: int = 30`<br>`extract_hands: bool = False`<br>`extract_face: bool = False`<br>`remove_background: bool = True`<br>`smoothing_window: int = 5` | `min_length=1`<br>`1 <= target_fps <= 120`<br>`1 <= smoothing_window <= 30` | Input payload for `extract_mocap` tool. |
| `MocapResult` | `animation_path: str`<br>`frame_count: int`<br>`fps: int = 30`<br>`duration: float`<br>`keyframes: Optional[List[Pose3DKeyframe]] = None`<br>`tracked_joints_count: int = 33` | `min_length=1`<br>`frame_count >= 0`<br>`duration >= 0.0`<br>`tracked_joints_count >= 1` | Output payload for `extract_mocap` tool. |

### 3.6 Scene Domain (`build_ue5_scene`)
| Model | Fields | Constraints & Defaults | FastMCP & Pipeline Contract |
|---|---|---|---|
| `CameraKeyframe` | `timestamp: float`<br>`position: Tuple[float, float, float]`<br>`rotation: Tuple[float, float, float] = (0, 0, 0)`<br>`focal_length: float = 35.0`<br>`aperture: float = 2.8`<br>`focus_distance: float = 1000.0` | `timestamp >= 0.0`<br>`10.0 <= focal_length <= 300.0`<br>`0.7 <= aperture <= 22.0`<br>Helper: `to_ue5_payload()` | CineCameraActor transform and lens optics keyframe. |
| `LumenLightConfig` | `preset_name: str = "cinematic_three_point"`<br>`directional_light_intensity: float = 10.0`<br>`directional_light_color: Tuple[float, float, float] = (1.0, 0.95, 0.9)`<br>`sky_light_intensity: float = 1.0`<br>`sky_light_color: Tuple[float, float, float] = (0.8, 0.88, 1.0)`<br>`key_light_intensity: float = 5000.0`<br>`fill_light_intensity: float = 2500.0`<br>`rim_light_intensity: float = 7500.0`<br>`use_lumen_gi: bool = True`<br>`use_lumen_reflections: bool = True` | All intensities `>= 0.0` | Unreal Engine 5 Lumen dynamic lighting rig settings. |
| `SceneConfig` | `mesh_path: str`<br>`animation_path: str`<br>`lighting_preset: str = "cinematic_three_point"`<br>`lighting_config: Optional[LumenLightConfig] = None`<br>`camera_choreography: List[CameraKeyframe] = []`<br>`audio_track_path: Optional[str] = None`<br>`level_name: str = "Stage_Main"` | `min_length=1` for paths | Input payload for `build_ue5_scene` tool. |
| `SceneBuildResult` | `success: bool`<br>`actor_ids: List[str]`<br>`scene_path: str`<br>`camera_actor_id: Optional[str] = None`<br>`character_actor_id: Optional[str] = None`<br>`message: str = "Scene constructed successfully"` | `min_length=1` for `scene_path` | Output payload for `build_ue5_scene` tool. |

### 3.7 Render Domain (`render_video`)
| Model | Fields | Constraints & Defaults | FastMCP & Pipeline Contract |
|---|---|---|---|
| `MovieRenderQueueJobConfig` | `scene_path: str`<br>`output_path: str`<br>`fps: int = 60`<br>`resolution: str = "1920x1080"`<br>`codec: str = "h264"`<br>`anti_aliasing_samples: int = 16`<br>`warmup_frames: int = 30`<br>`render_passes: List[str] = ["FinalImage"]` | `pattern=r"^\d+x\d+$"`<br>`1 <= fps <= 240`<br>`1 <= anti_aliasing_samples <= 64`<br>Helper: `get_resolution_dimensions()` | MRQ configuration for high-fidelity offline rendering. |
| `RenderResult` | `video_path: str`<br>`frame_count: int`<br>`elapsed_seconds: float`<br>`fps: int = 60`<br>`resolution: str = "1920x1080"`<br>`file_size_bytes: int = 0`<br>`success: bool = True` | `frame_count >= 0`<br>`elapsed_seconds >= 0.0`<br>`file_size_bytes >= 0` | Output payload for `render_video` tool. |

### 3.8 Copilot & Production Plan Domain (HITL)
| Model | Fields | Constraints & Defaults | FastMCP & Pipeline Contract |
|---|---|---|---|
| `PlanRiskLevel` | `LOW = "low"`<br>`MEDIUM = "medium"`<br>`HIGH = "high"`<br>`CRITICAL = "critical"` | `StrEnum` | Automated risk assessment for destructive or heavy GPU operations. |
| `PlanStatus` | `PROPOSED = "proposed"`<br>`APPROVED = "approved"`<br>`REJECTED = "rejected"`<br>`IN_PROGRESS = "in_progress"`<br>`COMPLETED = "completed"`<br>`FAILED = "failed"` | `StrEnum` | Plan & Step lifecycle states. |
| `PlanStep` | `step_id: str`<br>`index: int`<br>`tool_name: str`<br>`description: str`<br>`parameters: Dict[str, PlanParamValue]`<br>`risk_level: PlanRiskLevel = LOW`<br>`requires_confirmation: bool = False`<br>`status: PlanStatus = PROPOSED`<br>`output_preview: Optional[str] = None`<br>`error_message: Optional[str] = None` | `min_length=1`<br>`index >= 0` | Atomic step proposed by Copilot for user approval. |
| `ProductionPlan` | `plan_id: str`<br>`title: str`<br>`description: str`<br>`steps: List[PlanStep]`<br>`status: PlanStatus = PROPOSED`<br>`created_at: str (ISO 8601)`<br>`updated_at: str (ISO 8601)`<br>`total_estimated_duration_seconds: float = 0.0` | `total_estimated_duration_seconds >= 0.0`<br>Helpers: `get_step(...)`, `mark_step_status(...)`, `is_all_completed()` | Multi-step end-to-end plan proposed by Copilot. |
| `PlanConfirmationRequest` | `plan_id: str`<br>`step_id: Optional[str] = None`<br>`auto_proceed: bool = False`<br>`user_prompt: Optional[str] = None` | `min_length=1` | Copilot gate asking user for permission. |
| `PlanConfirmationResponse` | `plan_id: str`<br>`step_id: Optional[str] = None`<br>`approved: bool`<br>`feedback: Optional[str] = None`<br>`modified_parameters: Optional[Dict[str, PlanParamValue]] = None`<br>`timestamp: str (ISO 8601)` | `approved: bool` | User gate approval/rejection with parameter adjustments. |

### 3.9 Telemetry & Progress Domain (WebSocket / SSE)
| Model | Fields | Type Literal | Telemetry Bus Contract |
|---|---|---|---|
| `AssetType` | `AUDIO_STEMS = "audio_stems"`<br>`MESH_3D = "mesh_3d"`<br>`RIGGED_MESH = "rigged_mesh"`<br>`MOCAP = "mocap"`<br>`RENDER_VIDEO = "render_video"` | `StrEnum` | Asset category discriminator. |
| `LogLevel` | `INFO = "info"`<br>`WARNING = "warning"`<br>`ERROR = "error"` | `StrEnum` | Log severity level. |
| `ProgressEvent` | `type: Literal["progress"] = "progress"`<br>`stage: str`<br>`percentage: float (0.0-100.0)`<br>`message: str`<br>`timestamp: str` | `"progress"` | Streamed to UI progress bar and status footer. |
| `PlanProposalEvent` | `type: Literal["plan_proposal"] = "plan_proposal"`<br>`plan_id: str`<br>`steps: List[PlanStep]`<br>`status: PlanStatus` | `"plan_proposal"` | Streamed to Copilot chat cards in UI. |
| `AssetReadyEvent` | `type: Literal["asset_ready"] = "asset_ready"`<br>`asset_id: str`<br>`asset_type: AssetType`<br>`file_path: str` | `"asset_ready"` | Emitted to update intermediate asset tray in UI. |
| `LogEvent` | `type: Literal["log"] = "log"`<br>`level: LogLevel`<br>`message: str`<br>`timestamp: str` | `"log"` | Streamed to Copilot terminal console. |
| `TelemetryEvent` | `Union[ProgressEvent, PlanProposalEvent, AssetReadyEvent, LogEvent]` | Discriminated Union | Top-level SSE / WebSocket message wrapper. |

---

## 4. Frontend Zod & TypeScript Alignment

The models in `backend/core/models.py` map 1:1 to the frontend Zod schemas in `src/types/telemetry.ts`:

```typescript
// src/types/telemetry.ts (matching backend/core/models.py)
import { z } from "zod";

export const PlanRiskLevelSchema = z.enum(["low", "medium", "high", "critical"]);
export const PlanStatusSchema = z.enum(["proposed", "approved", "rejected", "in_progress", "completed", "failed"]);
export const AssetTypeSchema = z.enum(["audio_stems", "mesh_3d", "rigged_mesh", "mocap", "render_video"]);
export const LogLevelSchema = z.enum(["info", "warning", "error"]);

export const PlanStepSchema = z.object({
  step_id: z.string(),
  index: z.number().int().nonnegative(),
  tool_name: z.string(),
  description: z.string(),
  parameters: z.record(z.union([z.string(), z.number(), z.boolean(), z.array(z.string()), z.record(z.string())])),
  risk_level: PlanRiskLevelSchema,
  requires_confirmation: z.boolean(),
  status: PlanStatusSchema,
  output_preview: z.string().nullable().optional(),
  error_message: z.string().nullable().optional(),
});

export const TelemetryEventSchema = z.discriminatedUnion("type", [
  z.object({
    type: z.literal("progress"),
    stage: z.string(),
    percentage: z.number().min(0).max(100),
    message: z.string(),
    timestamp: z.string(),
  }),
  z.object({
    type: z.literal("plan_proposal"),
    plan_id: z.string(),
    steps: z.array(PlanStepSchema),
    status: PlanStatusSchema,
  }),
  z.object({
    type: z.literal("asset_ready"),
    asset_id: z.string(),
    asset_type: AssetTypeSchema,
    file_path: z.string(),
  }),
  z.object({
    type: z.literal("log"),
    level: LogLevelSchema,
    message: z.string(),
    timestamp: z.string(),
  }),
]);
```

---

## 5. Drop-in Implementation and Test Suite

1. **Production Code**: The drop-in implementation has been drafted and validated in:
   `.agents/teamwork/explorer_m1_1/proposed_models.py`
   Target production location: `backend/core/models.py`
2. **Automated Unit Tests**: The pytest test suite covering all 11 test categories and 100% of the models has been drafted and executed:
   `.agents/teamwork/explorer_m1_1/test_models_suite.py`
   Target production location: `tests/backend/test_models.py`
   Command to verify:
   ```bash
   python -m pytest tests/backend/test_models.py
   ```
