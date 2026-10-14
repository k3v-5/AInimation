import { describe, it, expect } from 'vitest';
import { useUIStore } from '../../src/store';
import {
  Vector3DSchema,
  Rotator3DSchema,
  CameraKeyframeSchema,
  AudioAnalysisSchema,
  PlanStepSchema,
  ProductionPlanSchema,
  TelemetryEventSchema,
} from '../../src/types';

describe('Frontend Data Contracts and Store', () => {
  it('validates Vector3D and Rotator3D schemas', () => {
    const vec = Vector3DSchema.parse({ x: 10.0, y: -20.0, z: 120.0 });
    expect(vec.z).toBe(120.0);

    const rot = Rotator3DSchema.parse({ pitch: -10, yaw: 45, roll: 0 });
    expect(rot.yaw).toBe(45);
  });

  it('validates CameraKeyframeSchema bounds', () => {
    const kf = CameraKeyframeSchema.parse({
      time: 2.5,
      x: 0,
      y: -400,
      z: 120,
      pitch: 0,
      yaw: 15,
      fov: 60,
    });
    expect(kf.time).toBe(2.5);
    expect(kf.fov).toBe(60);
  });

  it('validates ProductionPlan and Step approval state transition in Zustand', () => {
    const store = useUIStore.getState();
    const plan = ProductionPlanSchema.parse({
      plan_id: 'test_plan_001',
      title: 'Demo Plan',
      description: 'End-to-end video test',
      steps: [
        {
          step_id: 'step_1',
          index: 0,
          tool_name: 'analyze_audio',
          description: 'Analyze beats',
          parameters: {},
          risk_level: 'low',
          requires_confirmation: false,
          status: 'proposed',
        },
        {
          step_id: 'step_2',
          index: 1,
          tool_name: 'render_video',
          description: 'Render video',
          parameters: {},
          risk_level: 'high',
          requires_confirmation: true,
          status: 'proposed',
        },
      ],
      status: 'proposed',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      total_estimated_duration_seconds: 15,
    });

    store.setActivePlan(plan);
    expect(useUIStore.getState().activePlan?.steps[1].status).toBe('proposed');

    store.approveStep('step_2');
    expect(useUIStore.getState().activePlan?.steps[1].status).toBe('approved');

    store.rejectStep('step_2');
    expect(useUIStore.getState().activePlan?.steps[1].status).toBe('rejected');
    expect(useUIStore.getState().activePlan?.status).toBe('rejected');
  });

  it('validates TelemetryEvent discriminated union parsing', () => {
    const progressEvent = TelemetryEventSchema.parse({
      type: 'progress',
      stage: 'image_to_3d',
      percentage: 75.5,
      message: 'Generating GLB mesh',
      timestamp: new Date().toISOString(),
    });
    expect(progressEvent.type).toBe('progress');

    const logEvent = TelemetryEventSchema.parse({
      type: 'log',
      level: 'info',
      message: 'UE5 bridge connected',
      source: 'FastMCP',
      timestamp: new Date().toISOString(),
    });
    expect(logEvent.type).toBe('log');
  });

  it('validates complete production plan lifecycle with 6 stages', () => {
    const store = useUIStore.getState();
    const sixStagePlan = ProductionPlanSchema.parse({
      plan_id: 'plan_six_stage_001',
      title: 'Full Cinematic Orchestration',
      description: 'End-to-end 6-stage audio-reactive video generation',
      steps: [
        {
          step_id: 'step_1_audio',
          index: 0,
          tool_name: 'analyze_audio',
          description: 'Extract BPM and onsets',
          parameters: { audio_path: 'track.wav' },
          risk_level: 'low',
          requires_confirmation: false,
          status: 'completed',
        },
        {
          step_id: 'step_2_mesh',
          index: 1,
          tool_name: 'image_to_3d',
          description: 'Generate GLB mesh',
          parameters: { image_path: 'concept.png' },
          risk_level: 'medium',
          requires_confirmation: true,
          status: 'proposed',
        },
        {
          step_id: 'step_3_rig',
          index: 2,
          tool_name: 'auto_rig',
          description: 'Skeletal rigging',
          parameters: { mesh_path: 'character.glb' },
          risk_level: 'medium',
          requires_confirmation: true,
          status: 'proposed',
        },
        {
          step_id: 'step_4_mocap',
          index: 3,
          tool_name: 'extract_mocap',
          description: 'Extract 3D dance mocap',
          parameters: { video_path: 'dance.mp4' },
          risk_level: 'medium',
          requires_confirmation: true,
          status: 'proposed',
        },
        {
          step_id: 'step_5_scene',
          index: 4,
          tool_name: 'build_ue5_scene',
          description: 'Construct UE5 CineCamera and Lumen scene',
          parameters: { style: 'cyberpunk' },
          risk_level: 'low',
          requires_confirmation: false,
          status: 'proposed',
        },
        {
          step_id: 'step_6_render',
          index: 5,
          tool_name: 'render_video',
          description: 'Render video via MRQ',
          parameters: { resolution: '3840x2160', fps: 60 },
          risk_level: 'high',
          requires_confirmation: true,
          status: 'proposed',
        },
      ],
      status: 'proposed',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      total_estimated_duration_seconds: 60,
    });

    store.setActivePlan(sixStagePlan);
    expect(useUIStore.getState().activePlan?.steps.length).toBe(6);

    // Approve intermediate steps
    store.approveStep('step_2_mesh');
    store.approveStep('step_3_rig');
    store.approveStep('step_4_mocap');
    store.approveStep('step_6_render');

    const updated = useUIStore.getState().activePlan;
    expect(updated?.steps[1].status).toBe('approved');
    expect(updated?.steps[2].status).toBe('approved');
    expect(updated?.steps[3].status).toBe('approved');
    expect(updated?.steps[5].status).toBe('approved');
  });

  it('validates audio analysis with beat grid and envelope', () => {
    const analysis = AudioAnalysisSchema.parse({
      bpm: 128.0,
      duration_seconds: 10.0,
      beat_timestamps: [0.0, 0.468, 0.937, 1.406, 1.875],
      onset_envelope: [0.1, 0.8, 0.9, 0.3],
      time_signature: '4/4',
      danceability: 0.85,
    });
    expect(analysis.bpm).toBe(128.0);
    expect(analysis.beat_timestamps.length).toBe(5);
    expect(analysis.time_signature).toBe('4/4');
  });

  it('validates LightingPreset and CameraPreset schemas and state controls', () => {
    const store = useUIStore.getState();

    store.setLightingPreset('cyberpunk_neon');
    expect(useUIStore.getState().lightingPreset).toBe('cyberpunk_neon');

    store.setLightingPreset('studio_3point');
    expect(useUIStore.getState().lightingPreset).toBe('studio_3point');

    store.setCameraPreset('dramatic_orbit');
    expect(useUIStore.getState().cameraPreset).toBe('dramatic_orbit');

    store.setCameraPreset('spiral_ascent');
    expect(useUIStore.getState().cameraPreset).toBe('spiral_ascent');
  });

  it('validates playback transport and timeline state management', () => {
    const store = useUIStore.getState();

    store.setCurrentTime(4.25);
    expect(useUIStore.getState().currentTime).toBe(4.25);

    store.setIsPlaying(true);
    expect(useUIStore.getState().isPlaying).toBe(true);

    store.setIsPlaying(false);
    expect(useUIStore.getState().isPlaying).toBe(false);

    store.setDuration(30.0);
    expect(useUIStore.getState().duration).toBe(30.0);
  });

  it('validates WebRTC pixel streaming state transitions', () => {
    const store = useUIStore.getState();

    store.setSignalingUrl('ws://127.0.0.1:8888');
    expect(useUIStore.getState().signalingUrl).toBe('ws://127.0.0.1:8888');

    store.setPixelStreamingStatus('connecting');
    expect(useUIStore.getState().pixelStreamingStatus).toBe('connecting');

    store.setPixelStreamingStatus('connected');
    expect(useUIStore.getState().pixelStreamingStatus).toBe('connected');

    store.setPixelStreamingStatus('disconnected');
    expect(useUIStore.getState().pixelStreamingStatus).toBe('disconnected');
  });

  it('validates media dropzone path updates and clears', () => {
    const store = useUIStore.getState();

    store.setAudioPath('test_beat.wav');
    store.setImagePath('test_character.png');
    store.setVideoPath('test_dance.mp4');

    expect(useUIStore.getState().audioPath).toBe('test_beat.wav');
    expect(useUIStore.getState().imagePath).toBe('test_character.png');
    expect(useUIStore.getState().videoPath).toBe('test_dance.mp4');

    store.setAudioPath(null);
    expect(useUIStore.getState().audioPath).toBeNull();
  });

  it('F-UI-07: validates intermediate asset card schemas across all 5 key production outputs', () => {
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

