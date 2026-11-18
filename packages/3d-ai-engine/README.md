# `@ianimation/3d-ai-engine` — Orquestador 3D AI-First, Blender 5.2 & Unreal Engine 5

Paquete descriptor del núcleo Python + Tauri/React alojado en la raíz de este monorepo ([`backend/`](../../backend/), [`scripts/`](../../scripts/), [`src/`](../../src/), [`src-tauri/`](../../src-tauri/)). Se conserva la ubicación física en raíz para garantizar 100% de retrocompatibilidad con `pytest`, `pyproject`/imports (`import backend.*`) y la aplicación de escritorio Tauri v2.

---

## Arquitectura del Subsistema

| Capa / Módulo | Ruta en el Monorepo | Responsabilidad Principal |
| :--- | :--- | :--- |
| **Core & Telemetría** | [`backend/core/`](../../backend/core/) | Modelos Pydantic v2 (`Zero-Any`), almacén CAS SHA-256 (`cache.py`), configuración y bus de telemetría asíncrono. |
| **Motor Neural 3D & Topología** | [`backend/ai/`](../../backend/ai/) | `image_to_3d.py`, `neural_3d_engine.py`, `quad_remesher.py`, `pbr_baker.py`, `volumetric_3d.py`, `defringe.py`, `component_decomposer.py`. |
| **Cinemática & Rigging 3D** | [`backend/ai/`](../../backend/ai/) | `auto_rig.py`, `advanced_kinematics.py` (Two-Bone IK), `character_dynamics.py` (Twist bones + Verlet), `modular_articulation.py` (Isometría rígida $SE(3)$). |
| **Adaptador Blender 5.2 LTS** | [`backend/blender/`](../../backend/blender/) | Ejecución headless (`E:\Blender\blender.exe --factory-startup -b -P ...`), `adapter.py`, `rigging.py`, `live_bridge.py` y scripts en `backend/blender/scripts/`. |
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
C:\Python314\python.exe -m backend.main

# Ejecutar pruebas de integridad visual y articulación 3D
C:\Python314\python.exe -m pytest tests/backend/test_animation_visual_integrity.py tests/backend/test_modular_articulation.py tests/backend/test_fastmcp_server.py -v
```
