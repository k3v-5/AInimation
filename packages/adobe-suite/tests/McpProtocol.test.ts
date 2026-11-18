import { describe, it, expect, afterAll } from 'vitest';
import { characterTools } from '../src/tools/characterTools.js';
import { illustratorTools } from '../src/tools/illustratorTools.js';
import { audioTools } from '../src/tools/audioTools.js';
import { afterEffectsTools } from '../src/tools/afterEffectsTools.js';
import { blenderTools } from '../src/tools/blenderTools.js';
import { pipelineTools } from '../src/tools/pipelineTools.js';
import path from 'path';
import os from 'os';
import fs from 'fs';

describe('MCP Protocol & Tools Registry', () => {
  const allTools = [
    ...characterTools,
    ...illustratorTools,
    ...audioTools,
    ...afterEffectsTools,
    ...blenderTools,
    ...pipelineTools
  ];

  const tempPsd = path.join(os.tmpdir(), `mcp_test_${Date.now()}.psd`);
  const tempWav = path.join(os.tmpdir(), `mcp_test_audio_${Date.now()}.wav`);
  const tempMarkers = path.join(os.tmpdir(), `mcp_test_markers_${Date.now()}`);
  const tempManifestDir = path.join(os.tmpdir(), `mcp_test_manifest_${Date.now()}`);
  const tempBlenderDir = path.join(os.tmpdir(), `mcp_test_blender_${Date.now()}`);
  const tempPipelineDir = path.join(os.tmpdir(), `mcp_test_pipeline_${Date.now()}`);

  afterAll(() => {
    try { if (fs.existsSync(tempPsd)) fs.unlinkSync(tempPsd); } catch {}
    try { if (fs.existsSync(tempWav)) fs.unlinkSync(tempWav); } catch {}
    try { if (fs.existsSync(tempMarkers)) fs.rmSync(tempMarkers, { recursive: true, force: true }); } catch {}
    try { if (fs.existsSync(tempManifestDir)) fs.rmSync(tempManifestDir, { recursive: true, force: true }); } catch {}
    try { if (fs.existsSync(tempBlenderDir)) fs.rmSync(tempBlenderDir, { recursive: true, force: true }); } catch {}
    try { if (fs.existsSync(tempPipelineDir)) fs.rmSync(tempPipelineDir, { recursive: true, force: true }); } catch {}
  });

  it('registers all 38 tools with valid schemas and descriptions', () => {
    expect(allTools.length).toBe(38);

    const toolNames = allTools.map(t => t.name);
    // Character Animator tools (12)
    expect(toolNames).toContain('ch_scaffold_puppet');
    expect(toolNames).toContain('ch_validate_puppet');
    expect(toolNames).toContain('ch_launch_character_animator');
    expect(toolNames).toContain('ch_inspect_environment');
    expect(toolNames).toContain('ch_get_roadmap_status');
    expect(toolNames).toContain('ch_scaffold_multi_angle_puppet');
    expect(toolNames).toContain('ch_scaffold_walk_puppet');
    expect(toolNames).toContain('ch_slice_artwork_to_puppet');
    expect(toolNames).toContain('ch_add_puppet_triggers_and_physics');
    expect(toolNames).toContain('ch_audit_puppet_deep');
    expect(toolNames).toContain('ch_auto_repair_puppet');
    expect(toolNames).toContain('ch_prepare_recording_take');

    // Illustrator tools (6)
    expect(toolNames).toContain('ai_create_document');
    expect(toolNames).toContain('ai_execute_jsx');
    expect(toolNames).toContain('ai_trace_and_clean_sketch');
    expect(toolNames).toContain('ai_auto_rig_slice');
    expect(toolNames).toContain('ai_apply_color_palette');
    expect(toolNames).toContain('ai_export_character_package');

    // Audio tools (5)
    expect(toolNames).toContain('audio_generate_speech');
    expect(toolNames).toContain('audio_calculate_viseme_cues');
    expect(toolNames).toContain('audio_generate_expressive_speech');
    expect(toolNames).toContain('audio_export_lip_sync_markers');
    expect(toolNames).toContain('audio_list_available_voices');

    // After Effects tools (7)
    expect(toolNames).toContain('ae_import_puppet_scene');
    expect(toolNames).toContain('ae_execute_jsx');
    expect(toolNames).toContain('ae_render_comp');
    expect(toolNames).toContain('ae_generate_scene_manifest');
    expect(toolNames).toContain('ae_setup_25d_stage');
    expect(toolNames).toContain('ae_apply_animation_expressions');
    expect(toolNames).toContain('ae_batch_render_queue');

    // Blender tools (5)
    expect(toolNames).toContain('blender_execute_script');
    expect(toolNames).toContain('blender_render_frame');
    expect(toolNames).toContain('blender_scaffold_3d_room');
    expect(toolNames).toContain('blender_render_parallax_passes');
    expect(toolNames).toContain('blender_grease_pencil_sketch');

    // Pipeline tools (3 - Phase 7)
    expect(toolNames).toContain('render_preview_frame_to_base64');
    expect(toolNames).toContain('pipeline_create_talking_character');
    expect(toolNames).toContain('pipeline_render_social_clip');

    for (const tool of allTools) {
      expect(tool.description).toBeDefined();
      expect(tool.description.length).toBeGreaterThan(10);
      expect(tool.inputSchema).toBeDefined();
      expect(typeof tool.handler).toBe('function');
    }
  });

  it('executes ch_scaffold_puppet tool successfully with Phase 2 deep puppet features', async () => {
    const scaffoldTool = characterTools.find(t => t.name === 'ch_scaffold_puppet')!;
    const res = await scaffoldTool.handler({
      character_name: 'Robot',
      output_path: tempPsd,
      width: 800,
      height: 800,
      include_physics_tags: true,
      include_hand_triggers: true,
      include_face_parallax: true
    });

    expect(res.content[0].type).toBe('text');
    const parsed = JSON.parse(res.content[0].text);
    expect(parsed.status).toBe('SUCCESS');
    expect(parsed.features_included.custom_graphic_visemes).toBe(14);
    expect(parsed.features_included.physics_tags).toBe(true);
    expect(parsed.features_included.hand_swap_triggers).toBe(true);
    expect(fs.existsSync(tempPsd)).toBe(true);
  });

  it('executes ch_validate_puppet verifying Phase 2 physics tags and hand triggers', async () => {
    const validateTool = characterTools.find(t => t.name === 'ch_validate_puppet')!;
    const res = await validateTool.handler({ file_path: tempPsd });

    const parsed = JSON.parse(res.content[0].text);
    expect(parsed.status).toBe('VALID');
    expect(parsed.hasHead).toBe(true);
    expect(parsed.hasMouth).toBe(true);
    expect(parsed.physicsFeatures.hasDangle).toBe(true);
    expect(parsed.physicsFeatures.hasFixed).toBe(true);
    expect(parsed.handTriggers.hasSwapSets).toBe(true);
  });

  it('executes audio_generate_expressive_speech (Phase 4)', async () => {
    const ttsTool = audioTools.find(t => t.name === 'audio_generate_expressive_speech')!;
    const res = await ttsTool.handler({
      text: '¡Hola! Este es un diálogo expresivo de prueba.',
      output_path: tempWav,
      voice: 'mexico_female',
      emotion_preset: 'cheerful'
    });

    const parsed = JSON.parse(res.content[0].text);
    expect(parsed.status).toBe('SUCCESS');
    expect(parsed.sample_rate).toBe('48,000 Hz');
    expect(parsed.channels).toBe('Mono');
    expect(parsed.ready_for_character_animator).toBe(true);
    expect(fs.existsSync(tempWav)).toBe(true);
  }, 15000);

  it('executes audio_export_lip_sync_markers (Phase 4)', async () => {
    const markerTool = audioTools.find(t => t.name === 'audio_export_lip_sync_markers')!;
    const res = await markerTool.handler({
      text: '¡Hola! Este es un diálogo expresivo de prueba.',
      output_path: path.join(tempMarkers, 'dialogue_cues'),
      fps: 24,
      format: 'all'
    });

    const parsed = JSON.parse(res.content[0].text);
    expect(parsed.status).toBe('SUCCESS');
    expect(parsed.total_cues).toBeGreaterThan(0);
    expect(parsed.exported_files.json).toBeDefined();
    expect(parsed.exported_files.after_effects_jsx).toBeDefined();
    expect(parsed.exported_files.csv_markers).toBeDefined();
    expect(fs.existsSync(parsed.exported_files.json)).toBe(true);
  });

  it('executes ae_generate_scene_manifest tool (Phase 5)', async () => {
    const manifestTool = afterEffectsTools.find(t => t.name === 'ae_generate_scene_manifest')!;
    const jsonPath = path.join(tempManifestDir, 'test_manifest.json');
    const res = await manifestTool.handler({
      scene_name: 'Hero_Intro',
      output_manifest_path: jsonPath,
      layers: [
        { name: 'Background', file_path: 'F:/bg.png', layer_type: 'background', z_depth: 1500 },
        { name: 'Hero', file_path: 'F:/hero.psd', layer_type: 'character', z_depth: 0 }
      ],
      enable_camera: true,
      enable_depth_of_field: true
    });

    const parsed = JSON.parse(res.content[0].text);
    expect(parsed.status).toBe('SUCCESS');
    expect(parsed.manifest_json).toBe(jsonPath);
    expect(parsed.constructor_jsx).toBeDefined();
    expect(fs.existsSync(jsonPath)).toBe(true);
    expect(fs.existsSync(parsed.constructor_jsx)).toBe(true);
  });

  it('executes ae_setup_25d_stage tool (Phase 5)', async () => {
    const stageTool = afterEffectsTools.find(t => t.name === 'ae_setup_25d_stage')!;
    const outJsx = path.join(tempManifestDir, 'stage_test.jsx');
    const res = await stageTool.handler({
      scene_name: 'Studio_Stage',
      background_file: 'F:/bg.png',
      character_file: 'F:/char.psd',
      execute_now: false,
      output_script_path: outJsx
    });

    const parsed = JSON.parse(res.content[0].text);
    expect(parsed.status).toBe('SUCCESS');
    expect(parsed.jsx_path).toBe(outJsx);
    expect(fs.existsSync(outJsx)).toBe(true);
  });

  it('executes ae_apply_animation_expressions tool (Phase 5)', async () => {
    const exprTool = afterEffectsTools.find(t => t.name === 'ae_apply_animation_expressions')!;
    const res = await exprTool.handler({
      expression_type: 'squash_and_stretch',
      target_layer_name: 'Hero',
      target_property: 'Scale',
      params: { maxAmplitude: 15, frequency: 3 },
      execute_now: false
    });

    const parsed = JSON.parse(res.content[0].text);
    expect(parsed.status).toBe('SUCCESS');
    expect(parsed.expression_snippet).toContain('var maxAmp = 15;');
    expect(parsed.expression_snippet).toContain('var freq = 3;');
    expect(fs.existsSync(parsed.jsx_path)).toBe(true);
  });

  it('executes blender_scaffold_3d_room tool (Phase 6)', async () => {
    const roomTool = blenderTools.find(t => t.name === 'blender_scaffold_3d_room')!;
    const blendPath = path.join(tempBlenderDir, 'room_mcp.blend');
    const res = await roomTool.handler({
      room_type: 'studio_stage',
      output_path: blendPath,
      render_preview: false,
      width: 640,
      height: 360
    });

    const parsed = JSON.parse(res.content[0].text);
    expect(parsed.status).toBe('SUCCESS');
    expect(parsed.blend_file).toBe(blendPath);
    expect(fs.existsSync(blendPath)).toBe(true);
  }, 30000);

  it('executes blender_grease_pencil_sketch tool (Phase 6)', async () => {
    const gpTool = blenderTools.find(t => t.name === 'blender_grease_pencil_sketch')!;
    const gpBlend = path.join(tempBlenderDir, 'gp_mcp.blend');
    const res = await gpTool.handler({
      sketch_type: 'speed_lines',
      output_path: gpBlend,
      render_preview: false,
      width: 640,
      height: 360
    });

    const parsed = JSON.parse(res.content[0].text);
    expect(parsed.status).toBe('SUCCESS');
    expect(parsed.blend_file).toBe(gpBlend);
    expect(fs.existsSync(gpBlend)).toBe(true);
  }, 30000);

  it('executes render_preview_frame_to_base64 tool (Phase 7)', async () => {
    const visionTool = pipelineTools.find(t => t.name === 'render_preview_frame_to_base64')!;
    fs.mkdirSync(tempPipelineDir, { recursive: true });
    const samplePng = path.join(tempPipelineDir, 'test_frame.png');
    const pngBase64 = 'iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAFElEQVQIW2P8z/D/PwMjgxhDAwMDAB1nBAX+I8WdAAAAAElFTkSuQmCC';
    fs.writeFileSync(samplePng, Buffer.from(pngBase64, 'base64'));

    const res = await visionTool.handler({ file_path: samplePng });
    expect(res.content.length).toBe(2);
    expect(res.content[0].type).toBe('text');
    expect(res.content[1].type).toBe('image');
    expect(res.content[1].mimeType).toBe('image/png');
    expect(res.content[1].data.length).toBeGreaterThan(10);
  });

  it('executes pipeline_render_social_clip tool (Phase 7)', async () => {
    const socialTool = pipelineTools.find(t => t.name === 'pipeline_render_social_clip')!;
    const outDir = path.join(tempPipelineDir, 'social_test');
    const dummyChar = path.join(outDir, 'dummy.psd');
    fs.mkdirSync(outDir, { recursive: true });
    fs.writeFileSync(dummyChar, 'dummy content');

    const res = await socialTool.handler({
      project_name: 'Shorts_Test',
      output_dir: outDir,
      character_file: dummyChar,
      aspect_ratio: '9:16'
    });

    const parsed = JSON.parse(res.content[0].text);
    expect(parsed.status).toBe('SUCCESS');
    expect(parsed.aspectRatio).toBe('9:16');
    expect(parsed.resolution.width).toBe(1080);
    expect(parsed.resolution.height).toBe(1920);
    expect(fs.existsSync(parsed.sceneManifestPath)).toBe(true);
  });

  it('executes ch_inspect_environment tool', async () => {
    const envTool = characterTools.find(t => t.name === 'ch_inspect_environment')!;
    const res = await envTool.handler({});

    const parsed = JSON.parse(res.content[0].text);
    expect(parsed.status).toBe('SUCCESS');
    expect(parsed.environment.characterAnimator.installed).toBe(true);
    expect(parsed.environment.illustrator.installed).toBe(true);
    expect(parsed.environment.blender.installed).toBe(true);
  });

  it('executes ch_get_roadmap_status hook reporting all 7 phases completed', async () => {
    const hookTool = characterTools.find(t => t.name === 'ch_get_roadmap_status')!;
    const res = await hookTool.handler({});

    const parsed = JSON.parse(res.content[0].text);
    expect(parsed.status).toBe('SUCCESS');
    expect(parsed.roadmap.currentPhase).toBe(7);
    expect(parsed.roadmap.status).toBe('ALL_PHASES_COMPLETED');
  });
});
