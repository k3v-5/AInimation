# `@ianimation/adobe-suite` (`adobe-animation-mcp`)

Servidor MCP especializado en **animación 2D de personajes, rigging `.psd` para Adobe Character Animator, vectores para Adobe Illustrator, voz neural HD con cálculo de visemas/lip-sync, escenografía 2.5D en After Effects y bocetado Grease Pencil en Blender**.

> Migrado de `E:\Disco F\Dev\AdobeEngineSuit` aplicando filtro binario estricto contra corrupción heredada en disco (cero archivos en blanco/nulos). Ver [`../INGESTION_MANIFEST.json`](../INGESTION_MANIFEST.json).

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
cd packages\adobe-suite
npm install
npm run build
npm test
```
