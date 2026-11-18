# Recetas de Flujo de Trabajo Multi-Motor (`WORKFLOW_RECIPES.md`)

Esta guía describe **6 flujos de producción end-to-end** diseñados para ser ejecutados directamente por agentes de IA combinando los distintos subsistemas del monorepo `IANIMATION`.

---

## Receta 1: Imagen Conceptual 2D $\to$ Personaje 3D Articulado Cero-Deformación + Render MP4

**Objetivo**: Convertir una ilustración o fotografía conceptual (con casco, rostro o accesorios rígidos) en un personaje 3D watertight animado en caminata bípeda o danza con **0% de deformación elástica** ([`GEMINI.md`](../GEMINI.md) §7).

**Subsistemas**: `ianimation-3d` ([`backend/`](../backend/), [`scripts/`](../scripts/))

1. **Análisis Rítmico (si hay música)**: Invocar `analyze_audio(audio_path="...")` en `ianimation-3d` para extraer `bpm` y `beat_timestamps`.
2. **Reconstrucción Volumétrica 3D**: Invocar `image_to_3d(image_path="inputs/...", provider="auto", texture_resolution=1024)` para generar la malla `.glb` con mapas PBR.
3. **Estandarización Watertight, Rigging y Prop Rígido $SE(3)$**:
   - Usar el módulo [`backend/ai/modular_articulation.py`](../backend/ai/modular_articulation.py) o tomar como plantilla de producción [`scripts/build_clean_watertight_ragdoll.py`](../scripts/build_clean_watertight_ragdoll.py):
     - Soldar triángulos neurales con `remove_doubles`, podar láminas de sombra parásita y sellar bucles abiertos con `holes_fill`.
     - Vincular cabeza/casco con peso $w = 1.0$ al hueso `Head` y props rígidos (ej. hacha/arma) exclusivamente a `Spine` o socket de mano ($0\%$ peso cruzado).
     - Limpiar proyecciones 2D fantasma sobre la ropa mediante transferencia simétrica BVH.
4. **Render Headless y Validación Cero-Falsos-Positivos**:
   - Ejecutar `E:\Blender\blender.exe --factory-startup -b -P scripts/build_clean_watertight_ragdoll.py`.
   - Ejecutar `C:\Python314\python.exe -m pytest tests/backend/test_animation_visual_integrity.py -v` para comprobar $\sigma^2 < 10^{-10}$ bajo el *depsgraph* real.
   - Inspeccionar visualmente los renders PNG resultantes con `read_file`.

---

## Receta 2: Personaje Hablante 2D Multi-Ángulo en Character Animator + Composición 2.5D en After Effects

**Objetivo**: Crear una cápsula vertical (9:16) o escena 16:9 con marioneta `.psd` riggeada, voz neural expresiva con lip-sync y escenario 3D parallax sin abrir manualmente Photoshop.

**Subsistemas**: `adobe-animation-mcp` (`packages/adobe-suite/`) $\to$ `after-effects-motion-engine` (`packages/motion-vfx/`)

1. **Auditoría del Entorno**: Llamar `ch_inspect_environment()` para validar rutas locales de Adobe Character Animator, After Effects y Blender.
2. **Generación Autónoma de Marioneta + Voz Neural + Lip-Sync**:
   - Invocar `pipeline_create_talking_character(...)` (o paso a paso: `ch_scaffold_multi_angle_puppet` + `ch_add_puppet_triggers_and_physics` + `audio_generate_expressive_speech` + `audio_export_lip_sync_markers`).
   - Validar el `.psd` resultante con `ch_audit_puppet_deep` (puntuación objetivo $\ge 90/100$) y `ch_validate_puppet`.
3. **Escenario 2.5D y Post-Procesado VFX**:
   - Generar pases de fondo con paralaje en Blender vía `blender_scaffold_3d_room` + `blender_render_parallax_passes`.
   - Montar el escenario en After Effects con `ae_setup_25d_stage` y `ae_apply_animation_expressions`.
   - Aplicar tipografía editorial brutalista y etalonaje fílmico desde `after-effects-motion-engine` (`apply_brutalist_kinetic_title`, `apply_film_grain_and_halation`) y renderizar con `ae_render_comp`.

---

## Receta 3: Edición Beat-Sync & VFX Cinematográfico para After Effects desde Audio/Guion

**Objetivo**: Producir un video editorial estilo *TIME Poster* con cortes al ritmo de la música, speed ramps, texto detrás del sujeto y exportación lista para render en After Effects.

**Subsistema**: `after-effects-motion-engine` (`packages/motion-vfx/`)

1. **Creación e Ingesta de Proyecto**: Llamar `create_project(...)` y opcionalmente `transcribe_local_audio(...)` o `vlog_produce(...)`.
2. **Detección de Sujetos y Profundidad 2.5D**: Llamar `detect_subjects_in_clip` y `compose_text_behind_subject` respetando las reglas de [`packages/motion-vfx/docs/USER_DESIGN_PREFERENCES.md`](../packages/motion-vfx/docs/USER_DESIGN_PREFERENCES.md).
3. **Orquestación de Óptica, Tiempo y Fotónica**:
   - `compile_speed_ramp_to_beat` + `apply_snap_zooms_to_timeline`
   - `compile_perspective_anchored_typography` + `apply_brutalist_kinetic_title`
   - `compile_film_emulation_plan` + `compile_photonics_plan`
   - Si aplica estética cómic/Y2K: `compile_mixed_media_plan` o `compile_stem_kinetics_plan`.
4. **QA y Compilación a ExtendScript**: Ejecutar `editorial_run_qa`, `validate_project` y finalmente `export_to_after_effects_jsx` (o `run-script` en sesión viva AE).

---

## Receta 4: Coreografía 2D de Stick-Figures con Cinemática Inversa (IK) $\to$ HTML5 / MP4

**Objetivo**: Crear una secuencia de combate o acrobacia de figuras articuladas con pies firmes al suelo y manos guiadas por IK, sin GPU ni navegador.

**Subsistema**: `stykanimate-mcp` (`packages/stick-animator/`)

1. **Inspección de Capacidades y Apertura**: Llamar `capabilities` y `project_open` (por ejemplo sobre [`packages/stick-animator/examples/cyber_samurai.styk`](../packages/stick-animator/examples/cyber_samurai.styk)).
2. **Escena y Capas**: Revisar jerarquías con `figure_list`, `figure_describe` y `layer_list`; añadir o duplicar actores con `figure_add` / `figure_duplicate`.
3. **Posado con IK y Keyframes**:
   - Anclar pies o posicionar manos usando `pose_set_ik` y `pose_ik_set`, o rotar segmentos directamente con `pose_set`.
   - Inspeccionar coordenadas exactas en píxeles con `pose_evaluate` para evitar penetración de suelo.
   - Insertar y espaciar fotogramas clave con `keyframe_edit` y `keyframe_timing`, guardando al final con `project_save`.
4. **Exportación a Video / Web**: Ejecutar [`packages/stick-animator/cli/export-html.js`](../packages/stick-animator/cli/export-html.js) o [`packages/stick-animator/cli/render_mp4.py`](../packages/stick-animator/cli/render_mp4.py).

---

## Receta 5: Banco Procedural PBR + Kit Modular 3D en Blender $\to$ Escena en Unreal Engine 5

**Objetivo**: Sintetizar mapas PBR físicos 2K, validar materiales sobre Shader Balls en estudio 3 puntos, exportar activos FBX y ensamblar una secuencia cinemática en UE5.

**Subsistemas**: `blender-procedural-lab` (`packages/blender-procedural-lab/`) $\to$ `ianimation-3d` (`backend/ue5/`)

1. **Síntesis de Texturas PBR 2K**: Ejecutar `procesar_mapas_pbr_cinematograficos.py` o `generar_trimsheet_industrial.py` en [`packages/blender-procedural-lab/generators/pbr_textures_and_benches/`](../packages/blender-procedural-lab/generators/pbr_textures_and_benches/).
2. **Inspección Visual en Estudio Shader Ball**: Ejecutar `generar_material_test_bench_v5.py` vía `E:\Blender\blender.exe --factory-startup -b -P ...` y revisar el render con `read_file`.
3. **Generación de Geometría Modular y Exportación FBX**: Ejecutar el generador de kit correspondiente (p. ej. `generar_catalogo_modular_90_master_oficial.py`) y su exportador FBX en [`packages/blender-procedural-lab/exporters/`](../packages/blender-procedural-lab/exporters/).
4. **Montaje y Render en Unreal Engine 5**: Usar `build_ue5_scene` y `render_video` desde `ianimation-3d` (o verificar conectividad con [`backend/ue5/companion.py`](../backend/ue5/companion.py)).

---

## Receta 6: Orquestación Determinista de Activos 3D, Terrenos `.r16`, Niveles WFC e IA GOAP (`AOE + UAF`)

**Objetivo**: Compilar intenciones de lenguaje natural a activos 3D listos para producción, generar mundos procedurales (terrenos con erosión hidráulica `.r16` y niveles WFC 2D/3D sin softlocks), o importar activos desde Hunyuan3D / Hyper3D Rodin / PolyHaven / Sketchfab en Blender y Unreal Engine 5.

**Subsistema**: `aoe-blender-mcp` ([`packages/asset-orchestration-engine/`](../packages/asset-orchestration-engine/))

1. **Orquestación de Activo 3D (19 etapas, Fases F1–F80)**:
   - Importar `ProductionOrchestrator` y `ProductionRequest` desde `packages/asset-orchestration-engine/src/production_orchestration` para compilar una intención natural a `SemanticMeshSpec`, grafo PBR, evaluación del crítico geométrico/visual y exportación FBX.
2. **Puente Live con Blender MCP (22 Tools)**:
   - Usar `generate_hunyuan3d_model` o `generate_hyper3d_model_via_text` / `generate_hyper3d_model_via_images` para síntesis neural 3D.
   - Descargar HDRIs/texturas CC0 con `search_polyhaven_assets` + `download_polyhaven_asset` o modelos de `search_sketchfab_models` + `download_sketchfab_model`.
   - Inspeccionar la escena con `get_scene_info`, `get_object_info`, `execute_blender_code` y `get_viewport_screenshot`.
3. **Generación de Mundos Next-Gen (`Universal Asset Factory — src/uaf/`)**:
   - **Terreno Macro (`UAF-81.91`)**: `LandscapeGenerator(LandscapeConfig(...)).generate_full_landscape(...)` $\to$ heightmap binario `.r16` de 16 bits + biomas Whittaker + splines.
   - **Niveles Procedurales (`UAF-81.90`)**: `ProceduralLevelDirector(LevelDirectorConfig(...)).generate_complete_level(...)` $\to$ WFC 2D/3D + Mission DAG Lock-and-Key.
   - **IA Cognitiva de Escuadrones (`UAF-81.92`)**: `SquadCoordinator` + GOAP $A^*$ exportable a StateTree de Unreal Engine 5.
