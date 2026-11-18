# AGENTS.md — Manual Operativo Maestro del Monorepo `IANIMATION` para Agentes de IA

> **Propósito**: Este documento es la guía de entrada principal para cualquier modelo de lenguaje o agente autónomo (Antigravity, Claude Code, Cursor, Gemini CLI) que opere sobre el monorepo unificado **`IANIMATION`**. Define la anatomía exacta de los **5 subsistemas unificados**, la matriz de enrutamiento de intenciones, los comandos de ejecución y las reglas inquebrantables de ingeniería y calidad visual.

---

## 1. Mapa del Monorepo Unificado

El repositorio consolida **5 dominios especializados** bajo una estructura modular estandarizada, conectando **144 herramientas MCP verificadas** y **123 generadores procedurales 3D/PBR en Blender 5.2 LTS**:

| Paquete (`packages/`) | ID MCP / Motor | Runtime | Capacidad Principal | Documentación Propia |
| :--- | :--- | :--- | :--- | :--- |
| [`packages/3d-ai-engine/`](packages/3d-ai-engine/) *(enlace a [`backend/`](backend/) y [`scripts/`](scripts/))* | `ianimation-3d` | Python >=3.10 + Blender 5.2 + UE5 | Pipeline 3D AI-First (Image-to-3D, Quad Remeshing, PBR Baking, Two-Bone IK, Isometría Rígida $SE(3)$, Unreal Engine 5 Remote Control/MRQ, UI Tauri v2). **8 tools MCP**. | [`packages/3d-ai-engine/README.md`](packages/3d-ai-engine/README.md) |
| [`packages/adobe-suite/`](packages/adobe-suite/) | `adobe-animation-mcp` | Node.js / TypeScript | Animación 2D profesional: Rigging `.psd` Character Animator (14 visemas, Head Turner, Walk, Física Dangle/Draggable/Fixed), Illustrator vectorial, TTS 48kHz Lip-Sync, After Effects 2.5D y Blender Grease Pencil. **38 tools MCP**. | [`packages/adobe-suite/README.md`](packages/adobe-suite/README.md) |
| [`packages/motion-vfx/`](packages/motion-vfx/) | `after-effects-motion-engine` | Node.js / TypeScript | Motion Graphics, VFX y Editorial para After Effects: óptica, temporal/speed-ramps, emulación fílmica Kodak, ritmo, tipografía cinética brutalista, Snorricam, fotónica, FLIR, mixed-media, vlog CLI y data-viz. **72 tools MCP**. | [`packages/motion-vfx/README.md`](packages/motion-vfx/README.md) |
| [`packages/stick-animator/`](packages/stick-animator/) | `stykanimate-mcp` | Node.js >=20 + Códec Python | Animación 2D rápida headless de figuras articuladas (*stick figures*) con Cinemática Inversa (IK), timeline por keyframes, soporte `.styk`/`.piv`/`.stk`, HTML5 Canvas y MP4. **26 tools MCP**. | [`packages/stick-animator/README.md`](packages/stick-animator/README.md) |
| [`packages/blender-procedural-lab/`](packages/blender-procedural-lab/) | `blender-procedural-lab` | Blender 5.2 LTS (`--factory-startup -b -P`) | Laboratorio masivo de generación 3D procedural: personajes riggeados, solvers IK bimanuales, Material Test Bench Pro V5, Trim Sheets 2K, 90 activos modulares, 50 props, bestiario 3D, 20 armas y exportadores FBX UE5. **123 scripts `.py`**. | [`packages/blender-procedural-lab/README.md`](packages/blender-procedural-lab/README.md) |

> **Nota de Auditoría e Integridad**: Ver el reporte generado por el pipeline de ingestión en [`packages/INGESTION_MANIFEST.json`](packages/INGESTION_MANIFEST.json). Todos los paquetes han sido filtrados para garantizar **0 archivos vacíos o corruptos** dentro de `packages/` y `backend/`.

---

## 2. Matriz de Enrutamiento de Intenciones (*Intent-to-Engine Routing*)

Antes de escribir código o invocar herramientas, el agente **debe** seleccionar el subsistema correcto usando esta matriz:

| Si el usuario pide... | Motor / Paquete Destino | Herramientas / Entrypoints Clave |
| :--- | :--- | :--- |
| Convertir un concept art o imagen en un personaje/prop **3D volumétrico** riggeado y animarlo en Blender o Unreal Engine 5 | `ianimation-3d` ([`backend/`](backend/) + [`scripts/`](scripts/)) | `image_to_3d`, `auto_rig`, `build_ue5_scene`, `render_video`, [`scripts/build_clean_watertight_ragdoll.py`](scripts/build_clean_watertight_ragdoll.py) |
| Crear una marioneta 2D `.psd` riggeada para **Adobe Character Animator** con lip-sync, visemas y voz neural 48kHz | `adobe-animation-mcp` ([`packages/adobe-suite/`](packages/adobe-suite/)) | `ch_scaffold_puppet`, `ch_scaffold_multi_angle_puppet`, `audio_generate_expressive_speech`, `pipeline_create_talking_character` |
| Vectorizar bocetos o rebanar capas en **Adobe Illustrator** para rigging 2D | `adobe-animation-mcp` ([`packages/adobe-suite/`](packages/adobe-suite/)) | `ai_trace_and_clean_sketch`, `ai_auto_rig_slice`, `ai_export_character_package` |
| Editar video, crear **Motion Graphics**, tipografía cinética brutalista, VFX óptico/fílmico, beat-sync o Data-Viz en **After Effects** | `after-effects-motion-engine` ([`packages/motion-vfx/`](packages/motion-vfx/)) | `create_video_from_script`, `vlog_produce`, `editorial_compile_data_visualization`, `apply_brutalist_kinetic_title`, `export_to_after_effects_jsx`, `run-script` |
| Prototipar coreografías de acción o animaciones 2D ligeras con **stick figures + IK** sin GPU | `stykanimate-mcp` ([`packages/stick-animator/`](packages/stick-animator/)) | `project_open`, `figure_add`, `pose_ik_set`, `keyframe_edit`, [`packages/stick-animator/cli/render_mp4.py`](packages/stick-animator/cli/render_mp4.py) |
| Generar proceduralmente **texturas PBR 2K, shader balls, kits modulares 3D, bestiario o props** en Blender 5.2 | `blender-procedural-lab` ([`packages/blender-procedural-lab/`](packages/blender-procedural-lab/)) | `generar_material_test_bench_v5.py`, `procesar_mapas_pbr_cinematograficos.py`, `generar_catalogo_modular_90_master_oficial.py`, `exportar_*_fbx.py` |
| Descubrir herramientas o validar salud del monorepo programáticamente desde Python/MCP | `backend.mcp.unified_registry` | `list_monorepo_subsystems()`, `search_monorepo_tools(query, domain)` |

---

## 3. Reglas Inquebrantables para Agentes de IA

Las siguientes normas combinan [`GEMINI.md`](GEMINI.md) y los estándares específicos heredados de cada motor:

1. **Principio 3D-First Inviolable ([`GEMINI.md`](GEMINI.md) §7)**: En tareas de animación de imágenes con `ianimation-3d`, queda prohibido animar imágenes como recortes 2D planos o filtros de malla 2D. Todo activo debe tener profundidad $Z(x,y)$, normales PBR y malla estándar glTF/GLB/OBJ. Accesorios rígidos (casco, rostro de muñeco, hacha, armas) deben mantener **isometría rígida $SE(3)$** ($\sigma^2 < 10^{-10}$).
2. **Estándar Visual de Motion Graphics ([`packages/motion-vfx/docs/USER_DESIGN_PREFERENCES.md`](packages/motion-vfx/docs/USER_DESIGN_PREFERENCES.md))**: Al generar composiciones de After Effects, aplicar **Editorial Poster / TIME Style** (tipografía ultra-bold condensada estirada verticalmente 120%-150%, carmesí `#FF1424` + blanco puro, `CENTER_JUSTIFY`, tracking negativo y `comp.motionBlur = true`). Prohibidas las fuentes Serif genéricas tipo `Times New Roman`.
3. **Tipado Estricto 100% (Zero-Any) y Validación en Fronteras ([`GEMINI.md`](GEMINI.md) §2-3)**: Todo código nuevo en Python debe usar tipado explícito y `StrictBaseModel` (Pydantic v2); todo TypeScript debe usar `strict: true` y esquemas `zod` sin `any`. Mitigar siempre *path traversal* confinando rutas al directorio permitido.
4. **Verificación Empírica y Cero Falsos Positivos ([`GEMINI.md`](GEMINI.md) §6)**:
   - Nunca modificar o relajar aserciones de tests para ocultar fallos.
   - Nunca dar por terminada una tarea visual sin inspeccionar los renders/frames reales con `read_file`.
   - Verificar deformaciones reales evaluando el *depsgraph* de Blender (`evaluated_get(depsgraph)`).
5. **Protocolo de Relevo Continuo ([`GEMINI.md`](GEMINI.md) §5)**: Mantener sincronizado [`PROJECT_STATUS.md`](PROJECT_STATUS.md) tras cada hito relevante.

---

## 4. Descubrimiento Programático y Servidores MCP

### Configuración Lista para Clientes MCP
El archivo [`mcp_servers.config.json`](mcp_servers.config.json) en la raíz contiene los 4 servidores MCP listos para conectar (`ianimation-3d`, `adobe-animation-mcp`, `after-effects-motion-engine`, `stykanimate-mcp`).

### Consultas en Python desde el Orquestador

```python
from backend.mcp.unified_registry import get_unified_registry
from backend.mcp.tools import list_monorepo_subsystems, search_monorepo_tools

registry = get_unified_registry()
integrity = list_monorepo_subsystems()
assert integrity.is_valid

# Buscar herramientas por capacidad o dominio
adobe_visemes = search_monorepo_tools(query="viseme", domain="adobe_2d_suite")
ae_optics = search_monorepo_tools(query="dolly", domain="after_effects_vfx")
```

---

## 5. Comandos Estándar de Desarrollo y Verificación

```powershell
# 1. Suite completa del Gateway Unificado y Visual 3D Integrity (Python 3.14)
C:\Python314\python.exe -m pytest tests/backend/test_unified_registry.py tests/backend/test_fastmcp_server.py tests/backend/test_animation_visual_integrity.py tests/backend/test_modular_articulation.py -v

# 2. Validar todo el paquete stykanimate-mcp (Node >= 20)
node --test packages/stick-animator/stykanimate-mcp/test/*.test.mjs

# 3. Instalar dependencias y compilar los paquetes TypeScript (requiere npm install por paquete)
cd packages/adobe-suite && npm install && npm run build && npm test
cd packages/motion-vfx && npm install && npm run build && npm test

# 4. Ejecutar un generador headless en Blender 5.2 LTS
E:\Blender\blender.exe --factory-startup -b -P scripts/build_clean_watertight_ragdoll.py
```

---

## 6. Índice Documental Complementario

- Arquitectura unificada e interoperabilidad: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- Catálogo completo de herramientas MCP y generadores: [`docs/MCP_CATALOG.md`](docs/MCP_CATALOG.md)
- Recetas paso a paso multi-motor para IA: [`docs/WORKFLOW_RECIPES.md`](docs/WORKFLOW_RECIPES.md)
- Estado histórico y relevo: [`PROJECT_STATUS.md`](PROJECT_STATUS.md)
