# `@ianimation/motion-vfx` (`after-effects-mcp` / `motion-engine` v3.0.0)

Plataforma de **Motion Graphics, VFX, Cinematografía Algorítmica, Tipografía Cinética, Data-Viz y Edición Editorial Automática** para Adobe After Effects vía Model Context Protocol (MCP).

> Migrado de `E:\Disco F\Dev\after-effects-mcp` filtrando archivos vacíos/corruptos en disco y excluyendo `dist/` (532 MB), `models/` y `build/` obsoletos. Ver [`../INGESTION_MANIFEST.json`](../INGESTION_MANIFEST.json).

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
