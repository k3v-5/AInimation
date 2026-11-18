"""Unified Monorepo Subsystem & MCP Tool Registry for IANIMATION.

Provides strongly typed discovery, path-sanitized disk validation, tool
search across all 5 animation/render/VFX engines, and unified MCP configuration
export (``mcp_servers.config.json``).

Complies 100% with GEMINI.md (SOLID, Zero-Any Policy, Pydantic v2 StrictBaseModel).
"""

from __future__ import annotations

from enum import StrEnum
import json
from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple, Union

from pydantic import Field

from backend.core.models import StrictBaseModel

DEFAULT_MONOREPO_ROOT = Path(__file__).resolve().parents[2]
MCPConfigPayload = Dict[str, Dict[str, Dict[str, Union[str, List[str]]]]]


class SubsystemDomain(StrEnum):
    """Canonical animation/render domain identifiers across the monorepo."""

    AI_3D_ORCHESTRATOR = "ai_3d_orchestrator"
    ADOBE_2D_SUITE = "adobe_2d_suite"
    AFTER_EFFECTS_VFX = "after_effects_vfx"
    STICK_2D_IK = "stick_2d_ik"
    BLENDER_PROCEDURAL_LAB = "blender_procedural_lab"
    ASSET_ORCHESTRATION_ENGINE = "asset_orchestration_engine"


RuntimeKind = Literal["python", "node", "blender-python"]


class MCPToolSummary(StrictBaseModel):
    """Compact descriptor for a single MCP tool or gateway command."""

    name: str = Field(..., min_length=1)
    subsystem_id: str = Field(..., min_length=1)
    domain: SubsystemDomain
    category: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)


class SubsystemDescriptor(StrictBaseModel):
    """Complete architectural descriptor for one monorepo package."""

    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    domain: SubsystemDomain
    version: str = Field(..., min_length=1)
    runtime: RuntimeKind
    root_dir: str = Field(..., min_length=1)
    entrypoint: str = Field(..., min_length=1)
    readme_path: str = Field(..., min_length=1)
    command: str = Field(..., min_length=1)
    args: List[str] = Field(default_factory=list)
    tool_count: int = Field(..., ge=0)
    verified_files_count: int = Field(..., ge=0)
    capabilities: List[str] = Field(default_factory=list)
    tools: List[MCPToolSummary] = Field(default_factory=list)


class MonorepoIntegrityReport(StrictBaseModel):
    """Disk and schema validation report returned by ``validate_monorepo_integrity``."""

    is_valid: bool
    monorepo_root: str
    total_subsystems: int
    total_mcp_tools: int
    total_procedural_generators: int
    corrupt_files_detected: int
    subsystems_status: Dict[str, bool] = Field(default_factory=dict)
    missing_paths: List[str] = Field(default_factory=list)


class MonorepoToolSearchResult(StrictBaseModel):
    """Structured search response across the unified monorepo registry."""

    query: str
    domain_filter: Optional[str] = None
    total_matches: int
    matches: List[MCPToolSummary] = Field(default_factory=list)


def _confine_to_root(root: Path, relative_path: str) -> Path:
    """Resolve ``relative_path`` and verify it stays strictly within ``root``."""
    resolved_root = root.resolve()
    candidate = (resolved_root / relative_path).resolve()
    try:
        candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(
            f"Path traversal rejected: '{relative_path}' escapes '{resolved_root}'"
        ) from exc
    return candidate


def _is_non_blank_file(path: Path) -> bool:
    """Return True if file exists and contains non-whitespace, non-null bytes."""
    if not path.is_file() or path.stat().st_size == 0:
        return False
    with path.open("rb") as fh:
        head = fh.read(4096)
        if len(head.strip(b" \t\r\n\x00")) > 0:
            return True
        return len(fh.read().strip(b" \t\r\n\x00")) > 0


def _build_tools(
    subsystem_id: str,
    domain: SubsystemDomain,
    grouped_specs: List[Tuple[str, List[Tuple[str, str]]]],
) -> List[MCPToolSummary]:
    """Build typed ``MCPToolSummary`` entries from compact category/tool pairs."""
    items: List[MCPToolSummary] = []
    for category, entries in grouped_specs:
        for tool_name, description in entries:
            items.append(
                MCPToolSummary(
                    name=tool_name,
                    subsystem_id=subsystem_id,
                    domain=domain,
                    category=category,
                    description=description,
                )
            )
    return items


def _ianimation_3d_tools() -> List[MCPToolSummary]:
    return _build_tools(
        "ianimation-3d",
        SubsystemDomain.AI_3D_ORCHESTRATOR,
        [
            (
                "3d-pipeline",
                [
                    ("analyze_audio", "Extract musical BPM, rhythm onsets, and beat timestamps from audio."),
                    ("image_to_3d", "Generate a 3D textured mesh (.glb) with PBR maps from a 2D image."),
                    ("auto_rig", "Bind an anatomical skeletal hierarchy to a static 3D mesh."),
                    ("extract_mocap", "Extract 3D skeletal motion capture animation from reference video."),
                    ("build_ue5_scene", "Assemble an Unreal Engine 5 Level Sequence with lighting and camera."),
                    ("render_video", "Render final MP4 video or still via UE5 MRQ or headless Blender."),
                ],
            ),
            (
                "monorepo-discovery",
                [
                    ("list_monorepo_subsystems", "List all unified monorepo packages, paths, and integrity metrics."),
                    ("search_monorepo_tools", "Search MCP tools and generators across all 5 animation engines."),
                ],
            ),
        ],
    )


def _adobe_suite_tools() -> List[MCPToolSummary]:
    return _build_tools(
        "adobe-animation-mcp",
        SubsystemDomain.ADOBE_2D_SUITE,
        [
            (
                "character-animator",
                [
                    ("ch_scaffold_puppet", "Generate rigged PSD puppet with +Head, 14 visemes, and Dangle/Fixed physics."),
                    ("ch_scaffold_multi_angle_puppet", "Generate 3-view or 5-view Multi-Angle Head Turner PSD puppet."),
                    ("ch_scaffold_walk_puppet", "Generate multi-view Walk behavior rigged PSD puppet with limb tags."),
                    ("ch_slice_artwork_to_puppet", "Convert 2D artwork parameters into an anatomically sliced puppet PSD."),
                    ("ch_add_puppet_triggers_and_physics", "Inject emotional swap sets, tears cycle, hand triggers, and breathing."),
                    ("ch_audit_puppet_deep", "Audit PSD/AI puppet scoring 0-100 on independence, visemes, limbs, and physics."),
                    ("ch_auto_repair_puppet", "Auto-repair missing head/limb independence tags and puppet structure."),
                    ("ch_prepare_recording_take", "Bundle 48kHz speech WAV, viseme JSON cues, trigger sheet, and AE JSX script."),
                    ("ch_validate_puppet", "Inspect existing PSD compliance against Adobe Character Animator rigging rules."),
                    ("ch_launch_character_animator", "Launch Adobe Character Animator opening a target puppet or project."),
                    ("ch_inspect_environment", "Report installed paths for Character Animator, Illustrator, AE, and Blender."),
                    ("ch_get_roadmap_status", "Return active phase progress of the Adobe Animation Roadmap."),
                ],
            ),
            (
                "after-effects-25d",
                [
                    ("ae_execute_jsx", "Execute an ExtendScript (.jsx) script in Adobe After Effects via CLI bridge."),
                    ("ae_import_puppet_scene", "Import 2D puppet PSD/AI or Character Animator scene into After Effects."),
                    ("ae_render_comp", "Trigger headless background rendering via Adobe aerender."),
                    ("ae_generate_scene_manifest", "Create standard 2.5D Scene Manifest JSON + ExtendScript constructor."),
                    ("ae_setup_25d_stage", "Assemble full 2.5D parallax camera stage in After Effects."),
                    ("ae_apply_animation_expressions", "Apply squash/stretch, audio bounce, camera shake, or blink expressions."),
                    ("ae_batch_render_queue", "Batch enqueue compositions to aerender with H.264/ProRes 4444 output."),
                ],
            ),
            (
                "illustrator-vector",
                [
                    ("ai_execute_jsx", "Execute ExtendScript (.jsx) inside Adobe Illustrator via automation bridge."),
                    ("ai_create_document", "Create vector document in Adobe Illustrator with custom artboard dimensions."),
                    ("ai_trace_and_clean_sketch", "Vectorize raster sketch using Illustrator Image Trace and expand paths."),
                    ("ai_auto_rig_slice", "Sort vector artwork paths spatially into Character Animator layer groups."),
                    ("ai_apply_color_palette", "Harmonize character palette using designer themes or custom hex swatches."),
                    ("ai_export_character_package", "Export active Illustrator character to .ai puppet and optimized .svg."),
                ],
            ),
            (
                "neural-audio-lipsync",
                [
                    ("audio_generate_speech", "Synthesize clean 48kHz 16-bit PCM WAV dialogue for lip-sync."),
                    ("audio_calculate_viseme_cues", "Compute phoneme/viseme timeline cues (Ah, Ee, Oh, M, etc.) from text."),
                    ("audio_generate_expressive_speech", "Synthesize multi-lingual emotional neural speech resampled to 48kHz PCM."),
                    ("audio_export_lip_sync_markers", "Export viseme timeline markers to AE .jsx, JSON Cue Sheet, or CSV."),
                    ("audio_list_available_voices", "List available neural regional voices (MX, ES, US, JP, etc.)."),
                ],
            ),
            (
                "blender-25d",
                [
                    ("blender_execute_script", "Execute headless Python script in Blender (bpy) without GUI."),
                    ("blender_render_frame", "Render 3D scene, background, or Grease Pencil element to PNG."),
                    ("blender_scaffold_3d_room", "Generate procedural architectural room (anime bedroom, cyberpunk, studio)."),
                    ("blender_render_parallax_passes", "Render Beauty RGBA, Shadow Catcher Alpha, and Z-Depth/Mist passes."),
                    ("blender_grease_pencil_sketch", "Generate stylized 2D Grease Pencil strokes in 3D space."),
                ],
            ),
            (
                "autonomous-pipelines",
                [
                    ("render_preview_frame_to_base64", "Encode rendered image or animation frame as Base64 PNG/JPEG in MCP."),
                    ("pipeline_create_talking_character", "One-click puppet PSD + 48kHz neural speech WAV + lip-sync cues."),
                    ("pipeline_render_social_clip", "One-click 9:16/16:9 composite package of puppet, 2.5D stage, and audio."),
                ],
            ),
        ],
    )


def _motion_vfx_tools() -> List[MCPToolSummary]:
    return _build_tools(
        "after-effects-motion-engine",
        SubsystemDomain.AFTER_EFFECTS_VFX,
        [
            (
                "project-runtime",
                [
                    ("create_video_from_script", "Orchestrate multi-agent audiovisual project in canonical IR from script."),
                    ("export_to_after_effects_jsx", "Compile canonical project or composition into Adobe AE ExtendScript (.jsx)."),
                    ("get_timeline_preview_frame", "Inspect evaluated visual and temporal frame state at timestamp t."),
                    ("apply_viral_caption_style", "Apply kinetic typography/caption presets creating an immutable revision."),
                    ("create_project", "Create persistent versioned project envelope in production runtime."),
                    ("open_project", "Open existing persistent project with recovery and active editing session."),
                    ("save_project", "Save project envelope applying optimistic concurrency checks."),
                    ("close_project", "Close active project session releasing concurrency locks."),
                    ("get_project_status", "Query runtime status, revision HEAD, lock state, and health report."),
                    ("list_project_revisions", "List immutable revision history for a persistent project."),
                    ("diff_project_revisions", "Calculate structural and semantic diff between two revisions."),
                    ("restore_project_revision", "Restore historical revision non-destructively as a new revision."),
                    ("validate_project", "Execute 6-layer non-mutating validation on a project."),
                    ("cancel_operation", "Cooperatively cancel an active long-running runtime operation."),
                ],
            ),
            (
                "ae-live-bridge",
                [
                    ("run-script", "Run a predefined ExtendScript bridge command inside Adobe After Effects."),
                    ("get-results", "Retrieve JSON results from the last script executed in After Effects."),
                    ("create-composition", "Create a new After Effects composition with width, height, fps, duration."),
                    ("apply-effect", "Apply an After Effects native/plugin effect to a target layer."),
                    ("list-presets", "List available After Effects .ffx presets installed on the host."),
                    ("set-audio-levels", "Set audio gain levels in dB on an audio or AV layer."),
                ],
            ),
            (
                "social-and-vlog",
                [
                    ("transcribe_local_audio", "Transcribe local video/audio phonetically word-by-word at zero API cost."),
                    ("detect_viral_clips", "Extract top viral 30s-60s segments scored 0-100 from transcripts and energy."),
                    ("package_social_release", "Generate A/B High-CTR titles, chapters, and viral hashtags."),
                    ("auto_reframe_video", "Calculate dynamic pan-and-scan keyframes from 16:9 to 9:16 vertical."),
                    ("vlog_generate_jump_cut_plan", "Compute silence removal, phonetic word boundary protection, and punch-ins."),
                    ("vlog_classify_footage", "Classify raw footage into A-Roll, B-Roll, Timelapse, Action, Photo, Screen."),
                    ("vlog_match_broll", "Rank and match B-Roll clips against narrative intent with multicriteria scoring."),
                    ("vlog_produce", "Orchestrate 22-phase multi-lingual vlog production into AE ExtendScript."),
                    ("vlog_get_status", "Retrieve runtime status and deliverable manifest of a vlog production run."),
                ],
            ),
            (
                "editorial-dataviz-qa",
                [
                    ("editorial_compile_data_visualization", "Compile structured datasets into animated AE DataViz specs."),
                    ("editorial_dataviz_to_jsx", "Transpile DataViz IR AST into executable After Effects JSX."),
                    ("editorial_parse_dataset", "Parse raw CSV or JSON text into a normalized DataSet structure."),
                    ("editorial_run_qa", "Audit Editorial Document against v4 structural, pacing, visual, audio QA rules."),
                    ("editorial_compare_revisions", "Perform semantic diff analysis between two editorial revisions."),
                    ("editorial_generate_trim_plan", "Compute semantic trimming and best take selection across segments."),
                    ("editorial_detect_redundancy", "Flag semantically redundant arguments and repetitive dialogue."),
                ],
            ),
            (
                "compositing-and-vision",
                [
                    ("compose_text_behind_subject", "Assemble 3-layer depth sandwich placing editorial text behind subject."),
                    ("compose_multi_take_clones", "Weave multiple takes of a subject into a seamless single-plate clone shot."),
                    ("detect_subjects_in_clip", "Detect subject bounding boxes and silhouette contour points in frames."),
                ],
            ),
            (
                "optics-temporal-film",
                [
                    ("apply_snap_zooms_to_timeline", "Apply percussive snap/crash zooms with inertial bounce on beats."),
                    ("apply_fisheye_optics", "Apply 90s vintage fisheye barrel distortion and chromatic aberration."),
                    ("compile_dolly_zoom", "Compute exact scale compensation curves for virtual Vertigo Dolly Zoom."),
                    ("apply_posterize_time", "Apply variable stylized frame rates (12fps anime, 8fps stop-motion)."),
                    ("compile_speed_ramp_to_beat", "Build C^1 time remapping speed ramps landing slow-motion on beat drop."),
                    ("compile_temporal_orchestration", "Orchestrate Posterize Time, Speed Ramps, and Stutter Freeze into AE plan."),
                    ("apply_film_grain_and_halation", "Apply 16mm/35mm organic grain and Kodak Vision3 red halation glow."),
                    ("apply_auteur_color_grading", "Apply auteur color grading LUTs (Tyler Pastel, Kendrick BW, MiniDV Acid)."),
                    ("compile_film_emulation_plan", "Consolidate grain, halation, gate weave, and grading into AE plan."),
                ],
            ),
            (
                "rhythm-and-typography",
                [
                    ("apply_machine_gun_flash_cuts", "Generate frame-quantized stroboscopic flash cuts and burst interleaving."),
                    ("apply_blackout_vacuum_drop", "Insert absolute blackout vacuum window before musical beat drop."),
                    ("compile_syncopated_rhythm_cut", "Assemble syncopated flash bursts and pre-drop blackouts in AE."),
                    ("apply_brutalist_kinetic_title", "Create ultra-bold brutalist editorial title with vertical stretch & negative tracking."),
                    ("apply_liquid_chrome_text_effect", "Apply reflective liquid chrome shader with bevel and turbulent displacement."),
                    ("compile_perspective_anchored_typography", "Consolidate brutalist text, liquid chrome, 3D orientation, and word slam."),
                ],
            ),
            (
                "spatial-mechanics-photonics",
                [
                    ("apply_snorricam_body_lock", "Lock subject to frame center transferring inertia to mirrored background."),
                    ("apply_infinite_zoom_portal", "Generate super-exponential crash zoom wormhole portal transitions."),
                    ("compile_spatial_cinematography_plan", "Consolidate Snorricam, infinite zoom portals, and parallax wipes."),
                    ("apply_centrifugal_gyro_roll", "Execute 360-degree Z-axis centrifugal barrel rolls with scale guard."),
                    ("apply_directional_whip_pan", "Generate invisible directional whip-pan match cut with symmetric blur."),
                    ("compile_dynamic_mechanics_plan", "Consolidate gyro rolls, whip-pan match cuts, and lens breathing."),
                    ("apply_shutter_drag_echo", "Emulate slow-shutter kinetic ghosting trails via ADBE Echo decay."),
                    ("apply_anamorphic_streak_flare", "Generate horizontal anamorphic optical streak flares over highlights."),
                    ("apply_flir_thermal_vision", "Apply FLIR infrared thermal false-color shader with edge contours."),
                    ("compile_photonics_plan", "Consolidate shutter drag, anamorphic flares, prism star, and FLIR thermal."),
                ],
            ),
            (
                "mixed-media-and-kinetics",
                [
                    ("apply_manga_impact_frame", "Insert 1-2 frame stroboscopic manga high-contrast impact cuts."),
                    ("apply_procedural_speed_lines", "Generate convergent anime speed lines with central exclusion zone."),
                    ("apply_film_sprocket_holes", "Simulate 35mm/16mm film sprocket holes with KeyKode marginal text."),
                    ("compile_mixed_media_plan", "Consolidate impact frames, speed lines, sprockets, paper tear, and boil."),
                    ("apply_audio_reactive_physics", "Compute damped viscoelastic bounce and chromatic shift reacting to 808 sub-bass."),
                    ("apply_dynamic_aspect_ratio_breathing", "Animate dynamic aspect ratio transitions (9:16, 1:1, 16:9, 2.39:1)."),
                    ("apply_datamosh_pframe_glitch", "Emulate Y2K MPEG I-frame loss and macroblock displacement glitches."),
                    ("compile_stem_kinetics_plan", "Consolidate 808 bounce physics, breathing mattes, and datamosh into AE plan."),
                ],
            ),
        ],
    )


def _stick_animator_tools() -> List[MCPToolSummary]:
    return _build_tools(
        "stykanimate-mcp",
        SubsystemDomain.STICK_2D_IK,
        [
            (
                "capabilities",
                [
                    ("capabilities", "Report supported formats (.styk, .stkz, .stykmov, .piv, .stk), Python codec, and open projects."),
                ],
            ),
            (
                "project-lifecycle",
                [
                    ("project_open", "Open a StykAnimate (.styk/.stkz) or Pivot (.piv/.stk) file as active project."),
                    ("project_close", "Close open project and release editor session."),
                    ("project_describe", "Report canvas size, frame rate, keyframes, and figure definitions."),
                    ("project_validate", "Validate open project consistency and integrity."),
                    ("project_save", "Write open project cleanly to disk."),
                    ("project_timeline", "List full timeline structure, ticks, and keyframe sequence."),
                    ("project_seek", "Seek editor playhead to a specified keyframe index."),
                ],
            ),
            (
                "figures",
                [
                    ("figure_list", "List active figure instances with IDs, names, layers, position, and scale."),
                    ("figure_describe", "Report full joint hierarchy, parent links, lengths, and bend handles of a figure."),
                    ("figure_add", "Instantiate a figure definition on the active keyframe."),
                    ("figure_duplicate", "Duplicate a figure including its current pose into a target keyframe."),
                    ("figure_delete", "Remove a figure instance cleanly from a keyframe."),
                    ("figure_transform", "Translate, rotate, scale, flip, or align a figure instance on canvas."),
                ],
            ),
            (
                "pose-and-ik",
                [
                    ("pose_evaluate", "Solve forward/inverse kinematics and return joint positions in canvas pixels."),
                    ("pose_set", "Set joint angles, segment lengths, and bends on a figure pose."),
                    ("pose_ik_set", "Move inverse kinematics target of a joint (e.g., hand or foot placement)."),
                    ("pose_set_ik", "Enable/disable or pin/unpin inverse kinematics controller targets on a joint."),
                    ("pose_reset", "Reset figure pose back to its definition rest pose."),
                ],
            ),
            (
                "layers-and-styles",
                [
                    ("layer_list", "List project layers with z-order, visibility, and lock state."),
                    ("layer_edit", "Create, rename, delete, reorder layers, or move figures between layers."),
                    ("style_set", "Update figure color, opacity, or stroke thickness styling."),
                ],
            ),
            (
                "timeline-and-history",
                [
                    ("keyframe_edit", "Add, delete, duplicate, or reorder animation keyframes."),
                    ("keyframe_timing", "Modify keyframe tick duration or global project FPS."),
                    ("history_undo", "Undo the most recent non-destructive project edit."),
                    ("history_redo", "Redo the previously undone project edit."),
                ],
            ),
        ],
    )


def _blender_lab_tools() -> List[MCPToolSummary]:
    return _build_tools(
        "blender-procedural-lab",
        SubsystemDomain.BLENDER_PROCEDURAL_LAB,
        [
            (
                "procedural-generators",
                [
                    ("generar_material_test_bench_v5", "Generate Shader Balls Pro V5 Material Test Bench with 3-point studio lighting."),
                    ("procesar_mapas_pbr_cinematograficos", "Synthesize 2K BaseColor, DirectX Normal, and packed ORM PBR maps."),
                    ("generar_trimsheet_industrial", "Generate 2048x2048 industrial architectural trim sheet textures."),
                    ("generar_personaje_riggeado_oficial", "Generate rigged UE5 Rest A-Pose skeletal firefighter mesh and FBX."),
                    ("generar_animaciones_locomocion_oficial", "Generate 10 3D locomotion & combat animations calibrated without clipping."),
                    ("generar_catalogo_modular_90_master_oficial", "Generate 90-asset modular architectural kit (Industrial/ArtDeco/Plasma/BioLab)."),
                    ("generar_bestiario_10_entidades_oficial", "Generate 10-entity 3D sci-fi bestiary with custom meshes."),
                    ("exportar_90_activos_modulares_fbx", "Batch export procedural modular kits to Unreal Engine 5 FBX."),
                ],
            ),
        ],
    )


def _aoe_blender_mcp_tools() -> List[MCPToolSummary]:
    return _build_tools(
        "aoe-blender-mcp",
        SubsystemDomain.ASSET_ORCHESTRATION_ENGINE,
        [
            (
                "blender-live-control",
                [
                    ("execute_blender_code", "Execute arbitrary Python (bpy) code inside the live Blender MCP socket server."),
                    ("get_scene_info", "Get detailed information about the current Blender scene, objects, and materials."),
                    ("get_object_info", "Retrieve transform, mesh topology, bounding box, and material slots for a Blender object."),
                    ("get_viewport_screenshot", "Capture and save a 3D viewport screenshot from the active Blender session."),
                    ("set_texture", "Apply downloaded or generated PBR texture maps onto a target Blender object material."),
                ],
            ),
            (
                "hunyuan3d-generation",
                [
                    ("generate_hunyuan3d_model", "Generate a 3D textured mesh asset via Tencent Hunyuan3D from text or reference image."),
                    ("get_hunyuan3d_status", "Check whether Hunyuan3D integration is enabled and configured in Blender MCP."),
                    ("poll_hunyuan_job_status", "Poll asynchronous Hunyuan3D generation job status until completion."),
                    ("import_generated_asset_hunyuan", "Import completed Hunyuan3D 3D model directly into the active Blender scene."),
                ],
            ),
            (
                "hyper3d-rodin-generation",
                [
                    ("generate_hyper3d_model_via_text", "Generate a 3D asset via Hyper3D Rodin from a natural language text prompt."),
                    ("generate_hyper3d_model_via_images", "Generate a 3D asset via Hyper3D Rodin from single or multi-view reference images."),
                    ("get_hyper3d_status", "Check Hyper3D Rodin API availability and quota status in Blender MCP."),
                    ("poll_rodin_job_status", "Poll Hyper3D Rodin asynchronous generation task status."),
                    ("import_generated_asset", "Import completed Hyper3D Rodin 3D mesh into the active Blender scene."),
                ],
            ),
            (
                "polyhaven-assets",
                [
                    ("get_polyhaven_status", "Verify PolyHaven API integration status in Blender MCP."),
                    ("get_polyhaven_categories", "List available PolyHaven asset categories for HDRIs, textures, or models."),
                    ("search_polyhaven_assets", "Search PolyHaven catalog for CC0 HDRIs, PBR texture sets, and 3D models."),
                    ("download_polyhaven_asset", "Download and import a PolyHaven HDRI, PBR texture set, or 3D model into Blender."),
                ],
            ),
            (
                "sketchfab-repository",
                [
                    ("get_sketchfab_status", "Check Sketchfab API authentication and integration status in Blender MCP."),
                    ("search_sketchfab_models", "Search downloadable 3D models in Sketchfab by keyword, category, and face count."),
                    ("get_sketchfab_model_preview", "Fetch thumbnail preview of a Sketchfab model before downloading."),
                    ("download_sketchfab_model", "Download and import a glTF/Blender model from Sketchfab into the active scene."),
                ],
            ),
        ],
    )


class UnifiedAnimationRegistry:
    """Central discovery and validation gateway across all 6 unified animation subsystems."""

    def __init__(self, monorepo_root: Optional[Path] = None) -> None:
        self.root: Path = (monorepo_root or DEFAULT_MONOREPO_ROOT).resolve()
        self._subsystems: Dict[str, SubsystemDescriptor] = {}
        self._build_registry()

    def _count_verified_files(self, rel_dir: str) -> int:
        target = _confine_to_root(self.root, rel_dir)
        if not target.exists():
            return 0
        return sum(1 for p in target.rglob("*") if _is_non_blank_file(p))

    def _build_registry(self) -> None:
        defs: List[SubsystemDescriptor] = [
            SubsystemDescriptor(
                id="ianimation-3d",
                name="IANIMATION 3D AI Orchestrator",
                domain=SubsystemDomain.AI_3D_ORCHESTRATOR,
                version="1.0.0",
                runtime="python",
                root_dir="packages/3d-ai-engine",
                entrypoint="backend/mcp/server.py",
                readme_path="packages/3d-ai-engine/README.md",
                command="python",
                args=["-m", "backend.main"],
                tool_count=len(_ianimation_3d_tools()),
                verified_files_count=self._count_verified_files("backend"),
                capabilities=[
                    "image-to-3d-volumetric",
                    "quad-remeshing",
                    "pbr-baking",
                    "se3-rigid-articulation",
                    "two-bone-ik",
                    "blender-headless",
                    "unreal-engine-5-remote-control",
                    "tauri-3d-viewport",
                ],
                tools=_ianimation_3d_tools(),
            ),
            SubsystemDescriptor(
                id="adobe-animation-mcp",
                name="Adobe Animation Suite & Character Animator MCP",
                domain=SubsystemDomain.ADOBE_2D_SUITE,
                version="4.2.0",
                runtime="node",
                root_dir="packages/adobe-suite",
                entrypoint="packages/adobe-suite/src/index.ts",
                readme_path="packages/adobe-suite/README.md",
                command="npx",
                args=["tsx", "packages/adobe-suite/src/index.ts"],
                tool_count=len(_adobe_suite_tools()),
                verified_files_count=self._count_verified_files("packages/adobe-suite"),
                capabilities=[
                    "character-animator-psd-rigging",
                    "14-mouth-visemes",
                    "head-turner-multi-angle",
                    "illustrator-vector-slicing",
                    "neural-tts-48khz-lipsync",
                    "after-effects-25d-stage",
                    "blender-grease-pencil",
                ],
                tools=_adobe_suite_tools(),
            ),
            SubsystemDescriptor(
                id="after-effects-motion-engine",
                name="After Effects Motion Graphics & VFX Engine",
                domain=SubsystemDomain.AFTER_EFFECTS_VFX,
                version="3.0.0",
                runtime="node",
                root_dir="packages/motion-vfx",
                entrypoint="packages/motion-vfx/src/index.ts",
                readme_path="packages/motion-vfx/README.md",
                command="npx",
                args=["tsx", "packages/motion-vfx/src/index.ts"],
                tool_count=len(_motion_vfx_tools()),
                verified_files_count=self._count_verified_files("packages/motion-vfx"),
                capabilities=[
                    "after-effects-extendscript-ir",
                    "kinetic-typography-brutalist",
                    "beat-sync-speed-ramps",
                    "kodak-film-emulation",
                    "snorricam-and-dolly-zoom",
                    "anamorphic-and-flir-photonics",
                    "autonomous-vlog-and-dataviz",
                    "editorial-qa-validation",
                ],
                tools=_motion_vfx_tools(),
            ),
            SubsystemDescriptor(
                id="stykanimate-mcp",
                name="StykAnimate 2D Stick-Figure IK Engine",
                domain=SubsystemDomain.STICK_2D_IK,
                version="0.1.0",
                runtime="node",
                root_dir="packages/stick-animator",
                entrypoint="packages/stick-animator/stykanimate-mcp/src/index.js",
                readme_path="packages/stick-animator/README.md",
                command="node",
                args=["packages/stick-animator/stykanimate-mcp/src/index.js"],
                tool_count=len(_stick_animator_tools()),
                verified_files_count=self._count_verified_files("packages/stick-animator"),
                capabilities=[
                    "2d-stick-figure-ik",
                    "styk-stkz-stykmov-codec",
                    "pivot-piv-stk-bridge",
                    "headless-pose-solver",
                    "html5-and-mp4-export",
                ],
                tools=_stick_animator_tools(),
            ),
            SubsystemDescriptor(
                id="blender-procedural-lab",
                name="Blender 5.2 Procedural 3D & PBR Texture Lab",
                domain=SubsystemDomain.BLENDER_PROCEDURAL_LAB,
                version="1.0.0",
                runtime="blender-python",
                root_dir="packages/blender-procedural-lab",
                entrypoint="packages/blender-procedural-lab/README.md",
                readme_path="packages/blender-procedural-lab/README.md",
                command="E:\\Blender\\blender.exe",
                args=["--factory-startup", "-b", "-P"],
                tool_count=len(_blender_lab_tools()),
                verified_files_count=self._count_verified_files("packages/blender-procedural-lab"),
                capabilities=[
                    "shader-balls-material-test-bench",
                    "2k-pbr-orm-normal-synthesis",
                    "modular-kits-90-assets",
                    "3d-bestiary-and-arsenal",
                    "bimanual-ik-solvers",
                    "ue5-fbx-batch-export",
                ],
                tools=_blender_lab_tools(),
            ),
            SubsystemDescriptor(
                id="aoe-blender-mcp",
                name="Asset Orchestration Engine (AOE) & Universal Asset Factory",
                domain=SubsystemDomain.ASSET_ORCHESTRATION_ENGINE,
                version="1.0.0",
                runtime="python",
                root_dir="packages/asset-orchestration-engine",
                entrypoint="packages/asset-orchestration-engine/mcp/blender/blender_mcp_addon.py",
                readme_path="packages/asset-orchestration-engine/README.md",
                command="python",
                args=["packages/asset-orchestration-engine/runner.py"],
                tool_count=len(_aoe_blender_mcp_tools()),
                verified_files_count=self._count_verified_files("packages/asset-orchestration-engine"),
                capabilities=[
                    "deterministic-intent-compiler-f1-f80",
                    "universal-asset-factory-uaf",
                    "wfc-2d-3d-procedural-levels",
                    "macro-landscape-hydraulic-erosion-r16",
                    "goap-multi-agent-npc-ai",
                    "hunyuan3d-and-hyper3d-rodin",
                    "polyhaven-and-sketchfab-bridge",
                    "ue5-portable-asset-bundling",
                ],
                tools=_aoe_blender_mcp_tools(),
            ),
        ]
        self._subsystems = {item.id: item for item in defs}

    def list_subsystems(self) -> List[SubsystemDescriptor]:
        """Return descriptors for all registered monorepo subsystems."""
        return list(self._subsystems.values())

    def get_subsystem(self, subsystem_id: str) -> SubsystemDescriptor:
        """Retrieve a subsystem descriptor by ID or raise KeyError."""
        if subsystem_id not in self._subsystems:
            raise KeyError(f"Unknown subsystem '{subsystem_id}'. Available: {list(self._subsystems.keys())}")
        return self._subsystems[subsystem_id]

    def count_procedural_generators(self) -> int:
        """Count verified Python generator/exporter scripts inside blender-procedural-lab."""
        lab_root = _confine_to_root(self.root, "packages/blender-procedural-lab")
        count = 0
        for sub in ("generators", "exporters"):
            sub_dir = lab_root / sub
            if sub_dir.exists():
                count += sum(1 for p in sub_dir.rglob("*.py") if _is_non_blank_file(p))
        return count

    def search_tools(self, query: str, domain: Optional[str] = None) -> List[MCPToolSummary]:
        """Search registered tools case-insensitively across subsystems."""
        q = query.strip().lower()
        dom_filter = domain.strip().lower() if domain else None
        results: List[MCPToolSummary] = []

        for subsystem in self._subsystems.values():
            if dom_filter and subsystem.domain.value != dom_filter and subsystem.id != dom_filter:
                continue
            for tool in subsystem.tools:
                if not q:
                    results.append(tool)
                    continue
                haystack = f"{tool.name} {tool.category} {tool.description} {tool.subsystem_id}".lower()
                cap_match = any(q in cap.lower() for cap in subsystem.capabilities)
                if q in haystack or cap_match:
                    results.append(tool)
        return results

    def validate_monorepo_integrity(self) -> MonorepoIntegrityReport:
        """Verify all 5 packages exist on disk, entrypoints exist, and 0 blank/corrupt files reside in packages/."""
        missing_paths: List[str] = []
        subsystems_status: Dict[str, bool] = {}

        for sub in self._subsystems.values():
            ok = True
            for rel in (sub.root_dir, sub.entrypoint, sub.readme_path):
                resolved = _confine_to_root(self.root, rel)
                if not resolved.exists():
                    missing_paths.append(rel)
                    ok = False
                elif resolved.is_file() and not _is_non_blank_file(resolved):
                    missing_paths.append(f"{rel} (corrupt/blank)")
                    ok = False
            subsystems_status[sub.id] = ok

        packages_root = _confine_to_root(self.root, "packages")
        corrupt_files_detected = 0
        if packages_root.exists():
            for p in packages_root.rglob("*"):
                if p.is_file() and not _is_non_blank_file(p):
                    corrupt_files_detected += 1

        total_mcp_tools = sum(
            s.tool_count for s in self._subsystems.values() if s.domain != SubsystemDomain.BLENDER_PROCEDURAL_LAB
        )
        total_generators = self.count_procedural_generators()
        is_valid = (
            all(subsystems_status.values())
            and len(missing_paths) == 0
            and corrupt_files_detected == 0
            and len(self._subsystems) == 6
        )

        return MonorepoIntegrityReport(
            is_valid=is_valid,
            monorepo_root=str(self.root),
            total_subsystems=len(self._subsystems),
            total_mcp_tools=total_mcp_tools,
            total_procedural_generators=total_generators,
            corrupt_files_detected=corrupt_files_detected,
            subsystems_status=subsystems_status,
            missing_paths=missing_paths,
        )

    def build_mcp_config(self) -> MCPConfigPayload:
        """Build standard ``mcpServers`` dictionary ready for Claude/Cursor/Antigravity."""
        servers: Dict[str, Dict[str, Union[str, List[str]]]] = {}
        for sub in self._subsystems.values():
            if sub.domain == SubsystemDomain.BLENDER_PROCEDURAL_LAB:
                continue
            servers[sub.id] = {
                "command": sub.command,
                "args": list(sub.args),
                "cwd": str(_confine_to_root(self.root, ".")),
            }
        return {"mcpServers": servers}

    def export_mcp_config(
        self,
        output_path: Optional[Path] = None,
    ) -> MCPConfigPayload:
        """Write ``mcp_servers.config.json`` confined to monorepo root."""
        config = self.build_mcp_config()
        target = output_path or (self.root / "mcp_servers.config.json")
        if target.is_absolute():
            rel_str = str(target.resolve().relative_to(self.root))
        else:
            rel_str = str(target)
        resolved_target = _confine_to_root(self.root, rel_str)
        resolved_target.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        return config


_default_registry: Optional[UnifiedAnimationRegistry] = None


def get_unified_registry() -> UnifiedAnimationRegistry:
    """Return process-wide singleton ``UnifiedAnimationRegistry`` instance."""
    global _default_registry
    if _default_registry is None:
        _default_registry = UnifiedAnimationRegistry()
    return _default_registry
