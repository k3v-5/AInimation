# Catálogo Maestro de Herramientas MCP y Generadores Procedurales (`MCP_CATALOG.md`)

> **Índice Verificado en Tiempo Real**: **166 herramientas MCP** distribuidas en 5 servidores activos + **123 scripts generadores/exportadores en Blender 5.2 LTS** (`blender-procedural-lab`).
> Configuración unificada lista para clientes MCP: [`mcp_servers.config.json`](../mcp_servers.config.json).

---

## Resumen Ejecutivo

| Servidor / Subsistema | ID | Runtime | Cantidad | README |
| :--- | :--- | :--- | :---: | :--- |
| **IANIMATION 3D AI Orchestrator** | `ianimation-3d` | `python` | **8 tools MCP** | [`packages/3d-ai-engine/README.md`](../packages/3d-ai-engine/README.md) |
| **Adobe Animation Suite & Character Animator MCP** | `adobe-animation-mcp` | `node` | **38 tools MCP** | [`packages/adobe-suite/README.md`](../packages/adobe-suite/README.md) |
| **After Effects Motion Graphics & VFX Engine** | `after-effects-motion-engine` | `node` | **72 tools MCP** | [`packages/motion-vfx/README.md`](../packages/motion-vfx/README.md) |
| **StykAnimate 2D Stick-Figure IK Engine** | `stykanimate-mcp` | `node` | **26 tools MCP** | [`packages/stick-animator/README.md`](../packages/stick-animator/README.md) |
| **Blender 5.2 Procedural 3D & PBR Texture Lab** | `blender-procedural-lab` | `blender-python` | **123 scripts `.py`** | [`packages/blender-procedural-lab/README.md`](../packages/blender-procedural-lab/README.md) |
| **Asset Orchestration Engine (AOE) & Universal Asset Factory** | `aoe-blender-mcp` | `python` | **22 tools MCP** | [`packages/asset-orchestration-engine/README.md`](../packages/asset-orchestration-engine/README.md) |

---

## 1. `ianimation-3d` — IANIMATION 3D AI Orchestrator (8 Tools MCP)

- **Comando**: `python -m backend.main`
- **Entrypoint**: [`backend/mcp/server.py`](../backend/mcp/server.py)

| # | Herramienta MCP | Categoría | Descripción |
| :---: | :--- | :--- | :--- |
| 1 | `analyze_audio` | `3d-pipeline` | Extract musical BPM, rhythm onsets, and beat timestamps from audio. |
| 2 | `image_to_3d` | `3d-pipeline` | Generate a 3D textured mesh (.glb) with PBR maps from a 2D image. |
| 3 | `auto_rig` | `3d-pipeline` | Bind an anatomical skeletal hierarchy to a static 3D mesh. |
| 4 | `extract_mocap` | `3d-pipeline` | Extract 3D skeletal motion capture animation from reference video. |
| 5 | `build_ue5_scene` | `3d-pipeline` | Assemble an Unreal Engine 5 Level Sequence with lighting and camera. |
| 6 | `render_video` | `3d-pipeline` | Render final MP4 video or still via UE5 MRQ or headless Blender. |
| 7 | `list_monorepo_subsystems` | `monorepo-discovery` | List all unified monorepo packages, paths, and integrity metrics. |
| 8 | `search_monorepo_tools` | `monorepo-discovery` | Search MCP tools and generators across all 5 animation engines. |

---

## 2. `adobe-animation-mcp` — Adobe Animation Suite & Character Animator MCP (38 Tools MCP)

- **Comando**: `npx tsx packages/adobe-suite/src/index.ts`
- **Entrypoint**: [`packages/adobe-suite/src/index.ts`](../packages/adobe-suite/src/index.ts)

| # | Herramienta MCP | Categoría | Descripción |
| :---: | :--- | :--- | :--- |
| 1 | `ch_scaffold_puppet` | `character-animator` | Generate rigged PSD puppet with +Head, 14 visemes, and Dangle/Fixed physics. |
| 2 | `ch_scaffold_multi_angle_puppet` | `character-animator` | Generate 3-view or 5-view Multi-Angle Head Turner PSD puppet. |
| 3 | `ch_scaffold_walk_puppet` | `character-animator` | Generate multi-view Walk behavior rigged PSD puppet with limb tags. |
| 4 | `ch_slice_artwork_to_puppet` | `character-animator` | Convert 2D artwork parameters into an anatomically sliced puppet PSD. |
| 5 | `ch_add_puppet_triggers_and_physics` | `character-animator` | Inject emotional swap sets, tears cycle, hand triggers, and breathing. |
| 6 | `ch_audit_puppet_deep` | `character-animator` | Audit PSD/AI puppet scoring 0-100 on independence, visemes, limbs, and physics. |
| 7 | `ch_auto_repair_puppet` | `character-animator` | Auto-repair missing head/limb independence tags and puppet structure. |
| 8 | `ch_prepare_recording_take` | `character-animator` | Bundle 48kHz speech WAV, viseme JSON cues, trigger sheet, and AE JSX script. |
| 9 | `ch_validate_puppet` | `character-animator` | Inspect existing PSD compliance against Adobe Character Animator rigging rules. |
| 10 | `ch_launch_character_animator` | `character-animator` | Launch Adobe Character Animator opening a target puppet or project. |
| 11 | `ch_inspect_environment` | `character-animator` | Report installed paths for Character Animator, Illustrator, AE, and Blender. |
| 12 | `ch_get_roadmap_status` | `character-animator` | Return active phase progress of the Adobe Animation Roadmap. |
| 13 | `ae_execute_jsx` | `after-effects-25d` | Execute an ExtendScript (.jsx) script in Adobe After Effects via CLI bridge. |
| 14 | `ae_import_puppet_scene` | `after-effects-25d` | Import 2D puppet PSD/AI or Character Animator scene into After Effects. |
| 15 | `ae_render_comp` | `after-effects-25d` | Trigger headless background rendering via Adobe aerender. |
| 16 | `ae_generate_scene_manifest` | `after-effects-25d` | Create standard 2.5D Scene Manifest JSON + ExtendScript constructor. |
| 17 | `ae_setup_25d_stage` | `after-effects-25d` | Assemble full 2.5D parallax camera stage in After Effects. |
| 18 | `ae_apply_animation_expressions` | `after-effects-25d` | Apply squash/stretch, audio bounce, camera shake, or blink expressions. |
| 19 | `ae_batch_render_queue` | `after-effects-25d` | Batch enqueue compositions to aerender with H.264/ProRes 4444 output. |
| 20 | `ai_execute_jsx` | `illustrator-vector` | Execute ExtendScript (.jsx) inside Adobe Illustrator via automation bridge. |
| 21 | `ai_create_document` | `illustrator-vector` | Create vector document in Adobe Illustrator with custom artboard dimensions. |
| 22 | `ai_trace_and_clean_sketch` | `illustrator-vector` | Vectorize raster sketch using Illustrator Image Trace and expand paths. |
| 23 | `ai_auto_rig_slice` | `illustrator-vector` | Sort vector artwork paths spatially into Character Animator layer groups. |
| 24 | `ai_apply_color_palette` | `illustrator-vector` | Harmonize character palette using designer themes or custom hex swatches. |
| 25 | `ai_export_character_package` | `illustrator-vector` | Export active Illustrator character to .ai puppet and optimized .svg. |
| 26 | `audio_generate_speech` | `neural-audio-lipsync` | Synthesize clean 48kHz 16-bit PCM WAV dialogue for lip-sync. |
| 27 | `audio_calculate_viseme_cues` | `neural-audio-lipsync` | Compute phoneme/viseme timeline cues (Ah, Ee, Oh, M, etc.) from text. |
| 28 | `audio_generate_expressive_speech` | `neural-audio-lipsync` | Synthesize multi-lingual emotional neural speech resampled to 48kHz PCM. |
| 29 | `audio_export_lip_sync_markers` | `neural-audio-lipsync` | Export viseme timeline markers to AE .jsx, JSON Cue Sheet, or CSV. |
| 30 | `audio_list_available_voices` | `neural-audio-lipsync` | List available neural regional voices (MX, ES, US, JP, etc.). |
| 31 | `blender_execute_script` | `blender-25d` | Execute headless Python script in Blender (bpy) without GUI. |
| 32 | `blender_render_frame` | `blender-25d` | Render 3D scene, background, or Grease Pencil element to PNG. |
| 33 | `blender_scaffold_3d_room` | `blender-25d` | Generate procedural architectural room (anime bedroom, cyberpunk, studio). |
| 34 | `blender_render_parallax_passes` | `blender-25d` | Render Beauty RGBA, Shadow Catcher Alpha, and Z-Depth/Mist passes. |
| 35 | `blender_grease_pencil_sketch` | `blender-25d` | Generate stylized 2D Grease Pencil strokes in 3D space. |
| 36 | `render_preview_frame_to_base64` | `autonomous-pipelines` | Encode rendered image or animation frame as Base64 PNG/JPEG in MCP. |
| 37 | `pipeline_create_talking_character` | `autonomous-pipelines` | One-click puppet PSD + 48kHz neural speech WAV + lip-sync cues. |
| 38 | `pipeline_render_social_clip` | `autonomous-pipelines` | One-click 9:16/16:9 composite package of puppet, 2.5D stage, and audio. |

---

## 3. `after-effects-motion-engine` — After Effects Motion Graphics & VFX Engine (72 Tools MCP)

- **Comando**: `npx tsx packages/motion-vfx/src/index.ts`
- **Entrypoint**: [`packages/motion-vfx/src/index.ts`](../packages/motion-vfx/src/index.ts)

| # | Herramienta MCP | Categoría | Descripción |
| :---: | :--- | :--- | :--- |
| 1 | `create_video_from_script` | `project-runtime` | Orchestrate multi-agent audiovisual project in canonical IR from script. |
| 2 | `export_to_after_effects_jsx` | `project-runtime` | Compile canonical project or composition into Adobe AE ExtendScript (.jsx). |
| 3 | `get_timeline_preview_frame` | `project-runtime` | Inspect evaluated visual and temporal frame state at timestamp t. |
| 4 | `apply_viral_caption_style` | `project-runtime` | Apply kinetic typography/caption presets creating an immutable revision. |
| 5 | `create_project` | `project-runtime` | Create persistent versioned project envelope in production runtime. |
| 6 | `open_project` | `project-runtime` | Open existing persistent project with recovery and active editing session. |
| 7 | `save_project` | `project-runtime` | Save project envelope applying optimistic concurrency checks. |
| 8 | `close_project` | `project-runtime` | Close active project session releasing concurrency locks. |
| 9 | `get_project_status` | `project-runtime` | Query runtime status, revision HEAD, lock state, and health report. |
| 10 | `list_project_revisions` | `project-runtime` | List immutable revision history for a persistent project. |
| 11 | `diff_project_revisions` | `project-runtime` | Calculate structural and semantic diff between two revisions. |
| 12 | `restore_project_revision` | `project-runtime` | Restore historical revision non-destructively as a new revision. |
| 13 | `validate_project` | `project-runtime` | Execute 6-layer non-mutating validation on a project. |
| 14 | `cancel_operation` | `project-runtime` | Cooperatively cancel an active long-running runtime operation. |
| 15 | `run-script` | `ae-live-bridge` | Run a predefined ExtendScript bridge command inside Adobe After Effects. |
| 16 | `get-results` | `ae-live-bridge` | Retrieve JSON results from the last script executed in After Effects. |
| 17 | `create-composition` | `ae-live-bridge` | Create a new After Effects composition with width, height, fps, duration. |
| 18 | `apply-effect` | `ae-live-bridge` | Apply an After Effects native/plugin effect to a target layer. |
| 19 | `list-presets` | `ae-live-bridge` | List available After Effects .ffx presets installed on the host. |
| 20 | `set-audio-levels` | `ae-live-bridge` | Set audio gain levels in dB on an audio or AV layer. |
| 21 | `transcribe_local_audio` | `social-and-vlog` | Transcribe local video/audio phonetically word-by-word at zero API cost. |
| 22 | `detect_viral_clips` | `social-and-vlog` | Extract top viral 30s-60s segments scored 0-100 from transcripts and energy. |
| 23 | `package_social_release` | `social-and-vlog` | Generate A/B High-CTR titles, chapters, and viral hashtags. |
| 24 | `auto_reframe_video` | `social-and-vlog` | Calculate dynamic pan-and-scan keyframes from 16:9 to 9:16 vertical. |
| 25 | `vlog_generate_jump_cut_plan` | `social-and-vlog` | Compute silence removal, phonetic word boundary protection, and punch-ins. |
| 26 | `vlog_classify_footage` | `social-and-vlog` | Classify raw footage into A-Roll, B-Roll, Timelapse, Action, Photo, Screen. |
| 27 | `vlog_match_broll` | `social-and-vlog` | Rank and match B-Roll clips against narrative intent with multicriteria scoring. |
| 28 | `vlog_produce` | `social-and-vlog` | Orchestrate 22-phase multi-lingual vlog production into AE ExtendScript. |
| 29 | `vlog_get_status` | `social-and-vlog` | Retrieve runtime status and deliverable manifest of a vlog production run. |
| 30 | `editorial_compile_data_visualization` | `editorial-dataviz-qa` | Compile structured datasets into animated AE DataViz specs. |
| 31 | `editorial_dataviz_to_jsx` | `editorial-dataviz-qa` | Transpile DataViz IR AST into executable After Effects JSX. |
| 32 | `editorial_parse_dataset` | `editorial-dataviz-qa` | Parse raw CSV or JSON text into a normalized DataSet structure. |
| 33 | `editorial_run_qa` | `editorial-dataviz-qa` | Audit Editorial Document against v4 structural, pacing, visual, audio QA rules. |
| 34 | `editorial_compare_revisions` | `editorial-dataviz-qa` | Perform semantic diff analysis between two editorial revisions. |
| 35 | `editorial_generate_trim_plan` | `editorial-dataviz-qa` | Compute semantic trimming and best take selection across segments. |
| 36 | `editorial_detect_redundancy` | `editorial-dataviz-qa` | Flag semantically redundant arguments and repetitive dialogue. |
| 37 | `compose_text_behind_subject` | `compositing-and-vision` | Assemble 3-layer depth sandwich placing editorial text behind subject. |
| 38 | `compose_multi_take_clones` | `compositing-and-vision` | Weave multiple takes of a subject into a seamless single-plate clone shot. |
| 39 | `detect_subjects_in_clip` | `compositing-and-vision` | Detect subject bounding boxes and silhouette contour points in frames. |
| 40 | `apply_snap_zooms_to_timeline` | `optics-temporal-film` | Apply percussive snap/crash zooms with inertial bounce on beats. |
| 41 | `apply_fisheye_optics` | `optics-temporal-film` | Apply 90s vintage fisheye barrel distortion and chromatic aberration. |
| 42 | `compile_dolly_zoom` | `optics-temporal-film` | Compute exact scale compensation curves for virtual Vertigo Dolly Zoom. |
| 43 | `apply_posterize_time` | `optics-temporal-film` | Apply variable stylized frame rates (12fps anime, 8fps stop-motion). |
| 44 | `compile_speed_ramp_to_beat` | `optics-temporal-film` | Build C^1 time remapping speed ramps landing slow-motion on beat drop. |
| 45 | `compile_temporal_orchestration` | `optics-temporal-film` | Orchestrate Posterize Time, Speed Ramps, and Stutter Freeze into AE plan. |
| 46 | `apply_film_grain_and_halation` | `optics-temporal-film` | Apply 16mm/35mm organic grain and Kodak Vision3 red halation glow. |
| 47 | `apply_auteur_color_grading` | `optics-temporal-film` | Apply auteur color grading LUTs (Tyler Pastel, Kendrick BW, MiniDV Acid). |
| 48 | `compile_film_emulation_plan` | `optics-temporal-film` | Consolidate grain, halation, gate weave, and grading into AE plan. |
| 49 | `apply_machine_gun_flash_cuts` | `rhythm-and-typography` | Generate frame-quantized stroboscopic flash cuts and burst interleaving. |
| 50 | `apply_blackout_vacuum_drop` | `rhythm-and-typography` | Insert absolute blackout vacuum window before musical beat drop. |
| 51 | `compile_syncopated_rhythm_cut` | `rhythm-and-typography` | Assemble syncopated flash bursts and pre-drop blackouts in AE. |
| 52 | `apply_brutalist_kinetic_title` | `rhythm-and-typography` | Create ultra-bold brutalist editorial title with vertical stretch & negative tracking. |
| 53 | `apply_liquid_chrome_text_effect` | `rhythm-and-typography` | Apply reflective liquid chrome shader with bevel and turbulent displacement. |
| 54 | `compile_perspective_anchored_typography` | `rhythm-and-typography` | Consolidate brutalist text, liquid chrome, 3D orientation, and word slam. |
| 55 | `apply_snorricam_body_lock` | `spatial-mechanics-photonics` | Lock subject to frame center transferring inertia to mirrored background. |
| 56 | `apply_infinite_zoom_portal` | `spatial-mechanics-photonics` | Generate super-exponential crash zoom wormhole portal transitions. |
| 57 | `compile_spatial_cinematography_plan` | `spatial-mechanics-photonics` | Consolidate Snorricam, infinite zoom portals, and parallax wipes. |
| 58 | `apply_centrifugal_gyro_roll` | `spatial-mechanics-photonics` | Execute 360-degree Z-axis centrifugal barrel rolls with scale guard. |
| 59 | `apply_directional_whip_pan` | `spatial-mechanics-photonics` | Generate invisible directional whip-pan match cut with symmetric blur. |
| 60 | `compile_dynamic_mechanics_plan` | `spatial-mechanics-photonics` | Consolidate gyro rolls, whip-pan match cuts, and lens breathing. |
| 61 | `apply_shutter_drag_echo` | `spatial-mechanics-photonics` | Emulate slow-shutter kinetic ghosting trails via ADBE Echo decay. |
| 62 | `apply_anamorphic_streak_flare` | `spatial-mechanics-photonics` | Generate horizontal anamorphic optical streak flares over highlights. |
| 63 | `apply_flir_thermal_vision` | `spatial-mechanics-photonics` | Apply FLIR infrared thermal false-color shader with edge contours. |
| 64 | `compile_photonics_plan` | `spatial-mechanics-photonics` | Consolidate shutter drag, anamorphic flares, prism star, and FLIR thermal. |
| 65 | `apply_manga_impact_frame` | `mixed-media-and-kinetics` | Insert 1-2 frame stroboscopic manga high-contrast impact cuts. |
| 66 | `apply_procedural_speed_lines` | `mixed-media-and-kinetics` | Generate convergent anime speed lines with central exclusion zone. |
| 67 | `apply_film_sprocket_holes` | `mixed-media-and-kinetics` | Simulate 35mm/16mm film sprocket holes with KeyKode marginal text. |
| 68 | `compile_mixed_media_plan` | `mixed-media-and-kinetics` | Consolidate impact frames, speed lines, sprockets, paper tear, and boil. |
| 69 | `apply_audio_reactive_physics` | `mixed-media-and-kinetics` | Compute damped viscoelastic bounce and chromatic shift reacting to 808 sub-bass. |
| 70 | `apply_dynamic_aspect_ratio_breathing` | `mixed-media-and-kinetics` | Animate dynamic aspect ratio transitions (9:16, 1:1, 16:9, 2.39:1). |
| 71 | `apply_datamosh_pframe_glitch` | `mixed-media-and-kinetics` | Emulate Y2K MPEG I-frame loss and macroblock displacement glitches. |
| 72 | `compile_stem_kinetics_plan` | `mixed-media-and-kinetics` | Consolidate 808 bounce physics, breathing mattes, and datamosh into AE plan. |

---

## 4. `stykanimate-mcp` — StykAnimate 2D Stick-Figure IK Engine (26 Tools MCP)

- **Comando**: `node packages/stick-animator/stykanimate-mcp/src/index.js`
- **Entrypoint**: [`packages/stick-animator/stykanimate-mcp/src/index.js`](../packages/stick-animator/stykanimate-mcp/src/index.js)

| # | Herramienta MCP | Categoría | Descripción |
| :---: | :--- | :--- | :--- |
| 1 | `capabilities` | `capabilities` | Report supported formats (.styk, .stkz, .stykmov, .piv, .stk), Python codec, and open projects. |
| 2 | `project_open` | `project-lifecycle` | Open a StykAnimate (.styk/.stkz) or Pivot (.piv/.stk) file as active project. |
| 3 | `project_close` | `project-lifecycle` | Close open project and release editor session. |
| 4 | `project_describe` | `project-lifecycle` | Report canvas size, frame rate, keyframes, and figure definitions. |
| 5 | `project_validate` | `project-lifecycle` | Validate open project consistency and integrity. |
| 6 | `project_save` | `project-lifecycle` | Write open project cleanly to disk. |
| 7 | `project_timeline` | `project-lifecycle` | List full timeline structure, ticks, and keyframe sequence. |
| 8 | `project_seek` | `project-lifecycle` | Seek editor playhead to a specified keyframe index. |
| 9 | `figure_list` | `figures` | List active figure instances with IDs, names, layers, position, and scale. |
| 10 | `figure_describe` | `figures` | Report full joint hierarchy, parent links, lengths, and bend handles of a figure. |
| 11 | `figure_add` | `figures` | Instantiate a figure definition on the active keyframe. |
| 12 | `figure_duplicate` | `figures` | Duplicate a figure including its current pose into a target keyframe. |
| 13 | `figure_delete` | `figures` | Remove a figure instance cleanly from a keyframe. |
| 14 | `figure_transform` | `figures` | Translate, rotate, scale, flip, or align a figure instance on canvas. |
| 15 | `pose_evaluate` | `pose-and-ik` | Solve forward/inverse kinematics and return joint positions in canvas pixels. |
| 16 | `pose_set` | `pose-and-ik` | Set joint angles, segment lengths, and bends on a figure pose. |
| 17 | `pose_ik_set` | `pose-and-ik` | Move inverse kinematics target of a joint (e.g., hand or foot placement). |
| 18 | `pose_set_ik` | `pose-and-ik` | Enable/disable or pin/unpin inverse kinematics controller targets on a joint. |
| 19 | `pose_reset` | `pose-and-ik` | Reset figure pose back to its definition rest pose. |
| 20 | `layer_list` | `layers-and-styles` | List project layers with z-order, visibility, and lock state. |
| 21 | `layer_edit` | `layers-and-styles` | Create, rename, delete, reorder layers, or move figures between layers. |
| 22 | `style_set` | `layers-and-styles` | Update figure color, opacity, or stroke thickness styling. |
| 23 | `keyframe_edit` | `timeline-and-history` | Add, delete, duplicate, or reorder animation keyframes. |
| 24 | `keyframe_timing` | `timeline-and-history` | Modify keyframe tick duration or global project FPS. |
| 25 | `history_undo` | `timeline-and-history` | Undo the most recent non-destructive project edit. |
| 26 | `history_redo` | `timeline-and-history` | Redo the previously undone project edit. |

---

## 5. `blender-procedural-lab` — Generadores Procedurales 3D/PBR (123 Scripts `.py`)

Ejecución estándar headless: `E:\Blender\blender.exe --factory-startup -b -P <ruta_script>`

### `generators/characters_and_rigs/` — Personajes 3D, Ragdolls y Estilización (16 scripts)

- [`astra_blender_styling.py`](../packages/blender-procedural-lab/generators/characters_and_rigs/astra_blender_styling.py)
- [`buscar_rotacion_upright.py`](../packages/blender-procedural-lab/generators/characters_and_rigs/buscar_rotacion_upright.py)
- [`generar_lote3_personajes.py`](../packages/blender-procedural-lab/generators/characters_and_rigs/generar_lote3_personajes.py)
- [`generar_personaje_fiel_referencia.py`](../packages/blender-procedural-lab/generators/characters_and_rigs/generar_personaje_fiel_referencia.py)
- [`generar_personaje_fiel_referencia_v10.py`](../packages/blender-procedural-lab/generators/characters_and_rigs/generar_personaje_fiel_referencia_v10.py)
- [`generar_personaje_fiel_referencia_v11.py`](../packages/blender-procedural-lab/generators/characters_and_rigs/generar_personaje_fiel_referencia_v11.py)
- [`generar_personaje_fiel_referencia_v2.py`](../packages/blender-procedural-lab/generators/characters_and_rigs/generar_personaje_fiel_referencia_v2.py)
- [`generar_personaje_fiel_referencia_v3.py`](../packages/blender-procedural-lab/generators/characters_and_rigs/generar_personaje_fiel_referencia_v3.py)
- [`generar_personaje_fiel_referencia_v5.py`](../packages/blender-procedural-lab/generators/characters_and_rigs/generar_personaje_fiel_referencia_v5.py)
- [`generar_personaje_fiel_referencia_v6.py`](../packages/blender-procedural-lab/generators/characters_and_rigs/generar_personaje_fiel_referencia_v6.py)
- [`generar_personaje_fiel_referencia_v7.py`](../packages/blender-procedural-lab/generators/characters_and_rigs/generar_personaje_fiel_referencia_v7.py)
- [`generar_personaje_fiel_referencia_v8.py`](../packages/blender-procedural-lab/generators/characters_and_rigs/generar_personaje_fiel_referencia_v8.py)
- [`generar_personaje_fiel_referencia_v9.py`](../packages/blender-procedural-lab/generators/characters_and_rigs/generar_personaje_fiel_referencia_v9.py)
- [`generar_personaje_riggeado_oficial.py`](../packages/blender-procedural-lab/generators/characters_and_rigs/generar_personaje_riggeado_oficial.py)
- [`generar_supervivientes_y_mascota_oficial.py`](../packages/blender-procedural-lab/generators/characters_and_rigs/generar_supervivientes_y_mascota_oficial.py)
- [`generar_testdummy_fiel_referencia.py`](../packages/blender-procedural-lab/generators/characters_and_rigs/generar_testdummy_fiel_referencia.py)

### `generators/animations_and_ik/` — Animación Locomoción/Combate y Solvers IK (15 scripts)

- [`diagnosticar_bones_blender.py`](../packages/blender-procedural-lab/generators/animations_and_ik/diagnosticar_bones_blender.py)
- [`generar_animaciones_combate_y_transporte_oficial.py`](../packages/blender-procedural-lab/generators/animations_and_ik/generar_animaciones_combate_y_transporte_oficial.py)
- [`generar_animaciones_locomocion_oficial.py`](../packages/blender-procedural-lab/generators/animations_and_ik/generar_animaciones_locomocion_oficial.py)
- [`solver_exacto_bimanual.py`](../packages/blender-procedural-lab/generators/animations_and_ik/solver_exacto_bimanual.py)
- [`solver_exacto_v2.py`](../packages/blender-procedural-lab/generators/animations_and_ik/solver_exacto_v2.py)
- [`solver_pose_agarre_arma.py`](../packages/blender-procedural-lab/generators/animations_and_ik/solver_pose_agarre_arma.py)
- [`solver_pose_agarre_arma_v2.py`](../packages/blender-procedural-lab/generators/animations_and_ik/solver_pose_agarre_arma_v2.py)
- [`solver_pose_agarre_arma_v3.py`](../packages/blender-procedural-lab/generators/animations_and_ik/solver_pose_agarre_arma_v3.py)
- [`solver_pose_ik_blender.py`](../packages/blender-procedural-lab/generators/animations_and_ik/solver_pose_ik_blender.py)
- [`test_bimanual_pose.py`](../packages/blender-procedural-lab/generators/animations_and_ik/test_bimanual_pose.py)
- [`test_ejes_brazos.py`](../packages/blender-procedural-lab/generators/animations_and_ik/test_ejes_brazos.py)
- [`test_ik_pose.py`](../packages/blender-procedural-lab/generators/animations_and_ik/test_ik_pose.py)
- [`test_rotacion_brazos.py`](../packages/blender-procedural-lab/generators/animations_and_ik/test_rotacion_brazos.py)
- [`verificar_pose_con_socket.py`](../packages/blender-procedural-lab/generators/animations_and_ik/verificar_pose_con_socket.py)
- [`verificar_pose_con_socket_v2.py`](../packages/blender-procedural-lab/generators/animations_and_ik/verificar_pose_con_socket_v2.py)

### `generators/pbr_textures_and_benches/` — Texturas PBR 2K, Trim Sheets y Material Test Bench (19 scripts)

- [`componer_showcase_texturas.py`](../packages/blender-procedural-lab/generators/pbr_textures_and_benches/componer_showcase_texturas.py)
- [`generar_material_test_bench.py`](../packages/blender-procedural-lab/generators/pbr_textures_and_benches/generar_material_test_bench.py)
- [`generar_material_test_bench_v2.py`](../packages/blender-procedural-lab/generators/pbr_textures_and_benches/generar_material_test_bench_v2.py)
- [`generar_material_test_bench_v3.py`](../packages/blender-procedural-lab/generators/pbr_textures_and_benches/generar_material_test_bench_v3.py)
- [`generar_material_test_bench_v4.py`](../packages/blender-procedural-lab/generators/pbr_textures_and_benches/generar_material_test_bench_v4.py)
- [`generar_material_test_bench_v5.py`](../packages/blender-procedural-lab/generators/pbr_textures_and_benches/generar_material_test_bench_v5.py)
- [`generar_showcase_oxidados_y_lujo.py`](../packages/blender-procedural-lab/generators/pbr_textures_and_benches/generar_showcase_oxidados_y_lujo.py)
- [`generar_texturas_pbr_bombero_oficial.py`](../packages/blender-procedural-lab/generators/pbr_textures_and_benches/generar_texturas_pbr_bombero_oficial.py)
- [`generar_trimsheet_industrial.py`](../packages/blender-procedural-lab/generators/pbr_textures_and_benches/generar_trimsheet_industrial.py)
- [`modular_componer_showcase_lujo_master.py`](../packages/blender-procedural-lab/generators/pbr_textures_and_benches/modular_componer_showcase_lujo_master.py)
- [`modular_componer_showcase_oxidados_master.py`](../packages/blender-procedural-lab/generators/pbr_textures_and_benches/modular_componer_showcase_oxidados_master.py)
- [`modular_generar_pbr_texturas_industriales.py`](../packages/blender-procedural-lab/generators/pbr_textures_and_benches/modular_generar_pbr_texturas_industriales.py)
- [`modular_generar_pbr_texturas_industriales_v2.py`](../packages/blender-procedural-lab/generators/pbr_textures_and_benches/modular_generar_pbr_texturas_industriales_v2.py)
- [`modular_generar_pbr_texturas_oxidadas_y_lujo.py`](../packages/blender-procedural-lab/generators/pbr_textures_and_benches/modular_generar_pbr_texturas_oxidadas_y_lujo.py)
- [`modular_generar_texturas_modulares.py`](../packages/blender-procedural-lab/generators/pbr_textures_and_benches/modular_generar_texturas_modulares.py)
- [`modular_procesar_mapas_pbr_cinematograficos.py`](../packages/blender-procedural-lab/generators/pbr_textures_and_benches/modular_procesar_mapas_pbr_cinematograficos.py)
- [`modular_sintetizar_texturas_pbr_alta_fidelidad.py`](../packages/blender-procedural-lab/generators/pbr_textures_and_benches/modular_sintetizar_texturas_pbr_alta_fidelidad.py)
- [`test_shaderball_uv.py`](../packages/blender-procedural-lab/generators/pbr_textures_and_benches/test_shaderball_uv.py)
- [`ui_generar_texturas_hud.py`](../packages/blender-procedural-lab/generators/pbr_textures_and_benches/ui_generar_texturas_hud.py)

### `generators/modular_kits_and_props/` — Kits Modulares (90 Activos), Props (50), Bestiario y Armas (64 scripts)

- [`catalogo_modulares_kit1_industrial.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/catalogo_modulares_kit1_industrial.py)
- [`catalogo_modulares_kit2_artdeco.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/catalogo_modulares_kit2_artdeco.py)
- [`catalogo_modulares_kit3_plasma.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/catalogo_modulares_kit3_plasma.py)
- [`catalogo_modulares_kit4_biolab.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/catalogo_modulares_kit4_biolab.py)
- [`catalogo_modulares_kit5_habitat.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/catalogo_modulares_kit5_habitat.py)
- [`catalogo_modulares_maestro_90.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/catalogo_modulares_maestro_90.py)
- [`componer_50_props_master.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/componer_50_props_master.py)
- [`componer_peligros_30_master.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/componer_peligros_30_master.py)
- [`componer_showcase_hud.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/componer_showcase_hud.py)
- [`generar_armory_tool_rack.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_armory_tool_rack.py)
- [`generar_arsenal_20_armas_oficial.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_arsenal_20_armas_oficial.py)
- [`generar_arsenal_armas_20_oficial.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_arsenal_armas_20_oficial.py)
- [`generar_bestiario_10_entidades_oficial.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_bestiario_10_entidades_oficial.py)
- [`generar_bestiario_3d_completo_10_entidades.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_bestiario_3d_completo_10_entidades.py)
- [`generar_bestiario_avanzado_showcase.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_bestiario_avanzado_showcase.py)
- [`generar_bestiario_cinematico.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_bestiario_cinematico.py)
- [`generar_bestiario_maestro_showcase.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_bestiario_maestro_showcase.py)
- [`generar_bestiario_pulido_showcase.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_bestiario_pulido_showcase.py)
- [`generar_bestiario_y_entidades_oficial.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_bestiario_y_entidades_oficial.py)
- [`generar_bloques_brecha_y_causalidad_oficial.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_bloques_brecha_y_causalidad_oficial.py)
- [`generar_bloques_modulares_oficial.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_bloques_modulares_oficial.py)
- [`generar_camilla_tandem_oficial.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_camilla_tandem_oficial.py)
- [`generar_catalogo_activos_modulares.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_catalogo_activos_modulares.py)
- [`generar_catalogo_activos_modulares_v2.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_catalogo_activos_modulares_v2.py)
- [`generar_catalogo_activos_modulares_v3.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_catalogo_activos_modulares_v3.py)
- [`generar_catalogo_activos_modulares_v4.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_catalogo_activos_modulares_v4.py)
- [`generar_catalogo_activos_modulares_v5.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_catalogo_activos_modulares_v5.py)
- [`generar_catalogo_activos_modulares_v6.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_catalogo_activos_modulares_v6.py)
- [`generar_catalogo_modular_90_loteA.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_catalogo_modular_90_loteA.py)
- [`generar_catalogo_modular_90_loteB.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_catalogo_modular_90_loteB.py)
- [`generar_catalogo_modular_90_loteC.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_catalogo_modular_90_loteC.py)
- [`generar_catalogo_modular_90_master_oficial.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_catalogo_modular_90_master_oficial.py)
- [`generar_dispositivo_muneca_y_hud.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_dispositivo_muneca_y_hud.py)
- [`generar_hardware_mision_y_gadgets.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_hardware_mision_y_gadgets.py)
- [`generar_hardware_shuttle_maestro.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_hardware_shuttle_maestro.py)
- [`generar_hardware_tactico_5_oficial.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_hardware_tactico_5_oficial.py)
- [`generar_hardware_tactico_expandido_oficial.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_hardware_tactico_expandido_oficial.py)
- [`generar_herramientas_tacticas_8_oficial.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_herramientas_tacticas_8_oficial.py)
- [`generar_herramientas_tacticas_avanzadas_oficial.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_herramientas_tacticas_avanzadas_oficial.py)
- [`generar_lote10_props_maestros.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_lote10_props_maestros.py)
- [`generar_lote1_props_maestros.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_lote1_props_maestros.py)
- [`generar_lote2_herramientas.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_lote2_herramientas.py)
- [`generar_lote2_props_maestros.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_lote2_props_maestros.py)
- [`generar_lote3_herramientas.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_lote3_herramientas.py)
- [`generar_lote3_props_maestros.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_lote3_props_maestros.py)
- [`generar_lote4_props_maestros.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_lote4_props_maestros.py)
- [`generar_lote5_props_maestros.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_lote5_props_maestros.py)
- [`generar_lote6_props_maestros.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_lote6_props_maestros.py)
- [`generar_lote7_props_maestros.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_lote7_props_maestros.py)
- [`generar_lote8_props_maestros.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_lote8_props_maestros.py)
- [`generar_lote9_props_maestros.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_lote9_props_maestros.py)
- [`generar_mapas_dioramas_maestro.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_mapas_dioramas_maestro.py)
- [`generar_peligros_lote1_termicos.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_peligros_lote1_termicos.py)
- [`generar_peligros_lote2_fluidos.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_peligros_lote2_fluidos.py)
- [`generar_peligros_lote3_electricos.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_peligros_lote3_electricos.py)
- [`generar_peligros_lote4_estructurales.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_peligros_lote4_estructurales.py)
- [`generar_peligros_lote5_biologicos.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_peligros_lote5_biologicos.py)
- [`generar_props_interactivos.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_props_interactivos.py)
- [`generar_salas_modulares_ensambladas_oficial.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_salas_modulares_ensambladas_oficial.py)
- [`generar_tres_arquetipos_mapas.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_tres_arquetipos_mapas.py)
- [`generar_viga_colapso_oficial.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/generar_viga_colapso_oficial.py)
- [`test_carguero.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/test_carguero.py)
- [`test_crucero.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/test_crucero.py)
- [`test_refineria.py`](../packages/blender-procedural-lab/generators/modular_kits_and_props/test_refineria.py)

### `exporters/` — Exportadores Automáticos FBX para Unreal Engine 5 (9 scripts)

- [`export_fixed_props.py`](../packages/blender-procedural-lab/exporters/export_fixed_props.py)
- [`exportar_20_armas_fbx.py`](../packages/blender-procedural-lab/exporters/exportar_20_armas_fbx.py)
- [`exportar_30_peligros_fbx.py`](../packages/blender-procedural-lab/exporters/exportar_30_peligros_fbx.py)
- [`exportar_50_props_fbx.py`](../packages/blender-procedural-lab/exporters/exportar_50_props_fbx.py)
- [`exportar_6_hardware_tactico_fbx.py`](../packages/blender-procedural-lab/exporters/exportar_6_hardware_tactico_fbx.py)
- [`exportar_8_herramientas_tacticas_fbx.py`](../packages/blender-procedural-lab/exporters/exportar_8_herramientas_tacticas_fbx.py)
- [`exportar_90_activos_modulares_fbx.py`](../packages/blender-procedural-lab/exporters/exportar_90_activos_modulares_fbx.py)
- [`exportar_bestiario_fbx.py`](../packages/blender-procedural-lab/exporters/exportar_bestiario_fbx.py)
- [`regenerar_portales_abiertos_fbx.py`](../packages/blender-procedural-lab/exporters/regenerar_portales_abiertos_fbx.py)

---

## 6. `aoe-blender-mcp` — Asset Orchestration Engine (AOE) & Universal Asset Factory (22 Tools MCP)

- **Comando**: `python packages/asset-orchestration-engine/runner.py`
- **Addon & Schemas MCP**: [`packages/asset-orchestration-engine/mcp/blender/blender_mcp_addon.py`](../packages/asset-orchestration-engine/mcp/blender/blender_mcp_addon.py) y [`packages/asset-orchestration-engine/mcp/blender/schemas/`](../packages/asset-orchestration-engine/mcp/blender/schemas/)

| # | Herramienta MCP | Categoría | Descripción |
| :---: | :--- | :--- | :--- |
| 1 | `execute_blender_code` | `blender-live-control` | Execute arbitrary Python (bpy) code inside the live Blender MCP socket server. |
| 2 | `get_scene_info` | `blender-live-control` | Get detailed information about the current Blender scene, objects, and materials. |
| 3 | `get_object_info` | `blender-live-control` | Retrieve transform, mesh topology, bounding box, and material slots for a Blender object. |
| 4 | `get_viewport_screenshot` | `blender-live-control` | Capture and save a 3D viewport screenshot from the active Blender session. |
| 5 | `set_texture` | `blender-live-control` | Apply downloaded or generated PBR texture maps onto a target Blender object material. |
| 6 | `generate_hunyuan3d_model` | `hunyuan3d-generation` | Generate a 3D textured mesh asset via Tencent Hunyuan3D from text or reference image. |
| 7 | `get_hunyuan3d_status` | `hunyuan3d-generation` | Check whether Hunyuan3D integration is enabled and configured in Blender MCP. |
| 8 | `poll_hunyuan_job_status` | `hunyuan3d-generation` | Poll asynchronous Hunyuan3D generation job status until completion. |
| 9 | `import_generated_asset_hunyuan` | `hunyuan3d-generation` | Import completed Hunyuan3D 3D model directly into the active Blender scene. |
| 10 | `generate_hyper3d_model_via_text` | `hyper3d-rodin-generation` | Generate a 3D asset via Hyper3D Rodin from a natural language text prompt. |
| 11 | `generate_hyper3d_model_via_images` | `hyper3d-rodin-generation` | Generate a 3D asset via Hyper3D Rodin from single or multi-view reference images. |
| 12 | `get_hyper3d_status` | `hyper3d-rodin-generation` | Check Hyper3D Rodin API availability and quota status in Blender MCP. |
| 13 | `poll_rodin_job_status` | `hyper3d-rodin-generation` | Poll Hyper3D Rodin asynchronous generation task status. |
| 14 | `import_generated_asset` | `hyper3d-rodin-generation` | Import completed Hyper3D Rodin 3D mesh into the active Blender scene. |
| 15 | `get_polyhaven_status` | `polyhaven-assets` | Verify PolyHaven API integration status in Blender MCP. |
| 16 | `get_polyhaven_categories` | `polyhaven-assets` | List available PolyHaven asset categories for HDRIs, textures, or models. |
| 17 | `search_polyhaven_assets` | `polyhaven-assets` | Search PolyHaven catalog for CC0 HDRIs, PBR texture sets, and 3D models. |
| 18 | `download_polyhaven_asset` | `polyhaven-assets` | Download and import a PolyHaven HDRI, PBR texture set, or 3D model into Blender. |
| 19 | `get_sketchfab_status` | `sketchfab-repository` | Check Sketchfab API authentication and integration status in Blender MCP. |
| 20 | `search_sketchfab_models` | `sketchfab-repository` | Search downloadable 3D models in Sketchfab by keyword, category, and face count. |
| 21 | `get_sketchfab_model_preview` | `sketchfab-repository` | Fetch thumbnail preview of a Sketchfab model before downloading. |
| 22 | `download_sketchfab_model` | `sketchfab-repository` | Download and import a glTF/Blender model from Sketchfab into the active scene. |

