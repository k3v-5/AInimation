# `@ianimation/asset-orchestration-engine` (`aoe-blender-mcp` / AOE + UAF v1.0.0)

Motor industrial autónomo y determinista de **Orquestación de Activos 3D, Compilación de Intenciones, Universal Asset Factory (UAF), Diseño de Niveles Procedurales (WFC 2D/3D), Terrenos Macro con Erosión Hidráulica (`.r16`), IA Cognitiva GOAP para NPCs y Puente Blender MCP** (Hunyuan3D, Hyper3D Rodin, PolyHaven, Sketchfab).

> Migrado de `E:\AssetOrchestrationEngine` filtrando archivos vacíos (`gen_script.py`, 0 bytes) y excluyendo archivos comprimidos pesados (`AssetOrchestrationEngine.rar`, 42.6 MB) y carpetas de salida temporal (`Saved/`, `output/`, `dist/`). Ver [`../INGESTION_MANIFEST.json`](../INGESTION_MANIFEST.json).

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
C:\Python314\python.exe packages\asset-orchestration-engine\runner.py
```
