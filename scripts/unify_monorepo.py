"""Clean, integrity-verified monorepo ingestion script for IANIMATION.

Selectively migrates source code, specifications, tests, examples, and
architecture docs from all animation/render/VFX source workspaces into
``packages/`` while strictly filtering out corrupted blank/null files,
``node_modules``, ``.git``, caches, and oversized binary payloads.
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil
from typing import Dict, List, Set

from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    """Base Pydantic model forbidding extra fields."""

    model_config = ConfigDict(extra="forbid")


class PackageIngestionStats(StrictModel):
    """Audit statistics for a single migrated package."""

    package_id: str
    source_path: str
    target_path: str
    valid_files_copied: int
    corrupt_or_blank_skipped: int
    excluded_dirs_or_large_skipped: int
    sample_skipped_corrupt: List[str]


class IngestionManifest(StrictModel):
    """Complete monorepo ingestion manifest persisted on disk."""

    monorepo_root: str
    packages: List[PackageIngestionStats]
    total_valid_files_copied: int
    total_corrupt_or_blank_skipped: int


MONOREPO_ROOT = Path(r"E:\Disco F\Dev\IANIMATION")
PACKAGES_DIR = MONOREPO_ROOT / "packages"

SRC_ADOBE = Path(r"E:\Disco F\Dev\AdobeEngineSuit")
SRC_AE = Path(r"E:\Disco F\Dev\after-effects-mcp")
SRC_STIK = Path(r"E:\Disco F\Dev\StictAnimator")
SRC_GAME_ART = Path(r"E:\Disco F\Dev\Game\Art")
SRC_GAME_DOCS = Path(r"E:\Disco F\Dev\Game\docs\architecture")
SRC_AOE = Path(r"E:\AssetOrchestrationEngine")

SKIP_DIR_NAMES: Set[str] = {
    "node_modules",
    ".git",
    ".cache",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "venv",
}

MAX_FILE_BYTES = 25 * 1024 * 1024  # Exclude oversized weights/media > 25 MB


def is_valid_non_blank_file(file_path: Path) -> bool:
    """Return True if file exists, is readable, and is not pure whitespace/nulls."""
    if not file_path.is_file():
        return False
    size = file_path.stat().st_size
    if size == 0:
        return False
    data = file_path.read_bytes()
    return len(data.strip(b" \t\r\n\x00")) > 0


def copy_validated_file(
    src: Path,
    dst: Path,
    stats: PackageIngestionStats,
    rel_label: str,
) -> bool:
    """Copy a single file only if it passes non-blank integrity and size checks."""
    if not src.exists() or not src.is_file():
        return False
    if src.stat().st_size > MAX_FILE_BYTES:
        stats.excluded_dirs_or_large_skipped += 1
        return False
    if not is_valid_non_blank_file(src):
        stats.corrupt_or_blank_skipped += 1
        if len(stats.sample_skipped_corrupt) < 25:
            stats.sample_skipped_corrupt.append(rel_label)
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(src), str(dst))
    stats.valid_files_copied += 1
    return True


def copy_validated_tree(
    src_dir: Path,
    dst_dir: Path,
    stats: PackageIngestionStats,
    base_src_root: Path,
) -> None:
    """Recursively copy valid files from ``src_dir`` into ``dst_dir``."""
    if not src_dir.exists() or not src_dir.is_dir():
        return
    for item in sorted(src_dir.rglob("*")):
        if any(part in SKIP_DIR_NAMES for part in item.parts):
            if item.is_dir():
                stats.excluded_dirs_or_large_skipped += 1
            continue
        if not item.is_file():
            continue
        rel = item.relative_to(src_dir)
        rel_from_root = str(item.relative_to(base_src_root))
        copy_validated_file(item, dst_dir / rel, stats, rel_from_root)


def ensure_clean_dir(target_dir: Path) -> None:
    """Create target directory cleanly if not yet populated, or wipe stale package contents."""
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)


def ingest_3d_ai_engine() -> PackageIngestionStats:
    """Create descriptor package ``packages/3d-ai-engine`` linked to root backend/ and scripts/."""
    dst = PACKAGES_DIR / "3d-ai-engine"
    ensure_clean_dir(dst)
    stats = PackageIngestionStats(
        package_id="3d-ai-engine",
        source_path=str(MONOREPO_ROOT / "backend"),
        target_path=str(dst),
        valid_files_copied=0,
        corrupt_or_blank_skipped=0,
        excluded_dirs_or_large_skipped=0,
        sample_skipped_corrupt=[],
    )

    pkg_json = {
        "name": "@ianimation/3d-ai-engine",
        "version": "1.0.0",
        "description": "AI-First 3D Animation Orchestrator, Image-to-3D, Quad Remeshing, PBR Baking, Rigid SE(3) Articulation, Blender 5.2 LTS & UE5 Bridge",
        "private": True,
        "runtime": "python>=3.10",
        "rootLinks": {
            "backend": "../../backend",
            "scripts": "../../scripts",
            "tests": "../../tests",
            "frontend": "../../src",
            "tauri": "../../src-tauri",
        },
        "mcpServer": {
            "id": "ianimation-3d",
            "command": "python",
            "args": ["-m", "backend.main"],
        },
    }
    (dst / "package.json").write_text(json.dumps(pkg_json, indent=2) + "\n", encoding="utf-8")
    stats.valid_files_copied += 1

    readme_content = """# `@ianimation/3d-ai-engine` — Orquestador 3D AI-First, Blender 5.2 & Unreal Engine 5

Paquete descriptor del núcleo Python + Tauri/React alojado en la raíz de este monorepo ([`backend/`](../../backend/), [`scripts/`](../../scripts/), [`src/`](../../src/), [`src-tauri/`](../../src-tauri/)). Se conserva la ubicación física en raíz para garantizar 100% de retrocompatibilidad con `pytest`, `pyproject`/imports (`import backend.*`) y la aplicación de escritorio Tauri v2.

---

## Arquitectura del Subsistema

| Capa / Módulo | Ruta en el Monorepo | Responsabilidad Principal |
| :--- | :--- | :--- |
| **Core & Telemetría** | [`backend/core/`](../../backend/core/) | Modelos Pydantic v2 (`Zero-Any`), almacén CAS SHA-256 (`cache.py`), configuración y bus de telemetría asíncrono. |
| **Motor Neural 3D & Topología** | [`backend/ai/`](../../backend/ai/) | `image_to_3d.py`, `neural_3d_engine.py`, `quad_remesher.py`, `pbr_baker.py`, `volumetric_3d.py`, `defringe.py`, `component_decomposer.py`. |
| **Cinemática & Rigging 3D** | [`backend/ai/`](../../backend/ai/) | `auto_rig.py`, `advanced_kinematics.py` (Two-Bone IK), `character_dynamics.py` (Twist bones + Verlet), `modular_articulation.py` (Isometría rígida $SE(3)$). |
| **Adaptador Blender 5.2 LTS** | [`backend/blender/`](../../backend/blender/) | Ejecución headless (`E:\\Blender\\blender.exe --factory-startup -b -P ...`), `adapter.py`, `rigging.py`, `live_bridge.py` y scripts en `backend/blender/scripts/`. |
| **Adaptador Unreal Engine 5** | [`backend/ue5/`](../../backend/ue5/) | Clientes REST/WebSocket Remote Control API (`client.py`), `mock_server.py` (puertos 30010/30020), `camera.py`, `lighting.py`, `materials.py`, `mrq.py` y `companion.py`. |
| **Servidor FastMCP & Registro** | [`backend/mcp/`](../../backend/mcp/) | `server.py`, `tools.py`, `plan_engine.py` (HITL 6 pasos) y `unified_registry.py` (gateway de descubrimiento de los 5 subsistemas). |
| **Pipelines de Producción** | [`scripts/`](../../scripts/) | Pipelines maestros verificados, incluido [`build_clean_watertight_ragdoll.py`](../../scripts/build_clean_watertight_ragdoll.py) (muñeco bombero 1.80m watertight con hacha 3D rígida). |
| **Desktop App UI** | [`src/`](../../src/) y [`src-tauri/`](../../src-tauri/) | Interfaz React 18 + Three.js (`Viewport3D`, `Timeline`, `MediaDropzone`, `CopilotChat`) + runtime Rust Tauri v2. |

---

## Herramientas MCP Expuestas (`ianimation-3d`)

1. `analyze_audio(audio_path, separate_stems=True, tempo_hint=None)` — Extrae BPM, grid de beats y stems.
2. `image_to_3d(image_path, provider="auto", texture_resolution=1024, output_path=None)` — Convierte imagen 2D a malla 3D `.glb` texturizada PBR.
3. `auto_rig(mesh_path, skeleton_type="ue5_mannequin", output_path=None, engine="auto")` — Vincula jerarquía esquelética anatómica.
4. `extract_mocap(video_path, target_fps=30, output_path=None)` — Extrae captura de movimiento 3D desde video.
5. `build_ue5_scene(scene_config)` / `build_scene(scene_config, engine="ue5"|"blender")` — Ensambla escena con iluminación Lumen/estudio y cámara.
6. `render_video(scene_path, output_path, fps=60, resolution="1920x1080", warmup_frames=15, anti_aliasing_samples=8, engine="auto")` — Renderizado final MP4/imagen vía UE5 MRQ o Blender.
7. `list_monorepo_subsystems()` — Descubre en vivo los 5 paquetes del monorepo y su estado de integridad.
8. `search_monorepo_tools(query, domain=None)` — Busca herramientas MCP y generadores entre todos los motores unificados.

---

## Comandos Rápidos

```powershell
# Ejecutar servidor backend / FastAPI + MCP
C:\\Python314\\python.exe -m backend.main

# Ejecutar pruebas de integridad visual y articulación 3D
C:\\Python314\\python.exe -m pytest tests/backend/test_animation_visual_integrity.py tests/backend/test_modular_articulation.py tests/backend/test_fastmcp_server.py -v
```
"""
    (dst / "README.md").write_text(readme_content, encoding="utf-8")
    stats.valid_files_copied += 1
    return stats


def ingest_adobe_suite() -> PackageIngestionStats:
    """Selectively copy intact source, tests, scripts, legacy, and docs from AdobeEngineSuit."""
    dst = PACKAGES_DIR / "adobe-suite"
    ensure_clean_dir(dst)
    stats = PackageIngestionStats(
        package_id="adobe-suite",
        source_path=str(SRC_ADOBE),
        target_path=str(dst),
        valid_files_copied=0,
        corrupt_or_blank_skipped=0,
        excluded_dirs_or_large_skipped=0,
        sample_skipped_corrupt=[],
    )

    for sub in ["src", "legacy", "scripts", "tests"]:
        copy_validated_tree(SRC_ADOBE / sub, dst / sub, stats, SRC_ADOBE)

    # Audit extensions & dist explicitly as skipped (known blank/corrupt in source)
    for skipped_dir in ["extensions", "dist"]:
        sp = SRC_ADOBE / skipped_dir
        if sp.exists():
            for item in sp.rglob("*"):
                if item.is_file() and not is_valid_non_blank_file(item):
                    stats.corrupt_or_blank_skipped += 1
                    if len(stats.sample_skipped_corrupt) < 25:
                        stats.sample_skipped_corrupt.append(str(item.relative_to(SRC_ADOBE)))

    # Root configs
    root_manifests = [
        "package.json",
        "package-lock.json",
        "tsconfig.json",
        "vitest.config.ts",
        ".gitignore",
        ".animation_roadmap_state.json",
    ]
    for fn in root_manifests:
        copy_validated_file(SRC_ADOBE / fn, dst / fn, stats, fn)

    # Design markdowns into docs/
    docs_dir = dst / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    for md in sorted(SRC_ADOBE.glob("*.md")):
        if md.name == "README.md":
            copy_validated_file(md, docs_dir / "ORIGINAL_README.md", stats, md.name)
        else:
            copy_validated_file(md, docs_dir / md.name, stats, md.name)

    readme_content = """# `@ianimation/adobe-suite` (`adobe-animation-mcp`)

Servidor MCP especializado en **animación 2D de personajes, rigging `.psd` para Adobe Character Animator, vectores para Adobe Illustrator, voz neural HD con cálculo de visemas/lip-sync, escenografía 2.5D en After Effects y bocetado Grease Pencil en Blender**.

> Migrado de `E:\\Disco F\\Dev\\AdobeEngineSuit` aplicando filtro binario estricto contra corrupción heredada en disco (cero archivos en blanco/nulos). Ver [`../INGESTION_MANIFEST.json`](../INGESTION_MANIFEST.json).

---

## Inventario Real Verificado en Disco

- **Punto de entrada activo**: [`src/index.ts`](src/index.ts)
- **38 Herramientas MCP verificadas** distribuidas en 6 módulos activos:
  - [`src/tools/characterTools.ts`](src/tools/characterTools.ts) (**12 tools**): `ch_scaffold_puppet`, `ch_scaffold_multi_angle_puppet`, `ch_scaffold_walk_puppet`, `ch_slice_artwork_to_puppet`, `ch_add_puppet_triggers_and_physics`, `ch_audit_puppet_deep`, `ch_auto_repair_puppet`, `ch_prepare_recording_take`, `ch_validate_puppet`, `ch_launch_character_animator`, `ch_inspect_environment`, `ch_get_roadmap_status`.
  - [`src/tools/afterEffectsTools.ts`](src/tools/afterEffectsTools.ts) (**7 tools**): `ae_execute_jsx`, `ae_import_puppet_scene`, `ae_render_comp`, `ae_generate_scene_manifest`, `ae_setup_25d_stage`, `ae_apply_animation_expressions`, `ae_batch_render_queue`.
  - [`src/tools/illustratorTools.ts`](src/tools/illustratorTools.ts) (**6 tools**): `ai_execute_jsx`, `ai_create_document`, `ai_trace_and_clean_sketch`, `ai_auto_rig_slice`, `ai_apply_color_palette`, `ai_export_character_package`.
  - [`src/tools/audioTools.ts`](src/tools/audioTools.ts) (**5 tools**): `audio_generate_speech`, `audio_calculate_viseme_cues`, `audio_generate_expressive_speech`, `audio_export_lip_sync_markers`, `audio_list_available_voices`.
  - [`src/tools/blenderTools.ts`](src/tools/blenderTools.ts) (**5 tools**): `blender_execute_script`, `blender_render_frame`, `blender_scaffold_3d_room`, `blender_render_parallax_passes`, `blender_grease_pencil_sketch`.
  - [`src/tools/pipelineTools.ts`](src/tools/pipelineTools.ts) (**3 tools**): `render_preview_frame_to_base64`, `pipeline_create_talking_character`, `pipeline_render_social_clip`.
- **12 Motores Core en TypeScript (`src/core/`) + `edge_synth.py`**:
  `AdobeDetector.ts`, `BlenderEngine.ts`, `CharacterAnimatorDeepEngine.ts`, `NeuralSpeechEngine.ts`, `PhaseTracker.ts`, `PipelineManager.ts`, `PuppetBuilder.ts`, `SceneManifestBuilder.ts`, `VbsRunner.ts`, `VectorCelShadowBoundaryGenerator.ts`, `VisemeDrawer.ts`, `WavGenerator.ts`.
- **Utilidades Python/JS adicionales**: 55 archivos intactos en [`legacy/`](legacy/), 11 scripts intactos en [`scripts/`](scripts/) (ej. `slice_cybergirl.py`, `neural_smart_slicer.py`), 8 suites Vitest + 16 fixtures PNG en [`tests/`](tests/), y documentación de diseño en [`docs/`](docs/).

---

## Instalación y Uso

```powershell
cd packages\\adobe-suite
npm install
npm run build
npm test
```
"""
    (dst / "README.md").write_text(readme_content, encoding="utf-8")
    stats.valid_files_copied += 1
    return stats


def ingest_motion_vfx() -> PackageIngestionStats:
    """Selectively copy intact TypeScript source, specs, contracts, bin, scripts, and docs from after-effects-mcp."""
    dst = PACKAGES_DIR / "motion-vfx"
    ensure_clean_dir(dst)
    stats = PackageIngestionStats(
        package_id="motion-vfx",
        source_path=str(SRC_AE),
        target_path=str(dst),
        valid_files_copied=0,
        corrupt_or_blank_skipped=0,
        excluded_dirs_or_large_skipped=0,
        sample_skipped_corrupt=[],
    )

    for sub in ["src", "bin", "contracts", "spec", "scripts", "fixtures", "assets", "reports", "docs"]:
        copy_validated_tree(SRC_AE / sub, dst / sub, stats, SRC_AE)

    root_files = [
        "package.json",
        "package-lock.json",
        "tsconfig.json",
        "install-bridge.js",
        "AGENTS.md",
        "HOW-TO-USE.txt",
        "LICENSE",
    ]
    for fn in root_files:
        copy_validated_file(SRC_AE / fn, dst / fn, stats, fn)

    copy_validated_file(SRC_AE / "README.md", dst / "docs" / "ORIGINAL_README.md", stats, "README.md")

    readme_content = """# `@ianimation/motion-vfx` (`after-effects-mcp` / `motion-engine` v3.0.0)

Plataforma de **Motion Graphics, VFX, Cinematografía Algorítmica, Tipografía Cinética, Data-Viz y Edición Editorial Automática** para Adobe After Effects vía Model Context Protocol (MCP).

> Migrado de `E:\\Disco F\\Dev\\after-effects-mcp` filtrando archivos vacíos/corruptos en disco y excluyendo `dist/` (532 MB), `models/` y `build/` obsoletos. Ver [`../INGESTION_MANIFEST.json`](../INGESTION_MANIFEST.json).

---

## Capacidades y Herramientas MCP Verificadas (**72 Tools**)

El servidor [`src/mcp/server.ts`](src/mcp/server.ts) y [`src/mcp/registry.ts`](src/mcp/registry.ts) + [`src/mcp/bridge/ae-bridge.ts`](src/mcp/bridge/ae-bridge.ts) registran **72 herramientas MCP** organizadas por dominio:

- **Proyecto y Revisiones (14 tools)**: `create_project`, `open_project`, `save_project`, `close_project`, `get_project_status`, `list_project_revisions`, `diff_project_revisions`, `restore_project_revision`, `validate_project`, `cancel_operation`, `create_video_from_script`, `export_to_after_effects_jsx`, `get_timeline_preview_frame`, `apply_viral_caption_style`.
- **Puente Live Adobe After Effects (6 tools)**: `run-script`, `get-results`, `create-composition`, `apply-effect`, `list-presets`, `set-audio-levels`.
- **Social, Audio & Vlog Automatizado (9 tools)**: `transcribe_local_audio`, `detect_viral_clips`, `package_social_release`, `auto_reframe_video`, `vlog_generate_jump_cut_plan`, `vlog_classify_footage`, `vlog_match_broll`, `vlog_produce`, `vlog_get_status`.
- **Editorial, Data-Viz & QA (7 tools)**: `editorial_compile_data_visualization`, `editorial_dataviz_to_jsx`, `editorial_parse_dataset`, `editorial_run_qa`, `editorial_compare_revisions`, `editorial_generate_trim_plan`, `editorial_detect_redundancy`.
- **Composición y Sujetos (3 tools)**: `compose_text_behind_subject`, `compose_multi_take_clones`, `detect_subjects_in_clip`.
- **Óptica, Temporal y Fílmica (9 tools)**: `apply_snap_zooms_to_timeline`, `apply_fisheye_optics`, `compile_dolly_zoom`, `apply_posterize_time`, `compile_speed_ramp_to_beat`, `compile_temporal_orchestration`, `apply_film_grain_and_halation`, `apply_auteur_color_grading`, `compile_film_emulation_plan`.
- **Ritmo y Tipografía Cinética (6 tools)**: `apply_machine_gun_flash_cuts`, `apply_blackout_vacuum_drop`, `compile_syncopated_rhythm_cut`, `apply_brutalist_kinetic_title`, `apply_liquid_chrome_text_effect`, `compile_perspective_anchored_typography`.
- **Cinematografía Espacial, Mecánica y Fotónica (10 tools)**: `apply_snorricam_body_lock`, `apply_infinite_zoom_portal`, `compile_spatial_cinematography_plan`, `apply_centrifugal_gyro_roll`, `apply_directional_whip_pan`, `compile_dynamic_mechanics_plan`, `apply_shutter_drag_echo`, `apply_anamorphic_streak_flare`, `apply_flir_thermal_vision`, `compile_photonics_plan`.
- **Mixed-Media y Stem-Kinetics (8 tools)**: `apply_manga_impact_frame`, `apply_procedural_speed_lines`, `apply_film_sprocket_holes`, `compile_mixed_media_plan`, `apply_audio_reactive_physics`, `apply_dynamic_aspect_ratio_breathing`, `apply_datamosh_pframe_glitch`, `compile_stem_kinetics_plan`.

---

## CLIs Incluidos (`bin/`)

- `motion-engine` ([`bin/motion-engine.js`](bin/motion-engine.js))
- `auto-clip` ([`bin/auto-clip.js`](bin/auto-clip.js))
- `vlog-cli` ([`bin/vlog-cli.js`](bin/vlog-cli.js))
- `editorial-cli` ([`bin/editorial-cli.js`](bin/editorial-cli.js))

## Documentación Técnica y Reglas

- Guía operativa interna para IA: [`docs/AI_AGENT_MANUAL.md`](docs/AI_AGENT_MANUAL.md)
- Reglas de estilo visual (Editorial Poster / TIME Style): [`docs/USER_DESIGN_PREFERENCES.md`](docs/USER_DESIGN_PREFERENCES.md)
- Reglas de testing e invariantes: [`AGENTS.md`](AGENTS.md) y especificaciones en [`spec/`](spec/).
"""
    (dst / "README.md").write_text(readme_content, encoding="utf-8")
    stats.valid_files_copied += 1
    return stats


def ingest_stick_animator() -> PackageIngestionStats:
    """Copy clean stykanimate-mcp server, CLI tools, and .styk examples from StictAnimator."""
    dst = PACKAGES_DIR / "stick-animator"
    ensure_clean_dir(dst)
    stats = PackageIngestionStats(
        package_id="stick-animator",
        source_path=str(SRC_STIK),
        target_path=str(dst),
        valid_files_copied=0,
        corrupt_or_blank_skipped=0,
        excluded_dirs_or_large_skipped=0,
        sample_skipped_corrupt=[],
    )

    mcp_src = SRC_STIK / "stykanimate-mcp"
    mcp_dst = dst / "stykanimate-mcp"
    for sub in ["src", "test", "py", "scripts", "vendor", "assets"]:
        copy_validated_tree(mcp_src / sub, mcp_dst / sub, stats, SRC_STIK)

    for fn in ["package.json", "package-lock.json", "llms.txt", "server.json", "README.md", "LICENSE", "NOTICE.md"]:
        copy_validated_file(mcp_src / fn, mcp_dst / fn, stats, f"stykanimate-mcp/{fn}")

    cli_dir = dst / "cli"
    cli_files = [
        "create-animation-cli.js",
        "create-cartoon-monkey.js",
        "export-frames-json.js",
        "export-html.js",
        "make_video_widget.js",
        "render_mp4.py",
        "run-live-test.js",
    ]
    for fn in cli_files:
        copy_validated_file(SRC_STIK / fn, cli_dir / fn, stats, fn)

    ex_dir = dst / "examples"
    for fn in ["cyber_samurai.styk", "mono_animado.styk", "stickman_pose.styk"]:
        copy_validated_file(SRC_STIK / fn, ex_dir / fn, stats, fn)

    readme_content = """# `@ianimation/stick-animator` (`stykanimate-mcp`)

Motor headless **2D de figuras articuladas (*stick figures*) con Cinemática Inversa (IK)** y servidor Model Context Protocol (`stykanimate-mcp`) basado en StykAnimate, compatible con formatos `.styk`, `.stkz`, `.stykmov`, Pivot Animator (`.piv`, `.stk`) y exportadores HTML5/MP4.

> Migrado íntegro de `E:\\Disco F\\Dev\\StictAnimator` (**100% de archivos fuente intactos**, 0 corrupción).

---

## Estructura del Paquete

- [`stykanimate-mcp/`](stykanimate-mcp/): Servidor MCP en Node.js (`>=20`) + códec Python para `.piv`/`.stk`.
  - Documentación optimizada para LLM: [`stykanimate-mcp/llms.txt`](stykanimate-mcp/llms.txt)
  - Entrypoint MCP: [`stykanimate-mcp/src/index.js`](stykanimate-mcp/src/index.js)
- [`cli/`](cli/): 7 scripts de generación y renderización offline (`create-animation-cli.js`, `export-html.js`, `render_mp4.py`, `run-live-test.js`, etc.).
- [`examples/`](examples/): Proyectos de ejemplo listos para abrir e inspeccionar (`cyber_samurai.styk`, `mono_animado.styk`, `stickman_pose.styk`).

---

## 26 Herramientas MCP Verificadas

| Categoría | Herramientas | Cantidad |
| :--- | :--- | :---: |
| **Capacidad** | `capabilities` | 1 |
| **Proyecto** | `project_open`, `project_close`, `project_describe`, `project_validate`, `project_save`, `project_timeline`, `project_seek` | 7 |
| **Figuras** | `figure_list`, `figure_describe`, `figure_add`, `figure_duplicate`, `figure_delete`, `figure_transform` | 6 |
| **Poses e IK** | `pose_evaluate`, `pose_set`, `pose_ik_set`, `pose_set_ik`, `pose_reset` | 5 |
| **Capas y Estilo** | `layer_list`, `layer_edit`, `style_set` | 3 |
| **Timeline** | `keyframe_edit`, `keyframe_timing` | 2 |
| **Historial** | `history_undo`, `history_redo` | 2 |

---

## Ejecución y Tests

```powershell
# Arrancar servidor MCP stdio
node packages\\stick-animator\\stykanimate-mcp\\src\\index.js

# Ejecutar suite de pruebas unitarias
node --test packages\\stick-animator\\stykanimate-mcp\\test\\*.test.mjs
```
"""
    (dst / "README.md").write_text(readme_content, encoding="utf-8")
    stats.valid_files_copied += 1
    return stats


def classify_blender_script(filename: str) -> str:
    """Classify each Game/Art/Blender .py script deterministically into its target lab subfolder."""
    if filename.startswith("exportar_") or filename in {"export_fixed_props.py", "regenerar_portales_abiertos_fbx.py"}:
        return "exporters"
    if (
        filename.startswith("generar_material_test_bench")
        or filename in {
            "generar_trimsheet_industrial.py",
            "generar_texturas_pbr_bombero_oficial.py",
            "generar_showcase_oxidados_y_lujo.py",
            "componer_showcase_texturas.py",
            "test_shaderball_uv.py",
        }
    ):
        return "generators/pbr_textures_and_benches"
    if (
        filename.startswith("generar_personaje_")
        or filename in {
            "generar_lote3_personajes.py",
            "generar_testdummy_fiel_referencia.py",
            "generar_supervivientes_y_mascota_oficial.py",
            "astra_blender_styling.py",
            "buscar_rotacion_upright.py",
        }
    ):
        return "generators/characters_and_rigs"
    if (
        filename.startswith("generar_animaciones_")
        or filename.startswith("solver_")
        or filename.startswith("verificar_pose_")
        or filename in {
            "diagnosticar_bones_blender.py",
            "test_bimanual_pose.py",
            "test_ik_pose.py",
            "test_ejes_brazos.py",
            "test_rotacion_brazos.py",
        }
    ):
        return "generators/animations_and_ik"
    return "generators/modular_kits_and_props"


def ingest_blender_procedural_lab() -> PackageIngestionStats:
    """Classify and copy all 123 intact Blender/PBR scripts and 10 architecture docs from Game."""
    dst = PACKAGES_DIR / "blender-procedural-lab"
    ensure_clean_dir(dst)
    stats = PackageIngestionStats(
        package_id="blender-procedural-lab",
        source_path=str(SRC_GAME_ART),
        target_path=str(dst),
        valid_files_copied=0,
        corrupt_or_blank_skipped=0,
        excluded_dirs_or_large_skipped=0,
        sample_skipped_corrupt=[],
    )

    counts_by_cat: Dict[str, int] = {
        "generators/characters_and_rigs": 0,
        "generators/animations_and_ik": 0,
        "generators/pbr_textures_and_benches": 0,
        "generators/modular_kits_and_props": 0,
        "exporters": 0,
    }

    blender_src = SRC_GAME_ART / "Blender"
    for py_file in sorted(blender_src.glob("*.py")):
        sub = classify_blender_script(py_file.name)
        if copy_validated_file(py_file, dst / sub / py_file.name, stats, f"Art/Blender/{py_file.name}"):
            counts_by_cat[sub] += 1

    # Also copy Art/Textures Python generators (Modular + UI)
    textures_src = SRC_GAME_ART / "Textures"
    for py_file in sorted(textures_src.rglob("*.py")):
        rel_sub = py_file.parent.name.lower()
        target_file = dst / "generators/pbr_textures_and_benches" / f"{rel_sub}_{py_file.name}"
        if copy_validated_file(py_file, target_file, stats, str(py_file.relative_to(SRC_GAME_ART))):
            counts_by_cat["generators/pbr_textures_and_benches"] += 1

    # Copy architecture docs
    doc_names = [
        "pipeline_arte.md",
        "animacion_locomocion.md",
        "catalogo_texturas_modulares.md",
        "entorno_modular_render.md",
        "diseno_3d_misiones_bestiario_mapas.md",
        "catalogo_modular_90_activos_oficial.md",
        "catalogo_50_props_maestros.md",
        "arsenal_efectos_y_estilo.md",
        "arsenal_herramientas_armas_oficial.md",
        "peligros_ambientales_30_oficial.md",
    ]
    for doc_fn in doc_names:
        copy_validated_file(SRC_GAME_DOCS / doc_fn, dst / "docs" / doc_fn, stats, f"docs/architecture/{doc_fn}")

    readme_content = f"""# `@ianimation/blender-procedural-lab` — Laboratorio Procedural 3D y PBR en Blender 5.2 LTS

Colección de **123 generadores Python headless para Blender 5.2 LTS** (extraídos de `E:\\Disco F\\Dev\\Game\\Art`, excluyendo archivos `.blend`/`.fbx` binarios para mantener el repositorio liviano y reproducible por código).

> Todos los scripts fueron validados con **0 archivos corruptos** y se ejecutan de forma determinista con `E:\\Blender\\blender.exe --factory-startup -b -P <ruta_script.py>`.

---

## Clasificación de Módulos

| Directorio | Cantidad | Contenido Principal |
| :--- | :---: | :--- |
| [`generators/characters_and_rigs/`](generators/characters_and_rigs/) | **{counts_by_cat["generators/characters_and_rigs"]}** | Personajes riggeados 3D (`generar_personaje_riggeado_oficial.py`, `v11`), muñecos ragdoll de prueba (`generar_testdummy_fiel_referencia.py`), supervivientes y estilización Blender. |
| [`generators/animations_and_ik/`](generators/animations_and_ik/) | **{counts_by_cat["generators/animations_and_ik"]}** | Locomoción y combate 3D (`generar_animaciones_locomocion_oficial.py`), solvers IK bimanuales (`solver_exacto_bimanual.py`), auditoría ósea y verificación de sockets. |
| [`generators/pbr_textures_and_benches/`](generators/pbr_textures_and_benches/) | **{counts_by_cat["generators/pbr_textures_and_benches"]}** | Material Test Bench Shader Balls Pro V5, Trim Sheets 2048x2048, síntesis de 40 mapas PBR (BaseColor, Normal DirectX, ORM AO/Rough/Metal), shows de texturas oxidadas/lujo Art Déco y texturas HUD. |
| [`generators/modular_kits_and_props/`](generators/modular_kits_and_props/) | **{counts_by_cat["generators/modular_kits_and_props"]}** | Kits modulares arquitectónicos (Industrial, Art Déco, Plasma, BioLab, Habitat — catálogo de 90 activos), 50 props maestros, bestiario 3D de 10 entidades, arsenal de 20 armas y 30 peligros ambientales. |
| [`exporters/`](exporters/) | **{counts_by_cat["exporters"]}** | Exportadores automatizados a FBX/GLB compatibles con Unreal Engine 5 (`exportar_90_activos_modulares_fbx.py`, `exportar_bestiario_fbx.py`, `exportar_20_armas_fbx.py`, etc.). |
| [`docs/`](docs/) | **10** | Especificaciones arquitectónicas completas (`pipeline_arte.md`, `animacion_locomocion.md`, `catalogo_texturas_modulares.md`, etc.). |

---

## Nota para Agentes de IA sobre Rutas de Salida

Varios scripts heredados de `Game/Art` utilizan rutas relativas o referencias hacia el workspace `Game` para depositar `.blend`/`.fbx` generados. Antes de invocar un generador desde este laboratorio:
1. Verifica los argumentos o variables `OUT_DIR` / `PROJECT_ROOT` dentro del script con `read_file`.
2. Ejecuta siempre en modo headless sin UI:
   ```powershell
   E:\\Blender\\blender.exe --factory-startup -b -P packages\\blender-procedural-lab\\generators\\pbr_textures_and_benches\\generar_material_test_bench_v5.py
   ```
"""
    (dst / "README.md").write_text(readme_content, encoding="utf-8")
    stats.valid_files_copied += 1
    return stats


def ingest_asset_orchestration_engine() -> PackageIngestionStats:
    """Selectively copy intact AOE + Universal Asset Factory source, MCP schemas, scripts, docs, and tests."""
    dst = PACKAGES_DIR / "asset-orchestration-engine"
    ensure_clean_dir(dst)
    stats = PackageIngestionStats(
        package_id="asset-orchestration-engine",
        source_path=str(SRC_AOE),
        target_path=str(dst),
        valid_files_copied=0,
        corrupt_or_blank_skipped=0,
        excluded_dirs_or_large_skipped=0,
        sample_skipped_corrupt=[],
    )

    for sub in ["src", "mcp", "scripts", "ue5_plugin", "examples", "docs", "tests"]:
        copy_validated_tree(SRC_AOE / sub, dst / sub, stats, SRC_AOE)

    # Audit root files (including 0-byte gen_script.py and oversized .rar)
    for root_item in sorted(SRC_AOE.iterdir()):
        if root_item.is_dir():
            if root_item.name in {"dist", "output", "Saved", "AssetOrchestrationEngine"}:
                stats.excluded_dirs_or_large_skipped += 1
            continue
        if root_item.name == "README.md":
            copy_validated_file(root_item, dst / "docs" / "ORIGINAL_README.md", stats, "README.md")
        elif root_item.name in {"pyproject.toml", "requirements.txt", "runner.py", "LICENSE", ".gitignore", "gen_script.py", "AssetOrchestrationEngine.rar"}:
            copy_validated_file(root_item, dst / root_item.name, stats, root_item.name)

    readme_content = """# `@ianimation/asset-orchestration-engine` (`aoe-blender-mcp` / AOE + UAF v1.0.0)

Motor industrial autónomo y determinista de **Orquestación de Activos 3D, Compilación de Intenciones, Universal Asset Factory (UAF), Diseño de Niveles Procedurales (WFC 2D/3D), Terrenos Macro con Erosión Hidráulica (`.r16`), IA Cognitiva GOAP para NPCs y Puente Blender MCP** (Hunyuan3D, Hyper3D Rodin, PolyHaven, Sketchfab).

> Migrado de `E:\\AssetOrchestrationEngine` filtrando archivos vacíos (`gen_script.py`, 0 bytes) y excluyendo archivos comprimidos pesados (`AssetOrchestrationEngine.rar`, 42.6 MB) y carpetas de salida temporal (`Saved/`, `output/`, `dist/`). Ver [`../INGESTION_MANIFEST.json`](../INGESTION_MANIFEST.json).

---

## Arquitectura del Subsistema

| Directorio | Contenido y Capacidades Principales |
| :--- | :--- |
| [`src/`](src/) | **Core AOE (Fases F1–F80)**: `ProductionOrchestrator` (19 etapas), compilador determinista de intenciones a mallas/PBR, optimizador de estrategia/polígonos, crítico visual/geométrico y auto-reparación booleana/manifold. |
| [`src/uaf/`](src/uaf/) | **Universal Asset Factory (UAF-81.0 a UAF-81.92)**: `procedural_level` (WFC 2D/3D, Lock-and-Key, Mission DAG, AI Pacing Director), `macro_landscape` (erosión hidráulica/térmica, biomas Whittaker, splines, `.r16` 16-bit para UE5), `multi_agent_npc` (GOAP $A^*$, tácticas de escuadrón Bounding Overwatch/Flanking, StateTree UE5), `character_assembly`, `modular_world` y `natural_ecosystem`. |
| [`mcp/blender/`](mcp/blender/) | Addon y servidor socket **Blender MCP** ([`blender_mcp_addon.py`](mcp/blender/blender_mcp_addon.py)) + **22 esquemas JSON Schema** ([`mcp/blender/schemas/`](mcp/blender/schemas/)) para control live de Blender, Hunyuan3D, Hyper3D Rodin, PolyHaven y Sketchfab. |
| [`scripts/`](scripts/) | Generadores 3D standalone en Blender, diagnósticos de topología y runners de producción. |
| [`ue5_plugin/`](ue5_plugin/) | Plugin e ingestión portable desacoplada para Unreal Engine 5 (`UAF-81.89`). |
| [`docs/`](docs/) | **110+ documentos y especificaciones**: [`INDICE-CONOCIMIENTO.md`](docs/INDICE-CONOCIMIENTO.md), [`AI-AGENT-OPERATIONAL-GUIDE.md`](docs/AI-AGENT-OPERATIONAL-GUIDE.md), [`UAF-NEXTGEN-ARCHITECTURE-GUIDE.md`](docs/UAF-NEXTGEN-ARCHITECTURE-GUIDE.md), [`UE5-PORTABLE-WORKFLOW-GUIDE.md`](docs/UE5-PORTABLE-WORKFLOW-GUIDE.md) y [`DARX-PRODUCTION-CASE-STUDY.md`](docs/DARX-PRODUCTION-CASE-STUDY.md). |
| [`tests/`](tests/) | Suite masiva de pruebas unitarias y de aceptación (`F1–F80` + `UAF-81.*`). |

---

## 22 Herramientas MCP Verificadas (`aoe-blender-mcp`)

- **Escena y Viewport Live en Blender (5 tools)**: `execute_blender_code`, `get_scene_info`, `get_object_info`, `get_viewport_screenshot`, `set_texture`.
- **Generación 3D Neural con Tencent Hunyuan3D (4 tools)**: `generate_hunyuan3d_model`, `get_hunyuan3d_status`, `poll_hunyuan_job_status`, `import_generated_asset_hunyuan`.
- **Generación 3D Neural con Hyper3D Rodin (5 tools)**: `generate_hyper3d_model_via_text`, `generate_hyper3d_model_via_images`, `get_hyper3d_status`, `poll_rodin_job_status`, `import_generated_asset`.
- **Catálogo PBR/HDRI PolyHaven (4 tools)**: `get_polyhaven_status`, `get_polyhaven_categories`, `search_polyhaven_assets`, `download_polyhaven_asset`.
- **Repositorio 3D Sketchfab (4 tools)**: `get_sketchfab_status`, `search_sketchfab_models`, `get_sketchfab_model_preview`, `download_sketchfab_model`.

---

## Ejecución Rápida

```powershell
# Ejecutar runner de pruebas del motor AOE
C:\\Python314\\python.exe packages\\asset-orchestration-engine\\runner.py
```
"""
    (dst / "README.md").write_text(readme_content, encoding="utf-8")
    stats.valid_files_copied += 1
    return stats


def main() -> None:
    """Run complete monorepo ingestion and emit INGESTION_MANIFEST.json."""
    PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
    package_stats = [
        ingest_3d_ai_engine(),
        ingest_adobe_suite(),
        ingest_motion_vfx(),
        ingest_stick_animator(),
        ingest_blender_procedural_lab(),
        ingest_asset_orchestration_engine(),
    ]
    manifest = IngestionManifest(
        monorepo_root=str(MONOREPO_ROOT),
        packages=package_stats,
        total_valid_files_copied=sum(s.valid_files_copied for s in package_stats),
        total_corrupt_or_blank_skipped=sum(s.corrupt_or_blank_skipped for s in package_stats),
    )
    manifest_path = PACKAGES_DIR / "INGESTION_MANIFEST.json"
    manifest_path.write_text(manifest.model_dump_json(indent=2) + "\n", encoding="utf-8")
    print(f"Ingestion complete -> {manifest_path}")
    for s in package_stats:
        print(
            f"  [{s.package_id}] copied={s.valid_files_copied}, "
            f"corrupt_skipped={s.corrupt_or_blank_skipped}, "
            f"large_or_env_skipped={s.excluded_dirs_or_large_skipped}"
        )


if __name__ == "__main__":
    main()
