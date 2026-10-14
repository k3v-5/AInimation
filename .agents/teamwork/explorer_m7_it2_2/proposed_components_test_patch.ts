// Test addition for tests/frontend/components.test.ts:
// Verifies Intermediate Asset Card data contracts for F-UI-07

import { describe, it, expect } from 'vitest';
import { PlanStepSchema, ProductionPlanSchema } from '../../src/types';

describe('F-UI-07: Intermediate Asset Cards Contract', () => {
  it('validates intermediate asset card schemas across all 5 key production outputs', () => {
    // 1. Audio analysis stems output
    const audioStep = PlanStepSchema.parse({
      step_id: 'step_audio',
      index: 0,
      tool_name: 'analyze_audio',
      title: 'Análisis de Audio y Detección de BPM',
      description: 'Extracción de BPM y stems',
      parameters: { bpm_hint: 128 },
      risk_level: 'low',
      requires_confirmation: false,
      status: 'completed',
      output_preview: 'stems:vocals.wav,drums.wav,bass.wav,other.wav',
    });
    expect(audioStep.output_preview).toContain('stems:');
    expect(audioStep.status).toBe('completed');

    // 2. Image-to-3D mesh output
    const meshStep = PlanStepSchema.parse({
      step_id: 'step_mesh',
      index: 1,
      tool_name: 'image_to_3d',
      title: 'Generación de Malla 3D',
      description: 'Creación de GLB',
      parameters: { image_path: 'concept.png' },
      risk_level: 'medium',
      requires_confirmation: true,
      status: 'approved',
      output_preview: 'outputs/character_mesh.glb',
    });
    expect(meshStep.output_preview).toMatch(/\.glb$/);
    expect(meshStep.status).toBe('approved');

    // 3. Auto-rigging output
    const rigStep = PlanStepSchema.parse({
      step_id: 'step_rig',
      index: 2,
      tool_name: 'auto_rig',
      title: 'Auto-Rigging Bípedo',
      description: 'Rigging UE5 Mannequin',
      parameters: { mesh_path: 'character.glb' },
      risk_level: 'medium',
      requires_confirmation: true,
      status: 'approved',
      output_preview: 'outputs/character_rigged.glb',
    });
    expect(rigStep.output_preview).toContain('rigged');

    // 4. Mocap extraction output
    const mocapStep = PlanStepSchema.parse({
      step_id: 'step_mocap',
      index: 3,
      tool_name: 'extract_mocap',
      title: 'Mocap GVHMR',
      description: 'Extracción de movimiento',
      parameters: { video_path: 'dance.mp4' },
      risk_level: 'medium',
      requires_confirmation: true,
      status: 'approved',
      output_preview: 'outputs/dance_mocap.glb',
    });
    expect(mocapStep.output_preview).toContain('mocap');

    // 5. Rendered video output
    const renderStep = PlanStepSchema.parse({
      step_id: 'step_render',
      index: 5,
      tool_name: 'render_video',
      title: 'Render Cinemático MRQ',
      description: 'Exportación a 4K 60fps',
      parameters: { resolution: '3840x2160', fps: 60 },
      risk_level: 'high',
      requires_confirmation: true,
      status: 'completed',
      output_preview: 'outputs/final_music_video.mp4',
    });
    expect(renderStep.output_preview).toMatch(/\.mp4$/);
  });
});
